"""
Provider-agnostic client for free-tier LLM APIs.

Scope decision (see DECISIONS.md): OpenAI-compatible chat-completions APIs (Groq,
Cerebras, Together, OpenRouter) share one implementation (`chat_completion`). Google
Gemini uses a different API shape (`v1beta/models/{model}:generateContent`, a
`contents`/`parts` body, no `Authorization` header) and was deliberately left
unimplemented in Round 1 until a key was actually available; added in Round 2 once
GOOGLE_API_KEY was provided and verified live (see DECISIONS.md 2026-10-02).

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
]


@dataclass
class Provider:
    name: str
    base_url: str
    api_key: str
    models_path: str
    chat_path: str


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
        headers={"Authorization": f"Bearer {provider.api_key}"},
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
                headers={"Authorization": f"Bearer {provider.api_key}", "Content-Type": "application/json"},
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


GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


@dataclass
class GeminiProvider:
    name: str
    api_key: str


def available_gemini_provider():
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    return GeminiProvider(name="gemini", api_key=key) if key else None


def gemini_list_models(provider: GeminiProvider):
    r = requests.get(f"{GEMINI_BASE_URL}/models", params={"key": provider.api_key}, timeout=30)
    r.raise_for_status()
    return [m["name"].removeprefix("models/") for m in r.json().get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])]


class GeminiDailyQuotaExceeded(RuntimeError):
    """Raised when the 429 is specifically the free-tier REQUESTS-PER-DAY cap (not the
    per-minute one), so callers can exit promptly instead of sleeping in-process for
    however many hours remain -- the intended use is a daily-scheduled task (e.g. Windows
    Task Scheduler running run_gemini_daily.bat) that simply tries again tomorrow, not a
    single long-lived process sitting idle. See DECISIONS.md, 2026-10-05."""


def _parse_gemini_429(resp):
    """Returns (retry_delay_seconds_or_None, is_daily_quota: bool) from a 429 response.

    Confirmed live (2026-10-05, see DECISIONS.md) that Gemini's free tier for a Flash
    model enforces TWO separate quotas, each surfaced via a distinct `quotaId` in the
    structured QuotaFailure detail:
      - "GenerateRequestsPerMinutePerProjectPerModel-FreeTier" (observed value: 5/min)
      - "GenerateRequestsPerDayPerProjectPerModel-FreeTier" (observed value: 20/day)
    Both report their wait via the same RetryInfo.retryDelay field, which is read and
    respected exactly either way -- the only difference in handling is whether the
    caller should sleep in-process (short, per-minute case) or raise and let a daily
    scheduled re-run handle it (long, per-day case)."""
    retry_delay = None
    is_daily = False
    try:
        data = resp.json()
        for d in data.get("error", {}).get("details", []):
            type_ = d.get("@type", "")
            if type_.endswith("RetryInfo"):
                delay = d.get("retryDelay", "")
                if delay.endswith("s"):
                    retry_delay = float(delay[:-1])
            elif type_.endswith("QuotaFailure"):
                for v in d.get("violations", []):
                    if "PerDay" in v.get("quotaId", ""):
                        is_daily = True
    except (ValueError, KeyError):
        pass
    if retry_delay is None:
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                retry_delay = float(retry_after)
            except ValueError:
                pass
    return retry_delay, is_daily


_last_gemini_request_time = 0.0


def gemini_chat_completion(provider: GeminiProvider, model: str, prompt_text: str,
                            temperature=0.0, thinking_level="low", max_retries=10, timeout=60,
                            min_request_interval=13.0):
    """Calls Gemini's generateContent endpoint and returns the response wrapped in the
    same {"choices": [{"message": {"content": ...}}]} shape the OpenAI-compatible path
    uses, so run_llm_classification.py's parse_prediction/classify_one work unchanged
    for either provider.

    No `tools` key is ever included in the request body -- this is what keeps Google
    Search grounding and all other tools disabled (Gemini only activates them when a
    `tools` array is explicitly present in the request). `thinkingConfig.thinkingLevel`
    is set to "low" -- the minimum level the API accepts (its own docs state "minimal is
    not supported and returns an error") -- for consistency with the other 3 models' low
    reasoning effort and to conserve the free tier's tight per-minute quota.

    `min_request_interval` paces requests proactively at ~13s apart (the observed
    free-tier cap is 5 requests/minute = 12s/request; 13s leaves a small margin) so most
    calls never hit a 429 in the first place, rather than relying purely on reactive
    backoff. On a 429 that does happen anyway, the wait is exactly what the server's own
    RetryInfo says (see _parse_gemini_retry_delay), not a guessed escalating backoff."""
    global _last_gemini_request_time
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": temperature, "thinkingConfig": {"thinkingLevel": thinking_level}},
    }
    url = f"{GEMINI_BASE_URL}/models/{model}:generateContent"
    for attempt in range(1, max_retries + 1):
        wait_for_pacing = min_request_interval - (time.monotonic() - _last_gemini_request_time)
        if wait_for_pacing > 0:
            time.sleep(wait_for_pacing)
        try:
            resp = requests.post(url, params={"key": provider.api_key}, json=body, timeout=timeout)
            _last_gemini_request_time = time.monotonic()
        except requests.exceptions.RequestException as e:
            wait = min(60, 2 ** attempt)
            print(f"  [network error] gemini/{model}: {e}; sleeping {wait}s (attempt {attempt}/{max_retries})")
            time.sleep(wait)
            continue
        if resp.status_code == 429:
            delay, is_daily = _parse_gemini_429(resp)
            if is_daily:
                print(f"  [429] gemini/{model}: daily free-tier quota hit "
                      f"(resets in {delay/3600:.1f}h if given) -- exiting cleanly rather "
                      f"than sleeping in-process; a daily-scheduled re-run will pick "
                      f"this back up tomorrow (see run_gemini_daily.bat)")
                raise GeminiDailyQuotaExceeded(
                    f"gemini/{model} daily quota exceeded, resets in "
                    f"{delay if delay is not None else 'an unknown number of'} seconds")
            wait = (delay + 2) if delay is not None else min(60, 15 * attempt)
            print(f"  [429] gemini/{model}: server says retry in {delay}s, sleeping {wait:.0f}s "
                  f"(attempt {attempt}/{max_retries})")
            time.sleep(wait)
            continue
        if resp.status_code == 503:
            # "Model is currently experiencing high demand" -- transient overload,
            # observed to clear within seconds, unrelated to the free-tier quota.
            wait = min(30, 5 * attempt)
            print(f"  [503] gemini/{model}: overloaded, sleeping {wait}s (attempt {attempt}/{max_retries})")
            time.sleep(wait)
            continue
        if resp.status_code >= 500:
            wait = min(60, 2 ** attempt)
            print(f"  [{resp.status_code}] gemini/{model}: server error, sleeping {wait}s")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        text = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
        # Wrapped in the same shape chat_completion() returns (a single dict with
        # choices[0].message.content) so parse_prediction()/classify_one() work
        # unchanged regardless of provider; the full native Gemini response is kept
        # under _raw for caching/debugging without breaking that shared contract.
        return {"choices": [{"message": {"content": text}}], "_raw": data}
    raise RuntimeError(f"Exceeded retries calling gemini/{model}")


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
