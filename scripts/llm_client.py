"""
Provider-agnostic client for free-tier LLM APIs.

Scope decision (see DECISIONS.md): OpenAI-compatible chat-completions APIs (Groq,
Cerebras, Together, OpenRouter) share one implementation (`chat_completion`). A client for
another API shape was added in Round 2 and removed on 2026-10-11 when that run was dropped
(see DECISIONS.md).

Every provider here is checked via its env var; GROQ_API_KEY is checked first per the
build prompt's instruction.
"""
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests


def _load_dotenv():
    """Load KEY=VALUE lines from a local, gitignored .env into os.environ (only if not
    already set). Keeps free-tier keys out of every Bash invocation and out of the repo
    -- .env is never read back or printed by any script, including this one."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

# (env var, display name, base_url, models_path, chat_path)
PROVIDERS = [
    ("GROQ_API_KEY", "groq", "https://api.groq.com/openai/v1", "/models", "/chat/completions"),
    ("CEREBRAS_API_KEY", "cerebras", "https://api.cerebras.ai/v1", "/models", "/chat/completions"),
    ("TOGETHER_API_KEY", "together", "https://api.together.xyz/v1", "/models", "/chat/completions"),
    ("OPENROUTER_API_KEY", "openrouter", "https://openrouter.ai/api/v1", "/models", "/chat/completions"),
    ("BASETEN_API_KEY", "baseten", "https://inference.baseten.co/v1", "/models", "/chat/completions"),
]

# Baseten's OpenAI-compatible endpoint authenticates with "Api-Key <key>" (verified
# 2026-10-07); every other provider here uses "Bearer <key>".
AUTH_SCHEME = {"baseten": "Api-Key"}


@dataclass
class Provider:
    name: str
    base_url: str
    api_key: str
    models_path: str
    chat_path: str

    @property
    def auth_header(self):
        return {"Authorization": f"{AUTH_SCHEME.get(self.name, 'Bearer')} {self.api_key}"}


def available_providers():
    found = []
    for env_var, name, base_url, models_path, chat_path in PROVIDERS:
        key = os.environ.get(env_var)
        if key:
            found.append(Provider(name=name, base_url=base_url, api_key=key,
                                   models_path=models_path, chat_path=chat_path))
    return found


def list_models(provider: Provider):
    r = requests.get(
        provider.base_url + provider.models_path,
        headers=provider.auth_header,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    models = data.get("data", data if isinstance(data, list) else [])
    return [m.get("id", m) if isinstance(m, dict) else m for m in models]


def chat_completion(provider: Provider, model: str, messages, temperature=0.0,
                     max_retries=8, reasoning_effort=None, timeout=60):
    """Returns (raw_response_dict, wait_seconds_if_retry_needed_else_None)."""
    body = {"model": model, "messages": messages, "temperature": temperature}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort  # ignored by providers that don't support it
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(
                provider.base_url + provider.chat_path,
                headers={**provider.auth_header, "Content-Type": "application/json"},
                json=body,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            # Network hiccups (connection reset, DNS blip, timeout) shouldn't kill a
            # run that's expected to take hours unattended -- observed in practice
            # (2026-09-29: a ConnectionResetError silently ended an overnight run,
            # requiring a manual restart even though caching made the restart cheap).
            wait = min(60, 2 ** attempt)
            print(f"  [network error] {provider.name}/{model}: {e}; sleeping {wait}s "
                  f"(attempt {attempt}/{max_retries})")
            time.sleep(wait)
            continue
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else min(60, 2 ** attempt)
            print(f"  [429] {provider.name}/{model}: sleeping {wait}s (attempt {attempt}/{max_retries})")
            time.sleep(wait)
            continue
        if resp.status_code >= 500:
            wait = min(60, 2 ** attempt)
            print(f"  [{resp.status_code}] {provider.name}/{model}: server error, sleeping {wait}s")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Exceeded retries calling {provider.name}/{model}")


class DryRunProvider:
    """A fake provider for testing the pipeline's mechanics (caching, JSON validation,
    resume-after-crash) without any network access or real key. Never used for reported
    results -- see run_llm_classification.py's --dry-run flag, which refuses to write
    into the real llm_logs/ directory."""
    name = "dryrun"

    def __init__(self, canned_code="1234.56.7890"):
        self.canned_code = canned_code

    def classify(self, description):
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "hts_code": self.canned_code,
                        "reason": "dry-run canned response for pipeline testing",
                    })
                }
            }]
        }
