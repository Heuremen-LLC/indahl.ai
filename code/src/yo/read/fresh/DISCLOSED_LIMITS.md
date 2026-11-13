# Disclosed limits of the FRESH TEST after Addendum 6 (4 Nov 2026 ~23:33Z, Sage on A6). None changes what the run measures, so none is a new stamp.
1. Empty driver hash. RUN_MANIFEST.txt hashes "$0". That line is empty unless yf_drive.sh is started from fresh/. yf_wait.sh, the only launcher, does
   cd "$HOME/bones-forge/yo/read/fresh" and runs ./yf_drive.sh, so the line is filled. A manifest with an empty "running driver" line counts as unwitnessed.
2. Gate block heights are not written into RUN_MANIFEST.txt. The gate's PASS lines go to yf_drive.log and yf_gate_poll.log, which are not hashed. The
   heights the gate accepted are the Bitcoin attestations inside the committed .ots proofs of the plan and Addenda 1-6, which anyone can read.
3. TRANSFORMERS_OFFLINE is exported by the driver (line 4, under Addendum 6's hash) but not printed in the manifest. HF_HUB_OFFLINE is printed.
4. One-shot is per folder. A copy of fresh/ elsewhere would pass the gate, and nothing outside our own disk would show it. RUN_STARTED.log, written
   by yf_wait.sh, is not hashed into OUTPUTS_YO_FRESH.sha256. The outside witness of the run is the post-run output stamp, and we publish it whatever
   the result.
5. SIGKILL or power loss cannot be trapped (Addendum 6 item 3).

Corrections (2026-11-04T23:39:27Z, Sage A6 VERDICT 23:38Z):
- The header of this file says "~23:33Z"; the file was committed at 23:31:46Z (commit 18140cc). The two STAMP_LOG lines marked "23:33Z" were written in that same commit. The attribution "Sage on A6" refers to her 23:31Z message.
- Item 1 corrected: the "running driver" line is empty only if yf_drive.sh is started by a relative path from outside fresh/, or read from stdin. yf_wait.sh now starts it by its absolute path, which hashes correctly.
- Item 2: "committed .ots proofs" is true only once yf_wait.sh has committed the upgraded proofs. Its first version (472c849) would have failed that commit, because yo/.gitignore ignores *.log and the add included one. Fixed: add -f, and the launcher refuses to run if the proofs are not committed.
- Added: 6. The launcher, yf_wait.sh, is not pinned by any stamp. It logs every driver exit ("driver exit <code> at <time>") in RUN_STARTED.log and commits it. The page prints the number of driver executions after the blocks, whatever it is.
