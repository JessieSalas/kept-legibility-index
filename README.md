# The Kept Legibility Index

A reproducible, machine-vision legibility benchmark for typefaces, and the
harness that built three fonts with it.

Twenty typefaces are rendered into ten degraded conditions, nine-pixel
body text, blur, downscaled glances, keystone warps, inverted polarity, noisy
passthrough backgrounds, adversarial alphanumeric codes, then read back by
Apple's Vision text recognizer with language correction off, and scored by
character accuracy against ground truth. Eight shuffled repetitions per cell,
per-repetition raw data published, differences under a point are ties.

Legibility, not "readability": readability in the reading literature means the
linguistic difficulty of a text (Flesch scores); what this index measures is
whether letterforms survive degradation. The name says what it is, and every
claim is scoped in [PROTOCOL.md](PROTOCOL.md). (Earlier versions were titled
the Kept Readability Index.)

## Reproduce it

Two ways, pick your temperament:

**Run the code** (macOS, needs Xcode command line tools and Python 3.11+):

```sh
git clone https://github.com/JessieSalas/kept-legibility-index
cd kept-legibility-index
sh fonts/fetch.sh                      # open-licensed faces from google/fonts
swiftc -O -o ocr/visionocr ocr/visionocr.swift
python3 -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/python bench/run_index.py     # renders, OCRs, scores, prints the table
```

**Rebuild it from the spec.** [PROTOCOL.md](PROTOCOL.md) specifies the corpus,
conditions, seeds, scoring, and statistics precisely enough to reimplement in
any language, by hand or by handing it to your AI assistant. Independent
implementations that disagree with ours are the most valuable issue you can
file.

## Results

The current table, the per-condition cells, controls (word-level scoring,
pseudoword lexicon-break, matched x-height), and every per-repetition raw value
live in [results/](results/). The narrative version with figures:
[kept.do/most-legible-font](https://kept.do/most-legible-font).

## The fonts it built

The index was the audition for Kept's type program. Three faces came out of it,
all free under the SIL Open Font License 1.1, downloadable at
[kept.do/type](https://kept.do/type):

- **Kept Sans**, the interface face (Figtree chassis, five measured corrections)
- **Numen Title**, the headline serif (Fraunces chassis, axes pinned by data)
- **Legibility Sans**, the pure legibility play (based on Atkinson Hyperlegible
  Next by the Braille Institute, pushed to the top of the table)

## What this is not

One OCR engine, one rasterizer, Latin script, no human subjects, no crowding or
eye-movement modeling. It is an index of the mechanical preconditions of
legibility, not a human reading study. Scope every claim accordingly; we do.

## License

Code and protocol: MIT. Fonts referenced here carry their own licenses; the
fetch script downloads only open-licensed files, and nothing proprietary is
redistributed. Atkinson Hyperlegible is a trademark of the Braille Institute of
America; Legibility Sans is an independent OFL derivative and is not endorsed
by the Braille Institute. Bear Sans belongs to the Bear team; it is measured, with
admiration, from a locally installed copy only.
