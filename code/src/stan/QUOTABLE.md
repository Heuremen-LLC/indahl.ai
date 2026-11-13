# Which statuses a quote from an abstract can show (frozen 12 Nov 2026, before any v2 label is read)

Written after STAN v1 and after the spot check were read, so this list is post hoc to v1. It is derived from the
Faults and Guards text (the Test and the PRESENT/ABSENT lines of each code, as in scripts/common.py code_block), by one rule
fixed here before applying it:

A status is quotable from an abstract when its Test can be completed from a sentence in the title or abstract alone. It is not
quotable when completing it needs any of: (a) a released file, table, figure or caption, (b) a recomputation or a new run,
(c) a statement about every item in the whole paper (a universal, which an abstract cannot cover).

| Code | PRESENT | ABSENT | Why |
|---|---|---|---|
| F1 Self-built reference | quotable | quotable | both turn on how the reference is described, which a sentence can state |
| F2 Selected result | quotable | quotable | "up to", "best case", "projected" or "mean over N runs" are statements in the text |
| F3 Reading without a width | quotable | not quotable | PRESENT needs one bare yes/no reading; ABSENT needs every reading in the paper (c) |
| F4 Reading not released | not quotable | not quotable | both need the paper and its files (a, c) |
| F5 Number recomputes differently | not quotable | not quotable | needs a recomputation (b) |
| F6 Text differs from own table | not quotable | not quotable | needs the table, figure or file (a) |
| F7 Classical comparison available | not quotable | not quotable | needs a classical run on the same instances (b) |

Use in v2: a teacher PRESENT/ABSENT on a non-quotable cell is not silver; the row goes to CANNOT_TELL only if the teachers chose
CANNOT_TELL themselves, otherwise it leaves the training set. STAN v2 is scored per code, and the non-quotable cells are reported
as out of scope for an abstract, never as a model result.

Note for the standard (Sage break 2): absence calls (F3 ABSENT, F4 ABSENT, F5 and F6 ABSENT) need a stated scope of search.
2.0 does not require the reader to say what was searched. Raise for 2.1.
