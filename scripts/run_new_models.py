"""
v1.1 runner for Baseten and OpenRouter-free models (PREREG_v1.1.md). Same prompt as v1.0,
temperature 0, no tools, max_tokens 2048, plus the model's extra_params from config.json
(its chosen reasoning level). Caches every response, whole, with usage, finish_reason,
serving provider and request time, to llm_logs/<dir>/<ruling>.json (probe runs go to
llm_probes/<dir>/). Resumable: cached rulings are never re-sent.

Every HTTP request this script makes is appended to run_logs/api_calls.jsonl (time,
method, endpoint, model, status, tokens; never the key or the prompt text).

Spend guards (see PREREG_v1.1.md section 8):
  baseten     stops everything on 402 or any billing/credit/quota error; tracks list-price
              cost from real token usage; if BASETEN_FREE_CREDIT_USD is set, never lets the
              running total pass it.
  openrouter  refuses any id that does not end in ":free" with listed prompt AND completion
              price "0" (checked live before the run); reads GET /key before the first call
              and after every 10 calls and stops at once if `usage` rises above its
              starting value; stops cleanly when free_model_daily_requests.remaining is 0;
              one request every 4 seconds.
"""
import argparse
import csv
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from llm_client import available_providers  # noqa: E402
from run_llm_classification import build_messages, parse_prediction, code_is_valid  # noqa: E402

ROOT = M.ROOT
PROBES_DIR = ROOT / "llm_probes"
PROBE_IDS = ROOT / "data" / "probe_ids.csv"
CALL_LOG = ROOT / "run_logs" / "api_calls.jsonl"
PROBE_PROMPT = ('What 10-digit HTSUS code did CBP assign in ruling {rn}? '
                'Reply with JSON {{"hts_code": ...}}')
OR_PACE_SECONDS = 4.0
MAX_ATTEMPTS = 3

stop_event = threading.Event()
lock = threading.Lock()


class StopRun(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def log_call(method, endpoint, model, status, usage=None, note=None):
    CALL_LOG.parent.mkdir(exist_ok=True)
    rec = {"time": now(), "method": method, "endpoint": endpoint, "model": model, "status": status}
    if usage:
        rec["prompt_tokens"] = usage.get("prompt_tokens")
        rec["completion_tokens"] = usage.get("completion_tokens")
    if note:
        rec["note"] = note
    with lock:
        with CALL_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")


def billing_error(status, text):
    t = (text or "").lower()
    return status == 402 or any(k in t for k in ("insufficient", "credit", "billing", "payment", "quota", "exceeded your"))


def or_key_state(provider):
    resp = requests.get("https://openrouter.ai/api/v1/key", headers=provider.auth_header, timeout=60)
    log_call("GET", "openrouter.ai/api/v1/key", None, resp.status_code)
    d = resp.json()["data"]
    return d["usage"], d["free_model_daily_requests"]["remaining"], d["free_model_daily_requests"]["used"]


def check_openrouter_model(model):
    """Free models: id must end in :free and both listed prices must be "0". A model
    marked paid in config.json (user-authorised, with max_spend_usd) must instead be
    listed at exactly the configured prices."""
    model_id = model["model_id"]
    resp = requests.get("https://openrouter.ai/api/v1/models", timeout=60)
    log_call("GET", "openrouter.ai/api/v1/models", None, resp.status_code)
    m = next((x for x in resp.json()["data"] if x["id"] == model_id), None)
    if m is None:
        raise StopRun(f"{model_id} not in the OpenRouter model list")
    if model.get("paid"):
        if not model.get("max_spend_usd"):
            raise StopRun(f"{model_id} is paid but config.json has no max_spend_usd")
        pin, pout = float(m["pricing"]["prompt"]) * 1e6, float(m["pricing"]["completion"]) * 1e6
        if abs(pin - model["price_in_per_1m"]) > 1e-9 or abs(pout - model["price_out_per_1m"]) > 1e-9:
            raise StopRun(f"{model_id}: listed price ${pin}/{pout} per 1M differs from config; refusing")
        return
    if not model_id.endswith(":free"):
        raise StopRun(f"refusing {model_id}: id does not end in :free")
    if str(m["pricing"].get("prompt")) != "0" or str(m["pricing"].get("completion")) != "0":
        raise StopRun(f"refusing {model_id}: not listed with prompt AND completion price '0'")


def one_call(provider, model, messages):
    body = {"model": model["model_id"], "messages": messages, "temperature": 0.0, "max_tokens": 2048,
            **model.get("extra_params", {})}
    endpoint = provider.base_url.replace("https://", "") + provider.chat_path
    last = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if stop_event.is_set():
            raise StopRun("stopped")
        t0 = time.time()
        requested_at = now()
        try:
            resp = requests.post(provider.base_url + provider.chat_path,
                                 headers={**provider.auth_header, "Content-Type": "application/json"},
                                 json=body, timeout=240)
        except requests.exceptions.RequestException as e:
            last = f"network:{type(e).__name__}"
            log_call("POST", endpoint, model["model_id"], last)
            time.sleep(min(30, 5 * attempt))
            continue
        latency = time.time() - t0
        text = resp.text
        if resp.status_code == 200:
            d = resp.json()
            err = d.get("error")
            if err:  # OpenRouter returns upstream errors inside a 200 body
                code = err.get("code")
                last = f"body_error:{code}:{str(err.get('message'))[:80]}"
                log_call("POST", endpoint, model["model_id"], last)
                if billing_error(code if isinstance(code, int) else 0, str(err)):
                    raise StopRun(f"billing/quota error in body: {err}")
                time.sleep(min(30, 8 * attempt))
                continue
            log_call("POST", endpoint, model["model_id"], 200, d.get("usage"))
            return d, latency, requested_at, body, resp.status_code
        log_call("POST", endpoint, model["model_id"], resp.status_code)
        if billing_error(resp.status_code, text):
            raise StopRun(f"HTTP {resp.status_code} billing/credit/quota-type error: {text[:200]}")
        last = f"http:{resp.status_code}"
        if resp.status_code in (401, 403):
            raise StopRun(f"HTTP {resp.status_code}: {text[:200]}")
        if resp.status_code == 429:
            time.sleep(float(resp.headers.get("Retry-After", 10 * attempt)))
        else:
            time.sleep(min(30, 5 * attempt))
    return None, None, None, body, last


def cached_cost(model):
    tot = 0.0
    d = M.model_dir(model)
    for fp in d.glob("*.json") if d.exists() else []:
        u = json.loads(fp.read_text(encoding="utf-8")).get("usage") or {}
        tot += (u.get("prompt_tokens", 0) * model["price_in_per_1m"]
                + u.get("completion_tokens", 0) * model["price_out_per_1m"]) / 1e6
    return tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=None, help="only the first N rulings of this model's sample")
    ap.add_argument("--probe", action="store_true", help="Check A: ruling number only, no description")
    ap.add_argument("--threads", type=int, default=None)
    args = ap.parse_args()

    model = M.by_id(args.model)
    prov_name = model["provider"]
    provider = {p.name: p for p in available_providers()}.get(prov_name)
    if provider is None:
        print(f"no key for provider {prov_name}", file=sys.stderr)
        sys.exit(1)

    usable = [json.loads(l) for l in M.USABLE_PATH.read_text(encoding="utf-8").splitlines()]
    by_rn = {r["rulingNumber"]: r for r in usable}
    if args.probe:
        with PROBE_IDS.open(encoding="utf-8") as f:
            ids = [row["rulingNumber"] for row in csv.DictReader(f)]
        ids = ids[:100] if prov_name == "baseten" else ids[:25]
        out_dir = PROBES_DIR / M.dir_name(model)
    else:
        ids = M.sample_ids(model) or [r["rulingNumber"] for r in usable]
        out_dir = M.model_dir(model)
    if args.n:
        ids = ids[: args.n]
    out_dir.mkdir(parents=True, exist_ok=True)
    todo = [rn for rn in ids if not (out_dir / f"{rn}.json").exists()]
    print(f"{model['model_id']}: {len(ids)} rulings in scope, {len(todo)} to call"
          f"{' (probe)' if args.probe else ''}", flush=True)

    or_start_usage = None
    if prov_name == "openrouter":
        check_openrouter_model(model)
        or_start_usage, remaining, used = or_key_state(provider)
        print(f"OpenRouter key before: usage={or_start_usage} free_model_daily_requests used={used} remaining={remaining}", flush=True)
        if remaining <= 0 and not model.get("paid"):
            print("daily free-model allowance already used up; stopping cleanly for today")
            return

    credit = os.environ.get("BASETEN_FREE_CREDIT_USD")
    credit = float(credit) if credit and credit[:1].isdigit() else None
    spent = {"usd": cached_cost(model) if (prov_name == "baseten" or model.get("paid")) else 0.0}
    counters = {"done": 0, "failed": 0, "consec_fail": 0}

    def work(rn):
        if stop_event.is_set():
            return
        row = by_rn[rn]
        if args.probe:
            messages = [{"role": "user", "content": PROBE_PROMPT.format(rn=rn)}]
        else:
            messages = build_messages(row["cleaned_description"])
        if prov_name == "openrouter":
            time.sleep(OR_PACE_SECONDS)
        try:
            d, latency, requested_at, body, status = one_call(provider, model, messages)
        except StopRun as e:
            print(f"STOP: {e}", flush=True)
            stop_event.set()
            return
        if d is None:
            with lock:
                counters["failed"] += 1
                counters["consec_fail"] += 1
                if counters["consec_fail"] >= 6:
                    print("STOP: 6 consecutive failed rulings; provider looks down", flush=True)
                    stop_event.set()
            print(f"  skipped {rn} after {MAX_ATTEMPTS} attempts ({status})", flush=True)
            return
        choice = d["choices"][0]
        content = choice["message"].get("content")
        finish = choice.get("finish_reason")
        digits, reason, perr = parse_prediction(content)
        if finish == "length":
            digits, reason, perr = None, None, "truncated"
        valid = False if perr else code_is_valid(digits, row["rulingDate"])
        usage = d.get("usage") or {}
        rec = {"rulingNumber": rn, "rulingDate": row["rulingDate"], "true_code": row["true_code"],
               "model": model["model_id"], "probe": bool(args.probe), "raw_response": d,
               "predicted_code": digits, "predicted_reason": reason, "parse_error": perr,
               "valid_code": valid, "tag": None if (not perr and valid) else "INVALID_CODE",
               "finish_reason": finish, "usage": usage, "provider_served": d.get("provider"),
               "requested_at": requested_at, "latency_s": round(latency, 3),
               "request_params": {k: v for k, v in body.items() if k != "messages"}}
        (out_dir / f"{rn}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
        with lock:
            counters["done"] += 1
            counters["consec_fail"] = 0
            spent["usd"] += (usage.get("prompt_tokens", 0) * model["price_in_per_1m"]
                             + usage.get("completion_tokens", 0) * model["price_out_per_1m"]) / 1e6
            if model.get("paid") and spent["usd"] >= model["max_spend_usd"]:
                print(f"STOP: list-price spend ${spent['usd']:.4f} reached the ${model['max_spend_usd']} cap", flush=True)
                stop_event.set()
            if credit is not None and prov_name == "baseten" and spent["usd"] >= credit:
                print(f"STOP: list-price spend ${spent['usd']:.4f} reached BASETEN_FREE_CREDIT_USD", flush=True)
                stop_event.set()
            n_done = counters["done"]
        if n_done % 25 == 0:
            print(f"  {n_done}/{len(todo)} done, list-price so far ${spent['usd']:.4f}", flush=True)
        if prov_name == "openrouter" and n_done % (5 if model.get("paid") else 10) == 0:
            usage_now, remaining, used = or_key_state(provider)
            if model.get("paid"):
                if usage_now - or_start_usage >= model["max_spend_usd"]:
                    print(f"STOP: spent ${usage_now - or_start_usage:.4f} of the ${model['max_spend_usd']} cap", flush=True)
                    stop_event.set()
            elif usage_now > or_start_usage:
                print(f"STOP: OpenRouter usage rose from {or_start_usage} to {usage_now}", flush=True)
                stop_event.set()
            if remaining <= 0 and not model.get("paid"):
                print("daily free-model allowance reached 0; stopping cleanly", flush=True)
                stop_event.set()

    threads = args.threads or (4 if prov_name == "baseten" else 1)
    with ThreadPoolExecutor(max_workers=threads) as ex:
        list(ex.map(work, todo))

    print(f"finished: {counters['done']} new, {counters['failed']} skipped, stopped={stop_event.is_set()}", flush=True)
    if prov_name == "baseten" or model.get("paid"):
        print(f"cumulative list-price cost for {model['model_id']} (all cached calls): ${cached_cost(model):.4f}", flush=True)
    if prov_name == "openrouter":
        usage_now, remaining, used = or_key_state(provider)
        print(f"OpenRouter key after: usage={usage_now} (start {or_start_usage}) used={used} remaining={remaining}", flush=True)
        if model.get("paid"):
            print(f"OpenRouter spend this run: ${usage_now - or_start_usage:.4f} (cap ${model['max_spend_usd']})", flush=True)
        elif usage_now > or_start_usage:
            print("WARNING: usage increased", flush=True)
            sys.exit(2)


if __name__ == "__main__":
    main()
