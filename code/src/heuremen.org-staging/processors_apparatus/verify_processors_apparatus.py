#!/usr/bin/env python3
"""verify_processors_apparatus.py -- recompute the processor-sort, decay-time, idle-control, non-exponential-decay,
gate-error and simulated-plant numbers published on heuremen.org, from the compact JSON in data/.

    python3 verify_processors_apparatus.py

Standard library only. No account, no network, no numpy. Reads data/*.json (about 0.7 MB) and prints each
published claim beside the value this script computes from the data, marked OK or DIFFERS, followed by a short
note wherever the wording of the claim is not what the data say.

OK means: the recomputed number matches the claim to the stated tolerance.
It does NOT mean the claim's wording is right; read the NOTE lines.
"""
import json, math, os, random, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda f: json.load(open(os.path.join(HERE, 'data', f)))
LOOKS = [1, 2, 3, 4, 6, 9]
RESULTS = []          # (section, label, claim, got, status)


def check(sec, label, claim, got, tol, fmt='%.4f'):
    ok = abs(got - claim) <= tol
    RESULTS.append((sec, ok))
    print('   %-62s claim %-10s recomputed %-10s %s' % (label, fmt % claim, fmt % got, 'OK    ' if ok else 'DIFFERS'))
    return ok


def note(s):
    print('   NOTE: ' + s)


def head(s):
    print('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)


# ------------------------------------------------------------------------------------------------ small numerics
def linfit(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx


def nanmedian(v):
    v = [a for a in v if a == a]
    return st.median(v) if v else float('nan')


def unwrap(seq):
    out = [seq[0]]; corr = 0.0
    for a, b in zip(seq, seq[1:]):
        d = b - a; dd = (d + math.pi) % (2 * math.pi) - math.pi
        if dd == -math.pi and d > 0: dd = math.pi
        if abs(d) >= math.pi: corr += dd - d
        out.append(b + corr)
    return out


def quad_no_intercept(t, y):
    """least squares y = c0 t + c1 t^2 (the witness 'laid hand curve')."""
    s2 = sum(a ** 2 for a in t); s3 = sum(a ** 3 for a in t); s4 = sum(a ** 4 for a in t)
    b0 = sum(a * b for a, b in zip(t, y)); b1 = sum(a * a * b for a, b in zip(t, y))
    det = s2 * s4 - s3 * s3
    return (b0 * s4 - b1 * s3) / det, (s2 * b1 - s3 * b0) / det


def equiv_time(c0, c1, a):
    """real root of c1 x^2 + c0 x = a, inside (-5, 60) us, nearest to the linear estimate a/c0 (as the private reader)."""
    if c0 == 0: return float('nan')
    if c1 == 0: r = [a / c0]
    else:
        disc = c0 * c0 + 4 * c1 * a
        r = [] if disc < 0 else [(-c0 + s * math.sqrt(disc)) / (2 * c1) for s in (1, -1)]
    r = [x for x in r if -5 < x < 60]
    return min(r, key=lambda x: abs(x - a / c0)) if r else float('nan')


def witness_look(angles):
    """angles: [T10,T20,T30,K1,K2,K3,K4,K6,K9] radians -> look length (us) by the slope over looks 1..9; nan if <4 usable."""
    uw = unwrap([0.0] + angles[:3])
    c0, c1 = quad_no_intercept([10.0, 20.0, 30.0], uw[1:4])
    teq = [equiv_time(c0, c1, a) for a in angles[3:]]
    ok = [i for i, v in enumerate(teq) if v == v]
    if len(ok) < 4: return float('nan')
    return linfit([LOOKS[i] for i in ok], [teq[i] for i in ok])


def looked_at_look(row):
    """row: [AW10,AW20,AW40, A1..A9 levels] of a bit that was itself looked at -> its own-clock look length (us), or None."""
    clip = lambda v, lo, hi: min(max(v, lo), hi)
    L = [1.0] + [clip(v, 0.02, 1.0) for v in row[:3]]
    sl = linfit([0.0, 10.0, 20.0, 40.0], [math.log(v) for v in L])
    if sl >= 0: return None
    teq = [math.log(clip(v, 0.02, 1.0)) / sl for v in row[3:]]
    return linfit([float(k) for k in LOOKS], teq)


def pearson(a, b):
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den


def ranks(v):                       # ordinal ranks, like argsort(argsort(.)) (no tie handling, as the private script)
    order = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
    for k, i in enumerate(order): r[i] = k
    return r


def spearman(a, b):
    """with average ranks for ties"""
    def avg(v):
        s = sorted(v); out = []
        for x in v:
            idx = [i for i, y in enumerate(s) if y == x]; out.append(sum(idx) / len(idx))
        return out
    return pearson(avg(a), avg(b))


# ================================================================================================ 1. PROCESSORS SORT
# maker's median T2:T1 (chip calibration record), copied from the private ledger / read files; the chip records themselves are
# IBM's daily calibration data and are not re-derived here.   (source in README)
T2T1 = {'ibm_marrakesh': 0.519, 'ibm_kingston': 0.638, 'ibm_fez': 0.683, 'ibm_phoenix': 0.851, 'ibm_pittsburgh': 1.160, 'ibm_boston': 1.183}
# six_blind_20261007.txt as printed by the private script (pooled / blind / seeing), for comparison only
LEDGER_SIX = {('ibm_boston', '4 Oct'): (1.227, 1.246, 1.177), ('ibm_fez', '4 Oct'): (1.564, 1.616, 1.522), ('ibm_fez', '6 Oct'): (1.784, 1.783, 1.768),
              ('ibm_kingston', '4 Oct'): (1.574, 1.631, 1.503), ('ibm_kingston', '6 Oct'): (1.572, 1.602, 1.543),
              ('ibm_marrakesh', '4 Oct'): (1.445, 1.405, 1.377), ('ibm_pittsburgh', '4 Oct'): (1.317, 1.345, 1.293), ('ibm_pittsburgh', '5 Oct'): (1.289, 1.342, 1.199)}


def sort_section():
    head('1. PROCESSORS SORT   (T/W = looked-at qubit\'s own clock over untouched spectators\' clock; see README)')
    data = D('sort_witness_and_looked_at.json')
    rows = {}
    for cd in data['chipdays']:
        Ts, Wa, Wb, Ws = [], [], [], []
        for run in cd['runs']:
            W = [(r[1], witness_look(r[2:])) for r in run['witness_rows']]
            Wa.append(nanmedian([w for _, w in W]))
            b = [w for n, w in W if n == 0]; s = [w for n, w in W if n >= 2]
            Wb.append(nanmedian(b) if b else float('nan')); Ws.append(nanmedian(s) if s else float('nan'))
            tt = [looked_at_look(r[1:]) for r in run['far_rows']]; Ts.append(st.median([t for t in tt if t is not None]))
        T = st.mean(Ts)
        rows[(cd['chip'], cd['day'])] = (T / st.mean(Wa), T / st.mean(Wb) if all(x == x for x in Wb) else None,
                                         T / st.mean(Ws) if all(x == x for x in Ws) else None, [r['run'] for r in cd['runs']])
    print('   chip-day              runs          T/W pooled   T/W blind   T/W seeing      (ledger six_blind: pooled/blind/seeing)')
    for k in sorted(rows):
        p, b, s, runs = rows[k]
        led = LEDGER_SIX.get(k)
        print('   %-14s %-6s %-14s %8.3f   %8s   %9s      %s' % (k[0], k[1], ','.join(map(str, runs)), p, '%.3f' % b if b else 'n/a (not Heron layout)',
              '%.3f' % s if s else 'n/a', '%.3f / %.3f / %.3f' % led if led else '(not in the private script)'))
    print()
    five = sorted(k for k in LEDGER_SIX)
    for k in five:
        p, b, s, _ = rows[k]
        check('1', 'T/W pooled %s %s vs private script' % (k[0][4:], k[1]), LEDGER_SIX[k][0], p, 0.003, '%.3f')
    # rank agreement, as the private script: ordinal ranks, Pearson, across the 8 chip-days
    P = [rows[k][0] for k in five]; B = [rows[k][1] for k in five]; S = [rows[k][2] for k in five]
    check('1', 'rank agreement pooled vs blind (8 chip-days, 5 chips)', 0.98, pearson(ranks(P), ranks(B)), 0.005, '%+.2f')
    check('1', 'rank agreement pooled vs seeing (8 chip-days, 5 chips)', 0.93, pearson(ranks(P), ranks(S)), 0.005, '%+.2f')
    # per chip (mean of days)
    chip = {}
    for (c, d), v in rows.items(): chip.setdefault(c, []).append(v[0])
    print('\n   per-chip pooled T/W (every chip-day listed above):')
    for c in sorted(chip, key=lambda c: st.mean(chip[c])):
        print('     %-16s %s   mean %.3f   %s' % (c, ' '.join('%.3f' % x for x in chip[c]), st.mean(chip[c]),
              'maker T2:T1 %.3f' % T2T1[c] if c in T2T1 else 'maker T2:T1 not on file'))
    lowg = ['ibm_boston', 'ibm_pittsburgh', 'ibm_phoenix']; highg = ['ibm_kingston', 'ibm_fez', 'ibm_marrakesh']
    lo = [x for c in lowg for x in chip[c]]; hi = [x for c in highg for x in chip[c]]
    check('1', 'lowest T/W of Boston, Pittsburgh, Phoenix (claim 1.22)', 1.22, min(lo), 0.006, '%.3f')
    check('1', 'highest T/W of Boston, Pittsburgh, Phoenix (claim 1.35)', 1.35, max(lo), 0.006, '%.3f')
    check('1', 'lowest T/W of Kingston, Fez, Marrakesh (claim 1.45)', 1.45, min(hi), 0.006, '%.3f')
    check('1', 'highest T/W of Kingston, Fez, Marrakesh (claim 1.78)', 1.78, max(hi), 0.006, '%.3f')
    print()
    print('   is it two groups or a continuum?')
    allv = sorted((x, c) for c in chip for x in chip[c])
    gaps = [(allv[i + 1][0] - allv[i][0], allv[i][1], allv[i + 1][1]) for i in range(len(allv) - 1)]
    print('     all chip-day values, sorted: ' + ' '.join('%.3f' % v for v, _ in allv))
    big = max(gaps)
    bnd = min(hi) - max(lo)
    print('     gap at the claimed boundary (highest of Boston/Pittsburgh/Phoenix to lowest of Kingston/Fez/Marrakesh): %.3f' % bnd)
    print('     largest gap anywhere: %.3f (between %s and %s)' % (big[0], big[1][4:], big[2][4:]))
    fez = chip['ibm_fez']
    print('     Fez alone moves %.3f between its two days, %.1f times the gap at the boundary' % (max(fez) - min(fez), (max(fez) - min(fez)) / bnd))
    print('     spread inside the low group %.3f, inside the high group %.3f (with Aachen in the low group: %.3f)' % (max(lo) - min(lo), max(hi) - min(hi), max(lo) - min(chip['ibm_aachen'] + lo)))
    m6 = [c for c in T2T1]
    xs = [st.mean(chip[c]) for c in m6]; ys = [T2T1[c] for c in m6]
    rho = spearman(xs, ys)
    print('     rank correlation, chip mean T/W against maker T2:T1, six chips: %+.3f' % rho)
    pred = sorted(m6, key=lambda c: -T2T1[c]); obs = sorted(m6, key=lambda c: st.mean(chip[c]))
    print('       order by T2:T1 high->low: ' + ' '.join(c[4:] for c in pred))
    print('       order by T/W low->high  : ' + ' '.join(c[4:] for c in obs))
    # chance of the two-group split: label chips with T2:T1>1 (2 chips) vs the rest; how often would a random label put both in the lowest two?
    n = len(m6); tot = math.comb(n, 2)
    print('     chance that the 2 chips with T2:T1 > 1 are the 2 lowest T/W by luck, among 6 chips: 1 in %d' % tot)
    ph = chip['ibm_phoenix']
    note('Aachen is the 7th chip and is computed above, but is NOT in the published ranges; its maker T2:T1 is not in any file I could find, so it cannot be placed on the T2:T1 axis.')
    note('Phoenix has T2:T1 = %.3f (below 1, like Kingston/Fez/Marrakesh) but sits in the LOW T/W group (%.2f-%.2f). The page lists Phoenix with Boston and Pittsburgh as matching the T2:T1 ordering; by the maker numbers it does not.'
         % (T2T1['ibm_phoenix'], min(ph), max(ph)))
    note('Within the high group the order is Marrakesh < Kingston < Fez in T/W, the reverse of the T2:T1 order Fez > Kingston > Marrakesh. The data support a split at T2:T1 = 1 on heavy-hex chips, not an ordering.')
    note('The +0.98 / +0.93 are rank agreements BETWEEN THREE WAYS OF CHOOSING SPECTATORS over 8 chip-days of 5 chips, not agreement between T/W and T2:T1. Phoenix and Aachen are not in them.')


# ================================================================================================ 2 & 4. TIME RUNS
def tau_of(l300):
    return -300.0 / math.log(min(max(l300, 0.02), 0.98))


def time_section():
    head('2. T1 DRIFT   (the "ruler": fading time of a qubit left in |1> and read after 300 us, three copies a/b/c per job)')
    data = D('time_runs_ruler_copies.json')['runs']
    by = {}
    for run in data:
        taus = []
        for ci in range(3):
            base = 1 + 4 * ci         # row = [q, (30,100,300,600) x copy a, b, c, idle300, idle600]
            taus.append(st.median([tau_of(r[base + 2]) for r in run['rows']]))
        by.setdefault(run['chip'], []).append((run['run'], run['start'][:16], taus))
    for chip in ('ibm_marrakesh', 'ibm_kingston', 'ibm_pittsburgh'):
        runs = by[chip]
        print('\n   %s   fading time (us), median over readable qubits' % chip)
        print('     %-6s %-17s %8s %8s %8s   | mean of copies   range of copies (inside one job)' % ('run', 'started', 'copy a', 'copy b', 'copy c'))
        for r, t0, t in runs:
            print('     %-6d %-17s %8.1f %8.1f %8.1f   | %8.1f         %5.1f' % (r, t0, t[0], t[1], t[2], st.mean(t), max(t) - min(t)))
        copy_means = [st.mean([r[2][c] for r in runs]) for c in range(3)]
        read_means = [st.mean(r[2]) for r in runs]
        print('     mean over the %d jobs, copy a/b/c: %s      |  mean over copies, job by job: %s' % (len(runs), ' / '.join('%.1f' % x for x in copy_means), ' / '.join('%.1f' % x for x in read_means)))
        by[chip] = (runs, copy_means, read_means)
    print()
    m = by['ibm_marrakesh']; k = by['ibm_kingston']; p = by['ibm_pittsburgh']
    for i, (c, claim) in enumerate(zip(m[1], (174, 177, 181))):
        check('2', 'marrakesh "174/177/181 us": mean of COPY %s over 3 jobs' % 'abc'[i], claim, c, 0.6, '%.1f')
    for i, c in enumerate(m[2]):
        print('   marrakesh job %d, mean over its three copies: %.1f us' % (i + 1, c))
    check('2', 'kingston low end of "260-266" (copy means)', 260, min(k[1]), 0.6, '%.1f')
    check('2', 'kingston high end of "260-266" (copy means)', 266, max(k[1]), 0.6, '%.1f')
    pr = p[0]
    first = pr[0][2]
    check('2', 'pittsburgh "294-297" low end: run %d copies' % pr[0][0], 294, min(first), 0.6, '%.1f')
    check('2', 'pittsburgh "294-297" high end: run %d copies' % pr[0][0], 297, max(first), 0.6, '%.1f')
    spread = lambda runs, c: max(r[2][c] for r in runs) - min(r[2][c] for r in runs)
    print('\n   how far each copy moves BETWEEN jobs (max - min of that copy over the jobs):')
    for nm, bb in (('marrakesh', m[0]), ('kingston', k[0]), ('pittsburgh', p[0])):
        print('     %-11s copy a/b/c: %s us' % (nm, ' / '.join('%.1f' % spread(bb, c) for c in range(3))))
    check('2', '"up to 10 us between jobs": largest job-to-job move of any copy, 3 chips', 10, max(spread(bb, c) for bb in (m[0], k[0], p[0]) for c in range(3)), 1.5, '%.1f')
    within = [max(r[2]) - min(r[2]) for bb in (m[0], k[0], p[0]) for r in bb]
    print('   range of the three copies INSIDE a single job: min %.1f, max %.1f us (marrakesh jobs: %s)' % (min(within), max(within), ' / '.join('%.1f' % (max(r[2]) - min(r[2])) for r in m[0])))
    note('"174 / 177 / 181", "260-266" and "294-297" are the three RULER COPIES (a, b, c) inside the jobs, averaged over jobs (Marrakesh, Kingston) or from the first job alone (Pittsburgh).')
    note('The page presents them as values at different jobs. The job-to-job movement is the second table above; the copy-to-copy difference inside one job is as large (Marrakesh job 1: %.1f us).' % (max(m[0][0][2]) - min(m[0][0][2])))
    note('"Steady within one job" is therefore not supported for Marrakesh job 1; the private ledger itself says read 1 had an in-job slide that did not repeat in reads 2-3.')
    note('Pittsburgh: three jobs exist (runs 361-363); their copy-means are %s us, so 294-297 is not a between-jobs range.' % ' / '.join('%.1f' % x for x in p[2]))
    return data


def bend_section(data):
    head('4. NON-EXPONENTIAL DECAY   (|1> level at 30 us below that qubit-copy\'s own 300 us single-exponential extrapolation)')
    ledger = {('ibm_marrakesh', 301): 84, ('ibm_marrakesh', 302): 80, ('ibm_marrakesh', 303): 83, ('ibm_kingston', 301): 78, ('ibm_kingston', 302): 72, ('ibm_kingston', 303): 75,
              ('ibm_pittsburgh', 361): 62}
    shares = {}
    print('   chip           run   readable qubit-copies   share below at 30 us    private file decay_bend_per_qubit_20261004.txt')
    for run in data:
        n = b = 0
        for r in run['rows']:
            for ci in range(3):
                base = 1 + 4 * ci; l30, l300 = r[base], r[base + 2]
                tau = tau_of(l300); pred = math.exp(-30.0 / tau)
                n += 1; b += (l30 - pred) < 0
        shares[(run['chip'], run['run'])] = 100.0 * b / n
        led = ledger.get((run['chip'], run['run']))
        print('   %-14s %-5d %-22d %5.1f %%                 %s' % (run['chip'], run['run'], n, shares[(run['chip'], run['run'])], '%d %%' % led if led else '-'))
    print()
    for k, v in ledger.items():
        check('4', 'share below at 30 us, %s run %d' % (k[0][4:], k[1]), v, shares[k], 1.0, '%.0f')
    six = [shares[k] for k in ledger]
    check('4', 'lowest of the 7 runs the claim rests on', 62, min(six), 1.0, '%.0f')
    check('4', 'highest of the 7 runs the claim rests on', 84, max(six), 1.0, '%.0f')
    others = {k: v for k, v in shares.items() if k not in ledger}
    print('   same measurement on the other time-design runs on disk (not in the claim): lowest %.0f %%, highest %.0f %% over %d runs' % (min(others.values()), max(others.values()), len(others)))
    pit = [v for k, v in shares.items() if k[0] == 'ibm_pittsburgh']
    print('   Pittsburgh, all three jobs: %s %%' % ' / '.join('%.0f' % x for x in pit))
    note('"62-84 %" is the spread of seven per-job shares, one Pittsburgh job at the low end. Below 50 % never occurs, so the sign of the effect is stable; the exact range depends on which jobs are counted.')
    note('Idle |0> after 300 us (the "OFF left alone" arm of the same jobs) is in section 3.')


# ================================================================================================ 3. PARK + IDLE
def book(p300, nseg):
    q = p300 ** (1.0 / nseg); on, off = 1.0, 0.0
    for _ in range(nseg): on, off = off + on * (1 - q), on * q
    return on


def idle_section(pdata):
    head('3. IDLE CONTROL')
    print('   (a) "parking" runs 71-73, ibm_pittsburgh: qubit starts in |1>, an X gate after each interval so it spends alternate intervals in |0>,')
    print('       300 us in all; measured level minus that qubit\'s own decay bookkeeping (its own 300-us nothing-done level, cut into the intervals).')
    claims = {'P1': (0.0017, 0.0013, 'a  parked once       (2 x 150 us)', 2), 'P3': (0.0020, 0.0015, 'b  alternate quarters (4 x 75 us)', 4), 'P9': (0.0014, 0.0015, 'c  alternate tenths   (10 x 30 us)', 10)}
    for key, (cm, cw, label, n) in claims.items():
        means, widths = [], []
        for run in pdata['park']:
            sep = run['sep']; g = [i for i, s in enumerate(sep) if s > 4]
            dl, sq = [], []
            for i in g:
                p300 = min(max(run['lv_N0'][i], 0.02), 0.98)
                d = run['lv_' + key][i] - book(p300, n); dl.append(d)
                eps = 1e-4; dd = (book(min(p300 + eps, 0.98), n) - book(max(p300 - eps, 0.02), n)) / (2 * eps)
                sq.append(run['se_' + key][i] ** 2 + (dd * run['se_N0'][i]) ** 2)
            means.append(st.mean(dl)); widths.append(math.sqrt(sum(sq)) / len(g))
        m = st.mean(means); w = math.sqrt(sum(x * x for x in widths)) / 3
        print('     %s: reads %s (readable %s)' % (label, ' '.join('%+.4f' % x for x in means), '/'.join(str(sum(1 for s in r['sep'] if s > 4)) for r in pdata['park'])))
        check('3', '   residual, three-read mean (claim %+.4f)' % cm, cm, m, 0.00006, '%+.4f')
        check('3', '   width (analytic shot error; the claim used a bootstrap)', cw, w, 0.0003, '%.4f')
    note('The page says "a qubit prepared in |0> and left". These runs prepare |1> and flip it with X gates (the |0> time is every other interval). One chip (Pittsburgh), one day, 3 jobs.')
    print()
    print('   (b) idle |0> for 300 us: the "OFF left alone 300 us" arm of run 121, ibm_pittsburgh (one job).')
    rows = pdata['idle_run121']['rows']
    z = [r[1] for r in rows]; se = [math.hypot(r[2], r[3]) for r in rows]   # level error and OFF-reference error
    mean = st.mean(z); w = math.sqrt(sum(x * x for x in se)) / len(z)
    check('3', 'idle |0> after 300 us, gain in percent (claim +0.02)', 0.02, 100 * mean, 0.015, '%+.3f')
    check('3', '   width in percent (claim 0.15)', 0.15, 100 * w, 0.03, '%.3f')
    print('     readable qubits: %d' % len(z))
    # the same arm in the time-design jobs on the other chips
    td = D('time_runs_ruler_copies.json')['runs']
    print('   the same idle-|0> arm (300 us) in the time-design jobs on all chips, mean over readable qubits (percent):')
    per = {}
    for run in td:
        per.setdefault(run['chip'], []).append(100 * st.mean([r[13] for r in run['rows']]))
    for c in sorted(per): print('     %-15s %s' % (c, ' '.join('%+.2f' % x for x in per[c])))
    allj = [x for v in per.values() for x in v]
    note('The "+0.02 +- 0.15 %%" is one Pittsburgh job. In the %d time-design jobs above the same arm reads %+.2f to %+.2f %% (positive in %d); the private SEVEN.md says "about +0.5 %%". The ledger (sec. 176) quotes push-job idle arms of +0.26 +- 0.14 %% (Kingston) and -0.43 +- 0.13 %% (Marrakesh).' % (len(allj), min(allj), max(allj), sum(1 for x in allj if x > 0)))
    note('The page headline calls the three residuals "within +-0.002"; the three means are 0.0017, 0.0020, 0.0014 with widths 0.0013-0.0015, i.e. consistent with zero at about 1.2 to 1.4 sigma, all three positive.')


# ================================================================================================ 5. LEAKAGE
def leak_section(pdata):
    head('5. "LEAKAGE CAPPED AT 0.26 +- 0.12 % PER GATE"   (push run 91-93, ibm_pittsburgh, back-to-back X gates, no wait)')
    cols = None; acc = {}
    for run in pdata['push']:
        rows = run['rows']; names = run['columns']
        idx = {n: i for i, n in enumerate(names)}
        for arm, n in (('OFF', 2), ('OFF', 10), ('ON', 2), ('ON', 10)):
            a = 'lv %s|p%d' % (arm, n); b = 'lv %s|p0' % arm
            sa = 'se %s|p%d' % (arm, n); sb = 'se %s|p0' % arm
            d = [r[idx[a]] - r[idx[b]] for r in rows]
            w = math.sqrt(sum(r[idx[sa]] ** 2 + r[idx[sb]] ** 2 for r in rows)) / len(rows)
            acc.setdefault((arm, n), []).append((st.mean(d), w))
    val = {}
    for key, lst in acc.items():
        m = st.mean(x for x, _ in lst); w = math.sqrt(sum(x * x for _, x in lst)) / len(lst)
        val[key] = (m, w)
    claim = {('OFF', 2): (0.19, 0.06), ('ON', 2): (-0.20, 0.07), ('OFF', 10): (2.29, 0.07), ('ON', 10): (-2.32, 0.08)}
    for key in (('OFF', 2), ('ON', 2), ('OFF', 10), ('ON', 10)):
        check('5', 'shift after %2d back-to-back X gates, start %s (percent)' % (key[1], key[0]), claim[key][0], 100 * val[key][0], 0.02, '%+.2f')
    o2, u2 = val[('OFF', 2)][0], -val[('ON', 2)][0]; o10, u10 = val[('OFF', 10)][0], -val[('ON', 10)][0]
    # weighted least squares of o_N = N^2 e2/4 + N b  (e2 = eps^2) on the four numbers
    pts = [(2, val[('OFF', 2)]), (2, (-val[('ON', 2)][0], val[('ON', 2)][1])), (10, val[('OFF', 10)]), (10, (-val[('ON', 10)][0], val[('ON', 10)][1]))]
    A11 = A12 = A22 = B1 = B2 = 0.0
    for N, (y, s) in pts:
        w = 1 / s ** 2; f1 = N * N / 4.0; f2 = float(N)
        A11 += w * f1 * f1; A12 += w * f1 * f2; A22 += w * f2 * f2; B1 += w * f1 * y; B2 += w * f2 * y
    det = A11 * A22 - A12 * A12
    e2 = (B1 * A22 - B2 * A12) / det; b = (A11 * B2 - A12 * B1) / det
    se_e2 = math.sqrt(A22 / det); se_b = math.sqrt(A11 / det)
    eps = math.sqrt(e2); eps_deg = math.degrees(eps); se_deg = math.degrees(se_e2 / (2 * eps))
    check('5', 'push falls short by (degrees)', 1.48, eps_deg, 0.05, '%.2f')
    print('     (+-%.2f deg; ledger sec. 147: 1.48 +- 0.14)' % se_deg)
    print('     count-linear term b in  shift(N) = N^2 eps^2/4 + N b :  b = %.3f +- %.3f %%' % (100 * b, 100 * se_b))
    check('5', 'published "0.26" versus b x 1 (as population error per gate)', 0.26, 100 * b, 0.02, '%.3f')
    check('5', 'published "0.26" versus 4 x b (the only convention that reproduces it)', 0.26, 400 * b, 0.02, '%.3f')
    check('5', '   its width (4 x width of b) vs the claimed 0.12', 0.12, 400 * se_b, 0.02, '%.3f')
    print('     upper edge at two widths, 4 x (b + 2 se): %.2f %%  (ledger: 0.49)' % (400 * (b + 2 * se_b)))
    note('Arithmetic reproduces the ledger\'s 1.48 deg and a linear term; the published 0.26 equals FOUR times the fitted linear coefficient b. I found no file stating why the factor 4 (the derivation was done in the review exchange, ledger sec. 147).')
    note('0.26 +- 0.12 is a measured value %.1f sigma from zero, not an upper bound; the ledger\'s bound is 0.49 at two widths. It is the cap on EVERY count-growing error per gate (leakage, fading during the pulse, pulse noise), not on leakage alone.' % (0.26 / 0.12))
    note('It rests on the assumption that the |2> population after N gates is the same for an OFF and an ON start (ledger sec. 148, "secondary"); one chip (Pittsburgh).')


# ================================================================================================ 6. SIMULATED PLANT
def simulate(plant, noise, seed, n_clocks=100, repeats=30, O=2.18):
    rng = random.Random(seed)
    fit_all, w39_all = [], []
    for rep in range(repeats):
        wfit, w39 = [], []
        for _ in range(n_clocks):
            rate = math.radians(rng.uniform(2.3, 5.6))               # rad per us
            ang = lambda t: rate * t + rng.gauss(0, noise)
            T = [ang(t) for t in (10.0, 20.0, 30.0)]
            K = [ang(k * O * (1.0 + plant)) for k in LOOKS]
            a = unwrap([0.0] + T)
            c0, c1 = quad_no_intercept([10.0, 20.0, 30.0], a[1:4])
            teq = [equiv_time(c0, c1, x) for x in K]
            ok = [i for i, v in enumerate(teq) if v == v]
            if len(ok) >= 4: wfit.append(linfit([LOOKS[i] for i in ok], [teq[i] for i in ok]))
            if teq[2] == teq[2] and teq[5] == teq[5]: w39.append((teq[5] - teq[2]) / 6.0)
        fit_all.append(nanmedian(wfit) / O); w39_all.append(nanmedian(w39) / O)
    return st.mean(fit_all), st.pstdev(fit_all), st.mean(w39_all), st.pstdev(w39_all)


def plant_section():
    head('6. SIMULATED PLANT   (re-implementation: the original simulation script is not on disk, only its result line in ledger sec. 328)')
    print('   100 synthetic spectator clocks, rates uniform 2.3-5.6 deg/us, looks of exactly 2.18 us x (1 + planted), 30 repeats per seed, 8 seeds,')
    print('   read with the same inversion as the real data (quadratic through the origin on 10/20/30 us, roots per look, slope over 1..9 looks).')
    print('   Gaussian phase noise added to every measured angle. The ledger does not say which noise; its 0.06 rad is used, with 0.12 for contrast.')
    print('   %-38s %-34s %-34s' % ('case', 'fit 1-9: mean over seeds [min,max]', '3-and-9: mean over seeds [min,max]'))
    res = {}
    for label, plant, noise in (('nothing planted, no noise', 0.0, 0.0), ('nothing planted, phase noise 0.06 rad', 0.0, 0.06), ('nothing planted, phase noise 0.12 rad', 0.0, 0.12),
                                ('4 % planted, no noise', 0.04, 0.0), ('4 % planted, phase noise 0.06 rad', 0.04, 0.06), ('4 % planted, phase noise 0.12 rad', 0.04, 0.12)):
        rs = [simulate(plant, noise, 100 + s) for s in range(8)]
        f = [r[0] for r in rs]; g = [r[2] for r in rs]
        res[label] = (st.mean(f), st.mean(g), min(f), max(f), min(g), max(g))
        print('   %-38s %.4f  [%.4f, %.4f]          %.4f  [%.4f, %.4f]' % (label, st.mean(f), min(f), max(f), st.mean(g), min(g), max(g)))
    r = res['nothing planted, no noise']
    check('6', 'nothing planted, no noise: reads', 1.000, r[0], 0.0005, '%.4f')
    r = res['nothing planted, phase noise 0.06 rad']
    check('6', 'nothing planted, noise 0.06: fit 1-9 (claim "1.000")', 1.000, r[0], 0.004, '%.4f')
    check('6', 'nothing planted, noise 0.06: 3-and-9 (claim "1.000")', 1.000, r[1], 0.004, '%.4f')
    r = res['4 % planted, phase noise 0.06 rad']
    check('6', 'plant 4 %, noise 0.06: fit 1-9 (claim low end 1.037)', 1.037, r[0], 0.004, '%.4f')
    check('6', 'plant 4 %, noise 0.06: 3-and-9 (claim high end 1.039)', 1.039, r[1], 0.004, '%.4f')
    note('The claim holds only with real-data-sized phase noise. With NO noise a planted 4 % reads back 1.0400 exactly; with noise it reads a few tenths of a percent low, and the unplanted case a few tenths low of 1.000. The seed-to-seed range is about +-0.003, so "1.037-1.039" and "1.000" are not distinguishable from 1.034-1.040 and 0.996-1.000 here.')
    note('This tests the witness-clock ruler only (spectators / stated look). It does not test the T/W ratio of section 1, and it does not test the "equal-length idle" analysis that replaced the stated-duration comparison on 21 Oct 2026.')


# ================================================================================================
def main():
    print(__doc__.split('\n\n')[0])
    sort_section()
    td = time_section()
    pd = D('pittsburgh_park_idle_push.json')
    idle_section(pd)
    bend_section(td)
    leak_section(pd)
    plant_section()
    secs = {}
    for s, ok in RESULTS: secs.setdefault(s, []).append(ok)
    print('\n' + '=' * 100 + '\nSUMMARY  (OK = recomputed number matches the claim to tolerance; wording problems are in the NOTE lines)\n' + '=' * 100)
    for s in sorted(secs): print('   section %s: %d of %d numbers OK' % (s, sum(secs[s]), len(secs[s])))


if __name__ == '__main__':
    main()
