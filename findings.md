# Findings

**v1.0.** The findings below are complete and final for the 3 models they cover. A 4th
model (`gemini-3.8-flash`, free tier) is in progress on a separate fixed 200-ruling
sample (`data/gemini_subset.csv`) and will be added here in **v1.1** once its run
finishes — see [STATUS.md](STATUS.md) for status. No Gemini results are published
until all 200 rulings are done. Nothing below depends on or changes because of Gemini's
results.

**Scope note, read first:** every claim in this document is about **3 free, open-weight
models run on Groq's free tier** — `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, and
`allam-2-7b` — at temperature 0, low reasoning effort, single-shot, no tools or
retrieval. Nothing here generalizes to larger, fine-tuned, or paid-tier models; where a
comparison to such a model is made (prior work), that's flagged explicitly.

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
ground truth and the official USITC Harmonized Tariff Schedule for duty rates — and
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
   HTS code — 1,098 of 1,816.
4. **Duty rates:** column-1 General (MFN) rate for each true code, from the USITC HTS
   revision in force on the ruling's date. Cost analysis uses ad valorem and free rates
   only. Section 301/232/reciprocal Chapter 99 duties are entirely out of scope (country-
   of-origin dependent, changed frequently through 2025-2026), so **every duty figure
   here is a lower bound**.
5. **Models:** `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b` — all free-tier,
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
| 1a | ≥45/50 rulings with ruling#, date, text, tariffs | **PASS — 50/50** |
| 1b | ≥300 usable post-cutoff rulings | **PASS — 1,098** |
| 2 | ≥90% of cleaned inputs non-empty and leak-free | **PASS — 99.5%** (1,807/1,816) |
| 3 | ≥85% of true codes resolve to ad valorem/free | **PASS — 96.6%** (1,061/1,098) |
| 4 | pilot accuracy reported regardless of outcome | 10-digit accuracy 0% on the pilot — far below the 90% "weak cost story" threshold |
| 5 | full run, 3 models × 1,098 rulings | **3,294/3,294 calls complete** |
| 6 | analysis | this document |
| Round 2, Gate A | Headline A (low accuracy) survives a hostile bug hunt | **PASS** |
| Round 2, Gate B | Headline B (underpay bias) beats two chance baselines at p<0.05 | **PASS, all 3 models** |
| 7 | paired language comparison | **done** — see Language Comparison below |

## Results

### Accuracy by digit level — 8-digit is the headline figure

The last 2 digits of a 10-digit HTS code are a US-only statistical suffix that is
frequently *not* binding for duty purposes — the duty rate is usually set at the
8-digit tariff-item level (see DECISIONS.md's "Gate 3" entry). 8-digit accuracy is
therefore the duty-relevant headline number, reported here alongside 6- and 10-digit.

| Model | 6-digit | **8-digit (headline)** | 10-digit |
|---|---|---|---|
| gpt-oss-120b | 21.1% | **5.6%** | 0.5% |
| allam-2-7b | 4.4% | **2.4%** | 1.7% |
| gpt-oss-20b | 3.0% | **0.3%** | 0.0% |

All three models are far below the 90% threshold that would make the cost story weak —
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

gpt-oss-120b's errors are markedly "deeper" — nearly 45% first diverge at 8 or 10
digits, meaning it usually gets the general classification (chapter/heading) right and
fails only on fine precision. allam-2-7b and gpt-oss-20b diverge earlier on average
(roughly 60% and 44% at the 2-digit chapter level), indicating more fundamental
classification errors, not just precision loss.

### Invalid codes

| Model | Unparseable or non-existent code, as a share of all answers |
|---|---|
| gpt-oss-20b | 98.4% |
| gpt-oss-120b | 96.6% |
| allam-2-7b | 87.2% |

The overwhelming majority of wrong answers are not "classified under the wrong but
real code" — they're codes that don't exist in the HTS at all, often an 8-digit tariff
item with a guessed or omitted statistical suffix. Manually tracing individual cases
(DECISIONS.md) found this reflects genuine model behavior: systematic confusion between
adjacent headings (HTS 6801 vs. 6802 for worked stone, 6109 vs. 6110 for knit garments)
and a frequent failure to commit to the final 2-digit statistical suffix.

### Direction bias — confirmed against chance, not just observed

| Model | Underpay share | n (rate-changing errors) | Exact binomial p vs. 50% |
|---|---|---|---|
| allam-2-7b | 65.2% | 115 | 0.0014 |
| gpt-oss-20b | 67.4% | 46 | 0.0259 |
| gpt-oss-120b | 63.8% | 47 | 0.0789 |

All three lean toward underpaying. **Round 2 tested whether this beats a fair baseline**
(random guessing could underpay more than 50% of the time just because of where true
codes happen to sit in the tariff schedule) rather than assuming bias from the raw
number. Two baselines were simulated at 1,000 reps each: a random sibling code under the
true code's 4-digit heading, and the harder test — a random sibling under the *model's
own* deepest-correct prefix.

| Model | Observed | Baseline 1 (heading-random) | Baseline 2 (model's-depth-random) |
|---|---|---|---|
| allam-2-7b | 0.652 | 0.563, **p < 0.001** | 0.454, **p < 0.001** |
| gpt-oss-120b | 0.638 | 0.563, **p < 0.001** | 0.499, **p < 0.001** |
| gpt-oss-20b | 0.674 | 0.562, p = 0.742 (not significant) | 0.485, **p < 0.001** |

**All three models beat the harder baseline (Baseline 2) at p < 0.001** — the underpay
bias is not explained by where true codes sit in the schedule, even accounting for each
model's own depth of error. (gpt-oss-20b does not beat the simpler heading-level
baseline, because errors at its own matched depth have a structurally lower baseline
underpay rate than heading-level random — but it clears the harder, more specific test
easily, which is the actual pass condition.)

A hypothesized mechanism — models defaulting to cheaper "Other" catch-all subheadings
more often than the true codes do — was checked and **ruled out**: predicted codes land
in "Other" baskets *less* often than true codes across all 3 models (11-49% vs. 62-63%),
which if anything would predict overpaying, not underpaying.

### Free errors and duty at stake

| Model | Share of wrong answers with zero rate difference ("free errors") | Median duty at stake per $100,000 declared (IQR) |
|---|---|---|
| gpt-oss-20b | 54.5% | $0 ($0–$3,500) |
| gpt-oss-120b | 44.7% | $600 ($0–$2,600) |
| allam-2-7b | 20.7% | $3,500 ($500–$6,500) |

Split by direction (median per $100,000, among wrong answers with a resolvable rate):

| Model | Underpay median (n) | Overpay median (n) |
|---|---|---|
| allam-2-7b | $4,400 (75) | $5,400 (40) |
| gpt-oss-120b | $2,550 (30) | $2,100 (17) |
| gpt-oss-20b | $4,200 (31) | $4,900 (15) |

These figures exclude all Chapter 99 trade-remedy duties and are computed over a
small subset of wrong answers (those with a resolvable rate on both sides) — real
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
difference detected at this sample size," not as evidence of no difference** — a power
analysis (Monte Carlo, 2,000 simulations per candidate effect size, under a simplifying
independence assumption that likely *understates* true power) found the smallest
10-digit accuracy gap detectable at 80% power with n≈90-93 is approximately 0.10-0.15 —
i.e., only a 10-15 percentage-point difference or larger would reliably show up at this
sample size. Paired bootstrap duty-at-stake differences were similarly not distinguishable
from zero (every 95% CI spans $0).

### allam-2-7b: Arabic vs. English, specifically

allam-2-7b is the one Arabic-focused model among the three tested — does that
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
English in origin) conducted in that language — this is a data point, not a finding.

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
even their **general-purpose, non-fine-tuned** frontier baselines score 7-15x higher
than this project's best 10-digit number. This gap is attributed to **model capability
and configuration** — this project deliberately tests only free, open-weight,
non-fine-tuned, low-reasoning-effort models, a narrower and weaker slice of what's
possible than ATLAS's comparison set — **not to the classification task itself being
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
| Of usable set: resolves to ad valorem/free rate (Gate 3) | 1,061 |
| Of usable set: specific rate (excluded from cost analysis) | 7 |
| Of usable set: compound rate (excluded) | 8 |
| Of usable set: other/unparseable rate (excluded) | 18 |
| Of usable set: code not found in its HTS revision (excluded) | 1 |
| Of usable set: rate field blank at every digit level checked (excluded) | 3 |

## Limitations (stated before interpretation)

- All duty-at-stake figures are a **lower bound**: column-1 General (MFN) rates only,
  excluding all Section 301/232/reciprocal-tariff Chapter 99 overlays.
- Ground truth is limited to the **NY collection** — HQ rulings and court decisions are
  not included.
- `allam-2-7b`'s training cutoff is unconfirmed; its results carry a residual,
  unquantified contamination risk the other two models' results don't.
- Direction-test and duty-at-stake sample sizes (n=46-115 per model) are small because
  most wrong answers are non-existent codes with no comparable rate.
- Digit-level accuracy credits a prediction at any level it actually specified (e.g. an
  8-digit-only answer can score correct at 6/8 digits even though it can never score at
  10) — a deliberate scoring choice, not an all-or-nothing one; see DECISIONS.md.
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
  much of the gap to ATLAS's numbers — this project deliberately didn't test that, per
  its zero-spend constraint, so it cannot speak to whether the underpay bias and
  near-zero full-precision accuracy are specific to free-tier models or hold more
  broadly.
