# What a validity check would flag (scripts/analyze_validity_check.py)

| Model | wrong answers | wrong and flagged (detection rate, Wilson 95% CI) | wrong but not flagged (valid wrong code) | correct answers (10-digit) | correct and flagged (false-flag rate) | 8-digit-correct answers | 8-digit-correct and flagged |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 1080 (98.4%; 97.4% to 99.0%) | 18 | 0 | n/a (0 correct) | 3 | 3 of 3 (100.0%) |
| openai/gpt-oss-120b | 1092 | 1061 (97.2%; 96.0% to 98.0%) | 31 | 6 | 0 of 6 (0.0%) | 61 | 55 of 61 (90.2%) |
| allam-2-7b | 1079 | 957 (88.7%; 86.7% to 90.4%) | 122 | 19 | 0 of 19 (0.0%) | 26 | 7 of 26 (26.9%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 823 | 347 (42.2%; 38.8% to 45.6%) | 476 | 275 | 7 of 275 (2.5%) | 431 | 87 of 431 (20.2%) |
| zai-org/GLM-5.3 | 962 | 739 (76.8%; 74.0% to 79.4%) | 223 | 136 | 3 of 136 (2.2%) | 276 | 123 of 276 (44.6%) |
| moonshotai/Kimi-K3 | 786 | 270 (34.4%; 31.1% to 37.7%) | 516 | 312 | 8 of 312 (2.6%) | 477 | 97 of 477 (20.3%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 172 | 74 (43.0%; 35.9% to 50.5%) | 98 | 28 | 1 of 28 (3.6%) | 58 | 17 of 58 (29.3%) |
| openai/gpt-6-sol | 135 | 49 (36.3%; 28.7% to 44.7%) | 86 | 65 | 1 of 65 (1.5%) | 99 | 19 of 99 (19.2%) |
