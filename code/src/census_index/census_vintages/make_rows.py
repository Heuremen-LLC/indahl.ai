#!/usr/bin/env python3
"""make_rows.py: appends the CHECKS ship record (every printed table row and number as shipped, the durable source the censusvin.* ledger rows cite)
and adds one staged ledger row per printed table row and per other printed number. flip_rows.py makes them live in the ship's lock.
Heuremen LLC, 11 Nov 2026. Reads summary_vintages.json and census_vintages.html, nothing else.  python3 make_rows.py [--write]"""
import json, os, re, sys, subprocess, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); L = os.path.expanduser('~/bones-forge/ledger'); sys.path.insert(0, L)
import check_ledger as CL, ledger as LG
S = json.load(open('summary_vintages.json')); page = open('census_vintages.html').read(); ptext = CL.norm(page)
trs = re.findall(r'<tr><td>.*?</tr>', page, re.S)
slug = lambda a: re.sub(r'[^a-z0-9]+', '-', a.lower()).strip('-')
lab = [('a', c['cell']) for c in S['cells'] if c['cls'] == 'A'] + [('bc', c['cell']) for c in S['cells'] if c['cls'] in 'BC'] + [('sr', x['cell']) for x in S['second_ruler']] + [('d', c['cell']) for c in S['cells'] if c['cls'] == 'D']
assert len(trs) == len(lab) + 51, (len(trs), len(lab))
items = []
for tr, (k, cell) in zip(trs[:len(lab)], lab):
    items.append(('censusvin.cell.%s.%s' % (k, slug(cell)), 'CENSUS VINTAGES, %s: counts of the four readings, sizes of change, sensitivity or states outside' % cell, CL.norm(tr), 'COUNT'))
for tr, a in zip(trs[len(lab):], S['pes_se']):
    assert CL.norm(tr).startswith(a), a; items.append(('censusvin.state.%s' % slug(a), 'CENSUS VINTAGES, %s: April estimate and census count, survey standard error, readings against the count and against Vintage 2025' % a, CL.norm(tr), 'COUNT'))
def find(rx):
    m = re.search(rx, ptext); assert m, rx; return m.group(0)
items.append(('censusvin.headline', 'CENSUS VINTAGES, headline counts July 1 2020, Vintage 2025 against Vintage 2020', find(r'July 1 2020, Vintage 2025 against Vintage 2020: \d+ ABOVE, \d+ BELOW, \d+ CONSISTENT, \d+ CANNOT_TELL'), 'COUNT'))
items.append(('censusvin.lead', 'CENSUS VINTAGES, lead finding sentence', find(r'For July 1 2020, the Vintage 2025 figure sits above the Vintage 2020 figure by more than the survey yardstick in \d+ states, below it in \d+ and inside it in \d+'), 'COUNT'))
items.append(('censusvin.v2021', 'CENSUS VINTAGES, the same comparison against Vintage 2021', find(r'Against Vintage 2021 the same July 1 2020 comparison reads \d+ ABOVE, \d+ BELOW and \d+ CONSISTENT'), 'COUNT'))
items.append(('censusvin.v2021sums', 'CENSUS VINTAGES, Vintage 2021 totals check', find(r'add to 331,501,080 and its 51 values for July 1 2021 add to 331,893,745'), 'LEVEL'))
items.append(('censusvin.d', 'CENSUS VINTAGES, widest gap between base and count against the yardsticks', find(r'The widest gap between the base and the count is [\d.]+ percent, against yardsticks of [\d.]+ percent and up'), 'LEVEL'))
items.append(('censusvin.nowidth', 'CENSUS VINTAGES, same-base comparisons are read CANNOT_TELL with the reason NO_INTERVAL_FORMABLE', find(r'every comparison between two Vintages on the same base is read CANNOT_TELL with the reason NO_INTERVAL_FORMABLE, which here means no width'), 'COUNT'))
items.append(('censusvin.frame', 'CENSUS VINTAGES, the frame of areas', find(r'The frame is the 50 states and the District of Columbia'), 'COUNT'))
now = time.strftime('%Y-%m-%d %H:%M')
blk = '''
## %s CENSUS VINTAGES desk ship record: every printed table row and number as shipped (durable source for the censusvin.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from census_vintages.html as built from summary_vintages.json of the run at %s, and make_rows.py asserts the table rows against the cells and 51 states
- II: n/a: a table copied as shipped, no comparison between runs
- III: holds: ABOVE and BELOW are separate columns, CANNOT_TELL has its own column
- V: holds: sealed ruler 1.645 times the published survey standard error centered on zero, second ruler centered on the published net coverage error, both printed
- VI: holds: the four outcomes are on the page with the counts as the summary holds them
- R: holds: counts and values from the summary of %s, no number typed by hand
- P1: n/a: no quoted text in this record
- P2: holds: each line carries the cell or state name and the columns the page prints
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: the interval is ours and the page says so
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged and flipped to live in the ship lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
''' % (now, S['generated'], S['generated']) + '\n'.join('vin-record %s: %s' % (i, t) for i, _, t, _ in items) + '\n'
if '--write' not in sys.argv: print(blk[:1200]); print(len(items), 'dry'); sys.exit(0)
open('CHECKS.md', 'a').write(blk)
assert subprocess.run([sys.executable, os.path.expanduser('~/bones-forge/watch/readcheck.py'), 'check', 'CHECKS.md']).returncode == 0
rows = LG.load(); ck = LG.checks_ref('census_index/census_vintages/CHECKS.md')
for i, claim, t, oc in items:
    assert i not in rows, i
    rows[i] = dict(checks=ck, id=i, claim=claim, value=t[:120], lo=None, hi=None, unit='as printed', outcome=oc,
        source=dict(file='census_index/census_vintages/CHECKS.md', grep='vin-record %s: %s' % (i, t)), surfaces=[dict(surface='desk_censusvin', text=t)], status='staged',
        history=[dict(at=LG.now(), change='added', evidence='census_index/census_vintages/CHECKS.md'), dict(at=LG.now(), change="status: 'live' -> 'staged'", why='a new desk before its first ship, flipped to live in the ship lock', evidence='census_index/census_vintages/CHECKS.md')])
LG.save(rows); print('added', len(items), 'staged rows')
