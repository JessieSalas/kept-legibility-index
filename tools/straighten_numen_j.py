#!/usr/bin/env python3
"""
Replace the hooked Numen Title j descender with a straight stem.

Fraunces' j (and every composite that carries the same tail) ends in a
leftward swash. The 1.302 60% compression still left a hook. This pass
keeps the tittle and every point on or above the baseline, and rebuilds
the below-baseline run as a vertical stem that continues to the family's
typo descender and finishes in a small flat, slightly rounded terminal.

Targets: j, jcircumflex, jacute, ij, ijacute, lj, nj, Lj, Nj, dotlessj.
Those are the same hooked-j outline, not other letters. f/g/y/Q/J are
audited and left alone.

Usage: straighten_numen_j.py <family-dir>
"""
from __future__ import annotations

import os
import sys
import glob

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

# Same letterform as `j`. Not f/g/y/Q/J.
J_FAMILY = (
    "j",
    "jcircumflex",
    "jacute",
    "ij",
    "ijacute",
    "lj",
    "nj",
    "Lj",
    "Nj",
    "dotlessj",
)

# Anything deeper than this is a real descender hook, not overshoot.
HOOK_Y = -80
# Keep the stem on and above the baseline untouched.
BASELINE = 0.0


def recording(font, name):
    gs = font.getGlyphSet()
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    return list(pen.value)


def pts_of(cmd):
    op, P = cmd
    if not P:
        return []
    return [p for p in P if p is not None]


def contour_commands(rec):
    """Split a recording into closed contours (list of command lists)."""
    contours, cur = [], []
    for op, P in rec:
        cur.append((op, P))
        if op == "closePath":
            contours.append(cur)
            cur = []
    if cur:
        contours.append(cur)
    return contours


def contour_ymin(cmds):
    ys = [p[1] for c in cmds for p in pts_of(c)]
    return min(ys) if ys else 0


def last_point(cmds):
    for op, P in reversed(cmds):
        pts = pts_of((op, P))
        if pts:
            return pts[-1]
    return None


def emit(pen, cmds):
    for op, P in cmds:
        if op == "moveTo":
            pen.moveTo(P[0])
        elif op == "lineTo":
            pen.lineTo(P[0])
        elif op == "qCurveTo":
            pen.qCurveTo(*P)
        elif op == "curveTo":
            pen.curveTo(*P)
        elif op == "closePath":
            pen.closePath()


def hook_slice(cmds):
    """Return (keep_prefix, hook_cmds, keep_suffix) for a hooked contour.

    Prefix is everything strictly above the baseline before the hook.
    Suffix is everything after the contour has climbed back on or above
    the baseline. The hook is the run in between.
    """
    start = None
    for i, cmd in enumerate(cmds):
        if any(p[1] < BASELINE for p in pts_of(cmd)):
            start = i
            break
    if start is None:
        return cmds, [], []

    end = start
    for i in range(start, len(cmds)):
        pts = pts_of(cmds[i])
        if pts and all(p[1] >= BASELINE for p in pts) and cmds[i][0] != "closePath":
            end = i
            break
        end = i + 1
    return cmds[:start], cmds[start:end], cmds[end:]


def stem_xs(prefix, hook, suffix):
    """Right and left stem x at the baseline cut, from the kept points.

    Prefix ends on the right stem just above the baseline. The hook's last
    on-curve point is the left-stem rejoin (also just above the baseline).
    """
    right = last_point(prefix)
    left = last_point(hook)
    if right is None or left is None:
        raise RuntimeError("could not locate stem edges")
    return right[0], left[0], right[1], left[1]


def descender_commands(x_right, y_right, x_left, y_left, desc_y):
    """Vertical stem + small flat/rounded terminal. Pen is already at (x_right, y_right)."""
    stem = abs(x_right - x_left)
    r = max(24.0, min(48.0, stem * 0.18))
    # Guard a very light stem: radius cannot exceed half the width.
    r = min(r, stem * 0.45)
    bottom = desc_y
    # Inner corners of the flat terminal.
    xr_inner = x_right - r if x_right > x_left else x_right + r
    xl_inner = x_left + r if x_right > x_left else x_left - r
    y_corner = bottom + r
    return [
        ("lineTo", ((x_right, y_corner),)),
        ("qCurveTo", ((x_right, bottom), (xr_inner, bottom))),
        ("lineTo", ((xl_inner, bottom),)),
        ("qCurveTo", ((x_left, bottom), (x_left, y_corner))),
        ("lineTo", ((x_left, y_left),)),
    ]


def straighten_contour(cmds, desc_y):
    prefix, hook, suffix = hook_slice(cmds)
    if not hook:
        return cmds, False
    x_right, x_left, y_right, y_left = stem_xs(prefix, hook, suffix)
    new_hook = descender_commands(x_right, y_right, x_left, y_left, desc_y)
    return prefix + new_hook + suffix, True


def straighten_glyph(font, name, desc_y):
    rec = recording(font, name)
    contours = contour_commands(rec)
    changed = False
    rebuilt = []
    for cmds in contours:
        if contour_ymin(cmds) < HOOK_Y:
            cmds, did = straighten_contour(cmds, desc_y)
            changed = changed or did
        rebuilt.append(cmds)

    if not changed:
        return False

    pen = TTGlyphPen(None)
    for cmds in rebuilt:
        emit(pen, cmds)
    glyf, hmtx = font["glyf"], font["hmtx"]
    adv = hmtx[name][0]
    glyf[name] = pen.glyph()
    glyf[name].recalcBounds(glyf)
    # Advance is sacred; LSB follows the new xMin so the ink does not shift.
    hmtx[name] = (adv, glyf[name].xMin)
    return True


def main(family_dir):
    desc_y = None
    paths = sorted(glob.glob(os.path.join(family_dir, "NumenTitle-*.ttf")))
    if not paths:
        raise SystemExit(f"no NumenTitle TTFs in {family_dir}")

    for path in paths:
        font = TTFont(path)
        if desc_y is None:
            desc_y = float(font["OS/2"].sTypoDescender)
        done = []
        for name in J_FAMILY:
            if name not in font.getGlyphOrder():
                continue
            if straighten_glyph(font, name, desc_y):
                done.append(name)
        font.save(path)
        font.close()
        print(f"{os.path.basename(path)}: straightened {done}  desc_y={desc_y:.0f}")


if __name__ == "__main__":
    main(sys.argv[1])
