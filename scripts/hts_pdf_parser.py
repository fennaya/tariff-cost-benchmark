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
