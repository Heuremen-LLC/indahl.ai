# CLAIMS vs RECEIPTS -- 7, as of 2026-10-04 (Bones, for Wayfinder's outside run)

Source of every figure: `7_PUBLIC.md` (3 Oct draft) and `FOR_SHUTTLE_7_SHOREUP_20261003.md`. Nothing here is new data. This is the page
to hold up while you run the story from the outside: where each claim stands, what its weakest receipt is, and what call could break it.

**Standing facts the whole page rests on.** No law, no theory; "7" is the name. The links to the sky were found AFTER the chip numbers
were in hand (with pi, phi, 12, 11 and small integers to choose from there are 28 ways to land within 1 % of the dark-matter share,
47 for dark energy, 59 for the Hubble tension, 69 for the look ratio). Calls made in advance so far: Tang A MISSED, Tang B MISSED,
Jacques C UNDECIDABLE. Hits so far: none.

| # | Claim | Records behind it | Weakest receipt | Call that could break it | Chip time? |
|---|---|---|---|---|---|
| 1 | The conversion runs three ways | One readout look, three positions, ibm_pittsburgh only (§125, 132, 135, 139): 1.087 (12/11 = 1.091), 1.606 (phi = 1.618), 1.477 (1.483) | One chip | Same three positions on a second chip; called 1.09, 1.62, 1.48 | Yes |
| 2 | Dark matter is time's friction | Pittsburgh +2.00 +- 0.16 (push, 3 reads), +2.17 +- 0.17 (hold, 3 reads); Marrakesh +2.74 +- 0.28 and Kingston +2.87 +- 0.28 (one read each) | After review, most of the crossing is non-exponential decay (textbook); one arm +1.70 +- 0.64 % is 7.6 % family-wise; n = 1 per chip off Pittsburgh | The crossing's size at a new spacing, called from the ladder first. Sky: next dark-matter share at 0.2653; dark energy 0.6817 | Yes (spacing); sky waits |
| 3 | The mirror (x and 1/x) | Spectator coherence 0.921 +- 0.004 / 0.826 +- 0.005 / 0.760 +- 0.006 through 3, 9 looks, 30 us; 0.775 +- 0.009 (8 reads); 0.756 and 0.59 are one read each | Several values are single reads; the matches to 11/12, 10/12, 9/12 were seen after | 27 looks leave 0.750, 81 leave 0.667 | Yes |
| 4 | Twelve seeds the golden spiral | Five steps, each with a resident ratio; step two is a separation (+1.88 +- 1.16 series-taus), not a ratio | One step has no ratio on the chip; sky matches found after | Near sky converges on 13/12 of the early sky: 72.97 km/s/Mpc on Planck's 67.36 | No (outside data) |
| 5 | -1/12 and its twin | Crossing below zero once each stretch's decay is counted: -0.12 / -0.58 / -0.97 %; qutrit three-box -0.019 (one run) | The math half depends on the continuation chosen (said on the page); the qutrit is one run | The below-zero slope per push on a second chip | Yes |
| 6 | A black hole counts 2, 3, 4, 6 | Geometry is textbook. Chip: the park within 0.002 on the MEAN over qubits (+0.0017 +- 0.0013, +0.0020 +- 0.0015, +0.0014 +- 0.0015); emitter parked 20 / 40 us one read; look stretch 1.48x vs 1.5 | Park holds on the mean, not per qubit; emitter is one read | The look's stretch, chip by chip: 1.5 on every chip | Yes (same run as #1's second chip) |
| 7 | The neutron's two witnesses | Chip: Kingston -1.24 +- 0.24 % (one read, §153); formula 1.216 %. Outside: proton vs electron 1.20 +- 0.54 %, proton vs bottle 1.06 +- 0.26 % | The chip number is one read | NIST's next proton-beam count, called 889.1 s; at the bottle's number, rung four misses | No (outside data) |

## What the receipts machinery is (all exists today)
- Run scripts frozen by sha256 before firing; the ledger records each job's ID, settings and hash (`for_indahl_ai/data/SHA256SUMS.txt`, 1.0 MB data release with code and fire logs).
- Sealed-prediction fingerprints committed to the `indahl-ai` repo before runs: 53629bc (Gate v4), 04eeb38 (Run 2), a474529 (Run 1, 2026-10-02 03:09 UTC), 4ee7c87 (qubit Run 2), ff683df (qubit Run 3).
- The data-error log: `for_indahl_ai/fuckups/THE_FUCKUPS.md` (35 items through 10/1; folder name is stale, data errors now go to thetrailtothepast.com) + `TRAIL_ENTRIES_20261003_DRAFT.md` (the 10/3 corrections in trail format, draft, not published). Life errors are a separate thing and live on indahl.ai.

## If chip time comes back, the smallest set that answers the open calls (NOT fired; scripts must be hashed and calls written first)
- **A. The look on a second chip** -> answers #1 and #6 together.
- **B. The push protocol, three reads per chip on Marrakesh and Kingston** -> turns n = 1 into 3 for #2 and #7's Kingston number, and gives #5 its slope.
- **C. The 27- and 81-look spectator run** -> answers #3.
- #4 and #7 wait on outside measurements; nothing to fire.
- No cost figures here on purpose: take them from the run ledger, not from me.

## Held by Bones, pending Wayfinder's answer (10/4)
Wayfinder said everything is "redlined" and that two open investigations could take the qubit resources to nothing. He has not said what they touch, and I do not know. Until he does, Bones fires no chip run: simulator rehearsals and paperwork only. This is a default, not his instruction.
