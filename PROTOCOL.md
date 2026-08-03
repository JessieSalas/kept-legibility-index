# The Kept Legibility Index · Protocol v3.1

*Formerly the Kept Readability Index; renamed because the word matters (see below).*

This document is the complete specification of the index. It is written so that
you can reproduce the measurement two ways:

1. **Run our code.** Clone this repo, `sh fonts/fetch.sh`, build the OCR tool,
   run the driver. Same images, same numbers.
2. **Rebuild it from this page alone.** Everything below is precise enough to
   reimplement in any language, or to hand to an AI assistant with the words
   "implement this." If your independent implementation disagrees with ours, we
   want to hear about it.

This index measures **legibility**, whether letterforms survive degradation,
not **readability** in the academic sense, which is about the linguistic
difficulty of a text (as in Flesch scores). The index is named accordingly.
Search phrases like "most readable font" are answered on the site with the
same distinction stated in the first breath.

---

## 0. First principles: what legibility means here

Reading has mechanical preconditions before it has psychology. A reader, human
or machine, must be able to:

1. **Identify** a letter at the angular size it lands on the retina or sensor.
2. **Separate** it from its neighbors. In normal reading, this crowding limit,
   not raw acuity, is usually what binds.
3. **Discriminate** it from its lookalikes: I from l from 1, rn from m, 0 from
   O, 8 from B.
4. **Survive the optics**: defocus and motion blur, contrast loss from
   sunlight or gray-on-white styling, inverted polarity, projection geometry,
   cluttered backgrounds.

The battery measures each precondition directly: the size sweep for
identification, a tight-set crowding condition for separation, adversarial
codes plus an empirical confusion matrix for discrimination, and the
degradation conditions for optics.

**On "nobody reads 8-pixel text all day":** correct, and not the point. Nominal
size is the physical model of viewing distance. Sixteen-pixel text read from
twice as far lands on your retina exactly as eight-pixel text does from here;
the phone across the desk, the lock screen at arm's length, the sign down the
hall. A font's small-size threshold is its distance budget, and its blur cells
are its focus budget. What this index does not model, stated once more: reading
speed, comprehension, comfort, and taste. Below the critical size, human
reading speed collapses (Legge's psychophysics); a lower threshold therefore
buys real speed headroom, but we measure the threshold, not the speed.

## 1. The reader

- Apple Vision framework, `VNRecognizeTextRequest`.
- `recognitionLevel = .accurate`
- `usesLanguageCorrection = false` — the lexicon post-pass is disabled so the
  engine reads letterforms rather than guessing vocabulary.
- `recognitionLanguages = ["en-US"]` — requested, because the corpus is
  English. Note what we measured: with correction off, Vision revision 3 can
  still emit non-Latin interpretations of a badly degraded line (we observed a
  9 px line read as Cyrillic-lookalike output). The request does not prevent it; it
  is recorded here so nobody mistakes it for a fix. Such misreads score as
  errors under the same rule for every font. (The trained recognizer also
  carries letter-sequence statistics; the pseudoword control in §6 quantifies
  what remains.)
- The tool prints its settings, the Vision request revision, and the macOS
  version to stderr on every run. Source: `ocr/visionocr.swift` (~40 lines).
- One reader is a stated limitation, not a hidden one. A second engine
  (Tesseract) is a welcome community contribution; publish the rank correlation
  if you run it.

## 2. Rendering

- Shaping: HarfBuzz with kerning and ligatures on. Rasterization: FreeType,
  `FT_LOAD_TARGET_NORMAL`, grayscale antialiasing, no subpixel rendering.
- Canvas: warm paper `#FAFBF6`, ink `#173362` (the product's palette).
- Body images: tokens are laid out 5 per line; line height = `int(size × 1.7)`
  pixels; left/top padding 16 px; canvas width 780 px (560 px for codes).
- Every font renders the identical token sequence at the identical nominal size.
  Fonts differ in x-height at equal nominal size; that is part of what is being
  measured (§6 has the matched-x-height control).

## 3. The corpus

**Body tokens** (48 per image, shuffled together each repetition):

- 40 lowercase English words:
  `modern kernel million graduate keyboard obvious clean particular illusion
parallel calendar morning franchise deliberate quiet exact unkempt afford
bubble hyphen quickly hijack buoyant mirror grammar pillow official civil
vivid banana unique council flying graph jigsaw kingdom lullaby minimum
opinion puzzle`
- 8 capitalized tokens: `Illinois Zurich Dublin ILLINOIS OQGDC Madrid Quebec
BENCHMARK`

**Codes** (12, three per line):
`K3PT-011l · X4O0-Q8B5 · S52Z-Il1J · rn-m-nn · 0O8B · I1l| · G6C · 8B5S-2Z0O ·
L1I7-G6C0 · M3rn-NN11 · Q0OD-C6G8 · 17Il-l1I7`

Codes are deliberately adversarial: they concentrate the letter pairs humans and
machines actually confuse (I/l/1, O/0, 8/B, 5/S, 2/Z, rn/m).

## 4. Conditions

Twelve conditions. Eight body, two codes, plus two added in v3.1: a crowding
condition (separation is usually the binding limit of real reading) and a
low-contrast condition (gray-on-white is how interfaces actually style text). Degradations are applied to the rendered
image in the order listed.

| condition      | text  | nominal size | degradation                                    |
| -------------- | ----- | ------------ | ---------------------------------------------- |
| body-9px       | body  | 9 px         | none                                           |
| body-12px      | body  | 12 px        | none                                           |
| body-9px-blur  | body  | 9 px         | Gaussian blur σ 0.6                            |
| body-12px-blur | body  | 12 px        | Gaussian blur σ 1.0                            |
| glance         | body  | 26 px        | downscale ×0.42 (Lanczos), blur σ 0.3          |
| keystone       | body  | 14 px        | perspective warp, 0.45 vertical shear factor   |
| inverted       | body  | 12 px        | full RGB inversion                             |
| passthrough    | body  | 13 px        | bright procedural noise background, blur σ 0.5 |
| codes-11px     | codes | 11 px        | none                                           |
| codes-glance   | codes | 24 px        | downscale ×0.42, blur σ 0.3                    |
| crowded        | body  | 11 px        | leading 1.15× (vs 1.7×), tracking −0.01 em     |
| low-contrast   | body  | 12 px        | ink #8A92A0 on the paper, ≈3:1                 |

Names are honest descriptions of the treatment: `keystone` is a perspective
shear (v1/v2 called it "tilt-45"), `inverted` is a naive polarity flip, which
raises effective contrast on some displays and is not a full dark-mode model.
The treatment code is byte-identical to v2 (`bench/bench_v2_core.py`).

**Size-threshold sweep.** Clean body text additionally renders at
6, 7, 8, 9, 10, 11, 12, 14, 16 px. A font's **"legible down to N px"** is the
smallest size whose mean character accuracy meets or exceeds **90%**.

## 5. Repetitions, seeds, scoring

- **8 repetitions** per cell. Repetition _r_ shuffles the token order with a
  deterministic seed: `random.Random(r × 31 + 7)` over the token list. Every
  font sees the same eight orderings (a paired design; between-font comparisons
  cancel ordering effects).
- **Character accuracy** per image: `max(0, 1 − Levenshtein(gt, ocr) / len(gt))`
  over whitespace-normalized strings (single spaces between tokens).
- A cell = mean of its 8 repetitions; per-rep raw values are published in the
  results JSON, with the SD.
- **Grand mean** = unweighted mean of the twelve condition cells.
- **Ranks are bands, not decimals.** With this design the SE of a grand mean is
  roughly 0.3–0.5 points; differences under about one point are ties and the
  published table must say so.
- **Empirical confusion matrix** (v3.1): the reader's raw output is retained
  for every non-threshold cell, and character-level substitutions are
  accumulated from the Levenshtein alignments per font. Which letters actually
  became which is published, not inferred from pixels. (The old pixel-diff
  pair score is retired; it never decided a rank and correlated with nothing.)

## 6. Controls

Run once per protocol version, published with the results:

- **Word accuracy.** Same runs rescored by whole-token recovery. Confirms the
  character-level ranking is not an artifact of the metric.
- **Pseudoword control.** The 40 words with interiors scrambled
  (`random.Random(99)`, first/last letter fixed). If rankings held while scores
  dropped only a few points, the engine is reading letterforms, not vocabulary.
- **Matched x-height control.** Body conditions re-run with each font's size
  scaled so all fonts share Verdana-class x-height (0.52 × nominal). Separates
  the "wears a big x-height" advantage from letterform construction.


- **Holdout confirmation.** Kept's own faces were designed by iterating against
  this benchmark. As a Goodhart check, a holdout corpus (20 words and 4 codes
  never used during any design iteration, listed in `bench/holdout.py`) is run
  once against the final binaries and published beside the main table. A face
  that won the main corpus but collapses on the holdout has learned the test;
  none of ours does, and you can verify that.

## 7. What this index is not

No eye movements, no crowding model, no exposure-time control, no human
subjects, one script (Latin), one rasterizer, one reader. It is an index of
letterform survival under degradation: the mechanical precondition of human
legibility, not the whole of it. Claims made from this data must be scoped to
what was measured.

## 8. The panel

The v3.1 panel adds the frequently cited readability projects, measured under
the same rules as everything else: Atkinson Hyperlegible and Atkinson
Hyperlegible Next (Braille Institute), Lexend, OpenDyslexic, Andika (SIL's
literacy face), Noto Sans, Source Sans 3, IBM Plex Sans, Public Sans, and
Comic Sans MS, which the dyslexia community folk-recommends and which deserves
measurement rather than mockery. Luciole and APHont are invited additions;
their download terms want a human read before we vendor anything.

Bear Sans UI and Bear Sans Heading appeared in v2/v3 tables and measured
excellently; they are omitted from v3.1 at the publisher's discretion since
they are another product's embedded fonts, not faces a reader can license.
Their v3 numbers remain in results/v3/.

## 8b. Fonts and licensing

The fetch script downloads only open-licensed faces (from google/fonts, pinned
URLs). System faces (Verdana, Georgia, Arial, Times New Roman, SF Pro, Helvetica
Neue, Charter) are read from their standard macOS paths and are never
redistributed. Bear Sans UI/Heading are read from a locally installed Bear.app
if present, and are never redistributed. Kept's own faces (Kept Sans, Numen
Title, Index Sans) are SIL OFL 1.1 and ship at kept.do/type.

## 9. Versioning

- **v1/v2** (July–Aug 2026): 20 words + 7 codes, 3 reps, condition names
  `tilt-45`/`dark`. Results preserved under `results/v2/`.
- **v3** (Aug 2026): this document. Corpus expanded, 6 reps, threshold sweep,
  renamed conditions, per-rep raw data, rank bands.

Changes to the protocol bump the version; numbers are only comparable within a
version.
