"""
Phase 0: query each available LLM provider's live model list and pin exact model IDs
into config.json. Never guesses model names from memory (per the build prompt's hard
rule and the honesty rule) -- if no provider key is present, it says so and exits
without writing placeholder models.

Run this once a free-tier key (GROQ_API_KEY checked first, per the build prompt) is
added to the environment. It only lists models and writes config.json; picking which of
the listed models to actually pin still needs a human or a follow-up rule once we see
what's really on offer (e.g. avoiding vision-only or embedding-only models), so this
prints the full list and only auto-fills config.json with an OBVIOUS best guess per
provider (first chat-capable-looking model id) that a human should review before Phase 4
runs.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import available_providers, list_models  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

# Model ids containing these substrings are almost certainly not chat/instruct text
# models (embeddings, TTS, vision-only, moderation, whisper, image gen) and are skipped
# from the auto-picked default -- still shown in the full listing for a human to check.
NON_CHAT_HINTS = ["embed", "whisper", "tts", "moderation", "guard", "vision", "image", "dall-e"]


def looks_like_chat_model(model_id: str) -> bool:
    low = model_id.lower()
    return not any(h in low for h in NON_CHAT_HINTS)


def main():
    providers = available_providers()
    if not providers:
        print("No free-tier LLM API key found in the environment. Checked: GROQ_API_KEY, "
              "CEREBRAS_API_KEY, TOGETHER_API_KEY, OPENROUTER_API_KEY (in that order). "
              "See BLOCKERS.md. Nothing written to config.json.", file=sys.stderr)
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    all_listings = {}
    auto_picked = []
    for p in providers:
        try:
            models = list_models(p)
        except Exception as e:  # noqa: BLE001 -- report and move on to other providers
            print(f"[{p.name}] failed to list models: {e}", file=sys.stderr)
            continue
        all_listings[p.name] = models
        print(f"[{p.name}] {len(models)} models available:")
        for m in models:
            print(f"    {m}")
        chat_models = [m for m in models if looks_like_chat_model(m)]
        if chat_models:
            auto_picked.append({"provider": p.name, "model_id": chat_models[0], "reasoning_effort": "low"})

    (ROOT / "data" / "raw" / "provider_model_listings.json").write_text(
        json.dumps(all_listings, indent=2), encoding="utf-8"
    )

    print("\nAuto-picked defaults (REVIEW BEFORE RUNNING PHASE 4 -- these are just the "
          "first chat-looking model per provider, not a judged choice):")
    for pick in auto_picked:
        print(f"  {pick}")

    config["models"] = auto_picked[:3]  # hard rule: at most 3 models
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"\nWrote {len(config['models'])} model(s) to config.json.")


if __name__ == "__main__":
    main()
