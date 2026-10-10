"""
v1.2 self-check: recompute every number in the two README model tables from the raw cached responses,
independently of analysis.py's and analyze_same_sample.py's saved outputs. For each model, the raw response
text is re-parsed with parse_prediction and code validity is re-checked against the HTS release for the
ruling date. Then, for Table 1 (the same 228 rulings dated 2026-07-01 or later) and Table 2 (the same 1,098
rulings) it compares: n, 8-digit and 10-digit accuracy with Wilson 95% CIs, invalid share, the FORMAT /
INVENTED split of the invalid answers, the number of duty-changing errors and the underpaid share; for
Table 2 also the Gate B verdict (analyze_v1_1.gate_b). It also asserts that every Table 1 row says n = 228
and every Table 2 row says n = 1,098. Exits non-zero on any mismatch.
"""
import json
import re
import sys
from collections import Counter
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
from analysis import digit_match, wilson_ci  # noqa: E402
from run_llm_classification import parse_prediction, code_is_valid  # noqa: E402
import analyze_v1_1 as A  # noqa: E402
from analyze_format_vs_invention import group_of  # noqa: E402

START = date(2026, 7, 1)


# One v1.0 answer parses differently with the v1.1 parser (allam-2-7b N358156, a JSON array of three identical
# objects; DECISIONS.md 2026-10-07 item 6). The cached v1.0 value is kept everywhere in the project, so for that
# row the check uses the cached fields and reports the difference instead of failing.
KNOWN_PARSE_DIFFERENCES = {("allam-2-7b", "N358156")}
PARSE_DIFFERENCES = set()


def recompute(m):
    rows = []
    for fp in sorted(M.model_dir(m).glob("*.json")):
        r = json.loads(fp.read_text(encoding="utf-8"))
        content = r["raw_response"]["choices"][0]["message"].get("content")
        digits, _, err = parse_prediction(content)
        if r["raw_response"]["choices"][0].get("finish_reason") == "length":
            digits, err = None, "truncated"
        valid = False if err else code_is_valid(digits, r["rulingDate"])
        if digits != r.get("predicted_code"):
            PARSE_DIFFERENCES.add((m["model_id"], r["rulingNumber"]))
            rows.append({**r})  # cached predicted_code, parse_error and tag, as used by every table
            continue
        rows.append({**r, "predicted_code": digits, "parse_error": err, "tag": None if (not err and valid) else "INVALID_CODE"})
    return rows


def ci(k, n):
    lo, hi = wilson_ci(k, n)
    return f"{k / n:.1%} ({max(0.0, lo):.1%} to {hi:.1%})"


def parse_tables(readme):
    """Return (table1, table2) as {short model name: cells}."""
    out = []
    lines = readme.split("\n")
    for head in ("| Model | n | 8-digit accuracy (95% CI) | 10-digit accuracy (95% CI) | Invalid share | Format / invented, of invalid | Duty-changing errors (n) | Underpaid share (descriptive only) |",
                 "| Model | n | 8-digit accuracy (95% CI) | 10-digit accuracy (95% CI) | Invalid share | Format / invented, of invalid | Duty-changing errors (n) | Underpaid share | Gate B |"):
        i = lines.index(head)
        j = i + 2
        t = {}
        while j < len(lines) and lines[j].startswith("|"):
            cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
            t[re.sub(r"\s*[†‡]", "", cells[0]).strip()] = cells
            j += 1
        out.append(t)
    return out


def main():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    t1, t2 = parse_tables(readme)
    bad = checked = 0
    models = M.analysis_models()
    assert len(models) == 11, len(models)
    assert len(t1) == 11 and len(t2) == 11, (len(t1), len(t2))
    for m in models:
        short = m["model_id"].split("/")[-1].replace(":free", "")
        all_rows = recompute(m)
        sets = {1: [r for r in all_rows if datetime.fromisoformat(r["rulingDate"].replace("Z", "")).date() >= START], 2: all_rows}
        for which, rows in sets.items():
            cells = (t1 if which == 1 else t2).get(short)
            if cells is None:
                print(f"README table {which} has no row for {short}")
                bad += 1
                continue
            n = len(rows)
            k8 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 8))
            k10 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 10))
            inv = [r for r in rows if r["tag"] == "INVALID_CODE"]
            gc = Counter(group_of(r) for r in inv)
            fmt = gc["a"] + gc["b8"] + gc["b9"] + gc["c"]
            cases = A.build_wrong_cases(rows)
            share, nr, _ = A.observed_underpay_share(cases)
            want = {"n": f"{n:,}", "acc8": ci(k8, n), "acc10": ci(k10, n), "invalid": f"{len(inv) / n:.1%}",
                    "split": f"{fmt / len(inv):.0%} / {(len(inv) - fmt) / len(inv):.0%}", "dc_n": str(nr),
                    "under": f"{share:.1%}" if nr else "n/a"}
            got = {"n": cells[1], "acc8": cells[2], "acc10": cells[3], "invalid": cells[4], "split": cells[5], "dc_n": cells[6], "under": cells[7]}
            if which == 2:
                g = A.gate_b(rows)
                want["gate"] = "too few cases" if g["n"] < 30 else ("met" if g["verdict"].startswith("underpays") else "not met")
                got["gate"] = cells[8]
            want_n = "228" if which == 1 else "1,098"
            checked += 1
            if got["n"] != want_n or want["n"] != want_n:
                bad += 1
                print(f"N CHECK {short} table {which}: README {got['n']!r}, recomputed {want['n']!r}, required {want_n!r}")
            for k in want:
                checked += 1
                if want[k] != got[k]:
                    bad += 1
                    print(f"MISMATCH {short} table {which} {k}: recomputed {want[k]!r} vs README {got[k]!r}")
        print(f"checked {short}: table 1 n={len(sets[1])}, table 2 n={len(sets[2])}")
    print(f"re-parse vs cache differences: {sorted(PARSE_DIFFERENCES)} (documented: {sorted(KNOWN_PARSE_DIFFERENCES)})")
    if PARSE_DIFFERENCES != KNOWN_PARSE_DIFFERENCES:
        bad += 1
        print("MISMATCH: re-parse differs from the cache for rows other than the documented one")
    print(f"\n{checked} README table values recomputed from raw responses (both tables, every row n checked); mismatches: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
