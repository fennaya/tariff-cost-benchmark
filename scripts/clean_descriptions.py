"""
Phase 2: build the model input WITHOUT leaking the answer.

The raw ruling text contains the classification discussion and the answer itself. An
importer describing their product to a model would only know the merchandise
description, not CBP's legal reasoning. This script extracts just that description and
runs an automated leak test on the result.

Approach:
  1. Normalize whitespace. Find the "Dear ...:" greeting by regex on the raw string (not
     by naive sentence-splitting -- "Dear Ms. Yang:" contains an abbreviation period that
     breaks period-based sentence tokenizers and was observed, on manual review of the
     first pass, to make the start-anchor latch onto header/address text instead of the
     actual description).
  2. After the greeting, find the first occurrence of a strong marker phrase that CBP
     rulings use to open the merchandise description ("the merchandise under
     consideration is", "the subject merchandise is", etc.). Start there. If no marker
     phrase is found, fall back to the first non-boilerplate sentence after the greeting.
  3. From that start point, split the remaining text into sentences and keep them until
     hitting one that trips a cut trigger: an HTS-code-shaped pattern, classification/
     tariff/duty language, an Explanatory Notes or GRI reference, or a citation to another
     ruling or court case. This trigger set is deliberately broader than Gate 2's own
     pass/fail definition (see below) because a narrower cut left in legal case citations
     and cross-references on manual review of the first pass.
  4. Gate 2's reported pass/fail number uses exactly the pattern given in the build
     prompt -- `\\d{4}\\.\\d{2}` or the literal words heading/subheading/HTSUS/tariff --
     kept as a separate, narrower check (OFFICIAL_LEAK_RE) so the reported gate number
     matches the spec exactly regardless of the broader cut logic above.

Every ruling that fails (empty result, or fails the official leak test) is counted and
listed, not silently skipped -- Gate 2 needs the real failure count.
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULINGS_DIR = ROOT / "data" / "raw" / "rulings"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REVIEW_DIR = ROOT / "review"
REVIEW_DIR.mkdir(parents=True, exist_ok=True)

# Exactly the pattern specified in the build prompt for Gate 2.
OFFICIAL_LEAK_RE = re.compile(
    r"\d{4}\.\d{2}|heading|subheading|htsus|tariff", re.IGNORECASE
)

# Broader trigger set used to decide WHERE to cut (see module docstring).
HTS_CODE_RE = re.compile(r"\d{4}\.\d{2}")
RULING_REF_RE = re.compile(r"\b(?:NY|HQ)\s?[A-Z]?\d{5,6}\b", re.IGNORECASE)
CASE_CITATION_RE = re.compile(r"\bv\.\s+United States\b|\bF\.\s?(?:2d|3d|Supp)\b|\bC\.I\.T\.\b|\bC\.C\.P\.A\.\b")

CUT_KEYWORDS = [
    "heading", "subheading", "chapter", "htsus", "classif", "tariff",
    "explanatory note", "gri ", "general rule of interpretation",
    "note to chapter", "note to the tariff", "provides for", "duty rate",
    "duty will be", "rate of duty", "u.s. note", "see, e.g.",
    "ct. int'l trade", "court of international trade",
]
# NOTE: "ruling request" and "ruling letter" were previously in this list to catch
# references to OTHER rulings, but manual review (2026-09-28, see DECISIONS.md) found
# they are near-universal boilerplate referring to the CURRENT submission ("samples were
# submitted with your ruling request") and were truncating good, non-leaky descriptive
# content immediately after the opening sentence in ~44+ cases. Genuine cross-references
# to other rulings are still caught by RULING_REF_RE (NY/HQ + number) below.

STRONG_START_PATTERNS = [
    r"the merchandise under consideration",
    r"the subject merchandise",
    r"the product(?:s)? under consideration",
    r"the item(?:s)? under consideration",
    r"the article(?:s)? under consideration",
    r"the subject article",
    r"the instant merchandise",
    r"the merchandise concerned",
    r"the merchandise at issue",
    r"the subject product",
]
STRONG_START_RE = re.compile("|".join(STRONG_START_PATTERNS), re.IGNORECASE)

GREETING_RE = re.compile(r"Dear\s+[^:]{1,60}:")

# Some rulings use explicit section headers (FACTS: / ISSUES: / CLASSIFICATION: / ...)
# instead of a narrative flow. When present, "FACTS:" is a highly reliable anchor for
# where the actual product description starts -- more reliable than STRONG_START_RE,
# which was observed (2026-09-28, see DECISIONS.md) to sometimes latch onto a later,
# unrelated occurrence of a marker phrase inside the ISSUES/legal-analysis section of
# these structured rulings, skipping over the real description entirely.
FACTS_HEADER_RE = re.compile(r"\bFACTS:\s*")

BOILERPLATE_START_KEYWORDS = [
    "you requested", "letter dated", "ruling on behalf", "in your letter",
    "in your submission", "your request",
]

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WHITESPACE_RE = re.compile(r"\s+")


def contains_cut_trigger(sentence: str) -> bool:
    s = sentence.lower()
    if HTS_CODE_RE.search(sentence):
        return True
    if RULING_REF_RE.search(sentence):
        return True
    if CASE_CITATION_RE.search(sentence):
        return True
    return any(kw in s for kw in CUT_KEYWORDS)


def is_boilerplate_start(sentence: str) -> bool:
    s = sentence.lower()
    return any(kw in s for kw in BOILERPLATE_START_KEYWORDS)


def find_fallback_start(text: str, search_from: int):
    """First non-boilerplate, non-leaky sentence after `search_from`, tokenized only
    over the post-greeting text so header abbreviations can't misalign indices. Returns
    a char offset into `text`, or None if no such sentence exists."""
    tail = text[search_from:]
    sentences = SENTENCE_SPLIT_RE.split(tail)
    offset = search_from
    for s in sentences:
        s_stripped = s.strip()
        if s_stripped and not contains_cut_trigger(s) and not is_boilerplate_start(s) and len(s_stripped) >= 15:
            return text.index(s_stripped, offset)
        offset += len(s) + 1
    return None


def clean_one(raw_text: str):
    text = WHITESPACE_RE.sub(" ", raw_text).strip()

    greet_match = GREETING_RE.search(text)
    search_from = greet_match.end() if greet_match else 0

    # Three candidate anchors for where the real description starts: an explicit
    # "FACTS:" header, a known marker phrase ("the merchandise under consideration is",
    # etc.), or the first plain non-boilerplate sentence. Any of these can occur first
    # depending on how a given ruling is drafted -- taking whichever is EARLIEST in the
    # text (not a fixed priority order) matters because a marker phrase can also appear
    # much later, inside the ISSUES/legal-analysis section restating the question (e.g.
    # "What is the classification of the subject merchandise?"), which would otherwise
    # win by fixed priority and skip over a good, earlier plain-sentence description
    # entirely (found via manual review 2026-09-28, see DECISIONS.md).
    facts_match = FACTS_HEADER_RE.search(text, search_from)
    strong_match = STRONG_START_RE.search(text, search_from)
    fallback_start = find_fallback_start(text, search_from)

    candidates = [c for c in (
        facts_match.end() if facts_match else None,
        strong_match.start() if strong_match else None,
        fallback_start,
    ) if c is not None]
    if not candidates:
        return None, "no_description_start_found"
    start_char = min(candidates)

    tail_sentences = SENTENCE_SPLIT_RE.split(text[start_char:])
    kept = []
    for s in tail_sentences:
        if contains_cut_trigger(s):
            break
        kept.append(s.strip())

    cleaned = " ".join(s for s in kept if s).strip()
    if not cleaned:
        return None, "empty_after_cleaning"
    if OFFICIAL_LEAK_RE.search(cleaned):
        return None, "failed_official_leak_test"
    return cleaned, None


def main():
    files = sorted(RULINGS_DIR.glob("*.json"))
    results = []
    failures = {}
    for fp in files:
        data = json.loads(fp.read_text(encoding="utf-8"))
        raw_text = data.get("text", "")
        cleaned, fail_reason = clean_one(raw_text)
        row = {
            "rulingNumber": data.get("rulingNumber"),
            "rulingDate": data.get("rulingDate"),
            "tariffs": data.get("tariffs"),
            "subject": data.get("subject"),
            "cleaned_description": cleaned,
            "failure_reason": fail_reason,
        }
        results.append(row)
        if fail_reason:
            failures[fail_reason] = failures.get(fail_reason, 0) + 1

    ok = [r for r in results if r["cleaned_description"]]
    print(f"Total rulings processed: {len(results)}")
    print(f"Clean, non-empty descriptions: {len(ok)} ({100 * len(ok) / len(results):.1f}%)")
    print("Failure breakdown:")
    for reason, count in sorted(failures.items(), key=lambda kv: -kv[1]):
        print(f"  {reason}: {count}")

    out_path = OUT_DIR / "cleaned_descriptions.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {out_path}")

    sample_pool = [r for r in results if r["cleaned_description"]]
    random.seed(42)
    sample = random.sample(sample_pool, min(20, len(sample_pool)))
    lines = ["# Leak sample review\n", "20 random cleaned inputs next to their original ruling text.\n"]
    orig_by_num = {}
    for fp in files:
        data = json.loads(fp.read_text(encoding="utf-8"))
        orig_by_num[data.get("rulingNumber")] = data.get("text", "")
    for r in sample:
        lines.append(f"\n## {r['rulingNumber']} ({r['rulingDate']})\n")
        lines.append(f"**True tariffs:** {r['tariffs']}\n")
        lines.append(f"\n**Cleaned description:**\n\n> {r['cleaned_description']}\n")
        orig = orig_by_num.get(r["rulingNumber"], "")
        lines.append(f"\n<details><summary>Original text</summary>\n\n```\n{orig}\n```\n</details>\n")
    (REVIEW_DIR / "leak_sample.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REVIEW_DIR / 'leak_sample.md'}")


if __name__ == "__main__":
    main()
