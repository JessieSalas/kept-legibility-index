"""Holdout confirmation corpus. These tokens were never used during any design
iteration of Kept's faces; they exist to prove the fonts did not learn the test.
Run against final binaries only, published beside the main table."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import json, random, subprocess
from bench_v2_core import render_lines, degrade, accuracy, chunk_words

HOLDOUT_WORDS = ("velvet oxygen thimble journey crimson whisker plateau gnarled "
                 "symphony quartz dwelling fabric mosaic hollow trinket varnish "
                 "ember glacier plywood saffron").split()
HOLDOUT_CODES = ["W7V0-O0Q9", "f1lJ-iI1L", "3E8B-6GC0", "Z2S5-rnm1"]
CONDS = [
    ('body-9px', 'words', 9, {}),
    ('body-9px-blur', 'words', 9, {'blur': 0.6}),
    ('codes-11px', 'codes', 11, {}),
    ('codes-glance', 'codes', 24, {'downscale': 0.42, 'blur': 0.3}),
]
REPS = 8

def run(fonts, ocr_path, out_name='results-holdout.json'):
    OUT = os.path.join(HERE, 'img-holdout')
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for label, path, idx, wght in fonts:
        for cond, textset, size, kw in CONDS:
            items = HOLDOUT_WORDS if textset == 'words' else HOLDOUT_CODES
            per = 5 if textset == 'words' else 2
            for rep in range(REPS):
                rnd = random.Random(rep * 31 + 7)
                order = items[:]
                rnd.shuffle(order)
                img = render_lines(path, idx, wght, chunk_words(order, per), size,
                                   width=780 if textset == 'words' else 560)
                img = degrade(img, **kw)
                p = os.path.join(OUT, f"{label.replace(' ', '_')}__{cond}__r{rep}.png")
                img.save(p)
                manifest.append((p, label, cond, ' '.join(order)))
    ocr_out = {}
    for i in range(0, len(manifest), 40):
        chunk = manifest[i:i + 40]
        proc = subprocess.run([ocr_path] + [m[0] for m in chunk], capture_output=True, text=True)
        for ln in proc.stdout.splitlines():
            parts = ln.split('\t')
            if len(parts) >= 2:
                ocr_out[parts[0]] = parts[1]
    acc = {}
    for p, label, cond, gt in manifest:
        acc.setdefault(label, {}).setdefault(cond, []).append(accuracy(gt, ocr_out.get(p, '')))
    res = {l: {c: round(sum(v) / len(v), 4) for c, v in conds.items()} for l, conds in acc.items()}
    json.dump(res, open(os.path.join(HERE, out_name), 'w'), indent=1)
    for l, cs in sorted(res.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"{l:22s} " + '  '.join(f"{c}:{v*100:.1f}" for c, v in cs.items()))
    return res
