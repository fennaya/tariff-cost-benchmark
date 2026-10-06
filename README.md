# Tariff Cost Benchmark

**v1.0.** Results below are complete and final for the 3 models tested. A 4th model
(Gemini, free tier) is in progress and will be added in **v1.1** once its run finishes
— see [STATUS.md](STATUS.md) for live progress; nothing here depends on it.

**Headline:** Three free, open-weight models on Groq's free tier — `openai/gpt-oss-20b`,
`openai/gpt-oss-120b`, `allam-2-7b` — top out at 5.6% accuracy on the duty-relevant
8-digit US customs code, and when they're wrong in a way that changes the duty rate, all
three underpay significantly more often than two different chance baselines predict
(p < 0.001 against each model's own matched-depth baseline) — the legally dangerous
direction. This is a finding about these three free-tier models, not about the task
being inherently hard: even non-fine-tuned frontier models in prior work score 7-15x
higher.

**Three key numbers:**
- **5.6% / 2.4% / 0.3%** — 8-digit (duty-bearing) accuracy (gpt-oss-120b / allam-2-7b / gpt-oss-20b) on 1,098 post-training-cutoff CBP rulings. 10-digit accuracy is lower still (0.5% / 1.7% / 0.0%).
- **63.8%-67.4%** underpay share among rate-changing errors — confirmed (not just observed) to beat two random-chance baselines at p < 0.001 per model.
- **87.2%-98.4%** — share of wrong answers that are a non-existent HTS code, not just the wrong real one.

Both headlines survived a hostile Round 2 re-audit (bug hunts, baseline tests, a
stripping-quality review, and a verified comparison against prior work) before being
reported here — see [findings.md](findings.md) for the full results, method, and
limitations, and [DECISIONS.md](DECISIONS.md) for the audit trail.

**Question:** When AI models classify imported goods for US customs, how often are they
wrong, how much duty is at stake per error, and do their errors lean toward underpaying
(the legally dangerous direction)?

- **Ground truth:** US Customs and Border Protection (CBP) binding classification rulings
  from the CROSS database (rulings.cbp.gov), NY collection.
- **Duty data:** the official Harmonized Tariff Schedule from USITC (hts.usitc.gov), the
  revision in force on each ruling's date.
- **What's new vs. prior work** (ATLAS arXiv 2509.18400, Tarifflo arXiv 2412.14179, UNB
  arXiv 2606.16987 — all accuracy-only): this project measures the *duty cost* of
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
```

All raw data is cached under `data/raw/` (CBP rulings, HTS revisions) and `llm_logs/`
(model responses) — every script is resumable and re-downloads nothing already cached.
All numbers in `findings.md` are produced by these scripts run against that cached data
— nothing is hand-typed. See [STATUS.md](STATUS.md) for what's actually been run so far.

## What is tracked, and rebuilding the raw data

Everything needed to reproduce every number in `findings.md` is in git:
`data/raw/rulings/` and `data/raw/search_pages/` (the CBP rulings as fetched, 18 MB),
`data/processed/` (cleaned descriptions, usable set, duty rates), `data/compact/hts_revisions/`
(the HTS rate tables, trimmed and gzipped, 9 MB), `llm_logs/` (every model response),
`review/translation_review_marked.csv`, and all scripts. Run `analysis.py` and the
`scripts/audit_*.py` / `analyze_language.py` scripts above directly on a fresh clone.

Only the raw USITC HTS dumps (`data/raw/hts_revisions/`, 255 MB) are gitignored. To
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
States Government" — https://www.law.cornell.edu/uscode/text/17/105). CBP's own site
states this explicitly for its content: "information on the U.S. Customs and Border
Protection website is in the public domain and may be reproduced, published or
otherwise used without the permission of the CBP" (https://www.cbp.gov/site-policy-notices/copyright-notice).
This project's own code is MIT licensed; its analysis and findings are CC BY 4.0 — see
`CITATION.cff`.
