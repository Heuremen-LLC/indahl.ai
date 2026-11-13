# RANK desk: New Jersey college public-record sources (read 10 Nov 2026)

Request header on every fetch: `HeuremenRANK/0.1 (+https://indahl.ai/oy)`. No browser tools, no usnews.com, no workarounds for blocks. Neutral facts only.

## Sources
- IPEDS via the Urban Institute Education Data API, NJ rows (`fips=34`), filtered to each unitid: directory 2023, fall-enrollment 2023/2024 (undergraduate totals), admissions-enrollment 2023/2024, fall-retention 2023/2024, student-faculty-ratio 2024, grad-rates 2022/2023 (bachelor's subcohort), grad-rates-pell 2022/2023. Raw responses in `ipeds/raw/`, directory in `ipeds/directory/`, summary in `ipeds/ipeds_summary.json`.
- College Scorecard, Most Recent Cohorts institution file, release 2 Nov 2026: `https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_11022026.zip`. Same file (identical SHA-256) as the one already downloaded for `public/college/`, copied to `scorecard/`. Extract: `scorecard/scorecard_extract.json`.
- Each college's own Common Data Set from its own site. Files in `cds/<slug>/`, extracts in `cds/<slug>/cds_extract.json` (URL, item, counts, notes).
- Princeton: the CDS 2024-25 PDF and extract read earlier for `public/college/` were copied in. The 2025-26 page (Cloudflare bot check) was not re-requested; it is already listed in `~/bones-forge/research/MANUAL_READS.md`.

## What does not exist yet (10 Nov 2026)
- IPEDS fall 2025 enrollment, admissions and retention are not in the Urban API (2025 queries return 0 rows or a server error). Newest IPEDS graduation cohort there: fall 2018 (Urban year 2023). The four-year count in that endpoint is -1 (not published).

## Build
- `scripts/unitids.json`, `scripts/build/ipeds_summary.py`, `scripts/build/scorecard_pull.py`, `scripts/build/merge.py` (all run with `python3 -I`). Output: `nj_college_public.json`, same keys as `public/college/college_public.json`.

## CDS files used (each college's own site)
- Princeton 2024-25: ir.princeton.edu (copied from public/college). 2025-26: bot check, in MANUAL_READS.
- Stevens 2025-26 and 2024-25: Stevens IR PDFs (2025-26 pages carry a stale "2024-2025" header; the body says Fall 2025).
- NJIT 2025-26 (Google Sheet xlsx export linked from https://www.njit.edu/oie/external-surveys, opened with no sign-in) and 2024-25 (xlsx). I2 2025-26 stored as 15.8968 (11096 students / 689 faculty); display format not captured.
- TCNJ 2025-26 and 2024-25: ira.tcnj.edu PDFs. curl got HTTP 403; one WebFetch retry returned the files. Local copies are the WebFetch-saved binaries.
- Montclair 2025-26 and 2024-25: irdata.montclair.edu PDFs (CDS 2025-26 and 2024-25 print no ACT composite).
- Rowan 2025-26: https://sites.rowan.edu/academic-affairs/ida/_docs/rowan_university_cds.pdf. 2024-25 not posted (the IR page links only the current file).

## Not posted on the college's own site (10 Nov 2026)
- Rutgers New Brunswick, Newark, Camden: the OIRAP index (https://oirap.rutgers.edu/ReportingCommonDataSet.html) runs to 2023-24. Neither 2024-25 nor 2025-26 is listed.
- Seton Hall: the IR reports page links CDS only for 2002-03 to 2004-05.
- Monmouth: the IR page links a 2023 Factbook, no CDS.
- Drew: the IR page lists CDS 2013-14 to 2022-23 only.
- Rowan 2024-25.

## Refusals
- Princeton (see public/college/SOURCES.md), TCNJ curl 403 (WebFetch succeeded). Guessed NJIT and Rutgers paths returned 404. No new MANUAL_READS rows were needed.
