"""
v1.2 self-check: recompute every number in the README model table from the raw cached responses,
independently of analysis.py's saved outputs. For each model, the raw response text is re-parsed
with parse_prediction, code validity is re-checked against the HTS release for the ruling date,
and rows are restricted to the model's own post-cutoff rulings (all rulings if no stated cutoff).
Then 8-digit accuracy, invalid share, rate-changing n and underpay share (Gate B code from
analyze_v1_1) are compared with the README table. Exits non-zero on any mismatch.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
from analysis import digit_match  # noqa: E402
from run_llm_classification import parse_prediction, code_is_valid  # noqa: E402
import analyze_v1_1 as A  # noqa: E402


def recompute(m):
    rows = []
    for fp in sorted(M.model_dir(m).glob("*.json")):
        r = json.loads(fp.read_text(encoding="utf-8"))
        content = r["raw_response"]["choices"][0]["message"].get("content")
        digits, _, err = parse_prediction(content)
        if r["raw_response"]["choices"][0].get("finish_reason") == "length":
            digits, err = None, "truncated"
        valid = False if err else code_is_valid(digits, r["rulingDate"])
        rows.append({**r, "predicted_code": digits, "tag": None if (not err and valid) else "INVALID_CODE"})
    return rows


def main():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    table = [l for l in readme.split("\n") if l.startswith("| ") and "Rulings scored" not in l and "---" not in l]
    by_short = {}
    for l in table:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) == 7:
            by_short[cells[0].replace(" †", "")] = cells
    bad = checked = 0
    for m in M.analysis_models():
        short = m["model_id"].split("/")[-1].replace(":free", "")
        cells = by_short.get(short)
        if cells is None:
            print(f"README has no row for {short}")
            bad += 1
            continue
        rows = A.primary_rows(m, recompute(m))
        n = len(rows)
        k8 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 8))
        inv = sum(1 for r in rows if r["tag"] == "INVALID_CODE")
        g = A.gate_b(rows)
        want = {"n": f"{n:,}", "acc8": f"{k8 / n:.1%}", "inv": f"{inv / n:.1%}", "under": f"{g['share']:.1%} (n = {g['n']})"}
        got = {"n": cells[1], "acc8": cells[2].split(" ")[0], "inv": cells[3], "under": cells[5]}
        for k in want:
            checked += 1
            if want[k] != got[k]:
                bad += 1
                print(f"MISMATCH {short} {k}: recomputed {want[k]!r} vs README {got[k]!r}")
        print(f"checked {short}: n={n}, 8-digit {k8 / n:.1%}, invalid {inv / n:.1%}, underpay {g['share']:.1%} (n = {g['n']})")
    print(f"\n{checked} README table values recomputed from raw responses; mismatches: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
