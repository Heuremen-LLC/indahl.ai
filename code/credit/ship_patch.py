#!/usr/bin/env python3
"""CREDIT ship patch, run under ledger/site_lock.py inside the ship command: wires /credit into build_site.py (HERMES, beside TORNADO), the ledger
surface, the worker feed route, the live headline, the desk pack list, the public code mirror, receipts and the brand pages. Idempotent. Backups *.bak-20261110-credit."""
import os, shutil, json
B = os.path.expanduser('~/bones-forge')
def patch(path, pairs, mark):
    s = open(path).read()
    if mark in s: print('already', path); return
    shutil.copy2(path, path + '.bak-20261110-credit')
    for old, new in pairs:
        assert s.count(old) >= 1, (path, old[:90]); s = s.replace(old, new, 1)
    open(path, 'w').write(s); print('patched', path)

# 1. build_site.py
BS = B + '/indahl-ai/build_site.py'
block = '''
# 10 Nov 2026: CREDIT, under HERMES beside TORNADO. CFPB printed figures (timely responses, forwarding) against the CFPB Consumer Complaint Database,
# each company against the printed figure, the three credit bureaus' closures, the FCRA 30-day period (cannot tell), and TCCP card plan APRs beside G.19.
# Plan: credit_index/PLAN.md, committed (8ef6f26) before the first comparison. Outside referee credit_index_referee/REFEREE.md. Body from credit_index/credit.html.
_credit = open(os.path.join(HERE, '..', 'credit_index', 'credit.html'), encoding='utf-8').read()
_credit_main = _credit[_credit.index('<main class="wrap">') + len('<main class="wrap">'):_credit.index('</main>')]
assert _credit_main.startswith('<section id="hl-slot"'), 'CREDIT: the headline block is not where build_page.py puts it'
_CREDITBODY = _credit_main[_credit_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _CREDITBODY, 'CREDIT: the division line is not where build_page.py puts it'
_CREDITBODY = _CREDITBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\\n')
_CREDITBODY = _CREDITBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/credit'] = page('/credit', 'CREDIT | Stated Complaint Responses and Card Terms Against the Public Record | Heuremen LLC', 'CREDIT: the CFPB printed timely response and forwarding shares against its own complaint database, each company against the printed figure, how the credit bureaus closed complaints, and card plan APRs beside the Federal Reserve averages.', _CREDITBODY, hero_slim('CREDIT &middot; Stated Complaint Responses and Card Terms Against the Public Record'))
_FEED.append(('/credit', 'CREDIT: Stated Complaint Responses and Card Terms Against the Public Record', 'CFPB printed timely response figures against its own complaint database, company by company, and card plan APRs beside the Federal Reserve averages.'))
'''
anchor = "# 10 Nov 2026: TORNADO, under HERMES beside FORECAST."
patch(BS, [("'/tornado': '/hermes', ", "'/tornado': '/hermes', '/credit': '/hermes', "),
           ("'cone','tornado'}", "'cone','tornado','credit'}"),
           ("('/tornado', 'TORNADO', 'Stated tornado chances and warning goals against the tornadoes that came'), ",
            "('/tornado', 'TORNADO', 'Stated tornado chances and warning goals against the tornadoes that came'), ('/credit', 'CREDIT', 'Stated complaint responses and card terms against the public record'), "),
           (anchor, block.lstrip('\n') + '\n' + anchor)], "PAGES['/credit']")
# 2. ledger surface
patch(B + '/ledger/ledger.py', [("    'desk_tornado': 'indahl-ai/tornado.html',", "    'desk_credit': 'indahl-ai/credit.html',   # 10 Nov 2026: the CREDIT desk (HERMES); page body from credit_index/credit.html\n    'desk_tornado': 'indahl-ai/tornado.html',")], "'desk_credit'")
# 3. public code mirror and receipts
patch(B + '/ledger/push_public.sh', [("'tornado': ('tornado_index', A), ", "'tornado': ('tornado_index', A), 'credit': ('credit_index', A), ")], "'credit': ('credit_index', A)")
patch(B + '/ledger/receipts.py', [("'tornado_index': 'tornado', ", "'tornado_index': 'tornado', 'credit_index': 'credit', ")], "'credit_index': 'credit'")
os.makedirs(B + '/public_mirror/indahl.ai/code/credit', exist_ok=True)
for f in ('PLAN.md', 'credit_tick.py', 'credit_headline.py', 'build_page.py', 'heuremen_kit.py', 'xlsx_lite.py', 'lint_copy.py', 'CHECKS.md'):
    shutil.copy2(os.path.join(B, 'credit_index', f), os.path.join(B, 'public_mirror/indahl.ai/code/credit', f))
print('code/credit mirrored')
# 4. worker feed route and respond prefix
WJ = B + '/cloudflare-workers/heuremen-door/worker.js'
route = "    if ((host === 'indahl.ai' || host === 'www.indahl.ai') && u.pathname === '/credit/live.json' && env.IRIS_BENCH) { const v = await env.IRIS_BENCH.get('credit_live'); return new Response(v || '{}', { headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } }); }   // 10 Nov: credit (HERMES), put by credit_index/credit_tick --publish\n"
s = open(WJ).read(); tl = [l for l in s.split('\n') if "u.pathname === '/tornado/live.json'" in l][0] + '\n'
patch(WJ, [(tl, tl + route), ("|neo|tornado|", "|neo|tornado|credit|")], "'/credit/live.json'")
# 5. live headline (watch/headlines.py) and the live headline row spec
HP = B + '/watch/headlines.py'
patch(HP, [("'tornado': B + '/tornado_index/data/tornado_live.json'", "'tornado': B + '/tornado_index/data/tornado_live.json', 'credit': B + '/credit_index/data/credit_live.json'"),
           ("def flu():", "def credit():\n    # 10 Nov 2026: CREDIT (HERMES). The line comes from credit_index/credit_headline.py, the same function that writes the page.\n    import sys as _s; _s.path.insert(0, B + '/credit_index'); from credit_headline import headline as _h\n    big, line = _h(feed('credit')); add('credit', big, line)\ndef flu():"),
           ("'cone', 'tornado', 'flu'", "'cone', 'tornado', 'credit', 'flu'")], "def credit():")
LH = B + '/ledger/live_headlines.py'
spec = (" 'credit': dict(name='CREDIT', field=P('ruler1', {'year': 2025}, 'timely'), show='pct1', stamp=P('updated'), cadence_h=192.0, kind='interval',\n"
        "   outcome=P('ruler1', {'year': 2025}, 'outcome'), lo=P('ruler1', {'year': 2025}, 'lo'), hi=P('ruler1', {'year': 2025}, 'hi'),\n"
        "   cadence_why='The credit_tick.py rider runs every 1,800 ticks (median 0.0917 h a tick, about 7 days) and downloads the complaint file when it is older than 160 h. Rounded up to 8 days. The 2025 cell moves only when complaints received in 2025 are added or change in the file.',\n"
        "   rule_why='PLAN.md (Rules, Headline) fixes ruler one for 2025: the database timely share with a company-month block bootstrap 95 percent interval against the band 99.55 to 99.65 percent that the CFPB printed 99.6 percent allows. The value row credit.timely.2025 holds the shipped reading.'),\n")
patch(LH, [(" 'tornado': dict(name='TORNADO',", spec + " 'tornado': dict(name='TORNADO',"),
           ("'tornado': 'When the Storm Prediction Center draws a tornado chance, how often does a tornado come?', ",
            "'tornado': 'When the Storm Prediction Center draws a tornado chance, how often does a tornado come?', 'credit': 'When the CFPB states how companies answer complaints, what does its own database show?', ")], "'credit': dict(name='CREDIT'")
# 6. desk pack list
DP = B + '/tools/desk_pack.py'
patch(DP, [(" 'tornado': dict(name='TORNADO',", " 'credit': dict(name='CREDIT', folder='credit_index', lic='full', q='Stated complaint responses and card terms against the public record',\n"
            "     src=[('CFPB Consumer Complaint Database (company-level counts only, no complaint text or ZIP code)', 'https://www.consumerfinance.gov/data-research/consumer-complaints/', 'CC0 as the CFPB search service states, U.S. government work'),\n"
            "          ('CFPB Consumer Response Annual Reports 2021 to 2025', 'https://www.consumerfinance.gov/data-research/research-reports/', 'U.S. government work, public domain (17 U.S.C. 105)'),\n"
            "          ('CFPB Terms of Credit Card Plans survey', 'https://www.consumerfinance.gov/data-research/credit-card-data/terms-credit-card-plans-survey/', 'U.S. government work, public domain (17 U.S.C. 105)'),\n"
            "          ('Federal Reserve G.19 Consumer Credit, terms of credit', 'https://www.federalreserve.gov/releases/g19/', 'Federal Reserve Board data, public')]),\n"
            " 'tornado': dict(name='TORNADO',")], "'credit': dict(name='CREDIT'")
# 7. brand pages: the CFPB's printed figures (its statement) and the three bureaus (named in the row)
BR = B + '/indahl-ai/brands.py'
ex = '''def ex_credit():
    k = 'credit'; d = snap(k); rd = _upd(k); out = []
    if d is None: raise Miss('no snapshot credit')
    for i, r in enumerate(d.get('ruler1', [])):
        p = ('f', k, 'ruler1', i)
        out.append(R(k, [('CFPB', 'statement')], 'Does the timely response share the CFPB prints match its own complaint database?', C('complaints received in {0:q}', p + ('year',)),
                     C('printed: {0:q} of complaints sent to companies', p + ('printed',)), C('database: {0:pct} of {1} complaints', p + ('timely',), p + ('rows',)), C('{0:pct} to {1:pct}', p + ('lo',), p + ('hi',)),
                     C('{0:out}', p + ('outcome',)), C('the printed figure counts every complaint sent, the database the published ones'), read=rd))
    for i, c in enumerate(d.get('companies', [])):
        if not c.get('bureau'): continue
        p = ('f', k, 'companies', i)
        out.append(R(k, [(c['company'], 'named')], 'How often is a company flagged not timely against the share the CFPB printed figure leaves?', C('complaints received in {0:q}', p + ('year',)),
                     C('printed all-company figure leaves {0:pct} to {1:pct} not timely', p + ('band', 0), p + ('band', 1)), C('not timely: {0} of {1}', p + ('not_timely',), p + ('rows',)),
                     C('{0:pct} to {1:pct}', p + ('lo',), p + ('hi',)), C('{0:out}', p + ('outcome',)), C('the printed figure is an all-company average, not a per-company limit'), read=rd))
    return out

EXTRACT = ['''
patch(BR, [("    'pkglicense': ('url:/pkglicense/live.json', 'PKGLICENSE', '/pkglicense'), 'wiki': ('url:/wiki/live.json', 'WIKI', '/wiki'),",
            "    'pkglicense': ('url:/pkglicense/live.json', 'PKGLICENSE', '/pkglicense'), 'wiki': ('url:/wiki/live.json', 'WIKI', '/wiki'), 'credit': ('file:credit_index/data/credit_live.json', 'CREDIT', '/credit'),"),
           ("EXTRACT = [", ex), ("ex_social_bluesky, ex_ledger_social]", "ex_social_bluesky, ex_ledger_social, ex_credit]")], "def ex_credit():")
EN = B + '/brands/entities.json'; e = json.load(open(EN))
have = {x['slug'] for x in e['entities']}
add = [('consumer-financial-protection-bureau', 'Consumer Financial Protection Bureau', 'agency', 'CFPB', 'the CFPB, whose annual report prints the figure'),
       ('equifax', 'Equifax', 'company', 'EQUIFAX, INC.', 'the Company value exactly as the CFPB complaint database gives it'),
       ('experian', 'Experian', 'company', 'Experian Information Solutions Inc.', 'the Company value exactly as the CFPB complaint database gives it'),
       ('transunion', 'TransUnion', 'company', 'TRANSUNION INTERMEDIATE HOLDINGS, INC.', 'the Company value exactly as the CFPB complaint database gives it')]
if any(s not in have for s, *_ in add):
    shutil.copy2(EN, EN + '.bak-20261110-credit')
    for slug, name, kind, raw, dec in add:
        if slug in have: continue
        e['entities'].append(dict(slug=slug, name=name, kind=kind, note=('Company name as the CFPB complaint database gives it. Other names in the same group are not merged.' if kind == 'company' else 'The agency that prints the figure.'),
                                  aliases=[dict(desk='credit', raw=raw, decided=dec)]))
    e['entities'].sort(key=lambda x: x['slug']); json.dump(e, open(EN, 'w'), indent=1, ensure_ascii=False); print('patched', EN)
else: print('already', EN)
