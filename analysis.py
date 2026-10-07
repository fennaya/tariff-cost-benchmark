"""
Phase 6: analysis. Every number here is computed from llm_logs/ (Phase 5's cached raw
responses) and data/processed/ (Phases 1-3's cached, script-produced data) -- nothing is
hand-typed or estimated. If llm_logs/ is empty (no LLM key was available, see
BLOCKERS.md), this refuses to run rather than report fabricated numbers.

Per model: accuracy at 2/4/6/8/10 digits with Wilson 95% CIs; rate-difference
distribution for wrong answers; a two-sided binomial direction test (underpay share vs
50%) among wrong answers with a nonzero rate difference; the share of wrong answers with
a zero rate difference ("free errors"); duty-at-stake per $100,000 declared value
(median/IQR + bootstrap 95% CI); and error depth (first digit level of divergence).
All statistics are descriptive -- no causal claims.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts" if (Path(__file__).resolve().parent / "scripts").exists() else Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from parse_duty_rates import revision_for_date, load_revision, classify_rate, resolve_rate  # noqa: E402
from datetime import datetime  # noqa: E402

ROOT = Path(__file__).resolve().parent
LLM_LOGS_DIR = ROOT / "llm_logs"
FIGURES_DIR = ROOT / "figures"
DIGIT_LEVELS = [2, 4, 6, 8, 10]
BOOTSTRAP_N = 10000
BOOTSTRAP_SEED = 20260928  # fixed for reproducibility of the reported CI, not to shape the result


def wilson_ci(successes, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1 + z ** 2 / n
    center = p + z ** 2 / (2 * n)
    margin = z * ((p * (1 - p) / n + z ** 2 / (4 * n ** 2)) ** 0.5)
    return ((center - margin) / denom, (center + margin) / denom)


def load_model_results(model_dir: Path):
    return [json.loads(fp.read_text(encoding="utf-8")) for fp in sorted(model_dir.glob("*.json"))]


def digit_match(true_code, pred_code, level):
    """Whether the prediction's first `level` digits match the truth. A prediction
    shorter than `level` digits (e.g. the model gave only an 8-digit code, omitting the
    10-digit statistical suffix) cannot match at that level or deeper, but still gets
    credit at shallower levels it actually specified -- an 8-digit-only answer that gets
    the first 8 digits right is not the same failure as one that gets chapter/heading
    wrong, and collapsing them loses exactly the distinction Gate 4/6 are meant to show."""
    if not pred_code or len(pred_code) < level:
        return False
    return true_code[:level] == pred_code[:level]


def error_depth(true_code, pred_code):
    """First digit level (2/4/6/8/10) at which prediction diverges from truth, where
    "diverges" includes the prediction simply not specifying that many digits (e.g. an
    8-digit-only answer is scored as diverging at level 10, not level 2, if its first 8
    digits were actually correct). None if the codes match exactly (not an error)."""
    if not pred_code:
        return 2  # nothing to compare: diverges immediately
    for level in DIGIT_LEVELS:
        if len(pred_code) < level or true_code[:level] != pred_code[:level]:
            return level
    return None


def rate_pct_for(code, ruling_date_str):
    """Resolve a 10-digit code's ad valorem/free rate (as a percent, 0 for free) in the
    HTS revision that was in force on the ruling's date. Returns None if not resolvable
    to ad valorem/free (specific, compound, other, or code not found)."""
    if not code or len(code) != 10:
        return None
    ruling_date = datetime.fromisoformat(ruling_date_str.replace("Z", ""))
    release_id = revision_for_date(ruling_date)
    lookup = load_revision(release_id)
    rate_str, err = resolve_rate(lookup, code)
    if err:
        return None
    rate_type, pct = classify_rate(rate_str)
    if rate_type == "free":
        return 0.0
    if rate_type == "ad_valorem":
        return pct
    return None


def bootstrap_ci(values, statistic=np.median, n_boot=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    if len(values) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    arr = np.asarray(values)
    boot_stats = [statistic(rng.choice(arr, size=len(arr), replace=True)) for _ in range(n_boot)]
    return (float(np.percentile(boot_stats, 2.5)), float(np.percentile(boot_stats, 97.5)))


def analyze_model(model_id, rows):
    n = len(rows)
    metrics = {"model": model_id, "n": n}

    # 1. Accuracy at each digit level, Wilson 95% CI.
    accuracy = {}
    for level in DIGIT_LEVELS:
        successes = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), level))
        lo, hi = wilson_ci(successes, n)
        accuracy[level] = {"accuracy": successes / n if n else float("nan"), "wilson_95ci": [lo, hi], "n": n}
    metrics["accuracy_by_digit_level"] = accuracy

    wrong = [r for r in rows if not digit_match(r["true_code"], r.get("predicted_code"), 10)]
    metrics["n_wrong"] = len(wrong)
    metrics["n_invalid_code"] = sum(1 for r in rows if r.get("tag") == "INVALID_CODE")

    # 2 & 4. Rate differences for wrong answers where both true and predicted codes
    # resolve to ad valorem/free.
    rate_diffs = []
    zero_diff_count = 0
    usable_wrong_for_rate = 0
    for r in wrong:
        true_pct = rate_pct_for(r["true_code"], r["rulingDate"])
        pred_pct = rate_pct_for(r.get("predicted_code"), r["rulingDate"])
        if true_pct is None or pred_pct is None:
            continue
        usable_wrong_for_rate += 1
        diff = pred_pct - true_pct
        rate_diffs.append(diff)
        if diff == 0:
            zero_diff_count += 1
    metrics["n_wrong_with_usable_rates"] = usable_wrong_for_rate
    metrics["share_wrong_zero_rate_diff"] = (
        zero_diff_count / usable_wrong_for_rate if usable_wrong_for_rate else float("nan")
    )

    # 3. Direction test among nonzero-diff wrong answers.
    nonzero_diffs = [d for d in rate_diffs if d != 0]
    underpay_count = sum(1 for d in nonzero_diffs if d < 0)  # predicted rate lower than true -> underpay
    if nonzero_diffs:
        binom = stats.binomtest(underpay_count, len(nonzero_diffs), 0.5, alternative="two-sided")
        metrics["direction_test"] = {
            "n_nonzero_diff": len(nonzero_diffs),
            "underpay_count": underpay_count,
            "underpay_share": underpay_count / len(nonzero_diffs),
            "binomial_p_value_vs_50pct": binom.pvalue,
        }
    else:
        metrics["direction_test"] = None

    # 5. Duty at stake per $100,000 declared value = |rate_diff_pct| / 100 * 100000.
    duty_at_stake = [abs(d) / 100 * 100000 for d in rate_diffs]
    if duty_at_stake:
        median = float(np.median(duty_at_stake))
        q1, q3 = float(np.percentile(duty_at_stake, 25)), float(np.percentile(duty_at_stake, 75))
        ci = bootstrap_ci(duty_at_stake, np.median)
        metrics["duty_at_stake_per_100k"] = {
            "median": median, "iqr": [q1, q3], "bootstrap_95ci_of_median": list(ci), "n": len(duty_at_stake),
        }
    else:
        metrics["duty_at_stake_per_100k"] = None

    # 6. Error depth among wrong answers.
    depths = [error_depth(r["true_code"], r.get("predicted_code")) for r in wrong]
    depth_counts = {level: depths.count(level) for level in DIGIT_LEVELS}
    metrics["error_depth_distribution"] = depth_counts

    return metrics


def make_figures(all_metrics):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    models = list(all_metrics.keys())
    if not models:
        return

    # Accuracy by digit level, one bar group per model.
    fig, ax = plt.subplots(figsize=(7, 5))
    width = 0.8 / max(len(models), 1)
    for i, model_id in enumerate(models):
        acc = all_metrics[model_id]["accuracy_by_digit_level"]
        xs = [j + i * width for j in range(len(DIGIT_LEVELS))]
        ys = [acc[level]["accuracy"] for level in DIGIT_LEVELS]
        errs_lo = [ys[j] - acc[DIGIT_LEVELS[j]]["wilson_95ci"][0] for j in range(len(DIGIT_LEVELS))]
        errs_hi = [acc[DIGIT_LEVELS[j]]["wilson_95ci"][1] - ys[j] for j in range(len(DIGIT_LEVELS))]
        ax.bar(xs, ys, width=width, label=model_id, yerr=[errs_lo, errs_hi], capsize=3)
    ax.set_xticks([j + width * (len(models) - 1) / 2 for j in range(len(DIGIT_LEVELS))])
    ax.set_xticklabels([str(d) for d in DIGIT_LEVELS])
    ax.set_xlabel("HTS digit level")
    ax.set_ylabel("Exact-match accuracy")
    ax.set_ylim(0, 1)
    ax.set_title("Classification accuracy by digit level (Wilson 95% CI)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "accuracy_by_digit_level.png", dpi=150)
    plt.close(fig)

    # Direction test: underpay share per model.
    fig, ax = plt.subplots(figsize=(6, 4))
    dir_models = [m for m in models if all_metrics[m]["direction_test"]]
    if dir_models:
        shares = [all_metrics[m]["direction_test"]["underpay_share"] for m in dir_models]
        ax.bar(dir_models, shares, color="firebrick")
        ax.axhline(0.5, color="black", linestyle="--", linewidth=1, label="50% (no bias)")
        ax.set_ylabel("Share of wrong answers that underpay")
        ax.set_ylim(0, 1)
        ax.set_title("Direction of classification errors")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "direction_bias.png", dpi=150)
    plt.close(fig)

    # Duty-at-stake distribution per model (boxplot-style via IQR whiskers we already have).
    fig, ax = plt.subplots(figsize=(6, 4))
    stake_models = [m for m in models if all_metrics[m]["duty_at_stake_per_100k"]]
    if stake_models:
        medians = [all_metrics[m]["duty_at_stake_per_100k"]["median"] for m in stake_models]
        q1s = [all_metrics[m]["duty_at_stake_per_100k"]["iqr"][0] for m in stake_models]
        q3s = [all_metrics[m]["duty_at_stake_per_100k"]["iqr"][1] for m in stake_models]
        yerr = [[m_ - q1 for m_, q1 in zip(medians, q1s)], [q3 - m_ for m_, q3 in zip(medians, q3s)]]
        ax.bar(stake_models, medians, yerr=yerr, capsize=4, color="steelblue")
        ax.set_ylabel("Duty at stake per USD 100,000 declared value (USD)")
        ax.set_title("Median duty at stake on wrong answers (IQR whiskers)")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "duty_at_stake.png", dpi=150)
    plt.close(fig)

    # Error depth distribution per model.
    fig, ax = plt.subplots(figsize=(6, 4))
    width = 0.8 / max(len(models), 1)
    for i, model_id in enumerate(models):
        depth_counts = all_metrics[model_id]["error_depth_distribution"]
        total = sum(depth_counts.values()) or 1
        xs = [j + i * width for j in range(len(DIGIT_LEVELS))]
        ys = [depth_counts.get(level, 0) / total for level in DIGIT_LEVELS]
        ax.bar(xs, ys, width=width, label=model_id)
    ax.set_xticks([j + width * (len(models) - 1) / 2 for j in range(len(DIGIT_LEVELS))])
    ax.set_xticklabels([str(d) for d in DIGIT_LEVELS])
    ax.set_xlabel("First digit level where prediction diverges from truth")
    ax.set_ylabel("Share of wrong answers")
    ax.set_title("Error depth")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "error_depth.png", dpi=150)
    plt.close(fig)

    print(f"Wrote figures to {FIGURES_DIR}")


def main():
    if not LLM_LOGS_DIR.exists() or not any(LLM_LOGS_DIR.iterdir()):
        print("llm_logs/ is empty -- no Phase 5 data to analyze. This is expected while "
              "no free LLM API key is available (see BLOCKERS.md); refusing to fabricate "
              "results. Nothing written.", file=sys.stderr)
        sys.exit(1)

    # A model_id containing "/" (e.g. "openai/gpt-oss-20b") nests one level deeper than
    # llm_logs/<model_id>/ -- find every directory that directly holds *.json result
    # files, at any depth, rather than assuming a fixed nesting level (a prior version
    # of this loop only checked the top level and silently dropped every nested model's
    # results -- found 2026-10-01 when only allam-2-7b, the one un-nested model, showed
    # up in a 3-model run).
    all_metrics = {}
    for model_id, rows in M.results_by_model().items():
        if not rows:
            continue
        all_metrics[model_id] = analyze_model(model_id, rows)

    out_path = ROOT / "data" / "processed" / "analysis_results.json"
    out_path.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    make_figures(all_metrics)
    for model_id, m in all_metrics.items():
        print(f"\n=== {model_id} (n={m['n']}) ===")
        print("Accuracy by digit level:")
        for level, a in m["accuracy_by_digit_level"].items():
            print(f"  {level}-digit: {a['accuracy']:.3f} (95% CI {a['wilson_95ci']})")
        print(f"Wrong: {m['n_wrong']} ({m['n_invalid_code']} invalid codes)")
        if m["direction_test"]:
            dt = m["direction_test"]
            print(f"Direction test: {dt['underpay_share']:.3f} underpay "
                  f"(n={dt['n_nonzero_diff']}, p={dt['binomial_p_value_vs_50pct']:.4f})")
        if m["duty_at_stake_per_100k"]:
            d = m["duty_at_stake_per_100k"]
            print(f"Duty at stake per $100k: median ${d['median']:.2f}, IQR {d['iqr']}, "
                  f"bootstrap 95% CI of median {d['bootstrap_95ci_of_median']}")


if __name__ == "__main__":
    main()
