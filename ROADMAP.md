# Roadmap · Protocol v4

Protocol v3 (this repo) is what shipped. The design below is the peer-review-grade
upgrade produced by our research pass; it is published so the direction is public
and criticizable before it is built. Contributions toward any block are welcome.

## The v4 design

**Governing ruling on budget:** the psychophysics report's full design (~1.2M renders) is overruled by the <10k-image constraint. We recover its statistical power by putting many characters in each image (MNREAD-style 60-char sentence blocks), running a paired design (identical items across faces per cell), and two-stage adaptive size sampling. Result: ~8.5k images, ~515k scored characters, roughly 2,400x v2's per-cell character volume. Both reports' core structural demands (threshold metric, x-height units, item-level inference, dev/test split, second engine) are kept in full.

## Fixed apparatus

| Parameter | Value |
|---|---|
| Declared geometry | 35 cm viewing distance; 1 iOS logical pt = 1.53 arcmin |
| Size unit | x-height in arcmin; logMAR = log10(x-height arcmin / 5); every level also published in px and pt |
| Renderer | CoreText at @2x device scale (the pipeline users actually see). FreeType retired. |
| Degradation math | All blur/noise/downsample/inversion/compositing in linear light, then sRGB encode |
| Photometry | Text/background luminance, Weber and Michelson contrast published per condition |
| Normalization | Matched x-height PRIMARY for the whole battery; matched-em and matched-advance-width as clean-only sensitivity arms |
| Typefaces | 21 = the v2 twenty + Index Sans |
| Readers | Apple Vision (language correction OFF, OS+framework version pinned) as headline; Tesseract 5 LSTM reads the identical images as held-out engine. Cross-engine Spearman published; single-engine-only results labeled engine-specific. |
| Replication | "Reps" DELETED (OCR is deterministic). Each image gets one seeded nuisance draw: sub-pixel x/y phase U[0,1), noise seed, rotation jitter ±0.25°. Seeds logged. Variance is carried by ITEMS. |

## Conditions (v2's 10 → 7 arms + the size axis)

| v2 condition | v3 disposition | v3 parameters |
|---|---|---|
| 9px body, 12px body, downscaled "glance" | **FOLDED into size sweep** (they were 3 points on one axis). The word "glance" is dropped everywhere; in the literature it means an exposure-duration threshold OCR cannot have. | n/a |
| Clean (implicit) | **C1 KEPT** · full size sweep | Stage 1: 6 levels, 0.20 logMAR steps, −0.40 to +0.60, 2 sentences each. Stage 2: 9 levels, 0.05 steps, centered on stage-1 T̂, 12 sentences each. |
| Blur | **C2 RENAMED** "low-pass (defocus proxy)" | Gaussian σ = 0.15 x-height, cutoff reported in cycles/x-height; no dioptric claim. Mini-sweep: 7 levels, 0.10 steps, centered clean-T80 + 0.10, 5 sentences each. |
| Noisy passthrough background | **C3 REBUILT as two noise arms** | C3a white noise, C3b 1/f noise; RMS contrast 0.20, SNR reported. Same mini-sweep shape as C2. |
| Inverted "dark mode" | **C4 RENAMED** "negative polarity" | Contrast- and luminance-matched inversion, uncompensated. Explicit page note: this cannot reproduce the human polarity effect (pupil-driven). Grade-compensated arm deferred to v3.1. Same mini-sweep. |
| "45° tilt" | **C5 RENAMED** "keystone" | Full 3x3 homography, rotation axis, camera distance/focal length, and 0.71 center foreshortening published. Same mini-sweep. |
| (none in v2) | **C6 ADDED** "crowded list" | Product-mimicking 5-line list, leading 1.0x, tracking −1%. Both reports demand crowding; full leading x tracking factorial deferred to v3.1 for budget. Same mini-sweep. |
| Codes straight + glanced | **C7 KEPT, merged** | 8-char alphanumeric codes, 10 per image, own 7-level sweep. Scored separately, never pooled into sentence results. |
| Confusable-pair pixel diff | **REPLACED** | Empirical confusion matrix from the runs: P(output\|truth) with binomial CIs, pooled at sizes within ±0.10 logMAR of T80, plus per-pair size at which confusion <5%. L2 pixel difference retired. |
| Pseudoword scramble | **PROMOTED to standing arm** | 5 levels around clean T̂, 4 sentences each, matched pseudoword corpus. Bounds the engine's lexical prior every release. |

## Corpus spec

MNREAD-compliant generated sentences: exactly 60 chars incl. spaces + implied period, 10–15 words, 3,000-word grade-3 lexicon, no proper nouns, no punctuation, sentence-initial cap only; rendered as 3 justified lines at 17.3 x-heights line width, inter-word space clamped 80–125%. Frozen splits: **TEST 120 sentences** (published runs), **DEV 120 disjoint** (Index Sans design loop only, never scored publicly), 60 matched pseudoword sentences, 100 codes. Per cell, sentences are sampled without replacement with a logged seed and are **identical across all 21 faces** (paired design).

## Image budget (target < 10k)

| Block | Images |
|---|---|
| C1 stage 1 (21 x 6 x 2) | 252 |
| C1 stage 2 (21 x 9 x 12) | 2,268 |
| C2–C6 mini-sweeps (6 arms x 21 x 7 x 5) | 4,410 |
| C7 codes (21 x 7 x 2) | 294 |
| Pseudoword arm (21 x 5 x 4) | 420 |
| Normalization sensitivity (2 x 21 x 5 x 4) | 840 |
| **Total** | **8,484** (~1.5k headroom for reruns) |

## Statistical reporting spec

- **Primary metric:** size threshold, not fixed-condition accuracy. Per (face x condition): fit logistic in log10 x-height to per-sentence character-correct proportions, constrained ML, lapse rate λ free in [0, 0.06], guess 0; Monte Carlo deviance goodness-of-fit. Report **T50** (ranking, tightest CI), **T80** (the criterion behind any "legible down to N" sentence), **T95** (conservative public claim), and slope (graceful-degradation measure).
- **Error metrics:** CER primary (accuracy = 1 − CER), WER secondary; sentences, pseudowords, codes always reported separately.
- **CIs:** BCa bootstrap over sentence items, 10,000 replicates. Never over reps.
- **Ranking:** hierarchical bootstrap → per-face 95% rank intervals; "top tier" = every face whose CI overlaps the top face's lower bound. No bare ordinal list, ever.
- **Composite ruling:** the 0–100 score is RETIRED as headline. Headline = clean T80 in arcmin with CI; overall standing = mean rank across non-ceiling conditions with rank intervals. Ceiling rule: a condition whose every face-CI contains a sweep endpoint is excluded from the summary and reported as a check. v2 table archived as superseded.
- **Confirmatory model:** GLMM, correct ~ face x log_size x condition + (1|item) + (1|item:face).
- **Effect calibration:** report Δ logMAR and % size (10^Δ − 1); any Index Sans advantage over Verdana >0.10 logMAR triggers an overfitting investigation before publication (the classic Times-vs-Courier effect is only 0.05–0.09 logMAR).
- **Multiplicity:** pre-registered Index-Sans-vs-incumbent contrasts; Holm correction for everything else; all losses published.
- **Covariates:** per-face perimetric complexity (perimeter²/ink area) and ink area at matched x-height, published in the results table and included in the model.
- **Deferred to v3.1 (ruled out of v3 for budget/scope):** human validation study (AgeLab-replica lexical decision), grade-compensated dark-mode arm, full crowding factorial, distance-threshold arm. Listed in the repo roadmap; v3 claims are scoped to machine legibility so nothing published depends on them.


## Citations behind the design



| # | Citation | Status | Plain takeaway |
|---|---|---|---|
| 1 | Legge & Bigelow 2011, J. Vision 11(5):8 | already on page | Size must be x-height in visual angle; point size compares x-heights, not designs. |
| 2 | Sheedy, Subbaram, Zimmerman & Hayes 2005, Human Factors 47(4) | already on page | Threshold-size "relative legibility" is the human ancestor of our metric, and Verdana topping the table matches their result. |
| 3 | Mansfield, Legge & Bane 1996, IOVS 37(8) | NEW | Real typeface effects are only 0.05–0.09 logMAR and live near threshold; x-height matching alone is not sufficient. |
| 4 | Mansfield, Atilgan, Lewis & Legge 2019, Vision Research 158 | NEW | The MNREAD sentence-generator constraints are the blueprint for our corpus. |
| 5 | Wichmann & Hill 2001 (I and II), Perception & Psychophysics 63(8) | NEW | How to fit thresholds properly: free lapse rate, ML fits, bootstrap confidence intervals. |
| 6 | Legge, Xiong, Gao, Gage, Knickel & Bigelow 2026, PLoS One 21(3) | NEW | OCR-based font assessment already exists; we can never claim to be first, only first open ranking. |
| 7 | Gao, Manduchi, Ramulu, Legge & Xiong 2026, Scientific Reports 16:1269 (VI-OCR) | NEW | Engine choice changes how faithfully machines track human legibility; justifies our second engine. |
| 8 | Dobres, Chahine, Reimer et al. 2016, Ergonomics 59(10) | already on page (listed as 2017; fix year) | "Glance" means an exposure-duration threshold, which OCR cannot have; polarity effects are real but human. |
| 9 | Beier & Larson 2010, Information Design Journal 18(2) | already on page | The design playbook for fixing misrecognized letters; how to build Index Sans honestly. |
| 10 | Pelli & Tillman 2008, Nature Neuroscience 11(10) | NEW | Crowding dominates real-world reading; motivates the crowded-list condition. |
| 11 | Bigelow 2019, Vision Research 165 | NEW | The modern review anchoring the legibility-vs-readability terminology ruling. |
| 12 | Wallace et al. 2022, ACM TOCHI 29(4) | NEW | Different fonts win for different humans, so a universal human ranking is incoherent; our machine scope is why one ranking is coherent. |

(Existing page citations Arditi & Cho 2005, Mueller & Weidemann 2012, and Pelli et al. 2006 remain valid and stay on the page; they are simply outside the top-12 for v3.)