#!/usr/bin/env python3
"""receipts.py: one public receipt page per ledger row, at https://indahl.ai/r/<id> (10 Nov 2026, "receipts available to anyone").

  receipts.py build          write cloudflare-workers/heuremen-door/public/r/ (one page per row, the index /r/, one page per desk /r/desk/<slug>,
                             and r/sitemap.txt, which the worker appends to /sitemap.xml)
  receipts.py check          the gate: every ledger row has its receipt page, and every receipt link on a served page resolves (exit 1 if not)
  receipts.py live N         open N random receipts and N random receipt links from served pages on https://indahl.ai (exit 1 on any miss)
  receipts.py seed-indexnow  record the current receipt pages in tools/indexnow_state.json without sending (first release only), so IndexNow
                             is told about receipts only when one changes

A receipt prints, for one row: the number as published and the sentence it sits in on each page, the ledger value with its outcome and interval,
the source file with the line the number is read from, its public copy and file date, the code file and the commit that holds it, the row's sha256
and the ledger file's sha256 when that version of the row was first committed (or first built for the site), its history, and the OpenTimestamps and
Wayback receipts when ledger/stamps/ holds them. Nothing is deleted: withdrawn and superseded rows keep their pages, marked, with a link forward.

link_pages(PAGES) is called by indahl-ai/build_site.py: for every live row whose snippet is on a page, a small receipt link (class "rcpt") goes right
after the snippet. check_ledger.norm strips those links, so a receipt link never changes the text a ledger snippet is compared with.
Pages are plain HTML, no scripts. Public copy: plain sentences, no semicolons, no counts in titles or headings."""
import datetime as D, hashlib, html, json, os, random, re, subprocess, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ledger import LEDGER, SURFACES, ROOT, load
_load_all = load
def load():   # 10 Nov: staged rows (a desk before its first ship) get no public receipt until the desk flips them to live
    return {k: v for k, v in _load_all().items() if v.get('status') != 'staged'}
B = ROOT; SITE = os.path.join(B, 'indahl-ai'); W = os.path.join(B, 'cloudflare-workers', 'heuremen-door')
OUT = os.path.join(W, 'public', 'r'); SEEN = os.path.join(HERE, 'receipts_seen.json'); LINKS = os.path.join(HERE, 'receipts_links.json')
STAMPS = os.path.join(HERE, 'stamps'); MIRROR = os.path.join(B, 'public_mirror')
ORIGIN = 'https://indahl.ai'; E = html.escape

# ---------- ids ----------
ALIAS = (('flock', 'house'),)   # 8 Nov 2026 public copy says "house" (site rule 0b.10); the ledger key keeps its own word, the row hash commits it
def public_id(rid):
    for a, b in ALIAS: rid = rid.replace(a, b)
    return rid
def slug(rid):
    return re.sub(r'[^A-Za-z0-9._-]', lambda m: '~%02X' % ord(m.group()), public_id(rid))
def href(rid): return '/r/' + slug(rid)

# ---------- text ----------
def norm(s):
    from check_ledger import norm as _n
    return _n(s)
RC_A = re.compile(r'<a class="rcpt"[^>]*>[^<]*</a>')
DENY = re.compile(r'(?i)\bSage\b(?! V)|Wayfinder|\bBones\b|\bNova\b|NovaTable|Claude Code|An AI assistant|flock|his word|his call|\bhis\b|/q\b|/Users/|PREREG|session transcript|Bonefish')
def clean_prose(t):
    """Ledger prose made public: cut the machine tail, split semicolons into sentences, drop any clause that names a person or the house's tools."""
    if not t: return ''
    t = t.split(' | ')[0].strip()
    parts = [p.strip() for p in re.split(r';\s+|;\s*$', t) if p.strip()]
    keep = [p for p in parts if not DENY.search(p)]
    out = []
    for p in keep:
        p = p.replace(';', ',')
        p = re.sub(r'(?i)\bby hand\b', 'in full', p); p = re.sub(r'(?i)\bhand[- ]?(checked|read|counted)\b', r'\1 in full', p); p = re.sub(r'(?i)\bhand-written\b', 'written', p)
        p = p[0].upper() + p[1:] if p[:1].islower() and not re.match(r'^[a-z]+[A-Z0-9_]', p) else p
        out.append(p if p.endswith(('.', '?', '!', ')')) else p + '.')
    return ' '.join(out)
def day(iso):
    try: d = D.datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except Exception: return iso[:10] if iso else ''
    return f'{d.day} {d.strftime("%b")} {d.year}'

# ---------- the served pages ----------
_served = None
def served():
    """path -> file (relative to indahl-ai), read from pages.js: the pages the worker serves."""
    global _served
    if _served is None:
        js = open(os.path.join(SITE, 'pages.js'), encoding='utf-8').read()
        imp = dict(re.findall(r"import (P\d+) from '\./([^']+\.html)';", js))
        _served = {p: imp[v] for p, v in re.findall(r"^\s*'([^']+)': (P\d+),?$", js, re.M) if v in imp}
    return _served
def file_to_path():
    return {f: p for p, f in served().items()}

BLOCK = re.compile(r'<(?:/?(?:p|li|h[1-6]|tr|caption|figcaption|dd|dt|blockquote|section|div|header|footer|main|ul|ol|table|thead|tbody|tfoot|details|summary|nav|article|aside|pre|form|label|option)\b[^>]*|br\s*/?)>', re.I)
_blocks = {}
def blocks_of(path_or_file, raw=None):
    """[(plain, shown)] for each block of a page: plain is compared with snippets, shown keeps table cells apart."""
    if path_or_file in _blocks: return _blocks[path_or_file]
    s = raw if raw is not None else open(path_or_file, encoding='utf-8', errors='ignore').read()
    s = RC_A.sub('', s)
    s = re.sub(r'(?is)<head\b.*?</head>|<(script|style|svg|noscript)\b.*?</\1>|<!--.*?-->', ' ', s)
    out = []
    for ch in BLOCK.split(s):
        plain = norm(ch)
        if not plain: continue
        shown = norm(re.sub(r'(?i)</t[dh]>\s*<t[dh][^>]*>', ' \u00b7 ', ch)) if re.search(r'(?i)<t[dh]', ch) else plain
        out.append((plain, shown))
    _blocks[path_or_file] = out
    return out
SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9\u201c"(])')
def trim_sentence(text, snip, cap=420):
    """The sentence (or sentences) of text that hold snip, cut at sentence ends, never longer than cap without an ellipsis."""
    i = text.find(snip)
    if i < 0 or len(text) <= cap: return text
    starts = [0] + [m.end() for m in SENT.finditer(text)]
    a = max([x for x in starts if x <= i] or [0]); ends = [m.start() for m in SENT.finditer(text)] + [len(text)]
    b = min([x for x in ends if x >= i + len(snip)] or [len(text)])
    out = text[a:b]
    if len(out) > cap:
        a2 = max(a, i - cap // 2); b2 = min(b, i + len(snip) + cap // 2)
        out = ('\u2026' if a2 > 0 else '') + text[a2:b2].strip() + ('\u2026' if b2 < len(text) else '')
    else:
        out = ('\u2026 ' if a > 0 else '') + out.strip() + (' \u2026' if b < len(text) else '')
    return out
def find_in_html(fp, snip, raw=None):
    n = norm(snip)
    if not n: return None
    for plain, shown in blocks_of(fp, raw):
        if n in plain:
            return trim_sentence(shown, n) if n in shown else trim_sentence(plain, n)
    full = ' '.join(p for p, _ in blocks_of(fp, raw))
    i = full.find(n)
    if i >= 0: return trim_sentence(full[max(0, i - 200): i + len(n) + 200], n)
    return None
def detex(s):
    s = re.sub(r'\\(?:ref|eqref|cite|citep|citet|label|autoref|cref)\{[^}]*\}', '', s)
    for a, b in (('\\textmu ', '\u00b5'), ('\\rangle', '\u27e9'), ('\\langle', '\u27e8'), ('\\textmu', '\u00b5'), ('\\us{}', ' \u00b5s'), ('\\us', ' \u00b5s'), ('\\chi', '\u03c7'), ('^\\circ', '\u00b0'),
                 ('\\circ', '\u00b0'), ('\\%', '%'), ('\\pm', '\u00b1'), ('\\times', '\u00d7'), ('\\,', ' '), ('~', ' '), ('\\&', '&'), ('\\sim', '~'), ('\\approx', '\u2248'), ('\\le', '\u2264'), ('\\ge', '\u2265')):
        s = s.replace(a, b)
    s = re.sub(r'\\(?:texttt|emph|textbf|mathrm|textit|text)\{([^}]*)\}', r'\1', s)
    s = s.replace('$', '').replace('{', '').replace('}', '').replace(' & ', ' \u00b7 ').replace('\\\\', ' ')
    s = re.sub(r'\\[a-zA-Z]+\*?', '', s)
    return re.sub(r'\s+', ' ', s).strip()
_texts = {}
def find_in_text(fp, snip):
    if fp not in _texts:
        try:
            t = open(fp, encoding='utf-8', errors='ignore').read()
            if fp.endswith('.json'):
                strs = []
                def walk(o):
                    if isinstance(o, str): strs.append(o)
                    elif isinstance(o, dict): [walk(v) for v in o.values()]
                    elif isinstance(o, list): [walk(v) for v in o]
                try: walk(json.loads(t)); t = [norm(x) for x in strs]
                except Exception: t = [norm(t)]
            else:
                t = [norm(detex(t))] if fp.endswith('.tex') else [re.sub(r'\s+', ' ', re.sub(r'\\[a-zA-Z]+\*?', '', norm(t)))]
        except Exception: t = []
        _texts[fp] = t
    n = norm(detex(snip)) if fp.endswith('.tex') else norm(snip)
    for t in _texts[fp]:
        i = t.find(n)
        if i >= 0: return trim_sentence(t[max(0, i - 260): i + len(n) + 260] if len(t) > 900 else t, n)
    return None

def surface_places(key):
    """(label, url, kind, file) for a surface: kind 'page' (an indahl.ai page), 'pages' (search these), 'doc' (a public document), 'private' (not on the web)."""
    f2p = file_to_path()
    if key.startswith('site:'):
        rel = key[5:]; u = 'https://heuremen.org/' + re.sub(r'(^|/)index\.html$', r'\1', rel)
        return [('heuremen.org: ' + (re.sub(r'(^|/)index\.html$', '', rel) or 'home'), u, 'doc', os.path.join(B, 'heuremen.org', rel))]
    p = SURFACES.get(key, '')
    if p.startswith('indahl-ai/') and p.endswith('.html'):
        rel = p[len('indahl-ai/'):]
        if rel in f2p: return [(None, ORIGIN + (f2p[rel] if f2p[rel] != '/' else '/'), 'page', os.path.join(SITE, rel))]
        if key == 'sad': return [(None, ORIGIN + pth, 'page', os.path.join(SITE, f)) for pth, f in served().items() if pth == '/hermes/model' or pth.startswith('/hermes/model/')]
        return []
    if key == 'indahl': return [(None, ORIGIN + pth, 'page', os.path.join(SITE, f)) for pth, f in served().items()]
    if key.startswith('qia_') and key.endswith('_js'): return [('QIA live panel', ORIGIN + '/qia', 'doc', os.path.join(B, p))]
    if key == 'model_live': return [('MODEL live claims rounds', ORIGIN + '/hermes/model', 'doc', os.path.join(B, p))]
    fixed = {'paper': ('Paper, A Readout Is Not an Idle (PDF)', 'https://heuremen.org/a-readout-is-not-an-idle.pdf'),
             'abstract': ('Abstract of the paper A Readout Is Not an Idle', 'https://heuremen.org/a-readout-is-not-an-idle.pdf'),
             'bill': ('QIA bill QIA-2026-001 (PDF)', ORIGIN + '/quantum-idle-audit.pdf'),
             'faults': ('Faults (PDF)', 'https://heuremen.org/faults.pdf'), 'guards': ('Guards (PDF)', 'https://heuremen.org/guards.pdf'),
             'zenodo': ('Zenodo record of the paper', 'https://doi.org/10.5281/zenodo.23169755')}
    if key in fixed:
        lab, u = fixed[key]; fp = p if p.startswith('/') else os.path.expanduser(p) if p.startswith('~') else os.path.join(B, p)
        return [(lab, u, 'doc', fp)]
    if key == 'iris_paper': return [('IRIS paper manuscript, not yet public', None, 'private', os.path.join(B, p))]
    if key == 'messages': return [('Message to outside readers, not a web page', None, 'private', os.path.expanduser(p))]
    return []

_titles = {}
def page_title(url):
    if url in _titles: return _titles[url]
    t = None
    if url and url.startswith(ORIGIN):
        pth = url[len(ORIGIN):] or '/'
        f = served().get(pth)
        if f:
            m = re.search(r'<title>(.*?)</title>', open(os.path.join(SITE, f), encoding='utf-8', errors='ignore').read(), re.S)
            if m: t = html.unescape(m.group(1)).replace(' | Heuremen LLC', '').strip()
    _titles[url] = t or url
    return _titles[url]

def placements(r):
    """Where the row's number is printed: [(label, url, sentence or None, kind)]."""
    out = []
    for s in r['surfaces']:
        cands = surface_places(s['surface']); hit = None
        for lab, u, kind, fp in cands:
            if kind == 'private': hit = (lab, None, None, kind, None); break
            if not fp or not os.path.exists(fp): continue
            sen = find_in_html(fp, s['text']) if fp.endswith('.html') else find_in_text(fp, s['text'])
            shown = detex(s['text']) if fp.endswith('.tex') else html.unescape(s['text'])
            if sen: hit = (lab or page_title(u), u, sen, kind, shown); break
        if not hit and cands:
            lab, u, kind, fp = cands[0]
            hit = (lab or page_title(u), u, None, kind, detex(s['text']) if (fp or '').endswith('.tex') else html.unescape(s['text']))
        if hit and hit not in out: out.append(hit)
    return out

# ---------- desks ----------
def nav_labels():
    try: s = open(os.path.join(SITE, '404.html'), encoding='utf-8').read()
    except Exception: return {}
    return {h: html.unescape(t) for h, t in re.findall(r'<a(?: class="[^"]*")? href="(/[^"#?]*)">([^<]+)</a>', s.split('<main')[0])}
_NAV = None
def desk_of_surface(key):
    global _NAV
    if _NAV is None: _NAV = nav_labels()
    if key in ('paper', 'abstract', 'zenodo', 'messages'): return ('paper', 'Paper: A Readout Is Not an Idle', 'https://heuremen.org/a-readout-is-not-an-idle.pdf')
    if key.startswith('site:'): return ('heuremen-org', 'heuremen.org experiments', 'https://heuremen.org/')
    if key == 'bill': return ('qia-bill', 'QIA bill QIA-2026-001', ORIGIN + '/quantum-idle-audit.pdf')
    if key in ('faults', 'guards'): return ('faults-guards', 'Faults and Guards', 'https://heuremen.org/faults.pdf')
    if key == 'iris_paper': return ('iris-paper', 'IRIS paper manuscript', None)
    if key in ('sad', 'model_live', 'model_pack'): return ('model', 'MODEL', ORIGIN + '/hermes/model')
    if key.startswith('qia_') and key.endswith('_js'): return ('qia', 'QIA', ORIGIN + '/qia')
    if key == 'indahl': return ('home', 'Home', ORIGIN + '/')
    p = SURFACES.get(key, '')
    if p.startswith('indahl-ai/') and p.endswith('.html'):
        pth = file_to_path().get(p[len('indahl-ai/'):])
        if pth:
            if pth.startswith('/hermes/model'): return ('model', 'MODEL', ORIGIN + '/hermes/model')
            sl = 'home' if pth == '/' else pth.strip('/').replace('/', '-')
            nm = _NAV.get(pth) or ('Home' if pth == '/' else pth.strip('/').replace('/', ' ').upper())
            nm = {'/atlas/data-pack': 'ATLAS Data Pack', '/oy/data-pack': 'OY Data Pack', '/media': 'Media', '/media/2026-10-26': 'Media release of 26 Oct 2026'}.get(pth, nm)
            if pth.startswith('/atlas/') and nm.isupper(): nm = 'ATLAS ' + nm
            if pth.startswith('/oy/') and nm.isupper(): nm = 'OY ' + nm
            return (sl, nm, ORIGIN + pth)
    return None
PRIORITY = lambda k: 0 if (SURFACES.get(k, '').startswith('indahl-ai/') or k in ('sad', 'model_live', 'indahl') or (k.startswith('qia_') and k.endswith('_js'))) else 1
def desks(rows):
    """row id -> (slug, name, url). A row printed nowhere now goes with the desk most rows of its id family sit on."""
    got = {}
    for r in rows.values():
        ks = sorted((s['surface'] for s in r['surfaces']), key=PRIORITY)
        for k in ks:
            d = desk_of_surface(k)
            if d: got[r['id']] = d; break
    if True:
        for r in rows.values():   # live value rows sit with their headline
            if r.get('kind') == 'live_value' and r.get('live_of') in got: got[r['id']] = got[r['live_of']]
    fam = {}
    for rid, d in got.items(): fam.setdefault(rid.split('.')[0], []).append(d)
    for r in rows.values():
        if r['id'] in got: continue
        ds = fam.get(r['id'].split('.')[0])
        got[r['id']] = max(set(ds), key=ds.count) if ds else ('other', 'Other rows', None)
    return got

# ---------- git ----------
def git(repo, *a):
    return subprocess.run(['git', '-C', repo] + list(a), capture_output=True, text=True).stdout
def blob_sha(path):
    try: data = open(path, 'rb').read()
    except Exception: return None
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
_repo_of = {}
def repo_of(path):
    d = os.path.dirname(path)
    if d in _repo_of: return _repo_of[d]
    top = subprocess.run(['git', '-C', d, 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip() if os.path.isdir(d) else ''
    _repo_of[d] = top or None
    return _repo_of[d]
_first = {}
def first_commit_with(repo, rel, blob):
    """The earliest commit in repo where rel holds exactly this blob: (hash, iso date), or None."""
    k = (repo, rel, blob)
    if k in _first: return _first[k]
    out = git(repo, 'log', '--format=C %H %cI', '--raw', '--no-abbrev', '--', rel); cur = None; best = None
    for line in out.splitlines():
        if line.startswith('C '): _, h, t = line.split(' ', 2); cur = (h, t)
        elif line.startswith(':') and cur:
            f = line.split()
            if len(f) >= 4 and f[3] == blob: best = cur   # log is newest first, so the last match is the earliest
    _first[k] = best
    return best
_mirror_index = None
def mirror_index():
    """git blob sha -> [(repo name, path)] for every file tracked in the public repositories (Heuremen-LLC/indahl.ai and Heuremen-LLC/heuremen.org)."""
    global _mirror_index
    if _mirror_index is None:
        _mirror_index = {}
        for name in ('indahl.ai', 'heuremen.org'):
            repo = os.path.join(MIRROR, name)
            if not os.path.isdir(os.path.join(repo, '.git')): continue
            for line in git(repo, 'ls-files', '-s').splitlines():
                m = re.match(r'\d+ ([0-9a-f]{40}) \d\t(.+)$', line)
                if m: _mirror_index.setdefault(m.group(1), []).append((name, m.group(2)))
    return _mirror_index
CODE_DIRS = {'time_index': 'time', 'caca_index': 'cada', 'status_index': 'uptime', 'forecast_index': 'forecast', 'cadence_index': 'cadence', 'trials_index': 'trials',
             'launch_index': 'launch', 'linkrot_index': 'linkrot', 'tape_index': 'tape', 'hosts_index': 'hosts', 'campus_index': 'campus', 'airq_index': 'airq',
             'ailuminate_index': 'ailuminate', 'hpt_index': 'hpt', 'weights_index': 'weights', 'bts_index': 'airline', 'fedsep_index': 'fedsep', 'revise_index': 'revise',
             'stack_index': 'stack', 'pkginstall_index': 'pkginstall', 'seat_index': 'seat', 'secrecords_index': 'secrecords', 'change_index': 'change', 'hfsize_index': 'hfsize',
             'hflicense_index': 'hflicense', 'pkglicense_index': 'pkglicense', 'support_index': 'support', 'arxivdrift_index': 'arxivdrift', 'water_index': 'water', 'neo_index': 'neo', 'seasonal_index': 'seasonal', 'rank_index': 'rank', 'steo_index': 'steo', 'quake_index': 'quake', 'census_index': 'census', 'fidelity_index': 'fidelity', 'census_coverage': 'census-coverage', 'flu_index': 'flu', 'tornado_index': 'tornado', 'credit_index': 'credit', 'cone_index': 'cone', 'solar_index': 'solar',
             'wiki_index': 'wiki', 'social_index': 'social', 't1t2_check': 't1t2-check', 'qia_mirror': 'mirror', 'iris_index': 'iris', 'mlperf_index': 'model', 'yo': 'yo',
             'qia_offchain': 'qia-offchain', 'qia_queue': 'qia-queue', 'qia_cal': 'qia-cal', 'bq_index': 'bigquery', 'darkwave_kit': 'darkwave-kit', 'iris_package': 'iris-package',
             'atlas_package': 'atlas-data-pack', 'list_packs': 'list-packs', 'oy_package': 'oy-data-pack', 'model_package': 'model-data-pack'}   # ledger/push_public.sh DESKS and packs
def public_copy(path):
    """For a kept file: its public copy, the first public commit that holds it unchanged, the file's commit in our own repository,
    and, when no public copy holds this exact version, the public file of the same name in the desk's code folder."""
    b = blob_sha(path)
    if not b: return None
    out = {'blob': b}
    for name, rel in mirror_index().get(b, [])[:1]:
        c = first_commit_with(os.path.join(MIRROR, name), rel, b)
        out['public'] = dict(repo=name, path=rel, commit=c[0] if c else None, date=c[1] if c else None,
                             url=f'https://github.com/Heuremen-LLC/{name}/blob/{c[0] if c else "main"}/{rel}')
        if name == 'heuremen.org': out['public']['live'] = 'https://heuremen.org/' + re.sub(r'(^|/)index\.html$', r'\1', rel)
    if 'public' not in out and path.startswith(B + '/'):
        top = os.path.relpath(path, B).split('/')[0]; cd = CODE_DIRS.get(top)
        if cd:
            rel = 'code/' + cd + '/' + os.path.relpath(path, os.path.join(B, top))
            if os.path.exists(os.path.join(MIRROR, 'indahl.ai', rel)):
                last = git(os.path.join(MIRROR, 'indahl.ai'), 'log', '-1', '--format=%H %cI', '--', rel).split()
                if last: out['public_other'] = dict(repo='indahl.ai', path=rel, commit=last[0], date=last[1], url=f'https://github.com/Heuremen-LLC/indahl.ai/blob/{last[0]}/{rel}')
    repo = repo_of(path)
    if repo:
        rel = os.path.relpath(path, repo); c = first_commit_with(repo, rel, b)
        if c: out['own'] = dict(repo=os.path.basename(repo), commit=c[0], date=c[1])
        else:
            last = git(repo, 'log', '-1', '--format=%H %cI', '--', rel).split()
            out['own_changed'] = dict(repo=os.path.basename(repo), commit=last[0] if last else None, date=last[1] if last else None)
    return out

def show_path(p):
    if not p: return ''
    ap = p if p.startswith('/') else os.path.join(B, p)
    return public_id(os.path.relpath(ap, B) if ap.startswith(B + '/') else os.path.basename(ap))
def abspath(p): return p if p.startswith('/') else os.path.join(B, p)

SCRIPT_EXT = ('.py', '.sh', '.swift', '.c', '.js')
def derive_code(src):
    """The script that writes a source file: the row's own record first, else the script in the source's folder (or one up) that names the file."""
    if not src: return None
    if src.endswith(SCRIPT_EXT): return (src, 'The source is itself the code.')
    base = os.path.basename(src); d = os.path.dirname(src); cands = []
    for dd in (d, os.path.dirname(d)):
        if not dd.startswith(B + '/') or dd == B or not os.path.isdir(dd): continue
        for f in sorted(os.listdir(dd)):
            if not f.endswith(SCRIPT_EXT) or '.bak' in f or '.pre-' in f: continue
            fp = os.path.join(dd, f)
            try: t = open(fp, encoding='utf-8', errors='ignore').read()
            except Exception: continue
            if base in t or os.path.splitext(base)[0] in t and len(os.path.splitext(base)[0]) > 5:
                w = bool(re.search(r"""open\([^)]*['"]w|write_text|\.dump\(|> *["']?\$?\w*""" + re.escape(base), t))
                cands.append((0 if dd == d else 1, 0 if w else 1, f, fp))
        if cands: break
    if cands:
        cands.sort(); return (cands[0][3], 'Found by name: the script in the source folder that names this file.')
    if os.path.isdir(d):
        ss = [f for f in os.listdir(d) if f.endswith(SCRIPT_EXT) and '.bak' not in f and '.pre-' not in f]
        if len(ss) == 1: return (os.path.join(d, ss[0]), 'Found by place: the only script in the source folder.')
    return None

# ---------- ledger history in git ----------
def ledger_git_index():
    """sha256 of a row's exact line -> (commit, iso date, sha256 of ledger.jsonl at that commit), earliest first."""
    idx = {}
    for line in git(HERE, 'log', '--reverse', '--format=%H %cI', '--', 'ledger.jsonl').splitlines():
        h, t = line.split(' ', 1)
        data = subprocess.run(['git', '-C', HERE, 'show', f'{h}:ledger.jsonl'], capture_output=True).stdout
        fsha = hashlib.sha256(data).hexdigest()
        for ln in data.splitlines():
            if ln.strip():
                k = hashlib.sha256(ln).hexdigest()
                if k not in idx: idx[k] = (h, t, fsha)
    return idx
def raw_lines():
    out = {}
    for ln in open(LEDGER, 'rb').read().splitlines():
        if ln.strip(): out[json.loads(ln)['id']] = ln
    return out

# ---------- stamps (written by the stamps agent, when it exists) ----------
def stamps_index():
    """ledger/stamps (stamps.py): the releases with their OpenTimestamps proofs, and the Internet Archive captures by URL."""
    rel = []; ots = {}; wb = {}
    try: rel = [json.loads(l) for l in open(os.path.join(STAMPS, 'releases.jsonl')) if l.strip()]
    except Exception: pass
    try: ots = json.load(open(os.path.join(STAMPS, 'ots_status.json')))
    except Exception: pass
    try:
        for l in open(os.path.join(STAMPS, 'wayback.jsonl')):
            try: w = json.loads(l)
            except Exception: continue
            if w.get('capture') and w.get('url'): wb[w['url'].rstrip('/') or w['url']] = w   # newest last
    except Exception: pass
    rel.sort(key=lambda x: x.get('released_at', ''))
    return dict(releases=rel, ots=ots, wayback=wb)
def utc(iso):
    try: return D.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(D.timezone.utc)
    except Exception: return None
def stamp_lines(sidx, pub_date, urls):
    out = []; t0 = utc(pub_date)
    for x in sidx.get('releases', []):
        t = utc(x.get('released_at', ''))
        if t and t0 and t >= t0:
            st = sidx.get('ots', {}).get(x['id'], x.get('ots', 'pending'))
            out.append(f'OpenTimestamps: release <a href="/receipts/stamps/{E(x["file"])}">{E(x["id"])}</a> of {E(day(x["released_at"]))} records the ledger file sha256 <code class="rp-h">{E(x.get("ledger_sha256", ""))}</code>, '
                       f'a ledger that holds this row as it stands. Proof: <a href="/receipts/stamps/{E(x["file"])}.ots">{E(x["file"])}.ots</a> ({E("confirmed in Bitcoin" if st in ("confirmed", "complete", "upgraded") else "waiting for its Bitcoin block" if st == "pending" else st)}).')
            break
    for u, lab in urls:
        w = sidx.get('wayback', {}).get(u.rstrip('/') or u)
        if w: out.append(f'Internet Archive copy of {E(lab)}: <a href="{E(w["capture"])}">{E(w["capture"])}</a> ({E(day(w.get("at", "")))}).')
    return out

# ---------- the page ----------
FOOT = None
def foot(path):
    try:
        sys.path.insert(0, SITE); from hlcref import ref
        rf = ref('page:' + path)
    except Exception: rf = ''
    return ('<footer class="foot"><div class="wrap">\n<p class="fl"><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="/security">Security</a><a href="/conflict-of-interest">Conflict of interest</a><a href="https://github.com/Heuremen-LLC/indahl.ai">GitHub</a><a href="https://huggingface.co/indahl">Hugging Face</a><a href="/changes">Changes</a><a href="/community">Community</a><a href="/r/">Receipts</a><a href="/contact">Inquiry</a></p>\n'
            '<p class="fs">Heuremen LLC</p>\n<p class="fs">&ldquo;We found it.&rdquo;</p>\n'
            '<p class="ai">Heuremen LLC reserves all rights. Content and data may be read, downloaded and cited with attribution. Text and data mining and use as AI training data are not permitted. <a href="/terms#ai-training">Details</a>' + (f' &middot; Reference {rf}' if rf else '') + '</p>\n</div></footer>')
MARK = '<svg class="mark" viewBox="0 0 200 200" aria-hidden="true"><polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5"/></svg>'
def cssv():
    try: return re.search(r'/style\.css\?v=([0-9a-f]{8})', open(os.path.join(SITE, '404.html'), encoding='utf-8').read()).group(1)
    except Exception: return ''
def shell(path, title, desc, h1, sub, body, css):
    url = ORIGIN + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(url)}">
<meta name="tdm-reservation" content="1">
<meta name="tdm-policy" content="https://indahl.ai/terms#ai-training">
<meta property="og:site_name" content="Heuremen LLC">
<meta property="og:type" content="website">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{E(url)}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="theme-color" content="#f7f0e0">
<link rel="stylesheet" href="/style.css?v={css}">
</head>
<body class="rp">
<header class="top"><div class="wrap bar">
<a class="brand" href="/">{MARK}<span>Heuremen LLC</span></a>
<nav class="links"><a href="/qia">QIA</a><a href="/iris">IRIS</a><a href="/hermes">HERMES</a><a href="/atlas">ATLAS</a><a href="/oy">OY</a><a href="/social">SOCIAL</a><a href="/r/" aria-current="page">RECEIPTS</a></nav>
</div></header>
<section class="hero slim"><div class="wrap"><h1>{h1}</h1>{f'<p class="sub">{sub}</p>' if sub else ''}</div></section>
<main class="wrap rp-main">
{body}
</main>
{foot(path)}
</body>
</html>
'''

STATUS_WORD = {'live': 'Live', 'withdrawn': 'Withdrawn', 'held': 'Held', 'cannot_tell': 'Cannot tell'}
def iv(r):
    return f'[{r["lo"]}, {r["hi"]}]' if r.get('lo') not in (None, '') and r.get('hi') not in (None, '') else ''

def build_rows(rows):
    """Everything a receipt needs, per row (no HTML yet)."""
    lines = raw_lines(); gidx = ledger_git_index()
    seen = json.load(open(SEEN)) if os.path.exists(SEEN) else {}
    fsha_now = hashlib.sha256(open(LEDGER, 'rb').read()).hexdigest(); now = D.datetime.now().astimezone().isoformat(timespec='seconds')
    sidx = stamps_index(); dk = desks(rows)
    kids = {}
    for r in rows.values():
        if r.get('kind') == 'live_value' and r.get('live_of'): kids.setdefault(r['live_of'], []).append(r['id'])
    for k in kids: kids[k].sort()
    info = {}
    for rid, r in rows.items():
        ln = lines[rid]; rsha = hashlib.sha256(ln).hexdigest()
        if rsha in gidx: pub = dict(how='commit', commit=gidx[rsha][0], date=gidx[rsha][1], ledger_sha256=gidx[rsha][2])
        else:
            if rsha not in seen: seen[rsha] = dict(id=rid, ledger_sha256=fsha_now, at=now)
            pub = dict(how='build', date=seen[rsha]['at'], ledger_sha256=seen[rsha]['ledger_sha256'])
        info[rid] = dict(row_sha256=rsha, pub=pub, desk=dk[rid], stamps=sidx)
    tmp = SEEN + '.tmp'; json.dump(seen, open(tmp, 'w'), indent=0, sort_keys=True); os.replace(tmp, SEEN)
    return info, kids

def forward_links(r, rows, kids):
    """For a row that no longer stands: the rows that carry it now."""
    fw = []
    if r.get('kind') == 'live_value':
        sib = kids.get(r.get('live_of'), []); i = sib.index(r['id']) if r['id'] in sib else -1
        if 0 <= i < len(sib) - 1: fw.append(sib[i + 1])
    if r['status'] != 'live':
        txt = ' '.join(str(h.get('why', '')) + ' ' + str(h.get('change', '')) for h in r['history'])
        for m in re.finditer(r'\b([a-z][a-z0-9_]*(?:\.[A-Za-z0-9_:/-]+)+)', txt):
            c = m.group(1).rstrip('.,)')
            for cc in [c] + (lambda b: [b.rsplit('.', 1)[0] + '.' + x for x in c.rsplit('.', 1)[1].split('/')] if '/' in c.rsplit('.', 1)[-1] else [])(c):
                if cc in rows and cc != r['id'] and rows[cc]['status'] == 'live' and cc not in fw: fw.append(cc)
        if not fw:
            mine = {(s['surface'], norm(s['text'])) for s in r['surfaces']}
            for o in rows.values():
                if o['status'] == 'live' and o['id'] != r['id'] and mine & {(s['surface'], norm(s['text'])) for s in o['surfaces']}: fw.append(o['id'])
    return fw[:6]

def surface_label(key):
    key = re.match(r'(site:[^:\s]+|[A-Za-z0-9_]+)', key.strip()).group(1) if re.match(r'(site:[^:\s]+|[A-Za-z0-9_]+)', key.strip()) else key
    for lab, u, kind, fp in surface_places(key)[:1]:
        return lab or page_title(u)
    return 'a page'
def history_items(r):
    out = []
    for h in r['history']:
        ch = str(h.get('change', '')); at = day(h.get('at', ''))
        if ch == 'added': t = 'Entered the ledger.'
        elif ch.startswith('on '): t = f'Printed on {E(surface_label(ch[3:]))}.'
        elif ch.startswith('off '): t = f'Taken off {E(surface_label(ch[4:]))}. The row stays.'
        elif ch == 'withdrawn': w = clean_prose(h.get('why', '')); t = 'Withdrawn.' + (' Reason given: ' + E(w) if w else '')
        elif ch == 'cannot_tell': w = clean_prose(h.get('why', '')); t = 'Moved to cannot tell.' + (' Reason given: ' + E(w) if w else '')
        else:
            m = re.match(r'^([a-z_.]+): (.*) -> (.*)$', ch, re.S)
            if m and m.group(1) in ('value', 'lo', 'hi', 'outcome', 'unit'):
                f = {'lo': 'Low end of the interval', 'hi': 'High end of the interval'}.get(m.group(1), m.group(1).capitalize())
                t = f'{f} changed from <code>{E(m.group(2).strip(chr(39)))}</code> to <code>{E(m.group(3).strip(chr(39)))}</code>.'
            elif m and m.group(1) == 'status': t = f'Status changed to {E(m.group(3).strip(chr(39)))}.'
            elif m and m.group(1).startswith('source'): t = 'Source pointer corrected.'
            elif m and m.group(1) == 'code': t = 'Code file recorded.'
            elif m and m.group(1) == 'witness': t = 'Job records linked.'
            elif m and m.group(1) == 'claim': t = 'Description in the ledger reworded.'
            else: t = 'Ledger entry updated.'
        out.append(f'<li><span class="rp-d">{E(at)}</span> {t}</li>')
    return out

def code_block(r):
    src = abspath(r['source']['file']); rec = r.get('code'); lines = []
    if r.get('kind') == 'live_headline':
        cands = [(abspath('watch/headlines.py'), 'Recorded in the row: the producer function ' + E(r['source']['grep'].replace('def ', '').rstrip(':')) + ' in watch/headlines.py.'),
                 (abspath('ledger/live_headlines.py'), 'Recorded in the row: the writer of the value rows.')]
    elif r.get('kind') == 'live_value':
        cands = [(abspath('ledger/live_headlines.py'), 'Recorded in the row: the writer of this value row.'), (abspath('watch/headlines.py'), 'The producer of the headline it reads.')]
    elif rec: cands = [(abspath(rec), 'Recorded in the row.')]
    else:
        d = derive_code(src); cands = [d] if d else []
    if not cands:
        d = os.path.dirname(src)
        near = sorted(f for f in os.listdir(d) if f.endswith(SCRIPT_EXT) and '.bak' not in f and '.pre-' not in f) if os.path.isdir(d) else []
        if not near or len(near) > 8: return ['<p>Code file: not recorded. The row names its source file only, and no script in the source folder names that file.</p>']
        lines.append('<p>Code file: not recorded in the row, and no script names the source file. The scripts kept in the same folder:</p>')
        cands = [(os.path.join(d, f), 'Kept beside the source.') for f in near]
    for fp, why in cands:
        pc = (public_copy(fp) if os.path.exists(fp) else None) or {}
        bits = [f'<code>{E(show_path(fp))}</code>. {why}']
        if pc.get('public'):
            p = pc['public']
            bits.append(f'Public copy of this exact version: <a href="{E(p["url"])}">{E(p["repo"])}/{E(p["path"])}</a>' + (f', commit <code>{E(p["commit"][:12])}</code> of {E(day(p["date"]))}' if p.get('commit') else '') + '.')
        if pc.get('own'):
            o = pc['own']; bits.append(f'In our working repository {E(o["repo"])} this version was first committed in <code>{E(o["commit"][:12])}</code> on {E(day(o["date"]))}.')
        elif pc.get('own_changed'):
            o = pc['own_changed']; bits.append(f'In our working repository {E(o["repo"])} this version is newer than its last commit' + (f' (<code>{E(o["commit"][:12])}</code> of {E(day(o["date"]))})' if o.get('commit') else '') + ', so its commit is not recorded yet.')
        if pc.get('public_other') and not pc.get('public'):
            p = pc['public_other']; bits.append(f'The public code folder holds a different version of this file: <a href="{E(p["url"])}">{E(p["repo"])}/{E(p["path"])}</a> (commit <code>{E(p["commit"][:12])}</code> of {E(day(p["date"]))}).')
        if not (pc.get('public') or pc.get('own') or pc.get('own_changed') or pc.get('public_other')):
            bits.append('Git commit: not recorded. The file is kept outside version control and no public copy holds it.' if os.path.exists(fp) else 'The file is no longer kept.')
        lines.append('<p>' + ' '.join(bits) + '</p>')
    return lines

URLS = re.compile(r'https?://[^\s"\'<>)\],]+')
def source_block(r):
    s = r['source']; fp = abspath(s['file']); out = []
    line = None
    if os.path.exists(fp) and not os.path.isdir(fp):
        try:
            for ln in open(fp, encoding='utf-8', errors='ignore'):
                if s['grep'] in ln: line = ln.rstrip('\n'); break
        except Exception: pass
    q = line if line and len(line) <= 600 else s['grep']
    out.append(f'<p>File: <code>{E(show_path(s["file"]))}</code>' + ('' if os.path.exists(fp) else '. The file is no longer kept, so the ledger check reports it') + '.</p>')
    out.append(f'<p>The line the number is read from:</p><pre class="rp-pre">{E(q[:1200])}</pre>')
    if r.get('kind') == 'live_headline' and r.get('live'):
        lv = r['live']
        out.append(f'<p>Live feed: <a href="{E(lv["feed"])}">{E(lv["feed"])}</a>, field <code>{E(json.dumps(lv["field"]))}</code>, read by the stamp <code>{E(json.dumps(lv.get("stamp")))}</code>. '
                   f'It refreshes about every {E(str(lv.get("cadence_h")))} hours and reads stale after {E(str(lv.get("stale_after_h")))} hours.</p>')
    if r.get('kind') == 'live_value' and r.get('reading'):
        out.append(f'<p>Pull date: the feed stamp {E(str(r["reading"].get("stamp")))} (read {E(day(r["history"][0]["at"]))}).</p>')
    ups = sorted(set(u.rstrip('.') for u in URLS.findall(line or s['grep'])))
    if ups: out.append('<p>Addresses named in that line: ' + ' &middot; '.join(f'<a href="{E(u)}">{E(u)}</a>' for u in ups[:6]) + '.</p>')
    pc = public_copy(fp) if os.path.exists(fp) and not os.path.isdir(fp) else None
    if pc and pc.get('public'):
        p = pc['public']
        out.append(f'<p>Public copy of the file: ' + (f'<a href="{E(p["live"])}">{E(p["live"])}</a>, also ' if p.get('live') else '') + f'<a href="{E(p["url"])}">{E(p["repo"])}/{E(p["path"])}</a>' + (f' (commit <code>{E(p["commit"][:12])}</code> of {E(day(p["date"]))})' if p.get('commit') else '') + '.</p>')
    if r.get('kind') == 'live_headline':
        out.append('<p>Pull date: the feed carries the time of its own read, and each reading kept below has its feed stamp.</p>')
    elif r.get('kind') != 'live_value':
        if pc and pc.get('own'):
            o = pc['own']; out.append(f'<p>File date: this version was first committed on {E(day(o["date"]))} (<code>{E(o["commit"][:12])}</code> in {E(o["repo"])}). Pull date of the data inside it: not recorded in the row.</p>')
        elif pc and pc.get('public') and pc['public'].get('date'):
            out.append(f'<p>File date: this version was first published on {E(day(pc["public"]["date"]))}. Pull date of the data inside it: not recorded in the row.</p>')
        else:
            out.append('<p>Pull date: not recorded in the row. The row entered the ledger on ' + E(day(r['history'][0]['at'])) + '.</p>')
    return out

PRIVATE = ('iris_paper', 'messages')
def private_only(r): return bool(r['surfaces']) and all(x['surface'] in PRIVATE for x in r['surfaces'])
def receipt(r, rows, info, kids):
    rid = r['id']; inf = info[rid]; pid = public_id(rid); path = href(rid)
    if private_only(r):
        sl, dn, du = inf['desk']; p = inf['pub']
        body = ['<p class="rp-status"><b>Not public yet.</b> This row belongs to a manuscript that is not published. Its number, the sentence, the source and the code are printed here when the manuscript is.</p>',
                '<section class="rp-sec"><h2>Hashes</h2><table class="rp-kv"><tbody>'
                f'<tr><th scope="row">Ledger row</th><td><code>{E(pid)}</code></td></tr><tr><th scope="row">Status</th><td>{E(STATUS_WORD.get(r["status"], r["status"]))}</td></tr>'
                f'<tr><th scope="row">Row sha256</th><td><code class="rp-h">{inf["row_sha256"]}</code></td></tr>'
                f'<tr><th scope="row">Ledger file sha256</th><td><code class="rp-h">{p["ledger_sha256"]}</code></td></tr>'
                f'<tr><th scope="row">At</th><td>' + (f'Ledger commit <code>{p["commit"][:12]}</code> of {E(day(p["date"]))}.' if p['how'] == 'commit' else f'{E(day(p["date"]))}, first site build.') + '</td></tr>'
                '</tbody></table><p class="meta">The row hash commits the row as it stands, so the published row can be checked against it later.</p></section>',
                '<section class="rp-sec"><h2>History</h2><ul class="rp-hist">' + ''.join(f'<li><span class="rp-d">{E(day(h.get("at", "")))}</span> {"Entered the ledger." if h.get("change") == "added" else "Ledger entry updated."}</li>' for h in r['history']) + '</ul></section>',
                f'<p class="rp-nav"><a href="/r/">All receipts</a> &middot; <a href="/r/desk/{E(sl)}">{E(dn)} receipts</a></p>']
        return shell(path, f'Receipt {pid} | Heuremen LLC', 'Receipt for a ledger row of a manuscript that is not public yet.', 'Receipt', E(pid), '\n'.join(body), cssv())
    sl, dn, du = inf['desk']; pl = placements(r); fw = forward_links(r, rows, kids)
    superseded = r.get('kind') == 'live_value' and bool(fw)
    body = []
    if r['status'] != 'live' or superseded:
        word = 'Superseded' if superseded and r['status'] == 'live' else STATUS_WORD.get(r['status'], r['status'])
        when = next((day(h['at']) for h in reversed(r['history']) if h.get('change') in ('withdrawn', 'cannot_tell') or str(h.get('change', '')).startswith('status')), '')
        if superseded: when = day(rows[fw[0]]['history'][0]['at'])
        msg = {'Superseded': 'A newer reading replaced this one', 'Withdrawn': 'This number was withdrawn', 'Held': 'This number is held out while it is read again', 'Cannot tell': 'This number was moved to cannot tell'}.get(word, word)
        body.append(f'<p class="rp-status"><b>{E(word)}.</b> {E(msg)}' + (f' on {E(when)}' if when else '') + '. The page stays, as every receipt does.'
                    + (' Carried now by ' + ', '.join(f'<a href="{href(x)}">{E(public_id(x))}</a>' for x in fw) + '.' if fw else '') + '</p>')
    body.append('<section class="rp-sec"><h2>The number</h2>')
    if pl:
        shown = []
        for lab, u, sen, kind, snip in pl:
            if snip and snip not in shown: shown.append(snip)
        body.append(''.join(f'<p class="rp-num">{E(sn)}</p>' for sn in shown[:3]))
    elif r.get('kind') == 'live_value' and r.get('reading'):
        body.append(f'<p class="rp-num">{E(str(r["reading"].get("display", r["value"])))}</p>')
    body.append('<table class="rp-kv"><tbody>'
                f'<tr><th scope="row">Ledger value</th><td><code>{E(str(r["value"]))}</code>{(" " + E(r["unit"])) if r.get("unit") else ""}</td></tr>'
                + (f'<tr><th scope="row">Interval</th><td><code>{E(iv(r))}</code></td></tr>' if iv(r) else '')
                + f'<tr><th scope="row">Outcome</th><td>{E(r["outcome"])}</td></tr>'
                f'<tr><th scope="row">Status</th><td>{E("Superseded" if superseded and r["status"] == "live" else STATUS_WORD.get(r["status"], r["status"]))}</td></tr>'
                f'<tr><th scope="row">Desk</th><td>' + (f'<a href="/r/desk/{E(sl)}">{E(dn)}</a>') + '</td></tr>'
                f'<tr><th scope="row">Ledger row</th><td><code>{E(pid)}</code></td></tr>'
                '</tbody></table>')
    c = clean_prose(r.get('claim', ''))
    if c: body.append(f'<p>What it is: {E(c)}</p>')
    body.append('</section>')
    body.append('<section class="rp-sec"><h2>Where it is printed</h2>')
    if pl:
        for lab, u, sen, kind, snip in pl:
            head = f'<a href="{E(u)}">{E(lab)}</a>' if u else E(lab)
            if sen: body.append(f'<p>{head}</p><blockquote class="rp-q">{E(sen)}</blockquote>')
            elif kind == 'private': body.append(f'<p>{head}</p>')
            else: body.append(f'<p>{head}' + (' (the sentence was not found in the current page)' if r['status'] == 'live' else ' (no longer printed there)') + '</p>')
    else:
        body.append('<p>Not printed on a page at present. The row stays in the ledger and keeps this receipt.</p>' if r.get('kind') != 'live_value'
                    else f'<p>A reading of the live headline on <a href="{E(du or "/")}">{E(dn)}</a>. The page shows the newest reading, and every reading kept is listed below.</p>')
    body.append('</section>')
    body.append('<section class="rp-sec"><h2>Source</h2>' + ''.join(source_block(r)) + '</section>')
    body.append('<section class="rp-sec"><h2>Code</h2>' + ''.join(code_block(r)) + '</section>')
    p = inf['pub']
    body.append('<section class="rp-sec"><h2>Hashes</h2><table class="rp-kv"><tbody>'
                f'<tr><th scope="row">Row sha256</th><td><code class="rp-h">{inf["row_sha256"]}</code></td></tr>'
                f'<tr><th scope="row">Ledger file sha256</th><td><code class="rp-h">{p["ledger_sha256"]}</code></td></tr>'
                f'<tr><th scope="row">At</th><td>' + (f'Ledger commit <code>{p["commit"][:12]}</code> of {E(day(p["date"]))}, the first commit holding this exact row.' if p['how'] == 'commit'
                                                      else f'{E(day(p["date"]))}, the first site build holding this exact row.') + '</td></tr>'
                + (f'<tr><th scope="row">Check block</th><td><code class="rp-h">{E(r["checks"]["sha256"])}</code></td></tr>' if isinstance(r.get('checks'), dict) and r['checks'].get('sha256') else '')
                + '</tbody></table><p class="meta">The row hash is the sha256 of the row&rsquo;s line in ledger.jsonl, byte for byte. The ledger file hash is the sha256 of the whole file at that point.</p></section>')
    st = stamp_lines(inf['stamps'], p['date'], [(ORIGIN + path, 'this receipt')] + [(u, lab) for lab, u, sen, kind, snip in pl if u and u.startswith(ORIGIN)][:3])
    if st: body.append('<section class="rp-sec rp-stamps"><h2>Timestamps</h2><ul>' + ''.join(f'<li>{x}</li>' for x in st) + '</ul></section>')
    hi = history_items(r)
    if r.get('kind') == 'live_headline' and kids.get(rid):
        trs = []
        for k in reversed(kids[rid]):
            kr = rows[k]; rd = kr.get('reading', {})
            trs.append(f'<tr><td>{E(str(rd.get("stamp", "")))}</td><td><code>{E(str(rd.get("display", kr["value"])))}</code></td><td>{E(kr["outcome"])}</td><td>{E(iv(kr))}</td><td><a href="{href(k)}">{"Newest" if k == kids[rid][-1] else "Superseded"}</a></td></tr>')
        body.append('<section class="rp-sec"><h2>Readings kept</h2><div class="tablewrap"><table class="rp-t"><thead><tr><th>Feed stamp</th><th>Value</th><th>Outcome</th><th>Interval</th><th>Receipt</th></tr></thead><tbody>' + ''.join(trs) + '</tbody></table></div>'
                    '<p class="meta">A reading is kept when it moves outside the previous interval, when its outcome flips, or under the desk&rsquo;s own stated rule. None is deleted.</p></section>')
    if r.get('kind') == 'live_value':
        sib = kids.get(r.get('live_of'), []); i = sib.index(rid) if rid in sib else -1
        nav = [f'Headline: <a href="{href(r["live_of"])}">{E(public_id(r["live_of"]))}</a>']
        if i > 0: nav.append(f'previous reading: <a href="{href(sib[i - 1])}">{E(public_id(sib[i - 1]))}</a>')
        if 0 <= i < len(sib) - 1: nav.append(f'next reading: <a href="{href(sib[i + 1])}">{E(public_id(sib[i + 1]))}</a>')
        body.append('<p>' + ' &middot; '.join(nav) + '.</p>')
    body.append('<section class="rp-sec"><h2>History</h2><ul class="rp-hist">' + ''.join(hi) + '</ul></section>')
    body.append(f'<p class="rp-nav"><a href="/r/">All receipts</a> &middot; <a href="/r/desk/{E(sl)}">{E(dn)} receipts</a>' + (f' &middot; <a href="{E(du)}">{E(dn)} page</a>' if du else '') + '</p>')
    desc = f'Receipt for a number Heuremen LLC publishes on {dn}: where it is printed, its source, code, hashes and history.'
    return shell(path, f'Receipt {pid} | Heuremen LLC', desc, 'Receipt', E(pid), '\n'.join(body), cssv())

def lastmod(r, kids, rows):
    ts = [h.get('at', '') for h in r['history']] + [rows[k]['history'][0]['at'] for k in kids.get(r['id'], [])]
    return max(t for t in ts if t)[:10] if any(ts) else D.date.today().isoformat()

def index_pages(rows, info, kids):
    by = {}
    for rid in sorted(rows):
        by.setdefault(info[rid]['desk'], []).append(rid)
    order = sorted(by, key=lambda d: (d[0] in ('other',), d[1].lower()))
    css = cssv(); pages = {}
    opts = ''.join(f'<option value="{E(d[0])}">{E(d[1])}</option>' for d in order)
    trs = ''.join(f'<tr><td><a href="/r/desk/{E(d[0])}">{E(d[1])}</a></td><td class="r">{sum(1 for x in by[d] if rows[x]["status"] == "live")}</td><td class="r">{sum(1 for x in by[d] if rows[x]["status"] != "live")}</td><td>' + (f'<a href="{E(d[2])}">page</a>' if d[2] else '') + '</td></tr>' for d in order)
    body = ('<p class="rp-lead">Every number Heuremen LLC publishes has a ledger row, and every row has a receipt here. A receipt shows where the number is printed, the file and line it is read from, the code, the hashes and the history. '
            'Withdrawn and superseded numbers keep their receipts.</p>'
            '<form class="rp-find" action="/r/go" method="get"><div class="rc-field"><label for="rp-d">Desk</label><select id="rp-d" name="d">' + opts + '</select></div>'
            '<div class="rc-field"><label for="rp-i">Ledger row</label><input id="rp-i" name="id" type="text" inputmode="text" autocomplete="off" spellcheck="false" placeholder="qia.mx.r1.fez"></div>'
            '<div class="rc-field"><label>&nbsp;</label><button type="submit">Open</button></div></form>'
            '<p class="meta">A ledger row name opens that receipt. Otherwise the desk opens. Every receipt link on the site carries the row name.</p>'
            '<div class="tablewrap"><table class="rp-t"><thead><tr><th>Desk</th><th class="r">Standing</th><th class="r">Withdrawn or superseded</th><th>Page</th></tr></thead><tbody>' + trs + '</tbody></table></div>')
    pages['index'] = shell('/r/', 'Receipts | Heuremen LLC', 'A receipt for every number Heuremen LLC publishes: where it is printed, its source, code, hashes and history.', 'Receipts', 'One page for every number we publish', body, css)
    for d in order:
        rs = by[d]; rows_html = []
        for rid in rs:
            r = rows[rid]; sup = r.get('kind') == 'live_value' and forward_links(r, rows, kids)
            stt = 'Superseded' if sup and r['status'] == 'live' else STATUS_WORD.get(r['status'], r['status'])
            shown = 'Manuscript, not public yet' if private_only(r) else next((x['text'] for x in r['surfaces'] if x['surface'] not in PRIVATE), None) or (r.get('reading', {}).get('display') or str(r['value']))
            rows_html.append(f'<tr><td><a href="{href(rid)}"><code>{E(public_id(rid))}</code></a></td><td>{E(shown[:160])}</td><td>{E(r["outcome"])}</td><td>{E(stt)}</td></tr>')
        body = (f'<p class="rp-lead">Receipts for the numbers on {E(d[1])}' + (f' (<a href="{E(d[2])}">the page</a>)' if d[2] else '') + '. Each row name opens its receipt. <a href="/r/">All desks</a>.</p>'
                '<div class="tablewrap"><table class="rp-t"><thead><tr><th>Ledger row</th><th>As printed</th><th>Outcome</th><th>Status</th></tr></thead><tbody>' + ''.join(rows_html) + '</tbody></table></div>')
        pages['desk/' + d[0]] = shell(f'/r/desk/{d[0]}', f'Receipts for {d[1]} | Heuremen LLC', f'Receipts for the numbers Heuremen LLC publishes on {d[1]}.', 'Receipts', E(d[1]), body, css)
    return pages, by

def write_if_changed(fp, text):
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    if os.path.exists(fp) and open(fp, encoding='utf-8').read() == text: return False
    tmp = fp + '.tmp'; open(tmp, 'w', encoding='utf-8').write(text); os.replace(tmp, fp); return True

def build():
    rows = load(); slugs = {}
    for rid in rows:
        s = slug(rid)
        if s.lower() in slugs: sys.exit(f'receipts: slug collision {rid} / {slugs[s.lower()]}')
        if s in ('index', 'go', 'desk', 'sitemap.txt'): sys.exit(f'receipts: row id {rid} takes a reserved name')
        slugs[s.lower()] = rid
    info, kids = build_rows(rows); want = set(); changed = 0; sm = []
    for rid, r in rows.items():
        fp = os.path.join(OUT, slug(rid) + '.html'); want.add(fp)
        changed += write_if_changed(fp, receipt(r, rows, info, kids)); sm.append((href(rid), lastmod(r, kids, rows)))
    pages, by = index_pages(rows, info, kids)
    for k, t in pages.items():
        fp = os.path.join(OUT, k + '.html'); want.add(fp); changed += write_if_changed(fp, t)
        if k == 'index': sm.insert(0, ('/r/', max(m for _, m in sm)))
        else:
            d = next(x for x in by if 'desk/' + x[0] == k)
            sm.append(('/r/' + k, max(lastmod(rows[x], kids, rows) for x in by[d])))
    fp = os.path.join(OUT, 'sitemap.txt'); want.add(fp); write_if_changed(fp, ''.join(f'{u}\t{m}\n' for u, m in sm))
    gone = 0
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            p = os.path.join(dp, f)
            if p not in want: os.remove(p); gone += 1
    print(f'receipts: {len(rows)} rows, {len(pages)} index pages, {changed} written, {gone} stale files removed')

# ---------- link-up (called by indahl-ai/build_site.py) ----------
SKIP_EL = {'script', 'style', 'title', 'head', 'textarea', 'option', 'select', 'button', 'svg', 'noscript', 'label', 'summary'}
TOK = re.compile(r'<!--.*?-->|<[^>]+>|[^<]+', re.S)
def _map(doc):
    """Normalised text of a page as check_ledger reads it, with each character's raw end offset and whether a link may go there."""
    chars = []; ends = []; ok = []; stack = []; in_body = False; skip_depth = 0; a_close = []
    for m in TOK.finditer(doc):
        t = m.group(0)
        if t.startswith('<!--'): continue
        if t.startswith('<'):
            tm = re.match(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)', t)
            if tm:
                close, name = tm.group(1) == '/', tm.group(2).lower()
                if name == 'body' and not close: in_body = True
                if (name in SKIP_EL or name == 'a') and not t.startswith('<a class="rcpt"'):
                    if not close and not t.endswith('/>'): stack.append(name)
                    elif close and name in stack:
                        while stack and stack.pop() != name: pass
            if t.startswith('<a class="rcpt"'): continue
            chars.append(' '); ends.append(m.start()); ok.append(False)
            continue
        if not in_body or any(x in SKIP_EL for x in stack):
            for _ in t: chars.append(' ' if _.isspace() else _); ends.append(m.start()); ok.append(False)
            continue
        inside_a = 'a' in stack
        for pm in re.finditer(r'&#?\w+;|.', t, re.S):
            u = html.unescape(pm.group(0))
            for ch in u:
                ch = {'\u2212': '-', '\u2013': '-', '\u2014': '-', '\u2009': ' ', '\xa0': ' '}.get(ch, ch)
                chars.append(ch); ends.append(pm.end() + m.start()); ok.append('A' if inside_a else True)
    out = []; oe = []; ook = []; prev_sp = True
    for ch, e, k in zip(chars, ends, ok):
        if ch.isspace():
            if prev_sp: continue
            out.append(' '); oe.append(e); ook.append(False); prev_sp = True
        else: out.append(ch); oe.append(e); ook.append(k); prev_sp = False
    return ''.join(out), oe, ook

def link_pages(PAGES, rows=None):
    """Put a receipt link after each live row's snippet on the pages it is printed on. Returns the changed PAGES and writes ledger/receipts_links.json."""
    rows = rows or load(); want = {}
    f2p = {}
    for k, p in SURFACES.items():
        if p.startswith('indahl-ai/') and p.endswith('.html'):
            rel = p[len('indahl-ai/'):]; pth = '/' if rel == 'index.html' else '/' + rel[:-5]
            if k == 'sad': f2p[k] = [x for x in PAGES if x == '/hermes/model' or x.startswith('/hermes/model/')]
            elif pth in PAGES: f2p[k] = [pth]
    f2p['indahl'] = list(PAGES)
    need = {}   # (row, surface) -> pages it may be on
    for r in sorted(rows.values(), key=lambda r: r['id']):
        if r['status'] != 'live': continue
        for sf in r['surfaces']:
            for pth in f2p.get(sf['surface'], []):
                want.setdefault(pth, []).append((r['id'], sf['text'], sf['surface']))
                need.setdefault((r['id'], sf['surface']), set())
    report = {}; state = {}; shared = set(); dks = desks(rows)   # (row, surface) -> 'linked' | 'nospot'
    for pth, items in want.items():
        doc = PAGES[pth]; text, ends, ok = _map(doc); ins = []; found_here = set(); used = set()
        for rid, snip, sk in items:
            n = norm(snip)
            if not n: continue
            if (rid, n) in found_here: state[(rid, sk)] = 'linked'; continue
            i = text.find(n); placed = False; seen_any = i >= 0; first = None
            while i >= 0:
                j = i + len(n) - 1
                while j + 1 < len(text) and (text[j + 1].isalnum() or text[j + 1] == '%' or (text[j + 1] in '.,' and j + 2 < len(text) and text[j + 2].isdigit())): j += 1
                pos = ends[j] if ok[j] is True else (doc.find('</a>', ends[j]) + 4 if ok[j] == 'A' and doc.find('</a>', ends[j]) >= 0 else None)   # inside a link: right after it closes
                if pos is not None:
                    first = pos if first is None else first
                    if (pos, n) not in used:   # rows sharing one snippet take its occurrences in order, so receipt links do not pile up on the first
                        ins.append((pos, rid, n)); used.add((pos, n)); placed = True; break
                i = text.find(n, i + 1)
            if not placed and first is not None: ins.append((first, rid, n)); placed = True
            if placed: found_here.add((rid, n)); state[(rid, sk)] = 'linked'
            elif seen_any and state.get((rid, sk)) != 'linked': state[(rid, sk)] = 'nospot'
        if not ins: continue
        ins.sort(key=lambda x: x[0]); parts = []; last = 0; done = []; grp = {}
        for pos, rid, n in ins: grp.setdefault(pos, []).append((rid, n))
        for pos in sorted(grp):
            parts.append(doc[last:pos]); last = pos; g = grp[pos]
            if len(g) > 3:   # many rows print the same words at one spot (a shared phrase): one link to their desk's receipts, not a pile of arrows
                dsk = dks.get(g[0][0], ('other',))[0]
                parts.append(f'<a class="rcpt" href="/r/desk/{dsk}" aria-label="Receipts for the rows printed here" title="Receipts"></a>'); done += [r for r, _ in g]; shared.update((r, pth) for r, _ in g); continue
            for rid, n in g:
                lab = n if len(n) <= 70 else n[:67].rsplit(' ', 1)[0] + '\u2026'
                parts.append(f'<a class="rcpt" href="{href(rid)}" aria-label="Receipt for {E(lab, quote=True)}" title="Receipt"></a>'); done.append(rid)
        parts.append(doc[last:]); PAGES[pth] = ''.join(parts); report[pth] = done
    tot = len(need); got = sum(1 for k in need if state.get(k) == 'linked'); nospot = sorted(k for k in need if state.get(k) == 'nospot'); absent = sorted(k for k in need if k not in state)
    json.dump({'built': D.datetime.now().astimezone().isoformat(timespec='seconds'), 'snippets': tot, 'linked': got, 'links': sum(len(v) for v in report.values()),
               'pages': {p: [[rid, slug(rid)] for rid in v] for p, v in sorted(report.items())}, 'no_spot': nospot, 'not_on_page': absent, 'via_desk_page': sorted(shared)}, open(LINKS, 'w'), indent=0)
    print(f'receipts: {got} of {tot} live snippets on indahl.ai pages carry a receipt link ({sum(len(v) for v in report.values())} links on {len(report)} pages, '
          f'{len(nospot)} sit only where a link cannot go, {len(absent)} not found on their page, {len(shared)} share one spot and link to their desk receipts)')
    return PAGES
def s_on_page(text, n): return n in text

# ---------- gate ----------
RCPT = re.compile(r'<a class="rcpt" href="/r/([^"]+)"')
def check(verbose=True):
    rows = load(); bad = []
    for rid in rows:
        if not os.path.exists(os.path.join(OUT, slug(rid) + '.html')): bad.append(('NORECEIPT', rid))
    for k in ('index',):
        if not os.path.exists(os.path.join(OUT, k + '.html')): bad.append(('NOINDEX', k))
    n = 0
    for pth, f in served().items():
        s = open(os.path.join(SITE, f), encoding='utf-8', errors='ignore').read()
        for m in RCPT.finditer(s):
            n += 1
            if not os.path.exists(os.path.join(OUT, m.group(1) + '.html')): bad.append(('DEADLINK', f'{pth} -> /r/{m.group(1)}'))
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            if not f.endswith('.html'): continue
            s = open(os.path.join(dp, f), encoding='utf-8').read()
            for m in re.finditer(r'href="(/r/[^"]*)"', s):
                u = m.group(1)
                if u in ('/r/', '/r/go'): continue
                if not os.path.exists(os.path.join(OUT, u[3:] + '.html')): bad.append(('DEADLINK', f'{os.path.relpath(os.path.join(dp, f), OUT)} -> {u}')); break
            if re.search(r'(?i)<script\b', s): bad.append(('SCRIPT', f))
            if re.search(r'(?i)\bflock', s): bad.append(('WORD', f + ': flock'))
    print(f'receipts gate: {len(rows)} ledger rows, {n} receipt links on served pages; breaches: {len(bad)}')
    for b in bad[:40]: print('  %-10s %s' % b)
    return 1 if bad else 0

def live(n):
    rows = load(); ids = random.sample(sorted(rows), n); bad = 0
    def get(u):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'heuremen-receipts-check/1'}), timeout=30); return r.status, r.read().decode('utf-8', 'ignore')
        except Exception as e: return getattr(e, 'code', 0), ''
    print('random receipts:')
    for rid in ids:
        st, t = get(ORIGIN + href(rid) + '?x=' + str(random.randint(1, 1 << 30)))
        ok = st == 200 and E(public_id(rid)) in t
        bad += not ok; print(f'  {"ok " if ok else "BAD"} {st} {href(rid)}')
    links = json.load(open(LINKS)) if os.path.exists(LINKS) else {'pages': {}}
    viad = {tuple(x) for x in links.get('via_desk_page', [])}; dks = desks(rows)
    pairs = [(p, rid, ('desk/' + dks[rid][0]) if (rid, p) in viad and rid in dks else sl) for p, v in links['pages'].items() for rid, sl in v]   # rows sharing one spot link to their desk's receipts
    print('random receipt links from pages:')
    for p, rid, sl in random.sample(pairs, min(n, len(pairs))):
        st, t = get(ORIGIN + p + '?x=' + str(random.randint(1, 1 << 30)))
        has = f'href="/r/{sl}"' in t
        st2, t2 = get(ORIGIN + '/r/' + sl) if has else (0, '')
        ok = st == 200 and has and st2 == 200
        bad += not ok; print(f'  {"ok " if ok else "BAD"} {p} -> /r/{sl} (page {st}, link {"on page" if has else "MISSING"}, receipt {st2})')
    print(f'live: {bad} misses'); return 1 if bad else 0

def seed_indexnow():
    S = os.path.join(B, 'tools', 'indexnow_state.json'); st = json.load(open(S)) if os.path.exists(S) else {}; n = 0
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            if not f.endswith('.html'): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, OUT)[:-5]
            u = ORIGIN + ('/r/' if rel == 'index' else '/r/' + rel)
            st[u] = hashlib.sha256(re.sub(rb'<section class="rp-sec rp-stamps">.*?</section>', b'', re.sub(rb'\?v=[0-9a-f]{8}', b'', open(p, 'rb').read()), flags=re.S)).hexdigest()[:16]; n += 1   # the same hash tools/indexnow.py takes
    json.dump(st, open(S, 'w')); print(f'indexnow: recorded {n} receipt pages without sending')

if __name__ == '__main__':
    a = sys.argv[1:] or ['build']
    if a[0] == 'build': build()
    elif a[0] == 'check': sys.exit(check())
    elif a[0] == 'live': sys.exit(live(int(a[1]) if len(a) > 1 else 10))
    elif a[0] == 'seed-indexnow': seed_indexnow()
    else: sys.exit(__doc__)
