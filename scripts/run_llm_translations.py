"""
Round 2, Part 4, step 2: run the same 3 models, same prompt template, same settings as
Phase 5 (temperature 0, low reasoning effort, no tools) on the APPROVED translations
(review/translation_review_marked.csv), one language at a time.

Only rows marked "OK" for a given language are run in that language -- a row marked
"Fix" or left blank was not approved as a faithful translation, so testing a model on it
would be testing translation quality, not language effect. Results are cached under
llm_logs/<model>/lang_<fr|ar>/<rulingNumber>.json, parallel to (never overwriting) the
English results in llm_logs/<model>/<rulingNumber>.json.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import available_providers  # noqa: E402
from run_llm_classification import classify_one  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
TRANSLATIONS_PATH = ROOT / "review" / "translation_review.csv"
MARKED_PATH = ROOT / "review" / "translation_review_marked.csv"
LLM_LOGS_DIR = ROOT / "llm_logs"

LANG_COLUMN = {"fr": "french", "ar": "arabic"}
LANG_MARK_COLUMN = {"fr": "fr_ok", "ar": "ar_ok"}


def load_approved_rows(lang):
    with TRANSLATIONS_PATH.open(encoding="utf-8") as f:
        translations = {r["id"]: r for r in csv.DictReader(f)}
    with MARKED_PATH.open(encoding="utf-8-sig") as f:
        marks = {r["id"]: r for r in csv.DictReader(f)}
    usable_by_rn = {r["rulingNumber"]: r for r in
                    (json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines())}

    approved = []
    for rn, mark in marks.items():
        if mark.get(LANG_MARK_COLUMN[lang]) != "OK":
            continue
        base = usable_by_rn.get(rn)
        translated_text = translations.get(rn, {}).get(LANG_COLUMN[lang])
        if base is None or not translated_text:
            continue
        row = dict(base)
        row["cleaned_description"] = translated_text  # swap in the approved translation
        approved.append(row)
    return approved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, choices=["fr", "ar"])
    ap.add_argument("--model", default=None, help="only run this model_id (see config.json)")
    args = ap.parse_args()

    rows = load_approved_rows(args.lang)
    print(f"{len(rows)} rows approved for {args.lang}")

    config = json.loads(CONFIG_PATH.read_text())
    models = config.get("models", [])
    if args.model:
        models = [m for m in models if m["model_id"] == args.model]

    providers_by_name = {p.name: p for p in available_providers()}
    for m in models:
        provider = providers_by_name.get(m["provider"])
        if provider is None:
            print(f"Skipping {m}: no key for provider {m['provider']}", file=sys.stderr)
            continue
        out_dir = LLM_LOGS_DIR / m["model_id"] / f"lang_{args.lang}"
        print(f"Running {m['provider']}/{m['model_id']} ({args.lang}) over {len(rows)} rulings...")
        results = [classify_one(provider, m["model_id"], r, out_dir,
                                 reasoning_effort=m.get("reasoning_effort")) for r in rows]
        valid = sum(1 for r in results if r["valid_code"])
        print(f"  done: {len(results)} processed, {valid} valid_code, {len(results)-valid} invalid")


if __name__ == "__main__":
    main()
