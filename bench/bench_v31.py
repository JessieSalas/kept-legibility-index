"""Kept Legibility Index · protocol v3.1.

The first-principles frame. Reading has four mechanical preconditions, and the
battery now measures each directly:

1. IDENTIFICATION  — can the letter be recognized at all at a given angular
   size. The size sweep. A small nominal size is not "reading 8px text all
   day": it is the physical model of distance and eccentricity. 16px viewed
   from twice as far lands on the retina exactly as 8px does from here.
2. SEPARATION      — crowding. Letters interfere with their neighbors; in
   normal reading this, not acuity, is usually the binding limit. New
   condition: body text with tightened tracking and leading.
3. DISCRIMINATION  — confusability. I/l/1, O/0, 8/B, rn/m. The codes cells,
   plus a new empirical confusion matrix accumulated from the reader's actual
   substitution errors.
4. OPTICAL ROBUSTNESS — the transfer function of real viewing: blur (focus,
   motion, cheap panels), contrast loss (sunlight, dimming, gray-on-white
   styling), polarity, geometry, background clutter.

Changes from v3: two new conditions (crowded, low-contrast), raw reader output
retained for confusion analysis, comparables panel expanded. Bear Sans rows move to
the archive: they are another product's embedded binaries, locally resolved
and not licensable by a reader, so third parties cannot reproduce those rows.
System fonts (Verdana, Georgia, Comic Sans MS) stay: they resolve on any Mac. Rendering, scoring,
seeds, and all ten v3 conditions are unchanged.
"""
import json, math, os, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render import Line, PAPER, INK  # noqa: E402
from PIL import Image  # noqa: E402
from bench_v2_core import degrade, render_lines, chunk_words, accuracy  # noqa: E402
from bench_v3 import (TOKENS, CODES, CONDS as V3_CONDS, REPS,  # noqa: E402
                      THRESHOLD_SIZES, THRESHOLD_CRITERION)

OCR = os.environ.get('VISIONOCR', os.path.join(os.path.dirname(HERE), 'ocr', 'visionocr'))
OUT = os.path.join(HERE, 'img-v31')
os.makedirs(OUT, exist_ok=True)

MUTED_INK = (138, 146, 160, 255)   # ~3.1:1 on the warm paper: gray-on-white UI text

def render_crowded(path, idx, wght, lines, size, width, pad=16):
    """Tight setting: leading 1.15x (vs 1.7x), tracking -0.01em."""
    lh = int(size * 1.15)
    img = Image.new('RGBA', (width, lh * len(lines) + 2 * pad + int(size)), PAPER)
    for i, text in enumerate(lines):
        line = Line(path, text, size, wght, None, idx, letterspace=-0.01)
        line.paint(img, pad, pad + int(size * 1.25) + i * lh, INK)
    return img.convert('RGB')

def render_lowcontrast(path, idx, wght, lines, size, width, pad=16):
    lh = int(size * 1.7)
    img = Image.new('RGBA', (width, lh * len(lines) + 2 * pad + int(size)), PAPER)
    for i, text in enumerate(lines):
        line = Line(path, text, size, wght, None, idx)
        line.paint(img, pad, pad + int(size * 1.25) + i * lh, MUTED_INK)
    return img.convert('RGB')

# (name, textset, size, kwargs, custom_renderer)
CONDS = [c + (None,) for c in V3_CONDS] + [
    ('crowded', 'words', 11, {}, render_crowded),
    ('low-contrast', 'words', 12, {}, render_lowcontrast),
]

def run(fonts, out_name='results-v31.json', keep_raw=True):
    manifest = []
    for label, path, idx, wght in fonts:
        safe = label.replace(' ', '_')
        for cond, textset, size, kw, custom in CONDS:
            items = TOKENS if textset == 'words' else CODES
            per_line = 5 if textset == 'words' else 3
            for rep in range(REPS):
                rnd = random.Random(rep * 31 + 7)
                order = items[:]
                rnd.shuffle(order)
                lines = chunk_words(order, per_line)
                w = 780 if textset == 'words' else 560
                if custom is not None:
                    img = custom(path, idx, wght, lines, size, width=w)
                else:
                    img = render_lines(path, idx, wght, lines, size, width=w)
                    img = degrade(img, **kw)
                p = os.path.join(OUT, f"{safe}__{cond}__r{rep}.png")
                img.save(p)
                manifest.append((p, label, cond, None, ' '.join(order)))
        for size in THRESHOLD_SIZES:
            for rep in range(REPS):
                rnd = random.Random(rep * 31 + 7)
                order = TOKENS[:]
                rnd.shuffle(order)
                img = render_lines(path, idx, wght, chunk_words(order, 5), size, width=780)
                p = os.path.join(OUT, f"{safe}__thresh{size}__r{rep}.png")
                img.save(p)
                manifest.append((p, label, f'thresh-{size}', size, ' '.join(order)))

    ocr_out = {}
    for i in range(0, len(manifest), 40):
        chunk = manifest[i:i + 40]
        proc = subprocess.run([OCR] + [m[0] for m in chunk], capture_output=True, text=True)
        for ln in proc.stdout.splitlines():
            parts = ln.split('\t')
            if len(parts) >= 2:
                ocr_out[parts[0]] = parts[1]

    raw, texts = {}, {}
    for p, label, cond, size, gt in manifest:
        o = ocr_out.get(p, '')
        raw.setdefault(label, {}).setdefault(cond, []).append(accuracy(gt, o))
        if keep_raw and not cond.startswith('thresh'):
            texts.setdefault(label, {}).setdefault(cond, []).append({'gt': gt, 'ocr': o})

    results = {}
    cond_names = [c[0] for c in CONDS]
    for label, conds in raw.items():
        cells = {}
        for cond, vals in conds.items():
            m = sum(vals) / len(vals)
            sd = math.sqrt(sum((x - m) ** 2 for x in vals) / max(1, len(vals) - 1))
            cells[cond] = {'mean': round(m, 4), 'sd': round(sd, 4),
                           'reps': [round(v, 4) for v in vals]}
        grand = sum(cells[c]['mean'] for c in cond_names) / len(cond_names)
        legible_at = None
        for size in THRESHOLD_SIZES:
            if cells.get(f'thresh-{size}', {}).get('mean', 0) >= THRESHOLD_CRITERION:
                legible_at = size
                break
        results[label] = {'grand_mean': round(grand, 4),
                          'legible_down_to_px': legible_at, 'cells': cells}

    out = {'protocol': 'v3.1', 'reps': REPS, 'criterion': THRESHOLD_CRITERION,
           'conditions': cond_names, 'threshold_sizes': THRESHOLD_SIZES,
           'tokens': TOKENS, 'codes': CODES, 'results': results,
           'raw_reader_output': texts if keep_raw else None}
    with open(os.path.join(HERE, out_name), 'w') as f:
        json.dump(out, f, indent=1)
    print(f"{'font':24s} {'grand':>7s} {'crowd':>6s} {'locon':>6s} {'legible@':>9s}")
    rows = []
    for label, r in results.items():
        rows.append((r['grand_mean'], label, r['cells']['crowded']['mean'],
                     r['cells']['low-contrast']['mean'], r['legible_down_to_px']))
    for m, label, cr, lc, la in sorted(rows, reverse=True):
        print(f"{label:24s} {m*100:6.1f}% {cr*100:5.1f} {lc*100:5.1f} {str(la)+'px':>9s}")
    return out
