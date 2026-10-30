#!/usr/bin/env python3
"""known_good.py: rebuild Mandujano Reyes (arXiv 2608.22659) Table 1 and Table 3 from his released mmlu_pro_real_data.csv with our code.
Table 1: mean accuracy and naive SE sqrt(p(1-p)/n). Table 3: paired z on per-item differences (Miller Eq. 7, SE = sd(d)/sqrt(n), sd with n-1),
two-sided normal p, Bonferroni and Holm over 15 pairs at .05. Reads theirs/ as data only."""
import csv, os, math, itertools, collections
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs')
S = collections.defaultdict(dict); cat = {}
for r in csv.DictReader(open(T + '/mmlu_pro_real_data.csv')):
    S[r['model']][r['question_id']] = int(r['correct']); cat[r['question_id']] = r['category']
M = sorted(S); Q = sorted(set.intersection(*(set(S[m]) for m in M)), key=int); n = len(Q)
print('models', M); print('shared questions', n, '| rows per model', {m: len(S[m]) for m in M}, '| categories', len(set(cat.values())))
def phi(z): return 0.5 * math.erfc(-z / math.sqrt(2))
print('\nTable 1 rebuild: model, mean, naive SE')
for m in sorted(M, key=lambda m: -sum(S[m][q] for q in Q)):
    p = sum(S[m][q] for q in Q) / n; print('  %-26s %.3f  %.4f' % (m, p, math.sqrt(p * (1 - p) / n)))
rows = []
for a, b in itertools.combinations(M, 2):
    d = [S[a][q] - S[b][q] for q in Q]; mu = sum(d) / n; sd = math.sqrt(sum((x - mu) ** 2 for x in d) / (n - 1)); se = sd / math.sqrt(n)
    z = mu / se; p = 2 * (1 - phi(abs(z)))
    pa = sum(S[a][q] for q in Q) / n; pb = sum(S[b][q] for q in Q) / n; seu = math.sqrt(pa * (1 - pa) / n + pb * (1 - pb) / n); pu = 2 * (1 - phi(abs((pa - pb) / seu)))
    b10 = sum(1 for x in d if x == 1); b01 = sum(1 for x in d if x == -1)
    rows.append(dict(a=a, b=b, diff=mu, se=se, z=z, p=p, pu=pu, seu=seu, b10=b10, b01=b01))
rows.sort(key=lambda r: r['p']); K = len(rows)
for i, r in enumerate(rows):   # Holm step-down
    r['bonf'] = r['p'] < 0.05 / K
    r['holm'] = all(rows[j]['p'] < 0.05 / (K - j) for j in range(i + 1))
print('\nTable 3 rebuild (paired z), sorted by p: A - B, diff, SE, p, unc/bonf/holm, discordant A-only / B-only, unpaired p')
for r in rows:
    print('  %-26s %-26s %+.4f %.4f  p %.4f  %s %s %s   %4d / %-4d  unpaired p %.4f' % (r['a'], r['b'], r['diff'], r['se'], r['p'], 'U' if r['p'] < .05 else '-', 'B' if r['bonf'] else '-', 'H' if r['holm'] else '-', r['b10'], r['b01'], r['pu']))
print('\nunc %d, bonferroni %d, holm %d of %d' % (sum(r['p'] < .05 for r in rows), sum(r['bonf'] for r in rows), sum(r['holm'] for r in rows), K))

# Tables 5 and 4: omnibus F with and without question blocking, Friedman, and the Eq. 3 contrasts through the identity his paper reports
# (the full mixed model's residual equals the question-blocked ANOVA residual mean square, contrast SE = sqrt(2 MSres / n)).
import numpy as np
X = np.array([[S[m][q] for m in M] for q in Q], float); K_ = len(M); g = X.mean()
ss_tot = ((X - g) ** 2).sum(); ss_mod = n * ((X.mean(0) - g) ** 2).sum(); ss_q = K_ * ((X.mean(1) - g) ** 2).sum()
ss_res = ss_tot - ss_mod - ss_q; df_m, df_r = K_ - 1, (n - 1) * (K_ - 1); ms_res = ss_res / df_r; F_rm = (ss_mod / df_m) / ms_res
F_naive = (ss_mod / df_m) / ((ss_tot - ss_mod) / (n * K_ - K_))
from math import lgamma, exp, log
def f_sf(F, d1, d2):   # survival of F via the regularized incomplete beta (continued fraction), stdlib only
    x = d2 / (d2 + d1 * F); a, b = d2 / 2, d1 / 2
    def cf(a, b, x):
        qab, qap, qam = a + b, a + 1, a - 1; c, d = 1.0, 1 - qab * x / qap; d = 1 / d; h = d
        for m in range(1, 400):
            m2 = 2 * m; aa = m * (b - m) * x / ((qam + m2) * (a + m2)); d = 1 / (1 + aa * d); c = 1 + aa / c; h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2)); d = 1 / (1 + aa * d); c = 1 + aa / c; h *= d * c
        return h
    bt = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log(1 - x)); return bt * cf(a, b, x) / a
print('\nTable 5 rebuild: naive one-way F(%d,%d) = %.2f p %.3f | question-blocked F(%d,%d) = %.2f p %.1e | residual MS %.4f' % (df_m, n * K_ - K_, F_naive, f_sf(F_naive, df_m, n * K_ - K_), df_m, df_r, F_rm, f_sf(F_rm, df_m, df_r), ms_res))
R_ = np.apply_along_axis(lambda r: np.argsort(np.argsort(r)) * 0 + np.array([ (r < v).sum() + ((r == v).sum() + 1) / 2 for v in r]), 1, X)
Rj = R_.sum(0); tie = sum(((np.unique(r, return_counts=True)[1]) ** 3 - np.unique(r, return_counts=True)[1]).sum() for r in X)
chi = (12 / (n * K_ * (K_ + 1)) * (Rj ** 2).sum() - 3 * n * (K_ + 1)) / (1 - tie / (n * (K_ ** 3 - K_)))
def chi2_sf(x, k):   # k = 5 odd: closed form via the incomplete gamma series
    s, t = 0.0, exp(-x / 2) * (x / 2) ** (k / 2) / exp(lgamma(k / 2 + 1)); j = 0
    while t > 1e-18: s += t; j += 1; t *= (x / 2) / (k / 2 + j)
    return 1 - s
print('Friedman chi2(%d) = %.1f p %.1e (tie-corrected)' % (K_ - 1, chi, chi2_sf(chi, K_ - 1)))
se_c = math.sqrt(2 * ms_res / n); print('Eq. 3 contrast SE through the identity: %.4f' % se_c)
t4 = sorted(({'a': a, 'b': b, 'd': X[:, M.index(a)].mean() - X[:, M.index(b)].mean()} for a, b in itertools.combinations(M, 2)), key=lambda r: -abs(r['d']))
print('Table 4 rebuild, top rows: A - B, diff, raw p (z against the pooled SE)')
for r in t4[:7]: z = r['d'] / se_c; print('  %-26s %-26s %+.4f  raw p %.4f' % (r['a'], r['b'], r['d'], 2 * (1 - phi(abs(z)))))
