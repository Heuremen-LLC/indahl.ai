"""Christensen et al. 2013 (Illinois) CH Bell data: settings are fixed for a 1-second file, taken from a
stored QRNG bit list (randomdata): Alice = random(i), Bob = random(i+1) (Matlab 1-based).
Unit of shuffling = FILE (the key only changes file to file). Trial = one Pockels-cell window
(ch15 trigger plus the hidden trigger halfway). Click = detection 8000..26000 bins (156.25 ps) after trial start."""
import os, glob, re, json, numpy as np, scipy.io as sio, sys
sys.path.insert(0, os.path.dirname(__file__))
import bellsort as bs
from scipy.stats import chi2
B = os.path.expanduser('~/bones-forge/public_bell')
LO, HI = 8000, 26000

def per_file():
    recs = []
    for d in sorted(glob.glob(os.path.join(B, 'illinois2013', 'CH_Bell_Data', '*'))):
        if not os.path.isdir(d):
            continue
        ds = os.path.basename(d).split(' ')[0]
        for f in glob.glob(os.path.join(d, '*.mat')):
            m = sio.loadmat(f)
            ch = [k for k in m if k.startswith('channel')][0]
            c = m[ch].ravel(); t = m[ch.replace('channel', 'timetags')].ravel()
            o = np.argsort(t); c, t = c[o], t[o]
            t15 = t[c == 15]
            if t15.size < 100:
                continue
            sp = np.median(np.diff(t15)); starts = np.sort(np.concatenate([t15, t15 + sp / 2]))
            ntr = starts.size
            def clicks(chn):
                tc = t[c == chn]; j = np.searchsorted(starts, tc) - 1; ok = j >= 0
                dl = tc[ok] - starts[j[ok]]; sel = (dl >= LO) & (dl < HI)
                return j[ok][sel], dl[sel]
            ja, dla = clicks(1); jb, dlb = clicks(2)
            A = np.zeros(ntr, bool); A[ja] = True; Bc = np.zeros(ntr, bool); Bc[jb] = True
            i = int(m['i'].ravel()[0]); r = m['randomdata'].ravel().astype(int)
            recs.append(dict(ds=ds, i=i, a=int(m['asetting'].ravel()[0]) - 1, b=int(m['bsetting'].ravel()[0]) - 1,
                             a_seq=int(r[i - 1]), b_seq=int(r[i]),
                             a_next=int(r[i + 1]), b_next=int(r[i + 2]), a_prev=int(r[i - 3]), b_prev=int(r[i - 2]),
                             ntr=int(ntr), n00=int((~A & ~Bc).sum()), n01=int((~A & Bc).sum()), n10=int((A & ~Bc).sum()), n11=int((A & Bc).sum()),
                             tA=np.histogram(dla, bins=np.linspace(LO, HI, 7))[0].tolist(), tB=np.histogram(dlb, bins=np.linspace(LO, HI, 7))[0].tolist()))
    return recs

def cluster_test(s, k, g, O, S, K, R=5000, rng=None):
    """Table T[s,k,e] = sum over files of O_f; null = shuffle key among files within (group, stratum)."""
    rng = rng or np.random.default_rng(7)
    E = O.shape[1]
    def table(kk):
        T = np.zeros((S * K, E))
        np.add.at(T, s * K + kk, O)
        return T.reshape(S, K, E)
    T = table(k); Gobs = float(bs.G_of(T))
    cells = {}
    for idx, key in enumerate(zip(g, s)):
        cells.setdefault(key, []).append(idx)
    cells = [np.array(v) for v in cells.values()]
    Gp = np.empty(R)
    for r in range(R):
        kk = k.copy()
        for v in cells:
            kk[v] = k[v][rng.permutation(v.size)]
        Gp[r] = bs.G_of(table(kk))
    return dict(G=Gobs, df=bs.dof(T), p_naive_trialwise=float(chi2.sf(Gobs, bs.dof(T))),
                p_shuffle=float((1 + (Gp >= Gobs).sum()) / (1 + R)), z_vs_shuffle=float((Gobs - Gp.mean()) / Gp.std()), N=int(T.sum()), R=R), T

if __name__ == '__main__':
    recs = per_file()
    json.dump(recs, open(os.path.join(B, 'results', 'illinois_perfile.json'), 'w'))
    print('files', len(recs), 'setting check a,b == seq:', np.mean([r['a'] == r['a_seq'] and r['b'] == r['b_seq'] for r in recs]))

def analyze(R=5000):
    recs = json.load(open(os.path.join(B, 'results', 'illinois_perfile.json')))
    recs.sort(key=lambda r: (r['ds'], r['i']))
    # interior files only (a real later AND a real earlier measurement exists in the same data set)
    byds = {}
    for r in recs: byds.setdefault(r['ds'], []).append(r)
    use = []
    for ds, L in byds.items():
        iset = {r['i'] for r in L}
        use += [r for r in L if (r['i'] + 2 in iset) and (r['i'] - 2 in iset)]
    g = np.array([hash(r['ds']) % 100000 for r in use]); a = np.array([r['a'] for r in use]); b = np.array([r['b'] for r in use])
    s0 = a * 2 + b
    O = np.array([[r['n00'], r['n01'], r['n10'], r['n11']] for r in use], float)
    OA = np.stack([O[:, 0] + O[:, 1], O[:, 2] + O[:, 3]], 1)      # Alice no-click / click
    OB = np.stack([O[:, 0] + O[:, 2], O[:, 1] + O[:, 3]], 1)
    TA = np.array([r['tA'] for r in use], float); TB = np.array([r['tB'] for r in use], float)
    rows = []
    rng = np.random.default_rng(99)
    for tag, ka, kb in (('later', 'a_next', 'b_next'), ('earlier', 'a_prev', 'b_prev')):
        KA = np.array([r[ka] for r in use]); KB = np.array([r[kb] for r in use])
        for name, OO, K, key in (('Aclick~Aset', OA, 2, KA), ('Aclick~Bset', OA, 2, KB), ('Bclick~Bset', OB, 2, KB), ('Bclick~Aset', OB, 2, KA),
                                 ('joint~jointset', O, 4, KA * 2 + KB), ('Atime~Aset', TA, 2, KA), ('Atime~Bset', TA, 2, KB),
                                 ('Btime~Bset', TB, 2, KB), ('Btime~Aset', TB, 2, KA)):
            res, T = cluster_test(s0, key, g, OO, 4, K, R=R, rng=rng)
            eff = ''
            if K == 2 and OO.shape[1] == 2:
                rs = bs.rate_split(T, 1); eff = f"click rate {rs['base_rate']:.4g}; key1-key0 adj diff {rs['adj_diff']:+.3g} (relative {rs['adj_diff']/rs['base_rate']:+.2%})"
            if K == 2 and OO.shape[1] == 6:
                centers = (np.linspace(LO, HI, 7)[:-1] + (HI - LO) / 12) * 0.15625
                eff = f"mean click-time shift key1-key0 {bs.mean_split(T, centers):+.3f} ns"
            res.update(dataset='Illinois2013', part='all interior files', sort=f'{tag}|{name}', effect=eff)
            rows.append(res)
    # control: same-file Bell correlation and no-signalling (file-level shuffle of own settings is not meaningful; report trial-wise G only)
    Tc = np.zeros((1, 4, 4)); np.add.at(Tc[0], s0, O)
    rows.append(dict(dataset='Illinois2013', part='all interior files', sort='ctrl|joint~jointset_same', G=float(bs.G_of(Tc)), df=bs.dof(Tc),
                     p_naive_trialwise=float(chi2.sf(bs.G_of(Tc), bs.dof(Tc))), p_shuffle=np.nan, z_vs_shuffle=np.nan, N=int(Tc.sum()), effect=''))
    json.dump(rows, open(os.path.join(B, 'results', 'illinois_results.json'), 'w'), indent=1, default=float)
    for r in rows:
        print(f"{r['sort']:26s} N={r['N']:>9d} G={r['G']:8.2f} df={r['df']:3d} p_trialwise={r['p_naive_trialwise']:.3g} p_fileshuffle={r['p_shuffle']:.4f} z={r['z_vs_shuffle']:+.2f} {r['effect']}")
    print('files used', len(use))
