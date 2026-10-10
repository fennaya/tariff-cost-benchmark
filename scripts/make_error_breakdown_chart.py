"""
Error-breakdown figures: one stacked bar per model, share of that model's answers by class.
Reads review/same_sample.json (written by analyze_same_sample.py); no numbers are computed or typed here.

  figures/error_breakdown.png      primary: all 11 models on the same 228 rulings dated July 1 to August 14, 2026
  figures/error_breakdown_all.png  upper bound: all 11 models on the same 1,098 rulings (may include rulings in training data)

Palette: the validated reference categorical order (slots 1-7), light surface; text stays in ink colors, not series colors.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "review" / "same_sample.json").read_text(encoding="utf-8"))
ORDER = data["ranking_8digit_228"]
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


def draw(key, title, footnote, out):
    fig, ax = plt.subplots(figsize=(11, 1.9 + 0.72 * len(ORDER)), dpi=200, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, m in enumerate(ORDER):
        c = data["models"][m][key]
        n = c["n"]
        left = 0.0
        for k, label, color in SERIES:
            v = c["classes"][k] / n * 100
            if v > 0:
                ax.barh(i, v, left=left, height=0.55, color=color, edgecolor=SURFACE, linewidth=2)
                if v >= 4:
                    ax.text(left + v / 2, i, f"{v:.1f}%", ha="center", va="center", fontsize=9, color=INK)
                left += v
    ax.set_yticks(range(len(ORDER)))
    ax.set_yticklabels([f"{m}{' †' if data['models'][m]['dagger'] else ''}\n(n = {data['models'][m][key]['n']:,})" for m in ORDER], fontsize=9, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of answers (%)", fontsize=10, color=MUTED)
    ax.tick_params(axis="x", colors=MUTED, labelsize=9)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#d9d8d2")
    ax.set_title(title, loc="left", fontsize=12, color=INK, pad=14)
    handles = [Patch(facecolor=c, edgecolor=SURFACE, label=l) for _, l, c in SERIES]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False, fontsize=9,
              labelcolor=INK, handlelength=1.2, columnspacing=1.4)
    fig.tight_layout()
    fig.text(0.01, 0.005, footnote, fontsize=8, color=MUTED)
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
    print(f"Wrote {out}")


draw("p228", "What each model returned, by error type (same 228 rulings, July 1 to August 14, 2026)",
     "† no stated cutoff: July-August is the best available window, not a guarantee.",
     ROOT / "figures" / "error_breakdown.png")
draw("p1098", "What each model returned, by error type (same 1,098 rulings; upper bound: may include rulings in training data)",
     "† contamination not ruled out (no stated cutoff). Upper bound: includes rulings that may be in training data.",
     ROOT / "figures" / "error_breakdown_all.png")
