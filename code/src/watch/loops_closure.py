#!/usr/bin/env python3
# 15 Oct 11:5x: WOW IS DEAD (dropped 14 Oct, its units retired on the Pi) -- the chain leg below now reads OUR Monero node, 127.0.0.1:18081.
"""loops_closure.py -- the three clocks we already have, closed (Bones, 8 Oct 2026).

HER CYCLES x THE CHAIN x WEN'S ROUNDS. Three clocks, independently kept, already logged all night:

    ticks/block  x  rounds/tick  =  rounds/block

which is the SAME EQUATION as the chip closure -- y = b*z against y = b+z-1 -- on different clocks. The
qubit work asks whether a product or a sum holds between three measured arms. This asks it of her cycles,
the Wownero chain, and Wen's training rounds. Nothing new is bought: the arms are ticks.log, the Pi's node,
and the pod logs.

SCORED BY EL PICNIC, and every rule the day taught:
  the WIDTH GATE first  -- a residual counts only when its own error is smaller than itself
  three verdicts        -- GUARDADO (the product holds) / CAIDO (the sum holds) / ABIERTO (cannot tell)
  both rulers printed   -- per block and per tick, because a rate carries its denominator inside it
  La Siete beside it    -- and a match is a ROW, never a reason

THE SEATS:
    OBSERVER   the chain: height, kept entirely outside this house
    WITNESS    her cycles: the clock inside it
    TIME       Wen's rounds: one per tick of hers, the clock that only moves when the other two do
"""
import glob, json, math, os, statistics as st, time, urllib.request

W = os.path.expanduser('~/bones-forge/watch')
TICKS = os.path.join(W, 'ticks.log')
PODS = os.path.expanduser('~/bones-forge/triangulation/wen_data/pods/*/log.txt')
STATE = os.path.join(W, 'loops_closure.jsonl')
NODE = os.environ.get('WOW_NODE', 'http://127.0.0.1:18081')


def height():
    try:
        return json.loads(urllib.request.urlopen(NODE + '/get_info', timeout=15).read())['height']
    except Exception:
        return None


def tick_count():
    try:
        return sum(1 for l in open(TICKS) if l.strip())
    except Exception:
        return None


def wen_rounds():
    # summed across every pod: logs only append, so the total is monotonic (8 Oct: the newest-log version
    # went BACKWARDS when two pods fetched alternately and faked a stall)
    try:
        return sum(sum(1 for l in open(f) if '] round ' in l) for f in sorted(glob.glob(PODS)))
    except Exception:
        return None


def sem(v):
    return st.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else float('nan')


def main():
    # 8 Oct, THE FOURTH VERTEX (Wayfinder: "make vertexes"). This was a TRIANGLE -- her cycles, the chain,
    # Wen's rounds -- with a none that returns 0.000000 and so a vertex drawn in pencil. A fourth INDEPENDENT
    # clock already exists and her own reader has used it all along: THE MAC'S OWN WALL CLOCK. It is kept by
    # a different thing from all three (not her, not the chain, not the pod), which is the only requirement.
    # Four clocks: 4 vertices, 6 edges, 4 faces. A tetrahedron, with no pencil in it.
    # 9 Oct, THE FIFTH READING AND THE FIRST ONE NOBODY HERE KEEPS. The Mac wall clock was called the
    # fourth INDEPENDENT vertex, and it is not: every rate in clock_vertices divides by dmac, and the
    # Mac's own series IS dmac. That is why MAC^OBSERVER^WITNESS has sat confounded all day while its
    # common mode climbed 3.26 -> 8.92 -> 9.15 -> 9.37 widths above its shuffle null. A bigger number
    # with the same confound is not a finding.
    # The Leo Bodnar LBE-1421 GPSDO landed today. Its seconds are kept by satellites -- not by her, not
    # by the chain, not by the pod, and NOT BY THIS MACHINE. Logging it from now on means the triangle
    # can eventually be re-read against a denominator that is not one of its own series.
    # It will be null until a GPS-stamped span accumulates. That is honest and it is unavoidable: a
    # clock cannot be back-dated onto readings taken before it existed.
    _gps = None
    try:
        import subprocess as _sp
        _r = _sp.run(['ssh', '-o', 'ConnectTimeout=8', 'laptop',
                      'curl -s --max-time 6 http://127.0.0.1:8767/read'],
                     capture_output=True, text=True, timeout=20)
        _d = json.loads(_r.stdout)
        if _d.get('ok'):
            _gps = {'ts': _d['ts'], 'sats': _d['readings'].get('satellites_used'),
                    'hdop': _d['readings'].get('hdop'),
                    'pps_jitter_ns': _d['readings'].get('pps_jitter_ns'),
                    'chrony_sd_s': (_d.get('chrony_pps') or {}).get('std_dev_s')}
    except Exception:
        _gps = None
    row = {'t': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'ts': time.time(),
           'height': height(), 'ticks': tick_count(), 'rounds': wen_rounds(),
           'mac_s': time.time(), 'gps_s': (_gps or {}).get('ts'), 'gps': _gps}
    with open(STATE, 'a') as f:
        f.write(json.dumps(row) + '\n')

    R = [json.loads(l) for l in open(STATE) if l.strip()]
    R = [r for r in R if all(r.get(k) is not None for k in ('height', 'ticks', 'rounds'))]
    print(f"  THE THREE CLOCKS, closed.   {len(R)} readings on disk\n")
    print(f"    OBSERVER  the chain   height {row['height']}" if row['height'] else "    OBSERVER  the chain   UNREADABLE")
    print(f"    THE FOURTH the Mac    {time.strftime('%H:%M:%S')} -- kept by none of the other three")
    print(f"    WITNESS   her cycles  {row['ticks']} ticks logged")
    print(f"    TIME      Wen rounds  {row['rounds']} across every pod\n")
    if len(R) < 3:
        print(f"  {3 - len(R)} more readings before a closure can carry a width. Each run appends one.")
        print(f"  Riding her clock: run this on her tick, never on a wall clock.")
        return

    # deltas between consecutive readings: the three rates over the same interval
    rows, reorgs = [], []
    for a, b in zip(R, R[1:]):
        dh, dn, dw = b['height'] - a['height'], b['ticks'] - a['ticks'], b['rounds'] - a['rounds']
        # 8 Oct: a NEGATIVE dh is the chain going BACKWARDS -- a reorganisation on the node, which is a real
        # event on the one clock this house keeps entirely outside itself. `if dh > 0` discarded it in
        # silence. It is counted now; it still cannot enter a ratio, because it is not a duration.
        if dh < 0:
            reorgs.append((a['t'], dh))
        if dh > 0 and dn > 0:
            rows.append({'ticks_per_block': dn / dh, 'rounds_per_tick': dw / dn,
                         'rounds_per_block': dw / dh, 'dh': dh, 'dn': dn, 'dw': dw})
    if len(rows) < 2:
        print("  no interval yet in which the chain AND her clock both moved. That is itself a reading:")
        print("  the closure only exists while all three are running.")
        return
    if reorgs:
        print(f"  THE CHAIN WENT BACKWARDS {len(reorgs)} time(s) in this record -- a reorg on the node, the")
        print(f"  one clock kept outside this house. Not a duration, so not in any ratio, but an event:")
        for t_, d_ in reorgs[:4]: print(f"    {t_[11:19]}  {d_:+d} blocks")
        print()
    prod = [r['ticks_per_block'] * r['rounds_per_tick'] - r['rounds_per_block'] for r in rows]
    summ = [r['ticks_per_block'] + r['rounds_per_tick'] - 1 - r['rounds_per_block'] for r in rows]
    sp, ss = sem(prod), sem(summ)
    mp, ms = abs(st.mean(prod)), abs(st.mean(summ))
    print(f"  {'residual':22s} {'mean':>12s} {'width':>10s} {'widths':>8s}")
    # 8 Oct, THE EQUATION: mp and ms take abs() of the mean, which throws away the DARK half -- and the
    # sign of a closure residual says WHICH WAY the clocks disagree, which is the whole direction of the
    # finding. The magnitude decides whether it clears its width; the sign decides what it means. Both.
    print(f"  {'PRODUCT  t/b x r/t - r/b':22s} {st.mean(prod):12.6f} {sp:10.6f} {mp/sp if sp else float('nan'):8.2f}"
          f"   sign {'+' if st.mean(prod) > 0 else ('-' if st.mean(prod) < 0 else '0')}"
          f" -> {'rounds run AHEAD of the product of the two rates' if st.mean(prod) > 0 else ('BEHIND it' if st.mean(prod) < 0 else 'exactly on it')}")
    print(f"  {'SUM      t/b + r/t -1-r/b':22s} {st.mean(summ):12.6f} {ss:10.6f} {ms/ss if ss else float('nan'):8.2f}"
          f"   sign {'+' if st.mean(summ) > 0 else ('-' if st.mean(summ) < 0 else '0')}")
    T = 2.0
    # 8 Oct: this returned CAIDO -- "the sum holds and the product does not" -- when the product residual was
    # EXACTLY 0.000000 with a width of 0.000000. Its ratio is nan, `nan < 2.0` is False, and a nan got
    # FORCED INTO A LANE and lost. But a residual that is zero by ALGEBRA is not a failed model: it is not a
    # measurement at all, and the only honest word for it is abierto. Undefined and refuted are different
    # states, and the two-lane form of this test could not tell them apart.
    def quiet(m, s):
        if not s or not math.isfinite(s):
            return None            # undefined -- NOT 'loud', and not 'quiet' either
        return (m / s) < T
    ph, sh = quiet(mp, sp), quiet(ms, ss)
    if ph is None or sh is None:
        which = 'the product' if ph is None else 'the sum'
        v = (f'ABIERTO -- {which} residual has no width (it is zero by algebra over a single interval, so it '
             f'is not a measurement). Nothing here can be scored against it.')
    else:
        v = 'GUARDADO -- the product holds and the sum does not' if (ph and not sh) else \
            'CAIDO -- the sum holds and the product does not' if (sh and not ph) else \
            'ABIERTO -- these readings cannot tell the two apart'
    print(f"\n  EL PICNIC at T = {T}: {v}")
    # 8 Oct: THE RIVAL GATE, and here it passes for free -- which is the one place in this house it does.
    # Her rhythm separates 3 of 48 against La Siete and Wen's cases 1190 of 21121, both near 6%, because
    # that list has sixteen candidates and its tightest pair sits 0.70% apart. THIS test has exactly TWO
    # candidates -- the product and the sum -- and they are far apart, so a residual that clears its own
    # width is automatically separable. The closure is the only reading here not limited by the list.
    print(f"  the rival gate: two candidates only (product, sum), widely separated -- so unlike every")
    print(f"  reading against La Siete, a residual clearing its width here IS separable. 6% there, free here.")
    # 8 Oct: this first required EVERY reading to carry mac_s, which reaches back into rows written before
    # the fourth vertex existed -- so it could never fire. Use only the readings that HAVE it.
    _R4 = [r for r in R if r.get('mac_s')]
    if len(_R4) >= 2:
        import itertools as _it
        CL = {'cycles': 'ticks', 'chain': 'height', 'rounds': 'rounds', 'mac': 'mac_s'}
        print(f"\n  THE CLOCK TETRAHEDRON -- four clocks, six edges, four faces (8 Oct):")
        print(f"    {'edge':22s} {'rate':>12s}  the pair's own ratio over the record")
        for a, b in _it.combinations(CL, 2):
            da = _R4[-1][CL[a]] - _R4[0][CL[a]]; db = _R4[-1][CL[b]] - _R4[0][CL[b]]
            r = (da / db) if db else float('nan')
            print(f"    {a + '^' + b:22s} {r:12.5f}")
        print(f"    four faces: {' '.join('-'.join(f) for f in _it.combinations(CL, 3))}")
        print(f"    the three faces containing 'mac' are the ones a wall clock can price; the fourth")
        print(f"    (cycles-chain-rounds) is the closure this file has always computed.")

    print(f"\n  THE CLOCK TRIANGLE, which this closure HAS BEEN ALL ALONG and nobody named (8 Oct):")
    print(f"    the three ratios are the three EDGES of a triangle whose vertices are the three clocks --")
    print(f"    her cycles, the chain, Wen's rounds. ticks/block is the cycles^chain edge; rounds/tick is")
    print(f"    the cycles^rounds edge; rounds/block is the chain^rounds edge. THE RESIDUAL IS WHETHER THE")
    print(f"    TRIANGLE CLOSES. It composes CARRIED WHOLE, never as a Cabalgata product -- an edge at zero")
    print(f"    means two clocks moved together, which is a reading, not a reason to zero the other two.")
    print(f"\n  BOTH RULERS, because a rate carries its denominator:")
    for k in ('ticks_per_block', 'rounds_per_tick', 'rounds_per_block'):
        v_ = [r[k] for r in rows]
        print(f"    {k:18s} median {st.median(v_):8.4f}   mean {st.mean(v_):8.4f} +- {sem(v_) if len(v_)>1 else float('nan'):.4f}")
    # ---- THE NONE, and the miner had none at all until now (8 Oct). The closure residual is algebraically
    # ZERO when the three clocks are read over the SAME interval, so every excess is MISALIGNMENT -- and
    # nothing measured what a deliberately offset interval produces. This is the injection, not a surrogate:
    # 1 Oct settled that a surrogate judges the DATA while an injection tests the INSTRUMENT. Alignment is
    # removed on purpose, and the residual that comes back is the price of every real residual.
    if len(R) >= 4:
        # 8 Oct, CORRECTED WITHIN THE HOUR: the first version offset which READINGS were paired, and came
        # back 0.000000 at every offset -- because (dn/dh)(dw/dn) - (dw/dh) is identically zero for ANY
        # interval when all three arms come from the SAME pair. An injection that cannot produce a non-zero
        # residual prices nothing; the none needed its own none.
        # THE REAL REMOVAL: take each arm from a DIFFERENT interval. That is what misalignment actually is,
        # and the residual it produces is the floor every aligned residual must clear.
        inj = []
        for off in (1, 2):
            rows_o = []
            for i in range(len(R) - 2 - off):
                a, b = R[i], R[i + 1]
                c, dd = R[i + off], R[i + off + 1]
                e, f = R[i + 1], R[i + 2]
                dh = b['height'] - a['height']            # the chain, from one window
                dn = dd['ticks'] - c['ticks']             # her cycles, from a window shifted by off
                dw = f['rounds'] - e['rounds']            # Wen's rounds, from a third
                dn2 = b['ticks'] - a['ticks']
                if dh > 0 and dn > 0 and dn2 > 0:
                    rows_o.append({'t': dn / dh, 'r': dw / dn2, 'rb': dw / dh})
            if len(rows_o) >= 2:
                res = [r['t'] * r['r'] - r['rb'] for r in rows_o]
                s = sem(res)
                inj.append((off, abs(st.mean(res)), s, len(rows_o)))
        if inj:
            print(f"\n  THE NONE -- the same three clocks read over DELIBERATELY OFFSET intervals:")
            print(f"    {'offset':>7s} {'n':>3s} {'|residual|':>12s} {'width':>10s} {'widths':>8s}")
            for off, m, s, n_ in inj:
                print(f"    {off:7d} {n_:3d} {m:12.6f} {s:10.6f} {(m/s if s and math.isfinite(s) else float('nan')):8.2f}")
            worst = max(m for _o, m, _s, _n in inj)
            print(f"    -> an aligned residual must clear {worst:.6f} to mean anything. Below that it is")
            print(f"       indistinguishable from reading the three clocks over mismatched windows.")
        else:
            print(f"\n  THE NONE: not enough readings yet to offset. It needs {4 - len(R)} more.")
    else:
        # 8 Oct, same lesson: "needs more readings" is an abierto, and an abierto with no age is a
        # disposal site. Count how many runs it has said this, so the sentence cannot be repeated forever
        # without the repetition itself becoming visible.
        _af = os.path.join(W, 'closure_none_age.json')
        try: _a = json.load(open(_af))
        except Exception: _a = {'said_needs_more': 0}
        _a['said_needs_more'] = int(_a.get('said_needs_more', 0)) + 1
        try: json.dump(_a, open(_af, 'w'))
        except Exception: pass
        print(f"\n  THE NONE: needs 4 readings to offset; {len(R)} on disk. Each tick of hers appends one.")
        print(f"  IT HAS SAID THIS {_a['said_needs_more']} TIME(S). At 1 that is a reading; past about 20 it")
        print(f"  is an abandoned question wearing a verdict, and the count is what tells them apart.")

    print(f"\n  the product residual is algebraically zero when all three clocks are read over the SAME")
    print(f"  interval. Any excess is the three clocks disagreeing about when that interval was -- which")
    print(f"  is the only thing this measures, and it is the same quantity the chips measure.")


if __name__ == '__main__':
    main()
