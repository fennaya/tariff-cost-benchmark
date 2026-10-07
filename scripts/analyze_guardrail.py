"""
Guardrail test results (Groq models, fixed 200-ruling sample). "Before" = each model's
first answers. "After" = the same answers, except where the first answer was invalid, in
which case the answer from the single follow-up turn replaces it (whatever it is, valid
or not). Accuracy uses the project's digit-prefix scoring (analysis.digit_match).
Writes review/guardrail.md and review/guardrail.json.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts" if (Path(__file__).resolve().parent / "scripts").exists() else Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from analysis import digit_match  # noqa: E402

MODELS = [m for m in M.model_ids() if (ROOT / "llm_followups" / M.dir_name(M.by_id(m))).exists()]


def main():
    ids = [r["rulingNumber"] for r in csv.DictReader((ROOT / "data" / "gemini_subset.csv").open(encoding="utf-8"))]
    res, L = {}, ["# Guardrail test: one follow-up turn after an invalid first answer\n",
                  f"{len(ids)} rulings (data/gemini_subset.csv), Groq models only. Follow-up text: "
                  "\"That code does not exist in the current HTS. Give a valid 10-digit code.\"\n",
                  "| Model | invalid first answers | follow-up valid code (fixed) | fixed and correct (10-digit) | still invalid | 8-digit acc before | 8-digit acc after | 10-digit acc before | 10-digit acc after |",
                  "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        before, after = [], []
        n_inv = fixed = fixed_correct = still = n_http_err = 0
        for rn in ids:
            first = json.loads((M.path_for(m) / f"{rn}.json").read_text(encoding="utf-8"))
            before.append(first)
            if first["tag"] != "INVALID_CODE":
                after.append(first)
                continue
            n_inv += 1
            fu = json.loads((ROOT / "llm_followups" / M.dir_name(M.by_id(m)) / f"{rn}.json").read_text(encoding="utf-8"))
            after.append(fu)
            if fu["valid_code"]:
                fixed += 1
                if digit_match(fu["true_code"], fu["predicted_code"], 10):
                    fixed_correct += 1
            else:
                still += 1
                if (fu.get("parse_error") or "").startswith("http_400"):
                    n_http_err += 1
        n = len(ids)
        def acc(rows, lvl): return sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), lvl))
        d = {"n": n, "invalid_first": n_inv, "fixed_valid": fixed, "fixed_and_correct10": fixed_correct,
             "still_invalid": still, "no_answer_http_400": n_http_err,
             "acc8_before": acc(before, 8), "acc8_after": acc(after, 8),
             "acc10_before": acc(before, 10), "acc10_after": acc(after, 10)}
        res[m] = d
        L.append(f"| {m} | {n_inv} of {n} | {fixed} ({fixed / n_inv:.1%}) | {fixed_correct} | {still} ({still / n_inv:.1%}) | "
                 f"{d['acc8_before']}/{n} ({d['acc8_before'] / n:.1%}) | {d['acc8_after']}/{n} ({d['acc8_after'] / n:.1%}) | "
                 f"{d['acc10_before']}/{n} ({d['acc10_before'] / n:.1%}) | {d['acc10_after']}/{n} ({d['acc10_after'] / n:.1%}) |")
    L.append("")
    L.append("Still-invalid counts include follow-ups that returned no answer at all because the request failed with HTTP 400 (context window exceeded): " + ", ".join(f"{m}: {res[m]['no_answer_http_400']}" for m in MODELS) + ".")
    (ROOT / "review" / "guardrail.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    (ROOT / "review" / "guardrail.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
