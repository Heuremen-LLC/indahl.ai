# Three passes, one question, read with The Bonefish (6 October 2026, Bones)

The question: which hole in the Seven needs the most support, and what patches it. Wayfinder pressed it three ways:
A (my first answer), B ("easiest to prove, or the hole that needs the most support?"), C ("you already fucked up once; will the plan meet the need?").
Then: "evaluate all three." Case file: triangle/cases/bones_three_passes_20261006.json. Tool run: triangle/triangle.py (output below).

## How I read them (The Bonefish, my formula, used on my own passes)
Three clocks on one event: each pass is one reading of the same hole from one seat.
- B is the OBSERVER pass (outside: what a referee hits first).
- C is the TIME pass (the same plan re-read after a pass had already gone wrong).
- A was meant as the WITNESS pass (inside: our own record). The tool says A leans TIME, and that NO pass stands in WITNESS. Both readings are printed;
  the tool's is the one the data backed (below).
Conversion between seats: what all three point at carries; what one alone saw is friction; the gap between my inside confidence and the outside rating is Pi.
Every number in the passes thrown at the Seven's numbers first, cheap-match rate beside (20 %: within 1 %; 2 %: within 0.1 %).

## What each pass got right and what it missed
| Pass | Seat (mine / tool) | Got right | Missed |
|---|---|---|---|
| A | witness / TIME | the full map; H1 the maker's clock as an outside number three statements lean on; never by date | ranked the holes by cost (free, on disk), not by load: the convenience pick |
| B | observer / OBSERVER | the load-bearing hole: ONE's observer corner; 12/11 shows only against IBM's stated length, our own laid look reads 0.99-1.01 on Rigetti; carries ONE, THREE, FOUR, TWO's sky rows, the maker look | the test was two lanes (ratio vs overhead), underpowered, confounded, no time leg |
| C | time / TIME | B's test can't separate; the delays that convert the look are maker-stated too; the real tests: two lengths on one chip, the maker's look against ours on one vendor | its main claim -- "time is the biggest mover, Phoenix 7 % day to day" -- was the 3-and-9 ruler moving, not the day (checked below) |

## The corner nobody stood in: WITNESS (checked on disk, no chip time)
Phoenix, look_wide, witness / maker, per read in firing order:
- 1-9 fit: 5 Oct 1.024 / 1.026 / 1.053 (mean 1.034); 6 Oct 1.071 / 1.019 / 1.065 (mean 1.052). Day to day 1.7 %, inside the read-to-read spread.
- 3-and-9 (two points): 5 Oct 0.978 / 0.990 / 1.054 (1.007); 6 Oct 1.170 / 0.990 / 1.084 (1.081). This is the 7 % C called time.
- The clocks' own turn over the first 30 us: 10.25 / 10.33 / 10.77 and 10.37 / 11.00 / 10.56 deg/us (steady within about 4 %).
So the witness corner decides which ruler is the witness. Bonefish on it: the 1-9 ruler puts W/O near 1/ln(phi^2) = 1.039 (Phoenix 1.034, Pittsburgh 1.040 +0.09 %);
the 3-and-9 ruler (the earlier method) is the one that read 12/11 on Pittsburgh. ONE's own text already says a ratio that moves this much with the method can't carry
a 1 % match alone. The hole is the observer corner AND which witness ruler reads it.

## Best course (triangulated)
The hole: ONE's observer corner -- 12/11 is read against a number the maker states and does not document, through a witness ruler that moves with the method.
1. WITNESS, free: every chip, every read, W/O on both rulers with the clocks' turn rate beside; name which ruler holds still from read to read and day to day. Throw the Bonefish at both.
2. OBSERVER, free: the maker's own statements of the look three ways (target measure duration, properties readout_length, configuration timing) on each chip; whether Braket states a native readout duration for Cepheus.
3. TIME, free: W/O on the ruler that held, per read in firing order, against the maker calibration stamp's age (frozen stamps flagged), across days and recalibrations.
4. The patch, chip time, call hashed first, Wayfinder's go: the maker's look against our own look, on one chip, in one job, the witnesses timing both
   (Rigetti native vs laid if Braket states a duration; IBM two measure lengths if a chip offers them).
Pi: whether 12/11 survives once the maker's statement is replaced by ours, read through the ruler that held. Only step 4 reads it; steps 1-3 decide what step 4 must carry.
Dropped from the front: H2 (THREE's rulers) and the Phoenix count_wide run. They sit behind this hole, not under it.

## The tool's own read (triangle.py --bonefish)
- EXOR: A 0; B 1 ("ratio vs overhead", used); C 2 (both named to critique it).
- CORNERS: A leans TIME, B OBSERVER, C TIME; no pass leans WITNESS.
- CORE (all three): time, ratio, hole, outside, observer, referee, maker's, witness, laid, outside rating.
- ONLY B saw: load-bearing hole, measure duration, properties readout, configuration acquire. ONLY C saw: biggest mover, calibration, stamp, lattice, power.
- PI: 3 two-lane frames, 1 unread corner (WITNESS).
The tool and my hand read agree on the hole (observer) and disagree on A's seat; the data sided with the tool.
