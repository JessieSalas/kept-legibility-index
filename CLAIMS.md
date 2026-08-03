# Claims ledger

Every public sentence about these results maps to a cell in this repo. If a
sentence is not in this file, it is not a claim we make.

| Claim | Evidence |
|---|---|
| "Legibility Sans is statistically tied with Verdana at the top of the index." | `results/v3/results-v3-OFFICIAL.json` grand means 95.8 vs 96.1; paired by-rep bootstrap of the difference: −0.28pt, 95% CI [−0.75, +0.13], crosses zero. |
| "Legibility Sans is the only typeface in the index that stays legible down to 8 px." | Threshold sweep, criterion 90% character accuracy: Legibility Sans 92% at 8 px; every other face < 90% at 8 px (Verdana 88%, Kept Sans 86%). |
| "Kept Sans sits in the top tier, tied with Verdana and Bear Sans Heading." | Grand 95.7; paired CI vs Verdana [−1.47, +0.55], crosses zero. |
| "Numen Title is the strongest serif we measured, ahead of Georgia by a margin our bootstrap does not explain away." | Grand 95.1 vs Georgia 93.6; paired difference +1.49pt, 95% CI [+0.43, +2.67], excludes zero. |
| "Instrument Serif reads 55% at 9 px and needs 12 px to cross 90%." | `body-9px` cell 55.0; threshold ladder first ≥90 at 12 px. |
| "Our fonts did not learn the test." | Holdout corpus (tokens never used during design): `results/v3/results-holdout.json`; Legibility Sans body-9px-blur 99.4 on holdout vs 92.5 on the main corpus; no face collapses. |
| "Breaking the lexicon costs a few points and no rank inversions." | v2-protocol pseudoword control, `results/v2/pseudoword-control.json`. |
| "Designed against this benchmark." | Stated wherever a Kept face's score appears. The protocol, corpus, seeds, and scoring are public; the holdout tokens were never part of any design loop. |

Sentences we do not publish, anywhere: "the most legible font, period", any
human reading-speed, comprehension, accessibility, dyslexia, or low-vision
claim, and any single-rank statement whose confidence interval overlaps a
neighbor's.
