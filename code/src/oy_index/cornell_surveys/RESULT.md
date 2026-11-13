# Cornell Spring 2025 GenAI surveys - recount (Bones, 25 Oct 2026; recount.py on Faculty-focus_data.csv / Student-focus_data.csv)
Data released: group-level aggregates (question x response x discipline group: count + %), instruments, PDFs, Tableau. No microdata.
C2 group sizes: student discipline-group labels sum to n = 2,539 (864 + 335 + 894 + 446) against 1,988 stated respondents and 2,029
   on the usage item. Item counts (field "count d emplid", read as a distinct-ID count) sum to 2,034 - 5 more than 2,029, consistent with
   5 students sitting in two groups. Overlap cannot account for the 551 gap between labels and respondents: in every student group the
   item count is ~0.79-0.84 of the label n. The label base is unidentified (candidates: students who opened the survey, a pre-exclusion
   count, another term) -> CANNOT_TELL. Faculty labels sum to 735 of 737; faculty usage counts 732 (page 737).
   [Corrected after referee 25 Oct: the first version said the groups overlap and the printed item n is a sum over them - withdrawn.]
C1 item n: the page prints "Students: 2,029" for the usage question, above its own stated total of 1,988, without explanation.
C3 percentages: "% of Total valid response" is computed on each group's valid responses for that item, not on the label n
   (e.g. 53 "Not at all" in Social & Behavioral Sciences = 7.74%, so base ~685, not 864). Single-choice items: 0 mismatches > 0.5 pt;
   multi-select tool items differ by construction (shares of respondents, not of selections) - not an error.
C4 S0: every "learning outcome" item is self-reported agreement ("GenAI has helped me better understand difficult concepts", etc.);
   the page header line "In general, GenAI tools have improved teaching and learning at Cornell." is a rated statement (Chart 1, item n
   700 faculty / 1,804 students). No measured outcome -> S0 = USAGE-OR-ATTITUDE ONLY.
C5 implied invited populations: 737 / 0.32 = ~2,300 faculty; 1,988 / 0.14 = ~14,200 students (stated rates are rounded).
Credit: of the Ivy rows read so far (25 Oct), Cornell is the one that released response counts, both instruments and machine-readable files.
State: RECOUNTED (aggregates). Not a recount of individual answers (none released).
