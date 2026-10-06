# What a validity check would flag (scripts/analyze_validity_check.py)

| Model | wrong answers | wrong and flagged (detection rate, Wilson 95% CI) | wrong but not flagged (valid wrong code) | correct answers (10-digit) | correct and flagged (false-flag rate) | 8-digit-correct answers | 8-digit-correct and flagged |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 1080 (98.4%; 97.4% to 99.0%) | 18 | 0 | n/a (0 correct) | 3 | 3 of 3 (100.0%) |
| openai/gpt-oss-120b | 1092 | 1061 (97.2%; 96.0% to 98.0%) | 31 | 6 | 0 of 6 (0.0%) | 61 | 55 of 61 (90.2%) |
| allam-2-7b | 1079 | 957 (88.7%; 86.7% to 90.4%) | 122 | 19 | 0 of 19 (0.0%) | 26 | 7 of 26 (26.9%) |
