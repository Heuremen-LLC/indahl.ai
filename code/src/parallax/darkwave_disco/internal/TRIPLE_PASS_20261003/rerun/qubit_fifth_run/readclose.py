"""readclose.py -- reads the CLOSE-IT-ALL runs on ibm_pittsburgh (push 91-93, look-time 101-103, give-back 111-113). By hand, outside every freeze.
All bits, no cut beyond the readable-clouds rule (separation > 4 widths), means over bits, widths from shot resampling, each read against the other two.
No verdict word. A run is read only when all three of its reads have landed.
  python readclose.py push|looktime|giveback"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); RNG = np.random.default_rng(20261002); NB = 100


def load(r):
    m = json.load(open(os.path.join(D, f'run{r}_meta.json')))
    if m.get('complete') is not True: raise SystemExit(f'run {r} not complete: not read')
    z = np.load(os.path.join(D, f'run{r}_results.npz')); return m, {k: np.asarray(z[k]).astype(complex) for k in z.files}


def frame(A, off, on):
    c0 = A[off].mean(0); d = A[on].mean(0) - c0
    return (lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2), np.abs(d) / np.sqrt((np.abs(A[off] - c0) ** 2).mean(0) / 2)


def resample(A):
    out = {}; idx = {}
    for k, v in A.items():
        base = k.split('__')[0]
        if base not in idx: idx[base] = RNG.integers(0, v.shape[0], v.shape[0])
        out[k] = v[idx[base]]
    return out


def three(vals, widths):
    v = np.array(vals); w = np.array(widths); mean = v.mean(); wid = np.sqrt((w ** 2).sum()) / len(v)
    other = [v[i] - np.mean(np.delete(v, i)) for i in range(len(v))]
    return mean, wid, other


def show(label, per, unit=''):
    m, w, o = three([p[0] for p in per], [p[1] for p in per])
    print(f'   {label:<58} ' + '  '.join(f'{p[0]:+.4f} +- {p[1]:.4f}' for p in per) + f'   | all {m:+.4f} +- {w:.4f}{unit}   each minus the other two ' + ' '.join(f'{x:+.4f}' for x in o))
    return m, w


# ---------------------------------------------------------------------------------------------------------------------------------------- PUSH
def book(m0, q, nseg):
    on, off = m0, 1 - m0
    for _ in range(nseg): on, off = off + on * (1 - q), on * q
    return on


def push_stats(A):
    al, sep = frame(A, 'OFF|p0__L1', 'ON|p0__L1'); g = sep > 4; lv = {k.split('__')[0]: al(v).mean(0) for k, v in A.items()}
    q = np.clip(lv['ON|n300'], 0.02, 0.98) ** 0.1; out = {}
    for s, base in (('OFF', 'OFF|p0'), ('ON', 'ON|p0'), ('MID', 'MID|p0')):
        for n in ('p2', 'p10'): out[f'{s} {n} back-to-back minus no push'] = (lv[f'{s}|{n}'] - lv[base])[g].mean()
        start = np.zeros_like(lv[base]) if s == 'OFF' else (np.ones_like(lv[base]) if s == 'ON' else lv[base])
        out[f'{s} s10 spread minus bookkeeping'] = (lv[f'{s}|s10'] - book(start, q, 10))[g].mean()
    out['OFF n300 (nothing done, 300 us)'] = lv['OFF|n300'][g].mean(); out['ON n300 (nothing done, 300 us)'] = lv['ON|n300'][g].mean()
    out['MID no push (level)'] = lv['MID|p0'][g].mean(); out['_bits'] = int(g.sum())
    return out


def read_push():
    R = []
    for r in (91, 92, 93):
        m, A = load(r); s = push_stats(A); B = [push_stats(resample(A)) for _ in range(NB)]
        R.append((m['start_time'][11:16], s, {k: np.std([b[k] for b in B]) for k in s if not k.startswith('_')}))
    print('THE PUSH RUN, ibm_pittsburgh, reads at ' + ' '.join(t for t, _, _ in R) + f"; {R[0][1]['_bits']} bits with clouds >4 widths apart. Levels: OFF = 0, ON = 1 (lone looks).")
    for k in [k for k in R[0][1] if not k.startswith('_')]:
        show(k, [(s[k], w[k]) for _, s, w in R])
    print('\n   THE BOXES, side by side (all three reads):')
    for s in ('OFF', 'ON', 'MID'):
        a = three([x[1][f'{s} p10 back-to-back minus no push'] for x in R], [x[2][f'{s} p10 back-to-back minus no push'] for x in R])
        b = three([x[1][f'{s} s10 spread minus bookkeeping'] for x in R], [x[2][f'{s} s10 spread minus bookkeeping'] for x in R])
        c = three([x[1][f'{s} p2 back-to-back minus no push'] for x in R], [x[2][f'{s} p2 back-to-back minus no push'] for x in R])
        print(f'   {s:<4} ten pushes, NO time between: {a[0]:+.4f} +- {a[1]:.4f}   ten pushes over 300 us, beyond bookkeeping: {b[0]:+.4f} +- {b[1]:.4f}   two pushes, no time: {c[0]:+.4f} +- {c[1]:.4f}')


# ---------------------------------------------------------------------------------------------------------------------------------------- GIVE-BACK
def give_stats(A):
    al, sep = frame(A, 'OFF|w0__L1', 'ON|w0__L1'); g = sep > 4; out = {}
    none = np.clip(al(A['ON|none__L1']).mean(0), 0.02, 0.98); tau = -300 / np.log(none)
    for a, mid_at in (('at0', 0), ('at150', 150), ('at270', 270)):
        end = np.clip(al(A[f'ON|{a}__L2']).mean(0), 0.02, 0.98); mid = al(A[f'ON|{a}__L1']).mean(0)
        out[f'look at {mid_at:>3} us: what it costs by the end (us)'] = (tau * np.log(none / end))[g].mean()
        out[f'look at {mid_at:>3} us: what the look itself reads, over plain fading'] = (mid / np.exp(-mid_at / tau))[g].mean()
    out['nothing on the way: left at 300 us'] = none[g].mean(); out['_bits'] = int(g.sum())
    return out


def read_give():
    R = []
    for r in (111, 112, 113):
        m, A = load(r); s = give_stats(A); B = [give_stats(resample(A)) for _ in range(NB)]
        R.append((m['start_time'][11:16], s, {k: np.std([b[k] for b in B]) for k in s if not k.startswith('_')}))
    print('THE GIVE-BACK RUN, ibm_pittsburgh, reads at ' + ' '.join(t for t, _, _ in R) + f"; {R[0][1]['_bits']} bits. ON, 300 us, last look; one look on the way at 0 / 150 / 270 us.")
    for k in [k for k in R[0][1] if not k.startswith('_')]: show(k, [(s[k], w[k]) for _, s, w in R])


# ---------------------------------------------------------------------------------------------------------------------------------------- LOOK-TIME
def look_stats(A, RO):
    al, sep = frame(A, 'F0__L1', 'F1__L1'); EM = RO['emitters']; WOF = {int(k): v for k, v in RO['witness_of'].items()}; FAR = set(RO['far'])
    nb = {}
    for a, b in RO['edges']: nb.setdefault(a, set()).add(b); nb.setdefault(b, set()).add(a)
    fin = lambda key: [k for k in A if k.startswith(key + '__')][-1]                 # the last register = the final look
    P = {key: al(A[fin(key)]) for key in {k.split('__')[0] for k in A}}
    H = {a: (2 * P[f'{a}|X'].mean(0) - 1) - 1j * (2 * P[f'{a}|Y'].mean(0) - 1) for a in ('T0', 'T30', 'T60', 'T120', 'K3', 'K9')}
    W = [w for w in sorted(WOF) if abs(H['T0'][w]) > 0.15 and sep[w] > 3 and sep[WOF[w]] > 3]
    ang = {a: np.angle(H[a] / H['T0']) for a in ('T30', 'T60', 'T120', 'K3', 'K9')}
    uw = np.unwrap(np.vstack([np.zeros_like(ang['T30']), ang['T30'], ang['T60'], ang['T120']]), axis=0)     # each clock's turn over 0 / 30 / 60 / 120 us, unwrapped in order
    ang['T30'], ang['T60'], ang['T120'] = uw[1], uw[2], uw[3]
    out = {'_W': W}
    # the clock's own curve over OUR laid time, per clock: angle(T) through 0, 30, 60 (quadratic through the origin); the look windows read off it
    slots = {3: [], 9: []}; adj = {3: [], 9: []}
    for w in W:
        t = np.array([30.0, 60.0]); y = np.array([ang['T30'][w], ang['T60'][w]])
        A2 = np.vstack([t, t ** 2]).T; c = np.linalg.solve(A2, y)                      # angle = c0 T + c1 T^2
        for k in (3, 9):
            yk = ang[f'K{k}'][w]; roots = np.roots([c[1], c[0], -yk]); roots = [r.real for r in roots if abs(r.imag) < 1e-9 and -5 < r.real < 80]
            win = min(roots, key=lambda r: abs(r - (yk / c[0] if c[0] else 0))) if roots else np.nan
            slots[k].append(win / k); adj[k].append(bool(nb.get(w, set()) & FAR))
    for k in (3, 9):
        s = np.array(slots[k]); a = np.array(adj[k])
        out[f'one look, timed by the clocks ({k} looks), us'] = np.nanmedian(s)
        out[f'   clocks NOT wired to a looked-at bit ({k} looks), us'] = np.nanmedian(s[~a]) if (~a).sum() else np.nan
        out[f'   clocks wired to a looked-at bit ({k} looks), us'] = np.nanmedian(s[a]) if a.sum() else np.nan
        out[f'hand kept through {k} looks (over the hand at no window)'] = np.median(np.abs(H[f'K{k}'][W] / H['T0'][W]))
    out['hand kept through 30 us of laid time'] = np.median(np.abs(H['T30'][W] / H['T0'][W]))
    out['clock turn per us over the first 30 us (deg)'] = np.degrees(np.median(np.abs(ang['T30'][W]))) / 30
    # seat 3: does each clock follow ITS OWN emitter's fading? the emitter's own end level in the window arms gives its fading in this job
    le = {t: np.mean([P[f'T{t}|X'].mean(0), P[f'T{t}|Y'].mean(0)], axis=0) for t in (0, 30, 60, 120)}
    tau_e = {e: (-120 / np.log(np.clip(le[120][e] / max(le[0][e], 0.05), 0.05, 0.999))) for e in EM}
    tc = np.median([tau_e[e] for e in EM]); mis_own, mis_chip, te = [], [], []
    for w in W:
        y = np.array([ang['T30'][w], ang['T60'][w], ang['T120'][w]]); T = np.array([30.0, 60.0, 120.0])
        for tau, lst in ((tau_e[WOF[w]], mis_own), (tc, mis_chip)):
            X = np.vstack([T, tau * (1 - np.exp(-T / tau))]).T; coef, *_ = np.linalg.lstsq(X, y, rcond=None); lst.append(np.degrees(np.sqrt(np.mean((X @ coef - y) ** 2))))
        te.append(tau_e[WOF[w]])
    out['clock curve misfit with ITS OWN emitter\'s fading (deg)'] = np.median(mis_own); out['clock curve misfit with the chip\'s typical fading (deg)'] = np.median(mis_chip)
    out['own minus typical misfit (deg)'] = np.median(np.array(mis_own) - np.array(mis_chip)); out['emitter fading time in this job, middle (us)'] = tc
    return out


def read_look():
    RO = json.load(open(os.path.join(HERE, 'data', 'reads', 'looktime_roles.json'))); R = []
    for r in (101, 102, 103):
        m, A = load(r); s = look_stats(A, RO); B = [look_stats(resample(A), RO) for _ in range(NB)]
        R.append((m['start_time'][11:16], s, {k: np.nanstd([b[k] for b in B]) for k in s if not k.startswith('_')}))
    print('THE WITNESS TIMES THE LOOK, ibm_pittsburgh, reads at ' + ' '.join(t for t, _, _ in R) + f"; {len(R[0][1]['_W'])} readable clocks; roles from {RO['source']}")
    for k in [k for k in R[0][1] if not k.startswith('_')]: show(k, [(s[k], w[k]) for _, s, w in R])
    p = os.path.join(HERE, 'data', 'reads', 'pittsburgh_config_timing.json')
    if os.path.exists(p): print('\n   the maker\'s timing numbers in the static configuration (read at fire): ' + json.dumps({k: v for k, v in json.load(open(p))['fields'].items() if k not in ('meas_map', 'supported_instructions')}, default=str)[:900])
    print("   the maker's stated length of one look on this chip (read 11:02): 2.180 us")


if __name__ == '__main__':
    {'push': read_push, 'giveback': read_give, 'looktime': read_look}[sys.argv[1]]()
