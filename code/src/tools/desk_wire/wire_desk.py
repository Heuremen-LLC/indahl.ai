#!/usr/bin/env python3
"""wire_desk.py SLUG: places a forecaster desk (FLU, STEO, SEASONAL, 10 Nov 2026) on indahl.ai the way NEO was placed: build_site.py block (body from
<slug>_index/<slug>.html, under HERMES beside FORECAST), worker route for /<slug>/live.json from KV <slug>_live, respond prefix, headlines.py,
receipts.py and push_public.sh code maps, ledger.py surface. Idempotent: a file that already names the desk is left alone. Backs up each file it
changes as <file>.bak-20261110-<slug>. Run only while holding ledger/.site_edit.lock."""
import os, re, sys, shutil, json
B = os.path.expanduser('~/bones-forge'); SLUG = sys.argv[1]; NAME = SLUG.upper()
CFG = json.load(open(os.path.join(B, 'tools', 'desk_wire', SLUG + '.json')))
def patch(rel, fn):
    p = os.path.join(B, rel); t = open(p).read(); n = fn(t)
    if n is None or n == t: print('  unchanged', rel); return
    shutil.copy2(p, p + '.bak-20261110-' + SLUG); open(p, 'w').write(n); print('  patched', rel)
def once(t, marker, old, new, count=1):
    if marker in t: return t
    assert old in t, (old[:80], 'anchor missing'); return t.replace(old, new, count)
# build_site.py
def bs(t):
    m = f"PAGES['/{SLUG}']"
    if m in t: return t
    t = t.replace("'/neo': '/atlas',", f"'/neo': '/atlas', '/{SLUG}': '/hermes',", 1)
    t = t.replace("'water','neo','wiki'}", f"'water','neo','wiki','{SLUG}'}}", 1)
    t = t.replace("('/forecast', 'FORECAST', 'Stated chance against what happened'),", f"('/forecast', 'FORECAST', 'Stated chance against what happened'), ('/{SLUG}', '{NAME}', '{CFG['short']}'),", 1)
    v = '_' + SLUG
    block = f'''
# 10 Nov 2026: {NAME}, under HERMES beside FORECAST. Plan: {SLUG}_index/PLAN.md, committed ({CFG['seal']}) before the first comparison, outside referee
# {SLUG}_index_referee/REFEREE.md (fixes applied in {SLUG}_index/build_page.py). The body is taken from {SLUG}_index/{SLUG}.html as for NEO. The headline is the
# live one (watch/headlines.py {SLUG}(), same function as the page). The feed /{SLUG}/live.json is the summary of the newest run.
{v} = open(os.path.join(HERE, '..', '{SLUG}_index', '{SLUG}.html'), encoding='utf-8').read()
{v}_main = {v}[{v}.index('<main class="wrap">') + len('<main class="wrap">'):{v}.index('</main>')]
assert {v}_main.startswith('<section id="hl-slot"'), '{NAME}: the headline block is not where build_page.py puts it'
{v.upper()}BODY = {v}_main[{v}_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in {v.upper()}BODY, '{NAME}: the division line is not where build_page.py puts it'
{v.upper()}BODY = {v.upper()}BODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\\n')
{v.upper()}BODY = {v.upper()}BODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/{SLUG}'] = page('/{SLUG}', {CFG['title']!r}, {CFG['desc']!r}, {v.upper()}BODY, hero_slim({CFG['hero']!r}))
_FEED.append(('/{SLUG}', {CFG['feed_title']!r}, {CFG['feed_desc']!r}))
'''
    anchor = "_FEED.append(('/neo',"
    i = t.index(anchor); j = t.index('\n', i) + 1
    return t[:j] + block + t[j:]
patch('indahl-ai/build_site.py', bs)
# worker.js
def wk(t):
    if f"'/{SLUG}/live.json'" in t: return t
    line = f"    if ((host === 'indahl.ai' || host === 'www.indahl.ai') && u.pathname === '/{SLUG}/live.json' && env.IRIS_BENCH) {{ const v = await env.IRIS_BENCH.get('{SLUG}_live'); return new Response(v || '{{}}', {{ headers: {{ 'content-type': 'application/json', 'cache-control': 'no-store' }} }}); }}   // 10 Nov: {SLUG} (HERMES), put by {SLUG}_index/{SLUG}_tick --publish\n"
    i = t.index("u.pathname === '/neo/live.json'"); i = t.rindex('\n', 0, i) + 1
    t = t[:i] + line + t[i:]
    t = t.replace('|water|neo|wiki|', f'|water|neo|wiki|{SLUG}|', 1)
    return t
patch('cloudflare-workers/heuremen-door/worker.js', wk)
# headlines.py
def hd(t):
    if f'def {SLUG}():' in t: return t
    t = t.replace("'neo': B + '/neo_index/data/neo_live.json'}", f"'neo': B + '/neo_index/data/neo_live.json', '{SLUG}': B + '/{SLUG}_index/data/{SLUG}_live.json'}}", 1)
    fn = f'''def {SLUG}():
    # 10 Nov 2026: {NAME} (HERMES). The line comes from {SLUG}_index/{SLUG}_headline.py, the same function that writes the page.
    import sys as _s; _s.path.insert(0, B + '/{SLUG}_index'); from {SLUG}_headline import headline as _h
    big, line = _h(feed('{SLUG}')); add('{SLUG}', big, line)
'''
    i = t.index('def neo():'); t = t[:i] + fn + t[i:]
    t = t.replace("'atlas', 'water', 'neo'): safe(n, fn)", f"'atlas', 'water', 'neo', '{SLUG}'): safe(n, fn)", 1)  # dispatch list now carries flu, steo, seasonal
    return t
patch('watch/headlines.py', hd)
patch('ledger/receipts.py', lambda t: t if f"'{SLUG}_index'" in t else t.replace("'neo_index': 'neo',", f"'neo_index': 'neo', '{SLUG}_index': '{SLUG}',", 1))
patch('ledger/push_public.sh', lambda t: t if f"'{SLUG}': ('{SLUG}_index'" in t else t.replace("'neo': ('neo_index', A),", f"'neo': ('neo_index', A), '{SLUG}': ('{SLUG}_index', A),", 1))
patch('ledger/ledger.py', lambda t: t if f"'desk_{SLUG}'" in t else t.replace("    'desk_neo': 'indahl-ai/neo.html',", f"    'desk_{SLUG}': 'indahl-ai/{SLUG}.html',   # 10 Nov 2026: the {NAME} desk (HERMES); page body from {SLUG}_index/{SLUG}.html\n    'desk_neo': 'indahl-ai/neo.html',", 1))
print('done', SLUG)
