"""
Exports one row per model call, from the response caches, to data/exports/api_calls.csv so the
calls can be analysed elsewhere (spreadsheet, pandas, R). Covers every cached call: the three
v1.0 Groq models, the v1.1 models (llm_logs/), and the memorisation probes (llm_probes/).
The raw requests and full responses stay in the cache files named in the last column.
Also writes data/exports/api_calls_summary.csv (one row per model and kind) and prints it.
No keys or prompts are written. Gemini cache files are included only if
TARIFF_INCLUDE_PARTIAL=1 (its run is unpublished until all 200 are done).
"""
import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import models_config as M  # noqa: E402

OUT_DIR = ROOT / "data" / "exports"
FIELDS = ["model", "provider", "kind", "ruling", "ruling_date", "requested_at", "latency_s", "finish_reason",
          "prompt_tokens", "completion_tokens", "reasoning_tokens", "list_price_usd", "provider_served",
          "predicted_code", "true_code", "valid_code", "parse_error", "cache_file"]


def rows_for(model, base_dir, kind):
    if not base_dir.exists():
        return
    for fp in sorted(base_dir.glob("*.json")):
        r = json.loads(fp.read_text(encoding="utf-8"))
        u = r.get("usage") or (r.get("raw_response") or {}).get("usage") or {}
        pt, ct = u.get("prompt_tokens"), u.get("completion_tokens")
        rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens")
        price = ""
        if pt is not None and ct is not None:
            price = round((pt * model.get("price_in_per_1m", 0) + ct * model.get("price_out_per_1m", 0)) / 1e6, 6)
        yield {
            "model": model["model_id"], "provider": model["provider"], "kind": kind, "ruling": r["rulingNumber"],
            "ruling_date": r.get("rulingDate"), "requested_at": r.get("requested_at", ""),
            "latency_s": r.get("latency_s", ""), "finish_reason": r.get("finish_reason")
            or ((r.get("raw_response") or {}).get("choices") or [{}])[0].get("finish_reason", ""),
            "prompt_tokens": pt, "completion_tokens": ct, "reasoning_tokens": rt, "list_price_usd": price,
            "provider_served": r.get("provider_served", ""), "predicted_code": r.get("predicted_code"),
            "true_code": r.get("true_code"), "valid_code": r.get("valid_code"), "parse_error": r.get("parse_error"),
            "cache_file": str(fp.relative_to(ROOT)).replace("\\", "/"),
        }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    include_partial = os.environ.get("TARIFF_INCLUDE_PARTIAL") == "1"
    summary = defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "usd": 0.0, "latency": 0.0, "n_lat": 0})
    n = 0
    with (OUT_DIR / "api_calls.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for m in M.load():
            if m["provider"] == "gemini" and not include_partial:
                continue
            for kind, base in (("main", M.model_dir(m)), ("probe", ROOT / "llm_probes" / M.dir_name(m))):
                for row in rows_for(m, base, kind):
                    w.writerow(row)
                    n += 1
                    s = summary[(m["model_id"], kind)]
                    s["calls"] += 1
                    s["prompt_tokens"] += row["prompt_tokens"] or 0
                    s["completion_tokens"] += row["completion_tokens"] or 0
                    s["usd"] += row["list_price_usd"] or 0
                    if row["latency_s"] != "":
                        s["latency"] += float(row["latency_s"]); s["n_lat"] += 1
    with (OUT_DIR / "api_calls_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "kind", "calls", "prompt_tokens", "completion_tokens", "list_price_usd", "avg_latency_s"])
        for (mid, kind), s in summary.items():
            avg = round(s["latency"] / s["n_lat"], 2) if s["n_lat"] else ""
            w.writerow([mid, kind, s["calls"], s["prompt_tokens"], s["completion_tokens"], round(s["usd"], 4), avg])
            print(f"{mid:45s} {kind:5s} calls={s['calls']:5d} in={s['prompt_tokens']:8d} out={s['completion_tokens']:8d} list=${s['usd']:.4f} avg_latency={avg}")
    by_provider = defaultdict(float)
    prov = {m["model_id"]: m["provider"] for m in M.load()}
    for (mid, kind), sm in summary.items():
        by_provider[prov[mid]] += sm["usd"]
    print("\nList-price cost of all cached calls by provider (main runs and probes; a handful of uncached settings tests are not included):")
    for k, v in by_provider.items():
        print(f"  {k}: ${v:.4f}")
    with (OUT_DIR / "api_calls_summary.csv").open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for k, v in by_provider.items():
            w.writerow([f"TOTAL {k}", "all", "", "", "", round(v, 4), ""])
    print(f"\nwrote data/exports/api_calls.csv ({n} rows) and api_calls_summary.csv")


if __name__ == "__main__":
    main()
