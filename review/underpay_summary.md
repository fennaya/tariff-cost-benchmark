# Underpay result with sample sizes (scripts/analyze_underpay_summary.py)

Rule: the word "significant" is used only for models with n >= 30 rate-changing errors.

| Model | n rate-changing errors | underpaid | underpay share (Wilson 95% CI) | binomial p vs 50% | p vs Baseline 1 (heading) | p vs Baseline 2 (matched depth) | wording |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 46 | 31 | 67.4% (53.0% to 79.1%) | 0.0259 | < 0.001 | < 0.001 | significantly more than the matched-depth baseline |
| openai/gpt-oss-120b | 49 | 32 | 65.3% (51.3% to 77.1%) | 0.0444 | < 0.001 | < 0.001 | significantly more than the matched-depth baseline |
| allam-2-7b | 116 | 76 | 65.5% (56.5% to 73.5%) | 0.0011 | < 0.001 | < 0.001 | significantly more than the matched-depth baseline |
| deepseek-ai/DeepSeek-V4.1-Flash | 324 | 175 | 54.0% (48.6% to 59.4%) | 0.1648 | 0.9930 | 0.1748 | not significantly different from the matched-depth baseline |
| zai-org/GLM-5.3 | 212 | 118 | 55.7% (48.9% to 62.2%) | 0.1140 | 0.8322 | 0.0060 | significantly more than the matched-depth baseline |
| moonshotai/Kimi-K3 | 311 | 184 | 59.2% (53.6% to 64.5%) | 0.0015 | 0.4496 | 0.0040 | significantly more than the matched-depth baseline |
| nvidia/nemotron-3-ultra-550b-a55b:free | 66 | 34 | 51.5% (39.7% to 63.2%) | 0.9022 | 0.6803 | 0.0959 | not significantly different from the matched-depth baseline |
| openai/gpt-6-sol | 49 | 26 | 53.1% (39.4% to 66.3%) | 0.7754 | 0.6883 | 0.1279 | not significantly different from the matched-depth baseline |
