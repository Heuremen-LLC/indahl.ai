# IRIS sweep report, 2026-11-11

Candidates from arXiv: 15841. Skipped (already in SCAN_register or removed at request): 20 ids on skip list.
Screened: 4598.

## Counts by status
- INDEXED: 10
- MATRIX_ONLY_COMPANY: 4
- (of MATRIX_ONLY_COMPANY, vendor-authored: 2)
- rows with outputs_checked = yes: 14
- dropped total: 4493
- needs_review: 91
- rows that would be listed (INDEXED + MATRIX_ONLY_COMPANY): 14

## Dropped by reason
- NOT_LLM_EVAL: 2016
- NO_RELEASE_LINK: 1288
- NOT_ENGLISH: 463
- NO_MODEL_OUTPUT_FILES: 358
- NO_OUTPUT_FILES: 216
- OUTPUTS_NOT_CONFIRMED: 149
- DROPPED_FUNDER: 3

## DROPPED_FUNDER by funder class (a paper can hit several)
- ONR/Navy: 3
- AFOSR: 1
- DARPA: 1

## needs_review by reason
- release links found but none could be listed: 43
- affiliation not classifiable as university or company: 21
- outputs_checked unreadable: 11
- outputs released, funder clear, but no affiliations parsed from HTML: 11
- outputs released but no arXiv HTML full text: 5

## Rules not applied automatically
- Acknowledgments are read only from arXiv HTML (pdftotext is not installed, so there is no PDF fallback). Funding that sits only in a first-page footnote is not seen.
- 'Per-item outputs': accepted files need a model name in the path (or an output word inside a per-model folder); then the first 4 KB of up to 3 jsonl/json/csv files are read for an output-like text field. Parquet is never opened (needs_review). A heuristic key match is not proof the text is model text. Repos linked from full text count only when release language sits within ~200 characters of the link.
- Affiliation class (university / company / vendor) is keyword based. Anything ambiguous goes to needs_review.
- Language is a stop-word heuristic on title and abstract.
- Funder matching is a keyword list over the ack text; a generic mention (for example 'EU') can over-drop and a funder written in an unusual way can slip through. Every row is flagged 'not hand-read'.
