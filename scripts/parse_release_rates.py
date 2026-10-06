"""
Parses the General (column 1, MFN) rate text of every 2026 HTS release from the archived
PDFs (data/raw/hts_older_pdf/, fetched by fetch_older_hts.py) into
data/compact/hts_rates/<release>.rates.json.gz ({4/6/8-digit code: cleaned rate text}).
Parser accuracy against the current-schedule JSON is measured in check_rate_impact.py.
"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hts_pdf_parser import extract_rates, clean_rate_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PDFS = ROOT / "data" / "raw" / "hts_older_pdf"
OUT = ROOT / "data" / "compact" / "hts_rates"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for pdf in sorted(PDFS.glob("2026*.pdf")):
        out = OUT / f"{pdf.stem}.rates.json.gz"
        if out.exists():
            continue
        rates = {k: clean_rate_text(v) for k, v in extract_rates(str(pdf)).items()}
        with gzip.open(out, "wt", encoding="utf-8") as f:
            json.dump(rates, f, separators=(",", ":"), sort_keys=True)
        print(f"{pdf.stem}: {len(rates)} rated entries", flush=True)


if __name__ == "__main__":
    main()
