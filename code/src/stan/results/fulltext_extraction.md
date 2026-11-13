# Full-text extraction report for Sage break 7 (Bones, 12 Nov 2026)

Source: data/fulltext_coverage.json. Extraction is pypdf 6.21.1 with no OCR.

- Usable full text (fetched, at least 2,000 characters): 184 of 197 gold. Dev 92 of 98 (93 fetched, minus 08c4a2608cbe at 254 characters). Test 92 of 99.
- Characters per usable paper: median 60,406, 10th percentile 18,181, minimum 3,206, maximum 321,574.
- Hosts of the usable text: arXiv 154, Zenodo 30.

## The 13 left out

All 13 are non-arXiv. None of the 154 arXiv gold items is missing.

- 11 are Zenodo records with no PDF (code, data or bundle deposits).
- 1 is a Zenodo PDF that extracts to 254 characters (08c4a2608cbe).
- 1 has no identifier (570f6ffd1a09, an IBM documentation tutorial run as written).

That is 13 of the 43 non-arXiv gold items (30 percent) and 0 of the 154 arXiv items. Recount flags on the 13: F5 on 5, F4 on 3, F6 on 2, F2 on 2, F1 and F3 on none, no flag on 5.

So the full-text claim reads "open-access PDF slice only". The slice under-represents independent Zenodo deposits, which is where F4 and F5 flags sit. F4, F5 and F7 are already untested in the ceiling (fewer than 10 decided pairs), and these exclusions are part of the reason.

## Still owed for break 7
- Share of papers with obviously broken text, per code. The fetch-time extract_flag fired on none of the 184, but that flag only checks length. Columns and tables scrambled by pypdf are not measured yet, and F4 and F6 live in tables.
- Version read by the recount against the version fetched. Zenodo concept DOIs drift (results/twins_hand_read.md: 5 gold items). arXiv versions are not yet checked.

## Broken-text measure (PLAN_A_v2 section 7, run 12 Nov ~14:50)
Rows: results/broken_text.json. The 92 dev papers with extracted text were measured. Test text is not extracted and stays untouched.
Thresholds are the arXiv 95th percentiles: short-line share 0.180, odd-character share 0.0125.
- Flagged: 10 of 92. arXiv 7 of 80. Zenodo 3 of 12.
- The two cuts are each set at an arXiv 95th percentile, so about 10 percent of arXiv papers get flagged by construction.
  The reading is the comparison: Zenodo flags at 25 percent against arXiv at 9 percent.
- Flagged papers per code (with text): F1 3 of 24, F2 4 of 35, F3 2 of 22, F4 6 of 63, F5 2 of 15, F6 3 of 29, F7 1 of 8.
- Hand look at the two worst:
  - 6aecacfbca78 (odd-character share 0.11) is box-drawing characters from text-art diagrams in the source. That is the
    source's own formatting, not broken extraction.
  - 1da98d1a5556 (short-line share 0.63) is one word per line. That is real extraction breakage. The quote check normalises
    whitespace, so quotes still match, but BM25 chunk boundaries are unaffected and reading order is intact.
- So the measure flags at least one false positive. This is a screen, not a verdict. F4 and F6 tables are still owed a
  hand read on 10 papers.

## Version check, arXiv (12 Nov ~14:55)
Every arXiv gold link pins a version (for example 2610.21761v1). The fetched PDF URL carries the same version for all 154 arXiv items
(dev 80, test 74), with no case newer or older. Assuming the List link names the version the recount read, arXiv text matches the
recount. Version drift is a Zenodo concept-DOI problem only: 5 items, results/twins_hand_read.md.
