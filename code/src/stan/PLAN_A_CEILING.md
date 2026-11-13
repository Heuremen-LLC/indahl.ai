# STAN A retrieval ceiling, pre-registered 12 Nov 2026 (Sage break 1 on PLAN_A). Written before any retrieval runs.

Question: per code, on gold dev papers with full text (data/fulltext_coverage.json, split dev, FETCHED, at least 2,000 characters),
for each recount-flagged (paper, code) pair, does the evidence the recount used appear in the top 6 BM25 chunks retrieved for that
code under PLAN_A's frozen settings (pypdf 6.21.1 text, 1,200-token Qwen3 chunks, 150 overlap, query = the code's Test, PRESENT and
ABSENT lines from scripts/common.py code_block, no cue lists yet)?

Evidence: the recount note for the pair (the same note text the abstract ceiling used, ceiling/judgments.jsonl note_used, or the
List entry it came from). A pair counts as IN when the retrieved chunks contain the specific figure, table, caption, run date or
sentence the note names; OUT when the full text contains it and the top 6 do not; NOT_IN_TEXT when the extracted full text does
not contain it at all (extraction or files outside the PDF); CANNOT_TELL when the note does not name anything findable.

Two readers: a blind pass with its prompt saved to ceiling_ft/judge_prompt.txt, and Bones on a seeded 20 (seed derived from this
file's sha256, first 8 hex digits as an integer). Disagreements reported.

Pass line per code, fixed now: IN / (IN + OUT) at least 0.60, with the Wilson 95 percent lower bound reported beside it. A code below
the line is reported as retrieval-limited and BM25 is not swapped out for that reading. NOT_IN_TEXT is reported per code as the
extraction ceiling. Codes with fewer than 10 decided pairs are reported as untested.
