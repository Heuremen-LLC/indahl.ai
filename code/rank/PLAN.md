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
