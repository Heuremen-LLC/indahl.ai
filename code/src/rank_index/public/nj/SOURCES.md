# RANK desk: New Jersey public-record figures (26 schools)

Read 2026-11-10 (UTC 17:43 to 17:50), UA `HeuremenRANK/0.1 (+https://indahl.ai/oy)`. All primary state or federal files. No student-level data.
Results: `nj_public.json`. Each record copies one published row, uses the state's own column headers, and gives source URL, file, sheet, xlsx row and date read. The `summary` block per school only copies published cells.

## Files
| Source | URL | Local folder | Notes |
|---|---|---|---|
| NJ SPR database 2023-24 (school) | https://www.nj.gov/education/sprreports/download/DataFiles/2023-2024/Database_SchoolDetail.xlsx | files/spr_2023-2024/ | sha256 fd36785b…ce086b. Layout file in the same folder. Linked from https://www.nj.gov/education/spr/download/ (list built by script/download.js) |
| NJ SPR database 2024-25 (school) | https://www.nj.gov/education/sprreports/download/DataFiles/2024-2025/Database_SchoolDetail.xlsx | files/spr_2024-2025/ | sha256 546cc2c0…54ff. The 2024-25 sheets carry a SchoolYear column (2021-22 to 2024-25). Only the 2023-24 and 2024-25 rows are kept |
| NJSLA / NJGPA / DLM / ACCESS results 2023-24 | https://www.nj.gov/education/assessment/results/reports/2324/index.shtml (each .xlsx under /2324/spring/ and /2324/dlm/) | files/assess_2324/ | ELA03-09, MAT03-08, ALG01, GEO01, ALG02, SC05/08/11, ELAGP/MATGP (NJGPA), DLM ELA/Math/Science, ACCESS |
| Same, 2024-25 | https://www.nj.gov/education/assessment/results/reports/2425/index.shtml | files/assess_2425/ | File names on the server have spaces (%20), saved here with underscores |
| NCES CCD 2023-24 (API year 2023) and 2024-25 (API year 2024) | https://educationdata.urban.org/api/v1/schools/ccd/directory/{2023,2024}/?fips=34&per_page=10000 and /schools/ccd/enrollment/{y}/grade-{pk,k,1..13,99}/?fips=34 | files/nces_urban_20261110/ | Urban codes: -1 missing, -2 not applicable, -3 suppressed |

Extracts (filtered to the 26 schools by County/District/School code): files/extract_2324, files/extract_2425, files/assess_extract_2324, files/assess_extract_2425. Code: code/xlsx_stream.py (streams the xlsx to CSV and keeps the xlsx row number), code/build_nj.py, code/report.py, code/keys.txt (codes).

## School codes (county-district-school, NCES)
03-0290-020 Bergen County Academies 340147000250 · 03-0290-070 BCTHS Teterboro 340147000262 · 03-1760-065 Alexander Hamilton (Glen Rock) 340597000482 · 03-4390-120 Orchard Elementary (Ridgewood) 341383000780 · 13-2730-090 Harrison Elementary (Livingston) 340882002136 · 13-3190-070 Glenwood (Millburn) 341020002154 · 17-2390-002 Infinity Institute 340783003121 · 17-2390-075 Dr Ronald McNair HS 340783002778 · 17-2390-340 Cornelia F. Bradford 340783002834 · 17-5240-140 Sara M. Gilmore Academy 341638000143 · 23-3150-010 Edison Academy Magnet 341008000395 · 23-3150-070 Woodbridge Academy Magnet 341008003428 · 25-2720-050 Markham Place 340879003898 · 25-3260-010 High Technology HS 341750006095 · 25-3260-028 Biotechnology HS 341750006121 · 25-4570-050 Forrestdale 341437004092 · 25-4980-050 H W Mountz 341557004106 · 27-0785-060 Milton Avenue 340000406017 · 27-3100-060 Mendham Township MS 340993004322 · 31-4010-310 School 28 (Paterson) 341269004924 · 39-5260-020 Academy for Allied Health Sciences 341804000584 · 39-5260-030 Academy for Information Technology 341804006134 · 39-5260-040 Union County Magnet HS 341804000214 · 80-6036-921 Hoboken Dual Language CS 340073403037 · 80-6081-967 Thomas Edison EnergySmart CS 340074603143 · 80-7540-930 Princeton Charter 340004300323

## What the state publishes, by label
- SPR `ELAParticipationPerformance` / `MathParticipationPerformance`: Valid Scores, "% of Students taking test" (2023-24) / ParticipationRate_School (2024-25), met/exceeded %, federal proficiency rate, by student group.
- SPR `ELAPerformanceByGrade`, `MathPerformanceByGradeTest` (2023-24), `ELAPerformanceByTest`, `MathPerformancebyTest` (2024-25): valid scores, mean scale score, % Level 1-5, by grade/test and student group.
- SPR science: `ScienceAssessmentByGrade` (2023-24, % Level 1-4 by grade and group, no valid-score count); `OverallNJSLAScience` (2024-25, PercentageProficient_School) and `NJSLASciencebyGradeTrends`.
- SPR `NJGPA`: ELA/Math valid scores and % graduation ready (2023-24 prints ">90%" ranges).
- NJSLA results files: "Registered To Test", "Not Tested ** (See Below)" ("includes all students who were registered but did not receive a valid scale score"), Valid Scores, L1-L5 %, with subgroups incl. "SE Accommodation". Rows with fewer than 6 valid scores are not reported.
- Alternate assessment: SPR `AlternateAssessmentParticipatio` (2023-24) and `DLMTrends` (2024-25, label "Fewer then 10 students registered for DLM" as printed); DLM results files by grade.
- SPR `SchoolDay`: TypicalStartTime, TypicalEndTime, LengthOfDay, InstructionFullTime, InstructionSharedTime.
- SPR graduation: `FederalGraduationRates`, `GraduationRateTrendsProgress`, `4YrGraduationCohortProfile` (2023-24); `FederalGraduationRates`, `GraduationRateTrends`, `GraduationCohortProfile` (2024-25).

## Not published at school level (searched, not found in these files)
- Days per school year: no SPR field.
- Counts of first-year English learners exempt from ELA, medical exemptions, refusals: no school-level field in SPR or the results files. "Not Tested" is a single count, and it is "*" for all 26 schools in every test, both years. Statewide only 30 of 1,912 school rows in ELA03 2023-24 show it unsuppressed.
- "Number enrolled/expected" for the assessment: shown only as "Registered To Test", which is "*" for all 26 schools.
- 2023-24 science percent proficient as a single school figure: SPR 2023-24 gives levels by grade only.

## Value notes
- Some 2023-24 SPR percentages are stored as binary floats (for example `9.3000000000000007`, `16.600000000000001`). They are kept as stored. The display value is the short decimal.
- 2024-25 SPR values include the % sign as published. 2023-24 values do not.
- NCES free/reduced-lunch -1 (missing): Markham Place and Forrestdale 2024-25, H W Mountz 2023-24.
- Hoboken Dual Language CS 2024-25 data quality notes (state-published) cover Computer Science and Visual and Performing Arts only.
- The rc.doe.state.nj.us online report pages could not be read (TLS name mismatch). Logged in research/MANUAL_READS.md.
