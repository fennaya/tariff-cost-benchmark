"""
Phase 7 (prepare only): translate a random 100 cleaned descriptions into French and
Modern Standard Arabic using a free model that is NOT one of the models being tested
(config.json's "models" list), then write review/translation_review.csv for human
marking. Per the build prompt, this phase stops after writing the review file (allowed
stop case 4 -- language review needs a human who reads Arabic and French) and does NOT
run the language comparison until that file has been marked.

Only runs after Phase 6 (analysis.py) has produced results, and only if a free-tier key
is available for a model distinct from the ones tested.
"""
import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import available_providers, chat_completion  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
CONFIG_PATH = ROOT / "config.json"
REVIEW_DIR = ROOT / "review"
ANALYSIS_RESULTS = ROOT / "data" / "processed" / "analysis_results.json"

TRANSLATE_PROMPT = """Translate the following US customs product description into {lang}. \
Respond with ONLY the translation, no other text.

\"\"\"
{text}
\"\"\"
"""


NON_CHAT_HINTS = ["embed", "whisper", "tts", "moderation", "guard", "vision", "image",
                   "dall-e", "orpheus", "safeguard"]


def pick_translation_model(config):
    """A model distinct from config.json's tested set. Doesn't require a different
    *provider* (we only have one, Groq) -- just a different model_id, since the build
    prompt's intent is to avoid the translation model being one of the models under
    test, not to avoid reusing the same API account."""
    tested_ids = {m["model_id"] for m in config.get("models", [])}
    for p in available_providers():
        from llm_client import list_models
        for model_id in list_models(p):
            if model_id in tested_ids:
                continue
            if any(h in model_id.lower() for h in NON_CHAT_HINTS):
                continue
            return p, model_id
    return None, None


def translate(provider, model_id, text, lang):
    messages = [{"role": "user", "content": TRANSLATE_PROMPT.format(lang=lang, text=text)}]
    raw = chat_completion(provider, model_id, messages, temperature=0.0)
    return raw["choices"][0]["message"]["content"].strip()


def main():
    if not ANALYSIS_RESULTS.exists():
        print("Phase 6 (analysis.py) hasn't produced results yet -- Phase 7 only starts "
              "once Phase 6 is complete, per the build prompt. Stopping.", file=sys.stderr)
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    provider, translation_model = pick_translation_model(config)
    if provider is None:
        print("No free-tier key available for a model distinct from the tested set. "
              "See BLOCKERS.md.", file=sys.stderr)
        sys.exit(1)

    rows = [json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()]
    random.seed(20260928)
    sample = random.sample(rows, min(100, len(rows)))

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REVIEW_DIR / "translation_review.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "english", "french", "arabic", "fr_ok", "ar_ok"])
        for r in sample:
            en = r["cleaned_description"]
            fr = translate(provider, translation_model, en, "French")
            ar = translate(provider, translation_model, en, "Modern Standard Arabic")
            writer.writerow([r["rulingNumber"], en, fr, ar, "", ""])

    print(f"Wrote {out_path} using translation model {provider.name}/{translation_model}.")
    print("STOPPING per build prompt: language review needs a human who reads French and "
          "Arabic (allowed stop case 4). Do not run the language comparison until "
          "review/translation_review.csv has been marked.")


if __name__ == "__main__":
    main()
