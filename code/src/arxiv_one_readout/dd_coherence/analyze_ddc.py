"""Analysis of the DDC run exactly as PLAN_DDC.md. python analyze_ddc.py [folder]. Reads job_ddc_<chip>.json, raw_ddc_<chip>.npz, props_ddc_<chip>.json.
THIN WRAPPER: ../dd_run/analyze_dd.py (and through it the deciding runs' ruler, deciding_runs/analyze.py) is IMPORTED UNCHANGED and runs every
reading R0-R8 of the DD run on N = 2, 8 (analyze_dd.NSTEP set to (2, 8); with two N the phase slope is the line through the two points).
Added AFTER the DD readings, nothing before them changes:
  R9   R6 as a FRACTION of R4: median(R6) / median(R4) over spectators, paired bootstrap (0 = unchanged, -1 = removed, +1 = doubled).
  R10  RATE form: per spectator, per-readout loss -ln(coh_M / coh_D) / N with echo minus without (the PRODUCT form of the count run).
  R11  what 'same RATE' predicts for R6: R4 x (coh_D,on / coh_D,off - 1), per spectator, median (beside R6: same rate vs same amount).
  DECISION at N = 8, per chip and for the inverse-variance combination of the two chips (context), and the HEADLINE from the per-chip
  decisions, by the rules pre-registered in PLAN_DDC.md."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'dd_run'))
import analyze_dd                                  # unchanged; registers A.RUNS['dd']
A = analyze_dd.A
analyze_dd.NSTEP = (2, 8)
NDEC = 8
def lab(k, N):
    return {'R0': 'R0 null: coherence, N=0 "on" - "off" (identical circuits) [all]', 'R4': 'R4 coherence cost, DD off, N=%d (D - M) [all]' % N,
            'R5': 'R5 coherence cost, DD on, N=%d (D - M) [all]' % N, 'R6': 'R6 R5 - R4, N=%d [all]' % N}[k]
def decide(r0, r4, r5, r6):
    """r* = (value, lo, hi, n, outcome) or None (copies shifted). Returns (verdict, notes)."""
    if r4 is None or r5 is None or r6 is None: return 'CANNOT TELL (copies shifted on R4, R5 or R6)', ''
    v4, v5, v6 = r4[0], r5, r6
    notes = 'R6 half-width %.4g = %.2f x R4 (target <= 0.33)' % ((r6[2] - r6[1]) / 2, (r6[2] - r6[1]) / 2 / v4 if v4 > 0 else np.nan)
    notes += ' | R0 coherence %s' % ('CONSISTENT' if r0 is not None and r0[4] == 'CONSISTENT' else 'RESOLVED OR SHIFTED: decision PROVISIONAL, read against R0')
    if r4[4] != 'ABOVE': return 'CANNOT TELL (no cost resolved: R4 %s)' % r4[4], notes
    if (r6[2] - r6[1]) / 2 > v4: return 'CANNOT TELL (R6 half-width exceeds R4: too wide for a cost this small)', notes
    has = r6[1] <= -v4 <= r6[2]                         # literal form: R6 interval contains -R4
    o6, o5 = r6[4], r5[4]                               # paired form: R5 = R6 + R4 spectator by spectator
    notes += ' | literal: R6 interval %s -R4 = %+.4g; paired: R5 %s' % ('CONTAINS' if has else 'EXCLUDES', -v4, o5)
    if o6 == 'ABOVE': return 'THE ECHO INCREASES THE COST', notes
    if o6 == 'CONSISTENT' and not has and o5 == 'ABOVE': return 'THE ECHO DOES NOT REMOVE THE COST (unchanged within the interval)', notes
    if o6 == 'CONSISTENT' and has: return 'CANNOT TELL (interval too wide: unchanged and removed both fit)', notes
    if o6 == 'BELOW' and has and o5 == 'CONSISTENT': return 'THE ECHO REMOVES THE COST (within the interval)', notes
    if o6 == 'BELOW' and not has and o5 == 'ABOVE': return 'THE ECHO REDUCES THE COST, PART REMAINS', notes
    if o6 == 'BELOW' and not has and o5 == 'BELOW': return 'THE ECHO OVER-REMOVES (readout arm ends MORE coherent than idle)', notes
    return 'CANNOT TELL (literal and paired forms disagree)', notes
def ddc(J):
    analyze_dd.dd(J)
    I = J.info; S = np.array(I['S']); n = J.props_n; chip = A.CUR[0]
    def ex(c, d, mode, N, st): return J.mean_pm(c, 'fin', n, dd=d, mode=mode, N=N, setting=st)[S]
    def co(c, d, mode, N): return np.hypot(ex(c, d, mode, N, 'YY'), ex(c, d, mode, N, 'XX'))
    nsh = int(J.rec['shots']) * len(J.idx((0, 1), dd='off', mode='D', N=0, setting='XX')); floor = 5 / np.sqrt(nsh)
    print(' DDC additions (R9-R11, decision at N=%d)' % NDEC)
    for N in analyze_dd.NSTEP:
        r4 = co((0, 1), 'off', 'D', N) - co((0, 1), 'off', 'M', N); r6 = (co((0, 1), 'on', 'D', N) - co((0, 1), 'on', 'M', N)) - r4
        m4 = np.median(r4); idx = A.RNG.integers(0, len(S), (A.B, len(S)))
        with np.errstate(divide='ignore', invalid='ignore'):
            bs = np.median(r6[idx], 1) / np.median(r4[idx], 1); lo, hi = np.percentile(bs, [2.5, 97.5])
            print('  %-58s %+.3f [%+.3f, %+.3f]  (0 unchanged, -1 removed, +1 doubled)%s' % ('R9 R6 as a fraction of R4, N=%d [all]' % N, np.median(r6) / m4, lo, hi,
                  '' if m4 > 0 else '  R4 median <= 0: ratio undefined'))
    def lam(c, d, N):
        D, M = co(c, d, 'D', N), co(c, d, 'M', N)
        with np.errstate(divide='ignore', invalid='ignore'): return np.where((D >= floor) & (M >= floor), -np.log(M / D) / N, np.nan)
    for N in analyze_dd.NSTEP:
        A.reading('R10 RATE: per-readout loss, DD on - DD off, N=%d [all]' % N, lambda c, N=N: lam(c, 'on', N) - lam(c, 'off', N))
    for N in analyze_dd.NSTEP:   # a PREDICTION to set beside R6, not a test: printed with its interval, no outcome, not in the tally
        c = (0, 1); m, lo, hi, k, _ = A.boot((co(c, 'off', 'D', N) - co(c, 'off', 'M', N)) * (co(c, 'on', 'D', N) / co(c, 'off', 'D', N) - 1))
        print('  %-58s %+.4g [%+.4g, %+.4g] n=%d  (prediction for R6 if the echo keeps the RATE; R6 = 0 if it keeps the AMOUNT)' % ('R11 R6 predicted by SAME RATE, N=%d [all]' % N, m, lo, hi, k))
    got = {k: [p for l, ch, p in A.LOG if l == lab(k, NDEC if k != 'R0' else 0) and ch == chip] for k in ('R0', 'R4', 'R5', 'R6')}
    got = {k: (v[-1] if v else None) for k, v in got.items()}
    v, notes = decide(got['R0'], got['R4'], got['R5'], got['R6'])
    print('  DECISION %s N=%d: %s\n      %s' % (chip, NDEC, v, notes)); DEC[chip] = (v, known_good(chip, J.rec.get('plan_sha256') == 'SYNTH'))
A.RUNS['ddc'] = ddc; DEC = {}
# KNOWN-GOOD (PLAN_DDC.md): R4 [all] of the DD run, results_dd.txt 22 Oct 2026 (value, lo, hi); REQUIRED = resolved there (ABOVE)
OLD_R4 = {('ibm_marrakesh', 2): (0.004694, 0.001352, 0.007801, True), ('ibm_marrakesh', 8): (0.01224, 0.007445, 0.02387, True),
          ('ibm_fez', 2): (0.002315, -0.0009581, 0.004604, False), ('ibm_fez', 8): (0.004418, 0.001699, 0.007968, True)}
def known_good(chip, synth=False):
    """(1) R0 coherence (N = 0 'on' vs 'off', identical circuits) must read CONSISTENT; (2) R4 at each N the DD run RESOLVED must reproduce
    it: |new - old| <= 1.96 sqrt(s_new^2 + s_old^2), s = 95 % width / 3.92. Synthetic jobs: (2) not applicable (planted, not the chip)."""
    ok = True; r0 = [p for l, ch, p in A.LOG if l == lab('R0', 0) and ch == chip]; r0 = r0[-1] if r0 else None
    g = r0 is not None and r0[4] == 'CONSISTENT'; ok &= g
    print('  KNOWN-GOOD %s (1) R0 coherence, identical circuits: %s -> %s' % (chip, 'copies shifted' if r0 is None else '%+.4g [%+.4g, %+.4g] %s' % (r0[0], r0[1], r0[2], r0[4]), 'PASS' if g else 'FAIL'))
    for N in analyze_dd.NSTEP:
        if synth: print('  KNOWN-GOOD %s (2) R4 N=%d vs the DD run: SYNTH, not applicable' % (chip, N)); continue
        o = OLD_R4.get((chip, N)); r = [p for l, ch, p in A.LOG if l == lab('R4', N) and ch == chip]; r = r[-1] if r else None
        if o is None: print('  KNOWN-GOOD %s (2) R4 N=%d: no DD-run value for this chip' % (chip, N)); continue
        if r is None: g = False; txt = 'copies shifted'
        else:
            d = r[0] - o[0]; tol = 1.96 * np.hypot((r[2] - r[1]) / 3.92, (o[2] - o[1]) / 3.92); g = abs(d) <= tol
            txt = 'new %+.4g [%+.4g, %+.4g] vs DD run %+.4g [%+.4g, %+.4g]: difference %+.4g, allowed +-%.4g' % (r[0], r[1], r[2], o[0], o[1], o[2], d, tol)
        print('  KNOWN-GOOD %s (2) R4 N=%d %s -> %s' % (chip, N, txt, ('PASS' if g else 'FAIL') if o[3] else ('reproduced' if g else 'differs') + ' (printed only: not resolved in the DD run)'))
        if o[3]: ok &= g
    print('  KNOWN-GOOD %s: %s' % (chip, 'PASS' if ok else 'FAIL -> this chip\'s decision is printed but NOT counted in the HEADLINE')); return ok
def headline():
    """HEADLINE (pre-registered, PLAN_DDC.md): from the PER-CHIP decisions only. Same verdict on both -> that verdict, both chips;
    a verdict on one and CANNOT TELL on the other -> that verdict, ONE chip (named); different verdicts -> CHIPS DISAGREE; none -> CANNOT TELL.
    A chip whose KNOWN-GOOD check failed is left out (and named)."""
    bad = [c for c, (v, k) in DEC.items() if not k]
    if bad: print('HEADLINE excludes (KNOWN-GOOD failed): %s' % ', '.join(bad))
    told = {c: v for c, (v, k) in DEC.items() if k and not v.startswith('CANNOT TELL')}
    if not told: h = 'CANNOT TELL (no chip decided)'
    elif len(set(told.values())) > 1: h = 'CHIPS DISAGREE: ' + ' | '.join('%s %s' % (c, v) for c, v in told.items())
    else: h = '%s -- on %s (%d of %d chips decided)' % (list(told.values())[0], ', '.join(told), len(told), len(DEC))
    print('HEADLINE N=%d: %s' % (NDEC, h))
def combined():
    """Inverse-variance combination of the chips for R4, R5, R6 at N = 8 (as the summary does), then the same decision rule."""
    out = {}
    for k in ('R4', 'R5', 'R6'):
        rows = [p for l, ch, p in A.LOG if l == lab(k, NDEC)]
        if len(rows) < 2 or any(p is None for p in rows): out[k] = None; continue
        v = np.array([p[0] for p in rows]); s = np.array([(p[2] - p[1]) / 3.92 for p in rows]); w = 1 / s ** 2
        m = np.sum(w * v) / np.sum(w); se = 1 / np.sqrt(np.sum(w)); lo, hi = m - 1.96 * se, m + 1.96 * se; out[k] = (m, lo, hi, 99, A.outcome(lo, hi, 99))
    r0 = [p for l, ch, p in A.LOG if l == lab('R0', 0)]; r0ok = (None, None, None, None, 'CONSISTENT') if r0 and all(p is not None and p[4] == 'CONSISTENT' for p in r0) else None
    v, notes = decide(r0ok, out['R4'], out['R5'], out['R6'])
    print('=' * 100); print('DECISION COMBINED (inverse variance, %d chips) N=%d: %s\n      %s' % (len([1 for l, c, p in A.LOG if l == lab('R6', NDEC)]), NDEC, v, notes))
    for k in ('R4', 'R5', 'R6'):
        if out[k] is not None: print('      %s combined %+.4g [%+.4g, %+.4g] -> %s' % (k, out[k][0], out[k][1], out[k][2], out[k][4]))
def run_all(folder=HERE):
    A.run_all(folder); analyze_dd.tally(); combined(); headline()
if __name__ == '__main__': run_all(sys.argv[1] if len(sys.argv) > 1 else HERE)
