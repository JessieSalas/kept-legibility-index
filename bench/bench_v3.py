"""Kept Readability Index · protocol v3.

Changes from v2, all pre-registered here before the official run:
- 8 repetitions per cell (was 3); per-rep raw scores are published.
- Corpus: 40 lowercase words + 8 capitalized tokens shuffled together
  (48 tokens per body image), 12 alphanumeric codes (was 20 words / 7 codes).
- A size-threshold sweep: clean body text at 6..16 px; the reported
  "legible down to" figure is the smallest size whose character accuracy
  meets or exceeds 90%.
- Condition renames for honesty (treatments unchanged): tilt-45 -> keystone,
  dark -> inverted. The degradation code is byte-identical to v2's.
- Statistics: per-cell mean and SD across reps; by-items bootstrap CI on the
  grand mean; ranks are reported in bands, differences inside a band are ties.

The reader, scoring, rendering, and degradation functions are v2's, unchanged.
"""
import json, math, os, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render import Line, PAPER, INK  # noqa: E402
from PIL import Image  # noqa: E402

# --- v2 machinery, imported unchanged ---------------------------------------
from bench_v2_core import degrade, render_lines, chunk_words, accuracy  # noqa: E402

OCR = os.environ.get('VISIONOCR', os.path.join(os.path.dirname(HERE), 'ocr', 'visionocr'))
OUT = os.path.join(HERE, 'img-v3')
os.makedirs(OUT, exist_ok=True)

WORDS_A = ("modern kernel million graduate keyboard obvious clean particular "
           "illusion parallel calendar morning franchise deliberate quiet exact "
           "unkempt afford bubble hyphen").split()
WORDS_B = ("quickly hijack buoyant mirror grammar pillow official civil vivid "
           "banana unique council flying graph jigsaw kingdom lullaby minimum "
           "opinion puzzle").split()
CAPS = "Illinois Zurich Dublin ILLINOIS OQGDC Madrid Quebec BENCHMARK".split()
TOKENS = WORDS_A + WORDS_B + CAPS  # 48 tokens per body image
CODES = ["K3PT-011l", "X4O0-Q8B5", "S52Z-Il1J", "rn-m-nn", "0O8B", "I1l|", "G6C",
         "8B5S-2Z0O", "L1I7-G6C0", "M3rn-NN11", "Q0OD-C6G8", "17Il-l1I7"]

CONDS = [
    ('body-9px',       'words', 9,  {}),
    ('body-12px',      'words', 12, {}),
    ('body-9px-blur',  'words', 9,  {'blur': 0.6}),
    ('body-12px-blur', 'words', 12, {'blur': 1.0}),
    ('glance',         'words', 26, {'downscale': 0.42, 'blur': 0.3}),
    ('keystone',       'words', 14, {'tilt': 0.45}),
    ('inverted',       'words', 12, {'invert': True}),
    ('passthrough',    'words', 13, {'noise_bg': True, 'blur': 0.5}),
    ('codes-11px',     'codes', 11, {}),
    ('codes-glance',   'codes', 24, {'downscale': 0.42, 'blur': 0.3}),
]
REPS = 8
THRESHOLD_SIZES = [6, 7, 8, 9, 10, 11, 12, 14, 16]
THRESHOLD_CRITERION = 0.90


def run(fonts, out_name='results-v3.json'):
    manifest = []
    for label, path, idx, wght in fonts:
        safe = label.replace(' ', '_')
        for cond, textset, size, kw in CONDS:
            items = TOKENS if textset == 'words' else CODES
            per_line = 5 if textset == 'words' else 3
            for rep in range(REPS):
                rnd = random.Random(rep * 31 + 7)
                order = items[:]
                rnd.shuffle(order)
                img = render_lines(path, idx, wght, chunk_words(order, per_line), size,
                                   width=780 if textset == 'words' else 560)
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

    raw = {}
    for p, label, cond, size, gt in manifest:
        raw.setdefault(label, {}).setdefault(cond, []).append(accuracy(gt, ocr_out.get(p, '')))

    results = {}
    for label, conds in raw.items():
        cells = {}
        for cond, vals in conds.items():
            m = sum(vals) / len(vals)
            sd = math.sqrt(sum((x - m) ** 2 for x in vals) / max(1, len(vals) - 1))
            cells[cond] = {'mean': round(m, 4), 'sd': round(sd, 4), 'reps': [round(v, 4) for v in vals]}
        main_cells = [cells[c[0]]['mean'] for c in CONDS]
        grand = sum(main_cells) / len(main_cells)
        # legible-down-to: smallest sweep size meeting the criterion
        legible_at = None
        for size in THRESHOLD_SIZES:
            if cells.get(f'thresh-{size}', {}).get('mean', 0) >= THRESHOLD_CRITERION:
                legible_at = size
                break
        results[label] = {'grand_mean': round(grand, 4), 'legible_down_to_px': legible_at,
                          'cells': cells}

    out = {'protocol': 'v3', 'reps': REPS, 'criterion': THRESHOLD_CRITERION,
           'conditions': [c[0] for c in CONDS], 'threshold_sizes': THRESHOLD_SIZES,
           'tokens': TOKENS, 'codes': CODES, 'results': results}
    with open(os.path.join(HERE, out_name), 'w') as f:
        json.dump(out, f, indent=1)
    print(f"{'font':24s} {'grand':>7s} {'±sd':>5s} {'legible@':>9s}")
    rows = []
    for label, r in results.items():
        sds = [r['cells'][c[0]]['sd'] for c in CONDS]
        rows.append((r['grand_mean'], label, sum(sds) / len(sds), r['legible_down_to_px']))
    for m, label, sd, la in sorted(rows, reverse=True):
        print(f"{label:24s} {m*100:6.1f}% {sd*100:4.1f} {str(la)+'px':>9s}")
    return out
