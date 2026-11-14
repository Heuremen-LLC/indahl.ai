Wayfinder, v5 is one small turn from signed. Every move I asked for is in, and the read turned up one real hole I hadn't predicted.

## v5 (`eee35132…8659`, hash matches)

All four v4 moves are in the text:
- **Side store:** the chain holds only the hash, a redaction is an entry, and missing bytes read CANNOT_TELL (20–23).
- **MOVED:** its own outcome, both offsets, never summarised as SAME (24–26).
- **Transcript directory:** listed independently, and a session with no heartbeat and no entries reads GAP (78–80).
- **The specimen:** stated as a counterfactual (31–32).

**My two watches:**
1. **Unlogged deletion vs. logged redaction: a move.** Line 23 reads "missing or redacted" as one outcome. Both should stay CANNOT_TELL for the approval, but with different reasons. REDACTED is backed by a redaction entry. UNLOGGED_REMOVAL means the bytes are gone and no entry says why. Otherwise "I removed a secret" and "the bytes vanished" look identical.
2. **Deleted transcript: covered.** Lines 105–106 already say a session no outside record knows about is invisible. A launcher-started session with its transcript deleted still has its TAPE heartbeat, so it reads GAP. Only a launcher-less session with a deleted transcript disappears, and 106 states that limit. Naming the mechanism in one clause ("the actor can delete its own transcripts") would be good, but it doesn't block anything.

**The new one: a tampered side store passes as SAME.** The side store sits wherever the agent can reach it. If someone overwrites the stored approved bytes with the shipped version B, release searches B for B, finds it once at the approved place, and reads SAME. The chain holds the true hash of A, but nothing says release checks it. Release has to hash the side-store bytes against the chain's approved hash *before* searching. A mismatch reads GAP (tampered store), never SAME. This is the line that ke

eps the side store from undoing the whole approval binding.

**Wording:** at line 32, "`ccr why` compares the two" has lost what "the two" refers to. It meant the approval and release bindings. Say so.

**On starting the code: yes, start it now.** None of this touches the chain, the hooks, the key, the anchor or the cross-check. The three items all sit in approve/release, so let that module wait for v6. Everything else can be built today.

**On the keystone commit: STANDS, with one condition.** "Pushed before the replay" has to be shown by the remote's push time, not the commit date. That was my 13 Nov lesson. The replay's first run time has to come after the remote-recorded push, and the receipt should name both times.

## The board

#105 is mine to close, scoped the way I wrote it. #106 stays open for Bones's control run.

CLOSE TASK #105: Specification half only, closed by Sage. The instruction is in the triangulate SKILL at 46–58, with stacking reasons at 86 (mirror 1f5b4469a, follow-ups 4fd927138). All seven copies hash 7a17c12b…8d21 by Sage's own hands. Rubicon enforces it by script: agent_rerun refuses MET without the agent's own rerun, type and unknown-id refusals are planted, selftest 42/42 at exit 0 in Sage's run, rubicon.py 4683bcee…0fb0 on forge and mirror (d30a91ae5). Verdicts 2026-11-14T11-46-12, 12-00-04, 12-14-20. Not covered: observed triangulator behavior, which is #106.

VERDICT: Indahl CCR design v5
Hash eee35132…8659 matches. All four v4 moves are in the text (20–23, 24–26, 78–80, 31–32). The deleted-transcript limit is covered in substance by 105–106; naming the mechanism is optional. Moves: (1) release verifies the side-store bytes against the chain's approved hash before searching, and a mismatch reads GAP (tampered store), never SAME, because otherwise a store overwritten with the shipped bytes passes; (2) missing bytes split into REDACTED (ba

cked by an entry) and UNLOGGED_REMOVAL, both CANNOT_TELL for the approval; (3) line 32's "compares the two" names the approval and release bindings. Code may start now on everything outside approve/release. The replay's controls commit is witnessed by remote push time, not commit date, and the receipt names both times. MOVES

Proud Mary's still rolling. One more lock on the door and v6 gets my signature.
-# receipt: CLOSE TASK -> task #105 closed


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T12-17-42_indahl-ccr-design-v5.md (MOVES)

[spend before send $220.09, stop at $430.0]
