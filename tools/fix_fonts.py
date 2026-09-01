#!/usr/bin/env python3
"""
Fix the Google Fonts QA failures in the three Kept families.

Every fix below is traceable to a specific FontBakery googlefonts-profile check
that currently FAILs. Nothing here changes an outline that the designer drew;
the only glyph added is a combining ring (U+030A), which Numen Title needs for
Czech/Danish/Finnish/Norwegian/Swedish to shape at all.

Usage: fix_fonts.py <src-root> <dst-root>
"""
import os, sys, shutil
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

GF_LICENSE_TEXT = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org"
)
GF_LICENSE_URL = "https://openfontlicense.org"
REPO = "https://github.com/JessieSalas/kept-legibility-index"

# family -> (copyright line, extra attribution lines kept below it in OFL.txt)
FAMILIES = {
    "KeptSans": {
        "name": "Kept Sans",
        "year": "2026",
        "attrib": [
            "Kept Sans is a derivative of Figtree, Copyright 2022 The Figtree Project",
            "Authors (https://github.com/erikdkennedy/figtree). The K, k and ampersand are",
            "from Albert Sans, Copyright 2021 The Albert Sans Project Authors",
            "(https://github.com/googlefonts/albert-sans).",
        ],
        "version": "2.100",
    },
    "LegibilitySans": {
        "name": "Legibility Sans",
        "year": "2026",
        "attrib": [
            "Legibility Sans is a derivative of Atkinson Hyperlegible Next, Copyright",
            "2020-2024 The Atkinson Hyperlegible Next Project Authors",
            "(https://github.com/googlefonts/atkinson-hyperlegible-next).",
            "Atkinson Hyperlegible is a trademark of the Braille Institute of America, Inc.",
            "Legibility Sans is an independent derivative and is not endorsed by, or",
            "affiliated with, the Braille Institute of America.",
        ],
        "version": "2.100",
    },
    "NumenTitle": {
        "name": "Numen Title",
        "year": "2026",
        "attrib": [
            "Numen Title is a derivative of Fraunces, Copyright 2020 The Fraunces Project",
            "Authors (https://github.com/undercasetype/Fraunces).",
        ],
        "version": "1.400",
    },
}


def set_name(font, nid, value):
    """Set a name record on all (platform, encoding, language) records GF cares about."""
    font["name"].setName(value, nid, 3, 1, 0x409)   # Windows / Unicode BMP / en-US
    font["name"].setName(value, nid, 1, 0, 0)       # Mac / Roman / English


def copyright_line(fam):
    return f"Copyright {FAMILIES[fam]['year']} The {FAMILIES[fam]['name']} Project Authors ({REPO})"


def family_extremes(paths):
    """GF rule: usWinAscent/Descent must be consistent family-wide and must not clip.

    The window must cover both the real ink bounds and the typo metrics, otherwise
    Windows clips ascenders/descenders that the line height already accounts for.
    """
    ymax, ymin = None, None
    for p in paths:
        f = TTFont(p)
        h, os2 = f["head"], f["OS/2"]
        hi = max(h.yMax, os2.sTypoAscender)
        lo = min(h.yMin, os2.sTypoDescender)
        ymax = hi if ymax is None else max(ymax, hi)
        ymin = lo if ymin is None else min(ymin, lo)
        f.close()
    return ymax, ymin


def add_combining_ring(font):
    """Numen Title lacks U+030A; build it by reusing the ring from Aring."""
    cmap = font.getBestCmap()
    if 0x030A in cmap:
        return False
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    glyf, hmtx, gs = font["glyf"], font["hmtx"], font.getGlyphSet()
    src = cmap.get(ord("Å")) or cmap.get(ord("å"))
    base = cmap.get(ord("A")) or cmap.get(ord("a"))
    if not src or not base:
        raise RuntimeError("no Aring/aring to harvest a ring from")

    # The ring is whatever Aring has that A does not: take contours above cap height.
    rec = DecomposingRecordingPen(gs)
    gs[src].draw(rec)
    capish = font["OS/2"].sCapHeight or font["head"].yMax * 0.7
    pen = TTGlyphPen(None)
    keep = []
    contour = []
    for op, pts in rec.value:
        contour.append((op, pts))
        if op == "closePath":
            ys = [q[1] for o, P in contour if P for q in P if q]
            if ys and min(ys) >= capish * 0.95:
                keep.append(list(contour))
            contour = []
    if not keep:
        raise RuntimeError("could not isolate the ring contour")

    # Re-emit the ring, shifted so it sits as a zero-width combining mark.
    xs = [q[0] for c in keep for o, P in c if P for q in P if q]
    shift = -(min(xs) + max(xs)) / 2.0
    for c in keep:
        for op, pts in c:
            if op == "moveTo":
                pen.moveTo((pts[0][0] + shift, pts[0][1]))
            elif op == "lineTo":
                pen.lineTo((pts[0][0] + shift, pts[0][1]))
            elif op == "qCurveTo":
                pen.qCurveTo(*[(p[0] + shift, p[1]) if p else None for p in pts])
            elif op == "curveTo":
                pen.curveTo(*[(p[0] + shift, p[1]) for p in pts])
            elif op == "closePath":
                pen.closePath()

    name = "uni030A"
    glyf[name] = pen.glyph()
    glyf[name].recalcBounds(glyf)
    hmtx[name] = (0, glyf[name].xMin if glyf[name].numberOfContours else 0)
    # glyf.__setitem__ already appended `name` to the shared glyph order; just
    # make sure the font object and maxp agree with it.
    font.setGlyphOrder(glyf.glyphOrder)
    font["maxp"].numGlyphs = len(glyf.glyphOrder)
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap[0x030A] = name
    # Mark it as a nonspacing mark in GDEF so shapers attach it correctly.
    if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
        font["GDEF"].table.GlyphClassDef.classDefs[name] = 3
    return True


def fix_family(fam, srcdir, dstdir):
    os.makedirs(dstdir, exist_ok=True)
    ttfs = sorted(f for f in os.listdir(srcdir) if f.endswith(".ttf"))
    paths = [os.path.join(srcdir, f) for f in ttfs]
    ymax, ymin = family_extremes(paths)
    cline = copyright_line(fam)
    ver = FAMILIES[fam]["version"]
    changes = []

    # Underline metrics must agree family-wide; take the most common pair.
    from collections import Counter
    ul = Counter()
    for p in paths:
        f = TTFont(p); ul[(f["post"].underlineThickness, f["post"].underlinePosition)] += 1; f.close()
    ul_thick, ul_pos = ul.most_common(1)[0][0]

    for fn in ttfs:
        font = TTFont(os.path.join(srcdir, fn))

        # --- googlefonts/font_copyright + googlefonts/name/license ---
        set_name(font, 0, cline)
        set_name(font, 13, GF_LICENSE_TEXT)
        set_name(font, 14, GF_LICENSE_URL)

        # --- opentype/font_version: head.fontRevision must equal nameID 5 ---
        font["head"].fontRevision = round(float(ver), 3)
        set_name(font, 5, f"Version {ver}")

        # --- family/vertical_metrics + family/win_ascent_and_descent ---
        os2, hhea = font["OS/2"], font["hhea"]
        os2.usWinAscent = ymax
        os2.usWinDescent = abs(ymin)
        hhea.ascent = os2.sTypoAscender
        hhea.descent = os2.sTypoDescender
        hhea.lineGap = os2.sTypoLineGap
        os2.fsSelection |= 1 << 7          # USE_TYPO_METRICS

        # --- opentype/family/underline_thickness ---
        font["post"].underlineThickness = ul_thick
        font["post"].underlinePosition = ul_pos

        # --- googlefonts/glyph_coverage: U+030A for Nordic + Czech ---
        if add_combining_ring(font):
            changes.append(f"{fn}: added U+030A")

        out = os.path.join(dstdir, fn)
        font.save(out)
        font.close()

    return changes, (ymax, ymin), (ul_thick, ul_pos)


CANONICAL_OFL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OFL-canonical.txt.body")


def write_ofl(fam, dstdir, template_path):
    # Use google/fonts' own OFL body verbatim so the licence text is byte-identical
    # to every other family in the library.
    with open(CANONICAL_OFL, encoding="utf-8") as fh:
        tail = fh.read()
    header = copyright_line(fam) + "\n\n" + "\n".join(FAMILIES[fam]["attrib"]) + "\n\n"
    with open(os.path.join(dstdir, "OFL.txt"), "w", encoding="utf-8") as fh:
        fh.write(header + tail)


if __name__ == "__main__":
    src_root, dst_root = sys.argv[1], sys.argv[2]
    for fam in FAMILIES:
        s, d = os.path.join(src_root, fam), os.path.join(dst_root, fam)
        ch, vm, ul = fix_family(fam, s, d)
        write_ofl(fam, d, os.path.join(s, "OFL.txt"))
        print(f"{fam}: winAsc/Desc={vm[0]}/{abs(vm[1])} underline={ul} {'; '.join(ch) or ''}")
