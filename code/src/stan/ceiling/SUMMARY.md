# STAN ceiling check, summary

Judge: Claude Sonnet, one reader. A person should check the seeded sample in spot_check_20.md (seed 1112).

Unit: one (dev item, F-code) pair where the List marks the code present. 98 dev items, 200 pairs. Test split not touched. Shares use pairs judged (CANNOT_TELL excluded from both) with Wilson 95 percent intervals.

| Code | Pairs | IN_ABSTRACT | PARTLY | NOT_IN_ABSTRACT | CANNOT_TELL | IN share [95%] | IN+PARTLY share [95%] |
|---|---|---|---|---|---|---|---|
| F1 | 24 | 0 | 6 | 16 | 2 | 0.0 [0.0, 0.149] | 0.273 [0.132, 0.482] |
| F2 | 35 | 2 | 13 | 17 | 3 | 0.062 [0.017, 0.201] | 0.469 [0.309, 0.636] |
| F3 | 22 | 7 | 3 | 9 | 3 | 0.368 [0.191, 0.59] | 0.526 [0.317, 0.727] |
| F4 | 64 | 0 | 0 | 64 | 0 | 0.0 [0, 0.057] | 0.0 [0, 0.057] |
| F5 | 18 | 0 | 2 | 15 | 1 | 0.0 [0, 0.184] | 0.118 [0.033, 0.343] |
| F6 | 29 | 0 | 7 | 22 | 0 | 0.0 [0, 0.117] | 0.241 [0.122, 0.421] |
| F7 | 8 | 0 | 2 | 6 | 0 | 0.0 [0, 0.324] | 0.25 [0.071, 0.591] |
| Pooled | 200 | 9 | 33 | 149 | 9 | 0.047 [0.025, 0.087] | 0.22 [0.167, 0.284] |
| Pooled without F4 | 136 | 9 | 33 | 85 | 9 | 0.071 [0.038, 0.129] | 0.331 [0.255, 0.416] |

## Reading (rule fixed in PLAN.md before judging)

The pooled IN_ABSTRACT share is 9 of 191 judged pairs, 0.047, Wilson 95 percent interval 0.025 to 0.087. The upper end is below 0.25, so the pre-registered rule says the abstract is the ceiling and v2 on full text is justified. The result holds with F4 removed (0.071, upper end 0.129). The only code with a sizable abstract share is F3 (7 of 19, 0.37, interval 0.19 to 0.59), which is too few pairs to call and is the one place where an abstract-only reader can find the evidence. F4 is 64 of 200 pairs and is an absence code that an abstract cannot show, so no reader of abstracts can reach it. Counting PARTLY, the share rises to 0.22 (0.17 to 0.28) and most of that is an abstract that carries the claim wording while the evidence sits in a table, figure, file or rerun. PARTLY means the abstract names what to check and does not hold what the recount used.

## Limits

One judge, one reader, and the abstract-vs-note call is a judgment, so a person should check the sample. This test asks whether the evidence is in the abstract. It does not say a small model on full text can apply the codes. It removes the abstract-only ceiling as the explanation for STAN v1 abstaining and leaves the rival (small models cannot apply the codes) untested. Nine pairs are CANNOT_TELL because the List note is too thin (for example a note that reads only "large sigma claim"). The Q-code pairs on the List were not judged.
