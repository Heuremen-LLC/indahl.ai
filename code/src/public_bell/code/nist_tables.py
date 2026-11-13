"""Build later/earlier sort tables from NIST 2015 processed HDF5 runs (chunked, low memory).
Trial n = one 100 kHz sync. a,b = Alice/Bob setting bit; clickA/B = any click in the 16-slot window;
slot = which of the 16 laser pulses clicked (12.5 ns steps) = the raw detection time stamp we keep.
Output: results/nist_tables_<run>.npz
"""
import sys, os, numpy as np, h5py
CH = 5_000_000
def popslot(c):
    s = np.full(c.shape, -1, np.int64)
    for k in range(16):
        s[(c >> k) & 1 == 1] = k
    return s

def build(path, outdir):
    run = os.path.basename(path).split('.dat')[0]
    f = h5py.File(path, 'r')
    N = f['alice/settings'].shape[0]
    parts = [f[p + '/badSyncInfo'][0] for p in ('alice', 'bob') if 'badSyncInfo' in f[p]]
    bad = np.unique(np.concatenate(parts)).astype(np.int64) if parts else np.zeros(0, np.int64)
    bad = bad[(bad >= 0) & (bad < N)]
    badmask_idx = np.unique(np.clip(np.concatenate([bad + d for d in range(-2, 3)]), 0, N - 1))
    T = {}
    def add(name, S, K, E, s, k, e):
        code = (s * K + k) * E + e
        cnt = np.bincount(code, minlength=S * K * E).reshape(S, K, E)
        T[name] = T.get(name, 0) + cnt
    ntr = 0
    for st in range(1, N - 1, CH):
        en = min(st + CH, N - 1)
        lo, hi = st - 1, en + 1
        sa = f['alice/settings'][lo:hi].astype(np.int64); sb = f['bob/settings'][lo:hi].astype(np.int64)
        ca = f['alice/clicks'][lo:hi]; cb = f['bob/clicks'][lo:hi]
        okset = ((sa == 1) | (sa == 2)) & ((sb == 1) | (sb == 2))
        a = sa - 1; b = sb - 1
        clA = (ca > 0).astype(np.int64); clB = (cb > 0).astype(np.int64)
        slA = popslot(ca); slB = popslot(cb)
        del sa, sb, ca, cb
        m = np.arange(1, hi - lo - 1)            # local index of trial n
        valid = okset[m - 1] & okset[m] & okset[m + 1]
        g = m + lo                                # global index
        bi = badmask_idx[(badmask_idx >= lo) & (badmask_idx < hi)]
        if bi.size:
            badl = np.zeros(hi - lo, bool); badl[bi - lo] = True
            valid &= ~(badl[m - 1] | badl[m] | badl[m + 1])
        m = m[valid]; ntr += m.size
        A0, B0, Ap, Bp, An, Bn = a[m], b[m], a[m - 1], b[m - 1], a[m + 1], b[m + 1]
        sL = Ap * 8 + Bp * 4 + A0 * 2 + B0      # stratum for LATER sorts (prev+current settings)
        sE = A0 * 8 + B0 * 4 + An * 2 + Bn      # stratum for EARLIER sorts (current+next settings)
        s0 = A0 * 2 + B0
        cA, cB = clA[m], clB[m]
        joint = cA * 2 + cB
        # --- later vs earlier: clicks sorted by neighbour-trial settings
        for tag, S, key_a, key_b, strat in (('later', 16, An, Bn, sL), ('earlier', 16, Ap, Bp, sE)):
            add(f'{tag}|Aclick~Aset', S, 2, 2, strat, key_a, cA)
            add(f'{tag}|Aclick~Bset', S, 2, 2, strat, key_b, cA)
            add(f'{tag}|Bclick~Bset', S, 2, 2, strat, key_b, cB)
            add(f'{tag}|Bclick~Aset', S, 2, 2, strat, key_a, cB)
            add(f'{tag}|joint~jointset', S, 4, 4, strat, key_a * 2 + key_b, joint)
            ia = cA == 1; ib = cB == 1
            add(f'{tag}|Aslot~Aset', S, 2, 16, strat[ia], key_a[ia], slA[m][ia])
            add(f'{tag}|Aslot~Bset', S, 2, 16, strat[ia], key_b[ia], slA[m][ia])
            add(f'{tag}|Bslot~Bset', S, 2, 16, strat[ib], key_b[ib], slB[m][ib])
            add(f'{tag}|Bslot~Aset', S, 2, 16, strat[ib], key_a[ib], slB[m][ib])
        # --- cross-side click at lag +1 vs lag -1 (A now vs B next / B previous)
        add('later|Aclick~Bclick', 16, 2, 2, A0 * 8 + B0 * 4 + An * 2 + Bn, clB[m + 1], cA)
        add('earlier|Aclick~Bclick', 16, 2, 2, Ap * 8 + Bp * 4 + A0 * 2 + B0, clB[m - 1], cA)
        add('later|Bclick~Aclick', 16, 2, 2, A0 * 8 + B0 * 4 + An * 2 + Bn, clA[m + 1], cB)
        add('earlier|Bclick~Aclick', 16, 2, 2, Ap * 8 + Bp * 4 + A0 * 2 + B0, clA[m - 1], cB)
        # --- same-trial controls
        add('ctrl|joint~jointset_same', 1, 4, 4, np.zeros_like(s0), s0, joint)          # Bell correlation (must be huge)
        add('ctrl|Aclick~Bset_same', 2, 2, 2, A0, B0, cA)                              # no-signalling B->A
        add('ctrl|Bclick~Aset_same', 2, 2, 2, B0, A0, cB)                              # no-signalling A->B
        print(run, f'{en}/{N}', flush=True)
    np.savez(os.path.join(outdir, f'nist_tables_{run}.npz'), ntrials=ntr, **{k.replace('|', '__').replace('~', '_BY_'): v for k, v in T.items()})
    print('done', run, 'valid trials', ntr)

if __name__ == '__main__':
    out = os.path.expanduser('~/bones-forge/public_bell/results')
    for p in sys.argv[1:]:
        build(p, out)
