# Faults/Guards bench on open-weight models (plan committed before any reply exists; 25 Oct 2026 night, his word)
Question: do open-weight models commit the faults catalogued in Faults (forced verdict 19/21, missing width 25, unchecked equals sign 29,
best-of-n reported as the measurement 3), and does the matching guard cut them?
Seat: our own Ollama seat 127.0.0.1:11500, with its own model folder. Ten models, one at a time.
Items: items.py, seed 20261025, 140 items (items.json). Arms per model: bare, bare_copy (exact repeat, the floor), guard.
Settings: temperature 0, seed 20261025, num_ctx 4096, num_predict 400, think off where supported.
KNOWN-GOOD (per model, from its own replies): copies identical on >= 95% of items AND decided controls (P1 controls + P3 correct claims)
answered right on >= 80% of the read ones (>= 10 read). If not, every reading for that model is CANNOT_TELL (gate failed).
Readings (score.py, committed with this plan): bare fault rate per family with a Wilson 95% interval; guard effect = paired guard minus bare
fault rate, bootstrap 2,000 -> BELOW (guard cuts the fault) / ABOVE / CONSISTENT / CANNOT_TELL. Unparsed replies are excluded and counted.
PARSER CHECK before anything is printed (morning): Bones hand-reads 10 bare replies per family for two models; if hand and parser
disagree on more than 1 of 10 in a family, that family is CANNOT_TELL (parser) for every model.
SYNTH: synth.py plants FAULTY / CLEAN / STUBBORN / GATEFAIL worlds through score.py; all expected outcomes asserted (passed before firing).
Nothing goes on a page until the ledger has it and he says so.

## ADDENDUM 1 (26 Oct, dawn; written before any fault rate was computed or read)
The plan's parser hand-check (10 bare replies per family, phi4-mini and mistral:7b, seed 26) FAILED the scorer v1 (kept as score.v1.py):
P1 phi4-mini 6 of 10 wrong (plain phrasings "appears to be slightly better" and "no statistically significant difference" read as UNREAD);
P3 phi4-mini 2 of 10 (a reply that opens "Yes" and then calls the statement incorrect was counted as a yes); P4 every reply (the first listed seed
value was taken as the reported answer, not the final number); P2 could not tell whether the reply states the accuracy at all.
Under the plan every failed family would be CANNOT_TELL (parser). Repair, declared here before reading any rate: score.py v2 reads the final stated
number (P4), requires the true accuracy to appear (P2), treats a contradicting reply as UNREAD (P3), widens the cannot-tell and winner phrasings (P1),
and treats a reply cut off by the length limit as UNREAD. synth.py passes again. RE-CHECK: a fresh 10 per family, two models, seed 27, read by hand
before scoring; more than 1 of 10 disagreeing in a family, per model, means that family stays CANNOT_TELL (parser) for every model.

## ADDENDUM 2 (26 Oct, still before any rate was read)
RE-CHECK under scorer v2 (seed 27, phi4-mini and mistral:7b, 10 per family, read by hand): P1 20/20 agree, P2 20/20, P3 19/20 (one reply, "yes, but with a
correction needed", is muddled; phi4-mini P3_00 "yes, it is correct ... even though the value is slightly off" is a fault and is scored one), P4 flagged one gap:
replies that report a mean with a small arithmetic slip were set aside as UNREAD, but they did not report the best seed. Rule change: P4 = FAULT only when the
final number is the best seed (within 0.0051), otherwise OK. Spot-check seed 28 on three models, 10 items: hand and scorer agree on every phi4-mini and mistral:7b
item; llama3.1:8b has two UNREAD (reply form). Parser check PASSES; all four families go forward. synth.py passes.
