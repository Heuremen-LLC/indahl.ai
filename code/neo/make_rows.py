#!/usr/bin/env python3
"""make_rows.py (11 Nov 2026): the NEO desk's ledger rows (neo.*) recomputed from summary_neo.json and the page neo.html built from it.
  make_rows.py            dry run: prints the rows as they would read now
  make_rows.py --update   refresh the live neo.* rows from the current summary and rebuilt page, ledger before the surface.
                          Appends a dated "refresh record" to CHECKS.md only when a row changed (it must pass watch/readcheck.py),
                          updates rows in place through ledger.py load/save with a history entry, exits 2 if the set of rows changed
                          (a new or removed row needs a hand edit). The live.neo.headline row is not touched here.
Called by refresh_page.py (ship.sh step 1) after build_page.py. Heuremen LLC."""
import json, os, re, sys, subprocess, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); L = os.path.expanduser('~/bones-forge/ledger'); sys.path.insert(0, L)
import check_ledger as CL, ledger as LG
S = json.load(open('summary_neo.json')); page = open('neo.html').read(); ptext = CL.norm(page)
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else '%.1f' % (100 * x)
def v4(x): return '' if x is None else str(round(x, 4))
def find(rx):
    m = re.search(rx, ptext); assert m, rx; return m
cells = {c['cell']: c for c in S['cells']}
SPEC = []   # (id, claim or None to keep, value, lo, hi, unit, outcome, surface text)
for rid, name in (('neo.cell.all', 'all leads'), ('neo.cell.lead0_7', '0 to 7 days'), ('neo.cell.lead8_30', '8 to 30 days'), ('neo.cell.lead30', 'more than 30 days')):
    c = cells[name]
    SPEC.append((rid, None, v4(c['share']), v4(c['lo']), v4(c['hi']), '%d of %d' % (c['inside'], c['scored']), c['outcome'],
                 '%s %d %d %d %d %s %s to %s %s %d' % (name, c['scored'], c['inside'], c['above'], c['below'], pc(c['share']), pc(c['lo']), pc(c['hi']), WORD[c['outcome']], c['cannot_tell'])))
a = S['august_2026']
m = find(r'(\d+) rows are scored, (\d+) inside, (\d+) farther and (\d+) closer, and (\d+) cannot tell\.')
assert tuple(map(int, m.groups())) == (a['scored'], a['inside'], a['above'], a['below'], a['cannot_tell']), m.group(0)
SPEC.append(('neo.august2026', 'NEO, approaches dated August 2026, shown apart: %d of %d scored inside, %d cannot tell' % (a['inside'], a['scored'], a['cannot_tell']), v4(a['share']), v4(a['lo']), v4(a['hi']),
             '%d of %d' % (a['inside'], a['scored']), a['outcome'], m.group(0)))
D = S['dependence']; DC = {c['cell']: c for c in D['cells']}; allc = cells['all leads']
BIG = time.strftime('%d %B %Y', time.strptime(D['copy_day'], '%Y%m%d')).lstrip('0')
dc = DC['all leads']; mo = S['more']
m = find(r'It was made on (.+?) and it gives (\d+) of the (\d+) scored rows and (\d+) of the (\d+) rows outside the range\.')
assert m.group(1) == BIG and tuple(map(int, m.groups()[1:])) == (dc['from_copy_scored'], allc['scored'], dc['from_copy_outside'], allc['above'] + allc['below']), m.group(0)
SPEC.append(('neo.dep.copy20240209', 'NEO: the archived copy of %s gives %d of the %d scored rows and %d of the %d outside the range (display, after the data)' % (BIG, dc['from_copy_scored'], allc['scored'], dc['from_copy_outside'], allc['above'] + allc['below']),
             str(dc['from_copy_scored']), None, None, 'of %d scored, %d of %d outside' % (allc['scored'], dc['from_copy_outside'], allc['above'] + allc['below']), 'COUNT', m.group(0)))
w = dc['without']; n7 = DC['0 to 7 days']['without']
m = find(r'Without that copy (\d+) of (\d+) scored rows are inside and the first row reads ([a-z ]+?), and the 0 to 7 day cell holds (\d+) of (\d+) and reads ([a-z ]+?)\.')
assert m.groups() == (str(w['inside']), str(w['scored']), WORD[w['outcome']], str(n7['inside']), str(n7['scored']), WORD[n7['outcome']]), m.group(0)
SPEC.append(('neo.dep.without', 'NEO: without the copy of %s, all leads %d of %d inside (%s) and 0 to 7 days %d of %d (%s), after the data, decides nothing' % (BIG, w['inside'], w['scored'], WORD[w['outcome']], n7['inside'], n7['scored'], WORD[n7['outcome']]),
             v4(w['inside'] / w['scored']), v4(w['lo']), v4(w['hi']), '%d of %d' % (w['inside'], w['scored']), w['outcome'], m.group(0)))
m = find(r'(\d+) of the (\d+) stated ranges were under 1,000 km wide\.')
assert tuple(map(int, m.groups())) == (mo['outside_under_1000km_wide'], mo['outside_rows']), m.group(0)
SPEC.append(('neo.more.narrow', 'NEO: %d of the %d stated ranges outside were under 1,000 km wide (display, after the data)' % (mo['outside_under_1000km_wide'], mo['outside_rows']), str(mo['outside_under_1000km_wide']), None, None, 'of %d' % mo['outside_rows'], 'COUNT', m.group(0)))
na = mo['nominal_alone']
m = find(r'(\d+) of (\d+) are inside, which reads the same\.')
assert tuple(map(int, m.groups())) == (na['inside'], na['rows']), m.group(0)
SPEC.append(('neo.more.nominal', 'NEO: judged on the later nominal distance alone, counting rows that cross an edge, %d of %d are inside (display, after the data)' % (na['inside'], na['rows']), str(na['inside']), None, None, 'of %d' % na['rows'], 'COUNT', m.group(0)))
o3 = mo['other_copies_over30']
m = find(r'From other copies more than 30 days ahead: (\d+) scored, (\d+) inside\.')
assert tuple(map(int, m.groups())) == (o3['scored'], o3['inside']), m.group(0)
SPEC.append(('neo.more.other30', 'NEO: from copies other than %s, statements more than 30 days ahead: %d scored, %d inside (display, after the data)' % (BIG, o3['scored'], o3['inside']), str(o3['inside']), None, None, 'of %d' % o3['scored'], 'COUNT', m.group(0)))
o = mo['over365']
m = find(r'All (\d+) scored statements made more than 365 days ahead are from the (.+?) copy, and (\d+) are inside\.')
assert (int(m.group(1)), m.group(2), int(m.group(3))) == (o['scored'], BIG, o['inside']) and o['from_copy'] == o['scored'], m.group(0)
SPEC.append(('neo.more.over365', 'NEO: all %d scored statements made more than 365 days ahead are from the copy of %s, %d inside (display, after the data)' % (o['scored'], BIG, o['inside']), str(o['inside']), None, None, 'of %d' % o['scored'], 'COUNT', m.group(0)))
m = find(r'In (\d+) of these (\d+) rows the nominal distance moved by less than 2,000 km\.')
assert int(m.group(2)) == mo['outside_rows'], m.group(0)
SPEC.append(('neo.outside.small', 'NEO: in %s of the %s outside rows the nominal distance moved by less than 2,000 km' % m.groups(), m.group(1), None, None, 'of %s' % m.group(2), 'COUNT', m.group(0)))
for s in SPEC: assert CL.norm(s[7]) in ptext, s[7]
def rec(s): return 'row-record %s: value %s, lo %s, hi %s, unit %s, outcome %s, as printed: %s' % (s[0], s[2], s[3], s[4], s[5], s[6], s[7])
now = time.strftime('%Y-%m-%d %H:%M')
blk = '''
## %s NEO desk ship record: the rows as shipped, recomputed from the run of %s and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at %s, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of %s, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
''' % (now, S['generated'], S['generated'], S['generated']) + '\n'.join(rec(s) for s in SPEC) + '\n'
if '--update' in sys.argv:
    rows = LG.load(); have = {k for k in rows if k.startswith('neo.')}; want = {s[0] for s in SPEC}
    if have != want: print('make_rows --update: row set changed (%d live, %d now), run a hand edit' % (len(have), len(want))); sys.exit(2)
    def differs(r, s):
        cur = (r.get('value'), r.get('lo'), r.get('hi'), r.get('unit'), r.get('outcome'), (r['surfaces'] or [{}])[0].get('text') if not any(x['surface'] == 'desk_neo' for x in r['surfaces']) else next(x['text'] for x in r['surfaces'] if x['surface'] == 'desk_neo'))
        new = (s[2], s[3] or None, s[4] or None, s[5], s[6], s[7])
        cur = (cur[0], cur[1] or None, cur[2] or None) + cur[3:]
        return cur != new or (s[1] is not None and r.get('claim') != s[1])
    todo = [s for s in SPEC if differs(rows[s[0]], s)]
    if todo:
        open('CHECKS.md', 'a').write(blk.replace('NEO desk ship record', 'NEO desk refresh record'))
        assert subprocess.run([sys.executable, os.path.expanduser('~/bones-forge/watch/readcheck.py'), 'check', 'CHECKS.md']).returncode == 0
        ck = LG.checks_ref('neo_index/CHECKS.md')
        for s in todo:
            r = rows[s[0]]
            if s[1] is not None: r['claim'] = s[1]
            r.update(value=s[2], lo=s[3] or None, hi=s[4] or None, unit=s[5], outcome=s[6], checks=ck, source=dict(file='neo_index/CHECKS.md', grep=rec(s)),
                     surfaces=[dict(surface='desk_neo', text=s[7])] + [x for x in r['surfaces'] if x['surface'] != 'desk_neo'])
            r.setdefault('history', []).append(dict(at=LG.now(), change='refreshed from the run of %s' % S['generated'], why='desk run moved, page and row rebuilt together', evidence='neo_index/CHECKS.md'))
        LG.save(rows)
    print('make_rows --update: %d rows refreshed' % len(todo))
else:
    print('\n'.join(rec(s) for s in SPEC)); print(len(SPEC), 'rows dry')
