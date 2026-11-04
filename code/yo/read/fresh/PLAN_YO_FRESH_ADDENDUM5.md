# Addendum 5 to PLAN_YO_FRESH.md (4 Nov 2026, Sage on A4). The LAST addendum: anything found after the blocks goes on the page as a disclosed limit.
Stamped before any adapter answers a fresh item. Addenda 1-4 stand except where this changes them.
1. The driver is not its own witness. At start, after the gate passes and before the first adapter loads, the running driver writes RUN_MANIFEST.txt:
   the start time, sha256 of the running yf_drive.sh ($0), of yf_eval.py and of yo2_data.py, the Hugging Face refs/main it will load and
   HF_HUB_OFFLINE, and the live python, mlx, mlx_lm and transformers versions, printed by the venv itself. At the end RUN_MANIFEST.txt is hashed into
   OUTPUTS_YO_FRESH.sha256 with every answer file and log, and that file is OpenTimestamped. The block after the run then shows which driver and which
   versions actually ran, to compare with the lines stamped here and in Addendum 4.
2. The loaded model is the hashed model. yf_eval.py and yo2_data.py load "Qwen/Qwen3-1.7B" by name through the Hugging Face cache, which resolves
   refs/main. Today refs/main = 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e, the snapshot whose 10 files (chat template in tokenizer_config.json among
   them) are hashed in Addendum 4. The driver now sets HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1, so nothing is downloaded, and it refuses if
   refs/main is not that snapshot. Adapters load from the adapter folders hashed in Addendum 4 (adapter_path = ../adapters/readN,
   ../shuffled/selflabel/adapters/selfN, ../shuffled/adapters/shufN). mlx loads the safetensors in place; no converted folder is used.
   Decoding: greedy (mlx_lm.generate default, temperature 0), max_tokens 8, prompt rendered by yo2_data.render (chat template, thinking off).
3. The driver changed again for items 1-2. Its lines in Addendum 3 and Addendum 4 are superseded by this one (paths relative to yo/read/):
   29b462535ea89a3bb78390b13c7c4020c64ff0cbb4dd06c993b7e11a6b7bb23c  fresh/yf_drive.sh
   The driver checks every other line of Addendum 3's and Addendum 4's lists unchanged (it skips only its own fresh/yf_drive.sh line in each).
4. The gate (yf_gate.py) requires verified Bitcoin block attestations on the plan and Addenda 1-5 before the first adapter loads.
5. A first stamp of this addendum is WITHDRAWN before any run: item 2 said the snapshot has 11 files; it has 10. Kept in withdrawn/.
