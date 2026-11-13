"""Later/earlier sorts on the Weihs et al. 1998 Innsbruck time tags (Zenodo 7185335).
Each detection = (time tag, setting/switch bit, outcome/detector bit).  Files processed one at a time.
Every sort is stratified by 1-second time block (so slow drifts cannot fake a sort) plus the listed
conditioning records.  Far-lag controls (key taken 1000 records away) measure what drift alone does.
"""
import os, sys, glob, re, json, numpy as np
B = os.path.expanduser('~/bones-forge/public_bell')
W = os.path.join(B, 'weihs1998')
OUT = os.path.join(B, 'results')
GAP_EDGES = np.array([0.5e-6, 1e-6, 2e-6, 5e-6, 10e-6, 30e-6])   # -> 7 gap bins
BLOCK = 1.0
FAR = 1000

def load(side, folder, name):
    d = os.path.join(W, side, 'Timetags', folder)
    t = np.fromfile(os.path.join(d, name + '_V.dat'), dtype='>f8').astype(np.float64)
    c = np.fromfile(os.path.join(d, name + '_C.dat'), dtype='>u2').astype(np.int64)
    good = np.isfinite(t) & (t >= 0) & (t < 1e5)      # longtime1 (Bob) has ~765 corrupt entries (|t|~1e79 or sign-flipped)
    if (~good).any():
        print('  dropping', int((~good).sum()), 'corrupt time tags in', side, name)
    t, c = t[good], c[good]
    o = np.argsort(t, kind='stable')
    # NOTE: the Zenodo text says detector=LSB, switch=next bit.  Checked against the group's own
    # evaluation files (*_R.dat E(a,b) values): it is the other way round.  LSB = switch/setting.
    return t[o], c[o] & 1, (c[o] >> 1) & 1          # time, setting, outcome

def rwindow(name):
    try:
        for line in open(os.path.join(W, 'Alice', name + '_R.dat'), errors='ignore'):
            if line.startswith('Window'):
                return float(line.split()[-1])
    except FileNotFoundError:
        pass
    return 3.0

class Tab:
    def __init__(self): self.T = {}; self.nblk = 0
    def add(self, name, S, K, E, s, k, e):
        """s may include a block index already (global); S = inner stratum count; blocks are appended."""
        pass

def add(T, name, S, K, E, s, k, e):
    s = np.asarray(s); k = np.asarray(k); e = np.asarray(e)
    code = (s * K + k) * E + e
    cnt = np.bincount(code, minlength=S * K * E).reshape(S, K, E)
    if name in T:
        old = T[name]
        if old.shape[0] < S:
            old = np.concatenate([old, np.zeros((S - old.shape[0], K, E), old.dtype)])
        T[name] = old + cnt
    else:
        T[name] = cnt

def gbin(g):
    return np.searchsorted(GAP_EDGES, g)

def find_peak(tA, tB):
    j = np.searchsorted(tB, tA)
    j0 = np.clip(j - 1, 0, len(tB) - 1); j1 = np.clip(j, 0, len(tB) - 1)
    d = np.concatenate([tB[j0] - tA, tB[j1] - tA])
    d = d[np.abs(d) < 200e-9]
    h, e = np.histogram(d, bins=np.arange(-200e-9, 200e-9 + 1e-12, 0.25e-9))
    k = np.argmax(h)
    m = np.abs(d - (e[k] + 0.125e-9)) < 2e-9
    return float(np.median(d[m])), int(h.max()), int(np.median(h))

def coincidences(tA, tB, peak, half):
    j = np.searchsorted(tB, tA + peak)
    best = np.full(tA.size, -1); bestd = np.full(tA.size, np.inf)
    for jj in (j - 1, j):
        ok = (jj >= 0) & (jj < tB.size)
        dd = np.full(tA.size, np.inf); dd[ok] = np.abs(tB[jj[ok]] - tA[ok] - peak)
        better = dd < bestd; best[better] = jj[better]; bestd[better] = dd[better]
    ia = np.where(bestd <= half)[0]; ib = best[ia]
    u, cnt = np.unique(ib, return_counts=True); dup = u[cnt > 1]
    keep = ~np.isin(ib, dup)
    return ia[keep], ib[keep]

def per_detection(T, t, s, x, t_other, s_other, peak_to_other, side, blk0, nblk, t0):
    n = t.size; i = np.arange(FAR, n - FAR)
    blk = blk0 + np.clip(((t[i] - t0) / BLOCK).astype(int), 0, nblk - 1)
    S = (blk0 + nblk) * 14
    gn = gbin(t[i + 1] - t[i]); gp = gbin(t[i] - t[i - 1])
    add(T, f'later|{side}out~own_next_set', S, 2, 2, blk * 14 + s[i] * 7 + gn, s[i + 1], x[i])
    add(T, f'earlier|{side}out~own_prev_set', S, 2, 2, blk * 14 + s[i] * 7 + gp, s[i - 1], x[i])
    add(T, f'farlater|{side}out~own_set+{FAR}', S, 2, 2, blk * 14 + s[i] * 7, s[i + FAR], x[i])
    add(T, f'farearlier|{side}out~own_set-{FAR}', S, 2, 2, blk * 14 + s[i] * 7, s[i - FAR], x[i])
    tt = t[i] + peak_to_other
    j = np.searchsorted(t_other, tt)
    ok = (j >= FAR) & (j < t_other.size - FAR)
    ii, jn, jp, bb = i[ok], j[ok], j[ok] - 1, blk[ok]
    gn2 = gbin(t_other[jn] - tt[ok]); gp2 = gbin(tt[ok] - t_other[jp])
    add(T, f'later|{side}out~other_next_set', S, 2, 2, bb * 14 + s[ii] * 7 + gn2, s_other[jn], x[ii])
    add(T, f'earlier|{side}out~other_prev_set', S, 2, 2, bb * 14 + s[ii] * 7 + gp2, s_other[jp], x[ii])
    add(T, f'farlater|{side}out~other_set+{FAR}', S, 2, 2, bb * 14 + s[ii] * 7, s_other[jn + FAR], x[ii])
    add(T, f'farearlier|{side}out~other_set-{FAR}', S, 2, 2, bb * 14 + s[ii] * 7, s_other[jp - FAR], x[ii])

def run(files, label):
    T = {}; meta = []; blk0 = 0; C = {}
    for folder, name in files:
        try:
            tA, a, x = load('Alice', folder, name); tB, b, y = load('Bob', folder, name)
        except FileNotFoundError as e:
            print('missing', name, e); continue
        peak, hmax, hmed = find_peak(tA, tB)
        half = rwindow(name) * 1e-9
        ia, ib = coincidences(tA, tB, peak, half)
        if ia.size < 1000:
            print('SKIP (no coincidence peak; timing unusable)', name, 'peak_ns', round(peak * 1e9, 1), 'coinc', ia.size)
            meta.append(dict(name=name, skipped=True, coinc=int(ia.size), peak_ns=peak * 1e9)); continue
        t0 = min(tA[0], tB[0] - peak); nblk = int(np.ceil((max(tA[-1], tB[-1] - peak) - t0) / BLOCK)) + 1
        dt = tB[ib] - tA[ia] - peak
        twinA = np.sum((np.diff(tA) < 30e-9) & (x[1:] != x[:-1])); twinB = np.sum((np.diff(tB) < 30e-9) & (y[1:] != y[:-1]))
        meta.append(dict(name=name, nA=int(tA.size), nB=int(tB.size), peak_ns=peak * 1e9, half_window_ns=half * 1e9, coinc=int(ia.size),
                         twin_clicks_A=int(twinA), twin_clicks_B=int(twinB), span_s=float(tA[-1] - tA[0]), blocks=nblk))
        per_detection(T, tA, a, x, tB, b, peak, 'A', blk0, nblk, t0)
        per_detection(T, tB, b, y, tA, a, -peak, 'B', blk0, nblk, t0 + peak)
        o = np.argsort(tA[ia]); ia, ib, dt = ia[o], ib[o], dt[o]
        ca, cb, cx, cy = a[ia], b[ib], x[ia], y[ib]
        blk = blk0 + np.clip(((tA[ia] - t0) / BLOCK).astype(int), 0, nblk - 1)
        S = (blk0 + nblk) * 4
        for tagL, lag in (('later', 1), ('earlier', -1), ('farlater', FAR), ('farearlier', -FAR)):
            m = np.arange(FAR, ia.size - FAR); j = m + lag
            s0 = blk[m] * 4 + ca[m] * 2 + cb[m]
            dtb = np.clip(((dt + half) / (2 * half) * 6).astype(int), 0, 5)
            add(T, f'{tagL}|C_joint~jointset', S, 4, 4, s0, ca[j] * 2 + cb[j], cx[m] * 2 + cy[m])
            add(T, f'{tagL}|C_Aout~Aset', S, 2, 2, s0, ca[j], cx[m])
            add(T, f'{tagL}|C_Aout~Bset', S, 2, 2, s0, cb[j], cx[m])
            add(T, f'{tagL}|C_Bout~Bset', S, 2, 2, s0, cb[j], cy[m])
            add(T, f'{tagL}|C_Bout~Aset', S, 2, 2, s0, ca[j], cy[m])
            add(T, f'{tagL}|C_delay~jointset', S * 4, 4, 6, s0 * 4 + cx[m] * 2 + cy[m], ca[j] * 2 + cb[j], dtb[m])
        # same-coincidence controls (block-stratified)
        s1 = blk
        add(T, 'ctrl|C_joint~jointset_same', blk0 + nblk, 4, 4, s1, ca * 2 + cb, cx * 2 + cy)
        add(T, 'ctrl|C_delay~ownsettings_same', (blk0 + nblk) * 4, 4, 6, s1 * 4 + cx * 2 + cy, ca * 2 + cb, np.clip(((dt + half) / (2 * half) * 6).astype(int), 0, 5))
        add(T, 'ctrl|C_Aout~Bset_same', (blk0 + nblk) * 2, 2, 2, s1 * 2 + ca, cb, cx)
        add(T, 'ctrl|C_Bout~Aset_same', (blk0 + nblk) * 2, 2, 2, s1 * 2 + cb, ca, cy)
        # order inside a pair (which side's record is later) -- kept only as a diagnostic
        blater = dt > 0
        add(T, 'diag|inpair_Aout~Bset_Blater', (blk0 + nblk) * 2, 2, 2, (s1 * 2 + ca)[blater], cb[blater], cx[blater])
        add(T, 'diag|inpair_Aout~Bset_Bearlier', (blk0 + nblk) * 2, 2, 2, (s1 * 2 + ca)[~blater], cb[~blater], cx[~blater])
        blk0 += nblk
        print(name, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in meta[-1].items()}, flush=True)
    # pad all tables to the final number of strata
    for k, v in T.items():
        pass
    np.savez_compressed(os.path.join(OUT, f'weihs_{label}.npz'), **{k.replace('|', '__').replace('~', '_BY_').replace('+', 'p').replace('-', 'm'): v for k, v in T.items()})
    json.dump(meta, open(os.path.join(OUT, f'weihs_{label}_meta.json'), 'w'), indent=1)

if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else 'longdist'
    names = sorted({re.sub(r'_V\.dat$', '', os.path.basename(p)) for p in glob.glob(os.path.join(W, 'Alice', 'Timetags', folder, '*_V.dat'))},
                   key=lambda s: int(re.sub(r'\D', '', s) or 0))
    run([(folder, n) for n in names], folder)
