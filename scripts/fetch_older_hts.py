"""
Fetches every USITC HTS release named 2022*-2026* as its "finalCopy" PDF (free, public,
cached, resumable) into data/raw/hts_older_pdf/ (gitignored), parses each PDF's 10-digit
codes with hts_pdf_parser.py, and writes the parsed sets to
data/compact/hts_older/<release>.codes.json.gz (tracked, small).

Why PDFs: archived releases are published only as PDF. The site's JSON export
(reststop/exportList) takes no release parameter in the site's own code and always
returns the CURRENT schedule; scripts/fetch_hts.py passed `release=` to it and silently
got the current schedule every time (see DECISIONS.md, 2026-10-06). The release list is
from https://hts.usitc.gov/reststop/releaseList.
"""
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_hts import _throttled_get, BASE  # noqa: E402
from hts_pdf_parser import extract_codes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hts_older_pdf"
OUT = ROOT / "data" / "compact" / "hts_older"
YEARS = ("2022", "2023", "2024", "2025", "2026")


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    releases = _throttled_get(f"{BASE}/reststop/releaseList", params={}).json()
    sel = sorted(((r["name"], datetime.strptime(r["date"], "%m/%d/%Y").date().isoformat())
                  for r in releases if r["name"][:4] in YEARS), key=lambda x: x[1])
    (OUT / "release_list.json").write_text(json.dumps(sel, indent=1), encoding="utf-8")
    print(f"{len(sel)} releases named {YEARS[0]}-{YEARS[-1]}", flush=True)
    for name, date in sel:
        out = OUT / f"{name}.codes.json.gz"
        if out.exists():
            continue
        pdf = RAW / f"{name}.pdf"
        if not pdf.exists():
            resp = _throttled_get(f"{BASE}/reststop/file", params={"release": name, "filename": "finalCopy"})
            resp.raise_for_status()
            pdf.write_bytes(resp.content)
        codes = extract_codes(pdf.read_bytes())
        ten = sorted(c for c in codes if len(c) == 10)
        eight = sorted(c for c in codes if len(c) == 8)
        with gzip.open(out, "wt", encoding="utf-8") as f:
            json.dump({"release": name, "date": date, "codes10": ten, "codes8": eight}, f, separators=(",", ":"))
        flag = "" if len(ten) > 15000 else "  <-- FEW CODES, CHECK"
        print(f"  {name} ({date}): {pdf.stat().st_size / 1e6:.1f} MB pdf, {len(ten)} ten-digit codes{flag}", flush=True)


if __name__ == "__main__":
    main()
