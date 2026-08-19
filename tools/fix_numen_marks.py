#!/usr/bin/env python3
"""
Give Numen Title the combining marks and GDEF classing it needs to set
Vietnamese and Dutch.

Numen Title inherits two gaps from Fraunces: U+0309 (hook above) and U+0323
(dot below) are unmapped, and there is no GDEF table, so a shaper treats every
combining mark as a base glyph and stacks them wrongly.

Both are fixable without drawing anything new: the marks already exist inside
the precomposed Vietnamese glyphs the font ships (Ahookabove, Adotbelow, ...),
so we isolate them by subtracting the base letter's contours and re-emit them
as zero-width combining glyphs.

Usage: fix_numen_marks.py <family-dir>
"""
import sys, os, glob
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen


def contours_of(gs, name):
    """Split a glyph into a list of contours, each a list of (op, pts)."""
    rec = DecomposingRecordingPen(gs)
    gs[name].draw(rec)
    out, cur = [], []
    for op, pts in rec.value:
        cur.append((op, pts))
        if op == "closePath":
            out.append(cur)
            cur = []
    return out


def contour_points(contour):
    return [q for op, P in contour if P for q in P if q is not None]


def contour_key(contour):
    """Rounded bbox — stable enough to match a base glyph's contours."""
    pts = contour_points(contour)
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys)))


def emit(pen, contour, dx=0.0):
    for op, pts in contour:
        if op == "moveTo":
            pen.moveTo((pts[0][0] + dx, pts[0][1]))
        elif op == "lineTo":
            pen.lineTo((pts[0][0] + dx, pts[0][1]))
        elif op == "qCurveTo":
            pen.qCurveTo(*[(p[0] + dx, p[1]) if p else None for p in pts])
        elif op == "curveTo":
            pen.curveTo(*[(p[0] + dx, p[1]) for p in pts])
        elif op == "closePath":
            pen.closePath()


def extract_mark(font, composed_char, base_char, glyph_name):
    """Isolate the mark in `composed_char` by removing `base_char`'s contours."""
    cmap = font.getBestCmap()
    if ord(composed_char) not in cmap or ord(base_char) not in cmap:
        return None
    gs = font.getGlyphSet()
    comp = contours_of(gs, cmap[ord(composed_char)])
    base_keys = {contour_key(c) for c in contours_of(gs, cmap[ord(base_char)])}
    mark = [c for c in comp if contour_key(c) not in base_keys]
    if not mark:
        return None

    pts = [p for c in mark for p in contour_points(c)]
    xs = [p[0] for p in pts]
    dx = -(min(xs) + max(xs)) / 2.0     # centre it over the origin

    pen = TTGlyphPen(None)
    for c in mark:
        emit(pen, c, dx)

    glyf, hmtx = font["glyf"], font["hmtx"]
    glyf[glyph_name] = pen.glyph()
    glyf[glyph_name].recalcBounds(glyf)
    hmtx[glyph_name] = (0, glyf[glyph_name].xMin)
    font.setGlyphOrder(glyf.glyphOrder)
    font["maxp"].numGlyphs = len(glyf.glyphOrder)
    for t in font["cmap"].tables:
        if t.isUnicode():
            t.cmap[ord_of(glyph_name)] = glyph_name
    return glyph_name


def ord_of(glyph_name):
    return int(glyph_name[3:], 16)      # "uni0309" -> 0x0309


def build_gdef(font):
    """Class every combining mark as class 3 so shapers stop treating them as bases."""
    cmap = font.getBestCmap()
    marks = {
        name for cp, name in cmap.items()
        if 0x0300 <= cp <= 0x036F or 0x1AB0 <= cp <= 0x1AFF or 0x20D0 <= cp <= 0x20F0
    }
    # Zero-width glyphs whose name looks like a mark are marks too.
    hmtx = font["hmtx"]
    for name in font.getGlyphOrder():
        if hmtx[name][0] == 0 and ("comb" in name or name.startswith("uni03")):
            marks.add(name)
    if not marks:
        return 0

    classes = {name: 3 for name in marks}
    for name in font.getGlyphOrder():
        classes.setdefault(name, 1)     # 1 = base glyph

    gdef = otTables.GDEF()
    gdef.Version = 0x00010000
    gdef.GlyphClassDef = otTables.GlyphClassDef()
    gdef.GlyphClassDef.classDefs = classes
    gdef.AttachList = None
    gdef.LigCaretList = None
    gdef.MarkAttachClassDef = None

    table = font.get("GDEF")
    if table is None:
        from fontTools.ttLib import newTable
        table = newTable("GDEF")
        font["GDEF"] = table
    table.table = gdef
    return len(marks)


if __name__ == "__main__":
    famdir = sys.argv[1]
    for path in sorted(glob.glob(os.path.join(famdir, "*.ttf"))):
        font = TTFont(path)
        added = []
        for composed, base, name in [("Ả", "A", "uni0309"), ("Ạ", "A", "uni0323")]:
            if ord_of(name) in font.getBestCmap():
                continue
            if extract_mark(font, composed, base, name):
                added.append(name)
        n = build_gdef(font)
        font.save(path)
        font.close()
        print(f"{os.path.basename(path)}: added {added or 'nothing'}, GDEF classed {n} marks")
