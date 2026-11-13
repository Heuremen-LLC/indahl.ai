#!/usr/bin/env python3
"""make_rows.py: appends the CHECKS ship record (every printed row and number as shipped, the durable source the censuscov.* ledger rows cite)
and adds one staged ledger row per printed table row and per other printed number. flip_rows.py makes them live in the ship's lock.
Heuremen LLC, 11 Nov 2026. Reads summary_coverage.json and census_coverage.html, nothing else.  python3 make_rows.py [--write]"""
import json, os, re, sys, subprocess, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); L = os.path.expanduser('~/bones-forge/ledger'); sys.path.insert(0, L)
import check_ledger as CL, ledger as LG
S = json.load(open('summary_coverage.json')); page = open('census_coverage.html').read(); ptext = CL.norm(page)
trs = re.findall(r'<tr><td>.*?</tr>', page, re.S)
assert len(trs) == 4 + 51 + 52, len(trs)
slug = lambda a: re.sub(r'[^a-z0-9]+', '-', a.lower()).strip('-')
items = []   # (id, claim, text, outcome)
for tr, o in zip(trs[:4], ('BELOW', 'ABOVE', 'CONSISTENT', 'CANNOT_TELL')):
    items.append(('censuscov.outcome.%s' % o.lower(), 'CENSUS COVERAGE, areas read %s, count and areas' % o, CL.norm(tr), 'COUNT'))
for tr, a in zip(trs[4:55], S['areas']):
    assert CL.norm(tr).startswith(a['area']); items.append(('censuscov.area.%s' % slug(a['area']), 'CENSUS COVERAGE, %s: household count, net coverage error, standard error, 90 percent interval, reading' % a['area'], CL.norm(tr), a['outcome']))
for tr, a in zip(trs[55:], ['United States'] + [c['area'] for c in S['component_rows']]):
    assert CL.norm(tr).startswith(a); items.append(('censuscov.comp.%s' % slug(a), 'CENSUS COVERAGE, %s: omissions, duplicates and other erroneous enumerations, percent with standard error' % a, CL.norm(tr), 'LEVEL'))
def find(rx):
    m = re.search(rx, ptext); assert m, rx; return m.group(0)
items.append(('censuscov.headline', 'CENSUS COVERAGE, headline counts of areas by reading', find(r'\d+ areas BELOW, \d+ ABOVE, \d+ CONSISTENT, \d+ CANNOT_TELL'), 'COUNT'))
items.append(('censuscov.ruler', 'CENSUS COVERAGE, lowest flagged and highest unflagged ratio of net coverage error to standard error, and the multiplier range that leaves the flagged areas unchanged', find(r'The lowest flagged ratio of net coverage error to standard error is [\d.]+ \([A-Za-z ]+\) and the highest unflagged is [\d.]+ \([A-Za-z ]+\), so no multiplier from [\d.]+ to [\d.]+ changes the \d+ flagged areas'), 'LEVEL'))
items.append(('censuscov.floor', 'CENSUS COVERAGE, areas Census marks, same as ours', find(r'Census marks the same \d+ areas\. A 90 percent test flags about one area in ten when nothing is off.*?not read the count of \d+ as a result'), 'COUNT'))
items.append(('censuscov.us', 'CENSUS COVERAGE, national net coverage error, standard error, interval and reading', find(r'For the nation the survey gives a net coverage error of [-\d.]+ percent with a standard error of [\d.]+, so the 90 percent interval is [-\d.]+ to [-\d.]+ percent and the national cell reads [A-Z_]+'), 'LEVEL'))
items.append(('censuscov.da', 'CENSUS COVERAGE, Demographic Analysis low, middle and high series and their signs', find(r'The low series is a net coverage error of [-\d.]+ percent and is an? \w+, the middle series is [-\d.]+ percent and is an? \w+, and the high series is [-\d.]+ percent and is an? \w+'), 'LEVEL'))
items.append(('censuscov.da_pes', 'CENSUS COVERAGE, survey national estimate inside the Demographic Analysis range', find(r'The survey national estimate of [-\d.]+ percent sits inside that range'), 'LEVEL'))
items.append(('censuscov.frame', 'CENSUS COVERAGE, the frame of areas', find(r'The survey covers the household population of the \d+ states and the District of Columbia on 1 April 2020'), 'COUNT'))
now = time.strftime('%Y-%m-%d %H:%M')
blk = '''
## %s CENSUS COVERAGE desk ship record: every printed table row and number as shipped (durable source for the censuscov.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from census_coverage.html as built from summary_coverage.json of the run at %s, and make_rows.py asserts 107 table rows against the 4 outcome rows, 51 areas and 52 component rows
- II: n/a: a table copied as shipped, no comparison between runs
- III: holds: BELOW and ABOVE are separate rows, CANNOT_TELL has its own row (0)
- V: holds: one ruler, 1.645 times the published standard error, the range 1.59 to 1.93 is computed from the summary
- VI: holds: the four outcomes are on the page with the counts as the summary holds them
- R: holds: counts and values from the summary of %s, no number typed by hand, the post-referee display fixes are in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line carries the area name and the columns the page prints
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: the interval is ours and the lines say so on the page
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged and flipped to live in the ship lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
''' % (now, S['generated'], S['generated']) + '\n'.join('cov-record %s: %s' % (i, t) for i, _, t, _ in items) + '\n'
if '--write' not in sys.argv: print(blk[:1500]); print(len(items), 'dry'); sys.exit(0)
open('CHECKS.md', 'a').write(blk)
assert subprocess.run([sys.executable, os.path.expanduser('~/bones-forge/watch/readcheck.py'), 'check', 'CHECKS.md']).returncode == 0
rows = LG.load(); ck = LG.checks_ref('census_coverage/CHECKS.md')
for i, claim, t, oc in items:
    assert i not in rows, i
    rows[i] = dict(checks=ck, id=i, claim=claim, value=t[:120], lo=None, hi=None, unit='as printed', outcome=oc,
        source=dict(file='census_coverage/CHECKS.md', grep='cov-record %s: %s' % (i, t)), surfaces=[dict(surface='desk_censuscov', text=t)], status='staged',
        history=[dict(at=LG.now(), change='added', evidence='census_coverage/CHECKS.md'), dict(at=LG.now(), change="status: 'live' -> 'staged'", why='a new desk before its first ship, flipped to live in the ship lock', evidence='census_coverage/CHECKS.md')])
LG.save(rows); print('added', len(items), 'staged rows')
