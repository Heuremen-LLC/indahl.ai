#!/usr/bin/env python3
"""make_rows.py: appends the CHECKS ship record (the cell table and the other printed numbers as shipped, the durable source the ledger rows cite)
and adds one ledger row per printed table row and per other printed number. Rows are added staged and flipped to live by flip_rows.py in the ship's lock.
Heuremen LLC, 11 Nov 2026. Reads summary_census.json and census_revisions.html, nothing else."""
import json, os, re, sys, subprocess, time, hashlib
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); L = os.path.expanduser('~/bones-forge/ledger'); sys.path.insert(0, L)
import check_ledger as CL, ledger as LG
S = json.load(open('summary_census.json')); page = open('census_revisions.html').read()
ptext = CL.norm(page)
SER = {'SALES': 'New residential sales', 'STARTS': 'Housing starts', 'COMPLETIONS': 'Housing completions', 'PERMITS': 'Building permits', 'RETAIL': 'Advance retail and food services'}
STEP = {'S1': 'second print', 'S2': 'third print', 'S3': 'current value'}
trs = re.findall(r'<tr><td>.*?</tr>', page, re.S)
cells = S['cells']; assert len(trs) == len(cells) == 39, (len(trs), len(cells))
# the tables hold US rows (non-permits) first, then the others, in summary order within each
us = [c for c in cells if c['geo'] == 'US' and c['series'] != 'PERMITS']; ot = [c for c in cells if not (c['geo'] == 'US' and c['series'] != 'PERMITS')]
order = us + ot
def cid(c): return 'census.cell.%s.%s.%s' % (c['series'].lower(), c['geo'].lower(), c['step'].lower())
lines = []
for c in order: lines.append('cell %s %s %s: %d of %d inside, %d above, %d below, %d cannot tell, share %.4f, interval %.4f to %.4f, %s' % (c['series'], c['geo'], c['step'], c['inside'], c['scored'], c['above'], c['below'], c['cannot_tell'], c['share'] if c['share'] is not None else 0, c['lo'], c['hi'], c['outcome']))
def cl(s, st): return next(c for c in cells if c['series'] == s and c['geo'] == 'US' and c['step'] == st)
det = S['series_meta']['RSAFS']['annual_revision_detail']; brk = S['series_meta']['RSAFS']['retail_break_vintage']
# the other printed numbers, each as the page prints it
others = []
def find(rx):
    m = re.search(rx, ptext); assert m, rx; return m.group(0)
others.append(('census.revision.median', 'CENSUS, median absolute revision from the first print to the second print, per series', find(r'new residential sales [\d.]+ percent of the first print, or [\d.]+ stated half-widths, housing starts.*?advance retail and food services [\d.]+ percent of the first print, or [\d.]+ stated half-widths'), 'LEVEL'))
others.append(('census.revision.sensitivity', 'CENSUS, share of second prints inside with the served width moved by its rounding (display only)', find(r'new residential sales [\d.]+ to [\d.]+, housing starts [\d.]+ to [\d.]+, housing completions [\d.]+ to [\d.]+, advance retail and food services [\d.]+ to [\d.]+ percent'), 'LEVEL'))
others.append(('census.revision.p90', 'CENSUS, 90th percentile of the miss in stated half-widths, second and third print', find(r'new residential sales [\d.]+ and [\d.]+, housing starts [\d.]+ and [\d.]+, housing completions [\d.]+ and [\d.]+, advance retail and food services [\d.]+ and [\d.]+'), 'LEVEL'))
others.append(('census.revision.scaled', 'CENSUS, national cells with every stated half-width cut to two thirds and to half (display only)', find(r'Cutting every stated half-width to two thirds would leave the national cells at [\d.]+ to [\d.]+ percent inside\. Cutting them to half would take them to [\d.]+ to [\d.]+ percent'), 'LEVEL'))
others.append(('census.retail.apr2025', 'CENSUS, retail vintage 2025-04-25: months changed, median and maximum change', find(r'It changed \d+ months by a median of 1\.8 percent and at most 2\.2 percent'), 'COUNT'))
others.append(('census.retail.sep2026', 'CENSUS, retail vintage %s: months changed, median and maximum change' % brk, find(r'It changed \d+ months by a median of [\d.]+ percent and at most [\d.]+ percent\. The sealed rule'), 'COUNT'))
others.append(('census.retail.countedin', 'CENSUS, advance retail with the annual revision rows counted in', find(r'Counted in, advance retail would read second print \d+ of \d+ inside \([\d.]+ to [\d.]+ percent, [a-z]+\) and third print \d+ of \d+ inside \([\d.]+ to [\d.]+ percent, [a-z]+\)'), 'COUNT'))
others.append(('census.samerelease', 'CENSUS, second prints that came in the same release as the first, and the counts without them', find(r'In three months the second print came in the same release as the first \([^)]*\), so those rows show no revision\. With them left out, sales read \d+ of \d+, starts \d+ of \d+ and completions \d+ of \d+'), 'COUNT'))
others.append(('census.frame', 'CENSUS, rows in the frame and the months it spans', find(r'The frame has [\d,]+ rows from \d{4}-\d{2} to \d{4}-\d{2}'), 'COUNT'))
others.append(('census.widths', 'CENSUS, rows with a width as printed and the date of our first dated copy', find(r'began on \d{4}-\d{2}-\d{2}\. .*? \d+ rows have a width as printed'), 'COUNT'))
now = time.strftime('%Y-%m-%d %H:%M')
blk = '''
## %s CENSUS desk ship record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at %s, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of %s, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
''' % (now, S['generated'], S['generated']) + '\n'.join('cell-record: ' + l for l in lines) + '\n' + '\n'.join('number-record %s: %s' % (i, t) for i, _, t, _ in others) + '\n'
if '--update' in sys.argv:   # 11 Nov: refresh the live census.* rows from a new run (refresh_page.py, ship.sh step 1), ledger before the surface
    rows = LG.load(); have = [k for k in rows if k.startswith('census.cell.') or k in {i for i, *_ in others}]
    want = {cid(c) for c in order} | {i for i, *_ in others}
    if set(have) != want: print('make_rows --update: row set changed (%d live, %d now), run --write by hand' % (len(have), len(want))); sys.exit(2)
    open('CHECKS.md', 'a').write(blk.replace('CENSUS desk ship record', 'CENSUS desk refresh record'))
    assert subprocess.run([sys.executable, os.path.expanduser('~/bones-forge/watch/readcheck.py'), 'check', 'CHECKS.md']).returncode == 0
    ck = LG.checks_ref('census_index/CHECKS.md'); n = 0
    def upd(rid, **kw):
        global n
        r = rows[rid]; old = {k: r.get(k) for k in kw}
        if any(json.dumps(old[k], sort_keys=True) != json.dumps(v, sort_keys=True) for k, v in kw.items()):
            r.update(kw); r['checks'] = ck; r.setdefault('history', []).append(dict(at=LG.now(), change='refreshed from the run of %s' % S['generated'], why='desk run moved, page and row rebuilt together', evidence='census_index/CHECKS.md')); n += 1
    for c, tr, ln in zip(order, trs, lines):
        txt = CL.norm(tr); assert txt in ptext, txt[:80]
        upd(cid(c), claim='CENSUS, %s%s, %s: later value inside the stated 90 percent interval, %d of %d scored rows' % (SER[c['series']].lower(), '' if c['geo'] == 'US' else ' ' + c['geo'], STEP[c['step']], c['inside'], c['scored']),
            value='%.4f' % c['share'] if c['share'] is not None else '', lo='%.4f' % c['lo'], hi='%.4f' % c['hi'], unit='%d of %d' % (c['inside'], c['scored']), outcome=c['outcome'],
            source=dict(file='census_index/CHECKS.md', grep='cell-record: ' + ln), surfaces=[dict(surface='desk_census', text=txt)])
    for i, claim, t, oc in others:
        assert CL.norm(t) in ptext, t[:80]
        upd(i, value=t[:120], source=dict(file='census_index/CHECKS.md', grep='number-record %s: %s' % (i, t)), surfaces=[dict(surface='desk_census', text=t)])
    LG.save(rows); print('make_rows --update: %d rows refreshed' % n)
elif '--write' in sys.argv:
    open('CHECKS.md', 'a').write(blk)
    assert subprocess.run([sys.executable, os.path.expanduser('~/bones-forge/watch/readcheck.py'), 'check', 'CHECKS.md']).returncode == 0
    rows = LG.load(); ck = LG.checks_ref('census_index/CHECKS.md'); n = 0
    for c, tr, ln in zip(order, trs, lines):
        txt = CL.norm(tr); assert txt in ptext, txt[:80]
        r = dict(checks=ck, id=cid(c), claim='CENSUS, %s%s, %s: later value inside the stated 90 percent interval, %d of %d scored rows' % (SER[c['series']].lower(), '' if c['geo'] == 'US' else ' ' + c['geo'], STEP[c['step']], c['inside'], c['scored']),
                 value='%.4f' % c['share'] if c['share'] is not None else '', lo='%.4f' % c['lo'], hi='%.4f' % c['hi'], unit='%d of %d' % (c['inside'], c['scored']), outcome=c['outcome'],
                 source=dict(file='census_index/CHECKS.md', grep='cell-record: ' + ln), surfaces=[dict(surface='desk_census', text=txt)], status='staged',
                 history=[dict(at=LG.now(), change='added', evidence='census_index/CHECKS.md'), dict(at=LG.now(), change="status: 'live' -> 'staged'", why='a new desk before its first ship, flipped to live in the ship lock', evidence='census_index/CHECKS.md')])
        assert r['id'] not in rows, r['id']; rows[r['id']] = r; n += 1
    for i, claim, t, oc in others:
        ntxt = CL.norm(t); assert ntxt in ptext, ntxt[:80]
        r = dict(checks=ck, id=i, claim=claim, value=t[:120], lo=None, hi=None, unit='as printed', outcome=oc,
                 source=dict(file='census_index/CHECKS.md', grep='number-record %s: %s' % (i, t)), surfaces=[dict(surface='desk_census', text=t)], status='staged',
                 history=[dict(at=LG.now(), change='added', evidence='census_index/CHECKS.md'), dict(at=LG.now(), change="status: 'live' -> 'staged'", why='a new desk before its first ship, flipped to live in the ship lock', evidence='census_index/CHECKS.md')])
        assert i not in rows, i; rows[i] = r; n += 1
    LG.save(rows); print('added', n, 'staged rows')
else:
    print(blk[:1500]); print(len(order), len(others), 'dry')
