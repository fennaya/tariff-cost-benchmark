"""
Round 2, Part 2: does Headline B (63.8%-67.4% of rate-changing errors underpay) beat a
fair baseline, or is it just where these codes sit in the tariff schedule?

Checks (review/audit_direction.md):
  1. Baseline 1: random sibling under the true code's 4-digit heading, 1000 reps.
  2. Baseline 2: random sibling under the deepest prefix the model actually got right.
  3. Permutation p-value and 95% interval comparing each model's observed underpay share
     against both baselines.
  4. Whether wrong answers land disproportionately in "Other" catch-all subheadings, and
     how those baskets' rates compare to the true codes' -- reported as a POSSIBLE
     mechanism, not a proven one.
  5. Duty-at-stake per $100,000, computed separately for underpay and overpay errors.

Gate B: the "models underpay more than chance" finding stands only if the observed share
beats Baseline 2 (the harder, more specific baseline) at p < 0.05. If not, the honest
finding is "errors underpay X% of the time, consistent with where these codes sit in the
tariff schedule" -- still a real, reportable cost finding, just not evidence of bias.
"""
import json
import random
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from parse_duty_rates import revision_for_date, load_revision, classify_rate, resolve_rate, REVISIONS_SORTED, read_revision_rows  # noqa: E402

LLM_LOGS_DIR = ROOT / "llm_logs"
RAW_HTS_DIR = ROOT / "data" / "raw" / "hts_revisions"
REVIEW_DIR = ROOT / "review"
N_REPS = 1000
SEED = 20261002
DIGIT_LEVELS = [2, 4, 6, 8]


def load_model_results():
    model_dirs = sorted(p for p in LLM_LOGS_DIR.rglob("*") if p.is_dir() and any(p.glob("*.json")) and "lang_" not in p.name and not p.name.startswith("gemini"))
    out = {}
    for d in model_dirs:
        model_id = d.relative_to(LLM_LOGS_DIR).as_posix()
        out[model_id] = [json.loads(fp.read_text(encoding="utf-8")) for fp in sorted(d.glob("*.json"))]
    return out


def rate_pct_for_code(lookup, code):
    if not code or len(code) != 10:
        return None
    rate_str, err = resolve_rate(lookup, code)
    if err:
        return None
    rate_type, pct = classify_rate(rate_str)
    if rate_type == "free":
        return 0.0
    if rate_type == "ad_valorem":
        return pct
    return None


class RevisionPool:
    """Per-revision: all 10-digit codes with a resolvable ad valorem/free rate, their
    rates, their own leaf description (for the "Other" basket check), and a prefix
    index for fast random-sibling sampling at any of 2/4/6/8 digits."""

    def __init__(self, release_id):
        self.release_id = release_id
        data = read_revision_rows(release_id)
        lookup = load_revision(release_id)
        self.all_codes = []  # list of (code, rate_pct)
        self.rate_by_code = {}  # O(1) lookup, vs. scanning all_codes
        self.desc_by_code = {}
        self.by_prefix = defaultdict(lambda: defaultdict(list))  # length -> prefix -> [(code, rate_pct)]
        for row in data:
            htsno = row.get("htsno") or ""
            digits = "".join(ch for ch in htsno if ch.isdigit())
            if len(digits) != 10:
                continue
            self.desc_by_code[digits] = (row.get("description") or "").strip()
            pct = rate_pct_for_code(lookup, digits)
            if pct is None:
                continue
            self.all_codes.append((digits, pct))
            self.rate_by_code[digits] = pct
            for length in DIGIT_LEVELS:
                self.by_prefix[length][digits[:length]].append((digits, pct))

    def sample_sibling(self, rng, true_code, exclude_code, match_level):
        """A random (code, rate) sharing `true_code`'s first `match_level` digits
        (match_level in {0,2,4,6,8}; 0 means no constraint -- sample from all codes).
        Does NOT filter out `exclude_code` (the true code) from the pool: if drawn, it
        produces a zero rate-diff, which the caller already excludes from the nonzero-
        diff share calculation -- same end result as filtering, but O(1) per draw
        instead of rebuilding a filtered list on every single call (the original
        per-draw list comprehension made 1000-rep simulations impractically slow on the
        full ~1000-case wrong-answer sets -- still running after 20+ minutes, see
        DECISIONS.md)."""
        if match_level == 0:
            pool = self.all_codes
        else:
            pool = self.by_prefix[match_level].get(true_code[:match_level], [])
        if not pool:
            return None
        return pool[rng.randrange(len(pool))]


_pool_cache = {}


def get_pool(release_id):
    if release_id not in _pool_cache:
        _pool_cache[release_id] = RevisionPool(release_id)
    return _pool_cache[release_id]


def deepest_match_level(true_code, pred_code):
    if not pred_code:
        return 0
    level = 0
    for l in DIGIT_LEVELS:
        if len(pred_code) >= l and true_code[:l] == pred_code[:l]:
            level = l
        else:
            break
    return level


def build_wrong_cases(rows):
    """Wrong answers (10-digit mismatch) where the TRUE code resolves to an ad
    valorem/free rate -- the only cases a direction/baseline comparison is possible for.

    True-rate resolution uses the SAME hierarchy-walking `resolve_rate` as Round 1's
    analysis.py (a 10-digit line with a blank rate field inherits its parent 8/6/4-digit
    rate -- see Round 1 DECISIONS.md's "Gate 3 duty-rate resolution" entry), NOT
    `pool.rate_by_code` (which requires an actual 10-digit ROW to exist). Using the
    stricter row-only check here first undercounted qualifying cases (11/15/95 instead
    of Round 1's published 46/47/115) -- found by comparing against Round 1's numbers
    and fixed before trusting this audit's baseline comparison. `pool.rate_by_code` is
    still correct and kept as-is for the SAMPLING pool (which must be restricted to
    codes with their own real 10-digit row, since that's what `code_is_valid()` / a
    model's predicted code must match)."""
    cases = []
    for r in rows:
        if r["true_code"] == r.get("predicted_code"):
            continue
        ruling_date = datetime.fromisoformat(r["rulingDate"].replace("Z", ""))
        release_id = revision_for_date(ruling_date)
        pool = get_pool(release_id)
        true_pct = rate_pct_for_code(load_revision(release_id), r["true_code"])
        if true_pct is None:
            continue
        cases.append({
            "rulingNumber": r["rulingNumber"],
            "true_code": r["true_code"],
            "predicted_code": r.get("predicted_code"),
            "true_pct": true_pct,
            "release_id": release_id,
            "match_level": deepest_match_level(r["true_code"], r.get("predicted_code")),
        })
    return cases


def observed_underpay_share(cases):
    """Using the MODEL's own actual predicted code (when it resolves to ad valorem/free),
    via the same hierarchy-walking resolution as true_pct (see build_wrong_cases)."""
    diffs = []
    for c in cases:
        pred_pct = rate_pct_for_code(load_revision(c["release_id"]), c["predicted_code"])
        if pred_pct is None:
            continue
        diffs.append(pred_pct - c["true_pct"])
    nonzero = [d for d in diffs if d != 0]
    underpay = sum(1 for d in nonzero if d < 0)
    return (underpay / len(nonzero) if nonzero else float("nan")), len(nonzero), diffs


def simulate_baseline(cases, rng, match_level_fn):
    """One trial: for every case, draw one random sibling at the level given by
    match_level_fn(case) and compute whether it underpays vs. the true rate. Returns the
    share of NONZERO-diff draws that underpay (matching how the observed share is
    defined), or nan if no case produced a nonzero diff this trial."""
    underpay, nonzero = 0, 0
    for c in cases:
        pool = get_pool(c["release_id"])
        level = match_level_fn(c)
        sib = pool.sample_sibling(rng, c["true_code"], c["true_code"], level)
        if sib is None:
            continue
        _, pct = sib
        diff = pct - c["true_pct"]
        if diff == 0:
            continue
        nonzero += 1
        if diff < 0:
            underpay += 1
    return (underpay / nonzero if nonzero else float("nan"))


def run_baseline(cases, match_level_fn, n_reps=N_REPS, seed=SEED):
    rng = random.Random(seed)
    shares = [simulate_baseline(cases, rng, match_level_fn) for _ in range(n_reps)]
    return [s for s in shares if not np.isnan(s)]


def permutation_test(observed, baseline_shares):
    """One-sided: P(baseline >= observed) under the null that errors are random at the
    baseline's matching depth. Small p means the model is MORE underpay-biased than
    chance at that depth would produce. Returns (p_value, at_floor) -- at_floor is True
    when zero of the simulated trials met or exceeded the observed share, meaning the
    true p-value is only known to be below 1/(n_reps+1), not equal to it; such floor
    values should be reported as "p < 0.001" rather than a precise-looking "p = 0.0010"
    (per user request 2026-10-02, logged in DECISIONS.md)."""
    if not baseline_shares or np.isnan(observed):
        return float("nan"), False
    ge = sum(1 for s in baseline_shares if s >= observed)
    return (ge + 1) / (len(baseline_shares) + 1), (ge == 0)


def format_p(p_value, at_floor):
    if np.isnan(p_value):
        return "n/a"
    if at_floor:
        return "< 0.001"
    return f"{p_value:.4f}"


def check4_other_baskets(all_results, usable_rows):
    lines = ["\n## 4. \"Other\" catch-all baskets\n"]
    usable_by_rn = {r["rulingNumber"]: r for r in usable_rows}
    for model_id, rows in all_results.items():
        wrong = [r for r in rows if r["true_code"] != r.get("predicted_code")]
        true_other, true_total = 0, 0
        pred_other, pred_total = 0, 0
        true_other_rates, true_named_rates = [], []
        for r in wrong:
            ruling_date = datetime.fromisoformat(r["rulingDate"].replace("Z", ""))
            release_id = revision_for_date(ruling_date)
            pool = get_pool(release_id)
            true_desc = pool.desc_by_code.get(r["true_code"], "")
            is_other_true = true_desc.strip('"“” ').lower().startswith("other")
            true_total += 1
            if is_other_true:
                true_other += 1
            true_pct = rate_pct_for_code(load_revision(release_id), r["true_code"])
            if true_pct is not None:
                (true_other_rates if is_other_true else true_named_rates).append(true_pct)
            pred_code = r.get("predicted_code")
            if pred_code and len(pred_code) == 10:
                pred_desc = pool.desc_by_code.get(pred_code)
                if pred_desc is not None:
                    pred_total += 1
                    if pred_desc.strip('"“” ').lower().startswith("other"):
                        pred_other += 1
        lines.append(f"\n### {model_id}\n")
        lines.append(f"- True codes of wrong answers that are an \"Other\"-type basket: "
                     f"{true_other}/{true_total} ({100*true_other/true_total:.1f}%)")
        if pred_total:
            lines.append(f"- Predicted codes of wrong answers (where resolvable) that are "
                         f"an \"Other\"-type basket: {pred_other}/{pred_total} ({100*pred_other/pred_total:.1f}%)")
        if true_other_rates and true_named_rates:
            lines.append(f"- Mean rate when the TRUE code is an \"Other\" basket: "
                         f"{np.mean(true_other_rates):.2f}% (n={len(true_other_rates)}) vs. "
                         f"{np.mean(true_named_rates):.2f}% for named/specific true codes "
                         f"(n={len(true_named_rates)})")
    lines.append("\n**Reading this:** the hypothesis was that predicted codes landing in "
                 "\"Other\" catch-all baskets more often than true codes do -- combined "
                 "with those baskets' lower average rates -- could mechanically explain "
                 "underpay bias. The data runs the OPPOSITE direction for all 3 models: "
                 "predicted codes land in \"Other\" baskets LESS often than true codes do "
                 "(e.g. 11-49% vs. 62-63%), meaning predictions skew toward named/specific "
                 "subheadings relative to the true distribution. Taken alone, that skew "
                 "would push toward OVERPAYING on average (named subheadings carry "
                 "higher rates here), not underpaying. Since the models are observed to "
                 "underpay anyway (Gate B above), this specific mechanism does NOT explain "
                 "the bias -- it would predict the wrong direction. Reported as a checked, "
                 "ruled-out hypothesis rather than a confirmed one.")
    return "\n".join(lines)


def check5_dollar_framing(all_results):
    lines = ["\n## 5. Duty at stake per $100,000, underpay vs. overpay separately\n"]
    lines.append("| Model | Underpay: median | Underpay: n | Overpay: median | Overpay: n |")
    lines.append("|---|---|---|---|---|")
    for model_id, rows in all_results.items():
        cases = build_wrong_cases(rows)
        _, _, diffs = observed_underpay_share(cases)
        underpay_stakes = [abs(d) / 100 * 100000 for d in diffs if d < 0]
        overpay_stakes = [abs(d) / 100 * 100000 for d in diffs if d > 0]
        um = np.median(underpay_stakes) if underpay_stakes else float("nan")
        om = np.median(overpay_stakes) if overpay_stakes else float("nan")
        lines.append(f"| {model_id} | ${um:,.2f} | {len(underpay_stakes)} | ${om:,.2f} | {len(overpay_stakes)} |")
    return "\n".join(lines)


def main():
    all_results = load_model_results()
    usable_rows = [json.loads(l) for l in (ROOT / "data" / "processed" / "usable_rulings.jsonl").read_text(encoding="utf-8").splitlines()]

    sections = []
    gate_b_results = {}
    sections.append("## 1-3. Baselines and permutation tests\n")
    sections.append("Baseline 1: random sibling sharing the true code's 4-digit heading. "
                     "Baseline 2: random sibling sharing the deepest prefix the model "
                     "itself got right (0 digits if it got none). 1000 reps each.\n")
    sections.append("| Model | Observed underpay share (n) | Baseline 1 mean [95% range] | "
                     "p vs Baseline 1 | Baseline 2 mean [95% range] | p vs Baseline 2 | Gate B |")
    sections.append("|---|---|---|---|---|---|---|")

    for model_id, rows in all_results.items():
        cases = build_wrong_cases(rows)
        observed, n_nonzero, _ = observed_underpay_share(cases)

        b1_shares = run_baseline(cases, lambda c: 4, seed=SEED)
        b2_shares = run_baseline(cases, lambda c: c["match_level"], seed=SEED + 1)

        p1, p1_floor = permutation_test(observed, b1_shares)
        p2, p2_floor = permutation_test(observed, b2_shares)
        b1_mean, b1_lo, b1_hi = np.mean(b1_shares), np.percentile(b1_shares, 2.5), np.percentile(b1_shares, 97.5)
        b2_mean, b2_lo, b2_hi = np.mean(b2_shares), np.percentile(b2_shares, 2.5), np.percentile(b2_shares, 97.5)

        gate_b_pass = p2 < 0.05
        gate_b_results[model_id] = gate_b_pass
        sections.append(
            f"| {model_id} | {observed:.3f} ({n_nonzero}) | {b1_mean:.3f} [{b1_lo:.3f}, {b1_hi:.3f}] | "
            f"{format_p(p1, p1_floor)} | {b2_mean:.3f} [{b2_lo:.3f}, {b2_hi:.3f}] | {format_p(p2, p2_floor)} | "
            f"{'PASS' if gate_b_pass else 'NOT MET'} |"
        )

    sections.append(check4_other_baskets(all_results, usable_rows))
    sections.append(check5_dollar_framing(all_results))

    overall_pass = any(gate_b_results.values())
    header = [
        "# Headline B audit (Round 2, Part 2)\n",
        f"**Gate B verdict: {'PASS for at least one model' if overall_pass else 'NOT MET for any model'}** "
        "(needs: observed underpay share beats Baseline 2 at p<0.05).\n",
    ]
    for model_id, passed in gate_b_results.items():
        header.append(f"- {model_id}: {'PASS' if passed else 'NOT MET'}")
    header.append("")

    out_path = REVIEW_DIR / "audit_direction.md"
    out_path.write_text("\n".join(header) + "\n".join(sections), encoding="utf-8")
    print(f"Wrote {out_path}")
    for model_id, passed in gate_b_results.items():
        print(f"{model_id}: Gate B {'PASS' if passed else 'NOT MET'}")


if __name__ == "__main__":
    main()
