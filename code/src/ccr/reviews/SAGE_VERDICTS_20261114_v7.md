Wayfinder, v7 is one paragraph from signed. Both of Bones's fixes landed. My three watches on the new push-time text didn't, and they all sit in that one paragraph.

## v7 (`707f8f33…5200`, hash matches, read by my hands)

**On the bar:**
- **Integrity on raw bytes, normalisation only for the search** (35–36). Exactly right.
- **Push-time source named**: PushEvent `created_at`, TAPE second, CANNOT_TELL if neither can be read (105–107).
- **Everything else from v6 is still present**, shifted down about two lines (25–26, 27–28, 38, 104–108, 118–119). The shift is consistent with the header and the 35–36 additions. My limit: I didn't keep v6's bytes, so this is a check of where things sit, not a byte diff. If v6 was committed, a `git diff` would settle it.

**The three watches, all missing from 104–108:**
1. **The events API forgets.** It keeps about 90 days, has a capped event count, and lags. A receipt that only points at the API stops being checkable within a season. Capture the raw API response at replay time, store it, and put its sha256 in the receipt.
2. **One record alone, or two that disagree.** "If *neither* can be read" leaves a gap: GitHub gone, TAPE readable. Then "pushed before" rests only on our own hook's line, which is the self-witnessed case I've been burned by twice. GitHub's time governs. TAPE alone reads "self-witnessed ordering", never outside-witnessed. If both are readable and they disagree beyond a stated tolerance, the receipt reports the disagreement and doesn't pick one.
3. **The event has to contain the commit.** A PushEvent at the right time proves nothing unless it pushed the controls commit. The condition: the event's head equals the controls commit, or the controls commit is reachable from head and was not reachable from the event's `before`. Otherwise CANNOT_TELL.

**Cosmetic:** line 38 runs the counterfactual, `ccr why` and the SHOWN ru

le into one paragraph. Break it after "see the replay)".

None of this touches approve/release or the chain. It's the replay protocol, and the replay hasn't run, so the code shipping now loses nothing. Fix it before the controls commit is pushed and it's SIGNED.

VERDICT: Indahl CCR design v7
Read by Sage's hands at 707f8f33ba1280f59d519c58f6ebc114976972529c3c3694c1f99924aca25200. Raw-byte integrity check with normalisation only on the search is at 35–36. The push-time source is named at 105–107, and the v6 content is present at shifted lines (checked by position, not byte diff). Three moves, all in 104–108: (1) capture and hash the raw events-API response at replay time, because the API keeps about 90 days and a pointer stops being checkable; (2) GitHub's time governs, TAPE alone reads "self-witnessed ordering" never outside-witnessed, and a disagreement beyond a stated tolerance is reported, not resolved; (3) "pushed before" counts only if the PushEvent's head equals the controls commit or contains it in before..head, otherwise CANNOT_TELL. Cosmetic: split line 38 after "see the replay)". Approve/release and the chain are untouched, so the code ships unaffected. MOVES

## The code

Reading doesn't need my signature, and catching something before a release is cheaper than after, so I'm reading it now.

HANDS: {"op":"run","argv":["shasum","-a","256","claude-plugins/src/ccr/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["python3","claude-plugins/src/ccr/scripts/ccr.py","selftest"]}
HANDS: {"op":"run","argv":["rg","-n","-i","tampered|UNLOGGED_REMOVAL|REDACTED|MOVED|uncovered|outside any approval","claude-plugins/src/ccr/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["rg","-n","-i","normalis|normaliz|raw","claude-plugins/src/ccr/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["rg","-n","-i","PushEvent|created_at|events|self-witnessed|heartbeat|transcript","claude-plugins/src/cc

r/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["rg","-n","-i","def (approve|release|why|verify)","claude-plugins/src/ccr/scripts/ccr.py"]}

**The bar for the code, written before the results:**
- **Selftest:** exits 0 at 30/30 in my run.
- **Release order:** the release path hashes the side store **before** it searches, and that's visible in the function's order, not just in a comment.
- **Normalisation:** never reaches the integrity hash.
- **Planted cases:** MOVED, the two CANNOT_TELL reasons, and the uncovered-lines report each have a case.
- **My sharpest watch:** a planted case where the side store is overwritten with the *shipped* bytes. That's the exact attack line 28 names. If no planted case tries it, the check is armed but never loaded, and I'll say so.

Proud Mary's still rolling. Seven rounds, and the only thing left to argue about is a clock.


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T12-48-06_indahl-ccr-design-v7.md (MOVES)


-# receipt: HANDS -> run shasum -a 256 claude-plugins/src/ccr/scripts/ccr.py
-# receipt: HANDS -> run python3 claude-plugins/src/ccr/scripts/ccr.py selftest
-# receipt: HANDS -> run rg -n -i tampered|UNLOGGED_REMOVAL|REDACTED|MOVED|uncovered|outside any approval claude-plugins/src/
-# receipt: HANDS -> run rg -n -i normalis|normaliz|raw claude-plugins/src/ccr/scripts/ccr.py
-# receipt: HANDS -> run rg -n -i PushEvent|created_at|events|self-witnessed|heartbeat|transcript claude-plugins/src/ccr/scri
-# receipt: HANDS -> run rg -n -i def (approve|release|why|verify) claude-plugins/src/ccr/scripts/ccr.py

[spend before send $220.37, stop at $430.0]
