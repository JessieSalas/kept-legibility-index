"""v2 core functions, byte-for-byte from bench.py v2 (rendering, degradation,
scoring). Imported by bench_v3.py so the treatments stay identical."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import Line, PAPER, INK
from PIL import Image, ImageFilter

def render_lines(path, index, wght, lines, size, width, pad=16):
    lh = int(size * 1.7)
    img = Image.new('RGBA', (width, lh * len(lines) + 2 * pad + int(size)), PAPER)
    for i, text in enumerate(lines):
        line = Line(path, text, size, wght, None, index)
        line.paint(img, pad, pad + int(size * 1.25) + i * lh, INK)
    return img.convert('RGB')


def chunk_words(items, per_line):
    return [' '.join(items[i:i + per_line]) for i in range(0, len(items), per_line)]


def degrade(img, blur=0.0, downscale=1.0, tilt=0.0, invert=False, noise_bg=False):
    if invert:
        from PIL import ImageOps
        img = ImageOps.invert(img)
    if noise_bg:
        import random
        rnd = random.Random(7)
        bg = Image.new('RGB', img.size)
        px = bg.load()
        w, h = img.size
        for y in range(h):
            for x in range(0, w, 4):
                v = 150 + int(70 * math.sin(x / 37.0) * math.cos(y / 23.0)) + rnd.randint(-25, 25)
                for dx in range(4):
                    if x + dx < w:
                        px[x + dx, y] = (v, v - 10, v - 30)
        mask = img.convert('L').point(lambda v: 255 - v)
        bg.paste((25, 35, 55), (0, 0), mask)
        img = bg
    if tilt:
        w, h = img.size
        sh = int(h * tilt)
        coeffs = _persp((w, h), [(0, 0), (w, sh // 2), (w, h - sh // 2), (0, h)])
        img = img.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=(250, 251, 246))
    if downscale != 1.0:
        w, h = img.size
        img = img.resize((max(1, int(w * downscale)), max(1, int(h * downscale))), Image.LANCZOS)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    return img


def _persp(size, quad):
    import numpy as np
    w, h = size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    A = []
    for (x, y), (X, Y) in zip(quad, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y])
        A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
    B = []
    for (X, Y) in src:
        B += [X, Y]
    import numpy.linalg as la
    res = la.lstsq(np.array(A, dtype=float), np.array(B, dtype=float), rcond=None)[0]
    return list(res)




def levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def accuracy(gt, ocr):
    gt_n = ' '.join(gt.split())
    ocr_n = ' '.join((ocr or '').split())
    if not gt_n:
        return 0.0
    return max(0.0, 1.0 - levenshtein(gt_n, ocr_n) / len(gt_n))


