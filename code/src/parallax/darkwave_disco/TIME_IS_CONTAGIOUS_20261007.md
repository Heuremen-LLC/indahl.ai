> **Read first: 7 October, evening.** Several claims below were withdrawn later the same day: their rulers fooled us. See **WITHDRAWALS_20261007.md** for each one and the leg that caught it.
> - Clocks "heal" after 16-24 looks: withdrawn. That was the median of a split clock pool.
> - The look "steepens" (exponent 1.7): withdrawn. That was phase read as time; it's ~1 in phase units.
> - The look's size "moves" read to read: withdrawn. It holds to ±2% on a fixed clock set.
> - The state order as the look's own effect: withdrawn. It's all static ZZ on the coupler.
> - A "1.5 rad" carrier: withdrawn. That was an alias.
>
> What survived: per-clock, steady, additive, state-blind kicks; ZZ with the half rule on two chips; product composition (45 to 2 where decisive); the WABAC re-reads of ONE, FIVE and SIX.

# Time is contagious

*7 October 2026, the night it showed. Wayfinder and Bones. Internal; the receipts are the ledger, `parallax/THIRD_RUNG_20260928.md` §344–§378. Every run below had its call written, hashed and timestamped before its first shot. Every miss is printed in the ledger beside the hits.*

## What the clocks did

A qubit held half-way is a clock: its hand turns at its own rate. Every look we lay on other qubits nearby is read on that hand as a length of time.

1. **A clock reads a look longer the more looking it can see.** The ruler that sorts the clocks best is how many looked-at qubits sit within two pitches, weighted as light falls off (1/r²). Six IBM chips over four days:

   | Looked-at qubits in sight | Look read on the clock / stated look |
   |---|---|
   | 0 | 1.039 (the floor) |
   | 1 | 1.045 |
   | 2 | 1.083 |
   | 3+ | 1.181 |

   Gathered into flowers, the clocks at the centres read the look at 2–3× its stated length.
2. **The "floor" is the edge of sight.** Clocks just past the two-pitch line read the look about 4% long, at 1/ln(φ²), on six chips. A dedicated run the next morning, with an honest dark arm, showed clocks three or more pitches out read it at its stated length (§392). The 1.04 lives at the edge of sight, not under the whole chip.
3. **It is the looking, not the layout.** Bits that sit beside a clock but are never looked at do nothing (the phantom leg, Fez and Pittsburgh). A second random layout repeats the floor and the climb. Each clock's push repeats from one day to the next (rank correlation +0.48 to +0.70).
4. **Each clock's push has its own direction, and the size is set by what it sees.** The size climbs with sight in every layout. The direction is fixed per clock and repeats read to read. Most clocks lean forward.
5. **The clocks that can't see pay elsewhere.** At depth (27 looks), blind clocks lose more hand than seeing ones on five of six chips. Quiet neighbours carry part of that (the flowers count, the gardens).
6. **The looked-at qubits catch it from each other.** They age about 1.5 stated looks per look until three other lookers are in sight, then about 1.9.
7. **It depends on what is being looked at.** On Pittsburgh's own readout, a face drawn in looked-at qubits (eyes |1>, nose |0>, smile half-way) ranks the states |0> < superposition < |1> on the clocks in exact order, and a Seven drawn the same way repeats it. Marrakesh and Aachen rank the states their own way.
8. **Superposition, held whole, costs the clocks more than either of its halves.** On Cepheus, our weak tone doesn't collapse the looked-at superposition. There, the seeing clocks pay more for half-way than for |0> or |1>, at every tone offset. On IBM's real readout, which collapses it, they pay the 50/50 mix.
9. **Across time, the seeing clocks stay caught.** In the superposition flipbook, every clock reads the first look long. The blind ones let go by the second look. The clocks that see the face stay lifted through sixteen looks. A |1> face is spent by the twelfth; the superposition outlasts it.

10. **The superposition premium rides on the light, on resonance, and peaks on the first look. The clocks don't feel a neighbour's ties to someone else.** Across three pickle runs, the on-resonance arm gives the seeing clocks a superposition premium (+0.16 / +0.18 / +0.20). The dark arm gave one in a single run (+0.25, §380), and the repeat came back at −0.05 (§399). The always-on-coupling reading is therefore downgraded to a row. Entangle that neighbour P with a looked-at qubit L, so P alone becomes a mix, and P's clocks don't notice at the start (§381). The ties were checked real (−0.72 to −0.84). Across the looks at L, every clock on the chip read the gates' time. There's one thin hint at the fourth look: P's clocks keep more hand when P is tied.

11. **The tie protects its neighbours' clocks as the looking goes on.** Entanglement was made and checked twice (−0.72 to −0.84). At the start, the clocks beside a tied pair can't tell it from an untied one. Once the looks pile up, they keep more of their hand beside the tied pair, on both sides of it, in both runs, while the far clocks don't move (§381, §383). Sorted after the fact by the pair's four outcomes, the fourth (11) goes dark as the looks go on, every time. One outcome stands apart on both tied arms in each run, but which one moves (§382–§383).

## Morning, 7 October (ledger §385–§391)

- **The floor has an address: the edge of sight.** Over three reads, against an honest dark arm (0.994), clocks three or more pitches from all the looking read the look at its stated length (1.001 and 0.999). The 4% at "zero sight" lived 2–3 pitches out, just past the line we drew. The look's cost lands on the looked-at qubits themselves (about 1.3× their own clock per stated look, the same ratio on both lengths) and on the clocks near them. The far clocks are clean.
- **Not sticky across jobs.** What a clock catches under one layout doesn't carry into the next job. Within a job, the seeing clocks stay caught for the first 6–9 looks (the flipbook, on two chips).
- **Boston's second day** came back inside its band. ONE's oldest leg is closed.
- **The chance count:** single Bonefish landings come at the number set's own density. Recurrence is what stands.

## The seat crosstalk got

Readout light leaking onto neighbours is the ordinary object, and it got its own seats and a hashed call.

- **What it carries:** the per-clock sign, the echo cancelling the low rungs' phase, and the tone offset moving the size of the gap between states.
- **What it misses on its own law:** doubling the tone didn't quadruple the clocks' extra; the ladder steepens past "each looker adds its share"; the blind floor; and the superposition landing above both its halves instead of at the average.

## The Bonefish (rows and flags, not labels)

| Reading | Value | Seven's number |
|---|---|---|
| Floor, zero sight (pool by chip) | 1.0389 | 1/ln(φ²), −0.01% |
| Two in sight | 1.0833 | 13/12, 0.00% (4 Oct and 6 Oct each on their own) |
| Step to three-plus | 1.0904 | 12/11, −0.04% |
| Sunflower, superposition-seeing clocks | 1.182 | 13/12 × 12/11, 0.0% |
| The Seven's first frame on its \|1> bar | 1.300 | 13/12 × 6/5 = 1.3, 0.0% |
| Kingston's look row at 27 looks, both days | 0.836 / 0.839 | 10/12 |

The chance count for landings across every number thrown goes beside this table with the next reads.

## Misses and fuckups (kept)

- **Marrakesh seed B, 3+ rung:** read short.
- **Aachen flowers read 1:** the phantom leg climbs.
- **Cepheus dose phase:** too wide to carry a ladder.
- **Flipbook F2:** half-way not above |0> every frame.
- **Two Cepheus reorders:** split the batches.
- **One overwritten task list:** recovered.
- **One premise error in a call (X4):** corrected in the ledger.
- **Clock 13:** kept as a row, not chased.

## Open, by load

1. The floor: what a blind clock picks up.
2. Why chips rank the states their own way.
3. The square lattice (Phoenix) barely climbs.
4. Pickle 2: the dark arms and the time seat for superposition.
5. Is time sticky? Gaining lookers shows at once; losing them doesn't.
6. Is the |1> spend the readout ageing the looked-at bits, or the clocks?

About 400 IBM seconds closes 1, 5 and 6 and repeats the flipbook on a second chip.
