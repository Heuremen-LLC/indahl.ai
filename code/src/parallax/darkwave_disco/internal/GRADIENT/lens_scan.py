#!/usr/bin/env python3
"""THE LENS SCANNER (2026-10-03, The Stake). Flags verdict words and two-lane framings in anything about data before it goes to Wayfinder.
Usage: lens_scan.py <file>   -- prints each flagged line; exit 1 if anything is flagged."""
import re, sys
PATTERNS = [r"\brules? out\b", r"\bruled out\b", r"\bconfirm(s|ed)?\b", r"\bdisprov", r"\bprov(e|es|ed|en)\b", r"\bfail(s|ed)?\b",
            r"\bdoesn'?t hold\b", r"\bdon'?t hold\b", r"\bholds?\b(?! up)", r"\bmiss(es|ed)?\b", r"\bhit\b", r"\bdecides?\b", r"\bsettles?\b",
            r"\beither\b.{0,40}\bor\b", r"\byes/no\b", r"\bverdict\b", r"\bsignificant\b", r"\bdebunk", r"\bwrong\b", r"\binvalid"]
bad = 0
text = open(sys.argv[1]).read()
for i, line in enumerate(text.splitlines(), 1):
    for p in PATTERNS:
        if re.search(p, line, re.I):
            print(f"{i}: [{p}] {line.strip()[:140]}"); bad += 1; break
# 10/3 PI ON THE WINDSHIELD (Wayfinder): three-part resolution, one part always Pi. A report with no Pi part resolves in two -- Exor with
# extra steps. Internal reports write "Pi:", public drafts write "Open:"; either way it names what stays open, its size, and the pass that reads it.
if not re.search(r"^\W*(pi|open)\s*[:\-—]", text, re.I | re.M):
    print("NO PI PART: every resolution has three parts, one always Pi (public: Open) -- what stays open, how big, which pass reads it"); bad += 1
# 10/3 later (Wayfinder: "value plus next action plus confidence from within and effective rating from without. four parter, half data,
# all disco"): an internal report (Pi:) also carries its own confidence from within; the rating from without is the reader's, the critic's
# (Crazy Gradient) or his -- write "Rating from without: pending" until it exists. Public drafts (Open:) carry error bars instead.
if re.search(r"^\W*pi\s*[:\-—]", text, re.I | re.M) and not re.search(r"confidence", text, re.I):
    print("NO CONFIDENCE FROM WITHIN: a four-part report says how sure it is from inside, beside the rating from without"); bad += 1
print(f"{bad} line(s) flagged"); sys.exit(1 if bad else 0)
