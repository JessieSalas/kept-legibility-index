# Task: propose capital-O skeletons that a text recogniser will not read as a zero

## Measured context (all real, from a published benchmark)

A machine-vision legibility index measures 24 typefaces by rendering text, degrading
it (blur, downscale, tight setting, low contrast), and reading it back with an OCR
engine. Character errors are counted.

- `O` misread as `0` is the single largest cost in the index: 1108 errors over 24 faces.
- The field is uniformly bad at it: best 39, median 47, worst 53. A 1.36x spread.
- The mirror problem is solved: `0` misread as `O` spans 8 to 28, because a zero can be
  slashed or dotted.
- In the host typeface, `O` is ALREADY 1.25x wider than `0` and they still confuse.
  **Width is not the lever.**

## What I already tried, and the wall I hit

Six skeletons, all normalised to identical ink area so only shape varied:

| skeleton | O>0 errors | grand mean |
|---|---|---|
| original (oval) | 48 | 96.26 |
| squircle (superellipse n=3.2) | 45 | 95.96 |
| very square (n=5.0) | 43 | 96.13 — but `O` read as `D` 16 times |
| round outer, square counter | 46 | 96.31 |
| angled stress (counter rotated 22 deg) | 48 | 96.35 |
| flat-sided | 47 | 96.36 |
| square outer, round counter | **35** | 95.75 — best O>0, worst overall, `O`>`D` 5 |

**The finding: it is a constraint problem, not an open goal.** Round pulls `O` toward
`0`. Square pulls it toward `D`. The room between them is narrow.

My hypothesis for where to go next: **asymmetry**, because asymmetry is the one thing
`D` cannot borrow — `D` has a flat left stem and a round right bowl, and a zero is
symmetric about both axes. A shape that is deliberately asymmetric about the vertical
axis, or that breaks the horizontal symmetry, may separate from both attractors at once.

I want your proposals. Disagree with my hypothesis if you have a better one.

## Hard constraints (a proposal violating these cannot be measured)

The glyph must match the host typeface exactly or the experiment is confounded:

- outer bounding box: x from 54 to 738, y from -12 to 712  (684 wide, 724 tall)
- advance width: 792
- ink area: 162649 square units, +/- 1%   (outer area minus counter area)
- one outer contour, one inner contour, both closed
- units per em: 1000

Stroke weight for reference: the original has ~85 units of stem on the sides and
~77 at top and bottom. Overshoot is 12 units top and bottom.

## Output contract

Write a single Python file `proposals.py`. No dependencies beyond the standard library.
It must define:

    VARIANTS = {"name": callable, ...}

Each callable takes no arguments and returns `[outer_points, inner_points]` where each
is a list of `(x, y)` float tuples in order around the contour. Outer counter-clockwise,
inner clockwise. Do not close the contour explicitly; the last point should not repeat
the first. Sample curves densely (96+ points per contour is fine and normal here) --
these are measured, not drawn, so polygonal approximation is acceptable.

Include 4 to 6 genuinely different proposals with a one-line docstring each explaining
the idea and why you expect it to separate from BOTH `0` and `D`.

Do not try to match the ink area yourself; my harness rescales the counter to hit it.
Do get the bounding box exactly right.

Write only `proposals.py`. Do not create other files.
