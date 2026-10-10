# Pre-registration for v1.2 (written before any v1.2 model call)

Written 2026-10-10 and committed before any model call for this round. v1.2 is run exactly like v1.1 (PREREG_v1.1.md): same prompt, same temperature, same scoring code, same metrics, same Gate B rule. Nothing here is changed after results are seen; departures are appended under "Deviations", dated.

**Unchanged from v1.0 and v1.1:** `PROMPT_TEMPLATE` in `scripts/run_llm_classification.py`, temperature 0, the parser as updated in v1.1, `max_tokens` 2048, no tools, no web search (never an `:online` id), and every scoring function. No v1.0 or v1.1 result file is overwritten.

## 1. What is run

All calls go through OpenRouter (key in `.env`, never printed, logged or committed). Model ids were read from the live OpenRouter model list on 2026-10-10, not guessed; `:online`, `:batch`, `:free`, `-pro` and other variants are excluded.

| Part | Model (OpenRouter id) | List price per 1M tokens (in / out) | Rulings |
|---|---|---|---|
| A. Extension | `openai/gpt-6-sol` | $2 / $10 | the 898 usable rulings it has not yet seen, added to the 200 already cached in v1.1 (all 1,098) |
| B. New | `anthropic/claude-haiku-5.5` | $0.10 / $0.50 | all 1,098 |
| B. New | `anthropic/claude-sonnet-5.5` | $2 / $10 | all 1,098 |
| B. New | `anthropic/claude-opus-5.5` | $4 / $20 | all 1,098 |
| C. Replication | `moonshotai/kimi-k3` | $0.80 / $13.50 | all 1,098 |
| C. Replication | `deepseek/deepseek-v4.1-flash` | $0.30 / $1.20 | all 1,098 |
| C. Replication | `z-ai/glm-5.3` | $0.039 / $6 | all 1,098 |

Models that are not listed are skipped and reported. Run order: gpt-6-sol, Claude Haiku, Claude Sonnet, Claude Opus, DeepSeek, GLM, Kimi, preceded by a 50-ruling pilot per model, one model at a time, after which the run waits for an explicit go-ahead.

## 2. Part A: extension

`openai/gpt-6-sol` goes from the fixed 200-ruling sample to all 1,098 usable rulings. The 200 v1.1 responses stay as they are and are never resent; the remaining 898 are added to the same cache folder. Its configuration (reasoning effort none) is the one used in v1.1. Its stated cutoff now comes from OpenAI's own page (https://developers.openai.com/api/docs/models/gpt-6-sol: "Apr 20, 2026 knowledge cutoff"), where v1.1 used a third-party report.

## 3. Part B: Claude models

The three Claude models run on all 1,098 rulings with thinking or reasoning off where the model accepts it and otherwise at the lowest level accepted, tested on one call per model and recorded in an addendum before the pilot. Training cutoff, from Anthropic's models overview (https://platform.claude.com/docs/en/models/overview, which docs.claude.com redirects to): reliable knowledge cutoff Jun 2026 and training data cutoff Jun 2026 for all three. The later of the two is the same month, so the cutoff date used is 2026-06-30 (end of the month, the conservative choice). Their primary scores therefore use only rulings dated after 2026-06-30.

## 4. Part C: provider replication

Kimi K3, DeepSeek V4.1 Flash and GLM 5.3 are rerun through OpenRouter on all 1,098 rulings with Baseten excluded as a provider (`provider.ignore = ["Baseten"]`), to test whether the v1.1 results hold across providers. The primary results for these three models stay the v1.1 Baseten runs. The replication is reported separately and never enters a main table. Reasoning is off with the same setting as in config.json for each model in v1.1 (Kimi and DeepSeek `reasoning_effort` none; GLM thinking disabled), translated to OpenRouter's parameter names and tested on one call per model. For each model the replication reports:

- **agreement rate**: share of the 1,098 rulings on which both runs return the identical predicted code, and the same for the first 8 digits;
- **8-digit accuracy difference** (OpenRouter minus Baseten) on the same rulings with a 95% CI from a paired bootstrap (10,000 resamples, seed 20261010);
- the serving provider recorded in each response, counted per model, and the number of answers that differ in validity.

No threshold for "replicated" is set in advance; the numbers are reported as they are.

## 5. Metrics and rules (as in v1.1)

- 8-digit accuracy on rulings after the model's stated cutoff (6- and 10-digit alongside), with Wilson 95% CIs; the full-sample figure is secondary and labelled.
- Invalid share, the format-versus-invented split (groups a to e), the validity check, the underpay share among rate-changing errors with Wilson CI and both chance baselines, and median duty at stake per $100,000 (MFN-only lower bound).
- **Gate B:** "underpays more than chance" only if the share beats Baseline 2 at p < 0.05 and n >= 30 rate-changing errors; otherwise "same direction, too few cases to confirm (n = X)" or "not distinguishable from chance". The Holm correction across all main-table models and the exclusion of the 40 INADEQUATE descriptions (`review/description_quality.md`) are reported as sensitivity checks, as in v1.1.
- **Contamination rule:** a model's training cutoff is taken from the vendor's official page, and its cutoff and URL are recorded in `config.json`. Headline numbers use only rulings dated after the stated cutoff. If fewer than 30 rulings remain after the cutoff, the result is descriptive only. A model with no vendor-stated cutoff carries the † label ("contamination not ruled out (no stated cutoff); treat accuracy as an upper bound") and its primary score uses all rulings. A cutoff known only from a third party is treated as not stated. The three replication models and the three v1.1 Baseten models have no vendor-stated cutoff and keep the † label.
- **Same-sample table:** all main-table models on the post-cutoff rulings that every one of them shares, so the comparison is on identical rulings.

## 6. Guards on every call

- The key is never printed, logged or committed.
- **Spend:** hard stop when cumulative `usage.cost` of v1.2 calls passes $25. Cost is read from each response's own `usage.cost` and summed.
- **Model check:** each response's `raw_response.model` must match the requested model (compared lowercased, with "." and "-" treated alike, on the last path segment of the id); a mismatch is marked failed and retried once. The serving `raw_response.provider` is recorded; for Part C a response served by Baseten is treated as a failed call and retried once.
- Outputs go to their own folders: `llm_logs/anthropic/<model>/` for Claude, `llm_logs/openrouter_replication/<model>/` for Part C, and the existing `llm_logs/openai/gpt-6-sol/` for the extension, so no v1.1 file is overwritten. Every cached file holds the full raw response, usage, finish_reason, serving provider and request time.
- Every call is appended to `run_logs/api_calls.jsonl`.
- On HTTP 429 or 5xx the call backs off and retries; a run resumes from cache and never resends a finished ruling.

## 7. Analysis

Every script that names models reads them from `config.json`. A v1.2 section is added to `findings.md` with three parts (extension, Claude, replication) and the v1.1 text stays intact. The v1.1 self-attack checks (`review/v1_1_attack.md`) are repeated on the new results. All deviations are logged in DECISIONS.md and in a "Deviations from pre-registration" subsection. No other tests are added after results are seen.

## Addendum A: reasoning settings found (2026-10-10, before any pilot or full run)

One test call per setting on the first usable ruling, real prompt, temperature 0, `max_tokens` 2048; log in `run_logs/v1_2_settings_test.json`; test spend $0.0649 (counted against the $25 cap). The returned `model` matched the request in every accepted call and no response was served by Baseten.

| Model | Accepted setting | Reasoning tokens in the test | Notes |
|---|---|---|---|
| `anthropic/claude-haiku-5.5` | `reasoning.effort = none` | 0 | |
| `anthropic/claude-sonnet-5.5` | `reasoning.effort = minimal` | 0 reported | "none" and `enabled = false` rejected: "Reasoning is mandatory for this endpoint and cannot be disabled." The answer was 1,120 characters (452 output tokens). |
| `anthropic/claude-opus-5.5` | `reasoning.effort = low` | 424 | Same rejection for "none". Minimal gave 517, no parameter 778. Reasoning cannot be turned off for this model. |
| `moonshotai/kimi-k3` (replication) | `reasoning.effort = none` | 0 | served by Wafer |
| `deepseek/deepseek-v4.1-flash` (replication) | `reasoning.effort = none` | 0 | served by Morph |
| `z-ai/glm-5.3` (replication) | `reasoning.effort = low` | 180 | "none" and `enabled = false` rejected. Minimal gave 197; no parameter gave 2,044 reasoning tokens and an empty answer. Providers seen: Sail Research, Alibaba, Z.AI. |

`openai/gpt-6-sol` keeps its v1.1 setting (`reasoning.effort = none`).

## Deviations

- **2026-10-10, reasoning could not be turned off for three models.** Section 3 and 4 say "off where the model accepts it, otherwise the lowest level accepted, with the same settings as in v1.1". Sonnet 5.5 (minimal), Opus 5.5 (low) and GLM 5.3 on OpenRouter (low) reject "off". The GLM replication therefore differs from the v1.1 Baseten run, which used `thinking: disabled` (about 140 reasoning tokens per call); a difference between the two GLM runs can come from the setting as well as from the provider.
