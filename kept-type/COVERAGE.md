# Symbol coverage · three families

Checked Regular of each family against Latin-1 Supplement, Latin Extended-A,
the punctuation / currency / math / arrow / mark set the app relies on, and
the digits. Gaps are filled **only** when the upstream already draws the
glyph. Nothing below was invented.

| Family | cmap | `tnum` | Upstream |
|---|---:|---|---|
| Numen Title 1.400 | 629 | no (figures are display-cut) | Fraunces — same gaps |
| Kept Sans 2.100 | 393 | yes | Figtree — same gaps |
| Legibility Sans 2.100 | 362 | yes | Atkinson Hyperlegible Next — same gaps |

## Per-family gaps

### Numen Title

| Block | Present | Missing | In Fraunces? |
|---|---:|---|---|
| Latin-1 Supplement | 96/96 | — | — |
| Latin Extended-A | 126/128 | U+0149 n-apostrophe (deprecated), U+017F long s | no |
| General punctuation | 10/10 | — | — |
| Currency $ € £ ¥ | 4/4 | — | — |
| Math ± × ÷ ≤ ≥ ≠ ∞ | 6/7 | U+221E ∞ | no |
| Arrows ← → ↑ ↓ | 0/4 | all four | no |
| © ® ™ ° | 4/4 | — | — |
| Digits 0–9 | 10/10 | — | — |

### Kept Sans

| Block | Present | Missing | In Figtree? |
|---|---:|---|---|
| Latin-1 Supplement | 95/96 | U+00AD soft hyphen | no |
| Latin Extended-A | 109/128 | Ēē Ĩĩ Ĭĭ ĸ Ŀŀ ŉ Ŏŏ Ţţ Ŧŧ Ũũ ſ | no |
| General punctuation | 9/10 | U+00AD | no |
| Currency $ € £ ¥ | 4/4 | — | — |
| Math ± × ÷ ≤ ≥ ≠ ∞ | 6/7 | U+221E ∞ | no |
| Arrows ← → ↑ ↓ | 4/4 | — | — |
| © ® ™ ° | 4/4 | — | — |
| Digits 0–9 + `tnum` | 10/10 | — | — |

### Legibility Sans

| Block | Present | Missing | In Atkinson? |
|---|---:|---|---|
| Latin-1 Supplement | 94/96 | U+00AD soft hyphen, U+00B5 micro | no |
| Latin Extended-A | 93/128 | Ĉĉ Ēē Ĝĝ Ĥĥ Ĩĩ Ĭĭ Ĵĵ ĸ Ŀŀ ŉ Ŋŋ Ōō Ŏŏ Ŗŗ Ŝŝ Ŧŧ Ũũ Ŭŭ ſ | no |
| General punctuation | 9/10 | U+00AD | no |
| Currency $ € £ ¥ | 4/4 | — | — |
| Math ± × ÷ ≤ ≥ ≠ ∞ | 7/7 | — | — |
| Arrows ← → ↑ ↓ | 0/4 | all four | no |
| © ® ™ ° | 4/4 | — | — |
| Digits 0–9 + `tnum` | 10/10 | — | — |

Nothing was copied in. The remaining holes are upstream holes.
