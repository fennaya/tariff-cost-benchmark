# Tariff Cost Benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23197896.svg)](https://doi.org/10.5281/zenodo.23197896)

Interactive demo: https://claude.ai/artifact/F7JGzyoPMmeXtaNgDv4R3Z

**v1.1 (draft, 2026-10-07).** Adds stronger models and answers two follow-up questions: how good are stronger models, and is an invalid code a formatting slip or an invented code. The v1.0 numbers for the three Groq models are unchanged. Gemini 3.8 Flash is still running (one run a day) and is in no table until it reaches 200 rulings. Pre-registration: [PREREG_v1.1.md](PREREG_v1.1.md); deviations from it are listed in the [findings.md](findings.md) section "Deviations from pre-registration".

**Headline:** Model choice matters most. The three small free models score under 6% at 8 digits (the duty-relevant level); the stronger models score 25% to 50%. Among the most accurate models tested, GPT-6 Sol (a closed OpenAI model) and Kimi K3 still get the 8-digit line wrong about half the time or more: on the same 200 rulings GPT-6 Sol is right 49.5% of the time (95% CI 42.6% to 56.4%; 49.7% on the 167 of those rulings after its stated cutoff) and Kimi K3 37.0% (30.6% to 43.9%); the two intervals overlap slightly. The stronger models' invalid codes are mostly suffix slips on a real tariff line, while the small models mostly invent codes. The underpay lean is 65% to 67% in the small models and 51% to 60% in the stronger ones, and it beats the pre-registered chance baseline in 6 of 8 models (not DeepSeek V4.1 Flash or GPT-6 Sol; no verdict changes under a Holm correction). It does not beat chance in GPT-6 Sol, the most accurate model on the shared 200 rulings (n = 41 rate-changing errors, so weak evidence), so the lean may fade as models improve. All duty figures are MFN-only lower bounds.

| Model | Rulings scored | 8-digit accuracy (95% CI) | Invalid share | Format / invented, of invalid (all rulings run) | Underpay share (n) | Gate B |
|---|---|---|---|---|---|---|
| gpt-oss-20b | 1,098 | 0.3% (0.1% to 0.8%) | 98.4% | 14% / 86% | 67.4% (n = 46) | met |
| gpt-oss-120b | 1,098 | 5.6% (4.3% to 7.1%) | 96.6% | 23% / 77% | 65.3% (n = 49) | met |
| allam-2-7b † | 1,098 | 2.4% (1.6% to 3.4%) | 87.2% | 8% / 92% | 65.5% (n = 116) | met |
| DeepSeek-V4.1-Flash † | 1,098 | 39.3% (36.4% to 42.2%) | 32.2% | 58% / 42% | 54.0% (n = 324) | not met |
| GLM-5.3 † | 1,098 | 25.1% (22.7% to 27.8%) | 67.6% | 42% / 58% | 55.7% (n = 212) | met |
| Kimi-K3 † | 1,098 | 43.4% (40.5% to 46.4%) | 25.3% | 68% / 32% | 59.2% (n = 311) | met |
| nemotron-3-ultra-550b-a55b | 105 | 23.8% (16.7% to 32.8%) | 33.3% | 67% / 33% | 60.0% (n = 40) | met |
| gpt-6-sol | 167 | 49.7% (42.2% to 57.2%) | 25.7% | 74% / 26% | 51.2% (n = 41) | not met |

† contamination not ruled out (no stated cutoff); treat these models' accuracy as an upper bound. The models marked † are allam-2-7b, DeepSeek V4.1 Flash, GLM 5.3 and Kimi K3. The memorisation probe (ruling number only) is uninformative for DeepSeek and GLM, which refused 96 and 95 of 100 probes; Kimi answered all 100 and had 0 hits. Nemotron 3 Ultra scored 34.7% at 8 digits on rulings before its stated cutoff and 23.8% after it; that is a descriptive warning sign that contamination can inflate scores, not a test.

Nemotron 3 Ultra and GPT-6 Sol ran on a fixed 200-ruling sample, scored on the 105 and 167 rulings after their stated cutoffs, and are only comparable with other models restricted to the same 200 (see the same-sample table in findings.md). GPT-6 Sol is a closed OpenAI model (mid-tier of the GPT-6 family, below the Astra flagship) run on a paid route for $0.20; every other model was run free. No other closed model is in these tables, and none of these models stands in for GPT, Claude or Gemini. Reasoning was set to the lowest level each model accepts.

![Error breakdown by model](figures/error_breakdown.png)

**Format slip or invented code?** For the three small models, 77% to 93% of invalid answers name a tariff line that does not exist (groups d and e in [findings.md](findings.md)). For DeepSeek V4.1 Flash, Kimi K3, Nemotron 3 Ultra and GPT-6 Sol, 58% to 74% of invalid answers are on a real tariff line with a wrong or missing suffix, but only 34% to 53% of those have the true code's first 8 digits, so a true suffix slip is 23% to 38% of their invalid answers. GLM 5.3 is the exception (58% invented). Stale training data shows up too: 10-digit codes from older HTS releases make up 13% to 42% of the invalid answers of the four models above (v1.0: 1 answer).

**A validity check detects most errors for the small models, but not for the stronger ones.** Flagging any code that does not exist catches 98.4%, 97.2% and 88.7% of wrong answers for gpt-oss-20b, gpt-oss-120b and allam-2-7b, but only 34% to 42% for DeepSeek V4.1 Flash, Kimi K3, Nemotron 3 Ultra and GPT-6 Sol (77% for GLM 5.3), because their wrong answers are mostly valid codes. Asking a v1.0 model to retry after "that code does not exist" turned 1.5% to 7.2% of its invalid answers into valid codes and none into the correct code; the retry test was not repeated for the stronger models.

**Direction of errors:** Among rate-changing errors, 65% to 67% underpaid for the three small models and 51% to 60% for the stronger ones (n = 40 to 324). The intervals for GLM 5.3 and Nemotron 3 Ultra include 50%, and Nemotron's and GPT-6 Sol's n (40 and 41) sit just above the threshold of 30. Only a minority of wrong answers can be compared on duty (it needs a rate for both codes), so this describes that set, not all errors. The median duty at stake is $0 per $100,000 for most stronger models; MFN-only lower bounds.

**Key numbers (v1.0, unchanged):**
- **5.6% / 2.4% / 0.3%** is the 8-digit (duty-bearing) accuracy for gpt-oss-120b / allam-2-7b / gpt-oss-20b on 1,098 post-training-cutoff CBP rulings.
- **0.5% / 1.7% / 0.0%** is the 10-digit accuracy for the same models.

This is a finding about the models listed above at their lowest reasoning level, not a claim that the task is inherently hard. Prior work reports 10-digit scores of about 12.5% to 40% under different conditions (ATLAS: a different benchmark, models and prompting); the stronger models here score 12.4% to 31.7% at 10 digits, in that range. All findings survived a hostile re-audit: Round 2 for v1.0 and [review/v1_1_attack.md](review/v1_1_attack.md) for v1.1, which also lists what the results cannot support. See [findings.md](findings.md) for the full results, method, and limitations, and [DECISIONS.md](DECISIONS.md) for the audit trail. All calls are in `data/exports/api_calls.csv`.

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

# v1.1 (stronger models; keys in .env: BASETEN_API_KEY, OPENROUTER_API_KEY; models and settings in config.json):
.venv/Scripts/python scripts/build_probe_ids.py          # Check A sample (seed 20261007)
.venv/Scripts/python scripts/run_new_models.py --model <model_id> --n 50     # pilot; then without --n for the full run
.venv/Scripts/python scripts/run_new_models.py --model <model_id> --probe    # Check A, ruling number only
.venv/Scripts/python scripts/verify_parser.py             # new parser vs every cached v1.0 answer
.venv/Scripts/python scripts/analyze_format_vs_invention.py
.venv/Scripts/python scripts/analyze_v1_1.py              # review/v1_1_results.md, biggest_misses.md
.venv/Scripts/python scripts/export_api_calls.py          # data/exports/api_calls.csv
```

All raw data is cached under `data/raw/` (CBP rulings, HTS revisions) and `llm_logs/`
(model responses). Every script is resumable and re-downloads nothing already cached.
All numbers in `findings.md` are produced by these scripts run against that cached data
and nothing is hand-typed. See [STATUS.md](STATUS.md) for what's actually been run so far.

## What is tracked, and rebuilding the raw data

Everything needed to reproduce every number in `findings.md` is in git:
`data/raw/rulings/` and `data/raw/search_pages/` (the CBP rulings as fetched, 18 MB),
`data/processed/` (cleaned descriptions, usable set, duty rates), `data/compact/hts_revisions/`
(the HTS code and rate tables, trimmed and gzipped, 9 MB), `data/compact/hts_older/` and
`data/compact/hts_rates/` (HTS codes and MFN rates parsed from the archived release PDFs),
`llm_logs/`, `llm_probes/` and `llm_followups/` (every model response), `data/exports/` (one row per model call), `run_logs/` (console logs of the
runs), `review/translation_review_marked.csv`, and all scripts. Run `analysis.py` and the
`scripts/audit_*.py` / `analyze_language.py` scripts above directly on a fresh clone.

Not tracked: `data/raw/hts_revisions/` (255 MB of raw USITC dumps) and
`data/raw/hts_older_pdf/` (the archived HTS release PDFs, 1.7 GB), plus the local-only Gemini
files until v1.1. Note: the 21 files in `data/raw/hts_revisions/` are all copies of the current schedule, because USITC's JSON export ignores the release parameter. Archived releases exist only as PDFs, which `scripts/fetch_older_hts.py` fetches and parses. The scripts layer each ruling-date release's PDF rates onto the JSON. See the Limitations in findings.md. To
rebuild the untracked files from scratch, from a fresh clone:

```bash
uv venv --python 3.12.14 .venv
uv pip install --python .venv requests pandas scipy matplotlib pymupdf
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
