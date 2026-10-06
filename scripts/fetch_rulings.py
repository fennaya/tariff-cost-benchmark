"""
Phase 1: pull NY-collection CBP rulings from the CROSS API (rulings.cbp.gov).

Endpoints discovered by inspecting the CROSS site's own front-end network calls:
  - search:  GET /api/search?term=*&collection=NY&commodityGrouping=ALL
                  &fromDate=YYYY-MM-DD&pageSize=N&page=P&sortBy=RULING_DATE_ASC
             -> {"rulings": [ {rulingNumber, subject, rulingDate, tariffs, ...} ], "totalHits": N}
  - detail:  GET /api/ruling/{rulingNumber}
             -> {"text": "...", "tariffs": "...", "rulingDate": "...", "subject": "...", ...}

Resumable: every page and every ruling detail is cached to disk and skipped on rerun.
Politeness: >=1s between requests, descriptive User-Agent (see config.json).
"""
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())
RAW = ROOT / "data" / "raw"
SEARCH_DIR = RAW / "search_pages"
RULINGS_DIR = RAW / "rulings"
SEARCH_DIR.mkdir(parents=True, exist_ok=True)
RULINGS_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://rulings.cbp.gov"
HEADERS = {"User-Agent": CONFIG["cbp_user_agent"]}
RATE = CONFIG["rate_limit_seconds"]
FROM_DATE = CONFIG["ruling_window_start"]

session = requests.Session()
session.headers.update(HEADERS)

_last_request_time = 0.0


def _throttled_get(url, params=None, timeout=30, max_retries=3):
    global _last_request_time
    for attempt in range(1, max_retries + 1):
        wait = RATE - (time.monotonic() - _last_request_time)
        if wait > 0:
            time.sleep(wait)
        try:
            resp = session.get(url, params=params, timeout=timeout)
            _last_request_time = time.monotonic()
        except requests.RequestException as exc:
            print(f"  [retry {attempt}/{max_retries}] request error: {exc}", file=sys.stderr)
            time.sleep(RATE * attempt * 3)
            continue
        if resp.status_code == 429:
            retry_after = float(resp.headers.get("Retry-After", RATE * attempt * 5))
            print(f"  [429] rate limited, sleeping {retry_after}s", file=sys.stderr)
            time.sleep(retry_after)
            continue
        if resp.status_code >= 500:
            print(f"  [{resp.status_code}] server error, attempt {attempt}/{max_retries}", file=sys.stderr)
            time.sleep(RATE * attempt * 3)
            continue
        return resp
    raise RuntimeError(f"Failed after {max_retries} retries: {url} {params}")


def fetch_search_pages(page_size=100):
    """Paginate the NY-collection search sorted by ruling date ascending. Cache each page."""
    page = 1
    total_hits = None
    while True:
        cache_path = SEARCH_DIR / f"page_{page:04d}.json"
        if cache_path.exists():
            data = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            params = {
                "term": "*",
                "collection": "NY",
                "commodityGrouping": "ALL",
                "fromDate": FROM_DATE,
                "pageSize": page_size,
                "page": page,
                "sortBy": "RULING_DATE_ASC",
            }
            resp = _throttled_get(f"{BASE}/api/search", params=params)
            resp.raise_for_status()
            data = resp.json()
            cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"  fetched search page {page} ({len(data.get('rulings', []))} rulings)")
        total_hits = data.get("totalHits", total_hits)
        rulings = data.get("rulings", [])
        if not rulings:
            break
        yield from rulings
        if page * page_size >= (total_hits or 0):
            break
        page += 1


def fetch_ruling_detail(ruling_number):
    safe_name = ruling_number.replace("/", "_")
    cache_path = RULINGS_DIR / f"{safe_name}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    resp = _throttled_get(f"{BASE}/api/ruling/{ruling_number}")
    if resp.status_code != 200:
        print(f"  [{resp.status_code}] ruling {ruling_number} failed", file=sys.stderr)
        return None
    data = resp.json()
    cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def main(limit=None):
    print(f"Fetching NY rulings from {FROM_DATE} onward (limit={limit})...")
    count = 0
    fetched_ok = 0
    for summary in fetch_search_pages():
        if limit is not None and count >= limit:
            break
        count += 1
        rn = summary["rulingNumber"]
        detail = fetch_ruling_detail(rn)
        if detail and detail.get("text") and detail.get("rulingDate") and detail.get("tariffs") is not None:
            fetched_ok += 1
        if count % 25 == 0:
            print(f"  ...{count} processed, {fetched_ok} with all 4 fields")
    print(f"Done. Processed {count} rulings, {fetched_ok} had ruling number+date+text+tariffs.")


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit=lim)
