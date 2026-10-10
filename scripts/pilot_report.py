"""
Pilot report for one v1.1 model: accuracy at 2/4/6/8/10 digits, parse failures, finish_reason
counts, average input/output tokens, and the full-run list-price cost projected from the
pilot's real token usage. Usage: pilot_report.py --model <id> [--n 50]
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import models_config as M  # noqa: E402
from analysis import digit_match  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=50)
    args = ap.parse_args()
    m = M.by_id(args.model)
    ids = (M.sample_ids(m) or [json.loads(l)["rulingNumber"] for l in M.USABLE_PATH.read_text(encoding="utf-8").splitlines()])[: args.n]
    rows = []
    for rn in ids:
        fp = M.model_dir(m) / f"{rn}.json"
        if fp.exists():
            rows.append(json.loads(fp.read_text(encoding="utf-8")))
    n = len(rows)
    print(f"Pilot report: {m['model_id']}  ({n} of the first {args.n} rulings cached)")
    for lvl in (2, 4, 6, 8, 10):
        k = sum(1 for r in rows if digit_match(r["true_code"], r.get("predicted_code"), lvl))
        print(f"  {lvl}-digit accuracy: {k}/{n} = {k / n:.1%}")
    fin = Counter(r.get("finish_reason") for r in rows)
    perr = Counter(r["parse_error"].split(":")[0] for r in rows if r.get("parse_error"))
    print(f"  finish_reason: {dict(fin)}")
    print(f"  parse failures: {sum(perr.values())} {dict(perr)}; invalid-code answers: {sum(1 for r in rows if r['tag'])}")
    tin = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in rows) / n
    tout = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in rows) / n
    rtok = sum(((r.get("usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0 for r in rows) / n
    lat = sum(r.get("latency_s", 0) for r in rows) / n
    print(f"  avg input tokens {tin:.0f}, avg output tokens {tout:.0f} (reasoning {rtok:.0f}), avg latency {lat:.1f}s")
    full = M.expected_n(m)
    costs = [(r.get("usage") or {}).get("cost") for r in rows]
    costs = [c for c in costs if c is not None]
    if costs:
        avg = sum(costs) / len(costs)
        done = M.cached_n(m)
        print(f"  actual cost of these {len(costs)} calls: ${sum(costs):.4f} (avg ${avg:.5f} per call, from each response's usage.cost)")
        print(f"  projected cost to finish this model: {full - done} more rulings x avg = ${(full - done) * avg:.2f}; full {full}-ruling run would be ${full * avg:.2f}")
    else:
        cost = full * (tin * m["price_in_per_1m"] + tout * m["price_out_per_1m"]) / 1e6
        print(f"  projected list-price cost for the full {full} rulings: ${cost:.2f}")
    print(f"  returned model ids: {sorted({r['raw_response'].get('model') for r in rows})}; providers: {sorted({str(r.get('provider_served')) for r in rows})}")


if __name__ == "__main__":
    main()
