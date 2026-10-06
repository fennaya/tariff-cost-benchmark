"""
Local progress check for the daily Gemini run. Standard library only; calls no API.
Prints: cached responses out of the 200-ruling subset, days left at 20 per day, the last
5 lines of logs/gemini_daily.log, and the scheduled task's next run time (via schtasks).
"""
import csv
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBSET = ROOT / "data" / "gemini_subset.csv"
CACHE = ROOT / "llm_logs" / "gemini-3.8-flash"
LOG = ROOT / "logs" / "gemini_daily.log"
TASK = "GeminiTariffDailyRun"
PER_DAY = 20


def main():
    with SUBSET.open(encoding="utf-8") as f:
        subset = {row["rulingNumber"] for row in csv.DictReader(f)}
    cached = sum(1 for fp in CACHE.glob("*.json") if fp.stem in subset) if CACHE.exists() else 0
    left = len(subset) - cached
    print(f"Cached Gemini responses: {cached} / {len(subset)}")
    print(f"Days left at {PER_DAY}/day: {math.ceil(left / PER_DAY) if left > 0 else 0}")

    print("\nLast 5 lines of logs/gemini_daily.log:")
    if LOG.exists():
        lines = [l.rstrip("\n") for l in LOG.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
        for line in lines[-5:]:
            print(f"  {line}")
    else:
        print("  (log not found)")

    print("\nScheduled task next run:")
    try:
        out = subprocess.run(["schtasks", "/query", "/tn", TASK, "/fo", "LIST"],
                             capture_output=True, text=True, encoding="oem", errors="replace", timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"  schtasks unavailable: {e}")
        return
    if out.returncode != 0:
        print(f"  task '{TASK}' not found")
        return
    for line in out.stdout.splitlines():
        low = line.lower()
        if "next run" in low or "prochaine" in low:
            print(f"  {line.strip()}")
            break
    else:
        print("  (next run time not found in schtasks output)")


if __name__ == "__main__":
    main()
