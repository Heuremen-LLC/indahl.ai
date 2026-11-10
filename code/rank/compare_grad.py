#!/usr/bin/env python3
"""RANK Addendum 2 (sealed 04f16e5): graduate school checks. US News school pages as read 2026-11-10 (raw/grad_pages_20261110.txt, free tier)
against each school's own published reports and national files (public/grad/<list>/<list>_public.json, every value traced to a saved file).
Every comparison goes through rule.compare (the sealed rule). Each scored public value is picked by an explicit map below (PICK), naming
school, item and class or year. Paid-tier figures are one CANNOT_TELL (paid_tier) row per school and indicator, with the public figure shown.
Output: data/checks_grad.json. Standard library only. Heuremen LLC."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
from rule import compare
U = json.loads(open('raw/grad_pages_20261110.txt', encoding='utf-8').read().split('JSON:\n', 1)[1])
R = json.load(open('data/rank.json', encoding='utf-8'))
ROWS = {l['key']: [r['name'] for r in l['rows']] for l in R['lists'] if l['key'] in ('mba', 'eng', 'edu', 'med')}
SLUG = {k: [s for s in U if s.startswith(k + '/')] for k in ROWS}   # same order as the list pages
NAME = {s: ROWS[k][i] for k in ROWS for i, s in enumerate(SLUG[k])}
OUT = []
def add(lst, school, field, usn, usn_year, pub, pub_year, source, note='', same=True, shown_pub=None, outcome=None, reason=None):
    oc, why = compare(usn, pub, usn_year, pub_year, same)
    if outcome: oc, why = outcome, reason or ''
    OUT.append(dict(list=lst, school=school, field=field, usn=usn, usn_year=usn_year, pub=shown_pub if shown_pub is not None else pub,
                    pub_year=pub_year, source=source, note=note.replace(';', ','), outcome=oc, reason=why))
