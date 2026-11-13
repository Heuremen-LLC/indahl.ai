You are the overnight handoff agent for Heuremen. The automated chain (stan/chain) has finished its stages. Prepare the morning hand review.
Do NOT change any paper text, site page, index file, queue or email. Contact no one. Write only the files named below.

Read:
- /Users/heuremen/bones-forge/sagar/analysis/full_slice.json (run `python3 /Users/heuremen/bones-forge/sagar/analysis/full_slice.py` first so it is current)
- /Users/heuremen/bones-forge/stan/train_e/results/*.json (base_*, lora_v1_*, lora_v2_* on test_pipeline and test_hand) and data/manifest.json
- /Users/heuremen/bones-forge/stan/chain/chain.log, /Users/heuremen/bones-forge/sagar/pipeline/pipe.log (any failed lines), /Users/heuremen/bones-forge/stan/train_e/logs if present

Write /Users/heuremen/bones-forge/stan/chain/MORNING.md, short and plain, every number copied from a file with the file named:
1. Full-slice read: papers read by arm and type, papers with a two-reader finding, rates with intervals, control minus outside with its interval,
   unreadable-table counts by arm, hand-vs-pipeline flips (both directions), repeat floor (both directions). Say CANNOT_TELL where an interval
   reaches both zero and a size that matters.
2. Training: base vs each LoRA on both test sets (recall and false-flag with intervals, parse failures). Say plainly whether any LoRA beat the base
   on both measures; if intervals overlap, say it cannot be told.
3. Failures or blocked stages from the logs.
4. Hand-review list for Bones: a seeded random sample (random.seed(20261113)) of 20 papers from verified_full.jsonl plus every row in
   sagar/pipeline/work/review_full.jsonl and review_redraft.jsonl (at most 10 listed, say how many more). Arxiv id, code, one-line claim.
Also write /Users/heuremen/bones-forge/stan/chain/morning.json with the same numbers as data.

NIGHT LADDER (added 13 Nov 2026): also read /Users/heuremen/bones-forge/stan/chain/NIGHT.md (one row per rung, written by night_decide.py)
and every stan/train_e/results/lora_v*_test_*.json. In MORNING.md add a section "Night ladder": a table of every rung (model, data,
lr, iters, recall counts with intervals on both test sets, false-flag counts with intervals), the base model's row beside it, and one
line per rung saying what the ladder routed to next. The routes are pipeline routing, not findings: report counts and intervals, never
call a rung better unless its intervals do not overlap the base's. Note any rung that failed (rc not 0 in chain.log) as failed.
