"""
Round 2, Task 1: run Gemini (gemini-3.8-flash, the strongest model this free-tier key
can actually use -- see DECISIONS.md for why Pro-tier models were ruled out) as a 4th
model, on rulings dated on/after its published training cutoff.

Same prompt template, temperature 0, and JSON/code-validation logic as Phase 5's
run_llm_classification.py (imported directly, not duplicated). No `tools` key is ever
sent in the request body, which is what keeps Google Search grounding and all other
tools disabled -- see llm_client.gemini_chat_completion's docstring.

Caches to llm_logs/gemini-3.8-flash/<rulingNumber>.json, resumable like every other
model's run.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import available_gemini_provider, gemini_chat_completion, GeminiDailyQuotaExceeded  # noqa: E402
from run_llm_classification import PROMPT_TEMPLATE, parse_prediction, code_is_valid  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
LLM_LOGS_DIR = ROOT / "llm_logs"

MODEL_ID = "gemini-3.8-flash"  # strongest Gemini Flash model with confirmed free-tier
# access for this key as of 2026-10-05 (re-queried live; its free-tier access was
# restricted/unusable 3 days earlier and has since opened up -- see DECISIONS.md). Same
# published cutoff as gemini-3.7-flash (used previously): both inherit training data
# from the same lineage.
TRAINING_CUTOFF = "2026-03-01"  # knowledge cutoff is "March 2026" per the model's own
# page: https://deepmind.google/models/model-cards/gemini-3-8-flash/ (re-confirmed live
# 2026-10-05; same date as gemini-3.7-flash, which 3.8 is built on and inherits training
# data from -- see DECISIONS.md).
# The usable-rulings filter below uses POST_CUTOFF_START (2026-04-01), one full month
# later, to be safely clear of the entire cutoff month rather than guessing a specific day.
POST_CUTOFF_START = datetime(2026, 4, 1)

SUBSET_PATH = ROOT / "data" / "gemini_subset.csv"  # fixed-seed 200-ruling sample, saved
# by build_gemini_subset.py BEFORE any calls to this model (see DECISIONS.md) -- this is
# the actual set run and reported, not the full 661-ruling eligible pool.


def load_post_cutoff_rows():
    """Loads the fixed 200-ruling subset (data/gemini_subset.csv), joined back against
    usable_rulings.jsonl for the full row (cleaned_description etc.), which the subset
    CSV itself deliberately doesn't duplicate."""
    import csv
    if not SUBSET_PATH.exists():
        raise FileNotFoundError(
            f"{SUBSET_PATH} not found -- run scripts/build_gemini_subset.py first "
            f"to draw the fixed-seed sample before making any calls.")
    with SUBSET_PATH.open(encoding="utf-8") as f:
        subset_ids = {row["rulingNumber"] for row in csv.DictReader(f)}
    rows = [json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()]
    return [r for r in rows if r["rulingNumber"] in subset_ids]


def classify_one_gemini(provider, row, out_dir):
    cache_path = out_dir / f"{row['rulingNumber']}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    prompt_text = PROMPT_TEMPLATE.format(description=row["cleaned_description"])
    raw = gemini_chat_completion(provider, MODEL_ID, prompt_text, temperature=0.0, thinking_level="low")

    content = raw["choices"][0]["message"]["content"]
    digits, reason, parse_error = parse_prediction(content)
    valid = False if parse_error else code_is_valid(digits, row["rulingDate"])
    tag = None if (not parse_error and valid) else "INVALID_CODE"

    result = {
        "rulingNumber": row["rulingNumber"],
        "rulingDate": row["rulingDate"],
        "true_code": row["true_code"],
        "model": MODEL_ID,
        "raw_response": raw,
        "predicted_code": digits,
        "predicted_reason": reason,
        "parse_error": parse_error,
        "valid_code": valid,
        "tag": tag,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=None)
    args = ap.parse_args()

    provider = available_gemini_provider()
    if provider is None:
        print("No GOOGLE_API_KEY/GEMINI_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)

    rows = load_post_cutoff_rows()
    if args.n:
        rows = rows[: args.n]
    print(f"{len(rows)} rulings from the fixed 200-ruling subset ({SUBSET_PATH.name}, "
          f"all dated >= {POST_CUTOFF_START.date()})")

    out_dir = LLM_LOGS_DIR / MODEL_ID
    results = []
    try:
        for i, row in enumerate(rows):
            results.append(classify_one_gemini(provider, row, out_dir))
            if (i + 1) % 10 == 0:
                valid_so_far = sum(1 for r in results if r["valid_code"])
                print(f"  {i + 1}/{len(rows)} done, {valid_so_far} valid_code so far")
    except GeminiDailyQuotaExceeded as e:
        # Expected, not an error: the free tier's daily request cap (confirmed 20/day
        # for gemini-3.8-flash, see DECISIONS.md) ran out partway through. Exit 0 --
        # everything done so far is cached; a daily-scheduled re-run (run_gemini_daily.bat)
        # picks up tomorrow with no wasted work. A non-zero exit here would make Task
        # Scheduler flag an entirely normal, anticipated stopping point as a failure.
        print(f"  Stopping for today: {e}")
        valid = sum(1 for r in results if r["valid_code"])
        print(f"So far this run: {len(results)}/{len(rows)} processed, {valid} valid_code")
        return

    valid = sum(1 for r in results if r["valid_code"])
    print(f"Done: {len(results)} processed, {valid} valid_code, {len(results) - valid} invalid")


if __name__ == "__main__":
    main()
