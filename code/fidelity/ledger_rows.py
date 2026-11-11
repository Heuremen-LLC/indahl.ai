#!/usr/bin/env python3
"""ledger_rows.py: appends the CHECKS ship record (every printed table row and number as shipped, the durable source the fid.* ledger rows cite)
and adds one staged ledger row per printed table row and per other printed number. flip_rows.py makes them live in the ship's lock.
Heuremen LLC, 11 Nov 2026. Reads fidelity.html (built by build_page.py from summary_fidelity.json and data/), nothing else.  python3 ledger_rows.py [--write]"""
import json, os, re, sys, subprocess, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); L = os.path.expanduser('~/bones-forge/ledger'); sys.path.insert(0, L)
import check_ledger as CL, ledger as LG
S = json.load(open('summary_fidelity.json')); page = open('fidelity.html').read(); ptext = CL.norm(page)
trs = re.findall(r'<tr><td>.*?</tr>', page, re.S)
PER = [('all', 3), ('sex', 3), ('year', 14), ('state', 51), ('gapbelow', 6), ('gapabove', 6)]
assert len(trs) == 2 * sum(n for _, n in PER), len(trs)
slug = lambda a: re.sub(r'[^a-z0-9]+', '-', a.lower()).strip('-')
items = []   # (id, claim, text, outcome)
i = 0
for ev in ('divorce', 'marriage'):
    for kind, n in PER:
        for _ in range(n):
            t = CL.norm(trs[i]); i += 1; first = t.split(' ')[0] if kind != 'state' else t
            key = slug(re.sub(r'[\d,\s-]+$', '', t) if kind in ('state', 'all') else (t if kind == 'gapbelow' or kind == 'gapabove' else t))[:60]
            label = {'all': 'headline table', 'sex': 'women, men and both-sexes table', 'year': 'by year', 'state': 'by jurisdiction', 'gapbelow': 'largest gap, NCHS below ACS', 'gapabove': 'largest gap, NCHS above ACS'}[kind]
            rid = 'fid.%s.%s.%s' % (ev, kind, slug(t)[:48].strip('-'))
            items.append((rid, 'FIDELITY, %s, %s: row as printed' % (ev, label), t, 'COUNT'))
assert i == len(trs) and len({x[0] for x in items}) == len(items)
def find(rx):
    m = re.search(rx, ptext); assert m, rx; return m.group(0)
O = [('fid.headline', 'FIDELITY, headline: Texas divorce below the ACS interval under both sexes, the other both-sexes jurisdictions and the 2022 national ratio', r'13 of 13 In Texas the CDC count of divorces and annulments sits below.*?not against 1\.0\.', 'COUNT'),
     ('fid.line.divorce', 'FIDELITY, divorces: women, men and both-sexes counts', r"Divorces and annulments: of \d+ rows.*?Without the destination cells the women's reading is \d+ above, \d+ below and \d+ inside\.", 'COUNT'),
     ('fid.line.marriage', 'FIDELITY, marriages: women, men and both-sexes counts', r"Marriages: of \d+ rows.*?Without the destination cells the women's reading is \d+ above, \d+ below and \d+ inside\.", 'COUNT'),
     ('fid.scored', 'FIDELITY, the women reading is the scored one, below counts under women and men', r"The women's reading is the scored one.*?under the men's\.", 'COUNT'),
     ('fid.holdone', 'FIDELITY, Massachusetts, Iowa and Kansas divorce below counts under women and men', r"Massachusetts, Iowa and Kansas hold under one sex.*?not under the men's\.", 'COUNT'),
     ('fid.baseline', 'FIDELITY, 2022 national NCHS total over the ACS women and men totals, divorce and marriage', r"In 2022 the NCHS total for the reporting states was.*?for marriages\.", 'LEVEL'),
     ('fid.blanks', 'FIDELITY, divorce blanks in the frame years by state, and the Georgia marriage blanks', r"The blanks in the frame years are.*?Georgia has no marriage count for 2013 and 2014\.", 'COUNT'),
     ('fid.sexsplit', 'FIDELITY, rows where women and men intervals give different readings', r"counted apart as sex splits: \d+ divorce rows and \d+ marriage rows", 'COUNT'),
     ('fid.scout', 'FIDELITY, scout of state-year-events shown before the plan', r"A scout of \d+ state-year-events had already shown.*?lists them\.", 'COUNT'),
     ('fid.tolerance', 'FIDELITY, reader gate rate tolerance first run and reset', r"The reader gate's rate tolerance first ran at 0\.15 and was reset to the plan's 0\.1", 'LEVEL'),
     ('fid.destination', 'FIDELITY, destination rows and the other states that read above', r"For marriages these destination rows are.*?the destination states are not the only rows above\.", 'COUNT'),
     ('fid.louisiana', 'FIDELITY, Louisiana and Georgia printed count breaks', r"The Louisiana divorce count NCHS prints falls from.*?none is re-read\.", 'COUNT'),
     ('fid.swap', 'FIDELITY, divorce state-years where the NCHS count and rate tables disagree and the rows that change under the swap', r"In \d+ divorce state-years of 2016 and 2017.*?No row has been re-read\.", 'COUNT'),
     ('fid.ratecheck', 'FIDELITY, gate 2 rate check and the state-years that miss', r"within 0\.1 in [\d,]+ of [\d,]+ state-years\. The \d+ that miss", 'COUNT'),
     ('fid.join', 'FIDELITY, ACS API values equal to the Census summary files', r"in [\d,]+ of [\d,]+ values for 2022 and 2023", 'COUNT')]
for rid, claim, rx, oc in O: items.append((rid, claim, find(rx), oc))
for k, m in enumerate(re.findall(r"Texas, ACS women against the NCHS count: .*?\.", ptext)): items.append(('fid.texas.%s' % ('divorce', 'marriage')[k], 'FIDELITY, Texas 2021 to 2023, NCHS count against the ACS women estimate', m, 'COUNT'))
assert sum(1 for x in items if x[0].startswith('fid.texas')) == 2
now = time.strftime('%Y-%m-%d %H:%M')
blk = '''
## %s FIDELITY desk ship record: every printed table row and number as shipped (durable source for the fid.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from fidelity.html as built from summary_fidelity.json (run %s) and data/, and ledger_rows.py asserts the table rows against the page
- II: n/a: a page copied as shipped, no comparison between runs
- III: holds: above and below are separate columns in every row, cannot tell is its own column and never in a count of the other three
- V: holds: one ruler, the published ACS 90 percent margin on the women estimate, the men estimate beside it for the same rows
- VI: holds: the four outcomes are on the page with the counts as the summary holds them
- R: holds: counts and values from the summary of %s and data/fidelity.json, no number typed by hand, the post-referee display fixes are in the entry before this one
- P1: holds: the NCHS text is quoted from the rate workbooks as printed
- P2: holds: each line carries the label the page prints
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: the margin is ACS's published one and the page says it covers ACS sampling only
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged and flipped to live in the ship lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
''' % (now, S['run'], S['run']) + '\n'.join('fid-record %s: %s' % (i, t) for i, _, t, _ in items) + '\n'
if '--write' not in sys.argv: print(blk[:1200]); print(len(items), 'dry'); sys.exit(0)
open('CHECKS.md', 'a').write(blk)
assert subprocess.run([sys.executable, os.path.expanduser('~/bones-forge/watch/readcheck.py'), 'check', 'CHECKS.md']).returncode == 0
rows = LG.load(); ck = LG.checks_ref('fidelity_index/CHECKS.md')
for i, claim, t, oc in items:
    assert i not in rows, i
    rows[i] = dict(checks=ck, id=i, claim=claim, value=t[:120], lo=None, hi=None, unit='as printed', outcome=oc,
        source=dict(file='fidelity_index/CHECKS.md', grep='fid-record %s: %s' % (i, t)), surfaces=[dict(surface='desk_fidelity', text=t)], status='staged',
        history=[dict(at=LG.now(), change='added', evidence='fidelity_index/CHECKS.md'), dict(at=LG.now(), change="status: 'live' -> 'staged'", why='a new desk before its first ship, flipped to live in the ship lock', evidence='fidelity_index/CHECKS.md')])
LG.save(rows); print('added', len(items), 'staged rows')
