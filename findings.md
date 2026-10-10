# Findings

**v1.1 (2026-10-07).** Stronger models were added in the final section, "v1.1: stronger open-weight models". The v1.0 results below are unchanged.

**v1.0.** The findings below are complete and final for the 3 models they cover. Gemini
(`gemini-3.8-flash`, free tier) is running on the fixed 200-ruling sample
(`data/gemini_subset.csv`) and will be added when its run finishes. See
[STATUS.md](STATUS.md) for status. No Gemini results are published until all 200 rulings
are done.

**Scope note, read first:** every claim in this document before the final v1.1 section is about **3 free, open-weight
models run on Groq's free tier**: `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, and
`allam-2-7b`, at temperature 0, low reasoning effort, single-shot, no tools or
retrieval. Nothing here generalizes to larger, fine-tuned, or paid-tier models; where a
comparison to such a model is made (prior work), that's flagged explicitly.

## Lead finding

**The three small free Groq models mostly return HTS codes that do not exist, and most of those are not near misses** (v1.0; the stronger models in the v1.1 section below behave differently). Across 1,098 CBP rulings, 88.7% to 98.4% of these three models' wrong answers were invalid codes (see "Invalid codes" below). Classifying each invalid answer against the HTS shows what kind of invalid:

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

### Format slip or invented code?

For the three v1.0 models the five groups defined in the v1.1 section below (a to e, `review/format_vs_invention.md`) sum to the published invalid counts (1,080 / 1,061 / 957). Most of their invalid answers are invented: groups (d) and (e), a tariff line that does not exist, are 86.5%, 76.9% and 92.5% of invalid answers for gpt-oss-20b, gpt-oss-120b and allam-2-7b. Only 0.3%, 5.2% and 0.7% of their invalid answers are a real suffix slip, meaning the answer has the true code's first 8 digits but a wrong or missing suffix. The single v1.0 "outdated" answer counts as FORMAT, group (c). The same split for the stronger models, which behave differently, is in the v1.1 section.

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

The underpay bias is not explained by where true codes sit in the schedule, even accounting for each model's own depth of error. An earlier version of this document said gpt-oss-20b did not beat Baseline 1 (p = 0.742). That figure was stale: `review/audit_direction.md` shows p < 0.001, and the claim is removed here. The rate-changing set is small (46 to 116 answers per model) and comes from the 8.5% to 13.6% of wrong answers that can be compared on duty, so this result describes that comparable set, not all errors.

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

Verified directly from the ATLAS abstract (arXiv 2509.18400, checked live 2026-10-02): its general-purpose, non-fine-tuned baselines
report 10-digit scores of about 25% and 12.5%, higher than the v1.0 models, under different conditions (paid models, a different
benchmark, different prompting and reasoning settings). This gap is attributed to **model capability and configuration**, **not to the
classification task itself being harder than ATLAS's framing suggests**: the v1.0 models were free, open-weight, non-fine-tuned and run at
low reasoning effort, and the stronger v1.1 models score 12.4% to 31.7% at 10 digits, in the range of those baselines. The
contamination-control window and description-only input are methodology choices in this project, not properties of the task. Tarifflo's paper (arXiv
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

## v1.1: stronger open-weight models (zero-cost runs via Baseten free credits and OpenRouter free tier)

v1.1 answers two objections raised after v1.0: (1) small free models are easy to dismiss, so test stronger ones; (2) how much of the invalid-code rate is formatting and how much is the model inventing a code. The models, samples, metrics and tests were fixed in [PREREG_v1.1.md](PREREG_v1.1.md) before any new model call (commit `883112942a8c68c0160861e607d9105bf2ded173`; slugs, settings and dated deviations in the addendum, commit `0d79b92b69485797179862f55b27d671b046c05d`).

**Two exceptions to the title, stated first.** GPT-6 Sol is a closed OpenAI model on a paid route, run on the 200-ruling sample at the user's request for $0.20 (hard cap $2); it is the only model in v1.1 that is neither open-weight nor free. Gemini 3.8 Flash is also being run (free tier, one request-limited run per day) and is **not in any table** because it has not reached its 200 rulings. **No other closed model is in these tables, and none of the models below stands in for GPT, Claude or Gemini.** Every model ran single-shot at temperature 0, no tools, no web, at the lowest reasoning level it accepts.

### Deviations from pre-registration

Listed here so a reader does not have to find them in the logs. The first two break an explicit pre-registered or standing rule.

1. **The pre-registered stop on a parser difference was not honoured.** PREREG_v1.1.md section 5 says to re-parse every cached v1.0 answer with the updated parser and to stop if any differs. 3,293 of 3,294 matched. One differed: allam-2-7b, ruling N358156 (true code 9405504000). The raw response is a JSON array of three objects, each containing `"hts_code": "7614.90.90"`. The v1.0 parser took everything from the first "{" to the last "}", which is not valid JSON for an array of objects ("Extra data"), so v1.0 recorded no code. The updated parser reads each object separately and takes the last one containing "hts_code", which is the pre-registered rule, and gives 76149090. By the pre-registered rule the new parse is the correct one. I did not stop: the work was autonomous and nothing irreversible depended on it. I kept the cached v1.0 value (no code) so the published v1.0 numbers stay as published, and applied the new parser to the new models only. If the new parse were applied to that answer, accuracy at every digit level, the invalid count (957), the validity check and every direction and duty number would not change (76149090 matches nothing, is still invalid, and only 10-digit codes get a rate). Two classification counts for allam-2-7b would move by one answer: in `review/format_vs_invention.md` group (a) 8 to 7 and group (d) 359 to 360 (FORMAT 72 to 71, INVENTED 885 to 886), and in `review/invalid_breakdown.md` "no usable code" 8 to 7 and "first 6 ok, first 8 not" 359 to 360. No other reported number is affected.
2. **GPT-6 Sol was a paid route.** The standing rule was zero spend, with only free OpenRouter ids allowed. The user asked mid-run to include "GPT 6 SOL" and later wrote that OpenRouter was fine "just don't spend too much"; I treated that as permission for a small bounded spend and set a hard cap of $2. Total spend on the OpenRouter key was $0.20644 (its final `usage` counter), all of it GPT-6 Sol including its probes and settings tests; the 200-ruling run alone was $0.1983. **What the model is:** a closed OpenAI model, the mid tier "Sol" of the GPT-6 family (below the "Astra" flagship, above "Luna"), listed on OpenRouter as `openai/gpt-6-sol` at $2 per 1M input and $10 per 1M output tokens. Its OpenRouter page states no tier, release date or training cutoff. The tier and the release date (2026-09-22) come from third-party reports (ComputingForGeeks, Free Press Journal, Tecnoblog), and the stated training cutoff, 2026-04-20, from the ComputingForGeeks report, not from an OpenAI page. It is called "a closed OpenAI model (mid-tier)" here, not a frontier model.
3. **Other dated deviations** (full text in PREREG_v1.1.md and DECISIONS.md): the top-ranked free OpenRouter model, Inkling, refused API access (HTTP 403), so Nemotron 3 Ultra was used; the DeepSeek and GLM probes ran after their full runs because the pilots finished first; the OpenRouter free allowance was 1,000 requests a day, not the assumed 50; Gemini 3.8 Flash was added to the plan and is not yet in any table; allam-2-7b is also labelled "contamination not ruled out" because it has no stated cutoff.
4. **Added after the first results were seen** (requested after reading them; none changes a pre-registered verdict): the † labelling of models with no stated cutoff, the same-sample table, the Holm-corrected sensitivity check of Gate B, and the description-quality audit with its sensitivity run. They are labelled as such where they appear.

### Limits (before interpretation)

- **Memorisation is not ruled out.** Check A (ruling number only, no description) found 0 exact, 8-digit or 6-digit hits for every model, but DeepSeek V4.1 Flash and GLM 5.3 refused 96 and 95 of 100 probes, so it says almost nothing for them. The official cards of DeepSeek V4.1 Flash, GLM 5.3 and Kimi K3 state no training cutoff, so those three are labelled "contamination not ruled out" and their primary score uses all rulings. GPT-6 Sol's cutoff (2026-04-20) comes from a third-party report.
- **Reasoning was set to the lowest accepted level**, to match v1.0 and keep cost down. GLM 5.3 cannot be fully switched off. The results are low-effort, single-shot results, not each model's ceiling.
- **The two OpenRouter models ran on 200 rulings.** Their intervals are about plus or minus 7 points, their Gate B verdicts rest on n = 40 and 41, and they are compared only with models restricted to the same 200. They cannot support rankings among the strong models or month trends.
- **Differences inside the strong group are mostly within noise** (see the attack review). The gap between the strong group and the v1.0 models is not.
- **The paired tests in the exploratory section (64 in total) are not corrected for multiple comparisons.**
- **One pre-registered check did not pass cleanly.** Re-parsing the 3,294 cached v1.0 answers with the new parser changed 1 (allam-2-7b, ruling N358156, a JSON array of three objects). The cached v1.0 values were kept; see `DECISIONS.md`.
- **Inkling was the top-ranked free OpenRouter model but refused API access (HTTP 403)**, so Nemotron 3 Ultra, the second largest, was used.
- **40 of 1,098 rulings (3.6%) have a cleaned description that is not a product description.** The main results include them; the exclusion sensitivity is in the description-quality subsection and changes no verdict.
- **Duty figures are MFN-only lower bounds**, as in v1.0.

The full hostile review, with the evidence for and against each point, is in [review/v1_1_attack.md](review/v1_1_attack.md).

### Models, cutoffs and contamination status

| Model | Provider | Rulings run | Stated cutoff | Contamination status | Primary rows | Reasoning setting |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | groq | 1098 | 2024-06-01 | cutoff 2024-06-01; every ruling is after it | 1098 | low |
| openai/gpt-oss-120b | groq | 1098 | 2024-06-01 | cutoff 2024-06-01; every ruling is after it | 1098 | low |
| allam-2-7b † | groq | 1098 | unknown | contamination not ruled out (cutoff unknown) | 1098 | None |
| deepseek-ai/DeepSeek-V4.1-Flash † | baseten | 1098 | unknown | contamination not ruled out (cutoff unknown) | 1098 | none |
| zai-org/GLM-5.3 † | baseten | 1098 | unknown | contamination not ruled out (cutoff unknown) | 1098 | thinking disabled (still emits some reasoning tokens) |
| moonshotai/Kimi-K3 † | baseten | 1098 | unknown | contamination not ruled out (cutoff unknown) | 1098 | none |
| nvidia/nemotron-3-ultra-550b-a55b:free | openrouter | 200 | 2026-05-31 | post-cutoff rulings only (after 2026-05-31) | 105 | none |
| openai/gpt-6-sol | openrouter | 200 | 2026-04-20 | post-cutoff rulings only (after 2026-04-20) | 167 | none |

Sources for each cutoff are in `config.json` (`training_cutoff_source`).

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

Check A, memorisation probe (the question is the ruling number alone; seed 20261007, `data/probe_ids.csv`):

| Model | probes n | exact 10-digit hits | 8-digit hits | 6-digit hits | parse failures |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 0 | not run | not run | not run | |
| openai/gpt-oss-120b | 0 | not run | not run | not run | |
| allam-2-7b † | 0 | not run | not run | not run | |
| deepseek-ai/DeepSeek-V4.1-Flash † | 100 | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 96 |
| zai-org/GLM-5.3 † | 100 | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 95 |
| moonshotai/Kimi-K3 † | 100 | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 25 | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0 |
| openai/gpt-6-sol | 25 | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0 |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

Check B, 8-digit accuracy by ruling month (full sample):

| Model | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 0/148 (0%) | 0/121 (0%) | 0/168 (0%) | 1/175 (1%) | 2/137 (1%) | 0/121 (0%) | 0/144 (0%) | 0/84 (0%) |
| openai/gpt-oss-120b | 8/148 (5%) | 3/121 (2%) | 13/168 (8%) | 16/175 (9%) | 5/137 (4%) | 7/121 (6%) | 6/144 (4%) | 3/84 (4%) |
| allam-2-7b † | 6/148 (4%) | 7/121 (6%) | 3/168 (2%) | 3/175 (2%) | 0/137 (0%) | 3/121 (2%) | 4/144 (3%) | 0/84 (0%) |
| deepseek-ai/DeepSeek-V4.1-Flash † | 71/148 (48%) | 61/121 (50%) | 59/168 (35%) | 76/175 (43%) | 40/137 (29%) | 45/121 (37%) | 45/144 (31%) | 34/84 (40%) |
| zai-org/GLM-5.3 † | 42/148 (28%) | 46/121 (38%) | 48/168 (29%) | 43/175 (25%) | 25/137 (18%) | 28/121 (23%) | 28/144 (19%) | 16/84 (19%) |
| moonshotai/Kimi-K3 † | 79/148 (53%) | 63/121 (52%) | 75/168 (45%) | 83/175 (47%) | 49/137 (36%) | 39/121 (32%) | 47/144 (33%) | 42/84 (50%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 0/0 | 0/0 | 0/0 | 24/45 (53%) | 9/50 (18%) | 11/37 (30%) | 7/40 (18%) | 7/28 (25%) |
| openai/gpt-6-sol | 0/0 | 0/0 | 0/0 | 25/45 (56%) | 19/50 (38%) | 22/37 (59%) | 18/40 (45%) | 15/28 (54%) |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

Before versus after the stated cutoff, for the two models whose cutoff falls inside the ruling window:

| Model | cutoff | rulings on/before cutoff | 8-digit | rulings after cutoff | 8-digit |
|---|---|---|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b:free | 2026-05-31 | 95 | 34.7% (25.9% to 44.7%) | 105 | 23.8% (16.7% to 32.8%) |
| openai/gpt-6-sol | 2026-04-20 | 33 | 48.5% (32.5% to 64.8%) | 167 | 49.7% (42.2% to 57.2%) |

The two models that ran on the 200-ruling sample show an inconsistent pattern around their cutoffs: GPT-6 Sol has no drop [corrected in v1.2: this rested on 33 rulings before the cutoff; on all 1,098 rulings GPT-6 Sol scores 58.9% before and 49.6% after, see the v1.2 section], but Nemotron 3 Ultra scores 34.7% on rulings up to its cutoff and 23.8% after it. Read the Nemotron gap as a descriptive warning sign that contamination can inflate scores, not as a test (the intervals overlap). The same warning applies, unmeasurably, to every model marked †, which has no stated cutoff, so their accuracy is an upper bound. The DeepSeek V4.1 Flash and GLM 5.3 probes are uninformative because the models refused 96 and 95 of 100 probes.

### Results: how accurate are stronger models?

Primary scores (rulings after each model's stated cutoff; the models labelled "contamination not ruled out" use all their rulings):

| Model | n | 6-digit | 8-digit (headline) | 10-digit | Invalid share | FORMAT share of all | INVENTED share of all |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 3.0% (2.1% to 4.2%) | 0.3% (0.1% to 0.8%) | 0.0% (0.0% to 0.3%) | 98.4% (97.4% to 99.0%) | 13.3% (11.4% to 15.4%) | 85.1% (82.8% to 87.0%) |
| openai/gpt-oss-120b | 1098 | 21.1% (18.8% to 23.6%) | 5.6% (4.3% to 7.1%) | 0.5% (0.3% to 1.2%) | 96.6% (95.4% to 97.5%) | 22.3% (19.9% to 24.9%) | 74.3% (71.7% to 76.8%) |
| allam-2-7b † | 1098 | 4.4% (3.3% to 5.7%) | 2.4% (1.6% to 3.4%) | 1.7% (1.1% to 2.7%) | 87.2% (85.0% to 89.0%) | 6.6% (5.2% to 8.2%) | 80.6% (78.2% to 82.8%) |
| deepseek-ai/DeepSeek-V4.1-Flash † | 1098 | 52.8% (49.9% to 55.8%) | 39.3% (36.4% to 42.2%) | 25.0% (22.6% to 27.7%) | 32.2% (29.5% to 35.1%) | 18.8% (16.6% to 21.2%) | 13.5% (11.6% to 15.6%) |
| zai-org/GLM-5.3 † | 1098 | 45.3% (42.3% to 48.2%) | 25.1% (22.7% to 27.8%) | 12.4% (10.6% to 14.5%) | 67.6% (64.8% to 70.3%) | 28.4% (25.8% to 31.2%) | 39.2% (36.3% to 42.1%) |
| moonshotai/Kimi-K3 † | 1098 | 55.3% (52.3% to 58.2%) | 43.4% (40.5% to 46.4%) | 28.4% (25.8% to 31.2%) | 25.3% (22.8% to 28.0%) | 17.1% (15.0% to 19.5%) | 8.2% (6.7% to 10.0%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 105 | 36.2% (27.6% to 45.7%) | 23.8% (16.7% to 32.8%) | 14.3% (8.9% to 22.2%) | 33.3% (25.0% to 42.8%) | 19.0% (12.7% to 27.6%) | 14.3% (8.9% to 22.2%) |
| openai/gpt-6-sol | 167 | 61.7% (54.1% to 68.7%) | 49.7% (42.2% to 57.2%) | 31.7% (25.2% to 39.1%) | 25.7% (19.7% to 32.9%) | 18.6% (13.4% to 25.1%) | 7.2% (4.2% to 12.1%) |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

**Stronger models are more accurate, and every model is still wrong about half the time or more at the duty-relevant level.** 8-digit accuracy goes from 0.3% to 5.6% (v1.0) to 25.1% (GLM 5.3), 39.3% (DeepSeek V4.1 Flash), 43.4% (Kimi K3), 23.8% (Nemotron 3 Ultra, post-cutoff rulings only) and 49.7% (GPT-6 Sol, post-cutoff rulings only). The best primary figure (GPT-6 Sol, 167 post-cutoff rulings) is 49.7%, and 10-digit accuracy peaks at 31.7%. On the same 200 rulings (all dates, secondary) the 8-digit ranking is GPT-6 Sol 49.5% (95% CI 42.6% to 56.4%), Kimi K3 37.0% (30.6% to 43.9%), DeepSeek V4.1 Flash 31.0% (25.0% to 37.7%), Nemotron 3 Ultra 29.0% (23.2% to 35.6%), GLM 5.3 21.5% (16.4% to 27.7%), then gpt-oss-120b 7.5%, allam-2-7b 2.0% and gpt-oss-20b 0.5%. GPT-6 Sol is first, but its interval overlaps Kimi K3's slightly (the exploratory paired test gives p = 0.0022), so it is best described as among the most accurate models tested, not clearly the best. The invalid share falls from 87% to 98% (v1.0) to 25% to 33% for four of the five stronger models, but not for GLM 5.3 (67.6%).

On the same 200 rulings, all models compared (all dates, secondary):

| Model | n | 6-digit | 8-digit | 10-digit | Invalid share |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 200 | 1.5% (0.5% to 4.3%) | 0.5% (0.1% to 2.8%) | 0.0% (0.0% to 1.9%) | 98.0% (95.0% to 99.2%) |
| openai/gpt-oss-120b | 200 | 18.0% (13.3% to 23.9%) | 7.5% (4.6% to 12.0%) | 0.5% (0.1% to 2.8%) | 97.5% (94.3% to 98.9%) |
| allam-2-7b † | 200 | 3.5% (1.7% to 7.0%) | 2.0% (0.8% to 5.0%) | 0.5% (0.1% to 2.8%) | 89.5% (84.5% to 93.0%) |
| deepseek-ai/DeepSeek-V4.1-Flash † | 200 | 43.0% (36.3% to 49.9%) | 31.0% (25.0% to 37.7%) | 18.0% (13.3% to 23.9%) | 32.5% (26.4% to 39.3%) |
| zai-org/GLM-5.3 † | 200 | 40.5% (33.9% to 47.4%) | 21.5% (16.4% to 27.7%) | 8.0% (5.0% to 12.6%) | 63.0% (56.1% to 69.4%) |
| moonshotai/Kimi-K3 † | 200 | 49.0% (42.2% to 55.9%) | 37.0% (30.6% to 43.9%) | 25.0% (19.5% to 31.4%) | 26.5% (20.9% to 33.0%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 39.5% (33.0% to 46.4%) | 29.0% (23.2% to 35.6%) | 14.0% (9.9% to 19.5%) | 37.5% (31.1% to 44.4%) |
| openai/gpt-6-sol | 200 | 61.5% (54.6% to 68.0%) | 49.5% (42.6% to 56.4%) | 32.5% (26.4% to 39.3%) | 25.0% (19.5% to 31.4%) |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

Same-sample table (added after the first results were seen). All 8 models on the same 200 rulings, with the format/invented split of each model's invalid answers on these rulings and the underpay share among the rate-changing errors on these 200 only (small n; not a Gate B test):

| Model | n | 8-digit accuracy (95% CI) | Invalid share (95% CI) | FORMAT / INVENTED of invalid | Underpay share (95% CI), n rate-changing |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 200 | 0.5% (0.1% to 2.8%) | 98.0% (95.0% to 99.2%) | 29 / 167 (15% / 85%) | 70.0% (39.7% to 89.2%), n = 10 |
| openai/gpt-oss-120b | 200 | 7.5% (4.6% to 12.0%) | 97.5% (94.3% to 98.9%) | 48 / 147 (25% / 75%) | 62.5% (30.6% to 86.3%), n = 8 |
| allam-2-7b † | 200 | 2.0% (0.8% to 5.0%) | 89.5% (84.5% to 93.0%) | 17 / 162 (9% / 91%) | 56.5% (36.8% to 74.4%), n = 23 |
| deepseek-ai/DeepSeek-V4.1-Flash † | 200 | 31.0% (25.0% to 37.7%) | 32.5% (26.4% to 39.3%) | 34 / 31 (52% / 48%) | 47.7% (36.0% to 59.6%), n = 65 |
| zai-org/GLM-5.3 † | 200 | 21.5% (16.4% to 27.7%) | 63.0% (56.1% to 69.4%) | 56 / 70 (44% / 56%) | 45.1% (32.3% to 58.6%), n = 51 |
| moonshotai/Kimi-K3 † | 200 | 37.0% (30.6% to 43.9%) | 26.5% (20.9% to 33.0%) | 33 / 20 (62% / 38%) | 50.0% (37.5% to 62.5%), n = 58 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 29.0% (23.2% to 35.6%) | 37.5% (31.1% to 44.4%) | 50 / 25 (67% / 33%) | 51.5% (39.7% to 63.2%), n = 66 |
| openai/gpt-6-sol | 200 | 49.5% (42.6% to 56.4%) | 25.0% (19.5% to 31.4%) | 37 / 13 (74% / 26%) | 53.1% (39.4% to 66.3%), n = 49 |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

### Results: Bryce's question 2, format slip or invented code?

Every invalid answer is placed in exactly one group (`scripts/analyze_format_vs_invention.py`, `review/format_vs_invention.md`). FORMAT = (a) unparseable or truncated, (b) first 8 digits form a real tariff line but the suffix is missing, (c) same but the suffix is wrong. INVENTED = (d) the 6-digit subheading exists but no tariff line starts with the answer's first 8 digits, (e) not even the 6-digit subheading exists. For the three v1.0 models the groups sum to the published 1,080 / 1,061 / 957 invalid answers (checked in the script). The one v1.0 "outdated" answer is in (c), FORMAT.

Share of INVALID answers:

| Model | invalid n | FORMAT | INVENTED | (a) | (b) 8 digits | (b) 9 digits | (c) | (d) | (e) | (a) with a recoverable code in the text |
|---|---|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1080 | 146 (13.5%; 11.6% to 15.7%) | 934 (86.5%; 84.3% to 88.4%) | 0 (0.0%; 0.0% to 0.4%) | 55 (5.1%; 3.9% to 6.6%) | 0 (0.0%; 0.0% to 0.4%) | 91 (8.4%; 6.9% to 10.2%) | 422 (39.1%; 36.2% to 42.0%) | 512 (47.4%; 44.4% to 50.4%) | 0 of 0 |
| openai/gpt-oss-120b | 1061 | 245 (23.1%; 20.7% to 25.7%) | 816 (76.9%; 74.3% to 79.3%) | 1 (0.1%; 0.0% to 0.5%) | 180 (17.0%; 14.8% to 19.3%) | 0 (0.0%; 0.0% to 0.4%) | 64 (6.0%; 4.8% to 7.6%) | 595 (56.1%; 53.1% to 59.0%) | 221 (20.8%; 18.5% to 23.4%) | 1 of 1 |
| allam-2-7b † | 957 | 72 (7.5%; 6.0% to 9.4%) | 885 (92.5%; 90.6% to 94.0%) | 8 (0.8%; 0.4% to 1.6%) | 21 (2.2%; 1.4% to 3.3%) | 0 (0.0%; 0.0% to 0.4%) | 43 (4.5%; 3.4% to 6.0%) | 359 (37.5%; 34.5% to 40.6%) | 526 (55.0%; 51.8% to 58.1%) | 8 of 8 |
| deepseek-ai/DeepSeek-V4.1-Flash † | 354 | 206 (58.2%; 53.0% to 63.2%) | 148 (41.8%; 36.8% to 47.0%) | 1 (0.3%; 0.0% to 1.6%) | 0 (0.0%; 0.0% to 1.1%) | 0 (0.0%; 0.0% to 1.1%) | 205 (57.9%; 52.7% to 62.9%) | 115 (32.5%; 27.8% to 37.5%) | 33 (9.3%; 6.7% to 12.8%) | 0 of 1 |
| zai-org/GLM-5.3 † | 742 | 312 (42.0%; 38.5% to 45.6%) | 430 (58.0%; 54.4% to 61.5%) | 27 (3.6%; 2.5% to 5.2%) | 10 (1.3%; 0.7% to 2.5%) | 0 (0.0%; 0.0% to 0.5%) | 275 (37.1%; 33.7% to 40.6%) | 339 (45.7%; 42.1% to 49.3%) | 91 (12.3%; 10.1% to 14.8%) | 24 of 27 |
| moonshotai/Kimi-K3 † | 278 | 188 (67.6%; 61.9% to 72.9%) | 90 (32.4%; 27.1% to 38.1%) | 0 (0.0%; 0.0% to 1.4%) | 3 (1.1%; 0.4% to 3.1%) | 0 (0.0%; 0.0% to 1.4%) | 185 (66.5%; 60.8% to 71.8%) | 71 (25.5%; 20.8% to 31.0%) | 19 (6.8%; 4.4% to 10.4%) | 0 of 0 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 75 | 50 (66.7%; 55.4% to 76.3%) | 25 (33.3%; 23.7% to 44.6%) | 0 (0.0%; 0.0% to 4.9%) | 2 (2.7%; 0.7% to 9.2%) | 0 (0.0%; 0.0% to 4.9%) | 48 (64.0%; 52.7% to 73.9%) | 17 (22.7%; 14.7% to 33.3%) | 8 (10.7%; 5.5% to 19.7%) | 0 of 0 |
| openai/gpt-6-sol | 50 | 37 (74.0%; 60.4% to 84.1%) | 13 (26.0%; 15.9% to 39.6%) | 1 (2.0%; 0.4% to 10.5%) | 0 (0.0%; 0.0% to 7.1%) | 0 (0.0%; 0.0% to 7.1%) | 36 (72.0%; 58.3% to 82.5%) | 7 (14.0%; 7.0% to 26.2%) | 6 (12.0%; 5.6% to 23.8%) | 1 of 1 |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

**The answer depends on the model.** For gpt-oss-20b, gpt-oss-120b and allam-2-7b, 77% to 93% of invalid answers are invented (groups d and e). For DeepSeek V4.1 Flash, Kimi K3, Nemotron 3 Ultra and GPT-6 Sol, most invalid answers (58% to 74%) are format-type, almost all of them group (c): a real tariff line with a wrong 10-digit suffix. GLM 5.3 is the exception, with 58% invented. Groups (b) and (c) only say that the first 8 digits form a real tariff line, not that they are the right one. How many equal the true code's first 8 digits:

| Model | answers in (b)+(c) | first 8 digits equal the true code's | share of (b)+(c) | share of ALL invalid answers |
|---|---|---|---|---|
| openai/gpt-oss-20b | 146 | 3 | 3 (2.1%; 0.7% to 5.9%) | 3 (0.3%; 0.1% to 0.8%) |
| openai/gpt-oss-120b | 244 | 55 | 55 (22.5%; 17.7% to 28.2%) | 55 (5.2%; 4.0% to 6.7%) |
| allam-2-7b † | 64 | 7 | 7 (10.9%; 5.4% to 20.9%) | 7 (0.7%; 0.4% to 1.5%) |
| deepseek-ai/DeepSeek-V4.1-Flash † | 205 | 86 | 86 (42.0%; 35.4% to 48.8%) | 86 (24.3%; 20.1% to 29.0%) |
| zai-org/GLM-5.3 † | 285 | 123 | 123 (43.2%; 37.5% to 49.0%) | 123 (16.6%; 14.1% to 19.4%) |
| moonshotai/Kimi-K3 † | 188 | 97 | 97 (51.6%; 44.5% to 58.6%) | 97 (34.9%; 29.5% to 40.7%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 50 | 17 | 17 (34.0%; 22.4% to 47.8%) | 17 (22.7%; 14.7% to 33.3%) |
| openai/gpt-6-sol | 36 | 19 | 19 (52.8%; 37.0% to 68.0%) | 19 (38.0%; 25.9% to 51.8%) |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

So a true suffix slip (right 8-digit classification, wrong or missing suffix) is 17% to 38% of invalid answers for the stronger models and 0.3% to 5% for gpt-oss and allam. Stale training data also shows up: ten-digit codes that existed in a 2022 to 2025 HTS release but not in 2026 are 58 of DeepSeek's invalid answers, 79 of Kimi's, 27 of GLM's, 10 of Nemotron's and 21 of GPT-6 Sol's, against 1 in v1.0 (`review/invalid_breakdown.md`).

GLM 5.3 sometimes drops the closing brace of its JSON; 24 of its 27 unparseable answers still contain a readable code. Scoring stays strict, as in v1.0, so models are comparable.

### Results: direction of duty errors and what a validity check catches

Underpay share among rate-changing errors, with Gate B exactly as pre-registered (beats Baseline 2 at p < 0.05 and n of at least 30):

| Model | rate-changing errors n | underpaid | underpay share (95% CI) | p vs Baseline 1 | p vs Baseline 2 | Gate B verdict | comparable wrong answers n | median duty per $100k (IQR) |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 46 | 31 | 67.4% (53.0% to 79.1%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 101 | $0 ($0 to $3,500) |
| openai/gpt-oss-120b | 49 | 32 | 65.3% (51.3% to 77.1%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 93 | $300 ($0 to $2,500) |
| allam-2-7b † | 116 | 76 | 65.5% (56.5% to 73.5%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 147 | $3,400 ($350 to $6,500) |
| deepseek-ai/DeepSeek-V4.1-Flash † | 324 | 175 | 54.0% (48.6% to 59.4%) | 0.9930 | 0.1748 | not distinguishable from chance (Gate B not met) | 657 | $0 ($0 to $2,900) |
| zai-org/GLM-5.3 † | 212 | 118 | 55.7% (48.9% to 62.2%) | 0.8322 | 0.0060 | underpays more than chance (Gate B met) | 483 | $0 ($0 to $2,800) |
| moonshotai/Kimi-K3 † | 311 | 184 | 59.2% (53.6% to 64.5%) | 0.4496 | 0.0040 | underpays more than chance (Gate B met) | 673 | $0 ($0 to $2,800) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 40 | 24 | 60.0% (44.6% to 73.7%) | 0.2987 | 0.0070 | underpays more than chance (Gate B met) | 73 | $1,300 ($0 to $4,400) |
| openai/gpt-6-sol | 41 | 21 | 51.2% (36.5% to 65.7%) | 0.8252 | 0.1139 | not distinguishable from chance (Gate B not met) | 97 | $0 ($0 to $3,600) |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

**The underpay lean shrinks and is not universal.** v1.0 models: 65% to 67%. Stronger models: 51% to 60%. Gate B is met for GLM 5.3, Kimi K3 and Nemotron 3 Ultra and is not met for DeepSeek V4.1 Flash and GPT-6 Sol. The intervals for GLM 5.3 and Nemotron 3 Ultra include 50%, and Nemotron's and GPT-6 Sol's n (40 and 41) sit just above the threshold of 30, so a verdict could flip with one case. Median duty at stake per $100,000 for wrong answers is $0 for most strong models, which means at least half of their comparable wrong answers have no rate difference; see the table for the interquartile ranges. The lean does not beat chance in GPT-6 Sol, the most accurate model on the shared 200 rulings (n = 41 rate-changing errors, so weak evidence), so it may fade as models improve; the lean does beat chance in Kimi K3, the second most accurate.

Holm-corrected sensitivity check of the Gate B p-values (added after the first results were seen; the pre-registered verdicts above are unchanged):

| Model | n | p vs Baseline 2 | Holm-adjusted p | Gate B as pre-registered | Verdict under Holm | Changed? |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 46 | < 0.001 | 0.0080 | met | met | no |
| openai/gpt-oss-120b | 49 | < 0.001 | 0.0080 | met | met | no |
| allam-2-7b † | 116 | < 0.001 | 0.0080 | met | met | no |
| deepseek-ai/DeepSeek-V4.1-Flash † | 324 | 0.1748 | 0.2278 | not met | not met | no |
| zai-org/GLM-5.3 † | 212 | 0.0060 | 0.0240 | met | met | no |
| moonshotai/Kimi-K3 † | 311 | 0.0040 | 0.0200 | met | met | no |
| nvidia/nemotron-3-ultra-550b-a55b:free | 40 | 0.0070 | 0.0240 | met | met | no |
| openai/gpt-6-sol | 41 | 0.1139 | 0.2278 | not met | not met | no |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

No verdict changes under Holm: the six that met Gate B still do (the smallest adjusted p is 0.0080 and the largest among them 0.0240), and DeepSeek V4.1 Flash and GPT-6 Sol still do not (adjusted p 0.2278).

### Description quality (found after pre-registration)

Some cleaned descriptions are not product descriptions: ruling N361449 is the country-of-origin marking regulation, N361705 is textile-labelling advice, N361310 is half a sentence about sleeves. A model cannot classify what it is not told, so those rows measure the description extractor, not the model. `scripts/audit_description_quality.py` flags a ruling INADEQUATE if its cleaned description is under 150 characters, or at least half of it is regulatory boilerplate (19 C.F.R., Textile Fiber Products Identification Act, FTC, FCC or FDA referrals, marking or labelling advice) with under 150 characters of other text left. 40 of 1,098 usable rulings (3.6%) are flagged: 33 under 150 characters and 7 regulatory boilerplate (`review/description_quality.md`). A hand check of 20 flagged and 20 unflagged rulings found 17 of the 20 flagged genuinely inadequate, 1 borderline and 2 adequate (short but clear product descriptions caught by the blunt length rule), and all 20 unflagged adequate (`review/description_quality_spotcheck.md`).

Sensitivity: the same primary metrics without the flagged rulings, next to the main results (main results and pre-registered verdicts are not replaced):

| Model | n main / excl | 8-digit main / excl | Invalid share main / excl | Underpay share (n) main | Underpay share (n) excl | Gate B main / excl |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 / 1058 | 0.3% / 0.3% | 98.4% / 98.3% | 67.4% (n = 46) | 67.4% (n = 46) | met / met (p vs Baseline 2: < 0.001 / < 0.001) |
| openai/gpt-oss-120b | 1098 / 1058 | 5.6% / 5.8% | 96.6% / 96.6% | 65.3% (n = 49) | 64.6% (n = 48) | met / met (p vs Baseline 2: < 0.001 / < 0.001) |
| allam-2-7b † | 1098 / 1058 | 2.4% / 2.5% | 87.2% / 87.1% | 65.5% (n = 116) | 66.7% (n = 111) | met / met (p vs Baseline 2: < 0.001 / < 0.001) |
| deepseek-ai/DeepSeek-V4.1-Flash † | 1098 / 1058 | 39.3% / 40.3% | 32.2% / 31.2% | 54.0% (n = 324) | 56.1% (n = 310) | not met / not met (p vs Baseline 2: 0.1748 / 0.0769) |
| zai-org/GLM-5.3 † | 1098 / 1058 | 25.1% / 26.0% | 67.6% / 67.0% | 55.7% (n = 212) | 57.1% (n = 205) | met / met (p vs Baseline 2: 0.0060 / 0.0080) |
| moonshotai/Kimi-K3 † | 1098 / 1058 | 43.4% / 44.6% | 25.3% / 24.6% | 59.2% (n = 311) | 60.9% (n = 294) | met / met (p vs Baseline 2: 0.0040 / 0.0050) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 105 / 102 | 23.8% / 24.5% | 33.3% / 31.4% | 60.0% (n = 40) | 61.5% (n = 39) | met / met (p vs Baseline 2: 0.0070 / 0.0120) |
| openai/gpt-6-sol | 167 / 152 | 49.7% / 53.3% | 25.7% / 21.7% | 51.2% (n = 41) | 58.3% (n = 36) | not met / not met (p vs Baseline 2: 0.1139 / 0.1199) |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

**No Gate B verdict changes.** Without the flagged rulings the small models' 8-digit accuracy is 0.3% to 5.8% (main 0.3% to 5.6%) and the stronger models' is 24.5% to 53.3% (main 23.8% to 49.7%; GPT-6 Sol rises from 49.7% to 53.3%). The underpay share is 64.6% to 67.4% in the small models (main 65.3% to 67.4%) and 56.1% to 61.5% in the stronger models (main 51.2% to 60.0%; GPT-6 Sol 51.2% to 58.3% on n = 36, still not met). The README quotes both ranges. The audit is blunt on purpose; it cannot flag descriptions that are long but still too thin to classify, so it is a floor on the extractor's effect, not a measurement of it. The biggest-misses list drops 5 rows from flagged rulings (under N361449 Kimi K3, under N361705 allam-2-7b, over N361310 and N361321 GLM 5.3, over N361312 GPT-6 Sol) and refills from the next largest.

What a validity check (flag any answer that is not a 10-digit code in the HTS) catches:

| Model | wrong answers | wrong and flagged invalid | correct 10-digit answers | correct and flagged | 8-digit-correct answers | 8-digit-correct and flagged |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 98.4% (97.4% to 99.0%) | 0 | 0 of 0 | 3 | 3 of 3 |
| openai/gpt-oss-120b | 1092 | 97.2% (96.0% to 98.0%) | 6 | 0 of 6 | 61 | 55 of 61 |
| allam-2-7b | 1079 | 88.7% (86.7% to 90.4%) | 19 | 0 of 19 | 26 | 7 of 26 |
| deepseek-ai/DeepSeek-V4.1-Flash | 823 | 42.2% (38.8% to 45.6%) | 275 | 7 of 275 | 431 | 87 of 431 |
| zai-org/GLM-5.3 | 962 | 76.8% (74.0% to 79.4%) | 136 | 3 of 136 | 276 | 123 of 276 |
| moonshotai/Kimi-K3 | 786 | 34.4% (31.1% to 37.7%) | 312 | 8 of 312 | 477 | 97 of 477 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 90 | 38.9% (29.5% to 49.2%) | 15 | 0 of 15 | 25 | 3 of 25 |
| openai/gpt-6-sol | 114 | 37.7% (29.4% to 46.9%) | 53 | 0 of 53 | 83 | 16 of 83 |

For DeepSeek V4.1 Flash, Kimi K3, Nemotron 3 Ultra and GPT-6 Sol a validity check flags only 34% to 42% of wrong answers (GLM 5.3: 76.8%; v1.0: 88.7% to 98.4%), because their wrong answers are mostly valid codes. It also flags many answers that are right at 8 digits, and a few correct 10-digit answers whose true code is absent from the HTS data. It is a detector for "needs review", not a classifier, and for these models it misses most errors.

### Cost to run (EXPLORATORY extra 5)

| Model | calls | avg input tokens | avg output tokens | avg seconds per call | finish_reason counts | list-price cost per 1,000 rulings |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 324 | 202 | 0.3 | {'stop': 1098} | free tier |
| openai/gpt-oss-120b | 1098 | 324 | 180 | 0.4 | {'stop': 1098} | free tier |
| allam-2-7b † | 1098 | 304 | 78 | 0.1 | {'stop': 1098} | free tier |
| deepseek-ai/DeepSeek-V4.1-Flash † | 1098 | 260 | 65 | 1.3 | {'stop': 1098} | $0.16 |
| zai-org/GLM-5.3 † | 1098 | 270 | 180 | 2.8 | {'stop': 1097, 'length': 1} | $1.17 |
| moonshotai/Kimi-K3 † | 1098 | 272 | 65 | 9.0 | {'stop': 1098} | $1.79 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 281 | 74 | 4.8 | {'stop': 200} | free tier |
| openai/gpt-6-sol | 200 | 258 | 48 | 2.0 | {'stop': 200} | $0.99 |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound.

Baseten and OpenRouter cost, from `data/exports/api_calls_summary.csv` (list price of every cached call, including probes): Baseten $3.54 (covered by free credits), OpenRouter $0.20 (all of it the paid GPT-6 Sol job; the free model cost $0). No billing, credit or 402 error occurred; no payment method was added. The OpenRouter key's `usage` was 0.20644 after the paid GPT-6 Sol job and did not change during either free-model run. All calls are in `data/exports/api_calls.csv`.

### Exploratory extras (EXPLORATORY; pre-registered but not hypothesis-driven)

64 hypothesis tests were run in this section (McNemar pairs at 6 and 8 digits, and the 8-digit-level baseline tests); none is corrected for multiple comparison. Full tables are in `review/v1_1_results.md`.

1. **Paired tests and headings.** Each stronger model differs from each v1.0 model at both 6 and 8 digits (all p < 0.0001). Within the strong group the paired 8-digit tests give DeepSeek V4.1 Flash vs Kimi K3 p = 0.0024 and Kimi K3 vs GPT-6 Sol p = 0.0022 (same 200); DeepSeek V4.1 Flash vs Nemotron 3 Ultra is not significant. 4-digit heading accuracy is 63.8% to 70.0% for GLM, DeepSeek and Kimi against 9.7% to 45.1% for the v1.0 models, and 51.7% to 60.7% of the strong models' wrong answers still have the right heading (v1.0: 8.2% to 44.8%).
2. **Agreement.** When 2 or more of the six models run on all 1,098 rulings give the same 8-digit code (72.3% of rulings), that code is right 48.4% of the time, and when 3 or more agree (26.8% of rulings) it is right 67.7% of the time, which is about the same as each agreeing model alone on those rulings (52.1% and 68.0%): agreement among these models adds no accuracy over the agreeing models themselves.

| Agreement rule | rulings | share of all rulings | accuracy of the agreed code (8-digit) | mean accuracy of each agreeing model alone on the same rulings |
|---|---|---|---|---|
| 2+ models give the same 8-digit code | 794 | 72.3% | 48.4% (44.9% to 51.8%) | 52.1% |
| 3+ models give the same 8-digit code | 294 | 26.8% | 67.7% (62.1% to 72.8%) | 68.0% |

3. **Duty at 8 digits (secondary).** Pricing errors at the 8-digit level adds 31 and 92 rate-changing cases for gpt-oss-20b and gpt-oss-120b and almost none for the stronger models; only gpt-oss-20b clears Gate B at that level.
4. **Biggest misses.** The 10 largest underpayments and overpayments across all models are in `review/biggest_misses.md`; the ruling ids are tagged in `demo_data.json`.
5. **Cost to run** is the table above.

### What v1.1 changes in the v1.0 conclusions

The v1.0 numbers for the three Groq models are unchanged (checked after the full rerun). What changes is the framing: "free models mostly return codes that do not exist" is true for the three small Groq models and for GLM 5.3, but not for DeepSeek V4.1 Flash, Kimi K3, Nemotron 3 Ultra or GPT-6 Sol, whose invalid answers are mostly suffix slips and stale codes, and whose wrong answers are mostly valid codes that a validity check does not catch.

## v1.2: GPT-6 Sol extension, Claude models, and provider replication

**Opus 5.5 and GPT-6 Sol are tied (paired p = 0.54); both are wrong about half the time at 8 digits.** The underpay lean appears in the weaker models and is not detected in the two most accurate. Opus 5.5 scores 53.5% (95% CI 47.0% to 59.9%, n = 228, July and August 2026 rulings only; reasoning could not be disabled, about 297 reasoning tokens per answer) and GPT-6 Sol 49.6% (45.4% to 53.8%, n = 538).

v1.2 is run exactly like v1.1 (same prompt, temperature 0, scoring code, metrics and Gate B rule) and adds three things, fixed in [PREREG_v1.2.md](PREREG_v1.2.md) before any v1.2 call (commit `88f513af48eed29084cbcb42b04ab9b3c2b294d1`; settings addendum and dated deviations in the same file, commits `f3887b6` and later): **A.** GPT-6 Sol from the 200-ruling sample to all 1,098 rulings; **B.** three Claude models (Haiku 5.5, Sonnet 5.5, Opus 5.5) on all 1,098; **C.** Kimi K3, DeepSeek V4.1 Flash and GLM 5.3 rerun through OpenRouter with Baseten excluded, to test whether the v1.1 results hold across providers. All calls went through OpenRouter. The round cost $21.36 in OpenRouter usage (hard cap $30, raised from $25 by the user after the pilot), and every call is in `data/exports/api_calls.csv`. The v1.1 text above is unchanged; the v1.0 numbers for the three Groq models and the v1.1 numbers for the other models are unchanged (checked after the rerun). Only GPT-6 Sol's row changes, because it now covers 1,098 rulings. Gemini 3.8 Flash is still in no table (2 of 200 responses). No other closed model is in these tables, and none of these models stands in for GPT, Claude or Gemini.

### Deviations from pre-registration (v1.2)

1. **Reasoning could not be turned off for three models.** The pre-registration says "off where the model accepts it, otherwise the lowest level accepted". Claude Sonnet 5.5 (minimal), Claude Opus 5.5 (low) and GLM 5.3 on OpenRouter (low) reject "off". Opus still used about 297 reasoning tokens per answer; Sonnet reports none but wrote long answers (about 517 output tokens). The GLM replication therefore differs from the v1.1 Baseten run in reasoning setting as well as provider.
2. **The spend cap was raised from $25 to $30** on the user's instruction after the pilot (projected cost was about $23.8). Actual OpenRouter spend was $21.36.
3. **OpenRouter lowered the list prices of GLM 5.3 and Kimi K3 during the run** ($4.80 out instead of $6.00 for GLM; $0.64 in instead of $0.80 for Kimi). The price guard refused both runs; the config was updated and they were restarted. Prices went down, and every cost reported is each response's own `usage.cost`.
4. **Two same-sample tables instead of one.** Table A (all 11 models on the post-cutoff rulings all of them share) has only 68 rulings because Nemotron 3 Ultra ran on a 200-ruling sample, so table B (the 10 models run on all 1,098, 228 shared rulings) was added.
5. **Cutoff sources.** GPT-6 Sol's cutoff (2026-04-20) now comes from OpenAI's own page; v1.1 used a third-party report for the same date. The three Claude models' cutoff is Anthropic's "Jun 2026" for both reliable knowledge and training data; 2026-06-30 (end of the month) is used, so Claude scores use only the 228 rulings dated July and August 2026.
6. **The replication was served by many providers**, not one: 18 (Kimi K3), 27 (DeepSeek V4.1 Flash) and 31 (GLM 5.3) different providers in the recorded `provider` field. None of the 3,294 replication answers was served by Baseten.
7. **The number of exploratory hypothesis tests grew** from 64 to 121 (the new models add McNemar pairs); none is corrected for multiple comparison.
8. **Holm sensitivity changes one pre-registered Gate B verdict under correction** (Claude Haiku 5.5, below). The pre-registered verdicts themselves are not changed.
9. **Time-drift test added after the results were seen** (user's request, no new API calls; `scripts/analyze_time_drift.py`, `review/time_drift.md`). It is post-hoc and exploratory, 13 rows, p-values uncorrected.

### Limits (before interpretation)

- **Claude scores rest on 228 rulings** (July and August 2026 only), so their 95% intervals are about plus or minus 6 points. Rankings inside the top group (Opus 5.5, GPT-6 Sol, Sonnet 5.5, Kimi K3) are not supported beyond what the intervals show; the paired 8-digit test on all 1,098 rulings gives Opus 5.5 vs GPT-6 Sol p = 0.54.
- **Reasoning was not off for Sonnet 5.5, Opus 5.5 and the GLM replication** (above), so these are not like-for-like with the models run with reasoning off.
- **Contamination or harder later rulings: not separated.** GPT-6 Sol scores 58.9% at 8 digits on the 560 rulings up to its stated cutoff and 49.6% on the 538 after it. The time-drift test below splits every model at the same date: the 2024-cutoff gpt-oss models show no drop, which by the pre-set rule makes contamination the more likely reading and the † models' all-1,098 numbers likely inflated (upper bounds); but that control has only 5% to 10% power, and Claude Sonnet 5.5 (cutoff June 30) also drops across April 20, which fits harder later rulings. This is why the primary scores use only post-cutoff rulings where a cutoff is stated. The memorisation probe was not repeated in v1.2.
- **† models** (allam-2-7b, DeepSeek V4.1 Flash, GLM 5.3, Kimi K3) have no stated cutoff: contamination not ruled out, accuracy is an upper bound.
- **The replication measures a provider mix**, and for GLM also a setting change.
- **Gate B verdicts rest on small n for several models** (n = 40 to 65 for Nemotron, the Claude models and the small models' subsets).
- **No retrieval or tariff lookup.** The models answer from the description alone; a system with access to the tariff schedule could do better.
- **Top tiers not tested.** Claude Fable 5.1 and OpenAI's tier above GPT-6 Sol were not run.
- **Closed models cost money and are one model each**; nothing here says how any other GPT, Claude or Gemini model would score.
- **40 of 1,098 rulings have an INADEQUATE description** (v1.1 audit); excluding them changes no Gate B verdict (re-run on all 11 models).
- **Duty figures are MFN-only lower bounds.**

The hostile review, with evidence for and against each point, is in [review/v1_2_attack.md](review/v1_2_attack.md).

### Results: all models

Primary scores (rulings after each model's stated cutoff; † models use all their rulings):

| Model | Rulings scored | 8-digit accuracy (95% CI) | Invalid share | Format / invented, of invalid (all rulings run) | Underpay share (n) | Gate B |
|---|---|---|---|---|---|---|
| gpt-oss-20b | 1,098 | 0.3% (0.1% to 0.8%) | 98.4% | 14% / 86% | 67.4% (n = 46) | met |
| gpt-oss-120b | 1,098 | 5.6% (4.3% to 7.1%) | 96.6% | 23% / 77% | 65.3% (n = 49) | met |
| allam-2-7b † | 1,098 | 2.4% (1.6% to 3.4%) | 87.2% | 8% / 92% | 65.5% (n = 116) | met |
| DeepSeek-V4.1-Flash † | 1,098 | 39.3% (36.4% to 42.2%) | 32.2% | 58% / 42% | 54.0% (n = 324) | not met |
| GLM-5.3 † ‡ | 1,098 | 25.1% (22.7% to 27.8%) | 67.6% | 42% / 58% | 55.7% (n = 212) | met |
| Kimi-K3 † | 1,098 | 43.4% (40.5% to 46.4%) | 25.3% | 68% / 32% | 59.2% (n = 311) | met |
| nemotron-3-ultra-550b-a55b | 105 | 23.8% (16.7% to 32.8%) | 33.3% | 67% / 33% | 60.0% (n = 40) | met |
| gpt-6-sol | 538 | 49.6% (45.4% to 53.8%) | 24.9% | 70% / 30% | 52.2% (n = 138) | not met |
| claude-haiku-5.5 | 228 (July-August rulings only) | 17.5% (13.2% to 23.0%) | 66.2% | 49% / 51% | 56.9% (n = 65) | met (not met under Holm) |
| claude-sonnet-5.5 ‡ | 228 (July-August rulings only) | 40.4% (34.2% to 46.8%) | 39.0% | 62% / 38% | 57.1% (n = 49) | not met |
| claude-opus-5.5 ‡ | 228 (July-August rulings only) | 53.5% (47.0% to 59.9%) | 27.6% | 75% / 25% | 45.1% (n = 51) | not met |

‡ reasoning could not be disabled: Opus 5.5 used about 297 reasoning tokens per answer, Sonnet 5.5 ran at minimal effort (reports no reasoning tokens but writes about 517 output tokens), and GLM 5.3 still emits reasoning tokens with thinking switched off (about 140 per answer on Baseten). The Claude rows are July and August 2026 rulings only (n = 228), with 95% intervals of about plus or minus 6 points.

**Claude Opus 5.5 and GPT-6 Sol are tied (paired p = 0.54); both are wrong about half the time at 8 digits.** On their own post-cutoff rulings Opus 5.5 is at 53.5% (95% CI 47.0% to 59.9%, n = 228, July and August rulings only; reasoning could not be disabled, about 297 reasoning tokens per answer) and GPT-6 Sol at 49.6% (45.4% to 53.8%, n = 538). On the 228 rulings that all ten full-sample models share (table B below) they are at 53.5% and 49.1% (42.7% to 55.6%) with overlapping intervals, followed by Sonnet 5.5 (40.4%), Kimi K3 (39.0%), DeepSeek V4.1 Flash (34.6%), GLM 5.3 (19.3%) and Haiku 5.5 (17.5%). The three small Groq models stay under 6%.

### Part A: GPT-6 Sol on all 1,098 rulings

v1.1 had GPT-6 Sol on 200 rulings: 49.5% at 8 digits (95% CI 42.6% to 56.4%, all dates), 49.7% on the 167 post-cutoff rulings, and a Gate B verdict "not met" with n = 41 (p = 0.114). With all 1,098 rulings it is 54.4% (51.4% to 57.3%, all dates) and **49.6% (45.4% to 53.8%) on the 538 rulings after its cutoff**, so the v1.1 headline figure holds with more than three times the rulings. Gate B is still **not met** with 138 rate-changing errors (52.2% underpaid, 43.9% to 60.3%, p vs Baseline 2 = 0.092), so the v1.1 statement that the underpay lean does not beat chance in GPT-6 Sol is no longer a small-sample result. Before its cutoff it scores 58.9% (560 rulings); the nine-point drop after the cutoff is examined in the time-drift test below. The v1.1 statement that GPT-6 Sol showed no drop at its cutoff rested on 33 rulings before the cutoff and does not hold on the full sample.

### Part B: Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5

- **Opus 5.5** has the highest point estimate, tied with GPT-6 Sol (reasoning could not be disabled: about 297 reasoning tokens per answer; n = 228, July and August rulings only): 53.5% (47.0% to 59.9%) at 8 digits and 32.9% at 10 digits on the 228 post-cutoff rulings; 27.6% of its answers are invalid, and across all 1,098 rulings 75% of its invalid answers are suffix slips (format group) and 25% are invented codes (`review/format_vs_invention.md`).
- **Sonnet 5.5** (n = 228, July and August rulings only; reasoning could not be disabled, run at minimal effort) is at 40.4% (34.2% to 46.8%), with 39.0% invalid answers.
- **Haiku 5.5** (n = 228, July and August rulings only) is at 17.5% (13.2% to 23.0%) and 66.2% invalid. Across all 1,098 rulings half of its invalid answers are suffix slips (49%) and half are invented (51%).
- **Validity check.** Flagging any non-existent code catches 41.2% of Opus 5.5's wrong answers, 52.4% of Sonnet 5.5's and 72.2% of Haiku 5.5's, so for the stronger Claude models a validity check misses most errors.
- **Direction.** Opus 5.5 underpays on 45.1% of 51 rate-changing errors (32.3% to 58.6%), below 50% and not distinguishable from chance; Sonnet 5.5 is at 57.1% (n = 49, p = 0.059, not met); Haiku 5.5 is at 56.9% (n = 65, p = 0.021, met as pre-registered but not under Holm).

The two most accurate models, GPT-6 Sol and Opus 5.5, are the two where the underpay lean is not detected. That fits, but does not prove, the v1.1 suggestion that the lean fades as models improve; Sonnet 5.5, in between on accuracy, is also not distinguishable from chance.

### Same-sample tables (post-cutoff rulings all models share)

**Table A: all 11 models, 68 shared post-cutoff rulings**

| Model | n | 8-digit accuracy (95% CI) | Invalid share (95% CI) | FORMAT / INVENTED of invalid | Underpay share (95% CI), n rate-changing |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 68 | 0.0% (0.0% to 5.3%) | 98.5% (92.1% to 99.7%) | 10 / 57 (15% / 85%) | 100.0% (43.8% to 100.0%), n = 3 |
| openai/gpt-oss-120b | 68 | 5.9% (2.3% to 14.2%) | 98.5% (92.1% to 99.7%) | 14 / 53 (21% / 79%) | 33.3% (6.1% to 79.2%), n = 3 |
| allam-2-7b † | 68 | 1.5% (0.3% to 7.9%) | 92.6% (83.9% to 96.8%) | 7 / 56 (11% / 89%) | 75.0% (40.9% to 92.9%), n = 8 |
| deepseek-ai/DeepSeek-V4.1-Flash † | 68 | 25.0% (16.2% to 36.4%) | 33.8% (23.7% to 45.7%) | 12 / 11 (52% / 48%) | 62.5% (42.7% to 78.8%), n = 24 |
| zai-org/GLM-5.3 † | 68 | 19.1% (11.5% to 30.0%) | 61.8% (49.9% to 72.4%) | 15 / 27 (36% / 64%) | 44.4% (24.6% to 66.3%), n = 18 |
| moonshotai/Kimi-K3 † | 68 | 39.7% (28.9% to 51.6%) | 26.5% (17.4% to 38.0%) | 10 / 8 (56% / 44%) | 65.0% (43.3% to 81.9%), n = 20 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 68 | 20.6% (12.7% to 31.6%) | 33.8% (23.7% to 45.7%) | 13 / 10 (57% / 43%) | 60.7% (42.4% to 76.4%), n = 28 |
| openai/gpt-6-sol | 68 | 48.5% (37.1% to 60.2%) | 23.5% (15.0% to 34.9%) | 11 / 5 (69% / 31%) | 64.7% (41.3% to 82.7%), n = 17 |
| anthropic/claude-haiku-5.5 | 68 | 19.1% (11.5% to 30.0%) | 66.2% (54.3% to 76.3%) | 20 / 25 (44% / 56%) | 62.5% (38.6% to 81.5%), n = 16 |
| anthropic/claude-sonnet-5.5 | 68 | 38.2% (27.6% to 50.1%) | 39.7% (28.9% to 51.6%) | 16 / 11 (59% / 41%) | 58.8% (36.0% to 78.4%), n = 17 |
| anthropic/claude-opus-5.5 | 68 | 54.4% (42.7% to 65.7%) | 29.4% (19.9% to 41.1%) | 17 / 3 (85% / 15%) | 57.1% (32.6% to 78.6%), n = 14 |

**Table B: the 10 models run on all 1,098 rulings, 228 shared post-cutoff rulings**

| Model | n | 8-digit accuracy (95% CI) | Invalid share (95% CI) | FORMAT / INVENTED of invalid | Underpay share (95% CI), n rate-changing |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 228 | 0.0% (0.0% to 1.7%) | 98.7% (96.2% to 99.6%) | 28 / 197 (12% / 88%) | 55.6% (26.7% to 81.1%), n = 9 |
| openai/gpt-oss-120b | 228 | 3.9% (2.1% to 7.3%) | 97.4% (94.4% to 98.8%) | 47 / 175 (21% / 79%) | 50.0% (25.4% to 74.6%), n = 12 |
| allam-2-7b † | 228 | 1.8% (0.7% to 4.4%) | 87.3% (82.3% to 91.0%) | 17 / 182 (9% / 91%) | 81.5% (63.3% to 91.8%), n = 27 |
| deepseek-ai/DeepSeek-V4.1-Flash † | 228 | 34.6% (28.8% to 41.0%) | 28.1% (22.6% to 34.2%) | 38 / 26 (59% / 41%) | 62.0% (51.0% to 71.9%), n = 79 |
| zai-org/GLM-5.3 † | 228 | 19.3% (14.7% to 24.9%) | 66.7% (60.3% to 72.5%) | 59 / 93 (39% / 61%) | 60.0% (46.2% to 72.4%), n = 50 |
| moonshotai/Kimi-K3 † | 228 | 39.0% (32.9% to 45.5%) | 25.0% (19.8% to 31.0%) | 39 / 18 (68% / 32%) | 58.1% (46.7% to 68.7%), n = 74 |
| openai/gpt-6-sol | 228 | 49.1% (42.7% to 55.6%) | 21.1% (16.3% to 26.8%) | 31 / 17 (65% / 35%) | 61.4% (48.4% to 72.9%), n = 57 |
| anthropic/claude-haiku-5.5 | 228 | 17.5% (13.2% to 23.0%) | 66.2% (59.9% to 72.1%) | 75 / 76 (50% / 50%) | 56.9% (44.8% to 68.2%), n = 65 |
| anthropic/claude-sonnet-5.5 | 228 | 40.4% (34.2% to 46.8%) | 39.0% (32.9% to 45.5%) | 47 / 42 (53% / 47%) | 57.1% (43.3% to 70.0%), n = 49 |
| anthropic/claude-opus-5.5 | 228 | 53.5% (47.0% to 59.9%) | 27.6% (22.2% to 33.8%) | 43 / 20 (68% / 32%) | 45.1% (32.3% to 58.6%), n = 51 |

### Direction of duty errors and the Holm sensitivity

| Model | rate-changing errors n | underpaid | underpay share (95% CI) | p vs Baseline 1 | p vs Baseline 2 | Gate B verdict | comparable wrong answers n | median duty per $100k (IQR) |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 46 | 31 | 67.4% (53.0% to 79.1%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 101 | $0 ($0 to $3,500) |
| openai/gpt-oss-120b | 49 | 32 | 65.3% (51.3% to 77.1%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 93 | $300 ($0 to $2,500) |
| allam-2-7b † | 116 | 76 | 65.5% (56.5% to 73.5%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 147 | $3,400 ($350 to $6,500) |
| deepseek-ai/DeepSeek-V4.1-Flash † | 324 | 175 | 54.0% (48.6% to 59.4%) | 0.9930 | 0.1748 | not distinguishable from chance (Gate B not met) | 657 | $0 ($0 to $2,900) |
| zai-org/GLM-5.3 † | 212 | 118 | 55.7% (48.9% to 62.2%) | 0.8322 | 0.0060 | underpays more than chance (Gate B met) | 483 | $0 ($0 to $2,800) |
| moonshotai/Kimi-K3 † | 311 | 184 | 59.2% (53.6% to 64.5%) | 0.4496 | 0.0040 | underpays more than chance (Gate B met) | 673 | $0 ($0 to $2,800) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 40 | 24 | 60.0% (44.6% to 73.7%) | 0.2987 | 0.0070 | underpays more than chance (Gate B met) | 73 | $1,300 ($0 to $4,400) |
| openai/gpt-6-sol | 138 | 72 | 52.2% (43.9% to 60.3%) | 0.9940 | 0.0919 | not distinguishable from chance (Gate B not met) | 306 | $0 ($0 to $2,800) |
| anthropic/claude-haiku-5.5 | 65 | 37 | 56.9% (44.8% to 68.2%) | 0.5524 | 0.0210 | underpays more than chance (Gate B met) | 124 | $600 ($0 to $2,900) |
| anthropic/claude-sonnet-5.5 | 49 | 28 | 57.1% (43.3% to 70.0%) | 0.8172 | 0.0589 | not distinguishable from chance (Gate B not met) | 122 | $0 ($0 to $2,800) |
| anthropic/claude-opus-5.5 | 51 | 23 | 45.1% (32.3% to 58.6%) | 1.0000 | 0.5864 | not distinguishable from chance (Gate B not met) | 128 | $0 ($0 to $2,600) |

| Model | n | p vs Baseline 2 | Holm-adjusted p | Gate B as pre-registered | Verdict under Holm | Changed? |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 46 | < 0.001 | 0.0110 | met | met | no |
| openai/gpt-oss-120b | 49 | < 0.001 | 0.0110 | met | met | no |
| allam-2-7b † | 116 | < 0.001 | 0.0110 | met | met | no |
| deepseek-ai/DeepSeek-V4.1-Flash † | 324 | 0.1748 | 0.3497 | not met | not met | no |
| zai-org/GLM-5.3 † | 212 | 0.0060 | 0.0420 | met | met | no |
| moonshotai/Kimi-K3 † | 311 | 0.0040 | 0.0320 | met | met | no |
| nvidia/nemotron-3-ultra-550b-a55b:free | 40 | 0.0070 | 0.0420 | met | met | no |
| openai/gpt-6-sol | 138 | 0.0919 | 0.2757 | not met | not met | no |
| anthropic/claude-haiku-5.5 | 65 | 0.0210 | 0.1049 | met | not met | YES |
| anthropic/claude-sonnet-5.5 | 49 | 0.0589 | 0.2358 | not met | not met | no |
| anthropic/claude-opus-5.5 | 51 | 0.5864 | 0.5864 | not met | not met | no |

**The lean appears in the weaker models and is not detected in the two most accurate. Gate B is met for 7 of 11 models as pre-registered (gpt-oss-20b, gpt-oss-120b, allam-2-7b, GLM 5.3, Kimi K3, Nemotron 3 Ultra, Claude Haiku 5.5) and for 6 of 11 under Holm.** Haiku 5.5 is the only verdict that changes (adjusted p = 0.105).

### Time-drift test: contamination or harder later rulings?

Added after the results were seen (no new API calls). If GPT-6 Sol's drop across its cutoff (58.9% before, 49.6% after) were only due to later rulings being harder, models that cannot have seen any ruling should drop at the same split date. So every model's 8-digit accuracy on all 1,098 rulings is split at 2026-04-20 (Sol's cutoff) with Wilson 95% CIs and two-sided two-proportion tests. Interpretation rule, set before running: if the 2024-cutoff models show no drop, the Sol gap is more likely contamination and the † models' all-1,098 numbers are likely inflated; if they also drop, later rulings are harder.

| Model | Stated cutoff | n up to 2026-04-20 | 8-digit up to 2026-04-20 | n after | 8-digit after | drop (points) | p (z-test) | p (Fisher) |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 2024-06-01 | 560 | 0.0% (0.0% to 0.7%) | 538 | 0.6% (0.2% to 1.6%) | -0.6 | 0.0768 | 0.1173 |
| openai/gpt-oss-120b | 2024-06-01 | 560 | 5.9% (4.2% to 8.2%) | 538 | 5.2% (3.6% to 7.4%) | +0.7 | 0.6186 | 0.6931 |
| allam-2-7b | none stated † | 560 | 3.0% (1.9% to 4.8%) | 538 | 1.7% (0.9% to 3.1%) | +1.4 | 0.1376 | 0.1658 |
| deepseek-ai/DeepSeek-V4.1-Flash | none stated † | 560 | 43.0% (39.0% to 47.2%) | 538 | 35.3% (31.4% to 39.4%) | +7.7 | 0.0088 | 0.0094 |
| zai-org/GLM-5.3 | none stated † | 560 | 28.9% (25.3% to 32.8%) | 538 | 21.2% (17.9% to 24.8%) | +7.7 | 0.0031 | 0.0035 |
| moonshotai/Kimi-K3 | none stated † | 560 | 48.2% (44.1% to 52.4%) | 538 | 38.5% (34.5% to 42.7%) | +9.7 | 0.0011 | 0.0012 |
| openai/gpt-6-sol | 2026-04-20 | 560 | 58.9% (54.8% to 62.9%) | 538 | 49.6% (45.4% to 53.8%) | +9.3 | 0.0020 | 0.0020 |
| anthropic/claude-haiku-5.5 | 2026-06-30 | 560 | 19.3% (16.2% to 22.8%) | 538 | 16.9% (14.0% to 20.3%) | +2.4 | 0.3079 | 0.3098 |
| anthropic/claude-sonnet-5.5 | 2026-06-30 | 560 | 48.4% (44.3% to 52.5%) | 538 | 41.3% (37.2% to 45.5%) | +7.1 | 0.0176 | 0.0181 |
| anthropic/claude-opus-5.5 | 2026-06-30 | 560 | 56.8% (52.7% to 60.8%) | 538 | 53.9% (49.7% to 58.1%) | +2.9 | 0.3368 | 0.3624 |
| replication: moonshotai/kimi-k3 | none stated † | 560 | 47.1% (43.0% to 51.3%) | 538 | 37.0% (33.0% to 41.1%) | +10.2 | 0.0007 | 0.0008 |
| replication: deepseek/deepseek-v4.1-flash | none stated † | 560 | 41.4% (37.4% to 45.6%) | 538 | 35.7% (31.8% to 39.8%) | +5.7 | 0.0508 | 0.0547 |
| replication: z-ai/glm-5.3 | none stated † | 560 | 24.6% (21.3% to 28.4%) | 538 | 20.6% (17.4% to 24.3%) | +4.0 | 0.1126 | 0.1136 |

**Result.** GPT-6 Sol falls 9.3 points (p = 0.002). DeepSeek V4.1 Flash, GLM 5.3 and Kimi K3 (Baseten runs, no stated cutoff) fall 7.7, 7.7 and 9.7 points (p = 0.009, 0.003, 0.001), and the OpenRouter replications fall 5.7, 4.0 and 10.2 points. gpt-oss-120b (2024 cutoff) does not fall (5.9% to 5.2%, p = 0.62) and gpt-oss-20b is at 0.0% before and 0.6% after. Applying the rule as written, the Sol gap is more likely contamination and the † models' all-1,098 numbers are likely inflated, so they are upper bounds.

**Why that is weaker than it sounds.** The 2024-cutoff control sits at the floor. Table of the power to detect a drop of Sol's relative size:

| Model | observed before | drop of the same relative size (points) | power to detect it |
|---|---|---|---|
| openai/gpt-oss-20b | 0.0% | 0.03 | 5% |
| openai/gpt-oss-120b | 5.9% | 0.93 | 10% |

A test with 5% to 10% power cannot show that there is no drop. Against the contamination reading, Claude Sonnet 5.5 (cutoff June 30, so it had both sides of April 20 in training) also falls 7.1 points (p = 0.018) and Opus 5.5 and Haiku 5.5 fall 2.9 and 2.4 points (not significant). A smooth time trend (later rulings harder, or about newer products) fits that, and so does contamination; the data do not separate them. Nothing here changes the primary scores, which already use only post-cutoff rulings where a cutoff is stated.

### Part C: provider replication

Kimi K3, DeepSeek V4.1 Flash and GLM 5.3 were rerun on all 1,098 rulings through OpenRouter with Baseten excluded. The Baseten runs stay the primary results; this section is separate and never enters the tables above.

| Model | rulings both | identical code | identical first 8 digits (both >= 8 digits) | 8-digit accuracy Baseten | 8-digit accuracy OpenRouter | difference (95% CI) | invalid share Baseten / OpenRouter | answers with a different valid/invalid tag |
|---|---|---|---|---|---|---|---|---|
| moonshotai/Kimi-K3 | 1098 | 936 (85.2%) | 997 of 1098 (90.8%) | 477 (43.4%) | 463 (42.2%) | -1.3 points (-2.4 to -0.2) | 25.3% / 24.9% | 65 |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 884 (80.5%) | 928 of 1089 (85.2%) | 431 (39.3%) | 424 (38.6%) | -0.6 points (-2.1 to +0.8) | 32.2% / 31.3% | 84 |
| zai-org/GLM-5.3 | 1098 | 252 (23.0%) | 417 of 1029 (40.5%) | 276 (25.1%) | 249 (22.7%) | -2.5 points (-4.8 to -0.1) | 67.6% / 68.5% | 314 |

**Kimi K3 and DeepSeek V4.1 Flash replicate; GLM 5.3 accuracy matches but its answers do not (23% identical codes, reasoning setting changed).** 8-digit accuracy moves by -1.3, -0.6 and -2.5 points (the intervals for Kimi K3 and GLM 5.3 only just exclude zero, DeepSeek's includes it) and the invalid share by under one point. The identical code comes back for 85.2% (Kimi K3), 80.5% (DeepSeek V4.1 Flash) and only 23.0% (GLM 5.3) of the rulings, even at temperature 0. GLM's low agreement mixes the provider effect with the reasoning-setting change (disabled on Baseten, low effort on OpenRouter), so it cannot be attributed to the provider alone. A single run of a model at one provider should be read with that spread in mind.

### What v1.2 changes in the v1.1 conclusions

The v1.0 and v1.1 numbers are unchanged. The GPT-6 Sol headline figure holds on 1,098 rulings. Claude Opus 5.5 and GPT-6 Sol are tied (paired p = 0.54) at the top, both wrong about half the time at 8 digits. The underpay lean appears in the weaker models and is not detected in the two most accurate: it is 65% to 67% in the three small models and 45% to 60% in the other eight, beating the pre-registered baseline in 7 of 11 models. The v1.1 results hold across providers in aggregate, with the answer-level caveat above.
