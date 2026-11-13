# mj4bu recount (Bones, 25 Oct 2026; our stdlib code: recount_r1.py, recount_r1b.py; data OSF Z5Q7S)
R1 synonym perturbation: REBUILDS to the printed count - pass->fail 47/100 (319 synonym variants), fail->pass 5/219; to_standard 1/15, 5/76.
   Their rule: a call passes only on tag [通過]; majority over 3 calls; UNPARSED counts as fail.
   Gap vs their own null (identity copies, separate fresh batch): 0.470 - 0.070 = +0.400 [+0.266, +0.534] (5000 bootstrap draws
   clustered by base answer, 45 bases) -> ABOVE.
   Sensitivity (post-hoc, labelled): UNPARSED calls treated as missing: 44/99 = 0.444; gap +0.375 [+0.244, +0.503] -> ABOVE.
   6 of the 47 failing variants have >=2 of 3 calls UNPARSED (format failure, not a rejection); the finding does not depend on them.
   Carrier noted: the null batch ran separately from the synonym batch (their own label: "fresh batch"); same model snapshot and seed.
R3 feedback effect (242 student x problem units, 43 students; our IRLS logistic with problem fixed effects, independence working
   correlation, 2000 student-cluster bootstrap draws; their exchangeable GEE in brackets):
   system strict A .91 B .71 OR 4.67 [2.47, 11.12] -> ABOVE   (theirs 4.61 [2.33, 9.12])
   uniform re-grader A .71 B .64 OR 1.45 [0.78, 2.76] -> CONSISTENT   (theirs 1.45 [0.80, 2.64])
   human strict A .78 B .72 OR 1.35 [0.75, 2.58] -> CONSISTENT   (theirs 1.39 [0.77, 2.49])
   REBUILDS (unit means exact; ORs within estimator difference). Abstract "it did not (OR 1.5 and 1.4)" is a CONSISTENT reading whose
   bound reaches ~2.6; the body already states it: "neither does it show that detailed feedback has no effect" (credited).
R2 false-pass rate (analysis window, non-stale, human-unacceptable submissions; strict pass = [可不修改] or [通過]; recount_r2.py):
   type-only defect: mode A 23/59 = 39%, mode B 21/87 = 24% -> REBUILDS exactly.
   "6-8% for substantive defects" rebuilds only as ALL non-type-only defects: A 8/138 = 6%, B 12/144 = 8%.
   Inside that pool (reading defined after the data): structural defects (E1/E2/E3/E5) A 2/116 = 2%, B 9/121 = 7%; "name or mixed (no
   structural defect)" A 6/22 = 27%, B 3/23 = 13% (pure name-only: A 5/14 = 36%, B 1/8 = 13%; type + bad name: A 1/8, B 2/15).
   The paper's "substantive" class includes unacceptable names by its own definition (its count: 5 of the 7 remaining mode-A over-counts
   are names) - credited; our split shows the pooled 6-8% is a 2% / 7% structural rate plus a 13-36% name stream.
R4 design counts: 43 students (AB 21, BA 22), 899 submissions in the analysis window (889 non-stale = Table 2's n), 503 distinct
   answers coded, 1,746 submissions in all -> REBUILDS.
SUMMARY (Bones, by hand): every headline figure rebuilds from the released files with our code (R1-R4). Outcomes: R1 ABOVE (+0.400
[+0.266,+0.534] over their own null); R3 system OR ABOVE, re-grader/human CONSISTENT (bounds to ~2.6-2.8, which the body states);
R2 holds, with the comparison class pooling a 2-7% structural rate and a 13-27% name-only rate. Funding: none; public university.
State: RECOUNTED; referee pending (batch with the next two booked rows).
Reading so far: every printed figure rebuilds; the paper prices its own instrument (self-audit log, null batch, re-grader,
human standard). Candidate P3 row as a KNOWN-GOOD contrast (a study that measured its LLM grader against humans), pending referee.
