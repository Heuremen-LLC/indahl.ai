# F2 silver hand read (Bones, 12 Nov 2026), Sage's precondition for pilot B

Seeded sample (random.Random(1112) shuffle of data/silver_v2/silver_all.jsonl F2 rows), 12 ABSENT and 12 PRESENT, each quote read
against the F2 rule. ABSENT: the headline is a summary over all rows with the row count printed, or a single pre-named row.
PRESENT: the headline is a maximum over rows, a best case, or a projection.

ABSENT, 12 read: supports 1 (2cb3cc43e5c4, "always lower ... 3 <= n <= 7", a statement over every stated size). Contradicts 2
(78fde9b9e689 "can reach values below 10^-22" is a best case; 95a9f1ebee0d "over 5x ... on common-success workloads" is a chosen
subset). The other 9 carry no headline figure at all (method or motivation sentences, one Spanish summary with no number).
PRESENT, 12 read: supports at most 2 (4710d8fdc98e "4.2%-9.5%" and 85b3ab066efb "1.7x-3.9x", ranges whose top may be the headline,
can't tell from the words). Contradicts 1 (45b35c0b371e "on average, 5x", a summary). The other 9 carry no selection: single
measured values, a population with its error, method sentences, "we maximize nonlocality" (a physics objective, not a selected row).
Lexical cue check: "up to / as high as / best / maximum / peak / projected" appears in 3 of 55 PRESENT quotes and 0 of 39 ABSENT.

Reading: about 1 in 12 ABSENT and at most 2 in 12 PRESENT quotes support their label. Three-way grounded agreement among the
local teachers (Llama 3.1 8B, Mistral 7B, Gemma 3 4B) on abstracts does not produce valid F2 labels. The fault is the label
source, not the cap or the decode order. Pilot B does not train on this silver. Same model family caveat does not apply: this
read is Bones against the rule text, one reader.
