#!/usr/bin/env python3
"""
Score a candidate face against the index, for use while drawing.

The full driver measures 24 faces and takes a long time. When you are iterating
on a letterform you want one question answered quickly: did this drawing help,
and what did it cost somewhere else? This runs the same v3.1 protocol over your
candidate plus whichever reference faces you name, then prints the per-condition
cells and, more usefully, the confusion pairs your change was aimed at.

Nothing here is a shortcut around the protocol: same corpus, same conditions,
same reader, same scoring. It is the same measurement over a smaller panel.

Examples:

    # score one candidate against the faces that currently lead the pairs you care about
    score_candidate.py --font "Draft A" path/to/Draft-A.ttf \\
                       --ref "Kept Sans" --ref "Verdana" --ref "OpenDyslexic"

    # compare two drafts head to head, no references
    score_candidate.py --font "Draft A" a.ttf --font "Draft B" b.ttf

    # focus the report on the pairs a change was meant to fix
    score_candidate.py --font "Draft A" a.ttf --ref "Kept Sans" --pairs O>0 0>O I>1
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# The Swift reader must be built once: swiftc -O -o ocr/visionocr ocr/visionocr.swift
os.environ.setdefault("VISIONOCR", os.path.join(ROOT, "ocr", "visionocr"))

import bench_v31  # noqa: E402

FONTS_DIR = os.path.join(ROOT, "fonts")
KEPT = os.path.join(FONTS_DIR, "kept-type")
SUP = "/System/Library/Fonts/Supplemental"
SYS = "/System/Library/Fonts"

# Where the reference faces live, so --ref takes a name rather than a path.
KNOWN = {
    "Kept Sans": (f"{KEPT}/KeptSans/KeptSans-Regular.ttf", 0, None),
    "Legibility Sans": (f"{KEPT}/LegibilitySans/LegibilitySans-Regular.ttf", 0, None),
    "Numen Title": (f"{KEPT}/NumenTitle/NumenTitle-Regular.ttf", 0, None),
    "Figtree": (f"{FONTS_DIR}/figtree.ttf", 0, 400),
    "Atkinson Next": (f"{FONTS_DIR}/atkinsonnext.ttf", 0, 400),
    "Inter": (f"{FONTS_DIR}/inter.ttf", 0, 400),
    "IBM Plex Sans": (f"{FONTS_DIR}/ibmplexsans.ttf", 0, 400),
    "Public Sans": (f"{FONTS_DIR}/publicsans.ttf", 0, 400),
    "Source Sans 3": (f"{FONTS_DIR}/sourcesans3.ttf", 0, 400),
    "Noto Sans": (f"{FONTS_DIR}/notosans.ttf", 0, 400),
    "Lexend": (f"{FONTS_DIR}/lexend.ttf", 0, 400),
    "Andika": (f"{FONTS_DIR}/andika.ttf", 0, None),
    "Verdana": (f"{SUP}/Verdana.ttf", 0, None),
    "Arial": (f"{SUP}/Arial.ttf", 0, None),
    "Georgia": (f"{SUP}/Georgia.ttf", 0, None),
    "Comic Sans MS": (f"{SUP}/Comic Sans MS.ttf", 0, None),
    "Times New Roman": (f"{SUP}/Times New Roman.ttf", 0, None),
    "Charter": (f"{SUP}/Charter.ttc", 0, None),
    "SF Pro": (f"{SYS}/SFNS.ttf", 0, None),
    "Helvetica Neue": (f"{SYS}/HelveticaNeue.ttc", 0, None),
    "OpenDyslexic": ("/Applications/Bear.app/Contents/Resources/OpenDyslexic-Regular.otf", 0, None),
}

# The published v3.1 numbers, so a candidate can be placed against the field
# without re-measuring 24 faces.
BASELINE = os.path.join(ROOT, "results", "v31", "results-v31-OFFICIAL.json")


def load_baseline():
    if not os.path.exists(BASELINE):
        return None
    with open(BASELINE) as fh:
        return json.load(fh)


def confusions_from_raw(raw):
    """Accumulate a confusion matrix from the reader's raw output.

    bench_v31.run keeps `gt` and `ocr` per condition per repetition but does not
    reduce them; the published matrices were built afterwards. This does the same
    reduction so a candidate run reports confusions without a second pass.

    Character-level alignment, counting only substitutions -- insertions and
    deletions are scored by the cell means and would only add noise here.

    KNOWN LIMIT, read before trusting a number here. Validated against the
    published v3.1 matrix for Kept Sans, this agrees within 2 on 9 of the top 12
    pairs (O>0, 0>O, l>t, I>l, n>m, r>t, B>8, l>|, i>I) and UNDERCOUNTS the
    I/l/1 cluster: I>1 reads 43 against a published 51, l>1 29 against 44, l>I
    11 against 18. A run like "Il1" misread as "1I1" admits several valid
    alignments and this picks one; the published reduction picks another.

    That cluster is exactly what a disambiguation face is drawn for, so: use
    these counts to compare YOUR candidates against each other, where the same
    reduction is applied to both sides and the bias cancels. Do not quote them
    against the published table, and do not publish them as index results.
    """
    from difflib import SequenceMatcher
    out = {}
    for font, conds in (raw or {}).items():
        counter = {}
        for reps in conds.values():
            for rep in reps:
                gt, ocr = rep.get("gt", ""), rep.get("ocr", "")
                if not gt or not ocr:
                    continue
                for tag, i1, i2, j1, j2 in SequenceMatcher(None, gt, ocr, autojunk=False).get_opcodes():
                    if tag != "replace":
                        continue
                    a, b = gt[i1:i2], ocr[j1:j2]
                    # Unequal spans are collapses or splits -- rn->m is the
                    # classic one. Right-align and pair the overlapping tail,
                    # which records rn->m as n>m, matching the published
                    # reduction.
                    if len(a) != len(b):
                        k = min(len(a), len(b))
                        if not k:
                            continue
                        a, b = a[-k:], b[-k:]
                    for x, y in zip(a, b):
                        if x.isspace() or y.isspace() or x == y:
                            continue
                        key = f"{x}>{y}"
                        counter[key] = counter.get(key, 0) + 1
        out[font] = counter
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", nargs=2, action="append", metavar=("NAME", "PATH"),
                    required=True, help="a candidate to score; repeatable")
    ap.add_argument("--ref", action="append", default=[],
                    help="reference face by name; repeatable")
    ap.add_argument("--wght", type=int, default=None,
                    help="pin a variable candidate to this weight")
    ap.add_argument("--pairs", nargs="*", default=None,
                    help="confusion pairs to foreground, e.g. O>0 0>O I>1")
    ap.add_argument("--out", default="results-candidate.json")
    args = ap.parse_args()

    panel = []
    for name, path in args.font:
        if not os.path.exists(path):
            sys.exit(f"candidate not found: {path}")
        panel.append((name, path, 0, args.wght))

    for name in args.ref:
        if name not in KNOWN:
            sys.exit(f"unknown reference {name!r}. known: {', '.join(sorted(KNOWN))}")
        path, idx, wght = KNOWN[name]
        if not os.path.exists(path):
            print(f"skip (not found): {name}", file=sys.stderr)
            continue
        panel.append((name, path, idx, wght))

    print(f"measuring {len(panel)} faces: {', '.join(p[0] for p in panel)}\n",
          file=sys.stderr)
    bench_v31.run(panel, out_name=args.out, keep_raw=True)

    with open(os.path.join(HERE, args.out)) as fh:
        res = json.load(fh)
    report(res, [n for n, _ in args.font], args.pairs)


def report(res, candidates, pairs):
    R = res.get("results", {})
    CM = res.get("confusion_matrices") or confusions_from_raw(res.get("raw_reader_output"))
    base = load_baseline()

    print("\n=== cells ===")
    conds = ["body-9px", "body-12px", "body-9px-blur", "glance", "crowded",
             "low-contrast", "codes-11px", "codes-glance"]
    head = f"{'face':<22}{'grand':>8}{'8px?':>6}" + "".join(f"{c[:11]:>13}" for c in conds)
    print(head)
    for name, r in R.items():
        cells = r.get("cells", {})
        mark = "*" if name in candidates else " "
        row = f"{mark}{name[:21]:<21}{r.get('grand_mean', 0):>8.4f}{str(r.get('legible_down_to_px','')):>6}"
        row += "".join(f"{cells.get(c, {}).get('mean', float('nan')):>13.4f}" for c in conds)
        print(row)

    print("\n=== confusions ===")
    watch = pairs
    if not watch:
        seen = {}
        for name in candidates:
            for p, n in CM.get(name, {}).items():
                seen[p] = seen.get(p, 0) + n
        watch = [p for p, _ in sorted(seen.items(), key=lambda kv: -kv[1])[:10]]

    fieldbest = {}
    if base:
        for p in watch:
            vals = {f: m.get(p) for f, m in base.get("confusion_matrices", {}).items()
                    if p in m}
            if vals:
                fieldbest[p] = min(vals.items(), key=lambda kv: kv[1])

    cols = list(R)
    print(f"{'pair':<9}" + "".join(f"{c[:12]:>14}" for c in cols) + "   best in v3.1 field")
    for p in watch:
        row = f"{p:<9}" + "".join(f"{CM.get(c, {}).get(p, 0):>14}" for c in cols)
        if p in fieldbest:
            f, v = fieldbest[p]
            row += f"   {f} ({v})"
        print(row)

    print("\nA difference under a point is a tie; see PROTOCOL.md §7. Confusion counts "
          "are raw over 8 reps and are noisier than the cell means -- treat a single "
          "run as a hint, not a result.")


if __name__ == "__main__":
    main()
