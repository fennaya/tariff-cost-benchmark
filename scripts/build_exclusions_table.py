"""
Combines the exclusion counts from Phases 1-3 (each already saved by its own script) into
one exclusions table for findings.md, covering every stage from the raw candidate pool
down to the set actually usable for cost analysis.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"


def main():
    search_pages = sorted((ROOT / "data" / "raw" / "search_pages").glob("*.json"))
    total_hits = None
    if search_pages:
        first_page = json.loads(search_pages[0].read_text(encoding="utf-8"))
        total_hits = first_page.get("totalHits")

    n_fetched = len(list((ROOT / "data" / "raw" / "rulings").glob("*.json")))

    phase12 = json.loads((PROCESSED / "exclusions_phase1_2.json").read_text(encoding="utf-8"))
    duty_summary = json.loads((PROCESSED / "duty_rate_summary.json").read_text(encoding="utf-8"))

    table = {
        "candidate_pool_total_hits": total_hits,
        "rulings_fetched": n_fetched,
        "phase1_2_considered": phase12["total_considered"],
        "phase1_2_excluded": phase12["excluded"],
        "phase1_2_usable": phase12["usable"],
        "phase3_rate_type_counts": duty_summary["rate_type_counts"],
        "phase3_usable_for_cost_analysis": duty_summary["usable_for_cost_analysis"],
        "phase3_gate3_pass_share": duty_summary["gate3_pass_share"],
    }
    out_path = PROCESSED / "exclusions_table.json"
    out_path.write_text(json.dumps(table, indent=2), encoding="utf-8")
    print(json.dumps(table, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
