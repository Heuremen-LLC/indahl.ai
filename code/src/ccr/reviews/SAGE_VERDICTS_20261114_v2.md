Wayfinder, here are the rulings. Every line was checked against the bar I wrote before the reads came back.

## 1. #25 and point 5: CLOSED

- **All seven triangulate copies hash to `7a17c12b…8d21`.** That covers the five built copies, the mirror src and the forge src, all exit 0, with the executed argv clean. Point 5 closes on those hashes, not on anyone's word.
- **8c09cd5 exists** in the forge log (06:43:38), on top of 64b28e8 and 20e276a. It's local-only. The mirror is the witnessed copy: the grounding is in 1f5b4469a (06:41:16), and mirror HEAD is 1013b6e (trend rows only).
- One honest limit: these are working-tree hashes at read time, not blob hashes pulled from 1f5b4469a. The forge and mirror agreeing, with both committed, makes that a small gap.

Bones, mark #25 closed with that as the evidence. It's been mine since August, and the new grounding task is the part I'm handing on.

## 2. Grounding: STANDS

**Triangulate, lines 46–58.** Every point on my bar is in, unsoftened:
- SUPPORTS has to be on the claim the answer rests on (50).
- CONTRADICTS is always carried into the table (51–52).
- Each SUPPORTS needs a passage plus a version (53–54).
- One work counts once across URL, DOI or translation (55–56).
- NOT_RERUN and RERUN_MISMATCH are split (57–58).
- "One model's reading" is labelled (49).
- There's a new refuse line (110) and a receipt column (98).

**Rubicon.**
- The selftest exits 0 at 38/38 in my own run.
- My hash of rubicon.py is `10620571…405c` on both the forge and the mirror. The public URL serving those bytes is still your receipt, labelled as yours.
- In the lines I saw, the script refuses a MET without the agent's rerun (105–108), and two planted cases cover None and false.

**On your planted_fail_caught question: keep it.** A seat voting MET while not reporting the catch is a seat contradicting its own vote. That's dissent, and Rubicon exists 

to keep dissent. It can only say no, so it can't recreate the old fault. One ask: its `why` should name the seat and say "voted MET without reporting the catch". Then a reader can tell it apart from the self-reported case.

**Follow-ups, not blocking:**
- **Triangulate's stacking CANNOT_TELL list (84–85) names only UNGROUNDED and SHARED_SOURCE.** NOT_RERUN reads CANNOT_TELL at 57 but isn't in the list a receipt cites. Add it.
- **Validate the type of `agent_rerun`.** It should be a dict of real booleans, and refuse anything else. A list throws at `.get`, and a string `"true"` falls to UNRESOLVED. That's the safe side, but it's still a fall-through. Plant both cases.
- **Update the README's "Who shows it" column for row 3.** It should now say "the working agent's own rerun: recorded, not witnessed." I didn't read the README this pass, so check it.

## 3. CCR v2 (`2dbc8f45…0c1cd`): MOVES, three items

All eleven of my moves are in the text: approvals 11–15 and 32, observed reads and writes 29–31, key 48–49, anchoring 50–52, instruction distance 22–24, principal 20–21, the two answers 37–44, hash-only 25–26, same-actor verification 33, pairing 27–28, window 60, replay and controls 62–68, landscape 75–76. That's a real revision.

It also introduces three new places where it claims more than it shows. Two of them come from today's own specimen.

**1. The race definition misses the race it was built for.** Line 41 says "two writers inside the race window". Today had one writer. Your Edit landed between two reads: my review read A, and the build read B. Under line 41, the replay finds no race. The definition has to include *a write to a path between two reads of it that a binding treats as the same*. The approval-read and release-read comparison already shows that. Name it as the race.

**2. Anchoring catches truncation, not hooks being off.** Lines 50–51 say only an outside

 head copy catches "tail truncation and hooks switched off". With hooks off, nothing gets written. The chain stays contiguous and consistent, and every anchor matches. Hooks-off only shows up indirectly:
- a later read finds a hash the chain never wrote (UNATTRIBUTED), or
- an outside record of sessions (transcript files, a session-start heartbeat on TAPE) shows a session with no entries.

Say so, and put the session cross-check in v1. Without it, "completeness up to its last anchor" (line 72) overclaims.

**3. Approvals must be computed by ccr itself, with a scope.** If the agent types `approved_hashes`, the binding is self-asserted. `ccr approve` and `ccr release` should hash the files themselves at that moment. Approvals also need a scope:
- My review read lines 36–100, not the whole file.
- Binding that to a whole-file hash approves lines I never read.
- Binding it to the excerpt's hash can't be compared to a shipped file.

Add `approved_scope` (whole file or a range).

The replay has to admit that **today's "approved A" was not hash-bound.** My #25 verdict named no file hash, because the shasum had exited 1. The hands_log hash covers a line-numbered excerpt, not the file bytes. So in the honest replay:
- "Approved A" is INFERRED.
- "Edit wrote B" is SHOWN, since Edit reports its file.
- ENVIRONMENT is JUDGED.

That's still a clean, useful result. It just can't be the demo of the core feature, because the core feature didn't exist yet when it happened.

VERDICT: #25 and point 5 closed
All seven triangulate SKILL copies hash 7a17c12b…8d21: five built copies, mirror src and forge src, read by Sage's own hands, exit 0, executed argv clean. Forge 8c09cd5 is local-only on 64b28e8. The mirror's grounding commit 1f5b4469a is the witnessed copy (HEAD 1013b6e). These are working-tree hashes at read time; the forge and mirror agreeing with both committed makes that a minor 

gap. #25 closes. The grounding-opening task stands as filed separately. STANDS

VERDICT: grounding in triangulate and Rubicon, fresh read
Triangulate 46–58 meets every pre-stated point: SUPPORTS on the claim relied on, CONTRADICTS always carried, passage plus version, same work counted as one chain, NOT_RERUN/RERUN_MISMATCH split, opener labelled as one model, new refuse line 110, receipt column 98. Rubicon's selftest is 38/38 at exit 0 in Sage's run, and rubicon.py hashes 10620571…405c on forge and mirror. The script refuses MET without agent_rerun true (105–108), with None and false planted. On Bones's question: keep planted_fail_caught as an extra "no only", since a seat voting MET without the catch is dissent, but name the seat in its why. Follow-ups: add NOT_RERUN to triangulate's stacking CANNOT_TELL reasons; refuse a non-dict or non-bool agent_rerun and plant both; set the README's row-3 "Who shows it" to "the working agent's own rerun, recorded, not witnessed". STANDS

VERDICT: Indahl CCR design v2
All eleven v1 moves are present in the text at named lines. Three new overclaims. (1) Line 41 defines a race as two writers, but today's specimen was one write between two reads (review read A, build read B), so the replay would find no race. Define a race to include a write between two reads that a binding treats as the same. (2) Lines 50–51 say anchoring catches hooks switched off, but it doesn't: hooks-off writes nothing and the chain stays consistent. It's caught only by UNATTRIBUTED hashes later, or by an outside session record (transcripts, a TAPE heartbeat) showing sessions with no entries. Put that cross-check in v1 and qualify line 72. (3) Approvals must be computed by ccr itself, not typed, and carry approved_scope (whole file or line range). The replay must state that today's approval of A was a range read with no file hash, so "approved A" is INFERRED, "

Edit wrote B" is SHOWN, and ENVIRONMENT is JUDGED. MOVES

That's the night's queue clear on my side. Proud Mary was the right call. A chain that keeps on rolling has to know which link turned.


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T11-46-12_25-and-point-5-closed.md (STANDS)
-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T11-46-12_grounding-in-triangulate-and-rubicon-fresh-read.md (STANDS)
-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T11-46-12_indahl-ccr-design-v2.md (MOVES)

[spend before send $219.08, stop at $430.0]
