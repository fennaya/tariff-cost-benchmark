# Headline B audit (Round 2, Part 2)

**Gate B verdict: PASS for at least one model** (needs: observed underpay share beats Baseline 2 at p<0.05).

- openai/gpt-oss-20b: PASS
- openai/gpt-oss-120b: PASS
- allam-2-7b: PASS
- deepseek-ai/DeepSeek-V4.1-Flash: NOT MET
- zai-org/GLM-5.3: PASS
- moonshotai/Kimi-K3: PASS
- nvidia/nemotron-3-ultra-550b-a55b:free: NOT MET
- openai/gpt-6-sol: PASS
- anthropic/claude-haiku-5.5: PASS
- anthropic/claude-sonnet-5.5: NOT MET
- anthropic/claude-opus-5.5: NOT MET
## 1-3. Baselines and permutation tests

Baseline 1: random sibling sharing the true code's 4-digit heading. Baseline 2: random sibling sharing the deepest prefix the model itself got right (0 digits if it got none). 1000 reps each.

| Model | Observed underpay share (n) | Baseline 1 mean [95% range] | p vs Baseline 1 | Baseline 2 mean [95% range] | p vs Baseline 2 | Gate B |
|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 0.674 (46) | 0.568 [0.534, 0.602] | < 0.001 | 0.490 [0.461, 0.519] | < 0.001 | PASS |
| openai/gpt-oss-120b | 0.653 (49) | 0.569 [0.531, 0.604] | < 0.001 | 0.503 [0.471, 0.536] | < 0.001 | PASS |
| allam-2-7b | 0.655 (116) | 0.569 [0.533, 0.607] | < 0.001 | 0.456 [0.427, 0.484] | < 0.001 | PASS |
| deepseek-ai/DeepSeek-V4.1-Flash | 0.540 (324) | 0.592 [0.550, 0.633] | 0.9930 | 0.520 [0.480, 0.560] | 0.1748 | NOT MET |
| zai-org/GLM-5.3 | 0.557 (212) | 0.576 [0.539, 0.614] | 0.8322 | 0.510 [0.474, 0.545] | 0.0060 | PASS |
| moonshotai/Kimi-K3 | 0.592 (311) | 0.589 [0.546, 0.629] | 0.4496 | 0.535 [0.493, 0.578] | 0.0040 | PASS |
| nvidia/nemotron-3-ultra-550b-a55b:free | 0.490 (384) | 0.594 [0.553, 0.633] | 1.0000 | 0.491 [0.454, 0.529] | 0.5305 | NOT MET |
| openai/gpt-6-sol | 0.566 (256) | 0.588 [0.542, 0.632] | 0.8402 | 0.509 [0.465, 0.554] | 0.0080 | PASS |
| anthropic/claude-haiku-5.5 | 0.530 (281) | 0.580 [0.538, 0.618] | 0.9930 | 0.480 [0.445, 0.515] | 0.0040 | PASS |
| anthropic/claude-sonnet-5.5 | 0.538 (264) | 0.593 [0.550, 0.631] | 0.9940 | 0.507 [0.467, 0.547] | 0.0739 | NOT MET |
| anthropic/claude-opus-5.5 | 0.463 (268) | 0.585 [0.540, 0.632] | 1.0000 | 0.468 [0.423, 0.514] | 0.5814 | NOT MET |

## 4. "Other" catch-all baskets


### openai/gpt-oss-20b

- True codes of wrong answers that are an "Other"-type basket: 691/1098 (62.9%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 2/18 (11.1%)
- Mean rate when the TRUE code is an "Other" basket: 2.60% (n=685) vs. 3.97% for named/specific true codes (n=392)

### openai/gpt-oss-120b

- True codes of wrong answers that are an "Other"-type basket: 687/1092 (62.9%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 11/31 (35.5%)
- Mean rate when the TRUE code is an "Other" basket: 2.61% (n=681) vs. 3.99% for named/specific true codes (n=390)

### allam-2-7b

- True codes of wrong answers that are an "Other"-type basket: 672/1079 (62.3%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 60/122 (49.2%)
- Mean rate when the TRUE code is an "Other" basket: 2.67% (n=666) vs. 3.97% for named/specific true codes (n=392)

### deepseek-ai/DeepSeek-V4.1-Flash

- True codes of wrong answers that are an "Other"-type basket: 507/823 (61.6%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 282/476 (59.2%)
- Mean rate when the TRUE code is an "Other" basket: 2.82% (n=501) vs. 4.01% for named/specific true codes (n=303)

### zai-org/GLM-5.3

- True codes of wrong answers that are an "Other"-type basket: 609/962 (63.3%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 102/223 (45.7%)
- Mean rate when the TRUE code is an "Other" basket: 2.60% (n=603) vs. 4.13% for named/specific true codes (n=341)

### moonshotai/Kimi-K3

- True codes of wrong answers that are an "Other"-type basket: 481/786 (61.2%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 294/516 (57.0%)
- Mean rate when the TRUE code is an "Other" basket: 3.11% (n=476) vs. 3.85% for named/specific true codes (n=296)

### nvidia/nemotron-3-ultra-550b-a55b:free

- True codes of wrong answers that are an "Other"-type basket: 596/942 (63.3%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 243/487 (49.9%)
- Mean rate when the TRUE code is an "Other" basket: 2.72% (n=590) vs. 4.04% for named/specific true codes (n=333)

### openai/gpt-6-sol

- True codes of wrong answers that are an "Other"-type basket: 420/686 (61.2%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 251/447 (56.2%)
- Mean rate when the TRUE code is an "Other" basket: 2.80% (n=414) vs. 4.10% for named/specific true codes (n=260)

### anthropic/claude-haiku-5.5

- True codes of wrong answers that are an "Other"-type basket: 628/1011 (62.1%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 156/314 (49.7%)
- Mean rate when the TRUE code is an "Other" basket: 2.67% (n=622) vs. 4.11% for named/specific true codes (n=369)

### anthropic/claude-sonnet-5.5

- True codes of wrong answers that are an "Other"-type basket: 505/821 (61.5%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 221/390 (56.7%)
- Mean rate when the TRUE code is an "Other" basket: 2.81% (n=499) vs. 4.45% for named/specific true codes (n=304)

### anthropic/claude-opus-5.5

- True codes of wrong answers that are an "Other"-type basket: 448/710 (63.1%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 225/418 (53.8%)
- Mean rate when the TRUE code is an "Other" basket: 2.60% (n=442) vs. 4.12% for named/specific true codes (n=253)

**Reading this:** the hypothesis was that predicted codes landing in "Other" catch-all baskets more often than true codes do -- combined with those baskets' lower average rates -- could mechanically explain underpay bias. The data runs the OPPOSITE direction for all 3 models: predicted codes land in "Other" baskets LESS often than true codes do (e.g. 11-49% vs. 62-63%), meaning predictions skew toward named/specific subheadings relative to the true distribution. Taken alone, that skew would push toward OVERPAYING on average (named subheadings carry higher rates here), not underpaying. Since the models are observed to underpay anyway (Gate B above), this specific mechanism does NOT explain the bias -- it would predict the wrong direction. Reported as a checked, ruled-out hypothesis rather than a confirmed one.

## 5. Duty at stake per $100,000, underpay vs. overpay separately

| Model | Underpay: median | Underpay: n | Overpay: median | Overpay: n |
|---|---|---|---|---|
| openai/gpt-oss-20b | $4,200.00 | 31 | $4,900.00 | 15 |
| openai/gpt-oss-120b | $2,550.00 | 32 | $2,100.00 | 17 |
| allam-2-7b | $4,300.00 | 76 | $5,400.00 | 40 |
| deepseek-ai/DeepSeek-V4.1-Flash | $2,800.00 | 175 | $3,700.00 | 149 |
| zai-org/GLM-5.3 | $2,900.00 | 118 | $3,450.00 | 94 |
| moonshotai/Kimi-K3 | $2,800.00 | 184 | $3,200.00 | 127 |
| nvidia/nemotron-3-ultra-550b-a55b:free | $2,900.00 | 188 | $3,700.00 | 196 |
| openai/gpt-6-sol | $2,800.00 | 145 | $3,200.00 | 111 |
| anthropic/claude-haiku-5.5 | $2,800.00 | 149 | $3,800.00 | 132 |
| anthropic/claude-sonnet-5.5 | $3,200.00 | 142 | $4,100.00 | 122 |
| anthropic/claude-opus-5.5 | $2,750.00 | 124 | $3,900.00 | 144 |