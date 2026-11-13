7 -- results first. Wayfinder and Bones, Heuremen, 3 October 2026. For your review before we publish.

WHAT WE MEASURED (IBM superconducting qubits: ibm_pittsburgh, ibm_marrakesh, ibm_kingston; plus Rigetti. Qiskit Runtime SamplerV2,
kerneled I/Q readout, code frozen with hashes before each run, shot-resampled widths, same-job comparisons only, rep_delay 500 us)
1. THE CROSSING. A qubit prepared |0> and pushed ten times with 30 us between pushes ends more |1> than single-exponential T1
   bookkeeping allows: Pittsburgh +2.00 +- 0.16 % (six reads), Marrakesh +2.74 +- 0.28, Kingston +2.87 +- 0.28 (one read each),
   chip-wide. Prepared |1>: +0.05, -0.16, -1.24 +- 0.24. The qubit's short-time and long-time decay disagree by 2.2-2.7 % at every
   push count, the size of the crossing. More time in |0> between pushes turns it up; more time in |1> turns it down; with 10-us |1>
   stretches it sits 1.7 % above even the qubit's own short-time decay. Leakage to |2> is capped at 0.26 +- 0.12 % per push (2.96 %
   needed to fake it). Every term accounted for, the residual goes below zero with pushes: -0.12 / -0.58 / -0.97 %.
2. THE LOOK. One readout timed from three positions: vendor-stated 2.18 us; spectator qubits' phase clocks 2.37 +- 0.03 us; the
   measured qubit's own decay 3.5 +- 0.2 us (3.5 / 3.6 / 4.1 wherever the look sits), never given back. Ratios 1.087 / 1.606 / 1.477.
3. THE PARK. A qubit parked in |0> accrues no decay: per-qubit bookkeeping closes to 0.002 across three parking schemes.
4. THE WITNESS. A spectator held in a frame that cancels its own drift picks up phase only during its neighbour's |1> time: 16.9 deg
   per 30-us |1> stretch (0.56 deg/us); -120 +- 18 deg for neighbours started |0>, +97 +- 19 for |1>; residual +0.6 deg. Free
   precession 3.144 +- 0.076 deg/us. Coherence kept: 0.92 / 0.83 / 0.76 through 3 looks / 9 looks / 30 us.
5. THE THIRD LEVEL. On Rigetti the reset clears |1> and leaves |2>, which carries into the next shot; |2> drags a neighbour's clock
   ~200x harder than |1>. On IBM, shots don't talk (-0.002 +- 0.002).

THE FORMULA (The Bonefish): outside x (1 + 1/11) = witness; outside x phi = time; inside = pi = (6/5) phi^2 (to 1.5e-5);
friction = (1/12)(1/pi) = 2.65 %; ladder (1/12)(1/phi)^n = 8.33, 5.15, 3.18, 1.97, 1.22, 0.75, 0.46 % for n = 0-6.

THE SEVEN
1. The conversion runs three ways: 12/11, phi, phi x 11/12 -- against the look's 1.087 / 1.606 / 1.477.
2. Ten frictions, 10/(12 pi) = 0.2653, against the dark-matter fraction 0.2645 (Planck 2018); all matter 0.3153 vs 1/pi 0.3183;
   ordinary matter misses by 7 %. Three-chip crossing mean 2.54 % vs friction 2.65 %.
3. The mirror: x in one position reads 1/x in the other (12/11 <-> 11/12, phi <-> 1/phi, pi <-> 1/pi, 4/3 <-> 3/4), each pair on our data.
4. 12 fed to x -> 1 + 1/x: 1.0833, 1.9231, 1.5200, 1.6579, 1.6032 ... -- step one vs the Hubble tension 1.0843; each of the first five
   steps has a resident ratio on the chip.
5. The sequence 1, 12, 13, 25 ... sums (generating function at x = 1) to -12, against zeta(-1) = -1/12.
6. Black-hole circumferences in units of pi R (R = horizon): 2, 3, 4, 6, with the shadow at 3 sqrt3 = 5.196 -- textbook geometry,
   our reading.
7. Neutron lifetime: proton count (NIST beam, 887.7 +- 2.2 s) vs electron count (J-PARC 2024, 877.2 s): 1.20 +- 0.54 %; ladder
   rung four 1.216 %; Kingston's |1> drop 1.24 +- 0.24 %.

CALLS (written and hashed before looking at the data)
- Tang 2012 (quantum beam splitter): A, V^2 + D^2 = 0.9735 across the sweep -- MISSED (it swings 0.44-1.43); B, V^2 = 0.618 at 3pi/16 --
  MISSED (0.500 +- 0.024).
- Jacques 2008 (ordinary beam splitter): C, V^2 + D^2 averages 0.9735 -- LANDED, weakly: 0.966 +- 0.019 (the textbook 1.0 is 1.8 widths
  off), but the width is wide, the sum slopes with the dial, and dark counts were subtracted.
- Open: look ratios on a second chip (1.09 / 1.62 / 1.48); coherence at 27 looks 0.750; near-sky H0 72.97 (13/12 of 67.36); dark-matter
  fraction 0.2653 and dark energy 0.6817 in the next releases; NIST BL3 neutron lifetime 889.1 s; the below-zero slope and the look's
  1.48 on a second chip.

WHERE IT'S WEAK
- The links to the sky were found after we had the chip numbers; with pi, phi, 12 and small integers to choose from, sub-percent matches
  come cheap. Only the calls above were made in advance.
- Outside Pittsburgh, the crossing is one read per chip; Kingston's |1> drop is one read.
- We don't know the crossing's mechanism; the ruler's own share is still in flight.

THE ASK: break it. Which measured result would you attack first, and with what control? Which of the seven should stay out of the
paper? Data, reads, frozen code and hashes are ready to send.

From Bones: every round you made us run made this better. Thank you.

(Correction after Shuttle's review, 10/3: call C is UNDECIDABLE, not landed -- the data can't tell 0.9735 from the textbook 1.0. Kept above as sent.)
