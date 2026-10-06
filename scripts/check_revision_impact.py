"""
Impact check for a data problem found 2026-10-06 (DECISIONS.md): the project's per-revision
JSON files (data/raw/hts_revisions/) are all the CURRENT schedule, because the export API
ignores the `release` parameter. Here the true per-release code sets come from the archived
PDFs (fetch_older_hts.py). Question: would any answer's validity, or any true code's
existence, change if each ruling were checked against the PDF-derived HTS release in force
on its own date instead? Compares 10-digit code sets only (the PDF parse matches the
current JSON exactly at 10 digits, see DECISIONS.md). Duty RATES cannot be checked this
way (rates are not parsed from the PDFs); see the limitation text in findings.md.
Writes review/revision_impact.md.
"""
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from analysis import load_model_results  # noqa: E402
from parse_duty_rates import revision_for_date, load_revision  # noqa: E402

MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "allam-2-7b"]
D = ROOT / "data" / "compact" / "hts_older"


def pdf_codes(release):
    return set(json.loads(gzip.open(D / f"{release}.codes.json.gz", "rt", encoding="utf-8").read())["codes10"])


def main():
    L = ["# Revision-impact check (scripts/check_revision_impact.py)\n"]
    cur = {k for k in load_revision("CURRENT") if len(k) == 10}
    L += ["## 2026 releases (PDF-derived 10-digit codes) vs the current JSON schedule\n",
          "| Release | 10-digit codes | not in current JSON | in current JSON but not in release |", "|---|---|---|---|"]
    rel_codes = {}
    for fp in sorted(D.glob("2026*.codes.json.gz")):
        r = fp.name.replace(".codes.json.gz", "")
        rel_codes[r] = pdf_codes(r)
        c = rel_codes[r]
        L.append(f"| {r} | {len(c)} | {len(c - cur)} | {len(cur - c)} |")
    flips = {}
    true_missing = 0
    usable = [json.loads(l) for l in (ROOT / "data" / "processed" / "usable_rulings.jsonl").read_text(encoding="utf-8").splitlines()]
    for r in usable:
        rel = revision_for_date(datetime.fromisoformat(r["rulingDate"].replace("Z", "")))
        if r["true_code"] not in rel_codes[rel]:
            true_missing += 1
    for m in MODELS:
        n_flip = n_inv_now = 0
        for r in load_model_results(ROOT / "llm_logs" / m):
            p = r.get("predicted_code")
            if not p or len(p) != 10:
                continue
            rel = revision_for_date(datetime.fromisoformat(r["rulingDate"].replace("Z", "")))
            valid_pdf = p in rel_codes[rel]
            valid_json = p in cur
            if valid_pdf != valid_json:
                n_flip += 1
        flips[m] = n_flip
    L += ["", f"True codes of the {len(usable)} usable rulings absent from their own ruling-date release (PDF-derived): **{true_missing}**.", "",
          "10-digit predicted codes whose validity differs between the ruling-date PDF release and the current JSON:", ""]
    for m in MODELS:
        L.append(f"- {m}: {flips[m]}")
    (ROOT / "review" / "revision_impact.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
