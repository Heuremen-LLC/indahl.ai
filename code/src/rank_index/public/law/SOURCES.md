# RANK / law: sources (read 2026-11-10)

All figures come from the ABA required disclosures site, https://www.abarequireddisclosures.org/ . The site is a JavaScript app. Its download buttons call the public backend below, and we fetched the same files with curl (UA "HeuremenRANK/0.1 (+https://indahl.ai/oy)"). We did not use usnews.com or any secondary source.

## Compilation spreadsheets (primary, row numbers cited in law_public.json)
| Key | File (downloads/) | URL |
|---|---|---|
| 509_2025 | comp509_2025_FirstYearClass.xlsx | https://backend.abarequireddisclosures.org/api/AnnualQuestionnaire/GetAllCompilationData?year=2025&scetionName=First%20Year%20Class |
| ft_2024 | bar_2024_First_Time_Bar_Passage.xlsx | https://backend.abarequireddisclosures.org/api/BarPassageOutcomes/GenerateBarPassageCompilationReport?year=2024&sectionName=First%20Time%20Bar%20Passage |
| ft_2025 | bar_2025_First_Time_Bar_Passage.xlsx | same, year=2025 |
| ft_2026 | bar_2026_First_Time_Bar_Passage.xlsx | same, year=2026 |
| ub_2025 | bar_2025_Two-Year_Ultimate_Bar_Passage.xlsx | ...GenerateBarPassageCompilationReport?year=2025&sectionName=Two-Year%20Ultimate%20Bar%20Passage |
| ub_2026 | bar_2026_Two-Year_Ultimate_Bar_Passage.xlsx | same, year=2026 |

(`scetionName` is spelled that way in the ABA's own code.) The "Bar Admission" section names return files with the same figures for these schools. They are kept in downloads/ but not cited.

## Individual school reports (cross-check)
downloads/individual/509_2025_school{code}.pdf and bar_{2024,2025,2026}_school{code}.pdf, from
- .../api/AnnualQuestionnaire/GenerateIndividualDisclosure509Report?schoolId={code}&year=2025
- .../api/BarPassageOutcomes/GenerateIndividualBarPassageReport?schoolId={code}&year={year}

ABA school codes: Stanford 21, Chicago 50, Yale 25, Penn 130, Virginia 153, Harvard 74, Duke 109, NYU 105, Columbia 101, Northwestern 49, Michigan 76.
Cross-check: scripts at ~/bones-forge/rank_index/scripts_law/crosscheck_pdfs.py. Log at crosscheck_pdfs.log. 0 mismatches.

## How to read the periods
- 509 report 2025 = entering class of fall 2025 (the PDF says "2025 First Year Class (Oct 6th 2024-Oct 5th 2025)"). "All" = full-time plus part-time. None of the 11 schools reports part-time entrants (PTEnrollees = 0), so All equals FT.
- Acceptance rate: we give both the ABA's published AcceptanceRate and offers/applications x 100 to one decimal (half-up).
- First-time bar data is listed by **calendar year of graduation**, not by exam year. Report 2024 covers graduates in 2023, report 2025 covers graduates in 2024, and report 2026 covers graduates in 2025. The comparison figure is called "ABA weighted average bar pass rate" in the 2025 PDF and "Council weighted average bar pass rate" in the 2026 PDF. In the spreadsheet it is the AvgStatePassPercent column.
- Two-Year Ultimate: report 2025 covers "2022 Graduates" and report 2026 covers "2023 Graduates".

## Rebuild
python3 -I ~/bones-forge/rank_index/scripts_law/build_law_public.py. This rewrites law_public.json without the crosscheck block, so run crosscheck_pdfs.py afterwards.
