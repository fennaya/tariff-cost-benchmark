# Status

**v1.0 is ready to publish now, with the 3 Groq models' results complete and final.**
Gemini is a 4th model running in the background on its own fixed sample, tracked
separately and explicitly labeled "in progress, v1.1" everywhere it's mentioned
(README, findings.md) so nothing in v1.0 depends on it landing.

## Round 3 (2026-10-06): invalid-code breakdown, guardrail, dollar figure: DONE

- Lead finding now: free models mostly return codes that do not exist (88.7% to 98.4% of wrong answers), and most are not near misses (suffix-only is 6.7% to 22.9% of invalid answers). Outdated codes explain 1 invalid answer. A one-turn guardrail fixes 1.5% to 7.2% of invalid answers, none correctly. See findings.md and `review/invalid_breakdown.md`, `review/guardrail.md`, `figures/error_breakdown.png`.
- **Data problem found and checked:** the Phase 3 "per-revision" HTS files were all the current schedule (the export API ignores `release`). Impact on validity checks: 1 answer. Duty rates not re-checked against ruling-date releases (stated as a limitation). Details in DECISIONS.md.
- Final fixes: validity-check framing (detects 88.7% to 98.4% of wrong answers; retry repairs none), underpay n/CI/baseline p reported per model, and MFN rates re-checked against each ruling-date release (0 of 4,060 code-date pairs had a different rate). A markup bug in rate parsing was fixed in the same pass (Gate 3: 1,077/1,098). See DECISIONS.md.
- Gemini run unchanged (in progress, no results published).

## Task 2 (pre-publish sweep): DONE, all 3 fixes applied (2026-10-05)

Full findings in [review/prepublish_check.md](review/prepublish_check.md); all 3
proposed fixes are now applied, not just reported:
- **No API keys or the personal email found anywhere they shouldn't be** — confirmed
  clean, no fix needed.
- **Git identity fix applied:** this repo's local git config now sets `user.name
  "fennaya"` / `user.email "fennaya@users.noreply.github.com"`, so a plain `git commit`
  can no longer silently fall back to the machine's global config.
- **Repo size fix applied:** `data/raw/hts_revisions/`, `data/raw/rulings/`, and
  `data/raw/search_pages/` (~272 MB of bulk, mechanically-fetched government data) are
  now gitignored and untracked (`git rm --cached`) — they stay on disk and are each
  individually regenerable via the existing fetch scripts, or restorable from this
  project's Zenodo archive once published. `data/processed/` and `llm_logs/` (the
  evidence behind every reported number) remain in git.
- **Data license fix applied:** README now has a "Data license" section citing 17
  U.S.C. § 105 and CBP's own public-domain statement for its site content.

## Task 1 (Gemini as a 4th model): IN PROGRESS, correctly diagnosed and now resumable

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
  `logs/gemini_daily.log`, gitignored) is the daily job; see the repo root for the one `schtasks`
  command to register it with Windows Task Scheduler. At 20/day max, 200 rulings is
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

## Summary

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
  available if a future round wants a stronger-model comparison. Not used this round;
  logged in BLOCKERS.md as available-but-unused, since adding a 4th model and a
  different API shape is a real scope expansion that needs an explicit ask.
- `findings.md` and `README.md` are fully rewritten with the audited numbers, correct
  scoping, and language-comparison results. `demo_data.json` and `figures/` regenerated.

## Headline (final)

Three free, open-weight models on Groq's free tier top out at 5.6% accuracy on the
duty-relevant 8-digit US customs code. When wrong in a way that changes the duty rate,
all three underpay significantly more often than two chance baselines predict
(p < 0.001 per model against the harder baseline) — the legally dangerous direction.
This is a finding about these three free-tier models' capability, not evidence the
classification task itself is unusually hard: non-fine-tuned frontier models in prior
work (ATLAS's own baselines) score 7-15x higher.

## What's NOT done (possible future rounds, not started)

- Gemini's run is in progress, not complete — see Task 1 above; tracked for v1.1, not
  v1.0.
- No larger-sample language comparison to resolve the "not detected at this sample
  size" result.
- No testing of non-free-tier or fine-tuned models.

## Known operational notes (for anyone resuming or extending this)

- This machine's `ps aux` shows process names without the `.exe` extension.
- Groq's rate limits are per-model — run multi-model work as separate processes.
- `llm_logs/<model>/lang_fr/` and `lang_ar/` hold the translation-run results, separate
  from English results in `llm_logs/<model>/`. Any script globbing `llm_logs/` for
  "models" must exclude `lang_*` directories (see DECISIONS.md — this bug hit 4 scripts
  before being caught).
- `.env` holds GROQ_API_KEY and GOOGLE_API_KEY locally; gitignored, never committed or
  printed (see DECISIONS.md).

## Blockers

None open. See [BLOCKERS.md](BLOCKERS.md) for the full history (both resolved): the
original missing LLM key, and the stronger-model-availability check.

---

**v1.0 is ready to publish now** (3 Groq models, complete and audited). Gemini
continues accumulating in the background via the scheduled daily task and will be
folded in as v1.1 once its 200-ruling run completes — no action needed to wait for it.
