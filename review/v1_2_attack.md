# v1.2 self-attack: arguing against my own results

Written after the v1.2 runs, as a hostile reviewer would, repeating the checks of `review/v1_1_attack.md` on the new results. Every number below is in `review/v1_1_results.md`, `review/format_vs_invention.md`, `review/invalid_breakdown.md`, `review/validity_check.md`, `review/replication.md`, `PREREG_v1.2.md` or `DECISIONS.md`. Anything I cannot defend is copied into the v1.2 "Limits" list in `findings.md`.

## 1. "The strongest models just memorised the rulings." (and the time-drift test)

- *Evidence against.* The memorisation probe from v1.1 (ruling number only, no description) gave 0 hits for every model it was run on. It was not repeated for the Claude models or for GPT-6 Sol beyond its v1.1 25 probes, so v1.2 adds no new evidence on this point.
- *Concession 1 (the warning sign got stronger for GPT-6 Sol).* With all 1,098 rulings GPT-6 Sol scores 58.9% at 8 digits on the 560 rulings up to its stated cutoff (2026-04-20) and 49.6% on the 538 after it (intervals 54.8% to 62.9% and 45.4% to 53.8%). In v1.1, with 33 rulings before the cutoff, the two figures were 48.5% and 49.7%, so the v1.1 statement that GPT-6 Sol showed no cliff at its cutoff does not survive the larger sample; it is corrected in findings.md and here.
- *Time-drift test (added after the results, `review/time_drift.md`, no new calls).* Every model's full-sample answers split at the same date (2026-04-20). gpt-oss-120b (cutoff 2024, cannot have seen any ruling) goes 5.9% to 5.2% (p = 0.62) and gpt-oss-20b 0.0% to 0.6%; the Baseten DeepSeek, GLM and Kimi runs fall 7.7, 7.7 and 9.7 points (p = 0.009, 0.003, 0.001); GPT-6 Sol falls 9.3 points (p = 0.002). By the rule set beforehand, the lack of a drop in the 2024-cutoff models would make contamination the more likely reading and the † models' all-1,098 numbers would be called likely inflated. That is the rule's output, not a finding: see the next point.
- *Why I do not lean on that.* The 2024-cutoff control is at the floor: a drop of Sol's relative size (16%) would be 0.03 points for gpt-oss-20b and 0.93 points for gpt-oss-120b, and the test has 5% and 10% power to see it. No drop there is not evidence of no drop. On the other side, Claude Sonnet 5.5 has a cutoff of June 30, so both sides of April 20 are inside its training window, yet it falls 7.1 points (p = 0.018) across that date, and the OpenRouter replications of Kimi, DeepSeek and GLM also fall (10.2, 5.7, 4.0 points). That fits harder or different later rulings. The two explanations are not separated by this data, and both could be true. A clean control would be a model with a mid-window cutoff and a known training set, which I do not have. The conservative consequences are kept either way: primary scores use only post-cutoff rulings, and † models' numbers are upper bounds.
- *Concession 2.* The three Claude models have a stated cutoff of "Jun 2026", so only the 228 rulings dated July and August 2026 count as primary. Sonnet 5.5 falls from 46.1% (870 rulings) to 40.4%, Opus 5.5 from 55.9% to 53.5% and Haiku 5.5 from 18.3% to 17.5%. The Opus and Haiku differences are well inside their intervals; Sonnet's is not clearly outside. If the real cutoff were earlier than the stated month, the primary rows would be even cleaner; if the vendors' statement is optimistic, they are not. I recorded only vendor-stated dates and did not second-guess them.
- *Concession 3.* DeepSeek V4.1 Flash, GLM 5.3, Kimi K3 and allam-2-7b still have no stated cutoff, so all four are marked † and their accuracy is an upper bound.
## 2. "The pipeline changed between v1.1 and v1.2, so old and new numbers are not comparable."

- The prompt template, temperature (0), parser, validity check and scoring code were not changed. The v1.0 rows for the three Groq models and the v1.1 rows for DeepSeek, GLM, Kimi and Nemotron are identical to the published ones in `analysis_results.json`, `invalid_breakdown.json`, `validity_check.json` and `underpay_summary.json`; only GPT-6 Sol's row changed, as it should after 898 more rulings.
- Every new answer's returned model name was compared with the requested one: 1,098 of 1,098 matched for each of the seven new caches. None of the 3,294 replication answers was served by Baseten.
- *Concession.* The analysis scripts were rewritten to read models from `config.json` and gained same-sample table B and the replication script. These are code changes after the v1.1 publication, though not changes to scoring.
- Parse failures are small but not zero: Claude Haiku 14, and in the replication DeepSeek 9 and GLM 42 (counted as invalid answers, as in v1.1). Non-stop finish reasons: Haiku 1, DeepSeek replication 6, GLM replication 13.

## 3. "Your differences between the top models are inside the noise."

- The gap between groups is real: the three small models are under 6% against 17.5% to 53.5% for the other eight.
- *Concession.* Inside the top group the picture is closer. On the same 1,098 rulings (all dates, exploratory McNemar) Opus 5.5 and GPT-6 Sol are indistinguishable at 8 digits (129 vs 140 discordant, p = 0.54) and at 6 digits (p = 0.12); on the 228 post-cutoff rulings they share, 53.5% (47.0% to 59.9%) and 49.1% (42.7% to 55.6%) overlap. Sonnet 5.5 and Kimi K3 are also indistinguishable at 8 digits (127 vs 143, p = 0.36). Opus 5.5 is above Sonnet 5.5 and Kimi K3 (p < 0.0001 on all dates) and GPT-6 Sol is above Sonnet 5.5 (p < 0.0001). So "neither Opus 5.5 nor GPT-6 Sol is clearly the best" is what I can support; "the best two" is only a statement about the point estimates.
- 121 exploratory tests were run in total (64 in v1.1), none corrected for multiple comparison.

## 4. "The underpay finding fades in the most accurate models" may be over-read.

- Gate B as pre-registered is met for 7 of 11 models and for 6 of 11 under Holm; the one change is Claude Haiku 5.5 (p = 0.021, adjusted p = 0.105).
- The two most accurate models are the two where it is not met: GPT-6 Sol 52.2% underpaid (n = 138, p = 0.092) and Claude Opus 5.5 45.1% (n = 51, p = 0.586). The one in between on accuracy, Claude Sonnet 5.5, is at 57.1% (n = 49, p = 0.059), also not met.
- *Concessions.* This is three or four models, not a trend test; I did not model accuracy against share. Opus 5.5's n = 51 and Sonnet's n = 49 are close to the n = 30 floor and the intervals are wide (32.3% to 58.6% for Opus, 43.3% to 70.0% for Sonnet). On the shared sample (table B) the underpay shares of the seven stronger full-sample models sit between 45% and 62%. The honest statement is "the lean is not detected in the two most accurate models", not "better models stop underpaying". The v1.1 conclusion (small lean in some, none in others) stands.
- Excluding the 40 INADEQUATE rulings changes no verdict among all 11 models.

## 5. "228 rulings is too small for the Claude models."

- *Supports:* the gap between Haiku (17.5%), Sonnet (40.4%) and Opus (53.5%) at 8 digits (intervals about plus or minus 6 points and mostly separated), and the validity-check numbers (41.2% of Opus' wrong answers are non-existent codes, 52.4% for Sonnet, 72.2% for Haiku).
- *Does not support:* a ranking of Opus against GPT-6 Sol or Kimi, month trends (84 to 144 rulings per month at most), the format-versus-invention split of Opus to better than a few points (it has 63 invalid answers on the 228), or Gate B verdicts (n = 49 to 65).
- Table A (all 11 models) has only 68 rulings because Nemotron 3 Ultra ran on 200; its numbers are only descriptive.

## 6. "Reasoning was set differently across the models, so the comparison is unfair."

- Yes, and it is in the deviations. Haiku 5.5 ran with reasoning off; Sonnet 5.5 (minimal) and Opus 5.5 (low) could not be turned off. Opus used about 297 reasoning tokens per answer, so its 53.5% is not a no-reasoning result like GPT-6 Sol's. Sonnet reports no reasoning tokens but wrote about 517 output tokens per call. GLM 5.3 on OpenRouter ran at low effort against "thinking disabled" on Baseten.
- The results describe single-shot, low-effort use. They are not the ceiling of any model, and Opus' edge over GPT-6 Sol may partly be extra reasoning.

## 7. "The replication shows nothing, or shows the opposite of what you say."

- *What it shows.* 8-digit accuracy differs by -1.3 (Kimi K3), -0.6 (DeepSeek V4.1 Flash) and -2.5 points (GLM 5.3) between the Baseten run and the OpenRouter rerun, with paired-bootstrap 95% intervals of -2.4 to -0.2, -2.1 to +0.8 and -4.8 to -0.1. The invalid share moves by less than one point.
- *Concessions.* Individual answers are not reproducible across providers at temperature 0: 85.2%, 80.5% and 23.0% of the rulings get the identical code (Kimi, DeepSeek, GLM). The three differences are all negative; with two intervals just excluding zero I cannot say that is chance. OpenRouter routed the replication to 18 to 31 different providers, so the replication is a provider mix, not one alternative host; some of those hosts may serve quantised weights, which I did not check. GLM's low agreement mixes provider and reasoning setting. No threshold for "replicated" was pre-registered, so the word is a judgement. The Baseten runs stay primary because they were first and were pre-registered as such.

## 8. Other points a reviewer would raise

- **"Invalid" is a strict rule.** Correct 10-digit answers are rarely flagged (0 of 75 Opus, 0 of 58 Sonnet, 3 of 175 GPT-6 Sol, 0 of 19 Haiku), but a validity check also flags 8-digit-correct answers (27 of 122 Opus, 20 of 92 Sonnet, 46 of 267 GPT-6 Sol), so it is a review trigger, not a classifier.
- **Suffix slips are not "nearly right".** Among Opus' 229 answers whose first 8 digits are a real tariff line but whose suffix is wrong or missing, only 131 (57%) have the true code's first 8 digits; the rest name a different line. For the suffix-only slips of Haiku the picture is similar (94 of 343 format answers).
- **Stale training data is still visible.** 93 of Opus' invalid answers (8.5% of all rulings), 73 of Sonnet's, 88 of GPT-6 Sol's and 45 of Haiku's are 10-digit codes that existed in a 2022 to 2025 HTS release but not in the 2026 schedule. A validity check cannot fix a model whose suffix table is a year old.
- **Cost.** The round cost $21.36 in OpenRouter usage (cap $30), $10.96 of it for Opus 5.5 and $6.60 for Sonnet 5.5. The cap was raised from $25 on the user's instruction after the pilot; the spend stayed under the original cap.
- **Closed models.** GPT-6 Sol and the three Claude models are one model each on one task; nothing here says how other GPT, Claude or Gemini models would score. Gemini 3.8 Flash is in no table.
- **Duty figures.** MFN-only lower bounds, unchanged from v1.1.
