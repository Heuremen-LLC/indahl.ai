#!/usr/bin/env python3
"""verify_gate_cost.py -- recompute every published gate-cost number from the published data.

    python3 verify_gate_cost.py

No account, no network, no dependencies beyond the standard library. Reads data/gate_cost.json
(per-qubit levels from 17 hardware jobs, ~300 KB) and recomputes each figure, printing it beside what
the page claims. OK = matches to the published precision; DIFFERS = does not. Items that cannot be
recomputed from the data are labelled UNSOURCED and are not counted as OK.

Estimator (plain words). A qubit starts in its ground state (population 0). We apply n X gates
(n = 2, 6, 10), waiting 30 microseconds after each. Each X gate flips ground<->excited, and during
every 30 us wait the excited population decays by a factor q (the survival over 30 us). Predicted
excited population after n gates = recursion  on <- off + on*(1-q), off <- on*q  (start on=0, off=1),
i.e. the gates are assumed perfect and only decay acts. The RESIDUAL is measured minus predicted,
averaged over qubits. The SLOPE PER GATE is the least-squares slope of the residual against n.
q comes from a reference measurement in the same job (qubit prepared excited and left alone):
  "own interval"  : q = the 30 us survival measured directly
  "90 us ruler"   : q = (survival after 90 us) ** (30/90)
  "one exponential": q = (survival after 300 us) ** (30/300)
Survival values are clipped to [0.02, 1] (Pittsburgh's original reader clipped to [0.02, 1.2]).
Widths are 1-sigma, propagated from shot noise on every level (no resampling; first order).
"""
import json, math, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
NS = (2, 6, 10)

# ---- what the pages claim (heuremen.org findings.html, what-we-measured.html, index.html) --------------
SITE = {
    'kingston day 1':               (-0.00198, 0.00035),
    'kingston day 2 (3-read mean)': (-0.00136, 0.00017),
    'fez':                          (-0.00182, 0.00027),
    'boston read 1 (day 2)':        (-0.00154, None),
    'boston read 2 (day 2)':        (-0.00080, None),
    'boston read 3 (day 2)':        (-0.00063, None),
    'phoenix figure 1':             (-0.00002, None),
    'phoenix figure 2':             (-0.00010, None),
}
CLAIM_PITT = (-0.00106, 0.0008)          # task statement / lab notebook, not in the site table
CLAIM_PCT_NEG = (54, 70)                 # "54-70 % of individual qubits carry their own negative slope"
CLAIM_RATIO = {'boston': 8.5, 'kingston': 8.4, 'fez': 6.0, 'pittsburgh': 5.5, 'phoenix': 4.1}   # notebook: "(90-us ruler)"
CLAIM_RATIO_RANGE = (4.0, 8.5)           # site: "4 to 8.5 times the chip's stated gate error"
# Manufacturer's stated X-gate error, median over qubits. UNSOURCED: copied from the lab notebook; the
# backend-properties read (6 Oct 23:35 UTC) was not saved. Not recomputable here.
STATED_X_ERR = {'boston': 1.63e-4, 'kingston': 2.35e-4, 'fez': 3.02e-4, 'pittsburgh': 1.92e-4, 'phoenix': 2.22e-4}


def book(q, n):
    on, off = 0.0, 1.0
    for _ in range(n):
        on, off = off + on * (1 - q), on * q
    return on


def clip(x, lo, hi): return min(max(x, lo), hi)


def qfun(ruler, r, i):
    hi = 1.2 if r['chip'] == 'ibm_pittsburgh' and ruler == 'own' else 1.0
    if ruler == 'own':  return clip(r['R30'][i], 0.02, hi), r['se_R30'][i], 1.0
    if ruler == 'r90':  return clip(r['R90'][i], 0.02, 1.0) ** (1 / 3), r['se_R90'][i], 1 / 3
    if ruler == 'r300': return clip(r['R300'][i], 0.02, 1.0) ** (1 / 10), r['se_R300'][i], 1 / 10


def residuals(r, ruler):
    """per-qubit residual at n=2,6,10 and per-qubit variance of (slope contribution)."""
    rows = []
    for i in range(len(r['qubits'])):
        q, seq, p = qfun(ruler, r, i)
        # derivative of q wrt the raw survival s: p * s^(p-1) (where not clipped) -> numeric
        d = []
        for n in NS:
            d.append(r['N%d' % n][i] - book(q, n))
        h = 1e-5
        dq = [(book(min(q + h, 1.0), n) - book(q - h, n)) / (min(q + h, 1.0) - (q - h)) for n in NS]
        # chain rule: q = s**p  ->  dq/ds = p*s**(p-1)
        s_raw = {'own': r['R30'][i], 'r90': r['R90'][i], 'r300': r['R300'][i]}[ruler]
        dqds = p * clip(s_raw, 0.02, 1.0) ** (p - 1) if p != 1.0 else 1.0
        rows.append((d, dq, dqds, seq))
    return rows


def slope_stats(r, ruler):
    rows = residuals(r, ruler); N = len(rows)
    dmean = [sum(row[0][k] for row in rows) / N for k in range(3)]
    slope = (dmean[2] - dmean[0]) / 8.0            # least squares through n = 2, 6, 10
    var = 0.0
    for i, (d, dq, dqds, seq) in enumerate(rows):
        var += (r['se_N10'][i] ** 2 + r['se_N2'][i] ** 2 + ((dq[2] - dq[0]) * dqds * seq) ** 2) / 64.0
    width = math.sqrt(var) / N
    per_bit = []
    for d, *_ in rows:
        per_bit.append((d[2] - d[0]) / 8.0)
    return slope, width, dmean, per_bit


def trim_mean(x, cut=0.2):
    x = sorted(x); k = int(cut * len(x)); return st.mean(x[k:len(x) - k])


def avg_slopes(r, ruler='own'):
    rows = residuals(r, ruler); cols = [[row[0][k] for row in rows] for k in range(3)]
    f = lambda agg: (agg(cols[2]) - agg(cols[0])) / 8.0
    return f(st.mean), f(st.median), f(trim_mean)


def binom_two_sided(k, n):
    """exact two-sided sign test p-value against p = 0.5."""
    kk = min(k, n - k); tail = sum(math.comb(n, j) for j in range(kk + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def flag(got, want, tol): return 'OK     ' if abs(got - want) <= tol else 'DIFFERS'


def main():
    D = json.load(open(os.path.join(HERE, 'data', 'gate_cost.json')))['runs']
    by = {(r['chip'], r['run']): r for r in D}
    S = {}
    for r in D:
        for ruler in ('own', 'r90', 'r300'):
            S[(r['chip'], r['run'], ruler)] = slope_stats(r, ruler)
    g = lambda chip, run, ruler='own': S[(chip, run, ruler)]
    n_ok = n_diff = 0

    def line(label, got, want, tol=0.0000051, wid=None, wantw=None, fmt='%+.5f'):
        nonlocal n_ok, n_diff
        f = flag(got, want, tol); n_ok += f.startswith('OK'); n_diff += not f.startswith('OK')
        s = '  %s  %-38s computed %s' % (f, label, fmt % got)
        if wid is not None: s += ' (shot-noise width %.5f)' % wid
        s += '   claimed %s' % (fmt % want)
        if wantw is not None: s += ' +- %.5f' % wantw
        print(s)

    print('GATE COST: slope of the residual excited population per X gate (own-interval estimator unless stated)')
    print('1. Slopes per gate, site table. The claimed +- is a shot-resampling width that also resamples the reference readouts;')
    print('   the width printed here is first-order shot noise on the levels only, so it is expected to be somewhat smaller.')
    s, w, *_ = g('ibm_kingston', 392);      line(SITE and 'kingston day 1 (run 392)', s, SITE['kingston day 1'][0], wid=w, wantw=0.00035)
    ks = [g('ibm_kingston', k) for k in (721, 722, 723)]
    m = st.mean(x[0] for x in ks); w = math.sqrt(sum(x[1] ** 2 for x in ks)) / 3
    line('kingston day 2, mean of runs 721-723', m, SITE['kingston day 2 (3-read mean)'][0], wid=w, wantw=0.00017)
    s, w, *_ = g('ibm_fez', 371);           line('fez (run 371)', s, SITE['fez'][0], wid=w, wantw=0.00027)
    for k, key in zip((711, 712, 713), ('boston read 1 (day 2)', 'boston read 2 (day 2)', 'boston read 3 (day 2)')):
        s, w, *_ = g('ibm_boston', k); line('%s (run %d)' % (key, k), s, SITE[key][0], wid=w)
    px = [g('ibm_phoenix', k) for k in (751, 752, 753)]
    pm_own = st.mean(x[0] for x in px); pm_90 = st.mean(g('ibm_phoenix', k, 'r90')[0] for k in (751, 752, 753))
    line('phoenix day 2, 3-read mean, own interval', pm_own, SITE['phoenix figure 1'][0])
    line('phoenix day 2, 3-read mean, 90 us ruler', pm_90, SITE['phoenix figure 2'][0])
    print('     (the page does not say what the two phoenix figures are; these two readings reproduce them to 5 decimals)')
    s, w, *_ = g('ibm_pittsburgh', 121);    line('pittsburgh 2 Oct (not in site table)', s, CLAIM_PITT[0], tol=0.0000101, wid=w, wantw=CLAIM_PITT[1])

    print('\n2. Numbers the site does NOT show but the same data give')
    for chip, run in (('ibm_boston', 441), ('ibm_phoenix', 531)):
        s, w, *_ = g(chip, run)
        print('        %-13s day 1 run %d own interval  %+.5f +- %.5f  (%.1f sigma)' % (chip, run, s, w, abs(s) / w))
    for chip, run in (('ibm_phoenix', 531), ('ibm_phoenix', 751), ('ibm_phoenix', 752), ('ibm_phoenix', 753), ('ibm_kingston', 392), ('ibm_boston', 441)):
        print('        %-13s run %d  own %+.5f   90us %+.5f   one-exponential %+.5f' % ((chip, run) + tuple(g(chip, run, k)[0] for k in ('own', 'r90', 'r300'))))
    pm300 = st.mean(g('ibm_phoenix', k, 'r300')[0] for k in (751, 752, 753))
    print('        phoenix day-2 3-read mean on the one-exponential ruler: %+.5f' % pm300)

    print('\n3. "Negative under every estimator, every read, every heavy-hex chip tested"')
    heavy_site = [(c, k) for c, ks_ in (('ibm_fez', [371]), ('ibm_kingston', [392, 721, 722, 723]), ('ibm_boston', [441, 711, 712, 713])) for k in ks_]
    heavy = heavy_site + [('ibm_aachen', k) for k in (841, 842, 843)]
    def neg_report(runs, name):
        nonlocal n_ok, n_diff
        allneg = 0; ruler_neg = 0
        for c, k in runs:
            a = avg_slopes(by[(c, k)])
            rn = all(g(c, k, x)[0] < 0 for x in ('own', 'r90', 'r300')); an = all(x < 0 for x in a)
            ruler_neg += rn; allneg += rn and an
        ok_ = allneg == len(runs)
        print('  %s  %s: %d of %d runs negative on all 3 rulers; %d of %d also negative on mean, median and 20%%-trim over qubits' % ('OK     ' if ok_ else 'DIFFERS', name, ruler_neg, len(runs), allneg, len(runs)))
        n_ok += ok_; n_diff += not ok_
        for c, k in runs:
            a = avg_slopes(by[(c, k)]); bad = [x for x in ('own', 'r90', 'r300') if g(c, k, x)[0] >= 0] + [n for n, x in zip(('mean', 'median', 'trim'), a) if x >= 0]
            if bad: print('        not negative: %s %d on %s' % (c, k, bad))
    neg_report(heavy_site, 'fez, kingston, boston (the chips on the site)')
    neg_report(heavy, 'adding aachen (3 reads, not on the site)')
    print('     single reads below 2 sigma on the own-interval ruler (shot-noise width):', ', '.join('%s %d (%.1f sigma)' % (c.replace('ibm_', ''), k, abs(g(c, k)[0]) / g(c, k)[1]) for c, k in heavy if abs(g(c, k)[0]) / g(c, k)[1] < 2) or 'none')

    print('\n4. Share of individual qubits with a negative own slope (claimed 54-70 %)')
    rng_ = {}
    for c, k in heavy + [('ibm_phoenix', 531), ('ibm_phoenix', 751), ('ibm_phoenix', 752), ('ibm_phoenix', 753)]:
        pb = g(c, k)[3]; n = len(pb); neg = sum(1 for x in pb if x < 0)
        rng_[(c, k)] = (100.0 * neg / n, binom_two_sided(neg, n))
        print('        %-13s run %4d  %3d qubits  %3.0f%% negative  (sign-test p = %.3f)' % (c, k, n, rng_[(c, k)][0], rng_[(c, k)][1]))
    site_chips = [(c, k) for c, k in heavy if c != 'ibm_aachen']
    lo = min(rng_[x][0] for x in site_chips); hi = max(rng_[x][0] for x in site_chips)
    lo_all = min(rng_[x][0] for x in heavy); hi_all = max(rng_[x][0] for x in heavy)
    ok = round(lo_all) == CLAIM_PCT_NEG[0] and round(hi_all) == CLAIM_PCT_NEG[1]
    print('  %s  range over the 3 chips on the site: %.0f-%.0f %%; over all heavy-hex runs incl. aachen: %.0f-%.0f %%; claimed %d-%d %%' % ('OK     ' if ok else 'DIFFERS', lo, hi, lo_all, hi_all, *CLAIM_PCT_NEG))
    n_ok += ok; n_diff += not ok
    pl = [rng_[x][0] for x in rng_ if x[0] == 'ibm_phoenix']
    print('     phoenix runs fall at %.0f-%.0f %%: inside the claimed range, so this share does not separate it from the heavy-hex chips' % (min(pl), max(pl)))

    print('\n5. Cost per gate as a multiple of the stated X-gate error')
    print('     stated errors are UNSOURCED (copied from the notebook; the properties read was not saved). Ratios use |slope| / stated error.')
    day1 = {'boston': ('ibm_boston', 441), 'kingston': ('ibm_kingston', 392), 'fez': ('ibm_fez', 371), 'pittsburgh': ('ibm_pittsburgh', 121), 'phoenix': ('ibm_phoenix', 531)}
    print('     %-11s %9s %12s %12s %12s' % ('chip', 'claimed', 'own interval', '90 us ruler', '300 us ruler'))
    rat = {}
    for ch, (c, k) in day1.items():
        v = [abs(g(c, k, x)[0]) / STATED_X_ERR[ch] for x in ('own', 'r90', 'r300')]; rat[ch] = v
        which = 'own' if abs(v[0] - CLAIM_RATIO[ch]) < 0.06 else ('90us' if abs(v[1] - CLAIM_RATIO[ch]) < 0.06 else 'neither')
        print('     %-11s %9.1f %12.2f %12.2f %12.2f   claimed value is the %s ruler' % (ch, CLAIM_RATIO[ch], v[0], v[1], v[2], which))
    bad = [ch for ch in rat if not abs(rat[ch][1] - CLAIM_RATIO[ch]) < 0.06]
    print('  %s  every claimed ratio reproduces on ONE ruler (the notebook says the 90 us ruler): fails for %s' % ('OK     ' if not bad else 'DIFFERS', ', '.join(bad) or 'none'))
    n_ok += not bad; n_diff += bool(bad)
    bad2 = [ch for ch in rat if not abs(rat[ch][0] - CLAIM_RATIO[ch]) < 0.06]
    print('     on the own-interval ruler instead, the claimed ratio fails for: %s' % (', '.join(bad2) or 'none'))
    lo_claim, hi_claim = CLAIM_RATIO_RANGE
    hv0 = [c for c in rat if c != 'phoenix']
    okr = abs(min(rat[c][0] for c in hv0) - lo_claim) < 0.5 and abs(max(rat[c][0] for c in hv0) - hi_claim) < 0.06
    print('  %s  "4 to 8.5 times" for the heavy-hex chips (own interval, day 1): computed %.1f to %.1f' % ('OK     ' if okr else 'DIFFERS', min(rat[c][0] for c in hv0), max(rat[c][0] for c in hv0)))
    n_ok += okr; n_diff += not okr
    mx90 = max(rat, key=lambda c: rat[c][1]); mxown = max(rat, key=lambda c: rat[c][0])
    print('  max ratio: own interval %s %.2f; 90 us ruler %s %.2f; claimed max 8.5' % (mxown, rat[mxown][0], mx90, rat[mx90][1]))
    hv = [c for c in rat if c != 'phoenix']
    print('  heavy-hex only, own interval: %.1f to %.1f; 90 us ruler: %.1f to %.1f   (site range 4 to 8.5; the 4 is the phoenix figure, a chip the site says shows zero)'
          % (min(rat[c][0] for c in hv), max(rat[c][0] for c in hv), min(rat[c][1] for c in hv), max(rat[c][1] for c in hv)))
    d2 = {'boston': [g('ibm_boston', k)[0] for k in (711, 712, 713)], 'kingston': [g('ibm_kingston', k)[0] for k in (721, 722, 723)]}
    for ch, v in d2.items():
        print('     day 2 %-9s own-interval 3-read mean %+.5f -> %.1f x stated   (single reads %s)' % (ch, st.mean(v), abs(st.mean(v)) / STATED_X_ERR[ch], ' / '.join('%.1f' % (abs(x) / STATED_X_ERR[ch]) for x in v)))

    print('\nSummary: %d OK, %d DIFFERS' % (n_ok, n_diff))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
