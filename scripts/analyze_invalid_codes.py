"""
Invalid-code breakdown, outdated-code check, and dollar figure for valid wrong codes.

For every answer of each Groq model on all 1,098 usable rulings, assign exactly one
class (checked in this order):
  correct         10-digit match with the true code
  wrong_valid     a real 10-digit code in the HTS, but not the true one
  outdated        INVALID, 10 digits, not in the ruling-date HTS but present in at least
                  one 2022-2025 HTS release (parsed from the archived PDFs, see
                  fetch_older_hts.py)
  suffix_only     INVALID, >=8 digits, first 8 digits exist in the ruling-date HTS
                  (only the statistical suffix is wrong, or it was left off)
  six_eight       INVALID, >=6 digits, first 6 exist but the first 8 do not
  fabricated      INVALID, >=6 digits, even the first 6 do not exist
  no_usable_code  INVALID, unparseable or fewer than 6 digits
"outdated" takes precedence so a code that was once real is not also counted as
fabricated. A non-exclusive crosstab (a/b/c x outdated) is also written. Prefix existence
is tested against the HTS data used throughout the project (data/raw|compact hts_revisions;
see DECISIONS.md 2026-10-06 on what that data actually is).
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts" if (Path(__file__).resolve().parent / "scripts").exists() else Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from analysis import digit_match, rate_pct_for, load_model_results  # noqa: E402
from parse_duty_rates import revision_for_date, load_revision  # noqa: E402
from datetime import datetime  # noqa: E402

MODELS = M.model_ids()
OLDER_DIR = ROOT / "data" / "compact" / "hts_older"
CLASSES = ["correct", "wrong_valid", "suffix_only", "six_eight", "fabricated", "outdated", "no_usable_code"]

_prefix_cache = {}


def prefixes(release_id):
    if release_id not in _prefix_cache:
        keys = load_revision(release_id).keys()
        _prefix_cache[release_id] = (
            {k[:6] for k in keys if len(k) >= 6},
            {k[:8] for k in keys if len(k) >= 8},
            set(keys),
        )
    return _prefix_cache[release_id]


def load_older_codes():
    first = {}
    for fp in sorted(OLDER_DIR.glob("*.codes.json.gz")):
        d = json.loads(gzip.open(fp, "rt", encoding="utf-8").read())
        if d["release"][:4] not in ("2022", "2023", "2024", "2025") or "Prelim" in d["release"]:
            continue  # "Prelim" = preliminary draft release, never in force (2022HTSAPrelimC)
        for c in d["codes10"]:
            first.setdefault(c, d["release"])
    return first


def classify(row, older):
    pred = row.get("predicted_code")
    if digit_match(row["true_code"], pred, 10):
        return "correct", None
    if row.get("tag") != "INVALID_CODE":
        return "wrong_valid", None
    rel = revision_for_date(datetime.fromisoformat(row["rulingDate"].replace("Z", "")))
    p6, p8, exact = prefixes(rel)
    if not pred or len(pred) < 6:
        return "no_usable_code", None
    abc = "suffix_only" if (len(pred) >= 8 and pred[:8] in p8) else \
          "six_eight" if pred[:6] in p6 else "fabricated"
    was_outdated = len(pred) == 10 and pred not in exact and pred in older
    return ("outdated" if was_outdated else abc), abc


def main():
    older = load_older_codes()
    print(f"older (2022-2025) 10-digit codes indexed: {len(older)}")
    res = {}
    for m in MODELS:
        rows = load_model_results(M.path_for(m))
        n = len(rows)
        cls = Counter()
        crosstab = Counter()
        len_split = Counter()
        wrong_valid_rows = []
        for r in rows:
            c, abc = classify(r, older)
            cls[c] += 1
            if abc is not None:
                crosstab[(abc, c == "outdated")] += 1
            if c == "suffix_only":
                len_split["8_digits_no_suffix" if len(r["predicted_code"]) == 8 else "10_digits_wrong_suffix_or_other"] += 1
            if c == "wrong_valid":
                wrong_valid_rows.append(r)
        n_invalid = sum(cls[k] for k in ("suffix_only", "six_eight", "fabricated", "outdated", "no_usable_code"))
        # duty at stake for valid wrong codes
        diffs = []
        for r in wrong_valid_rows:
            t = rate_pct_for(r["true_code"], r["rulingDate"])
            p = rate_pct_for(r.get("predicted_code"), r["rulingDate"])
            if t is None or p is None:
                continue
            diffs.append(abs(p - t) / 100 * 100000)
        dollar = None
        if diffs:
            dollar = {"n": len(diffs), "median": float(np.median(diffs)),
                      "q1": float(np.percentile(diffs, 25)), "q3": float(np.percentile(diffs, 75)),
                      "n_zero": int(sum(1 for d in diffs if d == 0))}
        res[m] = {"n": n, "classes": {k: cls[k] for k in CLASSES}, "n_invalid": n_invalid,
                  "n_wrong_valid": len(wrong_valid_rows), "suffix_only_split": dict(len_split),
                  "crosstab_abc_by_outdated": {f"{a}|outdated={o}": v for (a, o), v in sorted(crosstab.items())},
                  "dollar_valid_wrong": dollar}
    out_json = ROOT / "review" / "invalid_breakdown.json"
    out_json.write_text(json.dumps(res, indent=2), encoding="utf-8")

    L = ["# Invalid-code breakdown, outdated check, and dollar figure (scripts/analyze_invalid_codes.py)\n",
         f"All 1,098 usable rulings per model. Outdated check uses {len(older):,} distinct 10-digit codes from the 2022-2025 HTS releases.\n",
         "## Share of ALL answers\n",
         "| Model | n | correct | wrong, valid code | invalid: suffix only | invalid: first 6 ok, first 8 not | invalid: fabricated | invalid: outdated | invalid: no usable code |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        d = res[m]; n = d["n"]; c = d["classes"]
        L.append(f"| {m} | {n} | " + " | ".join(f"{c[k]} ({c[k]/n:.1%})" for k in
                 ["correct", "wrong_valid", "suffix_only", "six_eight", "fabricated", "outdated", "no_usable_code"]) + " |")
    L += ["", "## Share of INVALID answers\n",
          "| Model | n invalid | suffix only | first 6 ok, first 8 not | fabricated | outdated | no usable code |", "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        d = res[m]; c = d["classes"]; ni = d["n_invalid"]
        L.append(f"| {m} | {ni} | " + " | ".join(f"{c[k]} ({c[k]/ni:.1%})" for k in
                 ["suffix_only", "six_eight", "fabricated", "outdated", "no_usable_code"]) + " |")
    L += ["", "## Suffix-only invalid answers: left the suffix off vs wrote a wrong suffix\n",
          "| Model | suffix_only n | exactly 8 digits (no suffix) | other (wrong suffix etc.) |", "|---|---|---|---|"]
    for m in MODELS:
        d = res[m]; s = d["suffix_only_split"]; tot = d["classes"]["suffix_only"]
        a = s.get("8_digits_no_suffix", 0); b = s.get("10_digits_wrong_suffix_or_other", 0)
        L.append(f"| {m} | {tot} | {a} | {b} |")
    L += ["", "## Non-exclusive crosstab: a/b/c class by outdated flag (invalid answers with >=6 digits)\n",
          "| Model | key | n |", "|---|---|---|"]
    for m in MODELS:
        for k, v in res[m]["crosstab_abc_by_outdated"].items():
            L.append(f"| {m} | {k} | {v} |")
    L += ["", "## Duty at stake per $100,000 declared, valid wrong codes (both rates resolve)\n",
          "| Model | valid wrong codes | with usable rates (n) | median | IQR | zero-rate-difference |", "|---|---|---|---|---|---|"]
    for m in MODELS:
        d = res[m]; dv = d["dollar_valid_wrong"]
        if dv:
            L.append(f"| {m} | {d['n_wrong_valid']} | {dv['n']} | ${dv['median']:,.0f} | ${dv['q1']:,.0f} to ${dv['q3']:,.0f} | {dv['n_zero']} |")
        else:
            L.append(f"| {m} | {d['n_wrong_valid']} | 0 | n/a | n/a | n/a |")
    (ROOT / "review" / "invalid_breakdown.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
