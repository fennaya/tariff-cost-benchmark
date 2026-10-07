"""
PREREG_v1.1.md section 5: re-parse every cached response of the three original (v1.0)
models with the updated parse_prediction and confirm each predicted_code is identical to
the cached one. Exits non-zero (and the v1.1 work stops) if any differs.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import models_config as M  # noqa: E402
from run_llm_classification import parse_prediction  # noqa: E402


def main():
    bad = total = 0
    for m in M.load():
        if m.get("cohort", "v1.0") != "v1.0":
            continue
        n = diff = 0
        for fp in sorted(M.model_dir(m).glob("*.json")):
            r = json.loads(fp.read_text(encoding="utf-8"))
            content = r["raw_response"]["choices"][0]["message"].get("content")
            digits, _, err = parse_prediction(content)
            n += 1
            if digits != r.get("predicted_code") or (err is None) != (r.get("parse_error") is None):
                diff += 1
                if diff <= 3:
                    print(f"  DIFF {m['model_id']} {r['rulingNumber']}: cached={r.get('predicted_code')!r} new={digits!r}")
        print(f"{m['model_id']}: {n} re-parsed, {diff} differ")
        bad += diff
        total += n
    print(f"TOTAL: {total} re-parsed, {bad} differ")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
