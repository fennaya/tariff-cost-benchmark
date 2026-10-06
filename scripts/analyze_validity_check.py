"""
What a validity check (does the answer exist as a 10-digit code in the HTS at the ruling
date?) would catch, per model, on all 1,098 usable rulings. "Wrong" = not the 10-digit true
code. "Flagged" = tagged INVALID_CODE (unparseable, or not a 10-digit entry in the HTS).
  detection rate   = wrong answers flagged / wrong answers
  false-flag rate  = correct answers flagged / correct answers
Also reported for 8-digit-correct answers (the duty-relevant level), since an answer can
match the true code's first 8 digits and still be flagged for its suffix.
Writes review/validity_check.md/.json. The retry result is in review/guardrail.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from analysis import digit_match, load_model_results, wilson_ci  # noqa: E402

MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b"]


def main():
    res = {}
    L = ["# What a validity check would flag (scripts/analyze_validity_check.py)\n",
         "| Model | wrong answers | wrong and flagged (detection rate, Wilson 95% CI) | wrong but not flagged (valid wrong code) | correct answers (10-digit) | correct and flagged (false-flag rate) | 8-digit-correct answers | 8-digit-correct and flagged |",
         "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        rows = load_model_results(ROOT / "llm_logs" / m)
        flagged = lambda r: r.get("tag") == "INVALID_CODE"
        wrong = [r for r in rows if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
        right = [r for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 10)]
        r8 = [r for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 8)]
        wf = sum(1 for r in wrong if flagged(r))
        rf = sum(1 for r in right if flagged(r))
        r8f = sum(1 for r in r8 if flagged(r))
        lo, hi = wilson_ci(wf, len(wrong))
        res[m] = {"wrong": len(wrong), "wrong_flagged": wf, "wrong_unflagged": len(wrong) - wf,
                  "correct10": len(right), "correct10_flagged": rf, "correct8": len(r8), "correct8_flagged": r8f,
                  "detection_wilson": [lo, hi]}
        ff = f"{rf} of {len(right)} ({rf / len(right):.1%})" if right else "n/a (0 correct)"
        L.append(f"| {m} | {len(wrong)} | {wf} ({wf / len(wrong):.1%}; {lo:.1%} to {hi:.1%}) | {len(wrong) - wf} | {len(right)} | {ff} | {len(r8)} | {r8f} of {len(r8)} ({r8f / len(r8):.1%}) |")
    (ROOT / "review" / "validity_check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (ROOT / "review" / "validity_check.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
