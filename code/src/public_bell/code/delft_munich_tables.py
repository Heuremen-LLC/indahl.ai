"""Later/earlier sort tables for Delft 2015, Delft 2016 (4TU) and Munich 2017 (Zenodo) public files."""
import os, numpy as np
B = os.path.expanduser('~/bones-forge/public_bell')
OUT = os.path.join(B, 'results')

def add(T, name, S, K, E, s, k, e):
    code = (np.asarray(s) * K + np.asarray(k)) * E + np.asarray(e)
    T[name] = T.get(name, 0) + np.bincount(code, minlength=S * K * E).reshape(S, K, E)

def seq_sorts(T, a, b, x, y, grp, extra_strat=None, extra_S=1):
    """a,b settings; x,y outcomes (0/1); consecutive rows inside the same grp are neighbours."""
    n = len(a)
    idx = np.arange(1, n - 1)
    ok = (grp[idx - 1] == grp[idx]) & (grp[idx + 1] == grp[idx])
    m = idx[ok]
    es = extra_strat[m] if extra_strat is not None else np.zeros(m.size, int)
    s0 = (a[m] * 2 + b[m]) * extra_S + es
    S = 4 * extra_S
    for tag, j in (('later', m + 1), ('earlier', m - 1)):
        add(T, f'{tag}|Aout~Aset', S, 2, 2, s0, a[j], x[m])
        add(T, f'{tag}|Aout~Bset', S, 2, 2, s0, b[j], x[m])
        add(T, f'{tag}|Bout~Bset', S, 2, 2, s0, b[j], y[m])
        add(T, f'{tag}|Bout~Aset', S, 2, 2, s0, a[j], y[m])
        add(T, f'{tag}|joint~jointset', S, 4, 4, s0, a[j] * 2 + b[j], x[m] * 2 + y[m])
    add(T, 'ctrl|joint~jointset_same', extra_S, 4, 4, es, a[m] * 2 + b[m], x[m] * 2 + y[m])
    return m

def delft(files, win0s, tag, psi_plus=False):
    rows = []
    for fp, w0 in zip(files, win0s):
        d = np.loadtxt(fp, delimiter=',', usecols=np.arange(1, 17), dtype=np.int64)
        rows.append((d, w0))
    T = {}; Tv = {}
    for fi, (d, w0) in enumerate(rows):
        day, run = d[:, 0], d[:, 1]
        c1t, c1c, c2t, c2c = d[:, 2], d[:, 3], d[:, 4], d[:, 5]
        a, b = d[:, 6], d[:, 7]
        roA, roB = d[:, 10], d[:, 11]
        exA, exB, invA, invB = d[:, 12], d[:, 13], d[:, 14], d[:, 15]
        x = ((roA > 10620) & (roA <= 10620 + 3700)).astype(int)
        y = ((roB > 10620) & (roB <= 10620 + 3700)).astype(int)
        grp = fi * 100000 + day * 100 + run          # neighbours only inside one measurement run
        # all event-ready candidate rows (the file's own sequence)
        seq_sorts(T, a, b, x, y, grp)
        # event-ready click times (earliest records, ps) sorted by same-trial later RNG vs previous-trial RNG
        n = len(a); idx = np.arange(1, n - 1); ok = (grp[idx - 1] == grp[idx]) & (grp[idx + 1] == grp[idx]); m = idx[ok]
        q = np.quantile(c1t, [0.25, 0.5, 0.75]); tb1 = np.searchsorted(q, c1t)   # quartile bins of click-1 time
        q2 = np.quantile(c2t, [0.25, 0.5, 0.75]); tb2 = np.searchsorted(q2, c2t)
        herald_code = c1c * 2 + c2c
        for tagx, j in (('later', m), ('earlier', m - 1)):
            # 'later' here = the same trial's RNG, recorded ~5 us after the herald clicks in each station's frame
            add(T, f'{tagx}|heraldT1~Aset', 4, 2, 4, herald_code[m], a[j], tb1[m])
            add(T, f'{tagx}|heraldT1~Bset', 4, 2, 4, herald_code[m], b[j], tb1[m])
            add(T, f'{tagx}|heraldT2~Aset', 4, 2, 4, herald_code[m], a[j], tb2[m])
            add(T, f'{tagx}|heraldT2~Bset', 4, 2, 4, herald_code[m], b[j], tb2[m])
        # valid Bell trials only (paper's filter), sequence of valid trials
        wl = 55000 - 2550 if not psi_plus else 50000
        w1 = 5425700 if not psi_plus else 5425100
        f1 = ((w0 <= c1t) & (c1t < w0 + wl) & (c1c == 0)) | ((w1 <= c1t) & (c1t < w1 + wl) & (c1c == 1))
        f2m = ((w0 + 250000 <= c2t) & (c2t < w0 + 250000 + wl) & (c2c == 0)) | ((w1 + 250000 <= c2t) & (c2t < w1 + 250000 + wl) & (c2c == 1))
        psim = c1c != c2c
        if psi_plus:
            f2p = ((w0 + 250000 <= c2t) & (c2t < w0 + 250000 + 4000) & (c2c == 0)) | ((w1 + 250000 <= c2t) & (c2t < w1 + 250000 + 2500) & (c2c == 1))
            win = (f1 & f2m & psim) | (f1 & f2p & ~psim)
        else:
            win = f1 & f2m & psim
        valid = win & ((invA == 0) | (invA > 250)) & ((invB == 0) | (invB > 250)) & (exA == 0) & (exB == 0)
        v = np.where(valid)[0]
        seq_sorts(Tv, a[v], b[v], x[v], y[v], np.zeros(v.size, int), extra_strat=psim[v].astype(int), extra_S=2)
        print(tag, os.path.basename(fp := ''), 'rows', len(a), 'valid', valid.sum())
    np.savez(os.path.join(OUT, f'{tag}_allrows.npz'), **{k.replace('|', '__').replace('~', '_BY_'): v for k, v in T.items()})
    np.savez(os.path.join(OUT, f'{tag}_valid.npz'), **{k.replace('|', '__').replace('~', '_BY_'): v for k, v in Tv.items()})

def munich():
    T = {}
    for fi, d in enumerate(['d0415/Bell_2016-04-15_9_pairs.csv', 'd0614/Bell_2016-06-14_16_pairs.csv']):
        fp = os.path.join(B, 'munich2017', d)
        L = [l.rstrip('\n').split('\t') for l in open(fp)][1:]
        L = [r for r in L if len(r) >= 6]
        t = np.array([int(r[0]) for r in L]); st = np.array([1 if r[1].strip() == 'Psi+' else 0 for r in L])
        a = np.array([int(r[2]) for r in L]); x = np.array([int(r[3]) for r in L])
        b = np.array([int(r[4]) for r in L]); y = np.array([int(r[5]) for r in L])
        o = np.argsort(t, kind='stable'); t, st, a, x, b, y = t[o], st[o], a[o], x[o], b[o], y[o]
        print('munich', d, len(t), 'span days', (t[-1] - t[0]) / 86400e3, 'psi+ frac', st.mean())
        # break neighbour links across gaps > 1 hour (maintenance pauses)
        grp = fi * 10**6 + np.concatenate([[0], np.cumsum(np.diff(t) > 3600e3)])
        m = seq_sorts(T, a, b, x, y, grp, extra_strat=st, extra_S=2)
        # herald (Bell state, earliest record of an event) sorted by next vs previous event's settings
        for tagx, j in (('later', m + 1), ('earlier', m - 1)):
            add(T, f'{tagx}|herald~jointset', 1, 4, 2, np.zeros(m.size, int), a[j] * 2 + b[j], st[m])
            add(T, f'{tagx}|joint~herald', 8, 2, 4, (a[m] * 2 + b[m]) * 2 + st[m], st[j], x[m] * 2 + y[m])
    np.savez(os.path.join(OUT, 'munich2017_pairs.npz'), **{k.replace('|', '__').replace('~', '_BY_'): v for k, v in T.items()})

if __name__ == '__main__':
    delft([os.path.join(B, 'delft2015/data/bell_open_data.txt')], [5426350], 'delft2015')
    delft([os.path.join(B, 'delft2016/data/bell_open_data_2_old_detector.txt'), os.path.join(B, 'delft2016/data/bell_open_data_2_new_detector.txt')],
          [5426000, 5426000 - 700], 'delft2016', psi_plus=True)
    munich()
