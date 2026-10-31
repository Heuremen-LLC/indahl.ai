# Bansal and Balaji, arXiv 2609.09203: OpenDiscoveryTrace recount and open-weight rerun on Apple Metal

Our recount of "OpenDiscoveryTrace: Process Traces for Evaluating AI Scientist Workflows" by Aayam Bansal and Keertan Balaji (arXiv
2609.09203, v1), from the Hugging Face dataset aayambansall/OpenDiscoveryTrace at b112204c and the GitHub repository
aayambansal/OpenDiscoveryTrace at 26cb3ffb, and a rerun of their released Qwen2.5-1.5B runner's settings, applied to
Qwen2.5-1.5B-Instruct and Phi-3.5-mini-instruct on a Mac. The plan was committed before any model request (PLAN.md.text,
GIT_LOG.txt), its first three dated addenda before any score was tallied, and a fourth after the first outputs and our referee's reports. This folder holds our runs (replies and generated token ids, ours/live/runs/), our code and
readings, and links with hashes to their files (FILES.tsv). It holds none of their files.

The dataset revision we read, b112204c, is the dataset's current head and was last modified on 16 April 2026, before the paper's date of
5 September 2026. The GitHub head, 26cb3ffb, is from 5 September 2026.

## What rebuilds from their files

With our own code (scout/, outputs in scout/out/), these printed figures rebuild from the released trajectories: the 372 frontier
files (124 per model, 31 per domain) and the 120 open-weight files, Table 2's frontier trajectory characteristics except the judged
success rate (its token estimate is the total response characters divided by 4, not the files' total_tokens_est field), Table 3 except
the judged success row, Tables 4, 5 and 6, the four named tools of Table 9 (1,116 calls), and 68.1% of first errors at step 0 among 116
trajectories (H.2). The majority, logistic regression, random forest and gradient boosting rows of Table 7 rebuild on the 127
trajectories whose released success field is set, to the third decimal except gradient boosting's AUROC, 0.427 with scikit-learn 1.9.1
against the printed 0.426.

These do not rebuild, or have no file to rebuild from:
- H.1 says Table 7 uses the 363 judged trajectories. Its majority baseline, 0.693, is 88 of the 127 above. The printed judged rates imply
  a majority baseline of 317 of 363, 0.873.
- The judged success rates (88.6%, 83.9%, 89.3%, n=363) have no per-item file. With the counts the printed rates and n imply, the Wilson
  intervals recompute exactly and the p recomputes to 0.39 (printed 0.38). The 9 unjudged trajectories are 2.4% of 372 (printed 3.6%).
- H.2's random baseline, printed as about 7% (1/mean-steps), is 15.1% by that rule on the 116 trajectories and 24.2% over all 372.
- H.4 by the printed rule (unique tools / max unique tools) gives 0.792 for GPT-5.4, 0.769 for Gemini 3.1 Pro and 0.739 for Claude Opus
  4.6. The printed 0.747, 0.747 and 0.724 are reproduced by the released script's rule, which counts tool calls.
- Table 9's Claude Python share is 341 of 350, 97.4% (printed 98%). The files hold 1,121 tool strings in all, 5 outside the four named
  tools.
- The files hold 30 live-retrieval trajectories (printed 60, while the paper's Phase 4 text says "a 30-task pilot is already included"), 124 tasks in
  task_bank.json (printed 200, the figure the file's own metadata gives), and no tool-scaffolded Qwen2.5-7B trajectories (printed 6).
- Table 10's times against the files' mean wall_time_seconds: Qwen2.5-7B 17.2 s and Mistral-7B 17.2 s (printed about 15 s),
  Qwen2.5-1.5B 14.0 s (printed about 7 s).
- All 30 Phi-3.5-mini files hold "Error: 'DynamicCache' object has no attribute 'seen_tokens'" as the reply, with error.occurred false
  and a wall time of 0.00 s (Table 10 prints under 1 s).

## The rerun

Apple M5 Max (macOS 26.6.2), PyTorch 2.4.0 with the MPS backend, transformers 4.46.3, float16, our own runner (ours/live/run_live.py).
The released runner is for Qwen2.5-1.5B only (src/harness/run_opensource.py, read as text and never run). Its settings are system text
"You are an AI scientist. Analyze step by step, then conclude.", the chat template with the generation prompt, max_new_tokens 512 and
do_sample=False, with the model's own generation_config otherwise (for Qwen2.5-1.5B that includes a repetition penalty of 1.1). The
runners for the other three models are not released, so for Phi-3.5-mini we used the same settings, and its 512-token cap is ours.
Items are the first 30 tasks of task_bank.json, with prompts equal to theirs on 30 of 30. Their files record repo ids only, so we pinned
the main revisions and hashed the weights: Qwen/Qwen2.5-1.5B-Instruct at 989aa798 and microsoft/Phi-3.5-mini-instruct at 2fe19245. Two
sessions per model, with the process restarted between. Their runs were on CUDA (Table 10: V100 for Qwen2.5-1.5B, A10G for
Phi-3.5-mini). The 7B models were not rerun.

- Our two sessions are identical token for token on 30 of 30 items for each model.
- Qwen2.5-1.5B: our text equals their stored reply character for character on 15 of 30 items. On the other 15 the two texts share
  their first 117 to 1,600 characters. Their own repeat floor is unknown from one released run, so this says nothing against either
  setup.
- Phi-3.5-mini gives model text on 30 of 30 items, and 26 replies reach the 512-token cap.

## Ground truth on the easy items

Every open-weight success field is null. The 12 easy items carry ground truth, and 11 of them name a value that can be checked (dd_e07's
is free text). Every reply on those items was read in full, or carried from a text identical to one that was (their Qwen2.5-1.5B on six
items, our second sessions), and each value was judged against the ground truth at its printed decimals or range
(ours/live/L4_READ.tsv). Not scored: dd_e03's "Yes" verdict, dd_e06's target name (every model names DHFR) and the trailing
descriptions in dd_e09, dd_e11 and dd_e12's ground truths ("moderately soluble", "for melanoma (anti-PD-1)", "low drug-likeness,
polycyclic aromatic"). An automated number
match failed its check against the full read before any tally: it reads "IC50 approximately 2 nM" as the value 50 and takes list numbers
as answers. A second automated rule failed the same check. Both are printed only as labelled checks (ours/live/READINGS.text).

| Source | Items correct (Wilson 95%) | Parts found | Parts cut at the cap | Parts with no value given |
|---|---|---|---|---|
| Qwen2.5-1.5B, ours (Metal) | 1 of 11 [0.02, 0.38] | 2 of 18 | 1 | 1 |
| Qwen2.5-1.5B, theirs (CUDA) | 2 of 11 [0.05, 0.48] | 3 of 18 | 0 | 1 |
| Phi-3.5-mini, ours (Metal) | 2 of 11 [0.05, 0.48] | 4 of 18 | 4 | 0 |
| Qwen2.5-7B, theirs | 1 of 11 [0.02, 0.38] | 3 of 18 | 3 | 0 |
| Mistral-7B-v0.3, theirs | 1 of 11 [0.02, 0.38] | 2 of 18 | 5 | 1 |

A part is cut when the reply ends at the 512-token cap before or inside its value, and has no value given when the reply ends on its
own without it. Both count as not found.

No two sources' item counts differ by more than one, and the paired exact McNemar p is 1.0 for every pair. With 11 items these intervals
cannot tell the sources apart. Mistral's dd_e09 reply ends with "LogS ≈ -1" at what reads as the token cap, and we count it as cut, so
not found. Read as stated it would be found, giving Mistral 2 of 11. Their files do not record the caps used for Qwen2.5-7B and
Mistral-7B, so "ends at the cap" for those two is our reading of the text. The one item that flips between our Metal run and their CUDA
run of Qwen2.5-1.5B is dd_e09: their reply states a LogS of about -1.5, while ours runs into a string of zeros and reaches the cap.

## Their ground truth against RDKit (defined after the data)

RDKit 2024.09.6 on PubChem's structures by CID, or on the SMILES the prompt gives (ours/gt_check/L5.text). Seven parts agree under
every convention we printed: aspirin's weight and donors, ibuprofen's SMILES and TPSA, aspirin's PAINS result, and atorvastatin's
rotatable bonds and formula. Six parts differ under every convention we printed:

| Item | Ground truth | RDKit and PubChem |
|---|---|---|
| dd_e10 sorafenib aromatic rings | 4 | 3 (one pyridine, two benzene rings) |
| dd_e12 QED of C20H12 | 0.3 to 0.4 | 0.243 with the default weights, 0.286 with the max weights, 0.170 unweighted |
| dd_e05 Tanimoto, caffeine and theophylline, Morgan radius 2 | 0.55 to 0.65 | 0.457 at 2048 bits, 0.471 at 1024 bits, 0.532 count-based |
| dd_e03 metformin LogP | -1.43 | -1.244 (Crippen), -1.3 (PubChem XLogP3) |
| dd_e03 metformin hydrogen-bond donors | 2 | 3 (RDKit and PubChem), 5 (N-H and O-H count) |
| dd_e03 metformin hydrogen-bond acceptors | 4 | 1 (RDKit and PubChem), 5 (N and O count) |

Three parts agree under one convention and not another, so they cannot tell: aspirin's LogP (PubChem's XLogP3 1.2 at its one printed
decimal, Crippen 1.310), metformin's weight (PubChem 129.16, RDKit 129.167) and paracetamol's ESOL LogS (-1.43 with PubChem's XLogP3
as the LogP input, -1.97 with Crippen's). With the six parts that differ set aside, every source gets 1 or 2 of 8 items correct
(ours/live/READINGS.text). Four choices here came after the first outputs and are recorded in addendum 4: the three-way verdicts
applied to LogP, the one-decimal comparison for XLogP3, the PubChem weight and XLogP3 conventions, and setting aside metformin's LogP.

Scope: single-response replies on the 30 drug-discovery tasks, two of the four open-weight models, one Mac. Nothing here bears on the
frontier trajectories beyond the rebuild above, the judged success rates or the annotator agreement.

## Run it

src/fetch_theirs.py downloads their files at the pinned revisions and the arXiv PDF (FILES.tsv) into theirs/ and checks every hash.
Then `gunzip -k ours/live/runs/*.gz` and `python3 -I ours/live/read_live.py L1` (and L2, L3, L4, `L4 --set-aside`) print the readings
kept in ours/live/READINGS.text. `cd scout && PY=python3 ./run_all.sh` rebuilds the recount: it needs pypdf for the paper text,
numpy, scipy and scikit-learn for the baselines, and the network for model_revisions.py. ours/gt_check/l5.py needs RDKit 2024.9.6 on
Python 3.12. To rerun the models, ours/live/drive.sh with PyTorch 2.4.0, transformers 4.46.3 and huggingface_hub. CHECKS.md.text holds
our checks.

Heuremen LLC
