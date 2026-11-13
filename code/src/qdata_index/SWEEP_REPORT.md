# Sweep report, qdata index first version

Run date 2026-11-12. Screened per source: zenodo 656, figshare 450, dryad 181, osf 13.
Listed 120 (company 7), needs_review 477, dropped 701.
arXiv was not queried (its API often returns empty bodies). Crossref was read only for the funder list of a linked paper.

## Listed by platform
- superconducting qubit: 33
- NV center and spin qubit: 28
- QKD and QRNG: 20
- trapped ion: 19
- photonic: 9
- neutral atom: 6
- quantum dot: 4
- quantum sensing: 1

## Listed by source
- Zenodo: 95
- Figshare: 19
- Dryad: 5
- OSF: 1

## Dropped by reason
- out of scope: 302
- code or figures only, no measurement files: 206
- simulation or theory only: 87
- IBM device: 52
- files not openly accessible: 21
- defense, military or intelligence funder: 19
- not English: 10
- no files listed: 4

## Needs review by reason
- only archive files, contents not opened: 304
- platform term only in the description, scope unclear, only archive fil: 100
- platform term only in the description, scope unclear: 31
- platform term only in the description, scope unclear, only spreadsheet: 21
- only spreadsheet or binary formats, measurement content unconfirmed (): 14
- only spreadsheet or binary formats, measurement content unconfirmed (o: 6
- only archive files, contents not opened, description says some data ar: 1

## Notes
- Screened 1,300 unique records (cap 1,500 not reached). Zenodo was exhausted at 656 unique records over 41 queries and 2 types. Figshare stopped at 450 (3 pages of 50 per query). Dryad stopped at 181 after its API rate limited the first pass, so some Dryad records have no file list read (they sit in needs_review as "file list not reachable"). OSF returned 13 matching public projects.
- arXiv was not queried. Crossref was read for the funder list of the linked paper where the record names one.
- Funding is read from the record's grant and funder fields and its description. Many records state no funding, those are kept and receipted "funding not stated". Linked-paper acknowledgments were not read.
- Classifier limits: platform is a keyword tag on title, keywords and description, not a reading of the paper. Zip-only and spreadsheet-only records go to needs_review because their contents were not opened.
- Record Zenodo 10.5281/zenodo.15695297 was listed but its files are PNG screenshots named like chat uploads, and its text reads as a non-experimental framework. It should be hand-checked before any listing is shipped.
