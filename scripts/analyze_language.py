"""
Round 2, Part 4, steps 3-4: paired language comparison (English vs. approved French /
Arabic translations of the same products) and a power note for how small a gap this
sample could actually detect.

Pairing is at the ruling level: the SAME ruling, SAME model, English prediction vs. its
approved-translation prediction. Three comparisons:
  - 3-way set (both languages approved, n=84): EN vs FR and EN vs AR on the identical
    84-ruling set, so all three languages are directly comparable to each other.
  - EN vs FR on all French-approved rows (n=93, a superset of the 3-way set).
  - EN vs AR on all Arabic-approved rows (n=90, a superset of the 3-way set).

For each pair: McNemar's exact test (binomial on discordant pairs) at 6/8/10 digits,
paired bootstrap for duty-at-stake per $100,000, and underpay share per language.

Power note: Monte Carlo simulation under a simplifying independence assumption (each
language's correctness draw is independent given its own true accuracy -- real
correlation between languages, if positive as expected, would make McNemar's test MORE
powerful than this estimate, so this is a conservative/upper-bound estimate of the
minimum detectable difference, not an exact one).
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from parse_duty_rates import revision_for_date, load_revision, classify_rate, resolve_rate  # noqa: E402

LLM_LOGS_DIR = ROOT / "llm_logs"
MARKED_PATH = ROOT / "review" / "translation_review_marked.csv"
REVIEW_DIR = ROOT / "review"
DIGIT_LEVELS = [8, 6, 10]  # 8-digit (duty-bearing) is the lead accuracy figure per user request 2026-10-02
N_BOOT = 10000
SEED = 20261002


def load_marks():
    with MARKED_PATH.open(encoding="utf-8-sig") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def load_lang_results(model_id, lang=None):
    d = LLM_LOGS_DIR / model_id if lang is None else LLM_LOGS_DIR / model_id / f"lang_{lang}"
    if not d.exists():
        return {}
    return {json.loads(fp.read_text(encoding="utf-8"))["rulingNumber"]: json.loads(fp.read_text(encoding="utf-8"))
            for fp in d.glob("*.json")}


def digit_match(true_code, pred_code, level):
    if not pred_code or len(pred_code) < level:
        return False
    return true_code[:level] == pred_code[:level]


def rate_pct_for(code, ruling_date_str):
    if not code or len(code) != 10:
        return None
    ruling_date = datetime.fromisoformat(ruling_date_str.replace("Z", ""))
    lookup = load_revision(revision_for_date(ruling_date))
    rate_str, err = resolve_rate(lookup, code)
    if err:
        return None
    rate_type, pct = classify_rate(rate_str)
    return 0.0 if rate_type == "free" else (pct if rate_type == "ad_valorem" else None)


def mcnemar_exact(b, c):
    """b = correct-in-A-only count, c = correct-in-B-only count (discordant pairs).
    Exact two-sided binomial test, standard for small-to-moderate discordant counts."""
    n = b + c
    if n == 0:
        return float("nan"), 0
    return stats.binomtest(min(b, c), n, 0.5, alternative="two-sided").pvalue, n


def paired_comparison(model_id, ruling_ids, en_results, other_results, other_label):
    rows = []
    for rn in ruling_ids:
        en = en_results.get(rn)
        other = other_results.get(rn)
        if en is None or other is None:
            continue
        rows.append((rn, en, other))

    out = {"n": len(rows), "digit_levels": {}}
    for level in DIGIT_LEVELS:
        en_correct = [digit_match(en["true_code"], en.get("predicted_code"), level) for _, en, _ in rows]
        other_correct = [digit_match(en["true_code"], other.get("predicted_code"), level) for _, en, other in rows]
        b = sum(1 for ec, oc in zip(en_correct, other_correct) if ec and not oc)  # EN only
        c = sum(1 for ec, oc in zip(en_correct, other_correct) if oc and not ec)  # other only
        p, n_discordant = mcnemar_exact(b, c)
        out["digit_levels"][level] = {
            "en_accuracy": np.mean(en_correct) if en_correct else float("nan"),
            f"{other_label}_accuracy": np.mean(other_correct) if other_correct else float("nan"),
            "en_only_correct": b, f"{other_label}_only_correct": c,
            "n_discordant": n_discordant, "mcnemar_p": p,
        }

    # Paired duty-at-stake (wrong-at-10-digit cases with resolvable rates) + bootstrap.
    en_diffs, other_diffs = [], []
    en_underpay, en_nonzero = 0, 0
    other_underpay, other_nonzero = 0, 0
    for rn, en, other in rows:
        true_pct = rate_pct_for(en["true_code"], en["rulingDate"])
        if true_pct is None:
            continue
        en_pct = rate_pct_for(en.get("predicted_code"), en["rulingDate"])
        other_pct = rate_pct_for(other.get("predicted_code"), other["rulingDate"])
        if en_pct is not None and en["true_code"] != en.get("predicted_code"):
            d = en_pct - true_pct
            en_diffs.append(abs(d) / 100 * 100000)
            if d != 0:
                en_nonzero += 1
                if d < 0:
                    en_underpay += 1
        if other_pct is not None and other["true_code"] != other.get("predicted_code"):
            d = other_pct - true_pct
            other_diffs.append(abs(d) / 100 * 100000)
            if d != 0:
                other_nonzero += 1
                if d < 0:
                    other_underpay += 1

    rng = np.random.default_rng(SEED)

    def boot_median_diff(a, b):
        if not a or not b:
            return (float("nan"), float("nan"), float("nan"))
        a_arr, b_arr = np.array(a), np.array(b)
        diffs = [np.median(rng.choice(a_arr, len(a_arr), replace=True)) -
                 np.median(rng.choice(b_arr, len(b_arr), replace=True)) for _ in range(N_BOOT)]
        return (float(np.median(diffs)), float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)))

    stake_diff, stake_lo, stake_hi = boot_median_diff(other_diffs, en_diffs)
    out["duty_at_stake"] = {
        "en_median": float(np.median(en_diffs)) if en_diffs else float("nan"),
        f"{other_label}_median": float(np.median(other_diffs)) if other_diffs else float("nan"),
        "bootstrap_median_diff": stake_diff, "bootstrap_95ci": [stake_lo, stake_hi],
    }
    out["underpay_share"] = {
        "en": (en_underpay / en_nonzero if en_nonzero else float("nan")),
        other_label: (other_underpay / other_nonzero if other_nonzero else float("nan")),
    }
    return out


def power_note(n, baseline_acc, n_sims=2000, seed=SEED):
    """Smallest |delta| in accuracy such that McNemar's exact test (alpha=0.05) rejects
    at >=80% power, under an independence simplification (see module docstring)."""
    rng = np.random.default_rng(seed)
    for delta in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        p2 = min(max(baseline_acc + delta, 0.0), 1.0)
        rejections = 0
        for _ in range(n_sims):
            a = rng.random(n) < baseline_acc
            b = rng.random(n) < p2
            disc_b = int(np.sum(a & ~b))
            disc_c = int(np.sum(b & ~a))
            if disc_b + disc_c == 0:
                continue
            p = stats.binomtest(min(disc_b, disc_c), disc_b + disc_c, 0.5, alternative="two-sided").pvalue
            if p < 0.05:
                rejections += 1
        power = rejections / n_sims
        if power >= 0.80:
            return delta, power
    return None, None


def main():
    marks = load_marks()
    both_ok = [rn for rn, m in marks.items() if m.get("fr_ok") == "OK" and m.get("ar_ok") == "OK"]
    fr_ok = [rn for rn, m in marks.items() if m.get("fr_ok") == "OK"]
    ar_ok = [rn for rn, m in marks.items() if m.get("ar_ok") == "OK"]
    print(f"3-way (both OK): {len(both_ok)}; FR-OK: {len(fr_ok)}; AR-OK: {len(ar_ok)}")

    models = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b"]
    all_out = {"n_both_ok": len(both_ok), "n_fr_ok": len(fr_ok), "n_ar_ok": len(ar_ok), "models": {}}

    lines = [
        "# Language comparison (Round 2, Part 4)\n",
        f"3-way set (both languages approved): **{len(both_ok)}/100**. "
        f"EN-vs-FR set (French approved): **{len(fr_ok)}/100**. "
        f"EN-vs-AR set (Arabic approved): **{len(ar_ok)}/100**.\n",
    ]

    for model_id in models:
        en_results = load_lang_results(model_id)
        fr_results = load_lang_results(model_id, "fr")
        ar_results = load_lang_results(model_id, "ar")
        if not en_results or not fr_results or not ar_results:
            print(f"Skipping {model_id}: missing results", file=sys.stderr)
            continue

        model_out = {}
        model_out["en_vs_fr_all_approved"] = paired_comparison(model_id, fr_ok, en_results, fr_results, "fr")
        model_out["en_vs_ar_all_approved"] = paired_comparison(model_id, ar_ok, en_results, ar_results, "ar")
        model_out["en_vs_fr_3way"] = paired_comparison(model_id, both_ok, en_results, fr_results, "fr")
        model_out["en_vs_ar_3way"] = paired_comparison(model_id, both_ok, en_results, ar_results, "ar")

        en_acc10 = model_out["en_vs_fr_all_approved"]["digit_levels"][10]["en_accuracy"]
        delta, power = power_note(len(fr_ok), en_acc10 if not np.isnan(en_acc10) else 0.1)
        model_out["power_note_10digit"] = {
            "n": len(fr_ok), "baseline_accuracy": en_acc10,
            "smallest_detectable_delta_at_80pct_power": delta, "achieved_power": power,
        }

        all_out["models"][model_id] = model_out

        lines.append(f"\n## {model_id}\n")
        for comparison_key, label in [("en_vs_fr_all_approved", "EN vs FR (all FR-approved)"),
                                       ("en_vs_ar_all_approved", "EN vs AR (all AR-approved)")]:
            comp = model_out[comparison_key]
            lines.append(f"\n### {label} (n={comp['n']})\n")
            lines.append("| Digit level | EN accuracy | Other accuracy | McNemar p |")
            lines.append("|---|---|---|---|")
            other_key = "fr_accuracy" if "fr" in comparison_key else "ar_accuracy"
            for level in DIGIT_LEVELS:
                dl = comp["digit_levels"][level]
                sig = " **significant**" if dl["mcnemar_p"] < 0.05 else ""
                lead = " *(headline)*" if level == 8 else ""
                lines.append(f"| {level}{lead} | {dl['en_accuracy']:.3f} | {dl[other_key]:.3f} | {dl['mcnemar_p']:.4f}{sig} |")
            dstake = comp["duty_at_stake"]
            lines.append(f"\nDuty-at-stake median: EN ${dstake['en_median']:.2f} vs. "
                         f"other ${dstake[list(dstake.keys())[1]]:.2f}, paired bootstrap "
                         f"median diff ${dstake['bootstrap_median_diff']:.2f} "
                         f"[95% CI {dstake['bootstrap_95ci'][0]:.2f}, {dstake['bootstrap_95ci'][1]:.2f}]")
            us = comp["underpay_share"]
            us_other_key = [k for k in us if k != "en"][0]
            lines.append(f"\nUnderpay share: EN {us['en']:.3f} vs. other {us[us_other_key]:.3f}")

        pw = model_out["power_note_10digit"]
        delta = pw["smallest_detectable_delta_at_80pct_power"]
        delta_str = "not reached within the range tested (0.05-0.30)" if delta is None else f"{delta:.2f}"
        lines.append(f"\n**Power note (10-digit, n={pw['n']}):** at this sample size, the "
                     f"smallest EN-vs-translation accuracy difference detectable at 80% "
                     f"power (alpha=0.05) is approximately "
                     f"{delta_str} "
                     f"(baseline EN accuracy {pw['baseline_accuracy']:.3f}). Non-significant "
                     f"McNemar results above should be read as \"no difference detected at "
                     f"this sample size,\" not as evidence of no difference. This estimate "
                     f"assumes independence between languages' per-ruling correctness, a "
                     f"simplification likely to UNDERSTATE real power (positively "
                     f"correlated errors would make McNemar more sensitive).\n")

    # allam-2-7b is the one Arabic-focused model among the three tested -- called out
    # separately per user request 2026-10-02, since "does its own specialization show up
    # as better Arabic performance" is a specific, pointed question the general per-model
    # tables above don't answer on their own.
    if "allam-2-7b" in all_out["models"]:
        allam_ar = all_out["models"]["allam-2-7b"]["en_vs_ar_all_approved"]
        lines.append("\n## allam-2-7b: Arabic vs. English, specifically\n")
        lines.append("allam-2-7b (SDAIA/IBM) is the one Arabic-focused model among the "
                     "three tested here. Does that specialization show up as better "
                     "Arabic-language performance on this task?\n")
        lines.append(f"(n={allam_ar['n']} Arabic-approved rulings)\n")
        lines.append("| Digit level | English accuracy | Arabic accuracy | Arabic better? | McNemar p |")
        lines.append("|---|---|---|---|---|")
        for level in DIGIT_LEVELS:
            dl = allam_ar["digit_levels"][level]
            better = "yes" if dl["ar_accuracy"] > dl["en_accuracy"] else ("no" if dl["ar_accuracy"] < dl["en_accuracy"] else "tie")
            sig = " **significant**" if dl["mcnemar_p"] < 0.05 else ""
            lead = " *(headline)*" if level == 8 else ""
            lines.append(f"| {level}{lead} | {dl['en_accuracy']:.3f} | {dl['ar_accuracy']:.3f} | {better} | {dl['mcnemar_p']:.4f}{sig} |")
        us = allam_ar["underpay_share"]
        lines.append(f"\nUnderpay share: English {us['en']:.3f} vs. Arabic {us['ar']:.3f}")
        lines.append("\n**Reading this:** a model's language of training/focus does not "
                     "automatically translate into better performance on a DIFFERENT task "
                     "(US tariff classification) conducted in that language -- the HTS "
                     "schedule, product terminology, and classification logic are "
                     "English-language in origin regardless of which language the product "
                     "description is presented in. Whatever this table shows should be read "
                     "as a data point about this specific task, not a general claim about "
                     "allam-2-7b's Arabic capability.")

    out_path = REVIEW_DIR / "language_comparison.json"
    out_path.write_text(json.dumps(all_out, indent=2), encoding="utf-8")
    (REVIEW_DIR / "language_comparison.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path} and review/language_comparison.md")


if __name__ == "__main__":
    main()
