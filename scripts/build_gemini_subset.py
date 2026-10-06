"""
Round 2, Task 1 (redo): draw a fixed-seed random 200 from the eligible post-cutoff
rulings and save the list BEFORE any new Gemini calls are made, so the sample is fixed
in advance and can't be unconsciously cherry-picked by whatever happens to finish first
under a slow rate limit.

"Eligible" = usable rulings (Gate 1b set) dated on/after gemini-3.8-flash's published
training cutoff (March 2026 -> post-cutoff start 2026-04-01, same one-month buffer used
throughout this project -- see DECISIONS.md).
"""
import csv
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(ROOT))
from run_gemini_classification import POST_CUTOFF_START  # noqa: E402

PROJECT_ROOT = ROOT.parent
USABLE_PATH = PROJECT_ROOT / "data" / "processed" / "usable_rulings.jsonl"
OUT_PATH = PROJECT_ROOT / "data" / "gemini_subset.csv"
SEED = 20261005
N = 200


def main():
    import random
    usable = [json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()]
    eligible = [r for r in usable
                if datetime.fromisoformat(r["rulingDate"].replace("Z", "")) >= POST_CUTOFF_START]
    print(f"{len(eligible)} eligible (usable, dated >= {POST_CUTOFF_START.date()})")

    rng = random.Random(SEED)
    sample = rng.sample(eligible, min(N, len(eligible)))
    sample.sort(key=lambda r: r["rulingNumber"])  # stable, readable file order

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rulingNumber", "rulingDate", "true_code"])
        for r in sample:
            writer.writerow([r["rulingNumber"], r["rulingDate"], r["true_code"]])

    print(f"Wrote {OUT_PATH} ({len(sample)} rulings, seed={SEED})")


if __name__ == "__main__":
    main()
