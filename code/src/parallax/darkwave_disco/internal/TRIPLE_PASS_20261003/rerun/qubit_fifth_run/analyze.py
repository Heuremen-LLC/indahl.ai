"""analyze.py (v4) -- reads the THREE RUNS on THREE CHIPS. Modes: run1 | run1+2 | run1+2+3 (one chip: --chip NAME) | all (the three chips side by side).
(spec: ../../QUBIT_THREE_RUNS_APPROVED_20261001.md, incl. the night amendments, and the owner's WHOLE-CHIP BOXES change)

  python analyze.py run1|run1+2|run1+2+3 --chip NAME --data-dir DIR [--predictions P.json (OURS)] [--boot N]
  python analyze.py all --data-dir DIR [--predictions P1.json P2.json P3.json (OURS, one per run)] [--boot N]
  BLANK RULE: the BLANK chip's results are NOT opened by any mode until all nine jobs (3 runs x 3 chips) have landed; only mode `all` reads them.
  python analyze.py --make-template predictions_template.json

ORDER OF THE PROGRAM (this order is the guard):
  1. REFUSE any run whose results are not marked complete (or whose npz hash differs from the meta). No partial reads, ever.
  2. Print the CIRCULARITY AUDIT. It reads only the prediction file's HEADER (written_at, data_seen, which names are filled), never a number.
  3. Compute and print every measured quantity. NO function in steps 1-3 takes a prediction as an argument.
  4. Save the measured rows (analysis_*.json).
  5. LAST: score_predictions() -- the only code that loads predicted numbers. The miss column feeds nothing else.

HOUSE RULES, enforced in the code:
  * Raw I/Q is never cut to 0/1. Each look is projected onto the per-qubit line from the OFF centre to the ON centre (a continuous number,
    OFF = 0, ON = 1 in that frame). Third moments (skew) run on the continuous number only.
  * Every difference is a THREE (a start/wait/run read against the other two) or an equation with all its parts shown.
  * No pass/fail cut, no verdict word. Numbers carry widths (seeded bootstrap over shots, all qubits resampled jointly; plus the spread
    across the three groups of three). Pooling across qubits = MEDIAN. CAN'T READ is a row with its reason. Negative solves print raw.
  * THE LOOK LEDGER: every look of every circuit is in the ledger; this program lists which looks it read and flags any it did not.
"""
import os, sys, json, argparse, warnings, re, importlib
import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import (STARTS, WAITS_US as WAITS, TWINS, RUN3_LAYOUTS as LAYOUTS, MATCHED_TWIN, SHORT, MEDIUM, LONG, BOXES, SEEN_LEVELS, ALLOWED_SEEN, parse_iso,
                    freeze_path, recompute_hash_from_freeze, sha256_file, ledger_self_check, chip_assignment, box_of_chip, CHIP_OURS, maker_values, ZERO_EARLIER,
                    MACHINE_RESET_WHAT)

SEED = 20261031            # analysis seed (mixture draws and bootstrap)
BOOT = 200
MIN_SHOTS = 30
TAU_LO_US, TAU_HI_US = 1.0, 1.0e5
STATS = ['mean', 'var', 'skew']
DEFAULT_SEEN = {1: 'none', 2: 'run1', 3: 'runs1+2'}      # what a prediction sealed before run N has seen
warnings.filterwarnings('ignore', category=RuntimeWarning)


class Refused(Exception):
    pass


# ------------------------------------------------------------------------------------------------ look tracking (the ledger audit)
TRACK = {'on': False, 'set': set()}


def touch(run, key, i):
    if TRACK['on']: TRACK['set'].add((run, key, int(i)))


class TL(list):
    """list of projected looks that records every look that is read (run, circuit, look index)."""
    def __init__(self, items, run, key):
        super().__init__(items); self.run, self.key = run, key
    def __getitem__(self, i):
        if TRACK['on']:
            for j in (range(len(self))[i] if isinstance(i, slice) else [i % len(self)]): TRACK['set'].add((self.run, self.key, j))
        return super().__getitem__(i)
    def __iter__(self):
        if TRACK['on']:
            for j in range(len(self)): TRACK['set'].add((self.run, self.key, j))
        return super().__iter__()


# ------------------------------------------------------------------------------------------------ loading (refuses incomplete)
def load(data_dir, run_no):
    """data_dir = the chip's own folder."""
    mp = os.path.join(data_dir, f'run{run_no}_meta.json'); npz = os.path.join(data_dir, f'run{run_no}_results.npz')
    if not os.path.exists(mp) or not os.path.exists(npz): raise Refused(f'run {run_no}: results/meta not found in {data_dir}: nothing to read (no partial reads)')
    meta = json.load(open(mp))
    if meta.get('complete') is not True: raise Refused(f'run {run_no}: results are NOT marked complete. Refusing to read any outcome data.')
    if meta.get('results_sha256') != sha256_file(npz): raise Refused(f'run {run_no}: results file hash differs from the one recorded when it was marked complete')
    ledger = meta['ledger']; ledger_self_check(ledger)
    z = np.load(npz)
    want = {f"{c['key']}__L{k + 1}" for c in ledger['circuits'] for k in range(c['n_looks'])}
    if set(z.files) != want: raise Refused(f'run {run_no}: result arrays differ from the look ledger (a look not in the ledger, or one missing)')
    D = {c['key']: [np.asarray(z[f"{c['key']}__L{k + 1}"]).astype(complex) for k in range(c['n_looks'])] for c in ledger['circuits']}
    return D, meta


def keys_of(meta, start):
    return [c['key'] for c in meta['circuits'] if c['start'] == start]


def _wait_real(meta):
    m = {}
    for c in meta['circuits']:
        for w, r in zip(c['pre_waits_us'], c['pre_waits_realized_us']):
            if w: m[w] = r
    return m


# ------------------------------------------------------------------------------------------------ frames and projection
def _cat(D, run, keys):
    for k in keys: touch(run, k, 0)
    return np.concatenate([D[k][0] for k in keys])


def frame_own(D, meta, run):
    """This run's own frame, per qubit. Run 1 has no look without a wait, so its frame uses the SHORTEST wait's OFF and ON looks;
    runs 2 and 3 use look 1 (no wait) of every OFF and every ON circuit. Returns (mu0, d) complex per qubit."""
    if run == 1: ks = {s: [f'{s}|w{min(WAITS)}'] for s in ('OFF', 'ON')}
    else: ks = {s: keys_of(meta, s) for s in ('OFF', 'ON')}
    m0 = _cat(D, run, ks['OFF']).mean(0); m1 = _cat(D, run, ks['ON']).mean(0)
    return m0, m1 - m0


def frame_common(D2, m2, D3, m3):
    """The ONE frame for the combined equations: look 1 (no wait, no earlier look of ours, after the machine's reset) of every OFF and ON circuit of runs 2 and 3 pooled."""
    m0 = np.concatenate([_cat(D2, 2, keys_of(m2, 'OFF')), _cat(D3, 3, keys_of(m3, 'OFF'))]).mean(0)
    m1 = np.concatenate([_cat(D2, 2, keys_of(m2, 'ON')), _cat(D3, 3, keys_of(m3, 'ON'))]).mean(0)
    return m0, m1 - m0


def projected(D, fr, run):
    mu0, d = fr
    return {k: TL([np.real((L - mu0) * np.conj(d)) / np.abs(d) ** 2 for L in looks], run, k) for k, looks in D.items()}


def stats3(p):
    n = p.shape[0]
    if n < MIN_SHOTS:
        nan = np.full(p.shape[1:], np.nan); return nan, nan.copy(), nan.copy()
    m = p.mean(0); c = p - m; v = (c ** 2).sum(0) / (n - 1)
    return m, v, (c ** 3).mean(0) / v ** 1.5


def cov(a, b):
    n = a.shape[0]
    return ((a - a.mean(0)) * (b - b.mean(0))).sum(0) / (n - 1)


def mix(a, b, rng):
    n = min(len(a), len(b)); h = n // 2
    return np.concatenate([a[rng.integers(0, len(a), h)], b[rng.integers(0, len(b), n - h)]])


def loo(vals):
    ks = list(vals)
    return {k: vals[k] - np.mean([vals[j] for j in ks if j != k], axis=0) for k in ks}


# ------------------------------------------------------------------------------------------------ the fading fits
def _mdl(form, ws, G, tau):
    return G * (1 - np.exp(-ws / tau)) if form == 'gap' else G * np.exp(-ws / tau)    # gap: what a look changed by / level: what a look reads


def _g0(form, y):
    v = y[-1] if form == 'gap' else y[0]
    return v if v != 0 else 1e-3


def _fit_one(form, ws, y):
    best = None
    for t0 in (20.0, 100.0, 1000.0):
        try:
            r = least_squares(lambda par: _mdl(form, ws, par[0], np.exp(par[1])) - y, [_g0(form, y), np.log(t0)],
                              bounds=([-np.inf, np.log(TAU_LO_US)], [np.inf, np.log(TAU_HI_US)]))
        except Exception:
            continue
        if best is None or r.cost < best.cost: best = r
    return best


def _bound_reason(lt):
    if lt <= np.log(TAU_LO_US) + 1e-3: return f'fading time ran to the lower search edge ({TAU_LO_US:g} us): the waits set cannot place it'
    if lt >= np.log(TAU_HI_US) - 1e-3: return f'fading time ran to the upper search edge ({TAU_HI_US:g} us): the waits set cannot place it'
    return None


def fit_fade(ws, Y, form):
    """Y: start -> value at the three waits ws (us). Per-start fits (G, tau) and one shared-tau fit (tau shared, G per start)."""
    ws = np.asarray(ws, float); taus, reasons, resid = {}, {}, {}
    for s in STARTS:
        y = np.asarray(Y[s], float)
        if not np.all(np.isfinite(y)): taus[s] = np.nan; reasons[s] = 'values not finite (too few shots or zero spread)'; continue
        b = _fit_one(form, ws, y)
        if b is None: taus[s] = np.nan; reasons[s] = 'fit did not converge'; continue
        rs = _bound_reason(b.x[1]); taus[s] = np.nan if rs else float(np.exp(b.x[1]))
        if rs: reasons[s] = rs
    ys = np.concatenate([np.asarray(Y[s], float) for s in STARTS])
    for s in STARTS: resid[s] = np.full(len(ws), np.nan)
    if not np.all(np.isfinite(ys)): taus['shared'] = np.nan; reasons['shared'] = 'values not finite'; return taus, resid, reasons
    best = None
    for t0 in (20.0, 100.0, 1000.0):
        def r(par):
            return np.concatenate([_mdl(form, ws, par[1 + i], np.exp(par[0])) - np.asarray(Y[s], float) for i, s in enumerate(STARTS)])
        try:
            sol = least_squares(r, [np.log(t0)] + [_g0(form, np.asarray(Y[s], float)) for s in STARTS],
                                bounds=([np.log(TAU_LO_US), -np.inf, -np.inf, -np.inf], [np.log(TAU_HI_US), np.inf, np.inf, np.inf]))
        except Exception:
            continue
        if best is None or sol.cost < best.cost: best = sol
    if best is None: taus['shared'] = np.nan; reasons['shared'] = 'fit did not converge'; return taus, resid, reasons
    for i, s in enumerate(STARTS): resid[s] = best.fun[3 * i: 3 * i + 3]
    rs = _bound_reason(best.x[0]); taus['shared'] = np.nan if rs else float(np.exp(best.x[0]))
    if rs: reasons['shared'] = rs
    return taus, resid, reasons


def _add_fit(out, reasons, prefix, ws, Y, form, with_loo=False):
    """writes {prefix}.{OFF,MID,ON,shared} (and {prefix}.{start}-others)"""
    taus, resid, rs = fit_fade(ws, Y, form)
    for k in STARTS + ['shared']:
        out[f'{prefix}.{k}'] = taus[k]
        if k in rs: reasons[f'{prefix}.{k}'] = rs[k]
    if with_loo:
        for k, v in loo({s: taus[s] for s in STARTS}).items():
            out[f'{prefix}.{k}-others'] = v
            reasons[f'{prefix}.{k}-others'] = "a start-read-against-the-other-two needs all three fading times; one is CAN'T READ"
    return resid


# ------------------------------------------------------------------------------------------------ quantities per run
def q_run1(DS, MS, rng):
    """RUN 1 -- THE MESSAGE and the clock with ZERO earlier looks of ours (after the machine's reset): START, WAIT, LOOK."""
    D, meta = DS[1], MS[1]; out, reasons = {}, {}
    fr = frame_own(D, meta, 1); P = projected(D, fr, 1)
    for w in WAITS:
        pp = {s: P[f'{s}|w{w}'][0] for s in STARTS}
        st = {s: stats3(pp[s]) for s in STARTS}
        mixes = {'MIX': stats3(mix(pp['OFF'], pp['ON'], rng)), 'MIXrest.OFF': stats3(mix(pp['MID'], pp['ON'], rng)), 'MIXrest.ON': stats3(mix(pp['OFF'], pp['MID'], rng))}
        for s in STARTS:
            for i, n in enumerate(STATS): out[f'r1.{s}.w{w}.{n}'] = st[s][i]
        for nm, m in mixes.items():
            for i, n in enumerate(STATS): out[f'r1.{nm}.w{w}.{n}'] = m[i]
        for i, n in enumerate(STATS):
            out[f'r1.MID-MIX.w{w}.{n}'] = st['MID'][i] - mixes['MIX'][i]
            out[f'r1.OFF-MIXrest.w{w}.{n}'] = st['OFF'][i] - mixes['MIXrest.OFF'][i]
            out[f'r1.ON-MIXrest.w{w}.{n}'] = st['ON'][i] - mixes['MIXrest.ON'][i]
    wr = _wait_real(meta); ws = [wr[w] for w in WAITS]
    Y = {s: [np.median(P[f'{s}|w{w}'][0].mean(0)) for w in WAITS] for s in STARTS}
    _add_fit(out, reasons, 'r1.tauF', ws, Y, 'level')
    out['r1.sep_raw'] = np.abs(fr[1])
    out['r1.remainder_rms'] = np.sqrt(np.mean([out[f'r1.MID-MIX.w{w}.{n}'] ** 2 for w in WAITS for n in STATS], axis=0))
    return out, reasons


def _L1(out, P, meta, run):
    pp = {s: np.concatenate([P[k][0] for k in keys_of(meta, s)]) for s in STARTS}
    for s in STARTS:
        for i, n in enumerate(STATS): out[f'r{run}.L1.{s}.{n}'] = stats3(pp[s])[i]


def q_run2(DS, MS, rng):
    """RUN 2 -- THE CLOCK with ONE earlier look: START, LOOK, WAIT, LOOK."""
    D, meta = DS[2], MS[2]; out, reasons = {}, {}
    fr = frame_own(D, meta, 2); P = projected(D, fr, 2)
    _L1(out, P, meta, 2)
    wr = _wait_real(meta); ws = [wr[w] for w in WAITS]; Y, YF = {}, {}
    for s in STARTS:
        gm, fm = [], []
        for w in WAITS:
            p1, p2 = P[f'{s}|w{w}']; g = p2 - p1
            out[f'r2.{s}.w{w}.F'] = p2.mean(0)
            out[f'r2.{s}.w{w}.gap_mean'] = g.mean(0); out[f'r2.{s}.w{w}.gap_var'] = g.var(0, ddof=1)
            gm.append(g.mean(0)); fm.append(p2.mean(0))
        for w, v in zip(WAITS, loo({str(w): gm[i] for i, w in enumerate(WAITS)}).values()): out[f'r2.{s}.w{w}.gap_mean-otherwaits'] = v
        Y[s] = [np.median(x) for x in gm]; YF[s] = [np.median(x) for x in fm]
    resid = _add_fit(out, reasons, 'r2.tau', ws, Y, 'gap', True)
    for s in STARTS:
        for i, w in enumerate(WAITS): out[f'r2.{s}.w{w}.resid'] = resid[s][i]
    out['r2.remainder_rms'] = np.sqrt(np.mean(np.concatenate([resid[s] for s in STARTS]) ** 2))
    _add_fit(out, reasons, 'r2.tauF', ws, YF, 'level')
    return out, reasons


def q_run3(DS, MS, rng):
    """RUN 3 -- THE SUBSTRATE with TWO earlier looks, in MIRRORED TWINS: START, LOOK, WAIT a, LOOK, WAIT b, LOOK."""
    D, meta = DS[3], MS[3]; out, reasons = {}, {}
    fr = frame_own(D, meta, 3); P = projected(D, fr, 3)
    _L1(out, P, meta, 3)
    wr = _wait_real(meta); closure = []
    names = ['V12', 'V23', 'V13', 'hat1', 'hat2', 'hat3', 'C12', 'C23', 'C13', 'rem12', 'rem23', 'rem13', 'g12', 'g23', 'g13']
    per = {}
    for s in STARTS:
        for (a, b) in LAYOUTS:
            p1, p2, p3 = P[f'{s}|w{a}-{b}']
            V12, V23, V13 = (np.var(x, 0, ddof=1) for x in (p1 - p2, p2 - p3, p1 - p3))
            C12, C23, C13 = cov(p1, p2), cov(p2, p3), cov(p1, p3)
            r = {'V12': V12, 'V23': V23, 'V13': V13,
                 'hat1': (V12 + V13 - V23) / 2, 'hat2': (V12 + V23 - V13) / 2, 'hat3': (V13 + V23 - V12) / 2,     # three-cornered hat, RAW
                 'C12': C12, 'C23': C23, 'C13': C13,
                 'rem12': C12 - (C13 + C23) / 2, 'rem23': C23 - (C12 + C13) / 2, 'rem13': C13 - (C12 + C23) / 2,   # the remainder, not forced to zero
                 'g12': (p2 - p1).mean(0), 'g23': (p3 - p2).mean(0), 'g13': (p3 - p1).mean(0), 'm2': p2.mean(0), 'm3': p3.mean(0)}
            closure.append(np.abs(r['g12'] + r['g23'] - r['g13']))     # algebraic identity: ruler row, not a finding
            per[(s, a, b)] = r
            for n in names: out[f'r3.{s}.w{a}-{b}.{n}'] = r[n]
    for s in STARTS:
        for n in names: out[f'r3.{s}.pool.{n}'] = np.mean([per[(s, a, b)][n] for a, b in LAYOUTS], axis=0)
    for n in names: out[f'r3.ALL.{n}'] = np.mean([per[k][n] for k in per], axis=0)
    out['r3.closure_ruler'] = np.max(closure, axis=0)
    out['r3.remainder_rms'] = np.sqrt(np.mean([per[k][n] ** 2 for k in per for n in ('rem12', 'rem23', 'rem13')], axis=0))
    # TURNING BACK TIME: each twin, (a,b) minus (b,a), per start, per number
    for (a, b) in TWINS:
        for s in STARTS:
            for st, f in (('L2mean', lambda r: r['m2']), ('L3mean', lambda r: r['m3']), ('g13', lambda r: r['g13']), ('V13', lambda r: r['V13'])):
                out[f'r3.twin.{a}-{b}.{s}.{st}'] = f(per[(s, a, b)]) - f(per[(s, b, a)])
    ws = [wr[w] for w in WAITS]
    for gap, idx, pos in (('tau12', 'g12', 0), ('tau23', 'g23', 1)):
        Y = {s: [np.median(np.mean([per[(s, a, b)][idx] for (a, b) in LAYOUTS if (a, b)[pos] == w], axis=0)) for w in WAITS] for s in STARTS}
        _add_fit(out, reasons, f'r3.{gap}', ws, Y, 'gap')
    YF = {}
    for s in STARTS:
        YF[s] = []
        for w in WAITS:
            f2 = np.mean([per[(s, a, b)]['m3'] for (a, b) in LAYOUTS if b == w], axis=0)     # look 3, two earlier looks, wait w in the last gap
            out[f'r3.{s}.w{w}.F'] = f2; YF[s].append(np.median(f2))
    _add_fit(out, reasons, 'r3.tauF', ws, YF, 'level')
    return out, reasons


def q_comb(DS, MS, rng):
    """THE SELF-EFFECT EQUATION. F(n, wait, start) = what the look after a wait reads when n looks came before: n=0 Run 1, n=1 Run 2 (look 2),
    n=2 Run 3 (look 3, pooled over the two twin orders whose last wait is that wait). All on raw I/Q in ONE frame (look 1 of runs 2+3).
    first effect = F(1)-F(0); second effect = F(2)-F(1); the hunter's number = second / first. Three clocks: the fading time at n = 0, 1, 2."""
    out, reasons = {}, {}
    fr = frame_common(DS[2], MS[2], DS[3], MS[3])
    P = {1: projected(DS[1], fr, 1), 2: projected(DS[2], fr, 2), 3: projected(DS[3], fr, 3)}
    wr = _wait_real(MS[1]); ws = [wr[w] for w in WAITS]
    F = {0: {}, 1: {}, 2: {}}
    for s in STARTS:
        for w in WAITS:
            F[0][(s, w)] = P[1][f'{s}|w{w}'][0].mean(0)
            F[1][(s, w)] = P[2][f'{s}|w{w}'][1].mean(0)
            F[2][(s, w)] = np.mean([P[3][f'{s}|w{a}-{b}'][2].mean(0) for (a, b) in LAYOUTS if b == w], axis=0)
            e1 = F[1][(s, w)] - F[0][(s, w)]; e2 = F[2][(s, w)] - F[1][(s, w)]
            for n in (0, 1, 2): out[f'c.F.n{n}.{s}.w{w}'] = F[n][(s, w)]
            out[f'c.eff1.{s}.w{w}'] = e1; out[f'c.eff2.{s}.w{w}'] = e2
            m1, m2 = np.nanmedian(e1), np.nanmedian(e2)
            out[f'c.hunter.{s}.w{w}'] = m2 / m1 if m1 != 0 and np.isfinite(m1) and np.isfinite(m2) else np.nan
            reasons[f'c.hunter.{s}.w{w}'] = 'first look effect is zero or not finite: the ratio has no denominator'
    # F(2) split by the EARLIER wait a: look 3 sits after a + w of elapsed time, so the pooled F(2) is not a one-wait reading. Shown, not corrected.
    for s in STARTS:
        for w in WAITS:
            for (a, b) in LAYOUTS:
                if b != w: continue
                f2 = P[3][f'{s}|w{a}-{b}'][2].mean(0); out[f'c.F.n2.{s}.w{w}.a{a}'] = f2
                e1 = F[1][(s, w)] - F[0][(s, w)]; m1 = np.nanmedian(e1)
                out[f'c.hunter.{s}.w{w}.a{a}'] = np.nanmedian(f2 - F[1][(s, w)]) / m1 if m1 != 0 and np.isfinite(m1) else np.nan
                reasons[f'c.hunter.{s}.w{w}.a{a}'] = 'first look effect is zero or not finite: the ratio has no denominator'
    # FIX 1, THE HUNTER'S NUMBER AT MATCHED ELAPSED TIME. waits short + medium = long (to the 16-dt grid), so the twin (short,medium) and (medium,short) lands
    # its third look at exactly the LONG elapsed wait, where Run 1 (zero earlier looks of ours, after the machine's reset) and Run 2 (one earlier look) also have a look:
    #   F(0,long) = run 1, F(1,long) = run 2, F(2,long) = run 3 via the short+medium twin (both orders shown, and their mean).
    # ONLY this twin is matched in elapsed time to Runs 1 and 2. The other two twins are read against each other (their own mirror) only.
    sh, md, lg = MATCHED_TWIN[0], MATCHED_TWIN[1], LONG
    for s in STARTS:
        f0, f1 = F[0][(s, lg)], F[1][(s, lg)]
        e1 = f1 - f0; m1 = np.nanmedian(e1)
        fo = {o: P[3][f'{s}|w{o[0]}-{o[1]}'][2].mean(0) for o in ((sh, md), (md, sh))}
        fm = np.mean([fo[(sh, md)], fo[(md, sh)]], axis=0)
        out[f'c.Fm.n2.{s}'] = fm
        out[f'c.effm2.{s}'] = fm - f1
        ok1 = m1 != 0 and np.isfinite(m1)
        out[f'c.hunterm.{s}'] = np.nanmedian(fm - f1) / m1 if ok1 else np.nan
        reasons[f'c.hunterm.{s}'] = 'first look effect (matched, at the long wait) is zero or not finite: the ratio has no denominator'
        for o, f in fo.items():
            out[f'c.Fm.n2.{s}.o{o[0]}-{o[1]}'] = f
            out[f'c.hunterm.{s}.o{o[0]}-{o[1]}'] = np.nanmedian(f - f1) / m1 if ok1 else np.nan
            reasons[f'c.hunterm.{s}.o{o[0]}-{o[1]}'] = 'first look effect (matched) is zero or not finite'
    # the n=0 and n=1 clocks have ONE wait of elapsed time per circuit; for n=2 the like-for-like axis is TOTAL elapsed time a+b, which is the same for
    # both orders of a twin: so the n=2 clock is fitted on F(2) averaged over the two orders of each twin, against a+b.
    FT = {s: [] for s in STARTS}; wsT = []
    for (a, b) in TWINS:
        wsT.append(wr[a] + wr[b])
        for s in STARTS:
            f = np.mean([P[3][f'{s}|w{a}-{b}'][2].mean(0), P[3][f'{s}|w{b}-{a}'][2].mean(0)], axis=0)
            out[f'c.F.n2T.{s}.T{a}+{b}'] = f; FT[s].append(np.median(f))
    for n in (0, 1):
        _add_fit(out, reasons, f'c.tauF.n{n}', ws, {s: [np.median(F[n][(s, w)]) for w in WAITS] for s in STARTS}, 'level')
    _add_fit(out, reasons, 'c.tauF.n2', wsT, FT, 'level')
    for (i, j) in ((0, 1), (1, 2), (0, 2)):
        for k in STARTS + ['shared']:
            a, b = out[f'c.tauF.n{i}.{k}'], out[f'c.tauF.n{j}.{k}']
            out[f'c.tauratio.n{i}-n{j}.{k}'] = np.log10(b / a) if np.isfinite(a) and np.isfinite(b) and a > 0 and b > 0 else np.nan
            reasons[f'c.tauratio.n{i}-n{j}.{k}'] = "one of the two fading times is CAN'T READ"
    return out, reasons


def q_return(DS, MS, rng):
    """FIX B. THE RETURN PASS (analysis only; needs all three runs). Run 3 solves each look's OWN error from the other two (the three-cornered-hat solve, hat1 = the
    first look's own error variance). This carries that solved first-look error BACK onto Run 1's lone look, per start and per wait, in ONE frame: RUN 3's own frame
    (look 1 of every OFF and every ON circuit of Run 3), so the rows contain Run 1 and Run 3 data and nothing from Run 2.
      measured = the spread (variance) of Run 1's lone look as measured,  look = the part of it attributable to the look (Run 3's solved first-look error variance,
      pooled over the six layouts of that start; the same number at every wait: Run 3's first look has no wait before it, and nothing is rescaled for the wait),
      remains = measured - look. THE REMAINDER: raw, negatives kept, never zeroed, no verdict word. Whatever depends on the wait lands in it, by construction."""
    out, reasons = {}, {}
    fr = frame_own(DS[3], MS[3], 3)
    P1 = projected(DS[1], fr, 1); P3 = projected(DS[3], fr, 3)
    hat1 = {}
    for s_ in STARTS:
        h = []
        for (a, b) in LAYOUTS:
            p1, p2, p3 = P3[f'{s_}|w{a}-{b}']
            V12, V23, V13 = (np.var(x, 0, ddof=1) for x in (p1 - p2, p2 - p3, p1 - p3))
            h.append((V12 + V13 - V23) / 2)
        hat1[s_] = np.mean(h, axis=0)
    rems = []
    for w in WAITS:
        meas_all, look_all = [], []
        for s_ in STARTS:
            meas = np.var(P1[f'{s_}|w{w}'][0], 0, ddof=1)
            out[f'ret.{s_}.w{w}.measured'] = meas; out[f'ret.{s_}.w{w}.look'] = hat1[s_]; out[f'ret.{s_}.w{w}.remains'] = meas - hat1[s_]
            meas_all.append(meas); look_all.append(hat1[s_]); rems.append(meas - hat1[s_])
        out[f'ret.ALL.w{w}.measured'] = np.mean(meas_all, axis=0); out[f'ret.ALL.w{w}.look'] = np.mean(look_all, axis=0); out[f'ret.ALL.w{w}.remains'] = np.mean(meas_all, axis=0) - np.mean(look_all, axis=0)
    out['ret.remainder_rms'] = np.sqrt(np.mean([r ** 2 for r in rems], axis=0))
    return out, reasons


# ------------------------------------------------------------------------------------------------ bootstrap driver (rows for ALL qubits and per group)
def resample(D, rng):
    R = {}
    for k, looks in D.items():
        idx = rng.integers(0, looks[0].shape[0], looks[0].shape[0])
        R[k] = [L[idx] for L in looks]
    return R


def slice_cols(DS, cols):
    return {r: {k: [L[:, cols] for L in looks] for k, looks in D.items()} for r, D in DS.items()}


def pooled(v):
    a = np.asarray(v, float)
    return float(np.nanmedian(a)) if np.isfinite(a).any() else float('nan')   # MEDIAN across qubits: one poor qubit cannot own the pool


def pool_counts(v):
    """FIX K: how many qubits a pooled median had to drop because their value was NaN: (dropped, qubits). A scalar (a fit) has no per-qubit pool: (0, 1)."""
    a = np.asarray(v, float)
    return (0, 1) if a.ndim == 0 else (int(np.isnan(a).sum()), int(a.size))


def quantify(fn, DS, MS, B=BOOT, seed=SEED):
    """rows[name] = {value, width (bootstrap sd), width_pct (half of the 16-84 percentile range), group_spread, ..., groups: [3 rows]}.
    The bootstrap resamples shots of each circuit (all looks of a shot together, all qubits together), each run independently."""
    first = MS[min(MS)]; allq = first['all_q']; gi = [[allq.index(q) for q in g] for g in first['groups_of_three']]
    subsets = {'ALL': list(range(len(allq))), 0: gi[0], 1: gi[1], 2: gi[2]}
    TRACK['on'] = True; TRACK['set'] = set()
    full, reasons = fn(DS, MS, np.random.default_rng(seed))
    TRACK['on'] = False; tracked = set(TRACK['set'])
    fulls = {'ALL': full}
    for g in (0, 1, 2): fulls[g] = fn(slice_cols(DS, subsets[g]), MS, np.random.default_rng(seed))[0]
    brng = np.random.default_rng(seed + 7)
    reps = {sub: {k: [] for k in full} for sub in subsets}
    for _ in range(B):
        R = {r: resample(D, brng) for r, D in DS.items()}
        for sub, cols in subsets.items():
            r, _r = fn(R if sub == 'ALL' else slice_cols(R, cols), MS, brng)
            for k in full: reps[sub][k].append(pooled(r[k]))
    N = next(iter(DS[min(DS)].values()))[0].shape[0]
    def mkrow(val, a, extra=None):
        a = np.array(a); nf = int(np.isnan(a).sum()); ok = a[np.isfinite(a)]
        row = {'value': val, 'width': float(np.std(ok, ddof=1)) if ok.size > 1 else float('nan'),
               'width_pct': float((np.percentile(ok, 84) - np.percentile(ok, 16)) / 2) if ok.size > 1 else float('nan'),
               'n_refit_failed': nf, 'boot': B, 'shots': N}
        return row
    res = {}
    for k in full:
        row = mkrow(pooled(full[k]), reps['ALL'][k]); row['groups'] = [mkrow(pooled(fulls[g][k]), reps[g][k]) for g in (0, 1, 2)]
        for r_, src in [(row, full[k])] + [(row['groups'][g], fulls[g][k]) for g in (0, 1, 2)]:
            r_['n_qubits_dropped_nan'], r_['n_qubits_pooled'] = pool_counts(src)
        gv = [r['value'] for r in row['groups']]
        row['group_spread'] = float(np.std(gv, ddof=1)) if np.isfinite(gv).sum() > 1 else float('nan')
        for r in [row] + row['groups']:
            if not np.isfinite(r['value']):
                r['cant_read'] = reasons.get(k) or ('too few shots (%d < %d)' % (N, MIN_SHOTS) if N < MIN_SHOTS else 'no finite value (zero spread or empty)')
        res[k] = row
    return res, tracked


# ------------------------------------------------------------------------------------------------ FIX 6: carry-over between shots; per-qubit rows
def carry_rows(D, meta, run, B=BOOT, seed=SEED):
    """How the LAST look of one shot relates to the FIRST look of the NEXT shot (rep_delay 500 us between shots). A READING: no correction is applied anywhere.
    Per start, over the circuits of that start (pairs never cross a circuit boundary: each circuit is its own pub): x = last look of shot i, y = first look of shot i+1,
    both on the run's own projected line. Reported as the correlation and the slope (fraction of the OFF-to-ON separation that carries over), median across qubits,
    with a bootstrap width (pairs resampled) and the group-of-three spread. Run 1 has one look per shot, so there last = first (the look's lag-1 relation).
    It assumes the service returns shots in shot order (not documented as guaranteed: a fire-path risk)."""
    fr = frame_own(D, meta, run); P = projected(D, fr, run)
    allq = meta['all_q']; gi = [[allq.index(q) for q in gq] for gq in meta['groups_of_three']]
    subsets = {'ALL': list(range(len(allq))), 0: gi[0], 1: gi[1], 2: gi[2]}
    rng = np.random.default_rng(seed + 11); out = {}
    def st(x, y, cols):
        x = x[:, cols]; y = y[:, cols]; xc = x - x.mean(0); yc = y - y.mean(0)
        c = (xc * yc).sum(0); vx = (xc ** 2).sum(0); vy = (yc ** 2).sum(0)
        return float(np.nanmedian(c / np.sqrt(vx * vy))), float(np.nanmedian(c / vx)), int(np.isnan(c / np.sqrt(vx * vy)).sum()), int(len(cols))
    for s_ in STARTS:
        xs, ys = [], []
        for k in keys_of(meta, s_):
            looks = list(P[k]); La = np.asarray(looks[-1]); Lf = np.asarray(looks[0])
            xs.append((La - La.mean(0))[:-1]); ys.append((Lf - Lf.mean(0))[1:])     # centred within the circuit: circuits with different means must not look like carry-over
        x = np.concatenate(xs); y = np.concatenate(ys); n = len(x)
        reps = {sub: [] for sub in subsets}
        for _ in range(B):
            ix = rng.integers(0, n, n)
            for sub, cols in subsets.items(): reps[sub].append(st(x[ix], y[ix], cols))
        for ni, nm in enumerate(('corr', 'slope')):
            def mk(sub):
                full_ = st(x, y, subsets[sub]); v = full_[ni]; a = np.array([r[ni] for r in reps[sub]]); ok = a[np.isfinite(a)]
                row = {'value': v, 'width': float(np.std(ok, ddof=1)) if ok.size > 1 else float('nan'), 'width_pct': float((np.percentile(ok, 84) - np.percentile(ok, 16)) / 2) if ok.size > 1 else float('nan'),
                       'n_refit_failed': int(np.isnan(a).sum()), 'boot': B, 'shots': n, 'n_qubits_dropped_nan': full_[2], 'n_qubits_pooled': full_[3]}
                if not np.isfinite(v): row['cant_read'] = 'no finite value (zero spread)'
                return row
            row = mk('ALL'); row['groups'] = [mk(gq) for gq in (0, 1, 2)]
            gv = [r['value'] for r in row['groups']]; row['group_spread'] = float(np.std(gv, ddof=1)) if np.isfinite(gv).sum() > 1 else float('nan')
            out[f'carry.r{run}.{s_}.{nm}'] = row
    return out


def qubit_rows(D, meta, run):
    """One row per drawn qubit: how far apart the OFF and ON clouds sit against the OFF cloud's own width (raw I/Q units). A dead or noisy qubit drawn blind shows
    up HERE as a row (CAN'T READ when the clouds overlap or nothing is finite); nothing is checked beforehand and nothing is dropped."""
    if run == 1: ks = {s_: [f'{s_}|w{min(WAITS)}'] for s_ in ('OFF', 'ON')}
    else: ks = {s_: keys_of(meta, s_) for s_ in ('OFF', 'ON')}
    a0 = np.concatenate([D[k][0] for k in ks['OFF']]); a1 = np.concatenate([D[k][0] for k in ks['ON']])
    rows = []
    for j, q in enumerate(meta['all_q']):
        g_ = next(i for i, gq in enumerate(meta['groups_of_three']) if q in gq)
        sep = abs(a1[:, j].mean() - a0[:, j].mean()); sd = float(np.sqrt((a0[:, j].real.var() + a0[:, j].imag.var()) / 2))
        ratio = sep / sd if sd > 0 and np.isfinite(sep) and np.isfinite(sd) else float('nan')
        rows.append({'qubit': int(q), 'group': g_, 'separation_raw': float(sep), 'off_cloud_sd_raw': sd, 'separation_over_width': float(ratio),
                     'cant_read': (None if np.isfinite(ratio) and ratio >= 1.0 else "CAN'T READ (OFF and ON clouds overlap or are not finite)")})
    return rows


def print_carry(C, run):
    print(f'\n-- CARRY-OVER BETWEEN SHOTS, run {run} (rep_delay 500 us; last look of shot i vs first look of shot i+1; a reading, no correction applied; assumes shot order is kept)')
    for s_ in STARTS:
        for nm in ('corr', 'slope'): print(line(f'carry.r{run}.{s_}.{nm}', C[f'carry.r{run}.{s_}.{nm}']))


def print_qubits(rows, run, tag=''):
    print(f'\n-- THE DRAWN QUBITS, run {run}{tag}: OFF-to-ON separation / OFF cloud width (raw I/Q); an unusable qubit is a ROW here, not something checked beforehand')
    for r in rows: print(f"  q{r['qubit']:<4} group {r['group']}  separation {g(r['separation_raw'])}  width {g(r['off_cloud_sd_raw'])}  ratio {g(r['separation_over_width'])}" + (f"  {r['cant_read']}" if r['cant_read'] else ''))


# ------------------------------------------------------------------------------------------------ the template / data-of-each-quantity (rules for the audit)
IDENTITY_NAMES = ('r1.OFF.w60.mean', 'r1.ON.w60.mean')                 # ruler identities (0 and 1 by construction): measured and printed, never predicted or scored
IDENTITY_TRIPLES = {('OFF', 60, 'mean'), ('ON', 60, 'mean')}


def sealable_names():
    n = []
    # FIX J: r1.OFF.w60.mean and r1.ON.w60.mean are NOT sealable: Run 1's frame is built from those very circuits (0 and 1 by construction), so a prediction on them is a box proving its own box.
    n += [f'r1.{s}.w{w}.{x}' for s in STARTS for w in WAITS for x in STATS if (s, w, x) not in IDENTITY_TRIPLES] + [f'r1.MID-MIX.w{w}.{x}' for w in WAITS for x in STATS]
    n += [f'r1.tauF.{k}' for k in STARTS + ['shared']] + ['r1.remainder_rms']
    n += [f'r2.{s}.w{w}.{x}' for s in STARTS for w in WAITS for x in ('F', 'gap_mean')]
    n += [f'r2.tau.{k}' for k in STARTS + ['shared']] + [f'r2.tauF.{k}' for k in STARTS + ['shared']] + ['r2.remainder_rms']
    n += [f'r3.{s}.pool.hat{i}' for s in STARTS for i in (1, 2, 3)] + [f'r3.ALL.hat{i}' for i in (1, 2, 3)]
    n += [f'r3.tau12.shared', 'r3.tau23.shared'] + [f'r3.tauF.{k}' for k in STARTS + ['shared']] + ['r3.remainder_rms']
    n += [f'r3.twin.{a}-{b}.{s}.{x}' for (a, b) in TWINS for s in STARTS for x in ('L2mean', 'L3mean', 'g13', 'V13')]
    n += [f'c.F.n{k}.{s}.w{w}' for k in (0, 1, 2) for s in STARTS for w in WAITS]
    n += [f'c.{e}.{s}.w{w}' for e in ('eff1', 'eff2', 'hunter') for s in STARTS for w in WAITS]
    n += [f'c.Fm.n2.{s}' for s in STARTS] + [f'c.effm2.{s}' for s in STARTS] + [f'c.hunterm.{s}' for s in STARTS]
    n += [f'c.tauF.n{k}.{x}' for k in (0, 1, 2) for x in STARTS + ['shared']]
    n += [f'c.tauratio.n{i}-n{j}.{x}' for (i, j) in ((0, 1), (1, 2), (0, 2)) for x in STARTS + ['shared']]
    n += [f'drift.L1.{s}.{x}.run{r}' for s in STARTS for x in STATS for r in (1, 2, 3)]
    return n


def data_of(name):
    """THE RUNS WHOSE RAW DATA ENTER a quantity. The combined frame comes from look 1 of runs 2 and 3, so every c.* quantity contains runs 2 and 3
    (plus run 1 when a run-1 reading is in it). Own-run quantities use their own frame."""
    m = re.match(r'(r[123])\.', name)
    if m: return {int(m.group(1)[1])}
    if name.startswith('ret.'): return {1, 3}                    # THE RETURN PASS: Run 1's lone look and Run 3's solve, both in Run 3's own frame (no Run 2 data enters)
    if name.startswith('drift.'): return {1, 2, 3}
    if name.startswith('c.'):
        base = {2, 3}
        m = re.match(r'c\.(?:F|tauF)\.n(\d)T?\.', name)
        if m: return base | {int(m.group(1)) + 1}
        m = re.match(r'c\.tauratio\.n(\d)-n(\d)\.', name)
        if m: return base | {int(m.group(1)) + 1, int(m.group(2)) + 1}
        if name.startswith('c.eff2.') or name.startswith('c.effm2.') or name.startswith('c.Fm.'): return base   # F(2) - F(1): runs 3 and 2, frame from 2 and 3
        return {1, 2, 3}                                           # eff1 (runs 1,2), hunter (1,2,3): with the frame, all three
    return {1, 2, 3}


def family(name):
    return 'drift' if name.startswith('drift.') else ('c' if name.startswith('c.') else name.split('.')[0])   # 'ret' = THE RETURN PASS


def overlap(name, seen):
    """runs shared between what the prediction was written from and the data inside the measured quantity."""
    return sorted(data_of(name) & set(SEEN_LEVELS[seen]))


def make_template(path):
    ents = {n: {'written_at': None, 'data_seen': None, 'predicted': None, 'width': None} for n in sealable_names()}
    json.dump({'_note': 'THE PREDICTION IS A LOOK. Run freeze.py --run N FIRST. Then fill, per entry you use: written_at (ISO, with offset), data_seen '
                        '(none | maker | run1 | runs1+2), predicted, width (> 0). _written_at must be later than the freeze and earlier than the run, and so must EVERY entry written_at. '
                        'MISS = |measured - predicted| / width, computed last. A quantity that contains the data a prediction was written from is marked '
                        'BOX ON BOX and not scored. Leave predicted null to skip a quantity. The boxes are WHOLE CHIPS (OURS = ibm_kingston, MAKER, BLANK; a written seed draws which never-touched chip is which); this file is for OURS only. '
                        'The two ruler identities (r1.OFF.w60.mean, r1.ON.w60.mean) are not in this file. The fading time of an OFF start has NO BASIS: leave it null.',
               '_run': None, '_written_at': None, '_sealed_sha256': None, 'predictions': ents}, open(path, 'w'), indent=1)
    print(f'wrote template with {len(ents)} quantities -> {path}')


# ------------------------------------------------------------------------------------------------ printing
def g(x):
    return 'nan' if x is None or not np.isfinite(x) else f'{x:.4g}'


def line(name, row):
    if row is None: return f'  {name:<40} (not in this mode)'
    if row.get('cant_read'): return f"  {name:<40} CAN'T READ ({row['cant_read']})"
    extra = f'  groups-spread {g(row["group_spread"])}' if np.isfinite(row['group_spread']) else ''
    nf = f'  [{row["n_refit_failed"]}/{row["boot"]} refits CAN\'T READ]' if row['n_refit_failed'] else ''
    if row.get('n_qubits_dropped_nan'): nf += f'  [{row["n_qubits_dropped_nan"]} of {row["n_qubits_pooled"]} qubits NaN: dropped from the pooled median]'
    if name in IDENTITY_NAMES: nf += '  [ruler identity: 0 / 1 by construction, never predicted or scored]'
    pct = f'  [16-84%: +-{g(row["width_pct"])}]' if name.startswith('c.hunter') else ''
    return f'  {name:<40} {g(row["value"]):>10} +-{g(row["width"]):<9}{pct}{extra}{nf}'


def block(title, names, R):
    print(f'\n-- {title}')
    for n in names: print(line(n, R.get(n)))


def three_clocks(R, meta, tau_name, title):
    """Inside (fitted fading time) / outside (the waits we set) / the maker's published T1, T2. Each pair, third beside it."""
    row = R[tau_name]
    if not meta.get('maker_clock'):
        print(f'\n-- {title}: TWO CLOCKS (this chip is BLANK: its calibration was never read, so there is no maker clock and no third beside the pair)')
        if row.get('cant_read'): print(f"  inside time (fitted fading time): CAN'T READ ({row['cant_read']})")
        else: print(f"  inside  (the chip's own fading time, fitted)  {g(row['value'])} +-{g(row['width'])} us")
        print(f'  outside (the waits we set)                     {WAITS} us')
        if not row.get('cant_read'):
            for w in WAITS: print(f"  log10[inside / outside({w} us)] = {g(np.log10(row['value'] / w))} +-{g(row['width'] / row['value'] / np.log(10))}")
        return
    t1, n1, why1 = maker_values(meta['maker_clock'], 'T1_us'); t2, n2, why2 = maker_values(meta['maker_clock'], 'T2_us')
    print(f'\n-- {title}: THREE CLOCKS   [maker values: {meta["maker_clock_source"]}; calibration stamp {meta["calibration_timestamp"]}; '
          f'width for the maker = spread (sd) across the {len(t1)} qubits with a usable value, not a measurement error]')
    cr1 = f"CAN'T READ: {len(t1)} of {n1} qubits have a published T1 (need 2); reasons: {why1 or 'none given'}" if len(t1) < 2 else None
    cr2 = f"CAN'T READ: {len(t2)} of {n2} qubits have a published T2 (need 2); reasons: {why2 or 'none given'}" if len(t2) < 2 else None
    if row.get('cant_read'):
        print(f"  inside time (fitted fading time): CAN'T READ ({row['cant_read']}) -> every pair that needs it is CAN'T READ"); inside = None
    else:
        inside = (row['value'], row['width']); print(f"  inside  (the chip's own fading time, fitted)  {g(inside[0])} +-{g(inside[1])} us")
    print(f'  outside (the waits we set)                     {WAITS} us')
    if n1 - len(t1) or n2 - len(t2): print(f'  maker qubits without a usable value: T1 {n1 - len(t1)} of {n1}' + (f' ({why1})' if why1 else '') + f'; T2 {n2 - len(t2)} of {n2}' + (f' ({why2})' if why2 else ''))
    print('  maker   T1 ' + (cr1 if cr1 else f'median {g(np.median(t1))} us (sd {g(t1.std(ddof=1))})') + ';  T2 ' + (cr2 if cr2 else f'median {g(np.median(t2))} us (sd {g(t2.std(ddof=1))})'))
    def lr(a, wa, b, wb): return np.log10(a / b), np.hypot(wa / a, wb / b) / np.log(10)
    rows = []
    if not cr1:
        m1, m1w = np.median(t1), t1.std(ddof=1)
        if inside:
            for w in WAITS: v, e = lr(inside[0], inside[1], w, 0); rows.append((f'inside / outside({w} us)', v, e, f'maker T1 = {g(m1)} us'))
            v, e = lr(inside[0], inside[1], m1, m1w); rows.append(('inside / maker T1', v, e, f'outside = {WAITS} us'))
        for w in WAITS:
            v, e = lr(w, 0, m1, m1w); rows.append((f'outside({w} us) / maker T1', v, e, f'inside = {g(inside[0]) + " us" if inside else "CAN\'T READ"}'))
    else:
        print("  every pair that needs the maker's T1 is CAN'T READ (reason above)")
        if inside:
            for w in WAITS: v, e = lr(inside[0], inside[1], w, 0); rows.append((f'inside / outside({w} us)', v, e, "maker T1 = CAN'T READ"))
    if not cr2 and inside:
        m2, m2w = np.median(t2), t2.std(ddof=1); v, e = lr(inside[0], inside[1], m2, m2w); rows.append(('inside / maker T2', v, e, f'outside = {WAITS} us'))
    elif cr2: print("  every pair that needs the maker's T2 is CAN'T READ (reason above)")
    for nm, v, e, third in rows: print(f'  log10[{nm:<28}] = {g(v):>8} +-{g(e):<8}  | third beside: {third}')


# ------------------------------------------------------------------------------------------------ reports
DRY = '   [DRY RUN, SYNTHETIC I/Q: code path only]'


def report_run1(R, meta):
    print(f"\n==== RUN 1 -- {ZERO_EARLIER.upper()}: START, WAIT, LOOK (the message, and the clock with no earlier look of ours)" + (DRY if meta['synthetic_iq'] else ''))
    for w in WAITS:
        for n in STATS:
            block(f'wait {w} us, {n}: each start; the 50/50 OFF+ON pool; each start read against the pool of the other two',
                  [f'r1.{s}.w{w}.{n}' for s in STARTS] + [f'r1.MIX.w{w}.{n}', f'r1.MID-MIX.w{w}.{n}', f'r1.OFF-MIXrest.w{w}.{n}', f'r1.ON-MIXrest.w{w}.{n}'], R)
    block(f'the fading time with {ZERO_EARLIER} (level fit F(0,w) = G exp(-w/tau); per start; shared)', [f'r1.tauF.{k}' for k in STARTS + ['shared']], R)
    block('raw look geometry (raw I/Q units; per-qubit median)', ['r1.sep_raw'], R)
    block("run 1's own left-over (rms of the nine MID-minus-pool numbers)", ['r1.remainder_rms'], R)
    three_clocks(R, meta, 'r1.tauF.shared', 'RUN 1')


def report_run2(R, meta):
    print('\n==== RUN 2 -- ONE EARLIER LOOK: START, LOOK, WAIT, LOOK (the clock)' + (DRY if meta['synthetic_iq'] else ''))
    block('look 1 (no wait, no earlier look of ours, after the machine\'s reset), each start: mean / variance / skew', [f'r2.L1.{s}.{x}' for s in STARTS for x in STATS], R)
    for s in STARTS:
        block(f'start {s}: F(1,w) = what look 2 reads; gap look 1 -> look 2 (mean, spread), each wait read against the other two',
              [f'r2.{s}.w{w}.{x}' for w in WAITS for x in ('F', 'gap_mean', 'gap_var', 'gap_mean-otherwaits')], R)
    block("the chip's own fading time from the gap (G(1-exp(-w/tau)); per start; shared; each start read against the other two)",
          [f'r2.tau.{k}' for k in STARTS + ['shared']] + [f'r2.tau.{k}-others' for k in STARTS], R)
    block('the fading time with ONE earlier look (level fit F(1,w) = G exp(-w/tau))', [f'r2.tauF.{k}' for k in STARTS + ['shared']], R)
    block('what the shared gap fit leaves, per start and wait', [f'r2.{s}.w{w}.resid' for s in STARTS for w in WAITS], R)
    block("run 2's own left-over (rms of the shared-fit residuals)", ['r2.remainder_rms'], R)
    three_clocks(R, meta, 'r2.tau.shared', 'RUN 2')


def report_run3(R, meta):
    print('\n==== RUN 3 -- TWO EARLIER LOOKS, MIRRORED TWINS: START, LOOK, WAIT a, LOOK, WAIT b, LOOK (the substrate)' + (DRY if meta['synthetic_iq'] else ''))
    print('  layout (wait in gap 1, wait in gap 2) per start: ' + ', '.join(f'({a},{b})' for a, b in LAYOUTS) + ' us; three twins x two orders; each wait sits in each gap 6 times over the 18 circuits')
    print(f'  ONLY the {MATCHED_TWIN[0]}+{MATCHED_TWIN[1]} twin has a third look at the long elapsed wait ({LONG} us), matched to runs 1 and 2; the twins {SHORT}+{LONG} and {MEDIUM}+{LONG} are read against their own mirror only.')
    block('look 1 (no wait, no earlier look of ours, after the machine\'s reset), each start', [f'r3.L1.{s}.{x}' for s in STARTS for x in STATS], R)
    for s in STARTS + ['ALL']:
        pre = f'r3.{s}.pool' if s != 'ALL' else 'r3.ALL'
        block(f'{s}{" (pooled over the six layouts)" if s != "ALL" else " (all eighteen circuits)"}: the three pairwise disagreement variances, then each look\'s own error solved from the other two (RAW, negatives kept)',
              [f'{pre}.{n}' for n in ('V12', 'V23', 'V13', 'hat1', 'hat2', 'hat3')], R)
    for s in STARTS + ['ALL']:
        pre = f'r3.{s}.pool' if s != 'ALL' else 'r3.ALL'
        block(f'THE REMAINDER, {s}: what each pair shares, read against the other two pairs (variance in OFF-to-ON separations squared)',
              [f'{pre}.{n}' for n in ('C12', 'C23', 'C13', 'rem12', 'rem23', 'rem13')], R)
    block("run 3's own left-over (rms of all rem values over the eighteen circuits; never zeroed)", ['r3.remainder_rms'], R)
    print('\n-- TURNING BACK TIME: the two orders of each twin, (a then b) minus (b then a), per start, all three twins side by side (value +- width)')
    print('   (both orders cover the same total time a+b. Look 2 sits after a different wait in each order, so its difference is large by construction; look 3 and the look1->look3 change are the like-for-like numbers.)')
    for st, label in (('L2mean', 'look 2 mean'), ('L3mean', 'look 3 mean'), ('g13', 'look1->look3 change'), ('V13', 'look1-vs-look3 disagreement variance')):
        print(f'  {label}:')
        print(f'    {"start":<6}' + ''.join(f'{"twin " + str(a) + "/" + str(b):>30}' for a, b in TWINS))
        for s in STARTS:
            cells = []
            for a, b in TWINS:
                r = R[f'r3.twin.{a}-{b}.{s}.{st}']; cells.append("CAN'T READ" if r.get('cant_read') else f'{g(r["value"])} +-{g(r["width"])}')
            print(f'    {s:<6}' + ''.join(f'{c:>30}' for c in cells))
    block('fading time from gap 1->2 and gap 2->3 across the waits (per start; shared)', [f'r3.tau12.{k}' for k in STARTS + ['shared']] + [f'r3.tau23.{k}' for k in STARTS + ['shared']], R)
    block('the fading time with TWO earlier looks (level fit F(2,w) = G exp(-w/tau))', [f'r3.tauF.{k}' for k in STARTS + ['shared']], R)
    block('RULER row (an algebraic identity, shown to prove the plumbing, not a finding): |gap12 + gap23 - gap13|', ['r3.closure_ruler'], R)
    three_clocks(R, meta, 'r3.tau12.shared', 'RUN 3 (gap 1->2)')


def report_return(R, metas):
    print('\n==== THE RETURN PASS (needs runs 1+2+3; contains Run 1 AND Run 3 data: marked so in the circularity audit)' + (DRY if metas[1]['synthetic_iq'] else ''))
    print("  Run 3 solves each look's own error from the other two (the three-cornered-hat solve). Here the first look's solved error is carried BACK onto Run 1's lone look, per start and per wait.")
    print("  All in ONE frame: RUN 3's own frame (look 1 of every OFF and ON circuit of Run 3); Run 1's looks are projected into it, so Run 1 and Run 3 data enter and Run 2's do not.")
    print("  measured = the spread (variance, in OFF-to-ON separations squared) of Run 1's lone look as measured;")
    print("  the part attributable to the look = Run 3's solved first-look error variance for that start (the same number at each wait: Run 3's first look has no wait before it; nothing is rescaled for the wait);")
    print("  what remains = measured minus that part. Run 1's lone look has " + ZERO_EARLIER + ', so the part carried back is that of a first look, the same kind.')
    for s_ in STARTS + ['ALL']:
        print(f'\n-- start {s_}' + (' (the mean over the three starts of each column)' if s_ == 'ALL' else ''))
        for w in WAITS:
            for k in ('measured', 'look', 'remains'): print(line(f'ret.{s_}.w{w}.{k}', R.get(f'ret.{s_}.w{w}.{k}')))
    print('\n-- THE REMAINDER (after the return pass; raw, negatives kept, never zeroed)')
    for s_ in STARTS + ['ALL']:
        print('  ' + '   '.join(f"w{w}: {line(f'ret.{s_}.w{w}.remains', R.get(f'ret.{s_}.w{w}.remains')).split(None, 1)[1].strip()}" for w in WAITS) + f'    <- start {s_}')
    print(line('ret.remainder_rms', R.get('ret.remainder_rms')))


def report_comb(R, metas):
    print('\n==== THE SELF-EFFECT EQUATION (needs runs 1+2+3), raw I/Q in ONE frame (look 1 of runs 2+3 pooled)' + (DRY if metas[1]['synthetic_iq'] else ''))
    print('  F(n, wait, start) = what the look after a wait reads when n looks came before: n=0 run 1, n=1 run 2 look 2, n=2 run 3 look 3.')
    print("  first look's effect = F(1) - F(0); second look's effect = F(2) - F(1); the hunter's number = second effect / first effect.")
    print(f'\n  ---- A. THE HUNTER AT MATCHED ELAPSED TIME (the number to use). Waits are short {SHORT} + medium {MEDIUM} = long {LONG} us (on the 16-dt grid, realized exactly equal).')
    print(f'       F(0,long) = run 1;  F(1,long) = run 2;  F(2,long) = run 3 via the {MATCHED_TWIN[0]}+{MATCHED_TWIN[1]} twin, BOTH orders shown and their mean: its third look sits after {SHORT}+{MEDIUM} = {LONG} us of waiting, the same')
    print('       wait the one look of run 1 and the second look of run 2 sit after. (Remaining difference, not corrected: each earlier look also takes its own readout time, about 2.2 us.)')
    print(f'       ONLY the {MATCHED_TWIN[0]}+{MATCHED_TWIN[1]} twin is matched in elapsed time to runs 1 and 2. The other two twins ({SHORT}+{LONG} and {MEDIUM}+{LONG}) are read against their own mirror only (see TURNING BACK TIME in run 3).')
    for s in STARTS:
        print(f'  start {s}:')
        for nm in (f'c.F.n0.{s}.w{LONG}', f'c.F.n1.{s}.w{LONG}', f'c.Fm.n2.{s}.o{MATCHED_TWIN[0]}-{MATCHED_TWIN[1]}', f'c.Fm.n2.{s}.o{MATCHED_TWIN[1]}-{MATCHED_TWIN[0]}', f'c.Fm.n2.{s}',
                   f'c.eff1.{s}.w{LONG}', f'c.effm2.{s}', f'c.hunterm.{s}.o{MATCHED_TWIN[0]}-{MATCHED_TWIN[1]}', f'c.hunterm.{s}.o{MATCHED_TWIN[1]}-{MATCHED_TWIN[0]}', f'c.hunterm.{s}'):
            print('  ' + line(nm, R.get(nm)))
    print(f'\n  ---- B. UNMATCHED, POOLED (printed beside A, NOT the number to use): F(2) pooled over every layout whose LAST wait is w. This MIXES "one more look" WITH "more time passed":')
    print('       F(0) and F(1) sit after ONE wait w; F(2) sits after an earlier wait a PLUS w, so the second effect also carries the fading over a. Computed as the spec wrote it; the same numbers')
    print('       split by the earlier wait a follow each row; the n=2 clock is fitted against total elapsed time a+b (equal for both orders of a twin).')
    for s in STARTS:
        print(f'\n-- start {s}')
        for w in WAITS:
            for nm in (f'c.F.n0.{s}.w{w}', f'c.F.n1.{s}.w{w}', f'c.F.n2.{s}.w{w}', f'c.eff1.{s}.w{w}', f'c.eff2.{s}.w{w}', f'c.hunter.{s}.w{w}'): print(line(nm, R.get(nm)))
            for a in WAITS:
                for nm in (f'c.F.n2.{s}.w{w}.a{a}', f'c.hunter.{s}.w{w}.a{a}'):
                    if nm in R: print('    split by the earlier wait: ' + line(nm, R[nm]).strip())
            print('')
    print('-- F(2) against TOTAL elapsed time a+b (both orders of each twin averaged; this is the n=2 clock axis)')
    for s in STARTS:
        for (a, b) in TWINS: print(line(f'c.F.n2T.{s}.T{a}+{b}', R.get(f'c.F.n2T.{s}.T{a}+{b}')))
    print("-- THE THREE CLOCKS: fading time with 0, 1, 2 earlier looks of ours (0 = after the machine's reset only) (level fit G exp(-w/tau); per start and shared); log10 of each pair, the third beside it")
    if metas[1].get('maker_clock'):
        t1, n1, why1 = maker_values(metas[1]['maker_clock'], 'T1_us')
        print(f'  [maker T1 median {g(np.median(t1))} us over {len(t1)} of {n1} qubits, shown for scale only]' if len(t1) else f"  [maker T1: CAN'T READ: 0 of {n1} qubits have a usable value ({why1})]")
    else:
        print('  [BLANK chip: no maker clock was read]')
    for k in STARTS + ['shared']:
        print(f'  {k}:')
        for n in (0, 1, 2): print('    ' + line(f'c.tauF.n{n}.{k}', R[f'c.tauF.n{n}.{k}']).strip())
        for (i, j), third in (((0, 1), 2), ((1, 2), 0), ((0, 2), 1)):
            r = R[f'c.tauratio.n{i}-n{j}.{k}']; t = R[f'c.tauF.n{third}.{k}']
            tv = "CAN'T READ" if t.get('cant_read') else f'{g(t["value"])} +-{g(t["width"])} us'
            body = f"CAN'T READ ({r['cant_read']})" if r.get('cant_read') else f'{g(r["value"])} +-{g(r["width"])}'
            print(f'    log10[tau(n={j}) / tau(n={i})] = {body:<30} | third beside: tau(n={third}) = {tv}')


def drift_rows(RS):
    """Look 1 across runs. Run 1's look 1 sits after the SHORTEST wait (it has no wait-free look); runs 2 and 3's look 1 has no wait. So run 1's number
    carries the fading over that wait: stated, not corrected. Each run read against the mean of the other two. Needs all three."""
    def src(r, s, x): return f'r1.{s}.w{min(WAITS)}.{x}' if r == 1 else f'r{r}.L1.{s}.{x}'
    def mk(rows, i):
        if any(x is None or x.get('cant_read') for x in rows): return {'value': np.nan, 'width': np.nan, 'cant_read': "one of the three runs' look-1 number is CAN'T READ"}
        o = [rows[j] for j in range(3) if j != i]
        return {'value': rows[i]['value'] - (o[0]['value'] + o[1]['value']) / 2, 'width': float(np.sqrt(rows[i]['width'] ** 2 + (o[0]['width'] ** 2 + o[1]['width'] ** 2) / 4))}
    out = {}
    for s in STARTS:
        for x in STATS:
            rows = [RS[r][src(r, s, x)] for r in (1, 2, 3)]
            for i, r in enumerate((1, 2, 3)):
                row = mk(rows, i); row.update({'width_pct': np.nan, 'group_spread': np.nan, 'n_refit_failed': 0, 'boot': 0, 'shots': rows[0]['shots']})
                row['groups'] = [mk([rr['groups'][gq] for rr in rows], i) for gq in range(3)]
                out[f'drift.L1.{s}.{x}.run{r}'] = row
    return out


def side_by_side(RS, metas, D):
    from datetime import datetime
    print(f'\n==== ALL THREE RUNS SIDE BY SIDE -- the first look. Run 1: after the shortest wait ({min(WAITS)} us); runs 2, 3: no wait. DRIFT = each run read against the mean of the other two.')
    print('     NOTE: run 1 has no look without a wait, so its column also carries the fading over the shortest wait. Not corrected; stated.')
    print(f'  {"quantity":<24}' + ''.join(f'{"run" + str(r):>27}' for r in (1, 2, 3)) + f'{"drift run1":>27}{"drift run2":>27}{"drift run3":>27}')
    for s in STARTS:
        for x in STATS:
            cells = []
            for r in (1, 2, 3):
                row = RS[r][f'r1.{s}.w{min(WAITS)}.{x}' if r == 1 else f'r{r}.L1.{s}.{x}']; cells.append("CAN'T READ" if row.get('cant_read') else f'{g(row["value"])} +-{g(row["width"])}')
            for r in (1, 2, 3):
                row = D[f'drift.L1.{s}.{x}.run{r}']; cells.append("CAN'T READ" if row.get('cant_read') else f'{g(row["value"])} +-{g(row["width"])}')
            print(f'  {s + "." + x:<24}' + ''.join(f'{c:>27}' for c in cells))
    print("  time between runs (measured, not removed). end = the job's OWN metadata 'finished' stamp; start = the job's own 'running' stamp when the metadata has one, else the client submit stamp (labelled):")
    for a_, b_ in ((1, 2), (2, 3)):
        ea, sb = metas[a_].get('end_time'), (metas[b_].get('job_running_at') or metas[b_]['start_time'])
        lab = 'job running stamp' if metas[b_].get('job_running_at') else 'client submit stamp (the job metadata gave no running stamp)'
        if not ea: print(f"    end of run {a_} -> start of run {b_}: CAN'T READ ({metas[a_].get('end_time_source')})"); continue
        print(f'    end of run {a_} -> start of run {b_}: {(datetime.fromisoformat(str(sb)) - datetime.fromisoformat(str(ea))).total_seconds():.1f} s   [end: {metas[a_].get("end_time_source")}; start: {lab}]' + ('   [dry-run stamps: local simulation, not hardware time]' if metas[a_]['synthetic_iq'] else ''))
    for r in (1, 2, 3): print(f'    run {r}: submit stamp {metas[r]["start_time"]}  end {metas[r].get("end_time") or "CAN\'T READ"}  calibration stamp {metas[r]["calibration_timestamp"]}')


def remainder_line(RS, present):
    names = {1: 'r1.remainder_rms', 2: 'r2.remainder_rms', 3: 'r3.remainder_rms'}
    parts, readable = [], []
    for r in (1, 2, 3):
        if r not in present: parts.append(f"run{r} = CAN'T READ (run not in this mode)"); continue
        row = RS[r][names[r]]
        if row.get('cant_read'): parts.append(f"run{r} = CAN'T READ ({row['cant_read']})"); continue
        readable.append(r)
        parts.append(f'run{r} = {g(row["value"])} +-{g(row["width"])} ({g(row["value"] / row["width"]) if row["width"] else "nan"} widths)')
    rp = RS.get('ret', {}).get('ret.remainder_rms') if isinstance(RS.get('ret'), dict) else None
    if rp is not None: parts.append(f"THE RETURN PASS (runs 1 and 3, Run 3's frame) = " + ("CAN'T READ (" + rp['cant_read'] + ')' if rp.get('cant_read') else f'{g(rp["value"])} +-{g(rp["width"])} ({g(rp["value"] / rp["width"]) if rp["width"] else "nan"} widths)'))
    return ("THE REMAINDER (never zeroed; each run's own left-over, rms, in that run's own units): " + '; '.join(parts) +
            f'. Runs carrying a readable remainder: {readable if readable else "none"}. What it means is left to the owner.')


# ------------------------------------------------------------------------------------------------ circularity audit (HEADER ONLY: no number is read)
def template_names():
    p = os.path.join(HERE, 'predictions_template.json')
    try: return list(json.load(open(p))['predictions'])
    except Exception: return sealable_names()


def print_audit(hdr):
    names = template_names()
    fams = ['r1', 'r2', 'r3', 'c', 'drift']
    print('==== CIRCULARITY AUDIT (printed first, every report)')
    print('  RULE: a prediction is scored only if NONE of the data it was written from sits inside the measured quantity. If they overlap the row is')
    print('  BOX ON BOX and is NOT scored. "Data inside" = the runs whose raw looks enter the quantity (own-run quantities use their own frame; every')
    print('  combined c.* quantity uses a frame from look 1 of runs 2+3, so it contains runs 2 and 3; see data_of()). This audit reads only written_at / data_seen.')
    print(f'  Quantities in predictions_template.json: {len(names)}.  Scoreable count by the stage a prediction is sealed at (seen = what it was written from):')
    print(f'    {"stage (seen)":<24}' + ''.join(f'{f:>10}' for f in fams) + f'{"TOTAL":>10}   own-run quantities')
    for N in (1, 2, 3):
        seen = DEFAULT_SEEN[N]; cells = []; tot = 0
        for f in fams:
            fn_ = [n for n in names if family(n) == f]; ok = sum(1 for n in fn_ if not overlap(n, seen)); cells.append(f'{ok}/{len(fn_)}'); tot += ok
        own = [n for n in names if family(n) == f'r{N}']
        print(f'    {"run " + str(N) + " (" + seen + ")":<24}' + ''.join(f'{c:>10}' for c in cells) + f'{str(tot) + "/" + str(len(names)):>10}   {sum(1 for n in own if not overlap(n, seen))}/{len(own)}')
    print("  THE RETURN PASS rows (ret.*; Run 1's lone look carried back with Run 3's solve): data inside = runs [1, 3] (both in Run 3's own frame; no Run 2 data). A prediction written from")
    print(f"    nothing or the maker's numbers shares no run with them: scoreable. Written from run 1 (shared: {overlap('ret.ALL.w60.measured', 'run1')}) or from runs 1+2 (shared: {overlap('ret.ALL.w60.measured', 'runs1+2')}): BOX ON BOX, not scored.")
    if hdr is None:
        print('  (no prediction file given: no per-row lines)'); return
    print(f"  PREDICTION FILE: for run {hdr['run']}, written_at {hdr['written_at']}. Filled entries (written_at | written from | data inside the quantity | status):")
    nb = nok = 0
    for n, e in hdr['entries'].items():
        if not e['filled']: continue
        if e['data_seen'] not in SEEN_LEVELS: print(f"    {n:<34} data_seen={e['data_seen']!r} unknown: NOT scored"); continue
        ov = overlap(n, e['data_seen'])
        status = f'BOX ON BOX (shared: runs {ov}) -- not scored' if ov else 'scoreable'
        nb += bool(ov); nok += not ov
        print(f"    {n:<34} {str(e['written_at']):<26} from {e['data_seen']:<8} inside runs {sorted(data_of(n))}  {status}")
    print(f'  filled entries: {nb + nok}; scoreable {nok}; BOX ON BOX {nb}')


# ------------------------------------------------------------------------------------------------ scoring (LAST; the only place a predicted number is read)
def maker_number_from_freeze(name, fz):
    """THE MAKER'S box: the published T1 of the chip's nine qubits (median), the sd across them as its width, read at FREEZE time. Fading-time quantities
    only (not OFF: nothing to fade). No other quantity has a published number: then the maker made no prediction for it."""
    last = name.split('.')[-1]
    if '.tau' in name and 'tauratio' not in name and last in ('MID', 'ON', 'shared'):
        t1, n1, why = maker_values(fz['maker_calibration'], 'T1_us')
        if len(t1) >= 2: return float(np.median(t1)), float(np.std(t1, ddof=1)), (f'{len(t1)} of {n1} qubits' if len(t1) < n1 else None)
        return None, None, f"CAN'T READ: {len(t1)} of {n1} qubits have a published T1 (need 2); reasons: {why or 'none given'}"      # FIX K: never silently unscored
    return None


def _load_prediction_numbers(path, expected_sha):
    """FIX C: the file is read ONCE as bytes, its sha256 is compared with the hash recorded at fire, and the numbers are parsed from those same bytes."""
    raw = open(path, 'rb').read()
    import hashlib
    if hashlib.sha256(raw).hexdigest() != expected_sha: return None
    j = json.loads(raw)
    return {n: {'predicted': e.get('predicted'), 'width': e.get('width'), 'written_at': e.get('written_at'), 'data_seen': e.get('data_seen')} for n, e in j['predictions'].items()}


def _miss(row, p, w):
    if row.get('cant_read'): return "CAN'T READ"
    if p is None or w is None: return None
    if w <= 0: return "CAN'T READ (prediction width <= 0)"
    return abs(row['value'] - p) / w


def _check_freeze(chip, N, meta, box):
    fp = freeze_path(N, chip)
    if not os.path.exists(fp): return None, f'no freeze file for run {N} on {chip} ({os.path.basename(fp)}). A prediction without a freeze cannot be scored.'
    fz = json.load(open(fp)); cur = recompute_hash_from_freeze(fz, importlib.import_module(f'run{N}').specs())
    if not (fz['combined_sha256'] == meta.get('code_hash') == cur):
        return None, f"hash on file ({fz['combined_sha256'][:12]}) vs hash of the code that produced the results ({str(meta.get('code_hash'))[:12]}) vs the code on disk now ({cur[:12]}) do not all match."
    if box != 'blank' and fz.get('groups') != meta.get('groups_of_three'): return None, 'the qubit groups in the freeze file differ from the groups the run used'
    return fz, None


def score_ours(chip, path, hdr, flat, metas, data_dir, mode):
    """OURS: our sealed numbers. miss = |measured - predicted| / predicted width, on the whole chip."""
    print(f'\n==== PREDICTION SCORING, OURS ({chip}) -- computed LAST; feeds nothing above')
    N = hdr['run']
    if N not in metas: print(f'  REFUSED: the prediction file is for run {N}, which is not in this mode'); return 3
    fz, bad = _check_freeze(chip, N, metas[N], 'ours')
    if bad: print('  REFUSED: ' + bad); return 3
    meta = metas[N]
    try:
        frozen = parse_iso(fz['frozen_at'])
        if not hdr['written_at'] or parse_iso(hdr['written_at']) < frozen: print(f"  REFUSED: prediction _written_at {hdr['written_at']} is earlier than the freeze {fz['frozen_at']} (or missing)."); return 3
        if parse_iso(hdr['written_at']) > parse_iso(meta['start_time']): print(f"  REFUSED: prediction _written_at {hdr['written_at']} is later than the start of run {N} ({meta['start_time']})."); return 3
    except Exception as ex:
        print(f'  REFUSED: could not read timestamps ({ex})'); return 3
    exp = meta.get('prediction_sha256')
    if not exp: print(f'  REFUSED: run {N} recorded no prediction sha256 at fire (no prediction file was given then): nothing to score.'); return 3
    nums = _load_prediction_numbers(path, exp)                  # <-- the first and only place our numbers are read
    if nums is None:
        print(f"  REFUSED: the sha256 of {os.path.basename(path)} is not the one recorded at fire ({exp[:16]}...): the prediction file was changed after the run was fired. Nothing scored."); return 3
    print(f"  run {N}: freeze ok ({fz['frozen_at']}); code hash matches; prediction file sha256 equals the one recorded at fire ({exp[:16]}...); prediction written {hdr['written_at']}, run started {meta['start_time']}.  miss = |measured - predicted| / predicted width.")
    out = {}; nscored = 0
    for n, p in nums.items():
        if p['predicted'] is None or p['width'] is None: continue
        row = flat.get(n)
        if row is None: print(f'  {n:<36} (not measured in this mode)'); continue
        wa = p['written_at']; seen = p['data_seen']
        if n in IDENTITY_NAMES: print(f'  {n:<36} ruler identity (0 / 1 by construction): never scored'); continue
        try:
            bad = (seen not in ALLOWED_SEEN[N]) or (not wa) or parse_iso(wa) < frozen or parse_iso(wa) > parse_iso(meta['start_time'])        # FIX C: written_at inside [freeze, run start]
        except Exception: bad = True
        if bad: print(f'  {n:<36} entry written_at / data_seen missing, earlier than the freeze, later than the start of run {N}, or not allowed: not scored'); continue
        ov = overlap(n, seen)
        if ov: print(f'  {n:<36} BOX ON BOX (written from {seen}; the quantity contains run(s) {ov}): NOT scored'); continue
        m = _miss(row, p['predicted'], p['width']); val = "CAN'T READ" if row.get('cant_read') else f'{g(row["value"])} +-{g(row["width"])}'
        print(f'  {n:<36} measured {val}  pred {g(p["predicted"])} +-{g(p["width"])}  MISS {m if isinstance(m, str) else g(m)}'); out[n] = {'miss': m}; nscored += 1
    sp = os.path.join(data_dir, f'scores_ours_run{N}_{mode.replace("+", "_")}.json')
    json.dump(out, open(sp, 'w'), indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else str(x))
    print(f'  entries scored: {nscored}  (saved {sp})'); return 0


def score_maker(chip, flat, metas, data_dir, mode):
    """MAKER: the maker's published calibration read at freeze time is the only prediction (fading-time quantities)."""
    print(f'\n==== PREDICTION SCORING, MAKER ({chip}) -- the published calibration read at freeze time is the only prediction; no numbers of ours')
    nmax = max(metas); out = {}; fzs = {}
    for n, row in flat.items():
        fam = n.split('.')[0]; N = int(fam[1]) if re.match(r'r\d$', fam) else nmax
        if N not in metas: continue
        if N not in fzs:
            fzs[N] = _check_freeze(chip, N, metas[N], 'maker')
            if fzs[N][1]: print(f'  run {N}: REFUSED: {fzs[N][1]}')
        fz = fzs[N][0]
        if fz is None: continue
        mk = maker_number_from_freeze(n, fz)
        if mk is None: continue
        val = "CAN'T READ" if row.get('cant_read') else f'{g(row["value"])} +-{g(row["width"])}'
        if mk[0] is None:
            print(f'  {n:<36} measured {val}  maker T1 {mk[2]}  MISS CAN\'T READ'); out[n] = {'miss': "CAN'T READ", 'why': mk[2]}; continue
        m = _miss(row, mk[0], mk[1])
        print(f'  {n:<36} measured {val}  maker T1 {g(mk[0])} +-{g(mk[1])}' + (f' [{mk[2]} usable]' if mk[2] else '') + f' (cal {fz["maker_calibration"]["calibration_timestamp"]}, read once at freeze)  MISS {m if isinstance(m, str) else g(m)}'); out[n] = {'miss': m}
    sp = os.path.join(data_dir, f'scores_maker_{mode.replace("+", "_")}.json')
    json.dump(out, open(sp, 'w'), indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else str(x))
    print(f'  entries scored: {len(out)}  (saved {sp})'); return 0


# ------------------------------------------------------------------------------------------------ main
def ledger_check(metas, tracked_by_run):
    print('\n==== THE LOOK LEDGER (every circuit in each run; no calibration or test circuits; every look read)')
    for r, meta in metas.items():
        led = meta['ledger']; want = {(r, c['key'], k) for c in led['circuits'] for k in range(c['n_looks'])}
        got = {t for t in tracked_by_run if t[0] == r}
        print(f"  run {r}: {led['n_circuits']} circuits, {led['n_looks_total']} looks, looks per circuit {led['looks_per_circuit']}, calibration/test circuits {led['calibration_or_test_circuits']}; looks read by this analysis: {len(got & want)}; "
              f"in the analysis but not in the ledger: {len(got - want)}; in the ledger but never read: {len(want - got)}" + (f" {sorted(want - got)[:4]}" if want - got else ''))
    print(f"  THE MACHINE'S RESET (init_qubits), counted by the ledger self-check on every circuit of every run: " + MACHINE_RESET_WHAT)
    for r, meta in metas.items():
        led = meta['ledger']
        print(f"    run {r}: {led['n_machine_resets_per_shot']} reset entries (one per circuit, {led['circuits'][0]['machine_reset']['when']}); {led['machine_reset_events_total']} reset events over the run's shots; "
              f"our looks: {led['n_looks_total']}; sampler options pinned: " + ('; '.join(f'{k}={v}' for k, v in (meta.get('sampler_options_pinned') or {}).items()) or 'not recorded'))
        if meta.get('parser_sha256'): print(f"    run {r}: raw payload {meta.get('payload_file')} (sha256 {str(meta.get('payload_sha256'))[:16]}...), parsed by {meta.get('parser_file')} sha256 {meta['parser_sha256'][:16]}... (the parser is outside the freeze)")
        if led.get('reads_at_fire'):
            print(f"    run {r}: reads made by the fire itself (chip reads count as looks at that chip):")
            for e in led['reads_at_fire']: print(f"      {str(e.get('at'))[11:19]}  {e['what']}" + (f"  [{e['request']}]" if e.get('request') else ''))
    pre = next(iter(metas.values()))['ledger'].get('looks_taken_before_run_1')
    if pre:
        print(f"  {pre['title']} ({len(pre['entries'])} entries; none touched a bit: {pre['none_touched_a_bit']}):")
        for e in pre['entries']: print(f"    {e['date']} {e.get('time_of_day', '')}  {e['what']}")


def analyse_chip(chip_dir, nruns, boot, verbose=True):
    """Everything measured for ONE chip. No prediction is read here."""
    import contextlib, io
    DS, metas = {}, {}
    for r in range(1, nruns + 1): DS[r], metas[r] = load(chip_dir, r)
    if len({json.dumps(m['groups_of_three']) for m in metas.values()}) != 1: raise Refused('the qubit groups differ between runs')
    sink = contextlib.nullcontext() if verbose else contextlib.redirect_stdout(io.StringIO())
    fns = {1: q_run1, 2: q_run2, 3: q_run3}; reps = {1: report_run1, 2: report_run2, 3: report_run3}
    RS, tracked, carry, qrows = {}, set(), {}, {}
    with sink:
        for r in range(1, nruns + 1):
            RS[r], t = quantify(lambda DS_, MS_, rng, _r=r: fns[_r]({_r: DS_[_r]}, {_r: MS_[_r]}, rng), {r: DS[r]}, {r: metas[r]}, boot); tracked |= t
            reps[r](RS[r], metas[r])
            carry.update(carry_rows(DS[r], metas[r], r, boot))
            qrows[r] = qubit_rows(DS[r], metas[r], r)
            print_carry({k: v for k, v in carry.items() if k.startswith(f'carry.r{r}.')}, r); print_qubits(qrows[r], r)
        flat = {k: v for r in RS for k, v in RS[r].items()}; flat.update(carry)
        if nruns == 3:
            RC, t = quantify(q_comb, DS, metas, boot); tracked |= t
            report_comb(RC, metas); flat.update(RC)
            RR, t = quantify(q_return, DS, metas, boot); tracked |= t
            report_return(RR, metas); flat.update(RR); RS['ret'] = RR
            Dr = drift_rows(RS); flat.update(Dr); side_by_side(RS, metas, Dr)
        else:
            print(f"\n==== SELF-EFFECT EQUATION and DRIFT BETWEEN RUNS: CAN'T READ in this mode (they need all three runs; only {nruns} present)")
        ledger_check(metas, tracked)
        print('\n' + remainder_line(RS, set(range(1, nruns + 1))))
    return {'flat': flat, 'RS': RS, 'metas': metas, 'tracked': tracked, 'carry': carry, 'qrows': qrows}


def _nine_landed(data_root):
    a = chip_assignment(); miss = []
    for b in ('ours', 'maker', 'blank'):
        for r in (1, 2, 3):
            mp = os.path.join(data_root, a[b], f'run{r}_meta.json')          # the small meta file only: no outcome data is opened
            try: ok = json.load(open(mp)).get('complete') is True
            except Exception: ok = False
            if not ok: miss.append((a[b], r))
    return miss


def side_by_side_chips(F, labels):
    """Three chips side by side for every reading, each chip read against the other two. No verdict word."""
    fam_order = {'r1': 0, 'r2': 1, 'r3': 2, 'c': 3, 'drift': 4, 'carry': 5}
    names = sorted({n for b in labels for n in F[b]}, key=lambda n: (fam_order.get(family(n) if not n.startswith('carry') else 'carry', 9), n))
    def cell(row): return "CAN'T READ" if row is None or row.get('cant_read') or not np.isfinite(row['value']) else f'{g(row["value"])} +-{g(row["width"])}'
    print('\n==== THE THREE CHIPS SIDE BY SIDE (OURS / MAKER / BLANK). Every reading: each chip, then each chip read against the mean of the other two (value +- widths combined).')
    print(f'  {"quantity":<38}' + ''.join(f'{b.upper():>22}' for b in labels) + ''.join(f'{b.upper() + " vs others":>26}' for b in labels))
    rows = {}
    for n in names:
        rr = [F[b].get(n) for b in labels]; cells = [cell(r) for r in rr]; vs = []
        for i, b in enumerate(labels):
            o = [rr[j] for j in range(3) if j != i]
            if any(x is None or x.get('cant_read') or not np.isfinite(x['value']) for x in rr):
                vs.append("CAN'T READ"); continue
            v = rr[i]['value'] - (o[0]['value'] + o[1]['value']) / 2; w = float(np.sqrt(rr[i]['width'] ** 2 + (o[0]['width'] ** 2 + o[1]['width'] ** 2) / 4))
            vs.append(f'{g(v)} +-{g(w)}'); rows.setdefault(n, {})[b] = {'vs_others': v, 'width': w}
        print(f'  {n:<38}' + ''.join(f'{c:>22}' for c in cells) + ''.join(f'{c:>26}' for c in vs))
    return rows


def main():
    import contextlib
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', nargs='?', choices=['run1', 'run1+2', 'run1+2+3', 'all'])
    ap.add_argument('--data-dir', default=os.path.join(HERE, 'data', 'fire'), help='ROOT folder holding one sub-folder per chip. Default is the REAL results folder (data/fire), never the dry-run folder: pass --data-dir data/dryrun for synthetic data')
    ap.add_argument('--chip', default=CHIP_OURS)
    ap.add_argument('--predictions', nargs='*', default=None, help='OURS only. One file per run in mode all.')
    ap.add_argument('--make-template', default=None)
    ap.add_argument('--boot', type=int, default=BOOT)
    a = ap.parse_args()
    if a.make_template: return make_template(a.make_template)
    if not a.mode: ap.print_help(); return 0
    asg = chip_assignment()
    try:
        if a.mode == 'all':
            miss = _nine_landed(a.data_dir)
            if miss: raise Refused(f'mode all needs all nine jobs landed (3 runs x 3 chips); missing or not complete: {miss}. Nothing was opened.')
            labels = ['ours', 'maker', 'blank']; R = {}
            hdrs = [load_header(p) for p in (a.predictions or [])]
            print_audit(hdrs[0] if hdrs else None)
            for h in hdrs[1:]: print(f"  (further prediction file: run {h['run']}, written {h['written_at']})")
            for b in labels:
                R[b] = analyse_chip(os.path.join(a.data_dir, asg[b]), 3, a.boot, verbose=False)
                for r, m in R[b]['metas'].items():
                    if m['synthetic_iq']: print(f'{b.upper()} {asg[b]} run {r}: DRY-RUN DATA, I/Q IS SYNTHETIC (fabricated). Code path only, not the physics.')
            print('\nchips: ' + ', '.join(f'{b.upper()} = {asg[b]}' for b in labels) + f'; left alone, never touched: {asg["left_alone"]}')
            F = {b: R[b]['flat'] for b in labels}
            rows = side_by_side_chips(F, labels)
            for b in labels:
                print(f'\n==== {b.upper()} ({asg[b]}): the drawn qubits (a dead or noisy qubit is a row, not a pre-check)')
                for r in (1, 2, 3): print_qubits(R[b]['qrows'][r], r)
                ledger_check(R[b]['metas'], R[b]['tracked']); print('\n' + remainder_line(R[b]['RS'], {1, 2, 3}))
            out = os.path.join(a.data_dir, 'analysis_all.json')
            json.dump({'chips': {b: asg[b] for b in labels}, 'rows': {b: F[b] for b in labels}, 'vs_others': rows, 'qubits': {b: R[b]['qrows'] for b in labels}}, open(out, 'w'), indent=1,
                      default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else str(x))
            print(f'(full rows saved: {out})')
            # LAST: miss columns (OURS and MAKER only; BLANK has none)
            rc = 0
            for p, h in zip(a.predictions or [], hdrs): rc = max(rc, score_ours(asg['ours'], p, h, F['ours'], R['ours']['metas'], os.path.join(a.data_dir, asg['ours']), 'all'))
            rc = max(rc, score_maker(asg['maker'], F['maker'], R['maker']['metas'], os.path.join(a.data_dir, asg['maker']), 'all'))
            print('\nBLANK: no prediction and no miss column, by design.')
            return rc
        chip = a.chip; box = box_of_chip(chip)
        if box in (None, 'left_alone'): raise Refused(f'{chip} is not one of the three chips in play (the left-alone chip is never touched)')
        if box == 'blank':
            miss = _nine_landed(a.data_dir)
            if miss: raise Refused(f'{chip} is the BLANK chip: its results are NOT opened until all nine jobs have landed (missing: {miss}). Use mode all after that.')
        nruns = {'run1': 1, 'run1+2': 2, 'run1+2+3': 3}[a.mode]; chip_dir = os.path.join(a.data_dir, chip)
        hdr = load_header(a.predictions[0]) if (a.predictions and box == 'ours') else None
        if a.predictions and box != 'ours': raise Refused(f'a {box.upper()} chip takes no prediction file of ours')
        print(f'==== CHIP {chip}  BOX {box.upper()}')
        # (1) completeness is checked by load() inside analyse_chip before any output
        for r in range(1, nruns + 1):
            mp = os.path.join(chip_dir, f'run{r}_meta.json')
            if not os.path.exists(mp) or json.load(open(mp)).get('complete') is not True: raise Refused(f'run {r} on {chip}: not complete. Nothing was opened.')
        print_audit(hdr)
        res = analyse_chip(chip_dir, nruns, a.boot, verbose=True)
        for r, m in res['metas'].items():
            if m['synthetic_iq']: print(f'run {r}: DRY-RUN DATA, I/Q IS SYNTHETIC (fabricated). This report proves the code path only, not the physics.')
        out = os.path.join(chip_dir, f'analysis_{a.mode.replace("+", "_")}.json')
        json.dump(res['flat'], open(out, 'w'), indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else str(x))
        print(f'(full rows saved: {out})')
        if box == 'ours' and hdr: return score_ours(chip, a.predictions[0], hdr, res['flat'], res['metas'], chip_dir, a.mode)
        if box == 'maker': return score_maker(chip, res['flat'], res['metas'], chip_dir, a.mode)
        return 0
    except Refused as e:
        print(f'REFUSED: {e}'); return 2


def load_header(path):
    from common import load_prediction_header
    return load_prediction_header(path)


if __name__ == '__main__':
    sys.exit(main())
