# Can image generation draw a glyph?

Tested properly rather than assumed. Codex's `image_gen__imagegen` produced four capital
`O` references; `trace_glyph.py` traced them to contours; the contours were normalised to
Kept Sans' `O` metrics and ink area and measured on the index.

`BRIEF.md` is the prompt verbatim. `O-asym-stress.png` is the best of the four outputs,
kept because it is genuinely good and the honest verdict has to account for that.

## The images are better than expected

`O-asym-stress.png` is a well-formed `O` with real diagonal stress — thick at lower-left
and upper-right, thin on the opposite diagonal. That is exactly the asymmetry hypothesis
the superellipse study could not reach parametrically, and no amount of formula-tweaking
would have produced it. As **ideation**, this works.

## The measurement says it does not help

| variant | `O>0` | `O>D` | grand | crowded |
|---|---:|---:|---:|---:|
| original | 48 | 0 | 96.26 | 0.9639 |
| **F square-outer** (parametric, earlier study) | **35** | 5 | 95.75 | 0.9655 |
| traced: offset-counter | 44 | 0 | 96.20 | 0.9652 |
| traced: asym-stress | 47 | 0 | 96.13 | 0.9625 |
| traced: flat-top | 47 | 1 | 95.95 | **0.9260** |
| traced: tapered | **51** | 0 | 96.19 | 0.9649 |

Best traced result is 44 against an original 48 — inside noise. The tapered one scored
*worse* than the original. The hand-parameterised `F` at 35 still dominates everything.
And `flat-top` collapsed the crowded cell to 0.9260, the same failure mode a Codex
proposal hit earlier.

## Why the outlines cannot become a font

This is the part that settles it, and it is structural rather than a quality complaint.

**Node counts.** Tracing gave ~3000 raw boundary points per contour; RDP at 1.0 units
brings that to 60–68. A drawn `O` has **8–12**. The traced version carries five to eight
times the points, none of them where a type designer would put them.

**No extrema.** Every font format, and the Google Fonts outline guide, require on-curve
points at the horizontal and vertical extremes. A tracer places nodes where the *pixel
polygon* bends, which is not where the letterform's geometry turns. Nothing in the
pipeline knows what a letter is.

**Interpolation compatibility is the hard stop.** A multi-weight family requires every
master to share identical path, node and handle counts *in the same order*. Compatibility
is a **relational** property across masters; tracing is a **per-image** function. Tracing
the same glyph across six weights of one coherent family yields different node counts
every time. Independently generated images would diverge in structure, not just count.
Forcing compatibility afterwards redistributes points onto a designed template and throws
the traced geometry away — at which point the tracer contributed nothing.

So: fine for one static display glyph, structurally impossible for a family.

## Verdict

**Image generation is a legitimate ideation tool and not a drawing tool.** It reached a
shape the parametric search could not, and that is a real contribution to *thinking*. It
cannot produce outlines anyone can ship, and the reason is not resolution or prompt
quality — it is that tracing has no model of a letterform and no way to be compatible
across masters.

Worth noting: the two most-cited "AI typefaces" turn out on inspection to be humans
drawing in Glyphs while using AI images as reference. That is precisely the workflow these
results support.

```sh
python3 studies/imagegen/trace_glyph.py studies/imagegen/O-asym-stress.png
```
