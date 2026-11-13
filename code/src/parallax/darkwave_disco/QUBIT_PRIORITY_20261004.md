# Qubit plan -- reviewed for binary (Bones, 2026-10-04, second pass; replaces the first pass of the same day)

Wayfinder: "review your plan to shore up our data and make sure you didn't inadvertently go binary on us. We're chasing bugs in reality
as shown with qubits without measuring the ruler or limiting our outcomes with direct prediction."

## What the first pass got wrong (owned)
1. **Runs parked on our own numbers.** The look at the three positions that give 1.09 / 1.62 / 1.48; the push at a spacing "called from the
   ladder first"; the count run at exactly 27 and 81 looks. Each circuit was built around the guess, so the chip could only answer our question.
2. **A "what a miss means" column.** Hit or miss, per claim. Two lanes.
3. **Ranked by which claims could fail.** Outcome logic.
4. **No ruler measured.** The crossing was demoted to "non-exponential decay, T1 fluctuation", and that fluctuation is a label: no run reads
   it as its own object. Same for the readout clouds, the 500 us reset and the decay bookkeeping itself.
5. **No witness clocks** in the push or count runs: outside readout only.
6. **Four written off** ("qubits can't test it") because I wanted a ratio where the chip gave a separation (+1.88 +- 1.16). That threw out a measurement.
The three starts (OFF, ON, in-between) in the existing push runs were never binary; that part stays.

## Rules for every run, from here
- **No number in the design.** Sweeps go wide and plain, through our numbers and far past them on both sides, with nothing parked on a guess.
- **Three starts** (|0>, |1>, halfway) on IBM; **three levels** read directly on Rigetti.
- **Witness clocks inside** at three distances (neighbour, two steps, far), read against our outside readout of the same event. Any "no effect" says which side it is from.
- **The ruler read as an object, in the same job:** T1 and T2 of the same qubits interleaved through the job (the fluctuation measured, not
  named), calibration clouds at start / middle / end, the decay bookkeeping computed both ways with both kept.
- **Seats by written seed in random groups of three**, or the whole chip.
- **Failures are rows.** Failed jobs, dropped seats, NaN fits and error-bar sizes go in the same table as the results.
- **Logged before firing:** circuits, script sha256, job IDs. Nothing else. No guess written.
- **Read-out:** raw first in plain words, then hats (ours). Rulers compared as AGREE / STABLE DISAGREEMENT / UNSTABLE, in units. The calls
  already public on the page are read against what lands afterward as a distance, never as pass or fail.

## The runs (named by what they listen to)
1. **THE PUSH, WIDE** -- Marrakesh, Kingston, Fez. Three starts; spacing ladder 5-150 us (8 rungs); push counts 0-20; witnesses at three
   distances; the ruler interleaved. Three reads per chip. Feeds Two, Five and Seven's chip piece.
2. **THE LOOK, WIDE** -- two chips. The look's position and timing swept across the whole window; witnesses at three distances; three reads
   per chip. Feeds One and Six (the stretch).
3. **THE COUNT** -- two chips. A free-running spectator through 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96 and 128 looks: dense, through
   the old 3 / 9 / 27 / 81 spots without stopping on them. Feeds Three.
4. **THE PUSH, THIRD LEVEL (Rigetti Cepheus, Amazon)** -- the push with |2> read directly (a swap before readout), the explicit third-level
   read Shuttle asked for and IBM cannot do. Three starts plus a |2> start, the same spacing ladder trimmed to 6 rungs.
5. **Four** gets no run built for it. Runs 1-3 record every clock it reads; whatever lands there, lands.

## Where the record is thinnest (order of need; a coverage gap, not a chance of failing)
1. Two -- one chip has more than one read; its ruler (the decay bookkeeping, the "T1 fluctuation") is named, not measured; one vendor. Run 1 + run 4.
2. One -- one chip. Run 2.
3. Three -- one chip, several single reads. Run 3.
4. Six -- the stretch on one chip, the emitter park one read. Free with run 2.
5. Five -- Two's evidence read another way. Free with run 1.
6. Seven -- the chip piece is one Kingston read; the outside test is NIST's next count. Free with run 1.
7. Four -- no run built for it.

## What it takes
- **IBM:** working estimate about 250 s across runs 1-3 (run 1 ~120-150, run 2 ~40-50, run 3 ~40-60), from the ledger's 5-7 s per full-chip
  read, plus the ledger's 1.25 guard. Each script gets a fake-chip dry run first, and the exact seconds come from that before anything fires.
  Parallax has 4 s left. ibm_pittsburgh is not on Parallax's operational list today (fez, kingston, marrakesh are).
- **Amazon:** `aws login` on this Mac first (the CLI says no credentials). Then run 4 at about 96 circuits x 1,000 shots, two reads:
  ~192 tasks, ~192,000 shots. For scale, the whole 9/28 Rigetti night was 563 tasks. Dollars are his.
