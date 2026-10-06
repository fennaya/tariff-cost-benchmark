"""
Phase 1 (exclusion filter) + Gate 1b: keep only rulings that classify a single product
into exactly one 10-digit HTS code, and that survived Phase 2's leak-safe cleaning.

The CROSS `tariffs` field is a comma-separated list that mixes the real classification
code(s) (chapters 01-97) with Chapter 99 additional-duty codes (Section 301/232/
reciprocal tariffs etc., always prefixed "99"). Those Chapter 99 codes are not separate
products -- they're trade-remedy overlays on the same classification -- so they are
excluded from the "how many products/codes did this ruling classify" count.

Exclusion reasons counted here become the exclusions table row for this stage.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEANED_PATH = ROOT / "data" / "processed" / "cleaned_descriptions.jsonl"
OUT_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"

DIGIT_RE = re.compile(r"\d")


def classification_codes(tariffs_str):
    if not tariffs_str:
        return []
    codes = []
    for raw in tariffs_str.split(","):
        raw = raw.strip()
        if not raw:
            continue
        digits = "".join(DIGIT_RE.findall(raw))
        if not digits:
            continue
        if digits.startswith("99"):
            continue  # Chapter 99 additional-duty overlay, not a product classification
        codes.append(digits)
    return codes


def main():
    rows = [json.loads(l) for l in CLEANED_PATH.read_text(encoding="utf-8").splitlines()]
    usable = []
    reasons = {}

    def exclude(reason):
        reasons[reason] = reasons.get(reason, 0) + 1

    for r in rows:
        if not r["cleaned_description"]:
            exclude("phase2_cleaning_failed")
            continue
        codes = classification_codes(r["tariffs"])
        distinct_codes = sorted(set(codes))
        if len(distinct_codes) == 0:
            exclude("zero_classification_codes")
            continue
        if len(distinct_codes) > 1:
            exclude("multiple_products_or_codes")
            continue
        code = distinct_codes[0]
        if len(code) != 10:
            exclude(f"non_10_digit_code_len{len(code)}")
            continue
        usable.append({
            "rulingNumber": r["rulingNumber"],
            "rulingDate": r["rulingDate"],
            "true_code": code,
            "cleaned_description": r["cleaned_description"],
            "subject": r["subject"],
        })

    print(f"Total cleaned rulings considered: {len(rows)}")
    print(f"Usable (single product, single 10-digit code, clean description): {len(usable)}")
    print("Exclusion breakdown:")
    for reason, count in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"  {reason}: {count}")

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for r in usable:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {OUT_PATH}")

    exclusions_summary_path = ROOT / "data" / "processed" / "exclusions_phase1_2.json"
    exclusions_summary_path.write_text(
        json.dumps({"total_considered": len(rows), "usable": len(usable), "excluded": reasons}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
