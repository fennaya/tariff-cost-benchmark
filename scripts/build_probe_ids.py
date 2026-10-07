"""
Check A (memorisation probe) sample, PREREG_v1.1.md section 4: one fixed random draw of 100
usable rulings, seed 20261007, saved before any probe call. Baseten models use all 100;
the OpenRouter model uses the first 25.
"""
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261007
usable = [json.loads(l) for l in (ROOT / "data" / "processed" / "usable_rulings.jsonl").read_text(encoding="utf-8").splitlines()]
sample = random.Random(SEED).sample(usable, 100)
with (ROOT / "data" / "probe_ids.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rulingNumber", "rulingDate", "true_code"])
    for r in sample:
        w.writerow([r["rulingNumber"], r["rulingDate"], r["true_code"]])
print(f"wrote data/probe_ids.csv ({len(sample)} rulings, seed {SEED})")
