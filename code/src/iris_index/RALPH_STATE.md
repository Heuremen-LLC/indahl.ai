# Ralph state (tick = item done, with its commit)
- [x] L1 Pub #2 full draft (pub2/paper/main.pdf)
- [x] L2 Pub #1 recent citations (launch/L2_CITES.md; candidate PDF, ships after L3)
- [~] L3 triple pass: physics applied (candidate PDF), Pub #2 applied + round-2 referee out
- [ ] L4 endorsement drafts
- [ ] L5 launch checklist
- [x] 1 referee before booking (book_gate.py + pre-commit hook; pub2/WITHDRAWALS.md)
- [x] 2 Pub #1 batch refereed and SHIPPED on his Disco (heuremen.org 2510d9f, ledger 91635bc; live verified)
- [x] 3 blind sheet (blind/sheet.html; key in its own commit; waits on Wayfinder)
- [x] 4 frontier columns (matrix/frontier/RESULT.md; P2-20, P2-21)
- [x] 5 Matrix v2 plan (PLAN_v2.md; harness + synth for v2 still to build before running)
- [x] 6 neutral name ("Failure-Mode Matrix" on anything outgoing; rules in PUB2_IRIS.md)
- [ ] 7 QIA lane (after Monday)

## 25 Oct ~09:25 — passes
- Pub #2: pass 3 FINAL done (POPE 3.16 = difference of rounded F1s, 3.15 unrounded; tally holds). Commit 38df943. No more passes.
- Physics: pass-2's 9 items applied (+ 18-of-25 and 10-of-39 recounted by hand from the record, ledger rows added, drift 0); short abstract 1,915 chars; Smith + Blais drafts fixed. Pass 3 (final) referee running.
- ZENODO (his word 25 Oct): ONE upload for the LLM paper, only after everything is final. Physics: one more version at most, after physics pass 3.
- ~09:30 Physics pass 3 FINAL done: one fix (floor list now includes fez 3 couplings, in paper + staged in heuremen.org index/technical-summary). PDF main.pdf.final-20261025. Ledger drift 0 (ceaee85+). Both papers DONE with passes. Ship (heuremen.org via ship.sh) + Zenodo wait on his launch word; physics = last Zenodo version; LLM = ONE upload after Matrix v1 last model + referee.
- ~10:05 Matrix v1: all ten scored (deepseek known-good failed -> its order/batch cells CANNOT_TELL). Referee on the six unrefereed models running.
  Matrix v2 running on our seat (drive_v2.sh -> matrix/drive_v2.log). LLM Zenodo bundle: rebuild ONCE after the v1 referee; v2 stays out unless done before he uploads.
  OY: C-001 MIT inventory + hand counts; Oct OSF sweep; C-002..C-007 carded; mj4bu fully recounted (R1-R4 rebuild); The Wall row 0 = us.
  Ivy sweep agent out.
- ~10:30 Matrix v1 referee v1b: 6 real errors, all fixed (addendum 3), no outcome flipped; old values kept. LLM ZENODO BUNDLE FINAL:
  launch/zenodo_iris/iris_recount_bundle.zip (210 files, no v2) -> ready for his ONE upload. v2 running (parse fix applied before output read).
  OY: Ivy sweep in (oy_index/SWEEP_ivies.md): 39 docs; Cornell surveys with data CSVs + instruments; Harvard physics AI-tutor RCT data on GitHub.
  Next: card the Ivies on The Wall (S0-S7), recount Cornell + Harvard data.
- ~13:10 Matrix v2 partial: phi4-mini positive control 1.00, order flips (reverse, rotate) ABOVE with top-letter share 0.32 -> order
  sensitivity separated from letter fallback (the v1 limit). gemma3 pc 0.72 (CANNOT_TELL order cells); qwen3 truncated 191/200. mistral running.
  OY: 47 Wall rows written (6 batches), 40+ receipt-checked; S0 summary WALL_S0.md (1 policy-level MEASURED candidate: CMU). Recounts:
  mj4bu, harvard_kestin, cornell_surveys, umn_c008, bastani, cmu_oppenheimer (referee out on the last two + S0).
- ~15:00 OY: 67 Wall rows (batches 1-8 + MIT/Cornell/USC/Harvard by hand), S0 by script: MEASURED-POLICY 0 found; 7 measured pilots read.
  Recounts: mj4bu, harvard_kestin, cornell_surveys, umn_c008, bastani, cmu_oppenheimer, uchicago_ji, berkeley_pardos (+ umd plan check).
  PUB3 rows P3-01..P3-14 (P3-12..14 at referee). Batches 9-10 running; 11 ready. Matrix v2: 6 of 10 models (granite running).
- ~16:30 OY: 94 Wall rows; S0 by script: MEASURED-POLICY 1 (unm detector audit, verified live; referee out), PLANNED 30, USAGE 53, NONE 8,
  TRIAL w/o numbers 2. S3: 0 institutional microdata. S4 hand recounts held (mit, brown, yale, duke). Self-stated absences verified: auburn,
  lsu, ncsu, vt. PUB3 P3-01..P3-16. Batches 11-12 running; 13-14 ready. Matrix v2: deepseek running (last).
- 25 Oct ~12:25: Penn S4 hand recount (SCSEP 0 of 7-8 confirmed). Referee on UNM/P3-15/S0 applied: temple -> MEASURED-POLICY (2 found: unm, temple; Temple numbers verified live), uniform check redone (bu named), baylor/ttu/unt/msstate/okstate merged, S3 rebuilt by saved rows/extract_s3.py (98 inst: 0 microdata, 31 agg/instrument, 67 none). Tally 99 incl row 0: MP 2, NONE 9, PLANNED 30, TRIAL 2, USAGE 56. Batches 11+12 merged; 13 + 14 in flight; 15 (R1 rest) + 16 (liberal arts) scripted. Matrix v2: deepseek running (mcq4_A_copy).
- 25 Oct ~13:30: batches 13+14 merged (115 incl row 0: MP 2, NONE 12, PLANNED 36, TRIAL 2, USAGE 63); gatech Socratic Mind read -> MEASURED-PILOT; rochester pilot held; wsu ruled USAGE; case 8 submissions verified; S3 114 (0 microdata of use/outcomes, 38 agg, 76 none); P3-15 narrowed. 15 + 16 in flight; 17 + 18 (liberal arts) scripted.
- 25 Oct ~13:55 HOLD by his word: 92% usage, ~2 days to reset. No new agents/batches; 17 + 18 finish, then hand work only. Batches 15+16 merged (131 incl row 0). P3-17 chatbot-as-source: msstate, montanastate, tulane. gwu SR 24/8 arithmetic verified.
- 25 Oct ~14:00: Ralph loop PAUSED (9 state copies moved to ~/.Trash/ralph_paused_20261025/) to stop idle re-prompts burning usage under the HOLD. Restore those files to restart. Batch 17/18 + sweep notifications still wake Bones to merge.
- 25 Oct: Matrix v2 complete (10 models). deepseek: known-good FAIL, 108/200 truncated -> CANNOT_TELL all order cells. Referee of v2 owed (no agents under HOLD; by hand or after reset). v2 held out of Pub #2.
- 25 Oct ~14:45: ALL batches merged (1-18). Wall: 147 incl row 0 (MP 2, NONE 21, PLANNED 47, TRIAL 3, USAGE 74). P3-17 (ii) + wesleyan (Claude quoted to define an LLM). No agents running. Remaining hand work: search pass (after reset), receipts recheck (american, kenyon, cmc, macalester, hmc, fordham, williams live), referee P3-15/16/17 (after reset), S4 recounts.
- 25 Oct ~16:00: his order: do the small-private That School pass BY HAND, no agents, school to school; log in oy_index/THAT_SCHOOL_PASS.md; list of schools in that file's queue.
- 25 Oct (afternoon) DECISION (his word): Pub #3 is NO LONGER an arXiv paper (two submissions a month: physics + Pub #2 take them; he won't use the other ed-arXiv site). Instead: "Matrix data pages" for all THREE divisions (Quantum Hardware/QIA, Language Models/IRIS, Learning Research/OY), each a straight-up WORKING DRAFT of preliminary findings that says so, with limits stated (US institutions only, partial reads). Order: OY first (template), then IRIS, then QIA (needs its own review). Conditions (mine, accepted): quotes+links only for named schools (no adjectives), "as of" date, unread cells visible, alphabetical/no scores/no ranking, credit Fisher/Elon up front, public rule list; ledger entry BEFORE page, ship via ledger/ship.sh + check_ledger.py; the 4 newest items (P3-15 data release, P3-16 detector audits, P3-17 chatbot-as-source, P3-18 Fisher) go on LAST after an outside referee pass (needs fresh usage). Pages likely live at indahl.ai (papers stay heuremen.org/Zenodo) - his call, not decided. Switch: he moves me from Sonnet back to Opus next turn. NO AGENTS (token hungry) - everything by hand/local scripts until he lifts it. Crawler (smallpass pass 2) was still running; read smallpass/hits.jsonl + coverage.json when done. Also see ~/bones-forge/DISCO_CHECK_20261025.md and oy_index/pub3/paper/PUB3_FORMAT_PROOF.pdf (layout proof only).
- 25 Oct (late) HIS WORD: NO SHIP. "repeat No Ship, just final stages of production." All three guns fire at once at LAUNCH: opening bell 10/26/26, Heuremen Standard Time; he will show how. Until then: build, stage, commit locally; never run ship.sh, never push, never deploy, never upload. Faults/Guards open items: DROP the "four of five" referee claim and the 0.0005 width.
- 25 Oct: Pub #1 FULLY BUILT for launch (paper PDF, Faults/Guards with drops, arXiv tar, Zenodo v5), all local, committed, not deployed. See launch/LAUNCH.md.
