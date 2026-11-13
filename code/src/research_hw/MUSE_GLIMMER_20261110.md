# Muse Glimmer: model, licence, memory and hardware fit

Researched 10 Nov 2026 from the live pages. Every fact carries its source. Lines marked ESTIMATE are our arithmetic, with the working shown.

Main sources:
- Owner page: https://dev.meta.ai/models/muse-glimmer
- Model card: https://huggingface.co/meta-models/Muse-Glimmer-30B (README.md, config.json, LICENSE, USAGE_POLICY.md)
- Official GGUF repo: https://huggingface.co/meta-models/Muse-Glimmer-30B-GGUF
- Technical report: arXiv 2610.24628, "Muse Glimmer 30B: An On-Device Agentic Model", https://arxiv.org/abs/2610.24628
- Eval methodology PDF: https://research.meta.ai/static/muse-glimmer-methodology
- Independent: Artificial Analysis https://artificialanalysis.ai/articles/muse-glimmer , LMSYS/SGLang https://lmsys.org/blog/2026-08-10-meta-muse-glimmer/ , Classmethod DGX Spark test https://dev.classmethod.jp/en/articles/dgx-spark-muse-glimmer-first-touch/ , vLLM recipe https://recipes.vllm.ai/meta-models/Muse-Glimmer-30B , Unsloth training guide https://unsloth.ai/docs/models/muse-glimmer/train

## 1. Architecture

It is a dense model, not MoE. The card lists "Dense Causal Transformer with Perception Encoder" and about 29.6B total parameters, including the vision encoder (model card). Because it is dense, all parameters are active on every token. There are no experts. The report says Meta tested MoE designs with 1:8 and 1:16 sparsity at the same memory footprint and found dense was 2 to 2.5 times more compute-efficient under a 32 GB ceiling, so it chose dense (arXiv 2610.24628, section 2.3).

The parameters split as follows. The language backbone has about 25.16B parameters without embeddings. Input and output embeddings are untied, at about 1.34B each (202,048 × 6656). The perception encoder is about 1.8B (arXiv 2610.24628, sections 2.1 and 2.2).

Layer details from the model card and config.json:
- 52 layers, hidden size 6656, FFN intermediate 19,968 (SwiGLU).
- Attention repeats three local layers then one global layer. The sliding window is 2048 tokens. That gives 39 local and 13 global layers (config.json layer_types).
- Grouped-query attention with 32 query heads and 2 KV heads, head dimension 128. Attention is gated.
- RoPE with θ = 500,000, on local layers only.
- Vocabulary is 202,048 tokens, using the Llama 4 BPE tokenizer (arXiv 2610.24628, section 4.1).

Context is listed as "131,072+" (model card) with max_position_embeddings 131072 (config.json). Training extended the context from 32K to 128K in mid-training phase 2 (arXiv 2610.24628, section 4.2). The vLLM recipe treats 131,072 as the trained limit. Going past it with rope scaling is outside the recipe (vLLM recipe).

Modalities: text and image in, text out. Video is handled as frames and is not optimised. Audio is not supported (model card). Images can use up to 4,096 visual tokens each (model card).

Release: the card says August 2026 (model card). Artificial Analysis and press date the release to 10 August 2026 (https://artificialanalysis.ai/articles/muse-glimmer). Knowledge cutoff is 4 January 2026 (model card).

Lineage: it was distilled from Meta's closed Muse Spark. Pre-training used top-256 logit KL distillation for the first 95% of training, then cross-entropy for the final 5% (arXiv 2610.24628, section 4.2).

Variants and sizes. There is one model size, 30B (owner page, model card). The released artifacts are:
- BF16 weights, two safetensors shards totalling about 59.6 GB (HF file listing: 49.95 GB + 9.60 GB).
- Two official 4-bit GGUF builds: KQuant-17GB-Q4_K_M at 16.8 GB and KQuant-Dynamic-Q4_K_XL at 19.7 GB. Alongside them come a perception-encoder mmproj at 1.4 GB and a DFlash drafter GGUF at 1.6 GB (https://huggingface.co/meta-models/Muse-Glimmer-30B-GGUF).
- A DFlash speculative-decoding drafter (https://huggingface.co/meta-models/Muse-Glimmer-30B-assistant). It has 5 layers and proposes blocks of 16 tokens (model card).
- An ExecuTorch build for Apple devices (https://huggingface.co/meta-models/Muse-Glimmer-30B-ExecuTorch-PTE).
- Reasoning strength is set in the system prompt as low, medium, high or xhigh (model card).

## 2. Licence

The weights are released under plain Apache 2.0. The HF metadata says `license: apache-2.0`. The LICENSE file is the standard Apache License 2.0 text, and the card says "All artifacts are released under Apache 2.0" (model card, LICENSE). Separately, Meta publishes a Usage Policy. The owner page links it as applying to use of the model (owner page, USAGE_POLICY.md).

Each question in turn:

Commercial use is allowed. The card says "Muse Glimmer is intended for commercial and research use" (model card). Apache §2 grants "a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works" (LICENSE §2). §3 adds a patent licence to "make, have made, use, offer to sell, sell, import, and otherwise transfer the Work". That patent licence terminates only if you sue claiming the Work infringes a patent (LICENSE §3).

Fine-tuning and derivatives are allowed. They are covered by "prepare Derivative Works" (§2). The card describes the BF16 weights as "Complete model weights for fine-tuning and research" (model card). The report says the release is meant for "the community to deploy, fine-tune, and extend the model" (arXiv 2610.24628, section 1). You may license your own modifications under different terms: "You may add Your own copyright statement to Your modifications and may provide additional or different license terms" (LICENSE §4).

Distillation into other models is allowed. Neither the Apache text nor the Usage Policy has any clause restricting use of outputs to train other models. The card lists "Synthetic data generation: Generating high-quality training data for downstream model development" and "LLM-as-a-judge evaluation" as intended uses (model card). This is unlike the old Llama community licences.

There is no user-count threshold. Apache 2.0 has none, and the Usage Policy has none (LICENSE, USAGE_POLICY.md). The old Llama 700M-MAU clause does not apply.

Attribution applies only if we distribute the weights or a derivative. The conditions are: "(a) You must give any other recipients of the Work or Derivative Works a copy of this License; and (b) You must cause any modified files to carry prominent notices stating that You changed the files; and (c) You must retain ... all copyright, patent, trademark, and attribution notices", plus (d) a NOTICE-file clause (LICENSE §4). The repo has no NOTICE file in its file listing (HF file listing). Trademarks are not granted beyond describing origin (LICENSE §6). Using it in-house or behind our own service is not distribution, so §4 would not be triggered.

Acceptable use: the Usage Policy says it "applies to your access or use of Muse Glimmer" (USAGE_POLICY.md). The clauses that touch a data-audit business are:
- "Collect, process, disclose, generate, or infer private or sensitive information about individuals, including information about individuals' identity, health, or demographic information, unless you have obtained the right to do so in accordance with applicable law" (§1.1.5).
- "Engage in the unauthorized or unlicensed practice of any profession including, but not limited to, financial, legal, medical/health, or related professional practices" (§1.1.4).
- "Representing that the use of Muse Glimmer or outputs are human generated" (§3.5).
- "Fail to appropriately disclose to end users any known dangers of your AI system" (§4).
- The model "is not intended for individuals under the age of 18" (USAGE_POLICY.md, model card).
- The policy also bars military, ITAR, critical-infrastructure operation, malware, spam, fraud, defamation and similar uses (§1 to §5).

How binding is the policy? The Apache LICENSE text does not incorporate the Usage Policy, and Apache §2 is "irrevocable". Meta still presents the policy as applying to use (owner page, USAGE_POLICY.md), so the safe reading is to comply with it. None of its clauses blocks auditing public papers, measurements or vendor claims.

Verdict for Heuremen LLC: green. We can fine-tune it, distil it into our own models (including Qwen-based ones), use its outputs as synthetic training data, and sell products built on it. There is no size cap, no fee and no registration (the main repo is not gated: HF search shows `gated: false`). If we ever ship weights, we include the Apache LICENSE and mark changed files. In practice we honour the Usage Policy, chiefly §1.1.5 (no inferring personal or sensitive data about individuals without the right) and §3.5 (do not present outputs as human-made). This is a reading of the published text, not legal advice.

Note on the larger sibling: Muse Spark Open 816B-A42B is gated with manual approval on HF, and we could not read its terms without access (https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B). It is irrelevant to this hardware anyway.

## 3. Memory

### Weights (published sizes)
- BF16/FP16: 59.6 GB on disk (HF file listing). vLLM says "~55 GiB" (vLLM recipe). The card lists 64 GB VRAM as the full-precision target (model card).
- FP8 (fp8_block, with vision tower and embeddings kept in BF16): 32.78 GB checkpoint (vLLM recipe; repo https://huggingface.co/RedHatAI/Muse-Glimmer-30B-FP8-block).
- FP4 (NVFP4 W4A4): 25.42 GB checkpoint. vLLM used 28.8 GB of 32.6 GB on one RTX 5090 (vLLM recipe). SGLang's mixed NVFP4+MXFP8 recipe is about 19.5 GB (LMSYS).
- Q4 GGUF: Q4_K_M is 16.8 GB and Q4_K_XL is 19.7 GB. Add 1.4 GB for image input and 1.6 GB for the drafter (official GGUF repo). Meta's rough totals are about 17 GB for text only, 19 GB with vision, and 20 GB with vision plus drafter for the 17 GB build (official GGUF repo).
- Meta reports 0.2% average degradation for the Dynamic Q4 build and 1.0% for the 17 GB build, across 15 benchmarks (model card).

### KV cache (ESTIMATE, from config.json; Artificial Analysis cross-check)
The working:
- Per layer per token: 2 (K and V) × 2 KV heads × 128 dim × 2 bytes (BF16) = 1,024 bytes.
- Global layers cache every token: 13 × 1,024 = 13,312 bytes per token.
- Local layers cache at most 2,048 tokens: 39 × 1,024 × 2,048 = 81.8 MB, fixed.

The results, per sequence:
- 8K context: 13,312 × 8,192 = 109 MB, plus 82 MB, gives about 0.19 GB.
- 32K context: 13,312 × 32,768 = 436 MB, plus 82 MB, gives about 0.52 GB.
- 128K context: 1.745 GB plus 0.08 GB gives about 1.83 GB. This matches Artificial Analysis's "~1.8 GB" at 128K (https://artificialanalysis.ai/articles/muse-glimmer).
- An FP8 KV cache halves these figures. Batching multiplies them by the number of concurrent sequences.

Practical engines reserve more than this. In vLLM on a Spark, 76.6 GiB of pool held about 4.82M tokens, roughly 17 KB per token (Classmethod). The KV cache is still tiny next to the weights. That is the design point: sliding window plus 2 KV heads (arXiv 2610.24628, section 2.3).

### Total to run, one sequence (ESTIMATE: weights + KV + about 1.5 to 2 GB of runtime buffers; add 1.4 to 3.6 GB for vision)

| Precision | 8K context | 32K context |
|---|---|---|
| BF16/FP16 | ~61-62 GB | ~62 GB |
| FP8 | ~34-35 GB | ~35 GB |
| NVFP4 | ~27-28 GB (vLLM measured 28.8 GB) | ~28 GB |
| Q4_K_M GGUF | ~18 GB | ~18.5 GB |
| Q4_K_XL GGUF | ~21 GB | ~21.5 GB |

### Fine-tuning
- QLoRA: Unsloth says "30B QLoRA works with 24GB". Its measured run used seq 1024, batch 1 and r=16. Weights loaded at 18.22 GiB and peak reserved was 22.57 GiB (Unsloth). ESTIMATE: at 4K to 8K sequence length with gradient checkpointing, plan for about 26 to 36 GB.
- LoRA in BF16: Unsloth says ">40GB" (Unsloth). That understates it, since the BF16 weights alone are about 55 GiB. Spheron suggests an 80 GB A100 for LoRA (https://www.spheron.network/tools/gpu-recommender/meta-models/Muse-Glimmer-30B/). ESTIMATE: about 65 to 80 GB at 2K to 4K sequence length.
- Full fine-tune: Unsloth gives no figure and lists "Multi-GPU systems" (Unsloth). ESTIMATE: the standard mixed-precision AdamW figure is about 16 bytes per parameter. 29.6B × 16 gives about 470 GB before activations. With 8-bit optimiser states and BF16 master weights, the floor is still about 180 GB plus activations. That is outside every option below.
- Unsloth training currently supports NVIDIA only. It says MLX, AMD and Intel support is "coming" (Unsloth). NVIDIA NeMo AutoModel also lists the model (https://docs.nvidia.com/nemo/automodel/model-coverage/vision-language-models/meta-models/Muse-Glimmer-30B).

## 4. Hardware fit within $7-10k

Price warning first. The RTX PRO 6000 Blackwell has risen in price. Trackers show about $16,000 in October 2026, a June 2026 MSRP of $13,250, and a 12-month median of $10,458 (https://www.thundercompute.com/blog/nvidia-rtx-pro-6000-pricing , https://gpuprix.com/us/gpus/rtx-pro-6000-blackwell?show=listings , https://www.pulse.bot/hardware/news/nvidia-raises-rtx-pro-6000-blackwell-gpu-pricing-to-13250-55-increase-over-msrp-in-a-years-time-1a0c8cf3-8457-4e55-bb2a-c4427ad8efc2/). It may no longer fit a $10k budget. DGX Spark lists at $4,699 after a price rise from $3,999. One tracker shows $6,950 (https://www.spheron.network/gpu-price/gb10/). Two Sparks cost about $9.4k at $4,699, and more at the higher figure.

The bandwidth rule used below: at batch 1, each decoded token reads all the weights once. So the ceiling in tok/s is bandwidth divided by weight bytes. Real numbers land at about 60 to 95% of the ceiling.

### RTX PRO 6000 Blackwell, 96 GB, 1,792 GB/s (https://ifactoryapp.com/sap-integration/on-prem-ai/dgx-spark-vs-rtx-pro-6000-blackwell)
- Inference (measured, SGLang, LMSYS):
  - BF16: 25.7 tok/s at batch 1, 108 tok/s with DFlash, and 833 tok/s aggregate at batch 8 with DFlash.
  - NVFP4: 58.0 tok/s at batch 1, 214 tok/s with DFlash, and 1,403 tok/s aggregate at batch 8.
  - Arithmetic check: 1,792 / 59.6 = 30 tok/s ceiling for BF16, against 25.7 measured.
- Every precision fits, including BF16 with full 128K context and many concurrent sequences.
- QLoRA: yes, comfortably, at long sequence lengths. BF16 LoRA: yes at short to medium sequence lengths (ESTIMATE 65 to 80 GB, within 96 GB).
- Out of reach: full fine-tuning (about 180 to 470 GB or more).

### One DGX Spark, 128 GB unified, 273 GB/s (https://www.spheron.network/gpu-price/gb10/)
- Inference (measured):
  - LMSYS/SGLang, batch 1: BF16 4.4 tok/s (19.1 with DFlash), NVFP4 12.1 tok/s (36.4 with DFlash). Batch 8 aggregate: NVFP4 92 tok/s, or 301 with DFlash (LMSYS).
  - Classmethod, vLLM, NVFP4: 11.67 tok/s single request, 88.6 tok/s at 8 parallel, and 21.6 to 23.7 tok/s with DFlash (Classmethod).
  - Arithmetic check: 273 / 59.6 = 4.6 ceiling for BF16 (4.4 measured). 273 / 25.4 = 10.7 for the NVFP4 file, which is near the measured figure because the vision weights are not read per text token. For Q4_K_M, 273 / 16.8 = about 16 ceiling.
- QLoRA: yes on memory. BF16 LoRA also fits on memory (65 to 80 GB of 128 GB). The limits are speed and NVIDIA-only tooling, which does run on GB10 since it is CUDA. Training will be several times slower than the RTX PRO 6000. We found no published Spark training throughput for this model, so this is a gap.
- Out of reach: full fine-tuning on one unit. Fast single-user BF16 decode is also out of reach.

### Two DGX Sparks linked, 256 GB
- Inference: no gain for a 30B model at batch 1. The model already fits one unit, and splitting it across the link adds latency. It is better used as two independent servers, which doubles concurrent throughput, or as one training box plus one serving box.
- Full fine-tune: ESTIMATE about 180 GB plus activations with 8-bit optimisers. That is possible on memory in principle with FSDP, but slow and untested publicly. We found no report. Treat it as out of reach in practice.

### Existing 48 GB Apple M-series Mac (MLX)
- Inference fits. Community MLX 4-bit builds exist (https://huggingface.co/mlx-community/Muse-Glimmer-30B-4bit), and so do Meta's ExecuTorch builds.
- Measured speeds:
  - Meta: M4 Max 23.7 tok/s, or 37.8 with DFlash. M5 Max 26.6 tok/s, or 50.2 with DFlash. These used ExecuTorch with the 17 GB Q4 build (model card).
  - LMSYS: M5 Pro 15.3 tok/s for q4_k_m and 17.6 tok/s for MLX q4. MLX has no speculative decoding (LMSYS).
- Speed depends on the chip. Arithmetic: a Pro chip at 273 GB/s gives 273 / 16.8 = about 16 tok/s ceiling. A Max chip at about 400 to 546 GB/s gives about 24 to 32 tok/s ceiling. BF16 (60 GB) does not fit in 48 GB. FP8 (about 33 GB) fits but leaves little room.
- QLoRA: probably feasible at short sequence lengths with mlx-lm LoRA on the 4-bit weights. The memory is about 18 GB of weights plus activations. But Unsloth's MLX training is "coming", not shipped (Unsloth), and we found no published MLX fine-tune of this model. Treat it as unverified and slow.
- Out of reach: BF16 LoRA and full fine-tuning.

### Existing RTX 3080, 10 GB, about 760 GB/s
- Inference: only with offload. The smallest official Q4 is 16.8 GB. One guide says even the smallest community GGUF is 10.75 GB and that 8 GB cards are not workable (https://localaimaster.com/models/muse-glimmer-30b). We found no 3080 measurement.
- ESTIMATE for Q4_K_M with about 9 GB on the GPU and about 8 GB in system RAM at about 50 GB/s (dual-channel DDR4): 9/760 + 8/50 = 0.17 s per token, so about 6 tok/s ceiling and about 3 to 5 tok/s in practice.
- QLoRA: no. It needs about 22.6 GB peak even at seq 1024 (Unsloth).
- Use it for small helper models only, not this one.

### Summary
Within a true $7-10k budget, one DGX Spark (about $4.7k) or two (about $9.4k) is the buy that runs and QLoRA-tunes Muse Glimmer. It also does BF16 LoRA on memory, but it is slow at single-user decode: about 12 tok/s NVFP4, or about 36 with DFlash. The RTX PRO 6000 is the much faster box, at 58 tok/s NVFP4, 214 with DFlash, and fast training. At current listings it costs $10.5k to $18k. The 48 GB Mac already runs it at 4-bit today, at about 15 to 25 tok/s depending on chip. No option here does a full fine-tune.

## 5. Benchmark standing and error behaviour

Meta's own table, at high reasoning, compares only Gemma4-31B and Qwen3.6-27B (model card, owner page).
- Muse Glimmer leads on: MCP Atlas (75.5 vs 54.2 and 62.5), DeepSearch QA (74.6), τ³-Banking (23.5), Gaia2 (43.3), SWE-Bench Pro (51.2 vs 50.2 for Qwen), IFBench (77.0), AIME 2026 (94.7), AA-LCR (80.0) and Beam128K (65.1).
- Qwen3.6-27B leads on: GDPval-AA (1141 vs 953), OSWorld-Verified (75.6 vs 65.9), SWE-Bench Verified (77.2 vs 76.0), TerminalBench 2.1 (60.7 vs 51.7), OmniDocBench and MMMU Pro.
- Gemma4-31B leads on: GPQA Diamond (85.7 vs 83.5) and HLE (23.6 vs 22.0).
- Method caveat from Meta's own PDF: for rival models, Meta reports "the most favorable result between self-reported scores or our internal reproductions" (methodology PDF).

The card shows no comparison against Llama, DeepSeek, Mistral or gpt-oss (model card).

Independent results (Artificial Analysis article, https://artificialanalysis.ai/articles/muse-glimmer):
- Intelligence Index: Muse Glimmer (high) scores 35. Qwen3.6 27B scores 38, Ling 3.0 Flash 38, Kimi K2.5 36, Gemma 4 31B 30, Llama 4 Maverick 14, and Meta's closed Muse Spark 1.2 57. So it trails Qwen3.6-27B and beats Gemma 4 31B.
- The AA model page shows a value on a newer index version, v5.0.1. Its scale differs, and the extraction there was unclear, so we quote only the article (https://artificialanalysis.ai/models/muse-glimmer).
- Openness Index 44 (article).
- Also from AA: GDPval-AA v2 953, τ³-Banking 24%, Terminal-Bench 2.1 52% against 61% for Qwen3.6 27B.
- We found no independent head-to-head against gpt-oss, DeepSeek V4 or Mistral in these sources. DeepSeek V4 Flash appears only in AA's openness comparison (article).

Hallucination and grounding. This is the main weakness, and it matters for an audit product:
- Artificial Analysis AA-Omniscience: hallucination rate 82%, against 49% for Qwen3.6 27B and 34% for Gemini 3.5 Flash-Lite (lower is better). Omniscience Index −33. AA says accuracy matches peers, and the low index is driven by the model answering instead of abstaining (AA article).
- In plain terms, when it doesn't know, it guesses far more often than Qwen3.6-27B does.
- Meta's card says "The model may produce inaccurate, biased, or objectionable responses" and "may still make errors in multi-step reasoning, particularly in novel scenarios" (model card).
- Grounding in the GUI sense: ScreenSpot Pro 75.4, against 75.9 for Gemma and 76.1 for Qwen (model card). We found no published document-grounding or citation-faithfulness benchmark.
- Safety: Siren AgentDojo attack success rate is 28.4%, against 25.6% for Gemma and 40.3% for Qwen. CI Memories violation rate is 26.4%, against 12.1% and 53.4% (model card).

What this means for our use: as a distillation teacher or audit worker, it needs an abstain path and outside checks. A fine-tune for our products should train refusal or CANNOT_TELL on unknowns.

## 6. Smaller siblings and distilled versions

Meta released no smaller sibling. The meta-models org lists only Muse-Glimmer-30B and its GGUF, assistant/drafter and ExecuTorch repos, plus the gated Muse-Spark-Open-816B-A42B in BF16 and NVFP4 (HF search of meta-models). The DFlash drafter is a 5-layer speculative head, about 5 GB in BF16 and 1.6 GB as GGUF. It is not a standalone model (model card, vLLM recipe, official GGUF repo).

Builds that fit our hardware:
- Official Q4 GGUFs, 16.8 and 19.7 GB. These fit the Mac, a Spark, and the RTX PRO 6000 (official GGUF repo).
- Community builds: Unsloth GGUF (https://huggingface.co/unsloth/Muse-Glimmer-30B-GGUF), Unsloth bnb-4bit for QLoRA (https://huggingface.co/unsloth/Muse-Glimmer-30B-unsloth-bnb-4bit), MLX 4-bit (https://huggingface.co/mlx-community/Muse-Glimmer-30B-4bit), NVFP4 (https://huggingface.co/RadixArk/Muse-Glimmer-NVFP4) and FP8 (https://huggingface.co/RedHatAI/Muse-Glimmer-30B-FP8-block).
- A community pruned variant exists for English and Polish (https://huggingface.co/bluevoid-pl/Muse-Glimmer-30B-pruned-V2.5-en-pl-GGUF). Its quality is unreviewed.
- Several "abliterated" or "uncensored" community variants also exist (HF search). Using them would conflict with Usage Policy §1.1.8 on circumventing safety measures, so we skip them.

Nothing official fits the RTX 3080 10 GB in-GPU. For that card, Muse Glimmer means CPU offload at a few tok/s.

## Open gaps
- No published DGX Spark or Mac fine-tuning throughput for this model.
- No independent comparison against gpt-oss, DeepSeek V4 or Mistral found.
- The AA model page index value (v5.0.1) was not cleanly extracted.
- Muse Spark Open licence unread (gated).
- RTX PRO 6000 street price is volatile. Check retailers before buying.
