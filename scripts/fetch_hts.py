"""
Phase 3: download the HTS revisions in force across the ruling dates from USITC.

Endpoint discovered from hts.usitc.gov's own Export page network calls:
  GET /reststop/exportList?from=0101.&to=9999.&format=JSON&styles=true[&release=<id>]
Omitting `release` returns the current release; historical releases are named like
"2026HTSRev1" (from the archive page's per-revision links, e.g.
/download?release=2026HTSRev1&releaseDate=01%2F15%2F2026).

Each revision's raw JSON is cached whole (one file per revision) and never
re-downloaded. Revisions and their effective dates are hardcoded below since they were
read once from https://hts.usitc.gov/download/archive (no JSON API for the revision
*list* itself was found; the page is server-rendered HTML).
"""
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())
RAW = ROOT / "data" / "raw" / "hts_revisions"
RAW.mkdir(parents=True, exist_ok=True)

BASE = "https://hts.usitc.gov"
HEADERS = {"User-Agent": CONFIG["cbp_user_agent"]}
RATE = CONFIG["rate_limit_seconds"]

# (release_id, effective_date "YYYY-MM-DD") -- effective_date is the revision's own
# published date (the "(MM/DD/YYYY)" in its name), i.e. the first date it is in force.
# Read from https://hts.usitc.gov/download/archive on 2026-09-28.
REVISIONS = [
    ("2026HTSBasic", "2025-12-31"),
    ("2026HTSRev1", "2026-01-16"),
    ("2026HTSRev2", "2026-01-30"),
    ("2026HTSRev3", "2026-02-11"),
    ("2026HTSRev4", "2026-02-25"),
    ("2026HTSRev5", "2026-04-08"),
    ("2026HTSRev6", "2026-04-23"),
    ("2026HTSRev7", "2026-04-29"),
    ("2026HTSRev8", "2026-05-22"),
    ("2026HTSRev9", "2026-05-28"),
    ("2026HTSRev10", "2026-06-08"),
    ("2026HTSRev11", "2026-07-01"),
    ("2026HTSRev12", "2026-07-21"),
    ("2026HTSRev13", "2026-07-28"),
    ("2026HTSRev14", "2026-07-31"),
    ("2026HTSRev15", "2026-08-03"),
    ("2026HTSRev16", "2026-08-14"),
    ("2026HTSRev17", "2026-08-24"),
    ("2026HTSRev18", "2026-09-02"),
    ("2026HTSRev19", "2026-09-15"),
]

session = requests.Session()
session.headers.update(HEADERS)
_last_request_time = 0.0


def _throttled_get(url, params, max_retries=3):
    global _last_request_time
    for attempt in range(1, max_retries + 1):
        wait = RATE - (time.monotonic() - _last_request_time)
        if wait > 0:
            time.sleep(wait)
        try:
            resp = session.get(url, params=params, timeout=120)
            _last_request_time = time.monotonic()
        except requests.RequestException as exc:
            print(f"  [retry {attempt}] {exc}", file=sys.stderr)
            time.sleep(RATE * attempt * 3)
            continue
        if resp.status_code == 429:
            time.sleep(float(resp.headers.get("Retry-After", RATE * attempt * 5)))
            continue
        if resp.status_code >= 500:
            time.sleep(RATE * attempt * 3)
            continue
        return resp
    raise RuntimeError(f"Failed after {max_retries} retries: {url} {params}")


def fetch_revision(release_id):
    cache_path = RAW / f"{release_id}.json"
    if cache_path.exists():
        print(f"  {release_id}: cached, skipping")
        return
    params = {"from": "0101.", "to": "9999.", "format": "JSON", "styles": "true"}
    if release_id != "CURRENT":
        params["release"] = release_id
    resp = _throttled_get(f"{BASE}/reststop/exportList", params=params)
    resp.raise_for_status()
    cache_path.write_bytes(resp.content)
    print(f"  {release_id}: downloaded {len(resp.content):,} bytes")


def main():
    (ROOT / "data" / "raw" / "hts_revisions_index.json").write_text(
        json.dumps(REVISIONS, indent=2), encoding="utf-8"
    )
    for release_id, eff_date in REVISIONS:
        fetch_revision(release_id)
    fetch_revision("CURRENT")


if __name__ == "__main__":
    main()
