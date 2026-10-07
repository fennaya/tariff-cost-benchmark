# Invalid-code breakdown, outdated check, and dollar figure (scripts/analyze_invalid_codes.py)

All 1,098 usable rulings per model. Outdated check uses 20,876 distinct 10-digit codes from the 2022-2025 HTS releases.

## Share of ALL answers

| Model | n | correct | wrong, valid code | invalid: suffix only | invalid: first 6 ok, first 8 not | invalid: fabricated | invalid: outdated | invalid: no usable code |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 0 (0.0%) | 18 (1.6%) | 146 (13.3%) | 422 (38.4%) | 512 (46.6%) | 0 (0.0%) | 0 (0.0%) |
| openai/gpt-oss-120b | 1098 | 6 (0.5%) | 31 (2.8%) | 243 (22.1%) | 595 (54.2%) | 221 (20.1%) | 1 (0.1%) | 1 (0.1%) |
| allam-2-7b | 1098 | 19 (1.7%) | 122 (11.1%) | 64 (5.8%) | 359 (32.7%) | 526 (47.9%) | 0 (0.0%) | 8 (0.7%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 275 (25.0%) | 476 (43.4%) | 142 (12.9%) | 113 (10.3%) | 33 (3.0%) | 58 (5.3%) | 1 (0.1%) |
| zai-org/GLM-5.3 | 1098 | 136 (12.4%) | 223 (20.3%) | 255 (23.2%) | 339 (30.9%) | 91 (8.3%) | 27 (2.5%) | 27 (2.5%) |
| moonshotai/Kimi-K3 | 1098 | 312 (28.4%) | 516 (47.0%) | 102 (9.3%) | 70 (6.4%) | 19 (1.7%) | 79 (7.2%) | 0 (0.0%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 28 (14.0%) | 98 (49.0%) | 39 (19.5%) | 17 (8.5%) | 8 (4.0%) | 10 (5.0%) | 0 (0.0%) |
| openai/gpt-6-sol | 200 | 65 (32.5%) | 86 (43.0%) | 14 (7.0%) | 7 (3.5%) | 6 (3.0%) | 21 (10.5%) | 1 (0.5%) |

## Share of INVALID answers

| Model | n invalid | suffix only | first 6 ok, first 8 not | fabricated | outdated | no usable code |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1080 | 146 (13.5%) | 422 (39.1%) | 512 (47.4%) | 0 (0.0%) | 0 (0.0%) |
| openai/gpt-oss-120b | 1061 | 243 (22.9%) | 595 (56.1%) | 221 (20.8%) | 1 (0.1%) | 1 (0.1%) |
| allam-2-7b | 957 | 64 (6.7%) | 359 (37.5%) | 526 (55.0%) | 0 (0.0%) | 8 (0.8%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 347 | 142 (40.9%) | 113 (32.6%) | 33 (9.5%) | 58 (16.7%) | 1 (0.3%) |
| zai-org/GLM-5.3 | 739 | 255 (34.5%) | 339 (45.9%) | 91 (12.3%) | 27 (3.7%) | 27 (3.7%) |
| moonshotai/Kimi-K3 | 270 | 102 (37.8%) | 70 (25.9%) | 19 (7.0%) | 79 (29.3%) | 0 (0.0%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 74 | 39 (52.7%) | 17 (23.0%) | 8 (10.8%) | 10 (13.5%) | 0 (0.0%) |
| openai/gpt-6-sol | 49 | 14 (28.6%) | 7 (14.3%) | 6 (12.2%) | 21 (42.9%) | 1 (2.0%) |

## Suffix-only invalid answers: left the suffix off vs wrote a wrong suffix

| Model | suffix_only n | exactly 8 digits (no suffix) | other (wrong suffix etc.) |
|---|---|---|---|
| openai/gpt-oss-20b | 146 | 55 | 91 |
| openai/gpt-oss-120b | 243 | 180 | 63 |
| allam-2-7b | 64 | 21 | 43 |
| deepseek-ai/DeepSeek-V4.1-Flash | 142 | 0 | 142 |
| zai-org/GLM-5.3 | 255 | 10 | 245 |
| moonshotai/Kimi-K3 | 102 | 3 | 99 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 39 | 2 | 37 |
| openai/gpt-6-sol | 14 | 0 | 14 |

## Non-exclusive crosstab: a/b/c class by outdated flag (invalid answers with >=6 digits)

| Model | key | n |
|---|---|---|
| openai/gpt-oss-20b | fabricated|outdated=False | 512 |
| openai/gpt-oss-20b | six_eight|outdated=False | 422 |
| openai/gpt-oss-20b | suffix_only|outdated=False | 146 |
| openai/gpt-oss-120b | fabricated|outdated=False | 221 |
| openai/gpt-oss-120b | six_eight|outdated=False | 595 |
| openai/gpt-oss-120b | suffix_only|outdated=False | 243 |
| openai/gpt-oss-120b | suffix_only|outdated=True | 1 |
| allam-2-7b | fabricated|outdated=False | 526 |
| allam-2-7b | six_eight|outdated=False | 359 |
| allam-2-7b | suffix_only|outdated=False | 64 |
| deepseek-ai/DeepSeek-V4.1-Flash | fabricated|outdated=False | 33 |
| deepseek-ai/DeepSeek-V4.1-Flash | six_eight|outdated=False | 113 |
| deepseek-ai/DeepSeek-V4.1-Flash | six_eight|outdated=True | 1 |
| deepseek-ai/DeepSeek-V4.1-Flash | suffix_only|outdated=False | 142 |
| deepseek-ai/DeepSeek-V4.1-Flash | suffix_only|outdated=True | 57 |
| zai-org/GLM-5.3 | fabricated|outdated=False | 91 |
| zai-org/GLM-5.3 | six_eight|outdated=False | 339 |
| zai-org/GLM-5.3 | suffix_only|outdated=False | 255 |
| zai-org/GLM-5.3 | suffix_only|outdated=True | 27 |
| moonshotai/Kimi-K3 | fabricated|outdated=False | 19 |
| moonshotai/Kimi-K3 | six_eight|outdated=False | 70 |
| moonshotai/Kimi-K3 | six_eight|outdated=True | 1 |
| moonshotai/Kimi-K3 | suffix_only|outdated=False | 102 |
| moonshotai/Kimi-K3 | suffix_only|outdated=True | 78 |
| nvidia/nemotron-3-ultra-550b-a55b:free | fabricated|outdated=False | 8 |
| nvidia/nemotron-3-ultra-550b-a55b:free | six_eight|outdated=False | 17 |
| nvidia/nemotron-3-ultra-550b-a55b:free | suffix_only|outdated=False | 39 |
| nvidia/nemotron-3-ultra-550b-a55b:free | suffix_only|outdated=True | 10 |
| openai/gpt-6-sol | fabricated|outdated=False | 6 |
| openai/gpt-6-sol | six_eight|outdated=False | 7 |
| openai/gpt-6-sol | suffix_only|outdated=False | 14 |
| openai/gpt-6-sol | suffix_only|outdated=True | 21 |

## Duty at stake per $100,000 declared, valid wrong codes (both rates resolve)

| Model | valid wrong codes | with usable rates (n) | median | IQR | zero-rate-difference |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 18 | 15 | $1,500 | $200 to $3,500 | 4 |
| openai/gpt-oss-120b | 31 | 31 | $0 | $0 to $1,350 | 16 |
| allam-2-7b | 122 | 113 | $4,000 | $1,400 to $7,000 | 17 |
| deepseek-ai/DeepSeek-V4.1-Flash | 476 | 464 | $500 | $0 to $3,000 | 217 |
| zai-org/GLM-5.3 | 223 | 214 | $1,500 | $0 to $3,700 | 88 |
| moonshotai/Kimi-K3 | 516 | 497 | $100 | $0 to $2,900 | 245 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 98 | 92 | $1,250 | $0 to $5,000 | 43 |
| openai/gpt-6-sol | 86 | 83 | $0 | $0 to $3,800 | 43 |
