#!/usr/bin/env python3
"""
Build Numen Title italic statics from Fraunces Italic.

Same transform as the roman family (kept.do/type, measured):

  opsz=52  SOFT=75  WONK=0  (normalised h/m/n/s/& — italic: b/d/h/k/l/v/w/&)
  wght in {300, 400, 500, 600, 700, 800}
  scale x 0.95, y 1.02
  straight-j rule on the j family (stem continues at the italic slant)
  check / ballot-x grafted from the matching roman weight
  family vertical metrics kept at the roman values so styles mix

Usage:
  build_numen_italic.py \\
      <Fraunces-Italic-VF.ttf> \\
      <kept-type/NumenTitle> \\
      <out-dir>
"""
from __future__ import annotations

import math
import os
import sys

from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from straighten_numen_j import (  # noqa: E402
    J_FAMILY,
    HOOK_Y,
    BASELINE,
    contour_commands,
    contour_ymin,
    emit,
    recording,
)

SX = 0.95
SY = 1.02
OPSZ = 52
SOFT = 75
WONK = 0

WEIGHTS = [
    (300, "Light"),
    (400, "Regular"),
    (500, "Medium"),
    (600, "SemiBold"),
    (700, "Bold"),
    (800, "ExtraBold"),
]

FAMILY = "Numen Title"
VERSION = "1.400"
REPO = "https://github.com/JessieSalas/kept-legibility-index"

# Roman family metrics (unified). Italic must match so styles mix.
TYPO_ASC = 1956
TYPO_DESC = -510
TYPO_GAP = 0
WIN_ASC = 2299
WIN_DESC = 589

# Codepoints whose outlines are the hooked j, whatever the production name.
J_UNICODES = (
    0x006A,  # j
    0x0135,  # jcircumflex
    0x01F0,  # j caron (jacute in Fraunces/Glyphs)
    0x0133,  # ij
    0x0237,  # dotlessj
    0x01C9,  # lj
    0x01C8,  # Lj
)

GRAFT = {
    0x2713: "check",
    0x2717: "ballotx",
}


def set_name(font, nid, value):
    font["name"].setName(value, nid, 3, 1, 0x409)
    font["name"].setName(value, nid, 1, 0, 0)


def scale_valuerecord(vr, sx, sy):
    if vr is None:
        return
    for attr, s in (
        ("XPlacement", sx),
        ("YPlacement", sy),
        ("XAdvance", sx),
        ("YAdvance", sy),
        ("XPlaDevice", None),
        ("YPlaDevice", None),
    ):
        if s is None:
            continue
        if hasattr(vr, attr) and getattr(vr, attr):
            setattr(vr, attr, int(round(getattr(vr, attr) * s)))


def scale_anchor(anchor, sx, sy):
    if anchor is None:
        return
    if hasattr(anchor, "XCoordinate"):
        anchor.XCoordinate = int(round(anchor.XCoordinate * sx))
    if hasattr(anchor, "YCoordinate"):
        anchor.YCoordinate = int(round(anchor.YCoordinate * sy))


def scale_gpos_subtable(sub, sx, sy):
    fmt = getattr(sub, "Format", None)
    # Extension
    if hasattr(sub, "ExtSubTable") and sub.ExtSubTable is not None:
        scale_gpos_subtable(sub.ExtSubTable, sx, sy)
        return
    if hasattr(sub, "Value"):
        scale_valuerecord(sub.Value, sx, sy)
    if hasattr(sub, "ValueRecord"):
        scale_valuerecord(sub.ValueRecord, sx, sy)
    for attr in ("Value1", "Value2"):
        if hasattr(sub, attr):
            scale_valuerecord(getattr(sub, attr), sx, sy)
    # PairPos format 1 / 2
    if hasattr(sub, "PairSet"):
        for ps in sub.PairSet:
            for rec in ps.PairValueRecord:
                scale_valuerecord(rec.Value1, sx, sy)
                scale_valuerecord(rec.Value2, sx, sy)
    if hasattr(sub, "Class1Record"):
        for row in sub.Class1Record:
            for rec in row.Class2Record:
                scale_valuerecord(rec.Value1, sx, sy)
                scale_valuerecord(rec.Value2, sx, sy)
    # Coverage-based SinglePos format 2
    if hasattr(sub, "Value") and isinstance(sub.Value, list):
        for vr in sub.Value:
            scale_valuerecord(vr, sx, sy)
    # Mark / base / liga / mark-to-mark
    for arr_name, rec_name, anchor_names in (
        ("MarkArray", "MarkRecord", ("MarkAnchor",)),
        ("BaseArray", "BaseRecord", None),
        ("LigatureArray", "LigatureAttach", None),
        ("Mark2Array", "Mark2Record", None),
    ):
        arr = getattr(sub, arr_name, None)
        if arr is None:
            continue
        records = getattr(arr, rec_name, None) or getattr(arr, "MarkRecord", None)
        if records is None:
            continue
        for rec in records:
            if hasattr(rec, "MarkAnchor"):
                scale_anchor(rec.MarkAnchor, sx, sy)
            if hasattr(rec, "BaseAnchor"):
                for a in rec.BaseAnchor:
                    scale_anchor(a, sx, sy)
            if hasattr(rec, "Mark2Anchor"):
                for a in rec.Mark2Anchor:
                    scale_anchor(a, sx, sy)
            if hasattr(rec, "ComponentRecord"):
                for cr in rec.ComponentRecord:
                    for a in cr.LigatureAnchor:
                        scale_anchor(a, sx, sy)
    if hasattr(sub, "EntryAnchor"):
        scale_anchor(sub.EntryAnchor, sx, sy)
    if hasattr(sub, "ExitAnchor"):
        scale_anchor(sub.ExitAnchor, sx, sy)
    # Cursive per-glyph
    if hasattr(sub, "EntryExitRecord"):
        for rec in sub.EntryExitRecord:
            scale_anchor(rec.EntryAnchor, sx, sy)
            scale_anchor(rec.ExitAnchor, sx, sy)


def scale_layout(font, sx, sy):
    if "GPOS" not in font:
        return
    gpos = font["GPOS"].table
    if not gpos.LookupList:
        return
    for lookup in gpos.LookupList.Lookup:
        for sub in lookup.SubTable:
            scale_gpos_subtable(sub, sx, sy)
    if "kern" in font:
        kern = font["kern"]
        for table in getattr(kern, "tables", []) or []:
            if hasattr(table, "kernTable"):
                table.kernTable = {
                    k: int(round(v * sx)) for k, v in table.kernTable.items()
                }


def scale_glyf(font, sx, sy):
    glyf, hmtx = font["glyf"], font["hmtx"]
    xf = ((sx, 0), (0, sy))
    for name in font.getGlyphOrder():
        g = glyf[name]
        adv, lsb = hmtx[name]
        if g.isComposite():
            for c in g.components:
                c.x = c.x * sx
                c.y = c.y * sy
        elif getattr(g, "numberOfContours", 0) > 0:
            g.coordinates.transform(xf)
        try:
            g.recalcBounds(glyf)
            new_lsb = g.xMin if getattr(g, "numberOfContours", 0) else round(lsb * sx)
        except Exception:
            new_lsb = round(lsb * sx)
        hmtx[name] = (int(round(adv * sx)), int(round(new_lsb)))


def resolve_j_names(font):
    names = set()
    cmap = font.getBestCmap()
    for cp in J_UNICODES:
        if cp in cmap:
            names.add(cmap[cp])
    for n in J_FAMILY:
        if n in font.getGlyphOrder():
            names.add(n)
    # Accented / ligature production names that still carry the hook.
    for n in font.getGlyphOrder():
        low = n.lower()
        if low in {"uni006a", "uni0135", "uni01f0", "uni0133", "uni0237", "uni01c9", "uni01c8"}:
            names.add(n)
        if n in {"ijacute", "uni0133.acute", "jdotless"}:
            names.add(n)
    return sorted(names)


def pts_of(cmd):
    op, P = cmd
    if not P:
        return []
    return [p for p in P if p is not None]


def commands_to_points(cmds):
    pts = []
    for op, P in cmds:
        if op in ("moveTo", "lineTo"):
            pts.append((P[0][0], P[0][1], True))
        elif op == "qCurveTo":
            for p in P[:-1]:
                if p is not None:
                    pts.append((p[0], p[1], False))
            if P[-1] is not None:
                pts.append((P[-1][0], P[-1][1], True))
        elif op == "curveTo":
            for p in P:
                pts.append((p[0], p[1], True))
    return pts


def insert_baseline_crossings(pts):
    if len(pts) < 2:
        return pts
    out = [pts[0]]
    closed = pts + [pts[0]]
    for a, b in zip(closed, closed[1:]):
        if a[1] != 0 and b[1] != 0 and (a[1] > 0) != (b[1] > 0):
            t = (0.0 - a[1]) / (b[1] - a[1])
            out.append((a[0] + t * (b[0] - a[0]), 0.0, True))
        if b is not pts[0]:
            out.append(b)
    return out


def emit_points(pen, pts):
    if not pts:
        return
    pen.moveTo((pts[0][0], pts[0][1]))
    i = 1
    while i < len(pts):
        if pts[i][2]:
            pen.lineTo((pts[i][0], pts[i][1]))
            i += 1
            continue
        offs = []
        while i < len(pts) and not pts[i][2]:
            offs.append((pts[i][0], pts[i][1]))
            i += 1
        if i < len(pts):
            pen.qCurveTo(*offs, (pts[i][0], pts[i][1]))
            i += 1
        else:
            pen.qCurveTo(*offs, None)
    pen.closePath()


def slanted_descender(x_right, x_left, desc_y, slant):
    """Stem edges follow dx/dy = slant; flat rounded terminal at desc_y."""
    stem = abs(x_right - x_left)
    r = max(24.0, min(48.0, stem * 0.18))
    r = min(r, stem * 0.45)
    y_c = desc_y + r

    def x_at(x0, y):
        return x0 + slant * y

    xr_c, xl_c = x_at(x_right, y_c), x_at(x_left, y_c)
    xr_b, xl_b = x_at(x_right, desc_y), x_at(x_left, desc_y)
    # Horizontal flat between the two bottom corners, inset by r along the bottom.
    if xr_b > xl_b:
        xr_i, xl_i = xr_b - r, xl_b + r
    else:
        xr_i, xl_i = xr_b + r, xl_b - r
    return [
        (xr_c, y_c, True),
        (xr_b, desc_y, False),
        (xr_i, desc_y, True),
        (xl_i, desc_y, True),
        (xl_b, desc_y, False),
        (xl_c, y_c, True),
        (x_left, 0.0, True),
    ]


def straighten_italic_contour(cmds, desc_y, slant):
    pts = insert_baseline_crossings(commands_to_points(cmds))
    below_idx = [i for i, p in enumerate(pts) if p[1] < BASELINE]
    if not below_idx:
        return cmds, False
    # The hook is the contiguous below-baseline run (wrap-aware, but j doesn't wrap).
    start, end = below_idx[0], below_idx[-1]
    # Neighbours on the baseline are the stem cuts.
    left_cut = pts[end + 1] if end + 1 < len(pts) else pts[0]
    right_cut = pts[start - 1] if start > 0 else pts[-1]
    # Which cut is the right stem? Higher x at baseline, after un-slanting.
    a, b = right_cut, left_cut
    if a[0] < b[0]:
        a, b = b, a
        prefix, suffix = pts[: start], pts[end + 1 :]
        # start-1 is left, end+1 is right — rebuild from actual indices
    prefix = pts[:start]
    suffix = pts[end + 1 :]
    # prefix ends at the first baseline cut (right stem going down);
    # suffix starts at the second (left stem going up).
    if prefix:
        x_right = prefix[-1][0]
    else:
        x_right = a[0]
    if suffix:
        x_left = suffix[0][0]
    else:
        x_left = b[0]
    # Guarantee prefix ends on the baseline cut so the new run starts there.
    if prefix and abs(prefix[-1][1]) > 0.5:
        prefix = prefix + [(x_right, 0.0, True)]
    new_mid = slanted_descender(x_right, x_left, desc_y, slant)
    # slanted_descender already ends at (x_left, 0); drop a duplicate suffix start.
    if suffix and abs(suffix[0][0] - new_mid[-1][0]) < 1 and abs(suffix[0][1]) < 0.5:
        suffix = suffix[1:]
    return prefix + new_mid + suffix, True


def straighten_italic_glyph(font, name, desc_y, slant):
    rec = recording(font, name)
    contours = contour_commands(rec)
    changed = False
    rebuilt_cmds = []
    rebuilt_pts = []
    use_pts = False
    for cmds in contours:
        if contour_ymin(cmds) < HOOK_Y:
            pts, did = straighten_italic_contour(cmds, desc_y, slant)
            changed = changed or did
            if did:
                use_pts = True
                rebuilt_pts.append(("pts", pts))
            else:
                rebuilt_pts.append(("cmds", cmds))
            rebuilt_cmds.append(cmds)
        else:
            rebuilt_pts.append(("cmds", cmds))
            rebuilt_cmds.append(cmds)
    if not changed:
        return False
    pen = TTGlyphPen(None)
    for kind, payload in rebuilt_pts:
        if kind == "pts":
            emit_points(pen, payload)
        else:
            emit(pen, payload)
    glyf, hmtx = font["glyf"], font["hmtx"]
    adv = hmtx[name][0]
    glyf[name] = pen.glyph()
    glyf[name].recalcBounds(glyf)
    hmtx[name] = (adv, glyf[name].xMin)
    return True


def graft_marks(italic, roman):
    """Copy check / ballot-x from the matching roman weight."""
    rcmap = roman.getBestCmap()
    icmap = italic.getBestCmap()
    glyf_i, glyf_r = italic["glyf"], roman["glyf"]
    hmtx_i, hmtx_r = italic["hmtx"], roman["hmtx"]
    added = []
    for cp, fallback in GRAFT.items():
        src = rcmap.get(cp)
        if not src or src not in glyf_r:
            continue
        dst = icmap.get(cp) or fallback
        glyf_i[dst] = glyf_r[src]
        hmtx_i[dst] = hmtx_r[src]
        if dst not in italic.getGlyphOrder():
            italic.setGlyphOrder(glyf_i.glyphOrder)
        italic["maxp"].numGlyphs = len(glyf_i.glyphOrder)
        for table in italic["cmap"].tables:
            if table.isUnicode():
                table.cmap[cp] = dst
        added.append(dst)
    return added


def drop_name(font, nid):
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID == nid:
            name.names.remove(rec)


def apply_italic_names(font, weight_name, wght):
    # Regular italic is RIBBI: file + PS name are Family-Italic, no 16/17.
    ps = "NumenTitle-Italic" if weight_name == "Regular" else f"NumenTitle-{weight_name}Italic"
    if weight_name == "Regular":
        set_name(font, 1, FAMILY)
        set_name(font, 2, "Italic")
        set_name(font, 4, f"{FAMILY} Italic")
        drop_name(font, 16)
        drop_name(font, 17)
    elif weight_name == "Bold":
        set_name(font, 1, FAMILY)
        set_name(font, 2, "Bold Italic")
        set_name(font, 4, f"{FAMILY} Bold Italic")
        drop_name(font, 16)
        drop_name(font, 17)
    else:
        set_name(font, 1, f"{FAMILY} {weight_name}")
        set_name(font, 2, "Italic")
        set_name(font, 4, f"{FAMILY} {weight_name} Italic")
        set_name(font, 16, FAMILY)
        set_name(font, 17, f"{weight_name} Italic")
    set_name(font, 6, ps)
    set_name(font, 5, f"Version {VERSION}")
    set_name(font, 3, f"{VERSION};KEPT;{ps}")
    font["head"].fontRevision = round(float(VERSION), 3)

    os2, head, post = font["OS/2"], font["head"], font["post"]
    os2.usWeightClass = wght
    # bit0 ITALIC, bit5 BOLD (Bold only), bit6 REGULAR off, bit7 USE_TYPO_METRICS
    fs = (1 << 0) | (1 << 7)
    if weight_name == "Bold":
        fs |= 1 << 5
    os2.fsSelection = fs
    mac = 1 << 1  # italic
    if weight_name == "Bold":
        mac |= 1 << 0
    head.macStyle = mac
    # Fraunces Italic ships -16; keep it.
    if post.italicAngle == 0:
        post.italicAngle = -16.0

    os2.sTypoAscender = TYPO_ASC
    os2.sTypoDescender = TYPO_DESC
    os2.sTypoLineGap = TYPO_GAP
    os2.usWinAscent = WIN_ASC
    os2.usWinDescent = WIN_DESC
    font["hhea"].ascent = TYPO_ASC
    font["hhea"].descent = TYPO_DESC
    font["hhea"].lineGap = TYPO_GAP
    if os2.sCapHeight:
        os2.sCapHeight = int(round(os2.sCapHeight * SY))
    if os2.sxHeight:
        os2.sxHeight = int(round(os2.sxHeight * SY))
    return ps


def apply_stat(font, wght, italic=True):
    # Statics may list only the values that apply to this file. A full
    # wght+ital ladder on every static FAILs FontBakery STAT_in_statics.
    weight_name = {300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}[wght]
    wght_value = {"value": wght, "name": weight_name}
    if weight_name == "Regular":
        wght_value["flags"] = 2
        wght_value["linkedValue"] = 700
    ital_values = (
        [{"value": 1, "name": "Italic"}]
        if italic
        else [{"value": 0, "name": "Roman", "flags": 2, "linkedValue": 1}]
    )
    buildStatTable(
        font,
        [
            {"tag": "wght", "name": "Weight", "values": [wght_value]},
            {"tag": "ital", "name": "Italic", "values": ital_values},
        ],
    )


def instance_italic(vf_path, wght):
    font = instantiateVariableFont(
        TTFont(vf_path),
        {"opsz": OPSZ, "SOFT": SOFT, "WONK": WONK, "wght": wght},
        inplace=True,
    )
    return font


def build_one(vf_path, roman_path, out_path, wght, weight_name):
    font = instance_italic(vf_path, wght)
    scale_glyf(font, SX, SY)
    scale_layout(font, SX, SY)
    roman = TTFont(roman_path)
    grafted = graft_marks(font, roman)
    roman.close()

    slant = -math.tan(math.radians(font["post"].italicAngle or -16.0))
    desc_y = float(TYPO_DESC)
    js = resolve_j_names(font)
    done = [n for n in js if straighten_italic_glyph(font, n, desc_y, slant)]

    ps = apply_italic_names(font, weight_name, wght)
    apply_stat(font, wght, italic=True)
    font.save(out_path)
    font.close()
    return ps, done, grafted


def bump_roman_version(family_dir):
    """Whole-family version bump: nameID 5 + head.fontRevision → 1.400."""
    for fn in sorted(os.listdir(family_dir)):
        if not fn.endswith(".ttf") or "Italic" in fn:
            continue
        path = os.path.join(family_dir, fn)
        font = TTFont(path)
        set_name(font, 5, f"Version {VERSION}")
        font["head"].fontRevision = round(float(VERSION), 3)
        apply_stat(font, font["OS/2"].usWeightClass, italic=False)
        font.save(path)
        font.close()
        print(f"  bumped {fn} → {VERSION}")


def main(vf_path, family_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for wght, weight_name in WEIGHTS:
        roman_fn = f"NumenTitle-{weight_name}.ttf"
        roman_path = os.path.join(family_dir, roman_fn)
        # Regular italic is the RIBBI name Family-Italic.ttf (not RegularItalic).
        out_fn = (
            "NumenTitle-Italic.ttf"
            if weight_name == "Regular"
            else f"NumenTitle-{weight_name}Italic.ttf"
        )
        out_path = os.path.join(out_dir, out_fn)
        ps, done, grafted = build_one(vf_path, roman_path, out_path, wght, weight_name)
        print(f"{out_fn}: ps={ps} j={done} grafted={grafted}")
    bump_roman_version(family_dir)


if __name__ == "__main__":
    # Re-insert path before the late import above is the wrong order —
    # straighten_numen_j is imported at top. Ensure tools/ is on path first.
    main(sys.argv[1], sys.argv[2], sys.argv[3])
