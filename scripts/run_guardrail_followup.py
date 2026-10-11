"""
Guardrail test (Groq models only, on the fixed 200-ruling sample in data/sample200.csv):
when a model's FIRST answer is an invalid code, send exactly one follow-up turn,
"That code does not exist in the current HTS. Give a valid 10-digit code.", with the
original prompt and the model's own first reply as the conversation history. Same
temperature (0) and reasoning-effort settings as the original run.

Every response is cached to llm_followups/<model>/<rulingNumber>.json (NOT under
llm_logs/, which analysis.py globs as model directories) and never re-sent once cached,
so the run resumes after a rate-limit stall. Usage: --model <model_id> (one process per
model; Groq's limits are per model).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import available_providers, chat_completion  # noqa: E402
from run_llm_classification import build_messages, parse_prediction, code_is_valid  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FOLLOWUP_PROMPT = "That code does not exist in the current HTS. Give a valid 10-digit code."
SUBSET_PATH = ROOT / "data" / "sample200.csv"
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
LLM_LOGS_DIR = ROOT / "llm_logs"
OUT_DIR = ROOT / "llm_followups"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    args = ap.parse_args()
    config = json.loads((ROOT / "config.json").read_text())
    m = next(x for x in config["models"] if x["model_id"] == args.model)
    provider = {p.name: p for p in available_providers()}[m["provider"]]

    with SUBSET_PATH.open(encoding="utf-8") as f:
        subset_ids = [row["rulingNumber"] for row in csv.DictReader(f)]
    usable = {r["rulingNumber"]: r for r in
              (json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines())}
    out_dir = OUT_DIR / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    todo = done = 0
    for rn in subset_ids:
        first = json.loads((LLM_LOGS_DIR / args.model / f"{rn}.json").read_text(encoding="utf-8"))
        if first["tag"] != "INVALID_CODE":
            continue
        todo += 1
        cache = out_dir / f"{rn}.json"
        if cache.exists():
            done += 1
            continue
        row = usable[rn]
        first_reply = first["raw_response"]["choices"][0]["message"]["content"]
        messages = build_messages(row["cleaned_description"]) + [
            {"role": "assistant", "content": first_reply},
            {"role": "user", "content": FOLLOWUP_PROMPT},
        ]
        try:
            raw = chat_completion(provider, args.model, messages, temperature=0.0,
                                  reasoning_effort=m.get("reasoning_effort"))
            content = raw["choices"][0]["message"]["content"]
            digits, reason, parse_error = parse_prediction(content)
        except requests.exceptions.HTTPError as e:
            # A 400 (e.g. allam-2-7b's small context window exceeded by the longer
            # conversation) is a real, countable outcome of the guardrail: no follow-up
            # answer could be obtained. Recorded as still invalid, not skipped.
            if e.response is None or e.response.status_code != 400:
                raise
            raw = {"error": e.response.text[:500]}
            digits, reason, parse_error = None, None, "http_400:" + e.response.text[:200]
        valid = False if parse_error else code_is_valid(digits, row["rulingDate"])
        cache.write_text(json.dumps({
            "rulingNumber": rn, "rulingDate": row["rulingDate"], "true_code": row["true_code"],
            "model": args.model, "followup_prompt": FOLLOWUP_PROMPT,
            "first_predicted_code": first["predicted_code"], "raw_response": raw,
            "predicted_code": digits, "predicted_reason": reason, "parse_error": parse_error,
            "valid_code": valid, "tag": None if valid else "INVALID_CODE",
        }, indent=2), encoding="utf-8")
        done += 1
        if done % 20 == 0:
            print(f"  {args.model}: {done}/{todo} follow-ups done", flush=True)
    print(f"{args.model}: {done}/{todo} follow-ups cached", flush=True)


if __name__ == "__main__":
    main()
