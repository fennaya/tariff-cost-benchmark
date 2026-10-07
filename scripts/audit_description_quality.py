"""
Description-quality audit (found after pre-registration; DECISIONS.md 2026-10-07). Some cleaned
descriptions are not product descriptions at all (marking-rule boilerplate, labelling advice, half
a sentence), so a model cannot classify them and those rows measure the extractor, not the model.

A ruling is flagged INADEQUATE if its cleaned description
  (a) is under 150 characters, or
  (b) is mostly regulatory boilerplate: at least half of its characters sit in sentences that match
      a boilerplate pattern (19 C.F.R. / Customs Regulations, Textile Fiber Products Identification
      Act, FTC / FCC / FDA / CPSC referrals, marking or labelling advice, "country of origin",
      "contact the ...", "duties cited above", and similar) AND the text outside those sentences is
      under 150 characters, a stand-in for "no product noun" (no product description is left).
Rule (a) is deliberately blunt: some short descriptions are adequate (e.g. a one-sentence part
description) and are flagged anyway; the spot check records how many.

Writes review/description_quality.md and review/description_quality.json (the flagged ids and the
rule that fired). Also writes review/description_quality_spotcheck_sample.json: the fixed-seed
sample of 20 flagged and 20 unflagged rulings to be read by eye.
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_CHARS = 150
REST_CHARS = 150
SEED = 20261008

BOILER = re.compile(
    r"(19\s*C\.?F\.?R|Customs Regulations|Code of Federal Regulations|Textile Fiber Products Identification Act|"
    r"Wool Products Labeling|Federal Trade Commission|\bFTC\b|ftc\.gov|country of origin|ultimate purchaser|"
    r"conspicuous place|indelibly|marking|labell?(ed|ing)|Federal Communications Commission|\bFCC\b|"
    r"Food and Drug Administration|\bFDA\b|Consumer Product Safety|CPSC|duties cited above|We suggest you contact|"
    r"contact the|for information concerning|information may also be obtained|Tariff Act|section 304|Lacey Act|"
    r"binding ruling|\bAct\b|U\.S\.C\.)", re.I)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if s.strip()]


def assess(text):
    """Returns (flagged, rule, boilerplate_share, rest_chars)."""
    if len(text) < MIN_CHARS:
        return True, "under_150_chars", None, None
    bl = sum(len(s) for s in sentences(text) if BOILER.search(s))
    share = bl / len(text)
    rest = len(text) - bl
    if share >= 0.5 and rest < REST_CHARS:
        return True, "regulatory_boilerplate", round(share, 2), rest
    return False, None, round(share, 2), rest


def main():
    rows = [json.loads(l) for l in (ROOT / "data" / "processed" / "usable_rulings.jsonl").read_text(encoding="utf-8").splitlines()]
    flagged, ok = [], []
    for r in rows:
        f, rule, share, rest = assess(r["cleaned_description"])
        rec = {"rulingNumber": r["rulingNumber"], "rulingDate": r["rulingDate"], "rule": rule, "chars": len(r["cleaned_description"]),
               "text": r["cleaned_description"]}
        (flagged if f else ok).append(rec)
    n_short = sum(1 for x in flagged if x["rule"] == "under_150_chars")
    n_boiler = sum(1 for x in flagged if x["rule"] == "regulatory_boilerplate")
    print(f"{len(rows)} usable rulings; flagged INADEQUATE: {len(flagged)} ({len(flagged) / len(rows):.1%}); "
          f"under 150 characters: {n_short}; regulatory boilerplate (not already short): {n_boiler}")
    (ROOT / "review" / "description_quality.json").write_text(
        json.dumps({"flagged": {x["rulingNumber"]: x["rule"] for x in flagged}, "n_usable": len(rows)}, indent=2), encoding="utf-8")
    rng = random.Random(SEED)
    sample = {"flagged": [x["rulingNumber"] for x in rng.sample(flagged, min(20, len(flagged)))],
              "unflagged": [x["rulingNumber"] for x in rng.sample(ok, 20)]}
    (ROOT / "review" / "description_quality_spotcheck_sample.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")

    L = ["# Description-quality audit (scripts/audit_description_quality.py)\n",
         "Found after pre-registration. A ruling is INADEQUATE if its cleaned description is under 150 characters, or if at least half of it is regulatory boilerplate and under 150 characters of other text remain (a stand-in for \"no product noun\"). The 150-character rule is blunt: some short descriptions are adequate and are flagged anyway.\n",
         "Spot check by eye (20 flagged, 20 unflagged): review/description_quality_spotcheck.md.\n",
         f"**Flagged: {len(flagged)} of {len(rows)} usable rulings ({len(flagged) / len(rows):.1%})**: {n_short} under 150 characters, {n_boiler} regulatory boilerplate.\n",
         "| Ruling | Rule | Characters | First 200 characters of the cleaned description |", "|---|---|---|---|"]
    for x in sorted(flagged, key=lambda x: x["rulingNumber"]):
        L.append(f"| {x['rulingNumber']} | {x['rule']} | {x['chars']} | {x['text'][:200].replace('|', '/').replace(chr(10), ' ')} |")
    (ROOT / "review" / "description_quality.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
