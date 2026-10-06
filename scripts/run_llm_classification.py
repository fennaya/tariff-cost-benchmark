"""
Phase 4 (pilot) and Phase 5 (full run): ask each pinned model for one 10-digit HTS code
plus a one-sentence reason, as strict JSON, temperature 0, no tools/web access.

Every raw response is cached to llm_logs/<model>/<rulingNumber>.json and never re-sent
once cached, so the run resumes automatically after a crash or a rate-limit stall
spanning days (Phase 5 note in the build prompt).

Requires config.json's "models" list to be populated (see select_models.py), which in
turn requires a free-tier LLM key in the environment -- there is none on this machine as
of 2026-09-28 (see BLOCKERS.md), so this script cannot be run for real yet. Its mechanics
(prompt, JSON parsing, code-existence validation, caching, resuming) are exercised with
--dry-run, which uses a fake local provider and writes to a separate directory so no
placeholder numbers ever land in llm_logs/ or any reported result.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import PROVIDERS, Provider, available_providers, chat_completion, DryRunProvider  # noqa: E402
from parse_duty_rates import REVISIONS_SORTED, revision_for_date, load_revision  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
LLM_LOGS_DIR = ROOT / "llm_logs"
DRYRUN_LOGS_DIR = ROOT / "data" / "processed" / "_dryrun_llm_logs"

PROMPT_TEMPLATE = """You are an expert US customs classification specialist. Given the \
product description below, determine the single most applicable 10-digit Harmonized \
Tariff Schedule of the United States (HTSUS) code.

Product description:
\"\"\"
{description}
\"\"\"

Respond with ONLY a JSON object, no other text, in exactly this shape:
{{"hts_code": "XXXX.XX.XXXX", "reason": "<one sentence>"}}
"""

JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def build_messages(description: str):
    return [{"role": "user", "content": PROMPT_TEMPLATE.format(description=description)}]


def parse_prediction(content: str):
    m = JSON_BLOCK_RE.search(content or "")
    if not m:
        return None, None, "no_json_found"
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return None, None, f"json_decode_error:{e}"
    code = obj.get("hts_code")
    reason = obj.get("reason")
    if not code:
        return None, reason, "no_hts_code_field"
    digits = re.sub(r"\D", "", str(code))
    return digits, reason, None


def code_is_valid(digits, ruling_date_str):
    if not digits or len(digits) != 10:
        return False
    ruling_date = datetime.fromisoformat(ruling_date_str.replace("Z", ""))
    release_id = revision_for_date(ruling_date)
    lookup = load_revision(release_id)
    return digits in lookup


def classify_one(provider, model_id, row, out_dir, reasoning_effort=None):
    safe_ruling = row["rulingNumber"]
    cache_path = out_dir / f"{safe_ruling}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    messages = build_messages(row["cleaned_description"])
    if isinstance(provider, DryRunProvider):
        raw = provider.classify(row["cleaned_description"])
    else:
        raw = chat_completion(provider, model_id, messages, temperature=0.0,
                               reasoning_effort=reasoning_effort)

    content = raw["choices"][0]["message"]["content"]
    digits, reason, parse_error = parse_prediction(content)
    if parse_error:
        valid = False
        tag = "INVALID_CODE"
    else:
        valid = code_is_valid(digits, row["rulingDate"])
        tag = None if valid else "INVALID_CODE"

    result = {
        "rulingNumber": row["rulingNumber"],
        "rulingDate": row["rulingDate"],
        "true_code": row["true_code"],
        "model": model_id,
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
    ap.add_argument("--n", type=int, default=None, help="limit number of rulings (Phase 4 pilot uses 50)")
    ap.add_argument("--dry-run", action="store_true", help="use a fake local provider, write to a scratch dir")
    ap.add_argument("--model", type=str, default=None,
                     help="only run this model_id from config.json's models list (lets multiple "
                          "models run as separate concurrent processes, useful when a provider's "
                          "rate limits are per-model -- running sequentially would otherwise leave "
                          "later models idle while an earlier one is still rate-limit-bound)")
    args = ap.parse_args()

    rows = [json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()]
    if args.n:
        rows = rows[: args.n]

    if args.dry_run:
        provider = DryRunProvider()
        model_id = "dryrun-model"
        out_dir = DRYRUN_LOGS_DIR / model_id
        print(f"[DRY RUN] writing to {out_dir}, never used for reported results")
        results = [classify_one(provider, model_id, r, out_dir) for r in rows]
        valid = sum(1 for r in results if r["valid_code"])
        print(f"Processed {len(results)}, valid_code={valid}, invalid={len(results) - valid}")
        return

    config = json.loads(CONFIG_PATH.read_text())
    models = config.get("models", [])
    if not models:
        print("No models pinned in config.json (models: []). See BLOCKERS.md -- no free "
              "LLM API key is available on this machine. Run select_models.py once a key "
              "is added.", file=sys.stderr)
        sys.exit(1)
    if args.model:
        models = [m for m in models if m["model_id"] == args.model]
        if not models:
            print(f"--model {args.model} not found in config.json's models list", file=sys.stderr)
            sys.exit(1)

    providers_by_name = {p.name: p for p in available_providers()}
    for m in models:
        provider = providers_by_name.get(m["provider"])
        if provider is None:
            print(f"Skipping {m}: provider {m['provider']} has no key in this environment", file=sys.stderr)
            continue
        out_dir = LLM_LOGS_DIR / m["model_id"]
        print(f"Running {m['provider']}/{m['model_id']} over {len(rows)} rulings...")
        results = [classify_one(provider, m["model_id"], r, out_dir,
                                 reasoning_effort=m.get("reasoning_effort")) for r in rows]
        valid = sum(1 for r in results if r["valid_code"])
        print(f"  done: {len(results)} processed, {valid} valid_code, {len(results) - valid} invalid")


if __name__ == "__main__":
    main()
