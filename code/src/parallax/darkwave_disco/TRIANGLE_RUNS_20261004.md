# The triangle runs -- 4 October 2026 (raw, in plain words; no verdicts; hats are ours, after)

Three runs, one corner each, fired one at a time and checked between reads. Every script was frozen (sha256) before firing; no guess was written
(THIRD_RUNG §182-§188). Instance: Darkwave Disco (pay-as-you-go), 389 s used before today, cap 625 s.
Code and reads: `parallax/out/qubit_fifth_run/` -- time_wide.py, look_wide.py, count_wide.py (+ _kingston copies); readers readtime.py / sumtime.py,
readlook_wide.py, readwitness_wide.py.

## TIME -- clocks on one bit (ibm_marrakesh and ibm_kingston, three reads each, 90 s)
Every bit; three starts (OFF / ON / half-way); ten pushes spread at 5-150 us; the ruler (the bit's own fading, three copies through each job; idle OFF; echo) read in the same job.
- The bit's own fading time moves read to read: Marrakesh 174 / 177 / 181 us by copy, up to ~10 us between jobs; Kingston 260-266 us. Read 1's in-job slide did not repeat.
- The bit's measured fading curve is not one exponential: it falls faster early.
- OFF start, 10 pushes spread, minus the old one-exponential bookkeeping: Marrakesh +5.8 % at 5 us, +3.0 % at 30 us, ~0 at 150 us; Kingston +5.8 %, +3.3 %, +0.6 %.
  The old one-read figures at 30 us were +2.74 % (Marrakesh) and +2.87 % (Kingston).
- The same, minus the bit's measured curve: below zero past ~20 us on Marrakesh (-1.7 % at 30 us), near zero on Kingston (-0.4 %).
- Ten pushes back to back: OFF +1.1 %, ON -1.0 %, on both chips.
- The two chips on our laid clock: within a width of each other up to 30 us, ~2 widths apart past 45 us. On each bit's own clock: ~3 widths apart at 15-45 us-equivalent, together beyond.
- Idle OFF bit after 300 / 600 us: about +0.5 % (no heating seen).

## OBSERVER -- one look, timed from three positions in one job (ibm_marrakesh, three reads, 30 s)
- The maker's stated look: 2.684 us (the chip's target).
- The look on the clocks beside a driven emitter: 2.76 / 2.80 / 2.85 us (it rose read to read).
- The look on the looked-at bit's own fading: 4.01 / 4.13 / 4.01 us.
- Ratios, three reads: witness / maker 1.028 / 1.044 / 1.060; own / maker 1.50 / 1.54 / 1.50; own / witness 1.45 / 1.47 / 1.41.
  (Pittsburgh's earlier figures for the same three sides: 1.087, 1.606, 1.477.)

## WITNESS -- free clocks inside the chip (ibm_marrakesh, three reads, 24 s)
119 clocks, nothing driven beside them, read through 1-32 looks at 31 other bits and through laid time, split by distance to the nearest looked-at bit.
- Hand kept through 3 looks: one link 0.78-0.80, two links 0.66-0.72, three or more 0.77-0.78. Through 12 looks: 0.43-0.49 / 0.31-0.36 / 0.38-0.41.
- Hand kept through 30 us of laid time: 0.48-0.49 / 0.35-0.42 / 0.45-0.46. k looks cost about what k x 2.68 us of laid time costs.
- The two-link clocks lose their hand fastest on every read.
- The look as the free clocks time it: 1.7-2.0 us (one link), 1.2-1.3 (two links), 1.6-1.8 (three or more); widths 0.23-0.34 us.

## Kingston -- OBSERVER and WITNESS (three reads each, 54 s)
- OBSERVER: maker 2.180 us; witness 2.32 / 2.31 / 2.34; own fading 3.79 / 3.47 / 3.72. Witness / maker 1.065 / 1.061 / 1.072; own / maker 1.74 / 1.59 / 1.70.
- WITNESS: free clocks keep ~0.90 of the hand through 3 looks at every distance. One look on the free clocks: 1.4-1.7 us (one link), 0.70-1.00 (two links), 1.76-1.88 (three or more).
  The two-link clocks read the shortest look on all six reads across both chips.

## Pittsburgh -- the ruler of method against chip (one read each, 25 s)
- OBSERVER, new method on the old look work's chip: witness 2.27, own 3.06 us; witness / maker 1.040, own / maker 1.40 (old method there: 1.087, 1.606).
  The hand kept through 3 / 9 looks reproduces the old numbers on that chip: 0.924 / 0.821 against 0.921 / 0.826.
- TIME: at 30 us, minus the one-exponential bookkeeping +1.7 % (old: +2.00 +- 0.16); at 5 us +2.7 %, not the +5.8 % both other chips read.

## Across three chips, kept as rows
- Ten pushes back to back: OFF +1.0 to +1.15 %, ON -1.0 to -1.1 %, on all three.
- Witness / maker for one look: 1.040 to 1.072 on all three. Own / maker: 1.40 to 1.74, chip by chip.
- The hand a driven clock keeps through 3 looks: 0.77 / 0.90 / 0.92 -- one number per chip.
- The crossing's size against our laid clock: two chips agreed at short spacing; the third did not.
- The fading clock moves job to job by up to ~10 us on Marrakesh.

Billed today: 223 s (389 -> 612 of 625). Dry: 13 s left.
