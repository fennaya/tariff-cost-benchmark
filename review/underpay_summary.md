# Underpay result with sample sizes (scripts/analyze_underpay_summary.py)

Rule: the word "significant" is used only for models with n >= 30 rate-changing errors.

| Model | n rate-changing errors | underpaid | underpay share (Wilson 95% CI) | binomial p vs 50% | p vs Baseline 1 (heading) | p vs Baseline 2 (matched depth) | wording |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 46 | 31 | 67.4% (53.0% to 79.1%) | 0.0259 | < 0.001 | < 0.001 | significantly more than the matched-depth baseline |
| openai/gpt-oss-120b | 49 | 32 | 65.3% (51.3% to 77.1%) | 0.0444 | < 0.001 | < 0.001 | significantly more than the matched-depth baseline |
| allam-2-7b | 116 | 76 | 65.5% (56.5% to 73.5%) | 0.0011 | < 0.001 | < 0.001 | significantly more than the matched-depth baseline |
