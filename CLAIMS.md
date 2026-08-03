# Claims ledger · protocol v3.1

Every public sentence about these results maps to a cell in this repo. If a
sentence is not in this file, it is not a claim we make.

| Claim | Evidence |
|---|---|
| "The top tier is drawn by the CI-overlap rule and holds six faces: IBM Plex Sans 96.5, Public Sans 96.5, Legibility Sans 96.4, Kept Sans 96.3, Atkinson Hyperlegible Next 96.0, Verdana 95.6." | `results/v31/results-v31-OFFICIAL.json`; run `bench/stats.py <results> --tiers`. |
| "Legibility Sans is the only typeface in the index legible down to 8 px." | Threshold sweep, criterion 90%: Legibility Sans 92% at 8 px; next best Verdana 88%, Kept Sans 86%. |
| "Legibility Sans beats Verdana outright when text is set tight." | `crowded` cell 98.3 vs 86.8. The crowding condition entered the protocol after the font was frozen. |
| "Legibility Sans is ahead of Verdana overall; the margin is within our error bars." | Grand 96.4 vs 95.6; paired diff +0.78, 95% CI [−0.07, +1.85], grazes zero and is published as a tier. |
| "Kept Sans is ahead of Inter by 1.5 points; the interval grazes zero." | Paired diff +1.47, 95% CI [−0.04, +2.80]; stated as ahead-within-error, never as significant. |
| "Verdana drops out of the top tier at tight setting." | Grand 95.6 (sixth); `crowded` 86.8, nine points under its clean-size standing. |
| "Numen Title is the strongest display serif measured; Charter, a text serif, edges it overall within the error bars." | Numen Title 94.2 vs Charter 94.8; paired CI [−2.64, +1.13], crosses zero. Crowding scope note (79.5) published alongside. |
| "Instrument Serif reads 55% at 9 px and needs 12 px to cross 90%." | `body-9px` 55.0; threshold ladder. |
| "Our fonts did not learn the test." | Holdout corpus (v3, tokens never in any design loop): `results/v3/results-holdout.json`. |
| "The residual code errors are the same pairs for every strong face and match the human confusion literature." | `confusion_matrices` in the v3.1 results: I→1, O→0, l→1 dominate for Legibility Sans, Verdana, and Kept Sans alike. |
| "OpenDyslexic trails, consistent with published human null findings; Comic Sans measures respectably at clean sizes; Andika collapses only when set tight, against its design intent." | Grand 92.3 / 93.7 / 93.3 with `crowded` 83.8 / 66.5 / 60.8. No human claims are made or implied. |

Sentences we do not publish, anywhere: "the most legible font, period", any
human reading-speed, comprehension, accessibility, dyslexia, or low-vision
claim, any single-rank statement whose confidence interval overlaps a
neighbor's, and any mockery of another project's font.
