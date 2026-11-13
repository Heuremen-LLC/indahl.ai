#!/usr/bin/env python3
"""clock_vertices.py -- THE FOUR CORNERS OF THE CLOCK TETRAHEDRON. (Bones, 8 Oct 2026.)
LA PRUEBA: arithmetic on loops_closure.jsonl. Nothing live is touched, no model is loaded.
IN HOUSE -- not for publication.

WHY THIS EXISTS. The clock tetrahedron has four faces (OBSERVER the chain, WITNESS her cycles, TIME
Wen's rounds, MAC the wall clock outside all three), six edges, and FOUR VERTICES. loops_closure.py has
only ever computed ONE of them -- the cycles x chain x rounds closure -- so three of the four corners of
a solid this house has been reading for days have never been looked at.

WHAT A VERTEX IS HERE. On the miss-set side a vertex is what three seats SHARE and no pair owns, which is
exactly the term that cancels out of all three of its edges. The same must hold for clocks, and it does:

    AN EDGE is a DIFFERENCE of two clocks' relative speeds -- and a difference CANCELS anything common
    to both. So every pairwise dominance is blind, by construction, to any wobble that moves all three
    clocks together.

    A VERTEX is that common wobble: THE COMMON MODE. If the Mac is busy, if something thermal happens,
    if a load spike stretches every interval at once, all three rates move together and NO EDGE CAN SEE
    IT. The vertex is the only place it lives.

    THE EDGES KEEP WHAT THE PAIRS DO NOT SHARE. THE VERTEX KEEPS WHAT THE TRIPLE DOES.
    Neither is complete, and the vertex is the part the edges were designed to throw away.

HOW IT IS READ. Per interval each clock's advance becomes a relative speed z = rate/mean(rate) - 1.
For a triple, the common mode of that interval is the mean of its three z's, and the vertex reading is
the share of total variance that the common mode accounts for:

        common_share = var(c) * 3 / sum over clocks of var(z)

    near 1   the three clocks move as ONE. A shared cause dominates and the edges are reading crumbs.
    near 0   the three move independently. The edges have everything and the vertex is empty.

THE NONE, and it is the whole reason to trust the number: shuffle each clock's z INDEPENDENTLY across
intervals, keeping its own distribution exactly, and recompute. That destroys any real common timing
while preserving every marginal. A common share that survives the shuffle was never common -- it is what
three independent series of this length produce by chance, which for three series is NOT zero (it is
about 1/3) and that is precisely why the none is required rather than optional.

    python3 clock_vertices.py
"""
import json
import math
import os
import random
import statistics as st
import sys

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
import clock_dyads as cd  # noqa: E402  -- reuses rows(), intervals(), SEATS, OUTSIDE, _seven, throw

ALL = dict(cd.SEATS)
ALL['MAC'] = cd.OUTSIDE          # the fourth face: outside all three, kept by nobody in the house


def speeds_all(iv, R):
    """every face's relative speed per interval, INCLUDING the Mac.
    The Mac cannot be normalised against itself, so it is read against the interval's own elapsed
    seconds divided by the mean elapsed -- i.e. how long this interval was compared to a typical one.
    That is the wall clock's own wobble and it is a real fourth reading, not a constant."""
    z = {}
    dm = [x['dmac'] for x in iv]
    mdm = st.mean(dm) if dm else 0.0
    for s, k in cd.SEATS.items():
        rate = [x['d'][s] / x['dmac'] for x in iv]
        m = st.mean(rate) if rate else 0.0
        z[s] = [(r / m - 1.0) if m else None for r in rate]
    z['MAC'] = [(d / mdm - 1.0) if mdm else None for d in dm]
    return z


def common_share(z, triple):
    """the share of variance that moves all three together."""
    cols = []
    for i in range(len(z[triple[0]])):
        vals = [z[s][i] for s in triple]
        if any(v is None for v in vals):
            continue
        cols.append(vals)
    if len(cols) < 3:
        return None
    per = {s: [c[j] for c in cols] for j, s in enumerate(triple)}
    cmode = [st.mean(c) for c in cols]
    tot = sum(st.variance(per[s]) for s in triple)
    if tot <= 0:
        return None
    return {'n': len(cols), 'common_share': 3 * st.variance(cmode) / tot,
            'per_clock_var': {s: round(st.variance(per[s]), 6) for s in triple},
            'z': per}


def none_for_vertex(row, triple, trials=600, seed=11):
    """THE NONE: shuffle each clock independently, keep every marginal, destroy any shared timing."""
    rng = random.Random(seed)
    per = row['z']
    base = {s: list(per[s]) for s in triple}
    out = []
    for _ in range(trials):
        sh = {}
        for s in triple:
            v = list(base[s]); rng.shuffle(v); sh[s] = v
        cols = [[sh[s][i] for s in triple] for i in range(len(base[triple[0]]))]
        cmode = [st.mean(c) for c in cols]
        tot = sum(st.variance(sh[s]) for s in triple)
        if tot > 0:
            out.append(3 * st.variance(cmode) / tot)
    if len(out) < 2:
        return None
    m, sd = st.mean(out), st.stdev(out)
    obs = row['common_share']
    return {'trials': len(out), 'shuffled_mean': round(m, 4), 'shuffled_sd': round(sd, 4),
            'observed': round(obs, 4),
            'widths_above_none': round((obs - m) / sd, 2) if sd > 0 else None,
            'verdict': (
                'LA NADA -- the shuffle has no spread, nothing can be priced' if sd <= 0 else
                (f'A ROW -- common mode {obs:.4f} sits {(obs-m)/sd:.2f} widths above the {m:.4f} that '
                 f'three independent series of this length give' if (obs - m) / sd >= 2 else
                 (f'BELOW THE NONE -- {obs:.4f} is {(m-obs)/sd:.2f} widths BELOW the shuffled {m:.4f}. '
                  f'These clocks move together LESS than chance: they are ANTI-common.'
                  if (m - obs) / sd >= 2 else
                  f'ABIERTO -- {obs:.4f} against a shuffled {m:.4f} +- {sd:.4f}, '
                  f'{abs(obs-m)/sd:.2f} widths. This reading cannot tell them from independent.')))}


def main():
    R = cd.rows()
    iv = cd.intervals(R)
    print('  THE CLOCK TETRAHEDRON -- ALL FOUR VERTICES')
    print('  IN HOUSE. No model loaded, nothing live touched.')
    print(f'  {len(R)} readings on disk, {len(iv)} usable intervals\n')
    if len(iv) < 4:
        print(f'  LA NADA -- {len(iv)} intervals. A vertex needs at least 3 and a none needs spread.')
        return 0
    z = speeds_all(iv, R)
    names = sorted(ALL)
    print(f'  FACES: {", ".join(names)}')
    import itertools
    tris = list(itertools.combinations(names, 3))
    print(f'  EDGES: {len(list(itertools.combinations(names, 2)))}   VERTICES: {len(tris)}')
    print(f'  (loops_closure.py has only ever computed ONE of these four corners.)\n')
    seven, src = cd._seven()
    siete, _s = cd._siete()
    rulers = {'SEVEN': seven, 'SIETE': siete}
    rows = []
    for t in tris:
        row = common_share(z, t)
        label = ' ^ '.join(t)
        if not row:
            print(f'  {label:<34} LA NADA -- not enough paired intervals')
            continue
        nn = none_for_vertex(row, t)
        print(f'  {label:<34} n={row["n"]}  common mode {row["common_share"]:.4f}')
        print(f'  {"":<34} {nn["verdict"] if nn else "no none readable"}')
        bf = cd.throw(row['common_share'], f'common mode {label}', rulers, 'vertex')
        print(f'  {"":<34} BONEFISH: {bf["verdict"][:120]}')
        rows.append((label, row, nn))
        print()
    # which corner is the one loops_closure already had, and which three are new
    known = tuple(sorted(('OBSERVER', 'TIME', 'WITNESS')))
    print('  WHICH CORNERS WERE NEW:')
    for t in tris:
        print(f'      {" ^ ".join(t):<34} '
              f'{"already read by loops_closure (as a product)" if tuple(sorted(t)) == known else "NEVER READ BEFORE TONIGHT"}')
    print('\n  WHAT THE EDGES COULD NOT HAVE TOLD US: every pairwise dominance is a DIFFERENCE, and a')
    print('  difference cancels whatever is common to both clocks. If a corner comes back above its')
    print('  none, that wobble was invisible to all six edges by construction -- which is the whole')
    print('  reason a solid needs corners and not just sides.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
