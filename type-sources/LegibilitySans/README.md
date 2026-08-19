# Legibility Sans · sources

Legibility Sans has always been a parametric derivative of
[Atkinson Hyperlegible Next](https://github.com/googlefonts/atkinson-hyperlegible-next):
**no glyph is redrawn.** Until now that transform existed only as an edit applied to
compiled instances, which is why the family had no sources and could not be maintained,
re-weighted, or extended by anyone — including us.

`build_legibility_sans.py` is that transform, expressed against Atkinson's own OFL
Glyphs source. Running it regenerates the family from scratch.

## The transform

Measured off the shipped binaries, not guessed:

| | |
|---|---|
| **lowercase scaled ×1.10** | about the baseline, raising x-height against untouched caps |
| **+20 units tracking** | every glyph, +10 per sidebearing |
| **+52 units** on `i j l I 1` | +26 per side — the narrowest letters, and the I/l/1 confusion set |

Atkinson already separates lowercase marks (`acutecomb`) from cap marks
(`acutecomb.case`), so "lowercase" is a clean, unambiguous set: lowercase letters plus
the non-`.case` combining marks. Marks are re-seated on their bases' anchors after the
scale, so accents follow the taller lowercase automatically.

The six weights are cut at Atkinson design coordinates 80.7 / 100.3 / 118 / 130 / 144.4
/ 167.6 — equivalent to Atkinson wght **330 / 430 / 520 / 600 / 690 / 790**. That offset
is the original design decision and it is preserved in the instance positions.

## Build

```sh
git clone --depth 1 https://github.com/googlefonts/atkinson-hyperlegible-next
python3 build_legibility_sans.py atkinson-hyperlegible-next/sources ./out
gftools builder config.yaml
python3 ../../tools/fix_fonts.py <built-dir> <ship-dir>   # metadata + metrics pass
```

That last step is not optional. A raw `fontmake` build carries none of the Google
Fonts metadata conventions and reports **24 FontBakery FAILs** — name IDs, OFL header,
font version, family-consistent vertical metrics. `tools/fix_fonts.py` is the same pass
that took the shipped binaries from 21 FAILs to 0, and it belongs at the end of every
build.

## Fidelity

The regenerated statics reproduce the shipped binaries to within rounding:

| | |
|---|---|
| x-height | exact match, all six weights |
| glyph bounding boxes | 62/62 within 1 unit (61/62 on two weights, max 3u) |
| advance widths | 318/372 exact, 54 off by exactly **1 unit** |

Worst case is 1 unit on a 1000 upm em — 0.1%, attributable to interpolation and
cubic→quadratic conversion, not to design difference.

## Why statics and not a variable font

`buildVariable` is off. Atkinson's masters sit at design 60 / 94 / 158 / 170, and
Legibility Sans' Regular is cut at 100.3 — so a variable build has no master at its own
default location. Resolving that means either interpolating a new origin master or
accepting standard weight positions, and both change the shipped design. The six statics
are what the family ships; a VF is a real option later but it is a design decision, not
a build flag.

## Licensing

Atkinson Hyperlegible Next is SIL OFL 1.1 with **no Reserved Font Name**, so this
derivation is permitted and Legibility Sans is OFL 1.1 in turn. The upstream licence is
kept alongside as `OFL-AtkinsonHyperlegibleNext.txt`.

Source the upstream from **GitHub / Google Fonts**, not from brailleinstitute.org — the
Braille Institute's own download page ships under a different, bespoke EULA that *does*
declare a reserved typeface name and carries a termination clause. The two channels are
not interchangeable.

"Atkinson Hyperlegible" is a trademark of the Braille Institute of America. Legibility
Sans is an independent derivative and is not endorsed by, or affiliated with, the
Braille Institute.
