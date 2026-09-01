# Numen Title · build notes

Numen Title ships **binaries only** in `kept-type/NumenTitle/`. There is no
Glyphs source. The family is Fraunces with its axes pinned where the index
pointed, then a 5% condensation and 2% height raise. The transform was
measured, not guessed; the public write-up is [kept.do/type](https://kept.do/type).

## The transform

| | |
|---|---|
| **opsz 52** | optical-size knee: display presence that still survives 9 px |
| **SOFT 75** | serif in spirit, not doctrine |
| **WONK 0** | normalised forms. Roman swaps `h m n s &`; italic swaps `b d h k l v w &` |
| **wght 300–800** | Light, Regular, Medium, SemiBold, Bold, ExtraBold |
| **scale x 0.95, y 1.02** | Instrument’s stance; costs half a point, paid deliberately |
| **straight j** | hooked Fraunces descender rebuilt as a stem to the family descender (`tools/straighten_numen_j.py`, italic-aware in `tools/build_numen_italic.py`) |
| **Kept marks** | U+2713 / U+2717 grafted from the matching roman weight; Fraunces’ own ampersand stays |

Italic is the same transform applied to
`Fraunces-Italic[SOFT,WONK,opsz,wght].ttf`. Files are named
`NumenTitle-<Weight>Italic.ttf` (Regular italic is the RIBBI name
`NumenTitle-Italic.ttf`) with OS/2 italic bit, macStyle, `post.italicAngle`
−16, and a one-value-per-axis STAT so the twelve statics read as one family.

## Build italic

```sh
git clone --depth 1 https://github.com/undercasetype/Fraunces
python3 tools/build_numen_italic.py \
    Fraunces/fonts/variable/Fraunces-Italic\[SOFT,WONK,opsz,wght\].ttf \
    kept-type/NumenTitle \
    kept-type/NumenTitle
python3 tools/fix_numen_marks.py kept-type/NumenTitle
```

Roman statics are not regenerated from Fraunces: they already carry the
straight-j edit, the grown interpunct, and the QA pass. This script only
instances italic and bumps the whole family to the current version.

## Licensing

Fraunces is SIL OFL 1.1 with no Reserved Font Name. Numen Title is OFL 1.1
in turn. The OFL header credits Undercase Type.
