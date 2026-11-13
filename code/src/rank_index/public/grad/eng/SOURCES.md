# RANK engineering public pull, 10 November 2026

All files saved in files/. Fetched with curl, User-Agent HeuremenRANK/0.1 (+https://indahl.ai/oy). No ranking sites visited. No logins, no challenges bypassed.

Primary sources used
- NSF NCSES HERD FY2024, publication nsf26304, Table 21 (engineering R&D, standard form population, FYs 2021-24): https://ncses.nsf.gov/pubs/nsf26304/assets/data-tables/tables/nsf26304-tab021.xlsx (files/herd24/, zip files/nsf26304_tables_excels.zip, pdf files/nsf26304-tab021.pdf). HERD FY2025 survey page returned 404.
- IPEDS Completions C2024_A (AY 2023-24) and C2023_A (AY 2022-23): https://nces.ed.gov/ipeds/datacenter/data/ . C2025_A returned 404. The files carry 6-digit CIP rows only, no CIP 14 total row, so the value is the sum of CTOTALT over all 14.xxxx rows, MAJORNUM=1. By CIP family at the institution, not the school. Excludes computer science (CIP 11).
- MIT Facts: facts.mit.edu enrollment-statistics, faculty, graduate-student-admission (Fall 2025 / 2025-26).
- Georgia Tech IRP 2025 Fact Book PDF (Fall 2025, FY2025). Best source of the ten: applicants, admits, enrolled, tenure-track faculty by college.
- CMU IR Quick Facts 2025-2026 PDF (page image checked for column mapping).
- UCSD Jacobs rankings/statistics page (Fall 2025 enrollment split, FY2024-25 research expenditures).
- Stanford Facts graduate student profile, Berkeley Engineering facts-and-figures, Purdue Engineering facts page, Caltech EAS About and Registrar, Grainger About, Cockrell facts page.

Cautions
- Several school pages carry undated or mixed-year marketing figures (Purdue faculty line, Caltech EAS, Grainger, Cockrell). Year is recorded as "not stated".
- Berkeley's page prints "Fall 2026" and "2025-26" labels as retrieved on 2026-11-10; Fall 2025 not shown.
- The saved Purdue, Grainger, Cockrell and Jacobs pages contain sentences about third-party rankings. Those lines were not recorded.
- HERD "i" flag beside a value is printed in the xlsx; its meaning is not in the sheet read.
- Not published in the documents read (see null rows): school-level master's/Ph.D. applicants/admits for most schools, school-level research expenditures for most schools. See manual_reads.json.
