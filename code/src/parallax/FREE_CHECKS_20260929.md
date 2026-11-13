# FREE CHECKS, 2026-09-29 (the five cheap ones from the two sweeps)

Written ~03:00Z 9/29 by Bones's field hand. No quantum runs, no money spent. Everything comes from data on disk plus free
reads:
- Braket: task search and one S3 result object from our own bucket.
- IBM: published calibration snapshots for 9/26-9/28, and job lists.

One code change: `standoff/absence_ledger.py` (item 5). No guesses were written before looking.

---

## 1. Kingston q1 vs q16, same shot: NONE FOUND

**Raw.** No Kingston job on disk has ever measured q1 and q16 in the same shot, so q1's false-1 rate can't be split by
what q16 read.

**Closest jobs:**
- **9/24, two jobs submitted in the same second (20:53:55Z) and run back to back on the same chip.** The arrow job
  `daqorotb46qs73a1iccg` read q1, q2 and q133, each alone in a one-qubit circuit (21:03:51-21:11:04Z). The space job
  `daqorouekp0c73ar365g` read pairs 16-23 and 144-145. Same minutes, different shots.
- **9/24 dark_floor `daqljjqkqcdc73aau0n0`.** Has pair 16-23 but no q1, and kept only averages.
- **April.** Layouts were q0-q3 and q0-q7, and the raw shots are gone.
- **9/28 Kingston parallax (16:34Z).** Read q16 plus 77 other seats per shot, but only even seats, so q1 was never read.

**Substitute test (weak).** On 9/28, q16 was sitting in the same shots as its July-21 co-movers from the apr_aug record
(q80, q96, q102, q116). But q16 was healthy that day: 1.1% false-1 at rest, against 85% on 9/24.
- Its wrong reads do not line up with any co-mover's wrong reads, at rest or prepared in 1 (every p > 0.1).
- Across all 77 other seats, the best match has p = 0.05, which is what chance gives for 77 tries.

**IBM's record, 9/15-9/28.** q1 read false-1 0.2-1.5% and q16 0.3-1.6%. Neither was ever flagged. The 9/24 extra 1s
never showed up there (as the apr_aug sweep said).

**What's left.** The readout-group question needs one job that reads q1, q16, q80, q96, q102 and q116 in the same shot.
That would be a new run, not a free check.

## 2. Seat 62 on another day: a 9/23-9/24 SPELL, not a standing trait

**Raw, 9/28, Marrakesh q62:**
- **Morning parallax (12:30Z):** read 1 at rest on 1.15% of shots (115 of 10,000). That is 49th of 78 seats counting
  from the coldest; chip median 0.5%.
- **Afternoon echo run (~16:27Z):** 0.2% at rest (29th of 78).
- **Prepared 1:** lost 2.6% (105 of 4,000), steady. No spells: it ranks 39th of 78 on losses bunching together, and
  the 125-shot blocks swing only as much as noise.
- **For contrast, 9/24:** 2 ones at rest in 32,768 shots, and one prepared-1 circuit at 48% with the worst spells on
  the chip.

**IBM's own record agrees.**
- q62's false-1 rank among 156 seats: 76, 80, 124, 115, 12, 54, 54, 117 (9/15-9/22). Then **5 on 9/23 and 2 on 9/24**.
  Then 29, 42, 88, 100 (9/25-9/28).
- The two calibrations on either side of our 9/24 shots (23:08Z 9/23 and 23:36Z 9/24) both had it among the 5 coldest.
- The calibration in force during the 9/28 parallax run (22:31Z 9/27) had it 88th.

So the calibration and our shots agree on a two-day cold spell, and our 9/24 run landed inside it.

**q60.** Warm, not cold: 3.3% at rest in the parallax run (66th of 78) and 1.1% in the echo run. IBM ranks it anywhere
from 13th to 122nd. Its prepared 1 does not blink (25th of 78). Its flicker is the other kind: the third place at the
start, 5-9% in some echo jobs and ~0 in others (THIRD_RUNG §2).

**q61.** No 9/28 data, because it is an odd seat. On 9/24 it was the looked-at qubit of pair 61-62 and was never at rest.
Its 48 series show no spells (worst runs z -2.1). IBM ranks it 70-132 every day, so always on the warm side.

**Answer.** Cold-and-blinking belongs to q62 on 9/23-9/24 and was gone by 9/25. It is not a trait of the 60-61-62 row
end. The 9/28 Marrakesh seat whose prepared 1 blinked was q26 (runs z -26; blocks 20x noise), the seat that carries the
third place.

## 3. Reset memory on tonight's Rigetti data: order IS stored; the 9/26 rule is NOT there chip-wide; q0 carries rung 2, not rung 1

**Is shot order stored?** Yes.
- Every collector (rigetti_chip, blink_hour, witness_*, edge_room, fuckup_stack) saves Braket's per-shot `measurements`
  array in the order Braket returns it.
- The same array sits in each task's S3 `results.json`, so any task not saved to an npz can be pulled for fractions of a
  cent.
- The array is not sorted. Across the whole chip, failure pairs come out at 1.005x chance, which a sorted array could
  not give.

**How the test works.** Each shuffle sequence leaves the qubit on a known rung after a success. Each one also fails from a
known leftover rung:
- `a` fails from a leftover rung 1.
- `aba` and `bab` fail from a leftover rung 2.
- `e`, `b` and `bb` fail from either.
- `ba` can't see a leftover rung 1 at all, and a success never leaves rung 2, so it is the control.

**Whole chip.** Data: 107 qubits in 3,438 shot series (run.npz and blink.npz).
- Failure right after a failure: 231,443 times, against 230,392 by chance (0.5% more).
- In every split by the rung a success leaves behind (0, 1 or 2), the ratio is 1.00-1.01.
- The 9/26 pattern ("a failure never follows a failure") shows in **1 series** (q70 `bab`, 359 vs 406), where about 5
  would show by chance. **None found.**
- The opposite (failures clumping) is real but lives on a few qubits. 20 series have enough failures to judge.
  - 8 of them are **Rigetti q62**'s rung-2 read (`ba`) in the blink hour: 393 failure pairs against 180 expected
    (P 0.0002).
  - Its failures come in spells of 10-100 shots inside one task, up to 13 in a row. In check 5, blocks went 6%, then
    31-60%, then 3% within 800 shots.
  - Its plain reads do not clump (40 vs 35). So q62's rung-2 start switches on and off within a single task, well
    under a second.
  - Other clumpers: q61 (3 series) and q41 (3 series).

**q0 (named before looking).**
- Success leaves rung 1 (`a`): 26 failure pairs vs 24.6. **No memory.**
- Success leaves rung 2 (`ab`, `aba`, `bab`): 64 vs 88 (P 0.002). Counting only the two where a leftover rung 2 makes
  the next shot fail (`aba`, `bab`): 25 vs 43 (P 0.001). In `bab`, the next shot fails 2.3% after a failure but 6.4%
  after a success.
- Failure leaves q0 excited (plain, `b`, `bb`): failures clump, 67 vs 46 (P 0.0007).
- Control `ba`: 39 vs 39. Nothing.

Plain words: the reset between shots clears q0's rung 1 but sometimes leaves rung 2 behind, on a few % of shots.

Odds:
- q0 is the lowest of 95 pushed qubits on the rung-2 test; q49 is next (P 0.004).
- About 0.5 qubits would sit that low by chance; 2 do.
- Counting the five ways I split q0, call it about 1 in 100.

**q90 (the 9/26 qubit).**
- Rung-1 test: 1 failure pair vs 3.1 (P 0.18). Same direction as 9/26, but too few failures to call; its failure rate
  tonight is 2.5% against 6.7% on 9/26.
- Its plain-read failures clump: 17 vs 3.3 (P 0.0002).

**Caution.** The whole-chip "rung 2 at the start" fit assumes every sequence starts from the same place. On q0, the
sequences that end on rung 2 carry part of their own previous shot. So q0's start number (0.29%) is partly the
previous shot. Most qubits show no carry, so the chip map stands.

## 4. The orphaned Braket task: FOUND, and it holds nothing new

**Search.** 115 Cepheus tasks were created 00:45-01:45Z on 9/26. Exactly one is in no file under standoff/:
- `4f3a04f7-2eb6-44a4-a063-6c3acbef2454`, COMPLETED, created 01:15:57.5Z, ended 01:15:59.3Z, 300 shots on q0.
- Its program is step2b's delay-0 Ramsey: rx(pi), two f12 half-pushes (0.247) back to back, rx(pi), read.
- It ran 300 shots, the old count; step2b used 500.

**Raw.** 280 of 300 read 1 (93.3% +/- 1.4%).
- step2 at delay 0: 281/300 (93.7%). step2b at delay 0: 463/500 (92.6%).
- All three agree (P 0.83). Shot order shows 2 failure pairs vs 1.3 by chance, so no memory.
- The unopened drawer held a copy of what we already had.

**Saved.** `standoff/orphan_step2b_4f3a04f7-2eb6-44a4-a063-6c3acbef2454.json` (the S3 `results.json`, with metadata).
It's now on file, so the next ARN grep will find it.

## 5. Absence ledger blind spot: CLOSED, one new hole

**Change.** The IBM side now loops over every `~/bones-forge/.ibm_quantum_key*` file. Five were found: the plain key,
`_2`, `_3`, `_4` and `_parallax`.
- Duplicate job IDs across keys are recorded once.
- Each hole is stamped with the key file's NAME (never its contents).
- Backups: `absence_ledger.py.bak-20260928`, and `absence_ledger.jsonl.bak-20260928` taken before the run appended to
  the ledger.

**Ran once** (it only reads job lists). One new hole:
- Job `daqmtobt55cs738rvdfg`, ibm_marrakesh, ERROR 6073 ("size of the job exceeds the memory limits of the classical
  control hardware"), key `_2`.
- Created 2026-09-24 18:41:38Z. That confirms the sweep's timing correction (18:41Z, not ~19:05Z).
- The ledger now holds 21 holes: 20 Ring rejections plus this one.

**What each key holds:**
- Plain key: 6 jobs, all done.
- `_2`: 11 jobs, 1 error.
- `_3`: 31 jobs, all done. `_parallax` lists the same 31 (a second token on the same account).
- `_4`: 65 jobs on 9/28, all done.

No other IBM absence exists on any key. The April instance and the dead Aug-13 key aren't on disk, so their holes stay
out of sight.

---

## Cross-links to the other holes

- **Seat 62.**
  - Marrakesh 62's cold-and-blink was a 9/23-9/24 spell.
  - Kingston 62 sits at the same spot on the same Heron r2 blueprint. It is the carried-third-place seat (THIRD_RUNG
    §2) and 3rd warmest at rest on 9/28.
  - Rigetti q62 is tonight's strongest shot-to-shot clumper of rung-2 reads, and already a pitch-hopper, far listener
    and room-heater.
  - The Marrakesh/Kingston pair is a blueprint overlap, like 151/152 (about 1 in 5). Rigetti's 62 shares only the
    number on a different lattice. **I'm not counting it.**
- **Order-of-looking heat stack.** q0 adds the smallest-scale brick: what the last shot left behind (rung 2, not
  rung 1) sets how the next shot starts. Textbook mechanism: the reset can't clear rung 2.
- **The empty box riding on failed shots.** None found. Nothing checked tonight touches it.
- **Frozen numbers.** None found. The orphan's 280/300 next to step2's 281/300 is ordinary (the two counts would
  typically differ by about 6).

## Files
- Report: this file.
- Scripts and outputs: `parallax/out/free_checks_20260929/`
  - `reset_memory.py`, `perm.py`, `seat62.py`, with their JSON outputs.
  - `orphan_window.json` (the 115-task window).
- IBM calibration snapshots, 9/26-9/28 (Marrakesh and Kingston): `parallax/out/ibm_cal_20260929/`
- Orphan: `standoff/orphan_step2b_4f3a04f7-2eb6-44a4-a063-6c3acbef2454.json`
- Ledger: `standoff/absence_ledger.py`, `.jsonl`, and their `.bak-20260928` copies.
