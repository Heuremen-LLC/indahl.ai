# RANK med public pull, 10 Nov 2026
Fetched with curl, User-Agent "HeuremenRANK/0.1 (+https://indahl.ai/oy)". No ranking sites, no MSAR, no aggregators.

## AAMC FACTS (files/aamc, files/aamc_prior)
- 2026 FACTS applicants page: https://www.aamc.org/data-reports/students-residents/data/facts-applicants-and-matriculants (files/facts-applicants-and-matriculants.html). Table A-1 2025-2026 = media/86591.
- 2026 FACTS enrollment page: https://www.aamc.org/data-reports/students-residents/data/facts-enrollment-graduates-and-md-phd . Table B-1.2 (2021-22 to 2025-26) = media/87066.
- Prior-year pages: https://www.aamc.org/data-reports/data/2024-facts (holds "2025 FACTS" A-tables; Table A-1 2024-2025 = media/79766, B-1.2 prior edition = media/80601) .
- Glossary: https://www.aamc.org/data-reports/students-residents/data/facts-glossary
- B-1.2 2024-25 differs slightly between editions for some schools (e.g. UC San Diego 666 vs 668 in the 2025-26 edition; Emory 680 vs 679); both recorded.
- MCAT/GPA by school: not public. A-16..A-23 are national, by major, race, state, gender or grid.
- Sheet "row index" = position among the XLSX row elements, 1-based (parsed with a stdlib reader).

## Schools (files/schools)
Only pages that state the entering-2025 / Class of 2029 figure were recorded as values: Pitt, Yale, Colorado (news), Ohio State (news), USF (news). Others showed a different class year or nothing; see "where" in med_public.json.

## NIH RePORTER (files/nih)
POST https://api.reporter.nih.gov/v2/projects/search with {"criteria":{"org_names":[ORG],"fiscal_years":[FY]},"include_fields":[ApplId,ProjectNum,FiscalYear,AwardAmount,Organization,OrganizationType,ProjectStartDate],"limit":500,"offset":N,"sort_field":"appl_id"}.
Sum of award_amount over rows whose organization.org_name equals ORG exactly (the API matches names loosely: "UNIVERSITY OF FLORIDA" also returned UCF, UNF, USF, UWF rows; "VANDERBILT UNIVERSITY" returned VUMC rows), de-duplicated by appl_id. Second figure = same rows with organization_type.name SCHOOLS OF MEDICINE (Rochester: SCHOOL OF MEDICINE & DENTISTRY). Mayo Clinic Rochester rows are typed Other Domestic Non-Profits, VUMC rows Independent Hospitals, so no School of Medicine subset exists for them. Org names used are in files/nih/summary.json. NIH's report.nih.gov Awards by Location table was not used (not fetched).
