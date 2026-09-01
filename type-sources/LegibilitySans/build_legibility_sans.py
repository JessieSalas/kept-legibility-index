#!/usr/bin/env python3
"""
Build Legibility Sans sources from Atkinson Hyperlegible Next.

Legibility Sans has always been a parametric derivative: no glyph is redrawn.
Until now that transform only existed as an edit applied to compiled instances,
which is why the family had no sources and could not be maintained. This script
is the transform, expressed against Atkinson's own OFL Glyphs source, so the
family becomes buildable, re-weightable and fixable.

Three operations, measured off the shipped binaries:

  1. lowercase scaled x1.10 about the baseline, raising x-height against
     untouched caps. Atkinson already separates lowercase marks (`acutecomb`)
     from cap marks (`acutecomb.case`), so "lowercase" is a clean set: lowercase
     letters plus the non-.case combining marks.
  2. +20 units of tracking on every glyph (+10 per sidebearing).
  3. +52 units on i, j, l, I and 1 (+26 per side) -- extra room for the
     narrowest letters, which are also the I/l/1 confusion set.

The weight axis is remapped rather than the masters moved: the shipped statics
sit at Atkinson wght 330/430/520/600/690/790, so Legibility Sans' 300..800 map
onto those design coordinates. That keeps the design decision in `avar`, where
it belongs, instead of baking it into instance definitions.

Usage: build_legibility_sans.py <atkinson-sources-dir> <out-dir>

Italic: the same transform is applied to AtkinsonHyperlegibleNext-Italic.glyphs.
ExtraLight is dropped on italic too — LS ships Light..ExtraBold only.
"""
import os
import sys
import unicodedata

import glyphsLib
from glyphsLib.classes import GSCustomParameter

SCALE = 1.10
TRACK = 10          # per sidebearing, all glyphs
TRACK_NARROW = 26   # per sidebearing, the narrow set
# The narrow set, named by the glyph that actually carries the outline:
# i and j are composites over idotless/jdotless.
NARROW = {"idotless", "jdotless", "l", "I", "one"}

# Legibility Sans weight -> the Atkinson userspace weight it was cut from.
WEIGHT_MAP = {300: 330, 400: 430, 500: 520, 600: 600, 700: 690, 800: 790}

FAMILY = "Legibility Sans"


def is_lowercase_glyph(glyph):
    """Lowercase letters, and the lowercase (non-.case) combining marks."""
    name = glyph.name
    if "comb" in name:
        # Cap-height marks are suffixed .case; everything else rides the x-height.
        return not name.endswith(".case") and not name.startswith("_")
    uni = glyph.unicode
    if uni:
        try:
            ch = chr(int(uni, 16))
        except ValueError:
            return False
        return unicodedata.category(ch) == "Ll"
    # Unencoded lowercase workhorses that composites are built from.
    return name in {"idotless", "jdotless", "dotlessi", "dotlessj", "longs"}


def xy(pos):
    """glyphsLib hands back a Point on read and a tuple after assignment."""
    return (pos.x, pos.y) if hasattr(pos, "x") else (pos[0], pos[1])


def scale_layer(layer, s):
    for path in layer.paths:
        for node in path.nodes:
            x, y = xy(node.position)
            node.position = (x * s, y * s)
    for anchor in layer.anchors:
        x, y = xy(anchor.position)
        anchor.position = (x * s, y * s)
    layer.width = layer.width * s


def shift_layer(layer, dx):
    """Move ink right by dx and widen the advance by 2*dx: symmetric tracking."""
    for path in layer.paths:
        for node in path.nodes:
            x, y = xy(node.position)
            node.position = (x + dx, y)
    for anchor in layer.anchors:
        x, y = xy(anchor.position)
        anchor.position = (x + dx, y)
    for comp in layer.components:
        x, y = xy(comp.position)
        comp.position = (x + dx, y)
    layer.width = layer.width + 2 * dx


def anchor_at(layer, name):
    for a in layer.anchors:
        if a.name == name:
            return xy(a.position)
    return None


def realign_components(font, master_id):
    """Re-seat every mark on its base's anchor, now that bases have moved."""
    fixed = 0
    for glyph in font.glyphs:
        layer = glyph.layers[master_id]
        if not layer.components:
            continue
        base = layer.components[0]
        base_layer = font.glyphs[base.name].layers[master_id] if base.name in font.glyphs else None
        if base_layer is None:
            continue
        for comp in layer.components[1:]:
            if comp.name not in font.glyphs:
                continue
            mark_layer = font.glyphs[comp.name].layers[master_id]
            # A mark carries _top/_bottom/...; find the one its base offers.
            for mark_anchor in mark_layer.anchors:
                if not mark_anchor.name.startswith("_"):
                    continue
                base_pos = anchor_at(base_layer, mark_anchor.name[1:])
                if base_pos is None:
                    continue
                bx, by = xy(base.position)
                mx, my = xy(mark_anchor.position)
                comp.position = (bx + base_pos[0] - mx, by + base_pos[1] - my)
                fixed += 1
                break
        # A composite's advance follows its base.
        layer.width = base_layer.width
    return fixed


def remap_axis(font):
    """Point Legibility Sans' 300..800 at the Atkinson coordinates it was cut from."""
    old = None
    for p in font.customParameters:
        if p.name == "Axis Mappings":
            old = p.value
            break
    if not old:
        raise SystemExit("no Axis Mappings in source")
    wght = {int(k): float(v) for k, v in old["wght"].items()}
    stops = sorted(wght)

    def design_for(user):
        if user <= stops[0]:
            return wght[stops[0]]
        if user >= stops[-1]:
            return wght[stops[-1]]
        for a, b in zip(stops, stops[1:]):
            if a <= user <= b:
                t = (user - a) / (b - a)
                return wght[a] + t * (wght[b] - wght[a])
        return wght[stops[-1]]

    new = {str(ls): round(design_for(ahn), 2) for ls, ahn in sorted(WEIGHT_MAP.items())}
    # Bookend the mapping so every master stays inside the mapped design range.
    # Atkinson's ExtraLight and ExtraBold masters sit at 60 and 170; without
    # these, varLib silently drops them and interpolates from two masters.
    new["200"] = wght[stops[0]]
    new["900"] = wght[stops[-1]]
    new = {k: new[k] for k in sorted(new, key=int)}
    for p in font.customParameters:
        if p.name == "Axis Mappings":
            p.value = {"wght": new}
    return new


def transform_source(path, out_dir, italic=False):
    with open(path, encoding="utf-8") as fh:
        font = glyphsLib.load(fh)
    print(f"{'italic' if italic else 'roman'} from {path}")

    targets = [g for g in font.glyphs if is_lowercase_glyph(g)]
    print(f"scaling {len(targets)} lowercase glyphs by {SCALE}")

    for master in font.masters:
        mid = master.id
        for glyph in targets:
            layer = glyph.layers[mid]
            if layer.paths:                     # only scale real outlines
                scale_layer(layer, SCALE)
        # Tracking is applied only to glyphs that carry outlines. Composites
        # inherit it through their base, so shifting them too would double it.
        for glyph in font.glyphs:
            layer = glyph.layers[mid]
            if layer.paths and not layer.components:
                shift_layer(layer, TRACK_NARROW if glyph.name in NARROW else TRACK)
        # Re-seat marks last, against anchors that now carry both scale and
        # tracking, and let each composite take its base's advance.
        n = realign_components(font, mid)
        if master.xHeight:
            master.xHeight = round(master.xHeight * SCALE)
        print(f"  master {master.name:<18} re-seated {n} marks, "
              f"xHeight -> {master.xHeight}")

    mapping = remap_axis(font)
    print(f"axis mapping (Legibility Sans wght -> Atkinson design): {mapping}")

    font.familyName = FAMILY
    drop = {"ExtraLight", "ExtraLight Italic"}
    for inst in list(font.instances):
        if inst.name in drop:
            font.instances.remove(inst)         # LS ships Light..ExtraBold
    for inst in font.instances:
        inst.familyName = FAMILY

    font.customParameters.append(
        GSCustomParameter(
            "license",
            "This Font Software is licensed under the SIL Open Font License, "
            "Version 1.1. This license is available with a FAQ at: "
            "https://openfontlicense.org",
        )
    )

    out_name = "LegibilitySans-Italic.glyphs" if italic else "LegibilitySans.glyphs"
    out = os.path.join(out_dir, out_name)
    font.save(out)
    print(f"wrote {out}")


def main(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    italic = os.path.join(src_dir, "AtkinsonHyperlegibleNext-Italic.glyphs")
    roman = os.path.join(src_dir, "AtkinsonHyperlegibleNext.glyphs")
    # Roman source is already committed; italic is the new work.
    if os.path.exists(italic):
        transform_source(italic, out_dir, italic=True)
    elif os.path.exists(roman):
        transform_source(roman, out_dir, italic=False)
    else:
        raise SystemExit(f"no Atkinson sources in {src_dir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
