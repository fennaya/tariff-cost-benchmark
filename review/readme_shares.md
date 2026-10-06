# Derived shares behind the README framing (from analysis_results.json)

| Model | n answers | n wrong | invalid / all answers | invalid / wrong | wrong with usable rate (n) | usable / wrong | rate-changing (n) | underpay share |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 1098 | 1080/1098 = 98.4% | 1080/1098 = 98.4% | 101 | 101/1098 = 9.2% | 46 | 31/46 = 67.4% |
| openai/gpt-oss-120b | 1098 | 1092 | 1061/1098 = 96.6% | 1061/1092 = 97.2% | 85 | 85/1092 = 7.8% | 47 | 30/47 = 63.8% |
| allam-2-7b | 1098 | 1079 | 957/1098 = 87.2% | 957/1079 = 88.7% | 145 | 145/1079 = 13.4% | 115 | 75/115 = 65.2% |

## Overlap: usable-rate wrong answers that are also tagged INVALID_CODE

A predicted 8-digit code is tagged invalid (not a 10-digit code in the HTS) but still resolves to a rate by prefix walk, so the two groups overlap.

| Model | wrong with usable rate | of which tagged invalid | of which valid 10-digit code |
|---|---|---|---|
| openai/gpt-oss-20b | 101 | 86 | 15 |
| openai/gpt-oss-120b | 85 | 54 | 31 |
| allam-2-7b | 145 | 33 | 112 |
