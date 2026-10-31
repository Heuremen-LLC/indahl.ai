# Faults/Guards bench v2 on the RTX 3080 workstation with one parallel slot (plan committed before any reply on this server; 31 Oct 2026)

Why: Pub #2 compared the Mac (Ollama 0.34.2, one slot) with this workstation (Ollama 0.34.3, four slots). faultsbench2_mac_builds runs the
Mac under the official 0.34.2 and 0.34.3 builds with one slot. This run gives the workstation one slot, so the two machines can be read
with the Ollama version and the slot count matched.

Setup. The workstation (Windows, NVIDIA RTX 3080 10 GB, CUDA compute 8.6), its official Ollama 0.34.3 install, our own models there.
Its server today was started on 29 Oct by a launcher setting OLLAMA_HOST=0.0.0.0:11434, OLLAMA_KEEP_ALIVE=-1 and OLLAMA_NUM_PARALLEL=4
(ollama_serve.log: NUM_PARALLEL 4, FLASH_ATTENTION false, MAX_LOADED_MODELS 2). For this run the server is restarted with the same launcher
and NUM_PARALLEL=1, nothing else changed; its config line is recorded before any request (out/setup.json). Afterwards the original
launcher (NUM_PARALLEL=4) is restored and the rounds drive resumes. Requests are sent from the Mac one at a time.
Items, arms, request settings, gates and scorer: byte copies of faultsbench2_armature (CODE.sha256). run_armature.py differs from
faultsbench2_armature/run_armature.py only in a comment. Models: phi4-mini:latest, llama3.2:3b, qwen2.5:1.5b, granite4.1:3b,
ministral-3:3b, with manifest digests checked equal to seats_compare/setups_20261030.json before any reading.

Known-good: this server's own exact repeat (bare against bare_copy) per model.
Readings, with the operational rule of faultsbench2_mac_builds/PLAN.md addendum 1 (I = items byte-identical in both runs' repeats;
CONSISTENT if none of I changes across, ABOVE if any does, CANNOT_TELL if I holds fewer than 100 items), item-by-item scored-class changes
against each side's repeat floor, and the per-family paired bootstrap of seats_compare/compare.py:
C1 Slots, same machine and build: this run against faultsbench2_armature/out (four slots, 30 Oct).
C2 Machine, version and slot count matched: this run against faultsbench2_mac_builds/out/official-0.34.3 (the Mac, one slot).
Parser: the committed score.py, ten replies per family read in full before any rate is printed. Nothing goes on a page until the ledger has
it and he says so. One GPU job at a time on the workstation: the rounds drive is paused for this run and resumed after it.

## Addendum 1 (31 Oct 2026, defined after the data: written after C1 and C2 were read)
C1 reads CONSISTENT for four models and ABOVE for ministral-3:3b (84 changed items), but compares four slots on 30 Oct with one slot today,
across a server restart. C1b: the restored four-slot server (restarted 13:33 EDT today with the 29 Oct launcher, NUM_PARALLEL 4) runs the
same five models, three arms, today, into out_4slot_today/. Read: four slots today against four slots on 30 Oct (same configuration, a day
and a restart apart), and against one slot today (slots only, same day). The rounds drive pauses again for it (rounds addendum 2).
The one guard request that returned HTTP 500 (ministral-3:3b P2_21) stays as written and is counted as unread.

## Addendum 2 (31 Oct 2026, before any four-slot-today reply was read)
The first four-slot-today attempt (13:35 EDT) is discarded and kept in quarantine_4slot_today_partial_offload/ (89 phi4-mini bare
replies, none read). Its server log shows phi4-mini loaded with 7 of 33 layers on the GPU, against 33 of 33 on 30 Oct and in the one-slot
run: model runners left over from the earlier servers (llama-server.exe, started 12:52, 13:16 and 13:27 EDT) still held about 7.9 GB of
video memory, because the restarts stopped the ollama processes and not their runners. The runners were stopped at 13:47 EDT (video memory
44 MiB) and the four-slot-today run restarts on a clean GPU into out_4slot_today/. Every load in the 30 Oct run and in the one-slot run
put all of the model's layers on the GPU (server logs, gpu_layers.txt). Each run's GPU layer count per model is reported beside its
readings from now on.
