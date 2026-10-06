# Findings

**v1.0.** The findings below are complete and final for the 3 models they cover. A 4th
model (`gemini-3.8-flash`, free tier) is in progress on a separate fixed 200-ruling
sample (`data/gemini_subset.csv`) and will be added here in **v1.1** once its run
finishes. See [STATUS.md](STATUS.md) for status. No Gemini results are published
until all 200 rulings are done. Nothing below depends on or changes because of Gemini's
results.

**Scope note, read first:** every claim in this document is about **3 free, open-weight
models run on Groq's free tier**: `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, and
`allam-2-7b`, at temperature 0, low reasoning effort, single-shot, no tools or
retrieval. Nothing here generalizes to larger, fine-tuned, or paid-tier models; where a
comparison to such a model is made (prior work), that's flagged explicitly.

## Lead finding

**Free models mostly return HTS codes that do not exist, and most of those are not near misses.** Across 1,098 CBP rulings, 88.7% to 98.4% of wrong answers were invalid codes (see "Invalid codes" below). Classifying each invalid answer against the HTS shows what kind of invalid:

| Model | Invalid answers | Suffix only wrong | First 6 digits real, first 8 not | Fabricated (no such 6-digit subheading) |
|---|---|---|---|---|
| gpt-oss-20b | 1,080 | 13.5% | 39.1% | 47.4% |
| gpt-oss-120b | 1,061 | 22.9% | 56.1% | 20.8% |
| allam-2-7b | 957 | 6.7% | 37.5% | 55.0% |

Three things follow. A fix that only repaired the 2-digit suffix would rescue at most 6.7% to 22.9% of invalid answers. Stale training data does not explain the invalid answers: only 1 invalid answer across all three models was a code that existed in a 2022 to 2025 HTS release. A validity check detects most errors (88.7% to 98.4% of wrong answers are flagged, and none of the correct 10-digit answers is). Asking the model to retry does not repair them: after one follow-up saying the code does not exist, 1.5% to 7.2% of invalid answers became valid codes, and none became the correct code. Chart: `figures/error_breakdown.png`.

![Error breakdown by model](figures/error_breakdown.png)

## The question

When AI models classify imported goods for US customs, how often are they wrong, how
much duty is at stake per error, and do their errors lean toward underpaying (the
legally dangerous direction)?

## What is new here

Prior work on LLM tariff classification (ATLAS arXiv 2509.18400, Tarifflo arXiv
2412.14179, UNB arXiv 2606.16987) reports exact-match accuracy only. None of them:
1. measures the *duty cost* of a wrong classification,
2. tests whether errors are *directionally biased* toward underpaying vs. overpaying, or
3. controls for training-data contamination by restricting to rulings dated after the
   tested models' training cutoffs.

This project adds all three, using CBP's own binding classification rulings (CROSS) as
ground truth and the official USITC Harmonized Tariff Schedule for duty rates. It
then subjects both headline findings to a hostile re-audit (Round 2) before reporting
them as final.

## Method

1. **Ground truth:** 1,816 CBP binding rulings from the NY collection
   (rulings.cbp.gov/CROSS), dated 2026-01-01 or later (contamination window, see below).
2. **Model input:** only the merchandise-description portion of each ruling, with every
   HTS-code pattern and classification/tariff language stripped out (Gate 2's automated
   leak test), so the model sees only what an importer would know before a ruling is
   issued.
3. **Usable set:** only rulings that classify a single product into exactly one 10-digit
   HTS code: 1,098 of 1,816.
4. **Duty rates:** column-1 General (MFN) rate for each true and predicted code, from the
   USITC HTS release in force on the ruling's date. USITC's JSON export always returns the
   current schedule, so each release's rates are re-read from its archived PDF and layered
   onto the JSON; see Limitations for the checked impact. Cost analysis uses ad valorem and free rates
   only. Section 301/232/reciprocal Chapter 99 duties are entirely out of scope (country-
   of-origin dependent, changed frequently through 2025-2026), so **every duty figure
   here is a lower bound**.
5. **Models:** `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b`, all free-tier,
   all on Groq. (`qwen/qwen3.8-27b` was tried first but its free quota couldn't sustain
   a 1,098-call run; swapped out, see DECISIONS.md.)

## Contamination window

`gpt-oss-20b`/`gpt-oss-120b`'s training cutoff is 2024-06-01 (confirmed on
platform.openai.com). `allam-2-7b`'s cutoff is not publicly stated; treated as
latest-possible per this project's own conservative fallback rule. The ruling window
(≥2026-01-01) is comfortably after the one confirmed cutoff.

## Gate results

| Gate | Requirement | Result |
|---|---|---|
| 1a | ≥45/50 rulings with ruling#, date, text, tariffs | **PASS: 50/50** |
| 1b | ≥300 usable post-cutoff rulings | **PASS: 1,098** |
| 2 | ≥90% of cleaned inputs non-empty and leak-free | **PASS: 99.5%** (1,807/1,816) |
| 3 | ≥85% of true codes resolve to ad valorem/free | **PASS: 98.1%** (1,077/1,098) |
| 4 | pilot accuracy reported regardless of outcome | 10-digit accuracy 0% on the pilot, far below the 90% "weak cost story" threshold |
| 5 | full run, 3 models × 1,098 rulings | **3,294/3,294 calls complete** |
| 6 | analysis | this document |
| Round 2, Gate A | Headline A (low accuracy) survives a hostile bug hunt | **PASS** |
| Round 2, Gate B | Headline B (underpay bias) beats two chance baselines at p<0.05 | **PASS, all 3 models** |
| 7 | paired language comparison | **done**, see Language Comparison below |

## Results

### Accuracy by digit level: 8-digit is the headline figure

The last 2 digits of a 10-digit HTS code are a US-only statistical suffix that is
frequently *not* binding for duty purposes. The duty rate is usually set at the
8-digit tariff-item level (see DECISIONS.md's "Gate 3" entry). 8-digit accuracy is
therefore the duty-relevant headline number, reported here alongside 6- and 10-digit.

| Model | 6-digit | **8-digit (headline)** | 10-digit |
|---|---|---|---|
| gpt-oss-120b | 21.1% | **5.6%** | 0.5% |
| allam-2-7b | 4.4% | **2.4%** | 1.7% |
| gpt-oss-20b | 3.0% | **0.3%** | 0.0% |

All three models are far below the 90% threshold that would make the cost story weak.
8-digit accuracy tops out at 5.6%. A clear capability gradient shows up at the coarser
2/4/6-digit levels (gpt-oss-120b > allam-2-7b ≈ gpt-oss-20b at 6 digits), but **all
three collapse toward the same low 8-digit accuracy**, meaning picking a "better" free
model among these three does not reliably fix the duty-relevant precision problem.

### Error depth: where wrong answers first diverge from the truth

Share of wrong answers whose first digit-level mismatch occurs at each level:

| Model | 2-digit | 4-digit | 6-digit | 8-digit | 10-digit |
|---|---|---|---|---|---|
| allam-2-7b | 59.5% | 32.3% | 5.5% | 2.0% | 0.6% |
| gpt-oss-120b | 32.0% | 23.3% | 24.1% | 15.7% | 5.0% |
| gpt-oss-20b | 44.3% | 35.7% | 17.0% | 2.7% | 0.3% |

gpt-oss-120b's errors are markedly "deeper": nearly 45% first diverge at 8 or 10
digits, meaning it usually gets the general classification (chapter/heading) right and
fails only on fine precision. allam-2-7b and gpt-oss-20b diverge earlier on average
(roughly 60% and 44% at the 2-digit chapter level), indicating more fundamental
classification errors, not just precision loss.

### Invalid codes

"Invalid" means unparseable output, or a code that is not a 10-digit entry in the HTS
revision in force on the ruling date. Counts come from `data/processed/analysis_results.json`
(ratios in `review/readme_shares.md`).

| Model | Invalid, share of all 1,098 answers | Invalid, share of wrong answers |
|---|---|---|
| gpt-oss-20b | 98.4% (1,080) | 98.4% (1,080 of 1,098) |
| gpt-oss-120b | 96.6% (1,061) | 97.2% (1,061 of 1,092) |
| allam-2-7b | 87.2% (957) | 88.7% (957 of 1,079) |

#### What kind of invalid (`scripts/analyze_invalid_codes.py`, `review/invalid_breakdown.md`)

Each invalid answer is checked against the HTS data used in this project. "Suffix only" means the first 8 digits exist. "First 6 real, first 8 not" means the 6-digit subheading exists but no 8-digit tariff item starts with the answer's first 8 digits. "Fabricated" means even the first 6 digits do not exist. "Outdated" means a 10-digit code that is not in the current HTS but appears in at least one 2022 to 2025 HTS release. Releases named "Prelim" (a 2022 preliminary draft never in force) are not counted. Each answer gets one class; outdated is checked first.

Share of all 1,098 answers per model:

| Model | Correct | Wrong, valid code | Invalid: suffix only | Invalid: first 6 real, first 8 not | Invalid: fabricated | Invalid: outdated | Invalid: no usable code |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 0 (0.0%) | 18 (1.6%) | 146 (13.3%) | 422 (38.4%) | 512 (46.6%) | 0 (0.0%) | 0 (0.0%) |
| gpt-oss-120b | 6 (0.5%) | 31 (2.8%) | 243 (22.1%) | 595 (54.2%) | 221 (20.1%) | 1 (0.1%) | 1 (0.1%) |
| allam-2-7b | 19 (1.7%) | 122 (11.1%) | 64 (5.8%) | 359 (32.7%) | 526 (47.9%) | 0 (0.0%) | 8 (0.7%) |

Of the suffix-only answers, 55 of 146 (gpt-oss-20b), 180 of 243 (gpt-oss-120b), and 21 of 64 (allam-2-7b) were exactly 8 digits, meaning the model left the suffix off. The single outdated answer (gpt-oss-120b, ruling N359777) was a suffix-only case: 2106909995 existed through 2025 and the ruling's true code is 2106909998. Manual tracing (DECISIONS.md) also found systematic confusion between adjacent headings (HTS 6801 vs. 6802 for worked stone, 6109 vs. 6110 for knit garments).

An earlier version of this section said the invalid codes were "often an 8-digit tariff item with a guessed or omitted statistical suffix". The breakdown above does not support "often": suffix-only answers are 5.8% to 22.1% of all answers, and fabricated or wrong-first-8 answers are the bulk.

### Validity check and retry

**A validity check detects most errors. Asking the model to retry does not repair them.**

Validity check: flag any answer that is not a 10-digit code in the HTS (`scripts/analyze_validity_check.py`, `review/validity_check.md`). All 1,098 rulings per model.

| Model | Wrong answers | Wrong and flagged (detection rate, 95% CI) | Wrong but not flagged | Correct 10-digit answers | Correct and flagged | 8-digit-correct answers | 8-digit-correct and flagged |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 1,098 | 1,080 (98.4%; 97.4% to 99.0%) | 18 | 0 | n/a | 3 | 3 of 3 |
| gpt-oss-120b | 1,092 | 1,061 (97.2%; 96.0% to 98.0%) | 31 | 6 | 0 of 6 | 61 | 55 of 61 (90.2%) |
| allam-2-7b | 1,079 | 957 (88.7%; 86.7% to 90.4%) | 122 | 19 | 0 of 19 | 26 | 7 of 26 (26.9%) |

The check flags none of the correct 10-digit answers (0 of 6 for gpt-oss-120b and 0 of 19 for allam-2-7b; gpt-oss-20b has none). It does flag most answers that are right at the duty-relevant 8-digit level but lack a valid 10-digit suffix, so it is a detector for "needs review", not a classifier.

Retry: on the fixed 200-ruling sample (`data/gemini_subset.csv`), when a model's first answer was invalid, it was sent one follow-up turn: "That code does not exist in the current HTS. Give a valid 10-digit code." The follow-up answer replaced the first answer. Same temperature and reasoning settings as the original run (`scripts/run_guardrail_followup.py`, `scripts/analyze_guardrail.py`, `review/guardrail.md`).

| Model | Invalid first answers | Follow-up became a valid code | Of those, the correct 10-digit code | 8-digit accuracy before / after | 10-digit accuracy before / after |
|---|---|---|---|---|---|
| gpt-oss-20b | 196 of 200 | 3 (1.5%) | 0 | 1 / 1 of 200 | 0 / 0 of 200 |
| gpt-oss-120b | 195 of 200 | 14 (7.2%) | 0 | 15 / 13 of 200 | 1 / 1 of 200 |
| allam-2-7b | 179 of 200 | 4 (2.2%) | 0 | 4 / 1 of 200 | 1 / 1 of 200 |

Retrying repaired nothing: no follow-up produced the correct code, and 8-digit accuracy fell for gpt-oss-120b and allam-2-7b because the follow-up replaced some answers that had matched at 8 digits. One allam-2-7b follow-up could not be answered because the conversation exceeded that model's context window (counted as still invalid). Sample sizes are small, so differences between models are indicative only.

### Direction bias: tested against chance, with sample sizes

**Base for these numbers.** Only wrong answers where both the true code and the predicted code resolve to an ad valorem or free rate can be compared on duty. Only 10-digit answers get a rate. A 10-digit answer that is not in the HTS can still resolve through its 8-, 6- or 4-digit prefix. That gives 101, 93, and 147 comparable answers for gpt-oss-20b, gpt-oss-120b, and allam-2-7b (9.2%, 8.5%, and 13.6% of their wrong answers). Of those, 15, 31, and 113 are valid 10-digit codes. The table below uses the subset whose rates differ (`scripts/analyze_underpay_summary.py`, `review/underpay_summary.md`).

| Model | n (rate-changing errors) | Underpaid | Underpay share (Wilson 95% CI) | Binomial p vs. 50% | p vs. Baseline 1 (heading) | p vs. Baseline 2 (matched depth) |
|---|---|---|---|---|---|---|
| allam-2-7b | 116 | 76 | 65.5% (56.5% to 73.5%) | 0.0011 | < 0.001 | < 0.001 |
| gpt-oss-20b | 46 | 31 | 67.4% (53.0% to 79.1%) | 0.0259 | < 0.001 | < 0.001 |
| gpt-oss-120b | 49 | 32 | 65.3% (51.3% to 77.1%) | 0.0444 | < 0.001 | < 0.001 |

All three models have n of at least 30 and underpay significantly more often than both chance baselines. Against a plain 50% split all three are below p = 0.05, but the gpt-oss-20b and gpt-oss-120b intervals come close to 50%, so read the size of the effect from the confidence intervals, not the p-values. **Round 2 tested whether this beats a fair baseline** (random guessing could underpay more than 50% of the time just because of where true codes happen to sit in the tariff schedule) rather than assuming bias from the raw number. Two baselines were simulated at 1,000 reps each: a random sibling code under the true code's 4-digit heading, and the harder test: a random sibling under the *model's own* deepest-correct prefix.

| Model | Observed | Baseline 1 (heading-random) | Baseline 2 (model's-depth-random) |
|---|---|---|---|
| allam-2-7b | 0.655 | 0.569, **p < 0.001** | 0.456, **p < 0.001** |
| gpt-oss-120b | 0.653 | 0.569, **p < 0.001** | 0.503, **p < 0.001** |
| gpt-oss-20b | 0.674 | 0.568, **p < 0.001** | 0.490, **p < 0.001** |

The underpay bias is not explained by where true codes sit in the schedule, even accounting for each model's own depth of error. An earlier version of this document said gpt-oss-20b did not beat Baseline 1 (p = 0.742). That figure was stale: `review/audit_direction.md` shows p < 0.001, and the claim is removed here. The rate-changing set is small (46 to 116 answers per model) and comes from the 8% to 14% of wrong answers that can be compared on duty, so this result describes that comparable set, not all errors.

A hypothesized mechanism (models defaulting to cheaper "Other" catch-all subheadings more often than the true codes do) was checked and **ruled out**: predicted codes land in "Other" baskets *less* often than true codes across all 3 models (11-49% vs. 62-63%), which if anything would predict overpaying, not underpaying.

### Duty at stake for valid wrong codes

For wrong answers that are valid 10-digit codes and where both the true and predicted code resolve to an ad valorem or free rate (`review/invalid_breakdown.md`):

| Model | Valid wrong codes | With usable rates (n) | Median duty at stake per $100,000 | IQR | Zero rate difference |
|---|---|---|---|---|---|
| gpt-oss-20b | 18 | 15 | $1,500 | $200 to $3,500 | 4 |
| gpt-oss-120b | 31 | 31 | $0 | $0 to $1,350 | 16 |
| allam-2-7b | 122 | 113 | $4,000 | $1,400 to $7,000 | 17 |

These are MFN-only lower bounds. For gpt-oss-20b (n = 15) there are too few cases to confirm the median.

### Free errors and duty at stake

| Model | Share of wrong answers with zero rate difference ("free errors") | Median duty at stake per $100,000 declared (IQR) |
|---|---|---|
| gpt-oss-20b | 54.5% | $0 ($0–$3,500) |
| gpt-oss-120b | 47.3% | $300 ($0–$2,500) |
| allam-2-7b | 21.1% | $3,400 ($350–$6,500) |

Split by direction (median per $100,000, among wrong answers with a resolvable rate):

| Model | Underpay median (n) | Overpay median (n) |
|---|---|---|
| allam-2-7b | $4,300 (76) | $5,400 (40) |
| gpt-oss-120b | $2,550 (32) | $2,100 (17) |
| gpt-oss-20b | $4,200 (31) | $4,900 (15) |

These figures exclude all Chapter 99 trade-remedy duties and are computed over a
small subset of wrong answers (those with a resolvable rate on both sides). Real
statistical power for the dollar figures is lower than the 1,098-ruling headline count
suggests, but the upper IQR bound reaches several thousand dollars per $100,000
declared even on this conservative, MFN-only basis.

## Language comparison

100 cleaned descriptions were translated into French and Modern Standard Arabic (by
`qwen/qwen3.8-27b`, a model distinct from all 3 tested) and reviewed by a human fluent
in both languages. **84/100** were approved in both languages, **93/100** in French,
**90/100** in Arabic. The same 3 models were run on the approved translations with the
identical prompt, temperature, and reasoning-effort settings as the English run.

**No statistically significant accuracy difference was detected between English and
either translation, for any model, at any digit level.** All McNemar exact-test p-values
are ≥ 0.22 (many at 1.0, since discordant pairs were rare). This should be read as **"no
difference detected at this sample size," not as evidence of no difference**. A power
analysis (Monte Carlo, 2,000 simulations per candidate effect size, under a simplifying
independence assumption that likely *understates* true power) found the smallest
10-digit accuracy gap detectable at 80% power with n≈90-93 is approximately 0.10-0.15,
i.e., only a 10-15 percentage-point difference or larger would reliably show up at this
sample size. Paired bootstrap duty-at-stake differences were similarly not distinguishable
from zero (every 95% CI includes $0).

### allam-2-7b: Arabic vs. English, specifically

allam-2-7b is the one Arabic-focused model among the three tested. Does that
specialization show up as better Arabic performance on *this* task?

| Digit level | English | Arabic | Arabic better? | McNemar p |
|---|---|---|---|---|
| 8 (headline) | 0.0% | 1.1% | yes | 1.0000 |
| 6 | 3.3% | 6.7% | yes | 0.2500 |
| 10 | 0.0% | 1.1% | yes | 1.0000 |

Arabic is numerically higher at every level, but with n=90 and only 1-6 correct answers
per cell, none of this is statistically distinguishable from chance (same power
limitation as above). A model's training-language focus does not automatically transfer
to a different task (US tariff classification, whose schedule and terminology are
English in origin) conducted in that language. This is a data point, not a finding.

## Comparison with prior work

| Source | 6-digit | 10-digit |
|---|---|---|
| This project: gpt-oss-120b | 21.1% | 0.5% |
| This project: allam-2-7b | 4.4% | 1.7% |
| This project: gpt-oss-20b | 3.0% | 0.0% |
| ATLAS, fine-tuned Atlas model (LLaMA-3.3-70B) | 57.5% | 40% |
| ATLAS, GPT-5-Thinking (general-purpose, not fine-tuned) | not stated | ~25% (back-calculated from the abstract) |
| ATLAS, Gemini-2.5-Pro-Thinking (general-purpose, not fine-tuned) | not stated | ~12.5% (back-calculated) |

Verified directly from the ATLAS abstract (arXiv 2509.18400, checked live 2026-10-02):
even their **general-purpose, non-fine-tuned** frontier baselines report far higher
10-digit scores than this project's models, under different conditions (paid frontier
models, a different benchmark, different prompting and reasoning settings). This gap is
attributed to **model capability and configuration**. This project deliberately tests only free, open-weight,
non-fine-tuned, low-reasoning-effort models, a narrower and weaker slice of what's
possible than ATLAS's comparison set, **not to the classification task itself being
harder than ATLAS's framing suggests**; the contamination-control window and
description-only input are honesty-driven methodology choices in this project, not
properties of the task, and ATLAS's own general-purpose baselines already show frontier
models doing meaningfully better at the same kind of task. Tarifflo's paper (arXiv
2412.14179) benchmarks commercial, purpose-built classification *products* (Zonos,
Tarifflo, Avalara, WCO BACUDA), not a raw LLM given a generic prompt, so no number from
it is used here as a comparison point.

## Exclusions table (every stage, Phase 1-3)

| Stage | Count |
|---|---|
| Candidate pool (NY rulings, CROSS search, dated ≥2026-01-01) | 1,828 |
| Successfully fetched (ruling#, date, text, tariffs all present) | 1,816 |
| Excluded: zero classification codes (pure origin/marking rulings) | 458 |
| Excluded: multiple products or codes | 234 |
| Excluded: non-10-digit code | 17 |
| Excluded: Phase 2 cleaning failed (empty/leaky after extraction) | 9 |
| **Usable set (Gate 1b)** | **1,098** |
| Of usable set: resolves to ad valorem/free rate (Gate 3) | 1,077 |
| Of usable set: specific rate (excluded from cost analysis) | 7 |
| Of usable set: compound rate (excluded) | 8 |
| Of usable set: other/unparseable rate (excluded) | 2 |
| Of usable set: code not found in its HTS revision (excluded) | 1 |
| Of usable set: rate field blank at every digit level checked (excluded) | 3 |

## Limitations (stated before interpretation)

- **HTS data and MFN rates (found and checked 2026-10-06).** USITC's JSON export ignores the `release` parameter and always returns the current schedule, so the 21 per-revision files fetched in Phase 3 are identical copies of the current schedule. Archived releases exist only as PDFs. Two checks were run on them:
  - *Validity.* Using the PDF-derived code sets of every 2026 release (`scripts/check_revision_impact.py`, `review/revision_impact.md`), the validity of a 10-digit predicted code would differ for 1 answer (gpt-oss-120b) and 0 for each of the other two models. 5 true codes are absent from both the current and their ruling-date release.
  - *Rates.* The General rate of every true and predicted code in the cost analysis was re-read from the release in force on the ruling date (`scripts/parse_release_rates.py`, `scripts/check_rate_impact.py`, `review/revision_rates.md`). Of 4,060 distinct (code, ruling date) pairs, 0 had a different MFN rate in the ruling-date release than in the current release, so MFN rate changes during 2026 do not move any figure. The PDF parser agrees with the JSON on all but 10 pairs, where the PDF has a rate on an 8-digit parent line that the JSON has no row for. The reported figures now layer the ruling-date PDF rates onto the JSON (`parse_duty_rates.load_revision`). That raised gpt-oss-120b from 85 to 93 comparable answers (median duty at stake $600 to $300) and allam-2-7b from 145 to 147. Parser accuracy: 4,762 JSON rows with an ad valorem or free rate, 17 not reproduced from the PDF (14 of them in chapters 98 and 99).
  - *Markup bug fixed in the same pass.* Five chapter 87 rates carry HTML markup in the export ("2.5% <u></u>") and were classified "other" and dropped. Stripping it moved 16 rulings into the cost analysis (Gate 3: 1,061 to 1,077 of 1,098).
- All duty-at-stake figures are a **lower bound**: column-1 General (MFN) rates only,
  excluding all Section 301/232/reciprocal-tariff Chapter 99 overlays.
- Ground truth is limited to the **NY collection**. HQ rulings and court decisions are
  not included.
- `allam-2-7b`'s training cutoff is unconfirmed; its results carry a residual,
  unquantified contamination risk the other two models' results don't.
- Direction-test and duty-at-stake sample sizes (n=46-116 per model) are small because
  most wrong answers are non-existent codes with no comparable rate.
- Digit-level accuracy credits a prediction at any level it actually specified (e.g. an
  8-digit-only answer can score correct at 6/8 digits even though it can never score at
  10), a deliberate scoring choice, not an all-or-nothing one; see DECISIONS.md.
- A self-initiated, broader ground-truth cross-check (beyond the required 20-sample)
  found CBP's own ruling letters occasionally (~1%) have an internal inconsistency
  between their structured header field and a typo in the free-text holding sentence;
  this project uses the structured field, which matches the ruling's own official header
  and is the more reliable of the two.
- Language-comparison results (n=84-93) have limited statistical power: only a
  10-15 percentage-point accuracy gap or larger would be reliably detected. Non-
  significant results mean "not detected at this sample size," not "no difference."
  Translations were reviewed by one human for factual fidelity, not by a certified
  translation service.
- All findings are about 3 specific free-tier models on one provider (Groq) as of
  October 2026; results may not hold for other models, providers, or time periods as
  free-tier offerings and model versions change.
- Every statistic here is descriptive; no causal claims are made about *why* models
  underpay more than they overpay.

## What would change the conclusions

- A confirmed training cutoff for `allam-2-7b` falling after 2026-01-01 would require
  re-running its results on a later window.
- A larger paired language sample (several hundred rulings) could detect the
  10-15-point-or-smaller differences this sample cannot rule out.
- Testing a stronger, non-free-tier, or fine-tuned model would very plausibly close
  much of the gap to ATLAS's numbers. This project deliberately didn't test that, per
  its zero-spend constraint, so it cannot speak to whether the underpay bias and
  near-zero full-precision accuracy are specific to free-tier models or hold more
  broadly.
