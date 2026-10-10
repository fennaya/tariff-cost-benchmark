# Status

**v1.0.0 published 2026-10-06.** DOI [10.5281/zenodo.23197896](https://doi.org/10.5281/zenodo.23197896) (all versions). Repo: github.com/fennaya/tariff-cost-benchmark. **v1.1 (2026-10-07) is pushed to main; no release or tag has been created for it.**

**v1.2 (2026-10-10) is committed locally, not pushed** (version 1.2.0 in CITATION.cff). Pre-registered in [PREREG_v1.2.md](PREREG_v1.2.md) before any call. Adds GPT-6 Sol on all 1,098 rulings, Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 (OpenRouter, paid, 1,098 each) and an OpenRouter replication of Kimi K3, DeepSeek V4.1 Flash and GLM 5.3 with Baseten excluded. Round cost $21.36 (cap $30). Results: [findings.md](findings.md) section "v1.2", [review/v1_2_attack.md](review/v1_2_attack.md), [review/replication.md](review/replication.md); deviations in findings.md and DECISIONS.md. Self-check: `python scripts/verify_readme_numbers.py`. Pre-push follow-up: time-drift test (`review/time_drift.md`) and wording fixes, see DECISIONS.md.

- **v1.0 results:** final for the 3 Groq models (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b`) on 1,098 rulings; unchanged in v1.1 (checked after the full rerun).
- **v1.1 (version 1.1.0 in CITATION.cff):** deviations from the pre-registration (the unhonoured parser stop, the paid GPT-6 Sol route, and the others) are listed in findings.md under "Deviations from pre-registration". Pre-registered in [PREREG_v1.1.md](PREREG_v1.1.md) before any new call. Adds DeepSeek V4.1 Flash, GLM 5.3 and Kimi K3 (Baseten free credits, 1,098 rulings each), Nemotron 3 Ultra (OpenRouter free tier, 200 rulings) and GPT-6 Sol (OpenRouter, paid, hard cap $2, 200 rulings; run at the user's request, spend $0.20). Results: [findings.md](findings.md) final section, [review/v1_1_results.md](review/v1_1_results.md), [review/v1_1_attack.md](review/v1_1_attack.md), [review/format_vs_invention.md](review/format_vs_invention.md), [review/biggest_misses.md](review/biggest_misses.md). All calls: `data/exports/api_calls.csv`.
- **Description quality (found after pre-registration):** 40 of 1,098 rulings (3.6%) have a cleaned description that is not a product description (`scripts/audit_description_quality.py`, `review/description_quality.md`, hand spot check in `review/description_quality_spotcheck.md`). Excluding them changes no Gate B verdict; ranges move by a few points (see findings.md). The biggest-misses list drops the 5 rows from those rulings, and `demo_data.json` marks them `inadequate_description`.
- **OpenRouter run:** finished 2026-10-07 (the live allowance was 1,000 free requests a day, not 50, so all 200 ran in one day). `scripts/run_openrouter_daily.bat` is a no-op now and exists as insurance; no scheduled task was created for it.
- **Gemini** (`gemini-3.8-flash`, fixed 200-ruling subset in `data/gemini_subset.csv`) is running once a day through Windows Task Scheduler (`GeminiTariffDailyRun`, 09:00) at up to 20 rulings a day, so it should finish about 10 days after it starts counting daily (around 2026-10-17). It is in no table until all 200 are cached (`scripts/models_config.py` skips incomplete runs). Check progress with `python scripts/gemini_status.py`.
- **Parked:** nothing blocking. One pre-registered check did not pass cleanly (1 of 3,294 re-parsed v1.0 answers parsed differently; cached values kept), see DECISIONS.md. The top-ranked free OpenRouter model (Inkling) refused API access, so Nemotron 3 Ultra was used.
- **Tracked in git** (same as the README's "What is tracked" section): `data/raw/rulings/` and `data/raw/search_pages/`, `data/processed/`, `data/compact/` (HTS codes and rates, including `hts_older/` and `hts_rates/` parsed from archived release PDFs), `llm_logs/`, `llm_probes/`, `llm_followups/`, `run_logs/`, `data/exports/`, `review/`, `figures/`, and all scripts. **Not tracked:** `data/raw/hts_revisions/` and `data/raw/hts_older_pdf/`, plus the local-only Gemini files.
- **Duty rates were re-checked** against each ruling-date release's archived PDF: 0 of 4,060 (code, ruling date) pairs differ from the current schedule.
- **Next:** read v1.2 and push it yourself (v1.1 is already pushed). When Gemini reaches 200 rulings: rerun the analysis scripts (it is picked up from config.json automatically), `git add -f llm_logs/gemini-3.8-flash` and the Gemini comparison files that are gitignored, add Gemini to the write-up, and cut the release.

## History

Round-by-round notes. Where an older line was superseded, it has been corrected to match the facts above.

### Round 3 (2026-10-06): invalid-code breakdown, guardrail, dollar figure: DONE

- Lead finding (v1.0 models; v1.1 stronger models behave differently, see findings.md): free models mostly return codes that do not exist (88.7% to 98.4% of wrong answers), and most are not near misses (suffix-only is 6.7% to 22.9% of invalid answers). Outdated codes explain 1 invalid answer. A validity check flags 88.7% to 98.4% of wrong answers; a one-turn retry turned 1.5% to 7.2% of invalid answers into valid codes, none correct. See findings.md and `review/invalid_breakdown.md`, `review/guardrail.md`, `figures/error_breakdown.png`.
- **Data problem found and checked:** the Phase 3 "per-revision" HTS files were all the current schedule (the export API ignores `release`). Impact on validity checks: 1 answer. Duty rates were then re-checked against each ruling-date release: 0 of 4,060 code-date pairs differ. Details in DECISIONS.md.
- Final fixes: validity-check framing (detects 88.7% to 98.4% of wrong answers; retry repairs none), underpay n/CI/baseline p reported per model, and MFN rates re-checked against each ruling-date release (0 of 4,060 code-date pairs had a different rate). A markup bug in rate parsing was fixed in the same pass (Gate 3: 1,077/1,098). See DECISIONS.md.
- Gemini run unchanged (in progress, no results published).

### Task 2 (pre-publish sweep): DONE, all 3 fixes applied (2026-10-05)

Full findings in [review/prepublish_check.md](review/prepublish_check.md); all 3
proposed fixes are now applied, not just reported:
- **No API keys found anywhere they shouldn't be.** The personal email appeared only in
  this report itself; it was redacted and the git history was replaced with a single clean
  commit before publishing.
- **Git identity fix applied:** this repo's local git config now sets `user.name
  "fennaya"` / `user.email "fennaya@users.noreply.github.com"`, so a plain `git commit`
  can no longer silently fall back to the machine's global config.
- **Repo size fix applied:** `data/raw/hts_revisions/` (255 MB of raw USITC dumps) is
  gitignored; a trimmed, gzipped copy is tracked under `data/compact/` and the scripts fall
  back to it. `data/raw/rulings/` and `data/raw/search_pages/` (18 MB) are tracked, as are
  `data/processed/` and `llm_logs/`, so every reported number reproduces from a fresh clone.
- **Data license fix applied:** README now has a "Data license" section citing 17
  U.S.C. § 105 and CBP's own public-domain statement for its site content.

### Task 1 (Gemini as a 4th model): IN PROGRESS, correctly diagnosed and now resumable

- **Root cause of the slow rate, found 2026-10-05 by reading the actual 429 error body**
  (not inferring from timing, which is how the earlier "resets at Pacific midnight"
  theory was wrong): the free tier enforces **two separate quotas** — 5
  requests/minute AND 20 requests/day, each surfaced via its own `quotaId` in the
  structured `QuotaFailure` detail. Exact captured bodies for both are in DECISIONS.md.
  The client now reads the server's own `RetryInfo.retryDelay` directly instead of
  guessing a backoff, and raises a dedicated `GeminiDailyQuotaExceeded` to exit cleanly
  (code 0) specifically on the daily cap, rather than sleeping in-process for hours.
- **Model switched to `gemini-3.8-flash`** (the live model list's strongest Flash model
  with confirmed free-tier access as of 2026-10-05 — it was unusable 3 days earlier and
  has since opened up). Same training cutoff (March 2026, re-confirmed live),
  `thinkingConfig.thinkingLevel: "low"` (the API's minimum — "minimal" errors), no
  `tools` key (grounding/tools off), temperature 0, same prompt.
  `min_request_interval=13.0` paces calls under the 5/min cap proactively.
- **Fixed 200-ruling sample drawn before any new calls:** `data/gemini_subset.csv`
  (seed 20261005, from `scripts/build_gemini_subset.py`), not the full 661-ruling
  eligible pool — a defined, reproducible comparison population rather than whatever
  happened to finish.
- **Runs independent of any Claude Code session now:** `scripts/run_gemini_daily.bat`
  (tested, confirmed exit 0 on hitting the daily cap, logs to
  `logs/gemini_daily.log`, gitignored) is the daily job, registered as the Task Scheduler
  job `GeminiTariffDailyRun` (daily 09:00). At 20/day max, 200 rulings is
  **at least 10 days** even in the best case.
- **`scripts/analyze_gemini_comparison.py` re-pointed to the fixed 200-ruling subset**
  (was the full 661 pool) — the 3 Groq models are re-reported on exactly the same 200
  rulings Gemini runs on, reusing their existing Phase 5 cache (no new Groq calls). Its
  output (`review/gemini_comparison.*`) is gitignored and no Gemini numbers are
  published until all 200 are done; regenerate locally with
  `.venv/Scripts/python scripts/analyze_gemini_comparison.py`.
- **Not yet done:** the Gemini calls (accumulating up to 20/day via the
  scheduled task), final Gate B numbers for Gemini once enough land, and folding Gemini
  into findings.md/README.md as v1.1.

### Summary

- **Round 1 (Phases 0-6):** 1,816 CBP rulings collected, 1,098 usable, 3 free-tier Groq
  models (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b`) run on all of them
  (3,294 calls). All gates (1a/1b/2/3) passed.
- **Round 2, Parts 1-2 (hostile audit):** both headlines re-examined for bugs and tested
  against chance baselines. Gate A (is the low accuracy a bug?): **PASS**. Gate B (does
  the underpay bias beat chance?): **PASS for all 3 models**, p < 0.001 against each
  model's own matched-depth baseline. Two real bugs found and fixed in the audit
  scripts themselves along the way (see DECISIONS.md) — a performance bug and a
  case-counting inconsistency, both caught by comparing against Round 1's own numbers
  rather than trusting the new audit code blindly.
- **Round 2, Part 3:** self-contained HTML review page built, tested, and handed off.
  Aya marked all 100 rows; 84/100 approved in both languages, 93/100 in French, 90/100
  in Arabic.
- **Round 2, Part 4:** same 3 models run on the approved translations (549 more calls,
  one quota crash mid-run, resumed cleanly from cache). Paired McNemar test, paired
  bootstrap, and a Monte Carlo power note computed. **No statistically significant
  accuracy or cost difference was detected between English and either translation, for
  any model** — correctly reported as "not detected at this sample size" (power note:
  only a 10-15 percentage-point gap or larger would be reliably caught with n≈90).
  allam-2-7b's Arabic-vs-English comparison is numerically favorable to Arabic but not
  significant.
- **Five presentation changes applied per explicit request** (2026-10-02, logged in
  DECISIONS.md): 8-digit accuracy is now the lead headline figure; error depth is
  reported as a numeric per-model table; every claim is scoped to "free, open-weight
  models on Groq's free tier" with the 3 model IDs named, and the ATLAS-gap language no
  longer implies the task itself is hard (attributed to model capability/configuration
  instead); permutation p-values at their simulation floor read "p < 0.001"; allam-2-7b
  gets its own Arabic-vs-English section.
- **A Google AI Studio (Gemini) key was checked for and, once provided, verified live**
  (read-only model-list call, no spend) — `gemini-2.5-flash`/`gemini-2.5-pro` are
  available. Not used in Round 1 or 2; it was later used for the Gemini run (see Task 1
  above). History of the check is in BLOCKERS.md.
- `findings.md` and `README.md` are fully rewritten with the audited numbers, correct
  scoping, and language-comparison results. `demo_data.json` and `figures/` regenerated.

### Headline (final)

Three free, open-weight models on Groq's free tier top out at 5.6% accuracy on the
duty-relevant 8-digit US customs code. When wrong in a way that changes the duty rate,
all three underpay significantly more often than chance baselines predict
(p < 0.001 per model, n = 46 / 49 / 116 rate-changing errors; v1.0 models only, the lean is 51% to 60% in the stronger v1.1 models) — the legally dangerous
direction. This is a finding about these three free-tier models, not evidence the
classification task itself is unusually hard: prior work reports 10-digit scores of about
12.5% to 40% under different conditions (ATLAS), and the stronger v1.1 models score 12.4% to 31.7% at 10 digits.

### What's NOT done (possible future rounds, not started)

- Gemini's run is in progress, not complete: see Task 1 above; it goes into v1.1.
- No larger-sample language comparison to resolve the "not detected at this sample
  size" result.
- No testing of non-free-tier or fine-tuned models.

### Known operational notes (for anyone resuming or extending this)

- This machine's `ps aux` shows process names without the `.exe` extension.
- Groq's rate limits are per-model — run multi-model work as separate processes.
- `llm_logs/<model>/lang_fr/` and `lang_ar/` hold the translation-run results, separate
  from English results in `llm_logs/<model>/`. Any script globbing `llm_logs/` for
  "models" must exclude `lang_*` directories (see DECISIONS.md — this bug hit 4 scripts
  before being caught).
- `.env` holds GROQ_API_KEY and GOOGLE_API_KEY locally; gitignored, never committed or
  printed (see DECISIONS.md).

### Blockers

None open. See [BLOCKERS.md](BLOCKERS.md) for the full history (both resolved): the
original missing LLM key, and the stronger-model-availability check.
