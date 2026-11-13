"""build_org_queue.py (10 Nov 2026). DRAFTS ONLY, sends nothing. One notice per organisation on the indahl.ai brand pages (/brand/<slug>).
Reads live_pages.json (scrape_live.py, the live pages), contacts_*.json (published press/data contacts, with the URL where each is published)
and brands/entities.json. Writes:
  ~/bones-forge/notices/org_queue_20261110.json   every org: state READY / NO_PUBLIC_CONTACT / SKIPPED, contact, source URL, subject, body, links
  ~/bones-forge/notices/org_queue_20261110.jsonl  READY entries only, in send_guarded.py's queue format (key, to, subject, body, studies)
Order: agencies, then companies (desks other than TRIALS first), then nonprofits, universities, other organisations.
Each body quotes only rows as the live page shows them: the row, the stated figure, the outcome, the read time, and the receipt or desk link.
Run: python3 -I build_org_queue.py   (then python3 -I verify_org_queue.py before any batch goes to the sender)"""
import json, os, glob, re
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/bones-forge'); N = B + '/notices'; SITE = 'https://indahl.ai'
L = json.load(open(H + '/live_pages.json')); ENT = json.load(open(B + '/brands/entities.json'))
C = {c['slug']: c for f in sorted(glob.glob(H + '/contacts_*.json')) for c in json.load(open(f))}
OV = json.load(open(H + '/overrides.json'))['unverified'] if os.path.exists(H + '/overrides.json') else {}
for s_, why in OV.items():
    if s_ in C: C[s_] = dict(C[s_], state='NO_PUBLIC_CONTACT', comment='address not verified on its own site: ' + why, held_email=C[s_].get('email', ''), email='')
DEF = ('ABOVE', 'BELOW', 'CONSISTENT', 'AGREE', 'does not meet', 'mismatch', 'disagree', 'IBM above', 'CANNOT TELL', 'NOTHING RETURNED', 'change logged')
MAXR = 3
def absu(u): return u if u.startswith('http') else SITE + u
VOL = {'UPTIME', 'TIME', 'CADA', 'QIA'}   # desks whose live reading moves every round: quoted only when an org has nothing else
def okind(o): return next((d for d in DEF if o.startswith(d)), 'other')
def score(r):
    o = r.get('Outcome', ''); rec = any('/r/' in x for x in r['links'])
    return (not r.get('Stated'), okind(o) == 'other', r['desk'] in VOL, not rec)
def pick(rows):
    """Up to MAXR rows, chosen to show the spread of outcomes the page gives (a new outcome first, then a new desk), never only one side."""
    rows = sorted([r for r in rows if r['Role'] in ('Its statement', 'Its service, measured')], key=score)
    total = len(rows); stable = [r for r in rows if r['desk'] not in VOL]
    rows = stable or rows                         # a moving desk is quoted only when the org has no row on a stable desk
    best = []
    while len(best) < min(MAXR, len(rows)):
        so, sd = {okind(r['Outcome']) for r in best}, {r['desk'] for r in best}
        best.append(min((r for r in rows if r not in best), key=lambda r: (okind(r['Outcome']) in so, r['desk'] in sd) + score(r)))
    return best, total
def block(r):
    rec = [x for x in r['links'] if '/r/' in x]; desk = [x for x in r['links'] if '/r/' not in x]
    lines = [f"{r['desk']}: {r['question']}", f"Row: {r['Row']}", f"Stated: {r['Stated'] or '(the page shows no stated figure for this row)'}",
             f"Outcome: {r['Outcome']}", f"Read: {r['Read']}"]
    if rec: lines.append('Receipt: ' + absu(rec[0]))
    if desk: lines.append('Desk: ' + absu(desk[0]))
    return '\n'.join(lines)
def body(name, slug, page, picked, total):
    head = 'The page shows these rows, among others:' if total > len(picked) else ('The page shows this row:' if total == 1 else 'The page shows these rows:')
    return '\n\n'.join([
        'Hello,',
        f'{name} is named on a public page at indahl.ai that sets what was stated against the delivered record:',
        SITE + '/brand/' + slug,
        head,
        '\n\n---\n\n'.join(block(r) for r in picked),
        "The outcome is the desk's own word. Each row links to its desk, which holds the current reading.",
        'To answer a row, use the Respond link on the page:',
        absu(page['respond']),
        'To ask for a correction or removal, use this form:',
        absu(page['correction'] or '/correction'),
        'Any reply we receive is posted on the page.',
        'K. Indahl\nHeuremen LLC'])
order = {'agency': 0, 'company': 1, 'nonprofit': 2, 'university': 3, 'organisation': 4}
out = []
for e in ENT['entities']:
    s, page = e['slug'], L.get(e['slug'], {}); it = {'slug': s, 'name': e['name'], 'kind': e['kind'], 'page': SITE + '/brand/' + s}
    if page.get('status') != 200: it.update(state='SKIPPED', why=f"no live brand page (HTTP {page.get('status')})"); out.append(it); continue
    roles = {r['Role'] for r in page['rows']}; desks = sorted({r['desk'] for r in page['rows']})
    it['desks'] = desks; it['desk_links'] = sorted({absu(x) for r in page['rows'] for x in r['links'] if '/r/' not in x})
    if not roles & {'Its statement', 'Its service, measured'}:
        it.update(state='SKIPPED', why='no stated figure of its own on the page (roles: ' + ', '.join(sorted(roles)) + ')'); out.append(it); continue
    picked, total = pick(page['rows'])
    it['quoted'] = [{k: r[k] for k in ('desk', 'Row', 'Stated', 'Outcome', 'Read')} | {'links': [absu(x) for x in r['links']]} for r in picked]
    it['receipts'] = [absu(x) for r in picked for x in r['links'] if '/r/' in x]
    it['respond'] = absu(page['respond']); it['correction'] = absu(page['correction'] or '/correction')
    it['subject'] = f"{e['name']} on the indahl.ai brand pages: stated against delivered"
    it['body'] = body(e['name'], s, page, picked, total)
    c = C.get(s)
    if c is None: it.update(state='NO_PUBLIC_CONTACT', why='contact research not run')
    elif c.get('state') == 'FOUND' and c.get('email'):
        it.update(state='READY', to=[c['email'].strip()], contact_kind=c.get('contact_kind'), source_url=c.get('source_url'), named_person=bool(c.get('named_person')), contact_comment=c.get('comment', ''))
    else:
        it.update(state='NO_PUBLIC_CONTACT', contact_form=c.get('contact_form', ''), source_url=c.get('source_url', ''), why=c.get('comment', '') or c.get('state'))
    out.append(it)
for x in ENT.get('excluded', []): out.append({'slug': None, 'name': x['raw'], 'state': 'SKIPPED', 'why': f"kept off the brand pages ({x['desk']}): {x['why']}"})
st = {'READY': 0, 'NO_PUBLIC_CONTACT': 1, 'SKIPPED': 2}
out.sort(key=lambda x: (st[x['state']], bool(x.get('named_person')), order.get(x.get('kind'), 9), x.get('desks') == ['TRIALS'], x['name'].lower()))
for i, x in enumerate(out, 1): x['n'] = i; x['key'] = 'org-' + (x['slug'] or 'excluded-%d' % i)
# an inbox that serves several orgs (a parent's press office) gets its later notices moved to the end, so no inbox gets two in one sitting
seen, first, later = set(), [], []
for x in out:
    if x['state'] != 'READY': continue
    a = x['to'][0].lower(); (later if a in seen else first).append(x); seen.add(a)
    x['shared_inbox_later'] = x in later
json.dump({'built': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'note': 'DRAFTS ONLY. Nothing sent. The owner OKs each batch. READY rows are mirrored to org_queue_20261110.jsonl in send_guarded.py format.',
           'notices': out}, open(N + '/org_queue_20261110.json', 'w'), indent=1, ensure_ascii=False)
# Decision (Bones, 10 Nov): one notice per inbox. These nine get the QIA corporate notice only (qia_corporate_20261110, with a /brand line).
QCORP_ONE_NOTICE = {'org-aws', 'org-google', 'org-ibm', 'org-microsoft', 'org-nvidia', 'org-red-hat', 'org-hoffmann-la-roche', 'org-modernatx-inc', 'org-pfizer'}
with open(N + '/org_queue_20261110.jsonl', 'w') as f:
    for x in first + later:
        if x['key'] not in QCORP_ONE_NOTICE: f.write(json.dumps({'key': x['key'], 'to': x['to'], 'subject': x['subject'], 'body': x['body'], 'studies': ['brand-' + x['slug']]}) + '\n')
import collections; print(collections.Counter(x['state'] for x in out))
