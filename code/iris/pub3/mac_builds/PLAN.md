# Faults/Guards bench v2 on the Mac under two official Ollama builds (plan committed before any reply on either server; 31 Oct 2026)

Why: Pub #2's two-machine comparison set a Mac (Homebrew bottle of Ollama 0.34.2, one parallel slot) against an RTX 3080 workstation
(Ollama 0.34.3, started with four slots). An outside review named the engine version and slot count as differences that travel with the
hardware. This run holds the Mac and its model files fixed and changes the server build only, one step at a time.

Setup. The Mac (Apple M5 Max), our model folder (seats/models, our models only, never the other server on this Mac). Two official Ollama
release builds from github.com/ollama/ollama, each checked against the digest GitHub publishes before use:
- official-0.34.2: v0.34.2 ollama-darwin.tgz, sha256 f33b2a5aa59bc6c961ed3ec23ba9dc646ca6d99ced8d2a0d46eb3a522167dd3f, port 11502
- official-0.34.3: v0.34.3 ollama-darwin.tgz, sha256 2c45865f94bce0d4d1d2567603dd2fdacaf375585220a175aa4800105193d36e, port 11501
Each server: OLLAMA_NUM_PARALLEL=1, OLLAMA_MAX_LOADED_MODELS=1, OLLAMA_KEEP_ALIVE=5m, requests one at a time. drive.sh records the binary
hash, the version the server reports and its model list with digests (out/<build>/setup.json) before any request.
Items, arms, request settings, gates and scorer: byte copies of faultsbench2_mac_cross (items.py, items.json, score.py; CODE.sha256).
run.py differs from faultsbench2_mac_cross/run.py only in the server address and output folder, and publishes no status page.
Models: phi4-mini, llama3.2:3b, qwen2.5:1.5b, granite4.1:3b, ministral-3:3b (Pub #2's Table "Byte-identical replies out of 170").
Their manifest digests on each server are checked equal to those recorded for the 30 Oct runs (seats_compare/setups_20261030.json) before
any reading. A model whose digest differs is reported and not read.
The earlier Mac runs (faultsbench2/out/phi4-mini and faultsbench2_mac_cross/out, Homebrew 0.34.2) are the third build, brew-0.34.2.

Known-good before any cross-build reading: each build's own exact repeat (bare against bare_copy), byte-identical count and scored-class
changes, per model. These are the floors.

Readings (four outcomes, nothing folded; counts item by item before any net):
B1 Build, same version: brew-0.34.2 against official-0.34.2, per model and arm (bare, guard), byte-identical replies out of 170, beside
   both builds' repeats.
B2 Version, same build: official-0.34.2 against official-0.34.3, the same counts.
B3 For B1 and B2, the scored class item by item on items gated and read in all four runs of the pair, changes in each direction against
   each build's repeat floor, exact two-sided binomial on the changed items. Per family paired bare fault-rate difference, bootstrap
   2,000, 95%, as in Pub #2.
Outcome per model and pair: if the across-build identity equals both repeats (every byte-identical repeat also identical across builds),
the change carries nothing here (CONSISTENT, with the bound printed). Fewer identical across builds than either repeat is ABOVE (the
build or version carries the text). A pair whose repeats themselves differ is CANNOT_TELL.
Parser: the committed score.py, with ten replies per family read in full before any rate is printed.

What would come next (not part of this plan): an addendum for the RTX 3080 workstation at official 0.34.3 with OLLAMA_NUM_PARALLEL=1,
read against official-0.34.3 here, once its current job ends. Nothing goes on a page until the ledger has it and he says so.
One GPU job at a time (iris_index/queue.json).

## Addendum 1 (31 Oct 2026, written after the replies were in and before any of them was read or compared)
Operational form of the outcome rule above. For a pair of builds, I = the items whose bare and bare_copy replies are byte-identical in
both builds. CONSISTENT: every item in I is byte-identical across the two builds (bare against bare), printed with the exact
(Clopper-Pearson) 95% upper bound on the share of I that could change. ABOVE: at least one item in I differs across the builds. CANNOT_TELL:
I holds fewer than 100 items. The guard arm has no repeat, so it is reported as a count only. Gates, families and the bootstrap are those of
seats_compare/compare.py (score.py's own gates), run per pair. The reader is builds_compare.py, committed with this addendum.

## Addendum 2 (31 Oct 2026, defined after the data: written after B1 and B2 were read)
B1 reads ABOVE for ministral-3:3b only (14 of 170 bare replies change between the Homebrew build of 30 Oct and the official build of
31 Oct, with no scored class changed), and CONSISTENT for the other four. B1 compares two builds on two days, so it cannot say which.
B1b: the Homebrew 0.34.2 server (our seat on 11500, unchanged since 30 Oct) runs the same five models, three arms, today, into
out/brew-0.34.2-today/. Read: brew-0.34.2-today against brew-0.34.2 (same build, a day apart) and against official-0.34.2 (same day, two
builds), with the operational rule of addendum 1. The reading is labelled defined after the data wherever it appears.
