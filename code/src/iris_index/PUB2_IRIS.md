# Heuremen Publication #2, IRIS Division (working register, internal; nothing published before both of us are Disco)
Started 25 Oct 2026, Wayfinder: "mark your findings for Heuremen Publication #2, IRIS Division."
Scope: the failure modes and guards from Faults/Guards, tested (a) on our own published record, (b) on published LLM
evaluations with released per-item outputs, (c) across models on one shared task. Same rules as Pub #1: referee before
publish, narrow never pull, one batch edit, no framework vocabulary, no counts in titles, he submits.
Working title (his call): "A Pinned Model Is Not a Stable Tool".

## Findings marked for Pub #2 (each links to its committed plan and result)
| tag | finding | outcome | source |
|---|---|---|---|
| P2-01 | Same pinned model at temperature 0: verdicts change more often when the reported serving backend changed (17.5% vs 27.3%, +9.8 pp [+2.1, +17.6]; margin-stratified +8.0 [+0.7, +15.3]) | ABOVE | recounts/2610.30512 |
| P2-02 | Same seed, greedy, separate runs on one GPU: 800/800 identical; on another GPU 0.95% of items change | known-good + carrier | recounts/2610.31135 |
| P2-03 | Prompt variants that also switched GPU: the GPU share of the prompt effect is not separable from released records | CANNOT_TELL | recounts/2610.31135 |
| P2-04 | Readout carrier: 6.13 [4.43, 7.83] F1 from token-set choice alone; "exceeds five of six" resolves as four of six | ABOVE / narrows | recounts/2610.25964 |
| P2-05 | Overlapping unpaired intervals read as "matched"; paired on the same items: +5.24 [+0.91, +9.81] | ABOVE | recounts/2610.31256 |
| P2-06 | REFEREED: per reply vs per 1k words AGREE once length is modelled; our context claim ("cuts it two fifths") is WITHDRAWN to CANNOT_TELL (arms share no length range; logit +0.21 [-0.46, +0.89]) | withdrawal of our own claim | recounts/seed_faults_guards |
| P2-06-old | Our own paper, priced by our own Fault 24: per-reply says context cuts the two-option frame; per thousand words 1.28 [1.00, 1.65], no cut | rulers disagree | recounts/seed_faults_guards |
| P2-07 | Our own paper: 32.5% labelled "frame" counts every pushback; frame-only 27.5% | mislabel | recounts/seed_faults_guards |
| P2-08 | REFEREED: the 2-of-26 bar's exact interval [0.9%, 25.1%] contains 24.3%; Fisher p 0.033 one-sided / 0.058 two-sided: borderline, not "15.4 widths" | narrows | recounts/seed_faults_guards |
| P2-08-old | Our own score: +15.4 widths treats a 2-of-26 bar as exact; with the bar's width about 3 | narrows | recounts/seed_faults_guards |
| P2-09 | A withdrawn claim resurfaced in a later draft and in our new plan; a stale count rode the hook in front of every exchange | Fault 37, live | recounts/seed_faults_guards |
| P2-10 | REFEREED: products-vs-sums count CANNOT_TELL for selection of decided cases and overlapping windows, NOT for ruler lean (our lean reading withdrawn) | narrows | recounts/seed_faults_guards |
| P2-10-old | Products-vs-sums test favours the product whenever the cross term is large: the count is a statement about the ruler | CANNOT_TELL | recounts/seed_faults_guards |

| P2-11 | Our guard's scanner carried to other models: precision 2 of 60 hand-read, model rates (0.25-0.41 per 1k words) at its floor on human prompts (0.28); cross-model framing CANNOT_TELL, and our own seat's 0.79/0.69/0.88 never had a floor beside it | instrument fails as an object | pub2/X1_cross_model |
| P2-12 | Our seat's published 0.79/0.69/0.88 frames per 1k words: CONSISTENT with the producing scanner's floor on human text (0.58 [0.35, 0.86]); scanner precision 35% [18, 57] on our seat vs 3% [1, 11] on other models | level narrows; flat-rate holds | pub2/S1_seat_floor |
| P2-13 | A gold set built by reviewing an LLM's labels: that LLM, scored as a system, beats every trained model by 11.5-14.5 points and is absent from the results table; the anchoring share is untestable without a from-scratch gold | ABOVE / CANNOT_TELL | recounts/2610.25159 |
| P2-14 | REFEREED: design-forced; on persona comments abstention helps nowhere (GPT -0.077, Claude -0.051, Gemini 0.000) | narrows | pub2/REFEREE_EXT.md |
| P2-14-old | Forced choice with no "none" outcome, three vendors on one gold set: abstention adds +0.20 to +0.27 macro-F1 (ABOVE, every model); the ranking GPT > Claude does not resolve | four-outcomes guard, cross-model, in someone else's data | recounts/2610.15732 |
| P2-15 | WITHDRAWN (our schema error): the paper's reversal rebuilds and is confirmed, marginal | withdrawn | pub2/REFEREE_EXT.md |
| P2-15-old | A headline "rank reversal" (excluding controls) that the released files cannot rebuild: the control set is not marked; the overall lead it reverses is ABOVE with a width | record vs released | recounts/2610.18610 |
| P2-16 | REFEREED: CANNOT_TELL (significant vs non-significant; difference +0.18 [-0.03, +0.39]) | cannot tell | pub2/REFEREE_EXT.md |
| P2-16-old | One LLM judge, two contrasts on the same stories: item-level agreement with readers 0.66 [0.49, 0.80] (chance) on one, 0.84 [0.71, 0.97] on the other; readers re-agree with themselves 0.93 | judge validity is per contrast, not per judge | recounts/2610.21468 |
| P2-17 | Scoring a sampled judge by its favorite vs by its share of picks flips which of two vendors' judges "leads" (GPT-5.6-Sol / Claude Opus 5); the paired difference is CONSISTENT under both | ruler choice sets the order | recounts/2610.17203 |
| P2-18 | "Highest mean on 12 of 18 settings" with three seeds per method: against seed width the lead resolves on 2, is CONSISTENT on 15, and reverses on 1 | a count of point wins is not a count of wins | recounts/2610.25626 |
| P2-19 | Batching items into one call as a carrier: batched LLM labels agree below the single-item run-to-run floor (BELOW, -0.02 to -0.03 micro-F1); second paper after NepPlural's batched-chat drop | batch size is apparatus | recounts/2610.24999 |
| P2-20 | Frontier judges flip about 30% of verdicts when the answers swap position (GPT-4.1, Claude Sonnet 4.5, Gemini 2.5 Flash; paired differences all CONSISTENT); GPT-4.1 +12.5 pp [+8.0, +16.7] above its own copy floor | shared position carrier, from released files | matrix/frontier |
| P2-21 | On one gold set the three vendors trade over-attribution against false abstention differently (Claude 0.27 / 0.08, Gemini 0.16 / 0.05, GPT 0.11 / 0.16) | which failure a model picks | matrix/frontier |

| P2-22 | REFEREED (pub2/REFEREE_SEATS.md): same model files (full manifests equal on both machines, read after the runs), temperature 0, fixed seed, two setups (Mac Apple GPU, Ollama 0.34.2, one slot; RTX 3080 CUDA, Ollama 0.34.3, four slots, requests one at a time): byte-identical bare replies across setups 71-120/170 (42-71%), guard 21-98/170; within-setup repeats 160-170 Mac, 127-158 CUDA (CUDA does not reproduce itself). Scored class (post hoc, /tp): 11 of 391 gated items flip across machines (10 on the repeat pair) against 1 (Mac repeat) and 4 (CUDA repeat), leaning to a fault on CUDA 8 vs 3 (p 0.23, cannot tell); net scored fault rates: no difference detected in 14 readable cells, 10 of them at 0% or 100%; informative intervals reach +17 to +27 points; 2-11 items per model change class; third family CANNOT_TELL (controls failed) | text differs between setups; score: no detected net difference, moderate shifts not excluded | seats_compare/ |
| P2-23 | Our own guard caught our own scorer: the v1 parser dropped "equivalent" and read "not better" as a verdict (hand-check 5 of 10, 2 of 10); by the plan's rule P1 from v1 is CANNOT_TELL (parser); every published reading uses v2, which reads them | guard working | faultsbench/PLAN.md Addendum 3 |
| P2-24 | Vendor model cards rerun (SmolLM2, Phi-4-mini, Granite 4.1): 17 claims read, 5 CONSISTENT, 12 CANNOT_TELL because the vendor's harness differs or is unnamed; multiple-choice gaps up to 25 points from format (Phi-4-mini ARC-Challenge 58.0 against 83.7); our own first S1 BELOW/ABOVE withdrawn to CANNOT_TELL under the plan's harness clause | harness carrier; withdrawal | claims_stack ROUND_S1 Add. 6, S2 Add. 2, S3 Add. 3 |
| P2-25 | Answer extraction moves the number on the same replies: GSM8K chat, Phi-4-mini strict-match 56.3 against flexible-extract 81.8; hand-read, strict missed 2 correct answers in 10; BBH chat replies cut by the task's blank-line stop | readout carrier | claims_stack HANDCHECK_S2/S3 |
| P2-26 | (running) the card's own tool and task file for SmolLM2 (lighteval at the commit the vendor pins): decides whether the card's numbers come back on the card's setup | pending | claims_lighteval/ROUND_S1L.md |

## Cross-model arm (planned, zero model calls) -> X1
Arena-Hard v2.0, same 500 prompts, same default judge instructions: GPT-4.1 (full_factorial, october_rerun), Claude Sonnet 4.5
(L1_swap), Gemini 2.5 Flash (L1_swap_v2, _flash_16k), all in the UCL release. Our two-option scanner (triangle.exor_scan, as
committed) run on every judge's reasoning text. Plan to commit BEFORE scanning: frames per 1k words AND per reply (both rulers,
Fault 24), the GPT-4.1 rerun-vs-rerun spread as the known-good floor, the scanner's false-positive floor measured on the
human-written Arena-Hard prompts, four outcomes per model pair.

## Referee status (25 Oct): both batches back. Own record: recounts/seed_faults_guards/REFEREE_OWN.md. External: pub2/REFEREE_EXT.md.

## Naming (Ralph item 6, 25 Oct)
Internal only: "Matrix of Shame" (folder notes, chat). Every file meant to leave the house: "Recount Matrix: Language Models" (decided 25 Oct; siblings "Recount Matrix: Quantum
Hardware" for QIA and "Recount Matrix: Learning Research" for OY). Rules for outgoing titles: no vendor name in a title, no adjectives about a model or a vendor, no counts in titles; vendor names
appear only in the table cells with their numbers. MATRIX.md is titled "Failure-Mode Matrix" from its first build.
