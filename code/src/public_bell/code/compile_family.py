"""Collect every later/earlier/far sort, pick one p per test, correct for the number of tests."""
import json, os, numpy as np
from scipy.stats import norm
R = os.path.expanduser('~/bones-forge/public_bell/results')
files = ['nist_main6_results.json', 'nist_blind_results.json', 'weihs_longdist_results.json', 'weihs_longtime_results.json',
         'small_sets_results.json', 'illinois_results.json']
rows = []
for f in files:
    for r in json.load(open(os.path.join(R, f))):
        r['file'] = f; rows.append(r)
fam = []
for r in rows:
    tag = r['sort'].split('|')[0]
    if tag not in ('later', 'earlier', 'farlater', 'farearlier'):
        continue
    if 'Bclick~Aclick' in r['sort']:
        continue                      # exact duplicates of the Aclick~Bclick pairs (same trial pairs)
    ps = r['p_shuffle']; Rn = r.get('R', 2000) or 2000
    if ps <= 1.0 / (Rn + 1) + 1e-12:  # observed beyond every shuffle: use normal tail of z vs shuffle
        p = float(norm.sf(r['z_vs_shuffle']))
    else:
        p = ps
    fam.append(dict(dataset=r['dataset'], part=r['part'], sort=r['sort'], tag=tag, p=p, z=r['z_vs_shuffle'], N=r['N'], effect=r.get('effect', '')))
n = len(fam)
ps = np.array([x['p'] for x in fam])
order = np.argsort(ps); q = np.empty(n)
q[order] = np.minimum.accumulate((ps[order] * n / (np.arange(n) + 1))[::-1])[::-1]
for x, qq in zip(fam, q):
    x['bonferroni'] = min(1.0, x['p'] * n); x['bh_q'] = float(min(1.0, qq))
json.dump(fam, open(os.path.join(R, 'family_all_sorts.json'), 'w'), indent=1)
print('total sorts in family:', n)
for tag in ('later', 'earlier', 'farlater', 'farearlier'):
    sub = [x for x in fam if x['tag'] == tag]
    print(f"{tag:11s} n={len(sub):4d}  p<0.05: {sum(x['p'] < 0.05 for x in sub):3d} (expect {0.05*len(sub):.1f})  p<0.01: {sum(x['p'] < 0.01 for x in sub):3d} (expect {0.01*len(sub):.1f})  survive Bonferroni: {sum(x['bonferroni'] < 0.05 for x in sub)}  BH q<0.05: {sum(x['bh_q'] < 0.05 for x in sub)}")
print('\nsmallest 15:')
for x in sorted(fam, key=lambda x: x['p'])[:15]:
    print(f"{x['dataset']:16s} {x['part'][:30]:30s} {x['sort']:34s} p={x['p']:.2g} z={x['z']:+.1f} bonf={x['bonferroni']:.2g} q={x['bh_q']:.2g} {x['effect'][:70]}")
by = {}
for x in fam:
    by.setdefault(x['dataset'], []).append(x)
print()
for d, L in by.items():
    print(f"{d:18s} tests={len(L):4d} min p={min(x['p'] for x in L):.2g}  p<0.05: {sum(x['p']<0.05 for x in L)}")
