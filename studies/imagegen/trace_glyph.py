#!/usr/bin/env python3
"""
Trace a black-on-white glyph image into contours, and report what tracing costs.

This exists to answer one question empirically: can an image-generated letterform be
turned into a usable font outline? It traces the bitmap, simplifies at a range of
tolerances, and reports point counts so the quality gap is a number, not an opinion.

An `O` is topologically simple -- one ink blob with one hole -- so rather than a general
contour finder this takes the direct route: Moore-neighbour trace of the ink boundary for
the outer, and flood-fill from the frame to isolate the counter for the inner.

Usage: trace_glyph.py <image.png> [--rdp 1.5]
"""
import argparse
import math
from collections import deque

from PIL import Image


def load_mask(path, thresh=128):
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    return [[1 if px[x, y] < thresh else 0 for x in range(w)] for y in range(h)], w, h


NEIGH = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def moore_trace(mask, w, h, target=1):
    """Trace the boundary of the first `target` region found, scanning top-down."""
    def get(x, y):
        return mask[y][x] if 0 <= x < w and 0 <= y < h else 0

    start = None
    for y in range(h):
        for x in range(w):
            if get(x, y) == target:
                start = (x, y)
                break
        if start:
            break
    if not start:
        return []

    contour = [start]
    cur = start
    backtrack = (-1, 0)
    for _ in range(8 * w * h):
        bi = NEIGH.index(backtrack) if backtrack in NEIGH else 0
        found = None
        for k in range(8):
            d = NEIGH[(bi + 1 + k) % 8]
            nx, ny = cur[0] + d[0], cur[1] + d[1]
            if get(nx, ny) == target:
                found = (nx, ny)
                backtrack = (-d[0], -d[1])
                break
        if not found:
            break
        cur = found
        if cur == start and len(contour) > 2:
            break
        contour.append(cur)
    return contour


def counter_mask(mask, w, h):
    """Background not reachable from the frame == the enclosed counter."""
    out = [[0] * w for _ in range(h)]
    seen = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if mask[y][x] == 0 and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if mask[y][x] == 0 and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and mask[ny][nx] == 0:
                seen[ny][nx] = True
                q.append((nx, ny))
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y][x] == 0 and not seen[y][x]:
                out[y][x] = 1
                n += 1
    return out, n


def rdp(points, eps):
    if len(points) < 3:
        return points

    def seg_dist(p, a, b):
        ax, ay = a
        bx, by = b
        px, py = p
        dx, dy = bx - ax, by - ay
        if dx == dy == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        worst, wi = 0.0, i
        for k in range(i + 1, j):
            d = seg_dist(points[k], points[i], points[j])
            if d > worst:
                worst, wi = d, k
        if worst > eps:
            keep[wi] = True
            stack.append((i, wi))
            stack.append((wi, j))
    return [p for p, k in zip(points, keep) if k]


def area(pts):
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def trace(path, eps=1.5):
    mask, w, h = load_mask(path)
    outer = moore_trace(mask, w, h, 1)
    cmask, cn = counter_mask(mask, w, h)
    inner = moore_trace(cmask, w, h, 1) if cn else []
    return outer, inner, (w, h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--rdp", type=float, default=1.5)
    args = ap.parse_args()
    outer, inner, (w, h) = trace(args.image)
    name = args.image.split("/")[-1]
    print(f"  {name}  ({w}x{h})")
    for label, c in (("outer", outer), ("counter", inner)):
        if not c:
            print(f"     {label:<8} NOT FOUND")
            continue
        row = f"     {label:<8} {len(c):>6} raw"
        for e in (0.5, 1.0, 2.0, 4.0):
            row += f"   RDP{e}: {len(rdp(c, e)):>4}"
        row += f"   area {abs(area(c)):>11.0f}"
        print(row)


if __name__ == "__main__":
    main()
