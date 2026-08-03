"""Reusable specimen renderer: HarfBuzz shaping + FreeType rasterization -> PIL.

Row spec: dict(label, path, size, text, wght=None, features=None, face_index=0,
              color=INK, letterspace=0.0 (em units))
"""
import freetype
import uharfbuzz as hb
from PIL import Image, ImageDraw

PAPER = (250, 251, 246, 255)   # #FAFBF6
INK = (23, 51, 98, 255)        # #173362
MUTE = (102, 112, 133, 255)    # #667085

_label_font = None

def _get_label_font():
    global _label_font
    if _label_font is None:
        from PIL import ImageFont
        try:
            _label_font = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 13)
        except Exception:
            _label_font = ImageFont.load_default()
    return _label_font


def find_ttc_index(path, want):
    """Return face index in a ttc whose family+style matches `want` (substring, casefold)."""
    i = 0
    while True:
        try:
            f = freetype.Face(path, i)
        except Exception:
            break
        name = f"{f.family_name.decode()} {f.style_name.decode()}"
        if want.casefold() in name.casefold():
            return i, name
        i += 1
    return None, None


def list_ttc_faces(path):
    out, i = [], 0
    while True:
        try:
            f = freetype.Face(path, i)
        except Exception:
            break
        out.append((i, f"{f.family_name.decode()} {f.style_name.decode()}"))
        i += 1
    return out


class Line:
    """One shaped line ready to paint."""
    def __init__(self, path, text, size, wght=None, features=None, face_index=0,
                 letterspace=0.0):
        self.size = size
        with open(path, 'rb') as fh:
            data = fh.read()
        blob = hb.Blob(data)
        face = hb.Face(blob, face_index)
        font = hb.Font(face)
        upem = face.upem
        font.scale = (upem, upem)
        if wght is not None:
            try:
                font.set_variations({'wght': float(wght)})
            except Exception:
                pass
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        feats = {'kern': True, 'liga': True}
        if features:
            feats.update(features)
        hb.shape(font, buf, feats)
        self.infos = buf.glyph_infos
        self.poss = buf.glyph_positions
        self.upem = upem
        self.scale = size / upem
        self.letterspace = letterspace * upem  # em units -> font units

        self.ft = freetype.Face(path, face_index)
        self.ft.set_char_size(int(size * 64))
        if wght is not None:
            try:
                coords = list(self.ft.get_var_design_coords())
                # find wght axis index from MM var info
                mm = self.ft.get_variation_info()
                for ai, ax in enumerate(mm.axes):
                    if ax.tag == b'wght' or ax.tag == 'wght':
                        coords[ai] = float(wght)
                self.ft.set_var_design_coords(coords)
            except Exception:
                pass

    def width(self):
        adv = sum(p.x_advance + self.letterspace for p in self.poss)
        return adv * self.scale

    def paint(self, img, x, y, color=INK):
        """Paint at baseline y, origin x. Returns end x."""
        pen_x = x
        for info, pos in zip(self.infos, self.poss):
            gx = pen_x + (pos.x_offset * self.scale)
            gy = y - (pos.y_offset * self.scale)
            self.ft.load_glyph(info.codepoint, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
            g = self.ft.glyph
            bm = g.bitmap
            if bm.width and bm.rows:
                mask = Image.frombytes('L', (bm.width, bm.rows), bytes(bm.buffer))
                ox = int(round(gx + g.bitmap_left))
                oy = int(round(gy - g.bitmap_top))
                solid = Image.new('RGBA', mask.size, color)
                img.paste(solid, (ox, oy), mask)
            pen_x += (pos.x_advance + self.letterspace) * self.scale
        return pen_x


def render_rows(rows, out_path, width=1560, pad=36, gap=18, bg=PAPER):
    """rows: list of dicts or None (spacer). Renders stacked rows with labels."""
    # First pass: measure heights
    entries = []
    for r in rows:
        if r is None:
            entries.append(None)
            continue
        line = Line(r['path'], r['text'], r['size'], r.get('wght'),
                    r.get('features'), r.get('face_index', 0), r.get('letterspace', 0.0))
        entries.append((r, line))
    label_h = 18
    total_h = pad
    for e in entries:
        if e is None:
            total_h += 24
            continue
        r, line = e
        total_h += label_h + int(r['size'] * 1.35) + gap
    total_h += pad
    img = Image.new('RGBA', (width, total_h), bg)
    draw = ImageDraw.Draw(img)
    lf = _get_label_font()
    y = pad
    for e in entries:
        if e is None:
            y += 24
            continue
        r, line = e
        if r.get('label'):
            draw.text((pad, y), r['label'], font=lf, fill=MUTE)
        y += label_h
        baseline = y + int(r['size'] * 1.0)
        line.paint(img, pad, baseline, r.get('color', INK))
        y = baseline + int(r['size'] * 0.35) + gap
    img.convert('RGB').save(out_path)
    return out_path
