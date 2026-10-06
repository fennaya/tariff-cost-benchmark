"""
Derives the README/findings framing ratios from data/processed/analysis_results.json
(written by analysis.py). No new analysis: only divisions of counts analysis.py already
saved. Writes review/readme_shares.md so every figure quoted in the README traces to a
script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from analysis import digit_match, rate_pct_for, load_model_results  # noqa: E402
res = json.loads((ROOT / "data" / "processed" / "analysis_results.json").read_text(encoding="utf-8"))
ORDER = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b"]

lines = [
    "# Derived shares behind the README framing (from analysis_results.json)\n",
    "| Model | n answers | n wrong | invalid / all answers | invalid / wrong | wrong with usable rate (n) | usable / wrong | rate-changing (n) | underpay share |",
    "|---|---|---|---|---|---|---|---|---|",
]
for m in ORDER:
    d = res[m]
    n, w, inv, use = d["n"], d["n_wrong"], d["n_invalid_code"], d["n_wrong_with_usable_rates"]
    dt = d["direction_test"]
    lines.append(
        f"| {m} | {n} | {w} | {inv}/{n} = {inv / n:.1%} | {inv}/{w} = {inv / w:.1%} | "
        f"{use} | {use}/{w} = {use / w:.1%} | {dt['n_nonzero_diff']} | "
        f"{dt['underpay_count']}/{dt['n_nonzero_diff']} = {dt['underpay_share']:.1%} |")
lines += ["", "## Overlap: usable-rate wrong answers that are also tagged INVALID_CODE", "",
          "Only 10-digit answers get a rate (analysis.rate_pct_for). A 10-digit answer that is not in the HTS is tagged invalid but can still resolve to a rate through its 8-, 6- or 4-digit prefix, so the two groups overlap.", "",
          "| Model | wrong with usable rate | of which tagged invalid | of which valid 10-digit code |", "|---|---|---|---|"]
for m in ORDER:
    rows = load_model_results(ROOT / "llm_logs" / m)
    wrong = [r for r in rows if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
    usable = [r for r in wrong if rate_pct_for(r["true_code"], r["rulingDate"]) is not None
              and rate_pct_for(r.get("predicted_code"), r["rulingDate"]) is not None]
    inv = sum(1 for r in usable if r.get("tag") == "INVALID_CODE")
    assert len(usable) == res[m]["n_wrong_with_usable_rates"], m
    lines.append(f"| {m} | {len(usable)} | {inv} | {len(usable) - inv} |")
out = ROOT / "review" / "readme_shares.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print(f"\nWrote {out}")
