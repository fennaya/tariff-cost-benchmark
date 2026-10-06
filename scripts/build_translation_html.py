"""
Round 2, Part 3: build review/translation_review.html, a single self-contained offline
page for marking the 100 translated rows (no server, no internet -- just open the file).
Embeds the CSV data as inline JSON so the page needs nothing else.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "review" / "translation_review.csv"
OUT_PATH = ROOT / "review" / "translation_review.html"

with CSV_PATH.open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

data = [{"id": r["id"], "en": r["english"], "fr": r["french"], "ar": r["arabic"]} for r in rows]
data_json = json.dumps(data, ensure_ascii=False)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Translation review</title>
<style>
  :root {
    --bg: #f7f7f8; --card-bg: #ffffff; --text: #1a1a1a; --muted: #666;
    --border: #ddd; --ok: #1f9d55; --ok-bg: #e6f7ec; --fix: #d9534f; --fix-bg: #fdecea;
    --accent: #2563eb;
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background: var(--bg); color: var(--text); margin: 0; padding: 16px;
  }
  .wrap { max-width: 1100px; margin: 0 auto; }
  h1 { font-size: 20px; margin: 0 0 8px; }
  .rule-box {
    background: #fff8e1; border: 1px solid #f0d882; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 16px; font-size: 14px; line-height: 1.5;
  }
  .rule-box b { color: #8a6d00; }
  .toolbar {
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; margin-bottom: 12px; flex-wrap: wrap;
  }
  .toolbar .left { display: flex; align-items: center; gap: 10px; }
  .counter { font-weight: 600; }
  .progress-bar { width: 200px; height: 8px; background: #e2e2e2; border-radius: 4px; overflow: hidden; }
  .progress-fill { height: 100%; background: var(--accent); width: 0%; transition: width .2s; }
  button {
    font: inherit; cursor: pointer; border: 1px solid var(--border); background: #fff;
    border-radius: 6px; padding: 8px 14px;
  }
  button:hover { background: #f0f0f0; }
  button.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
  button.primary:hover { background: #1d4ed8; }
  .card {
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px;
    padding: 18px; margin-bottom: 16px;
  }
  .card-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
  .card-id { font-weight: 700; font-size: 15px; }
  .card-nav-hint { color: var(--muted); font-size: 12px; }
  .cols { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
  @media (max-width: 900px) { .cols { grid-template-columns: 1fr; } }
  .col { border: 1px solid var(--border); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; }
  .col h3 { margin: 0 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
  .col .text { flex: 1; font-size: 14px; line-height: 1.5; white-space: pre-wrap; margin-bottom: 10px; }
  .col[dir="rtl"] .text { text-align: right; }
  .mark-row { display: flex; gap: 8px; }
  .mark-btn { flex: 1; padding: 8px; border-radius: 6px; font-size: 13px; }
  .mark-btn.ok-selected { background: var(--ok-bg); border-color: var(--ok); color: var(--ok); font-weight: 600; }
  .mark-btn.fix-selected { background: var(--fix-bg); border-color: var(--fix); color: var(--fix); font-weight: 600; }
  textarea.note {
    width: 100%; margin-top: 8px; font: inherit; font-size: 13px; border: 1px solid var(--border);
    border-radius: 6px; padding: 6px; resize: vertical; min-height: 40px; display: none;
  }
  textarea.note.visible { display: block; }
  .shortcuts { color: var(--muted); font-size: 12px; margin-top: 4px; }
  kbd {
    background: #eee; border: 1px solid #ccc; border-radius: 3px; padding: 1px 5px;
    font-family: monospace; font-size: 11px;
  }
  .nav-row { display: flex; justify-content: space-between; margin-top: 10px; }
  .jump-row { display: flex; gap: 8px; align-items: center; }
  .export-note { color: var(--muted); font-size: 12px; margin-top: 4px; }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #15171a; --card-bg: #1e2126; --text: #e8e8e8; --muted: #9aa0a6;
      --border: #30343a; --ok-bg: #0f3321; --fix-bg: #3a1a18;
    }
    .rule-box { background: #332b0a; border-color: #5c4b0f; }
    .rule-box b { color: #e0c34a; }
    button { background: #22262c; color: var(--text); }
    button:hover { background: #2a2f36; }
    kbd { background: #2a2f36; border-color: #444; color: #ddd; }
    .progress-bar { background: #30343a; }
  }
</style>
</head>
<body>
<div class="wrap">
  <h1>Translation review -- 100 rulings, English / French / Modern Standard Arabic</h1>
  <div class="rule-box">
    <b>Grading rule:</b> mark <b>OK</b> if the translation keeps every product fact
    (material, function, composition, dimensions, use) and reads like something a real
    importer would write. Mark <b>Fix</b> if any fact is lost, changed, or invented.
    Style doesn't matter -- only facts.
  </div>

  <div class="toolbar">
    <div class="left">
      <span class="counter" id="counter">Card 1 of 100</span>
      <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
      <span id="markedCount" style="color:var(--muted); font-size:13px;"></span>
    </div>
    <div class="jump-row">
      <button id="jumpUnmarked">Jump to next unmarked</button>
      <button id="exportBtn" class="primary">Export marked CSV</button>
    </div>
  </div>

  <div class="card" id="card">
    <div class="card-head">
      <span class="card-id" id="cardId"></span>
      <span class="card-nav-hint">Use arrow keys or the buttons below to navigate</span>
    </div>
    <div class="cols">
      <div class="col" dir="ltr">
        <h3>English</h3>
        <div class="text" id="enText"></div>
      </div>
      <div class="col" dir="ltr">
        <h3>French</h3>
        <div class="text" id="frText"></div>
        <div class="mark-row">
          <button class="mark-btn" id="frOkBtn">OK (F)</button>
          <button class="mark-btn" id="frFixBtn">Fix (G)</button>
        </div>
        <textarea class="note" id="frNote" placeholder="What's wrong? (optional)"></textarea>
      </div>
      <div class="col" dir="rtl">
        <h3 dir="ltr" style="text-align:left">Arabic</h3>
        <div class="text" id="arText"></div>
        <div class="mark-row" dir="ltr">
          <button class="mark-btn" id="arOkBtn">OK (A)</button>
          <button class="mark-btn" id="arFixBtn">Fix (S)</button>
        </div>
        <textarea class="note" id="arNote" dir="rtl" placeholder="ما المشكلة؟ (اختياري)"></textarea>
      </div>
    </div>
    <div class="nav-row">
      <button id="prevBtn">&larr; Previous</button>
      <button id="nextBtn">Next &rarr;</button>
    </div>
  </div>

  <div class="shortcuts">
    Keyboard shortcuts: <kbd>F</kbd> French OK &nbsp; <kbd>G</kbd> French Fix &nbsp;
    <kbd>A</kbd> Arabic OK &nbsp; <kbd>S</kbd> Arabic Fix &nbsp;
    <kbd>&larr;</kbd>/<kbd>&rarr;</kbd> move between cards.
    Shortcuts are disabled while typing in a note box.
  </div>
  <div class="export-note">
    Progress is saved automatically in this browser (localStorage) -- closing the tab
    loses nothing. Click "Export marked CSV" when done with all 100 and save the
    downloaded file as <code>review/translation_review_marked.csv</code>.
  </div>
</div>

<script>
const DATA = __DATA_JSON__;
const STORAGE_KEY = "tariff_translation_review_v1";

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return { index: 0, marks: {} };
}
function saveState() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
}

let state = loadState();
if (!state.marks) state.marks = {};
if (typeof state.index !== "number" || state.index < 0 || state.index >= DATA.length) state.index = 0;

const els = {
  counter: document.getElementById("counter"),
  progressFill: document.getElementById("progressFill"),
  markedCount: document.getElementById("markedCount"),
  cardId: document.getElementById("cardId"),
  enText: document.getElementById("enText"),
  frText: document.getElementById("frText"),
  arText: document.getElementById("arText"),
  frOkBtn: document.getElementById("frOkBtn"),
  frFixBtn: document.getElementById("frFixBtn"),
  arOkBtn: document.getElementById("arOkBtn"),
  arFixBtn: document.getElementById("arFixBtn"),
  frNote: document.getElementById("frNote"),
  arNote: document.getElementById("arNote"),
  prevBtn: document.getElementById("prevBtn"),
  nextBtn: document.getElementById("nextBtn"),
  jumpUnmarked: document.getElementById("jumpUnmarked"),
  exportBtn: document.getElementById("exportBtn"),
};

function getMark(id) {
  if (!state.marks[id]) state.marks[id] = { fr_ok: "", ar_ok: "", fr_note: "", ar_note: "" };
  return state.marks[id];
}

function render() {
  const row = DATA[state.index];
  const mark = getMark(row.id);
  els.counter.textContent = `Card ${state.index + 1} of ${DATA.length}`;
  els.progressFill.style.width = `${((state.index + 1) / DATA.length) * 100}%`;
  const markedTotal = Object.values(state.marks).filter(m => m.fr_ok && m.ar_ok).length;
  els.markedCount.textContent = `${markedTotal}/${DATA.length} fully marked`;
  els.cardId.textContent = row.id;
  els.enText.textContent = row.en;
  els.frText.textContent = row.fr;
  els.arText.textContent = row.ar;

  els.frOkBtn.className = "mark-btn" + (mark.fr_ok === "OK" ? " ok-selected" : "");
  els.frFixBtn.className = "mark-btn" + (mark.fr_ok === "Fix" ? " fix-selected" : "");
  els.arOkBtn.className = "mark-btn" + (mark.ar_ok === "OK" ? " ok-selected" : "");
  els.arFixBtn.className = "mark-btn" + (mark.ar_ok === "Fix" ? " fix-selected" : "");

  els.frNote.value = mark.fr_note || "";
  els.arNote.value = mark.ar_note || "";
  els.frNote.classList.toggle("visible", mark.fr_ok === "Fix");
  els.arNote.classList.toggle("visible", mark.ar_ok === "Fix");

  els.prevBtn.disabled = state.index === 0;
  els.nextBtn.disabled = state.index === DATA.length - 1;
}

function setMark(lang, value) {
  const row = DATA[state.index];
  const mark = getMark(row.id);
  mark[lang + "_ok"] = value;
  saveState();
  render();
  if (lang === "fr" && value === "Fix") els.frNote.focus();
  if (lang === "ar" && value === "Fix") els.arNote.focus();
}

function goTo(index) {
  if (index < 0 || index >= DATA.length) return;
  state.index = index;
  saveState();
  render();
}

function jumpToNextUnmarked() {
  for (let i = 0; i < DATA.length; i++) {
    const idx = (state.index + 1 + i) % DATA.length;
    const m = state.marks[DATA[idx].id];
    if (!m || !m.fr_ok || !m.ar_ok) { goTo(idx); return; }
  }
  alert("All 100 rows are fully marked!");
}

function exportCsv() {
  const header = ["id", "fr_ok", "ar_ok", "fr_note", "ar_note"];
  const lines = [header.join(",")];
  const esc = (s) => '"' + String(s || "").replace(/"/g, '""') + '"';
  for (const row of DATA) {
    const m = getMark(row.id);
    lines.push([esc(row.id), esc(m.fr_ok), esc(m.ar_ok), esc(m.fr_note), esc(m.ar_note)].join(","));
  }
  const blob = new Blob(["\\ufeff" + lines.join("\\r\\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "translation_review_marked.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

els.frOkBtn.addEventListener("click", () => setMark("fr", "OK"));
els.frFixBtn.addEventListener("click", () => setMark("fr", "Fix"));
els.arOkBtn.addEventListener("click", () => setMark("ar", "OK"));
els.arFixBtn.addEventListener("click", () => setMark("ar", "Fix"));
els.frNote.addEventListener("input", () => { getMark(DATA[state.index].id).fr_note = els.frNote.value; saveState(); });
els.arNote.addEventListener("input", () => { getMark(DATA[state.index].id).ar_note = els.arNote.value; saveState(); });
els.prevBtn.addEventListener("click", () => goTo(state.index - 1));
els.nextBtn.addEventListener("click", () => goTo(state.index + 1));
els.jumpUnmarked.addEventListener("click", jumpToNextUnmarked);
els.exportBtn.addEventListener("click", exportCsv);

document.addEventListener("keydown", (e) => {
  const tag = (document.activeElement && document.activeElement.tagName) || "";
  if (tag === "TEXTAREA" || tag === "INPUT") {
    if (e.key === "Escape") document.activeElement.blur();
    return;
  }
  switch (e.key.toLowerCase()) {
    case "f": setMark("fr", "OK"); break;
    case "g": setMark("fr", "Fix"); break;
    case "a": setMark("ar", "OK"); break;
    case "s": setMark("ar", "Fix"); break;
    case "arrowleft": goTo(state.index - 1); break;
    case "arrowright": goTo(state.index + 1); break;
  }
});

render();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
OUT_PATH.write_text(html, encoding="utf-8")
print(f"Wrote {OUT_PATH} ({len(html):,} bytes, {len(data)} rows)")
