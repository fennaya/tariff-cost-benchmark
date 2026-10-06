# Tariff Cost Benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23197896.svg)](https://doi.org/10.5281/zenodo.23197896)

**v1.0.** The results below are complete and final for the 3 models tested. A 4th model (Gemini, free tier) is in progress. It will be added in **v1.1** when its run finishes. See [STATUS.md](STATUS.md). Nothing here depends on it.

**Lead finding:** Free models mostly return HTS codes that do not exist, and most of those are not near misses. Across 1,098 CBP rulings, 88.7% to 98.4% of wrong answers were invalid codes. "Invalid" means unparseable output, or a code that is not a 10-digit entry in the HTS.

| Model | Wrong answers | Invalid | Suffix only wrong | First 6 real, first 8 not | Fabricated |
|---|---|---|---|---|---|
| gpt-oss-20b | 1,098 | 1,080 (98.4%) | 13.5% of invalid | 39.1% | 47.4% |
| gpt-oss-120b | 1,092 | 1,061 (97.2%) | 22.9% | 56.1% | 20.8% |
| allam-2-7b | 1,079 | 957 (88.7%) | 6.7% | 37.5% | 55.0% |

**A validity check detects most errors. Asking the model to retry does not repair them.** A check that flags any non-existent code catches 98.4%, 97.2%, and 88.7% of wrong answers (gpt-oss-20b, gpt-oss-120b, allam-2-7b), and flags none of the correct 10-digit answers (0 of 6 and 0 of 19 for the two models that have any). It also flags most answers that are right at the 8-digit duty level but lack a valid suffix (55 of 61 for gpt-oss-120b), so it marks answers for review rather than classifying. When a model was told its code does not exist and asked again, 1.5% to 7.2% of its invalid answers became valid codes, and none became the correct code. Fixing only the 2-digit suffix would rescue 6.7% to 22.9% of invalid answers. Stale training data does not explain it: 1 invalid answer across all three models was a code that existed in a 2022 to 2025 HTS release. Details and the chart are in [findings.md](findings.md).

![Error breakdown by model](figures/error_breakdown.png)

**Direction of errors:** Only 8.5% to 13.6% of wrong answers can be compared on duty, because that needs a rate for both the true and the predicted code. In 46 to 116 of those per model, the rate differs, and 65.3% to 67.4% of those rate-changing errors underpaid.

| Model | Rate-changing errors (n) | Underpaid | Underpay share (95% CI) | p vs. matched-depth chance baseline |
|---|---|---|---|---|
| gpt-oss-20b | 46 | 31 | 67.4% (53.0% to 79.1%) | < 0.001 |
| gpt-oss-120b | 49 | 32 | 65.3% (51.3% to 77.1%) | < 0.001 |
| allam-2-7b | 116 | 76 | 65.5% (56.5% to 73.5%) | < 0.001 |

All three models have at least 30 cases and beat the chance baseline, so the underpay lean is significant for each. The intervals are wide for gpt-oss-20b and gpt-oss-120b. This describes the small comparable set, not all errors. For wrong answers that are valid codes, the median duty at stake is $1,500 / $0 / $4,000 per $100,000 (gpt-oss-20b / gpt-oss-120b / allam-2-7b; n = 15 / 31 / 113). The gpt-oss-20b figure has too few cases to confirm.

**Headline:** Three free, open-weight models on Groq's free tier were tested. They are `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, and `allam-2-7b`. None scores above 5.6% on the duty-relevant 8-digit code. Most of their wrong answers are invalid codes, and a validity check catches them, but retrying does not make them right. This is a finding about these three models. It is not a claim that the task is inherently hard. Prior work reports far higher scores under different conditions, such as paid frontier models, fine-tuning, and a different benchmark.

**Key numbers:**
- **5.6% / 2.4% / 0.3%** is the 8-digit (duty-bearing) accuracy for gpt-oss-120b / allam-2-7b / gpt-oss-20b. The set is 1,098 post-training-cutoff CBP rulings.
- **0.5% / 1.7% / 0.0%** is the 10-digit accuracy for the same models.

Both findings survived a hostile Round 2 re-audit. It covered bug hunts, baseline tests, a stripping-quality review, and a comparison with prior work. See [findings.md](findings.md) for the full results, method, and limitations. See [DECISIONS.md](DECISIONS.md) for the audit trail. The ratios above come from `scripts/derive_readme_shares.py`, `scripts/analyze_invalid_codes.py`, `scripts/analyze_validity_check.py`, `scripts/analyze_guardrail.py`, `scripts/analyze_underpay_summary.py`, `scripts/check_revision_impact.py`, and `scripts/check_rate_impact.py` (outputs in `review/`).

**Question:** When AI models classify imported goods for US customs, how often are they
wrong, how much duty is at stake per error, and do their errors lean toward underpaying
(the legally dangerous direction)?

- **Ground truth:** US Customs and Border Protection (CBP) binding classification rulings
  from the CROSS database (rulings.cbp.gov), NY collection.
- **Duty data:** the official Harmonized Tariff Schedule from USITC (hts.usitc.gov), the
  release in force on each ruling's date, with MFN rates re-read from each release's
  archived PDF (0 of 4,060 code-date pairs had a rate different from the current schedule).
- **What's new vs. prior work** (ATLAS arXiv 2509.18400, Tarifflo arXiv 2412.14179, UNB
  arXiv 2606.16987, all accuracy-only): this project measures the *duty cost* of
  classification errors, tests for *direction bias* (under- vs over-paying), and guards
  against training-data contamination by restricting to rulings dated after each model's
  training cutoff.

Author: Aya Emssaad (GitHub: fennaya)

## Status

See [STATUS.md](STATUS.md) for current phase, gate results, and what runs next.
See [DECISIONS.md](DECISIONS.md) for the log of judgment calls made along the way.
See [BLOCKERS.md](BLOCKERS.md) for anything parked pending money, credentials, or a
human decision.

## Reproduce

The commands use the Windows layout. On Mac or Linux, replace `.venv/Scripts/python` with `.venv/bin/python`. Nothing else changes. `scripts/run_gemini_daily.bat` is Windows only. On Mac or Linux, schedule the same Python command with cron instead.

```bash
uv venv --python 3.12.14 .venv
uv pip install --python .venv requests pandas scipy matplotlib

.venv/Scripts/python scripts/fetch_rulings.py        # Phase 1: CBP CROSS rulings (resumable)
.venv/Scripts/python scripts/fetch_hts.py             # Phase 3: USITC HTS revisions (resumable)
.venv/Scripts/python scripts/clean_descriptions.py    # Phase 2: leak-safe descriptions (Gate 2)
.venv/Scripts/python scripts/build_usable_set.py      # Phase 1: single-product/single-code filter (Gate 1b)
.venv/Scripts/python scripts/parse_duty_rates.py       # Phase 3: duty rate resolution (Gate 3)
.venv/Scripts/python scripts/build_exclusions_table.py

# Requires a free-tier LLM key (GROQ_API_KEY checked first) in the environment:
.venv/Scripts/python scripts/select_models.py          # Phase 0: pin exact model IDs
.venv/Scripts/python scripts/run_llm_classification.py --n 50   # Phase 4: pilot
.venv/Scripts/python scripts/run_llm_classification.py          # Phase 5: full run
.venv/Scripts/python analysis.py                        # Phase 6
.venv/Scripts/python scripts/build_demo_data.py
.venv/Scripts/python scripts/translate_sample.py         # Phase 7 prep (stops for human review)

# Round 2 (hostile audit of both headlines):
.venv/Scripts/python scripts/audit_accuracy.py          # Gate A: is the low accuracy a bug?
.venv/Scripts/python scripts/build_stripping_audit.py   # input generated; judgments are by hand
.venv/Scripts/python scripts/audit_direction.py         # Gate B: does underpay bias beat chance?
.venv/Scripts/python scripts/build_translation_html.py  # review/translation_review.html (mark by hand)
.venv/Scripts/python scripts/run_llm_translations.py --lang fr --model <model_id>   # Phase 7, once marked
.venv/Scripts/python scripts/run_llm_translations.py --lang ar --model <model_id>
.venv/Scripts/python scripts/analyze_language.py        # paired language comparison

# Round 3 (invalid-code breakdown, guardrail, chart):
.venv/Scripts/python scripts/fetch_older_hts.py         # archived HTS releases 2022-2026 as PDFs, parsed (slow: ~90 PDFs)
.venv/Scripts/python scripts/analyze_invalid_codes.py   # breakdown, outdated check, dollar figure
.venv/Scripts/python scripts/run_guardrail_followup.py --model <model_id>   # needs a Groq key; one run per model
.venv/Scripts/python scripts/analyze_guardrail.py
.venv/Scripts/python scripts/make_error_breakdown_chart.py   # figures/error_breakdown.png
.venv/Scripts/python scripts/check_revision_impact.py
.venv/Scripts/python scripts/parse_release_rates.py     # MFN rates per 2026 release from the PDFs
.venv/Scripts/python scripts/check_rate_impact.py       # ruling-date vs current rates, dollar figures re-run
.venv/Scripts/python scripts/analyze_validity_check.py  # what a validity check flags
.venv/Scripts/python scripts/analyze_underpay_summary.py  # underpay n, Wilson CI, baseline p
```

All raw data is cached under `data/raw/` (CBP rulings, HTS revisions) and `llm_logs/`
(model responses). Every script is resumable and re-downloads nothing already cached.
All numbers in `findings.md` are produced by these scripts run against that cached data
and nothing is hand-typed. See [STATUS.md](STATUS.md) for what's actually been run so far.

## What is tracked, and rebuilding the raw data

Everything needed to reproduce every number in `findings.md` is in git:
`data/raw/rulings/` and `data/raw/search_pages/` (the CBP rulings as fetched, 18 MB),
`data/processed/` (cleaned descriptions, usable set, duty rates), `data/compact/hts_revisions/`
(the HTS rate tables, trimmed and gzipped, 9 MB), `llm_logs/` (every model response),
`review/translation_review_marked.csv`, and all scripts. Run `analysis.py` and the
`scripts/audit_*.py` / `analyze_language.py` scripts above directly on a fresh clone.

Only the raw USITC HTS dumps (`data/raw/hts_revisions/`, 255 MB) are gitignored. Note: these 21 files are all copies of the current schedule, because USITC's JSON export ignores the release parameter. Archived releases exist only as PDFs, which `scripts/fetch_older_hts.py` fetches and parses (`data/compact/hts_older/` for codes, `data/compact/hts_rates/` for MFN rates). The scripts layer each ruling-date release's PDF rates onto the JSON. See the Limitations in findings.md. To
rebuild them from scratch, from a fresh clone:

```bash
uv venv --python 3.12.14 .venv
uv pip install --python .venv requests pandas scipy matplotlib
.venv/Scripts/python scripts/fetch_hts.py              # re-downloads the 21 USITC revisions
.venv/Scripts/python scripts/build_compact_hts.py      # optional: regenerates data/compact/
```

To rebuild everything upstream of that too (CBP rulings, cleaning, usable set, duty rates),
run the Phase 1-3 commands in the Reproduce section in order. All fetch scripts are
resumable and hit only the public CBP/USITC APIs, no key needed. Scripts use the raw HTS
files when present and the compact copy otherwise.

## Data license

CBP ruling text and the USITC Harmonized Tariff Schedule data used in this project are
**works of the United States Government and not subject to copyright** (17 U.S.C. § 105:
"Copyright protection under this title is not available for any work of the United
States Government"; https://www.law.cornell.edu/uscode/text/17/105). CBP's own site
states this explicitly for its content: "information on the U.S. Customs and Border
Protection website is in the public domain and may be reproduced, published or
otherwise used without the permission of the CBP" (https://www.cbp.gov/site-policy-notices/copyright-notice).
This project's own code is MIT licensed; its analysis and findings are CC BY 4.0. See
`CITATION.cff`.

## Cite this work

Emssaad, A. Tariff Cost Benchmark: Duty-at-Stake and Direction Bias in LLM Customs Classification. Zenodo. https://doi.org/10.5281/zenodo.23197896
