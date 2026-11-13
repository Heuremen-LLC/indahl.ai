# RANK: US News education rankings against the public record. Plan, written before any US News figure was set beside a public figure.

Written 2026-11-10. Sealed by git commit before the first comparison. Changes after the seal are dated addenda below the seal line, never edits.

## What is read
US News & World Report publishes rankings of schools. For each list it states the indicators and their weights. RANK records, for every list in scope, the current edition's top of the list, the edition, the list address and the method address. It then sets the figures US News prints against the same figures in the public record, and asks whether the order follows from the stated method where the method can be recomputed.

## Lists in scope (current edition, read 2026-11-10 in a signed-in browser session, raw captures in raw/, kept internal)
- Best High Schools, national (2026-2027 edition).
- Best Elementary Schools and Best Middle Schools. US News's method page says: "There is no national ranking". These two lists are recorded as no national list published. No state is picked in its place.
- Best Colleges: National Universities, National Liberal Arts Colleges (2027 edition). Regional lists later if time allows, by the same rule.
- Best Graduate Schools (2026 edition): Business (full-time MBA), Law, Medicine (Research), Engineering, Education. Medicine is published in tiers, not ranks, and is recorded as Tier 1 in the order US News shows it, with no rank.

## Top-ten rule
Every school whose printed rank is 10 or better, so a tie at the edge is kept whole (a list can hold more than ten). Rank, name and location as US News prints them.

## Step one (listing)
Each row reads "check in progress" until its checks below are done. Rank, edition, list link and method link only. Indicators and weights are quoted short from the method page.

## Step two (checks), per figure
Figures: only those US News prints on the list page or the school's page, and only those with a public counterpart.
- K-12 (high schools): graduation rate, enrollment, state assessment proficiency where printed. Public side: the state's own report card for the same school and year, NCES Common Core of Data (enrollment, FTE teachers, free and reduced-price lunch).
- Colleges: graduation rate, first-year retention, Pell share or Pell graduation rate, test score ranges, student-faculty ratio, class size, enrollment where printed. Public side: IPEDS, College Scorecard, the school's own Common Data Set.
- Graduate schools: figures printed per school (for law: bar passage, employment, LSAT, GPA, acceptance; business: salary, employment, GMAT, GPA, acceptance; engineering and education: acceptance, research spending, doctoral degrees; medicine: MCAT, GPA, acceptance). Public side: ABA Standard 509 disclosures and employment summaries, AAMC where public, the school's own published reports.
Outcomes per figure:
- MATCH: same quantity, same year (or the year US News names), equal after rounding the public figure to the precision US News prints.
- MISMATCH: same quantity and year, different after that rounding.
- CANNOT_TELL, reason counted apart: year differs or unstated, public figure not found, definition differs, US News prints a range or a floor (for example "> 95%") that the public figure does not settle, figure behind a paid tier (recorded as "paid tier, not read").
The year each side uses is printed beside every figure. No tolerance beyond rounding.

## Rank recompute
Recompute only where every indicator and weight is stated and every input is public. Where an input is a survey score (peer, recruiter, lawyers and judges), purchased data (AP and IB exam results), or a model US News fits (performance against expectations, predicted graduation rate), the recompute reads CANNOT_TELL, method not fully recomputable from public inputs, and names which input is missing.

## Blue Ribbon (K-12)
For each top-ten high school that holds a National Blue Ribbon award: award year, category (Exemplary High Performing or Exemplary Achievement Gap Closing) and the stated criterion, from the US Department of Education's own list. The criterion is checked against the state assessment data for the years the award cites. Outcomes as above.

## Instructional time
Where a state publishes instructional minutes or days per school, and the school's own public documents state a figure, the two are set side by side. Nothing else is said about it.

## Corrections cases
Public, documented cases where a school's submitted data was later found wrong and its US News rank changed are listed only from primary sources (a US News notice, the school's own statement, a court or regulator filing). Nothing is stated from memory.

## Rules
- Same rule for every school. No adjectives about schools, staff, parents or US News. No cause named for any gap. No student-level data. No staff names except published officials where needed.
- US News content is copyrighted. The page quotes only the rank, the method and the specific figures checked, each with a link. No US News table is republished. Raw captures stay internal.
- Every row has a respond link so the school or US News can answer.
- A referee with its own code re-reads every figure from US News and the public sources before each ship.

---
## Addendum 1, 2026-11-10 (before any New Jersey figure is compared): New Jersey

Lists, read 2026-11-10 in the owner's signed-in browser (raw/nj_*_20261110.txt):
- Best High Schools in New Jersey (2026-2027), state ranks 1 to 10, with the national rank US News prints beside each.
- Best Public Elementary Schools in New Jersey and Best Public Middle Schools in New Jersey (2027), state ranks 1 to 10.
- Colleges: US News's New Jersey page (2027) shows schools by list, then rank. The first ten rows it shows are all National Universities. The New Jersey school ranked highest on each other list it shows (National Liberal Arts Colleges, Regional Universities North) is added. Every rank is printed with the list it comes from. Ranks from different lists are never compared.

The source rule (owner's): for every indicator a list uses, name where its data comes from, and check the figure at that source.
- "Where the data comes from" table for every list on the page: indicator, weight, source as US News names it, and whether that source is public. Surveys US News runs, models US News fits, and purchased or school-submitted data that is not published per school read "not public".
- State test proficiency (NJ): New Jersey School Performance Reports (NJ SPR) and NJDOE assessment files, school year 2023-24 for high schools (US News names it). For elementary and middle schools the method page read names no test year, so each figure is read against 2023-24 and against 2024-25, scored CANNOT_TELL (year not printed), with both shown.
- Who is in the proficiency figure: from NJ SPR and NJDOE files, for each school and subject: enrolled or eligible count, tested count, participation rate, and every count of students not tested or not in the proficiency figure that the state publishes, by reason as the state names it (for example not tested, alternate assessment DLM, first-year English learners, medical exemption). The share of enrolled students whose scores are not in the figure is computed as (eligible minus counted) over eligible and shown for all schools side by side. Only counts are shown. No reason is given for any count.
- Subgroups: the subgroup proficiency and participation tables NJ SPR publishes for the same school and year, shown as published.
- Instructional time: NJ SPR's own reported length of school day and instructional time, set against the school's or district's published bell schedule or calendar where public. Only stated figures, side by side.
- Graduation, enrollment, lunch shares: NJ SPR and NCES CCD as in the plan.
- Colleges: Common Data Set, IPEDS, and the indicator list US News names, as in the plan.
- Rank claims: a public statement by a school or district about its US News rank (homepage, press release, board minutes) is quoted exactly, linked and dated, and set against the list: MATCH if the stated rank, list and edition equal what US News prints, MISMATCH if not (for example a state rank stated as a national rank), CANNOT_TELL if the statement names no edition or list.
- Same rules otherwise: same rule for every school, no cause, no adjectives, counts not motives. Pages that refuse automated reads are logged in research/MANUAL_READS.md for the owner to open.

---
## Addendum 2, 2026-11-10 (before any graduate school figure is set beside a public figure): business, engineering, education and medical schools

US News side: each school's US News page, read 2026-11-10 in the owner's signed-in browser without a paid tier (raw/grad_pages_20261110.txt), and the method pages (raw/grad_method_addendum_20261110.txt). Every school page says "details based on 2025 data". Figures behind the paid tier (GMAT and GRE, GPA, research expenditures, doctoral degrees, MCAT, NIH figures) are recorded once per school and indicator as CANNOT_TELL, paid tier, not read, with the public figure shown beside them where one was found. No purchase is made.

Years. US News's "2025 data" is read with the method page's own words: MBA employment and salary are the class graduating in 2025 (the method names "the 2025 graduating class" for profile outcomes), MBA admissions are full-time entrants of fall 2025, engineering and education admissions are fall 2025 or 2025-2026, medical figures are the 2025 entering class and 2025. A public figure for another class or year reads CANNOT_TELL (year). Two-year averages US News prints for MBA employment are not scored, because the method's weighting ("twice as many students") does not say whether graduates or job seekers are counted. They are shown beside the single-year readings where both public years were found.

Figures scored, and the public side for each:
- MBA (full-time): acceptance rate, applicants, new entrants: the school's own class profile for the class entering fall 2025. Employed at graduation, employed three months after graduation, average base salary: the school's own employment report for the class of 2025, read under the MBA CSEA standards where the report says it follows them. US News counts graduates seeking employment. The public figure used is the report's share of job seekers with an accepted offer. A report that gives only offers received, or only a median salary, reads CANNOT_TELL (definition), with its figure shown.
- Engineering: acceptance rate (master's and doctoral), total graduate engineering enrollment, master's and doctoral applicants, tenured or tenure-track faculty, doctoral students per faculty member: the school's own published figures (fact pages, data digests, ASEE profiles where public) for fall 2025. Research expenditures and doctoral degrees are paid tier on US News and are shown beside NSF HERD (engineering field, institution total, fiscal year 2024 and 2025 where released) and IPEDS completions (engineering doctorates), each labelled as a different scope from the ASEE definition US News names.
- Education: acceptance rate, applicants, accepted, total enrollment, tenured or tenure-track faculty, students who took an assessment: the school's own published figures for the year US News names. Research expenditures and doctoral degrees are paid tier and shown beside NSF HERD (education field) and IPEDS completions (education doctorates), labelled as different scope.
- Medicine (Tier 1 only): acceptance rate, total enrollment, full-time faculty, faculty-to-student ratio: the school's own published class profile and fact pages, and AAMC FACTS tables where public (applicants, matriculants, total enrollment by school). An acceptance rate needs an offers count, which AAMC does not publish by school, so it is scored only against a school's own published figure. Research activity and NIH grants are paid tier on US News and are shown beside NIH RePORTER totals for the school of medicine, fiscal years 2024 and 2025, labelled as a different scope (US News counts the medical school and its affiliated hospitals, from school reports).

Rounding and outcomes as in the plan: MATCH after rounding the public figure to the precision US News prints, MISMATCH otherwise, CANNOT_TELL by reason. A count is equal only if identical. A rate is worked from published counts when no rate is published, and the counts are shown.
"Where the data comes from" tables for these four lists are rewritten per indicator, and inputs no source publishes per school read "not public".
Pages that stop at a challenge or a login are logged in research/MANUAL_READS.md. Same rules otherwise: same rule for every school, no cause, no adjectives, no student-level data.
