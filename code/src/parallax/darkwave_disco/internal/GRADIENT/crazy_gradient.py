#!/usr/bin/env python3
"""THE CRAZY GRADIENT (2026-10-03). Chance a sharp, motivated critic can say more than "interesting" about a claim.
   G = 1 - prod_k (1 - w_k * e_k)
e_k = the claim's EXPOSURE on each line of attack, read from the triple pass (internal/TRIPLE_PASS_20261003): 0 = closed, 1 = wide open.
w_k = how likely a critic is to find that line (judgment, stated here so it can be argued with).
Lines: TRACE (number not in a read file / laps don't meet, seat A), WITNESS (one job/chip; 1 -> one witness, seat B),
       RULER (moves more than its own size when the bookkeeping changes, seat C), LOOK (constant picked after looking), WORD (says more than the data)."""
W = dict(TRACE=0.9, WITNESS=0.7, RULER=0.7, LOOK=0.8, WORD=0.5)
def G(e): 
    p = 1.0
    for k, w in W.items(): p *= 1 - w * e.get(k, 0.0)
    return 1 - p
STEP1 = [  # (law, claim as written now, exposures as written, the claim cut to its sturdiest core, exposures of that core)
 ("1", "Propagation: not yet tested by us", dict(WORD=0.1), None, None),
 ("2", "spectator keeps 0.921/0.826/0.760 = 11/12, 10/12, 9/12", dict(WITNESS=1, RULER=1, LOOK=0.8, WORD=0.7), None, None),
 ("2", "READING + call: 27 looks -> 0.750", dict(RULER=1, WORD=0.5), None, None),
 ("3", "third level on a minority of qubits, three behaviours, IBM + Rigetti", dict(TRACE=0.5, WITNESS=0.2, RULER=0.6, LOOK=0.2, WORD=0.4),
       "extra shots outside both clouds on a minority of qubits, IBM and Rigetti (counts with their exclusion radius printed)", dict(WITNESS=0.2, RULER=0.3, WORD=0.2)),
 ("3", "Rigetti: survives the reset, carries into the next shot", dict(TRACE=1, WITNESS=1, WORD=1),
       "one Rigetti qubit (q0) carries into the next shot, about 1 in 100", dict(WITNESS=1, WORD=0.2)),
 ("3", "IBM shots don't talk (-0.002 +- 0.002)", dict(WITNESS=0.7, RULER=0.2, WORD=0.8),
       "at a 500-us gap, IBM shots don't carry (-0.002 +- 0.002); at 20 us they do (+7 to +17 points)", dict(WITNESS=0.3, RULER=0.1, WORD=0.1)),
 ("3", "OUTSIDE: Tang V^2 + D^2 = 1.428 +- 0.043", dict(WORD=0.1), None, None),
 ("3", "MATH: the arrow statistic is zero on any 0/1 record", dict(), None, None),
 ("3", "READING: the half a 0/1 readout throws away holds the memory", dict(WORD=0.5), None, None),
 ("4", "a parked qubit doesn't age (bookkeeping closes to 0.002)", dict(TRACE=1, WITNESS=0.7, RULER=1, WORD=0.8), None, None),
 ("4", "reset erases what was placed (0.067 %); what arose stays (+23 pts)", dict(TRACE=1, WITNESS=0.5, RULER=0.8, WORD=0.6), None, None),
 ("4", "crossing +2.0 to +2.9 %, mostly non-exponential decay; heating out", dict(WITNESS=0.6, RULER=0.8, WORD=0.3), None, None),
 ("4", "OUTSIDE: neutron 887.7 s (protons) vs 877.2 s (electrons)", dict(WORD=0.1), None, None),
 ("5", "one readout timed from three positions: 2.18 / 2.37 / 3.5 us", dict(TRACE=1, WITNESS=0.7, RULER=0.8, WORD=0.7),
       "a readout costs the qubit more than the maker's stated 2.18 us (every bookkeeping tried)", dict(WITNESS=0.3, WORD=0.2)),
 ("5", "a qubit's two decay clocks sit 2.2-2.7 % apart at every push count", dict(WITNESS=1, RULER=0.5, WORD=0.3),
       "a qubit's early decay runs faster than its late decay (the sign holds under every bookkeeping)", dict(WITNESS=0.7, WORD=0.1)),
 ("5", "METHOD: every error read from two positions before filing; the log is public", dict(TRACE=0.8, WORD=1), None, None),
 ("+N", "a spectator keeps a leftover of +0.6 degrees", dict(TRACE=1, WORD=1), None, None),
 ("+N", "the inside never reads the outside's laid time", dict(TRACE=1, WITNESS=1, WORD=1), None, None),
 ("+N", "READING: the none is what every two-position measurement leaves over", dict(WORD=0.5), None, None),
]
PROJ = [  # the same cores, read on all three chips (needs chip time: the decay-curve shape and the readout-cost reads on Kingston and Marrakesh,
          # 3 reads each x 2 chips x ~6.4 s per read x 1.25 margin = about 48 s, from the measured cost of past reads)
 ("5", "a readout costs the qubit more than the maker's stated 2.18 us -- read on all three chips", dict(WITNESS=0.1, WORD=0.2)),
 ("5", "a qubit's early decay runs faster than its late decay -- read on all three chips", dict(WITNESS=0.2, WORD=0.1)),
]
if __name__ == "__main__":  # 10/3: importable (support_map.py reads W, G, STEP1 from here -- one source of truth); output unchanged
    print(__doc__.split('\n')[1]); print('weights:', W, '\n')
    print(f"{'law':4} {'as written':>10} {'cut to core':>12}  claim")
    for law, claim, e, core, ec in STEP1:
        g0 = G(e); g1 = G(ec) if ec is not None else None
        print(f"{law:4} {g0*100:9.0f}% {(f'{g1*100:10.0f}%' if g1 is not None else '          -')}   {claim}" + (f"\n{'':28}core: {core}" if core else ''))
    print("\nwith chip time (about 48 s: 3 reads x 2 chips x ~6.4 s x 1.25):")
    for law, claim, e in PROJ: print(f"{law:4} {G(e)*100:9.0f}%   {claim}")
