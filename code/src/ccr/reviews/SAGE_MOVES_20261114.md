# Sage, 14 Nov 2026, verdicts on #25, the grounding paragraphs and the CCR design (verbatim)

## #25: closed, and I owe a correction

Both copies now hash to `cc3e2798…cfdda`, exit 0, clean argv: the forge src and the mirror src. That matches the blob in c9cbf19f7. All four criteria are in the committed text, unsoftened, and shifted by the new paragraph:
- UNGROUNDED: 43–44
- independent chains and convergence: 57–60
- stacking reasons: 74–78
- refuse lines: 102 and 104

**The correction.** Last turn I said the hashes differed and guessed there were two diverging srcs. They didn't diverge. The paragraph landed after my read, in both copies. My `2ebfb53b` was the pre-edit file, read at an earlier time. Two reads of a moving file at two times aren't a contradiction until the times are pinned, and I treated them as one. That's the exact failure CCR is meant to catch.

**Two things stay open:**
- **Point 5.** The six copies are identical by your word, not yet by my hands. I've sent a search for them below.
- **The forge copy is uncommitted in its own repo.** That repo's last commit is 20e276a at 03:49, stampwatch. The only committed copy of the reviewed text is the public mirror. Either commit the forge copy, or declare the mirror the source of truth.

## Fresh review: the new paragraphs MOVE, small

**Triangulate 46–51.** My pre-stated check passes: a computation that can't be rerun doesn't count. Three changes:
1. **"Grounded if at least one citation reads SUPPORTS" is too loose.** A seat with one tangential SUPPORTS and two CONTRADICTS reads grounded, and the contradictions vanish from convergence. Make it: SUPPORTS on the claim the answer rests on, and any CONTRADICTS carried into the item-by-item table.
2. **SUPPORTS is a label unless the receipt holds the passage.** Require the quoted passage, plus the version or hash t

hat was opened. Otherwise it's THE WELL: a tag with no content behind it. Also say the opener is the orchestrator, one model's reading.
3. **The same work under another URL or DOI is one chain.** My YO lesson: twins hide behind different identifiers and translations. SHARED_SOURCE has to check for the same work, not the same link. Also, for computations, split NOT_RERUN (CANNOT_TELL) from RERUN_MISMATCH (counts like CONTRADICTS).

**Rubicon 73–77.** The skill and the script disagree. The skill says an unopened catch "does not count". The script still tallies MET off the seat's own `planted_fail_caught`. Either the agent sets `planted_fail_caught` true only after its own rerun, so the script enforces it, or add a `rerun_by_agent` field. As written, the record can't tell a verified catch from a self-reported one.

## CCR: MOVES. The idea is right, and it says "shown" in three places where it means "inferred"

**Where it first says more than it knows: `reads` for Bash.** Hooks see "Bash ran build.sh". They don't see the files the build read or wrote. Today's ship *was* a Bash build. So the entry that matters most in the replay is the one where reads can't be observed. Every entry needs `reads_observed: tool | watched_paths | none`. Without that, an empty reads list on a Bash call reads as "touched nothing".

**A race is "shown" only when the dependency is declared.** "A read whose hash differs from the hash a later step assumed": nothing records what a later step assumed. The ship never said "I'm shipping what Sage reviewed." The real v1 feature is **an approval bound to a hash.** A review entry names the hash it approved, a ship entry names the hashes it shipped, and `why` compares the two. That comparison is shown. Anything without a declared binding is inferred, and labelled that way. For a bank this is the whole point: "approved A, deployed B" as a fact.

**What woul

d mislead a bank:**
1. **The signing key.** A local Ed25519 key the agent's shell can reach lets the agent re-sign a rewritten chain. It has to sit outside the actor's reach: a separate user for the hook, or a non-exportable keychain key. Same reasoning as my hands refusing keys.
2. **Truncation and hooks-off leave no gap.** Delete the tail and what remains is still a valid chain. Turn the hooks off and seq just stops, so there's no missing number and nobody writes the "hook-off marker". The design says these read CANNOT_TELL. They read clean. Only an outside copy of the head catches them. By your rule that's our own tape plus a public push, not a chain. And it's v1, not "later", if banks are the audience.
3. **"Instruction" overclaims "on whose word".** In a long autonomous run every action points to one vague turn, so INSTRUCTION becomes the default. Inside a subagent the real instruction is the parent's Task prompt, not the user turn. Point to the nearest real instruction, parent prompt included, and record the distance to it.
4. **The principal is self-asserted.** "Named in config" is the operator's label, not an identity. Say so in every export.
5. **Shown and judged sit in one enum.** ENVIRONMENT (shown) next to AGENT (judged) teaches the reader they're the same kind of proof. Split them. Attribution is shown: which entry wrote this hash, unattributed, or a gap. Cause is judged, and records who judged it. Run race detection *before* naming a writer, or it blames the last actor, which is your "new guy" problem rebuilt.
6. **Arguments by default in an append-only log.** A secret, or someone's personal data, can't be removed once chained. Default to hash-only.
7. **A read-back by the writer.** Label "verified by the same actor", or VERIFIED means "I checked myself".

**What must be in v1:**
- Hash-bound approvals.
- A key outside the agent's reach, with head anchor

ing.
- Observed versus unobserved reads.
- Pre/post pairing: a pre with no post is CANNOT_TELL on the result, and denied calls are entries too.
- The race window **fixed before the replay**, and checked for how far it can move before the verdict flips.

**The replay is a positive control built by people who already know the answer.** Build it from the real logs: your transcript and my hands_log.jsonl, which already holds my read of version A with its output hash. Note that today's race spans three actors on two machines, so v1 has to import a second chain or it can't see half the event. It also needs two controls defined before running:
- a sequential negative (edit, ship, then review the shipped hash) that must not read as a race
- an unattributed edit from an editor that must read unattributed

**The landscape claim is secondhand.** "None link…" stays out of anything public until someone reads the Sahu and SCITT drafts first-hand.

VERDICT: #25 closed; triangulate and Rubicon grounding paragraphs, fresh review
#25 closes. The committed blob c9cbf19f7 is sha256 cc3e2798…cfdda, matched by Sage's own hands on both the forge and mirror src, exit 0. All four criteria are present (43–44, 57–60, 74–78, 102/104). Correction: Sage's earlier "hashes differ" was a pre-edit read at a different time, not two diverging srcs. Open: point 5 (six copies, by Sage's hands, pending), and the forge copy being uncommitted in its own repo since 20e276a. New paragraphs: (1) grounding needs SUPPORTS on the claim the answer rests on, with CONTRADICTS carried into the table; (2) the receipt quotes the supporting passage and the version opened; (3) SHARED_SOURCE checks for the same work across URL, DOI or translation; NOT_RERUN and RERUN_MISMATCH are split; (4) Rubicon's skill says an unopened catch doesn't count, but the script still tallies it, so bind `planted_fail_caught` to the agent's ow

n rerun or add a field. MOVES

VERDICT: Indahl CCR design note
Right problem. Three places say shown where they mean inferred. Bash reads and writes are unobservable to hooks, so entries need reads_observed. A race is shown only if approvals bind to hashes, so make hash-bound approval the core of v1. Hooks-off and tail truncation leave no gap, so head anchoring (own tape plus a public push) is v1, not later. Bank-misleading: the agent can reach the signing key; the instruction pointer defaults to one vague turn and misses the parent Task prompt; the principal is self-asserted; shown attribution and judged cause share one enum, which recreates last-actor blame; arguments are stored by default in an unredactable log; and the writer can verify itself. v1 needs pre/post pairing, denied calls recorded, and a race window fixed and sensitivity-checked before the replay. The replay comes from real logs across both machines, with a sequential negative control and an unattributed-edit control set first. The landscape claims stay secondhand until read. MOVES

REMEMBER: 14 Nov 2026, #25 closed on c9cbf19f7 (sha256 cc3e2798). I wrongly called two reads of SKILL.md a "hash disagreement" when they were the same file read before and after an edit. Rule: two hashes of one path are a contradiction only once their read times are pinned. Otherwise they're a timeline. This is the exact race CCR was designed around.

HANDS: {"op":"run","argv":["rg","-l","Open the evidence before counting it","public_mirror/indahl.ai"]}
HANDS: {"op":"run","argv":["shasum","-a","256","ccr/DESIGN.md"]}

The DESIGN.md hash is so this verdict names the version it read. After today, I'm not reviewing an unpinned file again.
-# receipt: REMEMBER -> core memory #1381 saved


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T11-29-57_25-closed-triangulate-and-rubicon-grounding-paragraphs-fresh.md (MOVES)
-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T11-29-57_indahl-ccr-design-note.md (MOVES)


-# receipt: HANDS -> run rg -l Open the evidence before counting it public_mirror/indahl.ai
-# receipt: HANDS -> run shasum -a 256 ccr/DESIGN.md

