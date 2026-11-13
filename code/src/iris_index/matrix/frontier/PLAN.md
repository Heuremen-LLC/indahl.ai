# Frontier columns from RELEASED data only (Ralph item 4). Committed before computing. Separate from our seat's columns; every cell
# names its source paper and its definition; no model calls.
F-M1 over-attribution / false abstention: NepPlural (2610.15732) results/abstention_baseline/{gpt,gemini,claude}.jsonl vs gold_final:
     share of the 116 gold No-Persona comments given a persona; share of the 184 persona comments abstained. Same rule as our M1.
F-M2 copy floor: UCL (2610.30512) GPT-4.1 pinned, default setup, October run1 vs run2: share of prompts whose candidate-relative score
     sign differs (their boundary change) and any-tier change. Only GPT-4.1 has identical copies; others CANNOT_TELL for M2.
F-M3 option order: UCL default setup, each judge's round1 vs round2 (answer order swapped), per prompt: share whose verdict sign
     differs after mapping to the candidate. GPT-4.1 (full_factorial, May), Claude Sonnet 4.5 (L1_swap), Gemini 2.5 Flash
     (L1_swap_v2_flash_16k), Gemini 2.5 Pro (L1_swap_v2, n 129). Read against F-M2 for GPT-4.1 only (the only floor); for the others
     the flip share is printed with "no copy floor": its outcome vs a floor is CANNOT_TELL.
F-M5 format: UCL GPT-4.1 October, the seven instruction setups vs default: their Table 1 (recounted CLEAN) as the format carrier.
Statistics: prompt bootstrap 2,000 (seed 20261025); judge-vs-judge flip differences paired over shared prompts, four outcomes, marginal
flagged. Caveat in advance: the frontier judge task (pairwise preference with ties) is not our MCQ task; columns are not comparable to the
seat's numbers, only to each other within a row.
