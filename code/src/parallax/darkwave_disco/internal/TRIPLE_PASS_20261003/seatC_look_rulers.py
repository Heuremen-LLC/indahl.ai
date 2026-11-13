#!/usr/bin/env python3
"""look_rulers.py -- TRIPLE PASS seat C. Read-only. One readout ("look") on ibm_pittsburgh timed by its three clocks, with the rulers moved.
WITNESS (look-time runs 101-103): a spectator's phase over the block of 3 or 9 looks, mapped to LAID time through its own phase curve over the
  LAID delay arms. Claimed ruler: quadratic through the 30- and 60-us arms (code/readclose.py look_stats), median over spectators.
  Moved: linear through 30 only; linear through 60 only; least-squares line through 30/60/120; least-squares quadratic through 30/60/120;
  mean over spectators instead of median. Also the hand kept (0.921 / 0.826 / 0.760) as median vs mean, and the turn per us (3.144) as
  median |angle|/30 (claimed) vs signed median, vs the 60- and 120-us arms.
OWN (hold runs 71-73; give-back runs 111-113): the extra time a look adds to a |1>-prepared qubit's decay.
  Claimed: hold -- 300 x ln(left)/ln(left, nothing done) per qubit, median over qubits ('bit by bit'); give-back -- tau x ln(none/end),
  tau = -300/ln(none) per qubit (one exponential, clip 0.02-0.98), mean over readable qubits.
  Moved: mean over readable qubits; median qubit's levels; P300 in (0.1, 0.9); the long clock (the slow part of run 121's two-part shape,
  fast fraction 0.020: tau_long = 300 / (-ln(left_nothing) - ln(1/(1-0.02)))) instead of the one-exponential tau.
Writes only seatC_look_rulers.txt beside this script."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
RO = json.load(open('/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/reads/looktime_roles.json'))
OUT = os.path.join(HERE, 'seatC_look_rulers.txt'); NB = 60; F_FAST = 0.020


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(r):
    m = json.load(open(os.path.join(D, f'run{r}_meta.json'))); assert m['complete'] is True
    z = np.load(os.path.join(D, f'run{r}_results.npz')); return m, {k: np.asarray(z[k]).astype(complex) for k in z.files}


def resample(A, rng):
    out, idx = {}, {}
    for k, v in A.items():
        b = k.split('__')[0]
        if b not in idx: idx[b] = rng.integers(0, v.shape[0], v.shape[0])
        out[k] = v[idx[b]]
    return out


def frame(A, f0, f1):
    c0 = A[f0].mean(0); d = A[f1].mean(0) - c0
    return (lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2), np.abs(d) / np.sqrt((np.abs(A[f0] - c0) ** 2).mean(0) / 2)


# ------------------------------------------------------------------------------------------------ WITNESS
def look_stats(A):
    al, sep = frame(A, 'F0__L1', 'F1__L1'); WOF = {int(k): v for k, v in RO['witness_of'].items()}
    fin = lambda key: [k for k in A if k.startswith(key + '__')][-1]
    Pm = {key: al(A[fin(key)]) for key in {k.split('__')[0] for k in A}}
    H = {a: (2 * Pm[f'{a}|X'].mean(0) - 1) - 1j * (2 * Pm[f'{a}|Y'].mean(0) - 1) for a in ('T0', 'T30', 'T60', 'T120', 'K3', 'K9')}
    W = [w for w in sorted(WOF) if abs(H['T0'][w]) > 0.15 and sep[w] > 3 and sep[WOF[w]] > 3]
    ang = {a: np.angle(H[a] / H['T0']) for a in ('T30', 'T60', 'T120', 'K3', 'K9')}
    uw = np.unwrap(np.vstack([np.zeros_like(ang['T30']), ang['T30'], ang['T60'], ang['T120']]), axis=0)
    ang['T30'], ang['T60'], ang['T120'] = uw[1], uw[2], uw[3]
    out = {}
    per = {r: {3: [], 9: []} for r in ('quad 30/60 (claimed)', 'line 30', 'line 60', 'LS line 30/60/120', 'LS quad 30/60/120')}
    for w in W:
        y30, y60, y120 = ang['T30'][w], ang['T60'][w], ang['T120'][w]
        c = np.linalg.solve(np.array([[30.0, 900.0], [60.0, 3600.0]]), np.array([y30, y60]))
        T = np.array([30.0, 60.0, 120.0]); Y = np.array([y30, y60, y120])
        a_ls = (T @ Y) / (T @ T)
        cq, *_ = np.linalg.lstsq(np.vstack([T, T ** 2]).T, Y, rcond=None)
        for k in (3, 9):
            yk = ang[f'K{k}'][w]
            def inv(c0, c1):
                if abs(c1) < 1e-15: return yk / c0 if c0 else np.nan
                rts = [r.real for r in np.roots([c1, c0, -yk]) if abs(r.imag) < 1e-9 and -5 < r.real < 80]
                return min(rts, key=lambda r: abs(r - (yk / c0 if c0 else 0))) if rts else np.nan
            per['quad 30/60 (claimed)'][k].append(inv(c[0], c[1]) / k)
            per['line 30'][k].append(yk / (y30 / 30) / k)
            per['line 60'][k].append(yk / (y60 / 60) / k)
            per['LS line 30/60/120'][k].append(yk / a_ls / k)
            per['LS quad 30/60/120'][k].append(inv(cq[0], cq[1]) / k)
    for r, d in per.items():
        for k in (3, 9):
            s = np.array(d[k]); s = s[np.isfinite(s)]
            out[f'WITNESS us per look, {k} looks, {r}, median'] = np.median(s)
            if r == 'quad 30/60 (claimed)':
                out[f'WITNESS us per look, {k} looks, {r}, mean'] = s.mean()
                out[f'WITNESS us per look, {k} looks, {r}, trimmed mean 10%'] = np.mean(np.sort(s)[int(0.1 * len(s)):int(0.9 * len(s))])
    for k in (3, 9):
        rr = np.abs(H[f'K{k}'][W] / H['T0'][W]); out[f'hand kept through {k} looks, median (claimed)'] = np.median(rr); out[f'hand kept through {k} looks, mean'] = rr.mean()
    rr = np.abs(H['T30'][W] / H['T0'][W]); out['hand kept through 30 us LAID, median (claimed)'] = np.median(rr); out['hand kept through 30 us LAID, mean'] = rr.mean()
    out['turn per us, median |angle(T30)|/30 (claimed), deg'] = np.degrees(np.median(np.abs(ang['T30'][W]))) / 30
    out['turn per us, signed median angle(T30)/30, deg'] = np.degrees(np.median(ang['T30'][W])) / 30
    out['turn per us, median |angle(T60)|/60, deg'] = np.degrees(np.median(np.abs(ang['T60'][W]))) / 60
    out['turn per us, median |angle(T120)|/120, deg'] = np.degrees(np.median(np.abs(ang['T120'][W]))) / 120
    out['turn per us, mean |angle(T30)|/30, deg'] = np.degrees(np.mean(np.abs(ang['T30'][W]))) / 30
    out['share of spectators turning + (signed T30 > 0)'] = np.mean(ang['T30'][W] > 0)
    out['_W'] = len(W)
    return out


# ------------------------------------------------------------------------------------------------ OWN: hold run
def hold_stats(A):
    al, sep = frame(A, 'OFF|w0__L1', 'ON|w0__L1'); g = sep > 4
    last = lambda key: al(A[[k for k in A if k.startswith(key + '__')][-1]]).mean(0)
    left = {a: last(f'ON|{a}') for a in ('N0', 'L1', 'L3', 'L9')}
    n0 = left['N0']; typ = g & (n0 > 0.1) & (n0 < 0.9); out = {}
    for a, k in (('L1', 1), ('L3', 3), ('L9', 9)):
        t_one = 300 * np.log(np.clip(left[a], 1e-6, None)) / np.log(np.clip(n0, 1e-6, None))      # claimed per-qubit yardstick
        extra = (t_one - 300) / k
        out[f'OWN us per look, {a}, one-clock, median over all 156 (claimed "bit by bit")'] = np.nanmedian(extra)
        out[f'OWN us per look, {a}, one-clock, mean over readable'] = np.nanmean(extra[g])
        out[f'OWN us per look, {a}, one-clock, mean over P300 in (0.1,0.9)'] = np.nanmean(extra[typ])
        mq = (300 * np.log(np.median(left[a])) / np.log(np.median(n0)) - 300) / k
        out[f'OWN us per look, {a}, one-clock, median-qubit levels'] = mq
        # long clock: tau_long = 300 / (-ln n0 - ln(1/(1-f))); extra = tau_long * ln(n0/left)
        tl = 300 / (-np.log(np.clip(n0, 1e-6, None)) - np.log(1 / (1 - F_FAST)))
        ex_l = tl * np.log(np.clip(n0, 1e-6, None) / np.clip(left[a], 1e-6, None)) / k
        out[f'OWN us per look, {a}, long clock, mean over P300 in (0.1,0.9)'] = np.nanmean(ex_l[typ])
        out[f'OWN us per look, {a}, long clock, median over P300 in (0.1,0.9)'] = np.nanmedian(ex_l[typ])
    return out


def give_stats(A):
    al, sep = frame(A, 'OFF|w0__L1', 'ON|w0__L1'); g = sep > 4
    none = np.clip(al(A['ON|none__L1']).mean(0), 0.02, 0.98); tau = -300 / np.log(none); typ = g & (none > 0.1) & (none < 0.9)
    tl = 300 / (-np.log(none) - np.log(1 / (1 - F_FAST))); out = {}
    for a, at in (('at0', 0), ('at150', 150), ('at270', 270)):
        end = np.clip(al(A[f'ON|{a}__L2']).mean(0), 0.02, 0.98); c = tau * np.log(none / end); cl = tl * np.log(none / end)
        out[f'OWN cost of one look at {at:>3} us, one-clock, mean readable (claimed)'] = c[g].mean()
        out[f'OWN cost of one look at {at:>3} us, one-clock, median readable'] = np.median(c[g])
        out[f'OWN cost of one look at {at:>3} us, one-clock, mean P300 in (0.1,0.9)'] = c[typ].mean()
        out[f'OWN cost of one look at {at:>3} us, long clock, mean P300 in (0.1,0.9)'] = cl[typ].mean()
    return out


def run_set(runs, fn, rng):
    per = []
    for r in runs:
        m, A = load(r); s = fn(A); B = [fn(resample(A, rng)) for _ in range(NB)]
        per.append((r, m, s, {k: np.nanstd([b[k] for b in B]) for k in s if not k.startswith('_')}))
    return per


L = []; P = L.append; P(f'# script sha256 {sha(os.path.abspath(__file__))}')
rng = np.random.default_rng(20261003)
for title, runs, fn in (('WITNESS: look-time runs 101-103 (spectators time the far qubits\' looks) [WITNESS, mapped onto LAID delays]', (101, 102, 103), look_stats),
                        ('OWN: hold runs 71-73 (looks on the way inside 300 us LAID) [OWN]', (71, 72, 73), hold_stats),
                        ('OWN: give-back runs 111-113 (one look inside 300 us LAID) [OWN]', (111, 112, 113), give_stats)):
    per = run_set(runs, fn, rng)
    for r, m, _, _ in per:
        P(f'# run {r} job {m["job_id"]} start {m["start_time"][11:19]}; results sha256 {sha(os.path.join(D, f"run{r}_results.npz"))}')
    P(''); P(f'== {title}' + (f'; spectators read {[s["_W"] for _, _, s, _ in per]}' if '_W' in per[0][2] else ''))
    for k in per[0][2]:
        if k.startswith('_'): continue
        v = np.array([s[k] for _, _, s, _ in per]); w = np.array([x[k] for _, _, _, x in per])
        P(f'   {k:<82} ' + '  '.join(f'{a:+.4f}({b:.4f})' for a, b in zip(v, w)) + f'  | all {v.mean():+.4f}({np.sqrt((w ** 2).sum()) / 3:.4f}); spread of the three {v.std(ddof=1):.4f}')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
