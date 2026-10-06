# Headline B audit (Round 2, Part 2)

**Gate B verdict: PASS for at least one model** (needs: observed underpay share beats Baseline 2 at p<0.05).

- allam-2-7b: PASS
- openai/gpt-oss-120b: PASS
- openai/gpt-oss-20b: PASS
## 1-3. Baselines and permutation tests

Baseline 1: random sibling sharing the true code's 4-digit heading. Baseline 2: random sibling sharing the deepest prefix the model itself got right (0 digits if it got none). 1000 reps each.

| Model | Observed underpay share (n) | Baseline 1 mean [95% range] | p vs Baseline 1 | Baseline 2 mean [95% range] | p vs Baseline 2 | Gate B |
|---|---|---|---|---|---|---|
| allam-2-7b | 0.655 (116) | 0.569 [0.533, 0.607] | < 0.001 | 0.456 [0.427, 0.484] | < 0.001 | PASS |
| openai/gpt-oss-120b | 0.653 (49) | 0.569 [0.531, 0.604] | < 0.001 | 0.503 [0.471, 0.536] | < 0.001 | PASS |
| openai/gpt-oss-20b | 0.674 (46) | 0.568 [0.534, 0.602] | < 0.001 | 0.490 [0.461, 0.519] | < 0.001 | PASS |

## 4. "Other" catch-all baskets


### allam-2-7b

- True codes of wrong answers that are an "Other"-type basket: 672/1079 (62.3%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 60/122 (49.2%)
- Mean rate when the TRUE code is an "Other" basket: 2.67% (n=666) vs. 3.97% for named/specific true codes (n=392)

### openai/gpt-oss-120b

- True codes of wrong answers that are an "Other"-type basket: 687/1092 (62.9%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 11/31 (35.5%)
- Mean rate when the TRUE code is an "Other" basket: 2.61% (n=681) vs. 3.99% for named/specific true codes (n=390)

### openai/gpt-oss-20b

- True codes of wrong answers that are an "Other"-type basket: 691/1098 (62.9%)
- Predicted codes of wrong answers (where resolvable) that are an "Other"-type basket: 2/18 (11.1%)
- Mean rate when the TRUE code is an "Other" basket: 2.60% (n=685) vs. 3.97% for named/specific true codes (n=392)

**Reading this:** the hypothesis was that predicted codes landing in "Other" catch-all baskets more often than true codes do -- combined with those baskets' lower average rates -- could mechanically explain underpay bias. The data runs the OPPOSITE direction for all 3 models: predicted codes land in "Other" baskets LESS often than true codes do (e.g. 11-49% vs. 62-63%), meaning predictions skew toward named/specific subheadings relative to the true distribution. Taken alone, that skew would push toward OVERPAYING on average (named subheadings carry higher rates here), not underpaying. Since the models are observed to underpay anyway (Gate B above), this specific mechanism does NOT explain the bias -- it would predict the wrong direction. Reported as a checked, ruled-out hypothesis rather than a confirmed one.

## 5. Duty at stake per $100,000, underpay vs. overpay separately

| Model | Underpay: median | Underpay: n | Overpay: median | Overpay: n |
|---|---|---|---|---|
| allam-2-7b | $4,300.00 | 76 | $5,400.00 | 40 |
| openai/gpt-oss-120b | $2,550.00 | 32 | $2,100.00 | 17 |
| openai/gpt-oss-20b | $4,200.00 | 31 | $4,900.00 | 15 |