# MFN rates at the ruling-date release vs the current schedule (scripts/check_rate_impact.py)

Distinct (code, ruling date) pairs used by the cost analysis (true and predicted codes of wrong answers, all 3 models): **4,060**; of these, 1,288 resolve to an ad valorem or free rate on the current JSON.

| Comparison | Pairs that differ |
|---|---|
| parser check: 2026HTSRev20 PDF vs current JSON | 10 |
| time effect: ruling-date release vs 2026HTSRev20 (same parser) | 0 |
| combined: ruling-date release vs current JSON | 10 |

## Direction and dollar figures re-run with ruling-date rates

| Model | basis | comparable wrong answers (n) | rate differs (n) | underpaid | underpay share (Wilson 95% CI) | median duty at stake per $100k | IQR |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | original Phase 3 (JSON only, markup unparsed) | 101 | 46 | 31 | 67.4% (53.0% to 79.1%) | $0 | $0 to $3,500 |
| openai/gpt-oss-20b | JSON only, markup stripped | 101 | 46 | 31 | 67.4% (53.0% to 79.1%) | $0 | $0 to $3,500 |
| openai/gpt-oss-20b | ruling-date release rates (final) | 101 | 46 | 31 | 67.4% (53.0% to 79.1%) | $0 | $0 to $3,500 |
| openai/gpt-oss-120b | original Phase 3 (JSON only, markup unparsed) | 85 | 47 | 30 | 63.8% (49.5% to 76.0%) | $600 | $0 to $2,600 |
| openai/gpt-oss-120b | JSON only, markup stripped | 85 | 47 | 30 | 63.8% (49.5% to 76.0%) | $600 | $0 to $2,600 |
| openai/gpt-oss-120b | ruling-date release rates (final) | 93 | 49 | 32 | 65.3% (51.3% to 77.1%) | $300 | $0 to $2,500 |
| allam-2-7b | original Phase 3 (JSON only, markup unparsed) | 145 | 115 | 75 | 65.2% (56.1% to 73.3%) | $3,500 | $500 to $6,500 |
| allam-2-7b | JSON only, markup stripped | 146 | 116 | 76 | 65.5% (56.5% to 73.5%) | $3,450 | $500 to $6,500 |
| allam-2-7b | ruling-date release rates (final) | 147 | 116 | 76 | 65.5% (56.5% to 73.5%) | $3,400 | $350 to $6,500 |

## Parser accuracy and markup (6/8-digit rows of the current release)

- JSON rows with an ad valorem or free General rate: 4,762; not reproduced by the PDF parse: 17 (of which in chapters 1-97: 3).
- JSON rates carrying HTML markup that the original classifier read as 'other' but are ad valorem or free once stripped: 5.
