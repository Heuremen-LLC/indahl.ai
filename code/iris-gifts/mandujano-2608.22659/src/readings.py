#!/usr/bin/env python3
"""G1-G6 (PLAN d4ec250 and Addendum 1 82d0f7d), all defined after reading his paper (G6 after K2). Our code, his CSV and TIGER-Lab's
released outputs read as data only."""
import csv, json, zipfile, os, math, itertools, collections, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); T = H + '/../theirs'
UP = {'Mistral-7B-Instruct-v0.1': 'Mistral-7B-Instruct-v0.1', 'Mistral-7B-Instruct-v0.2': 'Mistral-7B-Instruct-v0.2', 'Mistral-7B-v0.1': 'Mistral-7B-v0.1',
      'Qwen1.5-7B-Chat': 'Qwen1.5-7B-Chat', 'Yi-6B': 'Yi-6B', 'Yi-6B-Chat': 'Yi-6b-Chat'}
S = collections.defaultdict(dict)
for r in csv.DictReader(open(T + '/mmlu_pro_real_data.csv')): S[r['model']][r['question_id']] = int(r['correct'])
M = sorted(S); Q = sorted(S[M[0]], key=int); n = len(Q); X = np.array([[S[m][q] for m in M] for q in Q], float)
NL = np.zeros_like(X, bool); NOPT = np.zeros(n)
for j, m in enumerate(M):
    z = zipfile.ZipFile(T + '/upstream/%s.zip' % UP[m]); up = {str(x['question_id']): x for x in json.loads(z.read(z.infolist()[0].filename))}
    for i, q in enumerate(Q): NL[i, j] = up[q]['pred'] is None; NOPT[i] = len(up[q]['options'])
phi = lambda z: 0.5 * math.erfc(-z / math.sqrt(2))
def pz(d):   # paired z on per-item differences (Miller Eq. 7)
    k = len(d); mu = d.mean(); se = d.std(ddof=1) / math.sqrt(k); return (2 * (1 - phi(abs(mu / se))) if se > 0 else 1.0), mu
def pu(a, b):
    pa, pb = a.mean(), b.mean(); se = math.sqrt(pa * (1 - pa) / len(a) + pb * (1 - pb) / len(b)); return 2 * (1 - phi(abs((pa - pb) / se)))
def mcnemar(b, c):   # exact two-sided binomial on discordant items
    N = b + c; k = min(b, c); s = sum(math.comb(N, i) for i in range(k + 1)) / 2 ** N; return min(1.0, 2 * s)
def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); keep = [False] * len(ps)
    for r, i in enumerate(o):
        if ps[i] < 0.05 / (len(ps) - r): keep[i] = True
        else: break
    return keep
def ms_res(X):
    g = X.mean(); N, K = X.shape; ss = ((X - g) ** 2).sum() - N * ((X.mean(0) - g) ** 2).sum() - K * ((X.mean(1) - g) ** 2).sum(); return ss / ((N - 1) * (K - 1))
P = list(itertools.combinations(range(len(M)), 2)); nm = lambda i: M[i].replace('Mistral-7B-', 'M-').replace('Instruct-', 'Inst-').replace('-Chat', 'Chat')
def table(X):
    se3 = math.sqrt(2 * ms_res(X) / len(X)); out = []
    for a, b in P:
        d = X[:, a] - X[:, b]; p, mu = pz(d); out.append(dict(p=p, mu=mu, pu=pu(X[:, a], X[:, b]), p3=2 * (1 - phi(abs(mu / se3))),
                   pm=mcnemar(int((d > 0).sum()), int((d < 0).sum())), b10=int((d > 0).sum()), b01=int((d < 0).sum())))
    for key in ('p', 'pu', 'p3', 'pm'):
        h = holm([r[key] for r in out])
        for r, k in zip(out, h): r[key + '_holm'] = k; r[key + '_bonf'] = r[key] < 0.05 / len(P)
    return out
t = table(X)
print('G1 and G2 and G3: per pair, p under four rulers; U = uncorrected .05, B = Bonferroni, H = Holm')
print('%-22s %-22s  %-8s %-14s %-14s %-14s %-14s' % ('A', 'B', 'diff', 'paired z', 'unpaired z', 'exact McNemar', 'Eq.3 identity'))
f = lambda r, k: '%.4f %s%s%s' % (r[k], 'U' if r[k] < .05 else '-', 'B' if r[k + '_bonf'] else '-', 'H' if r[k + '_holm'] else '-')
for (a, b), r in sorted(zip(P, t), key=lambda x: x[1]['p']):
    print('%-22s %-22s  %+.4f  %-14s %-14s %-14s %-14s' % (nm(a), nm(b), r['mu'], f(r, 'p'), f(r, 'pu'), f(r, 'pm'), f(r, 'p3')))
for k, lab in (('p', 'paired z'), ('pu', 'unpaired z'), ('pm', 'exact McNemar'), ('p3', 'Eq.3 identity')):
    print('  %-14s uncorrected %d, Bonferroni %d, Holm %d of 15' % (lab, sum(r[k] < .05 for r in t), sum(r[k + '_bonf'] for r in t), sum(r[k + '_holm'] for r in t)))
print('  paired p below unpaired p on %d of 15 pairs' % sum(r['p'] < r['pu'] for r in t))
# G4: fewest single-item score changes that move Mistral-7B-v0.1 vs Yi-6B across its line, greedy and exact at each step
A, Bq = M.index('Mistral-7B-v0.1'), M.index('Yi-6B'); pi = P.index((A, Bq))
def status(X): r = table(X)[pi]; return {k: (r[k], r[k + '_bonf'], r[k + '_holm']) for k in ('p', 'pm', 'p3')}
print('\nG4: Mistral-7B-v0.1 vs Yi-6B, fewest single-item score changes to cross each line (each step picks the change that moves p most)')
moves = [('M 1->0 where Yi 1', A, 1, Bq, 1), ('M 1->0 where Yi 0', A, 1, Bq, 0), ('Yi 0->1 where M 0', Bq, 0, A, 0), ('Yi 0->1 where M 1', Bq, 0, A, 1)]
anti = [('M 0->1 where Yi 0', A, 0, Bq, 0), ('M 0->1 where Yi 1', A, 0, Bq, 1), ('Yi 1->0 where M 1', Bq, 1, A, 1), ('Yi 1->0 where M 0', Bq, 1, A, 0)]
for key, lab in (('p', 'paired z'), ('pm', 'exact McNemar'), ('p3', 'Eq.3 identity')):
    for rule, ri in (('Bonferroni', 1), ('Holm', 2)):
        s0 = status(X)[key][ri]; mv = moves if s0 else anti; Y = X.copy(); steps = []
        for k in range(1, 40):
            best = None
            for name, col, frm, oc, ov in mv:
                rows = np.where((Y[:, col] == frm) & (Y[:, oc] == ov))[0]
                if not len(rows): continue
                Z = Y.copy(); Z[rows[0], col] = 1 - frm; st = status(Z)[key]; score = st[0] if s0 else -st[0]
                if best is None or score > best[0]: best = (score, name, Z, st)
            Y = best[2]; steps.append(best[1])
            if best[3][ri] != s0: break
        print('  %-14s %-10s now %-9s -> %s after %d change(s): %s (p %.4f)' % (lab, rule, 'passes' if s0 else 'fails', 'fails' if s0 else 'passes', len(steps), ', '.join(collections.Counter(steps).keys()), best[3][0]))
# G6
print('\nG6a: no-letter share per model, 95% Wilson')
def wil(k, N, z=1.96):
    p = k / N; d = 1 + z * z / N; c = p + z * z / (2 * N); h = z * math.sqrt(p * (1 - p) / N + z * z / (4 * N * N)); return (c - h) / d, (c + h) / d
for j, m in enumerate(M): k = int(NL[:, j].sum()); print('  %-26s %4d of %d  %.3f [%.3f, %.3f]' % (m, k, n, k / n, *wil(k, n)))
print('\nG6b: discordant items per pair, split by reason (both gave a letter / one side gave no letter)')
for (a, b), r in sorted(zip(P, t), key=lambda x: x[1]['p'])[:6]:
    d = X[:, a] - X[:, b]; disc = d != 0; one = disc & (NL[:, a] ^ NL[:, b]); both = disc & ~NL[:, a] & ~NL[:, b]
    print('  %-22s %-22s discordant %3d: both-letter %3d, one-side-no-letter %3d (no-letter on A %d, on B %d)' % (nm(a), nm(b), disc.sum(), both.sum(), one.sum(), (one & NL[:, a]).sum(), (one & NL[:, b]).sum()))
print('\nG6c: paired z on items where both models gave a letter (each pair on its own item set); G6d: paired z under the benchmark rule (TIGER-Lab save_res, a guess among the options, scored by its expectation 1/options; realized guesses are not stored); Holm over 15 each')
c_ps, d_ps, rows = [], [], []
Xd = np.where(NL, 1 / NOPT[:, None], X)
for a, b in P:
    keep = ~NL[:, a] & ~NL[:, b]; pc, muc = pz(X[keep, a] - X[keep, b]); pd, mud = pz(Xd[:, a] - Xd[:, b]); c_ps.append(pc); d_ps.append(pd); rows.append((a, b, keep.sum(), muc, pc, mud, pd))
hc, hd = holm(c_ps), holm(d_ps)
for (a, b, k, muc, pc, mud, pd), x, y, r in sorted(zip(rows, hc, hd, t), key=lambda z: z[3]['p']):
    print('  %-22s %-22s his file %s | letters-only n %4d %+.4f p %.4f %s | benchmark rule %+.4f p %.4f %s' % (nm(a), nm(b), 'H' if r['p_holm'] else ('U' if r['p'] < .05 else '-'), k, muc, pc, 'H' if x else ('U' if pc < .05 else '-'), mud, pd, 'H' if y else ('U' if pd < .05 else '-')))
print('  Holm survivors: his file %d, letters-only per pair %d, benchmark rule %d' % (sum(r['p_holm'] for r in t), sum(hc), sum(hd)))
common = ~NL.any(1); cps = [pz(X[common, a] - X[common, b])[0] for a, b in P]; hcm = holm(cps)
print('G6c on one common set (all six gave a letter, n %d): uncorrected %d, Bonferroni %d, Holm %d of 15' % (common.sum(), sum(p < .05 for p in cps), sum(p < .05 / 15 for p in cps), sum(hcm)))
for (a, b), p_, k in sorted(zip(P, cps, hcm), key=lambda x: x[1])[:5]: print('  %-22s %-22s p %.4f %s' % (nm(a), nm(b), p_, 'H' if k else ('U' if p_ < .05 else '-')))
