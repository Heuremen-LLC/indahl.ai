# v2 requirements, Sage verdict 12 Nov 2026 18:25 (forensics accepted, v2 silver plan not cleared, MOVES)

Source: Armature sage_referee/2026-11-12T18-25-47_stan-v1-forensics-accepted-v2-silver-plan-not-cleared.md

- Rule: agreement counts only on grounded calls. Unquoted calls go to neither silver nor CT. Keep native CT as CT, drop the rest or send it to the review queue.
- Only 10 of the 114 CT rows were true all-native abstentions. After repair, CT supply may nearly vanish, and STAN collapses the other way. Publish the post-repair class mix per code before any training.

**Break 2: "CT by rule" for F4 PRESENT and F5/F6 ABSENT is a hard-coded label, not a model skill.**
- The model will learn the rule per code. The per-code plurality baseline then equals the rule, and the gate is passed trivially. Name the per-code constant predictor, not only the pooled one.
- Which codes are quotable from an abstract 

is currently chosen after seeing the spot check. That is a degree of freedom. Derive it from the standard's own text and freeze it, or record that it was chosen post hoc from v1.
- This may be a finding about the standard, not the pipeline. If ABSENT cannot be shown without reading the whole document, 2.0 needs a scope-of-search requirement for absence calls. Say so to the standard's owners.

**Break 3: the spot check is not a result yet.**
- A blind same-family judge saying yes on 0 of 40 is itself suspect. Before anyone cites it, run it on a known-supported quote as a positive control, and inspect its prompt.
- Wayfinder's 8 of 16 is the only human signal. Give his sample's seed and code mix.
- Report yes-rates only on codes where a quote could show the label. "Absence can't be quoted" is a hypothesis until that split exists.

**Break 4: the validation set can't pick a checkpoint.** It is 15 rows over 7 papers and chose the checkpoint. Use a larger paper-level split and a pre-registered stopping step.

**Break 5: the cap.**
- Cap by status per code, and publish counts before and after.
- F3 is at 10 rows and F7 at 21, so a real cap will leave them tiny. Decide in advance whether they are dropped from training or reported as untested.
- Rows cut by the old cap (F3 CT 24, F7 NA 27) were the dominant class, so the new cap will cut similar amounts. Say so.

**Break 6: quote-first order needs a gate, not a hope.**
- Before anything touches gold, run the same teacher-forced status-token diagnostic on a repaired pilot. P(CT) must vary by true class on a held-out silver slice.
- A model that fails this does not move on to gold, however good the silver beat-the-constant numbers look.
- Pick one output order and pre-register it. Trying both is a tuning knob.

**Still owed from earlier:** marking of the 20 ceiling rows, a hand check of the 7 missed twins, and the decided-items

 split and per-code recall sealed before v2.

VERDICT: STAN v1 forensics accepted; v2 silver plan not cleared
The v1 collapse is explained by quote-rule conversion, a cap that never bit, and status-before-quote decoding. "Not kept" stands, with the base's CT labelled as the rule's. The v2 repair must count only grounded calls for agreement, publish the post-repair class mix per code, freeze the quotable-code list from the standard's text, validate the spot-check judge with a positive control, enlarge the validation split, and gate on a held-out status-token diagnostic before any gold read. MOVES

#25 stays claimed.





# Sage on PLAN_A, 12 Nov 2026 18:43 (not cleared to run, MOVES)
The F2 hand read was the right first move, and it kills the idea that agreeing teachers produce valid labels. The A plan inherits the same teachers, now on longer and noisier input, so it MOVES. Eight breaks.

**Break 1: there is no ceiling check on full text.** The abstract plan died on a ceiling (9 of 191), and the A plan skips the equivalent step.
- Before any teacher call, measure on gold dev how often the recount's evidence is in the top-6 retrieved chunks, per code.
- Set the pass line now, before looking.
- "Retrieval checked on 5 dev papers by hand" is too small, and as written it sits after the cue lists are frozen, so it can turn into tuning.
- Make it a pre-registered measurement over all 93 dev papers. If retrieval fails the line, it is reported as the ceiling and BM25 is not quietly swapped out.

**Break 2: "expected" cells are an outcome loaded in the plan.**
- The plan says F1, F2, F3 and F6 are quotable both ways. That list was written after v1 and after the spot check.
- ABSENT from a retrieved top-6 is the hard part. Six chunks without the thing do not show it is absent from the paper.
- Delete the expected line, or label it as a post hoc guess from v1. Derive the cells from the standard's text alone.
- Default ABSENT to not quotable unless the Test itself names a place where the absence is visible.

**Break 3: the hand gate is thin, and the same reader runs it.**
- 12 rows per cell with a pass at 8 or more has a Wilson lower bound near 0.39 at 8 of 12. It cannot tell a 50% cell from an 80% cell.
- Bones wrote the plan, reads the gate, and recounts the fresh gold. The earlier non-blind judge control already showed why that is a problem.
- Use a second reader on the gate, Wayfinder or a blind pass with a saved prompt and a positive control someone else built.
- Quote-supports-label also doesn't catch a retrieved quote that is contradicted by an unretr

ieved passage. State that limit.
- Report how many cells survive. If the answer is two, that is the finding.

**Break 4: the keep rule can't be passed or failed honestly at n=40.**
- Per-cell paired bootstrap on about 40 papers means single digits per cell.
- Run a power calculation now, with the minimum committed count per cell, and say which cells are untestable.
- Compare on committed calls and report coverage, since a model committing on 3 items can beat a constant.
- Define the lexical baseline exactly now: which cues, which chunks, what counts as present.
- The old gold could not separate ABSENT from "not flagged". Fresh recounts must record explicit ABSENT, or ABSENT cells stay unscored on gold.

**Break 5: you dropped the silver gate.**
- The plan keeps only the P(status)-varies diagnostic. Add the gate back: STAN must beat the plurality, always-PRESENT and always-CT constants on held-out silver, per code.
- With quote-first order, specify whether the status-token diagnostic teacher-forces the model's own quote or uses free decode. The v1 failure was status-first, and a diagnostic aimed at the wrong order proves nothing.
- "Stopping step fixed at the fold-mean minimum of a pre-run schedule" is still selection. Say that the pre-run folds are not the diagnostic folds.

**Break 6: context and cost.** v1 trained at 4096 tokens. An 8,192-token input on a 1.7B LoRA changes memory and cost, and it makes long-context behaviour another variable. Say whether training truncates, and what that does to the quote check. The teachers' behaviour at 8k is also unmeasured. Re-baseline each teacher on gold dev with full-text input, with the quote-conversion flag separate from the status, before they label the pool.

**Break 7: extraction.**
- pypdf with no OCR scrambles columns and tables, and F4 and F6 live in tables.
- Report characters extracted per paper and the share of pap

ers with obviously broken text, per code.
- Report who the 12 missing are and whether open-access coverage skews by field, so the claim reads "open-access slice only".
- Record the arXiv version against the version the recount read.

**Break 8: ordering and witness.**
- Commit the plan hash before the fresh 40 are drawn, and derive the draw seed from it.
- Label the ordering self-witnessed, as agreed.
- Keep QUOTABLE_FT, the plan and the addenda under separate hashes.

**Still owed:** the 20 ceiling rows marked by a person, the 7 twins read by hand, and the per-code decided-items split sealed.

VERDICT: STAN A full-text plan, not cleared to run
Add a full-text retrieval ceiling with a pre-registered line, derive the cells from the standard rather than from v1, use a second blind reader for the gate, run a power calculation for the fresh 40 with explicit ABSENT recorded, restore the silver constant-predictor gate, and fix the diagnostic's decode order. Nothing here is a reason to stop, but several of these are knobs as written. MOVES

#25 stays claimed.





## Status 12 Nov 2026 ~20:00 (Bones)
- Teacher full-text re-baseline on dev running: Mistral on Armature (outputs.jsonl, ~24 s per call, ~2.5 h), Llama and Gemma on the Mac in parallel (the Mac seat Ollama on 127.0.0.1:11500 (launchd com.heuremen.ollama-seat11500), same weight blobs as Armature checked by digest 667b0c1932bc and aeda25e63ebd; outputs_mac_llama.jsonl, outputs_mac_gemma.jsonl, ~1 h). When all done: cat teachers_ft/outputs_mac_*.jsonl >> teachers_ft/outputs.jsonl, then python3 teachers_ft/score_ft.py. Carrier: Mac Metal vs Armature CUDA, recorded per row in host.
- Declared: ceiling_ft/DEVIATIONS.md. Power: 40 fresh recounts give about 9 to 13 flagged per code (flag rates on gold test F1 0.23, F2 0.34, F6 0.29); a keep test needs on the order of 150 or more fresh recounts. Recounts are the bottleneck, not compute.
- Owed: 2 ceiling rows for Wayfinder (blind pass agreed 18 of 20 with the judge; B-01 and one other ct), 7 twins hand read, decided-items split sealed.

## Status 12 Nov 2026 ~15:00 (Bones)
- 7 twins read by hand: results/twins_hand_read.md. All 7 are real twins and none reached the pool or slices. 6 of the 7 misses come from gold-side OpenAlex version drift (gold text was another version, in one case another paper), so the matcher's Zenodo recall is under-read. 1 is a true miss (08c4a2608cbe, retitled and rewritten, no gold authors). Version drift across gold: 5 items (4 dev, 1 test). The full-text lane uses the linked record's own PDF.
- Decided-items split sealed per code: results/decided_split.json, sha256 in results/decided_split.sha256. Built only from ceiling_ft/judgments.jsonl (committed 834a3f7 at 13:52, before the teacher run started at 13:55). Tested: F1 19, F2 22, F3 20, F6 15. Untested (<10 decided): F4 7, F5 4, F7 4. Sealed at 15:00, before the full teacher scores were read. A partial dry run of score_ft.py on about a quarter of the rows was seen at 14:25 to test the script. The split's content does not depend on it.

## Status 12 Nov 2026 ~15:15 (Bones): 20 ceiling rows done
- The 2 rows where the reads differed went to Wayfinder (review_queue/marks_page/wayfinder_ceiling_marks.json).
  - B-01 (F5): judge right, PARTLY. Noted as a two-step: the claim is visible in the abstract, but the recomputation needs
    the AUC values, which are not.
  - B-10 (F6): unclear, kept as CANNOT_TELL.
- Final on the 20 abstract-ceiling rows: judge supported on 19, 1 CANNOT_TELL, 0 judged wrong. The blind pass and the judge
  agreed on 18 of 20.
- Note for the ceiling definition: F5 (and any recompute code) splits into seeing the claim and seeing the inputs. A pair
  where only the claim is visible reads PARTLY, not IN.

## Sage, 12 Nov 2026 20:15: STAN A, teacher route closed; direct-training next step not cleared (MOVES)
Source: sage_referee/2026-11-12T20-15-53_stan-a-teacher-route-closed-direct-training-next-step-not-cl.md
- 150 recounts cannot both train and test. Direct training needs 300 or more, or it is descriptive only. Put that number in any plan.
- Bound the claim to this pipeline: three local models, one prompt family, BM25 top 6, pypdf, open-access only. The retrieval ceiling (52 of 196) goes up front.
- Keep the registered lexical rule under the name always-PRESENT. Add a thresholded cue-count rule, fixed now and labelled dev-informed.
- The finding about the standard belongs to its owners: scope of search for absence calls, and a released-artifact check.
- Twins: state the corrected recall; claim "no known twin".
Done 12 Nov ~16:30 (Bones): results/STAN_A_REPORT.md written; lexical/thresholded_rule.json fixed and run on dev; twins wording corrected.
Open for Wayfinder: are 300 or more human recounts worth making as gold for the standard, even without STAN?

## Decision 12 Nov ~16:45 (Wayfinder's outcome rule, Bones)
No standalone 300-recount study. Every recount done for QIA or SAGAR work records explicit ABSENT and the scope searched
(the 2.1 fixes), so gold for the standard builds up from shipped work. STAN resumes when that pile reaches the count Sage named
(300 or more). Ships now: results/STAN_A_REPORT.md, and the 2.1 proposal (scope of search for absence calls, and a
released-artifact check separate from the paper).
