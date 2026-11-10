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
