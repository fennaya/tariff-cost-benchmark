"""
v1.2 post-hoc restructure (no API calls): every model graded on exactly the same rulings. Possible because all 11
models have now answered all 1,098 usable rulings.

  PRIMARY set  = the 228 rulings dated 2026-07-01 to 2026-08-14, after every stated training cutoff
                 (latest stated: the Claude models, 2026-06-30). Models with no stated cutoff (marked dagger)
                 get no guarantee: July-August is only the best available window for them.
  SECOND set   = all 1,098 rulings ("upper bound: includes rulings that may be in training data").

Per model and set: n, 8-digit and 10-digit accuracy with Wilson 95% CIs, invalid share, FORMAT / INVENTED split
of the invalid answers (analyze_format_vs_invention.group_of), duty-changing (rate-changing) errors with n and the
underpaid share. Gate B (pre-registered rule: permutation p < 0.05 against Baseline 2 and n >= 30) is run on the
1,098 set only; on the 228 set several models have fewer than 30 duty-changing errors, so the 228 underpay numbers
are descriptive. Paired tests on the 228: exact McNemar (8-digit) for each pair of neighbours in the 8-digit ranking
with Holm correction over those 10 tests, plus all 55 pairs with Holm over 55 (supplementary) to show which models tie.
Also writes class counts (analyze_invalid_codes.classify) for the error-breakdown figures.
Writes review/same_sample.md and review/same_sample.json.
"""
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, date
from itertools import combinations
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
import analyze_v1_1 as A  # noqa: E402
from analysis import digit_match, wilson_ci  # noqa: E402
from analyze_format_vs_invention import group_of  # noqa: E402
import analyze_invalid_codes as IC  # noqa: E402

PRIMARY_START = date(2026, 7, 1)
CLASSES = IC.CLASSES


def rdate(r):
    return datetime.fromisoformat(r["rulingDate"].replace("Z", "")).date()


def ci(k, n):
    lo, hi = wilson_ci(k, n)
    return f"{k / n:.1%} ({max(0.0, lo):.1%} to {hi:.1%})"


def unknown_cutoff(m):
    try:
        date.fromisoformat(m.get("training_cutoff", "unknown"))
        return False
    except ValueError:
        return True


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [None] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def cell_stats(rows, older, with_gate):
    n = len(rows)
    k8 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 8))
    k10 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 10))
    inv = [r for r in rows if r.get("tag") == "INVALID_CODE"]
    gc = Counter(group_of(r) for r in inv)
    fmt = gc["a"] + gc["b8"] + gc["b9"] + gc["c"]
    invd = gc["d"] + gc["e"]
    cases = A.build_wrong_cases(rows)
    observed, nr, _ = A.observed_underpay_share(cases)
    out = {"n": n, "k8": k8, "k10": k10, "invalid": len(inv), "format": fmt, "invented": invd,
           "rate_changing_n": nr, "underpaid": round(observed * nr) if nr else 0, "under_share": observed if nr else None}
    if with_gate:
        g = A.gate_b(rows)
        out["gate_p2"] = g.get("p2_num")
        out["gate_b"] = "too few cases" if g["n"] < 30 else ("met" if g["verdict"].startswith("underpays") else "not met")
    wrong = [r for r in rows if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
    diffs = A.comparable_diffs(rows)
    out["wrong"] = len(wrong)
    out["wrong_flagged_invalid"] = sum(1 for r in wrong if r.get("tag") == "INVALID_CODE")
    out["invalid_first8_equals_true"] = sum(1 for r in inv if len(r.get("predicted_code") or "") >= 8 and r["predicted_code"][:8] == r["true_code"][:8])
    out["priced_wrong"] = len(diffs)
    out["median_duty_per_100k"] = float(statistics.median(abs(d[1]) * 1000 for d in diffs)) if diffs else None
    cls = Counter()
    for r in rows:
        c, _ = IC.classify(r, older)
        cls[c] += 1
    out["classes"] = {k: cls[k] for k in CLASSES}
    return out


def main():
    older = IC.load_older_codes()
    models = M.analysis_models()
    assert len(models) == 11
    rows_all = {m["model_id"]: M.load_results(m["model_id"]) for m in models}
    ids_all = {r["rulingNumber"] for r in next(iter(rows_all.values()))}
    for mid, rows in rows_all.items():
        assert len(rows) == 1098 and {r["rulingNumber"] for r in rows} == ids_all, mid
    rows_p = {mid: [r for r in rows if rdate(r) >= PRIMARY_START] for mid, rows in rows_all.items()}
    assert all(len(v) == 228 for v in rows_p.values())
    dates = sorted(rdate(r) for r in next(iter(rows_p.values())))

    res = {"primary_window": [str(dates[0]), str(dates[-1])], "models": {}}
    for m in models:
        mid = m["model_id"]
        res["models"][mid] = {"dagger": unknown_cutoff(m), "cutoff": m.get("training_cutoff"),
                              "p228": cell_stats(rows_p[mid], older, with_gate=False),
                              "p1098": cell_stats(rows_all[mid], older, with_gate=True)}
    ranking = sorted(res["models"], key=lambda k: (-res["models"][k]["p228"]["k8"], -res["models"][k]["p228"]["k10"], k))
    res["ranking_8digit_228"] = ranking
    # Holm over the 1,098 Gate B family (sensitivity)
    ps = [res["models"][k]["p1098"]["gate_p2"] for k in ranking]
    for k, ap in zip(ranking, holm(ps)):
        res["models"][k]["p1098"]["gate_holm_p"] = ap
        res["models"][k]["p1098"]["gate_b_holm"] = ("too few cases" if res["models"][k]["p1098"]["gate_b"] == "too few cases"
                                                      else ("met" if (ap < 0.05) else "not met"))

    # sensitivity: Table 2 without the rulings whose cleaned description is not a product description (review/description_quality.json)
    flagged = set(json.loads((ROOT / "review" / "description_quality.json").read_text(encoding="utf-8"))["flagged"])
    for mid in ranking:
        rows = [r for r in rows_all[mid] if r["rulingNumber"] not in flagged]
        k8 = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), 8))
        g = A.gate_b(rows)
        res["models"][mid]["p1098_excl_flagged"] = {
            "n": len(rows), "k8": k8, "gate_n": g["n"], "under_share": g.get("share"), "gate_p2": g.get("p2_num"),
            "gate_b": "too few cases" if g["n"] < 30 else ("met" if g["verdict"].startswith("underpays") else "not met")}
    res["n_flagged"] = len(flagged)

    # paired tests on the 228
    right = {mid: {r["rulingNumber"]: digit_match(r["true_code"], r.get("predicted_code"), 8) for r in rows_p[mid]} for mid in ranking}

    def mcnemar(a, b):
        x = sum(1 for rn in right[a] if right[a][rn] and not right[b][rn])
        y = sum(1 for rn in right[a] if (not right[a][rn]) and right[b][rn])
        p = 1.0 if x + y == 0 else float(stats.binomtest(x, x + y, 0.5).pvalue)
        return x, y, p

    neigh = []
    for a, b in zip(ranking, ranking[1:]):
        x, y, p = mcnemar(a, b)
        neigh.append({"a": a, "b": b, "a_only": x, "b_only": y, "p": p})
    for d, ap in zip(neigh, holm([d["p"] for d in neigh])):
        d["holm_p"] = ap
        d["verdict"] = "real gap" if ap < 0.05 else "tie (not distinguishable)"
    allpairs = []
    for a, b in combinations(ranking, 2):
        x, y, p = mcnemar(a, b)
        allpairs.append({"a": a, "b": b, "a_only": x, "b_only": y, "p": p})
    for d, ap in zip(allpairs, holm([d["p"] for d in allpairs])):
        d["holm_p"] = ap
    res["neighbour_tests"] = neigh
    res["all_pairs"] = allpairs

    # ---------------- markdown
    def tag(k):
        return k + (" †" if res["models"][k]["dagger"] else "")

    def split(c):
        return f"{c['format']} / {c['invented']}" + (f" ({c['format'] / c['invalid']:.0%} / {c['invented'] / c['invalid']:.0%})" if c["invalid"] else "")

    def und(c):
        if not c["rate_changing_n"]:
            return "n = 0"
        lo, hi = wilson_ci(c["underpaid"], c["rate_changing_n"])
        return f"{c['under_share']:.1%} ({max(0.0, lo):.1%} to {hi:.1%})"

    L = ["# Same-sample analysis: every model graded on exactly the same rulings (scripts/analyze_same_sample.py)\n",
         "Post hoc restructure, no API calls, possible because all 11 models have answered all 1,098 rulings. Ranking order is 8-digit accuracy on the 228. "
         "† = no stated training cutoff: July-August is the best available window for these models, not a guarantee.\n",
         f"## Table 1. Primary: all 11 models on the same 228 rulings dated {dates[0]} to {dates[-1]} (after every stated training cutoff)\n",
         "Duty-changing errors = wrong answers whose duty rate differs from the true code's (both rates must resolve). Underpaid share is descriptive only here: several models have fewer than 30 duty-changing errors on 228 rulings, so Gate B is not run on this set.\n",
         "| Model | n | 8-digit accuracy (95% CI) | 10-digit accuracy (95% CI) | Invalid share (95% CI) | Format / invented, of invalid | Duty-changing errors (n) | Underpaid share (descriptive only) |",
         "|---|---|---|---|---|---|---|---|"]
    for k in ranking:
        c = res["models"][k]["p228"]
        L.append(f"| {tag(k)} | {c['n']} | {ci(c['k8'], c['n'])} | {ci(c['k10'], c['n'])} | {ci(c['invalid'], c['n'])} | {split(c)} | {c['rate_changing_n']} | {und(c)} |")
    L += ["", "## Paired tests on the 228 (exact McNemar at 8 digits, neighbours in the ranking, Holm over these tests)\n",
          "a only = rulings the higher-ranked model got right and the lower-ranked missed; b only = the reverse.\n",
          "| Higher-ranked (a) | Next (b) | a only | b only | p | Holm-adjusted p | Verdict |", "|---|---|---|---|---|---|---|"]
    for d in neigh:
        L.append(f"| {tag(d['a'])} | {tag(d['b'])} | {d['a_only']} | {d['b_only']} | {d['p']:.4f} | {d['holm_p']:.4f} | {d['verdict']} |")
    ties = [(d["a"], d["b"], d["holm_p"]) for d in allpairs if d["holm_p"] >= 0.05]
    L += ["", f"Supplementary, all {len(allpairs)} pairs with Holm over {len(allpairs)} (exploratory): the pairs that are NOT distinguishable are:\n"]
    for a, b, p in ties:
        L.append(f"- {tag(a)} and {tag(b)} (Holm-adjusted p = {p:.3f})")
    L += ["", "## Table 2. Second: all 11 models on the same 1,098 rulings (upper bound: includes rulings that may be in training data)\n",
          "Gate B (pre-registered rule: permutation p < 0.05 against Baseline 2 and n >= 30 duty-changing errors) is run on this set. Same ranking order as Table 1.\n",
          "| Model | n | 8-digit accuracy (95% CI) | 10-digit accuracy (95% CI) | Invalid share (95% CI) | Format / invented, of invalid | Duty-changing errors (n) | Underpaid share (95% CI) | Gate B | Gate B under Holm |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k in ranking:
        c = res["models"][k]["p1098"]
        L.append(f"| {tag(k)} | {c['n']:,} | {ci(c['k8'], c['n'])} | {ci(c['k10'], c['n'])} | {ci(c['invalid'], c['n'])} | {split(c)} | {c['rate_changing_n']} | {und(c)} | {c['gate_b']} (p = {c['gate_p2']:.4f}) | {c['gate_b_holm']} (adjusted p = {c['gate_holm_p']:.4f}) |")
    L += ["", f"## Sensitivity: Table 2 without the {len(flagged)} rulings whose cleaned description is not a product description (review/description_quality.md)", "",
          "| Model | n | 8-digit accuracy | Duty-changing errors (n) | Underpaid share | Gate B | Gate B on all 1,098 | Changed? |", "|---|---|---|---|---|---|---|---|"]
    for k in ranking:
        e, c = res["models"][k]["p1098_excl_flagged"], res["models"][k]["p1098"]
        L.append(f"| {tag(k)} | {e['n']:,} | {e['k8'] / e['n']:.1%} | {e['gate_n']} | {e['under_share']:.1%} | {e['gate_b']} (p = {e['gate_p2']:.4f}) | {c['gate_b']} | {'YES' if e['gate_b'] != c['gate_b'] else 'no'} |")
    L += ["", "## Numbers behind the README plain summary (both sets)", "",
          "Wrong = not a 10-digit match. Validity check = flag any answer that is not a 10-digit code in the HTS. FORMAT share = suffix-slip share of invalid answers. First-8 = invalid answers whose first 8 digits equal the true code's. Priced = wrong answers for which both rates resolve; duty-changing = priced answers whose rate differs. Median duty = median |rate difference| x $100,000 over priced wrong answers.", "",
          "| Model | Set | Wrong | Wrong and flagged invalid | Wrong with a valid code | Invalid | FORMAT share of invalid | First 8 right, of invalid | Priced wrong | Duty-changing, of wrong | Duty-changing, of priced | Median duty per $100,000 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in ranking:
        for lab, key in (("228", "p228"), ("1,098", "p1098")):
            c = res["models"][k][key]
            if not c["invalid"] or not c["wrong"] or not c["priced_wrong"]:
                continue
            L.append(f"| {tag(k)} | {lab} | {c['wrong']} | {c['wrong_flagged_invalid']} ({c['wrong_flagged_invalid'] / c['wrong']:.1%}) | {c['wrong'] - c['wrong_flagged_invalid']} ({(c['wrong'] - c['wrong_flagged_invalid']) / c['wrong']:.1%}) | {c['invalid']} | "
                     f"{c['format']} ({c['format'] / c['invalid']:.1%}) | {c['invalid_first8_equals_true']} ({c['invalid_first8_equals_true'] / c['invalid']:.1%}) | {c['priced_wrong']} | {c['rate_changing_n']} ({c['rate_changing_n'] / c['wrong']:.1%}) | {c['rate_changing_n']} of {c['priced_wrong']} ({c['rate_changing_n'] / c['priced_wrong']:.1%}) | ${c['median_duty_per_100k']:,.0f} |")
    out = "\n".join(L) + "\n"
    (ROOT / "review" / "same_sample.md").write_text(out, encoding="utf-8")
    (ROOT / "review" / "same_sample.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
