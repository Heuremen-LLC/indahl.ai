# Capacity advice, 11 Nov 2026 (readings 00:11 to 00:22 UTC on 12 Nov, plus the capacity rider history and scheduler.log for 11 Nov)

Read-only review. Nothing was changed, started or stopped. The only probes I sent were one tiny judge request per replica per sample.

## 1. How busy is each GPU, and what is it waiting on when idle

Mac GPU: 99 percent in all four of my samples (ioreg Device Utilization), 95 and 98 percent in the rider's two readings. The Mac metal is not idle. It is the one resource that is saturated.
But busy is not the same as useful. The Mac GPU is shared by one job at a time (.train.lock) and right now council.log shows every council lane paused with "PAUSE_MAC (a seat is training on the Mac GPU)". So the council and the seat servers are parked while a train_live.py LoRA job runs. Of the Mac GPU time on 11 Nov, the scheduler.log shows these jobs: SFT and DPO for granite, hermes, llama, and repeated harvest generation for ernie. The ernie harvests are wasted, see section 2.

Armature GPU (RTX 3080, 10 GB): 0 percent in all four of my samples (nvidia-smi), 0.0 percent in both rider readings, power 5.8 to 6 W (idle) with one blip to 12 W. So the share of time busy over the window is about 0 percent. It holds qwen3:8b resident (5.7 GB VRAM, 6.0 GB used of 10.2 GB) and nothing is asking it anything. It is idle because:
- qwen3:8b is used by (a) the the council lane council as a writer and executive model (council.py WRITERS, EXEC_MODEL, ARM_FITS), and those lanes are paused whenever PAUSE_MAC is set, which is most of the time a seat trains; and (b) as the "q" judge inside harvest.py (_qwen_pass), whose score is recorded but, per harvest.py line 135 and 142 ("qwen3 q recorded in judged.json, decides nothing"), no longer decides keep or drop. DPO reads those q values, but the keep rule does not.
- The Armature CPU is the busy part: 70 to 100 percent of 16 logical cores, from the granite-guardian llama-server running on CPU (about 54 CPU-hours accumulated), serving the judge replica. That is a CPU judge doing work the 3080 could do in a second or two.

## 2. Pipeline bottleneck right now

The Mac GPU lock is the hard serial resource (generation, SFT and DPO all queue on it), so the Mac is saturated. But much of what saturates it is waste, and the slow side of the pipeline is judging:
- Ernie loop (largest waste). train/harvest ... ernie .drop flag says "REAL_FAIL adapter ... emit <unk> junk ... Training held until the cause is found." The scheduler still treats ernie as eligible every time a slot frees, so it runs the full turn: builds a fresh paired set, runs harvest (48 prompts x 8 samples of generation on the Mac GPU, plus judging every claim on all three judges), then train_live refuses with rc 4. scheduler.log shows 24 "rc 4" exits, ernie at 16:42, 19:33, 20:59 on 11 Nov alone, and a turn slot (MAXT = 4 in train_scheduler.py) held by it each time. The rider also reports ernie harvest silent 133 min, so those turns are long. That is generation, judge and a slot spent for a result that is thrown away.
- Judging is slow because two of three replicas are slow. Measured round-trip for one tiny claim, four samples each: Mac 1.2 to 1.7 s; laptop (192.168.8.145) 50.6, 60.8, 61.9 s; Armature CPU 36.4, 44.0, 35.6 s. Round-robin (council.py JUDGES, one worker per replica in harvest.py _mc_pass) sends one third of the claims to each. A harvest of 400 to 600 claims therefore finishes only when the slowest third finishes: roughly 200 claims at about 40 to 60 s each across one worker is hours, against minutes if all went to the Mac. The harvest silence numbers (granite 824 to 1375 s, llama 488 to 5800 s, hermes 4900 to 5500 s since the last harvest log line) are consistent with this.
- Scheduling limit. MAXT = 4 and four rotation seats, so all four seats are in flight at once (turnpid files for ernie, granite, hermes, llama). Slots are not the limit; one of the four is ernie's wasted turn.
- Other waste: DPO runs often end "promote refused" or "champion kept", which is by design, not idle.

So the bottleneck is: the Mac GPU is full, but a large share of it goes to ernie turns that are always refused, and the judge stage is gated by the slowest of three replicas (about 40 to 60 s per claim on two of them against about 1.5 s on the Mac) while the Armature GPU sits at 0 percent.

## 3. Is the Armature GPU doing useful work

Almost none right now. qwen3:8b there serves the paused council lanes and a q score that no longer decides anything. It costs 5.7 GB of the 10 GB card and 0 percent utilization.
- Worth its VRAM? Not as the permanent resident. The only live consumer of its output that matters is DPO's use of q, and that can be done in bursts.
- Could granite-guardian move to the Armature GPU? Yes, and that is the best use. granite-guardian-4.1-8b Q4_K_M is about 5 to 5.5 GB. With qwen3 (5.7 GB) also resident, the two do not fit in 10 GB. With qwen3 unloaded (ollama keep_alive 0 for qwen3, or OLLAMA_MAX_LOADED_MODELS=1) the guardian fits on the 3080 with room for context. On a 3080 an 8B Q4 prompt of this size should answer in about 1 to 2 s, the same order as the Mac (1.2 to 1.7 s measured), instead of 36 to 44 s on the CPU. The ollama server there is the same ollama that already holds the guardian, only with GPU layers on. Judge semantics do not change: same model file, same prompt, same rule. Only the device does.
- A training job on Armature: the 3080 with 10 GB can run a LoRA for the 3B or 4B seats (llama3.2:3b, phi4-mini) in 4-bit through a CUDA stack, but that needs a new, validated training path (mlx-lm adapters are not CUDA adapters), so it is a larger change with new risk (adapters trained one way, served another). The qubit adapter already trains there (PAUSE_ARM, PAUSE_ARM_TRAIN) so a CUDA path exists in some form; check with whoever wrote fire_qubit.sh before assuming it is reusable. I would do the judge move first; it needs no new training code.

## 4. Is the judge load spread well

No. Spread is even by count (strict round-robin, one third each, JUDGES in council.py line 174), which is the wrong goal when the replicas differ by 25 to 50 times in speed. The Mac does a claim in about 1.5 s and takes a third of the claims; the laptop takes 50 to 62 s and the Armature CPU 36 to 44 s, each also a third. The batch is as slow as its slowest worker. Fallback is also costly: any error or "zsc_only" reply on a replica (300 s timeout) sends the claim to the Mac after the wait.
- Give the laptop no weight (or only as overflow). At 50 to 62 s per claim it adds under 3 percent of the Mac's throughput.
- Give the Armature CPU replica no weight once the guardian runs on the Armature GPU (it then becomes a second fast judge). Until then, weight it at or near zero for the same reason.
- Better than weights: a shared work queue where each replica takes the next claim when free (pull, not round-robin). Fast replicas then take proportionally more with no tuning.
- Caveat: the Mac judge shares the Mac GPU with training. Measured 1.2 to 1.7 s while the GPU was at 99 percent training, so the cost to training is small, but moving all judging to it adds contention. That is the reason the Armature GPU move matters: it keeps the second fast judge off the Mac.

## 5. Changes, ranked by compute recovered

1. Stop ernie turns that are known to be refused.
   Touch: train_scheduler.py, function eligible() (around the line "def eligible"). Add: return False for a seat that has a drop/hold flag in train/ (the file whose text starts "REAL_FAIL adapter"), or a file such as train/HOLD_ernie4.5_21b-a3b. Or set a hold in scheduler_state.json for that seat the way hold_until_live_n works for granite.
   Effect: removes a full harvest (48 x 8 generations plus about 500 claims x 3 judges) and one of four slots every 1 to 3 hours. This is the largest single block of wasted Mac GPU time and judge time. Risk: none to the judge. It does not hide the ernie fault; it keeps the flag's own instruction ("Training held until the cause is found") and stops the loop. Needs the owner's okay because it is a scheduling rule change.

2. Move granite-guardian on Armature from CPU to the GPU, unloading qwen3 first.
   Touch: Armature ollama (192.168.8.158:11434): set the guardian to load with all layers on GPU (num_gpu 99, the same setting gg_num_gpu 99 that the Mac gg uses) and set qwen3:8b keep_alive to 0 or OLLAMA_MAX_LOADED_MODELS=1 so the two do not compete for 10 GB. Also the replica_server.py in C:\Users\Heure\council_judge, which points at the ollama and probably forces CPU (look for num_gpu 0).
   Effect: the Armature judge goes from about 36 to 44 s to roughly 1 to 3 s per claim (to be measured after the change), so a third of every harvest's judging stops taking tens of minutes. Same model, same rule, same prompt; only the device changes. Risk: qwen3 reload cost for the council lanes and the harvest q pass (a cold load of qwen3 each time the council lane wakes). Mitigation: change 3. Verify by re-running the parity check used for the pi judge (proposed/pi_judge/REPORT.md) on the 109 gold rows before turning it on.

3. Drop the qwen3 q pass from harvest.py (or run it only when DPO needs it) and let the Armature GPU hold the guardian permanently.
   Touch: harvest.py lines 99 to 122 (_qwen_pass) and the ThreadPoolExecutor(2) at the submit; DPO reads judged.json q (pref/harvest_judged.patch), so check that first; a cheap option is to keep qwen3 only for DPO harvests.
   Effect: frees about 5.7 GB VRAM and one HTTP request per claim on Armature. It is what makes change 2 stable. Risk: DPO loses its q column unless kept. This is a change to what the pipeline records, not to the judge, but it does change the harvest data, so referee it first.

4. Replace round-robin with a pull queue, or weights by measured speed.
   Touch: council.py JUDGES / mc_probs (lines 174 to 183) and harvest.py _mc_pass (one worker per replica already; change to a shared queue so a worker takes the next claim when free). Quick version before change 2 lands: remove 192.168.8.145 from JUDGES (it is 50 to 62 s) and keep Armature at low weight.
   Effect: the judge stage finishes in about the Mac's time instead of the slowest third's time. At the measured speeds a 500-claim harvest drops from hours to well under an hour. Risk: all the load lands on the Mac GPU until change 2; the 8892 Mac replica already answers in 1.2 to 1.7 s under a training load, so this looks acceptable. Semantics unchanged: same replicas, same model, same rule.

5. Let the Armature GPU do council and eval generation while the Mac trains.
   Touch: the lane pause rule in council.py line 549 area, where lanes 0 and 1 (which use ARM) are paused on PAUSE_MAC only because the Mac is training; they run on the Armature GPU, not the Mac, and PAUSE_MAC pauses lanes 0 and 1 too (lane 2 and 3 use MAC). Making lanes 0 and 1 ignore PAUSE_MAC would keep qwen3 busy during Mac training.
   Effect: the Armature GPU does council work instead of 0 percent. Risk: conflicts with change 2 (VRAM) and with the council paired-eval design, which may pause lanes on purpose so measurement is not disturbed. I would do this only after 1 to 4, and only with the owner's decision on whether council claims written during training count as live claims.

Not recommended now: a CUDA LoRA training path on the 3080. It is the most compute on paper, but it needs new training code and a new serve path and carries the most risk. Revisit after change 2.

## Flags

- Judge semantics: changes 2 and 4 move where the same granite-guardian and zsc models run; they do not change the model, the AND rule, or MC_T. Run the parity table again after change 2.
- Change 1 is a scheduling rule the owner should confirm; it also leaves the ernie fault itself (the adapter emits <unk> junk) as the real open problem.
- My probes were four samples over about 10 minutes (each sample took about 3.3 min because the laptop and Armature replicas are slow), not a full 15. The 98 to 99 percent Mac and 0 percent Armature readings agree with the rider's readings from the earlier ten minutes, so the picture is stable. The Armature CPU reading varied between 70 and 100 percent in my samples (3 percent in one earlier rider reading, taken while a request was between claims).
- Armature VRAM numbers (qwen3 5.7 GB, about 6.0 GB used of 10.2 GB) are measured. The guardian GPU fit (about 5 to 5.5 GB) and the 1 to 3 s estimate are my estimates, not measurements.
