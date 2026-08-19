# Can another model draw the glyph?

`BRIEF.md` is the prompt given to Codex (GPT, `codex exec`), verbatim. `proposals.py` is
what came back, unedited. Both are kept so the experiment is reproducible and so the
answer below is checkable rather than an opinion.

## What worked

Precise prompting worked mechanically, first try. All five proposals satisfied every hard
constraint — exact outer bounding box, correct winding (outer CCW, inner CW), counter
contained, standard library only, matching the callable contract the harness expects. It
self-validated those properties before returning. As a way to get more valid candidates
into the measurement loop cheaply, this is a real capability.

## What it produced

| variant | `O>0` | `O>D` | grand mean | note |
|---|---:|---:|---:|---|
| original | 48 | 0 | 96.26 | |
| **F square-outer** (mine, previous study) | **35** | 5 | 95.75 | best `O>0`, pays for it |
| cx diagonal_balance | 43 | 2 | 95.99 | |
| cx diagonal_corners | 44 | 3 | 96.23 | |
| cx high_shoulder | 45 | 1 | 95.95 | |
| **cx offset_counter** | 45 | **0** | 96.16 | no `D` penalty; codes-11px 0.8577 vs 0.8552 |
| cx pinched_quadrant | 44 | 2 | 95.63 | **crowded cell collapses: 0.9257 vs 0.9639** |

## The honest read

**It did not beat the hand-parameterised set on the target.** Best Codex result is 43;
the superellipse study got 35.

**It did find a corner the first study missed.** `offset_counter` moves `O>0` 48 → 45
while keeping `O>D` at zero and nudging codes-11px slightly *up*. F buys a bigger win and
pays half a point of grand mean plus a new `D` confusion. Those are different trades and
the second one is arguably the more useful shape to draw from.

**It clustered.** Asked explicitly for asymmetry, and given the finding that squareness
runs into `D`, all five came back as warped superellipses that look nearly identical to
each other and sit in the same squarish region already shown to be problematic. The
docstrings claim asymmetry; the geometry is mostly not asymmetric.

**One proposal broke something the brief never mentioned.** `pinched_quadrant` drops the
crowded cell from 0.9639 to 0.9257, the largest single-cell regression anywhere in these
studies. Nothing in the brief said "do not harm tight setting", so nothing stopped it.
That is the loop earning its keep: an unmeasured proposal would have looked fine.

## Verdict

Worth it as a **search** tool, not as a drawing tool. It widens the candidate pool cheaply
and the measurement decides. But the bottleneck was never candidate generation — it is
that both models are sampling the same parametric space (superellipses and warps), and the
answer to `O`/`0`/`D` probably is not in that space. Neither of us is drawing; we are both
picking points on a formula.

A type designer would produce shapes neither model can reach, because the move that
separates `O` from both attractors is likely a *stroke* decision — where the pen thins,
where it joins, how the counter tilts against the outer — not a boundary equation. The
loop is the durable asset here. The generator is interchangeable.

Reproduce:

```sh
cd studies/codex && codex exec --skip-git-repo-check --sandbox workspace-write \
  "Read BRIEF.md in this directory and follow it exactly. Write proposals.py."
```
