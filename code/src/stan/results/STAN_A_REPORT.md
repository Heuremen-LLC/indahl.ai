# STAN A, full text: stop and report (12 Nov 2026)

Sage's verdict, 12 Nov 20:15 (sage_referee 2026-11-12T20-15-53): the teacher route is closed, and the direct-training step is not cleared. MOVES.

## What was tested
Three local teachers (Llama 3.1 8B, Mistral 7B, Gemma 3 4B), one prompt family, BM25 top 6 chunks, pypdf text, open-access papers
only, on gold dev (92 papers; codes F1, F2, F6 and F3; 1,104 calls). The results hold for this setup only. They do not show that
local 4 to 8B models cannot sort. A student trained on human labels is a different question from a teacher prompted cold.

## The ceiling comes first
Retrieval caps any text model on this input, whoever labels the data. Of 196 recount-flagged pairs, 52 (27 percent) had their
evidence in the top 6 chunks. 45 (23 percent) cite evidence outside the paper's text (ceiling_ft/, DEVIATIONS.md).

## Teachers
0 of 12 teacher-code cells pass the keep line committed in PLAN_A_v2 section 6 before the full read.
- Gemma and Mistral call PRESENT on 89 to 100 percent of unflagged pairs. They read the definition back, and many of their
  quotes are the code's own text.
- Llama commits on under 10 percent of calls, so its cells fail on coverage.
- Mistral F1, [-0.006, 0.423], is CANNOT_TELL, not shown to be bad. The route is closed because the rule says so.
Numbers: teachers_ft/SUMMARY.md and teachers_ft/summary.json.

## Lexical baselines
- The registered rule (any PRESENT-line cue in the top 6) is the always-PRESENT constant in practice, and is reported under that name.
- A thresholded cue-count rule was added on Sage's word and fixed before any fresh draw (lexical/thresholded_rule.json): PRESENT
  when the cue count is above the dev median for that code. The threshold uses the count distribution only, not the flags, but the
  cues were chosen after dev was seen, so it is labelled dev-informed.
- On dev, PRESENT on flagged minus PRESENT on unflagged, with Newcombe 95 percent intervals:

| Code | Difference | Interval | Reads |
|---|---|---|---|
| F2 | 0.225 | [0.015, 0.408] | above zero |
| F1 | 0.169 | [-0.061, 0.368] | CANNOT_TELL |
| F3 | 0.219 | [-0.015, 0.424] | CANNOT_TELL |
| F6 | -0.044 | [-0.247, 0.169] | CANNOT_TELL |

- F2 is one of four codes tested. Corrected for the four, its interval reaches zero.
- This is not a like-for-like comparison with the teachers. The word-count threshold is dev-informed and needs no quote, while the
  teacher line required grounding. On raw PRESENT rates, without grounding, the teachers also did not separate on F2 (Gemma 35/35 against
  57/57, Mistral 35/35 against 56/57, Llama 2/35 against 2/57). It stands as the cheap sorter STAN has to beat on fresh recounts.

## The finding about the standard (this does not depend on STAN)
Faults and Guards 2.0 specifies tests that the paper body often cannot show:
- 45 flagged pairs cite evidence outside the PDF.
- 44 of 63 F4 recount notes name nothing to search for, because they are pure absence.
- F4 to F7 cannot be shown from the paper body (QUOTABLE_FT.md).

Two actions for 2.1:
- A scope-of-search requirement for absence calls (say what was searched).
- A released-artifact check, kept separate from the paper check.

## Contamination wall
The matcher's Zenodo-version recall was under-read. As reported it was 54 of 61. Counting only twins whose gold text is the right
version, it is 54 of 55: 6 of the 7 misses come from version drift on the gold side, where OpenAlex returned another version of a
Zenodo concept DOI (results/twins_hand_read.md). The wall's claim is "no known twin in the pool", not "no twin".

## Next
The recount route is a new plan with a cost gate. 150 recounts cannot both train and test, so direct training needs about 300 or
more, or it is descriptive only. The open question for Wayfinder and Bones: are 300 or more human recounts worth making for their
own sake, as better gold for the standard? If yes, STAN is a side use of them. If no, STAN stops here. No new rule is fixed after
fresh recounts are seen.
