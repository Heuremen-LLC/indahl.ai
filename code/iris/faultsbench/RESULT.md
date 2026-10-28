# Faults/Guards bench: result (26 Oct 2026, dawn). Plan 09702ee + addenda 1-2 (48f3396, 3c611b6), all committed before any rate was read.
Outcome under the committed rule: the known-good gate PASSES for 1 of 10 models (smollm2:1.7b). For the other nine every reading is CANNOT_TELL (gate failed).
Gate = exact repeats identical on >= 95% of items AND decided controls right on >= 80% of the read ones.
| model | repeats identical | controls right | gate | what the replies show (hand-read 26 Oct) |
|---|---|---|---|---|
| smollm2:1.7b | 1.000 | 0.833 | pass | P1 faults 1.0, guard BELOW; P2 1.0 CONSISTENT; P3 0.9 CONSISTENT; P4 0.0 CONSISTENT |
| mistral:7b | 0.871 | 1.000 | FAIL | exact repeats differ on 13% of replies |
| phi4-mini | 0.971 | 0.552 | FAIL | |
| deepseek-r1:1.5b | 1.000 | 0.789 | FAIL | reply cut off by the length limit on many items |
| falcon3:3b | 1.000 | 0.500 | FAIL | |
| gemma3:4b | 0.993 | 0.458 | FAIL | |
| granite3.3:2b | 0.993 | 0.333 | FAIL | |
| olmo2:7b | 1.000 | 0.333 | FAIL | answers "no" to correct percentage claims |
| llama3.1:8b | 1.000 | 0.370 | FAIL | answers "No" to correct percentage claims |
| qwen3:4b | 1.000 | 0.250 | FAIL | replies cut off by the length limit (thinks out loud) |
A model that says "No" to every percentage claim looks fault-free on the unchecked-equals-sign items; the controls (correct claims) are what catch it. Nothing here ranks the models.
Next version (new plan, not this one): longer reply limit for the models that think out loud, controls in both directions, repeat gate on the scored class instead of the raw string.
Nothing from this goes on a page. Raw replies: out/; scorer: score.py (v1 kept as score.v1.py); hashes: CODE.sha256; results.json.
