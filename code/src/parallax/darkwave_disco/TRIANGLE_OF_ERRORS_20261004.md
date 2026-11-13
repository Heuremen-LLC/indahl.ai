# Today's errors, lined up trianglewise (Bones, 2026-10-04; no new reads, no chip time; no causes hunted)

Every place today's data did not close, placed on the corner it holds up. Per row: what did not close; where and how often (the firmness);
its hole; which other corner covers the hole. Source: TRIANGLE_RUNS_20261004.md and THIRD_RUNG §182-§191.

## OBSERVER -- our act, our clock
- O1. One look timed three ways never closes on any chip. 3 chips, 7 reads. Hole: the maker's length is stated, not measured by us. Covered by WITNESS (W1).
- O2. Same chip, our method changed, the look's ratios changed (Pittsburgh 1.087 -> 1.040; 1.606 -> 1.40). Hole: one new read. Covered by TIME (T3: the bit's own side moved most).
- O3. Ten pushes with no time between move OFF +1.0..+1.15 %, ON -1.0..-1.1 %. 3 chips, 7 reads. Hole: the textbook name (rotation error) was measured once, on one chip (§147). Covered by TIME (T1: grows with the time laid between pushes).
- O4. Our laid clock: two chips agree at short spacing (+5.8 / +5.8 % at 5 us), the third does not (+2.7 %). Hole: n = 1 on the third. Covered by WITNESS (W4: the third chip's clocks hold their hand best).

## WITNESS -- clocks inside the chip
- W1. Clocks beside a driven bit read the look at 1.040-1.072 x the maker's, on all three chips. 7 reads. The one ratio that is the same everywhere. Hole: driven clocks only. Covered by OBSERVER (O1 sets what is being timed).
- W2. Free clocks read the look shorter than the maker (Marrakesh 1.2-2.0 us of 2.68; Kingston 0.7-1.9 of 2.18). 2 chips, 6 reads. Hole: they turn slowly, widths 0.2-0.3 us. Covered by W1 (same look, other clocks).
- W3. The free clocks two links from the looked-at bits read the shortest look on all six reads, both chips. Hole: what those seats are in the wiring is not measured. Covered by OBSERVER (which bits are looked at is our role seed: our choice places them).
- W4. The hand a driven clock keeps through 3 looks is one number per chip (0.77 / 0.90 / 0.92) and repeats on Pittsburgh across method and days (0.921 / 0.826 -> 0.924 / 0.821). Hole: one new read. Covered by TIME (each chip's own clock).
- W5. Marrakesh's clocks read the look longer read after read (2.76 -> 2.80 -> 2.85); Kingston's held (2.31-2.34). 1 chip moving. Covered by TIME (T2: Marrakesh's fading clock moved most too).

## TIME -- the bit's own clocks
- T1. Two bookkeepings of the same bit give the crossing opposite signs (one exponential: positive; the bit's measured curve: zero or below). 3 chips, 7 reads. Hole: both are our rulers. Covered by OBSERVER (O3: the no-time arm needs no bookkeeping).
- T2. The bit's fading clock moves between jobs (up to ~10 us on Marrakesh), not within one. 9 reads. Covered by WITNESS (W5, same chip).
- T3. The bit's own fading reads the look 1.40-1.74 x the maker's: the widest spread of the day, chip by chip. 7 reads. Covered by WITNESS (W1 holds still while this moves).
- T4. The fading curve is bent on each bit, not only in the average (faster early on 62-84 % of bit-copies, least on Pittsburgh). Textbook; kept as a row.
- T5. The half-way start after ten back-to-back pushes: +2.8 / -1.1 / +2.6 %. Kingston's sign differs. 7 reads. Hole: no third clock on it. Open.

## THE MARGIN
Simulator breaks (raw I/Q, reset delay); a reader's width column printed truncated; Marrakesh read 1's in-job slide that did not repeat; my two-lane slips (two bookkeepings, two clocks).

## Where it lands
- The WITNESS corner holds still across chips (W1). OBSERVER and TIME carry the errors: our method, our laid clock and the bit's own clock are what move chip to chip and job to job.
- Errors pair across corners on the same chip: Marrakesh's witness drift (W5) and fading drift (T2); Pittsburgh's held hand (W4) and its smaller crossing (O4).
- One reading never closes a row; every row above has its hole covered by another corner, and none is closed by one corner alone.
