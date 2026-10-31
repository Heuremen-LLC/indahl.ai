# Notes on RATES.text (31 Oct 2026, after the outside referee)

RATES.text is the committed reader's output (read_bridge.py --rates), unchanged. These notes correct one label and add context.
Readings below marked "defined after the data" were not in PLAN.md or Addendum 1.

## First differing token position (L6), listed instead of "quartiles"
With n = 8, 3 and 9 the "quartiles" printed in RATES.text are index picks. Session 1 (session 2 is token-identical):
- Q4_K_M, divergent items 5, 45, 51, 52, 119, 138, 144, 163: positions 1, 1, 8, 43, 87, 107, 289, 419
- Q8_0, divergent items 37, 124, 129: positions 17, 266, 508
- Q3_K_M, divergent items 1, 12, 18, 80, 87, 124, 136, 168, 191: positions 0, 20, 24, 36, 41, 134, 144, 186, 332

## Her CUDA F16 row (defined after the data)
Her Table 7 F16 row is 7 of 200, 3.5% [1.7, 7.0] (rebuilt from her logs in scout/run_bridge.log). Metal minus that row, Newcombe 95%:
Q4_K_M +0.5 pp [-3.6, +4.6], Q8_0 -2.0 pp [-5.7, +1.3], Q3_K_M +1.0 pp [-3.1, +5.2]. All three are CONSISTENT with it.
No Metal F16 run exists (the Mac's memory rule beside another workload excludes the 14.19 GiB file), so whether quantization raises
cold-against-warm divergence on Metal is untested here.

## Correctness flips
0 flips among the divergent items by her Table 7 scorer in every format. By her run-time rule there is 1 (Q8_0 item 124: the cold reply has
no "####" line, the warm reply ends "#### 10", gold 10). At her own flips-per-divergent-item rates the expected number of flips on 8, 3 and
9 divergent items is about 0.4, 0.1 and 0.3, so these runs cannot say whether Metal flips correctness less often.

## Scope
Single-turn GSM8K bridge, 200 items, one seat (Apple M5 Max, Metal, macOS 26.6.2), llama.cpp tag b10434 (commit 7e4c0a968), two server
sessions per format. Every warm request hit the prompt cache for all but one prompt token (prompts are 69 to 179 tokens), so nothing here
bears on partial prefix reuse or on her agentic results. The session floor (0 of 200 on both paths) is two sessions on one machine.

## What the data rule out and what they cannot
Ruled out: a warm path that did not hit the cache (client fields and server logs agree on every request), session noise, prompt or tokenizer
mismatch (prompt sha256 and token counts equal hers on 200 of 200), truncation (finish reason stop on 800 of 800 per session).
Not ruled out, and no mechanism is named: which kernel or attention difference makes the Metal gap smaller than CUDA's; the effective
flash-attention state and the host prompt-cache round trip, which neither side logged.
