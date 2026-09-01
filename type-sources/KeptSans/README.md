# Kept Sans · sources — **work in progress, do not ship from this yet**

This regenerates Kept Sans from [Figtree](https://github.com/erikdkennedy/figtree)'s
OFL Glyphs source. It is **not yet faithful enough to replace the shipped binaries** —
see *Known gaps* — but it is close, and it is committed so the remaining work is
visible rather than lost.

Contrast with [`../LegibilitySans`](../LegibilitySans), which reproduces its shipped
binaries to within 1 unit and *is* ready.

## The transform

Derived by measuring the shipped binaries against Figtree, not guessed:

| | |
|---|---|
| lowercase scaled **×1.0605** | caps and figures untouched |
| **+16 units** tracking | +8 per sidebearing, every glyph |
| **+44 units** on `1 I i j l` | +22 per side — the "five narrowest glyphs" of the specimen, confirmed to be exactly these five |
| five glyphs replaced | `I` and `l` are genuinely drawn (crossbarred I, tailed l); `K`, `k` and `&` come from Albert Sans, which the OFL header has always credited |

Kept Sans sits on Figtree's own weight positions — 300…900 map straight through, with
no shift — so a variable build is possible in principle, unlike Legibility Sans.

Figtree carries intermediate **brace layers at `{660}`** for `a`, `e` and `s`. These are
real interpolation sources and must take the same scale and tracking as the masters;
missing them bends those three glyphs by ~10 units at the middle weights. That bug is
fixed here, and it is the kind of thing that is invisible until you diff against the
shipped output.

## Known gaps

Fidelity against the shipped binaries, by weight (bounding boxes within 1 unit):

| weight | glyphs matching | worst | worst offenders |
|---|---|---|---|
| Light | 61/63 | 16u | `9`, `j` |
| Regular | 56/63 | 19u | `I`, `9`, `j`, `&` |
| Medium | 56/63 | 23u | `I`, `&`, `9`, `j` |
| SemiBold | 56/63 | 26u | `&`, `I`, `9` |
| Bold | 55/63 | 20u | `&`, `9`, `k` |
| ExtraBold | 56/63 | 17u | `9`, `K`, `k` |
| Black | 61/63 | 16u | `9`, `j` |

Two distinct causes:

1. **`9` is off by ~16 units at every weight, including both masters.** The shipped font
   gives it an asymmetric sidebearing adjustment that the uniform tracking rule does not
   capture. It needs to be measured per weight and added as an explicit rule.
2. **The five replaced glyphs diverge at intermediate weights.** They are lifted from the
   shipped Light and Black binaries and interpolated between, but the shipped statics
   appear to carry per-weight cuts that two-master interpolation does not reproduce.
   Fixing this properly means extracting each replaced glyph at all seven weights and
   either adding brace layers for them or reconciling them to a two-master system.

The ampersand additionally fails `fontmake`'s interpolation compatibility check — its
Light and Black outlines were converted from binaries independently and do not share a
point structure. That is what forces `buildVariable: false` today. Sourcing it from
Albert Sans' own variable source instead would likely resolve both that and its
intermediate-weight divergence.

## Build

```sh
git clone --depth 1 https://github.com/erikdkennedy/figtree
python3 build_kept_sans.py figtree/sources ../../kept-type/KeptSans ./sources
# italic: KeptSans-Italic.glyphs (scale + tracking; five redrawn glyphs
# stay Figtree-italic — no shipped italic binaries to harvest)
gftools builder config.yaml
python3 ../../tools/fix_fonts.py <built-dir> <ship-dir>   # metadata + metrics pass
```

Figtree's weight axis is **300–900** (Light–Black). There is no Thin or
ExtraLight upstream; we do not extrapolate those. Italic instances are
produced for every existing weight.

## Licensing

Figtree is SIL OFL 1.1 with no Reserved Font Name; Albert Sans likewise. Kept Sans is
OFL 1.1 in turn, and the OFL header credits both.
