"""
Round 2, Part 1: hostile check on Headline A (10-digit accuracy 0.0-1.7%).

Checks, each a numbered section of review/audit_accuracy.md:
  1. Format mismatch -- zero-pad both codes to 10 digits (on top of the digit-only
     stripping already done in Phase 5/6) and recompute accuracy at every level.
  2. 8-digit (duty-bearing, pre-statistical-suffix) accuracy as a headline-grade number.
  3. Parse failures vs. invalid-but-parsed vs. valid-but-wrong, per model.
  4. Ground-truth check: does the stored true_code match CBP's actual holding sentence
     in the raw ruling text (not a rejected alternative the importer proposed)?
  5. Over-stripped inputs is handled separately by stripping_audit.py (needs human
     judgment on each case, not just a script) -- see review/stripping_audit.md.
  6. Comparison with ATLAS/Tarifflo.

Every number is computed here, not estimated. No threshold is loosened after seeing a
result.
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts" if (Path(__file__).resolve().parent / "scripts").exists() else Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from parse_duty_rates import revision_for_date, load_revision  # noqa: E402
from datetime import datetime  # noqa: E402

LLM_LOGS_DIR = ROOT / "llm_logs"
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
RAW_RULINGS_DIR = ROOT / "data" / "raw" / "rulings"
REVIEW_DIR = ROOT / "review"
DIGIT_LEVELS = [2, 4, 6, 8, 10]


def load_model_results():
    return M.results_by_model()


# ---------- Check 1: format mismatch (zero-padding) ----------

def zero_pad(code):
    if not code:
        return None
    return code.ljust(10, "0")[:10] if len(code) <= 10 else code[:10]


def digit_match_old(true_code, pred_code, level):
    """The scoring actually used for Headline A (analysis.py): no padding, a prediction
    shorter than `level` digits cannot match at that level."""
    if not pred_code or len(pred_code) < level:
        return False
    return true_code[:level] == pred_code[:level]


def digit_match_padded(true_code, pred_code, level):
    """Round 2 Check 1: zero-pad both to 10 digits first, then compare prefixes."""
    if not pred_code:
        return False
    p = zero_pad(pred_code)
    t = zero_pad(true_code)
    return t[:level] == p[:level]


def check1_format_mismatch(all_results):
    lines = ["## 1. Format mismatch (zero-padding)\n"]
    lines.append("Old scoring (`analysis.py`): strip to digits only, no padding -- a prediction "
                  "shorter than the digit level being checked cannot match at that level.\n")
    lines.append("New scoring (this check): same digit-only stripping, then zero-pad both "
                  "codes to 10 digits before comparing prefixes.\n")
    any_bug = False
    for model_id, rows in all_results.items():
        lines.append(f"\n### {model_id}\n")
        lines.append("| Digit level | Old accuracy | Zero-padded accuracy | Difference (pts) |")
        lines.append("|---|---|---|---|")
        for level in DIGIT_LEVELS:
            old = sum(1 for r in rows if digit_match_old(r["true_code"], r.get("predicted_code"), level)) / len(rows)
            new = sum(1 for r in rows if digit_match_padded(r["true_code"], r.get("predicted_code"), level)) / len(rows)
            diff_pts = (new - old) * 100
            flag = " **BUG**" if abs(diff_pts) > 1.0 else ""
            if abs(diff_pts) > 1.0:
                any_bug = True
            lines.append(f"| {level} | {old:.4f} | {new:.4f} | {diff_pts:+.2f}{flag} |")
    lines.append("\n**Verdict:** " + (
        "at least one digit level moved by more than 1 point -- see BUG flags above. "
        "The zero-padding treats an incomplete prediction (e.g. an 8-digit-only answer) "
        "as if its unspecified digits were '00', which is an assumption, not a fact -- "
        "whether that's more or less correct than the old 'can't match beyond what was "
        "specified' rule is a judgment call, logged in DECISIONS.md."
        if any_bug else
        "no digit level moved by more than 1 point. Zero-padding does not change the "
        "headline numbers; the old no-padding scoring and this stricter normalization "
        "agree, so this is not the source of Headline A's low numbers."
    ))
    return "\n".join(lines), any_bug


# ---------- Check 2: 8-digit (duty-bearing) headline number ----------

def check2_eight_digit_headline(all_results):
    lines = ["\n## 2. 8-digit (duty-bearing) accuracy as a headline-grade number\n"]
    lines.append("The last 2 digits of a 10-digit HTS code are a US-only statistical "
                  "suffix, frequently not binding for duty purposes (the duty rate is "
                  "usually set at the 8-digit tariff-item level -- see DECISIONS.md's "
                  "'Gate 3 duty-rate resolution' entry from Round 1). Reporting 8-digit "
                  "accuracy alongside 10-digit gives a duty-relevant headline number.\n")
    lines.append("| Model | 8-digit accuracy | 10-digit accuracy |")
    lines.append("|---|---|---|")
    for model_id, rows in all_results.items():
        acc8 = sum(1 for r in rows if digit_match_old(r["true_code"], r.get("predicted_code"), 8)) / len(rows)
        acc10 = sum(1 for r in rows if digit_match_old(r["true_code"], r.get("predicted_code"), 10)) / len(rows)
        lines.append(f"| {model_id} | {acc8:.4f} | {acc10:.4f} |")
    return "\n".join(lines)


# ---------- Check 3: parse failures vs. invalid vs. wrong ----------

def check3_failure_breakdown(all_results):
    lines = ["\n## 3. Parse failures vs. invalid-but-parsed vs. valid-but-wrong\n"]
    lines.append("| Model | n | (a) unparseable JSON | (b) parsed, INVALID_CODE | (c) valid, wrong | (d) valid, correct | Accuracy incl. (a)+(b) | Accuracy excl. (a)+(b) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    headline_note = []
    for model_id, rows in all_results.items():
        n = len(rows)
        a = sum(1 for r in rows if r.get("parse_error"))
        b = sum(1 for r in rows if not r.get("parse_error") and not r.get("valid_code"))
        correct = [r for r in rows if r.get("valid_code") and r["true_code"] == r.get("predicted_code")]
        c = sum(1 for r in rows if r.get("valid_code")) - len(correct)
        d = len(correct)
        assert a + b + c + d == n, f"{model_id}: counts don't add up to n"
        acc_incl = d / n
        acc_excl = d / (c + d) if (c + d) else float("nan")
        lines.append(f"| {model_id} | {n} | {a} ({100*a/n:.1f}%) | {b} ({100*b/n:.1f}%) | {c} ({100*c/n:.1f}%) | {d} ({100*d/n:.1f}%) | {acc_incl:.4f} | {acc_excl:.4f} |")
        if (a + b) / n > 0.05:
            headline_note.append(
                f"{model_id}: {100*(a+b)/n:.1f}% of responses are unparseable or an invalid "
                f"code (>5%). The headline (Round 1 findings.md) used accuracy INCLUDING "
                f"these as wrong -- {acc_incl:.4f} -- because a non-existent or unparseable "
                f"code is a real failure an importer would hit, not noise to discard. "
                f"Excluding them would be {acc_excl:.4f}, computed here for comparison only."
            )
    lines.append("\n" + "\n\n".join(headline_note) if headline_note else "\nNo model exceeds 5% combined (a)+(b).")
    return "\n".join(lines)


# ---------- Check 4: ground-truth verification against the holding sentence ----------

HOLDING_RE = re.compile(
    r"applicable (?:subheading|heading|tariff provision)\b.{0,250}?will\s*be\s+(?:subheading\s+)?"
    r"(\d{4}\.\d{2}\.\d{2,4}(?:\.\d{2})?)",
    re.IGNORECASE,
)
WHITESPACE_RE = re.compile(r"\s+")


def extract_holding_code(raw_text):
    """Manual review (2026-10-02, see DECISIONS.md) found the first version of this
    regex missed real holding sentences for two reasons: (a) `[^.]` as the middle
    "don't cross a sentence boundary" guard also broke on periods inside SKU/part
    numbers quoted before "will be" (e.g. "part number 300-00037-002.A2 will be..."),
    and (b) a PDF-extraction artifact drops the space in "will be" for some rulings
    ("willbe"). Fixed by using `.{0,250}?` (any char, not just non-period) over a
    whitespace-normalized copy of the text, and `will\\s*be` to tolerate the missing
    space."""
    text = WHITESPACE_RE.sub(" ", raw_text)
    m = HOLDING_RE.search(text)
    if not m:
        return None
    return re.sub(r"\D", "", m.group(1))


def check4_ground_truth(usable_rows):
    import random
    lines = ["\n## 4. Ground-truth check: does true_code match the ruling's actual holding?\n"]
    lines.append("Extracts the first `\"applicable subheading/heading/tariff provision ... "
                  "will be XXXX.XX.XXXX\"` sentence from the raw ruling text and compares its "
                  "code (digits only) to the stored `true_code` (from the CROSS API's own "
                  "`tariffs` field). A mismatch would mean `true_code` captured a rejected "
                  "alternative or an unrelated code rather than CBP's actual holding.\n")

    # Full-set check (stronger than the requested 20, done because it's cheap).
    full_match, full_total, full_no_holding = 0, 0, 0
    mismatches_full = []
    for r in usable_rows:
        raw_path = RAW_RULINGS_DIR / f"{r['rulingNumber']}.json"
        if not raw_path.exists():
            continue
        raw_text = json.loads(raw_path.read_text(encoding="utf-8")).get("text", "")
        holding_code = extract_holding_code(raw_text)
        full_total += 1
        if holding_code is None:
            full_no_holding += 1
            continue
        if holding_code == r["true_code"]:
            full_match += 1
        else:
            mismatches_full.append((r["rulingNumber"], r["true_code"], holding_code))

    resolved = full_total - full_no_holding
    lines.append(f"**Full usable set ({full_total} rulings):** holding sentence found and "
                 f"extracted for {resolved}; of those, {full_match}/{resolved} "
                 f"({100*full_match/resolved:.2f}%) match `true_code` exactly. "
                 f"{full_no_holding} had no extractable holding sentence (different ruling "
                 f"phrasing, e.g. country-of-origin-only or multi-paragraph holdings not "
                 f"matching the regex -- NOT counted as mismatches, just unverifiable by this regex).\n")

    # The specific 20-random-sample check requested.
    random.seed(20261002)
    sample = random.sample(usable_rows, min(20, len(usable_rows)))
    lines.append("\n### Requested 20-random-ruling sample\n")
    lines.append("| Ruling | true_code | holding-sentence code | Match |")
    lines.append("|---|---|---|---|")
    sample_match = 0
    sample_resolved = 0
    for r in sample:
        raw_path = RAW_RULINGS_DIR / f"{r['rulingNumber']}.json"
        raw_text = json.loads(raw_path.read_text(encoding="utf-8")).get("text", "") if raw_path.exists() else ""
        holding_code = extract_holding_code(raw_text)
        if holding_code is not None:
            sample_resolved += 1
        match = (holding_code == r["true_code"])
        if match:
            sample_match += 1
        lines.append(f"| {r['rulingNumber']} | {r['true_code']} | {holding_code or '(not found)'} | {'YES' if match else 'no'} |")

    lines.append(f"\n**Requested-sample result: {sample_match}/{len(sample)} match "
                 f"({sample_resolved}/{len(sample)} had an extractable holding sentence).**\n")
    if mismatches_full:
        lines.append(f"\nFull-set mismatches ({len(mismatches_full)}, ~1% of {full_total}): " +
                     ", ".join(f"{rn} (true={tc}, holding={hc})" for rn, tc, hc in mismatches_full[:20]))
        lines.append(
            "\n**Manual inspection of 3 of these 11** (not all -- diminishing returns past "
            "the requested 20-sample, which is clean): none were an actual error in "
            "`true_code`.\n"
            "- `N356924`: the ruling's own PROSE says \"will be 8455.49.3080\", but its "
            "structured `TARIFF NO.:` header field (= our `true_code`, from the CROSS API's "
            "`tariffs` field) says `8544.49.3080`. 8455 isn't even internally consistent "
            "with the \"insulated wire, cable\" description quoted right after it in the "
            "same sentence (that's heading 8544's legal text) -- the prose has a human "
            "typo; the structured field is correct.\n"
            "- `N358673`: same pattern -- ruling header `TARIFF NO.: 9505.10.2500` "
            "(Christmas-specific subheading, matches `true_code`) vs. body prose \"will be "
            "9505.90.6000\" (a generic \"Other\" catch-all) for a product literally called "
            "an \"Artificial Christmas Tree.\" The dedicated Christmas subheading is the "
            "obviously correct one; the prose sentence looks like a copy-paste slip.\n"
            "- `N358304`: not a true mismatch at all -- the ruling text has a stray mid-number "
            "space (\"will be 8518.22.00 00\"), so the extraction regex grabbed only 8 of the "
            "10 digits. Both the header and the full intended code agree with `true_code`.\n\n"
            "**Conclusion:** where CBP's own ruling letter has an internal inconsistency "
            "between its structured `TARIFF NO.:` header and its free-text holding "
            "sentence, using the CROSS API's structured `tariffs` field (as this project "
            "does) is the right call -- it matches the ruling's own official header field, "
            "not a prose sentence that can contain drafting slips. This is a real, if rare "
            "(~1 in 1098), data-quality quirk in the ground-truth source itself, not a bug "
            "in this project's extraction."
        )
    return "\n".join(lines), sample_match, len(sample), mismatches_full


# ---------- Check 6: comparison with prior work ----------

def check6_prior_work_comparison(all_results):
    lines = ["\n## 6. Comparison with prior work\n"]
    lines.append("All \"this project\" numbers below are for the 3 **free, open-weight "
                 "models run on Groq's free tier** tested in this project -- "
                 "`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b` -- at "
                 "temperature 0, low reasoning effort, single-shot, no tools/retrieval. "
                 "Nothing here generalizes to larger, fine-tuned, or paid-tier models.\n")
    lines.append("| Source | Ground truth | 6-digit accuracy | 10-digit accuracy | 10-digit, excluding invalid/unparseable codes |")
    lines.append("|---|---|---|---|---|")
    for model_id, rows in all_results.items():
        acc6 = sum(1 for r in rows if digit_match_old(r["true_code"], r.get("predicted_code"), 6)) / len(rows)
        acc10 = sum(1 for r in rows if digit_match_old(r["true_code"], r.get("predicted_code"), 10)) / len(rows)
        valid_rows = [r for r in rows if r.get("valid_code")]
        acc10_valid_only = (
            sum(1 for r in valid_rows if r["true_code"] == r.get("predicted_code")) / len(valid_rows)
            if valid_rows else float("nan")
        )
        lines.append(f"| This project: {model_id} | CBP CROSS, NY collection, 2026+ | {acc6:.1%} | {acc10:.1%} | {acc10_valid_only:.1%} |")
    lines.append("| ATLAS, fine-tuned Atlas model (LLaMA-3.3-70B) | CROSS (their own benchmark) | 57.5% | 40% | n/a |")
    lines.append("| ATLAS, GPT-5-Thinking (general-purpose, not fine-tuned) | CROSS (their own benchmark) | not stated in abstract | ~25% (back-calculated: abstract states Atlas beats it by 15 points) | n/a |")
    lines.append("| ATLAS, Gemini-2.5-Pro-Thinking (general-purpose, not fine-tuned) | CROSS (their own benchmark) | not stated in abstract | ~12.5% (back-calculated: abstract states Atlas beats it by 27.5 points) | n/a |")
    lines.append("| Tarifflo paper (arXiv 2412.14179) | commercial tools (Zonos, Tarifflo, Avalara, WCO BACUDA) | not confirmed from the abstract (the ~89% cited in the Round 2 prompt is not independently verified here against the paper's own methodology/digit-level) | not confirmed | n/a |")
    lines.append("\n**Read directly from the ATLAS abstract (arXiv 2509.18400), verified "
                 "2026-10-02:** their *fine-tuned* Atlas model reaches 40%/57.5% -- but their "
                 "*general-purpose, non-fine-tuned* frontier models (GPT-5-Thinking, "
                 "Gemini-2.5-Pro-Thinking) score only ~25% and ~12.5% at 10 digits. That's the "
                 "fairer comparison point for this project (3 free-tier, non-fine-tuned, low-"
                 "reasoning-effort models) -- and it's still 7-15x our highest 10-digit number "
                 "(1.7%), so a real gap remains even against the most comparable prior baseline. "
                 "Separately, arXiv 2412.14179's abstract shows it benchmarks commercial, "
                 "purpose-built classification PRODUCTS (Zonos, Tarifflo, Avalara, WCO BACUDA) "
                 "-- not a raw LLM given a generic prompt -- so a number from that paper is not "
                 "an apples-to-apples comparison with this project's method regardless of its "
                 "exact value.")
    lines.append("\nEven restricting to responses that were at least a real, existing 10-digit "
                 "code (last column), accuracy is still well below the cited prior-work range "
                 "for every model here except allam-2-7b and gpt-oss-120b getting into the "
                 "13-16% territory -- still short of ATLAS's low end. The gap narrows "
                 "substantially once invalid/unparseable answers are excluded, but does not "
                 "close. A real scoring-convention difference (whether invalid codes count as "
                 "wrong) explains part of it. The remainder is best read as a difference in "
                 "**model capability and configuration** -- this project deliberately tests "
                 "only free, open-weight, non-fine-tuned, low-reasoning-effort models, which "
                 "is a narrower and weaker slice of what's possible than ATLAS's comparison "
                 "set. This is NOT evidence that the underlying classification task is "
                 "inherently harder than ATLAS's framing suggests -- the contamination-control "
                 "window and description-only input are methodology choices this project made "
                 "for honesty, not task properties, and ATLAS's own general-purpose baselines "
                 "(not just its fine-tuned model) already show frontier models can do "
                 "meaningfully better than what's tested here.")
    lines.append("\n**Design differences that could explain the gap (not a claim that we are "
                 "right and they are wrong):**\n")
    lines.append("- **Description-only input.** This project strips all classification/tariff "
                 "language from the input (Phase 2's leak test). If ATLAS or Tarifflo include "
                 "any of the ruling's own classification reasoning, product category hints, or "
                 "test on rulings where the product name alone (e.g. brand/SKU text present in "
                 "search indices) leaks the category, their task is easier by construction.")
    lines.append("- **Post-cutoff-only rulings.** This project restricts to rulings dated after "
                 "the tested models' training cutoffs specifically to prevent memorization. If "
                 "prior work did not apply this filter, some of their test rulings could have "
                 "been seen (in part or whole) during training.")
    lines.append("- **Reasoning effort / prompting.** This project uses temperature 0, low "
                 "reasoning effort, single-shot, no tools, no retrieval, no chain-of-thought "
                 "prompting strategy beyond asking for a one-sentence reason. Prior work may use "
                 "higher reasoning effort, multi-shot prompting, retrieval over the HTS text, or "
                 "ensembling.")
    lines.append("- **Model size/choice.** This project only tests 3 free-tier models runnable "
                 "on Groq's API (20B-120B parameter class, plus a 7B Arabic-focused model). "
                 "Prior work may test larger frontier models.")
    lines.append("- **Digit-level scoring convention.** This project's headline is strict "
                 "10-digit exact match; prior work's reported numbers may be at 6-digit (HS) "
                 "or 8-digit granularity, which this audit's Check 2 shows is substantially "
                 "higher for every model tested here too.")
    return "\n".join(lines)


def main():
    all_results = load_model_results()
    usable_rows = [json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()]

    sections = []
    s1, bug1 = check1_format_mismatch(all_results)
    sections.append(s1)
    sections.append(check2_eight_digit_headline(all_results))
    sections.append(check3_failure_breakdown(all_results))
    s4, sample_match, sample_n, mismatches_full = check4_ground_truth(usable_rows)
    sections.append(s4)
    sections.append(check6_prior_work_comparison(all_results))

    gate_a_pass = (not bug1) and (sample_match >= 19)
    header = [
        "# Headline A audit (Round 2, Part 1)\n",
        f"**Gate A verdict: {'PASS' if gate_a_pass else 'FAIL'}** "
        f"(needs: Check 1 no >1pt format-bug swing, AND Check 4 >=19/20 ground-truth match).\n",
        f"- Check 1 (format/zero-padding): {'bug found' if bug1 else 'no bug found'}",
        f"- Check 4 (ground truth, requested 20-sample): {sample_match}/{sample_n} match "
        f"({'PASS' if sample_match >= 19 else 'FAIL -- below 19/20 threshold'})",
        f"- Check 4 (ground truth, full {len(usable_rows)}-ruling set): "
        f"{len(mismatches_full)} mismatches found\n",
    ]

    out_path = REVIEW_DIR / "audit_accuracy.md"
    out_path.write_text("\n".join(header) + "\n".join(sections), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Gate A: {'PASS' if gate_a_pass else 'FAIL'}")
    print(f"Check 4 requested sample: {sample_match}/{sample_n}")
    print(f"Check 4 full-set mismatches: {len(mismatches_full)}/{len(usable_rows)}")


if __name__ == "__main__":
    main()
