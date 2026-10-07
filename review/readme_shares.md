# Derived shares behind the README framing (from analysis_results.json)

| Model | n answers | n wrong | invalid / all answers | invalid / wrong | wrong with usable rate (n) | usable / wrong | rate-changing (n) | underpay share |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 1098 | 1080/1098 = 98.4% | 1080/1098 = 98.4% | 101 | 101/1098 = 9.2% | 46 | 31/46 = 67.4% |
| openai/gpt-oss-120b | 1098 | 1092 | 1061/1098 = 96.6% | 1061/1092 = 97.2% | 93 | 93/1092 = 8.5% | 49 | 32/49 = 65.3% |
| allam-2-7b | 1098 | 1079 | 957/1098 = 87.2% | 957/1079 = 88.7% | 147 | 147/1079 = 13.6% | 116 | 76/116 = 65.5% |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 823 | 354/1098 = 32.2% | 354/823 = 43.0% | 657 | 657/823 = 79.8% | 324 | 175/324 = 54.0% |
| zai-org/GLM-5.3 | 1098 | 962 | 742/1098 = 67.6% | 742/962 = 77.1% | 483 | 483/962 = 50.2% | 212 | 118/212 = 55.7% |
| moonshotai/Kimi-K3 | 1098 | 786 | 278/1098 = 25.3% | 278/786 = 35.4% | 673 | 673/786 = 85.6% | 311 | 184/311 = 59.2% |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 172 | 75/200 = 37.5% | 75/172 = 43.6% | 138 | 138/172 = 80.2% | 66 | 34/66 = 51.5% |
| openai/gpt-6-sol | 200 | 135 | 50/200 = 25.0% | 50/135 = 37.0% | 117 | 117/135 = 86.7% | 49 | 26/49 = 53.1% |

## Overlap: usable-rate wrong answers that are also tagged INVALID_CODE

Only 10-digit answers get a rate (analysis.rate_pct_for). A 10-digit answer that is not in the HTS is tagged invalid but can still resolve to a rate through its 8-, 6- or 4-digit prefix, so the two groups overlap.

| Model | wrong with usable rate | of which tagged invalid | of which valid 10-digit code |
|---|---|---|---|
| openai/gpt-oss-20b | 101 | 86 | 15 |
| openai/gpt-oss-120b | 93 | 62 | 31 |
| allam-2-7b | 147 | 34 | 113 |
| deepseek-ai/DeepSeek-V4.1-Flash | 657 | 193 | 464 |
| zai-org/GLM-5.3 | 483 | 269 | 214 |
| moonshotai/Kimi-K3 | 673 | 176 | 497 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 138 | 46 | 92 |
| openai/gpt-6-sol | 117 | 34 | 83 |
