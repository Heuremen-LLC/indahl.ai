# Patodiya, arXiv 2609.04748: her GSM8K cache bridge rerun on Apple Metal

Our recount of "Same Request, Different Answer: Quantization Amplifies Cache-Induced Divergence in LLM Serving" by Aditi Patodiya
(arXiv 2609.04748, v2), from her repository aditi-p31/cache-divergence-study at bc0551d, and a rerun of her single-turn GSM8K bridge on a
Mac with Metal. The plan was committed before any request (PLAN.md.text, GIT_LOG.txt). This folder holds our runs (token ids and replies of
our own runs, ours/live/runs/*.jsonl.gz), our code and readings, and links with hashes to her files. From her repository it holds only the one-sentence system prompt her harness sends, which our client needs to send the same request.

## What rebuilds

From her released logs, with our own code, her Table 7 bridge rows rebuild to the printed digits (scout/run_bridge.log), including the
divergence counts 83, 89 and 96 of 200 for Qwen2.5-7B Q4_K_M, Q8_0 and Q3_K_M and her F16 row, 7 of 200.

## The rerun

llama.cpp tag b10434 (commit 7e4c0a968, her tag) built from source with Metal, on an Apple M5 Max (macOS 26.6.2, 48 GB). Her server flags
(--parallel 1 -c 16384 -ngl 99 --seed 42 --slots), her prompt strings (SHA-256 equal to hers on 200 of 200), weights equal to her
MODEL_SHA256SUMS, temperature 0, seed 42, logprobs 1, max_tokens 1024, items 0 to 199 in order, her four passes per item (cold, cold2 with
cache_prompt false, warm, warm2 with cache_prompt true), two server sessions per format. Her runs were on an RTX 4090 with CUDA. Our client is
our own (Python standard library); the request fields are hers. Effective defaults such as the flash-attention state were not logged on
either side.

- Every warm request hit the prompt cache for all but one prompt token, and no cold request did (client fields and server logs agree).
- Cold against warm, the replies differ on 8, 3 and 9 of 200 items (4.0% [2.0, 7.7], 1.5% [0.5, 4.3], 4.5% [2.4, 8.3], Wilson 95%), against
  her 41.5%, 44.5% and 48.0% at the same formats on CUDA (ours minus hers -37.5, -43.0 and -43.5 points, Newcombe 95% intervals in
  ours/live/RATES.text). Each path repeats itself exactly: cold equals cold2 and warm equals warm2 on 200 of 200.
- Defined after the data: her own CUDA F16 row is 7 of 200 (3.5%), and our three quantized rates on Metal are all consistent with it
  (+0.5, -2.0 and +1.0 points, intervals in ours/live/RATES_NOTES.md). No Metal F16 run exists, so whether quantization raises the
  divergence on Metal is untested here.
- Our two sessions are identical token for token on all 800 requests per format.
- Correctness: no flips between the paths among the divergent items by her Table 7 scorer; one by her run-time rule (Q8_0 item 124, a
  formatting change). Too few divergent items to say whether Metal flips correctness less often.
- Metal against her CUDA runs: identical token ids on 78 to 110 of 200 items per pass and format. Her own CUDA cold-against-warm identity is
  117, 111 and 104 of 200, the same order, so this says nothing against either setup.

Scope: one single-turn GSM8K bridge with a full-prefix cache hit, one Mac, three quantized formats. Nothing here bears on partial prefix
reuse or her agentic results, and no mechanism for the smaller divergence on Metal is named.

## Run it

src/fetch_theirs.py downloads her bridge logs, summaries and model manifest at the pinned commit and the GSM8K test rows 0 to 199 (FILES.tsv)
into theirs/ and checks their hashes. Then `gunzip -k ours/live/runs/*.gz` and `python3 -I ours/live/read_bridge.py --rates` prints
ours/live/RATES.text; `cd scout && python3 -I rebuild_bridge.py out.json` rebuilds her Table 7 rows (numpy and scipy). To rerun the server,
fetch the GGUF files with ours/live/fetch_gguf.py, build llama.cpp at b10434 with Metal, and run ours/live/bridge_drive.sh. CHECKS.md.text
holds our checks.

Heuremen LLC
