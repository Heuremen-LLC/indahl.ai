# MODEL HUNT: base for the triangulated token model
Date: 2026-10-06. Read-only web research. Model ids, parameter counts, licenses and configs were read from the live Hugging Face pages/configs on 6 Oct 2026. Anything not verified is marked UNVERIFIED.

## 0. The one thing to read first: the Anthropic terms problem

The planned training data (exported Claude.ai conversations) runs straight into Anthropic's terms. Full clause text is in section 4. Short version: the Consumer Terms bar using the Services "to develop or train any artificial intelligence or machine learning algorithms or models", with no private / non-commercial carve-out in the clause text. Anthropic's own support article names "General purpose chatbots", "Models designed for open-ended text generation" and "Using Outputs as training targets for models" as prohibited, and lists narrow non-competing tools (sentiment analysis, classification, summarization, extraction, search, anomaly detection) as permitted. A companion chat model trained on Claude's replies sits in the prohibited column on a plain reading. Section 4 lists designs that avoid Claude outputs as training targets. This is not legal advice; written permission from Anthropic is the only clean path for the chat-model version.

## 1. Recommendation

Top pick: Qwen/Qwen3-4B-Instruct-2507. Runner-up: allenai/Olmo-3-7B-Instruct (start from its -SFT or -DPO checkpoint). Third, the small fast option: ibm-granite/granite-4.2-3b.

Why: the experiment's novelty is the decoding rule (three seats, agreement gate, four output modes), not the base, so pick the base that gets out of the way. Qwen3-4B-Instruct-2507 is Apache-2.0, a plain dense text-only causal LM (Qwen3ForCausalLM), non-thinking (no think-tag interference with a mode token), 262,144 native context, and its KV cache is small (36 layers, 8 KV heads, head_dim 128 = about 147 KB per token fp16, so three 8k-token seats cost about 3.6 GB; my arithmetic from the config). A 4-bit copy of the weights is about 2.5-3 GB, so a three-seat batched decode fits on the 3080 with room left. Every stack in the brief supports it (transformers, TRL, PEFT, Unsloth (Qwen3-4B listed; the 2507 variant not listed by name in the catalog page I read, but same architecture), llama.cpp, vLLM, MLX, Ollama). Olmo 3 is the runner-up because it is the only fully open pipeline (Dolma 3 data, Dolci post-training data, code, checkpoints) with separate SFT / DPO / RL checkpoints, which is ideal for a preference-tuning experiment where you want to know what the base already learned. Its costs: 7B on 10 GB leaves little room, and it uses full multi-head KV (32 KV heads), about 16 KB per layer-token, so three long seats get expensive (UNVERIFIED arithmetic: roughly 2.6 GB per seat at 8k tokens including the sliding-window layers). Newer families (Qwen3.5, Gemma 4) are better models but are worse fits for this 10 GB, hack-the-logits experiment; see the table notes.

## 2. Candidate table

All licenses/ids/params read from the HF model pages (6 Oct 2026). "QLoRA fits 10 GB" is my judgment from sizes plus the cited vendor guidance unless a source is given.

| Model (HF id) | Params | License | Context | QLoRA on 10 GB 3080 | Tooling | Conversation / empathy evidence | Notes |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-4B-Instruct-2507 | 4.02B | apache-2.0 | 262,144 (config) | Yes, comfortable (4B, 4-bit) | transformers, TRL, PEFT, Unsloth (Qwen3-4B), llama.cpp/GGUF, vLLM, MLX, Ollama | None found. No EQ-Bench/empathy rows verified | TOP PICK. Dense, text-only, non-thinking |
| allenai/Olmo-3-7B-Instruct (also -Instruct-SFT, -Instruct-DPO, base allenai/Olmo-3-1025-7B) | 7.30B | apache-2.0 | 65,536 (config max_position_embeddings) | Yes at short seq (7B 4-bit about 4.5-5 GB weights); tight at long seq | transformers 4.57+, vLLM, SGLang, TRL/PEFT; an unsloth/Olmo-3-7B-Instruct repo exists but Olmo 3 is NOT in Unsloth's catalog page I read (UNVERIFIED support) | None found | RUNNER-UP. Fully open data + checkpoints; card says "research and educational" use guidelines. KV cache heavy |
| ibm-granite/granite-4.2-3b (and -8b) | 3.66B (8B: 8.79B) | apache-2.0 | 131,072 | 3B easy; 8B yes at short seq | transformers, MLX builds exist; NOT in Unsloth catalog page I read; TRL/PEFT generic | None found | Dense GQA, thinking on by default (toggle). Released Aug-Sep 2026. 3B: 40 layers, 8 KV heads, head_dim 64 = about 82 KB/token |
| google/gemma-4-E4B-it (base: google/gemma-4-E4B) | 4.5B effective, 8.0B total with per-layer embeddings | apache-2.0 (HF tag and card; Gemma 3 and earlier were the restrictive "gemma" license) | 131,072 | Borderline: Unsloth says E4B QLoRA about 10 GB | transformers 5.x, Unsloth (SFT/DPO/GRPO), llama.cpp GGUF (unsloth), litert | None found | Multimodal wrapper (Gemma4ForConditionalGeneration), vision/audio towers add complexity. Cheap KV (sliding window 512, 2 KV heads) |
| Qwen/Qwen3.5-4B (also -2B, -9B; Base variants exist) | 4.66B (9B: 9.65B; 2B: 2.27B) | apache-2.0 | 262,144 | NO via QLoRA: Unsloth says "not recommended to do QLoRA (4-bit) on Qwen3.5"; bf16 LoRA 4B needs about 10 GB (too tight on a 3080 that also drives Windows). 2B bf16 LoRA about 5 GB fits | transformers, Unsloth, vLLM, llama.cpp, Ollama | None verified (card shows IFEval 91.5 for 9B, no empathy rows) | Hybrid Gated-DeltaNet + attention (only 8 of 32 layers full attention, so KV is tiny, about 32 KB/token), thinking ON by default, multimodal wrapper. Best raw quality per GB, but recurrent state per seat and QLoRA warning make it a worse first base |
| mistralai/Ministral-3-8B-Instruct-2512 (3B and 14B too; base Ministral-3-8B-Base-2512) | 8.9B (8.4B LM + 0.4B vision) | apache-2.0 | 256k | 3B yes; 8B at short seq | vLLM (recommended), transformers via mistral-common, Unsloth lists Ministral 3 | None found | Vision encoder attached. Mistral's current small-model line; Mistral Small 4 is 119B (not usable here) |
| microsoft/Phi-4-mini-instruct | 3.84B | MIT | 128K | Yes | transformers (custom_code tag), Unsloth lists Phi-4-mini, llama.cpp, MLX | Card itself warns of repetitive/inconsistent output in very long chat sessions | Fully permissive but weakest fit for a companion |
| HuggingFaceTB/SmolLM3-3B (base: SmolLM3-3B-Base) | 3.08B | apache-2.0 | 64k native, 128k via YaRN | Yes | transformers, llama.cpp, MLX; not in Unsloth catalog page I read | None found | Fully open data/recipe; `/think` `/no_think` toggle |
| google/gemma-3-4b-it | 4.3B | "gemma" license (gated; restrictive terms) | 128K (UNVERIFIED, not re-read) | Yes | all stacks | None found | Superseded by Gemma 4 (Apache-2.0). Skip |
| Llama 3.2 3B / 3.1 8B | 3B / 8B | Llama community license (HF tag license:llama3.2); acceptable-use policy, attribution, MAU cap | 128K (UNVERIFIED) | Yes | all stacks | None found | Not fully open; no reason to prefer it now |

Empathy/conversation benchmarks: I could not retrieve per-model scores for any candidate. eqbench.com's current page is EQ-Bench 4 and its leaderboard table loads dynamically (not retrievable by my fetcher); EQ-Bench 3 is judged by an LLM and its public rows I could see were large frontier models only. Treat "empathy quality" as UNVERIFIED for every candidate and plan to run your own eval (section 3, step 6). Note that EQ-Bench-style judges reward warmth, which is the failure mode this experiment is trying not to optimize.

## 3. Best implementation route on one RTX 3080 (10 GB, Windows)

Recommended: Route A (logit-level three-seat decode) as the core, plus a thin Route C (small DPO/SFT pass) to teach the four-mode lead token. Route B is a later option. Mac is excluded as stated.

### Concrete stack
- Base: Qwen/Qwen3-4B-Instruct-2507 loaded in 4-bit NF4 (bitsandbytes) or a Q4/Q5 GGUF.
- Inference/decoding: Hugging Face transformers with a hand-written decode loop (not `generate()`), PyTorch + CUDA on Windows. Batch the three seats as one batch of 3 (left-padded) so one forward pass per step produces three next-token distributions. Per-step logits are plain tensors, so you can combine them any way you like.
- Training (if you do Route C): Unsloth on native Windows (Conda; RTX 30-series supported per Unsloth's Windows page) with TRL `SFTTrainer` / `DPOTrainer` underneath, QLoRA r=16, short sequences (1-2k), gradient checkpointing on, batch size 1 with accumulation. PEFT DPO needs no second model in memory (adapter-disabled reference). Fallback if Unsloth gives trouble on Windows: plain TRL + PEFT + bitsandbytes.
- vLLM only via WSL2 or Docker (no native Windows). Not needed for the experiment.

### Route A: how to build it
1. Seat contexts. S1 = message only. S2 = message + baseline summary (a few hundred tokens: normal register, typical topics, how they usually talk when fine). S3 = message + last N turns (trajectory). Same system prompt in all three. Keep the baseline as a compact text block, not raw history, to hold KV cost down.
2. Per step, get logits l1, l2, l3 (shape 3 x vocab). Convert to log-probs.
3. Combine: product-of-experts / log-linear pool, `logp = sum_i w_i * log_softmax(l_i)`, renormalize, then sample (temperature/top-p on the pooled distribution). This is the "generate where they agree" half: tokens that all seats support get amplified, tokens only one seat likes get suppressed. Contrastive variants (context-aware decoding: `(1+a)*l_with_context - a*l_without`) are a one-line change if you want S2/S3 to subtract S1.
4. Agreement gate (the "ask a question" half). Compute disagreement, for example mean pairwise Jensen-Shannon divergence between the three next-token distributions, or the entropy of the pooled distribution minus the mean seat entropy. Measure it on the first token of the reply (and optionally a running average over the first k tokens). Above threshold = seats disagree about how to open = switch to ASK mode.
5. Four modes as a control token. Fine-tune (small SFT, then DPO) so the model begins each reply with one of four mode tags: PRESENT / HELP / ASK / HELP+STAY. Then the three seats' distributions over that single mode-tag position are a clean, low-dimensional place to measure agreement (this is my design suggestion, not from a paper). Agreement on the tag: commit to it and decode the body with the PoE pool. Disagreement: force ASK and decode one plain question from the pooled distribution.
6. Eval before believing it. Keep S1-only, single-pass and "baseline-in-prompt" (S2-only) as comparison arms. Score all arms on a held-out set of turns where a keyword (sadness, tired, etc.) appears but baseline and trajectory say it is ordinary; measure worst-case-script rate, question rate, and a human blind rating. Score with every ruler, not one.

KV memory check for Qwen3-4B-Instruct-2507 fp16 (my arithmetic from config.json: 36 layers, 8 KV heads, head_dim 128): about 147 KB/token. S1 at 1k tokens + S2 at 3k + S3 at 6k is under 1.5 GB of KV in total. Weights 4-bit about 2.5-3 GB. Total well under 10 GB even with Windows display overhead. For a 7B base (Olmo 3) use shorter seats or a quantized KV cache.

### Existing code and papers to reuse (verified titles/venues via arXiv abstract pages)
- Context-aware decoding (contrast with vs without context): Shi et al., "Trusting Your Evidence: Hallucinate Less with Context-aware Decoding", https://arxiv.org/abs/2305.14739. Seat-2/3 vs seat-1 is exactly this pattern.
- Classifier-free guidance for LMs: Sanchez et al., "Stay on topic with Classifier-Free Guidance", https://arxiv.org/abs/2306.17806. In transformers: `UnbatchedClassifierFreeGuidanceLogitsProcessor` (guidance_scale, unconditional_ids), https://huggingface.co/docs/transformers/main/en/internal/generation_utils. It takes ONE unconditional context; for three seats you write your own processor or loop.
- Product-of-experts style decoding with experts and anti-experts: Liu et al., DExperts (ACL 2021), https://arxiv.org/abs/2105.03023.
- Contrastive decoding: Li et al. (ACL 2023), https://arxiv.org/abs/2210.15097.
- Decoding-time tuning by logit offset: Liu et al., "Tuning Language Models by Proxy" (COLM 2024), https://arxiv.org/abs/2401.08565. Closest template for "difference of two models' logits shifts a third".
- Token-level ensembling every step: Yu et al., "Breaking the Ceiling of the LLM Community by Treating Token Generation as a Classification for Ensembling" (EMNLP 2024), https://arxiv.org/abs/2406.12585.
- Self-consistency (sample many, take the consensus): Wang et al. (ICLR 2023), https://arxiv.org/abs/2203.11171. Sequence-level cousin; costs N full generations.

### Inference stack comparison for per-step logit access
| Stack | Per-step logits | Verdict for this box |
|---|---|---|
| transformers (PyTorch, Windows native) | Full: custom loop or `LogitsProcessor` subclass (`transformers.LogitsProcessor` is the base class) | USE THIS. Batch of 3 seats in one forward pass. Slowest of the options but fine at 4B |
| llama.cpp C API | Full logits per sequence, multiple sequences per context | Faster, but you write C/C++ (or bindings) |
| llama-cpp-python | `logits_processor: Optional[LogitsProcessorList]` on `Llama.__call__`/`create_completion` (read from its API reference); constructor has `lora_path`, `lora_scale`, `n_gpu_layers` | Works for one sequence per Llama object. Three seats = three contexts or a manual eval loop. Current maintenance and Windows CUDA wheel status UNVERIFIED |
| llama.cpp server | Returns top-probs only; no mixing across slots | Not for logit-level pooling |
| Ollama | `logprobs` / `top_logprobs` on output only; no raw logits, no injection (Ollama API reference) | Not usable for route A. Fine for serving the finished model |
| vLLM | Custom logits processors work at batch-row level; a processor cannot see other requests' rows, so cannot pool three requests (docs: custom_logitsprocs) | Not suited to cross-sequence pooling unless you pack the three seats into one request's n-way sampling; also needs WSL2/Docker on Windows |
| MLX (mlx-lm) | Has logits-processor hooks (UNVERIFIED, not re-read) | Mac only, and the Mac is off limits |

### Route B: one base + three LoRAs
- vLLM: multi-LoRA with `--enable-lora --lora-modules name=path --max-loras N --max-lora-rank R`; adapter chosen per request via the `model` field; runtime load/unload with `VLLM_ALLOW_RUNTIME_LORA_UPDATING=True` (https://docs.vllm.ai/en/latest/features/lora/). Needs WSL2/Docker on Windows.
- llama.cpp server: `--lora` / `--lora-scaled`, `--lora-init-without-apply`, per-request `lora: [{"id":0,"scale":0.5}, ...]`; but "requests with different LoRA configurations will not be batched together" (https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md). Native Windows OK.
- LoRAX (https://github.com/predibase/lorax): per-request adapter loading, Apache-2.0; README lists Llama, Mistral, Qwen families. Qwen3 / Gemma 4 / Olmo 3 support UNVERIFIED; I would not bet on it.
- mlx-lm: documents LoRA/DoRA/full training only; I found no multi-adapter serving in its docs. Mac only anyway.
- Ollama: Modelfile ADAPTER not documented in the API reference I read; no per-request adapter swap.
Why B is not first: the seats differ in CONTEXT, not in weights. Three LoRAs would add three training runs to learn something the prompt already provides, and still need a combiner. Use B only if S2/S3 turn out to need a learned "how to read a baseline/trajectory" skill.

### Route C: preference fine-tuning on 10 GB
| Trainer | Status (verified from docs) | Fit |
|---|---|---|
| Unsloth | DPO, ORPO, KTO supported with QLoRA (https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/preference-dpo-orpo-and-kto); native Windows (Conda) supported; Gemma 4 guide lists SFT/DPO/GRPO trainers | Best on 10 GB. Check your exact base is in its supported list (Qwen3-4B yes; Olmo 3 and Granite 4.x not in the catalog page I read) |
| TRL | `DPOTrainer`, `KTOTrainer` stable; `ORPOTrainer` experimental; QLoRA via `quantization_config` + `peft_config`; `precompute_ref_log_probs` saves memory; dataset format `prompt/chosen/rejected` (conversational supported) (https://huggingface.co/docs/trl/dpo_trainer) | Solid fallback; generic across all models |
| Axolotl | DPO, IPO, KTO, ORPO listed (https://docs.axolotl.ai/); Windows/WSL notes UNVERIFIED | Workable, heavier config |
| torchtune | DPO + QLoRA supported but "no longer actively maintained: torchtune development wound down in 2025" (https://github.com/pytorch/torchtune) | Skip |
| mlx-lm (Apple) | Official LORA.md lists lora/dora/full only | Mac only, unavailable |
| mlx-lm-lora (third party) | DPO, ORPO, CPO, GRPO, etc. (https://github.com/Goekdeniz-Guelmez/mlx-lm-lora) | Mac only, unavailable |

Practical settings: QLoRA r=16, seq 1-2k, batch 1, grad-accum 8-16, lr about 1e-5 for adapters (TRL docs), beta 0.1. Qwen3.5 is the exception: Unsloth recommends bf16 LoRA, not QLoRA.

Pair construction note (relevant to section 4): "chosen = stayed with what the person asked; rejected = inferred the worst branch". Both sides can be produced by the open model itself (sample several replies, label with your own rubric or by hand) instead of copying Claude's replies. That keeps Claude outputs out of the training targets.

### Cloud (only if a 4B QLoRA proves too slow; needs approval)
Not needed for the recommended plan. A 24 GB GPU rental for a few hours is the usual size for 7-9B bf16 LoRA (about 10-30 USD for a pilot; UNVERIFIED price estimate, no vendor quote fetched).

### Research on clarification triggers and multi-perspective deliberation (Route D; abstracts verified)
- Zhang & Choi, "Clarify When Necessary: Resolving Ambiguity Through Interaction with LMs": intent-sim, uncertainty as entropy over simulated user intents decides when to ask. https://arxiv.org/abs/2311.09469
- Kuhn, Gal, Farquhar, "CLAM: Selective Clarification for Ambiguous Questions with Generative Language Models": detect ambiguity, ask only when needed. https://arxiv.org/abs/2212.07769
- Kobalczyk et al., "Active Task Disambiguation with LLMs": Bayesian experimental design to pick questions with maximal information gain. https://arxiv.org/abs/2502.04485
- Du et al., "Improving Factuality and Reasoning in Language Models through Multiagent Debate": several instances debate over rounds. https://arxiv.org/abs/2305.14325
- Wang et al., "Unleashing the Emergent Cognitive Synergy in Large Language Models: A Task-Solving Agent through Multi-Persona Self-Collaboration" (Solo Performance Prompting, NAACL 2024): one model, several personas. https://arxiv.org/abs/2307.05300
None of these uses seat-disagreement across different context windows as the trigger; that part is new. Closest in spirit: CAD (with/without context) plus intent-sim (entropy as the ask signal).

## 4. Anthropic terms: what they say about training on Claude outputs

Sources read 6 Oct 2026. The Consumer Terms page I fetched shows "Effective Date: October 8, 2025" (no newer version found; the 2026 update I found was to the Privacy Policy, effective 8 July 2026, not the Terms). The Usage Policy page shows "Effective Date: September 15, 2025". The fetcher paraphrases pages through a small model, so check the quoted text against the live page before relying on it.

1. Consumer Terms of Service, https://www.anthropic.com/legal/consumer-terms ("Use of our Services"). Lead-in: "You may not access or use, or help another person to access or use, our Services in the following ways:" and among the items:
   > "To develop any products or services that compete with our Services, including to develop or train any artificial intelligence or machine learning algorithms or models or resell the Services."
   Outputs: "Subject to your compliance with our Terms, we assign to you all of our right, title, and interest—if any—in Outputs." So you own the exports, but ownership is expressly subject to compliance with the above.
2. Usage Policy, https://www.anthropic.com/legal/aup ("Do Not Abuse our Platform"), prohibited:
   > "Utilization of inputs and outputs to train an AI model (e.g., 'model scraping' or 'model distillation') without prior authorization from Anthropic"
3. Anthropic Support, "Can I use my Outputs to train an AI model?", https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model
   > "We prohibit customers from using our services to train or develop AI models without our written permission."
   > "You can use Claude's Outputs to train models that don't compete with Anthropic's own models."
   Permitted examples listed: "Sentiment analysis tools," "Content categorization systems," "Summarization tools," "Information extraction tools," "Semantic search tools," "Anomaly detection tools."
   Prohibited examples listed: "General purpose chatbots," "Models designed for open-ended text generation," "Using Outputs as training targets for models," "Reverse engineering training methods."
   (The article does not itself say which of Consumer vs Commercial terms it applies to.)

What this means for the plan, stated plainly:
- Nothing I found carves out private or non-commercial use. The Consumer Terms clause and the Usage Policy line are written without that exception. The support article's test is "competing", and its examples put a companion/chat model (open-ended text generation, general-purpose chatbot, Claude outputs as training targets) in the prohibited group. Private, non-commercial use makes enforcement less likely; it does not change what the text says.
- Designs that stay clearly inside the support article's permitted list or avoid Claude outputs as targets:
  a. Train only on the person's OWN messages (their side of the export) to build the S2 baseline and S3 trajectory machinery; do not train on Claude's replies. The Usage Policy line says "inputs and outputs", so whether your own messages count as "inputs" under it is a reading question; the Consumer Terms clause is about the Services being used to develop models, and your own writing is your own. UNVERIFIED which reading Anthropic takes.
  b. Build the seat tools as narrow classifiers or detectors (register drift, trajectory change, "keyword vs context" flag); that matches the permitted "sentiment analysis tools / anomaly detection tools" examples. A detector that gates a separately built chat model is still part of a chat system, so this is a gray area.
  c. Generate chosen/rejected replies with the open model (or write them yourself) and use the Claude exports only as test prompts / evaluation, not as training targets.
  d. Ask Anthropic for written permission (the policy text itself names "written permission" as the route). This is the only unambiguous path for training a chat model on Claude outputs.
- The Consumer Terms effective date I could read is a year old; confirm nothing newer has replaced it before relying on any of this.

## 5. Sources (all fetched 6 Oct 2026 unless noted)

Models (Hugging Face; ids, params, license tags verified from the pages/configs)
- https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 (apache-2.0, 4022.5M, config read)
- https://huggingface.co/Qwen/Qwen3-8B (apache-2.0, 8190.7M)
- https://huggingface.co/Qwen/Qwen3.5-4B , https://huggingface.co/Qwen/Qwen3.5-9B , https://huggingface.co/Qwen/Qwen3.5-2B (apache-2.0; 4659.9M / 9653.1M / 2274.1M; config read; 262,144 ctx; thinking default on)
- https://huggingface.co/allenai/Olmo-3-7B-Instruct , https://huggingface.co/allenai/Olmo-3-7B-Instruct-SFT , https://huggingface.co/allenai/Olmo-3-7B-Instruct-DPO , https://huggingface.co/allenai/Olmo-3-1025-7B (apache-2.0, 7298.0M; config read: 65,536 positions, 32 KV heads, 3:1 sliding/full attention)
- https://huggingface.co/google/gemma-4-E4B-it , https://huggingface.co/google/gemma-4-E4B , https://huggingface.co/google/gemma-4-12B-it (apache-2.0; E4B 4.5B effective / 8.0B total; 128K; config read)
- https://huggingface.co/google/gemma-3-4b-it (license: gemma; gated)
- https://huggingface.co/ibm-granite/granite-4.2-8b , https://huggingface.co/ibm-granite/granite-4.2-3b (apache-2.0; 8.79B / 3.66B; 131,072 ctx; config read)
- https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512 , https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512 , https://huggingface.co/mistralai/Ministral-3-8B-Base-2512 (apache-2.0; 256k)
- https://huggingface.co/microsoft/Phi-4-mini-instruct (MIT, 3.84B, 128K)
- https://huggingface.co/HuggingFaceTB/SmolLM3-3B , https://huggingface.co/HuggingFaceTB/SmolLM3-3B-Base (apache-2.0)
- Llama 3.2 license tag seen in HF search results (license:llama3.2), page not opened.

Training / serving tools
- Unsloth Qwen3.5 fine-tune guide (QLoRA warning, VRAM table): https://unsloth.ai/docs/models/qwen3.5/fine-tune
- Unsloth Gemma 4 guide (E4B QLoRA about 10 GB): https://unsloth.ai/docs/models/gemma-4/train
- Unsloth Windows install: https://unsloth.ai/docs/get-started/install/windows-installation
- Unsloth model catalog: https://unsloth.ai/docs/get-started/unsloth-model-catalog
- Unsloth DPO/ORPO/KTO: https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/preference-dpo-orpo-and-kto (from search result summary; page itself not opened)
- TRL index and DPO trainer: https://huggingface.co/docs/trl/index , https://huggingface.co/docs/trl/dpo_trainer
- Axolotl: https://docs.axolotl.ai/
- torchtune (unmaintained): https://github.com/pytorch/torchtune
- mlx-lm LoRA doc: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md ; mlx-lm-lora: https://github.com/Goekdeniz-Guelmez/mlx-lm-lora
- transformers generation utils: https://huggingface.co/docs/transformers/main/en/internal/generation_utils
- vLLM custom logits processors: https://docs.vllm.ai/en/latest/features/custom_logitsprocs/ ; multi-LoRA: https://docs.vllm.ai/en/latest/features/lora/ ; Windows note: https://docs.vllm.ai/en/latest/getting_started/installation/gpu/
- llama.cpp server README: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama-cpp-python API: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/ ; repo https://github.com/abetlen/llama-cpp-python
- LoRAX: https://github.com/predibase/lorax
- Ollama API (logprobs only): https://docs.ollama.com/api/generate

Papers (arXiv abstract pages)
- https://arxiv.org/abs/2305.14739 , https://arxiv.org/abs/2306.17806 , https://arxiv.org/abs/2105.03023 , https://arxiv.org/abs/2210.15097 , https://arxiv.org/abs/2401.08565 , https://arxiv.org/abs/2406.12585 , https://arxiv.org/abs/2203.11171 , https://arxiv.org/abs/2311.09469 , https://arxiv.org/abs/2212.07769 , https://arxiv.org/abs/2502.04485 , https://arxiv.org/abs/2305.14325 , https://arxiv.org/abs/2307.05300

Anthropic terms
- https://www.anthropic.com/legal/consumer-terms
- https://www.anthropic.com/legal/aup
- https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model

Benchmarks (could not extract per-model rows)
- https://eqbench.com/ (EQ-Bench 4 page; table loads dynamically)
- https://github.com/EQ-bench/eqbench3

## 6. Not verified (summary)
- Any empathy / EQ-Bench score for any candidate.
- Olmo 3, Granite 4.x, SmolLM3 and Qwen3-4B-Instruct-2507 (by exact name) in Unsloth's supported list.
- Gemma 3 and Llama 3.x context lengths; Llama 3.x license details beyond the HF tag.
- llama-cpp-python current maintenance and Windows CUDA wheels; mlx-lm logits-processor hooks.
- Cloud pricing figure.
- Whether the Usage Policy's "inputs and outputs" covers your own side of the conversation.
- KV-cache sizes are my arithmetic from each model's config.json (fp16 cache), not measured.
- Real VRAM headroom on the 3080 with Windows driving a display; measure before committing to 7B+ or to Gemma 4 E4B QLoRA.
