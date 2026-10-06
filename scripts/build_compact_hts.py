"""
Builds data/compact/hts_revisions/<release>.json.gz from the raw USITC revision dumps in
data/raw/hts_revisions/ (gitignored, ~255 MB). Keeps only the rows with an HTS number and
only the 3 fields any analysis script reads (htsno, general, description), gzip-compressed.
parse_duty_rates.py and audit_direction.py read the raw file if present and fall back to
this compact copy otherwise, so every reported number reproduces from tracked files alone.
"""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hts_revisions"
OUT = ROOT / "data" / "compact" / "hts_revisions"
KEEP = ("htsno", "general", "description")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for fp in sorted(RAW.glob("*.json")):
        rows = json.loads(fp.read_text(encoding="utf-8"))
        slim = [{k: r.get(k) for k in KEEP} for r in rows if (r.get("htsno") or "").strip()]
        out = OUT / f"{fp.stem}.json.gz"
        with gzip.open(out, "wt", encoding="utf-8", compresslevel=9) as f:
            json.dump(slim, f, separators=(",", ":"), sort_keys=True)
        total += out.stat().st_size
        print(f"{fp.name}: {len(rows)} -> {len(slim)} rows, {out.stat().st_size / 1e6:.2f} MB")
    print(f"Total compact size: {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
