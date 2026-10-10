"""
v1.2 part C (PREREG_v1.2.md section 4): provider replication. Each of Kimi K3, DeepSeek V4.1 Flash
and GLM 5.3 was run on all 1,098 rulings on Baseten (v1.1, primary) and again through OpenRouter
with Baseten excluded. Per model this reports, on the same rulings:
  - agreement: share of rulings with an identical predicted code, and with an identical first 8 digits
    (where both answers have at least 8 digits);
  - 8-digit accuracy of each run and the difference (OpenRouter minus Baseten) with a 95% CI from a
    paired bootstrap (10,000 resamples of rulings, seed 20261010);
  - validity: how many answers have a different valid/invalid tag, and the invalid share of each run;
  - the serving providers recorded in the OpenRouter responses (counts).
The replication never enters a main table. No threshold for "replicated" is set; numbers are reported
as they are. Writes review/replication.md and review/replication.json.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402
from analysis import digit_match, wilson_ci  # noqa: E402

SEED = 20261010
N_BOOT = 10000
# replication config id -> primary (Baseten, v1.1) config id
PAIRS = {"replication/moonshotai/kimi-k3": "moonshotai/Kimi-K3",
         "replication/deepseek/deepseek-v4.1-flash": "deepseek-ai/DeepSeek-V4.1-Flash",
         "replication/z-ai/glm-5.3": "zai-org/GLM-5.3"}


def main():
    res, L = {}, ["# Provider replication (scripts/analyze_replication.py)\n",
                  "Primary = the v1.1 Baseten run; replication = the same model through OpenRouter with Baseten excluded. Same 1,098 rulings, same prompt, temperature 0. "
                  "Difference = OpenRouter minus Baseten, 95% CI from a paired bootstrap (10,000 resamples, seed 20261010). The GLM runs also differ in reasoning setting "
                  "(Baseten: thinking disabled; OpenRouter: low effort, because it cannot be turned off there), and OpenRouter routes each call to one of several providers.\n",
                  "| Model | rulings both | identical code | identical first 8 digits (both >= 8 digits) | 8-digit accuracy Baseten | 8-digit accuracy OpenRouter | difference (95% CI) | invalid share Baseten / OpenRouter | answers with a different valid/invalid tag |",
                  "|---|---|---|---|---|---|---|---|---|"]
    for rid, pid in PAIRS.items():
        rep = {r["rulingNumber"]: r for r in M.load_results(rid)}
        pri = {r["rulingNumber"]: r for r in M.load_results(pid)}
        common = sorted(set(rep) & set(pri))
        n = len(common)
        if n == 0:
            continue
        same = sum(1 for rn in common if rep[rn].get("predicted_code") == pri[rn].get("predicted_code"))
        both8 = [rn for rn in common if len(rep[rn].get("predicted_code") or "") >= 8 and len(pri[rn].get("predicted_code") or "") >= 8]
        same8 = sum(1 for rn in both8 if rep[rn]["predicted_code"][:8] == pri[rn]["predicted_code"][:8])
        a = np.array([digit_match(pri[rn]["true_code"], pri[rn].get("predicted_code"), 8) for rn in common], dtype=float)
        b = np.array([digit_match(rep[rn]["true_code"], rep[rn].get("predicted_code"), 8) for rn in common], dtype=float)
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, n, size=(N_BOOT, n))
        diffs = (b[idx].mean(axis=1) - a[idx].mean(axis=1))
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        diff = b.mean() - a.mean()
        inv_a = sum(1 for rn in common if pri[rn].get("tag") == "INVALID_CODE")
        inv_b = sum(1 for rn in common if rep[rn].get("tag") == "INVALID_CODE")
        tagdiff = sum(1 for rn in common if (pri[rn].get("tag") == "INVALID_CODE") != (rep[rn].get("tag") == "INVALID_CODE"))
        provs = Counter(str(r.get("provider_served")) for r in rep.values())
        res[rid] = {"n": n, "identical_code": same, "identical_8": same8, "both_ge8": len(both8), "acc8_baseten": float(a.mean()),
                    "acc8_openrouter": float(b.mean()), "diff": float(diff), "ci": [float(lo), float(hi)], "invalid": [inv_a, inv_b],
                    "tag_differs": tagdiff, "providers": dict(provs.most_common())}
        L.append(f"| {pid} | {n} | {same} ({same / n:.1%}) | {same8} of {len(both8)} ({same8 / max(1, len(both8)):.1%}) | {int(a.sum())} ({a.mean():.1%}) | {int(b.sum())} ({b.mean():.1%}) | "
                 f"{diff * 100:+.1f} points ({lo * 100:+.1f} to {hi * 100:+.1f}) | {inv_a / n:.1%} / {inv_b / n:.1%} | {tagdiff} |")
    L += ["", "## Serving providers recorded in the OpenRouter responses", ""]
    for rid, r in res.items():
        L.append(f"- {PAIRS[rid]}: " + ", ".join(f"{k} {v}" for k, v in r["providers"].items()))
    out = "\n".join(L) + "\n"
    (ROOT / "review" / "replication.md").write_text(out, encoding="utf-8")
    (ROOT / "review" / "replication.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
