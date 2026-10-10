# v1.1 self-attack: arguing against my own results

Written before the write-up, as a hostile reviewer would. Every number below is in `review/v1_1_results.md`, `review/format_vs_invention.md`, `review/guardrail.md` or `DECISIONS.md`. Anything I cannot defend is copied word for word into the Limitations section of `findings.md`.

## 1. "The stronger models just memorised the rulings."

- *Evidence against.* Check A asked each model for the code of a ruling from the number alone, with no description. Exact 10-digit, 8-digit and 6-digit hits were 0 for every model: 0 of 100 for Kimi K3 (95% CI 0.0% to 3.7%), which answered all 100 probes with a code, 0 of 25 for Nemotron 3 Ultra and GPT-6 Sol (CI up to 13.3%). Check B shows no cliff at the stated cutoff for GPT-6 Sol: 48.5% at 8 digits on rulings up to its cutoff (n = 33) and 49.7% after it (n = 167). **[Corrected in v1.2: with all 1,098 rulings GPT-6 Sol scores 58.9% before its cutoff (n = 560) and 49.6% after it (n = 538), so there is a drop; see review/v1_2_attack.md and review/time_drift.md.]**
- *Concession 1.* DeepSeek V4.1 Flash and GLM 5.3 refused 96 and 95 of 100 probes ("I don't have access to the specific contents"). A refusal is not evidence that the ruling is not memorised, so Check A is nearly uninformative for those two. Check A also tests recall of a bare number, which is a harder question than recognising a product description.
- *Concession 2.* Nemotron 3 Ultra scored 34.7% (n = 95, rulings on or before its 2026-05-31 cutoff) and 23.8% (n = 105, after it). The intervals overlap (25.9% to 44.7% vs 16.7% to 32.8%), so this is not a test, but it is the direction a contamination effect would take. This is why the primary figure uses only post-cutoff rulings.
- *Concession 3.* The cutoffs of DeepSeek V4.1 Flash, GLM 5.3 and Kimi K3 are not stated on their official model cards, so all three are labelled "contamination not ruled out" and their primary rows are all rulings. Their accuracy by month falls from 48% to 53% in January and February to 29% to 37% in May to July (Kimi and DeepSeek). That could be case mix, or early rulings being easier to recall; v1.1 cannot separate the two.
- GPT-6 Sol's cutoff (2026-04-20) comes from a third-party report, not an OpenAI page.

## 2. "The parser change moved your v1.0 numbers."

- All 3,294 cached v1.0 answers were re-parsed with the new parser: 3,293 identical, 1 different (allam-2-7b, ruling N358156, a JSON array of three objects with the same code; the old parser failed, the new one reads the last object). Cache files were not touched, and every v1.0 model entry in `analysis_results.json`, `invalid_breakdown.json`, `validity_check.json`, `underpay_summary.json`, `guardrail.json` and `language_comparison.json` is identical to the published version (asserted in `scripts/analyze_v1_1.py`, checked again after the full rerun).
- *Concession.* The pre-registration said to stop if any answer differed. I did not stop (see DECISIONS.md). Had the new parser been applied to v1.0, allam-2-7b's "no usable code" count would be 7 instead of 8.

## 3. "Your differences between models are inside the noise."

- Among the models run on all 1,098 rulings, 8-digit accuracy is 0.3% / 5.6% / 2.4% (gpt-oss-20b / gpt-oss-120b / allam-2-7b) against 39.3% / 25.1% / 43.4% (DeepSeek V4.1 Flash / GLM 5.3 / Kimi K3). The two groups' intervals are 30 points apart, so that gap is real.
- *Concession.* Within the strong group the picture is closer. DeepSeek (36.4% to 42.2%) and Kimi (40.5% to 46.4%) have overlapping intervals; the paired McNemar test on the same 1,098 rulings gives p = 0.0869 at 6 digits and p = 0.0024 at 8 digits (exploratory). On the 200-ruling sample GPT-6 Sol (49.5%, 42.6% to 56.4%) and Kimi (37.0%, 30.6% to 43.9%) overlap too, but the paired test is p = 0.0022 at 8 digits. Rankings inside the strong group beyond "GLM below DeepSeek and Kimi, GPT-6 Sol above Kimi on the same 200" are not supported, and Nemotron's 200-ruling figures are too imprecise to rank against DeepSeek (paired p = 0.64 at 8 digits).
- 64 exploratory tests were run, none corrected for multiple comparison; p-values there are descriptive.

## 4. "The underpay finding was an artefact of weak models; it will disappear."

- It shrinks. v1.0 models: 65% to 67% of rate-changing errors underpaid. Stronger models: DeepSeek 54.0%, GLM 55.7%, Kimi 59.2%, Nemotron 60.0%, GPT-6 Sol 51.2%.
- Gate B as pre-registered (beats Baseline 2 at p < 0.05 with n of at least 30): met for GLM (n = 212, p = 0.006), Kimi (n = 311, p = 0.004) and Nemotron (n = 40, p = 0.007); not met for DeepSeek (n = 324, p = 0.17) and GPT-6 Sol (n = 41, p = 0.11).
- *Concessions.* The confidence intervals for GLM (48.9% to 62.2%) and Nemotron (44.6% to 73.7%) include 50%, so passing the baseline test does not mean a large effect. Nemotron's and GPT-6 Sol's n sit just above the threshold of 30; one more or fewer case could flip a verdict. At the 8-digit level (exploratory) only gpt-oss-20b clears Gate B. The honest summary is "a small lean toward underpaying persists in some stronger models and vanishes in others", not "stronger models underpay too".

## 5. "200 rulings is too small for the OpenRouter models."

- *Supports:* accuracy and invalid share with intervals of about plus or minus 7 points (n = 200), the pre-registered direction of the Nemotron and GPT-6 Sol 8-digit gap to the Groq models (30 to 50 points), and pairwise comparison with models on the same 200.
- *Does not support:* rankings among the strong models, month trends (28 to 50 rulings per month), the format-versus-invention split to better than plus or minus 10 points (Nemotron has 75 invalid answers and GPT-6 Sol 50), the Gate B verdicts (n = 40 and 41), or any claim about cutoff effects beyond the descriptive comparison above. Nemotron's post-cutoff primary figures use only 105 rulings and GPT-6 Sol's 167.
- Gemini 3.8 Flash is not in any table: its run has not reached 200.

## 6. "Setting reasoning to the minimum handicapped the models."

- Yes, probably. All models ran at the lowest reasoning level each accepted, to match v1.0 and keep cost down. For DeepSeek, Kimi, Nemotron and GPT-6 Sol that is "none" (0 reasoning tokens). GLM 5.3 cannot be switched off and still produced about 140 reasoning tokens per call on average. At default settings Kimi K3 and GLM 5.3 spent the whole 2,048-token budget on reasoning with an empty answer on the test ruling, so higher effort was not usable at this token limit and was not tested. The results describe low-effort, single-shot use; they are lower bounds on what these models can do, not their ceiling.

## 7. Other points a reviewer would raise

- **"Invalid" is a strict rule** (not a 10-digit code in the HTS release). Correct answers are not immune: 7 of 275 DeepSeek, 3 of 136 GLM and 8 of 312 Kimi 10-digit-correct answers were flagged invalid because the true code itself is absent from the HTS data (5 such true codes, documented in v1.0). A validity check also flags many answers that are right at 8 digits, so it is a review trigger, not a classifier.
- **"Format" is not "right".** Of the answers whose first 8 digits are a real tariff line but whose suffix is wrong or missing, only 42% (DeepSeek), 43% (GLM), 52% (Kimi), 34% (Nemotron) and 53% (GPT-6 Sol) have the true code's first 8 digits. A slip of the suffix on the right line is about 17% to 38% of invalid answers for the strong models, against 0.3% to 5% for gpt-oss and allam.
- **Stale training data is not zero for the strong models.** 58 of DeepSeek's invalid answers, 79 of Kimi's and 21 of GPT-6 Sol's are 10-digit codes that existed in a 2022 to 2025 HTS release but not in the 2026 schedule (v1.0 had 1). Retrying or a validity check cannot fix a model whose suffix table is a year old.
- **GPT-6 Sol was paid** ($0.20 for the 200 rulings, hard cap $2) and was run because the user asked; everything else is free-tier or free-credit.
- **Closed frontier models were not tested.** Nothing here says how Claude, Gemini or GPT variants not listed would score. **[Corrected in v1.2: GPT-6 Sol and three Claude models (Haiku, Sonnet, Opus 5.5) are now in the tables; Gemini is not.]** GPT-6 Sol is an OpenAI model, but it is one model on one 200-ruling sample.
- **Inkling** was the top-ranked free OpenRouter model but refused API access (HTTP 403), so Nemotron 3 Ultra, the second largest, was used instead.
