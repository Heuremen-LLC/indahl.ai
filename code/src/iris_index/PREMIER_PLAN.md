# Premier models: the same bench, full attribution (planning draft, 27 Oct 2026, his word)
Nothing here runs until he says and a budget cap per vendor exists. Written to be cheap to start and honest to read.

## What runs
- Same Faults and Guards bench (four families, bare / repeat / guard arms, same scorer and gates) and the IRIS option-order matrix, on each lab's flagship and small tier. Eleven rounds once the pilot passes.
- Pilot first: ONE round per model (510 calls). Measured on our own runs: about 52 tokens in and 146 out per call on small models, so a pilot is roughly 27k tokens in and 75k to 150k out visible per model, before any hidden reasoning tokens. Full eleven rounds: 5,610 calls per model, about 0.3M in and 0.8M to 1.7M out visible. Cost = those counts times each vendor's current rate card, with the batch discount where offered.
- Frontier models will likely pass the easy controls, so faults get rare. Pilot also tests a harder item set (v3: longer tables, subtler missing widths, near-miss equals signs) planned and committed before any reply, same rule as every round.

## Harness
- api_run.py: one adapter per vendor, same items.json, same plan-before-reply discipline, resumable, one model at a time, every request id and the exact model string logged. Settings are what the vendor allows (temperature, seed, reasoning effort) and are recorded in each row. If a model cannot repeat exactly, the repeat gate says so and that model's readings are CANNOT_TELL, never relaxed.
- Reasoning models: reply limit raised and the hidden-token count logged, because it is most of the cost.
- Keys: his, pasted per vendor, used and never stored; rotate after.

## Attribution (the part that makes it public-safe)
- Every row and page names the lab, the model id and version string, the date run, and the settings used. Vendor named as the source of the model, nothing about the vendor beyond the measurement. Raw replies released under our terms on indahl.ai and the indahl Hugging Face account.
- Same neutral wording as the open-model rounds. No ranking, four outcomes, widths on every rate.

## Order
1. Pick the lineup and a cap per vendor (his).
2. Build api_run.py and v3 items, synth, commit plan (me, no spend).
3. Pilot round per model, results graphic on the IRIS page under the open-model rounds.
4. Eleven rounds where the pilot shows readable gates.

## Needs from him
Which labs, a spend cap per vendor, and keys when ready. Until then: no spend, no calls.
