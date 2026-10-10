"""
Numbers quoted in the three-sentence plain summary at the top of README.md (GPT-6 Sol and Claude Opus 5.5).
Everything is recomputed from the cached raw responses; nothing is copied from another table.

  - 8-digit accuracy on each model's post-cutoff rulings (the README table basis) and the paired McNemar p on all 1,098
  - share of wrong answers (post-cutoff rulings) that are valid codes, and the share a "does this code exist?" check catches
  - share of invalid answers (all 1,098 rulings) that are suffix slips (FORMAT) and in which the first 8 digits equal the true code
  - share of wrong answers (post-cutoff rulings) that change the duty rate, and the median duty at stake per $100,000 (analyze_v1_1 basis)
Writes review/readme_summary_numbers.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
import analyze_v1_1 as A  # noqa: E402
from analysis import digit_match  # noqa: E402

MODELS = ["openai/gpt-6-sol", "anthropic/claude-opus-5.5"]


def main():
    fvi = json.loads((ROOT / "review" / "format_vs_invention.json").read_text(encoding="utf-8"))
    cfg = {m["model_id"]: m for m in M.analysis_models()}
    L = ["# Numbers behind the README plain summary (scripts/readme_summary_numbers.py)\n",
         "| Model | n (post-cutoff) | 8-digit correct | wrong answers | wrong answers with a valid code | wrong answers a validity check flags | wrong answers that change the duty rate | priced wrong answers | median duty at stake per $100,000 | invalid answers, all 1,098 | of those: suffix slips (FORMAT) | of those: first 8 digits equal the true code |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for mid in MODELS:
        m = cfg[mid]
        rows = A.primary_rows(m, M.load_results(mid))
        n = len(rows)
        k8 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 8))
        wrong = [r for r in rows if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
        flagged = sum(1 for r in wrong if r.get("tag") == "INVALID_CODE")
        diffs = A.comparable_diffs(rows)
        changed = sum(1 for d in diffs if abs(d[1]) > 1e-9)
        # duty at stake: |rate difference| x $100,000 on priced wrong answers (same basis as the README "median duty" sentence)
        import statistics
        med = statistics.median(abs(d[1]) * 1000 for d in diffs)
        f = fvi[mid]
        L.append(f"| {mid} | {n} | {k8} ({k8 / n:.1%}) | {len(wrong)} | {len(wrong) - flagged} ({(len(wrong) - flagged) / len(wrong):.1%}) | {flagged} ({flagged / len(wrong):.1%}) | "
                 f"{changed} ({changed / len(wrong):.1%} of wrong; {changed / len(diffs):.1%} of priced) | {len(diffs)} | ${med:,.0f} | {f['invalid']} | {f['format']} ({f['format'] / f['invalid']:.1%}) | "
                 f"{f['b_c_first8_equals_true']} ({f['b_c_first8_equals_true'] / f['invalid']:.1%} of all invalid) |")
    out = "\n".join(L) + "\n"
    (ROOT / "review" / "readme_summary_numbers.md").write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
