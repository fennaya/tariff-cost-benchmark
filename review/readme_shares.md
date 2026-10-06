# Derived shares behind the README framing (from analysis_results.json)

| Model | n answers | n wrong | invalid / all answers | invalid / wrong | wrong with usable rate (n) | usable / wrong | rate-changing (n) | underpay share |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 1098 | 1080/1098 = 98.4% | 1080/1098 = 98.4% | 101 | 101/1098 = 9.2% | 46 | 31/46 = 67.4% |
| openai/gpt-oss-120b | 1098 | 1092 | 1061/1098 = 96.6% | 1061/1092 = 97.2% | 93 | 93/1092 = 8.5% | 49 | 32/49 = 65.3% |
| allam-2-7b | 1098 | 1079 | 957/1098 = 87.2% | 957/1079 = 88.7% | 147 | 147/1079 = 13.6% | 116 | 76/116 = 65.5% |

## Overlap: usable-rate wrong answers that are also tagged INVALID_CODE

Only 10-digit answers get a rate (analysis.rate_pct_for). A 10-digit answer that is not in the HTS is tagged invalid but can still resolve to a rate through its 8-, 6- or 4-digit prefix, so the two groups overlap.

| Model | wrong with usable rate | of which tagged invalid | of which valid 10-digit code |
|---|---|---|---|
| openai/gpt-oss-20b | 101 | 86 | 15 |
| openai/gpt-oss-120b | 93 | 62 | 31 |
| allam-2-7b | 147 | 34 | 113 |
