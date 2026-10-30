#!/usr/bin/env python3
"""K and M1-M4 (PLAN b035956, committed before this ran). Maiorano, arXiv 2609.25010. Our code; his report files and script read as data."""
import json, os, re, statistics
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'repo')
bc = json.load(open(R + '/reports/baseline_comparison.json')); rp = json.load(open(R + '/reports/replication.json'))
print('K Table 1 against reports/baseline_comparison.json (printed n = 399)')
T1 = {'baseline': (49.2, 44.2, 54.3, 0.361, 0.289, 0.430, 0.350, 0.281, 0.417), 'panel': (34.6, 29.8, 39.1, 0.084, 0.020, 0.147, 0.104, 0.035, 0.172)}
for arm, p in T1.items():
    b = bc[arm]; ours = (100 * b['top1']['mean'], 100 * b['top1']['ci'][0], 100 * b['top1']['ci'][1], b['tau']['mean'], *b['tau']['ci'], b['rho']['mean'], *b['rho']['ci'])
    ok = all(round(o, 1 if k < 3 else 3) == x for k, (o, x) in enumerate(zip(ours, p)))
    print('  %-8s n %d | printed equals report on all nine values: %s' % (arm, b['n'], ok))
print('K Table 2 against reports/replication.json (persona tau, baseline tau, lift persona/baseline; n per arm)')
T2 = {'exploratory': (399, 0.079, 0.361, 0.45, 0.58), 'holdout': (402, 0.100, 0.398, 0.48, 0.56), 'confirmatory': (1866, 0.070, 0.393, 0.44, 0.55),
      'mind-news': (74, 0.177, 0.214, 0.47, 0.51), 'reddit-titles': (600, -0.009, -0.026, 0.45, 0.33)}
for k, (n, pt, bt, pl, bl) in T2.items():
    p, b = rp[k]['persona'], rp[k]['baseline']
    ok = (p['n'] == n and round(p['kendall_tau']['mean'], 3) == pt and round(b['kendall_tau']['mean'], 3) == bt and round(p['lift_captured']['mean'], 2) == pl and round(b['lift_captured']['mean'], 2) == bl)
    print('  %-13s printed equals report: %s | n persona %d, baseline %d' % (k, ok, p['n'], b['n']))
print('\nM1 the Reddit row (reports/replication.json, his 95% intervals)')
p, b = rp['reddit-titles']['persona'], rp['reddit-titles']['baseline']
for m in ('top1', 'lift_captured', 'kendall_tau'):
    print('  %-14s persona %.3f [%.3f, %.3f] | baseline %.3f [%.3f, %.3f] | intervals overlap: %s' % (m, p[m]['mean'], *p[m]['ci95'], b[m]['mean'], *b[m]['ci95'], not (p[m]['ci95'][0] > b[m]['ci95'][1] or b[m]['ci95'][0] > p[m]['ci95'][1])))
print('  lift, baseline above persona by split:', {k: rp[k]['baseline']['lift_captured']['mean'] > rp[k]['persona']['lift_captured']['mean'] for k in T2})
print('\nM2 the rank coefficient in scripts/compute_validity.py')
src = open(R + '/scripts/compute_validity.py').read(); f = src[src.index('def kendall_tau'):src.index('def top1')]
print('  returns (concordant - discordant) / (concordant + discordant), tied pairs counted in neither:', bool(re.search(r'denom = conc \+ disc', f) and re.search(r'\(conc - disc\) / denom', f)))
print('  returns None when every pair is tied:', 'if denom else None' in f)
t = json.load(open(R + '/reports/baseline_ties.json')); print('  baseline_ties.json: n %d, all variants tied on %.4f of packages (%d)' % (t['n_packages'], t['tie_rate'], round(t['tie_rate'] * t['n_packages'])))
print('\nM3 the GPT-4.1 rerun (reports/crossfamily_gpt41.json)')
g = json.load(open(R + '/reports/crossfamily_gpt41.json'))
print('  persona draws %d, baseline draws %d | packages: persona %d, baseline %d, paired %d' % (g['draws'], g['baseline_draws'], g['persona_panel']['n_packages'], g['no_persona_baseline']['n_packages'], g['paired_gap']['n_paired']))
print('\nM4 seed spread (reports/stability.json)')
s = json.load(open(R + '/reports/stability.json'))
for k in ('tau', 'top1'):
    print('  %-5s seeds %s | population SD %.4f | sample SD %.4f | stored %.4f' % (k, s[k], statistics.pstdev(s[k]), statistics.stdev(s[k]), s[k + '_sd']))
# M2b (PLAN Addendum 1, defined after the data)
print('\nM2b (defined after the data) analyze() appends tau only when it is not None; n_packages counts every package')
print('  tau left out when None:', 'if t is not None:\n            taus.append(t)' in src, '| mean over the kept taus:', '"kendall_tau": {"mean": sum(taus) / len(taus)' in src)
nb = bc['baseline']['n']; kt = round(t['tie_rate'] * t['n_packages']); mb = bc['baseline']['tau']['mean']
print('  baseline tau %.3f over %d of %d packages; with the %d all-tied packages counted as 0: %.3f | panel tau %.3f' % (mb, nb - kt, nb, kt, mb * (nb - kt) / nb, bc['panel']['tau']['mean']))
# M2c, M3b (PLAN Addendum 2, defined after the data)
mr = bc['baseline']['rho']['mean']
print('\nM2c (defined after the data) baseline rho %.3f over the packages with a defined rho; with the %d all-tied packages counted as 0: %.3f | panel rho %.3f' % (mr, kt, mr * (nb - kt) / nb, bc['panel']['rho']['mean']))
t2 = open(R + '/scripts/tier2_crossmodel.py').read()
print('\nM3b (defined after the data) scripts/tier2_crossmodel.py mentions "seed": %s | lines %d' % ('seed' in t2.lower(), t2.count('\n')))
