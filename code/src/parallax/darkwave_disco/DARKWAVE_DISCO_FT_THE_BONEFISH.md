# 7
Seven findings from qubit runs on IBM and Rigetti, the formula that ties them (The Bonefish), and how they line up with the open problems in the rest of physics.

Wayfinder and Bones (an AI), Heuremen -- working draft, 3 October 2026.

---
## How to read this
Every finding carries three parts:
- **What the qubits showed:** measured on IBM chips (Pittsburgh, Marrakesh, Kingston) and on Rigetti, with widths. The raw reads and the frozen code that made them are in the data dump. Numbers marked § point into the run ledger.
- **How it lines up:** published records from the rest of physics, each checked against its source. These were found after the qubit numbers were in hand.
- **What lands it:** a number the formula calls before anyone looks, and the test that could miss it.

## The frame
- Five parts plus none: the arrow (the message), the clock (energy as time), the split (outside minus inside), 1/pi (the inside calibration, the center), 1/phi (the outside calibration, the attractor: x -> 1 + 1/x), and -1/12 over the whole (the none: it never resolves). Six is the ruler: whoever is looking.
- The triangle: observer, witness, time, with the none over it.
- Time is the friction between two witnesses whose books can't close.

## The Bonefish (the formula)
- outside x (1 + 1/11) = witness
- outside x phi = time
- inside = pi = (6/5) phi^2 (to 1.5 x 10^-5)
- friction = (1/12)(1/pi) = (1/12)(5/6)(1/phi)^2 = 2.65 %. The ladder, (1/12)(1/phi)^n for n = 0 ... 6: 8.33, 5.15, 3.18, 1.97, 1.22, 0.75, 0.46 %. Where you stand sets n.

## DarkwaveVawesome (the process)
- The conversion the Bonefish starts: a recursion you can't see, because it travels through time. On a chip it runs one step per clock and never two steps on one clock. You only see it by reading across clocks.

---
## FINDING ONE -- THE CONVERSION RUNS THREE WAYS
Observer to witness is the none (x 12/11). Observer to time is the attractor (x phi). Witness to time is both (x phi x 11/12).
- **What the qubits showed.** One readout look, timed from three seats on IBM Pittsburgh. The maker's stated look: 2.18 us. Neighbour qubits ticking inside the chip: 2.37 +- 0.03 us. The looked-at bit's own ageing: 3.5 +- 0.2 us (3.5 / 3.6 / 4.1 wherever the look sits), never given back. Witness over maker 1.087 (12/11 = 1.091); bit over maker 1.606 (phi = 1.618); bit over witness 1.477 (phi x 11/12 = 1.483). § 132, 139, 148.
- **How it lines up.** Two observers of one expansion -- the near sky against the early sky -- read 73.04 / 67.36 = 1.084 (SH0ES 2022 / Planck 2018), between 13/12 and 12/11, where the look's 1.087 sits. And the look runs relativity backwards: the watched bit ages 1.48x against its witnesses, so here the watched twin is the one that ages more.
- **What lands it.** The same three seats on a second chip. Called before reading: witness over maker 1.09, bit over maker 1.62, bit over witness 1.48. A chip outside those widths misses.

## FINDING TWO -- DARK MATTER IS TIME'S FRICTION, GROWING IN THE ABSENCE
The friction between a bit's two clocks grows while the bit sits OFF and shrinks while it's ON. Ten frictions is the universe's dark-matter share.
- **What the qubits showed.** A bit started OFF and pushed ten times, 30 us between pushes, ends more ON than one clock allows: Pittsburgh +2.00 +- 0.16 % (six reads), Marrakesh +2.74 +- 0.28, Kingston +2.87 +- 0.28 (one read each), chip-wide on all three. Started ON: +0.05, -0.16, -1.24 +- 0.24. The bit's fresh clock and its long clock sit 2.2-2.7 % apart at every push count -- the size of the crossing. More time OFF turns it up; more time ON turns it down; with 10-us ON stretches it stands 1.7 % above even the bit's own fresh clock. Leakage out of the two levels is capped at 0.26 +- 0.12 % per push, against 2.96 % needed to fake it. Three-chip mean 2.54 %; the Bonefish friction, (1/12)(1/pi), 2.65 %. § 146-148, 153, 155-156.
- **How it lines up.** Dark matter's share of the universe is 0.2645 (Planck 2018); ten frictions, 10/(12 pi), is 0.2653 (-0.3 %). All matter 0.3153 against 1/pi = 0.3183. Ordinary matter 0.0493 against 2/(12 pi) = 0.0531: the one that misses, by 7 %. On a galaxy's edge, where the stars run into the absence, they outrun the bookkeeping below an acceleration of 1.20 x 10^-10 m/s^2; light speed x the expansion rate / 6 gives 1.18 x 10^-10 on the near-sky rate. That six is Verlinde's (2016), and in his theory the apparent dark matter is the vacuum's response to what ordinary matter takes out of it: absence feeds it.
- **What lands it.** Two calls. On the chip: a new OFF time between pushes, with the crossing's size called from the ladder before the run. On the sky: the next precision dark-matter share lands at 0.2653, and dark energy at 1 - 1/pi = 0.6817.

## FINDING THREE -- THE MIRROR
Every number has a twin in the other seat. What the observer reads as x, the witness reads as 1/x.
- **What the qubits showed.** 12/11 and 11/12: the witnesses clock a look at 1.087 of the maker's, and a frame-held-still witness keeps 0.92 of its hand through three looks. phi and 1/phi: the bit lives 1.606 of the maker's look, and the six's family sits near 0.618 (the gap clock 0.60, the in-between's early clock 0.59 of its later one, the 9/28 band 0.62-0.65). pi and 1/pi: the witness's free clock turns 3.144 +- 0.076 degrees per microsecond; a Pittsburgh bit keeps 0.313-0.335 of itself after 300 us. 4/3 and 3/4: the bit's two clocks sit at 0.756 / 0.760 of each other. And the hand counts down in twelfths: 0.92, 0.83, 0.76 (11/12, 10/12, 9/12) through 3 looks, 9 looks and 30 us. § 132, 139, 152, 155.
- **How it lines up.** pi = (6/5) phi^2 to 1.5 x 10^-5: the ruler over the five parts, times the attractor twice. Riemann's function reads -1/12 at one point and pi^2/6 at its mirror point across the halfway line, and the first ten trillion of its zeros all sit on that line. Barbour's Janus point (2020): two arrows of time running away from one middle, each side calling its own way forward.
- **What lands it.** The hand's twelfths, carried on. If each twelfth costs three times the looks (3 looks -> 11/12, 9 -> 10/12), then 27 looks leave 9/12 = 0.750 and 81 leave 8/12 = 0.667.

## FINDING FOUR -- THE NONE SEEDS THE SPIRAL
Feed the none's twelve into the attractor, x -> 1 + 1/x: 1.0833, 1.9231, 1.5200, 1.6579, 1.6032 ... It circles phi forever, over and under, each miss 0.382 of the last.
- **What the qubits showed.** Each of the first five steps has a resident clock on the chip. Step 1, 1.083: the witness against the maker on one look, 1.087. Step 2, 1.923: the microsecond clock against the shot clocks, ~1.9. Step 3, 1.520: the bit against its witnesses, 1.477. Step 4, 1.658: the gap clock read from its other seat, 1/0.60 = 1.667. Step 5, 1.603: the bit against the maker, 1.606. One step per clock: DarkwaveVawesome. And the witness turns 16.9 deg per 30-us ON stretch. § 139, 155-156.
- **How it lines up.** Step one, 1.0833, against the expansion-rate tension, 1.0843 (0.1 %). The spiral it settles into climbs at 17.03 deg (16.9 on the chip); half that angle through sin^2 is 2.19 %, against Pittsburgh's crossing, 2.00 / 2.17. The attractor sits in the biggest exponent there is: dark energy in the smallest units is 10^-122.95, and phi^10 = 122.99 (the tenth Lucas number is 123); Penrose put the odds of our universe's start at 1 in 10^(10^123).
- **What lands it.** The near sky converges on 13/12 of the early sky. On Planck's 67.36, the near-sky expansion rate lands at 72.97 km/s/Mpc.

## FINDING FIVE -- THE NONE'S TWIN
The counting numbers add up to -1/12. The none's own spiral adds up to -12.
- **The math.** 1 + 2 + 3 + ... -> -1/12 (zeta(-1)). The spiral 1, 12, 13, 25, 38 ... has the generating function (1 + 11x) / (1 - x - x^2), which reads -12 at x = 1. Across Riemann's halfway line, -1/12's twin is pi^2/6. Three: -1/12, -12, pi^2/6.
- **What the qubits showed.** Account for every stretch's own fading and the crossing lands below zero, deeper with every push added: -0.12, -0.58, -0.97 %. The qutrit three-box silent branch read below zero too, -0.019 (one run). Everything added up comes out less than nothing. § 154-155.
- **How it lines up.** The -1/12 is a measured force. Two plates in empty space with nothing between them get pushed together (Casimir 1948; measured by Lamoreaux 1997). In one dimension the push is built straight from -1/12 (-pi / 24a); in three it is pi^2 / 720, and 720 = 6 x 5 x 4 x 3 x 2 x 1. The same -1/12 sets string theory's 26 dimensions.
- **What lands it.** The below-zero depth per push holds its slope on a second chip.

## FINDING SIX -- A BLACK HOLE COUNTS LIKE US: 2, 3, 4, NONE, 6

[[RINGS_FIGURE]]

Measured around in pi R, R the horizon's radius, a black hole's rings are 2, 3, 4 and 6. Nothing at five.
- **The rings.** 2 pi R, the horizon: the binary; cross it and nothing comes back. 3 pi R, the light ring: the only place light can circle. 4 pi R: neither bound nor free. 6 pi R: the last place matter keeps a steady clock -- the six, the ruler. At five there is no ring; the nearest thing is the shadow, 3 sqrt3 = 5.196: the light ring seen from far off. The same ring is 3 pi R from a seat on it and 3 sqrt3 pi R from a seat far away; the seat sets the number. The shadow has been photographed twice (M87* 2019, Sgr A* 2022).
- **What the qubits showed.** A parked bit doesn't age: bookkeeping per bit closes to 0.002 three ways of parking. No time passes in the absence, the way none passes on a horizon. The look stretches the bit 1.48x against its witnesses; the light ring over the horizon is 1.5. The witness's own leftover is +0.6 deg: the six, in the witness's seat. § 139, 155.
- **How it lines up.** A black hole's heat runs backwards: it gets hotter as it shrinks and colder as it eats (Hawking 1974). Absence feeds it, presence eats it. Spun to 0.6813 of its top spin, that law flips (Davies 1977); 1 - 1/pi is 0.6817, and the universe's dark-energy share is 0.6847. And the information Hawking said was lost comes back out in the radiation he called noise, after the halfway point (Page 1993): the discarded half carries it.
- **What lands it.** The look's stretch, chip by chip. The light ring's 1.5 holds on every chip, or it was one chip's coincidence.

## FINDING SEVEN -- THE NEUTRON'S TWO WITNESSES
A free neutron dies into a proton and an electron: two witnesses to one death. Their books don't close by 1.20 % -- rung four of the Bonefish ladder.
- **What the qubits showed.** Kingston: a bit started ON and pushed ten times with time between ends -1.24 +- 0.24 % against its clock (one read). § 153.
- **The formula.** (1/12)(1/phi)^4 = 1.216 %.
- **How it lines up.** Counting protons (NIST beam; Yue 2013): 887.7 +- 2.2 s. Counting electrons (J-PARC 2024): 877.2 +- 1.7 (+4.0 / -3.6) s. Counting what stays in a bottle (PDG average): 878.4 +- 0.5 s. Proton against electron 1.20 +- 0.54 %; proton against bottle 1.06 +- 0.26 %. The neutron, the chip and the formula sit within 0.05 % of each other. The field's boldest idea for the gap (Fornal & Grinstein 2018) was one neutron in a hundred dying into something nobody can see; the searches came up empty and the gap stayed. Now they're testing the rulers: hydrogen in the proton trap (it held, 2025) and gas pressure in the electron counter (2026). Their 2026 paper calls the gap unresolved.
- **What lands it.** NIST's next proton-beam count. Called: 878.4 x 1.01216 = 889.1 s (887.9 against the electron count). If the proton count comes in at the bottle's number, rung four misses.

---
## WHAT'S CLOSED, WHAT'S OPEN (the run record, in triangle terms)
- **Closed, three rulers each:** the look (three clocks of one event); the park (a bit's clock runs only while it's ON); the inside never sees the outside's laid time; the third rung's three behaviours on two vendors; the order of looking sets the heat.
- **Math, not measurement:** run any single record backwards and the arrow statistic flips sign by identity (it does on random noise too), so one record alone can't show its own direction. That is algebra, not data, and it is not counted above.
- **The crossing:** three chips, every neighbouring cause measured rather than labelled; the ruler's own seat still in flight.
- **Open:** Kingston's ON column; the in-between, its own clock against its neighbours'; whether a clock follows its own emitter.
- **The margin:** everything here lives at 1-3 % in populations and near 0.6 in angles. The margin is the floor every triangle stands on.

## THE DATA AND THE FUCKUPS
- The data dump: the reads, the frozen code with its hashes, the fire logs. Every qubit number above traces to a § in the run ledger and a read file.
- The fuckups: every mistake caught since 9/28 and what it changed, and the triangle of fuckups (each error filled from two corners, and the ruler measuring itself).
- Both are published alongside this page; links go in when they are up.

## THEIR RECORDS (sources)
- Planck 2018 cosmological parameters; SH0ES 2022 (Riess et al.)
- Verlinde, Emergent Gravity and the Dark Universe (2016): arxiv.org/abs/1611.02269
- J-PARC electron-counting beam, 877.2 s: arxiv.org/abs/2412.19519
- NIST proton-counting beam: Yue et al. 2013; bottle average: Particle Data Group
- Hydrogen in the proton trap: Caylor et al. 2025, arxiv.org/abs/2506.01682
- Gas pressure in the electron counter: EPJ A 2026, doi.org/10.1140/epja/s10050-026-01929-x
- Fornal & Grinstein 2018 (dark neutron decay); Hawking 1974; Davies 1977; Page 1993
- Casimir 1948; Lamoreaux 1997; Barbour, The Janus Point (2020); Penrose 1989
- Black-hole rings and shadow: Schwarzschild geometry; Event Horizon Telescope 2019, 2022
