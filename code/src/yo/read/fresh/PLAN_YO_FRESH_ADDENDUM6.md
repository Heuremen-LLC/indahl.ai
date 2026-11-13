# Addendum 6 to PLAN_YO_FRESH.md (4 Nov 2026). The one exception to Addendum 5's freeze (Sage, A3 VERDICT 23:25Z): a failed or partial run must be
# witnessed. Stamped before any adapter answers a fresh item. Addenda 1-5 stand except where this changes them.
1. One-shot. After the gate passes and before RUN_MANIFEST.txt is written, the driver refuses to start if RUN_MANIFEST.txt, any eval_fresh_yo_*.jsonl,
   any out_*.log, OUTPUTS_YO_FRESH.sha256 or its .ots already exists. A run cannot be deleted and quietly repeated in this folder.
2. Every exit is stamped. From the moment the manifest is written, a bash EXIT trap appends "exit <code> at <time>" to RUN_MANIFEST.txt, hashes the
   manifest and whatever answer files and logs exist into OUTPUTS_YO_FRESH.sha256, and OpenTimestamps it. INT, TERM and HUP exit with code 130 through
   that trap. The end-of-run stamp of Addendum 5 item 1 is now this trap. Planted tests on copies (crash, second start, kill, clean finish) behaved as
   above; a TERM is handled after the adapter that is answering finishes.
3. Known limit, disclosed: SIGKILL or power loss cannot be trapped. Such a run leaves RUN_MANIFEST.txt with no "exit" line and no OUTPUTS stamp, and
   item 1 then refuses any rerun in this folder. That state is printed on the page as a failed run.
4. Executions so far. Every "dry run" reported before this addendum was the real yf_drive.sh, stopped by the gate with WAIT before any adapter
   loaded (no eval_fresh_* or out_* file has ever existed): the yf_wait.sh loop from ~22:52Z until it was stopped at ~22:58Z (yf_drive.log holds its
   last WAIT, 22:56:21Z), then single runs after Addendum 1 (twice), Addendum 2, Addendum 3 (twice), Addendum 4 and Addendum 5 (twice). From this
   addendum on, yf_drive.sh is not executed until the run. Its first execution after the blocks IS the run, and the gate is checked by calling
   yf_gate.py on its own.
5. The driver changed for items 1-2. Its lines in Addenda 3, 4 and 5 are superseded by this one (path relative to yo/read/):
   22b295456d330541f8aa93952e8a81b3ad1e8144313d9248d8b5443db1a4d68a  fresh/yf_drive.sh
6. The gate (yf_gate.py) requires verified Bitcoin block attestations on the plan and Addenda 1-6 before the first adapter loads.
