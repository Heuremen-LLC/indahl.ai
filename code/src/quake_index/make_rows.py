#!/usr/bin/env python3
"""make_rows.py (11 Nov 2026): the QUAKE desk's ledger rows (quake.*) recomputed from summary_quake.json and the page quake.html built from it.
  make_rows.py            dry run: prints the rows as they would read now
  make_rows.py --update   refresh the live quake.* rows from the current summary and rebuilt page, ledger before the surface.
                          Appends a dated "refresh record" to CHECKS.md only when a row changed (it must pass watch/readcheck.py),
                          updates rows in place through ledger.py load/save with a history entry, exits 2 if the set of rows changed
                          (a new or removed row needs a hand edit). The live.quake.headline row is not touched here.
Called by refresh_page.py (ship.sh step 1) after build_page.py. Heuremen LLC."""
import json, os, re, sys, subprocess, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); L = os.path.expanduser('~/bones-forge/ledger'); sys.path.insert(0, L)
import check_ledger as CL, ledger as LG
S = json.load(open('summary_quake.json')); page = open('quake.html').read(); ptext = CL.norm(page)
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
from quake_headline import rw
def pc(x): return '' if x is None else '%.1f' % (100 * x)
def n(x): return '{:,}'.format(x)
def iv(a): return '' if not a else '%s to %s' % (pc(a[0]), pc(a[1]))
def v4(x): return '' if x is None else str(round(x, 4))
def find(rx):
    m = re.search(rx, ptext); assert m, rx; return m
SPEC = []   # (id, claim or None to keep, value, lo, hi, unit, outcome, surface text)
def cover(rid, c):
    SPEC.append((rid, None, v4(c['share']), v4(c['lo']), v4(c['hi']), '%s of %s' % (n(c['inside']), n(c['scored'])), c['outcome'],
                 ' '.join([c['cell'], n(c['scored']), n(c['inside']), n(c['above']), n(c['below']), pc(c['share']), iv(c['wilson']), iv(c['boot']), rw(c), n(c['blocks']), n(c['range_zero_zero'])])))
def rel(rid, c, claim=None):
    SPEC.append((rid, claim, v4(c['share']), v4(c['lo']), v4(c['hi']), '%s of %s' % (n(c['occurred']), n(c['scored'])), c['outcome'],
                 ' '.join([c['cell'], n(c['scored']), n(c['occurred']), pc(c['stated_mean']), pc(c['share']), iv(c['wilson']), iv(c['boot']), rw(c), n(c['blocks'])])))
cover('quake.cover.m3', S['headline_cell'])
for c in S['cover_by_magnitude']:
    if c['cell'] != 'M3 and above': cover('quake.cover.' + c['cell'].split(' ')[0].lower(), c)
for c in S['cover_by_window']: cover('quake.cover.m3.' + c['cell'].split(' ')[-1], c)
cover('quake.cover.all', S['cover_all'])
oldclaims = {r['id']: r['claim'] for r in LG.load().values() if r['id'].startswith('quake.prob.')}
for c in S['reliability']:
    rid = 'quake.prob.%g_%g' % tuple(round(100 * b) for b in c['bin'])
    assert rid in oldclaims, rid
    rel(rid, c, re.sub(r'(mean stated chance )[\d.]+( percent)', lambda m: m.group(1) + pc(c['stated_mean']) + m.group(2), oldclaims[rid]))
ra = S['reliability_above_mainshock']
m = find(r'(\d+|[\d,]+) of ([\d,]+) windows saw one against a mean stated chance of ([\d.]+) percent, and the reading is ([a-z ]+?(?: \([A-Z_]+\))?)\.')
assert m.groups() == (n(ra['occurred']), n(ra['scored']), pc(ra['stated_mean']), rw(ra)), m.group(0)
SPEC.append(('quake.prob.mainshock', None, v4(ra['share']), v4(ra['lo']), v4(ra['hi']), '%s of %s' % (n(ra['occurred']), n(ra['scored'])), ra['outcome'], m.group(0)))
D = S['described']
for c in [D['stated_10_percent_or_more_all']] + D['stated_10_percent_or_more']:
    k = {'every magnitude, every window': 'all', 'M3 and above': 'm3', 'M4 and above, M5 and above, M6 and above and M7 and above': 'm4up'}.get(c['cell']) or c['cell'].split(' ')[-1]
    rel('quake.prob10.' + k, c)
fc = D['first_forecast_cover']
m = find(r'The first version of each forecast alone, for M3 and above: ([\d,]+) of ([\d,]+) inside, ([\d.]+) percent, with a sequence interval of ([\d.]+) to ([\d.]+) percent\.')
assert m.groups() == (n(fc['inside']), n(fc['scored']), pc(fc['share']), pc(fc['boot'][0]), pc(fc['boot'][1])), m.group(0)
SPEC.append(('quake.first.m3', None, v4(fc['share']), v4(fc['lo']), v4(fc['hi']), '%s of %s' % (n(fc['inside']), n(fc['scored'])), fc['outcome'],
             '%s of %s inside, %s percent, with a sequence interval of %s to %s percent.' % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))))
for s in SPEC: assert CL.norm(s[7]) in ptext, s[7]
def rec(s): return 'row-record %s: value %s, lo %s, hi %s, unit %s, outcome %s, as printed: %s' % (s[0], s[2], s[3], s[4], s[5], s[6], s[7])
now = time.strftime('%Y-%m-%d %H:%M')
blk = '''
## %s QUAKE desk ship record: the rows as shipped, recomputed from the run of %s and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at %s, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of %s, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
''' % (now, S['generated'], S['generated'], S['generated']) + '\n'.join(rec(s) for s in SPEC) + '\n'
if '--update' in sys.argv:
    rows = LG.load(); have = {k for k in rows if k.startswith('quake.')}; want = {s[0] for s in SPEC}
    if have != want: print('make_rows --update: row set changed (%d live, %d now), run a hand edit' % (len(have), len(want))); sys.exit(2)
    def differs(r, s):
        cur = (r.get('value'), r.get('lo'), r.get('hi'), r.get('unit'), r.get('outcome'), (r['surfaces'] or [{}])[0].get('text') if not any(x['surface'] == 'desk_quake' for x in r['surfaces']) else next(x['text'] for x in r['surfaces'] if x['surface'] == 'desk_quake'))
        new = (s[2], s[3] or None, s[4] or None, s[5], s[6], s[7])
        cur = (cur[0], cur[1] or None, cur[2] or None) + cur[3:]
        return cur != new or (s[1] is not None and r.get('claim') != s[1])
    todo = [s for s in SPEC if differs(rows[s[0]], s)]
    if todo:
        open('CHECKS.md', 'a').write(blk.replace('QUAKE desk ship record', 'QUAKE desk refresh record'))
        assert subprocess.run([sys.executable, os.path.expanduser('~/bones-forge/watch/readcheck.py'), 'check', 'CHECKS.md']).returncode == 0
        ck = LG.checks_ref('quake_index/CHECKS.md')
        for s in todo:
            r = rows[s[0]]
            if s[1] is not None: r['claim'] = s[1]
            r.update(value=s[2], lo=s[3] or None, hi=s[4] or None, unit=s[5], outcome=s[6], checks=ck, source=dict(file='quake_index/CHECKS.md', grep=rec(s)),
                     surfaces=[dict(surface='desk_quake', text=s[7])] + [x for x in r['surfaces'] if x['surface'] != 'desk_quake'])
            r.setdefault('history', []).append(dict(at=LG.now(), change='refreshed from the run of %s' % S['generated'], why='desk run moved, page and row rebuilt together', evidence='quake_index/CHECKS.md'))
        LG.save(rows)
    print('make_rows --update: %d rows refreshed' % len(todo))
else:
    print('\n'.join(rec(s) for s in SPEC)); print(len(SPEC), 'rows dry')
