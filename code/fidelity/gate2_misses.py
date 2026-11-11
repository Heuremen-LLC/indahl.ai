#!/usr/bin/env python3
"""gate2_misses.py (post-referee, 11 Nov 2026): lists the state-years where the NCHS count over the ACS population does not round to the printed NCHS rate within 0.1
(the gate 2 rate check in make_rows.py), and tests the 2016 and 2017 divorce count columns with the two years swapped. Writes data/gate2_rate_misses.csv and
data/gate2_swap_check.json. Offline. Re-classes nothing: the scored readings stay as read from the count table as printed."""
import json, os, sys, csv
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import make_rows as M
nchs = json.load(open('data/nchs_counts.json')); acs = M.load_acs()
rates = {'divorce': M.load_rates('raw/state-divorce-rates-90-95-00-24.xlsx'), 'marriage': M.load_rates('raw/state-marriage-rates-90-95-00-24.xlsx')}
miss = []; total = 0
for ev, (k, tab) in M.EV.items():
    for st, v in nchs[k].items():
        if st == 'United States': continue
        for y in M.YEARS:
            if y > 2023 or v[y - 2000] is None or (st, y) not in acs: continue
            r = rates[k].get(st, {}).get(y)
            if r is None: continue
            total += 1; pop = float(acs[(st, y)]['B01003_001E']); calc = v[y - 2000] / pop * 1000
            if abs(calc - r) > 0.1 + 1e-9: miss.append(dict(event=ev, state=st, year=y, nchs_count=v[y - 2000], acs_population=int(pop), count_per_1000=round(calc, 2), printed_rate=r, difference=round(calc - r, 2)))
miss.sort(key=lambda m: (m['event'], m['year'], m['state']))
with open('data/gate2_rate_misses.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(miss[0])); w.writeheader(); w.writerows(miss)
D = nchs['divorce']; dmiss = [m for m in miss if m['event'] == 'DIVORCE' and m['year'] in (2016, 2017)]
swap = []; flips = []
for st in sorted({m['state'] for m in dmiss}):
    fit = True; ok = True; rr = []
    for y, o in ((2016, 2017), (2017, 2016)):
        n = D[st][o - 2000]; r = rates['divorce'][st].get(y)
        if n is None or r is None: ok = False; continue
        pop = float(acs[(st, y)]['B01003_001E']); fit &= abs(n / pop * 1000 - r) <= 0.1 + 1e-9
        iv = M.interval(acs[(st, y)]['B12503_010E'], acs[(st, y)]['B12503_010M'])
        a = M.outcome(D[st][y - 2000], iv, y)[0]; b = M.outcome(n, iv, y)[0]
        rr.append(dict(year=y, read_as_printed=a, read_swapped=b))
        if a != b: flips.append(dict(state=st, year=y, as_printed=a, swapped=b))
    swap.append(dict(state=st, swapped_counts_fit_both_rates=bool(ok and fit), years=rr))
flips = [f for f in flips if next(s for s in swap if s['state'] == f['state'])['swapped_counts_fit_both_rates']]
out = dict(compared=total, within_tenth=total - len(miss), misses=len(miss), misses_by_event_year={'%s %d' % (m['event'], m['year']): 0 for m in miss},
           divorce_2016_17_misses=[(m['state'], m['year']) for m in dmiss], swap_test=swap, flips_if_swapped=flips)
for m in miss: out['misses_by_event_year']['%s %d' % (m['event'], m['year'])] += 1
json.dump(out, open('data/gate2_swap_check.json', 'w'), indent=1)
print(total, len(miss), len(dmiss), flips)
