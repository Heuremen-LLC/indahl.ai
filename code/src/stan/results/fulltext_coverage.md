# Full-text coverage of the STAN gold papers

Data file: data/fulltext_coverage.json. Files: data/fulltext_cache/<gold id>.pdf. Measured 12 Nov 2026; availability only, no labels read.

The gold set has 197 papers, 98 in dev and 99 in test. 185 full texts were fetched without login or CAPTCHA (93 of 98 dev, 92 of 99 test). 11 gold papers have a Zenodo record with no PDF file (NO_OA, 5 dev and 6 test), and 1 test paper has no link or identifier (NO_IDENTIFIER). No fetch failed on an OA link (OA_LINK_FAILED is 0).

Overall: {"FETCHED": 185, "NO_OA": 11, "NO_IDENTIFIER": 1}
Dev: {"FETCHED": 93, "NO_OA": 5}
Test: {"FETCHED": 92, "NO_OA": 6, "NO_IDENTIFIER": 1}

Fetched per host: {"export.arxiv.org": 154, "zenodo.org": 31}. Every arXiv link (154) returned a PDF from export.arxiv.org. 31 of the 42 Zenodo DOIs gave a PDF through the Zenodo record API. For the other 11, OpenAlex and Unpaywall found no OA PDF.

Text extraction used pypdf (pdftotext is not installed). 184 of 185 PDFs extracted at least 2,000 characters. One is flagged: 08c4a2608cbe, 254 characters (scanned or broken).

Missing gold ids (12): 23c298df9668, 1b5fd77201b7, c8464231d15c, c64790376be8, d2d4a7dab90f, e6242804a39e, 41a71ef528c1, 570f6ffd1a09, a7e5216992e7, 76fd4d1ffba9, 63bb4576036e, 92e1274eff5c.
