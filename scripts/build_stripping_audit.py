"""
Round 2, Part 1, Check 5: generate the side-by-side file for the over-stripped-input
audit. This script only ASSEMBLES the material -- the actual judgment ("could a
competent human reach at least the true 6-digit code from the cleaned description
alone?") is made by hand for each of the 20 sampled cases and written into the
generated file afterward, per the build prompt's instruction to judge each one.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LLM_LOGS_DIR = ROOT / "llm_logs"
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"
RAW_RULINGS_DIR = ROOT / "data" / "raw" / "rulings"
REVIEW_DIR = ROOT / "review"


def load_model_results():
    model_dirs = sorted(p for p in LLM_LOGS_DIR.rglob("*") if p.is_dir() and any(p.glob("*.json")) and "lang_" not in p.name and not p.name.startswith("gemini"))
    out = {}
    for d in model_dirs:
        model_id = d.relative_to(LLM_LOGS_DIR).as_posix()
        out[model_id] = [json.loads(fp.read_text(encoding="utf-8")) for fp in sorted(d.glob("*.json"))]
    return out


def main():
    all_results = load_model_results()
    usable_by_rn = {}
    for r in (json.loads(l) for l in USABLE_PATH.read_text(encoding="utf-8").splitlines()):
        usable_by_rn[r["rulingNumber"]] = r

    # Pool all (model, ruling) pairs that are wrong at the 10-digit level.
    wrong_pairs = []
    for model_id, rows in all_results.items():
        for r in rows:
            if r["true_code"] != r.get("predicted_code"):
                wrong_pairs.append((model_id, r))

    random.seed(20261002)
    sample = random.sample(wrong_pairs, 20)

    lines = [
        "# Stripping audit (Round 2, Part 1, Check 5)\n",
        "For each of 20 random wrong answers: the cleaned description actually sent to the "
        "model, the original ruling's full description section (everything before the "
        "classification discussion, undstripped), the true code, and the predicted code. "
        "**Judgment** (filled in by hand, not automated): could a competent human reach at "
        "least the true 6-digit code from the CLEANED description alone (material, "
        "function, composition, dimensions, use all present)?\n",
    ]

    for i, (model_id, r) in enumerate(sample, 1):
        rn = r["rulingNumber"]
        usable = usable_by_rn.get(rn, {})
        cleaned = usable.get("cleaned_description", "(not found)")
        raw_path = RAW_RULINGS_DIR / f"{rn}.json"
        raw_text = json.loads(raw_path.read_text(encoding="utf-8")).get("text", "") if raw_path.exists() else ""
        lines.append(f"\n## {i}. {rn} (model: {model_id})\n")
        lines.append(f"**True code:** {r['true_code']}  |  **Predicted:** {r.get('predicted_code')}\n")
        lines.append(f"\n**Cleaned description (sent to model):**\n\n> {cleaned}\n")
        lines.append(f"\n<details><summary>Original raw ruling text</summary>\n\n```\n{raw_text}\n```\n</details>\n")
        lines.append("\n**Judgment:** TODO\n")

    (REVIEW_DIR / "stripping_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REVIEW_DIR / 'stripping_audit.md'} with {len(sample)} cases -- judgments still TODO, to be filled in by hand.")


if __name__ == "__main__":
    main()
