"""Follow-up (found post hoc): click rate vs own setting at lag L (L=-6..+6), conditioned on the current
trial's two settings. Directed, stratum-adjusted relative change; per run and pooled."""
import h5py, numpy as np, glob, os, json
CH = 5_000_000
LAGS = [l for l in range(-6, 7) if l != 0]
out = {}
for fn in sorted(glob.glob(os.path.expanduser('~/bones-forge/public_bell/nist2015/*.hdf5'))):
    run = os.path.basename(fn).split('.dat')[0]
    f = h5py.File(fn, 'r'); N = f['alice/settings'].shape[0]
    T = {(side, key, L): np.zeros((4, 2, 2)) for side in 'AB' for key in 'AB' for L in LAGS}
    for st in range(6, N - 6, CH):
        en = min(st + CH, N - 6); lo, hi = st - 6, en + 6
        sa = f['alice/settings'][lo:hi].astype(np.int64); sb = f['bob/settings'][lo:hi].astype(np.int64)
        ca = (f['alice/clicks'][lo:hi] > 0).astype(np.int64); cb = (f['bob/clicks'][lo:hi] > 0).astype(np.int64)
        ok = ((sa == 1) | (sa == 2)) & ((sb == 1) | (sb == 2)); a = sa - 1; b = sb - 1
        m = np.arange(6, hi - lo - 6)
        v = ok[m].copy()
        for L in LAGS: v &= ok[m + L]
        m = m[v]; s0 = a[m] * 2 + b[m]
        for L in LAGS:
            for key, arr in (('A', a), ('B', b)):
                k = arr[m + L]
                for side, c in (('A', ca), ('B', cb)):
                    T[(side, key, L)] += np.bincount((s0 * 2 + k) * 2 + c[m], minlength=16).reshape(4, 2, 2)
    out[run] = {f'{s}click~{k}set@{L:+d}': T[(s, k, L)].tolist() for (s, k, L) in T}
    print('done', run, flush=True)
json.dump(out, open(os.path.expanduser('~/bones-forge/public_bell/results/nist_lagprofile_tables.json'), 'w'))
