# Language comparison (Round 2, Part 4)

3-way set (both languages approved): **84/100**. EN-vs-FR set (French approved): **93/100**. EN-vs-AR set (Arabic approved): **90/100**.


## openai/gpt-oss-20b


### EN vs FR (all FR-approved) (n=93)

| Digit level | EN accuracy | Other accuracy | McNemar p |
|---|---|---|---|
| 8 *(headline)* | 0.011 | 0.000 | 1.0000 |
| 6 | 0.075 | 0.043 | 0.3750 |
| 10 | 0.000 | 0.000 | nan |

Duty-at-stake median: EN $0.00 vs. other $2800.00, paired bootstrap median diff $2800.00 [95% CI -5200.00, 15500.00]

Underpay share: EN 0.600 vs. other 0.500

### EN vs AR (all AR-approved) (n=90)

| Digit level | EN accuracy | Other accuracy | McNemar p |
|---|---|---|---|
| 8 *(headline)* | 0.011 | 0.000 | 1.0000 |
| 6 | 0.078 | 0.033 | 0.2188 |
| 10 | 0.000 | 0.000 | nan |

Duty-at-stake median: EN $0.00 vs. other $0.00, paired bootstrap median diff $0.00 [95% CI -4000.00, 3050.00]

Underpay share: EN 0.500 vs. other 0.667

**Power note (10-digit, n=93):** at this sample size, the smallest EN-vs-translation accuracy difference detectable at 80% power (alpha=0.05) is approximately 0.10 (baseline EN accuracy 0.000). Non-significant McNemar results above should be read as "no difference detected at this sample size," not as evidence of no difference. This estimate assumes independence between languages' per-ruling correctness, a simplification likely to UNDERSTATE real power (positively correlated errors would make McNemar more sensitive).


## openai/gpt-oss-120b


### EN vs FR (all FR-approved) (n=93)

| Digit level | EN accuracy | Other accuracy | McNemar p |
|---|---|---|---|
| 8 *(headline)* | 0.097 | 0.086 | 1.0000 |
| 6 | 0.204 | 0.204 | 1.0000 |
| 10 | 0.011 | 0.011 | nan |

Duty-at-stake median: EN $0.00 vs. other $0.00, paired bootstrap median diff $0.00 [95% CI -24400.00, 0.00]

Underpay share: EN 1.000 vs. other 1.000

### EN vs AR (all AR-approved) (n=90)

| Digit level | EN accuracy | Other accuracy | McNemar p |
|---|---|---|---|
| 8 *(headline)* | 0.078 | 0.044 | 0.2500 |
| 6 | 0.189 | 0.167 | 0.7266 |
| 10 | 0.011 | 0.000 | 1.0000 |

Duty-at-stake median: EN $0.00 vs. other $0.00, paired bootstrap median diff $0.00 [95% CI -13650.00, 3950.00]

Underpay share: EN 0.500 vs. other 0.500

**Power note (10-digit, n=93):** at this sample size, the smallest EN-vs-translation accuracy difference detectable at 80% power (alpha=0.05) is approximately 0.15 (baseline EN accuracy 0.011). Non-significant McNemar results above should be read as "no difference detected at this sample size," not as evidence of no difference. This estimate assumes independence between languages' per-ruling correctness, a simplification likely to UNDERSTATE real power (positively correlated errors would make McNemar more sensitive).


## allam-2-7b


### EN vs FR (all FR-approved) (n=93)

| Digit level | EN accuracy | Other accuracy | McNemar p |
|---|---|---|---|
| 8 *(headline)* | 0.000 | 0.022 | 0.5000 |
| 6 | 0.022 | 0.032 | 1.0000 |
| 10 | 0.000 | 0.011 | 1.0000 |

Duty-at-stake median: EN $7000.00 vs. other $500.00, paired bootstrap median diff $-6100.00 [95% CI -12200.00, 0.00]

Underpay share: EN 0.545 vs. other 0.800

### EN vs AR (all AR-approved) (n=90)

| Digit level | EN accuracy | Other accuracy | McNemar p |
|---|---|---|---|
| 8 *(headline)* | 0.000 | 0.011 | 1.0000 |
| 6 | 0.033 | 0.067 | 0.2500 |
| 10 | 0.000 | 0.011 | 1.0000 |

Duty-at-stake median: EN $7000.00 vs. other $3700.00, paired bootstrap median diff $-3700.00 [95% CI -9900.00, 4800.00]

Underpay share: EN 0.556 vs. other 0.600

**Power note (10-digit, n=93):** at this sample size, the smallest EN-vs-translation accuracy difference detectable at 80% power (alpha=0.05) is approximately 0.10 (baseline EN accuracy 0.000). Non-significant McNemar results above should be read as "no difference detected at this sample size," not as evidence of no difference. This estimate assumes independence between languages' per-ruling correctness, a simplification likely to UNDERSTATE real power (positively correlated errors would make McNemar more sensitive).


## allam-2-7b: Arabic vs. English, specifically

allam-2-7b (SDAIA/IBM) is the one Arabic-focused model among the three tested here. Does that specialization show up as better Arabic-language performance on this task?

(n=90 Arabic-approved rulings)

| Digit level | English accuracy | Arabic accuracy | Arabic better? | McNemar p |
|---|---|---|---|---|
| 8 *(headline)* | 0.000 | 0.011 | yes | 1.0000 |
| 6 | 0.033 | 0.067 | yes | 0.2500 |
| 10 | 0.000 | 0.011 | yes | 1.0000 |

Underpay share: English 0.556 vs. Arabic 0.600

**Reading this:** a model's language of training/focus does not automatically translate into better performance on a DIFFERENT task (US tariff classification) conducted in that language -- the HTS schedule, product terminology, and classification logic are English-language in origin regardless of which language the product description is presented in. Whatever this table shows should be read as a data point about this specific task, not a general claim about allam-2-7b's Arabic capability.