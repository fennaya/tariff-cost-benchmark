"""
Phase 8: per-ruling rows for a later interactive demo (id, date, description, true code,
each model's code, rate difference). Reads only from data/processed/ and llm_logs/ --
nothing fabricated. Refuses to run if llm_logs/ is empty (no Phase 5 data yet).
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from parse_duty_rates import revision_for_date, load_revision, classify_rate, resolve_rate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LLM_LOGS_DIR = ROOT / "llm_logs"
DUTY_PATH = ROOT / "data" / "processed" / "rulings_with_duty.jsonl"
OUT_PATH = ROOT / "demo_data.json"


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


def main():
    if not LLM_LOGS_DIR.exists() or not any(LLM_LOGS_DIR.iterdir()):
        print("llm_logs/ is empty -- nothing to build demo_data.json from yet.", file=sys.stderr)
        sys.exit(1)

    duty_rows = {r["rulingNumber"]: r for r in
                 (json.loads(l) for l in DUTY_PATH.read_text(encoding="utf-8").splitlines())}

    per_ruling = {}
    # Models come from config.json (complete runs only, so a partial or unpublished run such
    # as an unfinished run never reaches the demo). Keyed by model_id, or
    # "<model_id>/lang_ar" for a translation run.
    pairs = []
    for m in M.analysis_models():
        pairs.append((m["model_id"], M.model_dir(m)))
        pairs += [(f"{m['model_id']}/{d.name}", d) for d in sorted(M.model_dir(m).glob("lang_*")) if d.is_dir()]
    for model_key, model_dir in pairs:
        for fp in model_dir.glob("*.json"):
            r = json.loads(fp.read_text(encoding="utf-8"))
            rn = r["rulingNumber"]
            base = duty_rows.get(rn)
            if base is None:
                continue
            row = per_ruling.setdefault(rn, {
                "id": rn,
                "date": r["rulingDate"],
                "description": base["cleaned_description"],
                "true_code": base["true_code"],
                "true_rate_type": base["true_rate_type"],
                "true_rate_ad_valorem_pct": base["true_rate_ad_valorem_pct"],
                "models": {},
            })
            pred_pct = rate_pct_for(r.get("predicted_code"), r["rulingDate"])
            true_pct = base["true_rate_ad_valorem_pct"] if base["true_rate_type"] == "ad_valorem" else (
                0.0 if base["true_rate_type"] == "free" else None
            )
            rate_diff = (pred_pct - true_pct) if (pred_pct is not None and true_pct is not None) else None
            row["models"][model_key] = {
                "predicted_code": r.get("predicted_code"),
                "valid_code": r.get("valid_code"),
                "rate_diff_pct": rate_diff,
            }

    out = list(per_ruling.values())
    bm_path = ROOT / "review" / "biggest_misses.json"
    if bm_path.exists():  # tag the 10 largest under- and over-payments (review/biggest_misses.md)
        bm = json.loads(bm_path.read_text(encoding="utf-8"))
        tags = {}
        for kind in ("under", "over"):
            for x in bm[kind]:
                tags.setdefault(x["rulingNumber"], []).append(
                    {"direction": kind, "model": x["model"], "usd_per_100k": round(abs(x["usd_per_100k"]))})
        for r in out:
            if r["id"] in tags:
                r["biggest_miss"] = tags[r["id"]]
    dq_path = ROOT / "review" / "description_quality.json"
    if dq_path.exists():  # rulings whose cleaned description is not a product description
        flagged = json.loads(dq_path.read_text(encoding="utf-8"))["flagged"]
        for r in out:
            if r["id"] in flagged:
                r["inadequate_description"] = True
    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(out)} rulings)")


if __name__ == "__main__":
    main()
