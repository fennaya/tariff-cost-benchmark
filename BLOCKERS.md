# Blockers

Each entry: what's blocked, why, free alternative recommended, status.

---

## 1. No free LLM API key available on this machine

**Blocks:** Phase 0 (query live model lists, pin model IDs), Phase 4 (pilot), Phase 5
(full run), Phase 6 (per-model analysis), Phase 7 (translation + language comparison).

**Why:** Environment scan found no GROQ_API_KEY or any other free-tier LLM provider key
(OpenAI, Together, Cerebras, Mistral, Google/Gemini, Cohere, Hugging Face, OpenRouter,
Anthropic). See [DECISIONS.md](DECISIONS.md) 2026-09-28 entry.

**Recommended free alternative:** Get a free API key from one or more of (no card
required for any of these, as of last general knowledge — needs live verification once a
key is added):
- Groq (GROQ_API_KEY) — fast free tier, good OSS model selection.
- Google AI Studio (Gemini free tier, GOOGLE_API_KEY / GEMINI_API_KEY).
- OpenRouter free-tier models (OPENROUTER_API_KEY) — several `:free` suffixed models.
- Cerebras free tier (CEREBRAS_API_KEY).

**Status:** RESOLVED 2026-09-29. The user provided a free GROQ_API_KEY, stored locally in
`.env` (gitignored, never committed — see DECISIONS.md). Phase 0's model query and
Phase 4 pilot are complete; Phase 5's full run is in progress (see STATUS.md).

**What resolved it:** Added GROQ_API_KEY, ran `scripts/select_models.py` to pin 3 models
from Groq's live listing.

---

## 2. Stronger free-tier model availability check (requested 2026-10-02)

**Ask:** before the Round 2 Part 4 final write-up, check whether a no-card free tier for
a stronger model (e.g. Google AI Studio / Gemini Flash) is available via an existing key
on this machine; if not, log it here with sign-up steps and stop -- don't sign up for
anything.

**Check result:** no GOOGLE_API_KEY or GEMINI_API_KEY existed in the environment or in
`.env` prior to this request (confirmed by a fresh scan). The user then supplied a
Google AI Studio key directly in chat. Stored it in `.env` (same pattern as
GROQ_API_KEY: gitignored, never committed, never printed in any output). Verified it
live against `https://generativelanguage.googleapis.com/v1beta/models` (a read-only
list call, no generation, no spend) -- it works and exposes `gemini-2.5-flash` and
`gemini-2.5-pro`, both well above the capability class of the 3 Groq models currently
tested.

**Status:** RESOLVED as a key-availability check. NOT acted on further: `llm_client.py`
only implements the OpenAI-compatible chat-completions shape (Groq, Cerebras, Together,
OpenRouter); Gemini's API has a different request/response shape and was explicitly
deferred in Round 1 ("deliberately not implemented until/unless it's the key actually
available" -- see DECISIONS.md 2026-09-28). Implementing Gemini support and running a
4th model would be a real scope expansion (new client code, a new full Phase 5-style run
likely large enough to need its own rate-limit handling, changes to every downstream
analysis script's model list) that wasn't asked for in this request -- the ask here was
specifically to check and stop. Flagged for a future round if wanted.

**If sign-up were still needed (for reference, not required now):** Google AI Studio
(aistudio.google.com) — sign in with any Google account, click "Get API key," no card
required for the free tier (subject to Google's own rate limits, which can change).

## 2026-10-07: GPT-6 Sol requested, but it is a paid model

The user asked mid-run to include "GPT 6 SOL". On OpenRouter it is `openai/gpt-6-sol` (also `gpt-6.1-sol`, `gpt-5.6-sol`), priced at $2 per 1M input and $10 per 1M output tokens, not free. The standing zero-spend rule ("OpenRouter: free variants only; refuse any other ID") overrides other instructions, so it was not called. **Needed to unblock:** an explicit OK to spend, with a cap. Rough size: about 270 input tokens per ruling plus the answer, so 200 rulings cost on the order of $1 and 1,098 rulings on the order of $5 at low reasoning. That is an estimate, not a measurement.
