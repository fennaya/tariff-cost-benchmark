"""
Bryce's question 2 (PREREG_v1.1.md section 6): how much of the invalid-code rate is formatting
and how much is the model inventing a code. Every invalid answer goes into exactly one group,
checked against the HTS release in force on the ruling date:

  FORMAT
    a  unparseable, no code, truncated, or fewer than 6 digits
    b  first 8 digits exist in the HTS but the answer stops short of 10 (b8 = exactly 8 digits,
       b9 = 9 digits): the suffix is missing
    c  first 8 digits exist and the answer has 10 or more digits: the suffix is wrong
  INVENTED
    d  the 6-digit subheading exists but no tariff line starts with the answer's first 8 digits
    e  even the 6-digit subheading does not exist

The single v1.0 "outdated" answer (gpt-oss-120b, ruling N359777: 2106909995 was a real code until
2025) has an existing first-8 prefix and 10 digits, so it falls in c (FORMAT), as pre-registered.
For the v1.0 models the five groups must sum to the published invalid counts or the script stops.
Counts and shares of all answers and of invalid answers carry Wilson 95% CIs. Models run on 200
rulings show n = 200. Writes review/format_vs_invention.md and .json.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
from analysis import wilson_ci  # noqa: E402
from parse_duty_rates import revision_for_date  # noqa: E402
from analyze_invalid_codes import prefixes  # noqa: E402

LENIENT = re.compile(r'"hts_code"\s*:\s*"([^"]+)"')
GROUPS = ["a", "b8", "b9", "c", "d", "e"]
LABELS = {"a": "(a) unparseable / no code / truncated", "b8": "(b) first 8 right, exactly 8 digits (suffix missing)",
          "b9": "(b) first 8 right, 9 digits", "c": "(c) first 8 right, wrong suffix",
          "d": "(d) 6-digit subheading exists, no tariff line with these 8 digits",
          "e": "(e) not even the 6-digit subheading exists"}


def group_of(row):
    pred = row.get("predicted_code")
    if row.get("parse_error") or not pred or len(pred) < 6:
        return "a"
    p6, p8, _ = prefixes(revision_for_date(datetime.fromisoformat(row["rulingDate"].replace("Z", ""))))
    if len(pred) >= 8 and pred[:8] in p8:
        return "b8" if len(pred) == 8 else ("b9" if len(pred) == 9 else "c")
    return "d" if pred[:6] in p6 else "e"


def recoverable(row):
    c = (((row.get("raw_response") or {}).get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    return bool(LENIENT.search(c))


def _unknown():
    out = set()
    for m in M.load():
        try:
            from datetime import date
            date.fromisoformat(m.get("training_cutoff", "unknown"))
        except ValueError:
            out.add(m["model_id"])
    return out


UNKNOWN = _unknown()


def lab(mid):
    return mid + (" †" if mid in UNKNOWN else "")


def ci(k, n):
    lo, hi = wilson_ci(k, n)
    lo = max(0.0, lo)
    return f"{k} ({k / n:.1%}; {lo:.1%} to {hi:.1%})" if n else "0"


def main():
    published = json.loads((ROOT / "data" / "processed" / "analysis_results.json").read_text(encoding="utf-8"))
    res = {}
    all_rows = ["# Format slip or invented code? (scripts/analyze_format_vs_invention.py)\n",
                "FORMAT = (a) unparseable or truncated, (b) first 8 digits right but suffix missing, (c) first 8 right but wrong suffix. "
                "INVENTED = (d) real 6-digit subheading but no tariff line with the answer's first 8 digits, (e) no such 6-digit subheading. "
                "The one v1.0 'outdated' answer is in (c), FORMAT. Shares carry Wilson 95% CIs. Models on the 200-ruling sample show n = 200.\n",
                "## Counts and shares of ALL answers\n",
                "| Model | n | invalid | FORMAT (a+b+c) | INVENTED (d+e) | (a) | (b) 8 digits | (b) 9 digits | (c) | (d) | (e) |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
    inv_rows = ["\n## Shares of INVALID answers\n",
                "| Model | invalid n | FORMAT | INVENTED | (a) | (b) 8 digits | (b) 9 digits | (c) | (d) | (e) | (a) with a recoverable code in the text |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
    for mid, rows in M.results_by_model().items():
        n = len(rows)
        inv = [r for r in rows if r.get("tag") == "INVALID_CODE"]
        counts = {g: 0 for g in GROUPS}
        rec = 0
        true8 = 0
        for r in inv:
            g = group_of(r)
            counts[g] += 1
            if g in ("b8", "b9", "c") and r["predicted_code"][:8] == r["true_code"][:8]:
                true8 += 1
            if g == "a" and recoverable(r):
                rec += 1
        total = sum(counts.values())
        assert total == len(inv), (mid, total, len(inv))
        if mid in published:
            assert len(inv) == published[mid]["n_invalid_code"], (mid, len(inv), published[mid]["n_invalid_code"])
        fmt = counts["a"] + counts["b8"] + counts["b9"] + counts["c"]
        inv_n = len(inv)
        res[mid] = {"n": n, "invalid": inv_n, "counts": counts, "format": fmt, "invented": counts["d"] + counts["e"],
                    "a_recoverable": rec, "b_c_first8_equals_true": true8}
        all_rows.append(f"| {lab(mid)} | {n} | {ci(inv_n, n)} | {ci(fmt, n)} | {ci(counts['d'] + counts['e'], n)} | "
                        + " | ".join(ci(counts[g], n) for g in GROUPS) + " |")
        if inv_n:
            inv_rows.append(f"| {lab(mid)} | {inv_n} | {ci(fmt, inv_n)} | {ci(counts['d'] + counts['e'], inv_n)} | "
                            + " | ".join(ci(counts[g], inv_n) for g in GROUPS) + f" | {rec} of {counts['a']} |")
        else:
            inv_rows.append(f"| {lab(mid)} | 0 | n/a | n/a | | | | | | | |")
    extra = ["\n## Are the FORMAT answers right at 8 digits?\n",
             "Groups (b) and (c) mean the answer's first 8 digits are a real tariff line. This counts how many of them equal the TRUE code's first 8 digits, i.e. the model had the duty-relevant classification right and only the suffix is off. The rest name a real tariff line that is not the right one.\n",
             "| Model | answers in (b)+(c) | first 8 digits equal the true code's | share of (b)+(c) | share of ALL invalid answers |", "|---|---|---|---|---|"]
    for mid, d in res.items():
        k = d["counts"]["b8"] + d["counts"]["b9"] + d["counts"]["c"]
        extra.append(f"| {lab(mid)} | {k} | {d['b_c_first8_equals_true']} | {ci(d['b_c_first8_equals_true'], k) if k else 'n/a'} | {ci(d['b_c_first8_equals_true'], d['invalid']) if d['invalid'] else 'n/a'} |")
    out = ("\n".join(all_rows + inv_rows + extra)
           + "\n\n† contamination not ruled out (no stated cutoff); treat this model's accuracy as an upper bound.\n"
           + "\nFor the v1.0 models the five groups sum to the published invalid counts (checked in the script).\n")
    (ROOT / "review" / "format_vs_invention.md").write_text(out, encoding="utf-8")
    (ROOT / "review" / "format_vs_invention.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
