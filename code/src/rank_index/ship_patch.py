#!/usr/bin/env python3
"""RANK ship patch, run under ledger/site_lock.py: wires /rank into build_site.py (OY division), the public code mirror and receipts. Idempotent."""
import os, re, shutil
B = os.path.expanduser('~/bones-forge')
def patch(path, pairs, mark):
    s = open(path).read()
    if mark in s: print('already', path); return
    shutil.copy2(path, path + '.bak-20261110-rank')
    for old, new in pairs:
        assert s.count(old) >= 1, (path, old[:80]); s = s.replace(old, new, 1)
    open(path, 'w').write(s); print('patched', path)
BS = B + '/indahl-ai/build_site.py'
block = '''
# 10 Nov 2026: RANK, under OY. US News education rankings against the public record. Plan: rank_index/PLAN.md, committed (b25e87f) before any
# figure was compared. Step one lists the current top of each list with edition, list and method links, every row check in progress.
# Outside referee: rank_index_referee/REFEREE.md. Body from rank_index/rank_body.html (rank_index/build_page.py from data/rank.json).
_RANKBODY = open(os.path.join(HERE, '..', 'rank_index', 'rank_body.html'), encoding='utf-8').read()
_RANKBODY = _RANKBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/rank'] = page('/rank', 'RANK | US News Education Rankings Against the Public Record | Heuremen LLC', 'RANK: the current top of each US News education ranking, with the stated method and weights, set against state report cards, federal school and college data and schools\\' own published reports.', _RANKBODY, hero_slim('RANK &middot; US News Education Rankings Against the Public Record'))
_FEED.append(('/rank', 'RANK: US News Education Rankings Against the Public Record', 'The current top of each US News education ranking with its stated method, set against the public record.'))
'''
anchor = "# 10 Nov 2026: FLU, under HERMES beside FORECAST."
patch(BS, [("'/campus': '/oy', ", "'/campus': '/oy', '/rank': '/oy', "),
           ("DESKS = {'/oy': [('/campus', 'CAMPUS', 'The documents behind the OY page, kept over time')", "DESKS = {'/oy': [('/campus', 'CAMPUS', 'The documents behind the OY page, kept over time'), ('/rank', 'RANK', 'US News education rankings against the public record')"),
           (anchor, block.lstrip('\n') + '\n' + anchor)], "PAGES['/rank']")
PP = B + '/ledger/push_public.sh'
patch(PP, [("'neo': ('neo_index', A), ", "'neo': ('neo_index', A), 'rank': ('rank_index', A), ")], "'rank': ('rank_index', A)")
RC = B + '/ledger/receipts.py'
patch(RC, [("'neo_index': 'neo', ", "'neo_index': 'neo', 'rank_index': 'rank', ")], "'rank_index': 'rank'")
os.makedirs(B + '/public_mirror/indahl.ai/code/rank', exist_ok=True)
for f in ('PLAN.md', 'build_data.py', 'build_page.py', 'lint_copy.py'):
    shutil.copy2(os.path.join(B, 'rank_index', f), os.path.join(B, 'public_mirror/indahl.ai/code/rank', f))
print('code/rank mirrored')
