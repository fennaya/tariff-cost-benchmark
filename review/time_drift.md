# Time-drift test: 8-digit accuracy before vs after 2026-04-20 (scripts/analyze_time_drift.py)

Added after the v1.2 results were seen; no new API calls. Rulings dated on or before 2026-04-20 vs after it, all 1,098 rulings per model, 8-digit accuracy with Wilson 95% CIs. 'Drop' = before minus after, in percentage points. p-values: two-sided pooled two-proportion z-test and Fisher exact test (descriptive, not corrected for multiple comparison; 14 rows). GPT-6 Sol's stated cutoff is the split date. gpt-oss-20b and gpt-oss-120b have a 2024 cutoff and cannot have seen any ruling. The Claude models' stated cutoff is 2026-06-30 and Nemotron's 2026-05-31, so the split here is not their cutoff and only shows the time trend. † no stated cutoff.

| Model | Stated cutoff | n up to 2026-04-20 | 8-digit up to 2026-04-20 | n after | 8-digit after | drop (points) | p (z-test) | p (Fisher) |
|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 2024-06-01 | 560 | 0.0% (0.0% to 0.7%) | 538 | 0.6% (0.2% to 1.6%) | -0.6 | 0.0768 | 0.1173 |
| openai/gpt-oss-120b | 2024-06-01 | 560 | 5.9% (4.2% to 8.2%) | 538 | 5.2% (3.6% to 7.4%) | +0.7 | 0.6186 | 0.6931 |
| allam-2-7b | none stated † | 560 | 3.0% (1.9% to 4.8%) | 538 | 1.7% (0.9% to 3.1%) | +1.4 | 0.1376 | 0.1658 |
| deepseek-ai/DeepSeek-V4.1-Flash | none stated † | 560 | 43.0% (39.0% to 47.2%) | 538 | 35.3% (31.4% to 39.4%) | +7.7 | 0.0088 | 0.0094 |
| zai-org/GLM-5.3 | none stated † | 560 | 28.9% (25.3% to 32.8%) | 538 | 21.2% (17.9% to 24.8%) | +7.7 | 0.0031 | 0.0035 |
| moonshotai/Kimi-K3 | none stated † | 560 | 48.2% (44.1% to 52.4%) | 538 | 38.5% (34.5% to 42.7%) | +9.7 | 0.0011 | 0.0012 |
| openai/gpt-6-sol | 2026-04-20 | 560 | 58.9% (54.8% to 62.9%) | 538 | 49.6% (45.4% to 53.8%) | +9.3 | 0.0020 | 0.0020 |
| anthropic/claude-haiku-5.5 | 2026-06-30 | 560 | 19.3% (16.2% to 22.8%) | 538 | 16.9% (14.0% to 20.3%) | +2.4 | 0.3079 | 0.3098 |
| anthropic/claude-sonnet-5.5 | 2026-06-30 | 560 | 48.4% (44.3% to 52.5%) | 538 | 41.3% (37.2% to 45.5%) | +7.1 | 0.0176 | 0.0181 |
| anthropic/claude-opus-5.5 | 2026-06-30 | 560 | 56.8% (52.7% to 60.8%) | 538 | 53.9% (49.7% to 58.1%) | +2.9 | 0.3368 | 0.3624 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 2026-05-31 | 560 | 32.9% (29.1% to 36.9%) | 538 | 27.0% (23.4% to 30.9%) | +5.9 | 0.0327 | 0.0350 |
| replication: moonshotai/kimi-k3 | none stated † | 560 | 47.1% (43.0% to 51.3%) | 538 | 37.0% (33.0% to 41.1%) | +10.2 | 0.0007 | 0.0008 |
| replication: deepseek/deepseek-v4.1-flash | none stated † | 560 | 41.4% (37.4% to 45.6%) | 538 | 35.7% (31.8% to 39.8%) | +5.7 | 0.0508 | 0.0547 |
| replication: z-ai/glm-5.3 | none stated † | 560 | 24.6% (21.3% to 28.4%) | 538 | 20.6% (17.4% to 24.3%) | +4.0 | 0.1126 | 0.1136 |

## Could the 2024-cutoff models have shown a drop like Sol's?

Sol's drop is 9.3 points, a relative drop of 15.8%. For each 2024-cutoff model, the table gives the drop in points that the same relative drop would be on its own pre-split accuracy, and the power of the two-sided z-test (alpha 0.05, normal approximation) to detect it with the observed n. A control with low power cannot show 'no drop'; it only fails to show one.

| Model | observed before | drop of the same relative size (points) | power to detect it |
|---|---|---|---|
| openai/gpt-oss-20b | 0.0% | 0.03 | 5% |
| openai/gpt-oss-120b | 5.9% | 0.93 | 10% |
