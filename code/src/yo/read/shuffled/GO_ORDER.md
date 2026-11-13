# Run order (internal run sheet, 4 Nov 2026; NOT an addendum, not stamped, so it moves no block). Sage's ordering rule.
Every start time below is read from the file or process record (stat / log line), never from memory.
SHUFFLED arm: plan + Addendum 1 blocks confirmed (block time read on mempool.space) -> then train shuf1, shuf2, shuf3, one GPU job at a time.
SELF-LABEL arm: the LATEST of the plan and Addenda 2-5 has a confirmed block whose time precedes the start of the BASE-RATE REPORT, which is
  the first touch of the real items (running the base model on train/valid prompts) -> base-rate + drop-count report written -> then train
  self1, self2, self3. No self-label generation of any kind before that block.
No further addenda unless something breaks (each one resets the latest block this arm waits on).
