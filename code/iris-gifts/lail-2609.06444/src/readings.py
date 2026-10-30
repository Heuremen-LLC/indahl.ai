#!/usr/bin/env python3
"""L1-L3 (PLAN 3b3c6f5, committed before this ran). Lail, arXiv 2609.06444. Our code; their files read as data, nothing of theirs run."""
import os, sys, json, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from known_good import load_items, judge, half_split, T
uids, counts, old = load_items(); q, conf, _ = judge(uids); N = len(uids)
freq = counts / 100.0; jerr = np.abs(q - freq).sum(1)
# L1
print('L1 the distance feature on labelled items (their build_features and fit_dcm, read; our reveal draw in their scheme)')
z = np.load(T + '/repo/chaosnli/embeddings_minilm.npz'); assert list(z['uids']) == uids, 'embedding order differs from item order'
E = z['embeddings'].astype(np.float64); En = E / np.linalg.norm(E, axis=1, keepdims=True)
rng = np.random.default_rng(0); n = rng.choice(np.array([0, 1, 2, 5, 10]), size=N); lab = n > 0
D = 1 - En @ En[lab].T          # cosine distance, as scipy cdist(metric='cosine')
S = np.sort(D, axis=1); near = S[:, 0]; dens = S[:, :10].mean(1)
selfd = np.full(N, np.nan); idx = np.where(lab)[0]; selfd[idx] = D[idx, np.arange(len(idx))]
print('  labelled items %d, zero-label items %d' % (lab.sum(), (~lab).sum()))
print('  labelled items whose own distance is the nearest (0 up to float rounding, max %.1e): %d of %d' % (np.nanmax(np.abs(selfd)), int((np.abs(near[lab] - selfd[lab]) < 1e-12).sum()), lab.sum()))
zc = (near - near.mean()) / near.std()
print('  standardised nearest-distance column: spread inside the fit set (labelled) sd %.2e, range %.2e | over zero-label items sd %.3f, range [%.2f, %.2f]' % (zc[lab].std(), np.ptp(zc[lab]), zc[~lab].std(), zc[~lab].min(), zc[~lab].max()))
dup = int(((1 - En @ En.T) + np.eye(N) * 9 < 1e-9).any(1).sum()); print('  items with an exact embedding duplicate elsewhere: %d' % dup)
S2 = np.sort(D + np.where(np.isclose(D, selfd[:, None]) & lab[:, None] & (np.arange(D.shape[1])[None, :] == np.searchsorted(idx, np.arange(N))[:, None]), 9, 0), axis=1)
dens_noself = np.where(lab, np.sort(np.where((np.arange(D.shape[1])[None, :] == np.searchsorted(idx, np.arange(N))[:, None]) & lab[:, None], 9, D), axis=1)[:, :10].mean(1), dens)
print('  10-nearest density column: labelled mean %.4f as computed (self included) against %.4f with self left out | zero-label mean %.4f' % (dens[lab].mean(), dens_noself[lab].mean(), dens[~lab].mean()))
# L2
print('\nL2 five labels against the judge, Manhattan units (0-2)')
M = {'entailment': 0, 'neutral': 1, 'contradiction': 2}
why = collections.Counter(); ok = np.zeros(N, bool); o5 = np.zeros((N, 3))
for i, ol in enumerate(old):
    if not ol: why['no old labels'] += 1; continue
    if len(ol) != 5: why['%d old labels' % len(ol)] += 1; continue
    if any(x not in M for x in ol): why['label outside e/n/c'] += 1; continue
    ok[i] = True
    for x in ol: o5[i, M[x]] += 0.2
print('  items with five valid old labels %d of %d | left out by reason %s' % (ok.sum(), N, dict(why)))
print('  old five unanimous on %d items (ChaosNLI chose items for disagreement among them)' % int((o5[ok].max(1) == 1).sum()))
def boot(x, B=10000, seed=42):
    r = np.random.default_rng(seed); m = np.array([x[r.integers(0, len(x), len(x))].mean() for _ in range(B)]); return np.percentile(m, [2.5, 97.5])
oerr = np.abs(o5 - freq).sum(1)
d = jerr[ok] - oerr[ok]; lo, hi = boot(d)
print('  (a) against all 100 labels, n %d: judge %.4f | old five %.4f | judge minus old five %+.4f [%+.4f, %+.4f] | judge closer on %d items, old five closer on %d, tied %d' % (
    ok.sum(), jerr[ok].mean(), oerr[ok].mean(), d.mean(), lo, hi, int((d < 0).sum()), int((d > 0).sum()), int((d == 0).sum())))
rng = np.random.default_rng(0); J, O, F, C = (np.zeros(N) for _ in range(4)); K = 200
for s in range(K):
    a, b = half_split(counts, rng); tb = b / 50.0
    f5 = np.zeros_like(a); draw = np.full(N, 5); pool = a.sum(1).copy()
    for j in range(3):
        t = rng.hypergeometric(a[:, j], pool - a[:, j], draw); f5[:, j] = t; draw -= t; pool -= a[:, j]
    J += np.abs(q - tb).sum(1); O += np.abs(o5 - tb).sum(1); F += np.abs(f5 / 5.0 - tb).sum(1); C += np.abs(a / 50.0 - tb).sum(1)
J, O, F, C = J / K, O / K, F / K, C / K
print('  (b) against a 50-label half, %d random half-splits, per-item means:' % K)
print('      all %d items: judge %.4f | five fresh labels from the other half %.4f | the other 50-label half (noise ceiling) %.4f' % (N, J.mean(), F.mean(), C.mean()))
d = J - F; lo, hi = boot(d); print('      judge minus five fresh labels %+.4f [%+.4f, %+.4f] | judge closer on %d items, five fresh closer on %d' % (d.mean(), lo, hi, int((d < 0).sum()), int((d > 0).sum())))
d = J[ok] - O[ok]; lo, hi = boot(d); print('      n %d with five old labels: judge %.4f | old five %.4f | judge minus old five %+.4f [%+.4f, %+.4f]' % (ok.sum(), J[ok].mean(), O[ok].mean(), d.mean(), lo, hi))
for nm, src in (('snli', 'snli'), ('mnli_m', 'mnli')):
    m = np.array([u for u in range(N)]) < sum(1 for _ in open('%s/chaosnli_mirror/raw/chaosNLI_snli.jsonl' % T)) if nm == 'snli' else None
    if m is None: m = ~(np.arange(N) < sum(1 for _ in open('%s/chaosnli_mirror/raw/chaosNLI_snli.jsonl' % T)))
    d = J[m] - F[m]; lo, hi = boot(d); print('      %-6s n %4d: judge %.4f | five fresh %.4f | difference %+.4f [%+.4f, %+.4f]' % (nm, m.sum(), J[m].mean(), F[m].mean(), d.mean(), lo, hi))
# L3
print('\nL3 Appendix C: self-update 0.258, conjugate with the familiarity channel 0.262, without 0.307 (paper text and dice/RESULTS.md line 174).')
v = {'self-update': 0.258, 'conjugate, familiarity channel': 0.262, 'conjugate, base': 0.307}
print('  lowest error (better):', min(v, key=v.get), '| order:', ' < '.join('%s %.3f' % (k, x) for k, x in sorted(v.items(), key=lambda t: t[1])), '| per-die values not rebuilt, no interval on the 0.004 gap')
# L2c (PLAN Addendum 1, defined after the data)
print('\nL2c (defined after the data) k fresh labels from one half against the other half, same 200 splits (seed 0 sequence restarted)')
rng = np.random.default_rng(0); Fk = {k: np.zeros(N) for k in range(1, 6)}; Jc = np.zeros(N)
for s in range(K):
    a, b = half_split(counts, rng); tb = b / 50.0; Jc += np.abs(q - tb).sum(1)
    for k in range(1, 6):
        fk = np.zeros_like(a); draw = np.full(N, k); pool = a.sum(1).copy()
        for j in range(3):
            t = rng.hypergeometric(a[:, j], pool - a[:, j], draw); fk[:, j] = t; draw -= t; pool -= a[:, j]
        Fk[k] += np.abs(fk / float(k) - tb).sum(1)
print('  judge %.4f | ' % (Jc.mean() / K) + ' | '.join('%d fresh %.4f' % (k, Fk[k].mean() / K) for k in range(1, 6)))
# L2d (PLAN Addendum 2, defined after the data)
print('\nL2d (defined after the data) the original five-label panel')
pat = collections.Counter('-'.join(str(x) for x in sorted([int(round(v * 5)) for v in o5[i] if v > 0], reverse=True)) for i in range(N) if ok[i])
print('  agreement pattern over %d items: %s' % (ok.sum(), dict(pat)))
nsnli = sum(1 for _ in open('%s/chaosnli_mirror/raw/chaosNLI_snli.jsonl' % T)); src = np.arange(N) < nsnli
for nm, m in (('snli', src & ok), ('mnli_m', (~src) & ok)):
    d = jerr[m] - oerr[m]; lo, hi = boot(d)
    print('  %-6s n %4d: judge %.4f | old five %.4f | judge minus old five %+.4f [%+.4f, %+.4f]' % (nm, m.sum(), jerr[m].mean(), oerr[m].mean(), d.mean(), lo, hi))
