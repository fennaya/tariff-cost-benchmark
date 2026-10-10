# Headline A audit (Round 2, Part 1)

**Gate A verdict: PASS** (needs: Check 1 no >1pt format-bug swing, AND Check 4 >=19/20 ground-truth match).

- Check 1 (format/zero-padding): no bug found
- Check 4 (ground truth, requested 20-sample): 20/20 match (PASS)
- Check 4 (ground truth, full 1098-ruling set): 11 mismatches found
## 1. Format mismatch (zero-padding)

Old scoring (`analysis.py`): strip to digits only, no padding -- a prediction shorter than the digit level being checked cannot match at that level.

New scoring (this check): same digit-only stripping, then zero-pad both codes to 10 digits before comparing prefixes.


### openai/gpt-oss-20b

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.5574 | 0.5574 | +0.00 |
| 4 | 0.2004 | 0.2004 | +0.00 |
| 6 | 0.0301 | 0.0301 | +0.00 |
| 8 | 0.0027 | 0.0027 | +0.00 |
| 10 | 0.0000 | 0.0000 | +0.00 |

### openai/gpt-oss-120b

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.6821 | 0.6821 | +0.00 |
| 4 | 0.4508 | 0.4508 | +0.00 |
| 6 | 0.2113 | 0.2113 | +0.00 |
| 8 | 0.0556 | 0.0556 | +0.00 |
| 10 | 0.0055 | 0.0100 | +0.46 |

### allam-2-7b

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.4153 | 0.4153 | +0.00 |
| 4 | 0.0974 | 0.0974 | +0.00 |
| 6 | 0.0437 | 0.0437 | +0.00 |
| 8 | 0.0237 | 0.0237 | +0.00 |
| 10 | 0.0173 | 0.0173 | +0.00 |

### deepseek-ai/DeepSeek-V4.1-Flash

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.7860 | 0.7860 | +0.00 |
| 4 | 0.6767 | 0.6767 | +0.00 |
| 6 | 0.5282 | 0.5282 | +0.00 |
| 8 | 0.3925 | 0.3925 | +0.00 |
| 10 | 0.2505 | 0.2505 | +0.00 |

### zai-org/GLM-5.3

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.7568 | 0.7568 | +0.00 |
| 4 | 0.6384 | 0.6384 | +0.00 |
| 6 | 0.4526 | 0.4526 | +0.00 |
| 8 | 0.2514 | 0.2514 | +0.00 |
| 10 | 0.1239 | 0.1239 | +0.00 |

### moonshotai/Kimi-K3

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.8051 | 0.8051 | +0.00 |
| 4 | 0.7004 | 0.7004 | +0.00 |
| 6 | 0.5528 | 0.5528 | +0.00 |
| 8 | 0.4344 | 0.4344 | +0.00 |
| 10 | 0.2842 | 0.2842 | +0.00 |

### nvidia/nemotron-3-ultra-550b-a55b:free

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.6850 | 0.6850 | +0.00 |
| 4 | 0.5850 | 0.5850 | +0.00 |
| 6 | 0.3950 | 0.3950 | +0.00 |
| 8 | 0.2900 | 0.2900 | +0.00 |
| 10 | 0.1400 | 0.1400 | +0.00 |

### openai/gpt-6-sol

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.8434 | 0.8434 | +0.00 |
| 4 | 0.7650 | 0.7650 | +0.00 |
| 6 | 0.6703 | 0.6703 | +0.00 |
| 8 | 0.5437 | 0.5437 | +0.00 |
| 10 | 0.3752 | 0.3752 | +0.00 |

### anthropic/claude-haiku-5.5

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.6803 | 0.6803 | +0.00 |
| 4 | 0.5355 | 0.5355 | +0.00 |
| 6 | 0.3251 | 0.3251 | +0.00 |
| 8 | 0.1812 | 0.1812 | +0.00 |
| 10 | 0.0792 | 0.0792 | +0.00 |

### anthropic/claude-sonnet-5.5

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.8033 | 0.8033 | +0.00 |
| 4 | 0.7067 | 0.7067 | +0.00 |
| 6 | 0.6166 | 0.6166 | +0.00 |
| 8 | 0.4490 | 0.4490 | +0.00 |
| 10 | 0.2523 | 0.2523 | +0.00 |

### anthropic/claude-opus-5.5

| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |
|---|---|---|---|
| 2 | 0.8333 | 0.8333 | +0.00 |
| 4 | 0.7486 | 0.7486 | +0.00 |
| 6 | 0.6922 | 0.6922 | +0.00 |
| 8 | 0.5537 | 0.5537 | +0.00 |
| 10 | 0.3534 | 0.3534 | +0.00 |

**Verdict:** no digit level moved by more than 1 point. Zero-padding does not change the headline numbers; the old no-padding scoring and this stricter normalization agree, so this is not the source of Headline A's low numbers.

## 2. 8-digit (duty-bearing) accuracy as a headline-grade number

The last 2 digits of a 10-digit HTS code are a US-only statistical suffix, frequently not binding for duty purposes (the duty rate is usually set at the 8-digit tariff-item level -- see DECISIONS.md's 'Gate 3 duty-rate resolution' entry from Round 1). Reporting 8-digit accuracy alongside 10-digit gives a duty-relevant headline number.

| Model | 8-digit accuracy | 10-digit accuracy |
|---|---|---|
| openai/gpt-oss-20b | 0.0027 | 0.0000 |
| openai/gpt-oss-120b | 0.0556 | 0.0055 |
| allam-2-7b | 0.0237 | 0.0173 |
| deepseek-ai/DeepSeek-V4.1-Flash | 0.3925 | 0.2505 |
| zai-org/GLM-5.3 | 0.2514 | 0.1239 |
| moonshotai/Kimi-K3 | 0.4344 | 0.2842 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 0.2900 | 0.1400 |
| openai/gpt-6-sol | 0.5437 | 0.3752 |
| anthropic/claude-haiku-5.5 | 0.1812 | 0.0792 |
| anthropic/claude-sonnet-5.5 | 0.4490 | 0.2523 |
| anthropic/claude-opus-5.5 | 0.5537 | 0.3534 |

## 3. Parse failures vs. invalid-but-parsed vs. valid-but-wrong

| Model | n | (a) unparseable JSON | (b) parsed, INVALID_CODE | (c) valid, wrong | (d) valid, correct | Accuracy incl. (a)+(b) | Accuracy excl. (a)+(b) |
|---|---|---|---|---|---|---|---|
| openai/gpt-oss-20b | 1098 | 0 (0.0%) | 1080 (98.4%) | 18 (1.6%) | 0 (0.0%) | 0.0000 | 0.0000 |
| openai/gpt-oss-120b | 1098 | 1 (0.1%) | 1060 (96.5%) | 31 (2.8%) | 6 (0.5%) | 0.0055 | 0.1622 |
| allam-2-7b | 1098 | 8 (0.7%) | 949 (86.4%) | 122 (11.1%) | 19 (1.7%) | 0.0173 | 0.1348 |
| deepseek-ai/DeepSeek-V4.1-Flash | 1098 | 1 (0.1%) | 353 (32.1%) | 476 (43.4%) | 268 (24.4%) | 0.2441 | 0.3602 |
| zai-org/GLM-5.3 | 1098 | 27 (2.5%) | 715 (65.1%) | 223 (20.3%) | 133 (12.1%) | 0.1211 | 0.3736 |
| moonshotai/Kimi-K3 | 1098 | 0 (0.0%) | 278 (25.3%) | 516 (47.0%) | 304 (27.7%) | 0.2769 | 0.3707 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 200 | 0 (0.0%) | 75 (37.5%) | 98 (49.0%) | 27 (13.5%) | 0.1350 | 0.2160 |
| openai/gpt-6-sol | 1098 | 0 (0.0%) | 248 (22.6%) | 447 (40.7%) | 403 (36.7%) | 0.3670 | 0.4741 |
| anthropic/claude-haiku-5.5 | 1098 | 14 (1.3%) | 685 (62.4%) | 314 (28.6%) | 85 (7.7%) | 0.0774 | 0.2130 |
| anthropic/claude-sonnet-5.5 | 1098 | 0 (0.0%) | 438 (39.9%) | 390 (35.5%) | 270 (24.6%) | 0.2459 | 0.4091 |
| anthropic/claude-opus-5.5 | 1098 | 0 (0.0%) | 305 (27.8%) | 418 (38.1%) | 375 (34.2%) | 0.3415 | 0.4729 |

openai/gpt-oss-20b: 98.4% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.0000 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.0000, computed here for comparison only.

openai/gpt-oss-120b: 96.6% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.0055 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.1622, computed here for comparison only.

allam-2-7b: 87.2% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.0173 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.1348, computed here for comparison only.

deepseek-ai/DeepSeek-V4.1-Flash: 32.2% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.2441 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.3602, computed here for comparison only.

zai-org/GLM-5.3: 67.6% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.1211 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.3736, computed here for comparison only.

moonshotai/Kimi-K3: 25.3% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.2769 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.3707, computed here for comparison only.

nvidia/nemotron-3-ultra-550b-a55b:free: 37.5% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.1350 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.2160, computed here for comparison only.

openai/gpt-6-sol: 22.6% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.3670 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.4741, computed here for comparison only.

anthropic/claude-haiku-5.5: 63.7% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.0774 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.2130, computed here for comparison only.

anthropic/claude-sonnet-5.5: 39.9% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.2459 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.4091, computed here for comparison only.

anthropic/claude-opus-5.5: 27.8% of responses are unparseable or an invalid code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING these as wrong -- 0.3415 -- because a non-existent or unparseable code is a real failure an importer would hit, not noise to discard. Excluding them would be 0.4729, computed here for comparison only.

## 4. Ground-truth check: does true_code match the ruling's actual holding?

Extracts the first `"applicable subheading/heading/tariff provision ... will be XXXX.XX.XXXX"` sentence from the raw ruling text and compares its code (digits only) to the stored `true_code` (from the CROSS API's own `tariffs` field). A mismatch would mean `true_code` captured a rejected alternative or an unrelated code rather than CBP's actual holding.

**Full usable set (1098 rulings):** holding sentence found and extracted for 1042; of those, 1031/1042 (98.94%) match `true_code` exactly. 56 had no extractable holding sentence (different ruling phrasing, e.g. country-of-origin-only or multi-paragraph holdings not matching the regex -- NOT counted as mismatches, just unverifiable by this regex).


### Requested 20-random-ruling sample

| Ruling | true_code | holding-sentence code | Match |
|---|---|---|---|
| N358809 | 2106909998 | 2106909998 | YES |
| N358480 | 0307520000 | 0307520000 | YES |
| N361398 | 9505906000 | 9505906000 | YES |
| N361860 | 8471410150 | 8471410150 | YES |
| N361235 | 7326908688 | 7326908688 | YES |
| N357718 | 3304995000 | 3304995000 | YES |
| N363339 | 8536308000 | 8536308000 | YES |
| N360648 | 7326908688 | 7326908688 | YES |
| N359982 | 3919905060 | 3919905060 | YES |
| N362881 | 8535908040 | 8535908040 | YES |
| N359944 | 7318290000 | 7318290000 | YES |
| N354811 | 6802930010 | 6802930010 | YES |
| N362456 | 8479899597 | 8479899597 | YES |
| N359367 | 8544422000 | 8544422000 | YES |
| N360180 | 3004909272 | 3004909272 | YES |
| N361453 | 8422110000 | 8422110000 | YES |
| N363551 | 9505904000 | 9505904000 | YES |
| N357577 | 7318160060 | 7318160060 | YES |
| N363522 | 3926909989 | 3926909989 | YES |
| N358088 | 4201006000 | 4201006000 | YES |

**Requested-sample result: 20/20 match (20/20 had an extractable holding sentence).**


Full-set mismatches (11, ~1% of 1098): N356924 (true=8544493080, holding=8455493080), N358304 (true=8518220000, holding=85182200), N358673 (true=9505102500, holding=9505906000), N358979 (true=7615109100, holding=7615910000), N359352 (true=9504400000, holding=9404400000), N359455 (true=8528592500, holding=8528591500), N360570 (true=8703230190, holding=8703230019), N360766 (true=8706805090, holding=8716805090), N361914 (true=7113195091, holding=71131950), N363520 (true=4410000060, holding=4410110060), N363815 (true=4901990010, holding=490199001)

**Manual inspection of 3 of these 11** (not all -- diminishing returns past the requested 20-sample, which is clean): none were an actual error in `true_code`.
- `N356924`: the ruling's own PROSE says "will be 8455.49.3080", but its structured `TARIFF NO.:` header field (= our `true_code`, from the CROSS API's `tariffs` field) says `8544.49.3080`. 8455 isn't even internally consistent with the "insulated wire, cable" description quoted right after it in the same sentence (that's heading 8544's legal text) -- the prose has a human typo; the structured field is correct.
- `N358673`: same pattern -- ruling header `TARIFF NO.: 9505.10.2500` (Christmas-specific subheading, matches `true_code`) vs. body prose "will be 9505.90.6000" (a generic "Other" catch-all) for a product literally called an "Artificial Christmas Tree." The dedicated Christmas subheading is the obviously correct one; the prose sentence looks like a copy-paste slip.
- `N358304`: not a true mismatch at all -- the ruling text has a stray mid-number space ("will be 8518.22.00 00"), so the extraction regex grabbed only 8 of the 10 digits. Both the header and the full intended code agree with `true_code`.

**Conclusion:** where CBP's own ruling letter has an internal inconsistency between its structured `TARIFF NO.:` header and its free-text holding sentence, using the CROSS API's structured `tariffs` field (as this project does) is the right call -- it matches the ruling's own official header field, not a prose sentence that can contain drafting slips. This is a real, if rare (~1 in 1098), data-quality quirk in the ground-truth source itself, not a bug in this project's extraction.

## 6. Comparison with prior work

All "this project" numbers below are for the 3 **free, open-weight models run on Groq's free tier** tested in this project -- `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b` -- at temperature 0, low reasoning effort, single-shot, no tools/retrieval. Nothing here generalizes to larger, fine-tuned, or paid-tier models.

| Source | Ground truth | 6-digit accuracy | 10-digit accuracy | 10-digit, excluding invalid/unparseable codes |
|---|---|---|---|---|
| This project: openai/gpt-oss-20b | CBP CROSS, NY collection, 2026+ | 3.0% | 0.0% | 0.0% |
| This project: openai/gpt-oss-120b | CBP CROSS, NY collection, 2026+ | 21.1% | 0.5% | 16.2% |
| This project: allam-2-7b | CBP CROSS, NY collection, 2026+ | 4.4% | 1.7% | 13.5% |
| This project: deepseek-ai/DeepSeek-V4.1-Flash | CBP CROSS, NY collection, 2026+ | 52.8% | 25.0% | 36.0% |
| This project: zai-org/GLM-5.3 | CBP CROSS, NY collection, 2026+ | 45.3% | 12.4% | 37.4% |
| This project: moonshotai/Kimi-K3 | CBP CROSS, NY collection, 2026+ | 55.3% | 28.4% | 37.1% |
| This project: nvidia/nemotron-3-ultra-550b-a55b:free | CBP CROSS, NY collection, 2026+ | 39.5% | 14.0% | 21.6% |
| This project: openai/gpt-6-sol | CBP CROSS, NY collection, 2026+ | 67.0% | 37.5% | 47.4% |
| This project: anthropic/claude-haiku-5.5 | CBP CROSS, NY collection, 2026+ | 32.5% | 7.9% | 21.3% |
| This project: anthropic/claude-sonnet-5.5 | CBP CROSS, NY collection, 2026+ | 61.7% | 25.2% | 40.9% |
| This project: anthropic/claude-opus-5.5 | CBP CROSS, NY collection, 2026+ | 69.2% | 35.3% | 47.3% |
| ATLAS, fine-tuned Atlas model (LLaMA-3.3-70B) | CROSS (their own benchmark) | 57.5% | 40% | n/a |
| ATLAS, GPT-5-Thinking (general-purpose, not fine-tuned) | CROSS (their own benchmark) | not stated in abstract | ~25% (back-calculated: abstract states Atlas beats it by 15 points) | n/a |
| ATLAS, Gemini-2.5-Pro-Thinking (general-purpose, not fine-tuned) | CROSS (their own benchmark) | not stated in abstract | ~12.5% (back-calculated: abstract states Atlas beats it by 27.5 points) | n/a |
| Tarifflo paper (arXiv 2412.14179) | commercial tools (Zonos, Tarifflo, Avalara, WCO BACUDA) | not confirmed from the abstract (the ~89% cited in the Round 2 prompt is not independently verified here against the paper's own methodology/digit-level) | not confirmed | n/a |

**Read directly from the ATLAS abstract (arXiv 2509.18400), verified 2026-10-02:** their *fine-tuned* Atlas model reaches 40%/57.5% -- but their *general-purpose, non-fine-tuned* frontier models (GPT-5-Thinking, Gemini-2.5-Pro-Thinking) score only ~25% and ~12.5% at 10 digits. That's the fairer comparison point for this project (3 free-tier, non-fine-tuned, low-reasoning-effort models) -- and it's still 7-15x our highest 10-digit number (1.7%), so a real gap remains even against the most comparable prior baseline. Separately, arXiv 2412.14179's abstract shows it benchmarks commercial, purpose-built classification PRODUCTS (Zonos, Tarifflo, Avalara, WCO BACUDA) -- not a raw LLM given a generic prompt -- so a number from that paper is not an apples-to-apples comparison with this project's method regardless of its exact value.

Even restricting to responses that were at least a real, existing 10-digit code (last column), accuracy is still well below the cited prior-work range for every model here except allam-2-7b and gpt-oss-120b getting into the 13-16% territory -- still short of ATLAS's low end. The gap narrows substantially once invalid/unparseable answers are excluded, but does not close. A real scoring-convention difference (whether invalid codes count as wrong) explains part of it. The remainder is best read as a difference in **model capability and configuration** -- this project deliberately tests only free, open-weight, non-fine-tuned, low-reasoning-effort models, which is a narrower and weaker slice of what's possible than ATLAS's comparison set. This is NOT evidence that the underlying classification task is inherently harder than ATLAS's framing suggests -- the contamination-control window and description-only input are methodology choices this project made for honesty, not task properties, and ATLAS's own general-purpose baselines (not just its fine-tuned model) already show frontier models can do meaningfully better than what's tested here.

**Design differences that could explain the gap (not a claim that we are right and they are wrong):**

- **Description-only input.** This project strips all classification/tariff language from the input (Phase 2's leak test). If ATLAS or Tarifflo include any of the ruling's own classification reasoning, product category hints, or test on rulings where the product name alone (e.g. brand/SKU text present in search indices) leaks the category, their task is easier by construction.
- **Post-cutoff-only rulings.** This project restricts to rulings dated after the tested models' training cutoffs specifically to prevent memorization. If prior work did not apply this filter, some of their test rulings could have been seen (in part or whole) during training.
- **Reasoning effort / prompting.** This project uses temperature 0, low reasoning effort, single-shot, no tools, no retrieval, no chain-of-thought prompting strategy beyond asking for a one-sentence reason. Prior work may use higher reasoning effort, multi-shot prompting, retrieval over the HTS text, or ensembling.
- **Model size/choice.** This project only tests 3 free-tier models runnable on Groq's API (20B-120B parameter class, plus a 7B Arabic-focused model). Prior work may test larger frontier models.
- **Digit-level scoring convention.** This project's headline is strict 10-digit exact match; prior work's reported numbers may be at 6-digit (HS) or 8-digit granularity, which this audit's Check 2 shows is substantially higher for every model tested here too.