# Format slip or invented code? (scripts/analyze_format_vs_invention.py)

FORMAT = (a) unparseable or truncated, (b) first 8 digits right but suffix missing, (c) first 8 right but wrong suffix. INVENTED = (d) real 6-digit subheading but no tariff line with the answer's first 8 digits, (e) no such 6-digit subheading. The one v1.0 'outdated' answer is in (c), FORMAT. Shares carry Wilson 95% CIs. Models on the 200-ruling sample show n = 200.

## Counts and shares of ALL answers

| Model | n | invalid | FORMAT (a+b+c) | INVENTED (d+e) | (a) | (b) 8 digits | (b) 9 digits | (c) | (d) | (e) |
|---|---|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 1080 (98.4%; 97.4% to 99.0%) | 146 (13.3%; 11.4% to 15.4%) | 934 (85.1%; 82.8% to 87.0%) | 0 (0.0%; 0.0% to 0.3%) | 55 (5.0%; 3.9% to 6.5%) | 0 (0.0%; 0.0% to 0.3%) | 91 (8.3%; 6.8% to 10.1%) | 422 (38.4%; 35.6% to 41.3%) | 512 (46.6%; 43.7% to 49.6%) |
| openai/gpt-oss-120b | 1098 | 1061 (96.6%; 95.4% to 97.5%) | 245 (22.3%; 19.9% to 24.9%) | 816 (74.3%; 71.7% to 76.8%) | 1 (0.1%; 0.0% to 0.5%) | 180 (16.4%; 14.3% to 18.7%) | 0 (0.0%; 0.0% to 0.3%) | 64 (5.8%; 4.6% to 7.4%) | 595 (54.2%; 51.2% to 57.1%) | 221 (20.1%; 17.9% to 22.6%) |
| allam-2-7b | 1098 | 957 (87.2%; 85.0% to 89.0%) | 72 (6.6%; 5.2% to 8.2%) | 885 (80.6%; 78.2% to 82.8%) | 8 (0.7%; 0.4% to 1.4%) | 21 (1.9%; 1.3% to 2.9%) | 0 (0.0%; 0.0% to 0.3%) | 43 (3.9%; 2.9% to 5.2%) | 359 (32.7%; 30.0% to 35.5%) | 526 (47.9%; 45.0% to 50.9%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 354 (32.2%; 29.5% to 35.1%) | 206 (18.8%; 16.6% to 21.2%) | 148 (13.5%; 11.6% to 15.6%) | 1 (0.1%; 0.0% to 0.5%) | 0 (0.0%; 0.0% to 0.3%) | 0 (0.0%; 0.0% to 0.3%) | 205 (18.7%; 16.5% to 21.1%) | 115 (10.5%; 8.8% to 12.4%) | 33 (3.0%; 2.1% to 4.2%) |
| zai-org/GLM-5.3 | 1098 | 742 (67.6%; 64.8% to 70.3%) | 312 (28.4%; 25.8% to 31.2%) | 430 (39.2%; 36.3% to 42.1%) | 27 (2.5%; 1.7% to 3.6%) | 10 (0.9%; 0.5% to 1.7%) | 0 (0.0%; 0.0% to 0.3%) | 275 (25.0%; 22.6% to 27.7%) | 339 (30.9%; 28.2% to 33.7%) | 91 (8.3%; 6.8% to 10.1%) |
| moonshotai/Kimi-K3 | 1098 | 278 (25.3%; 22.8% to 28.0%) | 188 (17.1%; 15.0% to 19.5%) | 90 (8.2%; 6.7% to 10.0%) | 0 (0.0%; 0.0% to 0.3%) | 3 (0.3%; 0.1% to 0.8%) | 0 (0.0%; 0.0% to 0.3%) | 185 (16.8%; 14.8% to 19.2%) | 71 (6.5%; 5.2% to 8.1%) | 19 (1.7%; 1.1% to 2.7%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 75 (37.5%; 31.1% to 44.4%) | 50 (25.0%; 19.5% to 31.4%) | 25 (12.5%; 8.6% to 17.8%) | 0 (0.0%; 0.0% to 1.9%) | 2 (1.0%; 0.3% to 3.6%) | 0 (0.0%; 0.0% to 1.9%) | 48 (24.0%; 18.6% to 30.4%) | 17 (8.5%; 5.4% to 13.2%) | 8 (4.0%; 2.0% to 7.7%) |
| openai/gpt-6-sol | 200 | 50 (25.0%; 19.5% to 31.4%) | 37 (18.5%; 13.7% to 24.5%) | 13 (6.5%; 3.8% to 10.8%) | 1 (0.5%; 0.1% to 2.8%) | 0 (0.0%; 0.0% to 1.9%) | 0 (0.0%; 0.0% to 1.9%) | 36 (18.0%; 13.3% to 23.9%) | 7 (3.5%; 1.7% to 7.0%) | 6 (3.0%; 1.4% to 6.4%) |

## Shares of INVALID answers

| Model | invalid n | FORMAT | INVENTED | (a) | (b) 8 digits | (b) 9 digits | (c) | (d) | (e) | (a) with a recoverable code in the text |
|---|---|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1080 | 146 (13.5%; 11.6% to 15.7%) | 934 (86.5%; 84.3% to 88.4%) | 0 (0.0%; 0.0% to 0.4%) | 55 (5.1%; 3.9% to 6.6%) | 0 (0.0%; 0.0% to 0.4%) | 91 (8.4%; 6.9% to 10.2%) | 422 (39.1%; 36.2% to 42.0%) | 512 (47.4%; 44.4% to 50.4%) | 0 of 0 |
| openai/gpt-oss-120b | 1061 | 245 (23.1%; 20.7% to 25.7%) | 816 (76.9%; 74.3% to 79.3%) | 1 (0.1%; 0.0% to 0.5%) | 180 (17.0%; 14.8% to 19.3%) | 0 (0.0%; 0.0% to 0.4%) | 64 (6.0%; 4.8% to 7.6%) | 595 (56.1%; 53.1% to 59.0%) | 221 (20.8%; 18.5% to 23.4%) | 1 of 1 |
| allam-2-7b | 957 | 72 (7.5%; 6.0% to 9.4%) | 885 (92.5%; 90.6% to 94.0%) | 8 (0.8%; 0.4% to 1.6%) | 21 (2.2%; 1.4% to 3.3%) | 0 (0.0%; 0.0% to 0.4%) | 43 (4.5%; 3.4% to 6.0%) | 359 (37.5%; 34.5% to 40.6%) | 526 (55.0%; 51.8% to 58.1%) | 8 of 8 |
| deepseek-ai/DeepSeek-V4.1-Flash | 354 | 206 (58.2%; 53.0% to 63.2%) | 148 (41.8%; 36.8% to 47.0%) | 1 (0.3%; 0.0% to 1.6%) | 0 (0.0%; 0.0% to 1.1%) | 0 (0.0%; 0.0% to 1.1%) | 205 (57.9%; 52.7% to 62.9%) | 115 (32.5%; 27.8% to 37.5%) | 33 (9.3%; 6.7% to 12.8%) | 0 of 1 |
| zai-org/GLM-5.3 | 742 | 312 (42.0%; 38.5% to 45.6%) | 430 (58.0%; 54.4% to 61.5%) | 27 (3.6%; 2.5% to 5.2%) | 10 (1.3%; 0.7% to 2.5%) | 0 (0.0%; 0.0% to 0.5%) | 275 (37.1%; 33.7% to 40.6%) | 339 (45.7%; 42.1% to 49.3%) | 91 (12.3%; 10.1% to 14.8%) | 24 of 27 |
| moonshotai/Kimi-K3 | 278 | 188 (67.6%; 61.9% to 72.9%) | 90 (32.4%; 27.1% to 38.1%) | 0 (0.0%; 0.0% to 1.4%) | 3 (1.1%; 0.4% to 3.1%) | 0 (0.0%; 0.0% to 1.4%) | 185 (66.5%; 60.8% to 71.8%) | 71 (25.5%; 20.8% to 31.0%) | 19 (6.8%; 4.4% to 10.4%) | 0 of 0 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 75 | 50 (66.7%; 55.4% to 76.3%) | 25 (33.3%; 23.7% to 44.6%) | 0 (0.0%; 0.0% to 4.9%) | 2 (2.7%; 0.7% to 9.2%) | 0 (0.0%; 0.0% to 4.9%) | 48 (64.0%; 52.7% to 73.9%) | 17 (22.7%; 14.7% to 33.3%) | 8 (10.7%; 5.5% to 19.7%) | 0 of 0 |
| openai/gpt-6-sol | 50 | 37 (74.0%; 60.4% to 84.1%) | 13 (26.0%; 15.9% to 39.6%) | 1 (2.0%; 0.4% to 10.5%) | 0 (0.0%; 0.0% to 7.1%) | 0 (0.0%; 0.0% to 7.1%) | 36 (72.0%; 58.3% to 82.5%) | 7 (14.0%; 7.0% to 26.2%) | 6 (12.0%; 5.6% to 23.8%) | 1 of 1 |

## Are the FORMAT answers right at 8 digits?

Groups (b) and (c) mean the answer's first 8 digits are a real tariff line. This counts how many of them equal the TRUE code's first 8 digits, i.e. the model had the duty-relevant classification right and only the suffix is off. The rest name a real tariff line that is not the right one.

| Model | answers in (b)+(c) | first 8 digits equal the true code's | share of (b)+(c) | share of ALL invalid answers |
|---|---|---|---|---|
| openai/gpt-oss-20b | 146 | 3 | 3 (2.1%; 0.7% to 5.9%) | 3 (0.3%; 0.1% to 0.8%) |
| openai/gpt-oss-120b | 244 | 55 | 55 (22.5%; 17.7% to 28.2%) | 55 (5.2%; 4.0% to 6.7%) |
| allam-2-7b | 64 | 7 | 7 (10.9%; 5.4% to 20.9%) | 7 (0.7%; 0.4% to 1.5%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 205 | 86 | 86 (42.0%; 35.4% to 48.8%) | 86 (24.3%; 20.1% to 29.0%) |
| zai-org/GLM-5.3 | 285 | 123 | 123 (43.2%; 37.5% to 49.0%) | 123 (16.6%; 14.1% to 19.4%) |
| moonshotai/Kimi-K3 | 188 | 97 | 97 (51.6%; 44.5% to 58.6%) | 97 (34.9%; 29.5% to 40.7%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 50 | 17 | 17 (34.0%; 22.4% to 47.8%) | 17 (22.7%; 14.7% to 33.3%) |
| openai/gpt-6-sol | 36 | 19 | 19 (52.8%; 37.0% to 68.0%) | 19 (38.0%; 25.9% to 51.8%) |

For the v1.0 models the five groups sum to the published invalid counts (checked in the script).
