"""
MFN duty rates against the release in force on each ruling's date.

Phase 3 used the current schedule for every ruling (see DECISIONS.md 2026-10-06). Here the
General (column 1) rate of every code in the cost analysis is re-read from the archived
PDF of the release in force on the ruling date (parse_release_rates.py), using the same
10 -> 8 -> 6 -> 4 digit walk-up and the same rate classification as parse_duty_rates.py.

Three comparisons per (code, ruling date) pair that the cost analysis uses (true code and
predicted code of every wrong answer):
  parser check   Rev20 PDF (the current release) vs the current JSON: how often the PDF
                 parser alone disagrees with the JSON
  time effect    ruling-date release vs Rev20, same parser: genuine rate changes in 2026
  combined       ruling-date release vs the current JSON
The ruling-date-release rates then re-run the direction and dollar figures next to the
JSON-based ones. Remaining PDF-vs-JSON differences are codes where the PDF has a rate on an
8-digit parent line that the JSON export has no row for (see DECISIONS.md 2026-10-06).
Writes review/revision_rates.md/.json.
"""
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts" if (Path(__file__).resolve().parent / "scripts").exists() else Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from analysis import digit_match, rate_pct_for, load_model_results, wilson_ci  # noqa: E402
from parse_duty_rates import classify_rate, revision_for_date, resolve_rate, load_revision, read_revision_rows  # noqa: E402

MODELS = M.model_ids()
RATES_DIR = ROOT / "data" / "compact" / "hts_rates"
CURRENT = "2026HTSRev20"
_cache = {}


def rates(release):
    if release not in _cache:
        _cache[release] = json.loads(gzip.open(RATES_DIR / f"{release}.rates.json.gz", "rt", encoding="utf-8").read())
    return _cache[release]


def pdf_pct(code, release):
    if not code or len(code) != 10:
        return None  # same rule as analysis.rate_pct_for: only 10-digit codes get a rate
    table = rates(release)
    for length in (10, 8, 6, 4):
        text = table.get(code[:length])
        if text:
            rate_type, pct = classify_rate(text)
            return pct if rate_type in ("ad_valorem", "free") else None
    return None


def json_only_pct(code, date_str, strip_markup):
    """Rate from the JSON export alone (always the current schedule), as Phase 3 did."""
    if not code or len(code) != 10:
        return None
    rate_str, err = resolve_rate(load_revision(release_for(date_str), False), code)
    if err:
        return None
    rate_type, pct = classify_rate(rate_str, strip_markup=strip_markup)
    return pct if rate_type in ("ad_valorem", "free") else None


def release_for(date_str):
    return revision_for_date(datetime.fromisoformat(date_str.replace("Z", "")))


def main():
    pairs = {}
    per_model = {}
    for m in MODELS:
        rows = load_model_results(M.path_for(m))
        wrong = [r for r in rows if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
        per_model[m] = wrong
        for r in wrong:
            for code in (r["true_code"], r.get("predicted_code")):
                if code:
                    pairs[(code, r["rulingDate"])] = None
    parser_bad = time_diff = combined = 0
    cur_has_rate = 0
    for (code, date) in pairs:
        j = json_only_pct(code, date, True)
        pc = pdf_pct(code, CURRENT)
        pr = pdf_pct(code, release_for(date))
        if j is not None:
            cur_has_rate += 1
        if pc != j:
            parser_bad += 1
        if pr != pc:
            time_diff += 1
        if pr != j:
            combined += 1
    L = ["# MFN rates at the ruling-date release vs the current schedule (scripts/check_rate_impact.py)\n",
         f"Distinct (code, ruling date) pairs used by the cost analysis (true and predicted codes of wrong answers, all 3 models): **{len(pairs):,}**; of these, {cur_has_rate:,} resolve to an ad valorem or free rate on the current JSON.\n",
         "| Comparison | Pairs that differ |", "|---|---|",
         f"| parser check: {CURRENT} PDF vs current JSON | {parser_bad} |",
         f"| time effect: ruling-date release vs {CURRENT} (same parser) | {time_diff} |",
         f"| combined: ruling-date release vs current JSON | {combined} |", ""]
    res = {"pairs": len(pairs), "parser_check_differ": parser_bad, "time_effect_differ": time_diff, "combined_differ": combined}

    L += ["## Direction and dollar figures re-run with ruling-date rates\n",
          "| Model | basis | comparable wrong answers (n) | rate differs (n) | underpaid | underpay share (Wilson 95% CI) | median duty at stake per $100k | IQR |",
          "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for basis in ("original Phase 3 (JSON only, markup unparsed)", "JSON only, markup stripped", "ruling-date release rates (final)"):
            diffs, signed = [], []
            for r in per_model[m]:
                if basis.startswith("original") or basis.startswith("JSON only"):
                    strip = not basis.startswith("original")
                    t, p = json_only_pct(r["true_code"], r["rulingDate"], strip), json_only_pct(r.get("predicted_code"), r["rulingDate"], strip)
                else:
                    t = pdf_pct(r["true_code"], release_for(r["rulingDate"]))
                    p = pdf_pct(r.get("predicted_code"), release_for(r["rulingDate"]))
                if t is None or p is None:
                    continue
                signed.append(p - t)
                diffs.append(abs(p - t) / 100 * 100000)
            nz = [d for d in signed if d != 0]
            under = sum(1 for d in nz if d < 0)
            lo, hi = wilson_ci(under, len(nz))
            q1, med, q3 = (float(np.percentile(diffs, q)) for q in (25, 50, 75))
            L.append(f"| {m} | {basis} | {len(signed)} | {len(nz)} | {under} | {under / len(nz):.1%} ({lo:.1%} to {hi:.1%}) | ${med:,.0f} | ${q1:,.0f} to ${q3:,.0f} |")
            res.setdefault(m, {})[basis] = {"comparable": len(signed), "rate_differs": len(nz), "underpaid": under,
                                            "wilson": [lo, hi], "median": med, "q1": q1, "q3": q3}
    # Parser accuracy and markup facts, measured on the current release (Rev20 PDF vs JSON export)
    import re
    cur_rows = read_revision_rows("CURRENT")
    if cur_rows is not None:
        j = {}
        n_markup = 0
        for row in cur_rows:
            d = re.sub(r"\D", "", row.get("htsno") or "")
            if len(d) in (6, 8):
                g = row.get("general") or ""
                j[d] = g
                if "<" in g and classify_rate(g, strip_markup=False)[0] == "other" and classify_rate(g)[0] in ("ad_valorem", "free"):
                    n_markup += 1
        rated = [d for d, g in j.items() if classify_rate(g)[0] in ("ad_valorem", "free")]
        pdf = rates(CURRENT)
        miss = [d for d in rated if classify_rate(pdf.get(d))[:1] != classify_rate(j[d])[:1] or classify_rate(pdf.get(d)) != classify_rate(j[d])]
        L += ["", "## Parser accuracy and markup (6/8-digit rows of the current release)", "",
              f"- JSON rows with an ad valorem or free General rate: {len(rated):,}; not reproduced by the PDF parse: {len(miss)} (of which in chapters 1-97: {sum(1 for d in miss if int(d[:2]) <= 97)}).",
              f"- JSON rates carrying HTML markup that the original classifier read as 'other' but are ad valorem or free once stripped: {n_markup}."]
        res["parser_rows"] = len(rated); res["parser_missed"] = len(miss); res["markup_rates"] = n_markup
    (ROOT / "review" / "revision_rates.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (ROOT / "review" / "revision_rates.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
