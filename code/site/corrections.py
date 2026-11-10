"""corrections.py -- the public corrections log of indahl.ai (10 Nov 2026).

Every referee catch and every fix to a published or staged reading, one row each, newest first. Rows live in corrections_rows.json beside
this file and are written by hand from the referee notes, plan addenda, check blocks, the ledger history and the cold read. A row is never
deleted. A later fix to the same reading is a new row.

Outputs:  /corrections (a page in the page map), and in the worker's public folder corrections.xml (Atom) and corrections.csv.
Hook:     build_site.py calls build(PAGES, page, hero_slim, _FEED) and adds CSS to the stylesheet. The build stops if gate() finds a problem.
Gate:     python3 corrections.py --gate   (every row links to a real file or commit, and its copy keeps the public-copy rules)

Row fields: id, date (YYYY-MM-DD), desk, page (site path or full URL), stage (public|staged), published, wrong, now, why,
caught_by (our referee|our cold read|our own check|an outside reader|the owner), worse (bool: the fix weakened, lowered or withdrew our
own reading), source (path under ~/bones-forge, optional :LINE, or ledger:<row id>), and optionally commit (<repo>@<sha>, repo a folder
under ~/bones-forge), public_commit (sha in the public repo Heuremen-LLC/indahl.ai), links (public URLs), receipt (ledger row id with a
page at /r/<id>), credit (a name, only when the person asked to be credited)."""
import csv, datetime as _dt, html, io, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)
ROWS = os.path.join(HERE, 'corrections_rows.json')
PUB = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public')
MIRROR = os.path.join(B, 'public_mirror', 'indahl.ai')
GH = 'https://github.com/Heuremen-LLC/indahl.ai'
SITE = 'https://indahl.ai'
CAUGHT = ('our referee', 'our cold read', 'our own check', 'an outside reader', 'the owner')
TEXT = ('published', 'wrong', 'now', 'why')
# public copy: plain sentences, no house words, no names, no AI statements (same spirit as ledger/receipts.py DENY)
DENY = re.compile(r'(?i)\bSage\b(?! V)|Wayfinder|\bBones\b|\bNova\b|NovaTable|Claude|An AI assistant|\bflock\b|his word|his call|/q\b|/tp\b|/Users/|Bonefish|tick bus|\brider\b|\btriangles?\b|we caught it first|\bhonest|by hand|hand[ -]read|\{[A-Z][A-Z0-9_]{2,}\}')   # site gate 0b.8, 0b.9, 0b.11
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
E = lambda s: html.escape(str(s), quote=True)


HANDS = re.compile(r'(?i)\bby hand\b|\bhand[- ](?:read|check|count)|\bhand-?checked\b')   # site gate 0b.9 (heuremen-specbook/site_gate.py)


def _argue():
    """the pitch-voice patterns the site gate reads on every business page (heuremen-specbook/tone_scan.py ARGUE)"""
    try:
        import importlib.util as u
        sp = u.spec_from_file_location('tone_scan', os.path.join(B, 'heuremen-specbook', 'tone_scan.py')); m = u.module_from_spec(sp); sp.loader.exec_module(m)
        return [re.compile(a, re.I) for a in m.ARGUE]
    except Exception:
        return []


def load():
    return json.load(open(ROWS, encoding='utf-8'))


def receipt_name(rid):
    """the file ledger/receipts.py writes for a row (receipts.py public_id + href)"""
    pid = rid.replace('flock', 'house')
    return re.sub(r'[^A-Za-z0-9._-]', lambda m: '~%02X' % ord(m.group()), pid)


def _git_has(repo, sha):
    try:
        return subprocess.run(['git', '-C', repo, 'cat-file', '-e', sha + '^{commit}'], capture_output=True).returncode == 0
    except Exception:
        return False


def _ledger_ids():
    ids = set()
    for l in open(os.path.join(B, 'ledger', 'ledger.jsonl'), encoding='utf-8'):
        if l.strip(): ids.add(json.loads(l)['id'])
    return ids


def _source_ok(src, ids):
    if src.startswith('ledger:'): return src[7:] in ids
    path, _, line = src.partition(':')
    p = os.path.join(B, path)
    if not os.path.isfile(p): return False
    if line:
        if not line.isdigit(): return False
        with open(p, 'rb') as f: n = sum(1 for _ in f)
        return 1 <= int(line) <= n
    return True


def _link_ok(u, pages):
    if u.startswith(GH + '/blob/main/') or u.startswith(GH + '/tree/main/'):
        return os.path.exists(os.path.join(MIRROR, u.split('/main/', 1)[1].split('#')[0].split('?')[0]))
    if u.startswith(GH + '/commit/'): return _git_has(MIRROR, u.rsplit('/', 1)[1])
    if u.startswith('https://heuremen.org/'): return os.path.exists(os.path.join(B, 'heuremen.org', u[len('https://heuremen.org/'):].split('#')[0] or 'index.html'))
    if u.startswith(SITE + '/') or u.startswith('/'): return _page_ok(u[len(SITE):] if u.startswith(SITE) else u, pages)
    return False


WORKER = {'/', '/feed.xml', '/sitemap.xml', '/robots.txt', '/llms.txt', '/headlines.json', '/activity.json'}   # served by the worker itself, not from a file


def _page_ok(p, pages):
    if p.startswith('https://heuremen.org/'): return _link_ok(p, pages)
    p = p.split('#')[0].split('?')[0]
    if p in WORKER: return True
    if pages and p in pages: return True
    if os.path.isfile(os.path.join(HERE, p.strip('/') + '.html')): return True
    return os.path.isfile(os.path.join(PUB, p.strip('/')))


def gate(rows=None, pages=None):
    """-> list of problems. Empty means every row is whole and links to a real file or commit."""
    rows = load() if rows is None else rows
    ids, bad, seen, argue = _ledger_ids(), [], set(), _argue()
    for r in rows:
        rid = r.get('id', '?')
        if rid in seen: bad.append(f'{rid}: duplicate id')
        seen.add(rid)
        for k in ('id', 'date', 'desk', 'page', 'stage', 'caught_by', 'source') + TEXT:
            if not str(r.get(k, '')).strip(): bad.append(f'{rid}: {k} is empty')
        if not re.fullmatch(r'2026-\d\d-\d\d', r.get('date', '')): bad.append(f'{rid}: date {r.get("date")!r}')
        if r.get('stage') not in ('public', 'staged'): bad.append(f'{rid}: stage {r.get("stage")!r}')
        if r.get('caught_by') not in CAUGHT: bad.append(f'{rid}: caught_by {r.get("caught_by")!r}')
        if not isinstance(r.get('worse'), bool): bad.append(f'{rid}: worse must be true or false')
        for k in TEXT + ('desk',):
            t = str(r.get(k, ''))
            if ';' in t: bad.append(f'{rid}: semicolon in {k}')
            m = DENY.search(t)
            if m: bad.append(f'{rid}: refused word {m.group()!r} in {k}')
            m = HANDS.search(t) or next((x for x in (a.search(t) for a in argue) if x), None)
            if m: bad.append(f'{rid}: site gate wording {m.group()!r} in {k}')
        if r.get('source') and not _source_ok(r['source'], ids): bad.append(f'{rid}: source not found: {r["source"]}')
        if r.get('commit'):
            repo, _, sha = r['commit'].partition('@')
            if not sha or not _git_has(os.path.join(B, repo), sha): bad.append(f'{rid}: commit not found: {r["commit"]}')
        if r.get('public_commit') and not _git_has(MIRROR, r['public_commit']): bad.append(f'{rid}: public commit not found: {r["public_commit"]}')
        for u in r.get('links', []):
            if not _link_ok(u, pages): bad.append(f'{rid}: link not found: {u}')
        if r.get('receipt'):
            if r['receipt'] not in ids: bad.append(f'{rid}: receipt row not in ledger: {r["receipt"]}')
            elif not os.path.isfile(os.path.join(PUB, 'r', receipt_name(r['receipt']) + '.html')): bad.append(f'{rid}: no receipt page /r/{r["receipt"]}')
        if r.get('page') and not _page_ok(r['page'], pages): bad.append(f'{rid}: page not found: {r["page"]}')
        # every row reaches a real public file or commit: a public link, the public commit, a receipt page, or the document itself (the bill PDF, a heuremen.org file)
        if not (r.get('links') or r.get('public_commit') or r.get('receipt') or str(r.get('page', '')).endswith('.pdf') or str(r.get('page', '')).startswith('https://heuremen.org/')): bad.append(f'{rid}: no public file, commit or receipt to link')
    return bad


def _day(d):
    y, m, dd = d.split('-'); return f'{int(dd)} {MONTHS[int(m) - 1]} {y}'


def _href_page(p):
    return p if p.startswith('http') else p


def _links(r):
    out = []
    p = r['page']
    out.append(f'<a href="{E(_href_page(p))}">{E("Page" if not p.endswith(".pdf") else "Document")}</a>')
    for u in r.get('links', []):
        lab = 'Plan' if u.endswith('PLAN.md') else ('Code' if '/code/' in u else 'Source')
        out.append(f'<a href="{E(u)}">{lab}</a>')
    if r.get('public_commit'): out.append(f'<a href="{GH}/commit/{E(r["public_commit"])}">Commit</a>')
    if r.get('receipt'): out.append(f'<a href="/r/{E(receipt_name(r["receipt"]))}">Receipt</a>')
    return ' &middot; '.join(out)


def _caught(r):
    c = r['caught_by']
    if c == 'an outside reader' and r.get('credit'): return 'Caught by ' + E(r['credit']) + ', who asked to be credited'
    return 'Caught by ' + E(c)


def _show_path(src):
    """the working-file path is printed unless it is a ledger pointer or its folder names carry a house word"""
    return not src.startswith('ledger:') and not DENY.search(src) and not re.search(r'(?i)sage|flock', src)


def page_body(rows):
    rows = sorted(rows, key=lambda r: (r['date'], r['id']), reverse=True)
    out = ['<section class="legal corr">',
           '<p>This log lists every referee catch and every fix we made to a reading on indahl.ai or heuremen.org, newest first. Each row says what was published or staged, what was wrong, what it is now, why, and who caught it. Staged means the reading was checked before it went public. Fixes that made our own numbers weaker are listed the same way as the others.</p>',
           '<p>Our referee is a reviewer who reads the data and the page before or after publication. Our cold read is a read-only pass of the live site. Our own check is a test we run on our own work. An outside reader is anyone outside Heuremen LLC, named only when they ask to be. The issued bill QIA-2026-001 is listed here when anything about it changes.</p>',
           '<p>Rows are never removed. To report an error, use the <a href="/correction">correction or removal form</a>. Each row links to its page and to the plan, commit or receipt that records the fix. Where the working file that records a catch is not in the public repository, its path is printed.</p>',
           f'<p class="meta">Atom feed: <a href="/corrections.xml">corrections.xml</a> &middot; CSV: <a href="/corrections.csv" download>corrections.csv</a> &middot; Code: <a href="{GH}/blob/main/code/site/corrections.py">corrections.py</a></p>']
    day = None
    for r in rows:
        if r['date'] != day:
            if day is not None: out.append('</div>')
            day = r['date']; out.append(f'<h2 id="d{day}">{_day(day)}</h2><div class="corr-day">')
        pub = 'What was staged' if r['stage'] == 'staged' else 'What was published'
        tag = ('Staged' if r['stage'] == 'staged' else 'Public') + (' &middot; Weaker reading after the fix' if r['worse'] else '')
        src = '' if not _show_path(r['source']) else f' &middot; Working file: <code>{E(r["source"])}</code>'
        out.append(f'<article class="corr-row" id="{E(r["id"])}"><h3>{E(r["desk"])} <span class="meta">{tag}</span></h3>'
                   f'<p><b>{pub}.</b> {E(r["published"])}</p><p><b>What was wrong.</b> {E(r["wrong"])}</p>'
                   f'<p><b>What it is now.</b> {E(r["now"])}</p><p><b>Why.</b> {E(r["why"])}</p>'
                   f'<p class="meta">{_caught(r)} &middot; {_links(r)}{src} &middot; <a href="#{E(r["id"])}">{E(r["id"])}</a></p></article>')
    if day is not None: out.append('</div>')
    out.append('</section>')
    return '\n'.join(out)


def atom(rows):
    rows = sorted(rows, key=lambda r: (r['date'], r['id']), reverse=True)
    upd = (rows[0]['date'] if rows else '2026-11-10') + 'T00:00:00Z'
    ent = []
    for r in rows:
        first = re.split(r'(?<=\.)\s', r['wrong'], 1)[0]
        body = (f'<p><b>{"What was staged" if r["stage"] == "staged" else "What was published"}.</b> {E(r["published"])}</p><p><b>What was wrong.</b> {E(r["wrong"])}</p>'
                f'<p><b>What it is now.</b> {E(r["now"])}</p><p><b>Why.</b> {E(r["why"])}</p><p>{_caught(r)}.</p>')
        page = r['page'] if r['page'].startswith('http') else SITE + r['page']
        ent.append(f'<entry><id>tag:indahl.ai,2026:corrections/{E(r["id"])}</id><title>{E(r["desk"] + ": " + first)}</title>'
                   f'<link href="{SITE}/corrections#{E(r["id"])}"/><link rel="related" href="{E(page)}"/><updated>{r["date"]}T00:00:00Z</updated>'
                   f'<category term="{E(r["desk"])}"/><content type="html">{E(body)}</content></entry>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><id>tag:indahl.ai,2026:corrections</id>'
            f'<title>Heuremen LLC: corrections</title><link href="{SITE}/corrections.xml" rel="self"/><link href="{SITE}/corrections"/>'
            f'<updated>{upd}</updated><author><name>Heuremen LLC</name></author>' + ''.join(ent) + '</feed>\n')


CSV_COLS = ['id', 'date', 'desk', 'page', 'stage', 'published', 'wrong', 'now', 'why', 'caught_by', 'weaker_after_fix', 'source', 'commit', 'public_commit', 'links', 'receipt']


def to_csv(rows):
    s = io.StringIO(); w = csv.writer(s, lineterminator='\n'); w.writerow(CSV_COLS)
    for r in sorted(rows, key=lambda r: (r['date'], r['id']), reverse=True):
        w.writerow([r['id'], r['date'], r['desk'], r['page'] if r['page'].startswith('http') else SITE + r['page'], r['stage'], r['published'], r['wrong'], r['now'], r['why'],
                    r['caught_by'], 'yes' if r['worse'] else 'no', r['source'] if _show_path(r['source']) or r['source'].startswith('ledger:') else '', r.get('commit', ''), (GH + '/commit/' + r['public_commit']) if r.get('public_commit') else '',
                    ' '.join(r.get('links', [])), (SITE + '/r/' + receipt_name(r['receipt'])) if r.get('receipt') else ''])
    return s.getvalue()


# appended to the site stylesheet by the hook (the page CSP allows no inline style)
CSS = ('\n.corr-row{border-top:1px solid var(--rule);padding:10px 0 4px}.corr-row h3{margin:0 0 4px}.corr-row h3 .meta{font-size:13px;font-weight:400;margin-left:6px}'
       '.corr-row p{margin:4px 0;font-size:14.5px;line-height:1.5}.corr-row code{font-size:12px;word-break:break-all}\n')


def build(PAGES, page, hero_slim, FEED=None):
    rows = load()
    bad = gate(rows, PAGES)
    if bad: raise SystemExit('BUILD REFUSED (corrections gate):\n  ' + '\n  '.join(bad))
    PAGES['/corrections'] = page('/corrections', 'Corrections: Every Catch and Every Fix, in the Open | Heuremen LLC',
                                 'Every referee catch and every fix to a published or staged reading on indahl.ai and heuremen.org, with what was wrong, what it is now, why, and who caught it.',
                                 page_body(rows), hero_slim('Corrections', 'Every catch and every fix, in the open'))
    PAGES['/corrections'] = PAGES['/corrections'].replace('</head>', '<link rel="alternate" type="application/atom+xml" title="Heuremen LLC: corrections" href="/corrections.xml">\n</head>', 1)
    for name, text in (('corrections.xml', atom(rows)), ('corrections.csv', to_csv(rows))):
        p = os.path.join(PUB, name)
        if not os.path.exists(p) or open(p, encoding='utf-8').read() != text: open(p, 'w', encoding='utf-8').write(text)
    if FEED is not None: FEED.append(('/corrections', 'Corrections : Every Catch and Every Fix, in the Open', 'Every referee catch and every fix to a published or staged reading, with what was wrong, what it is now and why.'))
    return len(rows)


if __name__ == '__main__':
    if '--gate' in sys.argv:
        bad = gate()
        if bad: print('CORRECTIONS GATE FAILED:\n  ' + '\n  '.join(bad)); sys.exit(1)
        print(f'corrections gate: ok, every row links to a real file or commit'); sys.exit(0)
    print(__doc__)
