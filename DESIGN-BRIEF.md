# Design brief: what the index says is worth drawing

Everything below comes from `results/v31/results-v31-OFFICIAL.json`, reduced across all
24 measured faces. It is a brief for a face whose letterforms are *drawn*, not a face
assembled by scaling someone else's — which is what Kept Sans, Legibility Sans and Numen
Title are, and why none of them clears an originality bar.

The point of drawing is not novelty for its own sake. The index says there are specific
letterform problems that **nobody in the field has solved**, and that is a real place to
put original work.

---

## 1. The headline finding

**No face in the index scores zero on any confusion pair.** Not one, across 24 faces and
every pair measured. Every typeface here — including the ones explicitly built for
legibility — leaks characters somewhere.

The twenty most expensive confusions, summed over all 24 faces:

| pair | total errors | best face | best | median | worst |
|---|---:|---|---:|---:|---:|
| `O>0` | 1108 | Source Sans 3 | 39 | 47 | 53 |
| `I>1` | 981 | Comic Sans MS | 21 | 45 | 60 |
| `l>1` | 952 | **Legibility Sans** | 21 | 41 | 59 |
| `n>m` | 735 | **Kept Sans** | 6 | 22 | 151 |
| `0>O` | 393 | OpenDyslexic | 8 | 19 | 28 |
| `l>I` | 338 | Noto Sans | 8 | 18 | 32 |
| `l>i` | 245 | Verdana | 6 | 17 | 45 |
| `l>t` | 242 | Verdana | 4 | 17 | 36 |
| `i>l` | 132 | Source Sans 3 | 6 | 19 | 47 |
| `I>l` | 126 | Roboto | 7 | 14 | 22 |

---

## 2. The one genuinely open problem: `O` → `0`

This is the brief.

`O>0` is the **largest single cost in the index** (1108 errors) and the field is
uniformly bad at it. Best 39, median 47, worst 53 — a **1.36× spread**. Twenty-four
typefaces, including three designed explicitly for legibility, and they all fail at
roughly the same rate.

Now compare its mirror. `0>O` — mistaking a zero for a capital O — has best 8, median
19, worst 28: a **3.5× spread**. OpenDyslexic gets it to 8.

That asymmetry is the whole insight:

> **A zero can be drawn so it is not an O — slash it, dot it, narrow it. Nobody has drawn
> an O that is not a zero.**

Every existing solution loads the disambiguation onto the *zero*. The capital O is left
alone, because it is a capital and designers treat it as sacred. The result is that the
error just moves: faces with a heavily marked zero still lose `O` to `0` at the field
rate.

An `O` drawn to be un-zero-like — squarer shoulders, a deliberate stress axis, a
flattened top-left, something that reads as *letter* rather than *counter* — is a real
open problem with 1108 errors of headroom and no incumbent. That is a defensible reason
for a typeface to exist.

---

## 3. Where the Kept faces already lead — keep these

These are genuine results and worth carrying into anything new:

| pair | face | rank | count |
|---|---|---|---|
| `n>m` | **Kept Sans** | **1 of 22** | 6 (median 22, worst 151) |
| `l>│` | **Kept Sans** | **1 of 10** | 4 |
| `l>1` | **Legibility Sans** | **1 of 23** | 21 |
| `h>n` | **Legibility Sans** | best | 4 |
| `I>l` | **Kept Sans** | 2 of 9 | 9 |

`n>m` at 6 against a worst of 151 is the strongest single result in the whole family.
Whatever the raised x-height plus open tracking is doing to `n`/`m` separation, it works,
and it is worth understanding before drawing anything that abandons it.

## 4. Where they trail — the honest weaknesses

| pair | face | rank | count | best in field |
|---|---|---|---|---|
| `0>O` | **Kept Sans** | **21 of 21 — last** | 28 | OpenDyslexic (8) |
| `I>1` | Kept Sans | 19 of 23 | 51 | Comic Sans MS (21) |
| `I>1` | Legibility Sans | 18 of 23 | 51 | — |
| `O>0` | Kept Sans | 15 of 24 | 48 | Source Sans 3 (39) |

Two things stand out and both are useful:

**The unslashed zero costs exactly what you would expect.** Kept Sans is dead last on
`0>O`. The specimen's reasoning — that grafting a slash onto Figtree's closed oval read
as an `8` — is sound as a critique of *grafting*. A zero drawn from the start to carry a
mark is a different proposition, and OpenDyslexic's 8 is the proof it can be done.

**A serifed `I` did not fix `I>1`.** Both Kept Sans and Legibility Sans have a
disambiguated `I` and both sit near the bottom of the field on `I>1` (51 each). Comic
Sans, with no such feature, gets 21. Meanwhile Numen Title — a serif, with no special
`I` treatment — ranks 6th at 35.

That is worth sitting with, because it contradicts the intuition the whole disambiguation
strategy rests on. The serif distinguishes `I` from `l` (and Kept Sans *is* 2nd on `I>l`),
but it does nothing about `1`, and may make things worse by giving `I` more of the
horizontal terminals a `1` has. **The `1`, not the `I`, is likely the glyph to draw.**

---

## 5. How to work

`bench/score_candidate.py` runs the v3.1 protocol over your candidate plus whichever
reference faces you name — the same corpus, conditions, reader and scoring as the full
driver, over a smaller panel so the loop is fast.

```sh
swiftc -O -o ocr/visionocr ocr/visionocr.swift     # once
sh fonts/fetch.sh                                   # once, for the reference faces

python3 bench/score_candidate.py \
    --font "Draft A" work/DraftA.ttf \
    --ref "Kept Sans" --ref "OpenDyslexic" --ref "Source Sans 3" \
    --pairs "O>0" "0>O" "I>1"
```

Three rules that keep this honest, and they matter more than the tooling:

1. **Draw first, measure second.** The index tells you where the problem is. It does not
   tell you what the shape should be, and a letterform optimised against an OCR engine is
   how you get OCR-A. Every claim in `CLAIMS.md` is scoped to machine legibility for a
   reason.
2. **Compare candidates to each other, not to the published table.** `score_candidate.py`
   reduces confusions with its own alignment, which agrees with the published matrix on 9
   of the top 12 pairs but undercounts the `I`/`l`/`1` cluster by 20–30%. Same reduction
   on both sides cancels that bias; cross-quoting does not.
3. **A single run is a hint.** Eight repetitions, and differences under a point are ties.
   `bench/stats.py --tiers` draws the CI-overlap tiers; use it before believing anything.

---

## 6. What this buys

Kept Sans has five drawn glyphs out of roughly 460. Legibility Sans and Numen Title have
none. That is why Google Fonts' first criterion — *"original, or a legitimate revival of a
design in the public domain"* — is the one wall the engineering could not remove.

A face where the drawing is yours clears that on its own merits. And unlike almost anyone
else submitting, you would be able to say *why* each decision was made, and show the
measurement. That combination — a drawn typeface with a reproducible evidentiary record —
is genuinely uncommon, and it is a much stronger position than a parametric derivative
however well it scores.
