"""
v1.2 time-drift test (added after the v1.2 results, no new API calls).

GPT-6 Sol scores 58.9% at 8 digits on the 560 rulings up to its stated cutoff (2026-04-20) and 49.6% on the
538 after it. If later rulings are simply harder, models that cannot have seen any ruling should drop at the
same split date too. This script splits every model's full-sample answers at the same date (on/before vs
after 2026-04-20) and reports 8-digit accuracy on each side with Wilson 95% CIs, the difference in points
and two-sided two-proportion tests (pooled z-test and Fisher exact).

Models: gpt-oss-20b and gpt-oss-120b (cutoff 2024-06-01, cannot have seen any 2026 ruling), allam-2-7b,
DeepSeek V4.1 Flash, GLM 5.3 and Kimi K3 (Baseten runs, no stated cutoff), GPT-6 Sol (reference), the three
Claude models (cutoff 2026-06-30, so their split here is a different, earlier date and only descriptive) and
the three OpenRouter replication runs (same models as the Baseten runs). Nemotron ran on 200 rulings and
is left out. Writes review/time_drift.md and review/time_drift.json.
"""
import json
import sys
from datetime import datetime, date
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
from analysis import digit_match, wilson_ci  # noqa: E402

SPLIT = date(2026, 4, 20)
DAG = " †"


def rdate(r):
    return datetime.fromisoformat(r["rulingDate"].replace("Z", "")).date()


def cell(k, n):
    lo, hi = wilson_ci(k, n)
    return f"{k / n:.1%} ({max(0.0, lo):.1%} to {hi:.1%})"


def pstr(p):
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"


def main():
    cfg = {m["model_id"]: m for m in M.load()}
    order = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b", "deepseek-ai/DeepSeek-V4.1-Flash",
             "zai-org/GLM-5.3", "moonshotai/Kimi-K3", "openai/gpt-6-sol", "anthropic/claude-haiku-5.5",
             "anthropic/claude-sonnet-5.5", "anthropic/claude-opus-5.5", "replication/moonshotai/kimi-k3",
             "replication/deepseek/deepseek-v4.1-flash", "replication/z-ai/glm-5.3"]
    res, rows_md = {}, []
    for mid in order:
        rows = M.load_results(mid)
        before = [r for r in rows if rdate(r) <= SPLIT]
        after = [r for r in rows if rdate(r) > SPLIT]
        kb = sum(1 for r in before if digit_match(r["true_code"], r.get("predicted_code"), 8))
        ka = sum(1 for r in after if digit_match(r["true_code"], r.get("predicted_code"), 8))
        nb, na = len(before), len(after)
        pb, pa = kb / nb, ka / na
        pool = (kb + ka) / (nb + na)
        se = (pool * (1 - pool) * (1 / nb + 1 / na)) ** 0.5
        z = (pb - pa) / se if se else 0.0
        p_z = float(2 * stats.norm.sf(abs(z))) if se else 1.0
        p_f = float(stats.fisher_exact([[kb, nb - kb], [ka, na - ka]])[1])
        cd = cfg[mid].get("training_cutoff", "unknown")
        res[mid] = {"cutoff": cd, "n_before": nb, "k_before": kb, "n_after": na, "k_after": ka,
                    "acc_before": pb, "acc_after": pa, "drop_points": (pb - pa) * 100, "p_z": p_z, "p_fisher": p_f}
        name = mid.split("/", 1)[1] if mid.startswith("replication/") else mid
        label = ("replication: " if mid.startswith("replication/") else "") + name
        try:
            date.fromisoformat(cd)
            c = cd
        except ValueError:
            c = "none stated" + DAG
        rows_md.append(f"| {label} | {c} | {nb} | {cell(kb, nb)} | {na} | {cell(ka, na)} | {(pb - pa) * 100:+.1f} | {pstr(p_z)} | {pstr(p_f)} |")
    L = ["# Time-drift test: 8-digit accuracy before vs after 2026-04-20 (scripts/analyze_time_drift.py)\n",
         "Added after the v1.2 results were seen; no new API calls. Rulings dated on or before 2026-04-20 vs after it, all 1,098 rulings per model, "
         "8-digit accuracy with Wilson 95% CIs. 'Drop' = before minus after, in percentage points. p-values: two-sided pooled two-proportion z-test and Fisher exact test (descriptive, not corrected for multiple comparison; "
         "13 rows). GPT-6 Sol's stated cutoff is the split date. gpt-oss-20b and gpt-oss-120b have a 2024 cutoff and cannot have seen any ruling. "
         "The Claude models' stated cutoff is 2026-06-30, so the split here is not their cutoff and only shows the time trend. † no stated cutoff.\n",
         "| Model | Stated cutoff | n up to 2026-04-20 | 8-digit up to 2026-04-20 | n after | 8-digit after | drop (points) | p (z-test) | p (Fisher) |",
         "|---|---|---|---|---|---|---|---|---|"] + rows_md
    # power of the control: could the 2024-cutoff models have shown a drop as large (in relative terms) as Sol's?
    sol = res["openai/gpt-6-sol"]
    rel = (sol["acc_before"] - sol["acc_after"]) / sol["acc_before"]
    L += ["", "## Could the 2024-cutoff models have shown a drop like Sol's?", "",
          f"Sol's drop is {sol['drop_points']:.1f} points, a relative drop of {rel:.1%}. For each 2024-cutoff model, the table gives the drop in points that the same relative drop would be "
          "on its own pre-split accuracy, and the power of the two-sided z-test (alpha 0.05, normal approximation) to detect it with the observed n. "
          "A control with low power cannot show 'no drop'; it only fails to show one.", "",
          "| Model | observed before | drop of the same relative size (points) | power to detect it |", "|---|---|---|---|"]
    power = {}
    for mid in ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
        r = res[mid]
        p1 = max(r["acc_before"], 1 / r["n_before"])
        p2 = p1 * (1 - rel)
        se = (p1 * (1 - p1) / r["n_before"] + p2 * (1 - p2) / r["n_after"]) ** 0.5
        pw = float(stats.norm.sf(1.96 - (p1 - p2) / se) + stats.norm.cdf(-1.96 - (p1 - p2) / se))
        power[mid] = {"relative_drop": rel, "expected_points": (p1 - p2) * 100, "power": pw}
        L.append(f"| {mid} | {r['acc_before']:.1%} | {(p1 - p2) * 100:.2f} | {pw:.0%} |")
    res["_power_gpt_oss"] = power
    out = "\n".join(L) + "\n"
    (ROOT / "review" / "time_drift.md").write_text(out, encoding="utf-8")
    (ROOT / "review" / "time_drift.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
