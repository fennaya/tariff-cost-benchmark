"""
Phase 3: resolve each usable ruling's true 10-digit code to the column-1 General (MFN)
duty rate from the HTS revision in force on the ruling's date, and classify the rate.

"In force on the ruling's date" = the most recent revision (by its own effective/
published date) that is <= the ruling's date. If a ruling predates the earliest
downloaded revision (2026 Basic Edition, 2025-12-31), the Basic Edition is used (it's
the earliest available and was in force at the start of the window).
"""
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTS_DIR = ROOT / "data" / "raw" / "hts_revisions"
COMPACT_HTS_DIR = ROOT / "data" / "compact" / "hts_revisions"  # tracked fallback, see build_compact_hts.py
REVISIONS_INDEX = json.loads((ROOT / "data" / "raw" / "hts_revisions_index.json").read_text())
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
OUT_PATH = ROOT / "data" / "processed" / "rulings_with_duty.jsonl"

REVISIONS_SORTED = sorted(
    ((rid, datetime.strptime(d, "%Y-%m-%d")) for rid, d in REVISIONS_INDEX),
    key=lambda x: x[1],
)

_revision_cache = {}


def revision_for_date(ruling_date: datetime):
    chosen = REVISIONS_SORTED[0][0]
    for rid, eff_date in REVISIONS_SORTED:
        if eff_date <= ruling_date:
            chosen = rid
        else:
            break
    return chosen


def read_revision_rows(release_id):
    """Rows (htsno/general/description at minimum) of one HTS revision: the raw USITC dump
    if it has been fetched locally, else the tracked compact copy."""
    raw = HTS_DIR / f"{release_id}.json"
    if raw.exists():
        return json.loads(raw.read_text(encoding="utf-8"))
    import gzip
    with gzip.open(COMPACT_HTS_DIR / f"{release_id}.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


RELEASE_RATES_DIR = ROOT / "data" / "compact" / "hts_rates"  # General rates parsed from the archived PDFs


def _release_rates(release_id):
    import gzip
    fp = RELEASE_RATES_DIR / f"{release_id}.rates.json.gz"
    if not fp.exists():
        return {}
    with gzip.open(fp, "rt", encoding="utf-8") as f:
        return json.load(f)


def load_revision(release_id, use_release_rates=True):
    """code-digits -> General rate text for one HTS release. The JSON export is always the
    CURRENT schedule (DECISIONS.md 2026-10-06), so with use_release_rates the rates parsed
    from that release's own archived PDF (parse_release_rates.py) are layered on top: they
    replace the JSON text when they parse cleanly, and add 8/6-digit parent lines the JSON
    has no row for. use_release_rates=False gives the original JSON-only lookup."""
    key = (release_id, use_release_rates)
    if key in _revision_cache:
        return _revision_cache[key]
    data = read_revision_rows(release_id)
    lookup = {}
    for row in data:
        htsno = row.get("htsno") or ""
        digits = re.sub(r"\D", "", htsno)
        if digits:
            lookup[digits] = row.get("general", "")
    if use_release_rates:
        for code, text in _release_rates(release_id).items():
            if classify_rate(text)[0] != "other":
                lookup[code] = text
            elif code not in lookup:
                lookup[code] = ""
    _revision_cache[key] = lookup
    return lookup


def resolve_rate(lookup, true_code_10digit):
    """The rate often lives at the 8-digit tariff-item level; the 10-digit statistical
    suffix just inherits it and has an empty `general` field of its own. Walk up through
    4-2-2-2 digit boundaries (10 -> 8 -> 6 -> 4) and use the first non-empty rate found."""
    found_any_code = False
    for length in (10, 8, 6, 4):
        prefix = true_code_10digit[:length]
        if prefix in lookup:
            found_any_code = True
            val = lookup[prefix]
            if val and val.strip():
                return val, None
    if not found_any_code:
        return None, "code_not_found"
    return "", None  # code exists at every level checked but every rate field was empty


def classify_rate(rate_str, strip_markup=True):
    """Return (rate_type, ad_valorem_pct_or_None)."""
    if rate_str is None:
        return "missing", None
    s = (re.sub(r"<[^>]+>", "", rate_str) if strip_markup else rate_str).strip()  # USITC markup, e.g. "2.5% <u></u>" (5 rates in ch. 87); strip_markup=False reproduces the original Phase 3 behavior
    if s == "":
        return "missing", None
    if s.lower() == "free":
        return "free", 0.0

    has_pct = "%" in s
    has_specific_unit = bool(re.search(r"[¢$]|/kg|/doz|/gross|/liter|/l\b|/m2|/m3|/pcs|/no\.|/tan", s, re.IGNORECASE))
    has_plus = "+" in s

    if has_pct and (has_specific_unit or has_plus):
        return "compound", None
    if has_pct and not has_specific_unit:
        m = re.match(r"^(\d+(?:\.\d+)?)\s*%$", s)
        if m:
            return "ad_valorem", float(m.group(1))
        return "other", None  # e.g. "Free + 5%" edge phrasing, or ranges -- treat conservatively
    if has_specific_unit:
        return "specific", None
    return "other", None


def main():
    rows = [json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()]
    out_rows = []
    rate_type_counts = {}
    missing_code_count = 0

    for r in rows:
        ruling_date = datetime.fromisoformat(r["rulingDate"].replace("Z", ""))
        release_id = revision_for_date(ruling_date)
        lookup = load_revision(release_id)
        rate_str, resolve_error = resolve_rate(lookup, r["true_code"])
        if resolve_error:
            missing_code_count += 1
            rate_type, ad_valorem_pct = resolve_error, None
        else:
            rate_type, ad_valorem_pct = classify_rate(rate_str)

        rate_type_counts[rate_type] = rate_type_counts.get(rate_type, 0) + 1
        out_rows.append({
            **r,
            "hts_revision_used": release_id,
            "true_rate_raw": rate_str,
            "true_rate_type": rate_type,
            "true_rate_ad_valorem_pct": ad_valorem_pct,
        })

    total = len(out_rows)
    usable_rate = rate_type_counts.get("ad_valorem", 0) + rate_type_counts.get("free", 0)
    print(f"Total usable rulings: {total}")
    print("Rate type breakdown:")
    for rt, count in sorted(rate_type_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {rt}: {count}")
    print(f"Codes not found in their revision's HTS export: {missing_code_count}")
    pct = 100 * usable_rate / total if total else 0
    print(f"Gate 3: {usable_rate}/{total} = {pct:.1f}% resolve to ad valorem or free (need >=85%)")

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {OUT_PATH}")

    summary_path = ROOT / "data" / "processed" / "duty_rate_summary.json"
    summary_path.write_text(json.dumps({
        "total_usable_rulings": total,
        "rate_type_counts": rate_type_counts,
        "usable_for_cost_analysis": usable_rate,
        "gate3_pass_share": usable_rate / total if total else None,
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
