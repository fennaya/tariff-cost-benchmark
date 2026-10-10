"""
v1.2: one test call per setting to find the lowest reasoning level each new model accepts
(PREREG_v1.2.md sections 3 and 4, same procedure as v1.1). Uses the first usable ruling and
the real prompt, temperature 0, max_tokens 2048. Picks the first variant that gives 0 reasoning
tokens and a non-empty answer, else the variant with the fewest reasoning tokens, writes it to
config.json (extra_params, reasoning_effort) and the full test log to
run_logs/v1_2_settings_test.json. Every call is logged to run_logs/api_calls.jsonl and counted
against the $25 session cap. The key is never printed.
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
import run_new_models as R  # noqa: E402
from llm_client import available_providers  # noqa: E402
from run_llm_classification import build_messages  # noqa: E402

VARIANTS = [("reasoning.effort=none", {"reasoning": {"effort": "none"}}),
            ("reasoning.enabled=false", {"reasoning": {"enabled": False}}),
            ("reasoning.effort=minimal", {"reasoning": {"effort": "minimal"}}),
            ("reasoning.effort=low", {"reasoning": {"effort": "low"}}),
            ("no reasoning parameter", {})]


def main():
    cfg = json.loads(M.CONFIG_PATH.read_text(encoding="utf-8"))
    provider = {p.name: p for p in available_providers()}["openrouter"]
    row = json.loads(M.USABLE_PATH.open(encoding="utf-8").readline())
    messages = build_messages(row["cleaned_description"])
    log = {}
    for m in cfg["models"]:
        if m.get("cohort") != "v1.2" or m.get("role") == "replication" and False:
            continue
        mid = m["model_id"]
        api = m.get("api_model", mid)
        tests = []
        chosen = None
        for name, extra in VARIANTS:
            R.check_session_cap(m)
            body = {"model": api, "messages": messages, "temperature": 0.0, "max_tokens": 2048, **extra}
            if m.get("provider_routing"):
                body["provider"] = m["provider_routing"]
            resp = requests.post(provider.base_url + provider.chat_path, headers={**provider.auth_header, "Content-Type": "application/json"},
                                 json=body, timeout=240)
            d = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            if resp.status_code != 200 or "choices" not in d:
                err = str((d.get("error") or {}).get("message") or resp.text)[:160]
                R.log_call("POST", "openrouter.ai/api/v1/chat/completions", mid, resp.status_code, note="settings test: " + name)
                tests.append({"variant": name, "http": resp.status_code, "error": err})
                print(f"{mid} | {name} -> HTTP {resp.status_code}: {err}", flush=True)
                time.sleep(2)
                continue
            u = d.get("usage") or {}
            R.log_call("POST", "openrouter.ai/api/v1/chat/completions", mid, 200, u, note="settings test: " + name)
            cost = R.add_session_cost(m, u)
            rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
            content = d["choices"][0]["message"].get("content") or ""
            problem = R.response_problem(d, m)
            t = {"variant": name, "http": 200, "returned_model": d.get("model"), "provider": d.get("provider"), "finish": d["choices"][0].get("finish_reason"),
                 "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"), "reasoning_tokens": rt, "content_chars": len(content), "cost": cost, "problem": problem}
            tests.append(t)
            print(f"{mid} | {name} -> 200 model={d.get('model')} provider={d.get('provider')} finish={t['finish']} in={t['in']} out={t['out']} reasoning={rt} chars={len(content)} cost=${cost:.5f} problem={problem}", flush=True)
            if rt == 0 and content.strip() and not problem:
                chosen = (name, extra)
                break
            time.sleep(1)
        if chosen is None:
            ok = [t for t in tests if t.get("http") == 200 and not t.get("problem") and t.get("content_chars")]
            if ok:
                best = min(ok, key=lambda t: t["reasoning_tokens"])
                chosen = next((n, e) for n, e in VARIANTS if n == best["variant"])
        log[mid] = {"tests": tests, "chosen": chosen[0] if chosen else None}
        if chosen:
            m["extra_params"] = chosen[1]
            m["reasoning_effort"] = chosen[0]
        print(f"==> {mid}: chosen = {chosen[0] if chosen else 'NONE ACCEPTED'}", flush=True)
    M.CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    (M.ROOT / "run_logs" / "v1_2_settings_test.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print("session cost so far: $%.5f" % R._session_read()["usd"])


if __name__ == "__main__":
    main()
