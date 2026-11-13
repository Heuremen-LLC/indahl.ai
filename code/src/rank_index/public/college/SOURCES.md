# RANK desk: college public-record sources (read 10 Nov 2026)

Request header on every fetch: `HeuremenRANK/0.1 (+https://indahl.ai/oy)`. No browser tools, no usnews.com, no workarounds for blocks.

## Sources used
- IPEDS via the Urban Institute Education Data API: `https://educationdata.urban.org/api/v1/college-university/ipeds/...` (directory 2023, fall-enrollment 2023/2024, admissions-enrollment 2023/2024, fall-retention 2023/2024, student-faculty-ratio 2024, grad-rates 2022/2023, grad-rates-pell 2022/2023, outcome-measures 2023). Raw responses: `ipeds/raw/`. Urban codebook: `ipeds/api_variables.json`.
- College Scorecard, Most Recent Cohorts institution file, release dated 2 Nov 2026: `https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_11022026.zip` (saved in `scorecard/`).
- Each college's own Common Data Set, from its own institutional research site. Files in `cds/<slug>/`; per-college extracts in `cds/<slug>/cds_extract.json` (URL, CDS item, counts).

## What does not exist yet (as of 10 Nov 2026)
- IPEDS fall 2025 enrollment, admissions, and retention are not in the Urban API (latest year 2024). The newest IPEDS graduation-rate cohort there is fall 2018 (Urban year 2023).
- The IPEDS graduation-rate endpoint gives the 150% (six-year) rate only. Its four-year count (`completers_100pct`) is -1 (not published) for every row. The four-year figure is taken from the CDS (B7/B6) and the Scorecard (`C100_4`).
- The Urban IPEDS admissions endpoint has no SAT/ACT after 2022. SAT/ACT figures come from the CDS (composite) and the Scorecard (section scores, ACT composite).

## Refusals and blocks (not worked around)
- api.data.gov Scorecard API with DEMO_KEY: HTTP 429 after 10 calls per hour. Used the Scorecard download file instead.
- nces.ed.gov IPEDS Data Center `data/EF2024A.zip`, `GR2024.zip`, `ADM2024.zip` and the 2025 versions: HTTP 404 at those names (the 2023 files answer 206). Urban API used instead.
- amherst: https://www.amherst.edu/about/facts/common_data_sets -> HTTP 405, WAF captcha (curl)
- amherst: same URL via WebFetch -> HTTP 405
- amherst: https://amherst.edu/system/files/A%2520General%2520Information_5.pdf -> HTTP 405 (curl)
- harvard: https://oir.harvard.edu/ -> HTTP 403 (wrong host; correct site oira.harvard.edu worked)
- jhu: https://oira.jhu.edu/common-data-set -> curl HTTP 403 (bot check/block page) and WebFetch HTTP 403; not worked around
- jhu: https://oira.jhu.edu/wp-content/uploads/CDS_2024-2025_JHU-2.pdf -> curl HTTP 403 (URL from search result)
- jhu: https://oira.jhu.edu/wp-content/uploads/2025-2026-CDS-Johns-Hopkins-University-v2.pdf -> curl HTTP 403 (URL cited by a third-party site, unverified)
- mit: https://ir.mit.edu/cds -> 404 (wrong guess; index found via search)
- penn: https://upenn.box.com/s/woo7d85yxpol6j9e2o121aucjc6dc1k5 -> Box shared-link viewer is JS-only; boxcloud content endpoint HTTP 401 (needs token). Stopped, no workaround.
- penn: https://upenn.box.com/s/ckv4frz37rzxa4u6bdiv2h4yzykqm4ef -> same Box wall, not attempted past the page
- pomona: Pomona: Tableau dashboard views other than the first sheet not reachable via public csv; portal API probe denied by permission system, not retried
- princeton: https://ir.princeton.edu/common-data-set -> HTTP 403
- princeton: https://ir.princeton.edu/other-university-data/common-data-set -> HTTP 403 (curl and WebFetch)
- princeton: https://ir.princeton.edu/document/606 (2025-26 CDS listing) -> HTTP 403 Cloudflare bot check (curl and WebFetch); not worked around
- princeton: https://ir.princeton.edu/sites/g/files/toruqf2041/files/documents/CDS_2526_Princeton_v1.4.pdf (URL from a third-party page) -> HTTP 404
- swarthmore: https://www.swarthmore.edu/sites/default/files/assets/documents/institutional-effectiveness-research-assessment/Swarthmore-College-CDS-2024-2025.pdf -> HTTP 404 (replaced by fillable-pdf-version link from IR page)
- usma: https://s3.amazonaws.com/usma-media/inline-images/about/g5/G5OIR_CDS_2025-2026.pdf (guessed URL, not linked on USMA page) -> HTTP 403 AccessDenied from S3; not worked around
- williams: https://www.williams.edu/institutional-research/common-data-set/ -> curl HTTP 403 (bot check/block page) and WebFetch HTTP 403; not worked around
- williams: https://www.williams.edu/institutional-research/files/2026/04/Williams-CDS-2025-2026-V2.pdf -> curl HTTP 403 (URL cited by a third-party site, unverified)

### CDS gaps by college
- Johns Hopkins, Williams, Amherst: own CDS sites refused the fetch (403 / 405 captcha) for curl and WebFetch. No CDS figures. IPEDS and Scorecard figures only.
- Princeton: CDS 2025-26 sits behind a Cloudflare bot check (403). CDS 2024-25 PDF downloaded (HTTP 200).
- Penn: both CDS years are listed on ira.upenn.edu as Box links. The Box content endpoint returned 401 (needs a token). No CDS figures.
- Pomona: CDS 2025-26 and 2024-25 are posted only as Tableau dashboards. The public CSV gives B1 only. A Tableau API probe was denied by the local permission system and not retried.
- USMA: CDS 2025-26 is not posted (its page lists 2021-22 through 2024-25).
- USNA: no CDS for any year on usna.edu. Its Class of 2029 portrait (cds/usna/ClassPortrait.pdf) is recorded in its extract as a non-CDS source.
- Blank cells as printed: the SAT composite is blank in Harvard (both years), Caltech (both years; all of C9 in 2024-25), and Duke 2024-25. Those files print the section ranges.
- IPEDS Pell graduation rate: USNA and USMA report a Pell sub-cohort of 0 (rate -1). Scorecard PCTPELL is 0 and C150_4_PELL is NA for both.

