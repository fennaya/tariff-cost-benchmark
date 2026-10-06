"""
Extracts the set of HTS code strings (4/6/8/10 digits, digits only) that appear in an
archived USITC HTS release PDF ("finalCopy"). Archived releases are only published as
PDF (the site's JSON export always returns the CURRENT schedule), so this is the only
free way to test whether a code existed in an earlier revision.

Method: word-level extraction. 8-digit codes look like 1234.56.78 in the heading column;
the 2-digit statistical suffix sits in the "Stat. Suffix" column below its 8-digit parent
(x position taken from each page's own "Stat." header word). 10-digit = parent + suffix.
Accuracy is validated against the current-schedule JSON in validate_pdf_parser.py.
"""
import re

import pymupdf

CODE8 = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
CODE6 = re.compile(r"^\d{4}\.\d{2}$")
CODE4 = re.compile(r"^\d{4}$")
SUF = re.compile(r"^\d{2}$")


def extract_codes(pdf_bytes):
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    codes = set()
    parent8 = None
    for page in doc:
        words = page.get_text("words")
        stat = [w for w in words if w[4] == "Stat."]
        if not stat:
            continue  # notes/cover pages
        sx0, sx1 = stat[0][0], stat[0][2]
        head = [w for w in words if w[4] == "Heading/"]
        hx0 = head[0][0] if head else 0
        # left margin region of the heading column: x within 40 pts of the header
        words.sort(key=lambda w: (round(w[1], 0), w[0]))
        for w in words:
            t = w[4]
            if CODE8.match(t) and abs(w[0] - hx0) < 60:
                parent8 = t.replace(".", "")
                codes.add(parent8)
                codes.add(parent8[:6])
                codes.add(parent8[:4])
            elif CODE6.match(t) and abs(w[0] - hx0) < 60:
                codes.add(t.replace(".", ""))
                codes.add(t.replace(".", "")[:4])
            elif CODE4.match(t) and abs(w[0] - hx0) < 60:
                codes.add(t)
            elif SUF.match(t) and parent8 and sx0 - 12 <= w[0] <= sx1 + 22:
                codes.add(parent8 + t)
    return codes


def clean_rate_text(text):
    """Drops footnote markers such as '1/' or '4/5/' that the PDF prints beside a rate."""
    if text is None:
        return None
    return " ".join(t for t in text.split() if not re.fullmatch(r"(?:\d+/)+", t))


def extract_rates(pdf_source):
    """{digits(4/6/8): General (column 1) rate text} from an archived release PDF. The
    rate text is the words in the General column (between the 'General' and 'Special'
    headers, minus a small left margin) that sit between a code's own row and the next code's
    row. Validated against the current-schedule JSON in review/revision_rates.md."""
    doc = pymupdf.open(pdf_source) if isinstance(pdf_source, str) else pymupdf.open(stream=pdf_source, filetype="pdf")
    rates = {}
    for page in doc:
        words = page.get_text("words")
        gen = [w for w in words if w[4] == "General"]
        spe = [w for w in words if w[4] == "Special"]
        head = [w for w in words if w[4] == "Heading/"]
        if not (gen and spe and head):
            continue
        gx0, sx0, hx0 = gen[0][0], spe[0][0], head[0][0]
        lo, hi = gx0 - 25, sx0 - 27
        codes = sorted(
            [(w[1], w[4].replace(".", "")) for w in words
             if abs(w[0] - hx0) < 60 and (CODE8.match(w[4]) or CODE6.match(w[4]))],
            key=lambda c: c[0])
        if not codes:
            continue
        cells = [w for w in words if lo <= w[0] < hi and w[1] > gen[0][3] + 2]
        for i, (y, code) in enumerate(codes):
            y_end = codes[i + 1][0] if i + 1 < len(codes) else 1e9
            toks = sorted((w for w in cells if y - 6 <= w[1] < y_end - 6), key=lambda w: (round(w[1]), w[0]))
            text = " ".join(t[4] for t in toks).strip()
            if text and code not in rates:
                rates[code] = text
    return rates
