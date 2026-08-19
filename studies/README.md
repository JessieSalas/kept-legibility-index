# Studies

Geometric prototypes built to be measured. **These are not finished letterforms** —
joints, optical correction and fitting are craft these scripts do not attempt. They
exist to test a hypothesis cheaply so that the drawing which follows is aimed somewhere.

## `draw_O.py` — a capital O that is not a zero

Motivated by the finding in [`../DESIGN-BRIEF.md`](../DESIGN-BRIEF.md): `O>0` is the
largest single cost in the index (1108 errors across 24 faces) and the field is uniformly
bad at it — best 39, median 47, a 1.36× spread. Kept Sans' `O` is already 1.25× wider
than its `0` and they confuse anyway, so width is not the lever. Skeleton might be.

Six variants, each pinned to Kept Sans' own `O` — same advance, same bounding box, and
**normalised to the same ink area (±0.3%)**, because changing how square a contour is
changes how much ink sits between the two. Without that normalisation the experiment
measures weight, not shape.

### Result

| variant | `O>0` | grand mean | note |
|---|---:|---:|---|
| original | 48 | 96.26 | |
| A squircle | 45 | 95.96 | |
| B very square | 43 | 96.13 | **introduces `O>D` 16** |
| C square counter | 46 | 96.31 | tie with original |
| D angled stress | 48 | 96.35 | tie |
| E flat sided | 47 | 96.36 | tie |
| **F square outer, round counter** | **35** | 95.75 | best `O>0` in the whole index, **worst grand mean here**, `O>D` 5 |

**The headline is the trade, not the win.** F takes `O>0` from 48 to 35 — below Source
Sans 3's field-leading 39 — and pays for it twice: the grand mean drops half a point, and
`O` starts being read as `D`. B shows the same effect harder: squarer still, and `O>D`
jumps to 16.

Which is the actual finding. **The `O`/`0` problem is a constraint satisfaction problem,
not an open goal.** The capital `O` sits between two attractors: round takes it toward
`0`, square takes it toward `D`. Nobody in the field has solved it because the room is
narrow, not because nobody tried. A drawn solution has to thread that gap — probably
with asymmetry rather than squareness, since asymmetry is what `D` cannot borrow.

### Caveats that matter

- **One run.** Eight repetitions; confusion counts are raw and noisier than the cell
  means. Every number above is a hint, not a result. Replicate before believing it.
- **Differences under a point are ties** (PROTOCOL.md §7). On grand mean, everything here
  including F is technically a tie with the original; only the `O>0` delta is large.
- **`Q` was not updated.** It still carries the original round bowl in every variant, so
  `OQGDC` is internally inconsistent and the codes cells are not a clean read. A real
  drawing must move `Q`, `C`, `G` and `D` with the `O`.
- These are sampled superellipses, not drawn curves. Good enough to answer "which
  skeleton", useless as an actual letterform.

```sh
python3 studies/draw_O.py kept-type/KeptSans/KeptSans-Regular.ttf out/
python3 bench/score_candidate.py --pairs "O>0" "0>O" "O>D" \
    --font orig kept-type/KeptSans/KeptSans-Regular.ttf \
    --font F out/KeptSans-O-F-squareout.ttf
```
