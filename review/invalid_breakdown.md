# Invalid-code breakdown, outdated check, and dollar figure (scripts/analyze_invalid_codes.py)

All 1,098 usable rulings per model. Outdated check uses 20,876 distinct 10-digit codes from the 2022-2025 HTS releases.

## Share of ALL answers

| Model | n | correct | wrong, valid code | invalid: suffix only | invalid: first 6 ok, first 8 not | invalid: fabricated | invalid: outdated | invalid: no usable code |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 0 (0.0%) | 18 (1.6%) | 146 (13.3%) | 422 (38.4%) | 512 (46.6%) | 0 (0.0%) | 0 (0.0%) |
| openai/gpt-oss-120b | 1098 | 6 (0.5%) | 31 (2.8%) | 243 (22.1%) | 595 (54.2%) | 221 (20.1%) | 1 (0.1%) | 1 (0.1%) |
| allam-2-7b | 1098 | 19 (1.7%) | 122 (11.1%) | 64 (5.8%) | 359 (32.7%) | 526 (47.9%) | 0 (0.0%) | 8 (0.7%) |

## Share of INVALID answers

| Model | n invalid | suffix only | first 6 ok, first 8 not | fabricated | outdated | no usable code |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1080 | 146 (13.5%) | 422 (39.1%) | 512 (47.4%) | 0 (0.0%) | 0 (0.0%) |
| openai/gpt-oss-120b | 1061 | 243 (22.9%) | 595 (56.1%) | 221 (20.8%) | 1 (0.1%) | 1 (0.1%) |
| allam-2-7b | 957 | 64 (6.7%) | 359 (37.5%) | 526 (55.0%) | 0 (0.0%) | 8 (0.8%) |

## Suffix-only invalid answers: left the suffix off vs wrote a wrong suffix

| Model | suffix_only n | exactly 8 digits (no suffix) | other (wrong suffix etc.) |
|---|---|---|---|
| openai/gpt-oss-20b | 146 | 55 | 91 |
| openai/gpt-oss-120b | 243 | 180 | 63 |
| allam-2-7b | 64 | 21 | 43 |

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

## Duty at stake per $100,000 declared, valid wrong codes (both rates resolve)

| Model | valid wrong codes | with usable rates (n) | median | IQR | zero-rate-difference |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 18 | 15 | $1,500 | $200 to $3,500 | 4 |
| openai/gpt-oss-120b | 31 | 31 | $0 | $0 to $1,350 | 16 |
| allam-2-7b | 122 | 113 | $4,000 | $1,400 to $7,000 | 17 |
