"""
v1.1 analysis (PREREG_v1.1.md). Reads the model list from config.json (models_config), uses only
complete runs, and writes review/v1_1_results.md, review/v1_1_results.json and
review/biggest_misses.md/.json. No number is typed here.

Primary score per model = rulings dated after the model's stated training cutoff. If the cutoff is
unknown, or later than 2026-08-14 (the last ruling), the model is labelled "contamination not ruled
out" and the primary rows are all rows. The full sample is reported as secondary.
Gate B (pre-registered): "underpays more than chance" only if the underpay share beats Baseline 2
at p < 0.05 AND n >= 30 rate-changing errors.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, date
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
from analysis import digit_match, wilson_ci, rate_pct_for  # noqa: E402
from parse_duty_rates import revision_for_date, load_revision, resolve_rate, classify_rate  # noqa: E402
from audit_direction import (  # noqa: E402
    SEED, build_wrong_cases, observed_underpay_share, run_baseline, permutation_test, format_p,
    deepest_match_level, get_pool,
)
from analyze_format_vs_invention import group_of  # noqa: E402
from analyze_invalid_codes import prefixes  # noqa: E402

LAST_RULING = date(2026, 8, 14)
usable = {r["rulingNumber"]: r for r in (json.loads(l) for l in M.USABLE_PATH.read_text(encoding="utf-8").splitlines())}
REPORT = []
_dq = ROOT / "review" / "description_quality.json"
FLAGGED = set(json.loads(_dq.read_text(encoding="utf-8"))["flagged"]) if _dq.exists() else set()


UNKNOWN_CUTOFF = set()  # filled in main(): models with no stated cutoff
DAGGER_NOTE = "† contamination not ruled out (no stated cutoff); treat this model's accuracy as an upper bound."


def mark(line):
    """Append a dagger to the model ids in the first two cells of a table row."""
    if not line.startswith("|"):
        return line
    cells = line.split("|")
    for i in (1, 2):
        if i < len(cells) - 1 and cells[i].strip() in UNKNOWN_CUTOFF:
            cells[i] = " " + cells[i].strip() + " † "
    return "|".join(cells)


def out(line=""):
    REPORT.append(mark(line))


def ci(k, n, digits=1):
    if not n:
        return "n/a"
    lo, hi = wilson_ci(k, n)
    lo = max(0.0, lo)
    return f"{k / n:.{digits}%} ({lo:.{digits}%} to {hi:.{digits}%})"


def rdate(row):
    return datetime.fromisoformat(row["rulingDate"].replace("Z", "")).date()


def cutoff_info(model):
    c = model.get("training_cutoff", "unknown")
    try:
        cd = date.fromisoformat(c)
    except ValueError:
        return None, "contamination not ruled out (cutoff unknown)"
    if cd >= LAST_RULING:
        return cd, "contamination not ruled out (cutoff after the last ruling)"
    first = date(2026, 1, 5)
    if cd < first:
        return cd, f"cutoff {cd}; every ruling is after it"
    return cd, f"post-cutoff rulings only (after {cd})"


def primary_rows(model, rows):
    cd, _ = cutoff_info(model)
    if cd is None:
        return rows
    return [r for r in rows if rdate(r) > cd]


def acc(rows, level):
    return sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), level))


def comparable_diffs(rows):
    """Signed rate difference (predicted minus true, percentage points) for wrong answers where
    both rates resolve, as in analysis.py."""
    diffs = []
    for r in rows:
        if digit_match(r["true_code"], r.get("predicted_code"), 10):
            continue
        t = rate_pct_for(r["true_code"], r["rulingDate"])
        p = rate_pct_for(r.get("predicted_code"), r["rulingDate"])
        if t is not None and p is not None:
            diffs.append((r, p - t, t, p))
    return diffs


def gate_b(rows):
    cases = build_wrong_cases(rows)
    observed, n, _ = observed_underpay_share(cases)
    if n == 0:
        return {"n": 0}
    under = round(observed * n)
    p1, f1 = permutation_test(observed, run_baseline(cases, lambda c: 4, seed=SEED))
    p2, f2 = permutation_test(observed, run_baseline(cases, lambda c: c["match_level"], seed=SEED + 1))
    passed = (p2 < 0.05) and n >= 30
    if n < 30:
        verdict = f"same direction, too few cases to confirm (n = {n})" if observed > 0.5 else f"not above 50%, too few cases (n = {n})"
    else:
        verdict = "underpays more than chance (Gate B met)" if passed else "not distinguishable from chance (Gate B not met)"
    return {"n": n, "under": under, "share": observed, "p1": format_p(p1, f1), "p2": format_p(p2, f2), "p2_num": p2, "verdict": verdict}


def main():
    models = M.analysis_models()
    ids = [m["model_id"] for m in models]
    UNKNOWN_CUTOFF.update(m["model_id"] for m in models if cutoff_info(m)[0] is None)
    rows_by = {m["model_id"]: M.results_by_model(include_partial=None)[m["model_id"]] for m in models} if False else M.results_by_model()
    assert list(rows_by) == ids
    published = json.loads((ROOT / "data" / "processed" / "analysis_results.json").read_text(encoding="utf-8"))
    res = {}

    out("# v1.1 results (scripts/analyze_v1_1.py)\n")
    out("Pre-registration: PREREG_v1.1.md. Primary = rulings dated after the model's stated training cutoff; if the cutoff is unknown "
        "or after 2026-08-14 the model is labelled \"contamination not ruled out\" and the primary rows are all its rows. "
        "Models on the 200-ruling sample always show n; they are compared only with other models on the same 200 rulings. "
        + DAGGER_NOTE + " "
        "Closed models in the tables: GPT-6 Sol and Claude Haiku/Sonnet/Opus 5.5 (paid, via OpenRouter); no other closed model was tested. Duty figures are MFN-only lower bounds.\n")

    out("## Models and scope\n")
    out("| Model | Provider | Rulings run | Stated cutoff (source) | Contamination status | Primary rows | Reasoning setting |")
    out("|---|---|---|---|---|---|---|")
    for m in models:
        rows = rows_by[m["model_id"]]
        prim = primary_rows(m, rows)
        cd, label = cutoff_info(m)
        out(f"| {m['model_id']} | {m['provider']} | {len(rows)} | {m.get('training_cutoff')} ({m.get('training_cutoff_source', '')[:90]}) | {label} | {len(prim)} | {m.get('reasoning_effort')} |")

    out("\n## Primary results (post-cutoff rows; see the status column above)\n")
    out("| Model | n | 6-digit | 8-digit (headline) | 10-digit | Invalid share | FORMAT share of all | INVENTED share of all |")
    out("|---|---|---|---|---|---|---|---|")
    for m in models:
        mid = m["model_id"]
        prim = primary_rows(m, rows_by[mid])
        n = len(prim)
        inv = [r for r in prim if r.get("tag") == "INVALID_CODE"]
        groups = Counter(group_of(r) for r in inv)
        fmt = groups["a"] + groups["b8"] + groups["b9"] + groups["c"]
        invd = groups["d"] + groups["e"]
        res[mid] = {"n_primary": n, "acc": {l: acc(prim, l) for l in (6, 8, 10)}, "invalid": len(inv), "format": fmt, "invented": invd,
                    "n_full": len(rows_by[mid]), "acc_full": {l: acc(rows_by[mid], l) for l in (6, 8, 10)}}
        out(f"| {mid} | {n} | {ci(acc(prim, 6), n)} | {ci(acc(prim, 8), n)} | {ci(acc(prim, 10), n)} | {ci(len(inv), n)} | {ci(fmt, n)} | {ci(invd, n)} |")
        if mid in published:  # v1.0 numbers must be unchanged
            assert len(rows_by[mid]) == published[mid]["n"]
            assert acc(rows_by[mid], 8) == round(published[mid]["accuracy_by_digit_level"]["8"]["accuracy"] * published[mid]["n"]), mid
            assert len(inv) == published[mid]["n_invalid_code"] or n != published[mid]["n"], mid

    out("\n## Secondary: full sample (all rulings run, regardless of cutoff)\n")
    out("| Model | n | 6-digit | 8-digit | 10-digit | Invalid share |")
    out("|---|---|---|---|---|---|")
    for m in models:
        rows = rows_by[m["model_id"]]
        n = len(rows)
        inv = sum(1 for r in rows if r.get("tag") == "INVALID_CODE")
        out(f"| {m['model_id']} | {n} | {ci(acc(rows, 6), n)} | {ci(acc(rows, 8), n)} | {ci(acc(rows, 10), n)} | {ci(inv, n)} |")

    out("\n## Direction of duty errors (Gate B as pre-registered), median duty at stake, validity check\n")
    out("| Model | rate-changing errors n | underpaid | underpay share (95% CI) | p vs Baseline 1 | p vs Baseline 2 | Gate B verdict | comparable wrong answers n | median duty per $100k (IQR) |")
    out("|---|---|---|---|---|---|---|---|---|")
    vc_lines = ["| Model | wrong answers | wrong and flagged invalid | correct 10-digit answers | correct and flagged | 8-digit-correct answers | 8-digit-correct and flagged |", "|---|---|---|---|---|---|---|"]
    for m in models:
        mid = m["model_id"]
        prim = primary_rows(m, rows_by[mid])
        g = gate_b(prim)
        d = comparable_diffs(prim)
        duty = [abs(x[1]) / 100 * 100000 for x in d]
        med = f"${np.median(duty):,.0f} (${np.percentile(duty, 25):,.0f} to ${np.percentile(duty, 75):,.0f})" if duty else "n/a"
        res[mid]["gate_b"] = g
        res[mid]["duty_n"] = len(duty)
        if g["n"]:
            lo, hi = wilson_ci(g["under"], g["n"])
            out(f"| {mid} | {g['n']} | {g['under']} | {g['share']:.1%} ({max(0, lo):.1%} to {hi:.1%}) | {g['p1']} | {g['p2']} | {g['verdict']} | {len(duty)} | {med} |")
        else:
            out(f"| {mid} | 0 | | | | | no rate-changing errors | {len(duty)} | {med} |")
        wrong = [r for r in prim if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
        right = [r for r in prim if digit_match(r["true_code"], r.get("predicted_code"), 10)]
        r8 = [r for r in prim if digit_match(r["true_code"], r.get("predicted_code"), 8)]
        fl = lambda rs: sum(1 for r in rs if r.get("tag") == "INVALID_CODE")
        wf = fl(wrong)
        vc_lines.append(f"| {mid} | {len(wrong)} | {ci(wf, len(wrong))} | {len(right)} | {fl(right)} of {len(right)} | {len(r8)} | {fl(r8)} of {len(r8)} |")
        res[mid]["validity"] = {"wrong": len(wrong), "wrong_flagged": wf, "correct": len(right), "correct_flagged": fl(right), "c8": len(r8), "c8_flagged": fl(r8)}
    out("\n### Validity check (flag any answer that is not a 10-digit code in the HTS)\n")
    out("\n".join(vc_lines))

    # ---- same-200 comparison
    with M.SUBSET_PATH.open(encoding="utf-8") as f:  # the fixed 200-ruling sample; every model's answers to these are in its cache
        ids200 = [row["rulingNumber"] for row in csv.DictReader(f)]
    if ids200:
        s200 = set(ids200)
        out(f"\n## Same-200 comparison (all models restricted to the {len(s200)} rulings in data/sample200.csv; all dates, secondary)\n")
        out("| Model | n | 6-digit | 8-digit | 10-digit | Invalid share |")
        out("|---|---|---|---|---|---|")
        for m in models:
            rows = [r for r in rows_by[m["model_id"]] if r["rulingNumber"] in s200]
            n = len(rows)
            inv = sum(1 for r in rows if r.get("tag") == "INVALID_CODE")
            out(f"| {m['model_id']} | {n} | {ci(acc(rows, 6), n)} | {ci(acc(rows, 8), n)} | {ci(acc(rows, 10), n)} | {ci(inv, n)} |")

    # ---- same-sample table (all models on the same 200 rulings)
    if ids200:
        out(f"\n## Same-sample table: all {len(models)} models on the same {len(s200)} rulings (data/sample200.csv; all dates, secondary)\n")
        out("The 200 rulings are dated 2026-04 to 2026-08. Models with a cutoff inside that window (Nemotron 3 Ultra, GPT-6 Sol) are scored here on all 200, including rulings before their cutoff. FORMAT / INVENTED is the split of each model's invalid answers on these rulings (groups in review/format_vs_invention.md). Underpay uses the rate-changing errors among these 200 only, so n is small; the share is shown with its Wilson 95% CI and is not a Gate B test.\n")
        out("| Model | n | 8-digit accuracy (95% CI) | Invalid share (95% CI) | FORMAT / INVENTED of invalid | Underpay share (95% CI), n rate-changing |")
        out("|---|---|---|---|---|---|")
        for m in models:
            rows = [r for r in rows_by[m["model_id"]] if r["rulingNumber"] in s200]
            n = len(rows)
            inv = [r for r in rows if r.get("tag") == "INVALID_CODE"]
            gc = Counter(group_of(r) for r in inv)
            fmt = gc["a"] + gc["b8"] + gc["b9"] + gc["c"]
            invd = gc["d"] + gc["e"]
            g = gate_b(rows)
            if g["n"]:
                lo, hi = wilson_ci(g["under"], g["n"])
                und = f"{g['share']:.1%} ({max(0, lo):.1%} to {hi:.1%}), n = {g['n']}"
            else:
                und = "n = 0"
            split = f"{fmt} / {invd}" + (f" ({fmt / len(inv):.0%} / {invd / len(inv):.0%})" if inv else "")
            out(f"| {m['model_id']} | {n} | {ci(acc(rows, 8), n)} | {ci(len(inv), n)} | {split} | {und} |")

    # ---- v1.2: same-sample table on the post-cutoff rulings that all models share
    def shared_table(title, group):
        sets = []
        for m in group:
            cd, _ = cutoff_info(m)
            rows = rows_by[m["model_id"]]
            sets.append({r["rulingNumber"] for r in rows if cd is None or rdate(r) > cd})
        shared = set.intersection(*sets) if sets else set()
        latest = max((cutoff_info(m)[0] for m in group if cutoff_info(m)[0] is not None), default=None)
        out("")
        out(f"## {title}")
        out("")
        out(f"{len(group)} models; {len(shared)} rulings that are after every model's stated cutoff (latest stated cutoff: {latest}; models with no stated cutoff contribute all their rulings) and that every model in the table answered. "
            "FORMAT / INVENTED is the split of each model's invalid answers on these rulings; underpay uses the rate-changing errors among them (small n, not a Gate B test). " + DAGGER_NOTE)
        out("")
        out("| Model | n | 8-digit accuracy (95% CI) | Invalid share (95% CI) | FORMAT / INVENTED of invalid | Underpay share (95% CI), n rate-changing |")
        out("|---|---|---|---|---|---|")
        for m in group:
            rows = [r for r in rows_by[m["model_id"]] if r["rulingNumber"] in shared]
            n = len(rows)
            inv = [r for r in rows if r.get("tag") == "INVALID_CODE"]
            gc = Counter(group_of(r) for r in inv)
            fmt = gc["a"] + gc["b8"] + gc["b9"] + gc["c"]
            invd = gc["d"] + gc["e"]
            g = gate_b(rows)
            if g["n"]:
                lo, hi = wilson_ci(g["under"], g["n"])
                und = f"{g['share']:.1%} ({max(0, lo):.1%} to {hi:.1%}), n = {g['n']}"
            else:
                und = "n = 0"
            split = f"{fmt} / {invd}" + (f" ({fmt / len(inv):.0%} / {invd / len(inv):.0%})" if inv else "")
            out(f"| {m['model_id']} | {n} | {ci(acc(rows, 8), n)} | {ci(len(inv), n)} | {split} | {und} |")

    shared_table("v1.2 same-sample table A: all main-table models on their shared post-cutoff rulings", models)
    group_b = [m for m in models if m.get("sample", "all") == "all"]
    if len(group_b) < len(models):
        shared_table("v1.2 same-sample table B: the models run on all 1,098 rulings, on their shared post-cutoff rulings", group_b)
    else:
        out("")
        out("## v1.2 same-sample table B")
        out("")
        out("Every model has now run all 1,098 rulings (Nemotron 3 Ultra was extended from 200 to 1,098 on 2026-10-10), so table B would repeat table A.")

    # ---- Holm sensitivity for Gate B (added after the first results were seen; not pre-registered)
    out("\n## Sensitivity: Holm correction of the Gate B p-values across all models\n")
    out("Added after the first results were seen, as a sensitivity check; the pre-registered verdicts above are not changed. The p-values are the permutation p-values against Baseline 2 on each model's primary rows (the floor of 1,000 simulations is 1/1001 = 0.000999). Holm step-down adjustment over all models; a model still needs n >= 30 rate-changing errors.\n")
    items = [(m["model_id"], res[m["model_id"]]["gate_b"]) for m in models if res[m["model_id"]]["gate_b"]["n"]]
    mm = len(items)
    order = sorted(range(mm), key=lambda i: items[i][1]["p2_num"])
    adj, running = {}, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (mm - rank) * items[i][1]["p2_num"]))
        adj[items[i][0]] = running
    out("| Model | n | p vs Baseline 2 | Holm-adjusted p | Gate B as pre-registered | Verdict under Holm | Changed? |")
    out("|---|---|---|---|---|---|---|")
    changed = []
    for mid, g in items:
        pre = g["verdict"].startswith("underpays")
        hol = adj[mid] < 0.05 and g["n"] >= 30
        if pre != hol:
            changed.append(mid)
        res[mid]["holm_p"] = adj[mid]
        out(f"| {mid} | {g['n']} | {g['p2']} | {adj[mid]:.4f} | {'met' if pre else 'not met'} | {'met' if hol else 'not met'} | {'YES' if pre != hol else 'no'} |")
    out(f"\nVerdicts that change under Holm: {', '.join(changed) if changed else 'none'}.")

    # ---- sensitivity: exclude rulings with inadequate descriptions (found after pre-registration)
    if FLAGGED:
        out("NLNL## Sensitivity: excluding rulings with an INADEQUATE description (found after pre-registration)NLNL".replace("NL", chr(10)))
        out(f"{len(FLAGGED)} usable rulings are flagged by `scripts/audit_description_quality.py` (review/description_quality.md). Each cell is the main result, then the result without the flagged rulings. Primary rows as above; Gate B exactly as pre-registered. The main results and verdicts are not replaced.")
        out("")
        out("| Model | n main / excl | 8-digit main / excl | Invalid share main / excl | Underpay share (n) main | Underpay share (n) excl | Gate B main / excl |")
        out("|---|---|---|---|---|---|---|")
        sens = {}
        for m in models:
            mid = m["model_id"]
            prim = primary_rows(m, rows_by[mid])
            px = [r for r in prim if r["rulingNumber"] not in FLAGGED]
            gm, gx = res[mid]["gate_b"], gate_b(px)
            inv = lambda rs: sum(1 for r in rs if r.get("tag") == "INVALID_CODE")

            def ushare(g):
                return f"{g['share']:.1%} (n = {g['n']})" if g["n"] else "n/a"

            def verdict(g):
                return "met" if g["n"] and g["verdict"].startswith("underpays") else ("not met" if g["n"] >= 30 else f"too few (n = {g['n']})")

            sens[mid] = {"n": (len(prim), len(px)), "acc8": (acc(prim, 8) / len(prim), acc(px, 8) / len(px)),
                         "invalid": (inv(prim) / len(prim), inv(px) / len(px)), "gate_main": verdict(gm), "gate_excl": verdict(gx),
                         "under_main": gm.get("share"), "under_excl": gx.get("share"), "p2_excl": gx.get("p2")}
            out(f"| {mid} | {len(prim)} / {len(px)} | {acc(prim, 8) / len(prim):.1%} / {acc(px, 8) / len(px):.1%} | {inv(prim) / len(prim):.1%} / {inv(px) / len(px):.1%} | {ushare(gm)} | {ushare(gx)} | {verdict(gm)} / {verdict(gx)} (p vs Baseline 2: {gm.get('p2')} / {gx.get('p2')}) |")
        moved = [mid for mid, v in sens.items() if v["gate_main"] != v["gate_excl"]]
        out("")
        out(f"Gate B verdicts that change when flagged rulings are excluded: {', '.join(moved) if moved else 'none'}.")
        small = [v for k, v in sens.items() if k in ("openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b")]
        strong = [v for k, v in sens.items() if k not in ("openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b")]
        rng = lambda vals: f"{min(vals):.1%} to {max(vals):.1%}"
        out(f"8-digit accuracy, small models: {rng([v['acc8'][0] for v in small])} main, {rng([v['acc8'][1] for v in small])} excluding. Stronger models: {rng([v['acc8'][0] for v in strong])} main, {rng([v['acc8'][1] for v in strong])} excluding.")
        out(f"Underpay share, small models: {rng([v['under_main'] for v in small])} main, {rng([v['under_excl'] for v in small])} excluding. Stronger models: {rng([v['under_main'] for v in strong])} main, {rng([v['under_excl'] for v in strong])} excluding.")
        res["_sensitivity_inadequate"] = sens

    # ---- contamination checks
    out("\n## Contamination check A: memorisation probe (ruling number only, no description)\n")
    out("Question asked: \"What 10-digit HTSUS code did CBP assign in ruling <number>? Reply with JSON {\"hts_code\": ...}\". Seed 20261007, `data/probe_ids.csv`. Exact hits clearly above zero would suggest memorisation.\n")
    out("| Model | probes n | exact 10-digit hits | 8-digit hits | 6-digit hits | parse failures |")
    out("|---|---|---|---|---|---|")
    for m in models:
        d = ROOT / "llm_probes" / M.dir_name(m)
        if not d.exists():
            out(f"| {m['model_id']} | 0 | not run | not run | not run | |")
            continue
        pr = [json.loads(fp.read_text(encoding="utf-8")) for fp in sorted(d.glob("*.json"))]
        n = len(pr)
        res[m["model_id"]]["probe"] = {"n": n, "h10": acc(pr, 10), "h8": acc(pr, 8), "h6": acc(pr, 6)}
        out(f"| {m['model_id']} | {n} | {ci(acc(pr, 10), n)} | {ci(acc(pr, 8), n)} | {ci(acc(pr, 6), n)} | {sum(1 for r in pr if r.get('parse_error'))} |")
    out("\n## Contamination check B: 8-digit accuracy by ruling month (full sample, n per month)\n")
    months = sorted({rdate(r).strftime("%Y-%m") for rows in rows_by.values() for r in rows})
    out("| Model | " + " | ".join(months) + " |")
    out("|---|" + "---|" * len(months))
    for m in models:
        rows = rows_by[m["model_id"]]
        cells = []
        for mo in months:
            rs = [r for r in rows if rdate(r).strftime("%Y-%m") == mo]
            cells.append(f"{acc(rs, 8)}/{len(rs)}" + (f" ({acc(rs, 8) / len(rs):.0%})" if rs else ""))
        out(f"| {m['model_id']} | " + " | ".join(cells) + " |")

    out("\n### Check B detail: 8-digit accuracy before vs after each model's stated cutoff (known cutoff inside the ruling window only)\n")
    out("Descriptive, no test. A drop right after the cutoff would be the signature of memorised rulings; a model with no drop is some evidence against it. Case mix differs by month, so this is not proof either way.\n")
    out("| Model | cutoff | rulings on/before cutoff | 8-digit | rulings after cutoff | 8-digit |")
    out("|---|---|---|---|---|---|")
    for m in models:
        cd, _ = cutoff_info(m)
        rows = rows_by[m["model_id"]]
        if cd is None or not (date(2026, 1, 5) <= cd < LAST_RULING):
            continue
        pre = [r for r in rows if rdate(r) <= cd]
        post = [r for r in rows if rdate(r) > cd]
        out(f"| {m['model_id']} | {cd} | {len(pre)} | {ci(acc(pre, 8), len(pre))} | {len(post)} | {ci(acc(post, 8), len(post))} |")

    # ---- exploratory extras
    n_tests = 0
    out("\n## EXPLORATORY extras (cached data only; pre-registered in PREREG_v1.1.md section 7)\n")
    out("### 1. Paired McNemar tests at 6 and 8 digits, and heading accuracy\n")
    out("Exact binomial test on discordant pairs, on the rulings both models ran. b = first model right and second wrong, c = the reverse.\n")
    out("| Model A | Model B | shared n | level | b | c | p |")
    out("|---|---|---|---|---|---|---|")
    idx = {mid: {r["rulingNumber"]: r for r in rows} for mid, rows in rows_by.items()}
    for a, b in combinations(ids, 2):
        shared = sorted(set(idx[a]) & set(idx[b]))
        for lvl in (6, 8):
            ba = ca = 0
            for rn in shared:
                x = digit_match(idx[a][rn]["true_code"], idx[a][rn].get("predicted_code"), lvl)
                y = digit_match(idx[b][rn]["true_code"], idx[b][rn].get("predicted_code"), lvl)
                ba += x and not y
                ca += y and not x
            p = stats.binomtest(ba, ba + ca, 0.5).pvalue if ba + ca else float("nan")
            n_tests += 1
            out(f"| {a} | {b} | {len(shared)} | {lvl} | {ba} | {ca} | {'n/a' if np.isnan(p) else ('< 0.0001' if p < 0.0001 else f'{p:.4f}')} |")
    out("\n| Model | n | 4-digit heading accuracy | wrong answers | wrong answers with the right heading |")
    out("|---|---|---|---|---|")
    for m in models:
        rows = rows_by[m["model_id"]]
        wr = [r for r in rows if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
        out(f"| {m['model_id']} | {len(rows)} | {ci(acc(rows, 4), len(rows))} | {len(wr)} | {ci(sum(1 for r in wr if digit_match(r['true_code'], r.get('predicted_code'), 4)), len(wr))} |")

    out("\n### 2. Agreement between models on the same 8-digit code (models run on all 1,098 rulings)\n")
    full_ids = [m["model_id"] for m in models if m.get("sample", "all") == "all"]
    by_rn = defaultdict(dict)
    for mid in full_ids:
        for rn, r in idx[mid].items():
            p = r.get("predicted_code")
            if p and len(p) >= 8:
                by_rn[rn][mid] = p[:8]
    out(f"Models: {', '.join(full_ids)} ({len(full_ids)} models). An 8-digit answer needs at least 8 digits.\n")
    out("| Agreement rule | rulings | share of all rulings | accuracy of the agreed code (8-digit) | mean accuracy of each agreeing model alone on the same rulings |")
    out("|---|---|---|---|---|")
    for k in (2, 3):
        hit = tot = 0
        alone = []
        for rn, d in by_rn.items():
            code, cnt = Counter(d.values()).most_common(1)[0]
            if cnt >= k:
                tot += 1
                true8 = usable[rn]["true_code"][:8]
                hit += code == true8
                for mid, c in d.items():
                    if c == code:
                        alone.append(c == true8)
        out(f"| {k}+ models give the same 8-digit code | {tot} | {tot / len(usable):.1%} | {ci(hit, tot)} | {np.mean(alone):.1%} |" if tot else f"| {k}+ | 0 | | | |")
    out("\n### 3. Duty priced at the 8-digit level (secondary)\n")
    out("For answers whose first 8 digits exist in the HTS, both the answer and the true code are priced at 8 digits. Gate B rules as above. 'Added cases' = rate-changing cases beyond the 10-digit analysis.\n")
    out("| Model | answers with first 8 existing | rate-changing at 8 digits (n) | underpaid | underpay share (95% CI) | p vs Baseline 2 | verdict | 10-digit-level n (primary table) | added cases |")
    out("|---|---|---|---|---|---|---|---|---|")
    for m in models:
        mid = m["model_id"]
        prim = primary_rows(m, rows_by[mid])
        cases, diffs, n8 = [], [], 0
        for r in prim:
            pred = r.get("predicted_code")
            if not pred or len(pred) < 8:
                continue
            rel = revision_for_date(datetime.fromisoformat(r["rulingDate"].replace("Z", "")))
            if pred[:8] not in prefixes(rel)[1]:
                continue
            n8 += 1
            lk = load_revision(rel)
            tr, e1 = resolve_rate(lk, r["true_code"][:8])
            pr, e2 = resolve_rate(lk, pred[:8])
            if e1 or e2:
                continue
            tt, tp = classify_rate(tr), classify_rate(pr)
            if tt[0] not in ("ad_valorem", "free") or tp[0] not in ("ad_valorem", "free"):
                continue
            t_pct = 0.0 if tt[0] == "free" else tt[1]
            p_pct = 0.0 if tp[0] == "free" else tp[1]
            diff = p_pct - t_pct
            diffs.append(diff)
            if diff != 0:
                cases.append({"rulingNumber": r["rulingNumber"], "true_code": r["true_code"], "true_pct": t_pct, "release_id": rel,
                              "match_level": deepest_match_level(r["true_code"], pred)})
        nz = [d for d in diffs if d != 0]
        under = sum(1 for d in nz if d < 0)
        base10 = res[mid]["gate_b"]["n"]
        if nz:
            obs = under / len(nz)
            p2, f2 = permutation_test(obs, run_baseline(cases, lambda c: c["match_level"], seed=SEED + 1))
            n_tests += 1
            lo, hi = wilson_ci(under, len(nz))
            verdict = ("underpays more than chance" if (p2 < 0.05 and len(nz) >= 30) else
                       (f"too few cases (n = {len(nz)})" if len(nz) < 30 else "not distinguishable from chance"))
            out(f"| {mid} | {n8} | {len(nz)} | {under} | {obs:.1%} ({max(0, lo):.1%} to {hi:.1%}) | {format_p(p2, f2)} | {verdict} | {base10} | {len(nz) - base10:+d} |")
        else:
            out(f"| {mid} | {n8} | 0 | | | | none | {base10} | |")

    # ---- biggest misses (extra 4)
    allmiss = []
    for m in models:
        for r, diff, t, p in comparable_diffs(rows_by[m["model_id"]]):
            if diff != 0:
                allmiss.append({"model": m["model_id"], "rulingNumber": r["rulingNumber"], "diff_pct": diff, "usd_per_100k": diff * 1000,
                                "true_code": r["true_code"], "true_rate": t, "pred_code": r["predicted_code"], "pred_rate": p,
                                "description": usable[r["rulingNumber"]]["cleaned_description"]})
    all_under = sorted([x for x in allmiss if x["diff_pct"] < 0], key=lambda x: x["diff_pct"])
    all_over = sorted([x for x in allmiss if x["diff_pct"] > 0], key=lambda x: -x["diff_pct"])
    dropped = [(k, x) for k, lst in (("under", all_under[:10]), ("over", all_over[:10])) for x in lst if x["rulingNumber"] in FLAGGED]
    under_l = [x for x in all_under if x["rulingNumber"] not in FLAGGED][:10]
    over_l = [x for x in all_over if x["rulingNumber"] not in FLAGGED][:10]
    bm = ["# Biggest misses (scripts/analyze_v1_1.py; EXPLORATORY)\n",
          "The 10 largest underpayments and 10 largest overpayments per $100,000 declared across all models, among wrong answers where both codes resolve to an ad valorem or free MFN rate. Dollar gap = rate difference x $1,000 per percentage point (MFN lower bound; Chapter 99 duties excluded).\n",
          f"Rows whose ruling has an INADEQUATE description (review/description_quality.md) are dropped and refilled from the next largest. Dropped from the unfiltered top 10 lists: {len(dropped)} row(s)"
          + (": " + "; ".join(f"{k} {x['rulingNumber']} ({x['model']}, ${abs(x['usd_per_100k']):,.0f})" for k, x in dropped) if dropped else "") + ".\n"]
    for title, lst in (("Largest underpayments (model's rate is lower)", under_l), ("Largest overpayments (model's rate is higher)", over_l)):
        bm.append(f"## {title}\n")
        bm.append("| # | Ruling | Model | Official code (MFN rate) | Model's code (MFN rate) | Gap per $100,000 | Description |")
        bm.append("|---|---|---|---|---|---|---|")
        for i, x in enumerate(lst, 1):
            desc = x["description"].replace("|", "/").replace("\n", " ")[:260]
            bm.append(f"| {i} | {x['rulingNumber']} | {x['model']} | {x['true_code']} ({x['true_rate']:g}%) | {x['pred_code']} ({x['pred_rate']:g}%) | ${abs(x['usd_per_100k']):,.0f} {'under' if x['diff_pct'] < 0 else 'over'} | {desc} |")
        bm.append("")
    (ROOT / "review" / "biggest_misses.md").write_text("\n".join(bm), encoding="utf-8")
    (ROOT / "review" / "biggest_misses.json").write_text(json.dumps({"under": under_l, "over": over_l}, indent=2), encoding="utf-8")
    out(f"\n### 4. Biggest misses\n\nSee review/biggest_misses.md (10 largest underpayments and overpayments across all models, after dropping {len(dropped)} row(s) whose ruling has an INADEQUATE description; the ruling ids are tagged in demo_data.json).")

    # ---- cost to run (extra 5)
    out("\n### 5. What it costs to run\n")
    out("| Model | calls | avg input tokens | avg output tokens | avg seconds per call | finish_reason counts | list-price cost per 1,000 rulings |")
    out("|---|---|---|---|---|---|---|")
    for m in models:
        rows = rows_by[m["model_id"]]
        us = [r.get("usage") or r["raw_response"].get("usage") or {} for r in rows]
        tin = np.mean([u.get("prompt_tokens", 0) for u in us]) if us else 0
        tout = np.mean([u.get("completion_tokens", 0) for u in us]) if us else 0
        lat = [r["latency_s"] for r in rows if r.get("latency_s")] or [u["total_time"] for u in us if u.get("total_time")]
        fin = Counter(r.get("finish_reason") or ((r["raw_response"].get("choices") or [{}])[0].get("finish_reason")) for r in rows)
        pin, pout = m.get("price_in_per_1m"), m.get("price_out_per_1m")
        cost = "free tier" if m["provider"] == "groq" or (pin == 0 and pout == 0) else f"${1000 * (tin * pin + tout * pout) / 1e6:.2f}"
        out(f"| {m['model_id']} | {len(rows)} | {tin:.0f} | {tout:.0f} | {np.mean(lat):.1f} | {dict(fin)} | {cost} |" if lat else
            f"| {m['model_id']} | {len(rows)} | {tin:.0f} | {tout:.0f} | n/a | {dict(fin)} | {cost} |")
    out(f"\n**Number of extra (exploratory) hypothesis tests run: {n_tests}** (McNemar pairs at two levels, plus the 8-digit-level baseline tests). The other extras are descriptive.")

    (ROOT / "review" / "v1_1_results.md").write_text("\n".join(REPORT) + "\n", encoding="utf-8")
    (ROOT / "review" / "v1_1_results.json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("\n".join(REPORT))


if __name__ == "__main__":
    main()
