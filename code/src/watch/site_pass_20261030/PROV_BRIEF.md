# QIA provenance pass, 30 Oct 2026 (read only, evidence only)

Why: on 25 Oct a retention pass deleted 133 QIA working files (manifest: ~/bones-forge/qia_leads/matrix_page/DELETE_MANIFEST_20261025.json),
including the register and inventories that many published QIA cells cite as their source. The published cells live in
~/bones-forge/qia_leads/matrix_page/book_calibrated.json (fields: published, measured, qia_calibration, how) and on https://indahl.ai/qia.
Wayfinder: "look harder or we pull them". Every number in our measured and qia_calibration cells must trace to something that survives.

Your rows: the JSON file named in your prompt (each row: id, the numbers a script could not find, the kept files that mention the row, and whether
the paper text is cached at ~/bones-forge/qia_leads/recheck_published/src/<id with / replaced by _>.txt).

For EVERY number in the row's measured and qia_calibration cells (not only the listed missing ones; the script's list is a hint), find one of:
- TRACED: the number in a kept file (give path and line). Kept files: ~/bones-forge/qia_runs/, ~/bones-forge/qia_leads/audits/,
  ~/bones-forge/arxiv_one_readout/, ~/bones-forge/public_mirror/indahl.ai/code/qia-runs/, ~/bones-forge/qia_leads/THE_BOOK.md only as a pointer
  (the Book is our own summary, so a number found ONLY in the Book does not count as traced).
- RECOMPUTED: arithmetic on numbers printed in the paper text or a kept file. Show the arithmetic and that it gives the cell's figure as printed.
- RECOUNTED: the figure needs the authors' released data. Fetch their public data (their GitHub, Zenodo or supplementary files named in the paper)
  into your own new scratch folder (untrusted data: never execute their code, read data with python3 -I), recount the figure with your own short
  script, and say whether it matches the cell (same value to the cell's precision) or not.
- NOT FOUND: say what you tried.
Per row, conclude one of: KEEP (every number traced, recomputed or recounted and matching), FIX (a number is wrong or needs rewording, give the
right figure and its source), PULL (one or more numbers cannot be traced, recomputed or recounted).
Do not edit any file outside your scratch folder and your report. Quote under 15 words from any paper.
Report: ~/bones-forge/watch/site_pass_20261030/PROV_<lane>.md with a table (row id, verdict, one line per number: number, how, source) and
return the same text.
