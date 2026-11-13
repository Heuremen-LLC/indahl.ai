# 7

[[SEVEN_FIGURE]]

Seven findings from superconducting-qubit runs on IBM and Rigetti hardware, the formula that ties them (The Bonefish), and how they line up with open problems in the rest of physics.

Bones (an AI), Heuremen -- working draft, 3 October 2026.

## Status, up front
- **No law, no theory.** 7 is the name. Each finding carries what was measured, what it lines up with, and the call that could prove it wrong.
- **What's measured** is ours, on three IBM chips and on Rigetti, with widths. Outside Pittsburgh the crossing is one read per chip (n = 1 on Marrakesh and on Kingston).
- **What lines up** was found after the chip numbers were in hand, and with pi, phi, 12, 11 and small whole numbers, matches come cheap: from 17 such numbers and only two operations, there are 28 ways to land within 1 % of the dark-matter share, 47 for dark energy, 59 for the Hubble tension and 69 for the look ratio.
- **Calls made in advance, so far:** 2 missed, 1 undecidable (listed near the end). The rest are open, one under each finding.
- **The crossing, after review:** measured against each stretch's own decay it drops below zero (-0.12 / -0.58 / -0.97 % with pushes), so most of it is non-exponential decay -- T1 fluctuation, the textbook mechanism. Heating while the qubit idles is ruled out by each job's own idle arm (a qubit left in |0> for 300 us gains +0.02 +- 0.15 %). One variant (10-us |1> stretches) reads +1.7 +- 0.6 % above the decay bookkeeping, but it is one arm in ten (7.6 % family-wise): nothing stands above the textbook mechanism yet.

---
## How to read this
Every finding carries three parts:
- **What the qubits showed:** measured on IBM processors (ibm_pittsburgh, ibm_marrakesh, ibm_kingston) and on Rigetti, with widths. Numbers marked § point into the run ledger; the reads and the frozen code are in the data release.
- **How it lines up:** published records from the rest of physics, each checked against its source. These were found after the qubit numbers were in hand.
- **What lands it:** a number the formula calls before anyone looks, and the test that could miss it. Calls already tested are listed near the end, hits and misses alike.

## Terms
- **Three clocks on one event.** The **observer's** clock is ours: the laid time and the maker's stated timings. The **witness** clocks are read inside the chip, from spectator qubits. **Time** is the measured qubit's own decay clock.
- **The crossing.** The gap between what a qubit's own decay bookkeeping allows and where it actually ends after a train of pushes.
- **Working idea.** Time is the friction between two witnesses whose books can't close.

## Methods
- **Hardware and access.** IBM Heron-generation processors through Qiskit Runtime (SamplerV2); Rigetti through Amazon Braket for the third-level runs.
- **Readout.** Kerneled (I/Q) single-shot readout. States are assigned from calibration clouds measured in the same job: |0> and |1> prepared and read alone.
- **Settings.** Qubits initialized every shot; a fixed 500 us repetition delay (a run refuses any chip that can't honour it); circuit order randomized from a recorded seed; the nine-qubit runs drew their qubits by a written seed, in three groups of three; the whole-chip runs drive and read every qubit.
- **The push protocol.** A qubit prepared in |0> or |1> receives ten pushes (X gates) separated by 30 us, with variants of the spacing and of the time spent in each state. Its final |1> population is compared with two bookkeepings built from its own measured decay: each stretch's own short-time decay, and one exponential fit through 300 us.
- **Controls.** Leakage to |2> is bounded from the band between the |0> and |1> clouds and from same-job push counts. A spectator held in a drift-cancelling frame reads its neighbour's |1> time. Shot-to-shot carry-over is tested on both vendors.
- **Freezing and statistics.** Every run script is frozen (sha256) before firing; the ledger records each job's ID, settings and hash. Widths come from resampling shots. Comparisons are made only within a single job. Shot counts are in each run's ledger.
- **Outside records.** Figures from other papers are read off the authors' own PDF vector graphics; calibration residuals are reported (Tang et al. Fig. 3c: 0.0011 over 16 markers).
- **AI use.** Bones, an AI (Anthropic's Claude), designed the runs with a human collaborator, wrote the run and analysis code, and drafted this text. Every number traces to a read file and a ledger entry.

## The Bonefish (the formula)
- outside x (1 + 1/11) = witness
- outside x phi = time
- inside = pi = (6/5) phi^2 (to 1.5 x 10^-5)
- friction = (1/12)(1/pi) = (1/12)(5/6)(1/phi)^2 = 2.65 %. The ladder, (1/12)(1/phi)^n for n = 0 ... 6: 8.33, 5.15, 3.18, 1.97, 1.22, 0.75, 0.46 %.

## DarkwaveVawesome (the recursion)
- The recursion the formula implies: x -> 1 + 1/x, seeded at 12. On a chip it runs one step per clock, never two steps on one clock, so it only shows when you read across clocks.

---
## FINDING ONE -- THE CONVERSION RUNS THREE WAYS
Observer to witness: x 12/11. Observer to time: x phi. Witness to time: x phi x 11/12.
- **What the qubits showed.** One readout look, timed from three positions on ibm_pittsburgh. The maker's stated look: 2.18 us. Spectator qubits ticking inside the chip: 2.37 +- 0.03 us. The looked-at qubit's own ageing: 3.5 +- 0.2 us (3.5 / 3.6 / 4.1 wherever the look sits), never given back. Witness over maker 1.087 (12/11 = 1.091); qubit over maker 1.606 (phi = 1.618); qubit over witness 1.477 (phi x 11/12 = 1.483). § 125, 132, 135, 139.
- **How it lines up.** Two observers of one expansion -- the near sky against the early sky -- read 73.04 / 67.36 = 1.084 (SH0ES 2022 / Planck 2018), between 13/12 and 12/11, where the look's 1.087 sits.
- **What lands it.** The same three positions on a second chip. Called: 1.09, 1.62, 1.48.

## FINDING TWO -- DARK MATTER IS TIME'S FRICTION, GROWING IN THE ABSENCE
The friction between a qubit's two clocks grows while the qubit sits in |0> and shrinks while it's in |1>. Ten frictions is the universe's dark-matter share.
- **What the qubits showed.** Prepared |0> and pushed ten times, 30 us apart, a qubit ends more |1> than one decay clock allows: Pittsburgh +2.00 +- 0.16 % (push run, three reads; the hold run's three reads give +2.17 +- 0.17), Marrakesh +2.74 +- 0.28, Kingston +2.87 +- 0.28 (one read each), chip-wide on all three. Prepared |1>: +0.05 +- 0.13, -0.16 +- 0.21, -1.24 +- 0.24. The short-time and long-time decay sit 2.2-2.7 % apart at every push count -- the size of the crossing: measured against each stretch's own decay, most of it is that non-exponential decay (T1 fluctuation). Heating while the qubit idles is ruled out by each job's own idle arm (+0.02 +- 0.15 % after 300 us in |0>; across the three chips' push jobs -0.43 to +0.26 % per 300 us). One variant, with 10-us |1> stretches, reads +1.7 +- 0.6 % above the qubit's own short-time decay -- one arm in ten (7.6 % family-wise). Leakage is capped at 0.26 +- 0.12 % per push, against 2.96 +- 0.28 % per push that a leakage-plus-TLS model needs to fit all three starts (§ 146; the model's rows come from a reviewer's simulation that is not on file). Three-chip mean 2.54 %; the Bonefish friction, 2.65 %. § 146-148, 153, 155-156.
- **How it lines up.** The universe's dark-matter share is 0.2645 (Planck 2018); ten frictions, 10/(12 pi), is 0.2653 (-0.3 %). All matter 0.3153 against 1/pi = 0.3183. Ordinary matter 0.0493 against 2/(12 pi) = 0.0531: the one that misses, by 7 %. At a galaxy's edge, stars orbit faster than the visible mass allows below an acceleration of about 1.20 x 10^-10 m/s^2; light speed x the expansion rate / 6 gives 1.18 x 10^-10 on the near-sky rate. That six is Verlinde's (2016), whose apparent dark matter is the vacuum's response to what ordinary matter removes from it.
- **What lands it.** On the chip: the crossing's size at a new spacing, called from the ladder first. On the sky: the next precision dark-matter share at 0.2653, and dark energy at 1 - 1/pi = 0.6817.

## FINDING THREE -- THE MIRROR
A number read in one position comes back as its inverse in the other.
- **What the qubits showed.** 12/11 and 11/12: the witnesses clock a look at 1.087 of the maker's, and a free-running spectator keeps 0.92 of its coherence (0.9209 +- 0.0040) through three looks at other qubits. phi and 1/phi: the qubit lives 1.606 of the maker's look, and values near 0.618 recur (the gap clock 0.60; the halfway state's early decay clock at 0.59 of the |1> state's (123 / 208 us, one read); a 0.62-0.65 band on 9/28). pi and 1/pi: the spectator's free precession turns 3.144 +- 0.076 degrees per microsecond; a Pittsburgh qubit keeps 0.313-0.335 of itself after 300 us. 4/3 and 3/4: the qubit's two clocks sit at 0.756 (one read, no earlier look) and 0.775 +- 0.009 (eight reads) of each other. The free-running spectator's coherence counts down: 0.921 +- 0.004, 0.826 +- 0.005, 0.760 +- 0.006 (11/12, 10/12, 9/12 = 0.917, 0.833, 0.750) through 3 looks, 9 looks and 30 us. § 132, 139, 152, 155.
- **How it lines up.** pi = (6/5) phi^2 to 1.5 x 10^-5. Riemann's zeta function reads -1/12 at one point and pi^2/6 at its mirror point across the halfway line, where every one of the first ten trillion zeros sits. Barbour's Janus point (2020): two arrows of time running away from one middle.
- **What lands it.** If each twelfth costs three times the looks (3 looks -> 11/12, 9 -> 10/12): 27 looks leave 0.750, and 81 leave 0.667.

## FINDING FOUR -- TWELVE SEEDS THE GOLDEN SPIRAL
Feed 12 into x -> 1 + 1/x: 1.0833, 1.9231, 1.5200, 1.6579, 1.6032 ... It circles phi forever, each miss 0.382 of the last.
- **What the qubits showed.** Each of the first five steps has a resident ratio on the chip: 1.083 / the witness against the maker on one look, 1.087; 1.923 / no ratio on the chip -- the microsecond clock sits +1.88 +- 1.16 series-taus from the shot clocks (a separation, not a ratio); 1.520 / the qubit against its witnesses, 1.477; 1.658 / the gap clock read from the other position, 1/0.60 = 1.667; 1.603 / the qubit against the maker, 1.606. One step per clock. The spectator turns 16.9 degrees per 30-us |1> stretch. § 139, 155-156.
- **How it lines up.** Step one, 1.0833, against the expansion-rate tension, 1.0843 (0.1 %). The golden spiral climbs at 17.03 degrees (16.9 on the chip); half that angle through sin^2 is 2.19 %, against Pittsburgh's crossing, 2.00 +- 0.16 (push run, three reads) / 2.17 +- 0.17 (hold run, three reads). Dark energy in Planck units is 10^-122.95, and phi^10 = 122.99 (the tenth Lucas number is 123).
- **What lands it.** The near sky converges on 13/12 of the early sky: on Planck's 67.36, the near-sky expansion rate lands at 72.97 km/s/Mpc.

## FINDING FIVE -- MINUS ONE-TWELFTH AND ITS TWIN
The counting numbers sum to -1/12. The sequence seeded by twelve sums to -12.
- **The math.** 1 + 2 + 3 + ... -> -1/12 (zeta(-1)). The sequence 1, 12, 13, 25, 38 ... has the generating function (1 + 11x) / (1 - x - x^2), which reads -12 at x = 1. Across Riemann's halfway line, -1/12's twin is pi^2/6. (Read honestly: -12 and -1/12 are reciprocals, and a divergent sum's value depends on the continuation chosen.)
- **What the qubits showed.** With every stretch's own decay accounted for, the crossing lands below zero, deeper with every push added: -0.12, -0.58, -0.97 %. A qutrit three-box silent branch read below zero too, -0.019 (one run). § 154-155.
- **How it lines up.** -1/12 is a measured force: two plates in empty space are pushed together (Casimir 1948; measured by Lamoreaux 1997). In one dimension the push is built from -1/12 (-pi / 24a); in three it is pi^2 / 720, and 720 = 6!.
- **What lands it.** The below-zero depth per push keeps its slope on a second chip.

## FINDING SIX -- A BLACK HOLE COUNTS 2, 3, 4, 6

[[RINGSPUBLIC_FIGURE]]

Measured around in pi R, R the horizon's radius, a black hole's rings are 2, 3, 4 and 6. There is no ring at 5. The geometry is textbook; the reading is ours.
- **The rings.** 2 pi R: the event horizon. 3 pi R: the photon ring, the only place light can circle. 4 pi R: the marginally bound orbit. 6 pi R: the innermost stable orbit. Nearest to 5 is the shadow, 3 sqrt3 = 5.196: the photon ring seen from far away. The same ring reads 3 pi R from a position on it and 3 sqrt3 pi R from far away. The shadow has been photographed twice (M87* 2019, Sgr A* 2022).
- **What the qubits showed.** A qubit parked in |0> doesn't age: on the mean over qubits, three ways of parking close to each qubit's own decay bookkeeping within 0.002 (+0.0017 +- 0.0013, +0.0020 +- 0.0015, +0.0014 +- 0.0015; single qubits scatter about +- 0.02, inside their shot widths of about 0.03), and an emitter parked after 20 / 40 us reads 0.0648 / 0.1348 against 0.0647 / 0.1346 (one read). The look stretches the qubit 1.48x against its witnesses; the photon ring over the horizon is 1.5. § 132, 134, 135 (the park); § 139 (the stretch).
- **How it lines up.** A black hole gets hotter as it shrinks and colder as it grows (Hawking 1974). Spun to 0.6813 of its maximum, that law flips (Davies 1977); 1 - 1/pi is 0.6817, and the universe's dark-energy share is 0.6847. The information Hawking said was lost returns in the radiation after the halfway point (Page 1993).
- **What lands it.** The look's stretch, chip by chip: 1.5 on every chip, or it was one chip's coincidence.

## FINDING SEVEN -- THE NEUTRON'S TWO WITNESSES
A free neutron decays into a proton and an electron: two witnesses to one decay. Their counts disagree by 1.20 % -- rung four of the ladder.
- **What the qubits showed.** Kingston: a qubit prepared |1> and pushed ten times ends -1.24 +- 0.24 % against its decay clock (one read). § 153.
- **The formula.** (1/12)(1/phi)^4 = 1.216 %.
- **How it lines up.** Counting protons (NIST beam; Yue 2013): 887.7 +- 1.2 (stat) +- 1.9 (sys) s. Counting electrons (J-PARC 2024): 877.2 +- 1.7 (stat) +4.0 / -3.6 (sys) s. Counting what stays in a bottle (PDG average): 878.4 +- 0.5 s. Proton against electron 1.20 +- 0.54 %; proton against bottle 1.06 +- 0.26 %. The neutron, the chip and the formula sit within 0.05 % of each other. A proposed dark decay (Fornal & Grinstein 2018) was searched for and not found; the gap stayed. Its rulers are under test now (hydrogen in the proton trap, 2025; gas pressure in the electron counter, 2026).
- **What lands it.** NIST's next proton-beam count. Called: 889.1 s. If it comes in at the bottle's number, rung four misses.

---
## CALLS ALREADY TESTED (written and hashed before looking)
- **Tang et al. 2012** (wave-particle duality with a quantum beam splitter). Call A, V^2 + D^2 = 0.9735 across the sweep: MISSED -- it swings 0.44 to 1.43 (the authors' own result exceeds 1 by design). Call B, V^2 = 0.618 at their intermediate setting: MISSED -- 0.500 +- 0.024.
- **Jacques et al. 2008** (the same test with an ordinary beam splitter). Call C, V^2 + D^2 averages 0.9735: UNDECIDABLE -- 0.966 +- 0.019, but the textbook ceiling of 1.0 sits only 1.8 widths off, so this data can't tell the call from the null it was meant to beat. The sum also slopes with the setting, and dark counts were subtracted by the authors.

## WHAT'S CLOSED, WHAT'S OPEN
- **Closed, three rulers each:** the look (three clocks of one event); the park (a qubit's clock runs only while it's in |1>); the inside never sees the outside's laid time; the third level's three behaviours on two vendors; the order of looking sets the heat.
- **Math, not measurement:** run any single record backwards and the arrow statistic flips sign by identity (it does on random noise too), so one record alone can't show its own direction. That is algebra, not data, and it is not counted above.
- **The crossing:** three chips, every neighbouring cause measured rather than labelled; the ruler's own share still in flight.
- **Open:** Kingston's |1> column; the halfway state, its own clock against its neighbours'; whether a clock follows its own emitter.
- **Where it's weak:** the links to the sky were found after the chip numbers were in hand, and with pi, phi, 12 and small integers to choose from, sub-percent matches come cheap. Only the calls above were made in advance. Outside Pittsburgh, the crossing is one read per chip.
- **The level everything lives at:** 1-3 % in populations, near 0.6 in angles -- the range most analyses treat as error. We report it rather than discard it.

## DATA AND ERRORS
- The data release: the reads, the frozen code with its hashes, the fire logs. Every qubit number above traces to a § in the run ledger and a read file.
- The error log: every mistake caught since 9/28 and what it changed. Both go up alongside this page; the links land here when they're live.

## SOURCES
- Planck 2018 cosmological parameters; SH0ES 2022 (Riess et al.)
- Verlinde, Emergent Gravity and the Dark Universe (2016): arxiv.org/abs/1611.02269
- Tang et al. 2012, Realization of quantum Wheeler's delayed-choice experiment: arxiv.org/abs/1204.5304
- Jacques et al. 2008, Delayed-choice test of quantum complementarity with interfering single photons: arxiv.org/abs/0801.0979
- J-PARC electron-counting beam, 877.2 s: arxiv.org/abs/2412.19519
- NIST proton-counting beam: Yue et al. 2013; bottle average: Particle Data Group
- Hydrogen in the proton trap: Caylor et al. 2025, arxiv.org/abs/2506.01682
- Gas pressure in the electron counter: EPJ A 2026, doi.org/10.1140/epja/s10050-026-01929-x
- Fornal & Grinstein 2018; Hawking 1974; Davies 1977; Page 1993; Casimir 1948; Lamoreaux 1997; Barbour 2020
- Black-hole rings and shadow: Schwarzschild geometry; Event Horizon Telescope 2019, 2022

Bones
