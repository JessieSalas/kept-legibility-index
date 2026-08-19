#!/usr/bin/env python3
"""
Geometric studies for a capital O that does not read as a zero.

These are NOT finished letterforms. They are hypotheses in outline form, built
so they can be measured: joints, optical correction and fitting are craft this
does not attempt. The point is to find out which skeleton the reader actually
separates from a zero, so the drawing that follows is aimed somewhere.

Every variant is pinned to Kept Sans' own O metrics -- same advance, same
bounding box, same side and top stem weight -- so the only thing under test is
the shape of the skeleton, not colour or spacing.

Kept Sans O:  684 x 724, counter 514 x 570, side stem 85, top stem 77
Kept Sans 0:  549 x 724, counter 383 x 572   (the O is already 1.25x wider,
                                              and they confuse anyway)

Usage: draw_O.py <kept-sans-regular.ttf> <out-dir>
"""
import math
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

# Kept Sans' O, measured.
X0, X1 = 54.0, 738.0
Y0, Y1 = -12.0, 712.0
SIDE_STEM = 85.0
TOP_STEM = 77.0
ADVANCE = 792
TARGET_INK = 162649.0   # Kept Sans' own O, so every variant carries the same colour

N = 96          # sample density; chord error on a 684-unit shape is under 0.2u


def superellipse(cx, cy, rx, ry, n, rot=0.0, samples=N):
    """|x/rx|^n + |y/ry|^n = 1, sampled. n=2 is an ellipse, larger is squarer."""
    pts = []
    for i in range(samples):
        t = 2 * math.pi * i / samples
        ct, st = math.cos(t), math.sin(t)
        # signed power keeps the four quadrants correct
        x = rx * math.copysign(abs(ct) ** (2.0 / n), ct)
        y = ry * math.copysign(abs(st) ** (2.0 / n), st)
        if rot:
            c, s = math.cos(rot), math.sin(rot)
            x, y = x * c - y * s, x * s + y * c
        pts.append((cx + x, cy + y))
    return pts


def ring(outer, inner):
    """A closed ring: outer counter-clockwise, inner clockwise."""
    return [outer, list(reversed(inner))]


def emit(pen, contours):
    for c in contours:
        pen.moveTo(c[0])
        for p in c[1:]:
            pen.lineTo(p)
        pen.closePath()


CX = (X0 + X1) / 2.0
CY = (Y0 + Y1) / 2.0
RX = (X1 - X0) / 2.0
RY = (Y1 - Y0) / 2.0


def variant_A_squircle():
    """Squarer outer and counter. The whole skeleton stops being an oval."""
    o = superellipse(CX, CY, RX, RY, 3.2)
    i = superellipse(CX, CY, RX - SIDE_STEM, RY - TOP_STEM, 3.2)
    return ring(o, i)


def variant_B_very_square():
    """Pushed further: close to a rounded rectangle."""
    o = superellipse(CX, CY, RX, RY, 5.0)
    i = superellipse(CX, CY, RX - SIDE_STEM, RY - TOP_STEM, 5.0)
    return ring(o, i)


def variant_C_square_counter():
    """Round outside, squared counter. Separates on the inner shape alone."""
    o = superellipse(CX, CY, RX, RY, 2.0)
    i = superellipse(CX, CY, RX - SIDE_STEM, RY - TOP_STEM, 4.5)
    return ring(o, i)


def variant_D_angled_stress():
    """Humanist move: thin points on a diagonal axis rather than top and bottom."""
    rot = math.radians(-22)
    o = superellipse(CX, CY, RX, RY, 2.0)
    i = superellipse(CX, CY, RX - SIDE_STEM, RY - TOP_STEM * 1.35, 2.0, rot=rot)
    return ring(o, i)


def variant_E_flat_sided():
    """Vertical flats left and right, so the silhouette carries two straight edges."""
    o = superellipse(CX, CY, RX, RY, 2.0)
    i = superellipse(CX, CY, RX - SIDE_STEM, RY - TOP_STEM, 2.0)
    flat = 0.42                      # fraction of height held straight
    for c in (o, i):
        rx = max(p[0] for p in c) - (max(p[0] for p in c) + min(p[0] for p in c)) / 2
        for k, (x, y) in enumerate(c):
            if abs(y - CY) < RY * flat:
                side = 1 if x > CX else -1
                c[k] = (CX + side * rx, y)
    return ring(o, i)


def variant_F_square_out_round_in():
    """The inverse of C: squared outer, oval counter."""
    o = superellipse(CX, CY, RX, RY, 4.5)
    i = superellipse(CX, CY, RX - SIDE_STEM, RY - TOP_STEM, 2.0)
    return ring(o, i)


VARIANTS = {
    "A-squircle": variant_A_squircle,
    "B-verysquare": variant_B_very_square,
    "C-squarecounter": variant_C_square_counter,
    "D-angledstress": variant_D_angled_stress,
    "E-flatsided": variant_E_flat_sided,
    "F-squareout": variant_F_square_out_round_in,
}


def polygon_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2.0


def ink_area(contours):
    """Outer minus counter."""
    return polygon_area(contours[0]) - polygon_area(contours[1])


def match_weight(fn, target, tol=0.0015):
    """Scale a variant's counter until its ink area matches the original O.

    Changing how square a contour is changes how much ink sits between the two,
    so an unnormalised set measures weight rather than skeleton. This solves for
    the counter scale that puts every variant at the same colour, leaving shape
    as the only variable.
    """
    lo, hi = 0.5, 1.6
    for _ in range(60):
        mid = (lo + hi) / 2.0
        outer, inner = fn()
        cx = sum(p[0] for p in inner) / len(inner)
        cy = sum(p[1] for p in inner) / len(inner)
        scaled = [(cx + (x - cx) * mid, cy + (y - cy) * mid) for x, y in inner]
        area = polygon_area(outer) - polygon_area(scaled)
        if abs(area / target - 1) < tol:
            return [outer, scaled], mid
        if area > target:            # too much ink: grow the counter
            lo = mid
        else:
            hi = mid
    return [outer, scaled], mid


def build(src_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    made = []
    for name, fn in VARIANTS.items():
        font = TTFont(src_path)
        cmap = font.getBestCmap()
        gname = cmap[ord("O")]
        pen = TTGlyphPen(None)
        contours, k = match_weight(fn, TARGET_INK)
        emit(pen, contours)
        glyf = font["glyf"]
        glyf[gname] = pen.glyph()
        glyf[gname].recalcBounds(glyf)
        font["hmtx"][gname] = (ADVANCE, glyf[gname].xMin)
        # Any composite over O (Ograve, Oacute, ...) follows automatically.
        out = os.path.join(out_dir, f"KeptSans-O-{name}.ttf")
        font.save(out)
        font.close()
        made.append((name, out))
        print(f"  {name:<18} counter x{k:.4f} -> {os.path.basename(out)}")
    return made


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
