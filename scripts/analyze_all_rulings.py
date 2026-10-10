"""
v1.2 post-hoc addition (no API calls): every model scored on ALL rulings it answered, next to its
post-cutoff (headline) numbers, with the same code as the main tables: 8-digit accuracy with Wilson 95% CI,
invalid share, underpay share with n and Gate B (analyze_v1_1.gate_b, pre-registered rule: beats Baseline 2
at permutation p < 0.05 with n >= 30 rate-changing errors).

All-ruling scores include rulings that may be in a model's training data, so they are upper bounds.
Replication runs (role "replication") are listed in a separate block. Writes review/all_rulings.md and .json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
import analyze_v1_1 as A  # noqa: E402
from analysis import digit_match, wilson_ci  # noqa: E402


def stats(m, rows):
    n = len(rows)
    k8 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 8))
    inv = sum(1 for r in rows if r.get("tag") == "INVALID_CODE")
    g = A.gate_b(rows)
    gv = "too few cases" if g["n"] < 30 else ("met" if g["verdict"].startswith("underpays") else "not met")
    lo, hi = wilson_ci(k8, n)
    return {"n": n, "k8": k8, "acc8": k8 / n, "ci": [max(0.0, lo), hi], "invalid": inv, "invalid_share": inv / n,
            "gate_n": g["n"], "under": g.get("under"), "under_share": g.get("share"), "p_baseline2": g.get("p2"), "gate_b": gv}


def cells(s):
    return (f"{s['n']:,} | {s['acc8']:.1%} ({s['ci'][0]:.1%} to {s['ci'][1]:.1%}) | {s['invalid_share']:.1%} | "
            f"{s['under_share']:.1%} (n = {s['gate_n']}) | {s['gate_b']}")


def main():
    res = {}
    for m in M.analysis_models(include_replication=True):
        rows = M.load_results(m["model_id"])
        res[m["model_id"]] = {"role": m.get("role", "main"), "all": stats(m, rows), "post": stats(m, A.primary_rows(m, rows))}
        res[m["model_id"]]["cutoff_status"] = A.cutoff_info(m)[1]
    hdr = ("| Model | n (post-cutoff) | 8-digit | Invalid | Underpay (n) | Gate B | n (all) | 8-digit, all rulings | Invalid, all | Underpay (n), all | Gate B, all | 8-digit difference (all minus post-cutoff, points) |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|---|")

    def block(role_main):
        out = []
        for mid, r in res.items():
            if (r["role"] != "replication") != role_main:
                continue
            same = r["all"]["n"] == r["post"]["n"]
            out.append(f"| {mid} | {cells(r['post'])} | {cells(r['all'])}{' (same rows)' if same else ''} | {(r['all']['acc8'] - r['post']['acc8']) * 100:+.1f} |")
        return hdr + "\n" + "\n".join(out)

    md = ["# All-ruling scores next to post-cutoff scores (scripts/analyze_all_rulings.py)\n",
          "Post hoc, no API calls. 'post-cutoff' = the headline basis (rulings after the model's vendor-stated cutoff; all rulings the model answered when no cutoff is stated); "
          "'all' = every ruling the model answered, including rulings that may be in training data, so read the 'all' columns as upper bounds. "
          "8-digit accuracy has Wilson 95% CIs. Underpay = share of rate-changing errors that underpay; Gate B uses the pre-registered rule (permutation p < 0.05 against Baseline 2 and n >= 30). "
          "For models with no stated cutoff, or with a cutoff before the first ruling, both blocks are the same rows.\n",
          "## Main-table models\n", block(True), "\n## Provider replication runs (OpenRouter, Baseten excluded; not in any main table)\n", block(False), ""]
    (ROOT / "review" / "all_rulings.md").write_text("\n".join(md), encoding="utf-8")
    (ROOT / "review" / "all_rulings.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
