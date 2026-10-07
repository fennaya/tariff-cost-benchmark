"""
figures/error_breakdown.png: one stacked bar per model, share of all 1,098 answers by
class. Reads review/invalid_breakdown.json (written by analyze_invalid_codes.py); no
numbers are computed or typed here. Palette: the validated reference categorical order
(slots 1-7), light surface; text stays in ink colors, not series colors.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "review" / "invalid_breakdown.json").read_text(encoding="utf-8"))
ORDER = list(data)
from datetime import date
UNKNOWN = set()
for _m in json.loads((ROOT / "config.json").read_text(encoding="utf-8"))["models"]:
    try:
        date.fromisoformat(_m.get("training_cutoff", "unknown"))
    except ValueError:
        UNKNOWN.add(_m["model_id"])
SERIES = [  # key, label, color (reference categorical slots 1-7, in order)
    ("correct", "Correct", "#2a78d6"),
    ("wrong_valid", "Wrong, valid code", "#eb6834"),
    ("suffix_only", "Invalid: suffix only", "#1baf7a"),
    ("six_eight", "Invalid: first 6 ok, first 8 not", "#eda100"),
    ("fabricated", "Invalid: fabricated", "#e87ba4"),
    ("outdated", "Invalid: outdated", "#008300"),
    ("no_usable_code", "Invalid: no usable code", "#4a3aa7"),
]
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"

fig, ax = plt.subplots(figsize=(11, 1.9 + 0.72 * len(ORDER)), dpi=200, facecolor=SURFACE)
ax.set_facecolor(SURFACE)
for i, m in enumerate(ORDER):
    n = data[m]["n"]
    left = 0.0
    for key, label, color in SERIES:
        v = data[m]["classes"][key] / n * 100
        if v > 0:
            ax.barh(i, v, left=left, height=0.55, color=color, edgecolor=SURFACE, linewidth=2,
                    label=label if i == 0 else None)
            if v >= 4:
                ax.text(left + v / 2, i, f"{v:.1f}%", ha="center", va="center", fontsize=9, color=INK)
            left += v
ax.set_yticks(range(len(ORDER)))
ax.set_yticklabels([f"{m}{' †' if m in UNKNOWN else ''}\n(n = {data[m]['n']:,})" for m in ORDER], fontsize=9, color=INK)
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("Share of all answers (%)", fontsize=10, color=MUTED)
ax.tick_params(axis="x", colors=MUTED, labelsize=9)
ax.tick_params(axis="y", length=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d9d8d2")
ax.set_title("What each model returned, by error type", loc="left", fontsize=12, color=INK, pad=14)
from matplotlib.patches import Patch
handles = [Patch(facecolor=c, edgecolor=SURFACE, label=l) for _, l, c in SERIES]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False, fontsize=9,
          labelcolor=INK, handlelength=1.2, columnspacing=1.4)
fig.tight_layout()
fig.text(0.01, 0.005, "† contamination not ruled out (no stated cutoff); treat accuracy as an upper bound.", fontsize=8, color=MUTED)
out = ROOT / "figures" / "error_breakdown.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, facecolor=SURFACE)
print(f"Wrote {out}")
