"""
Round 2, Task 1, step 5 (redo): fair 4-way comparison (the 3 Groq models + Gemini)
restricted to the FIXED 200-ruling subset (data/gemini_subset.csv), not the full
661-ruling eligible pool -- Gemini is only ever run on the 200, so comparing the Groq
models against the full 661 would understate Gemini's apparent coverage and isn't the
same population. See DECISIONS.md, 2026-10-05.

The 3 Groq models were already run on ALL 1,098 usable rulings in Phase 5, so "re-report
them on the same 200" means re-analyzing their EXISTING cached results filtered down to
the subset's ruling IDs -- no new API calls needed, only Gemini required new calls (it
was only ever run on this subset to begin with).

Also runs Gate B's baseline comparison for all 4 models on this subset, reusing
audit_direction.py's RevisionPool/baseline machinery.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts" if (Path(__file__).resolve().parent / "scripts").exists() else Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from parse_duty_rates import revision_for_date, load_revision, classify_rate, resolve_rate  # noqa: E402
from run_gemini_classification import SUBSET_PATH, MODEL_ID as GEMINI_MODEL_ID  # noqa: E402
from audit_direction import (  # noqa: E402
    get_pool, build_wrong_cases, observed_underpay_share, run_baseline, permutation_test,
    format_p, deepest_match_level,
)

LLM_LOGS_DIR = ROOT / "llm_logs"
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
REVIEW_DIR = ROOT / "review"
DIGIT_LEVELS = [8, 6, 10]  # 8-digit headline first, per the project's own convention
GROQ_MODELS = [m["model_id"] for m in M.load() if m["provider"] == "groq"]


def digit_match(true_code, pred_code, level):
    if not pred_code or len(pred_code) < level:
        return False
    return true_code[:level] == pred_code[:level]


def load_model_rows(model_id, subset_ids):
    d = M.path_for(model_id)
    if not d.exists():
        return []
    rows = [json.loads(fp.read_text(encoding="utf-8")) for fp in d.glob("*.json")]
    return [r for r in rows if r["rulingNumber"] in subset_ids]


def main():
    usable = [json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()]
    if not SUBSET_PATH.exists():
        raise FileNotFoundError(
            f"{SUBSET_PATH} not found -- run scripts/build_gemini_subset.py first.")
    with SUBSET_PATH.open(encoding="utf-8") as f:
        subset_ids = {row["rulingNumber"] for row in csv.DictReader(f)}
    subset = [r for r in usable if r["rulingNumber"] in subset_ids]
    print(f"Fair-comparison subset: {len(subset)}/{len(usable)} usable rulings "
          f"(fixed 200-ruling sample, {SUBSET_PATH.name})")

    all_models = GROQ_MODELS + [GEMINI_MODEL_ID]
    lines = [
        "# 4-way fair comparison: 3 Groq models + Gemini (Round 2, Task 1)\n",
        f"All 4 models compared on the SAME fixed {len(subset)}-ruling random sample "
        f"(seed 20261005, drawn from usable rulings dated on/after Gemini's training "
        f"cutoff -- see data/gemini_subset.csv and scripts/build_gemini_subset.py). The 3 "
        f"Groq models' numbers here are a re-analysis of their existing Phase 5 cached "
        f"results filtered to this subset -- not a new run. Gemini was only ever run on "
        f"this subset.\n",
    ]

    gate_b_rows = []
    acc_rows = {}
    for model_id in all_models:
        rows = load_model_rows(model_id, subset_ids)
        n = len(rows)
        acc_rows[model_id] = {"n": n, "rows": rows}
        if n == 0:
            print(f"  {model_id}: 0 rows found yet (Gemini run may still be in progress)")
            continue

        accs = {level: sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), level)) / n
                for level in DIGIT_LEVELS}
        invalid = sum(1 for r in rows if r.get("tag") == "INVALID_CODE")
        print(f"  {model_id}: n={n}, 8-digit acc={accs[8]:.3f}, invalid={invalid}/{n}")

        cases = build_wrong_cases(rows)
        observed, n_nonzero, _ = observed_underpay_share(cases)
        gate_b_line = f"| {model_id} | {n} | {accs[8]:.3f} | {accs[6]:.3f} | {accs[10]:.3f} | {invalid}/{n} |"
        acc_rows[model_id]["accs"] = accs
        acc_rows[model_id]["invalid"] = invalid
        acc_rows[model_id]["observed_underpay"] = observed
        acc_rows[model_id]["n_nonzero"] = n_nonzero

        if n_nonzero > 0:
            b2_shares = run_baseline(cases, lambda c: c["match_level"], seed=20261002 + 1)
            p2, p2_floor = permutation_test(observed, b2_shares)
            acc_rows[model_id]["gate_b_p"] = format_p(p2, p2_floor)
            acc_rows[model_id]["gate_b_pass"] = p2 < 0.05
        else:
            acc_rows[model_id]["gate_b_p"] = "n/a"
            acc_rows[model_id]["gate_b_pass"] = None

    lines.append("| Model | n | 8-digit (headline) | 6-digit | 10-digit | Invalid codes |")
    lines.append("|---|---|---|---|---|---|")
    for model_id in all_models:
        d = acc_rows[model_id]
        if d["n"] == 0:
            lines.append(f"| {model_id} | 0 | (no data yet) | | | |")
            continue
        lines.append(f"| {model_id} | {d['n']} | {d['accs'][8]:.3f} | {d['accs'][6]:.3f} | "
                     f"{d['accs'][10]:.3f} | {d['invalid']}/{d['n']} |")

    lines.append("\n## Direction bias (Gate B) on this subset\n")
    lines.append("| Model | Underpay share (n) | p vs. matched-depth baseline | Gate B |")
    lines.append("|---|---|---|---|")
    for model_id in all_models:
        d = acc_rows[model_id]
        if d["n"] == 0 or "observed_underpay" not in d:
            lines.append(f"| {model_id} | n/a | n/a | n/a |")
            continue
        verdict = "n/a (no nonzero-diff cases)" if d["gate_b_pass"] is None else ("PASS" if d["gate_b_pass"] else "NOT MET")
        lines.append(f"| {model_id} | {d['observed_underpay']:.3f} ({d['n_nonzero']}) | {d['gate_b_p']} | {verdict} |")

    out_md = REVIEW_DIR / "gemini_comparison.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    out_json = REVIEW_DIR / "gemini_comparison.json"
    out_json.write_text(json.dumps(
        {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in acc_rows.items()},
        indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_md} and {out_json}")


if __name__ == "__main__":
    main()
