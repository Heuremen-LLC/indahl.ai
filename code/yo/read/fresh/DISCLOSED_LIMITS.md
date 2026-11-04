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
