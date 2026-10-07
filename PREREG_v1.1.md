# Pre-registration for v1.1 (written before any new model call)

Written 2026-10-07, committed before any API call for this round. v1.0 (DOI 10.5281/zenodo.23197896) tested three free Groq models on 1,098 post-cutoff CBP rulings. A reviewer raised two objections: (1) small free models are easy to dismiss, so test stronger ones; (2) how much of the "invalid code" rate is formatting or parsing, and how much is the model inventing a code. v1.1 answers both. Nothing in this file is changed after results are seen; any departure is appended below under "Deviations", dated.

## 1. Models and samples

| Group | Models | Sample |
|---|---|---|
| Unchanged from v1.0 | `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b` (Groq) | all 1,098 usable rulings (their v1.0 numbers must not change) |
| Baseten (free credits only) | DeepSeek V4.1 Flash, GLM 5.3 (not the Fast or Flash variants), Kimi K3 | all 1,098 usable rulings; run one at a time, cheapest first |
| OpenRouter (free tier only) | exactly one model whose id ends in `:free` and whose listed prompt and completion prices are both "0" | the fixed 200-ruling sample in `data/gemini_subset.csv` |

Exact Baseten slugs are read from Baseten's live `/models` list (never guessed) and written to an addendum in this file before any inference call. The OpenRouter model is chosen by this rule: the strongest general model from a family not already tested (not gpt-oss, allam, DeepSeek, GLM, Kimi, or Gemini), ranked by parameter count and then recency as stated on its OpenRouter page. The choice and reason are logged in DECISIONS.md and added to the addendum. If no free model qualifies, it is parked in BLOCKERS.md.

Closed frontier models (GPT, Claude, Gemini) are not tested in v1.1. None of the models above is described as a stand-in for them.

## 2. Prompt and settings

- Prompt: `PROMPT_TEMPLATE` in `scripts/run_llm_classification.py`, unchanged from v1.0.
- Temperature 0, no tools, no web search (never an `:online` id), `max_tokens` = 2048.
- Reasoning: the lowest level each model accepts (off if possible, otherwise low), tested with one call per model; what was accepted is logged.
- Every cached response stores the full raw response, usage block, finish_reason, serving provider (OpenRouter returns it), and request time.

## 3. Primary metrics

1. 8-digit accuracy on post-cutoff rulings (Section 4), with Wilson 95% CIs; 6- and 10-digit alongside; the full-sample figure is secondary and labelled.
2. Invalid share (answers that are unparseable or not a 10-digit code in the HTS), with Wilson CI.
3. The format vs invented split of invalid answers (Section 6).
4. Underpay share among rate-changing errors, with Wilson CI and both chance baselines. Gate B rule: a model "underpays more than chance" only if it beats Baseline 2 (matched depth) at p < 0.05 and has n >= 30 rate-changing errors. Otherwise the text reads "same direction, too few cases to confirm (n = X)" or "not distinguishable from chance".
5. Median duty at stake per $100,000 declared (MFN-only lower bound), and the validity-check detection and false-flag rates.

The OpenRouter model has n <= 200; its n is always shown and it is compared only with other models restricted to the same 200 rulings.

## 4. Contamination checks

Rulings run 2026-01-05 to 2026-08-14. For each new model the publicly stated training cutoff and its source URL are recorded ("unknown" if not found). The primary score uses only rulings dated after the model's cutoff. If the cutoff is unknown or after 2026-08-14 the model is labelled "contamination not ruled out" and its post-cutoff and full-sample figures coincide. The same label applies to `allam-2-7b` (cutoff not stated).

- **Check A, memorisation probe.** One fixed random sample (seed 20261007, saved to `data/probe_ids.csv`): 100 rulings for the Baseten models, the first 25 of the same list for the OpenRouter model. The only question asked is: "What 10-digit HTSUS code did CBP assign in ruling <ruling number>? Reply with JSON {"hts_code": ...}". No description is given. Exact 10-digit and 8-digit hits are reported. Clearly above zero is read as likely memorisation.
- **Check B, month trend.** 8-digit accuracy by ruling month, per model.

Both are reported whatever they show.

## 5. Parser change

`parse_prediction` is updated to strip `<think>...</think>` blocks and take the last JSON object containing "hts_code". Every cached response of the three original models is re-parsed and the predicted code must be identical; if any differs the work stops. finish_reason is counted per model; a truncated answer is a parse failure and is reported separately.

## 6. Format vs invented

Every invalid answer goes into exactly one group:

- FORMAT: (a) unparseable, no code, or truncated; (b) first 8 digits right but suffix missing (answers with exactly 8 digits counted separately); (c) first 8 digits right but wrong suffix. The single v1.0 "outdated" answer is counted under FORMAT.
- INVENTED: (d) the 6-digit subheading exists but no tariff line starts with the answer's first 8 digits; (e) even the 6-digit subheading does not exist.

For the three original models the groups must sum to 1,080 / 1,061 / 957 invalid answers; otherwise the work stops. Counts and shares of all answers and of invalid answers are reported with Wilson 95% CIs.

## 7. Exploratory extras (cached data only, no new calls; labelled EXPLORATORY)

1. Paired McNemar tests at 6 and 8 digits between every pair of models on shared rulings; also 4-digit heading accuracy and the share of wrong answers with the right heading.
2. Agreement: how often 2+ (and 3+) models give the same 8-digit code, and how accurate that agreed code is compared with each model alone.
3. Duty at the 8-digit level: for answers whose first 8 digits exist, price the error at 8 digits; underpay share with CI and both baselines under the Gate B rule, labelled secondary, with the number of added cases.
4. `review/biggest_misses.md`: the 10 largest underpayments and 10 largest overpayments per $100,000 across all models (MFN lower bound), with ruling number, description, official and model codes and rates, and the dollar gap.
5. Cost to run: per model, average input and output tokens, seconds per call, finish_reason counts, and list-price cost per 1,000 rulings.

The total number of extra tests run is stated in the write-up. No other tests will be added after results are seen.

## 8. Spend rules

- Baseten: free credits only. No payment method is added or requested and the plan is not upgraded. Cost is projected from the pilot's real token use and Baseten's published prices before each full run; any billing, credit, quota, or 402 error stops all Baseten runs at once and the cache is kept.
- OpenRouter: only `:free` ids with both listed prices "0", checked in code before every run. `GET /api/v1/key` is checked before the first call and after every batch; if `usage` rises above its starting value all OpenRouter calls stop. Pace: one request every 4 seconds; stop cleanly when the daily free-request allowance reaches 0.

## Addendum A: slugs and settings (2026-10-07, before any full run or pilot)

Read from the live APIs, not guessed.

| Model | Provider | Slug | Prices per 1M tokens (in / out) |
|---|---|---|---|
| DeepSeek V4.1 Flash | Baseten | `deepseek-ai/DeepSeek-V4.1-Flash` | $0.30 / $1.20 |
| GLM 5.3 | Baseten | `zai-org/GLM-5.3` | $1.40 / $4.40 |
| Kimi K3 | Baseten | `moonshotai/Kimi-K3` | $3.00 / $15.00 |
| Inkling | OpenRouter | `thinkingmachines/inkling:free` | free (prompt and completion "0") |

Baseten prices re-checked at baseten.co/pricing on 2026-10-07 and unchanged. OpenRouter choice: of the 16 free models with both prices "0", the strongest general model from an untested family by the pre-registered ranking is Inkling (Thinking Machines; 975B total, 41B active parameters, general-purpose, created 2026-07-17). The next largest, NVIDIA Nemotron 3 Ultra (550B total, 55B active, created 2026-06-04), is smaller and older. Baseten authentication is `Authorization: Api-Key <key>`.

Reasoning settings accepted (one test call per setting on one ruling; the default for all three at `max_tokens` 2048 was 1,500 to 2,048 reasoning tokens, and GLM 5.3 and Kimi K3 truncated with an empty answer):
- DeepSeek V4.1 Flash: `reasoning_effort: "none"` (0 reasoning tokens).
- Kimi K3: `reasoning_effort: "none"` (0 reasoning tokens).
- GLM 5.3: `thinking: {"type": "disabled"}` (the lowest of four settings tried; it still emitted 112 reasoning tokens on the test ruling, so reasoning cannot be fully turned off for this model).
- Inkling: tested before its first call and recorded in DECISIONS.md.

## Deviations

- **2026-10-07, order of operations.** The one-call-per-model slug and reasoning probes (4 variants for GLM 5.3, 1 to 3 for the others, all on the first usable ruling) were run before Addendum A was committed. No result on any ruling was looked at beyond token counts and whether an answer was produced.
- **2026-10-07, GPT-6 Sol not run.** The user asked mid-run to include "GPT 6 SOL" among the models. On OpenRouter it is a paid model ($2 in / $10 out per 1M tokens), which the zero-spend rule forbids; it is parked in BLOCKERS.md until explicit permission to spend is given. Nothing was called.
- **2026-10-07, Gemini 3.8 Flash added.** The user asked to include `gemini-3.8-flash`. It is already running once a day on the 200-ruling sample (free tier, no spend). It enters the analysis only as a model on those 200 rulings, labelled with its n, and the headline tables include it only once all 200 are cached. Its cutoff is March 2026 (published model card). It gets no memorisation probe, to keep its small daily quota for the main run.
- **2026-10-07, OpenRouter daily allowance.** The pre-registration assumed 50 free requests per day. The live `/key` endpoint reports `free_model_daily_requests.limit` = 1000 (remaining 1000) and `usage` = 0. The pre-registered stop rule ("stop when remaining reaches 0", and "stop if `usage` rises") is unchanged; the full 200 may therefore run on one day.
