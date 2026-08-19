#!/usr/bin/env python3
"""
Build Kept Sans sources from Figtree.

Kept Sans is Figtree with a raised x-height, a little tracking, and five glyphs
that were genuinely redrawn. Unlike Legibility Sans it sits on Figtree's own
weight positions (300..900 map straight through), so this builds a real
variable font rather than six statics.

  1. lowercase scaled x1.0605 about the baseline, caps and figures untouched
  2. +16 units tracking on every glyph (+8 per sidebearing)
  3. five glyphs replaced outright: I and l are drawn for disambiguation
     (a crossbarred I, a tailed l); K, k and the ampersand come from Albert
     Sans, which the OFL header has always credited.

The replaced outlines are lifted from the shipped Kept Sans binaries at the two
weights that correspond to Figtree's masters -- Light (300) and Black (900) --
so they interpolate across the axis exactly as they did before.

Usage: build_kept_sans.py <figtree-sources-dir> <kept-sans-ttf-dir> <out-dir>
"""
import os
import sys
import unicodedata

import glyphsLib
from glyphsLib.classes import GSPath, GSNode
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.qu2cu import quadratic_to_curves

SCALE = 1.0605
TRACK = 8                      # per sidebearing
TRACK_NARROW = 22              # per sidebearing, the five narrowest glyphs
# "the five narrowest glyphs" from the specimen, named by the glyph that
# carries the outline: i and j are composites over idotless/jdotless.
NARROW = {"one", "I", "idotless", "jdotless", "l"}
REPLACED = ["I", "l", "K", "k", "ampersand"]

# Figtree master -> the shipped Kept Sans static cut at the same weight.
MASTER_TTF = {"Light": "KeptSans-Light.ttf", "Black": "KeptSans-Black.ttf"}

FAMILY = "Kept Sans"


def xy(pos):
    return (pos.x, pos.y) if hasattr(pos, "x") else (pos[0], pos[1])


def is_lowercase_glyph(glyph):
    """Lowercase letters and the lowercase-height combining marks."""
    name = glyph.name
    if "comb" in name or name.endswith("comb"):
        return not name.endswith(".case") and not name.startswith("_")
    uni = glyph.unicode
    if uni:
        try:
            ch = chr(int(uni, 16))
        except ValueError:
            return False
        return unicodedata.category(ch) == "Ll"
    return name in {"idotless", "jdotless", "dotlessi", "dotlessj", "longs"}


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
    for path in layer.paths:
        for node in path.nodes:
            x, y = xy(node.position)
            node.position = (x + dx, y)
    for anchor in layer.anchors:
        x, y = xy(anchor.position)
        anchor.position = (x + dx, y)
    layer.width = layer.width + 2 * dx


def anchor_at(layer, name):
    for a in layer.anchors:
        if a.name == name:
            return xy(a.position)
    return None


def realign_components(font, mid):
    fixed = 0
    for glyph in font.glyphs:
        layer = glyph.layers[mid]
        if not layer.components:
            continue
        base = layer.components[0]
        if base.name not in font.glyphs:
            continue
        base_layer = font.glyphs[base.name].layers[mid]
        for comp in layer.components[1:]:
            if comp.name not in font.glyphs:
                continue
            mark = font.glyphs[comp.name].layers[mid]
            for ma in mark.anchors:
                if not ma.name.startswith("_"):
                    continue
                bp = anchor_at(base_layer, ma.name[1:])
                if bp is None:
                    continue
                bx, by = xy(base.position)
                mx, my = xy(ma.position)
                comp.position = (bx + bp[0] - mx, by + bp[1] - my)
                fixed += 1
                break
        layer.width = base_layer.width
    return fixed


def ttf_contours(ttf, glyph_name):
    """Pull one glyph's outline out of a TTF as cubic contours."""
    gs = ttf.getGlyphSet()
    pen = DecomposingRecordingPen(gs)
    gs[glyph_name].draw(pen)
    contours, cur = [], []
    for op, P in pen.value:
        if op == "moveTo":
            cur = [("move", P[0])]
        elif op == "lineTo":
            cur.append(("line", P[0]))
        elif op == "qCurveTo":
            cur.append(("qcurve", P))
        elif op == "closePath":
            contours.append(cur)
            cur = []
    return contours


def install_outline(layer, contours):
    """Replace a layer's paths with contours taken from a compiled binary."""
    layer.paths = []
    for c in contours:
        path = GSPath()
        nodes = []
        for kind, data in c:
            if kind == "move":
                nodes.append(GSNode(data, "line"))
            elif kind == "line":
                nodes.append(GSNode(data, "line"))
            elif kind == "qcurve":
                on = data[-1]
                offs = data[:-1]
                if on is None:                 # all-offcurve contour
                    continue
                # Convert the quadratic run to cubics so the source stays cubic.
                start = xy(nodes[-1].position) if nodes else data[0]
                try:
                    curves = quadratic_to_curves([[start] + [tuple(p) for p in data if p]], 0.5)
                except Exception:
                    curves = None
                if curves:
                    for seg in curves:
                        if len(seg) == 4:
                            nodes.append(GSNode(seg[1], "offcurve"))
                            nodes.append(GSNode(seg[2], "offcurve"))
                            nodes.append(GSNode(seg[3], "curve"))
                        else:
                            nodes.append(GSNode(seg[-1], "line"))
                else:
                    for p in offs:
                        if p:
                            nodes.append(GSNode(tuple(p), "offcurve"))
                    nodes.append(GSNode(tuple(on), "curve"))
        path.nodes = nodes
        path.closed = True
        layer.paths.append(path)


def main(figtree_sources, kept_ttf_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(figtree_sources, "Figtree.glyphs")
    with open(path, encoding="utf-8") as fh:
        font = glyphsLib.load(fh)

    targets = [g for g in font.glyphs if is_lowercase_glyph(g)]
    print(f"scaling {len(targets)} lowercase glyphs by {SCALE}")

    master_ids = {m.id for m in font.masters}
    target_names = {g.name for g in targets}

    # Figtree carries intermediate ("brace") layers at {660} for a, e and s.
    # They are real interpolation sources, so they take the same treatment as
    # the masters; skipping them bends those glyphs at the middle weights.
    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.layerId in master_ids:
                continue
            if not (layer.name or "").startswith("{"):
                continue
            if glyph.name in target_names and layer.paths:
                scale_layer(layer, SCALE)
            if layer.paths and not layer.components:
                shift_layer(layer, TRACK_NARROW if glyph.name in NARROW else TRACK)

    for master in font.masters:
        mid = master.id
        for glyph in targets:
            layer = glyph.layers[mid]
            if layer.paths:
                scale_layer(layer, SCALE)
        for glyph in font.glyphs:
            layer = glyph.layers[mid]
            if layer.paths and not layer.components:
                shift_layer(layer, TRACK_NARROW if glyph.name in NARROW else TRACK)
        n = realign_components(font, mid)
        if master.xHeight:
            master.xHeight = round(master.xHeight * SCALE)

        # Swap in the five redrawn glyphs from the matching shipped weight.
        ttf_name = MASTER_TTF.get(master.name)
        swapped = []
        if ttf_name:
            ttf = TTFont(os.path.join(kept_ttf_dir, ttf_name))
            cmap = ttf.getBestCmap()
            for gname in REPLACED:
                src = {"ampersand": ord("&")}.get(gname)
                src = cmap.get(src) if src else cmap.get(ord(gname)) if len(gname) == 1 else None
                if not src or gname not in font.glyphs:
                    continue
                layer = font.glyphs[gname].layers[mid]
                install_outline(layer, ttf_contours(ttf, src))
                layer.components = []
                layer.width = ttf["hmtx"][src][0]
                swapped.append(gname)
            ttf.close()
        print(f"  master {master.name:<8} marks={n} xHeight->{master.xHeight} swapped={swapped}")

    font.familyName = FAMILY
    for inst in font.instances:
        inst.familyName = FAMILY
    out = os.path.join(out_dir, "KeptSans.glyphs")
    font.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
