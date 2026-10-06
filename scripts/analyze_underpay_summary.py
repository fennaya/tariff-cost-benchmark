"""
Underpay result with its sample size: per model, n of rate-changing errors, underpay share
with a Wilson 95% CI, the exact binomial p against a 50% split, and the permutation p
against the matched-depth baseline (Baseline 2) and heading baseline (Baseline 1) using the
same seeds and code as audit_direction.py. Reporting rule: "significant" is allowed only for
a model with n >= 30; otherwise the text is "same direction, too few cases to confirm (n = X)".
Writes review/underpay_summary.md/.json.
"""
import json
import sys
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from analysis import load_model_results, wilson_ci  # noqa: E402
from audit_direction import (  # noqa: E402
    SEED, build_wrong_cases, observed_underpay_share, run_baseline, permutation_test, format_p,
)

MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b"]
MIN_N = 30


def main():
    res = {}
    L = ["# Underpay result with sample sizes (scripts/analyze_underpay_summary.py)\n",
         f"Rule: the word \"significant\" is used only for models with n >= {MIN_N} rate-changing errors.\n",
         "| Model | n rate-changing errors | underpaid | underpay share (Wilson 95% CI) | binomial p vs 50% | p vs Baseline 1 (heading) | p vs Baseline 2 (matched depth) | wording |",
         "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        rows = load_model_results(ROOT / "llm_logs" / m)
        cases = build_wrong_cases(rows)
        observed, n, _ = observed_underpay_share(cases)
        under = round(observed * n)
        lo, hi = wilson_ci(under, n)
        p_bin = stats.binomtest(under, n, 0.5, alternative="two-sided").pvalue
        p1, f1 = permutation_test(observed, run_baseline(cases, lambda c: 4, seed=SEED))
        p2, f2 = permutation_test(observed, run_baseline(cases, lambda c: c["match_level"], seed=SEED + 1))
        if n >= MIN_N:
            wording = ("significantly more than the matched-depth baseline" if p2 < 0.05
                       else "not significantly different from the matched-depth baseline")
        else:
            wording = f"same direction, too few cases to confirm (n = {n})"
        res[m] = {"n": n, "underpaid": under, "share": observed, "wilson": [lo, hi], "binomial_p": p_bin,
                  "p_baseline1": format_p(p1, f1), "p_baseline2": format_p(p2, f2), "wording": wording}
        L.append(f"| {m} | {n} | {under} | {observed:.1%} ({lo:.1%} to {hi:.1%}) | {p_bin:.4f} | {format_p(p1, f1)} | {format_p(p2, f2)} | {wording} |")
    (ROOT / "review" / "underpay_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (ROOT / "review" / "underpay_summary.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
