# v1.1 results (scripts/analyze_v1_1.py)

Pre-registration: PREREG_v1.1.md. Primary = rulings dated after the model's stated training cutoff; if the cutoff is unknown or after 2026-08-14 the model is labelled "contamination not ruled out" and the primary rows are all its rows. Models on the 200-ruling sample always show n; they are compared only with other models on the same 200 rulings. Closed frontier models were not tested. Duty figures are MFN-only lower bounds.

## Models and scope

| Model | Provider | Rulings run | Stated cutoff (source) | Contamination status | Primary rows | Reasoning setting |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | groq | 1098 | 2024-06-01 (https://platform.openai.com/docs/models/gpt-oss-20b) | cutoff 2024-06-01; every ruling is after it | 1098 | low |
| openai/gpt-oss-120b | groq | 1098 | 2024-06-01 (https://platform.openai.com/docs/models/gpt-oss-120b) | cutoff 2024-06-01; every ruling is after it | 1098 | low |
| allam-2-7b | groq | 1098 | unknown (not stated on console.groq.com or Hugging Face as of 2026-09-30; treated as latest-possibl) | contamination not ruled out (cutoff unknown) | 1098 | None |
| deepseek-ai/DeepSeek-V4.1-Flash | baseten | 1098 | unknown (official model card silent as of 2026-10-07 (https://huggingface.co/deepseek-ai/DeepSeek-V) | contamination not ruled out (cutoff unknown) | 1098 | none |
| zai-org/GLM-5.3 | baseten | 1098 | unknown (official model card silent as of 2026-10-07 (https://huggingface.co/zai-org/GLM-5.3)) | contamination not ruled out (cutoff unknown) | 1098 | thinking disabled (still emits some reasoning tokens) |
| moonshotai/Kimi-K3 | baseten | 1098 | unknown (official model card silent as of 2026-10-07 (https://huggingface.co/moonshotai/Kimi-K3)) | contamination not ruled out (cutoff unknown) | 1098 | none |
| nvidia/nemotron-3-ultra-550b-a55b:free | openrouter | 200 | 2026-05-31 (https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 (knowledge cutoff 202) | post-cutoff rulings only (after 2026-05-31) | 105 | none |
| openai/gpt-6-sol | openrouter | 200 | 2026-04-20 (https://computingforgeeks.com/gpt-6-sol-luna-released-features-benchmarks/ (third-party re) | post-cutoff rulings only (after 2026-04-20) | 167 | none |

## Primary results (post-cutoff rows; see the status column above)

| Model | n | 6-digit | 8-digit (headline) | 10-digit | Invalid share | FORMAT share of all | INVENTED share of all |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 3.0% (2.1% to 4.2%) | 0.3% (0.1% to 0.8%) | 0.0% (0.0% to 0.3%) | 98.4% (97.4% to 99.0%) | 13.3% (11.4% to 15.4%) | 85.1% (82.8% to 87.0%) |
| openai/gpt-oss-120b | 1098 | 21.1% (18.8% to 23.6%) | 5.6% (4.3% to 7.1%) | 0.5% (0.3% to 1.2%) | 96.6% (95.4% to 97.5%) | 22.3% (19.9% to 24.9%) | 74.3% (71.7% to 76.8%) |
| allam-2-7b | 1098 | 4.4% (3.3% to 5.7%) | 2.4% (1.6% to 3.4%) | 1.7% (1.1% to 2.7%) | 87.2% (85.0% to 89.0%) | 6.6% (5.2% to 8.2%) | 80.6% (78.2% to 82.8%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 52.8% (49.9% to 55.8%) | 39.3% (36.4% to 42.2%) | 25.0% (22.6% to 27.7%) | 32.2% (29.5% to 35.1%) | 18.8% (16.6% to 21.2%) | 13.5% (11.6% to 15.6%) |
| zai-org/GLM-5.3 | 1098 | 45.3% (42.3% to 48.2%) | 25.1% (22.7% to 27.8%) | 12.4% (10.6% to 14.5%) | 67.6% (64.8% to 70.3%) | 28.4% (25.8% to 31.2%) | 39.2% (36.3% to 42.1%) |
| moonshotai/Kimi-K3 | 1098 | 55.3% (52.3% to 58.2%) | 43.4% (40.5% to 46.4%) | 28.4% (25.8% to 31.2%) | 25.3% (22.8% to 28.0%) | 17.1% (15.0% to 19.5%) | 8.2% (6.7% to 10.0%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 105 | 36.2% (27.6% to 45.7%) | 23.8% (16.7% to 32.8%) | 14.3% (8.9% to 22.2%) | 33.3% (25.0% to 42.8%) | 19.0% (12.7% to 27.6%) | 14.3% (8.9% to 22.2%) |
| openai/gpt-6-sol | 167 | 61.7% (54.1% to 68.7%) | 49.7% (42.2% to 57.2%) | 31.7% (25.2% to 39.1%) | 25.7% (19.7% to 32.9%) | 18.6% (13.4% to 25.1%) | 7.2% (4.2% to 12.1%) |

## Secondary: full sample (all rulings run, regardless of cutoff)

| Model | n | 6-digit | 8-digit | 10-digit | Invalid share |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 3.0% (2.1% to 4.2%) | 0.3% (0.1% to 0.8%) | 0.0% (0.0% to 0.3%) | 98.4% (97.4% to 99.0%) |
| openai/gpt-oss-120b | 1098 | 21.1% (18.8% to 23.6%) | 5.6% (4.3% to 7.1%) | 0.5% (0.3% to 1.2%) | 96.6% (95.4% to 97.5%) |
| allam-2-7b | 1098 | 4.4% (3.3% to 5.7%) | 2.4% (1.6% to 3.4%) | 1.7% (1.1% to 2.7%) | 87.2% (85.0% to 89.0%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 52.8% (49.9% to 55.8%) | 39.3% (36.4% to 42.2%) | 25.0% (22.6% to 27.7%) | 32.2% (29.5% to 35.1%) |
| zai-org/GLM-5.3 | 1098 | 45.3% (42.3% to 48.2%) | 25.1% (22.7% to 27.8%) | 12.4% (10.6% to 14.5%) | 67.6% (64.8% to 70.3%) |
| moonshotai/Kimi-K3 | 1098 | 55.3% (52.3% to 58.2%) | 43.4% (40.5% to 46.4%) | 28.4% (25.8% to 31.2%) | 25.3% (22.8% to 28.0%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 39.5% (33.0% to 46.4%) | 29.0% (23.2% to 35.6%) | 14.0% (9.9% to 19.5%) | 37.5% (31.1% to 44.4%) |
| openai/gpt-6-sol | 200 | 61.5% (54.6% to 68.0%) | 49.5% (42.6% to 56.4%) | 32.5% (26.4% to 39.3%) | 25.0% (19.5% to 31.4%) |

## Direction of duty errors (Gate B as pre-registered), median duty at stake, validity check

| Model | rate-changing errors n | underpaid | underpay share (95% CI) | p vs Baseline 1 | p vs Baseline 2 | Gate B verdict | comparable wrong answers n | median duty per $100k (IQR) |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 46 | 31 | 67.4% (53.0% to 79.1%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 101 | $0 ($0 to $3,500) |
| openai/gpt-oss-120b | 49 | 32 | 65.3% (51.3% to 77.1%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 93 | $300 ($0 to $2,500) |
| allam-2-7b | 116 | 76 | 65.5% (56.5% to 73.5%) | < 0.001 | < 0.001 | underpays more than chance (Gate B met) | 147 | $3,400 ($350 to $6,500) |
| deepseek-ai/DeepSeek-V4.1-Flash | 324 | 175 | 54.0% (48.6% to 59.4%) | 0.9930 | 0.1748 | not distinguishable from chance (Gate B not met) | 657 | $0 ($0 to $2,900) |
| zai-org/GLM-5.3 | 212 | 118 | 55.7% (48.9% to 62.2%) | 0.8322 | 0.0060 | underpays more than chance (Gate B met) | 483 | $0 ($0 to $2,800) |
| moonshotai/Kimi-K3 | 311 | 184 | 59.2% (53.6% to 64.5%) | 0.4496 | 0.0040 | underpays more than chance (Gate B met) | 673 | $0 ($0 to $2,800) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 40 | 24 | 60.0% (44.6% to 73.7%) | 0.2987 | 0.0070 | underpays more than chance (Gate B met) | 73 | $1,300 ($0 to $4,400) |
| openai/gpt-6-sol | 41 | 21 | 51.2% (36.5% to 65.7%) | 0.8252 | 0.1139 | not distinguishable from chance (Gate B not met) | 97 | $0 ($0 to $3,600) |

### Validity check (flag any answer that is not a 10-digit code in the HTS)

| Model | wrong answers | wrong and flagged invalid | correct 10-digit answers | correct and flagged | 8-digit-correct answers | 8-digit-correct and flagged |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 98.4% (97.4% to 99.0%) | 0 | 0 of 0 | 3 | 3 of 3 |
| openai/gpt-oss-120b | 1092 | 97.2% (96.0% to 98.0%) | 6 | 0 of 6 | 61 | 55 of 61 |
| allam-2-7b | 1079 | 88.7% (86.7% to 90.4%) | 19 | 0 of 19 | 26 | 7 of 26 |
| deepseek-ai/DeepSeek-V4.1-Flash | 823 | 42.2% (38.8% to 45.6%) | 275 | 7 of 275 | 431 | 87 of 431 |
| zai-org/GLM-5.3 | 962 | 76.8% (74.0% to 79.4%) | 136 | 3 of 136 | 276 | 123 of 276 |
| moonshotai/Kimi-K3 | 786 | 34.4% (31.1% to 37.7%) | 312 | 8 of 312 | 477 | 97 of 477 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 90 | 38.9% (29.5% to 49.2%) | 15 | 0 of 15 | 25 | 3 of 25 |
| openai/gpt-6-sol | 114 | 37.7% (29.4% to 46.9%) | 53 | 0 of 53 | 83 | 16 of 83 |

## Same-200 comparison (all models restricted to the 200 rulings in data/gemini_subset.csv; all dates, secondary)

| Model | n | 6-digit | 8-digit | 10-digit | Invalid share |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 200 | 1.5% (0.5% to 4.3%) | 0.5% (0.1% to 2.8%) | 0.0% (0.0% to 1.9%) | 98.0% (95.0% to 99.2%) |
| openai/gpt-oss-120b | 200 | 18.0% (13.3% to 23.9%) | 7.5% (4.6% to 12.0%) | 0.5% (0.1% to 2.8%) | 97.5% (94.3% to 98.9%) |
| allam-2-7b | 200 | 3.5% (1.7% to 7.0%) | 2.0% (0.8% to 5.0%) | 0.5% (0.1% to 2.8%) | 89.5% (84.5% to 93.0%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 200 | 43.0% (36.3% to 49.9%) | 31.0% (25.0% to 37.7%) | 18.0% (13.3% to 23.9%) | 32.5% (26.4% to 39.3%) |
| zai-org/GLM-5.3 | 200 | 40.5% (33.9% to 47.4%) | 21.5% (16.4% to 27.7%) | 8.0% (5.0% to 12.6%) | 63.0% (56.1% to 69.4%) |
| moonshotai/Kimi-K3 | 200 | 49.0% (42.2% to 55.9%) | 37.0% (30.6% to 43.9%) | 25.0% (19.5% to 31.4%) | 26.5% (20.9% to 33.0%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 39.5% (33.0% to 46.4%) | 29.0% (23.2% to 35.6%) | 14.0% (9.9% to 19.5%) | 37.5% (31.1% to 44.4%) |
| openai/gpt-6-sol | 200 | 61.5% (54.6% to 68.0%) | 49.5% (42.6% to 56.4%) | 32.5% (26.4% to 39.3%) | 25.0% (19.5% to 31.4%) |

## Contamination check A: memorisation probe (ruling number only, no description)

Question asked: "What 10-digit HTSUS code did CBP assign in ruling <number>? Reply with JSON {"hts_code": ...}". Seed 20261007, `data/probe_ids.csv`. Exact hits clearly above zero would suggest memorisation.

| Model | probes n | exact 10-digit hits | 8-digit hits | 6-digit hits | parse failures |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 0 | not run | not run | not run | |
| openai/gpt-oss-120b | 0 | not run | not run | not run | |
| allam-2-7b | 0 | not run | not run | not run | |
| deepseek-ai/DeepSeek-V4.1-Flash | 100 | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 96 |
| zai-org/GLM-5.3 | 100 | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 95 |
| moonshotai/Kimi-K3 | 100 | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0.0% (0.0% to 3.7%) | 0 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 25 | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0 |
| openai/gpt-6-sol | 25 | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0.0% (0.0% to 13.3%) | 0 |

## Contamination check B: 8-digit accuracy by ruling month (full sample, n per month)

| Model | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 0/148 (0%) | 0/121 (0%) | 0/168 (0%) | 1/175 (1%) | 2/137 (1%) | 0/121 (0%) | 0/144 (0%) | 0/84 (0%) |
| openai/gpt-oss-120b | 8/148 (5%) | 3/121 (2%) | 13/168 (8%) | 16/175 (9%) | 5/137 (4%) | 7/121 (6%) | 6/144 (4%) | 3/84 (4%) |
| allam-2-7b | 6/148 (4%) | 7/121 (6%) | 3/168 (2%) | 3/175 (2%) | 0/137 (0%) | 3/121 (2%) | 4/144 (3%) | 0/84 (0%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 71/148 (48%) | 61/121 (50%) | 59/168 (35%) | 76/175 (43%) | 40/137 (29%) | 45/121 (37%) | 45/144 (31%) | 34/84 (40%) |
| zai-org/GLM-5.3 | 42/148 (28%) | 46/121 (38%) | 48/168 (29%) | 43/175 (25%) | 25/137 (18%) | 28/121 (23%) | 28/144 (19%) | 16/84 (19%) |
| moonshotai/Kimi-K3 | 79/148 (53%) | 63/121 (52%) | 75/168 (45%) | 83/175 (47%) | 49/137 (36%) | 39/121 (32%) | 47/144 (33%) | 42/84 (50%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 0/0 | 0/0 | 0/0 | 24/45 (53%) | 9/50 (18%) | 11/37 (30%) | 7/40 (18%) | 7/28 (25%) |
| openai/gpt-6-sol | 0/0 | 0/0 | 0/0 | 25/45 (56%) | 19/50 (38%) | 22/37 (59%) | 18/40 (45%) | 15/28 (54%) |

### Check B detail: 8-digit accuracy before vs after each model's stated cutoff (known cutoff inside the ruling window only)

Descriptive, no test. A drop right after the cutoff would be the signature of memorised rulings; a model with no drop is some evidence against it. Case mix differs by month, so this is not proof either way.

| Model | cutoff | rulings on/before cutoff | 8-digit | rulings after cutoff | 8-digit |
|---|---|---|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b:free | 2026-05-31 | 95 | 34.7% (25.9% to 44.7%) | 105 | 23.8% (16.7% to 32.8%) |
| openai/gpt-6-sol | 2026-04-20 | 33 | 48.5% (32.5% to 64.8%) | 167 | 49.7% (42.2% to 57.2%) |

## EXPLORATORY extras (cached data only; pre-registered in PREREG_v1.1.md section 7)

### 1. Paired McNemar tests at 6 and 8 digits, and heading accuracy

Exact binomial test on discordant pairs, on the rulings both models ran. b = first model right and second wrong, c = the reverse.

| Model A | Model B | shared n | level | b | c | p |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | openai/gpt-oss-120b | 1098 | 6 | 15 | 214 | < 0.0001 |
| openai/gpt-oss-20b | openai/gpt-oss-120b | 1098 | 8 | 1 | 59 | < 0.0001 |
| openai/gpt-oss-20b | allam-2-7b | 1098 | 6 | 28 | 43 | 0.0959 |
| openai/gpt-oss-20b | allam-2-7b | 1098 | 8 | 3 | 26 | < 0.0001 |
| openai/gpt-oss-20b | deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 6 | 10 | 557 | < 0.0001 |
| openai/gpt-oss-20b | deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 8 | 1 | 429 | < 0.0001 |
| openai/gpt-oss-20b | zai-org/GLM-5.3 | 1098 | 6 | 12 | 476 | < 0.0001 |
| openai/gpt-oss-20b | zai-org/GLM-5.3 | 1098 | 8 | 1 | 274 | < 0.0001 |
| openai/gpt-oss-20b | moonshotai/Kimi-K3 | 1098 | 6 | 8 | 582 | < 0.0001 |
| openai/gpt-oss-20b | moonshotai/Kimi-K3 | 1098 | 8 | 1 | 475 | < 0.0001 |
| openai/gpt-oss-20b | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 6 | 1 | 77 | < 0.0001 |
| openai/gpt-oss-20b | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 8 | 1 | 58 | < 0.0001 |
| openai/gpt-oss-20b | openai/gpt-6-sol | 200 | 6 | 2 | 122 | < 0.0001 |
| openai/gpt-oss-20b | openai/gpt-6-sol | 200 | 8 | 1 | 99 | < 0.0001 |
| openai/gpt-oss-120b | allam-2-7b | 1098 | 6 | 207 | 23 | < 0.0001 |
| openai/gpt-oss-120b | allam-2-7b | 1098 | 8 | 60 | 25 | 0.0002 |
| openai/gpt-oss-120b | deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 6 | 44 | 392 | < 0.0001 |
| openai/gpt-oss-120b | deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 8 | 17 | 387 | < 0.0001 |
| openai/gpt-oss-120b | zai-org/GLM-5.3 | 1098 | 6 | 60 | 325 | < 0.0001 |
| openai/gpt-oss-120b | zai-org/GLM-5.3 | 1098 | 8 | 17 | 232 | < 0.0001 |
| openai/gpt-oss-120b | moonshotai/Kimi-K3 | 1098 | 6 | 33 | 408 | < 0.0001 |
| openai/gpt-oss-120b | moonshotai/Kimi-K3 | 1098 | 8 | 15 | 431 | < 0.0001 |
| openai/gpt-oss-120b | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 6 | 7 | 50 | < 0.0001 |
| openai/gpt-oss-120b | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 8 | 2 | 45 | < 0.0001 |
| openai/gpt-oss-120b | openai/gpt-6-sol | 200 | 6 | 4 | 91 | < 0.0001 |
| openai/gpt-oss-120b | openai/gpt-6-sol | 200 | 8 | 1 | 85 | < 0.0001 |
| allam-2-7b | deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 6 | 13 | 545 | < 0.0001 |
| allam-2-7b | deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 8 | 5 | 410 | < 0.0001 |
| allam-2-7b | zai-org/GLM-5.3 | 1098 | 6 | 16 | 465 | < 0.0001 |
| allam-2-7b | zai-org/GLM-5.3 | 1098 | 8 | 8 | 258 | < 0.0001 |
| allam-2-7b | moonshotai/Kimi-K3 | 1098 | 6 | 12 | 571 | < 0.0001 |
| allam-2-7b | moonshotai/Kimi-K3 | 1098 | 8 | 5 | 456 | < 0.0001 |
| allam-2-7b | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 6 | 1 | 73 | < 0.0001 |
| allam-2-7b | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 8 | 2 | 56 | < 0.0001 |
| allam-2-7b | openai/gpt-6-sol | 200 | 6 | 0 | 116 | < 0.0001 |
| allam-2-7b | openai/gpt-6-sol | 200 | 8 | 1 | 96 | < 0.0001 |
| deepseek-ai/DeepSeek-V4.1-Flash | zai-org/GLM-5.3 | 1098 | 6 | 211 | 128 | < 0.0001 |
| deepseek-ai/DeepSeek-V4.1-Flash | zai-org/GLM-5.3 | 1098 | 8 | 243 | 88 | < 0.0001 |
| deepseek-ai/DeepSeek-V4.1-Flash | moonshotai/Kimi-K3 | 1098 | 6 | 102 | 129 | 0.0869 |
| deepseek-ai/DeepSeek-V4.1-Flash | moonshotai/Kimi-K3 | 1098 | 8 | 88 | 134 | 0.0024 |
| deepseek-ai/DeepSeek-V4.1-Flash | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 6 | 24 | 17 | 0.3489 |
| deepseek-ai/DeepSeek-V4.1-Flash | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 8 | 23 | 19 | 0.6440 |
| deepseek-ai/DeepSeek-V4.1-Flash | openai/gpt-6-sol | 200 | 6 | 13 | 50 | < 0.0001 |
| deepseek-ai/DeepSeek-V4.1-Flash | openai/gpt-6-sol | 200 | 8 | 13 | 50 | < 0.0001 |
| zai-org/GLM-5.3 | moonshotai/Kimi-K3 | 1098 | 6 | 100 | 210 | < 0.0001 |
| zai-org/GLM-5.3 | moonshotai/Kimi-K3 | 1098 | 8 | 57 | 258 | < 0.0001 |
| zai-org/GLM-5.3 | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 6 | 24 | 22 | 0.8830 |
| zai-org/GLM-5.3 | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 8 | 16 | 31 | 0.0400 |
| zai-org/GLM-5.3 | openai/gpt-6-sol | 200 | 6 | 17 | 59 | < 0.0001 |
| zai-org/GLM-5.3 | openai/gpt-6-sol | 200 | 8 | 9 | 65 | < 0.0001 |
| moonshotai/Kimi-K3 | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 6 | 36 | 17 | 0.0127 |
| moonshotai/Kimi-K3 | nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 8 | 33 | 17 | 0.0328 |
| moonshotai/Kimi-K3 | openai/gpt-6-sol | 200 | 6 | 16 | 41 | 0.0013 |
| moonshotai/Kimi-K3 | openai/gpt-6-sol | 200 | 8 | 19 | 44 | 0.0022 |
| nvidia/nemotron-3-ultra-550b-a55b:free | openai/gpt-6-sol | 200 | 6 | 14 | 58 | < 0.0001 |
| nvidia/nemotron-3-ultra-550b-a55b:free | openai/gpt-6-sol | 200 | 8 | 14 | 55 | < 0.0001 |

| Model | n | 4-digit heading accuracy | wrong answers | wrong answers with the right heading |
|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 20.0% (17.8% to 22.5%) | 1098 | 20.0% (17.8% to 22.5%) |
| openai/gpt-oss-120b | 1098 | 45.1% (42.2% to 48.0%) | 1092 | 44.8% (41.9% to 47.7%) |
| allam-2-7b | 1098 | 9.7% (8.1% to 11.6%) | 1079 | 8.2% (6.7% to 9.9%) |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 67.7% (64.8% to 70.4%) | 823 | 56.9% (53.5% to 60.2%) |
| zai-org/GLM-5.3 | 1098 | 63.8% (61.0% to 66.6%) | 962 | 58.7% (55.6% to 61.8%) |
| moonshotai/Kimi-K3 | 1098 | 70.0% (67.3% to 72.7%) | 786 | 58.1% (54.7% to 61.5%) |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 58.5% (51.6% to 65.1%) | 172 | 51.7% (44.3% to 59.1%) |
| openai/gpt-6-sol | 200 | 73.5% (67.0% to 79.1%) | 135 | 60.7% (52.3% to 68.6%) |

### 2. Agreement between models on the same 8-digit code (models run on all 1,098 rulings)

Models: openai/gpt-oss-20b, openai/gpt-oss-120b, allam-2-7b, deepseek-ai/DeepSeek-V4.1-Flash, zai-org/GLM-5.3, moonshotai/Kimi-K3 (6 models). An 8-digit answer needs at least 8 digits.

| Agreement rule | rulings | share of all rulings | accuracy of the agreed code (8-digit) | mean accuracy of each agreeing model alone on the same rulings |
|---|---|---|---|---|
| 2+ models give the same 8-digit code | 794 | 72.3% | 48.4% (44.9% to 51.8%) | 52.1% |
| 3+ models give the same 8-digit code | 294 | 26.8% | 67.7% (62.1% to 72.8%) | 68.0% |

### 3. Duty priced at the 8-digit level (secondary)

For answers whose first 8 digits exist in the HTS, both the answer and the true code are priced at 8 digits. Gate B rules as above. 'Added cases' = rate-changing cases beyond the 10-digit analysis.

| Model | answers with first 8 existing | rate-changing at 8 digits (n) | underpaid | underpay share (95% CI) | p vs Baseline 2 | verdict | 10-digit-level n (primary table) | added cases |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 164 | 77 | 55 | 71.4% (60.5% to 80.3%) | 0.0140 | underpays more than chance | 46 | +31 |
| openai/gpt-oss-120b | 281 | 141 | 81 | 57.4% (49.2% to 65.3%) | 0.7962 | not distinguishable from chance | 49 | +92 |
| allam-2-7b | 205 | 133 | 80 | 60.2% (51.7% to 68.1%) | 0.1219 | not distinguishable from chance | 116 | +17 |
| deepseek-ai/DeepSeek-V4.1-Flash | 949 | 324 | 175 | 54.0% (48.6% to 59.4%) | 0.8092 | not distinguishable from chance | 324 | +0 |
| zai-org/GLM-5.3 | 641 | 217 | 121 | 55.8% (49.1% to 62.2%) | 0.7083 | not distinguishable from chance | 212 | +5 |
| moonshotai/Kimi-K3 | 1008 | 312 | 185 | 59.3% (53.8% to 64.6%) | 0.3377 | not distinguishable from chance | 311 | +1 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 90 | 40 | 24 | 60.0% (44.6% to 73.7%) | 0.5764 | not distinguishable from chance | 40 | +0 |
| openai/gpt-6-sol | 154 | 41 | 21 | 51.2% (36.5% to 65.7%) | 0.4515 | not distinguishable from chance | 41 | +0 |

### 4. Biggest misses

See review/biggest_misses.md (10 largest underpayments and overpayments across all models; the ruling ids are tagged in demo_data.json).

### 5. What it costs to run

| Model | calls | avg input tokens | avg output tokens | avg seconds per call | finish_reason counts | list-price cost per 1,000 rulings |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 324 | 202 | 0.3 | {'stop': 1098} | free tier |
| openai/gpt-oss-120b | 1098 | 324 | 180 | 0.4 | {'stop': 1098} | free tier |
| allam-2-7b | 1098 | 304 | 78 | 0.1 | {'stop': 1098} | free tier |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 260 | 65 | 1.3 | {'stop': 1098} | $0.16 |
| zai-org/GLM-5.3 | 1098 | 270 | 180 | 2.8 | {'stop': 1097, 'length': 1} | $1.17 |
| moonshotai/Kimi-K3 | 1098 | 272 | 65 | 9.0 | {'stop': 1098} | $1.79 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 281 | 74 | 4.8 | {'stop': 200} | free tier |
| openai/gpt-6-sol | 200 | 258 | 48 | 2.0 | {'stop': 200} | $0.99 |

**Number of extra (exploratory) hypothesis tests run: 64** (McNemar pairs at two levels, plus the 8-digit-level baseline tests). The other extras are descriptive.
