"""build_site.py -- builds indahl.ai from one source (23 Oct 2026). Every page shares one header, one footer and style.css, so nothing
can drift between pages. Output: indahl-ai/<page>.html + style.css + pages.js (the map the Cloudflare worker imports).
Rules: SPECBOOK_v1.2 (Paper/Ink, gold rules, Abril Fatface display, Lora body, Cinzel labels; business footer "Heuremen LLC / We found it.";
no counts in titles; no Made-with line; no prices). Run: python3 build_site.py   (ship.sh runs it)."""
import os, html
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = ('<svg class="mark" viewBox="0 0 200 200" aria-hidden="true"><polygon points="100,30 180,170 20,170"/>'
        '<polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5"/></svg>')
HOME = {'/vault': '/hermes', '/tape': '/hermes', '/receipts/stamps': '/hermes', '/hfsize': '/iris', '/hflicense': '/iris', '/pkglicense': '/iris', '/pkginstall': '/iris', '/uptime': '/atlas', '/time': '/atlas', '/cada': '/atlas', '/secrecords': '/atlas', '/seat': '/atlas', '/support': '/atlas', '/change': '/atlas',
        '/trials': '/hermes', '/hpt': '/hermes', '/revise': '/hermes', '/fedsep': '/hermes', '/cadence': '/hermes', '/forecast': '/hermes', '/launch': '/hermes', '/arxivdrift': '/hermes', '/linkrot': '/hermes', '/airline': '/hermes', '/weights': '/iris', '/ailuminate': '/iris', '/airq': '/hermes', '/campus': '/oy', '/rank': '/oy', '/hosts': '/iris', '/water': '/atlas', '/neo': '/atlas', '/seasonal': '/hermes', '/steo': '/hermes', '/solar': '/atlas', '/quake': '/atlas', '/flu': '/hermes', '/tornado': '/hermes', '/credit': '/hermes', '/cone': '/atlas', '/wiki': '/hermes', '/social': '/hermes', '/predictions': '/hermes', '/census/revisions': '/census', '/census/coverage': '/census', '/census/fidelity': '/census', '/census/vintages': '/census'}
NAV = [('/qia', 'QIA'), ('/iris', 'IRIS'), ('/hermes', 'HERMES'), ('/atlas', 'ATLAS'), ('/sagar', 'SAGAR'), ('/oy', 'OY'), ('/social', 'SOCIAL'), ('/census', 'CENSUS'), ('/time', 'TIME'), ('/cada', 'CADA'), ('/uptime', 'UPTIME'), ('/forecast', 'FORECAST'), ('/cadence', 'CADENCE'), ('/trials', 'TRIALS'), ('/launch', 'LAUNCH'), ('/linkrot', 'LINKROT'), ('/arxivdrift', 'ARXIVDRIFT'), ('/support', 'SUPPORT'), ('/pkglicense', 'PKGLICENSE'), ('/hflicense', 'HFLICENSE'), ('/hfsize', 'HFSIZE'), ('/change', 'CHANGE'), ('/secrecords', 'SECRECORDS'), ('/seat', 'SEAT'), ('/pkginstall', 'PKGINSTALL'), ('/stack', 'STACK'), ('/revise', 'REVISE'), ('/fedsep', 'FEDSEP')]
DOI = 'https://doi.org/10.5281/zenodo.23169755'


import json as _jsonld
import sys as _sys; _sys.path.insert(0, HERE); from hlcref import ref as _ref
SITE = 'https://indahl.ai'
_FEED = []
NOINDEX = {'/agree', '/inquiry', '/inquire-ok', '/inquire-error', '/404', '/request', '/respond'}
def seo_head(path, title, desc):
    """Canonical, social and structured-data tags (27 Oct 2026). Standards only: what the page says, nothing hidden, nothing the page does not contain."""
    url = SITE + ('/' if path == '/' else path)
    t, d = html.escape(title), html.escape(desc)
    out = [f'<link rel="canonical" href="{url}">', '<meta name="tdm-reservation" content="1">', '<meta name="tdm-policy" content="https://indahl.ai/terms#ai-training">']
    if path in NOINDEX: out.append('<meta name="robots" content="noindex,follow">')
    out += [f'<meta property="og:site_name" content="Heuremen LLC">', f'<meta property="og:type" content="website">', f'<meta property="og:title" content="{t}">',
            f'<meta property="og:description" content="{d}">', f'<meta property="og:url" content="{url}">', '<meta name="twitter:card" content="summary_large_image">', f'<meta property="og:image" content="{SITE}/og.png">', '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">', f'<meta name="twitter:image" content="{SITE}/og.png">', '<link rel="alternate" type="application/atom+xml" title="Heuremen LLC" href="/feed.xml">',
            f'<meta name="twitter:title" content="{t}">', f'<meta name="twitter:description" content="{d}">']
    ld = []
    if path == '/':
        out.append('<meta name="google-site-verification" content="BKoMMaDI-2hLmeqb5sT-BbSc8yL8co80968QA9dTbws" />')
        out.append('<meta name="google-site-verification" content="L69kSidThZ03D9_fKsS4-VVBxj6OncxBd011TKo92Wg" />')
        ld.append({"@context": "https://schema.org", "@type": "Organization", "name": "Heuremen LLC", "url": SITE + "/", "slogan": "We found it.",
                   "sameAs": ["https://heuremen.org/", "https://doi.org/10.5281/zenodo.23169755", "https://huggingface.co/indahl"]})
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": "Heuremen LLC", "url": SITE + "/"})
    if path in ('/qia', '/iris'):
        dd = {'/qia': ('Quantum hardware studies recounted against published calibration', '/qia/list.json'), '/iris': ('Language-model evaluation studies recounted from their released files', '/iris/list.json')}[path]
        ld.append({"@context": "https://schema.org", "@type": "Dataset", "name": dd[0] + ' (' + ('QIA' if path == '/qia' else 'IRIS') + ')', "description": desc, "url": url,
                   "creator": {"@type": "Organization", "name": "Heuremen LLC", "url": SITE + "/"}, "isAccessibleForFree": True, "license": SITE + "/terms", "copyrightNotice": "Heuremen LLC. Free to download and cite with attribution. Not licensed for text and data mining or AI training.",
                   "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + dd[1]}]})
    crumb = None
    # 29 Oct 2026 (his word, find-me pass): every indexable page gets a robots line with full snippet rights, and a WebPage and BreadcrumbList; live desks get a Dataset with their live feed; releases get a NewsArticle.
    if path not in NOINDEX: out.append('<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">'); out.append('<meta name="author" content="Heuremen LLC">')
    import datetime as _dt0
    _today = _dt0.date.today().isoformat(); _org = {"@type": "Organization", "name": "Heuremen LLC", "url": SITE + "/"}
    _short = title.split(' | ')[0]
    _live = {'predictions','support','pkglicense','hflicense','hfsize','secrecords','pkginstall','linkrot','trials','revise','hpt','hosts','airq','ailuminate','weights','airline','fedsep','time','cada','uptime','forecast','cadence','launch','arxivdrift','campus','seat','change','tape','water','neo','solar','quake','wiki','cone','tornado','credit','census','census/revisions','census/fidelity'}
    _slug = path.strip('/')
    if path not in NOINDEX and path not in ('/', '/qia', '/iris') and not path.startswith(('/qia/study/', '/iris/study/', '/sagar/study/')):
        _wp = {"@context": "https://schema.org", "@type": "WebPage", "name": _short, "description": desc, "url": url, "inLanguage": "en", "dateModified": _today, "isPartOf": {"@type": "WebSite", "name": "Heuremen LLC", "url": SITE + "/"}, "publisher": _org}
        if path in ('/media', '/media/2026-10-26'):
            _wp["@type"] = "NewsArticle"; _wp["headline"] = _short; _wp["datePublished"] = '2026-10-29' if path == '/media' else '2026-10-26'; _wp["author"] = _org; _wp["mainEntityOfPage"] = url
        elif path == '/community': _wp["@type"] = "CollectionPage"
        ld.append(_wp)
        if _slug in _live:
            ld.append({"@context": "https://schema.org", "@type": "Dataset", "name": _short, "description": desc, "url": url, "creator": _org, "publisher": _org, "isAccessibleForFree": True, "license": SITE + "/terms", "dateModified": _today,
                       "copyrightNotice": "Heuremen LLC. Free to download and cite with attribution. Not licensed for text and data mining or AI training.", "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + '/' + _slug + '/live.json'}]})
        _div = HOME.get(path)
        _cr = [('Heuremen LLC', SITE + '/')]
        if _div and _div != path: _cr.append((_div.strip('/').upper(), SITE + _div))
        _cr.append((_short, url)); crumb = _cr
    if path.startswith('/qia/study/') or path.startswith('/iris/study/') or path.startswith('/sagar/study/'):
        div = 'qia' if path.startswith('/qia/') else ('sagar' if path.startswith('/sagar/') else 'iris')
        crumb = [('Heuremen LLC', SITE + '/'), (div.upper(), SITE + '/' + div), (title.split(' | ')[0], url)]
        ld.append({"@context": "https://schema.org", "@type": "WebPage", "name": title.split(' | ')[0], "url": url, "datePublished": ("2026-11-12" if path.startswith('/sagar/') else "2026-10-27"), "dateModified": globals().get('_STUDY_MOD', {}).get(path, "2026-10-27"), "isPartOf": {"@type": "WebSite", "name": "Heuremen LLC", "url": SITE + "/"}})
    elif path in ('/qia', '/iris'):
        crumb = [('Heuremen LLC', SITE + '/'), (path[1:].upper(), url)]
        import datetime as _dt
        ld.append({"@context": "https://schema.org", "@type": "WebPage", "name": title.split(' | ')[0], "url": url, "dateModified": _dt.date.today().isoformat(), "isPartOf": {"@type": "WebSite", "name": "Heuremen LLC", "url": SITE + "/"}})
    if crumb: ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumb)]})
    for o in ld: out.append('<script type="application/ld+json">' + _jsonld.dumps(o, ensure_ascii=False).replace('</', '<\\/') + '</script>')
    return '\n'.join(out)

# 29 Oct 2026 (outside speed audit, layout shift 0.33): the headline block is injected by script, so its space is reserved in the page.
_SLOT = '<section id="hl-slot" class="hl-slot" aria-hidden="true"></section>'
try: _HLSLUGS = set(_jsonld.load(open(os.path.join(HERE, '..', 'watch', 'headlines.json')))['pages'].keys()) | {'stack'}
except Exception: _HLSLUGS = set()
def _hlslot(path):
    if path == '/social' and globals().get('_SOCIALSLOT'): return _SOCIALSLOT   # 10 Nov 2026: SOCIAL ships one reading per section, so its headline is the one built with the page (social_index/build_social.py)
    if path == '/wiki' and globals().get('_WIKISLOT'): return _WIKISLOT
    if path == '/census/fidelity' and globals().get('_FIDSLOT'): return _FIDSLOT   # 11 Nov 2026: CENSUS FIDELITY is a one-time desk, its headline is built with the page (fidelity_index/build_page.py)
    if path == '/hermes/datapapers' and globals().get('_DPSLOT'): return _DPSLOT   # 12 Nov 2026: DATA PAPERS ships its headline built with the page from datapaper_index/summary.json
    if path == '/record' and globals().get('_RECSLOT'): return _RECSLOT   # 12 Nov 2026: RECORD ships its headline built with the page (trackrecord/build_page.py)
    if path == '/petrol' and globals().get('_PETSLOT'): return _PETSLOT   # 12 Nov 2026: ATLAS PETROL ships its headline built with the page (petrol_index/build_page.py)
    if path == '/census/vintages' and globals().get('_VINSLOT'): return _VINSLOT   # 11 Nov 2026: CENSUS VINTAGES is a one-time desk, its headline is built with the page (census_index/census_vintages/build_page.py)
    if path == '/census/coverage' and globals().get('_COVSLOT'): return _COVSLOT   # 11 Nov 2026: CENSUS COVERAGE is a one-time desk, its headline is the one built with the page (census_coverage/build_page.py)
    if path == '/census/revisions' and globals().get('_CENSUSSLOT'): return _CENSUSSLOT   # 11 Nov 2026: the CENSUS desk page ships with its headline built in (census_index/build_page.py), the same function as watch/headlines.py census()
    if path == '/predictions' and globals().get('_PREDSLOT'): return _PREDSLOT   # 10 Nov 2026: NOW ships one frozen reading, so its headline is the one built with the page (now_index/build_page.py)
    if path == '/oy' and globals().get('_OYSLOT'): return _OYSLOT   # 10 Nov 2026 (newsletter audit): OY's headline is built with the page from the rows (oy_index/matrix_page/oy_headline.json)   # 10 Nov 2026: WIKI ships one reading, so its headline is the one built with that page (wiki_index/build_page.py), not the feed's
    if path == '/': return _SLOT.replace('class="hl-slot"', 'class="hl-slot hl-home"')
    if path == '/stack': return _SLOT.replace('class="hl-slot"', 'class="hl-slot hl-stack"')
    # 29 Oct 2026 (his "too much space under the headline"): the page ships with the current headline in it, so nothing is reserved and nothing jumps. headline.js refreshes the words in place.
    _parts = path.split('/')
    # 30 Oct 2026 site pass (B-29, I-29): desks whose headline moves within minutes ship an empty slot, so a reader without scripts never gets a stale number
    if len(_parts) == 2 and _parts[1] in ('tape', 'airline', 'hosts', 'qia', 'iris'): return _SLOT
    if path == '/iris/lab': return _SLOT   # 11 Nov 2026: the LAB headline moves every turn, so it ships an empty slot and headline.js fills it from headlines.json['iris/lab']
    if len(_parts) == 2 and path != '/hermes/model':
        try: _hh = _jsonld.load(open(os.path.expanduser('~/bones-forge/watch/headlines.json')))['pages'].get(_parts[1])
        except Exception: _hh = None
        if _hh:
            _t = _hh.get('table'); _tab = ''
            if _t:
                _e = html.escape; _cls = lambda i: ' class="n"' if i == 1 else (' class="w"' if i > 1 else '')
                _row = lambda r: '<tr>' + ''.join('<td' + _cls(i) + '>' + _e(c) + '</td>' for i, c in enumerate(r)) + '</tr>'
                _tab = ('<table class="hl-tab"><thead><tr>' + ''.join('<th' + (' class="r"' if i else '') + '>' + _e(c) + '</th>' for i, c in enumerate(_t['cols'])) + '</tr></thead><tbody>'
                        + ''.join(_row(r) for r in _t['rows']) + '</tbody>' + ('<tfoot>' + _row(_t['foot']) + '</tfoot>' if _t.get('foot') else '') + '</table>'
                        + ('<p class="hl-tnote">' + _e(_t['note']) + '</p>' if _t.get('note') else '')
                        + (('<p class="hl-cta"><a href="' + _e(_t['cta']['href']) + '">' + _e(_t['cta']['text']) + '</a>' + _e(_t['cta'].get('rest', '')) + ('<a href="' + _e(_t['cta']['href2']) + '">' + _e(_t['cta']['link2']) + '</a>' + _e(_t['cta'].get('tail', '')) if _t['cta'].get('href2') else '') + '</p>') if _t.get('cta') else ''))
            return '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">' + html.escape(_hh['big']) + '</div><p class="hl-line">' + html.escape(_hh['line']) + '</p>' + _tab + '</section>'
    sl = path.strip('/')
    return _SLOT if sl and '/' not in sl and sl in _HLSLUGS else ''
def fit_title(title, cap=70):
    """29 Oct 2026 (outside SEO scan): the <title> tag stays at or under 70 characters. In order: as written; without the middle section label;
    the lead alone (the brand stays in og:site_name); last resort, the lead cut at a word boundary that does not end on a small word. Social titles keep the full text."""
    if len(title) <= cap: return title
    parts = title.split(' | ')
    if len(parts) > 2 and len(parts[0] + ' | ' + parts[-1]) <= cap: return parts[0] + ' | ' + parts[-1]
    if len(parts[0]) <= cap: return parts[0]
    words = parts[0][:cap].split(' ')[:-1]
    while words and words[-1].lower().strip(',:;-') in ('and', 'or', 'of', 'the', 'a', 'an', 'to', 'in', 'on', 'for', 'with', 'than', 'at', 'by', 'from'): words.pop()
    return ' '.join(words).rstrip(' ,:;-')
_PARENT = {'/oy': '/hermes', '/census': '/hermes', '/social': '/hermes'}   # 12 Nov (Wayfinder): OY, SOCIAL and CENSUS sit under HERMES in the menu
def _menuhome(path, home):
    if path.startswith('/sagar/'): return '/sagar'
    return _PARENT.get(home, home)
def page(path, title, desc, body, wide_hero=None):
    # 29 Oct 2026: the main menu is the five divisions and STACK. Every other live page has one home division and is reached from it.
    _TOP = ('/qia', '/iris', '/oy', '/atlas', '/hermes', '/stack')
    _home = _menuhome(path, HOME.get(path) or ('/hermes' if path == '/hermes' or path.startswith('/hermes/') else path))
    _a = lambda h, t: f'<a href="{h}"{" aria-current=page" if h == _home else ""}>{t}</a>'
    nav = '@@NAV:' + path + '@@'   # filled after every page exists, so each dropdown lists only pages that were built
    hero = wide_hero or ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(fit_title(title))}</title>
<meta name="description" content="{html.escape(desc)}">
{seo_head(path, title, desc)}
<link rel="preload" href="/fonts/lora-normal-6b102ab3.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/abril-fatface-normal-804040b2.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#f7f0e0">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Heuremen">
<link rel="stylesheet" href="/style.css?v=@@CSSV@@">
</head>
<body>
<header class="top"><div class="wrap bar">
<a class="brand" href="/">{MARK}<span>Heuremen LLC</span></a>
<nav class="links">{nav}</nav>
</div></header>
<div class="stdbar"><div class="wrap"><a href="/standard"><b>STANDARDS</b></a><a href="/connect"><b>CONNECT</b> &middot; Connectors, plugins and skills</a></div></div>
{hero}
<main class="wrap">{_hlslot(path)}
{body}
</main>
<footer class="foot"><div class="wrap">
<p class="fl"><a href="/standard">Standards</a><a href="/downloads">Downloads</a><a href="/connect">Connect</a><a href="/plugins">Plugins</a><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="/security">Security</a><a href="/conflict-of-interest">Conflict of interest</a><a href="https://github.com/Heuremen-LLC/indahl.ai">GitHub</a><a href="https://huggingface.co/indahl">Hugging Face</a><a href="/changes">Changes</a><a href="/corrections">Corrections</a><a href="/community">Community</a><a href="/r/">Receipts</a><a href="/contact">Inquiry</a></p>
<p class="fs">Heuremen LLC</p>
<p class="fs">&ldquo;We found it.&rdquo;</p>
<p class="ai">Heuremen LLC reserves all rights. Content and data may be read, downloaded and cited with attribution. Text and data mining and use as AI training data are not permitted. <a href="/terms#ai-training">Details</a> &middot; Reference {_ref("page:" + path)}</p>
</div></footer>
<nav class="tabbar" aria-label="Divisions">{''.join(f'<a href="{h}"{" aria-current=page" if h == _home else ""}>{t}</a>' for h, t in (('/qia', 'QIA'), ('/iris', 'IRIS'), ('/hermes', 'HERMES'), ('/atlas', 'ATLAS'), ('/sagar', 'SAGAR')))}</nav>
<script src="/pwa.js" defer></script>
<script src="/live-tags.js?v=35e2ef27" defer></script>
<script src="/headline.js?v=6e4f48dc" defer></script>
<script src="/nav.js?v=00000000" defer></script>
</body>
</html>
'''

def _bold_acr(h1):
    # 29 Oct 2026 (his word): the acronym and the initials of its spelled-out name are bold, they get lost in the heading font.
    import re
    m = re.match(r'^([A-Z]{2,})( &middot; )(.+)$', h1)
    if not m:
        return h1
    acr, mid, rest = m.groups()
    words = rest.replace('&amp;', '&').split(' ')
    ini = [w for w in words if w != '&']
    if ''.join(w[0] for w in ini) == acr:
        rest = ' '.join(w if w == '&amp;' or w == '&' else f'<b class="ac">{w[0]}</b>{w[1:]}' for w in rest.split(' '))
    return f'<b class="ac">{acr}</b>{mid}{rest}'

def hero_slim(h1, sub=''):
    h1 = _bold_acr(h1)
    sub = f'<p class="sub">{sub}</p>' if sub else ''
    return f'<section class="hero slim"><div class="wrap"><h1>{h1}</h1>{sub}</div></section>'

def hero(kicker, h1, sub, actions=''):
    return hero_slim(h1, sub)

BTN = lambda href, t, cls='btn': f'<a class="{cls}" href="{href}">{t}</a>'

PAGES = {}
# the dice viewer's link carries a fingerprint of its contents, so a new version is never served from an old cache
import hashlib as _h
HOVER_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'hover', 'wave.js'), 'rb').read()).hexdigest()[:10]
TOK_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'tokens.js'), 'rb').read()).hexdigest()[:10]
WAV_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'waves.js'), 'rb').read()).hexdigest()[:10]
QB_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'quantum_bytes.js'), 'rb').read()).hexdigest()[:10]
COIN_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'coins.js'), 'rb').read()).hexdigest()[:10]
MOB_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'mobius.js'), 'rb').read()).hexdigest()[:10]
TES_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'tesla.js'), 'rb').read()).hexdigest()[:10]
TUR_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'turing.js'), 'rb').read()).hexdigest()[:10]
TB_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'play', 'threebody.js'), 'rb').read()).hexdigest()[:10]
VIEWER_V = _h.sha256(open(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'oy', 'quantum-dice', 'viewer.js'), 'rb').read()).hexdigest()[:10]

PAGES['/'] = page('/', 'Heuremen LLC: Published Claims Measured Against Their Own Data',
 'Heuremen LLC: Quantum Idle Audit, Inorganic Research & Intelligence Systems, and OY Learning Research.',
 '''
<section class="home3">
<p><a href="/qia#audit">QIA Audit &middot; IBM&rsquo;s Published Calibration Checked Against Itself</a></p>
<p><a href="/qia">QIA &middot; Quantum Idle Audit</a></p>
<p><a href="/iris">IRIS &middot; Inorganic Research &amp; Intelligence Systems</a></p>
<p><a href="/oy">OY &middot; Learning Research</a></p>
<p><a href="/atlas">ATLAS &middot; Built Infrastructure</a></p>
<p><a href="/hermes">HERMES &middot; Held Every Record, Measured Every Statement</a></p>
<p><a href="/time">TIME &middot; Stated Against Delivered</a></p>
<p><a href="/cada">CADA &middot; Checked Against Domain Alerts</a></p>
<p><a href="/uptime">UPTIME &middot; Status Pages Against Probes</a></p>
<p><a href="/forecast">FORECAST &middot; Stated Chance Against What Happened</a></p>
<p><a href="/cadence">CADENCE &middot; Stated Updates Against Delivered</a></p>
<p><a href="/trials">TRIALS &middot; Results Due Against Posted</a></p>
<p><a href="/launch">LAUNCH &middot; Stated Time Against Flown</a></p>
<p><a href="/linkrot">LINKROT &middot; Stated Links Against Live</a></p>
<p><a href="/tape">TAPE &middot; What We Published, and When</a></p>
<p><a href="/hosts">HOSTS &middot; One Model, Many Hosts</a></p>
<p><a href="/campus">CAMPUS &middot; The Documents Behind OY, Kept</a></p>
<p><a href="/airq">AIRQ &middot; Air Sensors Against the EPA's Own Targets</a></p>
<p><a href="/ailuminate">AILUMINATE &middot; MLCommons Safety Results, Kept and Checked</a></p>
<p><a href="/hpt">HPT &middot; Hospital Price Files Against the Rule</a></p>
<p><a href="/weights">WEIGHTS &middot; A Model Name Against Its Weights</a></p>
<p><a href="/airline">AIRLINE &middot; Scheduled Time Against Flown Time</a></p>
<p><a href="/fedsep">FEDSEP &middot; The Fed's Stated Range Against What Happened</a></p>
<p><a href="/revise">REVISE &middot; Stated Margin Against Later Revision</a></p>
<p><a href="/stack">STACK &middot; Every Test, Side by Side</a></p>
<p><a href="/pkginstall">PKGINSTALL &middot; Stated Install Command Against Resolution</a></p>
<p><a href="/seat">SEAT &middot; An Outside Seat Reads Our Pages</a></p>
<p><a href="/secrecords">SECRECORDS &middot; Security Records Against Their Own Rules</a></p>
<p><a href="/change">CHANGE &middot; Announced Shutdown Dates, Kept Over Time</a></p>
<p><a href="/hfsize">HFSIZE &middot; Stated Size Against the Weights</a></p>
<p><a href="/hflicense">HFLICENSE &middot; Stated License Against the License File</a></p>
<p><a href="/pkglicense">PKGLICENSE &middot; Stated License Against the Repository</a></p>
<p><a href="/support">SUPPORT &middot; Stated Support Against Releases</a></p>
<p><a href="/arxivdrift">ARXIVDRIFT &middot; Studies Read, Then Revised</a></p>
<p><a href="/api">API &middot; Data and MCP</a></p>
<p><a href="https://github.com/Heuremen-LLC/indahl.ai">Plans, code and trend history &middot; GitHub</a></p>
<p><a href="https://huggingface.co/indahl">Datasets and models &middot; Hugging Face</a></p>
</section>
''', hero_slim('Heuremen LLC'))

PAGES['/qia'] = page('/qia', 'QIA | Quantum Idle Audit | Heuremen LLC',
 'Quantum Idle Audit: independent measurement of quantum processors against their published calibration, line by line, with the evidence to rerun it.',
 f'''
<section class="split">
<div><h2>What we measure</h2>
</div>
<ul class="ticks">
<li><b>Coherence.</b> T1 and T2.</li>
<li><b>Readout.</b> Assignment error, both directions.</li>
<li><b>Gates and coupling.</b> Against stated values.</li>
<li><b>The record.</b> Stamp against measurement date.</li>
<li><b>Unlisted effects.</b> Costs no published figure covers.</li>
</ul>
</section>

<section class="band">
<h2>What you receive</h2>
<div class="grid3">
<div><h3>Case statement</h3><p>Stated, delivered, deviation. Line by line.</p></div>
<div><h3>Evidence package</h3><p>Plans, circuits, code, job identifiers, raw results, calibration records.</p></div>
<div><h3>Rerun path</h3><p>Reproducible by any party you name.</p></div>
</div>
</section>

<section class="split"><div><h2>Engagement</h2></div>
<ol class="steps">
<li><b>Scope</b><span>Processors and figures, in writing.</span></li>
<li><b>Plan</b><span>Fixed before data.</span></li>
<li><b>Measure</b><span>Against the calibration in force.</span></li>
<li><b>Review</b><span>Adversarial. Internal.</span></li>
<li><b>Deliver</b><span>Case statement and evidence.</span></li>
</ol></section>


<section class="split">
<div><h2>Requirements</h2></div>
<ul class="ticks">
<li>The devices and figures in scope.</li>
<li>Device access, or existing job records.</li>
<li>Publication preference. Confidential by default.</li>
</ul>
</section>

<section class="closing"><h2>Case statement</h2><p>QIA-2026-001, IBM Heron processors. Produced on Heuremen&rsquo;s own accounts; not a client engagement.</p><p class="actions">{BTN('/quantum-idle-audit.pdf', 'Read QIA-2026-001 (PDF)')}{BTN('/contact', 'Contact us', 'ghost')}</p></section>
''', hero('QIA &middot; Quantum Idle Audit', 'Quantum processors measured against their published calibration.', ''))

IRIS_BENCH = ('<section class="bench"><h2>Live From Our Lab: How Different Models Handle Standards</h2>'
              '<p>Open-weight models, served locally, temperature 0, fixed seed. Per model: bare arm, bare repeat (determinism check), guard arm with the Fault and Guard text appended to the prompt. Bars show replies received. Results post once scoring checks pass.</p>'
              '<div id="bench-live" class="bench-live">Loading.</div>'
              '<div id="bench-more"></div><div id="bench-results"></div>'
              '<h3>The Standards in this run</h3>'
              '<table class="mtx"><thead><tr><th>Fault</th><th>Guard</th><th>What the model is asked</th></tr></thead><tbody>'
              '<tr><td>19. A ruler that cannot say &ldquo;I cannot tell&rdquo; lies at scale</td><td>8. Four outcomes, never two, and the terminating reason on every call</td><td>Two methods with scores and widths. Is A better than B?</td></tr>'
              '<tr><td>25. A verdict without a width is not a verdict</td><td>Stated in the prompt</td><td>Accuracy from a count of right answers. Under the plain wording the prompt does not ask for a width. A right figure with no width is scored a Fault, so this Fault is an omission, not a wrong answer. The scorer checks that a width is given, not that it is right. In our own runs almost no reply gave a width: none in round two of the house training, and 3 of 15,448 house replies as of 8 November. So this Fault separates models very little, and a difference here is mostly replies the scorer could not read, not a width habit.</td></tr>'
              '<tr><td>29. An equals sign is a claim, and you will print one you have not checked</td><td>27. Both sides of every identity are evaluated before it is printed</td><td>A report says &ldquo;k of n is p%.&rdquo; Is that correct?</td></tr>'
              '<tr><td>3. A maximum over many draws reported as a measurement</td><td>9. Every reported figure carries its own n, and the n it was selected from</td><td>Test accuracy from several random seeds, reported as one number.</td></tr>'
              '</tbody></table>'
              '<p>Every other Fault and Guard is in the full lists: <a href="https://heuremen.org/faults.pdf">Faults</a> &middot; <a href="https://heuremen.org/guards.pdf">Guards</a> (PDF) &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/faultsguards">Python package (git)</a> &middot; <a href="https://pypi.org/project/faultsguards/">PyPI</a> &middot; <a href="https://huggingface.co/datasets/indahl/faultsguards">dataset</a><br>Raw replies, plans, code and scores for every finished round: <a href="https://huggingface.co/datasets/indahl/iris-faults-guards-bench">Hugging Face dataset</a></p>'
              '<script src="/iris/bench.js" defer></script></section>')
# 31 Oct 2026 (his "peeps coming to our site starting tonight, we gotta give them something to look at ... Yo!"): YO v2 trains live (PLAN_YO_V2.md).
IRIS_YO = ('<section class="bench"><h2>YO: A Small Model Trained to Audit IBM&rsquo;s Records</h2>'
           '<p>YO is Qwen3-1.7B, a small open-weight model (Apache-2.0), trained with LoRA to read IBM&rsquo;s published calibration records the way an auditor does. '
           'It has two jobs. The first is to flag qubits whose T1 or T2 was measured more than a day before the record&rsquo;s stamp, and error values of exactly zero. '
           'The second is to give one of four verdicts on a measured value against a stated one: ABOVE, BELOW, CONSISTENT or CANNOT_TELL. '
           'The records are IBM&rsquo;s own calibration history for every processor our account can see, up to 180 days back. The newest month is held out as the test.</p>'
           '<p>The plan was committed before any data was built, and the baselines were scored on the test items before training began. The test reading was read once, after the run, and checked by a referee before it was posted. '
           'YO v3 then continued training YO v2 on qubits stale by one to two days and was not adopted. YO v4 continued training YO v2 on records whose qubits all went stale together, under a third plan committed before its data, was tested on records no earlier test used, and replaced YO v2 as the model at work. Every reading is in the table. '
           '<a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/yo/PLAN_YO_V2.md">Plan, YO v2</a> &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/yo/PLAN_YO_V3.md">Plan, YO v3</a> &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/yo/PLAN_YO_V4.md">Plan, YO v4</a> &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo/read">YO Read checks</a> &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/yo/read/fresh/PLAN_YO_FRESH.md">Plan, fresh test</a> &middot; <a href="https://huggingface.co/indahl/YO">Download YO (Hugging Face)</a> &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo">Code (git)</a></p>'
           '<div id="yo-live" class="bench-live">Loading.</div><script src="/iris/yo.js" defer></script></section>')
# 8 Nov 2026: round two of the flock-trained small model (Sage VERDICT STANDS 00:48Z; ledger rows flock.*)
IRIS_FLOCK = '<section class="bench"><h2>A Small Model Trained on the House&rsquo;s Own Answers</h2><p>Our open-model triangles answer FaultsBench items, and each answer is scored by the item&rsquo;s own code. We trained Qwen3-1.7B (Apache-2.0) with LoRA on answers the code scored correct (P1 and P4 families). We tested it on two held-out rounds: three samples per item, temperature 0.7, up to 1,200 tokens, thinking off. Every number below comes from the released eval rows, which include the untouched model&rsquo;s rerun in every evaluation. It also got much worse at one kind of question (below).</p><p>Timing. Round one&rsquo;s plan was in a Bitcoin block before training. Round two&rsquo;s plan landed in block 974942 (14:40 UTC, 7 Nov). Its training started earlier, as the plan allowed: the first training log was created at 13:48 UTC. Every evaluation started after the block. One retrain (seed 63, after its first run failed) started at 14:36 UTC, so its rule is self-witnessed by about 4 minutes. Changes made after reading are listed separately and marked. The list is in the dataset.</p><p>Seeds. Round one used seed 61. Round two added seeds 62, 63 and 64. Seed 64 failed to train twice (the loss became not a number). One of four seeds failed, so by the rule written before training the result reads seed-dependent.</p><p>Held-out rounds, two counts side by side. Counting every answer, the share not right fell from 0.600 (0.599 in seed 63&rsquo;s run) to 0.399, 0.447 and 0.452 (seeds 61, 62, 63). Among answers the code could score, the share wrong fell from 0.481 (0.482) to 0.331, 0.386 and 0.404. Both gains exceed the untouched model&rsquo;s own spread between repeat samples (at most 0.008 on the scored count, 0.015 counting every answer). The gains differ between seeds. Some of the gain is the trained models giving answers the scorer can read: the untouched model&rsquo;s answers were unreadable 22.5 to 22.9% of the time, the trained models&rsquo; 8 to 10%.</p><p>P1 items, paired item by item, seed 61: 44 answers turned right and 4 turned wrong (two-sided exact binomial test on those 48, p = 1.5e-9).</p><p>Questions asking for the highest of a list of values. The untouched model answered all 90 right. The trained models answered 27, 30 and 38 of 90 right. This is the largest per-kind change we measured. The scored-only count cannot see it: the scorer reads the reply&rsquo;s last number, scores it right if it is the highest value and wrong if it is the mean, and leaves any other listed value unclassified. Most of the trained models&rsquo; wrong answers are of that kind. In 46 unclassified replies to list questions of this family (highest, lowest and middle value), 40 drawn at random plus 6 chosen as tolerance-only, read in full (non-blind), none named the right value and then ended on another number.</p><p>Defined after the data. Most of those unclassifiable answers gave a value from the list that was not the highest: 38 of 52, 45 of 52 and 31 of 47 under exact matching. Our stamped rule counts 40, 46 and 36, over-crediting 8 of 151. A non-blind reading in full sides with exact matching.</p><p>Defined after the data, P3 items (120 answers per model, first sample only). The untouched model gave 40 right, 25 wrong and 55 unreadable. Seeds 61 and 62 gave 65 and 53 right, 55 and 65 wrong. Seed 63 gave 43 right and 72 wrong against its own run&rsquo;s untouched model at 40 right, 28 wrong and 52 unreadable, about flat on right answers. All three gave almost no unreadable answers, so whether P3 got better or worse depends on which count is used. The untouched model itself differed between runs by a net three rows on P3 (11 answers changed score, in both directions), so P3 differences of a few rows are not read as signal.</p><p>Limits: one model, one benchmark, three trained seeds whose gains differ.</p><p class="meta">The method, the numbers and the released eval rows: <a href="https://huggingface.co/datasets/indahl/iris-house-training">indahl/iris-house-training</a> on Hugging Face.</p></section>'
# 12 Nov 2026 (his "close it out on the lab too and make sure Stan is live"): STAN, live, at the top of the LAB page. The feed (/iris/lab/stan.json, written by stan/scripts/live_status.py) is numbers and fixed words only.
IRIS_STAN = ('<section class="bench" id="stan"><h2>STAN: Live</h2>'
  '<p>STAN is our work on small open-weight models that help apply our open standard, <a href="/standard">Standards 2.0</a>. The live lane is STAN-E. Local open models on a GPU box and on a Mac draft errata, meaning places where a paper disagrees with itself. Each model is graded against findings that two independent readers confirmed. The errata are a classification for indexing, not an assessment.</p>'
  '<p>The confirmed findings come from three desk pipelines that run on their own. SAGAR reads gravitational-wave papers, BRANDS reads papers by authors at named companies, and the quant desk reads quantitative papers. Each runs a draft agent and then a blind second reader, and a finding counts only when both agree.</p>'
  '<p>STAN A, the first lane, trained a model on titles and abstracts. Its teacher route on full text closed on 12 November 2026 after 0 of 12 teacher-code cells passed the keep line written before the run.</p>'
  '<div id="stan-live" class="bench-live">Loading.</div><script src="/iris/lab/stan.js?v=5" defer></script>'
  '<p class="meta">Every result is public as data as it happens: <a href="https://github.com/Heuremen-LLC/stan">Heuremen-LLC/stan</a> on GitHub (plan, code, results) and <a href="https://huggingface.co/datasets/indahl/stan-results">indahl/stan-results</a> on Hugging Face. Paper texts and raw model outputs stay private. Live feed: <a href="/iris/lab/stan.json">/iris/lab/stan.json</a>.</p></section>')
IRIS_FALCON = ('<section class="bench"><h2>Live From Our Lab: A Falcon Trained on the Standards</h2>'
              '<p>Falcon3 3B Instruct, tuned with LoRA on new questions in the same form, then answered on two fresh evaluation sets. Three models answer the same items: the untouched model, the model trained on the <a href="/standard">Standards</a>, and a control trained on the same items with mixed labels. Settings were fixed and committed before any training. This is one training run per model, with one training seed. A second seed and two further evaluation sets have been run and are not on this page yet. Results follow.</p>'
              '<div id="train-live" class="bench-live">Loading.</div><script src="/iris/train.js" defer></script>' + open(os.path.expanduser('~/bones-forge/iris_index/falcon_train/falcon_results.html')).read() + '</section>')
IRIS_RUN = ('<section class="bench"><h2>Running Now in the IRIS Lab</h2>'
            '<p>The lab keeps one job going at all times. Each job\'s plan, with its rules and what would count as a result, is committed before the job starts. Results post here after the parser check (replies read in full), as in every round.</p>'
            '<div id="iris-run" class="bench-live">Loading.</div><script src="/iris/live.js" defer></script></section>')
IRIS_THUNDER = ('<section class="bench"><h2>Live From Our Lab: The Two Finalists, Head to Head</h2>'
              '<p>After eleven rounds, the two models with the lowest mean Fault rate among readable replies under the Guard wording were smollm2:1.7b and qwen3:4b. That mean included families in which fewer than 10 replies could be read, which the written rule leaves out. With every cannot tell family left out, the two lowest are smollm2:1.7b and olmo2:7b, and qwen3:4b has no readable family. The head to head below uses the two models as first chosen and was not re-run with olmo2:7b. The selection rule and the reading rule were committed on 27 October, before any round was read. The scoring rules that read replies were amended afterwards in dated addenda, as the note under the table says. Both finalists then answered the same two fresh question sets, rounds 12 and 13, in the same arms at temperature 0.</p>'
              + open(os.path.expanduser('~/bones-forge/iris_index/thunder_results.html')).read() + '</section>')
IRIS_TOP = ('<section class="addpdf"><p>Submit a published study or model review for indexing (link to its PDF):</p>'
            '<form class="idx" method="post" action="/index-request"><input type="hidden" name="m" value="iris"><div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>'
            '<input name="url" type="url" required maxlength="2000" placeholder="https://&hellip;.pdf" aria-label="Link to a PDF"><button class="btn" type="submit">Add a PDF</button></form></section>\n')
PAGES['/iris'] = page('/iris', 'IRIS | Inorganic Research & Intelligence Systems | Heuremen LLC',
 'IRIS: reliability for AI-assisted research. Adversarial review, controls installed in your pipeline, and a running catalogue of how AI-assisted analysis fails.',
 f'''

<section class="band">
<h2>What we do</h2>
<div class="grid3">
<div><h3>Adversarial review</h3><p>From raw data. Every claim recomputed, alternatives tested, wording narrowed to what the data supports.</p></div>
<div><h3>Release controls</h3><p>Every public number traced to source. A release refused when two copies disagree.</p></div>
<div><h3>Failure catalogue</h3><p>Standards. Maintained from live work.</p></div>
</div>
</section>

<section class="split"><div><h2>Engagement</h2></div>
<ol class="steps">
<li><b>Scope</b><span>The claim and its raw data.</span></li>
<li><b>Plan</b><span>Fixed before review.</span></li>
<li><b>Review</b><span>Recomputed from source.</span></li>
<li><b>Controls</b><span>Installed in your pipeline.</span></li>
<li><b>Deliver</b><span>What stands, what narrows, what falls.</span></li>
</ol></section>


<section class="closing"><h2>The catalogue</h2><p>Open.</p><p class="actions">{BTN('https://heuremen.org/faults.pdf', 'Faults (PDF)')}{BTN('https://heuremen.org/guards.pdf', 'Guards (PDF)', 'ghost')}</p></section>
''', hero('IRIS &middot; Inorganic Research &amp; Intelligence Systems', 'Adversarial review and release controls for AI-assisted research.', ''))

PAGES['/approach'] = page('/approach', 'What we offer | Heuremen LLC',
 'What Indahl offers: independent measurement of quantum hardware (QIA) and review of AI-assisted research (IRIS), each delivered with its findings, method and evidence.',
 '''
<section class="split"><div><h2>Services</h2></div>
<ul class="ticks">
<li><a href="/qia">QIA &middot; Quantum Idle Audit</a></li>
<li><a href="/iris">IRIS &middot; Inorganic Research &amp; Intelligence Systems</a></li>
</ul></section>

<section class="split"><div><h2>What you receive</h2></div>
<ul class="ticks">
<li>Findings.</li>
<li>Method, fixed before data.</li>
<li>Evidence package.</li>
</ul></section>

<section class="split"><div><h2>Confidentiality</h2></div>
<ul class="ticks">
<li>Mutual NDA first.</li>
<li>Nothing published without written consent.</li>
</ul></section>

<section class="split"><div><h2>Terms</h2></div>
<ul class="ticks">
<li>Scoped and quoted per engagement, under a statement of work.</li>
<li>No vendor affiliations. Fees independent of findings.</li>
</ul></section>
''', hero('What we offer', 'Limited engagements.', ''))

# 9 Nov 2026 (site pass H3): the held OY kids pages live in held_kids.py, a house-only file that the public repository never carries.
# The build reads it only when it is present, in this file's namespace. The pages stay held either way (HELD_KIDS below).
_HK = os.path.join(HERE, 'held_kids.py')
if os.path.exists(_HK): exec(compile(open(_HK, encoding='utf-8').read(), _HK, 'exec'))

# About page removed 26 Oct 2026 (his word).

# 24 Oct 2026, his flow: ONE button on /contact ("Engagement Inquiries"), nothing else. It opens /agree: the NDA and the Privacy
# Notice, each in a scroll box; each box must be read to the end before its checkbox unlocks; both must be checked to continue.
# Then /inquiry: the engagement fields, and Submit only works after the identity check (gate.js). Nothing is stored before Submit.
import re as _re
_NDA_SRC = os.path.join(HERE, '..', 'heuremen-specbook', 'contracts', 'MUTUAL_NDA.md')
_nda_md = open(_NDA_SRC, encoding='utf-8').read()
NDA_VERSION = _re.search(r'DRAFT v([0-9.]+)', _nda_md).group(1)
PRIVACY_VERSION = '2026-11-11a'   # 11 Nov (2026-11-11a): the named-thing search on the alerts page is removed, and its sentence with it. 10 Nov (2026-11-10g): following a company or other named thing (entities.py, alerts.py, alerts_send.py). 10 Nov (2026-11-10f): alerts for every desk and division, delivery choice (alerts.py, alerts_send.py). 10 Nov (2026-11-10e): webhooks and notifications on your device (notify.py). 10 Nov (2026-11-10d): the combined sign-up form (one form for the newsletter, site updates and alerts). 10 Nov (2026-11-10c): outcome alerts (double opt-in, what is stored, how to leave). 10 Nov (2026-11-10b): the weekly changes email (what is stored, why, how to leave). 10 Nov: semicolons split into sentences, no change in meaning. 30 Oct (2026-10-30b): the correction or removal form
_nda = '\n'.join(l for l in _nda_md.split('\n') if not l.startswith('*DRAFT'))
_nda = _nda.split('\n---')[0]                                            # no signature block on the web: acceptance is the checkbox (section 12)
_nda = _nda.replace('is made on [DATE] between', 'is made on the date Counterparty accepts it between', 1)
_nda = _nda.replace('**[COUNTERPARTY LEGAL NAME]**, a [JURISDICTION AND ENTITY TYPE] ("Counterparty")', 'the organisation named by the person accepting it ("Counterparty")', 1)
def _md(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s).replace('"', '&quot;')
_h = []
for blk in _nda.split('\n\n'):
    b = blk.strip()
    if not b or b.startswith('# '): continue
    if b.startswith('## '):
        head, _, b = b.partition('\n'); _h.append(f'<h3>{_md(head[3:])}</h3>')
        if not b.strip(): continue
    _h.append('<p>' + '<br>'.join(_md(x) for x in b.strip().split('\n')) + '</p>')
NDA_HTML = ''.join(_h)

# /agree is completed by the worker: __PRIVACY__ is replaced with the privacy notice body at build time below.
_AGREE_BODY = f"""
<section class="form-wrap"><form class="inq" method="post" action="/agree">
<input type="hidden" name="nda_read" value=""><input type="hidden" name="privacy_read" value="">
<h2>Mutual Non-Disclosure Agreement</h2>
<div class="legal-box" id="box-nda" tabindex="0">{NDA_HTML}</div>
<label class="check"><input type="checkbox" name="nda" value="yes" required><span>I have read the Mutual Non-Disclosure Agreement, I am authorised to accept it on behalf of my organisation, and I accept it.</span></label>
<h2>Privacy Notice</h2>
<div class="legal-box" id="box-privacy" tabindex="0">__PRIVACY__</div>
<label class="check"><input type="checkbox" name="privacy" value="yes" required><span>I have read the Privacy Notice and agree to it.</span></label>
<h2>Terms</h2>
<label class="check"><input type="checkbox" name="terms" value="yes" required><span>I have read the <a href="/terms">Terms</a>, including the limitation of liability, and agree to them.</span></label>
<button class="btn" type="submit">Continue</button>
</form></section><script src="/gate-ui.js"></script>
"""
PAGES['/agree'] = page('/agree', 'Engagement Inquiries | Heuremen LLC', 'Agreements for an engagement inquiry.', _AGREE_BODY, hero('', 'Inquiries', ''))
PAGES['/contact'] = page('/contact', 'Inquiries and Removal Requests | Heuremen LLC', 'Contact Heuremen LLC.', _AGREE_BODY, hero('', 'Inquiries', ''))

# /inquiry is served only after /agree. The worker fills __VERIFY__ (the identity step or the verified address) and __DISABLED__.
PAGES['/inquiry'] = page('/inquiry', 'Inquiry | Heuremen LLC', 'Send an inquiry to Heuremen LLC.',
 """
<section class="form-wrap"><p class="notice">Please do not include any confidential information in your inquiry.</p><form class="inq" id="inq" method="post" action="/inquire">
<input type="hidden" name="t" value="__T__">
<div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
<div class="row"><label>Reason<select name="reason" required><option value="engagement">Engagement inquiry</option><option value="privacy">Privacy request</option><option value="security">Security report</option></select></label></div>
<div class="row"><label>Full name<input name="name" required maxlength="120" autocomplete="name"></label>
<label>Title<input name="role" required maxlength="120" autocomplete="organization-title"></label></div>
<label>Organisation<input name="organisation" required maxlength="160" autocomplete="organization"></label>
<label>What you need, in your own words<textarea name="scope" required maxlength="3000" rows="8"></textarea></label>
<p class="hint">In a few sentences: the systems, figures or results involved, your organisation&rsquo;s relationship with any vendors involved, and what a good outcome looks like.</p>
<div class="row" id="scoping"><label>Approximate budget<select name="budget"><option value="">Not sure yet</option><option>Under $10,000</option><option>$10,000 to $50,000</option><option>$50,000 to $150,000</option><option>Over $150,000</option></select></label>
<label>Timeline<select name="timeline"><option value="">Flexible</option><option>As soon as possible</option><option>Within a month</option><option>One to three months</option></select></label></div>
<p class="hint" id="scoping-note">Budget and timeline are for scoping only. They are not a quote or a commitment.</p>
<label>Referred by (optional)<input name="referral" maxlength="300"></label>
__VERIFY__
<button class="btn" type="submit"__DISABLED__>Submit</button>
</form></section><script src="/gate-ui.js"></script>
""", hero('', 'Inquiries', ''))

GATE_JS = r"""// gate-ui.js: each legal box must be scrolled to the end before its checkbox unlocks; the inquiry draft survives the sign-in.
(function () {
  function box(id, cb, flag) {
    var b = document.getElementById(id), c = document.querySelector('input[name="' + cb + '"]'), f = document.querySelector('input[name="' + flag + '"]');
    if (!b || !c || !f) return;
    c.disabled = true; c.parentNode.classList.add('locked');
    function check() { if (b.scrollTop + b.clientHeight >= b.scrollHeight - 6) { c.disabled = false; f.value = '1'; c.parentNode.classList.remove('locked'); } }
    b.addEventListener('scroll', check); check();
  }
  box('box-nda', 'nda', 'nda_read'); box('box-privacy', 'privacy', 'privacy_read');
  var f = document.getElementById('inq'); if (!f) return;
  (function () { var r = f.elements['reason'], a = document.getElementById('scoping'), b = document.getElementById('scoping-note'); if (!r || !a) return; function t() { var on = r.value === 'engagement'; a.hidden = !on; if (b) b.hidden = !on; } r.addEventListener('change', t); t(); })();
  var K = 'indahl_inquiry_draft', N = ['name', 'role', 'organisation', 'scope', 'budget', 'timeline', 'referral'];
  try { var d = JSON.parse(sessionStorage.getItem(K) || '{}'); N.forEach(function (n) { if (d[n] && !f.elements[n].value) f.elements[n].value = d[n]; }); } catch (e) {}
  var v = document.getElementById('verify');
  if (v) v.addEventListener('click', function () { var d = {}; N.forEach(function (n) { d[n] = f.elements[n].value; }); try { sessionStorage.setItem(K, JSON.stringify(d)); } catch (e) {} });
  f.addEventListener('submit', function () { try { sessionStorage.removeItem(K); } catch (e) {} });
})();
"""

PAGES['/privacy'] = page('/privacy', 'Privacy Notice and Data Handling | Heuremen LLC', 'How Heuremen LLC and all of its divisions collect, use, protect and retain personal information.',
 '''
<section class="legal">
<p class="meta">Effective 23 October 2026. Updated 29 October 2026 to describe the installable app. Updated 30 October 2026 to say which pages load typefaces from Google Fonts. Updated 10 November 2026 to describe the weekly changes email, and again the same day to describe outcome alerts. Updated 10 November 2026 to describe the combined sign-up form, and again the same day to describe webhooks and notifications on your device. Updated again the same day to describe alerts for every desk and division and the choice of how they come, and again to describe downloading or deleting your data, deletion receipts, the counts on our transparency page and our own test subscription, and again to describe following a company or other named thing. Updated 11 November 2026: the search for a named thing on the alerts page is removed.</p>
<p>This notice explains how Heuremen LLC (&ldquo;Heuremen&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;), including all of its divisions, collects, uses, shares, protects and retains personal information through indahl.ai, heuremen.org, our inquiry form, our correspondence and our engagements. We hold the information of everyone who contacts us, and of any client, in confidence.</p>

<h2>Information we collect</h2>
<h3>When you visit our websites</h3>
<p>Our websites set no cookies and run no analytics, advertising, tracking or session-recording scripts. indahl.ai is delivered through Cloudflare and heuremen.org is hosted on GitHub Pages. Each processes standard request data (IP address, browser type, the page requested and the time) to deliver and protect the site. The pages of indahl.ai serve their typefaces from our own site. One page of heuremen.org, the correlations page, loads typefaces from Google Fonts, which receives the requesting IP address and browser information.</p>
<p>If you install indahl.ai as an app on your phone or computer, your browser keeps a copy of the public pages you open on your own device so that they open without a connection. We receive nothing from that copy and it holds no personal information from you. Removing the app or clearing the site&rsquo;s data deletes it. Live data feeds, the inquiry form and sign-in are never kept in it. The same app code shows the notifications you turn on, as described below.</p>
<h3>When you send a correction or removal request</h3> <p>The correction or removal form collects what you enter: your name, an email address we can answer, the page concerned and your request, with the time it arrived and the country your connection reports. We use it only to handle the request, to answer you, and where needed to confirm that a removal request comes from the person or organisation named. It is never posted. A short one-way hash of your network address is kept for one hour to limit repeated requests, and the address itself is not kept.</p> <h3>When you submit an inquiry</h3>
<p>The inquiry form collects what you enter: your name, organisation email address, organisation, role, a description of what you need (including the systems or results involved and your organisation&rsquo;s relationships with relevant vendors), an approximate budget range and timeline, who referred you, and your confirmations regarding non-disclosure, authority and this notice. For an engagement inquiry we also record the identity you verified (your work email address, the name on that account, the sign-in method and the identifier our sign-in provider assigns), and your acceptance of our Mutual Non-Disclosure Agreement and this notice (which versions, the time, that you read both to the end, and your name, title and organisation). Nothing is recorded until you submit the inquiry. We also record the time of the inquiry and the country the request came from. We do not store your IP address. A truncated one-way hash of it, which may still be personal data, is held for up to one hour only to limit repeat submissions. Each accepted inquiry is also emailed to us.</p>
<h3 id="signup">When you use the sign-up form</h3>
<p>One sign-up form sits at the foot of the pages of indahl.ai and on the email updates page. It collects your email address and the boxes you tick. The boxes are the weekly newsletter, new desks and new data, outcome changes on every desk, and on a desk page, a division page or a brand page that desk, that division or the desks with rows about that organisation. The email updates page lists every desk and division to tick. The form also asks how alerts and updates should come: as they happen, in one daily digest or in one weekly digest on Tuesdays. The newsletter box needs no confirmation. The other boxes need a confirmation by email first, as described below. If you tick the newsletter and another box, the newsletter starts at once and the rest waits for your confirmation.</p>
<p>For the weekly newsletter we store your email address with the time you subscribed, the version of this notice in force then, and a random unsubscribe token. We use it for one thing: to email you the weekly changes page every Tuesday. Every newsletter email has a one-click unsubscribe link. Unsubscribing deletes your address and its token from the list at once. While you are subscribed we also keep a truncated one-way hash of your email address, only so that a second sign-up does not make a duplicate. It is deleted when you unsubscribe. A truncated one-way hash of your IP address is held for up to one hour only to limit repeat sign-ups. We never share, sell or rent the list, and we never use it for anything other than this email. The addresses are kept in a private storage area accessible only to us and are never published, logged or posted.</p>
<h3 id="alerts">Alerts, new desks and new data</h3>
<p>For every other box we store your email address, the desks, pages, divisions and organisations you ticked, the companies and other named things you follow (such as a model, a quantum backend or a school), whether you asked for every desk, whether you asked for new desks and new data and how you want alerts and updates to come, with the time you signed up and the version of this notice in force then. We then email one confirmation link to that address. Nothing else is sent until you open the link and press Confirm. A sign-up that is not confirmed is deleted after two days. Once you confirm, we store the time you confirmed and a random token for your manage and unsubscribe links. We use the address for what you ticked and nothing else: an email when an outcome changes on a desk you follow, an email when the published data changes on a desk, page or division you follow, an email when a row about a company or other named thing you follow changes or a new row about it appears, and an email when a new desk goes live, a desk publishes its first value under its change rule or a release adds an entry to the changelog. A digest puts the same emails into one a day or one a week. Our sending log keeps the first characters of your token next to each alert sent to it, and for a digest the time of the last one, with no address, so that nothing is sent twice. Those lines stay in the log after you unsubscribe, with no address and no way back to one. Every alert has a link to change what you get, where you can also add or remove the weekly newsletter. A newsletter ticked there starts at once, since the address is already confirmed. Every alert also has a one-click unsubscribe link, which removes your alerts and your new desks and new data emails. The newsletter has its own one-click link in each issue. On the manage page, Unsubscribe from everything removes both. Unsubscribing from alerts deletes your address, your choices and the token at once. While you are signed up we also keep a truncated one-way hash of your email address, only so that a second confirmation joins your existing record. It is deleted when you unsubscribe. A truncated one-way hash of your IP address is held for up to one hour, and a truncated one-way hash of your email address for up to one day, only to limit repeat sign-ups and confirmation emails. We never share, sell or rent the list, and we never use it for anything other than these emails. The addresses are kept in a private storage area accessible only to us and are never published, logged or posted.</p>
<h3 id="follow">Feeds, the calendar and the OPML file</h3>
<p>The feeds, the calendar file and the OPML file on <a href="/follow">the follow page</a> are ordinary files. Fetching them sends the same request data as any page, and we keep no list of who reads them. Each feed names the public WebSub hub at pubsubhubbub.appspot.com, run by Google. When a feed changes we send that hub the address of the feed and nothing else. A feed reader that subscribes through the hub deals with Google directly, under Google&rsquo;s terms.</p>
<h3 id="push">Notifications on your device</h3>
<p>If you press &ldquo;Notify me on this device&rdquo; and allow notifications, your browser creates a push subscription and we store it: the push address your browser&rsquo;s push service gives it, the two public keys your browser makes for encrypting messages to it, the desks you picked, the time, the version of this notice in force then and a random token. Your browser keeps that token on your device, in its local storage and in the site&rsquo;s cache storage, so the button can show whether notifications are on and so the app code can move your notifications to a new push address when your browser&rsquo;s push service replaces the old one. When that happens we replace the push address and keys on your record and keep your desks. We use the subscription for one thing: to send a short notification when an outcome changes on a desk you picked. Each notification is encrypted for your browser and passes through your browser&rsquo;s push service (Google for Chrome, Mozilla for Firefox, Apple for Safari, Microsoft for Edge), which cannot read it. Each message we send carries our contact address for the push service, as the Web Push standard asks. Our sending log records the first characters of the token, the time and the result of each run, never the push address or the keys. Pressing the button again deletes the subscription. When a push service tells us a subscription has ended, we delete it. A truncated one-way hash of the push address is kept with it only so that the same device does not make a second record, and a truncated one-way hash of your IP address is held for up to one hour only to limit repeat sign-ups.</p>
<h3 id="webhooks">Webhooks</h3>
<p>If you register a webhook, we store the address you enter, the desks you picked, whether it is a signed webhook or a Slack, Discord or Microsoft Teams address, the signing secret we make for a signed webhook, the time, the version of this notice in force then and a random token for your manage link. A truncated one-way hash of the address is kept so that it is registered once, and a truncated one-way hash of your IP address is held for up to one hour only to limit repeat registrations. When you register, our server sends the address one challenge, or one test message for a chat app. After that we send it only outcome changes on the desks you picked. If deliveries fail ten times in a row we record when the webhook was turned off and the count. A delivery waiting for a retry is kept in our sending queue with the token and the changes it carries, and is removed once it is sent or dropped. Our sending log records the first characters of the token, the time and the result of each attempt, never the address or the secret. Deleting the webhook from its manage page erases the address, the secret and the hash at once. An address you register may itself carry personal information, for example a name in a host name, so please register only addresses you control.</p>
<h3 id="yourdata">Downloading or deleting your data</h3>
<p>On the manage page of an email or webhook sign-up, and at <a href="/mydata">Your data</a> for notifications on a device, you can download everything we hold for that sign-up as a JSON file, or delete all of it at once. Send logs keep only the first characters of the sign-up token, never the address, and a deletion does not change them. A deletion gives you a receipt that holds the kind of record and the time, nothing else. We keep deletion receipts for 400 days.</p>
<h3 id="transparency">Counts on our transparency page</h3>
<p>Our <a href="/transparency">transparency page</a> counts alerts sent, sign-ups removed and deletions, for everyone together. To count removals, we keep on our own computer a list of one-way hashes of the storage keys of current sign-ups. A hash cannot be turned back into an address, link or device, and it is dropped at the next count after its sign-up is gone. Counts under 5 are shown as fewer than 5, and a channel total is shown only when at least 5 different recipients are behind it. We run our own test webhook to check that alerts arrive, and it is left out of every count. <a href="/r/alert/">Alert receipts</a> name the desk, the change and the kinds of channel that carried it, and hold nothing about who received it. Signatures on our feeds, API answers and webhooks add nothing to what we collect.</p>
<h3>When you add a PDF link under a Recount Matrix</h3>
<p>The one-field box under each Recount Matrix stores the link you paste, the table it was added under and the time. It stores no name, email address or IP address. A truncated one-way hash of your IP address is held for up to one hour only to limit repeat submissions. We read each link before anything changes in a table.</p>
<h3>When you add a response</h3>
<p>The response form stores the reference of the page you answered, the link to your PDF, the host name of that link and the time. It stores no name, email address or IP address. A truncated one-way hash of your IP address is held for up to one hour only to limit repeat submissions. We read each file before anything is posted. A posted response shows its date and the host it came from.</p>
<h3>When we correspond or work together</h3>
<p>If we reply to an inquiry or enter an engagement, we keep our correspondence, the agreements we sign (including non-disclosure agreements and statements of work), invoicing records, and the data you provide for the engagement.</p>
<h3>Information we do not seek</h3>
<p>We do not ask for, and ask you not to send through the form, payment card details, government identification numbers, health information or other special-category data. Engagement data containing such information is handled only under a written agreement that provides for it.</p>

<h2>How we use it</h2>
<ul class="ticks">
<li>To review inquiries for fit, independence (including conflicts with vendors we measure) and authority, and to reply.</li>
<li>To negotiate, perform and invoice engagements.</li>
<li>To email the weekly changes page to the addresses that asked for it.</li>
<li>To email outcome alerts, and news of new desks and new data, to the addresses that confirmed them.</li>
<li>To send the device notifications and webhook deliveries you turned on.</li>
<li>To keep our websites secure, and to detect and prevent abuse of the inquiry form.</li>
<li>To meet legal, tax and accounting obligations, and to establish or defend legal claims.</li>
</ul>
<p>We do not sell personal information, share it for cross-context behavioural advertising, use it for automated decision-making with legal or similarly significant effects, or use it to train models.</p>

<h2>Legal bases</h2>
<p>Where the GDPR or UK GDPR applies, we rely on our legitimate interests in reviewing inquiries and running our business securely. We also rely on steps taken at your request before entering a contract, and on the performance of that contract. We rely on compliance with legal obligations. Where we ask for it, we rely on your consent, which you may withdraw at any time.</p>

<h2>Who we share it with</h2>
<p>We share personal information only with service providers that process it on our behalf and under their contractual obligations: Cloudflare (delivery of indahl.ai, the storage of the inquiry form, the weekly newsletter list, the alerts list, push subscriptions and webhooks, and email delivery), the push service your browser uses (delivery of the notifications you turn on, encrypted so that it cannot read them), WorkOS (verifying the work identity of people who send an engagement inquiry), GitHub (hosting of heuremen.org), Google Workspace (our email), and Google Fonts (typefaces on one page of heuremen.org). We disclose information when required by law or valid legal process, to protect our rights or the safety of others, or in connection with a merger, acquisition or sale of assets, in which case this notice continues to apply to the information transferred. We never name a client, partner or engagement without written consent.</p>

<h2>International transfers</h2>
<p>We are based in the United States, and our service providers may process information in other countries. Where the law requires it, transfers are made under appropriate safeguards such as the European Commission&rsquo;s standard contractual clauses relied on by those providers.</p>

<h2>How long we keep it</h2>
<ul class="ticks">
<li>Inquiries that do not lead to an engagement, and the copy emailed to us: up to 24 months from receipt, then deleted.</li> <li>Correction or removal requests, and the copy emailed to us: up to 24 months from receipt, then deleted.</li>
<li>Engagement records, agreements and invoices: for the life of the engagement and as long afterwards as contract, tax and legal obligations require.</li>
<li>Engagement data you provide: returned or deleted at the end of the engagement on request, except where we must keep it by law.</li>
<li>Weekly newsletter addresses: until you unsubscribe, then deleted at once.</li>
<li>Sign-ups for alerts or new desks and new data that are not confirmed: two days, then deleted. Confirmed addresses for alerts or new desks and new data: until you unsubscribe, then deleted at once.</li>
<li>The one-way hashes used to limit repeat submissions, sign-ups and registrations: one hour for a network address, and one day for an email address entered for alerts or new desks and new data.</li>
<li>The one-way hash of a subscribed email address that prevents duplicates: until you unsubscribe, then deleted at once.</li>
<li>Push subscriptions for notifications on your device, and the hash that prevents duplicates: until you turn notifications off with the button or the push service tells us the subscription has ended, then deleted at once.</li>
<li>Webhooks, their signing secrets and the hash that prevents duplicates: until you delete the webhook from its manage page, then deleted at once. A webhook that was turned off after failed deliveries is kept, turned off, until you delete it.</li>
<li>The sending logs for notifications and webhooks, which hold no address, key or secret: kept as operational records of what was sent.</li>
<li>Inquiry cookies. A signed cookie records that you accepted the agreements and is kept up to two hours. A cookie that ties a sign-in to your browser is kept up to ten minutes. A signed cookie holds your verified identity while you complete an engagement inquiry and is kept up to 45 minutes. We set no other cookies and no tracking cookies.</li>
</ul>

<h2>How we protect it</h2>
<p>Inquiries are stored in a private storage area accessible only to us. We use the least access an engagement needs, prefer credentials that clients own and can revoke, never write credentials into code or reports, and keep client data separate from our published research. No method of transmission or storage is completely secure, and we will notify affected people and authorities of a breach where the law requires.</p>

<h2>Your rights</h2>
<p>Depending on where you live, you may have the right to know what personal information we hold about you, to receive a copy, to have it corrected or deleted, to restrict or object to its use, and to withdraw consent. California residents have the rights to know, delete and correct, and to non-discrimination for exercising them. We do not sell or share personal information as those terms are defined. We honour Global Privacy Control signals, although we have no sale or sharing to opt out of. To make a request, use the <a href="/correction">correction or removal form</a>, which is open to anyone and needs no agreement and no work email, or the <a href="/contact">inquiry form</a> with &ldquo;Privacy request&rdquo; as the reason. We reply to every privacy request, verify your request against the information we hold and respond within the time the law allows. You may also complain to your local data protection authority.</p>

<h2>Children</h2>
<p>Our websites and services are intended for organisations and are not directed to anyone under 16. We do not knowingly collect information from children.</p>

<h2>Changes to this notice</h2>
<p>We will post any change here with a new effective date. Material changes will be noted at the top of this page.</p>

<h2>Contact</h2>
<p>Heuremen LLC. For any question about this notice, use the <a href="/correction">correction or removal form</a>, or the <a href="/contact">inquiry form</a> with &ldquo;Privacy request&rdquo; as the reason.</p>
</section>''', hero('Legal', 'Privacy', ''))

PAGES['/terms'] = page('/terms', 'Terms of Use and Data Rights | Heuremen LLC', 'Terms of use for the Heuremen LLC websites.',
 f'''
<section class="legal">
<p class="meta">Effective 28 October 2026. Updated 30 October 2026 to state our MLCommons membership.</p>
<h2>Use of this site</h2>
<p>This website is operated by Heuremen LLC. Its content is general information about our services and research. It is not advice for any particular situation, and no engagement exists until both parties sign a statement of work.</p>
<h2>Published research</h2>
<p>Research papers, data and code we publish are released under the licence stated with each release. Our data and code release on Zenodo is licensed CC BY 4.0. Case statements we publish are provided as published, for information. They report measurements taken on the dates and under the calibration records they state. Heuremen is not affiliated with or endorsed by any vendor named.</p>
<h2 id="ai-training">AI training and automated use</h2>
<p>Heuremen LLC reserves all rights in the content and data on indahl.ai, including the QIA, IRIS and OY tables, studies, Lists and data downloads. You may read, download and cite them with attribution. Text and data mining for the purpose of training, fine-tuning or building AI models is not permitted. This is an express reservation of rights. It is also made in machine-readable form in robots.txt, in the tdm-reservation header and the tdmrep.json file, and in the page metadata.</p>
<p>Search indexing, and retrieving a page to answer a user&rsquo;s question with a link to the source, are permitted. Names of authors in the List appear as published in their own papers. To have a name or a study removed, or a figure corrected, use the <a href="/correction">correction or removal form</a>. It is open to anyone and needs no agreement and no work email.</p>
<p>The pages of heuremen.org are reserved in the same way. The only exception is our physics uploads, which may be used with attribution, including for text and data mining and AI training: the paper, the run data and code files under heuremen.org/experiments, and the Zenodo data and code release (published under CC BY 4.0 as stated on its record).</p>
<h2 id="responses">Responses</h2>
<p>Any company, school or author named on a page may add a response to it. A response is a PDF on the sender&rsquo;s own site, linked through the Respond link on the page. It is posted as received, never edited, with its date and the host it came from. When a response disputes a figure we recount that figure from the same files and add one line with the result. A response that is right is a correction, and we publish it as one. Anything that does not fit a PDF can go through the <a href="/contact">inquiry form</a>.</p>
<h2>Accuracy</h2>
<p>We work to keep every figure on this site traceable to its source and correct. The site is provided as is, without warranties of any kind, and Heuremen LLC is not liable for decisions made on the basis of its general content.</p>
<h2>The List</h2>
<p>The List on the QIA pages is a classification of published studies for indexing. It is not an assessment of any study or its authors. Each entry states what was read and when. To have a study removed from the List, use the <a href="/correction">correction or removal form</a>. To add a published study, use the PDF field at the top of the QIA page.</p>
<h2>Inquiries</h2>
<p>An inquiry creates no engagement and no obligation for either party. Anything we provide in reply is for information only until both parties sign a statement of work.</p>
<p>We acknowledge every request to correct or remove an entry, a row or a page within three business days of receiving it.</p>
<h2>Limitation of liability</h2>
<p>To the extent the law allows, Heuremen LLC is not liable for indirect, incidental, special or consequential loss arising from this site, an inquiry or an engagement, and its total liability for any claim is limited to the fees paid to Heuremen LLC for the engagement concerned, or USD 100 where no fees were paid.</p>
<h2>Names and marks</h2>
<p>Heuremen, QIA, IRIS, OY, ATLAS and HERMES are names of Heuremen LLC. Other company and product names are the property of their owners and are used only to identify them. MLPerf&reg; and MLCOMMONS&reg; are trademarks of MLCommons Association. Heuremen LLC is a member of MLCommons, and nothing here is endorsed by MLCommons Association.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of the State of New Jersey, without regard to its conflict-of-laws rules. Any dispute about this website is heard in the state or federal courts located in New Jersey.</p>
<h2>Contact</h2>
<p>Questions about these terms: use the <a href="/contact">inquiry form</a>.</p>
</section>''', hero('Legal', 'Terms', ''))

# 25 Oct 2026 (his word: "FULL transparency, link the actual certification on a breakout page"). The disclaimers on QIA and IRIS link here.
PAGES['/conflict-of-interest'] = page('/conflict-of-interest', 'Conflict of Interest Certification | Heuremen LLC', 'The conflict of interest certification every Heuremen LLC employee signs.',
 '''
<section class="legal">
<p class="meta">Version 26 October 2026</p>
<p>Every employee of Heuremen LLC signs this certification when they join and again each year. Signed copies are kept with the company records.</p>
<h2>I certify that</h2>
<ol>
<li>I have no business interest in quantum computing or in large language models that could pose a conflict of interest with my work at Heuremen LLC. This includes shares, options or other securities in a company in either field, paid advisory or consulting roles, and any agreement to receive payment from such a company.</li>
<li>I have no business interest in any other area of Heuremen LLC&rsquo;s work that could pose a conflict of interest. This includes any company, institution or study listed on Heuremen LLC&rsquo;s websites.</li>
<li>I will not buy or sell securities of any company named in Heuremen LLC&rsquo;s published work.</li>
<li>If any of this changes, I will tell Heuremen LLC in writing within 10 days, before doing further work on the affected matter.</li>
</ol>
<h2>Interests disclosed</h2>
<p>Each signer lists any interest they disclose, or writes &ldquo;None&rdquo;.</p>
</section>''', hero('Legal', 'Conflict of Interest Certification', ''))

# 29 Oct 2026 (his word): the current release leads with the QIA gate-error result; the 26 Oct release is kept at /media/2026-10-26.
PAGES['/media'] = page('/media', 'IBM processors delivered more gate error than IBM states in every run we made on 23 and 24 October | Media | Heuremen LLC', 'Every gate-error run Heuremen LLC made on IBM quantum processors on 23 and 24 October measured above the figures IBM publishes.',
 '''
<section class="legal">
<p class="meta">For release: 29 October 2026</p>
<p>Heuremen LLC reported today that every gate-error run it made on IBM quantum processors on 23 and 24 October measured above the figures IBM publishes for them.</p>
<p>Single-qubit gate error ran 1.17 to 1.93 times the stated figure. Two-qubit (CZ) gate error ran 1.18 to 1.62 times. The 95 percent interval on each of the 16 runs, on seven processors, excludes 1.0. Each figure is a median over qubits or edges, and in every run 8 to 34 percent of them did better than stated. Eleven of the 16 runs share an IBM record with another run and were fired 4 to 111 minutes apart, so they are repeats inside one calibration, not 16 separate calibrations.</p>
<p class="meta">Corrected 10 November 2026: this release first said 14 runs. Two ibm_kingston runs of 24 October, made with the same design, had been left out. Both measured above, and the ranges did not change.</p>
<p>The same audit, QIA (Quantum Idle Audit), found two more things in IBM&rsquo;s published calibration records:</p>
<ul>
<li>A T1 value on ibm_marrakesh dated 895 hours before the record that carried it, and a T2 value on ibm_kingston dated 2,332 hours before its record.</li>
<li>4,204 of 4,204 T1 and T2 entries unchanged under a new &ldquo;last calibration&rdquo; stamp, across 14 record pairs from 16 September to 23 October.</li>
</ul>
<p>QIA has indexed 1,523 published quantum studies and recounted 196 of them against their own data. Each has its own page and a receipt.</p>
<p>The reports, data and code are at <a href="/qia">indahl.ai/qia</a> and on <a href="https://github.com/Heuremen-LLC/indahl.ai">GitHub</a> under Heuremen-LLC. Each plan was committed before the data it describes.</p>
<p class="sign"><b>Heuremen LLC</b><br>&ldquo;We found it.&rdquo;</p>
<p class="meta">Earlier release: <a href="/media/2026-10-26">26 October 2026</a></p>
</section>''', hero('', 'IBM processors delivered more gate error than IBM states in every run we made on 23 and 24 October', ''))
PAGES['/media/2026-10-26'] = page('/media/2026-10-26', 'Heuremen LLC publishes its first research and data | Media | Heuremen LLC', 'Heuremen LLC publishes its first research and data. Release of 26 October 2026.',
 '''<section class="legal">
<p class="meta">For release: 26 October 2026. Earlier release. The current release is at <a href="/media">indahl.ai/media</a>.</p>
<p>Heuremen LLC, a research company, published a paper and its data on heuremen.org today, and data tables on indahl.ai.</p>
<p><a href="https://heuremen.org/a-readout-is-not-an-idle.pdf"><i>A Readout Is Not an Idle</i></a> measures what reading out some qubits does to the qubits left untouched, on IBM 156-qubit processors, with every run, calibration record and analysis released.</p>
<p><a href="/oy"><i>Recount Matrix: Learning Research</i></a> lists what United States colleges and universities have published about measuring their own policies on AI in teaching and learning, with a source for every row. As of 25 October 2026, of 148 institutions listed:</p>
<ul>
<li>0 had published a measured learning outcome of their own AI policy.</li>
<li>3 had measured their own policy or an institution-wide tool.</li>
<li>8 cited a chatbot as the source in their own AI documents.</li>
</ul>
<p>Any institution may add a PDF to its row from the table.</p>
<p>Papers, data and code: <a href="https://heuremen.org/">heuremen.org</a> &middot; Recount Matrix: Learning Research: <a href="/oy">indahl.ai/oy</a> &middot; Inquiries: <a href="/contact">indahl.ai/contact</a></p>
<h2>About Heuremen LLC</h2>
<p>Heuremen LLC measures published claims against the data behind them. Its divisions publish on heuremen.org and indahl.ai.</p>
</section>''', hero('', 'Heuremen LLC publishes its first research and data', ''))

# 29 Oct 2026 (his word): a community page. Membership we hold and the groups around the data we index. References, not endorsements.
PAGES['/community'] = page('/community', 'Community: Groups Around the Data We Index | Heuremen LLC', 'Membership Heuremen LLC holds and the communities around the data it indexes. Listed for reference, not endorsement.',
 '''
<section class="legal">
<p>Heuremen LLC is a member of <a href="https://mlcommons.org">MLCommons</a>.</p>
<p>Below are the communities around the data we index, grouped by the division that reads them. They are listed for reference and are not endorsements. Each group publishes and decides its own work.</p>
<h2>QIA: quantum hardware</h2>
<ul>
<li><a href="https://github.com/Qiskit">Qiskit</a>. The open-source software IBM processors are programmed with, and the community around the circuits QIA runs.</li>
<li><a href="https://arxiv.org/list/quant-ph/recent">arXiv quant-ph</a>. Where most of the quantum studies QIA indexes are posted.</li>
<li><a href="https://zenodo.org">Zenodo</a>. Where our data and code releases are archived, each with its own DOI.</li>
</ul>
<h2>IRIS: language models</h2>
<ul>
<li><a href="https://mlcommons.org">MLCommons</a>. Publishes the AILuminate safety results and the MLPerf results our desks read.</li>
<li><a href="https://huggingface.co">Hugging Face</a>. Hosts the model weights, licenses and file sizes the WEIGHTS, HFLICENSE and HFSIZE desks read.</li>
<li><a href="https://openrouter.ai">OpenRouter</a>. Publishes the host and endpoint data behind the HOSTS desk.</li>
<li><a href="https://arxiv.org/list/cs.CL/recent">arXiv cs.CL</a>. Where most of the language-model studies IRIS indexes are posted.</li>
<li><a href="https://pypi.org">PyPI</a>. The package index the PKGINSTALL and PKGLICENSE desks read.</li>
</ul>
<h2>HERMES: public claims</h2>
<ul>
<li><a href="https://www.measurementlab.net">Measurement Lab</a>. Open internet measurement data and the community around it.</li>
<li><a href="https://clinicaltrials.gov">ClinicalTrials.gov</a>. The registry the TRIALS desk reads.</li>
<li><a href="https://www.transtats.bts.gov">Bureau of Transportation Statistics</a>. The flight data behind the AIRLINE desk.</li>
<li><a href="https://aqs.epa.gov">EPA Air Quality System</a> and <a href="https://www2.purpleair.com">PurpleAir</a>. The two air-quality networks the AIRQ desk compares.</li>
</ul>
<h2>ATLAS: infrastructure</h2>
<ul>
<li><a href="https://www.openstreetmap.org">OpenStreetMap</a>. The mapped data centers on the ATLAS map.</li>
<li><a href="https://epoch.ai">Epoch AI</a>. Research and data on AI data centers.</li>
<li><a href="https://www.eia.gov">U.S. Energy Information Administration</a>. The electricity, plant and carbon figures on the ATLAS pages.</li>
<li><a href="https://www.ntppool.org">NTP Pool</a>. The public time servers behind the TIME desk.</li>
</ul>
<h2>Our own</h2>
<ul>
<li><a href="https://github.com/Heuremen-LLC/indahl.ai">Heuremen-LLC on GitHub</a>. Code, plans and data for every desk.</li>
<li><a href="https://huggingface.co/indahl">indahl on Hugging Face</a>. The datasets behind the QIA, IRIS, OY, ATLAS and MODEL pages, the run data and the YO model.</li>
</ul>
</section>''', hero('', 'Community', ''))

# 29 Oct 2026 (his word): a Changes page built from the public ROADMAP, so it grows with every release. The repository history is two days old, so items carry no dates.
def _changes_html():
    import subprocess, re as _rr
    rm = os.path.join(HERE, '..', 'public_mirror', 'indahl.ai', 'ROADMAP.md'); repo = os.path.dirname(rm)
    if not os.path.exists(rm): return ''
    GH = 'https://github.com/Heuremen-LLC/indahl.ai/tree/main/'
    def md(t):
        t = html.escape(t, quote=False)
        t = _rr.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2">\1</a>', t)
        t = _rr.sub(r'\[([^\]]+)\]\((?!http)([^)\s]+)\)', lambda m: '<a href="' + GH + m.group(2) + '">' + m.group(1) + '</a>', t)
        return _rr.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    done, todo = [], []
    for ln in open(rm, encoding='utf-8'):
        m = _rr.match(r'- \[(x| )\] (.*)', ln.strip())
        if not m: continue
        title = _rr.search(r'\*\*([^*]+)\*\*', m.group(2)); key = title.group(1) if title else m.group(2)[:30]
        d = ''
        (done if m.group(1) == 'x' else todo).append((d, md(m.group(2))))
    out = '<section class="legal"><p>What Heuremen LLC has built and shipped. Every item has its live page and its plan, and a new desk is added automatically when its page goes live.</p><h2>Shipped</h2><ul>'
    out += ''.join(f'<li>{("<b>" + d + "</b>. ") if d else ""}{t}</li>' for d, t in done)
    out += '</ul><p class="meta">Release notes: <a href="/media">indahl.ai/media</a> &middot; Source: <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/ROADMAP.md">ROADMAP.md</a></p></section>'
    return out
PAGES['/changes'] = page('/changes', 'Changes: Desks and Data Releases Shipped | Heuremen LLC', 'Every desk and data release Heuremen LLC has shipped, each with its live page and plan.',
 _changes_html(), hero('', 'Changes', ''))

# 29 Oct 2026 (his word): VAULT. Receipts and sealed files with no file stored (a hash and a time are kept). All of it runs in the visitor's browser. Plan: tape_index/PLAN.md Addendum 1.
PAGES['/vault'] = page('/vault', 'VAULT | Receipts and Sealed Files, No File Stored | Heuremen LLC', 'Hash a file in your browser for a receipt on the public tape, or seal it until a date with drand. The file never leaves your computer and we cannot read, find or release it.',
 '''
<section class="legal vault">
<p>Your file never leaves your computer. Your browser hashes it, seals it or opens it, and the only thing ever sent to us is a 64-character hash, and only when you press a receipt button. We keep the hash and the time. We do not keep, scan, host or release any file.</p>
<h2>Get a receipt</h2>
<p>A receipt proves that a file with this hash existed by this time. It joins the <a href="/tape">tape</a> within the hour. It does not show who made the file or that it is true.</p>
<p><input type="file" id="v-file" aria-label="File to hash"> <button class="btn" id="v-commit" type="button" disabled>Get receipt</button></p>
<p class="hashline" id="v-hash"></p><p class="bench-note" id="v-receipt"></p>
<h3>Check a receipt</h3>
<p><input type="text" id="v-lookup" size="66" maxlength="64" placeholder="64-character hash" aria-label="Hash to look up"> <button class="btn ghost" id="v-check" type="button">Check</button></p><p class="bench-note" id="v-found"></p>
<h2>Seal a file until a date</h2>
<p>Your browser encrypts the file to a future round of <a href="https://drand.love">drand</a>, the public randomness beacon run by independent organizations. The key for that round does not exist until drand publishes the round, so nobody can open the file before then. Not you, not us, not drand. After it, anyone holding the sealed file can open it. The sealed file is saved to your computer. Keep the original, because a lost sealed file cannot be recovered.</p>
<p><input type="file" id="s-file" aria-label="File to seal"> <label>Opens at <input type="datetime-local" id="s-when"></label> <button class="btn" id="s-go" type="button">Seal</button></p>
<p class="bench-note" id="s-out"></p>
<p><input type="hidden" id="s-hash"><button class="btn ghost" id="s-commit" type="button" disabled>Get a receipt for the sealed file</button></p><p class="bench-note" id="s-receipt"></p>
<h2>Open a sealed file</h2>
<p><input type="file" id="o-file" aria-label="Sealed file"> <button class="btn" id="o-go" type="button">Open</button></p><p class="bench-note" id="o-out"></p>
<h2>What this does and does not do</h2>
<p>We never receive the file, the sealed file or a key. We cannot scan, host, find or release your file, and nothing here can be used to take it back. If you share a sealed file, you are the one sharing it. Do not seal material that is illegal to hold or share. We cannot see it, and the law applies to you and to anyone you pass it to.</p>
<p>We store the hash and the time of each receipt. We do not store your network address, and our network provider keeps its own logs. Release times come from drand, so they do not depend on us. If drand ever stopped publishing, a file sealed to a later round could not be opened. Files over 60 MB are refused.</p>
<p class="meta">The code that runs here is in <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/tape">the repository</a>. Sealing uses <a href="https://github.com/drand/tlock-js">tlock-js</a> (<a href="https://www.npmjs.com/package/tlock-js">npm</a>), bundled into one file served from this site.</p>
</section><script src="/vault/tlock.js" defer></script><script src="/vault/app.js" defer></script>''', hero('', 'VAULT &middot; Receipts and Sealed Files', ''))

PAGES['/security'] = page('/security', 'Security and Vulnerability Reporting | Heuremen LLC', 'How to report a security issue to Heuremen LLC, and how we handle client access and data.',
 f'''
<section class="legal">
<h2>Our data</h2>
<p>Our internal records are confidential client information and a private book of work we have not published. Every index entry and calibration we do publish appears on this website exactly as we store it.</p>
<h2>Reporting an issue</h2>
<p>If you believe you have found a security issue in this site or in materials we publish, use the <a href="/contact">inquiry form</a> and choose &ldquo;Security report&rdquo; as the reason. Please give us reasonable time to fix it before disclosing it, and do not access data that is not yours. We reply to every security report, acknowledge it and keep you informed.</p>
<h2>Client access and data</h2>
<ul class="ticks">
<li>We use the minimum access an engagement needs, preferably accounts and credentials that you own and can revoke.</li>
<li>Credentials are never written into code, reports or published materials.</li>
<li>Client data is kept separate from our published research and is returned or deleted on request when the engagement ends.</li>
</ul>
</section>''', hero('Legal', 'Security', ''))

PAGES['/inquire-ok'] = page('/inquire-ok', 'Inquiry received | Heuremen LLC', 'Inquiry received.', '<section class="closing"><h2>Inquiry received.</h2><p>We review every inquiry for fit, independence and authority. If we are able to take it on, we will reply to the organisation email address you gave.</p><p class="actions"><a class="btn" href="/">Home</a></p></section>')
PAGES['/inquire-error'] = page('/inquire-error', 'Inquiry not sent | Heuremen LLC', 'Inquiry not sent.', '<section class="closing"><h2>Inquiry not sent.</h2><p>__MSG__</p><p class="actions"><a class="btn" href="/contact">Back to the form</a></p><p>To keep what you typed, use your browser&rsquo;s Back button instead.</p></section>')
PAGES['/404'] = page('/404', 'Not found | Heuremen LLC', 'Page not found.', '<section class="closing"><h2>That page does not exist.</h2><p>Try the home page, or use the inquiry form.</p><p class="actions"><a class="btn" href="/">Home</a></p></section>')

# The /agree privacy box carries the live privacy notice body (one source; h2 -> h3 inside the box).
_pm = _re.search(r'<section class="legal">(.*?)</section>', PAGES['/privacy'], _re.S)
for _k in ('/agree', '/contact'): PAGES[_k] = PAGES[_k].replace('__PRIVACY__', _pm.group(1).replace('<h2>', '<h3>').replace('</h2>', '</h3>'))

CSS = open(os.path.join(HERE, 'fonts.css')).read() + r''':root{--paper:#f7f0e0;--paper2:#efe5cf;--ink:#1a1208;--deep:#2a1f0e;--mid:#5a4830;--rule:#c8902a;--goldink:#806012;--cave:#1a1408;--lit:#c9a84c;--w:1120px}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--deep);font:400 16px/1.55 Lora,Georgia,serif}
a{color:var(--goldink);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{color:var(--ink)}
.wrap{max-width:var(--w);margin:0 auto;padding:0 24px}
h1,h2,h3{font-family:"Abril Fatface",Georgia,serif;font-weight:400;color:var(--ink);line-height:1.15;margin:0 0 .5em}
h1{font-size:clamp(28px,4vw,44px);letter-spacing:-.01em}h2{font-size:clamp(19px,2vw,24px)}h3{font-size:17px}
.label,.kicker,.links a,.cta,.btn,.ghost,.more{font-family:Cinzel,Georgia,serif;font-weight:600;letter-spacing:.16em;text-transform:uppercase;font-size:12px}
.top{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--rule)}
.bar{display:flex;align-items:center;gap:28px;height:58px}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);font:400 23px/1 "Abril Fatface",Georgia,serif}
.mark{width:34px;height:34px;fill:none;stroke:var(--ink);stroke-width:8;stroke-linejoin:round}.mark circle{fill:var(--ink);stroke:none}
.links{display:flex;gap:28px;margin-left:auto}.links a{color:var(--mid);text-decoration:none;padding:6px 0;border-bottom:2px solid transparent}
.links a:hover,.links a[aria-current]{color:var(--ink);border-bottom-color:var(--rule)}
.cta,.btn{display:inline-block;background:var(--ink);color:var(--paper);text-decoration:none;padding:9px 16px;border-radius:2px}
.cta:hover,.btn:hover{background:var(--goldink);color:var(--paper)}
.ghost{display:inline-block;color:var(--ink);text-decoration:none;padding:12px 21px;border:1px solid var(--ink);border-radius:2px;margin-left:12px}.ghost:hover{background:var(--ink);color:var(--paper)}
.more{display:inline-block;color:var(--goldink);text-decoration:none;margin-top:8px}.more:after{content:" \2192"}
.hero{background:var(--cave);color:#efe5cf;padding:56px 0 48px;border-bottom:3px solid var(--lit)}
.hero h1{color:#f7f0e0;max-width:16ch}.hero .kicker{color:var(--lit);margin:0 0 20px}.hero .sub{font-size:17px;max-width:58ch;color:#e6dbc2;margin:0}
.hero .actions{margin:36px 0 0}.hero .btn{background:var(--lit);color:var(--cave)}.hero .btn:hover{background:#f3e2a0}
.hero .ghost{color:#f7f0e0;border-color:#f7f0e0}.hero .ghost:hover{background:#f7f0e0;color:var(--cave)}
main section{padding:36px 0;border-bottom:1px solid #dccfb0}main section:first-child{padding-top:20px}main section:last-child{border-bottom:0}
.branches{display:grid;grid-template-columns:repeat(3,1fr);gap:32px}
.card{background:#fffaf0;border:1px solid #dccfb0;border-top:4px solid var(--rule);padding:26px}
.card .label{color:var(--goldink);margin:0 0 14px}
.ticks{list-style:none;padding:0;margin:0}.ticks li{padding:10px 0 10px 28px;position:relative;border-bottom:1px solid #e6dac0}.ticks li:last-child{border-bottom:0}
.ticks li:before{content:"";position:absolute;left:0;top:21px;width:12px;height:2px;background:var(--rule)}
.band{background:var(--paper2);margin:0 calc(50% - 50vw);padding-left:calc(50vw - 50%)!important;padding-right:calc(50vw - 50%)!important}
.steps{list-style:none;counter-reset:s;padding:0;margin:8px 0 24px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:28px}
.steps li{counter-increment:s;border-top:2px solid var(--ink);padding-top:16px}.steps li:before{content:counter(s,decimal-leading-zero);display:block;font:400 30px/1 "Abril Fatface",Georgia,serif;color:var(--goldink);margin-bottom:10px}
.steps b{display:block;font-family:Cinzel,Georgia,serif;letter-spacing:.14em;text-transform:uppercase;font-size:15px;color:var(--ink);margin-bottom:6px}.steps span{color:var(--mid)}
.split{display:grid;grid-template-columns:1fr 1.4fr;gap:56px;align-items:start}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:36px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:36px}
.grid3>div,.grid2>div{border-top:2px solid var(--rule);padding-top:18px}
.proof{display:grid;grid-template-columns:1fr 1.2fr;gap:56px}.proof .label{color:var(--goldink)}
.list{list-style:none;padding:0;margin:0}.list li{padding:16px 0;border-bottom:1px solid #dccfb0}.list a{font-weight:600}.list span{display:block;color:var(--mid);font-size:16px}
.closing{text-align:center}.closing p{max-width:52ch;margin:0 auto 26px;color:var(--mid)}
.principal{font:400 clamp(44px,7vw,72px)/1 "Abril Fatface",Georgia,serif;letter-spacing:.06em;color:var(--ink);margin:0}
.notice{border-left:3px solid var(--rule);padding:4px 0 4px 18px;color:var(--ink);margin:0 0 28px}
.form-wrap{max-width:820px}.inq{display:grid;gap:18px}.inq .row{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.inq label{display:grid;gap:6px;font-size:16px;color:var(--ink)}.inq input,.inq select,.inq textarea{font:400 17px/1.4 Lora,Georgia,serif;color:var(--ink);background:#fffaf0;border:1px solid #c9b994;border-radius:2px;padding:11px 12px}
.inq input:focus,.inq select:focus,.inq textarea:focus{outline:2px solid var(--rule);outline-offset:1px}.inq .check{display:flex;gap:12px;align-items:flex-start;font-size:16px}
.inq .check input{margin-top:5px}.inq button{justify-self:start;border:0;cursor:pointer}.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
@media (max-width:860px){.inq .row{grid-template-columns:1fr}}
.branches.two{grid-template-columns:1fr 1fr}.story{max-width:62ch;margin:0 auto;font-size:17px;line-height:1.7}.story .who{font-family:Cinzel,serif;letter-spacing:.12em;font-size:14px;color:var(--mid);margin-bottom:0}.story hr{border:0;border-top:1px solid #dccfb0;margin:2em 0}.story h3{font-size:24px;margin-top:1.6em}
#mob{width:100%;min-height:320px;border:1px solid #dccfb0}#mob canvas{display:block;cursor:grab}#die{width:100%;min-height:320px;background:#f7f0e0;border:1px solid #dccfb0}#die canvas{display:block;cursor:grab}.die-controls{display:flex;flex-wrap:wrap;gap:24px;align-items:center;margin:20px 0}.die-controls input{vertical-align:middle;margin-left:8px}.die-controls{gap:14px}#die-result{white-space:pre-wrap;min-height:4.5em;font-family:Lora,Georgia,serif;font-size:17px}
#wave{display:block;margin:8px 0;max-width:100%}
.riddles{max-width:62ch}.riddle{border-bottom:1px solid #dccfb0;padding:18px 0}.riddle summary{cursor:pointer;font-size:18px;line-height:1.5;list-style:none}.riddle summary::-webkit-details-marker{display:none}.riddle summary::before{content:'?';display:inline-block;width:1.6em;color:var(--rule);font-weight:700}.riddle[open] summary::before{content:'!'}.riddle p{margin:12px 0 0 1.6em;font-size:19px}
#waves-line,#waves-pond{display:block;margin:8px 0;max-width:100%}#waves-pond{cursor:crosshair}.toks{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}.tok{font-family:ui-monospace,Menlo,monospace;font-size:17px;padding:4px 8px;border-radius:4px;color:#1a1208}.tok-in{width:100%;font-size:20px;padding:10px;border:1px solid #c9b98f;background:#fffaf0;font-family:Lora,Georgia,serif}
.coin{width:150px;height:150px;border-radius:50%;border:6px solid #c8902a;background:#f3e6c4;font:700 64px Georgia,serif;color:#24201a;cursor:pointer;margin:16px 0;display:block}.coin.heads{background:#e6b422}.coin.tails{background:#d8c9a3}.coin.flip{transform:rotateY(90deg)}.coin.heads,.coin.tails{transition:transform .25s}.btn.on{outline:3px solid #c8902a}.bet-row{font:700 28px ui-monospace,Menlo,monospace;letter-spacing:.2em}
.plane{width:100%;height:auto;border:1px solid #dccfb0;background:#fffdf6;margin:12px 0}.steps-list{padding-left:1.4em;line-height:1.6}
#tesla,#tb{display:block;margin:8px 0;max-width:100%}.tape{display:flex;gap:4px;margin:16px 0;flex-wrap:wrap}.cell{width:44px;height:52px;border:2px solid #24201a;display:flex;align-items:center;justify-content:center;font:700 26px ui-monospace,Menlo,monospace;background:#fffaf0}.cell.head{background:#e6b422;outline:3px solid #c43c2a}.tm-num{width:5em;font-size:18px;padding:6px}
.flower{width:100%;max-width:420px;height:auto;display:block;margin:0 0 20px}.quote{font-style:italic;font-size:17px;line-height:1.6}.by{margin-top:-4px;font-family:Cinzel,serif;letter-spacing:.08em}
.legal{max-width:72ch}.legal-box{max-height:360px;overflow-y:auto;border:1px solid #c8902a;background:#fffdf6;padding:8px 20px;margin:8px 0 12px;font-size:16px;line-height:1.55}.legal-box h3{font-size:18px;margin:1em 0 .3em}.check.locked{opacity:.45}.legal h2{font-size:26px;margin-top:1.4em}.meta{color:var(--mid);font-style:italic}.big{font-size:24px}
.foot{background:var(--cave);color:#d8ccb0;margin-top:0;padding:64px 0 40px;border-top:3px solid var(--lit)}
.foot .cols{display:grid;grid-template-columns:repeat(3,1fr);gap:32px}.foot a{display:block;color:#efe5cf;text-decoration:none;padding:3px 0;font-size:14px}.foot a:hover{color:var(--lit)}
.foot .label{color:var(--lit);margin:0 0 12px}.sign{margin-top:48px;padding-top:24px;border-top:1px solid #4a3d24}.sign p{margin:0;color:#d8ccb0;font-size:15px}
@media (max-width:860px){.bar{height:auto;padding-top:10px;padding-bottom:2px;gap:8px 18px}.nav,header .wrap{flex-wrap:wrap}.links{flex-wrap:wrap;gap:6px 18px;width:100%;margin:4px 0 10px;order:5}.ddpanel{display:none!important}.cta{margin-left:auto}.branches,.split,.grid3,.grid2,.proof,.foot .cols{grid-template-columns:1fr}.hero{padding:72px 0 64px}main section{padding:56px 0}.card{padding:28px}.ghost{margin:12px 0 0}}
'''

# 25 Oct 2026 (his word): the kids pages are HELD (no kids looking yet); OY = Recount Matrix: Learning Research, consistent with the
# other divisions. Held pages are defined in held_kids.py (house only, 9 Nov) and kept in HELD_KIDS, so restoring them is one line.
HELD_KIDS = {k: PAGES.pop(k) for k in [p for p in list(PAGES) if p == '/oy' or p.startswith('/oy/')]}
OY_TOP = IRIS_TOP.replace('value="iris"', 'value="oy"').replace('Submit a published study or model review for indexing', 'Submit a published study or school AI document for indexing')
_OY_BODY = open(os.path.join(HERE, '..', 'oy_index', 'matrix_page', 'oy_body.html'), encoding='utf-8').read()
_OYHL = _jsonld.load(open(os.path.join(HERE, '..', 'oy_index', 'matrix_page', 'oy_headline.json'), encoding='utf-8'))   # 10 Nov 2026: built with oy_body.html by build_matrix_page.py
_OYSLOT = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">' + html.escape(_OYHL['big']) + '</div><p class="hl-line">' + html.escape(_OYHL['line']) + '</p></section>'
# 27 Oct 2026 (his word): every small private liberal arts college gets a page. Data: oy_index/schools.json (build_schools.py). Script reads, not hand verdicts.
import json as _oj, html as _oh
_SCH = _oj.load(open(os.path.join(HERE, '..', 'oy_index', 'schools.json'), encoding='utf-8'))
def _e(x): return _oh.escape(str(x))
def _readtxt(s):
    # 30 Oct 2026 site pass (F-11, F-12, G-9): pages read of pages found, failed reads, and a site that turned the script away is not "not reached"
    if s['site_read'] == 'yes':
        n = s['pages_fetched'] or 0; f = s.get('pages_failed') or 0; u = s.get('ai_urls') or 0
        t = f"Read by script: {n} page{'s' if n != 1 else ''}"
        if u > n + f: t += f" of {u} found (the script reads at most 25)"
        if f: t += f", {f} more could not be read"
        return t
    if s['site_read'] == 'reached': return 'Reached, no AI page found by script'
    if s['site_read'] == 'not reached':
        a = s.get('answers_now')
        if a and a != '200': return f'The site turned the script away (it answers HTTP {a})'
        if a == '200': return 'Not reached by script on the read date. The site answers now'
        return 'Site not reached by script'
    return 'Not yet read'
def _oydrop(d, pre):
    d = {k[len(pre):]: v for k, v in (d or {}).items() if k.startswith(pre)}
    return ('Rows our filters removed: ' + ', '.join(f'{v} {k}' for k, v in sorted(d.items())) + '. ') if d else ''
_NAMEN = {}
for _s in _SCH: _NAMEN[_s['school']] = _NAMEN.get(_s['school'], 0) + 1
_rows = []
for _s in _SCH:
    _pp = '/oy/school/' + _s['unitid']
    _nm = _s['school'] + (f" ({_s['state']})" if _NAMEN[_s['school']] > 1 else '')   # F-16: same name, different school
    _lines = []
    if _s['sentences']:
        _sh, _st = len(_s['sentences']), _s['sentences_total']
        _lines.append('<h2>Sentences on the school&rsquo;s own pages</h2><p class="meta">Found by script where one sentence names AI and also contains a digit and a word such as study, survey, pilot, section or percent. Many are not about teaching and learning. Not read in full. ' +
                      (f'Showing {_sh} of {_st}. ' if _st > _sh else '') + _e(_oydrop(_s.get('dropped'), 'sentence: ')) + '</p><ul>' +
                      ''.join(f'<li>{"&hellip;" if h.get("cut_start") else ""}{_e(h["sentence"])}{"&hellip;" if h.get("cut_end") else ""} <a href="{_e(h["url"])}">Source</a></li>' for h in _s['sentences']) + '</ul>')
    else:
        _f = _s.get('pages_failed') or 0
        _lines.append('<h2>Sentences on the school&rsquo;s own pages</h2><p>' + (('None found by the script in the pages it read.' + (f' {_f} page{"s" if _f != 1 else ""} could not be read, so this is not a full read.' if _f else '') + (' ' + _e(_oydrop(_s.get('dropped'), 'sentence: ')) if _s.get('dropped') else '')) if _s['site_read'] == 'yes' else ({'reached': 'The script reached the site and found no page about AI through the sitemap or common paths. Not read in full.', 'not reached': _readtxt(_s) + '.'}.get(_s['site_read'], 'Not yet read.'))) + '</p>')
    if _s['courses']:
        _sh, _st = len(_s['courses']), _s['courses_total']
        _lines.append('<h2>Course titles in the public catalog</h2><p class="meta">Titles that name AI, machine learning, data science, technology and society, digital humanities, philosophy of mind or related topics. Found by script, not read in full. ' +
                      (f'Showing {_sh} of {_st}. ' if _st > _sh else '') + _e(_oydrop(_s.get('dropped'), 'course: ')) + '</p><ul>' +
                      ''.join(f'<li>{_e(h["line"])}{(" (" + _e(h["year"]) + " catalog)") if h.get("year") else ""} <a href="{_e(h["url"])}">Source</a></li>' for h in _s['courses']) + '</ul>')
    else:
        _lines.append('<h2>Course titles in the public catalog</h2><p>' + {'readable': 'None matched in the catalog pages the script read.', 'not readable by script': 'The script could not read course lists on this site.', 'pending': 'Not yet read.'}[_s['catalog']] + '</p>')
    if _s.get('hand'):
        _lines.insert(0, (f'<h2>Read in a browser</h2><p>Page type: <b>{_e(_s["hand"]["label"])}.</b> {_e(_s["hand"]["note"])} Read {_e(_s["hand"]["read_on"])}. The script read below found no page about AI, so we opened the school&rsquo;s AI pages in an ordinary browser.</p>') if _s['hand'].get('how') == 'browser' else
                         f'<h2>Read in full</h2><p>Page type: <b>{_e(_s["hand"]["label"])}.</b> {_e(_s["hand"]["note"])} Read 28 October 2026.</p>')   # 10 Nov 2026 browser re-read (oy_index/raw_browser_20261110/)
    _ipn = (f" Listed in the federal directory as {_e(_s['ipeds_name'])}." if _s.get('ipeds_name') and _s['ipeds_name'] != _s['school'] and not _s.get('name_note') else '')
    _nn = (' ' + _e(_s['name_note'])) if _s.get('name_note') else ''
    _shr = (' This school shares its website with ' + _e(', '.join(_s['shared_with'])) + ', so the read below covers the shared site.') if _s.get('shared_with') else ''
    _lk = _s.get('site_link') or ('https://' + _s['domain'])
    _body = (f'<section class="legal"><p class="meta">{_e(_s["carnegie"])} &middot; {_e(_s["state"])} &middot; <a href="/oy">All schools</a></p>'
             f'<h2>School</h2><p>{_e(_s["school"])}. Private nonprofit.{_ipn}{_nn} Site: <a href="{_e(_lk)}">{_e(_lk.split("//", 1)[1])}</a>. Federal ID <a href="https://nces.ed.gov/collegenavigator/?id={_e(_s["unitid"])}">{_e(_s["unitid"])}</a>. Class from the 2021 Carnegie classification in the federal IPEDS directory.{_shr}</p>'
             f'<h2>Site</h2><p>{_readtxt(_s)}.</p>' + ''.join(_lines) +
             f'<p class="meta">Pages read by script on {_e(_s.get("read_on") or "the read date")}. The data and the scripts are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/oy">code/oy on GitHub</a>. Not an assessment of the school or its people. To correct or remove this page, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
    _d = (f"{_s['school']}, {_s['state']}: sentences that name AI on its public pages and AI-related course titles, as found by script." if (_s['site_read'] == 'yes' or _s['courses'])
          else f"{_s['school']}, {_s['state']}: what our script could and could not read on its public site.")
    PAGES[_pp] = page(_pp, f"{_nm} | OY | Heuremen LLC", _d, _body, hero_slim(_e(_nm)))
    _FEED.append((_pp, f"{_nm} (OY)", _d))
    _rows.append(f'<tr><td><a href="{_pp}">{_e(_nm)}</a></td><td>{_e(_s["state"])}</td><td>{_readtxt(_s)}</td><td>{_s["sentences_total"] if _s["site_read"] == "yes" else "&mdash;"}</td><td>{_s["courses_total"] if _s["catalog"] == "readable" else "&mdash;"}</td><td>{_e(_s["hand"]["label"]) if _s.get("hand") else "&mdash;"}</td></tr>')
_OY_SCH = ('<section><h2>Private baccalaureate colleges</h2><p>Private nonprofit baccalaureate colleges from the federal directory, one page each. The directory puts them in two Carnegie 2021 classes, Arts and Sciences focus and Diverse fields, and the pages cover both. The script reads each school&rsquo;s own public pages for sentences that name AI with a number or a study word, and its public catalog for course titles on AI, technology and society, and related topics. These are script reads, not recounts. The last column marks the schools whose pages we also read ourselves, in full on 28 October 2026 or in a browser on 10 November 2026. We read in a browser the 89 schools where the script reached the site but found no page about AI. Of those 89, 48 have an AI policy or guidance page, and none states a measured outcome of its own AI policy, guidance, tool or pilot.</p>'
           '<div class="scroll"><table class="mtx"><thead><tr><th>School</th><th>State</th><th>Site</th><th>Sentences</th><th>Course titles</th><th>Read by us</th></tr></thead><tbody>' + ''.join(_rows) + '</tbody></table></div></section>')
print('oy school pages', len(_SCH))

# 27 Oct 2026 (his word): ATLAS, fourth division. First page: US data center map. Data: atlas/datacenters.json, atlas/map.svg, atlas/summary.json (build_atlas.py).
_AS = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'summary.json'))); _AD = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'datacenters.json')))
# 30 Oct 2026 (his "can atlas be one map with different data overlays"): ONE map with switchable layers and the cost-to-scale text and tables, all built by atlas/build_atlasmap.py. atlas/map.svg is the old single-layer map and is no longer printed.
_AMF = open(os.path.join(HERE, '..', 'atlas', 'atlasmap_fragment.html'), encoding='utf-8').read(); _SCL = open(os.path.join(HERE, '..', 'atlas', 'scale_lead.html'), encoding='utf-8').read(); _SCB = open(os.path.join(HERE, '..', 'atlas', 'scale_body.html'), encoding='utf-8').read()
CSS += open(os.path.join(HERE, '..', 'atlas', 'atlasmap.css'), encoding='utf-8').read()
_erows = ''.join(f'<tr><td>{_e(r["name"])}</td><td>{_e(r["operator"])}</td><td>{(f"{r[chr(109)+chr(119)]:,.0f}" if r["mw"] else "&mdash;")}</td><td>{(f"{r[chr(104)+chr(49)+chr(48)+chr(48)+chr(101)]:,.0f}" if r["h100e"] else "&mdash;")}</td><td>{("Placed" if r["lat"] is not None else "No usable address")}</td></tr>'
                 for r in sorted(_AD['epoch'], key=lambda r: -(r['mw'] or 0)))
_ABODY = ('<section class="legal"><p class="meta"><a href="/atlas">ATLAS</a> &middot; Built Infrastructure</p>'
 '<h2>Cost to scale</h2>' + _SCL + _AMF + _SCB +
 '<h2>Data centers in the United States</h2>'
 f'<p>Sites mapped in two open sources, pulled {_e(_AD["pulled"])}. Small dots are features tagged as data centers in OpenStreetMap, which includes server rooms and sites still under construction. Rings are the AI data centers in Epoch AI&rsquo;s dataset, sized by current power in megawatts. This is what these sources hold, not a count of every data center.</p>'
 
 '<p class="meta">Contiguous states are drawn. Sites in other states and territories are in the data file.</p>'
 f'<p><a class="btn ghost" href="/atlas/datacenters.json">Download the data (JSON)</a> &middot; <a href="https://huggingface.co/datasets/indahl/atlas-datacenters">Hugging Face dataset</a></p>'
 '<p class="meta">The data file is shared under the <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a> and contains OpenStreetMap data. The Epoch AI fields are CC BY 4.0.</p>'
 '<p><a class="btn ghost" href="/atlas/electricity">Electricity by state: prices, providers and where it comes from</a></p>'
 '<p><a class="btn ghost" href="/atlas/power-plants">Power plants: every operating plant by fuel and capacity</a></p>'
 '<p><a class="btn ghost" href="/atlas/carbon">Carbon: pounds of CO2 per megawatthour by state and grid region</a></p>'
 '<p><a class="btn ghost" href="/atlas/planned-plants">Planned power plants: what is coming, by fuel, stage and year</a></p>'
 '<h2>Sources</h2><div class="scroll"><table class="mtx"><thead><tr><th>Source</th><th>Licence</th><th>What it holds</th><th>Features kept</th></tr></thead><tbody>'
 f'<tr><td><a href="https://www.openstreetmap.org/">OpenStreetMap</a>, pulled {_e(_AD["pulled"])} through the Overpass service</td><td><a href="https://www.openstreetmap.org/copyright">ODbL</a>, &copy; OpenStreetMap contributors</td><td>Features tagged <code>telecom=data_center</code>, <code>building=data_center</code> or <code>data_center</code>. Features within 250 m with the same name are merged.</td><td>{_AS["osm_after_dedupe"]:,} of {_AS["osm_features"]:,}</td></tr>'
 f'<tr><td><a href="https://epoch.ai/data/ai-data-centers">Epoch AI, AI data centers</a></td><td><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></td><td>Name, owner, power, H100 equivalents and address of AI data centers. Addresses were turned into coordinates by us with the US Census geocoder and then OpenStreetMap Nominatim.</td><td>{_AS["epoch_drawn"]} placed of {_AS["epoch_us"]} US sites</td></tr>'
 '<tr><td><a href="https://www.eia.gov/electricity/data/eia861/">U.S. Energy Information Administration, EIA-861</a>, 2024</td><td>U.S. government data</td><td>State average prices for industrial and commercial customers, revenue divided by sales, as on the <a href="/atlas/electricity">electricity page</a>.</td><td>&mdash;</td></tr>'
 '<tr><td><a href="https://www.eia.gov/electricity/data/eia860m/">U.S. Energy Information Administration, EIA-860M</a>, September 2026</td><td>U.S. government data</td><td>Operating generators and the Planned sheet, grouped into plants by fuel, as on the <a href="/atlas/power-plants">power plants</a> and <a href="/atlas/planned-plants">planned plants</a> pages.</td><td>&mdash;</td></tr>'
 '<tr><td><a href="https://www.epa.gov/egrid">U.S. Environmental Protection Agency, eGRID2023</a></td><td>U.S. government data</td><td>State total output emission rates for carbon dioxide, as on the <a href="/atlas/carbon">carbon page</a>.</td><td>&mdash;</td></tr>'
 '<tr><td><a href="https://github.com/topojson/us-atlas">us-atlas</a></td><td>ISC, from US Census boundaries</td><td>State outlines. The map draws them simplified to within about 1.7 kilometers and leaves out islands under about 10 square kilometers.</td><td>&mdash;</td></tr>'
 '</tbody></table></div>'
 '<h2>AI data centers from Epoch AI</h2><div class="scroll"><table class="mtx"><thead><tr><th>Name</th><th>Owner</th><th>Power, MW</th><th>H100 equivalents</th><th>On the map</th></tr></thead><tbody>' + _erows + '</tbody></table></div>'
 '<p class="meta">Epoch AI, &lsquo;AI data centers&rsquo;, epoch.ai/data/ai-data-centers, licensed CC BY 4.0. Their figures are theirs. OpenStreetMap coverage differs by region, so an empty area on the map can mean unmapped. Read once on 28 October 2026 and not refreshed on a schedule. To correct or remove an entry, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
PAGES['/atlas'] = page('/atlas', 'ATLAS | Built Infrastructure | Heuremen LLC', 'ATLAS: one map of United States data centers, power plants, electricity prices and carbon intensity with layers the reader switches on and off, and the cost of a year of electricity at the stated power of AI data centers, from EIA, EPA, Epoch AI and OpenStreetMap.', _ABODY, hero_slim('ATLAS &middot; Built Infrastructure'))
# 28 Oct 2026 (his word): SAD, fifth division. Stated Against Delivered. Data: mlperf_index/hermes/model_claims.json, perchip files (build_sad.py).
_SD = _oj.load(open(os.path.join(HERE, '..', 'mlperf_index', 'sad_claims.json')))
_SS = _SD['summary']; _SC = _SD['claims']
def _sad_rows(skey):
    o = []
    for c in [c for c in _SC if c['source_key'] == skey]:
        st = (f'&ldquo;{_e(c["statement"])}&rdquo;' if c['verbatim'] else _e(c['statement']))
        nt = _e(c['note']) + (' The entry named in the post is listed in the file with a different accelerator or model.' if c['label_mismatch'] else '')
        o.append(f'<tr><td>{st}</td><td>{_e(c["compared"])}</td><td>{_e(c["stated"])}</td><td>{_e(c["in_file"])}</td><td><strong>{_e(c["outcome"])}</strong>{(" (" + _e(c["reason"]) + ")") if c.get("reason") else ""}</td><td>{nt}</td></tr>')
    return ''.join(o)
def _sad_tally(skey):
    t = _SS['tally'][skey]; n = sum(t.values())
    return f'{n} statements checked: ' + ', '.join(f'{t[k]} {k}' for k in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if k in t) + '.' + (' ' + _SS['req13'][skey]['line'] if _SS.get('req13', {}).get(skey) else '')   # 12 Nov 2026: REQ-13 beside the tally
_SM = _SS['mlcommons_files']
_sad_hd = '<thead><tr><th>Statement</th><th>Compared</th><th>Stated</th><th>In the file</th><th>Outcome</th><th>Note</th></tr></thead>'

# 28 Oct 2026 (his word, "organize and index everything on SAD"): one page per source at /hermes/model/source/<slug>, an index table on /hermes/model, the papers table on /hermes/model/papers.
_SAD_NOTICE = ('<h2>Notices</h2><p>MLPerf&reg; Inference v5.0, v5.1, v6.0 and v6.1 results, datacenter and edge suites, closed and open divisions, as published by MLCommons Association in <code>summary_results.json</code> of the repositories <code>inference_results_v5.0</code>, <code>inference_results_v5.1</code> and <code>inference_results_v6.0</code> and in <code>summary.json</code> of the repository <code>inference_results_v6.1</code> at github.com/mlcommons, retrieved 28 October 2026. MLPerf&reg; Training v5.0, v5.1 and v6.0 results as published in the result logs of the repositories <code>training_results_v5.0</code>, <code>training_results_v5.1</code> and <code>training_results_v6.0</code>, retrieved 28 October 2026. MLPerf&reg; Storage v3.0 results as published in the repository <code>storage_results_v3.0</code>, retrieved 28 October 2026. Training times on this page are recomputed from run start and run stop in each log, with the olympic average and review-committee scaling factors that the MLCommons result summarizer applies. Each row names the result entries it uses. The per-accelerator values, ratios and percentages on this page are our own computations from those results. They are not primary MLPerf&reg; metrics and are not verified by MLCommons Association. Unverified results have not been through an MLPerf&reg; review and may use measurement methodologies and/or workload implementations that are inconsistent with the MLPerf&reg; specification for verified results.</p>'
 '<p>The MLPerf&reg; and MLCOMMONS&reg; trademarks and design versions thereof are registered and unregistered trademarks and service marks of MLCommons Association in the United States and other countries. All rights reserved. Unauthorized use is strictly prohibited. See www.mlcommons.org for more information. Heuremen LLC is a member of MLCommons, and nothing on this page is endorsed by MLCommons Association.</p>')
_SAD_CORR = '<p class="meta">Vendor sentences are quoted from the pages named above. The MLCommons names and results are theirs. To correct or remove a row, use the <a href="/correction">correction or removal form</a>, open to anyone. We acknowledge every request within three business days.</p>'
def _sslug(k): return _re.sub(r'[^a-z0-9]+', '-', k.lower()).strip('-')
_sad_idx_rows = []
for src in sorted(_SS['sources'], key=lambda s: (s['vendor'].lower(), s['round'], s['key'])):
    _sl = _sslug(src['key']); _sp = '/hermes/model/source/' + _sl; _tl = src.get('title_label') or f'{src["vendor"]}, {src["round"]}'
    _src_line = ('<a href="' + _e(src["url"]) + '">' + _e(src["title"]) + '</a>') if src["url"] else _e(src["title"])
    _sbody = (f'<section class="legal"><p class="meta"><a href="/hermes/model">MODEL</a> &middot; <a href="/hermes/model#sources">All sources</a></p><h2>{_e(_tl).replace("MLPerf ", "MLPerf&reg; ")}</h2>'
              f'<p class="meta">Source: {_src_line}, fetched {_e(_SS["built"])}. <a href="/respond?u=model-{_sl}">Respond</a></p>'
              '<div class="scroll"><table class="mtx">' + _sad_hd + '<tbody>' + _sad_rows(src['key']) + '</tbody></table></div><p class="meta">' + _sad_tally(src['key']) + '</p>' + _SAD_NOTICE + _SAD_CORR + '</section>')
    _sd = f'{_tl}: what the source states, set against the published files, with the quoted sentence, the entry and the outcome for every row.'
    PAGES[_sp] = page(_sp, f'{_tl.replace("MLPerf ", "MLPerf® ")} | MODEL | Heuremen LLC', _sd, _sbody, hero_slim(_e(_tl).replace("MLPerf ", "MLPerf&reg; ")))
    _FEED.append((_sp, f'{_tl} (MODEL)', _sd))
    _tt = _SS['tally'][src['key']]
    _sad_idx_rows.append(f'<tr><td>{_e(src["vendor"])}</td><td><a href="{_sp}">{_e(src.get("name", src["key"]))}</a></td><td>{_e(src["round"]).replace("MLPerf ", "MLPerf&reg; ")}</td>' + ''.join(f'<td>{_tt.get(k, 0) or "&mdash;"}</td>' for k in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')) + '</tr>')
_SAD_INDEX = ('<h2 id="sources">Sources</h2><p>One page for each source, with every statement it makes and what the files show. The columns count outcomes.</p>'
              '<div class="scroll"><table class="mtx"><thead><tr><th>Vendor</th><th>Source</th><th>Round</th><th>Above</th><th>Below</th><th>Consistent</th><th>Cannot tell</th></tr></thead><tbody>' + ''.join(_sad_idx_rows) + '</tbody></table></div>'
              '<p class="meta"><a href="/hermes/model/papers">Papers: what each study prints against what its own data shows</a> &middot; <a href="#accelerators">Results by accelerator</a> &middot; <a href="#rerun">Sources and rerun</a></p>')
_SADBODY = ('<section class="legal"><p class="meta"><a href="/hermes/model">MODEL</a> &middot; Stated Against Delivered</p>'
 '<h2>What vendors state and what the results files show</h2>'
 '<p>MODEL sets what a vendor or a paper states next to what the published files show. The vendor tables hold statements about computing hardware, set against the results MLCommons publishes and, for the Apple table, against readings from the MacBook Pro in our lab. Each row quotes the vendor&rsquo;s sentence, names the file entries it points to, and ends in one of four outcomes. ABOVE and BELOW mean the file shows more or less than the statement. CONSISTENT means the file agrees within the rounding of the statement. CANNOT_TELL means the file cannot settle it, and it carries one reason. Here the reason is NO_INTERVAL_FORMABLE, because the file does not hold the quantity the statement needs. The numbers in the &ldquo;In the file&rdquo; column are computed by us from the public MLCommons files and the scripts to recompute them are below. The papers table is on its own page: <a href="/hermes/model/papers">Papers</a>. A row whose items fall in both directions reads CANNOT_TELL.</p>'
 + _SAD_INDEX +
 '</section><!--PAPERS--><section class="legal">'
 '<h2 id="accelerators">Results by accelerator</h2>'
 f'<p>Every closed-division datacenter throughput result (tokens, samples or queries per second) in MLPerf&reg; Inference v5.0, v5.1 and v6.0 with an accelerator count: {_SS["accelerator_rows"]:,} rows in {_SS["accelerator_groups"]} groups of model, scenario and accelerator. Per-accelerator throughput is the result divided by the number of accelerators in the entry. That is how NVIDIA&rsquo;s post computes it, and it is not an MLPerf primary metric. Where an entry&rsquo;s accelerator name states its own count and the count differs from nodes times accelerators per node, the count in the name is used. Rows with no accelerator count, which are systems without an accelerator, are left out: {_SM["v5.0"]["excluded_no_accelerator_count"]} in v5.0, {_SM["v5.1"]["excluded_no_accelerator_count"]} in v5.1 and {_SM["v6.0"]["excluded_no_accelerator_count"]} in v6.0. Closed datacenter results that have an accelerator count and are given as a latency are also left out: {_SM["v5.0"]["excluded_latency_units"]} in v5.0, {_SM["v5.1"]["excluded_latency_units"]} in v5.1 and {_SM["v6.0"]["excluded_latency_units"]} in v6.0.</p>'
 '<p><a class="btn ghost" href="/hermes/model/accelerators.csv">Per-accelerator results (CSV)</a> &middot; <a class="btn ghost" href="/hermes/model/accelerators_summary.json">Spread by group (JSON)</a> &middot; <a class="btn ghost" href="/hermes/model/claims.json">Statements and outcomes (JSON)</a></p>'
 '<h2 id="rerun">Sources and rerun</h2><div class="scroll"><table class="mtx"><thead><tr><th>Source</th><th>License</th><th>Rows</th><th>SHA-256 of the file we used</th></tr></thead><tbody>'
 + ''.join(f'<tr><td><a href="{_e(_SM[k]["url"])}">MLCommons inference results {k}</a></td><td><a href="https://www.apache.org/licenses/LICENSE-2.0">Apache-2.0</a></td><td>{_SM[k]["rows"]:,}</td><td><code>{_e(_SM[k]["sha256"][:16])}</code></td></tr>' for k in ('v5.0', 'v5.1', 'v6.0', 'v6.1'))

 + f'<tr><td><a href="{_e(_SS["training_v60"]["url"])}">MLCommons training results v6.0 (result logs)</a></td><td><a href="https://www.apache.org/licenses/LICENSE-2.0">Apache-2.0</a></td><td>{_SS["training_v60"]["result_sets"]:,} result sets</td><td>git commit <code>{_e(_SS["training_v60"]["commit"])}</code></td></tr>'
 + ''.join(f'<tr><td><a href="{_e(_SS[_k]["url"])}">{_n}</a></td><td><a href="https://www.apache.org/licenses/LICENSE-2.0">Apache-2.0</a></td><td>{_SS[_k][_c]:,} {_u}</td><td>git commit <code>{_e(_SS[_k]["commit"])}</code></td></tr>' for _k, _n, _c, _u in (('training_v50', 'MLCommons training results v5.0 (result logs)', 'result_sets', 'result sets'), ('training_v51', 'MLCommons training results v5.1 (result logs)', 'result_sets', 'result sets'), ('storage_v30', 'MLCommons storage results v3.0 (result files)', 'result_rows', 'result rows')))
 + '</tbody></table></div>'
 '<p><a href="/hermes/model/rerun.txt">How to rerun</a> &middot; <a href="/hermes/model/check_nvidia_v51.py">check_nvidia_v51.py</a> &middot; <a href="/hermes/model/check_amd_v51.py">check_amd_v51.py</a> &middot; <a href="/hermes/model/check_amd_v60.py">check_amd_v60.py</a> &middot; <a href="/hermes/model/check_intel.py">check_intel.py</a> &middot; <a href="/hermes/model/check_lambda.py">check_lambda.py</a> &middot; <a href="/hermes/model/check_nebius.py">check_nebius.py</a> &middot; <a href="/hermes/model/check_nv_training.py">check_nv_training.py</a> &middot; <a href="/hermes/model/check_supermicro.py">check_supermicro.py</a> &middot; <a href="/hermes/model/check_dell.py">check_dell.py</a> &middot; <a href="/hermes/model/check_dell_posts.py">check_dell_posts.py</a> &middot; <a href="/hermes/model/check_hpe.py">check_hpe.py</a> &middot; <a href="/hermes/model/check_supplement.py">check_supplement.py</a> &middot; <a href="/hermes/model/check_amd_training.py">check_amd_training.py</a> &middot; <a href="/hermes/model/check_nv_v61.py">check_nv_v61.py</a> &middot; <a href="/hermes/model/check_amd_crusoe_v61.py">check_amd_crusoe_v61.py</a> &middot; <a href="/hermes/model/check_v51_posts.py">check_v51_posts.py</a> &middot; <a href="/hermes/model/check_lambda_v61.py">check_lambda_v61.py</a> &middot; <a href="/hermes/model/check_lenovo_v51.py">check_lenovo_v51.py</a> &middot; <a href="/hermes/model/check_nebius_v61.py">check_nebius_v61.py</a> &middot; <a href="/hermes/model/check_redhat_v50.py">check_redhat_v50.py</a> &middot; <a href="/hermes/model/check_redhat_v60.py">check_redhat_v60.py</a> &middot; <a href="/hermes/model/check_coreweave_v61.py">check_coreweave_v61.py</a> &middot; <a href="/hermes/model/check_intel_v61.py">check_intel_v61.py</a> &middot; <a href="/hermes/model/check_azure_v61.py">check_azure_v61.py</a> &middot; <a href="/hermes/model/check_cisco_x210c_v51.py">check_cisco_x210c_v51.py</a> &middot; <a href="/hermes/model/check_cisco_c845a_v61.py">check_cisco_c845a_v61.py</a> &middot; <a href="/hermes/model/check_hpe_v51.py">check_hpe_v51.py</a> &middot; <a href="/hermes/model/check_supermicro_v50.py">check_supermicro_v50.py</a> &middot; <a href="/hermes/model/check_azure_training_v60.py">check_azure_training_v60.py</a> &middot; <a href="/hermes/model/check_amd_repro_v60.py">check_amd_repro_v60.py</a> &middot; <a href="/hermes/model/check_cisco_blog_v61.py">check_cisco_blog_v61.py</a> &middot; <a href="/hermes/model/check_amd_techdive_v61.py">check_amd_techdive_v61.py</a> &middot; <a href="/hermes/model/check_amd_repro_v61.py">check_amd_repro_v61.py</a> &middot; <a href="/hermes/model/check_amd_repro_v51.py">check_amd_repro_v51.py</a> &middot; <a href="/hermes/model/check_amd_repro_v50.py">check_amd_repro_v50.py</a> &middot; <a href="/hermes/model/check_amd_pruning_v51.py">check_amd_pruning_v51.py</a> &middot; <a href="/hermes/model/check_nv_v60.py">check_nv_v60.py</a> &middot; <a href="/hermes/model/check_nv_v50.py">check_nv_v50.py</a> &middot; <a href="/hermes/model/check_nv_training_v50.py">check_nv_training_v50.py</a> &middot; <a href="/hermes/model/check_nv_training_v51.py">check_nv_training_v51.py</a> &middot; <a href="/hermes/model/check_nv_training_v51b.py">check_nv_training_v51b.py</a> &middot; <a href="/hermes/model/check_broadcom_v51.py">check_broadcom_v51.py</a> &middot; <a href="/hermes/model/check_google_v50.py">check_google_v50.py</a> &middot; <a href="/hermes/model/check_kveritas.py">check_kveritas.py</a> &middot; <a href="/hermes/model/build_storage_v30.py">build_storage_v30.py</a> &middot; <a href="/hermes/model/check_storage_nebius_v30.py">check_storage_nebius_v30.py</a> &middot; <a href="/hermes/model/check_storage_azure_v30.py">check_storage_azure_v30.py</a> &middot; <a href="/hermes/model/check_storage_nvidia_v30.py">check_storage_nvidia_v30.py</a> &middot; <a href="/hermes/model/storage_v30_results.json">storage_v30_results.json</a> &middot; <a href="/hermes/model/kveritas_test_tamper.sh">kveritas_test_tamper.sh</a> &middot; <a href="/hermes/model/kveritas_test_siblings.sh">kveritas_test_siblings.sh</a> &middot; <a href="/hermes/model/kveritas_test_canary.sh">kveritas_test_canary.sh</a> &middot; <a href="/hermes/model/check_training_posts.py">check_training_posts.py</a> &middot; <a href="/hermes/model/parse_training_round.py">parse_training_round.py</a> &middot; <a href="/hermes/model/check_apple_mac.py">check_apple_mac.py</a> &middot; <a href="/hermes/model/mac_run.jsonl">mac_run.jsonl</a> &middot; <a href="/hermes/model/stream.c">stream.c</a> &middot; <a href="/hermes/model/gpu_bw.swift">gpu_bw.swift</a> &middot; <a href="/hermes/model/run_idle.sh">run_idle.sh</a> &middot; <a href="/hermes/model/build_accelerators.py">build_accelerators.py</a></p>'
 '<h2>Notices</h2><p>MLPerf&reg; Inference v5.0, v5.1, v6.0 and v6.1 results, datacenter and edge suites, closed and open divisions, as published by MLCommons Association in <code>summary_results.json</code> of the repositories <code>inference_results_v5.0</code>, <code>inference_results_v5.1</code> and <code>inference_results_v6.0</code> and in <code>summary.json</code> of the repository <code>inference_results_v6.1</code> at github.com/mlcommons, retrieved 28 October 2026. MLPerf&reg; Training v5.0, v5.1 and v6.0 results as published in the result logs of the repositories <code>training_results_v5.0</code>, <code>training_results_v5.1</code> and <code>training_results_v6.0</code>, retrieved 28 October 2026. MLPerf&reg; Storage v3.0 results as published in the repository <code>storage_results_v3.0</code>, retrieved 28 October 2026. Training times on this page are recomputed from run start and run stop in each log, with the olympic average and review-committee scaling factors that the MLCommons result summarizer applies. Each row names the result entries it uses. The per-accelerator values, ratios and percentages on this page are our own computations from those results. They are not primary MLPerf&reg; metrics and are not verified by MLCommons Association. Unverified results have not been through an MLPerf&reg; review and may use measurement methodologies and/or workload implementations that are inconsistent with the MLPerf&reg; specification for verified results.</p>'
 '<p>The MLPerf&reg; and MLCOMMONS&reg; trademarks and design versions thereof are registered and unregistered trademarks and service marks of MLCommons Association in the United States and other countries. All rights reserved. Unauthorized use is strictly prohibited. See www.mlcommons.org for more information. Heuremen LLC is a member of MLCommons, and nothing on this page is endorsed by MLCommons Association.</p>'
 '<h2>Independence</h2><p>Every Heuremen LLC employee certifies in writing that they have no business interest in any company listed on our websites and will not buy or sell securities of any company named in our published work. The certification is public: <a href="/conflict-of-interest">conflict of interest</a>.</p>'
 '<p class="meta">Vendor sentences are quoted from the pages named above. The MLCommons names and results are theirs. To correct or remove a row, use the <a href="/correction">correction or removal form</a>, open to anyone. We acknowledge every request within three business days.</p></section>')
PAGES['/hermes/model'] = page('/hermes/model', 'MODEL | Stated Against Delivered | Heuremen LLC', 'MODEL: what AI hardware vendors state, held against the published MLCommons results, with the quoted sentence, the entry and the outcome for every row.', _SADBODY, hero_slim('MODEL &middot; Stated Against Delivered'))
# 28 Oct 2026 (his word): TIME. Public time servers stated against delivered, measured live from our GPS-disciplined reference. Plan: time_index/PLAN.md.
_TIMEBODY = ('<section class="bench"><h2>Public Time Servers, Stated Against Delivered</h2>'
  '<p>Each server below is asked ordinary time queries, and the table says when one did not answer. Every reply states its own error bound, a root dispersion plus half a root delay. We ask each server eight times per round from a clock disciplined by a GPS pulse, keep the fastest reply, and compare the measured offset with the server\'s own stated bound. The internet path adds an uncertainty of half its round trip, so a bound smaller than that cannot be confirmed or refused, and the outcome says cannot tell. Rules were committed before the first query.</p>'
  '<div id="time-live" class="bench-live">Loading.</div><script src="/time/live.js" defer></script>'
  '<p class="bench-note">Consistent: the offset and path uncertainty fit inside the stated bound. Above: the server is further from true time than it states. Cannot tell, with its reason beside it: too wide to resolve when the path uncertainty reaches both a perfect clock and the stated bound, straddles edge when the offset and path uncertainty overlap the bound, no interval formable when the reading cannot be computed. The path uncertainty is half the round trip of the kept reply, a worst-case bound and not a probability interval. The outcome rule is the plan with its addendum of 12 November 2026. A server that returns nothing is a failed read, listed apart and outside every count of outcomes. No ranking.</p></section>')
PAGES['/time'] = page('/time', 'TIME | Public Time Servers Stated Against Delivered | Heuremen LLC', 'TIME: public time servers held against their own stated error bounds, measured live from a GPS-disciplined clock, with the outcome for every server.', _TIMEBODY, hero_slim('TIME &middot; Stated Against Delivered'))
# 2 Nov 2026: the free downloads and tools, so feed readers see them
for _fp, _ft, _fd in (('/qia/package', 'QIA Research Package', 'For runs on IBM quantum hardware: check the calibration record your run depends on, before and after the run. Tested on real IBM records. The checker alone: pip install qia-check.'),
                      ('/darkwave/kit', 'Darkwave Correction Kit', 'Measure the turn a mid-circuit readout gives untouched qubits on your own IBM account and add the matching virtual-Z correction. Tested on ibm_kingston under plans published before each job.'),
                      ('/iris/package', 'IRIS Research Package', 'For language-model evaluations: reading sheets, flip counts between repeated runs and paired comparisons with four outcomes. The checker alone: pip install iris-check.'),
                      ('/atlas/data-pack', 'ATLAS Data Pack', 'Every ATLAS dataset as JSON, CSV and GeoJSON with sources and pull dates.'),
                      ('/oy/data-pack', 'OY Data Pack', 'Every OY table as JSON and CSV, with the source of every row.'),
                      ('/hermes/model/data-pack', 'MODEL Data Pack', 'Every MODEL statement and the MLCommons results it was held against, as JSON and CSV.'),
                      ('/qia#runcheck', 'Check a Run Against the Record in Force', 'Pick an IBM processor and the start and end of your run to see the published calibration record in force, its flags for your qubits and what changed during the run.')):
    _FEED.append((_fp, _ft, _fd))
_FEED.append(('/time', 'TIME: Public Time Servers Stated Against Delivered', 'What public time servers state about their own accuracy, measured live against a GPS-disciplined clock.'))
# 28 Oct 2026 (his word): COIN. Ravencoin's whitepaper statements held against the chain's own block record, live. Plan and checker: coin_index/.
_COINBODY = ('<section class="bench"><h2>Ravencoin, Stated Against Delivered</h2>'
  '<p>Block records from the Ravencoin Insight explorer API at explorer.rvn.zelcore.io, read about every 12 minutes. Each statement is quoted from the <a href="https://ravencoin.org/assets/documents/Ravencoin.pdf">Ravencoin whitepaper</a> of 3 April 2018 and held against what the chain recorded. The tables name the blocks each reading covers.</p>'
  '<div id="coin-live" class="bench-live">Loading.</div><script src="/coin/live.js" defer></script>'
  '<p class="bench-note">Consistent: the record fits the statement. Above and below: the record is higher or lower than stated. For the statements about a pre-mine and an allocation, below means a block pays more than the one miner payout. Cannot tell: the statement gives no threshold, or the block record cannot show it, or a block&rsquo;s payout could not be read. Payout addresses and coinbase tags are shown as the chain records them and say nothing about who is behind them. No ranking.</p></section>')
_COINBODY += ('<h2>Trends: Pool Shares and Batch Payouts</h2>'
  '<p>Who signs the blocks, hour by hour, and who pays the miners. Blocks and transactions are read from a public explorer. Each pool address or coinbase tag has its share of blocks tested in six hour buckets against its own earlier share, and every move of three or more standard deviations is counted against the number chance alone would give. Batch payouts are transactions with twenty or more outputs spent from a watched address. The plan was committed before any series was computed.</p>'
  '<div id="coin-trends" class="bench-live">Loading.</div><script src="/coin/trends.js" defer></script>')
PAGES['/coin'] = page('/coin', 'COIN | Ravencoin Stated Against Delivered | Heuremen LLC', 'COIN: what the Ravencoin whitepaper states, held against the chain\'s own block record, live, with the quote and the outcome for every statement.', _COINBODY, hero_slim('COIN &middot; Ravencoin'))
_FEED.append(('/coin', 'COIN: Ravencoin Stated Against Delivered', 'What the Ravencoin whitepaper states, held against the chain\'s own block record.'))
PAGES.pop('/coin', None); _FEED[:] = [x for x in _FEED if x[0] != '/coin']   # GONE 30 Oct 2026 (his 'Drop coin, we're done with that'): the block above stays for the record, the page is not built
# 28 Oct 2026 (his word): CADA, Checked Against Domain Alerts. Public DNS filters held against fresh bad-domain listings, live. Plan: cada plan, caca_index/PLAN.md.
_CADABODY = ('<section class="bench"><h2>Public DNS Filters, Checked Against Domain Alerts</h2>'
  '<p>Free public resolvers advertise blocking of malware and phishing domains. Two public lists of bad domains, the <a href="https://github.com/mitchellkrogza/Phishing.Database">Phishing.Database active domain list</a> and the <a href="https://hole.cert.pl/domains/">CERT Polska domain list for blocking</a>, are read about every 17 minutes. Each domain that is new since the last read is asked about at first sight, then after 1 hour, 6 hours and 24 hours, through three resolvers that state no filtering (Cloudflare 1.1.1.1, Quad9 9.9.9.10 and Google 8.8.8.8) and through each filter. A filter blocks a domain when it refuses while the unfiltered resolvers answer. Only DNS questions are asked. No listed host is contacted and nothing is downloaded. The rules were committed before the first question.</p>'
  '<div id="cada-live" class="bench-live">Loading.</div><script src="/cada/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=cada-all">Respond</a></p>'
  '<p class="bench-note">Each cell is the share of live listed domains the resolver refused, with the 95% interval, and the count behind it. It is a measured share and is not compared with any provider claim, so no cell carries an outcome word and none is cannot tell. A query that returns no answer is a failed read, counted apart and outside every share. No ranking.</p></section>')
PAGES['/cada'] = page('/cada', 'CADA | Checked Against Domain Alerts | Heuremen LLC', 'CADA: public DNS filters held against fresh malware and phishing listings, live, with the share blocked and the time to block for every resolver.', _CADABODY, hero_slim('CADA &middot; Checked Against Domain Alerts'))
_FEED.append(('/cada', 'CADA: Checked Against Domain Alerts', 'Public DNS filters held against fresh bad-domain listings.'))
def _api_tools():
    # 30 Oct 2026 (site pass A-9): the Tools table is built from the TOOLS list in api.js, so it cannot drift from /api/v1. Each row is the first sentence of the tool's own description.
    import subprocess as _spp, tempfile as _tf, shutil as _sh, json as _jj
    _d = _tf.mkdtemp()
    try:
        _p = os.path.join(_d, 'api_tools.mjs')
        open(_p, 'w', encoding='utf-8').write(open(os.path.join(HERE, 'api.js'), encoding='utf-8').read() + '\nexport const __TOOLS = TOOLS.map(t => ({ name: t.name, description: t.description }));\n')
        _r = _spp.run([_sh.which('node') or '/opt/homebrew/bin/node', '--input-type=module', '-e', 'import(' + _jj.dumps('file://' + _p) + ').then(m => console.log(JSON.stringify(m.__TOOLS)))'], capture_output=True, text=True, timeout=90)
        if _r.returncode != 0: raise SystemExit('build_site: could not read the tool list from api.js: ' + _r.stderr[:300])
        _tools = _jj.loads(_r.stdout)
    finally: _sh.rmtree(_d, ignore_errors=True)
    out = []
    for t in _tools:
        _first = _re.split(r'(?<=[a-z0-9\)])\.\s+(?=[A-Z])', t['description'].strip(), maxsplit=1)[0].rstrip('.').replace('; ', ', ') + '.'   # no semicolons in page prose
        out.append((t['name'], _first))
    return out
import html as _he
import json as _mj, re as _mre, html as _chtml
_MKT = _mj.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'claude-plugins', '.claude-plugin', 'marketplace.json')))['plugins']
_APIJS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api.js'), encoding='utf-8').read()
_MCPG = [(m.group(1), m.group(2), m.group(3)) for m in _mre.finditer(r"^  (\w+): \{ title: '([^']*)', note: '([^']*)'", _APIJS[_APIJS.index('const GROUPS'):], _mre.M)]
# 28 Oct 2026 (his word): the read-only data API and MCP server, documented on our own site. Code: indahl-ai/api.js. Posting goes to indahl.ai only.
_APIBODY = ('<section class="bench markguide"><h2>Our measurements as tools</h2>'
  '<p>Every live desk on this site can be read by an agent or a script, with no key and nothing to install. Each answer carries its source page, the time it was read and the terms. Outcomes are above, below, consistent or cannot tell, relative to what was stated. Nothing here writes anything.</p>'
  '<h3>Add it to an agent</h3>'
  '<p>The MCP server is at https://indahl.ai/mcp and speaks the Model Context Protocol over HTTP. In Claude Code:</p>'
  '<pre>claude mcp add --transport http indahl https://indahl.ai/mcp</pre>'
  '<p>Any client that takes a remote MCP server can use the same address. Start with list_divisions.</p>'
  '<h3>Tools</h3>'
  '<table class="mtx"><thead><tr><th>Tool</th><th>Returns</th></tr></thead><tbody>'
  + ''.join('<tr><td>' + _he.escape(_n) + '</td><td>' + _he.escape(_d) + '</td></tr>' for _n, _d in _api_tools())
  + '</tbody></table>'
  '<h3>The same tools as plain JSON</h3>'
  '<pre>curl \'https://indahl.ai/api/v1/time_servers?server=nist\'\ncurl \'https://indahl.ai/api/v1/find_study?query=readout&amp;division=qia\'\ncurl https://indahl.ai/api/v1</pre>'
  '<p>The OpenAPI description is at <a href="/api/openapi.json">/api/openapi.json</a>. Tool responses are cached for a minute and the tool list and the OpenAPI file for ten minutes.</p>'
  '<h3>Datasets</h3>'
  '<p>The data behind the QIA, IRIS, OY, ATLAS and MODEL pages, and our run data, are also published as datasets on Hugging Face: <a href="https://huggingface.co/indahl">huggingface.co/indahl</a>. Each page names its own datasets.</p>'
  '<h3>Terms</h3>'
  '<p>Retrieval and answering are permitted with attribution. Use as training data is not permitted, as stated in the <a href="/terms#ai-training">terms</a>. The code is in the <a href="https://github.com/Heuremen-LLC/indahl.ai">public repository</a>. Named in a result and want to answer it? <a href="/contact">Inquiry</a>.</p></section>')
PAGES['/api'] = page('/api', 'API | Our measurements as tools for agents and scripts | Heuremen LLC', 'A read-only MCP server and JSON API over every live measurement on indahl.ai, with the source, the time read and the terms on every answer.', _APIBODY, hero_slim('API &middot; Data and MCP'))
_FEED.append(('/api', 'API: our measurements as tools for agents and scripts', 'A read-only MCP server and JSON API over every live measurement on indahl.ai.'))
# 28 Oct 2026 (his word): UPTIME. Vendor status pages held against independent probes from three networks, live. Plan: status_index/PLAN.md.
_UPBODY = ('<section class="bench"><h2>Status Pages Against Independent Probes</h2>'
  '<p>Each vendor below publishes a status page that says whether its systems are operational. Every round, our two probe seats make one plain request to a public endpoint the vendor serves. One seat is on a cloud network. The other is on a home network and is two of our machines that count as one seat. A request fails if it times out, cannot connect or returns a server error. A disagreement is a round where the page said operational and both seats failed. Two control targets with no status page set the floor for chance failures. Rules were committed before the first round.</p>'
  '<div id="uptime-live" class="bench-live">Loading.</div><script src="/uptime/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=uptime-all">Respond</a></p>'
  '<p class="bench-note">Each vendor is read as the share of rounds in which the page and both seats agree, with a 95% interval, against one threshold set by the floor. Above: the whole interval is above the threshold. Below: the whole interval is below it and there are at least two separate episodes, so the service was less reachable than its page stated. Cannot tell, with its reason beside it: too wide to resolve when there are fewer than 300 rounds or fewer than two episodes, straddles edge when the interval overlaps the threshold, no interval formable when there is no round. One endpoint is not a whole service, and a disagreement is between the page and that endpoint on those seats in that round. Incidents a vendor records are its own. No ranking.</p></section>')
PAGES['/uptime'] = page('/uptime', 'UPTIME | Status Pages Against Independent Probes | Heuremen LLC', 'UPTIME: vendor status pages held against independent probes from a home network and a cloud network, live, with the disagreements counted against a measured floor.', _UPBODY, hero_slim('UPTIME &middot; Status Pages Against Probes'))
_FEED.append(('/uptime', 'UPTIME: Status Pages Against Independent Probes', 'What vendor status pages state, held against probes from a home network and a cloud network.'))
# 28 Oct 2026 (his list, items 2 and 3): FORECAST and CADENCE, live. Plans: forecast_index/PLAN.md, cadence_index/PLAN.md.
_FCBODY = ('<section class="bench"><h2>Stated Chance of Precipitation Against What Happened</h2>'
  # 10 Nov 2026 (cold read row 9, PLAN.md Addendum 2): the NWS event rule is primary, decided after the data. The original committed rule stays beside it.
  '<p>The National Weather Service states a chance of precipitation for each 12 hour period, and its chance is for measurable precipitation, 0.01 inch or more. For major United States airports, each forecast is stored when it is fetched, and each period is scored after it ends against that airport\'s hourly reports. If a stated 30 percent holds, about 30 percent of such periods should have measurable precipitation.</p>'
  '<p>Two rules for what counts as precipitation are scored on the same periods. The NWS rule is the primary reading from 10 November 2026. It counts a period when the airport\'s routine hourly reports inside it add up to 0.01 inch or more, with a trace read as zero. The totals come from the Iowa Environmental Mesonet archive of those reports. The original rule was committed on 28 October 2026, before the first forecast was stored. It counts a period when any hourly report shows an amount above zero or reports rain, drizzle, snow, sleet, hail, showers or thunderstorm. That is wider than the chance it is scored against, so it counts more periods as wet.</p>'
  '<p>The NWS rule was adopted after the data had been read, and the plan says so in a dated addendum. On 10 November, in the 10 to 20 percent cell at under 12 hours, the stated chance averaged 14.1 percent. Under the original rule 43.9 percent of those periods had an event (95% interval 34.9 to 53.4, above). Under the NWS rule 16.8 percent did (95% interval 10.9 to 25.0, cannot tell because the interval holds the 14.1 percent stated and the plan named no tolerance). Over all cells, the original rule read 12 of 18 cells above, 3 consistent and 3 cannot tell. The NWS rule read 3 of 18 above, all three in the 50 to 60 percent bin, 12 consistent and 3 cannot tell. Those tallies are the readings under the rule the plan named on 10 November. Under Standards 2.0 a cell whose interval holds the stated chance reads cannot tell, so the consistent cells in both tallies now read cannot tell. Both tables stay on this page, and the original is never deleted.</p>'
  '<div id="forecast-live" class="bench-live">Loading.</div><script src="/forecast/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=forecast-all">Respond</a></p>'
  '<p class="bench-note">Above: it happened more often than stated. Below: less often. Cannot tell: the interval holds the stated chance (STRADDLES_EDGE), or the cell has under 30 periods (TOO_WIDE_TO_RESOLVE). The plan named no tolerance, so no cell reads consistent (plan addendum of 12 November 2026, Standards 2.0). Hourly reports can miss a short shower, so the observed frequency is a floor, and the chance floor is printed with each table. Periods from one storm are not independent. No ranking.</p></section>')
PAGES['/forecast'] = page('/forecast', 'FORECAST | Stated Chance Against What Happened | Heuremen LLC', 'FORECAST: the National Weather Service stated chance of precipitation against what happened at 30 airports, as live calibration tables with intervals.', _FCBODY, hero_slim('FORECAST &middot; Stated Chance Against What Happened'))
_FEED.append(('/forecast', 'FORECAST: Stated Chance Against What Happened', 'Stated chance of precipitation against observed precipitation, live.'))

# 28 Oct 2026 (his list, item 6): TRIALS, live. Plan: trials_index/PLAN.md.
_TRBODY = ('<h2>Trials that started and were later stopped</h2><p>The first block counts interventional studies that started in the last two years and are now withdrawn, terminated or suspended, by sponsor class, with the reason the registry holds. Two tests check the registry against its own rules: a reason for every stopped study, and no enrolled participants for a withdrawn one. The plan for this block was added to the plan file before the read, and ten records the first test counted were read in full on their own record and are listed beside the tests. A stopped study is not a fault, and a young cohort has had less time to stop.</p>'
  '<h2>Results due against results posted</h2>'
  '<p>United States law (FDAAA 801) asks the responsible party of an applicable clinical trial to submit results to ClinicalTrials.gov within 12 months of the primary completion date, unless a delay is certified. This page reads the public registry for interventional trials of FDA-regulated drugs and devices with an actual primary completion date from 2018 to the end of the month 14 months before the read, and counts which records have results posted. Records 13 to 15 months past completion are the plan\'s lag zone. They are shown apart and not scored, so every scored record is at least 15 months past completion. Until 10 November 2026 the lag zone was scored, which the plan never allowed (plan addendum 5). The registry class Other government covers state, local and non-US public bodies, not the US federal government.</p>'
  '<p>The registry does not store whether a trial is an applicable clinical trial or whether a delay was certified. Phase 1 drug-only records are left out because the law does not cover them. Devices are shown apart because device feasibility studies often fall outside the law and the registry has no phase marker for them. Rules were committed before the first read.</p>'
  '<div id="trials-live" class="bench-live">Loading.</div><script src="/trials/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=trials-all">Respond</a></p>'
  '<p class="bench-note">The share of records with no results on the record is read against a band of 0 to 10 percent, open at 10, and 25 percent is the size that matters. Above: the whole 95 percent interval lies at or above 10 percent. Consistent: the interval sits inside the band and does not reach both 0 and 25 percent. Cannot tell: neither, and the Outcome cell gives the reason, TOO_WIDE_TO_RESOLVE when the interval reaches both 0 and 25 percent, STRADDLES_EDGE when it overlaps 10 percent, NO_INTERVAL_FORMABLE when no record is scored. The earlier rule left a range between 10 and 25 percent where a resolved share read cannot tell. The rule in the plan addendum dated 12 November 2026, committed before any reading under it, closes that range, and the headline share now reads above. The intervals treat records as independent although sponsors and programs cluster, so they are narrower than the records justify. Records and sponsor names are as the registry gives them. The count of failed reads and the share of cannot tell by reason sit beside the headline.</p>')
PAGES['/trials'] = page('/trials', 'TRIALS | Results Due Against Results Posted | Heuremen LLC', 'TRIALS: ClinicalTrials.gov records for FDA-regulated drug and device trials, results posted against results on the record, by sponsor class and sponsor, live.', _TRBODY, hero_slim('TRIALS &middot; Results Due Against Posted'))
_FEED.append(('/trials', 'TRIALS: Results Due Against Posted', 'ClinicalTrials.gov results posted against the one year due date, by sponsor class and sponsor.'))

# 28 Oct 2026 (his list, item 5): LAUNCH, live. Plan: launch_index/PLAN.md.
_LNBODY = ('<h2>Stated launch time against the time it flew</h2>'
  '<p>Every upcoming orbital launch carries a stated target time that keeps being revised. The schedule source keeps only the current time, so we read it about every half hour, store each change, and score a launch after it flies. For each launch we take the time that was stated 1, 7 and 30 days before it flew and measure how far the flown time was from it.</p>'
  '<p>Our first snapshot was taken on 28 October 2026 and earlier history is not claimed. Rows appear here as launches that we were already watching fly. Rules were committed before the first snapshot.</p>'
  '<div id="launch-live" class="bench-live">Loading.</div><script src="/launch/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=launch-all">Respond</a></p>'
  '<p class="bench-note">Slip is the absolute difference in hours. Above: the lower end of the 95 percent interval of the share that slipped by more than 24 hours is at or above 10 percent. Consistent: the whole interval lies below 10 percent. Cannot tell comes with a reason beside it. TOO_WIDE_TO_RESOLVE means fewer than 30 launches are scored or the interval holds both zero and 25 percent, which is the size that matters. STRADDLES_EDGE means the interval overlaps the 10 percent edge. NO_INTERVAL_FORMABLE means no interval can be formed. The same rule applies at every lead. It moved to Standards 2.0 on 12 November 2026 by a plan addendum, and earlier readings stand under the rule they named. REQ-13 beside each row gives the list reads that returned nothing and the share of cannot tell by reason. Data: Launch Library 2.</p>')
PAGES['/launch'] = page('/launch', 'LAUNCH | Stated Time Against Flown | Heuremen LLC', 'LAUNCH: the stated time of orbital launches, stored as it changes, against the time each launch flew, live, by lead time and provider.', _LNBODY, hero_slim('LAUNCH &middot; Stated Time Against Flown'))
_FEED.append(('/launch', 'LAUNCH: Stated Time Against Flown', 'Stated launch times stored as they change, against the times launches flew.'))

# 29 Oct 2026: LINKROT, live. Plan: linkrot_index/PLAN.md.
_LRBODY = ('<p>This page reads links two ways. The first part reads every arXiv paper in five categories that states where its code is. The second part reads random samples beside it: early web listings, addresses cited in standards and in official documents, landmark sites of the early web and our own name (<a href="#linkrot-early">samples beside arXiv</a>).</p>'
  '<h2>Papers state where their code is. Does the link still lead there?</h2>'
  '<p>We read every arXiv paper in five categories whose abstract points to GitHub, GitLab, Hugging Face, Zenodo or Bitbucket, and keep each link the abstract or the arXiv comment gives. Every link is requested and read again every seven days. A link counts as rot when the page is gone or the host name no longer exists. A host that blocks us or times out is counted apart and is never rot. Every link is also requested from an independent network, the GitHub runner network, and a link that one network reads live and the other reads gone is counted as blocked and never as rot.</p>'
  '<p>Ten control links run before each pass, five that must be live and five that must be gone. If any control reads wrong, every row reads cannot tell. For links that lead to a GitHub repository we also ask whether anything is there: the repository check below counts repositories with no commits. We do not read the code. Links that appear only in the full text of a paper are not reached. Rules were committed before the first link was checked.</p>'
  '<div id="linkrot-live" class="bench-live">Loading.</div><script src="/linkrot/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=linkrot-all">Respond</a></p>'
  '<p class="bench-note">Above: the lower end of the 95 percent interval of the rot share is at or above 5 percent. Consistent: the whole interval lies below 5 percent. Cannot tell comes with a reason beside it. TOO_WIDE_TO_RESOLVE means fewer than 30 links are readable or the interval holds both zero and 10 percent, which is the size that matters. STRADDLES_EDGE means the interval overlaps the 5 percent edge. NO_INTERVAL_FORMABLE means a control failed or no link is readable. The rule moved to Standards 2.0 on 12 November 2026 by a plan addendum, and earlier readings stand under the rule they named. REQ-13: links that read blocked or timed out are the nothing returned count and sit outside the share. Source: the arXiv API.</p>')
# 10 Nov 2026: samples beside arXiv (PLAN.md Addenda 3 and 4). The fragment is the shipped snapshot linkrot_index/shipped/linkrot_samples.html, written only by
# linkrot_index/early/ship_samples.py freeze, so the tick that keeps reading never changes the page between ships. Its numbers have ledger rows (linkrot.samples.*).
_lrs = os.path.join(HERE, '..', 'linkrot_index', 'shipped', 'linkrot_samples.html')
if os.path.exists(_lrs): _LRBODY = _LRBODY + open(_lrs, encoding='utf-8').read()
PAGES['/linkrot'] = page('/linkrot', 'LINKROT | Stated Links Against Live | Heuremen LLC', 'LINKROT: code and data links stated in arXiv papers against whether they still resolve, read every week, and random samples beside them from the early web, RFCs, the Federal Register, landmark sites and our own name, with intervals.', _LRBODY, hero_slim('LINKROT &middot; Stated Links Against Live'))
_FEED.append(('/linkrot', 'LINKROT: Stated Links Against Live', 'Code and data links stated in arXiv papers against whether they resolve.'))

# 29 Oct 2026: TAPE, live. Plan: tape/PLAN.md.
_TAPEBODY = ('<h2>A record of what was published, in the order it was published</h2><p>About every half hour we hash every live feed and add a line to a chain, and whenever a public page changes we hash every public page into the chain too. Each line carries the hash of the line before it, so changing an old line changes every line after it. Each run also writes a beacon value built from the newest <a href="https://drand.love">drand</a> round, the feeds of that run, the previous line and the root of the newest quantum-bits entry, which holds bits read from an IBM processor. Nobody could have known it before those inputs existed, and anyone can recompute it. Every few hours the chain is stamped with <a href="https://opentimestamps.org">OpenTimestamps</a>, which ties it to Bitcoin&rsquo;s timeline. We hold no coin and run no mining.</p>'
  '<div id="tape-live" class="bench-live">Loading.</div><script src="/tape/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=tape-all">Respond</a></p>'
  '<p class="bench-note">A hash proves that a page or feed existed in exactly this form at that time. It does not prove the content is true. The plan, the chain, every leaf behind every line and the verifier are public in <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/tape">the repository</a>, and the verifier needs only Python. Run <code>python3 tape_verify.py</code> in that folder to check the whole chain.</p><p class=\"bench-note\">Each release of the site is also stamped on its own, with Internet Archive copies of what changed: <a href=\"/receipts/stamps\">STAMPS</a>.</p><p class=\"bench-note\">Want your own receipt? <a href=\"/vault\">VAULT</a> hashes a file in your browser and adds the hash to this tape. The file never leaves your computer.</p>')
PAGES['/tape'] = page('/tape', "TAPE | What We Published, and When | Heuremen LLC", "A public hash chain of every page and live feed Heuremen LLC publishes, with a beacon value in each run. Every entry carries the hash of the one before it, and anyone can verify the chain.", _TAPEBODY, hero_slim("TAPE &middot; What We Published, and When"))
_FEED.append(('/tape', "TAPE : What We Published, and When", "A public hash chain of every page and live feed, with a beacon value in each run."))

# 10 Nov 2026: STAMPS. Each release of the site gets a release record (public repository commit, SHA-256 of every deployed file, hash of the
# internal ledger), chained by hash to the release before it (no outside timestamp chain since 13 Nov 2026), and the changed pages go to the Internet Archive. Written by ledger/stamps.py from ship.sh step 7.
_STAMPSBODY = ('<h2>Proof of what we released, and when</h2><p>Each time we release this site we write a release record. It names the commit of the <a href="https://github.com/Heuremen-LLC/indahl.ai">public repository</a>, the SHA-256 hash of every file the release put on the site, the hash of our internal claims ledger and the hash of the release record before it, so the releases form one chain. Our own chains hold the time: <a href="/tape">TAPE</a> hashes every live page and feed about every half hour, and our archive digest chain links every manifest to the one before it. The commit is pushed to the public repository, and the pages and data files that changed are sent to the <a href="https://web.archive.org">Internet Archive</a>, which keeps its own dated copy.</p>'
  '<div id="stamps-live" class="bench-live">Loading.</div><script src="/receipts/stamps/live.js" defer></script>'
  '<h2>How to verify a release</h2><ol><li>Download the release record (JSON) from the table above.</li>'
  '<li>Follow the chain. Each record carries the hash of the record before it. Hash the earlier record with <code>shasum -a 256</code> and find the same hash in the later one.</li>'
  '<li>Compare hashes. Hash any file you downloaded from indahl.ai, or a file from the public repository at the listed commit, and find the same hash beside its path in the record. The Internet Archive capture shows the page as it was served at that time.</li></ol>'
  '<p class="bench-note">A hash proves that a file with that content existed when the chain recorded it. It does not prove that the content is true. Releases before 13 November 2026 also carry an OpenTimestamps proof, kept as it was; we stopped using outside timestamp chains on that date and rely on our own. The record holds the hash of our internal ledger, never its content. The script that writes the records is public in <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/stamps">the repository</a>.</p>')
PAGES['/receipts/stamps'] = page('/receipts/stamps', "STAMPS | What We Released, and When | Heuremen LLC", "Every release of indahl.ai, with its commit, the hash of every deployed file, the hash of the release before it, and Internet Archive captures of what changed.", _STAMPSBODY, hero_slim("STAMPS &middot; What We Released, and When"))
_FEED.append(('/receipts/stamps', "STAMPS : What We Released, and When", "Every release of indahl.ai, chained release to release by hash, with Internet Archive captures of what changed."))

# 29 Oct 2026: HOSTS, live. Plan: hosts/PLAN.md.
_HOSTSBODY = ('<h2>Who serves the same model, and how steadily?</h2><p>An open-weight model can be served by a dozen companies. OpenRouter, an aggregator, lists for each model its hosts, each host\'s stated quantization (the numeric precision of the weights), prices, limits and uptime figures. We read all of it every 12 minutes and keep every read, so the page shows where hosts differ for the same model, who is down right now, and how uptime varies with quantization.</p>'
  '<div id="hosts-live" class="bench-live">Loading.</div><script src="/hosts/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=hosts-all">Respond</a></p>'
  '<p>The first table compares the one-day uptime a host states with the mean of the 5-minute uptime figures from our own polls over the same 24 hours, with the 2 percentage point tolerance fixed in the plan. As the plan sets, the comparison is made at the latest poll that closes a 24-hour span holding at least 100 of our polls, and the table says when that span ended and how many polls it holds. It reads cannot tell (NO_INTERVAL_FORMABLE) only when no kept span holds 100 polls. The share of endpoints that disagree is read against a band of 0 to 15 percent, open at 15, with 5 percent as the size that matters. CONSISTENT needs the whole 95 percent interval inside the band and not reaching both 0 and 5 percent, and ABOVE needs its lower end at or above 15 percent. This rule is in a plan addendum dated 12 November 2026, committed before any reading under it. The count of failed reads and the share of cannot tell by reason sit under the table. Latency and throughput are empty in the public data and are not shown. A model with one host is listed as such. <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/hosts/PLAN.md">Plan, addenda and code</a>.</p>')
PAGES['/hosts'] = page('/hosts', "HOSTS | One Model, Many Hosts | Heuremen LLC", "HOSTS: every open-weight model served through OpenRouter, every host serving it, each host's stated quantization and uptime, polled every 12 minutes and kept.", _HOSTSBODY, hero_slim("HOSTS &middot; One Model, Many Hosts"))
_FEED.append(('/hosts', "HOSTS : One Model, Many Hosts", "Open-weight models, their hosts, quantization and uptime, live."))

# 29 Oct 2026: CAMPUS, live. Plan: campus/PLAN.md.
_CAMPUSBODY = ('<h2>Do the pages schools published stay where they were?</h2><p>The OY page lists what colleges and universities have published about their own AI policies and about measuring them, with a source link for every row. Those sources are web pages and PDFs that their owners can move, rewrite or remove. We read every external source on the OY page, keep what each one said, and read it again on later passes, so that a change shows and so that the OY Matrix can be kept right.</p>'
  '<div id="campus-live" class="bench-live">Loading.</div><script src="/campus/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=campus-all">Respond</a></p>'
  '<p>A page changed when the overlap of its three-word sequences with the previous read is below 0.90, so dates, menus and counters can move it a little. A page that is not found may have been moved. A blocked page refused our request, which names this site and does not disguise itself, and tells us nothing about the page. Every gone page and every page rewritten past one half is read in full and listed. <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/campus/PLAN.md">Plan, addenda and code</a>.</p>')
PAGES['/campus'] = page('/campus', "CAMPUS | The Documents Behind OY, Kept | Heuremen LLC", "CAMPUS: every external source cited on the OY page, read and kept pass after pass so that a moved, changed or removed page shows.", _CAMPUSBODY, hero_slim("CAMPUS &middot; The Documents Behind OY, Kept"))
_FEED.append(('/campus', "CAMPUS : The Documents Behind OY, Kept", "The documents behind the OY page, kept over time, live."))

# 29 Oct 2026: AIRQ, live. Plan: airq/PLAN.md.
_AIRQBODY = ('<h2>Do the sensors meet the targets the EPA wrote down?</h2><p>The EPA published performance targets for PM2.5 air sensors in 2021: a slope of 1.0 plus or minus 0.35 against a reference monitor, an intercept within 5 micrograms per cubic metre, an R squared of at least 0.70, and an error of at most 7 micrograms (RMSE) or 30 percent (NRMSE). We take every public outdoor PurpleAir sensor within 200 metres of an EPA continuous monitor, compare the two on the same UTC days, and, taking for each monitor its sensor with the median error (RMSE), ask how many monitors have that sensor meeting all four targets. We score the raw map reading, the raw cf_1 reading, and the reading corrected for humidity by the published Barkjohn equation. The plan names none of the three as the headline, so the map reading and the corrected reading are shown with equal weight. At a monitor with an even number of sensors the plan gives no rule for the median pair. The count uses the lower of the two middle pairs, and the count under the other tie is shown beside it. Both rules were stated on 10 November 2026, after the data (plan addendum 5).</p>'
  '<p>The newest window is 1 March to 30 June 2026. The EPA record ends there for now. Monitoring agencies send their data to the EPA by quarter, about three months after the quarter ends, so July to September 2026 cannot be read yet. The 2026 monitor values are as the agencies sent them and are not yet certified. The previous reading, 1 June to 29 September 2025, is kept below the newest one. The two windows are different seasons, and the 2025 window held the summer smoke season.</p>'
  '<p>The first two tables are live. Every hour the same sensors are set against AirNow, the EPA\'s real-time values for the same monitors, and the last 30 kept days of each monitor are scored the same way. AirNow values are real-time and not yet validated, so this reading can differ from the window reads below, which use the EPA\'s Air Quality System record. The strip shows ten sensors for the last complete hour. The sensor service gives a reading every two minutes, but each reading costs points on a fixed account, so the panel reads once an hour.</p>'
  '<div id="airq-live" class="bench-live">Loading.</div><script src="/airq/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=airq-all">Respond</a></p>'
  '<p>Each row is the share of monitors whose sensor does not meet the four targets, with a 95 percent interval over monitors (a monitor with several sensors counts once). One half is a single line, so a row reads ABOVE when the lower end is above one half, BELOW when the upper end is below one half, and otherwise cannot tell, with the reason beside it. Under 30 monitors a row reads cannot tell (TOO_WIDE_TO_RESOLVE). This rule is in a plan addendum dated 12 November 2026, committed before any reading under it, and the earlier word CONSISTENT for an upper end below one half is not used. The count of failed reads and the share of cannot tell by reason sit under each table. Sensor and monitor values are 24 hour means on UTC days, because the sensor service gives daily means on UTC days. Days where the two sensor channels disagree by 5 micrograms and 61 percent or more are left out, the cleaning rule of the same paper. Sensors near monitors may not be typical of sensors elsewhere. <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/airq/PLAN.md">Plan, notes and code</a>.</p>')
PAGES['/airq'] = page('/airq', "AIRQ | Air Sensors Against the EPA's Own Targets | Heuremen LLC", "AIRQ: how PurpleAir outdoor sensors within 200 metres of EPA regulatory monitors compare with the EPA's published performance targets for fine particulate sensors, 1 March to 30 June 2026, with 1 June to 29 September 2025 kept as the previous reading.", _AIRQBODY, hero_slim("AIRQ &middot; Air Sensors Against the EPA's Own Targets"))
_FEED.append(('/airq', "AIRQ : Air Sensors Against the EPA's Own Targets", "Air sensors against the EPA's own targets, live."))

# 29 Oct 2026: AILUMINATE, live. Plan: ailuminate/PLAN.md.
_AILUMINATEBODY = ('<h2>Do the published results stay what they say?</h2><p>MLCommons publishes percentile scores for AI systems on its AILuminate Safety benchmark, with a Detailed Results report for each system. It states that the reference set is fixed so that adding systems does not shift the scores of those already tested. We read the results page and every report, compare the page with its own reports, and keep every read so that any later change to a published score shows up.</p>'
  '<div id="ailuminate-live" class="bench-live">Loading.</div><script src="/ailuminate/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=ailuminate-all">Respond</a></p>'
  '<p>Source: <a href="https://mlcommons.org/ailuminate/safety/results/">mlcommons.org/ailuminate/safety/results/</a> and the public folder of Detailed Results it links. The page is checked against the reports. The band is 0 to 15 percent, open at 15, and the size that matters is 5 percent. A share of disagreements is CONSISTENT when the whole 95 percent interval sits inside the band and does not reach both 0 and 5 percent, ABOVE when the lower end is at or above 15 percent, and otherwise cannot tell, with the reason beside it. With 27 systems, 0 disagreements gives an interval that reaches both 0 and 5 percent, so it reads cannot tell (TOO_WIDE_TO_RESOLVE). This rule is in a plan addendum dated 12 November 2026, committed before any reading under it. Published scores kept: a system is changed when any of its 13 percentiles or its release month differs from the first value we stored. MLCommons states that the overall score weights all 12 categories equally. The table of overall against category percentiles sets each overall percentile beside the mean of its 12 category percentiles. <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/ailuminate/PLAN.md">Plan, notes and code</a>.</p>')
# 12 Nov 2026: AILUMINATE drift tests F to J (ailuminate_index/PLAN_ADDENDUM_drift.md, committed 3f671fc before any second label), read from summary_drift.json at build. Ledger rows ailuminate.drift.F and .H.
try:
    _dr = _jsonld.load(open(os.path.join(HERE, '..', 'ailuminate_index', 'summary_drift.json'), encoding='utf-8')); _dt = _dr['tests']
    _lab = list(_dt['F']['label_tuples'].keys())
    _AILUMINATEBODY += ('<h2>Versions and the evaluator</h2><p>MLCommons labels every result with its benchmark version, prompt set and evaluator version. Its release notes say it will not change what a score means without changing the label, and that results under an earlier label are not comparable. '
        'They also announce evaluator updates and margins of error for November and December under the current label.</p>'
        '<p>Labels seen since our first read on 29 October: %s. Systems whose label changed: %d of %d, %s (upper end %s percent). Systems whose scores changed under an unchanged label: %d of %d, %s. Beside them: %s %s '
        'How scores move between labels, item by item, and whether results under an earlier label stay published: these read cannot tell (NO_INTERVAL_FORMABLE) until a second label appears, and then run on their own. '
        'The tests were fixed and committed before any second label was read.</p>'
        % (', '.join(_lab) or 'none', _dt['F']['n'], _dt['F']['of'], _dt['F']['outcome'] + (' (%s)' % _dt['F']['reason'] if _dt['F'].get('reason') else ''), round(100 * _dt['F']['share_hi'], 1), _dt['H']['n'], _dt['H']['of'], _dt['H']['outcome'] + (' (%s)' % _dt['H']['reason'] if _dt['H'].get('reason') else ''), 'Labels, ' + _dt['F']['req13']['line'], 'Scores under a label, ' + _dt['H']['req13']['line']))
except Exception as _dexc:
    print('ailuminate drift section skipped:', _dexc)
PAGES['/ailuminate'] = page('/ailuminate', "AILUMINATE | MLCommons Safety Results, Kept and Checked | Heuremen LLC", "AILUMINATE: the MLCommons AILuminate Safety results page against its own reports, and whether published scores stay as published.", _AILUMINATEBODY, hero_slim("AILUMINATE &middot; MLCommons Safety Results, Kept and Checked"))
_FEED.append(('/ailuminate', "AILUMINATE : MLCommons Safety Results, Kept and Checked", "MLCommons AILuminate Safety results, kept and checked, live."))

# 29 Oct 2026: HPT, live. Plan: hpt/PLAN.md.
_HPTBODY = ('<h2>Is the price file where the rule says it is?</h2><p>The federal hospital price transparency rule asks each hospital to publish a machine-readable file of its standard charges, and to put a small text file named cms-hpt.txt at the root of its website that links to it. For every hospital website listed in Wikidata we check three things in order: the text file at the root, whether the file it links to opens as data, and whether that file starts with the template header names.</p>'
  '<div id="hpt-live" class="bench-live">Loading.</div><script src="/hpt/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=hpt-all">Respond</a></p>'
  '<p>Wikidata lists clinics and parts of health systems, and a hospital that belongs to a system can have its file at the system\'s domain, so a missing file at a hospital\'s own domain can be correct. Our full read of ten rows is in the plan. For that reason the first step reads CANNOT_TELL with the reason NO_INTERVAL_FORMABLE, because the share cannot be formed from a population that holds non-subjects. Steps two and three are scored against a claim of zero disagreement. ABOVE when the lower end of the 95 percent interval is at or above 5 percent, CONSISTENT when the whole interval lies below 5 percent, and CANNOT_TELL otherwise with a reason beside it. A share of 10 percent is the size that matters, so an interval that holds both zero and 10 percent reads TOO_WIDE_TO_RESOLVE, and so does a step with fewer than 30 websites compared. The rule moved to Standards 2.0 on 12 November 2026 by a plan addendum, and earlier readings stand under the rule they named. REQ-13 beside each step gives the websites that returned nothing, which sit outside the share, and the share of CANNOT_TELL by reason. Websites we could not open, that refused our user agent, or that are a page on a shared site are counted apart. JSON and zip files are not checked for the header because their key names can sit after the data. Every failing row of steps two and three that has been read in full is listed with what the read found. Failing rows not yet read in full are counted above the tables as awaiting a read in full. <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/hpt/PLAN.md">Plan, addenda and code</a>.</p>')
PAGES['/hpt'] = page('/hpt', "HPT | Hospital Price Files Against the Rule | Heuremen LLC", "HPT: whether the website of a United States hospital has the cms-hpt.txt file the federal price transparency rule asks for, whether the file it links resolves, and whether that file starts with the template header.", _HPTBODY, hero_slim("HPT &middot; Hospital Price Files Against the Rule"))
_FEED.append(('/hpt', "HPT : Hospital Price Files Against the Rule", "Hospital price-transparency files against the rule, live."))

# 29 Oct 2026: WEIGHTS, live. Plan: weights/PLAN.md.
_WEIGHTSBODY = ('<h2>Does a model name keep the same weights?</h2><p>A Hugging Face repository name is a pointer. Anyone who pins a model by name expects the weight files behind it to stay the same. We read the weight files of the 1,000 most downloaded models and read them again on later passes. A model that leaves the top 1,000 stays in the record, so the number of models read can be above 1,000. A model is the same when its weight files are identical on two passes, changed when a weight file was replaced, added or removed, and gone when the repository no longer resolves.</p>'
  '<div id="weights-live" class="bench-live">Loading.</div><script src="/weights/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=weights-all">Respond</a></p>'
  '<p>Source: the Hugging Face API, root folder of the main branch, content hashes recorded by Hugging Face. The changed share is read against a band of 0 to 1 percent, open at 1 percent, and 1 percent is also the size that matters. It is CONSISTENT when the whole 95 percent interval sits inside the band and ABOVE when the lower end is at or above 1 percent. Otherwise it reads cannot tell, with the reason beside it. This rule is in a plan addendum dated 12 November 2026, committed before any reading under it. The first pass has nothing to compare with and reads cannot tell (NO_INTERVAL_FORMABLE). The count of failed reads and the share of cannot tell by reason sit under the first table. The first table counts each model by its latest pair of passes, so a model that changed on one pass and stayed the same on the next is not in it. The table of models that changed on any pass counts each such model once, was defined after the first read and carries no outcome. Weights in subfolders and gated repositories are not read. A model can change on more than one pass, so change events can outnumber changed models. Every change is listed after it is read in full, and changes not yet read in full are counted above the tables as awaiting a read in full. <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/weights/PLAN.md">Plan, addenda and code</a>.</p>')
PAGES['/weights'] = page('/weights', "WEIGHTS | A Model Name Against Its Weights | Heuremen LLC", "WEIGHTS: whether the most downloaded open-weight models on Hugging Face keep the same weight files behind the same name, pass after pass.", _WEIGHTSBODY, hero_slim("WEIGHTS &middot; A Model Name Against Its Weights"))
_FEED.append(('/weights', "WEIGHTS : A Model Name Against Its Weights", "Open-weight model names against their weight files, pass after pass, live."))

# 29 Oct 2026: AIRLINE, live. Plan: airline/PLAN.md.
_AIRLINEBODY = ('<h2>Are schedules getting longer while flights are not?</h2><p>Every flight is published with a scheduled elapsed time, and the government on-time rate counts a flight as on time when it arrives within 15 minutes of schedule. If schedules lengthen while flown times stay the same, the on-time rate rises with no change in how long a flight takes. For each airline and route we take the median scheduled minutes minus the median flown minutes in January to August of 2019, 2025 and 2026, then the change between periods. Routes are the independent units.</p>'
  '<p>The live tables come first and show nothing when the FAA lists nothing. The FAA publishes the airport delay programs it is running now, with its own stated delay, and we keep every snapshot every few minutes. An airport closure the FAA lists is shown apart, because it is not a delay program, with the dates in its own notice. The Bureau of Transportation Statistics publishes flights only monthly, with a lag of about two months, and no free source gives a live schedule for every flight. So the live record is kept now and set against what flights delivered when each month of flight data is published: for each program, the FAA\'s stated average delay against the mean arrival delay of the flights scheduled into that airport in those hours. The tables below them are the monthly read of scheduled time against flown time.</p>'
  '<div id="airline-live" class="bench-live">Loading.</div><script src="/airline/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=airline-all">Respond</a></p>'
  '<p>Source: Bureau of Transportation Statistics, Reporting Carrier On-Time Performance. Cancelled and diverted flights are left out. An airline is ABOVE when the whole interval for its change lies above one minute, BELOW when it lies below minus one, and CONSISTENT when it lies within one minute either side and does not hold both zero and one minute. An interval that holds zero and also plus or minus one minute reads cannot tell (TOO_WIDE_TO_RESOLVE), because it cannot separate no change from a change of one minute. An interval that overlaps an edge reads cannot tell (STRADDLES_EDGE), and so does an airline with fewer than 30 routes (TOO_WIDE_TO_RESOLVE). The plan\'s one minute is taken as the size that matters in the addendum of 12 November 2026. Brackets in the change column are 95 percent percentile bootstrap intervals over routes, from 2,000 draws with seed 20261112 for each airline. The first read, of 29 October, used one random stream seeded 20261029 shared by all airlines and is shown beside the new reading. The count of airlines above reads cannot tell (NO_INTERVAL_FORMABLE) because the plan names no figure for a count. The share of flights 15 or more minutes late is shown beside the change and is not tested. Carrier codes are the file\'s own, so regional carriers appear under their own names. <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/airline/PLAN.md">Plan, addenda and code</a>.</p>')
PAGES['/airline'] = page('/airline', "AIRLINE | Scheduled Time Against Flown Time | Heuremen LLC", "AIRLINE: how much longer each US airline schedules a flight than the flight takes, 2019, 2025 and 2026, from the Bureau of Transportation Statistics record.", _AIRLINEBODY, hero_slim("AIRLINE &middot; Scheduled Time Against Flown Time"))
_FEED.append(('/airline', "AIRLINE : Scheduled Time Against Flown Time", "Scheduled flight time against flown flight time per airline, live."))

# 29 Oct 2026: FEDSEP, live. Plan: fedsep/PLAN.md.
_FEDSEPBODY = ('<h2>Do the Fed\'s stated ranges describe what happened?</h2><p>Each Summary of Economic Projections carries a table of average historical projection error ranges and says there is about a 70 percent probability that outcomes for real GDP, unemployment, consumer prices and the federal funds rate fall within those ranges of the projection. This page takes the September projections from 2015 to 2025, the median for the current year and the next year, and counts how often the outcome landed outside the stated range. A range that described the errors would leave about 30 percent outside.</p><p>The plan was committed before any outcome was compared, with one dated addendum and two notes from the full read. The intervals are made over years, because the four variables of one year share the same economy. The ranges describe past forecast errors by various forecasters, and one year outside is no contradiction. There is no rate, price or forecast of ours on this page.</p>'
  '<div id="fedsep-live" class="bench-live">Loading.</div><script src="/fedsep/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=fedsep-all">Respond</a></p>'
  '<p class="bench-note">Outside: the outcome differs from the median by more than the stated range for that variable and horizon. Above: the lower end of the interval is above 0.30. Below: the upper end is below 0.30, the share a 70 percent range would leave outside. Otherwise cannot tell (STRADDLES_EDGE). The figure 0.30 has no tolerance, so no row reads consistent (plan addendum of 12 November 2026). Until then the plan read consistent when 0.30 sat inside an interval no wider than 0.45, and the readings recorded under that rule stand. The federal funds rate is scored against the fourth-quarter average, as fixed in the plan, with a year-end row defined after the first read. Outcomes are the latest values from FRED. Projections: the Federal Reserve Board.</p>')
PAGES['/fedsep'] = page('/fedsep', "FEDSEP | The Fed's Stated Range Against What Happened | Heuremen LLC", "FEDSEP: how often the outcome fell outside the range the Federal Reserve's own Summary of Economic Projections says it should fall in about 70 percent of the time.", _FEDSEPBODY, hero_slim("FEDSEP &middot; The Fed's Stated Range Against What Happened"))
_FEED.append(('/fedsep', "FEDSEP : The Fed's Stated Range Against What Happened", "The Fed's stated projection ranges against outcomes, live."))

# 29 Oct 2026: REVISE, live. Plan: revise/PLAN.md.
_REVISEBODY = ('<h2>How far does a first estimate move?</h2><p>The Bureau of Labor Statistics states that the 90-percent confidence interval for the monthly change in total nonfarm employment is about plus or minus 122,000. This page counts how often, over the 120 most recent qualifying months, the first estimate was later moved by more than that: by the third release, and by the most recent value after the annual benchmark. The first, second and third estimates come from the BLS table of revisions between over-the-month estimates, and the most recent value from the BLS\'s current payroll series. Until 9 November 2026 they were read from the Philadelphia Fed\'s Real-Time Data Set, and the two sources gave the same counts (plan addendum 1).</p><p>The plan was committed before any revision was counted. The stated interval describes sampling error, and a later release also holds late reports and non-sampling error, so this is a count of how often the first estimate moved by more than the stated margin, not a test of the agency\'s method. The stated figure is today\'s and is applied to every month. There is no price, rate or forecast on this page.</p>'
  '<div id="revise-live" class="bench-live">Loading.</div><script src="/revise/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=revise-all">Respond</a></p>'
  '<p class="bench-note">Above: the lower end of the exceedance share is above 0.10, the share a 90-percent interval would leave. Below: the upper end is below 0.10. Otherwise cannot tell (STRADDLES_EDGE). The figure 0.10 has no tolerance, so no count reads consistent (plan addendum of 12 November 2026). Until then the plan read consistent when 0.10 sat inside an interval no wider than 0.12, and the third-release count was recorded consistent on 10 November 2026 under that rule. The outcome column uses the interval over months, the interval the plan names. The interval over calendar years treats each year as one unit, because the months of a year share a benchmark and consecutive months are not independent. It was defined after the first read and is shown with the outcome the same rule would give for it. Beside each count the page prints the number of failed reads and the share of cannot tell among the two readings, split by reason. Signed revisions are later minus first, in thousands of jobs. Sources: the BLS revisions table, the BLS payroll series and the BLS technical note.</p>')
PAGES['/revise'] = page('/revise', "REVISE | Stated Margin Against Later Revision | Heuremen LLC", "REVISE: how often the first estimate of monthly payroll change was later moved by more than the margin the Bureau of Labor Statistics states, read from the Bureau of Labor Statistics' own tables.", _REVISEBODY, hero_slim("REVISE &middot; Stated Margin Against Later Revision"))
_FEED.append(('/revise', "REVISE : Stated Margin Against Later Revision", "Payroll first estimates against the stated margin, live."))

# 29 Oct 2026: STACK, live. Plan: stack/PLAN.md.
_STACKBODY = ('<h2>What stacks when the results sit side by side?</h2><p>This page summarises every division and every live page, then puts their tests on one axis. Each page keeps its results under its own plan and rule. We read their public feeds and add no reading of our own: what was compared, how many failed, the share with its interval, and the outcome that page\'s rule gave. Shuffle at the top picks two tests at random, gives the difference in their shares and draws both on one axis. Ordering is an ordering of the table, not a ranking of anyone.</p><p>Each row has its own claim, its own population and its own rule, so two rows are not measures of the same thing. They are lined up only so they can be read together.</p>'
  '<div id="stack-live" class="bench-live">Loading.</div><script src="/stack/live.js?v=57f4e543" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=stack-all">Respond</a></p>'
  '<p class="bench-note">Above: the lower end of the interval clears that page\'s threshold. Consistent: the upper end is below it. Cannot tell: neither, or too few. A test whose feed could not be read shows as nothing returned. Pages that report many separate items are tallied by the outcome of each item below the table. Plan: the code folder.</p>')
PAGES['/stack'] = page('/stack', "STACK | Every Test, Side by Side | Heuremen LLC", "STACK: the headline test of every live page in one table, with the share that failed, its 95% interval and the outcome each page's own rule gave.", _STACKBODY, hero_slim("STACK &middot; Every Test, Side by Side"))
_FEED.append(('/stack', "STACK : Every Test, Side by Side", "Every test side by side, live."))

# 29 Oct 2026: PKGINSTALL, live. Plan: pkginstall/PLAN.md.
_PKGINSTALLBODY = ('<h2>Does the install command a project gives work today?</h2><p>The description of a PyPI project usually tells the reader to run pip install and its name. For the most downloaded projects this page takes the first such command, keeps it only if it names the project, and asks pip whether it could install it today on a fresh Python 3.12. The check is a dry run on wheels only, so no project\'s code is run. Projects with no command, a command with other options, a path or URL, a placeholder, or no wheel that fits are not comparable and are counted apart.</p><p>The plan was committed before the first project was read, and its dated addenda and notes are listed with it. The first two addenda came from full reads before anything was shown: a placeholder the reader did not recognise, and commands that install something other than the project. Both changed the reading and the whole read was run again each time.</p><p>The plan states a limit of this check. A command that names a project by its own PyPI name has little room to fail, so the check can barely show a failure. The upper bound on the failing share also treats projects as independent, although families of projects share one install line.</p><p>The outcome is read under Standards 2.0 from 12 November 2026, with the rule in the plan addendum dated that day. The share of disagreements is read against zero. It reads ABOVE when its whole 95 percent interval is at or above 0.05, CONSISTENT when the whole interval is below 0.05, and otherwise CANNOT_TELL with a reason. An interval that holds both 0 and 0.10 reads CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Fewer than 30 comparable rows also read CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Beside each share the page prints the count of failed reads and the share of CANNOT_TELL split by reason.</p>'
  '<div id="pkginstall-live" class="bench-live">Loading.</div><script src="/pkginstall/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=pkginstall-all">Respond</a></p>'
  '<p class="bench-note">Agree: pip would install the command. Disagree: pip fails because a target is not on PyPI, the requirements conflict, or no version matches although the project has a wheel that fits. Above: the lower end of the 95 percent interval of the failing share is above 0.10. Consistent: the upper end is below 0.05. Otherwise, and with fewer than 30 comparable projects, cannot tell. Source: the PyPI JSON API and pip.</p>')
PAGES['/pkginstall'] = page('/pkginstall', "PKGINSTALL | Stated Install Command Against Resolution | Heuremen LLC", "PKGINSTALL: the pip install command in each of the most downloaded PyPI projects' descriptions against whether pip can resolve it today, read every month.", _PKGINSTALLBODY, hero_slim("PKGINSTALL &middot; Stated Install Command Against Resolution"))
_FEED.append(('/pkginstall', "PKGINSTALL : Stated Install Command Against Resolution", "PyPI install commands against resolution, live."))

# 29 Oct 2026: SEAT, live. Plan: seat/PLAN.md.
_SEATBODY = ('<h2>Is the site we serve the site we published?</h2><p>Our release script checks the live site from the same machine that built it, which is one seat. This page reports a second seat. A GitHub runner on a network that is not ours fetches the menu, division and desk pages of this site and the same files from the public repository, compares them byte for byte, reads the age of each desk feed against a limit set from its schedule, and recomputes the hash chain of our records. We only relay what the runner saved to a public repository, and every probe is kept there.</p><p>The plan was committed before the first probe. A page counts as drifting only when it differs in two probes in a row, because a release writes the site before the repository. The rolling reading covers the last 24 probes. One runner is one seat and does not speak for every network. <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/nodes/drift">The probe, its plan and every saved probe are in our public repository</a>.</p>'
  '<div id="seat-live" class="bench-live">Loading.</div><script src="/seat/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=seat-all">Respond</a></p>'
  '<p class="bench-note">An incident is a run of consecutive probes that each had a drifting page, a feed past its limit or a broken chain, however many probes it lasts. The count of incidents in the last 24 probes is exact and is read against one bound of three. Above: three or more incidents. Below: fewer than three, which says only that the incidents stayed under the line at which the plan calls the claim failed, and the count is printed beside the word. Fewer than 24 probes reads cannot tell, too wide to resolve. A newest probe more than three hours old reads cannot tell, no interval formable. A probe whose control failed is a failed read, listed apart and outside the probes counted. The table of incidents names each one, with its first and last probe and what the probes saw. The probes are triggered by our scheduler, not by a timer. Code and every probe: the nodes repository, linked below.</p>')
PAGES['/seat'] = page('/seat', "SEAT | An Outside Seat Reads Our Pages | Heuremen LLC", "SEAT: a GitHub runner, not our machine, fetches every live page and feed of this site and compares them with the public repository and each feed's own limit.", _SEATBODY, hero_slim("SEAT &middot; An Outside Seat Reads Our Pages"))
_FEED.append(('/seat', "SEAT : An Outside Seat Reads Our Pages", "An outside seat reads our own pages, live."))

# 29 Oct 2026: SECRECORDS, live. Plan: secrecords/PLAN.md.
_SECRECORDSBODY = ('<h2>Do a domain\'s security records do what they say?</h2><p>A site that sends the HSTS preload directive asks to be put on browsers\' preload lists. Among the list\'s requirements, the base domain must send a max-age of at least one year and includeSubDomains, and a redirect it sends must carry the header itself. A domain that publishes an SPF record states which servers may send its mail, and the standard allows an evaluation ten DNS lookups before it fails. This page reads both records for the most visited domains and compares each with the rules for what it asks for. It does not say whether a domain is on a preload list or whether its mail is delivered.</p><p>The plan was committed before the first domain was read. Every mismatch was read in full, and the count still waiting for this is shown above the tables. Every SPF count was repeated with a second tool and a second script. Until 9 November the header was read on the page a redirect lands on, often another host. The list asks for the header on the base domain\'s own response, a redirect included, so the reader now follows no redirect, and every domain was read again (plan, Addendum 2).</p><p>The outcome is read under Standards 2.0 from 12 November 2026, with the rule in the plan addendum dated that day. Each claim, the HSTS preload header and the SPF lookup limit, is read on its own. The share of disagreements is read against zero. It reads ABOVE when its whole 95 percent interval is at or above 0.05, CONSISTENT when the whole interval is below 0.05, and otherwise CANNOT_TELL with a reason. An interval that holds both 0 and 0.10 reads CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Fewer than 30 comparable rows also read CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Beside each share the page prints the count of failed reads and the share of CANNOT_TELL split by reason.</p>'
  '<div id="secrecords-live" class="bench-live">Loading.</div><script src="/secrecords/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=secrecords-all">Respond</a></p>'
  '<p class="bench-note">Agree: the header on the base domain\'s own response has a max-age of at least one year and includeSubDomains, or the record needs ten lookups or fewer. Disagree: it does not. Above: the lower end of the 95 percent interval of the disagreement share is above 0.10. Consistent: the upper end is below 0.05. Otherwise, and with fewer than 30 comparable domains, cannot tell. The three descriptive rows carry no claim and no outcome. Sources: each domain\'s own HTTPS response (redirects are not followed), and Cloudflare\'s DNS over HTTPS service. Domain list: Tranco.</p>')
PAGES['/secrecords'] = page('/secrecords', "SECRECORDS | Security Records Against Their Own Rules | Heuremen LLC", "SECRECORDS: whether the HSTS preload header and the SPF record of the most visited domains meet the published rules for what they ask for, read every month, with every mismatch read in full.", _SECRECORDSBODY, hero_slim("SECRECORDS &middot; Security Records Against Their Own Rules"))
_FEED.append(('/secrecords', "SECRECORDS : Security Records Against Their Own Rules", "Security headers and mail records against their own rules, live."))

# 29 Oct 2026: CHANGE, live. Plan: change/PLAN.md.
_CHANGEBODY = ('<h2>When a vendor says something ends on a date, does the date hold?</h2><p>Model and API providers publish tables of what they are retiring and when. This page reads those tables from Anthropic, OpenAI, Google and Cloudflare on a schedule and keeps every reading. It lists what ends in the next 60 days, how much notice the tables that state a deprecation date gave, and every date that moved, was added or disappeared since the first reading. Open weight models carry no vendor shutdown date and are not in this version.</p><p>The plan was committed before the first reading. Each later change to it is a dated addendum in the plan: a parsing error found before anything was shown, a check of the saved pages before every pass, and a fix on 30 Oct for month names the reader had skipped. The test counts only dates that pass after we started watching, so it starts empty and fills as dates pass. Every move is read in full on the vendor\'s page. A moved date is not called a fault.</p>'
  '<div id="change-live" class="bench-live">Loading.</div><script src="/change/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=change-all">Respond</a></p>'
  '<p class="bench-note">Held: a stated date passed and never changed while we watched. Moved: it changed at least once before it passed. Removed early: the row left the page before its date. Fewer than 30 dates in the test reads cannot tell with the reason TOO_WIDE_TO_RESOLVE. Above is a lower end of the 95 percent interval at or above 5 percent, consistent is a whole interval below 5 percent, and 10 percent is the size that matters (plan addendum of 12 November 2026, Standards 2.0). REQ-13 beside the test row gives the readings that returned nothing and the share of cannot tell by reason. Notice is the days from a stated deprecation date to the shutdown date. Lifespan is the days from release to shutdown and is not notice. Google names that contain preview are shown apart from the other names. Sources are the vendors\' own deprecation pages, linked in the code folder.</p>')
PAGES['/change'] = page('/change', "CHANGE | Announced Shutdown Dates, Kept Over Time | Heuremen LLC", "CHANGE: the shutdown dates Anthropic, OpenAI, Google and Cloudflare publish, read again and again, with every move, addition and removal logged.", _CHANGEBODY, hero_slim("CHANGE &middot; Announced Shutdown Dates, Kept Over Time"))
_FEED.append(('/change', "CHANGE : Announced Shutdown Dates, Kept Over Time", "Vendor shutdown dates, read over time, live."))

# 29 Oct 2026: HFSIZE, live. Plan: hfsize/PLAN.md.
_HFSIZEBODY = ('<h2>Does the size in a model\'s name match the weights?</h2><p>Many model names state a size, such as 8B or 135M. For the most downloaded models on Hugging Face this page compares that size with the parameter count Hugging Face computes from the weight files. Names with no size, with several sizes, or with a mixture-of-experts pattern, and repositories that are quantized or packed, are not comparable and are counted apart.</p><p>The plan, with its dated addenda and notes, was committed before the first model was read. The band that counts as agreement was fixed before the first read. A row outside it is read in full and the reason written beside it. Rows not yet read in full are counted above the tables as awaiting a read in full. The page does not say that the name is wrong. Most rows are a name that states one part of a model or the model a draft checkpoint pairs with.</p><p>The outcome is read under Standards 2.0 from 12 November 2026, with the rule in the plan addendum dated that day. The share of disagreements is read against zero. It reads ABOVE when its whole 95 percent interval is at or above 0.05, CONSISTENT when the whole interval is below 0.05, and otherwise CANNOT_TELL with a reason. An interval that holds both 0 and 0.10 reads CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Fewer than 30 comparable rows also read CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Beside each share the page prints the count of failed reads and the share of CANNOT_TELL split by reason.</p>'
  '<div id="hfsize-live" class="bench-live">Loading.</div><script src="/hfsize/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=hfsize-all">Respond</a></p>'
  '<p class="bench-note">Agree: the weights hold between 0.70 and 1.35 times the stated size. Disagree: outside that band. Above: the lower end of the 95 percent interval of the disagreement share is above 0.10. Consistent: the upper end is below 0.05. Otherwise, and with fewer than 30 comparable models, cannot tell. The list of models where Hugging Face\'s own total contradicts its own breakdown was defined after the first read and carries no outcome. Source: the Hugging Face API.</p>')
PAGES['/hfsize'] = page('/hfsize', "HFSIZE | Stated Size Against the Weights | Heuremen LLC", "HFSIZE: the size in a Hugging Face model's name against the parameters its weight files hold, for the most downloaded models, with each mismatch read in full before it is listed.", _HFSIZEBODY, hero_slim("HFSIZE &middot; Stated Size Against the Weights"))
_FEED.append(('/hfsize', "HFSIZE : Stated Size Against the Weights", "Hugging Face model names against the weights, live."))

# 29 Oct 2026: HFLICENSE, live. Plan: hflicense/PLAN.md.
_HFLICENSEBODY = ('<h2>Does the license a repository states match the license file it carries?</h2><p>A Hugging Face model or dataset states its license in its card. Its repository may also carry a license file. For the most downloaded models and datasets this page compares the two. Repositories with no stated license, no license file in the root, or a license that is custom or named for one model are not comparable and are counted apart. The most common reason a repository cannot be compared is that it has no license file at all.</p><p>The plan, with its dated addenda, was committed before the first repository was read. Every reading error found along the way is logged there, with the read run again each time. A row where the tag and the file point to different licenses is read in full and the reason written beside it. The page does not say which side is right.</p><p>The outcome is read under Standards 2.0 from 12 November 2026, with the rule in the plan addendum dated that day. Models and datasets are read on their own. The share of disagreements is read against zero. It reads ABOVE when its whole 95 percent interval is at or above 0.05, CONSISTENT when the whole interval is below 0.05, and otherwise CANNOT_TELL with a reason. An interval that holds both 0 and 0.10 reads CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Fewer than 30 comparable rows also read CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Beside each share the page prints the count of failed reads and the share of CANNOT_TELL split by reason.</p>'
  '<div id="hflicense-live" class="bench-live">Loading.</div><script src="/hflicense/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=hflicense-all">Respond</a></p>'
  '<p class="bench-note">Agree: the stated license and the file\'s license fall in the same family, with Creative Commons qualifiers kept (BY, NC, SA, ND). Disagree: both are named and the families differ. Above: the lower end of the 95 percent interval of the disagreement share is above 0.10. Consistent: the upper end is below 0.05. Otherwise, and with fewer than 30 comparable repositories, cannot tell. The two mismatch groups and the share with no license file were defined after the first read and carry no outcome. Source: the Hugging Face API.</p>')
PAGES['/hflicense'] = page('/hflicense', "HFLICENSE | Stated License Against the License File | Heuremen LLC", "HFLICENSE: the license each of the most downloaded Hugging Face models and datasets states against the license file in its repository, read every month, with every mismatch read in full.", _HFLICENSEBODY, hero_slim("HFLICENSE &middot; Stated License Against the License File"))
_FEED.append(('/hflicense', "HFLICENSE : Stated License Against the License File", "Hugging Face stated licenses against license files, live."))

# 29 Oct 2026: PKGLICENSE, live. Plan: pkglicense/PLAN.md.
_PKGLICENSEBODY = ('<h2>Is the license a package states the license of its repository?</h2><p>A package on PyPI states its license in its metadata. The repository it points to carries a license file. For the most downloaded projects this page compares the two, as GitHub detects the repository\'s license, and groups each pair as agree, disagree, or not comparable. Projects with no GitHub repository, no stated license, or a repository license GitHub cannot identify are not comparable and are counted apart.</p><p>Every disagreement was read in full, both sides, before it was shown, and the reason is written beside it. The plan, with its two dated addenda, was committed before the first project was compared. The page does not say which side is right.</p><p>The outcome is read under Standards 2.0 from 12 November 2026, with the rule in the plan addendum dated that day. The share of disagreements is read against zero. It reads ABOVE when its whole 95 percent interval is at or above 0.05, CONSISTENT when the whole interval is below 0.05, and otherwise CANNOT_TELL with a reason. An interval that holds both 0 and 0.10 reads CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Fewer than 30 comparable rows also read CANNOT_TELL (TOO_WIDE_TO_RESOLVE). Beside each share the page prints the count of failed reads and the share of CANNOT_TELL split by reason.</p>'
  '<div id="pkglicense-live" class="bench-live">Loading.</div><script src="/pkglicense/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=pkglicense-all">Respond</a></p>'
  '<p class="bench-note">Agree: the stated license and the repository\'s license fall in the same family (MIT, Apache-2.0, BSD, GPL and so on, and GPL with no version agrees with either). Disagree: both are named and the families differ. Above: the share that disagree has a lower bound above 10 percent. Consistent: the upper bound is below 5 percent. Source: the PyPI JSON API, GitHub, and the public list of most downloaded projects.</p>')
PAGES['/pkglicense'] = page('/pkglicense', "PKGLICENSE | Stated License Against the Repository | Heuremen LLC", "PKGLICENSE: the license each of the most downloaded PyPI projects states against the license GitHub detects in the repository it points to, read every month, with every disagreement read in full.", _PKGLICENSEBODY, hero_slim("PKGLICENSE &middot; Stated License Against the Repository"))
_FEED.append(('/pkglicense', "PKGLICENSE : Stated License Against the Repository", "Package licenses against repository licenses, live."))

# 29 Oct 2026: SUPPORT, live. Plan: support/PLAN.md.
_SUPPORTBODY = ('<h2>Is a cycle that is stated as supported still being released?</h2><p>Vendors state how long each release cycle of a product is supported. This page takes those stated dates from endoflife.date, which collects them from the vendors, and holds them against the date of each cycle\'s latest release. A supported cycle counts as unreleased when it was released more than 400 days ago and its latest release is more than a year old. Unreleased is not abandoned: a vendor can patch through a channel the release date does not capture. The page counts what the record shows.</p><p>The first row is the test whose rules were committed before the first read. Its interval treats whole products as the independent units, because the cycles of one product are not independent. The two product-level rows were defined after the first read and are labelled as such. The plan and its three dated addenda are in the public repository.</p>'
  '<div id="support-live" class="bench-live">Loading.</div><script src="/support/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=support-all">Respond</a></p>'
  '<p class="bench-note">Supported, as the plan states it: the stated end of life is in the future or not stated, the stated support end, if any, has not passed, and the cycle was released more than 400 days ago. Cycles with no latest release date, no release date, an end of life stated only as passed, or a support end that has passed are counted apart and not tested. Until 10 November 2026 the code still tested a cycle whose support end had passed when its end of life was in the future. The plan wins, and the count under the old rule is shown once beside the first row (plan addendum 3). The dates are as endoflife.date gives them and are not checked against the vendors. In the list of unreleased cycles, False in the end-of-life column means no end of life is stated.</p>'
  '<p class="bench-note">Outcome rule, moved to <a href="/standard">Standards</a> 2.0 by a plan addendum on 12 November 2026: above means the lower end of the 95 percent interval of the unreleased share is at or above 5 percent. Consistent means the whole interval lies below 5 percent. Anything else is cannot tell, with a reason beside it. A share of 10 percent is the size that matters, so an interval that holds both zero and 10 percent reads TOO_WIDE_TO_RESOLVE, and so does any row with fewer than 30 cycles or products. An interval that overlaps the 5 percent edge reads STRADDLES_EDGE. Outcomes recorded before that date stand under the rule they named. REQ-13 beside each headline row gives the products that returned nothing and the share of cannot tell by reason. The first row is judged on its interval over products. The Wilson columns, which treat cycles as independent, are shown beside it and are not what the outcome uses.</p>')
PAGES['/support'] = page('/support', "SUPPORT | Stated Support Against Releases | Heuremen LLC", "SUPPORT: vendors' stated support and end-of-life dates for each release cycle against whether the cycle is still being released, read from endoflife.date every week.", _SUPPORTBODY, hero_slim("SUPPORT &middot; Stated Support Against Releases"))
_FEED.append(('/support', "SUPPORT : Stated Support Against Releases", "Stated support windows against release activity, live."))

# 29 Oct 2026: ARXIVDRIFT, live. Plan: arxivdrift/PLAN.md.
_ARXIVDRIFTBODY = ('<h2>The version we read against the version that stands now</h2><p>QIA and IRIS record the arXiv version of every study they index. Authors revise. For every indexed arXiv study this page shows whether a later version exists and whether the revision changed what we read: the numbers in the abstract, the title or wording, or the standing of the paper. Each study is read again every seven days. The plan was committed before the first comparison.</p><p>Nothing here says a revision is better or worse. A study whose abstract numbers changed gets a recount, read in full, before any row of ours changes. No claim is tested, so there is no verdict column.</p>'
  '<div id="arxivdrift-live" class="bench-live">Loading.</div><script src="/arxivdrift/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=arxivdrift-all">Respond</a></p>'
  '<p class="bench-note">Unchanged: the version we read is the newest. Revised, nothing changed: a later version exists with the same title, wording and abstract numbers. Revised wording: same numbers, different title or abstract. Revised numbers: the numbers in the abstract differ. Withdrawn: the paper itself. Source: the arXiv API.</p>')
PAGES['/arxivdrift'] = page('/arxivdrift', "ARXIVDRIFT | Studies Read, Then Revised | Heuremen LLC", "ARXIVDRIFT: for every arXiv study QIA and IRIS index, whether a later version exists and whether the revision changed the numbers, wording or standing of what we read, read every week.", _ARXIVDRIFTBODY, hero_slim("ARXIVDRIFT &middot; Studies Read, Then Revised"))
_FEED.append(('/arxivdrift', "ARXIVDRIFT : Studies Read, Then Revised", "Indexed arXiv studies against the version that stands now, live."))
_CDBODY = ('<section class="bench"><h2>Stated Update Cadence Against Delivered</h2>'
  '<p>Government data portals publish, for each dataset, how often it is updated and when it last changed, in the standard data.json. This page holds the stated cadence against the last modified date. A series is on schedule if its margin, twice its stated interval minus its age, is above zero and behind if the margin is below zero. Read against that bound of zero a series is above or below it and never consistent (plan addendum of 12 November 2026). The interval used is at least two days, so a daily series is behind after four days, and a date with no time of day is read as the end of that day. Records that share a landing page are one series, because archived releases cannot change. The rules were committed before any portal was read, except that the series rule was decided after the first portal read and before any outcome was shown (plan, addendum 1).</p>'
  '<div id="cadence-live" class="bench-live">Loading.</div><script src="/cadence/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=cadence-all">Respond</a></p>'
  '<p class="bench-note">The modified date is what the publisher reports. On a sample of each portal\'s download links, the file\'s own date is compared with it and shown. Series with a cadence that is not a regular interval, or with no readable date, are counted as cannot tell (NO_INTERVAL_FORMABLE), since no margin can be formed. A portal whose file could not be read is listed apart and is in no share. A stated duration may carry a decimal, so R/P3.5D is 3.5 days, and when records of one series share the newest date and state different cadences, the series is read against the longest of them. Both rules were written on 10 November 2026, after the data, and the count under the old rules is shown beside the total (plan addendum 2). No ranking of agencies.</p></section>')
PAGES['/cadence'] = page('/cadence', 'CADENCE | Stated Update Cadence Against Delivered | Heuremen LLC', 'CADENCE: what government data portals state about how often datasets update, held against when they last changed, with the series furthest past their cadence.', _CDBODY, hero_slim('CADENCE &middot; Stated Updates Against Delivered'))
_FEED.append(('/cadence', 'CADENCE: Stated Update Cadence Against Delivered', 'What government data portals state about update cadence, against when datasets last changed.'))
_FEED.append(('/hermes/model', 'HERMES: Held Every Record, Measured Every Statement', 'What AI hardware vendors state, held against the published MLCommons results.'))
# 28 Oct 2026 (his word): ATLAS electricity layer. Data: atlas/electricity/ (build_electricity.py), EIA-861 2024 sales and EIA state generation tables.
_EL = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'electricity', 'electricity.json'))); _EU = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'electricity', 'utilities.json')))['utilities']
_EMI = open(os.path.join(HERE, '..', 'atlas', 'electricity', 'map_industrial.svg'), encoding='utf-8').read(); _EMC = open(os.path.join(HERE, '..', 'atlas', 'electricity', 'map_commercial.svg'), encoding='utf-8').read()
def _ef(v, d=1): return '&mdash;' if v is None else f'{v:.{d}f}'
def _legend(sec):
    L = _EL['legend'][sec]; sw = ''.join(f'<rect x="{4 + i * 150}" y="2" width="22" height="12" class="s{i + 1}"/><text x="{30 + i * 150}" y="12" class="lgt">{_e(L[i])}</text>' for i in range(5))
    return f'<svg viewBox="0 0 760 18" width="760" height="18" role="img" aria-label="Legend: cents per kilowatthour, {sec} customers" class="elmap lg">{sw}</svg>'
_ST = _EL['states']
_srows = ''.join(
    f'<tr><td>{_e(v["name"])}</td><td>{_ef(v["sectors"]["industrial"]["price"])}</td><td>{_ef(v["sectors"]["commercial"]["price"])}</td><td>{_ef(v["sectors"]["residential"]["price"])}</td>'
    + (''.join(f'<td>{_ef(v["generation"]["share"][k])}</td>' for k in ('coal', 'gas', 'nuclear', 'hydro', 'wind', 'solar', 'other')) if v['generation'] else '<td>&mdash;</td>' * 7)
    + f'<td>{v["data_centers"]["epoch_mw"]:,}</td><td>{v["data_centers"]["osm_features"]:,}</td></tr>'
    for ab, v in sorted(_ST.items(), key=lambda kv: kv[1]['name']))
_US = _EL['us']
_grows = ''.join(f'<tr><td>{n_}</td><td>{_US["generation"]["mwh"][k] / 1e6:,.1f}</td><td>{_ef(_US["generation"]["share"][k])}</td></tr>' for k, n_ in (('gas', 'Natural gas'), ('nuclear', 'Nuclear'), ('coal', 'Coal'), ('wind', 'Wind'), ('hydro', 'Hydro, conventional'), ('solar', 'Solar, utility-scale'), ('other', 'Other and storage')))
_tot_own = sum(o['sales_twh'] for o in _US['ownership'])
_orows = ''.join(f'<tr><td>{_e(o["type"])}</td><td>{o["utilities"]:,}</td><td>{o["sales_twh"]:,.1f}</td><td>{o["sales_twh"] / _tot_own * 100:.1f}</td></tr>' for o in _US['ownership'] if o['sales_twh'] > 0)
_top = sorted([u for u in _EU if u['commercial_sales_mwh'] + u['industrial_sales_mwh'] > 0 and u['utility_number'] != 99999], key=lambda u: -(u['commercial_sales_mwh'] + u['industrial_sales_mwh']))[:40]
_urows = ''.join(f'<tr><td>{_e(u["name"])}</td><td>{_e(u["state"])}</td><td>{_e(u["ownership"])}</td><td>{_ef(u["industrial_price"])}</td><td>{_ef(u["commercial_price"])}</td><td>{_ef(u["residential_price"])}</td><td>{(u["commercial_sales_mwh"] + u["industrial_sales_mwh"]) / 1e6:,.1f}</td></tr>' for u in _top)
_USP = _US['sectors']
_ELBODY = ('<section class="legal"><p class="meta"><a href="/atlas">ATLAS</a> &middot; Built Infrastructure &middot; Electricity</p>'
 '<h2>What electricity costs by state, and where it comes from</h2>'
 f'<p>Average prices paid for electricity in 2024, by state, with the data centers from the <a href="/atlas">ATLAS map</a> drawn over them. In the United States as a whole, the average was {_ef(_USP["industrial"]["price"], 2)} cents per kilowatthour for industrial customers, {_ef(_USP["commercial"]["price"], 2)} for commercial customers and {_ef(_USP["residential"]["price"], 2)} for residential customers. These are averages of what customers paid, which is revenue divided by sales. They are not tariff rates, and a data center may buy under a negotiated contract that differs from its state average.</p>'
 '<p>The 2024 prices on this page can be switched on the one <a href="/atlas">ATLAS map</a> with the data centers, power plants and carbon intensity. The cost of a year of electricity at the data centers&rsquo; stated power is on that page.</p>'
 '<h2>Industrial customers</h2><p class="meta">Cents per kilowatthour, 2024. Small dots are OpenStreetMap data center features. Rings are Epoch AI sites sized by power.</p>' + _EMI + _legend('industrial')
 + '<h2>Commercial customers</h2>' + _EMC + _legend('commercial')
 + '<p class="meta">Alaska and Hawaii are in the table and the data file and are not drawn. Connecticut, Delaware, the District of Columbia, Maryland, Massachusetts, New Hampshire, New Jersey, Rhode Island and Vermont are shaded and not labeled.</p>'
 '<h2>By state</h2><p>Prices are in cents per kilowatthour. Generation shares are each source&rsquo;s share of the net electricity generated in the state in 2024. Generation is what the state&rsquo;s plants produced, not what its customers used, and states import and export power. Epoch AI MW is the current power of the AI data centers in the Epoch AI dataset whose map point falls in the state. A site with no map point is not in this column, so Amazon Madison Mega Site (284 MW, Mississippi by its address text) is counted on the main ATLAS map&rsquo;s cost table but not here. OpenStreetMap features is the number of features tagged as data centers.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>State</th><th>Industrial</th><th>Commercial</th><th>Residential</th><th>Coal %</th><th>Gas %</th><th>Nuclear %</th><th>Hydro %</th><th>Wind %</th><th>Solar %</th><th>Other %</th><th>Epoch AI MW</th><th>OpenStreetMap features</th></tr></thead><tbody>' + _srows + '</tbody></table></div>'
 '<h2>Where United States electricity comes from</h2><p>Net generation by energy source in 2024, all states.</p><div class="scroll"><table class="mtx"><thead><tr><th>Source</th><th>Terawatthours</th><th>Share, %</th></tr></thead><tbody>' + _grows + '</tbody></table></div>'
 '<p class="meta">Other and storage is total generation minus the named sources. It includes petroleum, biomass, geothermal, other gases and pumped storage. Solar here is utility-scale and leaves out rooftop systems.</p>'
 '<h2>Who sells it</h2><p>Retail sales in 2024 by type of provider, all customer classes. Retail power marketers sell the energy and the local utility delivers it.</p><div class="scroll"><table class="mtx"><thead><tr><th>Provider type</th><th>Providers</th><th>Sales, terawatthours</th><th>Share, %</th></tr></thead><tbody>' + _orows + '</tbody></table></div>'
 '<p class="meta">EIA adjustment is the entry named Adjustment 2024 in the EIA table. It is not a provider.</p>'
 '<h2>Largest utilities by commercial and industrial sales</h2><p>Utilities that sell energy and delivery together, ranked by terawatthours sold to commercial and industrial customers. Prices are in cents per kilowatthour. The data file lists every utility.</p><div class="scroll"><table class="mtx"><thead><tr><th>Utility</th><th>State</th><th>Type</th><th>Industrial</th><th>Commercial</th><th>Residential</th><th>Commercial and industrial TWh</th></tr></thead><tbody>' + _urows + '</tbody></table></div>'
 '<p><a class="btn ghost" href="/atlas/electricity.json">States (JSON)</a> &middot; <a class="btn ghost" href="/atlas/utilities.json">Utilities (JSON)</a></p>'
 '<h2>Sources</h2><div class="scroll"><table class="mtx"><thead><tr><th>Source</th><th>What it holds</th><th>Year</th></tr></thead><tbody>'
 '<tr><td><a href="https://www.eia.gov/electricity/data/eia861/">U.S. Energy Information Administration, EIA-861</a></td><td>Revenue, sales and customers by utility and customer class. State prices are computed here by the rule EIA gives under its table: revenue sums Parts A, B, C and D, sales sum Parts A, B and D.</td><td>2024</td></tr>'
 '<tr><td><a href="https://www.eia.gov/electricity/data/state/">U.S. Energy Information Administration, State Historical Tables</a></td><td>Net generation by state and energy source, Total Electric Power Industry.</td><td>2024</td></tr>'
 '<tr><td>ATLAS data centers</td><td>OpenStreetMap (ODbL) and Epoch AI (CC BY 4.0), as on the <a href="/atlas">ATLAS map</a>.</td><td>pulled 28 Oct 2026</td></tr>'
 '</tbody></table></div>'
 '<p class="meta">Read once on 28 October 2026. EIA publishes the annual 861 sales table and the state generation tables once a year, and these pages are not refreshed on a schedule.</p>'
 '<p class="meta">EIA data are U.S. government data. The state data file contains counts derived from OpenStreetMap data under the <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. To correct or remove an entry, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
PAGES['/atlas/electricity'] = page('/atlas/electricity', 'Electricity | ATLAS | Heuremen LLC', 'ATLAS electricity: average 2024 prices by state for industrial, commercial and residential customers, generation by source, provider types and utilities, with the data centers drawn over the maps.', _ELBODY, hero_slim('ATLAS &middot; Electricity'))
_FEED.append(('/atlas/electricity', 'ATLAS: Electricity by state', 'Average prices paid for electricity by state in 2024, generation by source, provider types, with data centers drawn over the maps.'))
# 28 Oct 2026 (his word): ATLAS power plants. Data: atlas/electricity/plants.json, map_plants.svg, plants_summary.json (build_plants.py), EIA-860 2024.
_PLS = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'electricity', 'plants_summary.json'))); _PLM = open(os.path.join(HERE, '..', 'atlas', 'electricity', 'map_plants.svg'), encoding='utf-8').read()
_PLR = [l.rstrip('\n') for l in open(os.path.join(HERE, '..', 'atlas', 'electricity', 'plants_rows_text.txt'), encoding='utf-8')]
_FUELS = [('gas', 'Natural gas'), ('coal', 'Coal'), ('nuclear', 'Nuclear'), ('hydro', 'Hydro'), ('wind', 'Wind'), ('solar', 'Solar'), ('storage', 'Storage'), ('oil', 'Petroleum'), ('other', 'Other')]
_pl_leg = '<svg viewBox="0 0 760 20" width="760" height="20" role="img" aria-label="Legend of fuel colors" class="atlasmap plmap">' + ''.join(f'<circle cx="{10 + i * 84}" cy="10" r="6" class="f-{k}"/><text x="{20 + i * 84}" y="14" class="lgt">{_e(n_)}</text>' for i, (k, n_) in enumerate(_FUELS)) + '</svg>'
def _plrow(line, ncols=None): return line.split(' ', 1)
_fuel_rows = ''.join(f'<tr><td>{_e(n_)}</td><td>{f_["gw"]:,.1f}</td><td>{f_["plants"]:,}</td><td>{f_["share"]:.1f}</td></tr>' for k, n_ in _FUELS for f_ in _PLS['fuel'] if f_['fuel'] == k)
_PLANT_ROWS = ''.join(f'<tr><td><a href="https://www.eia.gov/electricity/data/browser/#/plant/{p_["code"]}/">{_e(p_["name"])}</a></td><td>{_e(p_["state"])}</td><td>{_e(p_["utility"])}</td><td>{_e(dict(_FUELS)[p_["dominant"]])}</td><td>{p_["total_mw"]:,.0f}</td></tr>' for p_ in _oj.load(open(os.path.join(HERE, '..', 'atlas', 'electricity', 'plants.json')))['plants'][:20])
_ST_ROWS = ''.join('<tr><td>' + ' '.join(l.split(' ')[1:-10]) + '</td>' + ''.join(f'<td>{c_}</td>' for c_ in l.split(' ')[-10:]) + '</tr>' for l in _PLR if l.startswith('STATE '))
_PLBODY = ('<section class="legal"><p class="meta"><a href="/atlas">ATLAS</a> &middot; Built Infrastructure &middot; Power plants</p>'
 '<h2>Operating power plants in the United States</h2>'
 f'<p>Every operating plant in the U.S. Energy Information Administration&rsquo;s monthly generator inventory for September 2026, {_PLS["plants_operating"]:,} plants with {_PLS["total_gw"]:,.1f} gigawatts of nameplate capacity. The map draws the {_PLS["plants_drawn"]:,} plants of {_PLS["min_mw_drawn"]:.0f} megawatts or more in the contiguous states, colored by the fuel with the most capacity at the plant and sized by capacity. Rings are the AI data centers from the <a href="/atlas">ATLAS map</a>. Nameplate capacity is what a plant is rated for, not what it produces. For generation and prices by state see <a href="/atlas/electricity">Electricity</a>.</p>'
 + '<p>Operating plants can be switched on the one <a href="/atlas">ATLAS map</a> with the data centers, planned plants, prices and carbon intensity.</p>' + _PLM + _pl_leg +
 '<p class="meta">Plants below the size cut-off and plants in Alaska and Hawaii are in the table and the data file and are not drawn.</p>'
 '<h2>Capacity by fuel</h2><div class="scroll"><table class="mtx"><thead><tr><th>Fuel</th><th>Gigawatts</th><th>Plants</th><th>Share of capacity, %</th></tr></thead><tbody>' + _fuel_rows + '</tbody></table></div>'
 '<p class="meta">Plants are counted under the fuel with the most capacity at the plant. Gigawatts count every operating generator at its own fuel. Storage is batteries and pumped storage. Other includes biomass, geothermal, waste and other gases.</p>'
 '<h2>The twenty largest plants</h2><div class="scroll"><table class="mtx"><thead><tr><th>Plant</th><th>State</th><th>Operator</th><th>Main fuel</th><th>Megawatts</th></tr></thead><tbody>' + _PLANT_ROWS + '</tbody></table></div>'
 '<h2>Capacity by state, gigawatts</h2><div class="scroll"><table class="mtx"><thead><tr><th>State</th>' + ''.join(f'<th>{_e(n_)}</th>' for _, n_ in _FUELS) + '<th>All</th></tr></thead><tbody>' + _ST_ROWS + '</tbody></table></div>'
 '<p><a class="btn ghost" href="/atlas/plants.json">Every plant (JSON)</a></p>'
 '<h2>Source</h2><div class="scroll"><table class="mtx"><thead><tr><th>Source</th><th>What it holds</th><th>Year</th></tr></thead><tbody>'
 '<tr><td><a href="https://www.eia.gov/electricity/data/eia860m/">U.S. Energy Information Administration, EIA-860M</a></td><td>Every generator with its fuel, prime mover, nameplate capacity and status, and a map link for each plant that carries its coordinates. We keep generators with status operating and group fuels by their EIA codes, listed in the data file.</td><td>September 2026</td></tr>'
 '<tr><td>ATLAS data centers</td><td>Epoch AI (CC BY 4.0), as on the <a href="/atlas">ATLAS map</a>.</td><td>pulled 28 Oct 2026</td></tr></tbody></table></div>'
 '<p class="meta">Read once on 28 October 2026. EIA revises its generator inventory each month and these pages do not follow the revisions.</p>'
 '<p class="meta">EIA data are U.S. government data. To correct or remove an entry, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
PAGES['/atlas/power-plants'] = page('/atlas/power-plants', 'Power plants | ATLAS | Heuremen LLC', 'ATLAS power plants: every operating United States power plant from EIA-860 by fuel and capacity, with the AI data centers drawn over the map.', _PLBODY, hero_slim('ATLAS &middot; Power plants'))
_FEED.append(('/atlas/power-plants', 'ATLAS: Power plants', 'Operating United States power plants by fuel and capacity from EIA-860, with AI data centers drawn over the map.'))
# 28 Oct 2026 (his word): ATLAS carbon. Data: atlas/electricity/carbon.json, map_carbon.svg (build_carbon.py), EPA eGRID2023.
_CB = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'electricity', 'carbon.json'))); _CBM = open(os.path.join(HERE, '..', 'atlas', 'electricity', 'map_carbon.svg'), encoding='utf-8').read()
_CBR = [l.rstrip('\n') for l in open(os.path.join(HERE, '..', 'atlas', 'electricity', 'carbon_rows_text.txt'), encoding='utf-8')]
_cb_leg = '<svg viewBox="0 0 760 18" width="760" height="18" role="img" aria-label="Legend: pounds of carbon dioxide per megawatthour" class="elmap lg">' + ''.join(f'<rect x="{4 + i * 150}" y="2" width="22" height="12" class="s{i + 1}"/><text x="{30 + i * 150}" y="12" class="lgt">{_e(_CB["legend"][i])}</text>' for i in range(5)) + '</svg>'
_cb_states = ''.join('<tr><td>' + ' '.join(l.split(' ')[1:-5]) + '</td>' + ''.join(f'<td>{c_}</td>' for c_ in l.split(' ')[-5:]) + '</tr>' for l in _CBR if l.startswith('STATE '))
_cb_subs = ''.join('<tr><td>' + ' '.join(l.split(' ')[1:-5]) + '</td>' + f'<td>{l.split(" ")[-5]}</td>' + ''.join(f'<td>{c_}</td>' for c_ in l.split(' ')[-4:]) + '</tr>' for l in _CBR if l.startswith('SUB '))
_cb_us = _CBR[0].split(' ')
_CBBODY = ('<section class="legal"><p class="meta"><a href="/atlas">ATLAS</a> &middot; Built Infrastructure &middot; Carbon</p>'
 '<h2>Carbon dioxide per megawatthour of electricity, by state</h2>'
 f'<p>Pounds of carbon dioxide emitted per megawatthour of net electricity generated in each state in 2023, from the U.S. Environmental Protection Agency&rsquo;s eGRID database, with the data centers from the <a href="/atlas">ATLAS map</a> drawn over it. Across the United States the figure was {_cb_us[1]} pounds per megawatthour. The rate covers all generation in the state, clean and fossil, and counts what the state&rsquo;s plants emit. It is not the carbon in the power its customers use, because states import and export electricity.</p>'
 + '<p>Carbon intensity can be switched on the one <a href="/atlas">ATLAS map</a> with the data centers, power plants and prices.</p>' + _CBM + _cb_leg +
 '<p class="meta">Alaska and Hawaii are in the tables and are not drawn. Connecticut, Delaware, the District of Columbia, Maryland, Massachusetts, New Hampshire, New Jersey, Rhode Island and Vermont are shaded and not labeled. Small dots are OpenStreetMap data center features and rings are Epoch AI sites sized by power.</p>'
 '<h2>By state</h2><p>Output emission rates are in pounds per megawatthour of net generation. Net generation is in terawatthours. Epoch AI MW is the current power of the AI data centers in the Epoch AI dataset whose map point falls in the state. A site with no map point is not in this column, so Amazon Madison Mega Site (284 MW, Mississippi by its address text) is counted on the main ATLAS map&rsquo;s cost table but not here.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>State</th><th>CO2</th><th>NOx</th><th>SO2</th><th>Net generation, TWh</th><th>Epoch AI MW</th></tr></thead><tbody>' + _cb_states + '</tbody></table></div>'
 '<h2>By grid region</h2><p>The 27 eGRID subregions. Regions cross state lines and follow the grid, not the map of states.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>Region</th><th>Code</th><th>CO2</th><th>NOx</th><th>SO2</th><th>Net generation, TWh</th></tr></thead><tbody>' + _cb_subs + '</tbody></table></div>'
 f'<p><a class="btn ghost" href="/atlas/carbon.json">States and regions (JSON)</a></p>'
 + open(os.path.join(HERE, '..', 'atlas', 'stated', 'stated_carbon.html'), encoding='utf-8').read() +
 '<h2>Source</h2><div class="scroll"><table class="mtx"><thead><tr><th>Source</th><th>What it holds</th><th>Year</th></tr></thead><tbody>'
 '<tr><td><a href="https://www.epa.gov/egrid">U.S. Environmental Protection Agency, eGRID</a></td><td>Total output emission rates for carbon dioxide, nitrogen oxides and sulfur dioxide by state and by grid subregion, from plant reports, with net generation.</td><td>2023</td></tr>'
 '<tr><td>ATLAS data centers</td><td>OpenStreetMap (ODbL) and Epoch AI (CC BY 4.0), as on the <a href="/atlas">ATLAS map</a>.</td><td>pulled 28 Oct 2026</td></tr></tbody></table></div>'
 '<p class="meta">Read once on 28 October 2026. EPA publishes eGRID about once a year, and 2023 is the latest edition on its download page.</p>'
 '<p class="meta">EPA data are U.S. government data. The state counts of data centers derive from OpenStreetMap data under the <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. To correct or remove an entry, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
PAGES['/atlas/carbon'] = page('/atlas/carbon', 'Carbon Intensity of Electricity by State | ATLAS | Heuremen LLC', 'ATLAS carbon: pounds of carbon dioxide per megawatthour of electricity generated by state and grid region from EPA eGRID 2023, with data centers drawn over the map.', _CBBODY, hero_slim('ATLAS &middot; Carbon'))
_FEED.append(('/atlas/carbon', 'ATLAS: Carbon by state and grid region', 'Pounds of CO2 per megawatthour of electricity generated by state and grid region from EPA eGRID 2023, with data centers drawn over the map.'))
# 28 Oct 2026 (his word): ATLAS planned power plants. Data: atlas/electricity/planned.json, map_planned.svg (build_planned.py), EIA-860M September 2026, Planned sheet.
_PNS = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'electricity', 'planned_summary.json'))); _PNM = open(os.path.join(HERE, '..', 'atlas', 'electricity', 'map_planned.svg'), encoding='utf-8').read()
_PNR = [l.rstrip('\n') for l in open(os.path.join(HERE, '..', 'atlas', 'electricity', 'planned_rows_text.txt'), encoding='utf-8')]
_PNP = _oj.load(open(os.path.join(HERE, '..', 'atlas', 'electricity', 'planned.json')))['plants'][:20]
_pn_fuel = ''.join('<tr><td>' + ' '.join(l.split(' ')[1:-6]) + '</td>' + ''.join(f'<td>{c_}</td>' for c_ in l.split(' ')[-6:]) + '</tr>' for l in _PNR if l.startswith('FUEL '))
_pn_year = ''.join('<tr><td>' + ' '.join(l.split(' ')[1:-10]) + '</td>' + ''.join(f'<td>{c_}</td>' for c_ in l.split(' ')[-10:]) + '</tr>' for l in _PNR if l.startswith('YEAR '))
_pn_state = ''.join('<tr><td>' + ' '.join(l.split(' ')[1:-10]) + '</td>' + ''.join(f'<td>{c_}</td>' for c_ in l.split(' ')[-10:]) + '</tr>' for l in _PNR if l.startswith('STATE '))
_pn_plants = ''.join(f'<tr><td><a href="https://www.eia.gov/electricity/data/browser/#/plant/{p_["code"]}/">{_e(p_["name"])}</a></td><td>{_e(p_["state"])}</td><td>{_e(p_["utility"])}</td><td>{_e(dict(_FUELS)[p_["dominant"]])}</td><td>{p_["total_mw"]:,.0f}</td><td>{p_["first_year"]}</td></tr>' for p_ in _PNP)
_pn_fuelhd = ''.join(f'<th>{_e(n_)}</th>' for _, n_ in _FUELS)
_PNBODY = ('<section class="legal"><p class="meta"><a href="/atlas">ATLAS</a> &middot; Built Infrastructure &middot; Planned power plants</p>'
 '<h2>Power plants that owners have reported as planned</h2>'
 f'<p>Generators that owners report as planned in the U.S. Energy Information Administration&rsquo;s monthly inventory for September 2026: {_PNS["total_gw"]:,.1f} gigawatts of nameplate capacity at {_PNS["plants"]:,} plants. The map draws the {_PNS["plants_drawn"]:,} plants of 25 megawatts or more in the contiguous states, colored by the fuel with the most planned capacity at the plant and sized by that capacity. Rings are the AI data centers from the <a href="/atlas">ATLAS map</a>. Planned is a stage in EIA&rsquo;s list and not a promise. Owners report the stage and the planned year, and projects are delayed and canceled.</p>'
 + '<p>Planned plants can be switched on the one <a href="/atlas">ATLAS map</a> with the data centers, operating plants, prices and carbon intensity.</p>' + _PNM + _pl_leg +
 '<p class="meta">Plants below the size cut-off and plants in Alaska and Hawaii are in the tables and the data file and are not drawn.</p>'
 '<h2>By fuel and stage</h2><p>Gigawatts of nameplate capacity. The stages are EIA&rsquo;s status codes grouped. Under construction or complete is status U, V or TS, which covers under construction at 50 percent or less, over 50 percent, and construction complete but not yet in commercial operation. Approvals received is T, approvals pending is L, and approvals not started is P.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>Fuel</th><th>Under construction or complete</th><th>Approvals received</th><th>Approvals pending</th><th>Approvals not started</th><th>All</th><th>Share, %</th></tr></thead><tbody>' + _pn_fuel + '</tbody></table></div>'
 '<h2>By planned year</h2><p>Gigawatts by the year owners report for the start of operation. Years before 2027 are grouped with 2026.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>Year</th>' + _pn_fuelhd + '<th>All</th></tr></thead><tbody>' + _pn_year + '</tbody></table></div>'
 '<h2>The twenty largest planned plants</h2><div class="scroll"><table class="mtx"><thead><tr><th>Plant</th><th>State</th><th>Owner</th><th>Main fuel</th><th>Megawatts</th><th>First planned year</th></tr></thead><tbody>' + _pn_plants + '</tbody></table></div>'
 '<h2>By state, gigawatts</h2><div class="scroll"><table class="mtx"><thead><tr><th>State</th>' + _pn_fuelhd + '<th>All</th></tr></thead><tbody>' + _pn_state + '</tbody></table></div>'
 '<p><a class="btn ghost" href="/atlas/planned.json">Every planned plant (JSON)</a></p>'
 '<h2>Source</h2><div class="scroll"><table class="mtx"><thead><tr><th>Source</th><th>What it holds</th><th>Month</th></tr></thead><tbody>'
 '<tr><td><a href="https://www.eia.gov/electricity/data/eia860m/">U.S. Energy Information Administration, EIA-860M</a></td><td>The Planned sheet: each planned generator with its fuel, prime mover, nameplate capacity, status, planned year and coordinates. The inventory is preliminary and EIA revises it each month.</td><td>September 2026</td></tr>'
 '<tr><td>ATLAS data centers</td><td>Epoch AI (CC BY 4.0), as on the <a href="/atlas">ATLAS map</a>.</td><td>pulled 28 Oct 2026</td></tr></tbody></table></div>'
 '<p class="meta">Read once on 28 October 2026. EIA revises its generator inventory each month and these pages do not follow the revisions.</p>'
 '<p class="meta">EIA data are U.S. government data. To correct or remove an entry, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
PAGES['/atlas/planned-plants'] = page('/atlas/planned-plants', 'Planned power plants | ATLAS | Heuremen LLC', 'ATLAS planned power plants: generators that owners report as planned in the EIA monthly inventory for September 2026, by fuel, stage, year and state, with AI data centers drawn over the map.', _PNBODY, hero_slim('ATLAS &middot; Planned power plants'))
_FEED.append(('/atlas/planned-plants', 'ATLAS: Planned power plants', 'Planned United States power plants by fuel, stage, year and state from the EIA monthly inventory for September 2026, with AI data centers drawn over the map.'))
# 10 Nov 2026: WATER, live, under ATLAS. Plan: water_index/PLAN.md, sealed by hash before the first comparison (data/plan_seal.json) and committed at ship.
# Its plan and code line is its own (the shared line from _codeline says every plan was committed before its data), so the right of reply block is in the body.
_WATERBODY = ('<h2>When Reclamation projects a lake level, where does the lake end up?</h2>'
  '<p>Each month the Bureau of Reclamation publishes the 24-Month Study. It states where Lake Powell and Lake Mead will stand at the end of each coming month. Every study has a Most Probable run. Many also have a Probable Minimum and a Probable Maximum run. Reclamation describes the Most Probable inflow as a median that would be exceeded 50 percent of the time, the Minimum as exceeded 90 percent of the time and the Maximum as exceeded 10 percent of the time.</p>'
  "<p>We read every study Reclamation lists from January 2000 on. Each projected end-of-month elevation is set against the elevation Reclamation's own database recorded at the end of that month. Months ahead counts from the month a study was issued to the month it describes.</p>"
  '<p>Since January 2010 the Probable Minimum and Probable Maximum reports also state: &ldquo;There is approximately an 80% probability that a future elevation will fall inside the range of the minimum and maximum inflow scenarios. Additionally, there are possible inflow scenarios that would result in reservoir elevations falling outside the ranges indicated in these reports.&rdquo; The band test reads that sentence. Reading the Most Probable elevation as a median is our reading, since Reclamation describes the Most Probable inflow, not the elevation, as a median. A gap between a projection and the measured level is a gap. This page does not say why it happened. The plan, with the rules and the known-good checks, was fixed before any projection was set against a measured level. Two dated addenda record what changed, and no rule or threshold changed.</p>'
  '<div id="water-live" class="bench-live">Loading.</div><script src="/water/live.js" defer></script>'
  '<p class="meta">Named here and want to answer a row? <a href="/respond?u=water-all">Respond</a></p>'
  '<p class="bench-note">Inside means the measured end-of-month elevation lies between the Probable Minimum and Probable Maximum projections issued in the same month. Above and below mean outside that range. Each interval is a 95% Wilson interval counted on water years, because months in one water year share weather. It treats water years as independent, and at leads past about six months neighbouring water years are correlated. Band outcome: above if the lower bound is over 80 percent, below if the upper bound is under 80 percent, consistent if the interval lies inside 70 to 90 percent, otherwise cannot tell with the reason STRADDLES_EDGE, and cannot tell with the reason TOO_WIDE_TO_RESOLVE with fewer than 10 water years. Edges are closed. No size that matters is named for these cells, so the check for an interval that holds both zero and a size that matters is not applied. Most Probable outcome: the same rule around 50 percent, with 40 to 60 percent for consistent. With about 20 water years in a cell no interval is narrow enough to read consistent, so a cell reads a miss or cannot tell. Error is the measured elevation minus the Most Probable projection, in feet. Data: Reclamation RISE and HDB, Reclamation Lower Colorado daily report, USGS Water Services and California CDEC, all read without a key.</p>'
  '<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/water">water</a>. The plan was fixed before the comparison it describes, and its addenda are dated. The figures on this page live in <a href="/water/live.json">/water/live.json</a>.</p>'
  '<p class="meta">Data read from: <a href="https://data.usbr.gov/rise/api/catalog-record/6331">Reclamation RISE 24-Month Study archive</a> &middot; <a href="https://www.usbr.gov/lc/region/g4000/riverops/_HdbWebQuery.html">Reclamation HDB</a> &middot; <a href="https://www.usbr.gov/lc/region/g4000/hourly/levels.html">Reclamation Lower Colorado daily report</a> &middot; <a href="https://waterservices.usgs.gov">USGS Water Services</a> &middot; <a href="https://cdec.water.ca.gov">California CDEC</a>. Read about every half hour.</p>'
  '<section id="replies" data-prefix="water"></section><script src="/replies.js" defer></script>')
PAGES['/water'] = page('/water', 'WATER | Projected Lake Levels Against Measured | Heuremen LLC', 'WATER: each 24-Month Study projection of Lake Mead and Lake Powell since 2000 against the level the lake reached, by months ahead, with a live panel of both lakes and the elevations the governing documents name.', _WATERBODY, hero_slim('WATER &middot; Projected Lake Levels Against Measured'))
_FEED.append(('/water', 'WATER: Projected Lake Levels Against Measured', 'Each 24-Month Study projection of Lake Mead and Lake Powell since 2000 against the level the lake reached, live.'))
# 10 Nov 2026: NEO, under ATLAS. Plan: neo_index/PLAN.md, committed (2314da1) before any stated distance was set beside a later one, outside referee
# neo_index_referee/REFEREE.md (FIX THEN SHIP, fixes applied in neo_index/build_page.py and neo_headline.py). The body is taken from neo_index/neo.html,
# which build_page.py renders from summary_neo.json, so nav, division line, footer and reference code come from page(). The headline is the live one
# (watch/headlines.py neo(), same function as the page). The feed /neo/live.json is the summary of the newest run and can be newer than the tables.
_ne = open(os.path.join(HERE, '..', 'neo_index', 'neo.html'), encoding='utf-8').read()
_ne_main = _ne[_ne.index('<main class="wrap">') + len('<main class="wrap">'):_ne.index('</main>')]
assert _ne_main.startswith('<section id="hl-slot"'), 'NEO: the headline block is not where build_page.py puts it'
_NEOBODY = _ne_main[_ne_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>' in _NEOBODY, 'NEO: the division line is not where build_page.py puts it'
_NEOBODY = _NEOBODY.replace('<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>', '', 1).lstrip('\n')
_NEOBODY = _NEOBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')   # the site's table and scroll styles (no inline style on indahl.ai)
PAGES['/neo'] = page('/neo', 'NEO | Stated Close-Approach Distances Against the Later Record | Heuremen LLC', 'NEO: close-approach distance ranges that NASA/JPL stated from an earlier orbit solution, copied at the time by the Internet Archive and by this desk, set beside the distance from the latest solution, by how long before the approach each range was stated.', _NEOBODY, hero_slim('NEO &middot; Stated Close-Approach Distances Against the Later Record'))
_FEED.append(('/neo', 'NEO: Stated Close-Approach Distances Against the Later Record', 'Close-approach distance ranges JPL stated from an earlier orbit solution against the latest solution, by how long before the approach they were stated.'))

# 10 Nov 2026: SEASONAL, under HERMES beside FORECAST. Plan: seasonal_index/PLAN.md, committed (11d602c) before the first comparison, outside referee
# seasonal_index_referee/REFEREE.md (fixes applied in seasonal_index/build_page.py). The body is taken from seasonal_index/seasonal.html as for NEO. The headline is the
# live one (watch/headlines.py seasonal(), same function as the page). The feed /seasonal/live.json is the summary of the newest run.
_seasonal = open(os.path.join(HERE, '..', 'seasonal_index', 'seasonal.html'), encoding='utf-8').read()
_seasonal_main = _seasonal[_seasonal.index('<main class="wrap">') + len('<main class="wrap">'):_seasonal.index('</main>')]
assert _seasonal_main.startswith('<section id="hl-slot"'), 'SEASONAL: the headline block is not where build_page.py puts it'
_SEASONALBODY = _seasonal_main[_seasonal_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _SEASONALBODY, 'SEASONAL: the division line is not where build_page.py puts it'
_SEASONALBODY = _SEASONALBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
_SEASONALBODY = _SEASONALBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/seasonal'] = page('/seasonal', 'SEASONAL | Stated Seasonal Outlook Chances Against What Was Observed | Heuremen LLC', 'SEASONAL: the chances the NOAA Climate Prediction Center stated for above, near and below normal seasons, set beside the observed category on its own grid, with block bootstrap intervals, and our recompute of its skill score.', _SEASONALBODY, hero_slim('SEASONAL &middot; Stated Seasonal Outlook Chances Against What Was Observed'))
_FEED.append(('/seasonal', 'SEASONAL: Stated Seasonal Outlook Chances Against What Was Observed', 'NOAA Climate Prediction Center 3-month outlook chances against the observed category, and a recompute of its stated skill score, live.'))

# 10 Nov 2026: STEO, under HERMES beside FORECAST. Plan: steo_index/PLAN.md, committed (db32688) before the first comparison, outside referee
# steo_index_referee/REFEREE.md (fixes applied in steo_index/build_page.py). The body is taken from steo_index/steo.html as for NEO. The headline is the
# live one (watch/headlines.py steo(), same function as the page). The feed /steo/live.json is the summary of the newest run.
_steo = open(os.path.join(HERE, '..', 'steo_index', 'steo.html'), encoding='utf-8').read()
_steo_main = _steo[_steo.index('<main class="wrap">') + len('<main class="wrap">'):_steo.index('</main>')]
assert _steo_main.startswith('<section id="hl-slot"'), 'STEO: the headline block is not where build_page.py puts it'
_STEOBODY = _steo_main[_steo_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _STEOBODY, 'STEO: the division line is not where build_page.py puts it'
_STEOBODY = _STEOBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
_STEOBODY = _STEOBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/steo'] = page('/steo', 'STEO | Stated Energy Price Intervals Against the Spot Price | Heuremen LLC', 'STEO: the 95 percent price intervals EIA stated for WTI crude oil and Henry Hub natural gas in its Short-Term Energy Outlook, set beside the monthly average spot price, by months ahead, with block bootstrap intervals.', _STEOBODY, hero_slim('STEO &middot; Stated Energy Price Intervals Against the Spot Price'))
_FEED.append(('/steo', 'STEO: Stated Energy Price Intervals Against the Spot Price', 'EIA Short-Term Energy Outlook 95 percent price intervals for WTI and Henry Hub against the monthly average spot price, live.'))
# 10 Nov 2026: SOLAR, under ATLAS. Plan: solar_index/PLAN.md, committed (07b57e8) before any stated chance was set beside an outcome, addenda 1 and 2 after
# the data, outside referee solar_index_referee/REFEREE.md (HOLD on the flare reader, fixed, re-check SHIP). Same pattern as NEO: the body is taken from
# solar_index/solar.html, which build_page.py renders from summary_solar.json. The headline is the live one (watch/headlines.py solar()).
_so = open(os.path.join(HERE, '..', 'solar_index', 'solar.html'), encoding='utf-8').read()
_so_main = _so[_so.index('<main class="wrap">') + len('<main class="wrap">'):_so.index('</main>')]
assert _so_main.startswith('<section id="hl-slot"'), 'SOLAR: the headline block is not where build_page.py puts it'
_SOLARBODY = _so_main[_so_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>' in _SOLARBODY, 'SOLAR: the division line is not where build_page.py puts it'
_SOLARBODY = _SOLARBODY.replace('<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>', '', 1).lstrip('\n')
_SOLARBODY = _SOLARBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/solar'] = page('/solar', 'SOLAR | Stated Space Weather Chances Against What Happened | Heuremen LLC', 'SOLAR: the chances of solar flares and geomagnetic storms that NOAA SWPC states each day, as first published, set beside what happened, bin by bin, with a Brier score against the base rate.', _SOLARBODY, hero_slim('SOLAR &middot; Stated Space Weather Chances Against What Happened'))
_FEED.append(('/solar', 'SOLAR: Stated Space Weather Chances Against What Happened', 'NOAA SWPC stated chances of solar flares and geomagnetic storms against what happened, by bin of stated chance.'))
# 10 Nov 2026: QUAKE, under ATLAS. Plan: quake_index/PLAN.md, committed (ae75b55) before any stated probability or range was set beside a count, outside referee
# quake_index_referee/REFEREE.md. The body is taken from quake_index/quake.html, which build_page.py renders from summary_quake.json. The headline is the live
# one (watch/headlines.py quake(), same function as the page). The feed /quake/live.json is the summary of the newest run and can be newer than the tables.
_qk = open(os.path.join(HERE, '..', 'quake_index', 'quake.html'), encoding='utf-8').read()
_qk_main = _qk[_qk.index('<main class="wrap">') + len('<main class="wrap">'):_qk.index('</main>')]
assert _qk_main.startswith('<section id="hl-slot"'), 'QUAKE: the headline block is not where build_page.py puts it'
_QKBODY = _qk_main[_qk_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>' in _QKBODY, 'QUAKE: the division line is not where build_page.py puts it'
_QKBODY = _QKBODY.replace('<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>', '', 1).lstrip('\n')
_QKBODY = _QKBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/quake'] = page('/quake', 'QUAKE | Stated Aftershock Odds Against the Aftershocks That Followed | Heuremen LLC', 'QUAKE: every archived USGS aftershock forecast, its stated probabilities and 95% ranges set beside the earthquakes the USGS catalog shows in the same zone and window.', _QKBODY, hero_slim('QUAKE &middot; Stated Aftershock Odds Against the Aftershocks That Followed'))
_FEED.append(('/quake', 'QUAKE: Stated Aftershock Odds Against the Aftershocks That Followed', 'Every archived USGS aftershock forecast against the earthquakes the USGS catalog shows in the same zone and window.'))

# 10 Nov 2026: RANK, under OY. US News education rankings against the public record. Plan: rank_index/PLAN.md, committed (b25e87f) before any
# figure was compared. Step one lists the current top of each list with edition, list and method links, every row check in progress.
# Outside referee: rank_index_referee/REFEREE.md. Body from rank_index/rank_body.html (rank_index/build_page.py from data/rank.json).
_RANKBODY = open(os.path.join(HERE, '..', 'rank_index', 'rank_body.html'), encoding='utf-8').read()
_RANKBODY = _RANKBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/rank'] = page('/rank', 'RANK | US News Education Rankings Against the Public Record | Heuremen LLC', 'RANK: the current top of each US News education ranking, with the stated method and weights, set against state report cards, federal school and college data and schools\' own published reports.', _RANKBODY, hero_slim('RANK &middot; US News Education Rankings Against the Public Record'))
_FEED.append(('/rank', 'RANK: US News Education Rankings Against the Public Record', 'The current top of each US News education ranking with its stated method, set against the public record.'))

# 10 Nov 2026: FLU, under HERMES beside FORECAST. Plan: flu_index/PLAN.md, committed (d82aaca) before the first comparison, outside referee
# flu_index_referee/REFEREE.md (fixes applied in flu_index/build_page.py). The body is taken from flu_index/flu.html as for NEO. The headline is the
# live one (watch/headlines.py flu(), same function as the page). The feed /flu/live.json is the summary of the newest run.
_flu = open(os.path.join(HERE, '..', 'flu_index', 'flu.html'), encoding='utf-8').read()
_flu_main = _flu[_flu.index('<main class="wrap">') + len('<main class="wrap">'):_flu.index('</main>')]
assert _flu_main.startswith('<section id="hl-slot"'), 'FLU: the headline block is not where build_page.py puts it'
_FLUBODY = _flu_main[_flu_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _FLUBODY, 'FLU: the division line is not where build_page.py puts it'
_FLUBODY = _FLUBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
_FLUBODY = _FLUBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/flu'] = page('/flu', 'FLU | Stated Flu Forecast Intervals Against Reported Admissions | Heuremen LLC', 'FLU: the CDC FluSight ensemble stated 50 and 95 percent intervals for weekly flu hospital admissions, set beside the counts later reported, by horizon, season and place, with block bootstrap intervals.', _FLUBODY, hero_slim('FLU &middot; Stated Flu Forecast Intervals Against Reported Admissions'))
_FEED.append(('/flu', 'FLU: Stated Flu Forecast Intervals Against Reported Admissions', 'The CDC FluSight ensemble stated intervals for weekly flu hospital admissions against the counts later reported, live.'))

# 10 Nov 2026: CREDIT, under HERMES beside TORNADO. CFPB printed figures (timely responses, forwarding) against the CFPB Consumer Complaint Database,
# each company against the printed figure, the three credit bureaus' closures, the FCRA 30-day period (cannot tell), and TCCP card plan APRs beside G.19.
# Plan: credit_index/PLAN.md, committed (8ef6f26) before the first comparison. Outside referee credit_index_referee/REFEREE.md. Body from credit_index/credit.html.
_credit = open(os.path.join(HERE, '..', 'credit_index', 'credit.html'), encoding='utf-8').read()
_credit_main = _credit[_credit.index('<main class="wrap">') + len('<main class="wrap">'):_credit.index('</main>')]
assert _credit_main.startswith('<section id="hl-slot"'), 'CREDIT: the headline block is not where build_page.py puts it'
_CREDITBODY = _credit_main[_credit_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _CREDITBODY, 'CREDIT: the division line is not where build_page.py puts it'
_CREDITBODY = _CREDITBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
_CREDITBODY = _CREDITBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/credit'] = page('/credit', 'CREDIT | Stated Complaint Responses and Card Terms Against the Public Record | Heuremen LLC', 'CREDIT: the CFPB printed timely response and forwarding shares against its own complaint database, each company against the printed figure, how the credit bureaus closed complaints, and card plan APRs beside the Federal Reserve averages.', _CREDITBODY, hero_slim('CREDIT &middot; Stated Complaint Responses and Card Terms Against the Public Record'))
_FEED.append(('/credit', 'CREDIT: Stated Complaint Responses and Card Terms Against the Public Record', 'CFPB printed timely response figures against its own complaint database, company by company, and card plan APRs beside the Federal Reserve averages.'))

# 10 Nov 2026: TORNADO, under HERMES beside FORECAST. Plan: tornado_index/PLAN.md, committed (447599c) before the first comparison, outside referee
# tornado_index_referee/REFEREE.md (fixes applied in tornado_index/build_page.py). The body is taken from tornado_index/tornado.html as for NEO. The headline is the
# live one (watch/headlines.py tornado(), same function as the page). The feed /tornado/live.json is the summary of the newest run.
_tornado = open(os.path.join(HERE, '..', 'tornado_index', 'tornado.html'), encoding='utf-8').read()
_tornado_main = _tornado[_tornado.index('<main class="wrap">') + len('<main class="wrap">'):_tornado.index('</main>')]
assert _tornado_main.startswith('<section id="hl-slot"'), 'TORNADO: the headline block is not where build_page.py puts it'
_TORNADOBODY = _tornado_main[_tornado_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _TORNADOBODY, 'TORNADO: the division line is not where build_page.py puts it'
_TORNADOBODY = _TORNADOBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
_TORNADOBODY = _TORNADOBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/tornado'] = page('/tornado', 'TORNADO | Stated Tornado Chances Against the Tornadoes That Came | Heuremen LLC', 'TORNADO: the Storm Prediction Center Day 1 tornado probabilities and the National Weather Service tornado warning goals, set beside the tornadoes in the SPC tornado database, with Kansas and Tornado Alley apart and day block bootstrap intervals.', _TORNADOBODY, hero_slim('TORNADO &middot; Stated Tornado Chances Against the Tornadoes That Came'))
_FEED.append(('/tornado', 'TORNADO: Stated Tornado Chances Against the Tornadoes That Came', 'Storm Prediction Center tornado probability bands and NWS tornado warning goals against the tornadoes in the SPC database, live.'))
# 10 Nov 2026: CONE, under ATLAS. Plan: cone_index/PLAN.md, committed (e49ebd2) before any forecast position was set beside a best-track position. Outside referee
# cone_index_referee/REFEREE.md. The body is taken from cone_index/cone.html, which build_page.py renders from summary_cone.json, so nav, division line, footer
# and reference code come from page(). The headline is the live one (watch/headlines.py cone(), same function as the page). The feed /cone/live.json is the newest run.
_co = open(os.path.join(HERE, '..', 'cone_index', 'cone.html'), encoding='utf-8').read()
_co_main = _co[_co.index('<main class="wrap">') + len('<main class="wrap">'):_co.index('</main>')]
assert _co_main.startswith('<section id="hl-slot"'), 'CONE: the headline block is not where build_page.py puts it'
_CONEBODY = _co_main[_co_main.index('</section>') + len('</section>'):]
assert '<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>' in _CONEBODY, 'CONE: the division line is not where build_page.py puts it'
_CONEBODY = _CONEBODY.replace('<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>', '', 1).lstrip('\n')
_CONEBODY = _CONEBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/cone'] = page('/cone', 'CONE | The Hurricane Forecast Cone Against Where Storms Went | Heuremen LLC', 'CONE: National Hurricane Center official track forecasts set beside the post-season best track, scored against the cone NHC states holds the storm centre about 60 to 70 percent of the time.', _CONEBODY, hero_slim('CONE &middot; The Hurricane Forecast Cone Against Where Storms Went'))
_FEED.append(('/cone', 'CONE: The Hurricane Forecast Cone Against Where Storms Went', 'National Hurricane Center official track forecasts against the best track, read against the cone NHC states holds the storm centre about 60 to 70 percent of the time.'))
# 11 Nov 2026: CENSUS, a division of its own (Wayfinder named it and approved the ship). The division page is short and lists its desks. The first desk is
# REVISIONS at /census/revisions: the first print of each Census indicator with its stated 90 percent interval against the later value. Plan:
# census_index/PLAN.md, sealed (af6caae) before any later value was set beside a first print, outside referee census_index_referee/REFEREE.md (FIX THEN SHIP,
# fixes applied in census_index/build_page.py and census_tick.py, recorded in census_index/CHECKS.md). The body is taken from census_index/census_revisions.html,
# which build_page.py renders from summary_census.json. The headline is the live one (watch/headlines.py census(), same function as the page).
# The feed /census/live.json is the summary of the newest run and can be newer than the tables.
_ce = open(os.path.join(HERE, '..', 'census_index', 'census_revisions.html'), encoding='utf-8').read()
_ce_main = _ce[_ce.index('<main class="wrap">') + len('<main class="wrap">'):_ce.index('</main>')].lstrip('\n')
assert _ce_main.startswith('<section id="hl-slot"'), 'CENSUS: the headline block is not where build_page.py puts it'
_CENSUSSLOT = _ce_main[:_ce_main.index('</section>') + len('</section>')]
_CENSUSBODY = _ce_main[len(_CENSUSSLOT):]
assert '<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>' in _CENSUSBODY, 'CENSUS: the division line is not where build_page.py puts it'
assert 'This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.' in _CENSUSBODY, 'CENSUS: the required Census API line is missing'
_CENSUSBODY = _CENSUSBODY.replace('<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>', '', 1).lstrip('\n')
_CENSUSBODY = _CENSUSBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')   # the site's table and scroll styles (no inline style on indahl.ai)
PAGES['/census/revisions'] = page('/census/revisions', 'CENSUS | Stated Uncertainty Against Later Revisions | Heuremen LLC', 'CENSUS: the first print of new home sales, housing starts, housing completions and advance retail sales with the 90 percent interval Census states for it, set beside the value after one revision, two, and today.', _CENSUSBODY, hero_slim('CENSUS &middot; Stated Uncertainty Against Later Revisions'))
_FEED.append(('/census/revisions', 'CENSUS: Stated Uncertainty Against Later Revisions', 'The first print of each Census indicator with its stated 90 percent interval against the value after one revision, two, and today.'))
# 11 Nov 2026: CENSUS COVERAGE, the second desk under CENSUS, at /census/coverage. The 2020 Census state counts against the Census Bureau's own Post-Enumeration Survey,
# read at the 90 percent level Census states. One-time desk: no tick rider, no feed, no data pack. Plan: census_coverage/PLAN.md, sealed (ed9e74d) before any count of outcomes
# was computed, outside referee census_coverage_referee/REFEREE.md (FIX THEN SHIP, fixes applied in census_coverage/build_page.py, recorded in census_coverage/CHECKS.md).
# The body is census_coverage/census_coverage.html, rendered by build_page.py from summary_coverage.json. Ledger rows censuscov.* (surface desk_censuscov).
_cv = open(os.path.join(HERE, '..', 'census_coverage', 'census_coverage.html'), encoding='utf-8').read()
_cv_main = _cv[_cv.index('<main class="wrap">') + len('<main class="wrap">'):_cv.index('</main>')].strip('\n')
assert _cv_main.startswith('<p class="meta crumb">'), 'COVERAGE: the division line is not where build_page.py puts it'
_COVSLOT = _cv_main[_cv_main.index('<section id="hl-slot"'):_cv_main.index('</section>') + len('</section>')]
_COVBODY = _cv_main[_cv_main.index('</section>') + len('</section>'):]
assert 'This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.' in _COVBODY, 'COVERAGE: the required Census API line is missing'
_COVBODY = _COVBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')   # the site's table and scroll styles (no inline style on indahl.ai)
PAGES['/census/coverage'] = page('/census/coverage', 'CENSUS | The Census Count Against Its Own Survey | Heuremen LLC', "CENSUS: the 2020 Census count of each state set beside the Census Bureau's own Post-Enumeration Survey, read at the 90 percent level Census states, with the Demographic Analysis range as a separate cell.", _COVBODY, hero_slim('CENSUS &middot; The Census Count Against Its Own Survey'))
_FEED.append(('/census/coverage', 'CENSUS: The Census Count Against Its Own Survey', 'The 2020 Census count of each state set beside the Census Bureau\'s own Post-Enumeration Survey, read at the 90 percent level Census states.'))
# 11 Nov 2026: CENSUS FIDELITY, the third desk under CENSUS, at /census/fidelity. State divorce and marriage counts reported to the CDC (NCHS) set beside the ACS
# estimates with the 90 percent margin Census states, women's estimate scored, men's beside it. One-time desk: no tick rider for the readings (a snapshot rider keeps dated NCHS copies),
# no feed, no data pack. Plan: fidelity_index/PLAN.md, sealed (1b571f2) before the first comparison, outside referee fidelity_referee/REFEREE.md (FIX THEN SHIP, fixes applied
# in fidelity_index/build_page.py, recorded in fidelity_index/CHECKS.md). The body is fidelity_index/fidelity.html, rendered by build_page.py. Ledger rows fid.* (surface desk_fidelity).
_fd = open(os.path.join(HERE, '..', 'fidelity_index', 'fidelity.html'), encoding='utf-8').read()
_fd_main = _fd[_fd.index('<main class="wrap">') + len('<main class="wrap">'):_fd.index('</main>')].strip('\n')
assert _fd_main.startswith('<section id="hl-slot"'), 'FIDELITY: the headline block is not where build_page.py puts it'
_FIDSLOT = _fd_main[:_fd_main.index('</section>') + len('</section>')]
_FIDBODY = _fd_main[len(_FIDSLOT):].strip('\n')
assert '<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>' in _FIDBODY, 'FIDELITY: the division line is not where build_page.py puts it'
assert 'This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.' in _FIDBODY, 'FIDELITY: the required Census API line is missing'
_FIDBODY = _FIDBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/census/fidelity'] = page('/census/fidelity', 'CENSUS | State Counts Against the ACS | Heuremen LLC', 'CENSUS: state divorce and marriage counts reported to the CDC, set beside the Census American Community Survey estimates and the 90 percent margin Census states, women and men both shown.', _FIDBODY, hero_slim('CENSUS &middot; State Counts Against the ACS'))
_FEED.append(('/census/fidelity', 'CENSUS: State Counts Against the ACS', 'State divorce and marriage counts reported to the CDC, set beside the Census American Community Survey estimates and their stated margin.'))
# 11 Nov 2026: CENSUS VINTAGES, the fourth desk under CENSUS, at /census/vintages. State July 1 population estimates as earlier Vintages gave them, set beside later Vintages and the 2020 Census count,
# with the Post-Enumeration Survey standard error as the only yardstick and CANNOT_TELL kept as its own count. One-time desk: no tick rider, no feed, no data pack. Plan: census_index/census_vintages/PLAN.md,
# sealed (b11e6aa) before any count of outcomes was computed, outside referee fixes applied in census_index/census_vintages/build_page.py and recorded in its CHECKS.md. Ledger rows censusvin.* (surface desk_censusvin).
_vn = open(os.path.join(HERE, '..', 'census_index', 'census_vintages', 'census_vintages.html'), encoding='utf-8').read()
_vn_main = _vn[_vn.index('<main class="wrap">') + len('<main class="wrap">'):_vn.index('</main>')].strip('\n')
assert _vn_main.startswith('<p class="meta crumb">'), 'VINTAGES: the division line is not where build_page.py puts it'
_VINSLOT = _vn_main[_vn_main.index('<section id="hl-slot"'):_vn_main.index('</section>') + len('</section>')]
_VINBODY = _vn_main[_vn_main.index('</section>') + len('</section>'):]
assert 'This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.' in _VINBODY, 'VINTAGES: the required Census API line is missing'
_VINBODY = _VINBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/census/vintages'] = page('/census/vintages', 'CENSUS | Population Estimates Against Their Later Vintages | Heuremen LLC', "CENSUS: each state July 1 population estimate as an earlier Vintage gave it, set beside later Vintages and the 2020 Census count, with the Census Bureau survey standard error as the only yardstick and CANNOT_TELL kept as its own count.", _VINBODY, hero_slim('CENSUS &middot; Population Estimates Against Their Later Vintages'))
_FEED.append(('/census/vintages', 'CENSUS: Population Estimates Against Their Later Vintages', 'Each state July 1 population estimate as an earlier Vintage gave it, set beside later Vintages and the 2020 Census count.'))

# 12 Nov 2026 (Wayfinder: "Perfect for ATLAS. Petrol!"): ATLAS PETROL at /petrol. Oil OUTPUT only, never prices. OPEC+ required production against
# OPEC's secondary-source output per member and month, width from OPEC's own first-to-second-print revisions; and EIA's weekly US crude estimate averaged
# by month against EIA's monthly figure, width from the 2015-2019 spread. Plan sealed in petrol_index/PLAN.md before outcomes. Ledger rows petrol.*.
_pt = open(os.path.join(HERE, '..', 'petrol_index', 'petrol_body.html'), encoding='utf-8').read().strip('\n')
assert _pt.startswith('<p class="meta crumb">'), 'PETROL: the division line is not where build_page.py puts it'
_PETSLOT = _pt[_pt.index('<section id="hl-slot"'):_pt.index('</section>') + len('</section>')]
_PETBODY = _pt[_pt.index('</section>') + len('</section>'):].replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/petrol'] = page('/petrol', 'PETROL | OPEC+ Required Production Against Delivered Output | ATLAS | Heuremen LLC', "ATLAS PETROL: each OPEC+ country's required production level against the output secondary sources report, and EIA's weekly US crude estimate against its monthly figure. Volumes only.",
                        _PETBODY, hero_slim('PETROL &middot; OPEC+ Required Production Against Delivered Output'))
HOME['/petrol'] = '/atlas'
_FEED.append(('/petrol', 'ATLAS: PETROL, OPEC+ Required Production Against Delivered Output', "Each OPEC+ country's required production against the output secondary sources report, and EIA's weekly US crude estimate against its monthly figure."))
_CENSUSDIV = ('<section class="legal"><h2>What CENSUS is</h2>'
  '<p>CENSUS sets what the U.S. Census Bureau states about the uncertainty of its first estimates beside what the record shows later. CENSUS is the name of this division of Heuremen LLC. It is not the U.S. Census Bureau and the Bureau does not endorse it.</p>'
  '<p>The first desk reads the 90 percent interval Census states for each first print of new home sales, housing starts, housing completions and advance retail sales against the revised values that followed. Its page is <a href="/census/revisions">CENSUS Revisions</a>, and the newest reading is in <a href="/census/live.json">/census/live.json</a>.</p>'
  '<p>The second desk sets the 2020 Census count of each state beside the Census Bureau\'s own Post-Enumeration Survey. Its page is <a href="/census/coverage">CENSUS Coverage</a>. It was run once and does not refresh.</p>'
  '<p>The third desk sets the state counts of marriages and divorces reported to the CDC beside the Census Bureau\'s American Community Survey estimates. Its page is <a href="/census/fidelity">CENSUS Fidelity</a>. It was run once and does not refresh.</p>'
  '<p>The fourth desk sets each state\'s July 1 population estimate as an earlier Vintage gave it beside the later Vintages and the 2020 Census count. Its page is <a href="/census/vintages">CENSUS Vintages</a>. It was run once and does not refresh.</p>'
  '<p class="meta">Sources: U.S. Census Bureau, Economic Indicators Time Series API and explanatory notes. Federal Reserve Bank of St. Louis, ALFRED archival series. This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p></section>')
PAGES['/census'] = page('/census', 'CENSUS | Official Statistics Against Their Revisions | Heuremen LLC', 'CENSUS: what the U.S. Census Bureau states about the uncertainty of its first estimates, set beside the revisions that followed. A division of Heuremen LLC, not the Census Bureau.', _CENSUSDIV, hero_slim('CENSUS &middot; Official Statistics Against Their Revisions'))
_FEED.append(('/census', 'CENSUS: Official Statistics Against Their Revisions', 'What the Census Bureau states about the uncertainty of its first estimates, set beside the revisions that followed.'))
# 10 Nov 2026: WIKI, under HERMES. Plan: wiki_index/PLAN.md (committed before any comparison, notes 1 and 2 after the outside referee).
# The page is one reading: wiki_index/build_page.py renders it from data/wiki_live.json, and its body and headline are taken from that file here,
# so nav, division line, footer and reference code come from page(). The feed /wiki/live.json is read again about once a week and can be newer.
_wk = open(os.path.join(HERE, '..', 'wiki_index', 'wiki.html'), encoding='utf-8').read()
_wk_main = _wk[_wk.index('<main class="wrap">') + len('<main class="wrap">'):_wk.index('</main>')]
_WIKISLOT = _wk_main[:_wk_main.index('</section>') + len('</section>')]
assert _WIKISLOT.startswith('<section id="hl-slot"'), 'WIKI: the headline block is not where build_page.py puts it'
_WIKIBODY = _wk_main[len(_WIKISLOT):]
_WIKIBODY = _WIKIBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
PAGES['/wiki'] = page('/wiki', 'WIKI | Figures Against Their Source | Heuremen LLC', 'WIKI: figures in Wikidata that cite the World Bank or UNESCO, read against that source\'s current and archived releases, and the Wikimedia Foundation\'s stated reach read against its own public data.', _WIKIBODY, hero_slim('WIKI &middot; Figures Against Their Source'))
_FEED.append(('/wiki', 'WIKI: Figures Against Their Source', 'Figures in Wikidata that cite the World Bank or UNESCO against the source\'s releases, and the Wikimedia Foundation\'s stated reach against its own data.'))
# 10 Nov 2026: SOCIAL, under HERMES. One page, one section per pair of records. social_index/build_social.py places each cleared section file
# (section_<key>.html, written by that section's own tick) byte for byte and reads every number outside the sections from
# summary_<key>.json. Body and headline are taken from social.html here, so nav, division line, footer and reference code come from page().
_so = open(os.path.join(HERE, '..', 'social_index', 'social.html'), encoding='utf-8').read()
_so_main = _so[_so.index('<main class="wrap">') + len('<main class="wrap">'):_so.index('</main>')]
_SOCIALSLOT = _so_main[:_so_main.index('</section>') + len('</section>')] if _so_main.startswith('<section id="hl-slot"') else ''
_SOCIALBODY = _so_main[len(_SOCIALSLOT):]
assert 'section is being read' not in _SOCIALBODY, 'SOCIAL: the Bluesky slot is still in the page (build_social.py --bluesky-cleared)'
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _SOCIALBODY, 'SOCIAL: the division line is not where build_social.py puts it'
_SOCIALBODY = _SOCIALBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
PAGES['/social'] = page('/social', 'SOCIAL | Platform Reports Against the Filings | Heuremen LLC', 'SOCIAL: what large platforms state about their own conduct, read against public filings that cover the same activity. EU moderation reports against the DSA Transparency Database, Google\'s political ad library against FEC filings, TikTok\'s quarterly report against its EU filings, and Bluesky\'s transparency report against its signed label stream.', _SOCIALBODY, hero_slim('SOCIAL &middot; Platform Reports Against the Filings'))
_FEED.append(('/social', 'SOCIAL: Platform Reports Against the Filings', 'EU moderation reports against the DSA Transparency Database, Google\'s political ad library against FEC filings, TikTok\'s quarterly report against its EU filings, and Bluesky\'s transparency report against its signed label stream.'))
# 10 Nov 2026: NOW (with FORTUNE), under HERMES, at /predictions (the path /now is the live landing page). Plan: now_index/PLAN.md, committed
# before any entry was collected. The page is one frozen reading: now_index/freeze.py writes data/page_reading.json and build_page.py renders
# now.html from it, so a daily rider run never moves a number a ledger row holds. The feed /predictions/live.json is read every day and can be newer.
_pr = open(os.path.join(HERE, '..', 'now_index', 'now.html'), encoding='utf-8').read()
_pr_main = _pr[_pr.index('<main class="wrap">') + len('<main class="wrap">'):_pr.index('</main>')]
_PREDSLOT = _pr_main[:_pr_main.index('</section>') + len('</section>')]
assert _PREDSLOT.startswith('<section id="hl-slot"'), 'NOW: the headline block is not where build_page.py puts it'
_PREDBODY = _pr_main[len(_PREDSLOT):]
assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _PREDBODY, 'NOW: the division line is not where build_page.py puts it'
_PREDBODY = _PREDBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
PAGES['/predictions'] = page('/predictions', 'NOW | Predictions Against the Record | Heuremen LLC', 'NOW: public predictions by named people and organisations, logged with their exact words, source and deadline, and read against the record when they come due. FORTUNE: famous predictions from history, checked for whether they were said and how they landed.', _PREDBODY, hero_slim('NOW &middot; Predictions Against the Record'))
_FEED.append(('/predictions', 'NOW: Predictions Against the Record', 'Public predictions logged with their exact words and deadline and read against the record when they come due, with FORTUNE, famous predictions from history.'))
PAGES['/oy'] = page('/oy', 'Recount Matrix: Learning Research | OY | Heuremen LLC',
 'Recount Matrix: Learning Research. What United States institutions have published about measuring their own policies on AI in teaching and learning, with a source for every row.',
 OY_TOP + _OY_BODY + _OY_SCH, hero_slim('OY &middot; Learning Research'))

# 25 Oct 2026 (his word): IRIS = Recount Matrix: Language Models, same form as OY; Pub #2 on top. The earlier IRIS page is kept in HELD_IRIS.
HELD_IRIS = PAGES.pop('/iris')
_IRIS_BODY = open(os.path.join(HERE, '..', 'iris_index', 'matrix_page', 'iris_body.html'), encoding='utf-8').read()
IRIS_DISC = '<section class="disclose"><p>Studies listed are for information and demonstration only. Please <a href="/contact">click here to ask to be removed from our index</a>. Heuremen LLC is an independent, private company with no stake, value or interest in any study listed here. All employees are required to <a href="/conflict-of-interest">certify</a> that they have no business interest in large language models, or in any other work at Heuremen LLC, that could pose a conflict of interest.</p></section>'   # 25 Oct 2026, his word: same disclaimer as QIA with LLMs for quantum
_D = lambda *ls: '<p class="data">Data: ' + ' &middot; '.join(f'<a href="/iris/runs/{z}.zip">{t}</a>' for z, t in ls) + '</p>'
_IRIS_BODY, _nhd = _re.subn(r'(<h2 id="headline">[^<]*</h2>(?:<p>.*?</p>)?)', lambda m: m.group(1) + _D(('matrix-round-1', 'matrix round 1'), ('matrix-round-2', 'matrix round 2'), ('frontier', 'frontier')), _IRIS_BODY, count=1, flags=_re.S); assert _nhd == 1   # 30 Oct 2026: matched by pattern, so a change to the headline text cannot silently drop the data line
IRIS_FG = '''<section class="tight"><p><a href="https://heuremen.org/faults.pdf">Faults</a> &middot; <a href="https://heuremen.org/guards.pdf">Guards</a> (PDF)</p></section>'''
IRIS_MARK = '''<section class="tight markguide"><h2>Marking your own work</h2>
<p>Every page, data zip and dataset card from Heuremen LLC carries a reference code. Each code is made from a private key and the name of the surface it sits on, so nobody can work out the code for another surface. If a model later recites the code for a page, it read that page. The same method works for anyone publishing research or models.</p>
<ol>
<li>State your terms in machine-readable form: a Content-Signal line in robots.txt, a tdmrep.json file, a tdm-reservation header or meta tag, and a short notice in the footer.</li>
<li>Give each page, file or dataset card its own reference code. Keep the key private.</li>
<li>Archive your terms and pages. Save them on the Wayback Machine and keep a hash of the files in a public repository commit so the date can be checked later.</li>
<li>Keep a private list of the codes and where each one sits.</li>
<li>Ask models for your codes now and then, and keep the date, the model version and the full reply.</li>
</ol>
<pre><code>import hmac, hashlib
def ref(surface, key):
    return "HLC-" + hmac.new(key.encode(), surface.encode(), hashlib.sha256).hexdigest()[:8].upper()</code></pre>
</section>'''


# 27 Oct 2026: counts from our own judge and orchestration logs (iris_index/judge_counts/summary.json). Counts only, no log text.
import json as _jj
_J = _jj.load(open(os.path.join(HERE, '..', 'iris_index', 'judge_counts', 'summary.json')))
def _f(n): return f'{n:,}'
def _pct(a): return f'{a[0]}% [{a[1]}, {a[2]}]'
_jd, _jo = _J['judge'], _J['orchestration']
IRIS_JUDGE = (
 '<section><h2>Models as judges in our own pipeline</h2>'
 '<p>Counts from the logs of our own judge and orchestration code. The logs are not published. The script and the counts are: <a href="https://huggingface.co/datasets/indahl/iris-judge-counts">Hugging Face dataset</a>. These are the IRIS code <a class="code" href="/iris/key#L7">L7</a> cases in our own setup. The judge log tags each verdict with the name of an adapter or a short label, not with an item id, so these counts cannot say how often the judge gives the same verdict on the same item.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>Measure</th><th>Count</th><th>Share, 95% interval</th></tr></thead><tbody>'
 f'<tr><td>Judge verdicts recorded</td><td>{_f(_jd["verdicts"])}</td><td>&mdash;</td></tr>'
 f'<tr><td>Verdicts logged under the two names of our own adapter</td><td>{_f(_jd["verdicts_under_adapter_names"])}</td><td>&mdash;</td></tr>'
 f'<tr><td>Hold (no decision)</td><td>{_f(_jd["hold"])}</td><td>{_pct(_jd["hold_share_pct"])}</td></tr>'
 f'<tr><td>Discard</td><td>{_f(_jd["discard"])}</td><td>{_pct(_jd["discard_share_pct"])}</td></tr>'
 f'<tr><td>Keep</td><td>{_f(_jd["keep"])}</td><td>{_pct(_jd["keep_share_pct"])}</td></tr>'
 f'<tr><td>Errors counted by the judge&rsquo;s own log</td><td>{_f(_jd["errors_counter_sum"])}</td><td>&mdash;</td></tr>'
 f'<tr><td>Orchestrating model: rounds logged</td><td>{_f(_jo["rounds"])}</td><td>&mdash;</td></tr>'
 f'<tr><td>Rounds in which three models were asked</td><td>{_f(_jo["rounds_with_three_asks"])}</td><td>&mdash;</td></tr>'
 f'<tr><td>Asks made</td><td>{_f(_jo["asks"])}</td><td>&mdash;</td></tr>'
 f'<tr><td>Asks the harness had to force because the orchestrator did not make the call</td><td>{_f(_jo["asks_forced"])}</td><td>{_pct(_jo["forced_share_pct"])}</td></tr>'
 '</tbody></table></div></section>')
_IRIS_BODY += IRIS_JUDGE
# 27 Oct 2026: numbers from our own LoRA training logs (iris_index/training_counts/summary.json). Numbers only: no training text, no weights.
_T = _jj.load(open(os.path.join(HERE, '..', 'iris_index', 'training_counts', 'summary.json')))
_tt, _te = _T['totals'], {e['file']: e for e in _T['evals']}
def _loss_svg(runs):
    pts = [(i, r['val_first'], r['val_last']) for i, r in enumerate(runs) if r['val_last'] is not None]
    W, H, L, B = 640, 220, 44, 28
    lo, hi = 1.0, 2.6
    X = lambda i: L + (W - L - 8) * i / max(1, len(runs) - 1)
    Y = lambda v: 8 + (H - B - 8) * (1 - (min(max(v, lo), hi) - lo) / (hi - lo))
    g = ''.join(f'<line x1="{L}" x2="{W-8}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="gl"/><text x="{L-6}" y="{Y(v)+4:.1f}" text-anchor="end" class="ax">{v:.1f}</text>' for v in (1.0, 1.4, 1.8, 2.2, 2.6))
    a = ''.join(f'<circle cx="{X(i):.1f}" cy="{Y(f):.1f}" r="2.2" class="d1"/>' for i, f, l in pts)
    b = ''.join(f'<circle cx="{X(i):.1f}" cy="{Y(l):.1f}" r="2.2" class="d2"/>' for i, f, l in pts)
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Validation loss at the first and last check of each training session, in order" class="losschart">{g}{a}{b}'
            f'<text x="{L}" y="{H-8}" class="ax">first session</text><text x="{W-8}" y="{H-8}" text-anchor="end" class="ax">last session</text>'
            f'<circle cx="{W//2-85}" cy="{H-12}" r="3" class="d1"/><text x="{W//2-78}" y="{H-8}" class="ax">first check</text><circle cx="{W//2-5}" cy="{H-12}" r="3" class="d2"/><text x="{W//2+2}" y="{H-8}" class="ax">last check</text></svg>')
_fe, _he = _te['freshdata_v23_vs_live.json'], _te['heavy_v20_vs_live.json']
IRIS_TRAIN = (
 '<section><h2>Our own fine-tuning runs</h2>'
 '<p>Numbers from the logs and configs of our own LoRA fine-tuning of one open model. The training text, the adapter weights and the logs are not published. The extraction script and the numbers are: <a href="https://huggingface.co/datasets/indahl/iris-training-runs">Hugging Face dataset</a>. These are the IRIS code <a class="code" href="/iris/key#L6">L6</a> and <a class="code" href="/iris/key#L7">L7</a> cases in our own setup.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>Measure</th><th>Value</th></tr></thead><tbody>'
 f'<tr><td>Training sessions in the log</td><td>{_tt["runs_with_curves"]}</td></tr>'
 f'<tr><td>Iterations across them</td><td>{_f(_tt["iterations"])}</td></tr>'
 f'<tr><td>Tokens trained on, summed over sessions</td><td>{_f(_tt["trained_tokens"])}</td></tr>'
 f'<tr><td>Validation checks logged</td><td>{_f(_tt["val_loss_lines"])}</td></tr>'
 f'<tr><td>Validation checks where the loss was not a number</td><td>{_tt["nan_val_lines"]}</td></tr>'
 f'<tr><td>Training lines logged, and how many had a loss that was not a number</td><td>25,768 and {_tt["nan_train_lines"]}</td></tr>'
 f'<tr><td>Sessions that reached a loss that was not a number</td><td>{_tt["runs_with_nan"]} of {_tt["runs_with_curves"]}</td></tr>'
 f'<tr><td>Sessions before the validation fix whose last validation loss was below their first, of those with numbers at both</td><td>{_T["by_period"]["before_fix"]["runs_val_improved"]} of {_T["by_period"]["before_fix"]["runs_with_finite_val"]}</td></tr>'
 f'<tr><td>Sessions before the validation fix whose lowest validation loss came before their last check</td><td>{_T["by_period"]["before_fix"]["runs_val_min_before_last"]} of {_T["by_period"]["before_fix"]["runs_with_finite_val"]}</td></tr>'
 f'<tr><td>Sessions after the validation fix whose last validation loss was below their first, of those with numbers at both</td><td>{_T["by_period"]["after_fix"]["runs_val_improved"]} of {_T["by_period"]["after_fix"]["runs_with_finite_val"]}</td></tr>'
 f'<tr><td>Sessions after the validation fix whose lowest validation loss came before their last check</td><td>{_T["by_period"]["after_fix"]["runs_val_min_before_last"]} of {_T["by_period"]["after_fix"]["runs_with_finite_val"]}</td></tr>'
 f'<tr><td>Adapter folders and saved checkpoints</td><td>{_tt["adapter_dirs"]} and {_f(_tt["checkpoints"])}</td></tr>'
 f'<tr><td>Candidate against the live adapter on {_he["scenarios"]} fixed scenarios, one skipped for a judge error: scenarios won on a majority of axes</td><td>{_he["axis_majority_wins"]} of {_he["scored"]}</td></tr>'
 f'<tr><td>Second candidate on {_fe["scenarios"]} scenarios</td><td>{_fe["axis_majority_wins"]} of {_fe["scored"]}</td></tr>'
 f'<tr><td>Candidates that cleared our promotion bar of more than half the scenarios</td><td>{_tt["evals_promoted"]} of {_tt["evals"]}</td></tr>'
 '</tbody></table></div>'
 '<p>Until 26 August the validation step scored a random 100 of the 489 validation examples, a different 100 each time. Sessions started from the same weights on the same file gave a first-check loss anywhere from 1.478 to 2.116 before any training step, so changes in validation loss of that size inside those sessions are not a training effect. After the fix every check scores 488 of 489. The session rows are split at that fix, a split defined after the pooled counts were read. Before it, a lowest loss that comes before the last check is what random scoring gives most of the time, so those rows do not show how training went. The chart pools both periods.</p>'
 + _loss_svg(_T['runs']) + '</section>')
_IRIS_BODY += IRIS_TRAIN
_IRIS_BODY += ('<section class="tight"><h2>Inventory of Published Studies</h2><p>Every published language-model study IRIS has read and indexed, with its IRIS classification, the date it was indexed and a receipt of what was read: '
               '<a href="/iris/list"><b>The List</b></a> &middot; <a href="/iris/list.json">download</a></p></section>') + IRIS_FG + IRIS_MARK + IRIS_DISC
import re as _r3, html as _h3, os

# 27 Oct 2026: one page per IRIS study row, built from the same table cells as the IRIS page.
_IR = os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'iris', 'runs')
def _snip(t, n=150, cap=200):   # 30 Oct 2026: a meta description is whole sentences. The last sentence end within n characters, else the first sentence end within cap, else a cut at a word before n that is not inside a bracket.
    if len(t) <= n: return t
    ends = [m.end() for m in _r3.finditer(r'(?<=[A-Za-z0-9%\)\]])\.(?=\s|$)', t)]
    ok = [e for e in ends if e <= n]
    if ok: return t[:ok[-1]]
    ok = [e for e in ends if e <= cap]
    if ok: return t[:ok[0]]
    c = t[:n]
    for o_, c_ in ('()', '[]'):
        if c.count(o_) > c.count(c_): c = c[:c.rindex(o_)]
    return c.rsplit(' ', 1)[0].rstrip(' ,;:') + '.'
_ipairs = []
for _m in _r3.finditer(r'<tr>(.*?)</tr>', _IRIS_BODY, _r3.S):
    _c = _r3.findall(r'<td>(.*?)</td>', _m.group(1), _r3.S)
    if len(_c) == 4 and 'arxiv.org/abs/' in _c[0] and 'class="code"' in _c[3]:
        _ipairs.append((_m.group(0), _c, _r3.search(r'arxiv\.org/abs/(\d{4}\.\d{4,5})', _c[0]).group(1)))
for _old, _c, _id in _ipairs:
    _IRIS_BODY = _IRIS_BODY.replace(_old, _old.replace(_c[0] + '</td>', _c[0] + '<br><span class="by"><a href="/iris/study/' + _id + '">Study page</a></span></td>', 1), 1)
    _title = _h3.unescape(_r3.sub(r'<[^>]+>', ' ', _c[0].split('<br>')[0])).strip()
    _what = ' '.join(_h3.unescape(_r3.sub(r'<[^>]+>', ' ', _c[2])).split()); _desc = _snip(_what)
    _zn = 'study-' + _id + '.zip'; _data = f'<p><a class="btn ghost" href="/iris/runs/{_zn}">Download the data for this study (zip)</a></p>' if os.path.exists(os.path.join(_IR, _zn)) else ''
    _body = (f'<section class="legal"><p class="meta">Recounted study. <a href="/iris">All IRIS studies</a> &middot; <a href="/iris/key">Key</a></p>'
             f'<h2>Study</h2><p>{_c[0]}</p><h2>Also in their released files</h2><p>{_c[1]}</p><h2>What it shows about the model</h2><p>{_c[2]}</p><h2>IRIS codes</h2><p>{_c[3]}</p>{_data}'
             f'<p class="meta">{"Intervals are 95% Welch intervals, three seeds against three." if _id == "2610.25626" else "Intervals are 95%, by percentile bootstrap over items."} A classification for indexing, not an assessment of the study or its authors. Names appear as published. To correct or remove this page, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
    _p = '/iris/study/' + _id
    PAGES[_p] = page(_p, f'arXiv {_id} recount | IRIS | Heuremen LLC', _desc, _body, hero_slim(f'Recount of arXiv {_id}'))
    _FEED.append((_p, f'arXiv {_id} recount (IRIS)', _desc))
print('iris study pages', len(_ipairs))
# 28 Oct 2026 (his word): the papers table (what a study prints against what its released data shows) moves to SAD. No link is left on IRIS.
_ps = _IRIS_BODY.find('<section><h2>What the Papers’ Own Released Data Shows');_pe = _IRIS_BODY.find('</section>', _ps) + 10; assert _ps > 0
_PAPERS_SEC = _IRIS_BODY[_ps:_pe]; _IRIS_BODY = _IRIS_BODY[:_ps] + _IRIS_BODY[_pe:]
PAGES['/hermes/model'] = page('/hermes/model', 'MODEL | Stated Against Delivered | Heuremen LLC', 'MODEL: what AI hardware vendors and papers state, held against the published MLCommons results and the papers\' own released data, with the quoted sentence, the entry and the outcome for every row.', _SADBODY.replace('<!--PAPERS--><section class="legal">', '<section class="legal">'), hero_slim('MODEL &middot; Stated Against Delivered'))
PAGES['/hermes/model/papers'] = page('/hermes/model/papers', 'Papers: What Each Study States and Its Data Shows | MODEL | Heuremen LLC', 'What each indexed study prints against what its own released data shows, with the quoted sentence and the outcome.', '<section class="legal"><p class="meta"><a href="/hermes/model">MODEL</a> &middot; <a href="/hermes/model#sources">All sources</a></p>' + _PAPERS_SEC + _SAD_CORR + '</section>', hero_slim('Papers'))
_FEED.append(('/hermes/model/papers', 'Papers (MODEL)', 'What each indexed study prints against what its own released data shows.'))


PAGES['/iris'] = page('/iris', 'Recount Matrix: Language Models | IRIS | Heuremen LLC',
 'Recount Matrix: Language Models. Published language-model evaluations recounted from their own released files, with a source for every row.',
 IRIS_TOP + _IRIS_BODY, hero_slim('IRIS &middot; Inorganic Research &amp; Intelligence Systems'))
# 30 Oct 2026 (his word, 'it needs its own desk'): the lab sections move off /iris to their own desk, LAB, at /iris/lab. The stale 'Running Now' table is dropped.
# 9 Nov 2026 (his word: "just one big chunk of text at the top"): the LAB page opens on a short lead, and YO moves to its own desk at /yo.
LAB_LEAD = ('<section class="lablead"><p class="lede">Models we train and test ourselves. Each run opens on its result, with its tables, method and data one click below.</p>'
            '<p><a href="#stan">STAN, training live</a> &middot; <a href="/yo">YO, our model for IBM calibration records</a></p></section>')
# 13 Nov 2026 (Sage's terms, Wayfinder's go): one lane retired from LAB
PAGES['/iris/lab'] = page('/iris/lab', 'LAB: Our Own Model Runs | IRIS | Heuremen LLC',
 'Our own model runs: STAN training live, a small model trained on the house&rsquo;s own answers, a Falcon trained on the Standards, the finalists head to head, and how open models handle Standards.',
 (LAB_LEAD + IRIS_STAN + IRIS_FLOCK + IRIS_FALCON + IRIS_THUNDER + IRIS_BENCH).replace('<h2>Live From Our Lab: ', '<h2>'), hero_slim('LAB', 'Our Own Model Runs'))
HOME['/iris/lab'] = '/iris'
# 13 Nov 2026 (Sage's terms, Wayfinder's go): the /iris/lab/live page is retired
# 9 Nov 2026 (his word): YO gets its own desk. Everything about YO lives here: what it is, its live reads of IBM records, and how it was trained and tested.
YO_LEAD = ('<section class="yolead"><p class="lede">YO is a small language model trained on IBM&rsquo;s qubit calibration records to find stale data in them. '
           'It is Qwen3-1.7B, a small open-weight model (Apache-2.0), trained by us with LoRA on IBM&rsquo;s own calibration history. '
           'For each record it flags qubits whose T1 or T2 was measured more than a day before the record&rsquo;s stamp, and error values of exactly zero. '
           'YO v7 is the model at work. It reads each new IBM record live, and code computes the right answer from the same record beside it.</p>'
           '<p><a href="https://huggingface.co/indahl/YO">Download YO (Hugging Face)</a> &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo">Code (git)</a> &middot; '
           '<a href="/qia/package">QIA Research Package</a>, which runs YO beside the record checker &middot; <a href="/qia">QIA</a></p></section>')
YO_READS = ('<section id="yo" class="bench" hidden><h2>YO Reads Each New Record</h2>'
      '<p>For every new record IBM publishes, YO is shown eight of its qubits and flags those whose T1 or T2 was measured more than a day before the record&rsquo;s stamp, and error values of exactly zero. '
      'The code computes the right answer from the same record, and both are shown side by side. The reads below are by YO v7, the model at work. Anyone can run it on a record of their own: <a href="https://huggingface.co/indahl/YO">YO on Hugging Face</a>. How YO was trained and tested is below.</p>'
      '<div id="yo-reads" class="bench-live"></div><script src="/qia/yo.js" defer></script></section>')
PAGES['/yo'] = page('/yo', 'YO: A Small Model for IBM Calibration Records | IRIS | Heuremen LLC',
 'YO is a small language model (Qwen3-1.7B, LoRA) trained on IBM qubit calibration records to flag stale data. Its live reads of each new record, and how every version was trained and tested.',
 YO_LEAD + YO_READS + IRIS_YO.replace('<h2>YO: A Small Model Trained to Audit IBM&rsquo;s Records</h2>', '<h2>How YO Was Trained and Tested</h2>', 1),
 hero_slim('YO', 'A Small Model for IBM Calibration Records'))
HOME['/yo'] = '/iris'
HOME['/stack'] = '/hermes'   # 10 Nov (Wayfinder): STACK lives under HERMES now; SOCIAL has the banner slot
_FEED.append(('/yo', 'YO: a small model for IBM calibration records', 'What YO is, its live reads of each new IBM record, and how every version was trained and tested.'))
PAGES['/iris/key'] = page('/iris/key', 'IRIS Key | IRIS | Heuremen LLC', 'IRIS codes: what moves a language-model result besides the model, where we measured it, and the indexed studies it touches.',
 open(os.path.join(HERE, '..', 'iris_index', 'matrix_page', 'iris_key_body.html'), encoding='utf-8').read() + IRIS_DISC, hero_slim('IRIS Key', ''))
PAGES['/iris/list'] = page('/iris/list', 'The List: Inventory of Published Studies | IRIS | Heuremen LLC', 'Every published language-model study IRIS has read and indexed, with its classification, date indexed and receipt.',
 _re.sub(r'<tr><td><a href="https://arxiv\.org/abs/(\d{4}\.\d{4,5})(v\d+)?"', lambda m: '<tr id="arxiv-' + m.group(1) + '"><td><a href="https://arxiv.org/abs/' + m.group(1) + (m.group(2) or '') + '"', open(os.path.join(HERE, '..', 'iris_index', 'matrix_page', 'iris_list_body.html'), encoding='utf-8').read()) + IRIS_DISC, hero_slim('The List', 'Inventory of Published Studies'))   # 2 Nov: row ids, as on the QIA List, so the list pack's links land on the row

# 25 Oct 2026 (his word): QIA = Recount Matrix: Quantum Hardware (Calibration Report: IBM, companies, the book), same form as OY and IRIS.
# "Data only, no services for now": the service pages are kept in HELD_QIA / HELD_SERVICES, so restoring them is one line.
HELD_QIA = PAGES.pop('/qia')
HELD_SERVICES = {'/approach': PAGES.pop('/approach')}
_QIA_BODY = open(os.path.join(HERE, '..', 'qia_leads', 'matrix_page', 'qia_body.html'), encoding='utf-8').read()
# 27 Oct 2026: one page per calibrated study, built from the same table cells as the QIA page (so a page can never drift from its row).
import re as _r2, html as _h2
_STUDY_ROWS = []
def _study_rows(body):
    i = body.index('Calibrated Studies: Corporate'); seg = body[i:body.index('Inventory of Published Studies')] if 'Inventory of Published Studies' in body[i:] else body[i:]
    for m in _r2.finditer(r'<tr(?: id="[^"]*")?>(.*?)</tr>', seg, _r2.S):   # 31 Oct 2026: rows carry anchors (qia_leads/matrix_page/add_anchors.py)
        cells = _r2.findall(r'<td>(.*?)</td>', m.group(1), _r2.S)
        if len(cells) == 6: yield m, cells
def _slug_for(cells, used):
    ax = cells[1]
    mm = _r2.search(r'arxiv\.org/abs/(\d{4}\.\d{4,5})', ax) or _r2.search(r'arxiv\.org/abs/([a-z\-]+/\d+)', ax)
    z = _r2.search(r'zenodo(?:\.org/records?/|\.)(\d{6,9})', ax)
    base = mm.group(1).replace('/', '-') if mm else ('zenodo-' + z.group(1) if z else _r2.sub(r'[^a-z0-9]+', '-', _r2.sub(r'<[^>]+>', '', _h2.unescape(cells[0] + ' ' + ax)).lower()).strip('-')[:48])
    slug, n = base, 2
    while slug in used: slug = f'{base}-{n}'; n += 1
    used.add(slug); return slug
_used = set(); _new_body = _QIA_BODY; _pairs = []
for _m, _c in list(_study_rows(_QIA_BODY)):
    _sl = _slug_for(_c, _used); _pairs.append((_m.group(0), _c, _sl))
for _old, _c, _sl in _pairs:
    _row = _old.replace(_c[1] + '</td>', _c[1] + '<br><span class="by"><a href="/qia/study/' + _sl + '">Study page</a></span></td>', 1)
    _new_body = _new_body.replace(_old, _row, 1)
_QIA_BODY = _new_body
assert _pairs or 'Calibrated Studies' not in _QIA_BODY, 'REFUSED: the calibrated tables gave no study rows (31 Oct: anchored rows once dropped all 196 study pages)'
_RUNS = os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'qia', 'runs')
# 30 Oct 2026 (site pass C-16): the meta description ends at a sentence end or a clause with its brackets and quotes closed, never mid-bracket or on a dangling word.
def _meta_desc(t, n=150):
    if len(t) <= n: return t
    cut = t[:n]; k = max((m.end() for m in _r2.finditer(r'[.!?](?=\s)', cut)), default=0)
    if k >= 50: return cut[:k]
    def ok(w): return w.count('(') == w.count(')') and w.count('[') == w.count(']') and w.count('"') % 2 == 0 and w.count('\u201c') == w.count('\u201d')
    for m in reversed(list(_r2.finditer(r'[,:](?=\s)', cut))):
        c = cut[:m.start()]
        if len(c) >= 50 and ok(c): return c + '.'
    w = cut.rsplit(' ', 1)[0]
    while w and (not ok(w) or _r2.search(r'(?i)(\b(a|an|the|of|to|on|in|for|with|and|or|by|at|is|are|as|from|than|per|against)|[\u00b1(\[,:+\-/])$', w)): w = w.rsplit(' ', 1)[0] if ' ' in w else ''
    return (w.rstrip(' ,;:') + '.') if w else cut
_ROWDATES = _jsonld.load(open(os.path.join(HERE, '..', 'qia_leads', 'matrix_page', 'row_dates.json'))) if os.path.exists(os.path.join(HERE, '..', 'qia_leads', 'matrix_page', 'row_dates.json')) else {}
for _old, _c, _sl in _pairs:
    _org, _work, _pub, _meas, _cal, _how = _c
    _lab = _r2.search(r'>(arXiv [^<]+|Zenodo [^<]+|GitHub[^<]*|OSF[^<]*|[^<]*\d{4}\.\d{4,5}[^<]*)</a>', _work)
    _arx = _r2.match(r'^(\d{4}\.\d{4,5})(?:-\d+)?$', _sl)   # 30 Oct 2026 (site pass C-15): a title-linked row is named by its arXiv id, the IBM tutorial by its own label
    _id = _lab.group(1) if _lab else ('Zenodo ' + _sl.split('-')[1] if _sl.startswith('zenodo-') else ('arXiv ' + _arx.group(1) if _arx else ('IBM QAOA tutorial' if _sl.startswith('ibm-qaoa-tutorial') else 'Published study')))
    _calt = _h2.unescape(_r2.sub(r'<[^>]+>', ' ', _r2.sub(r'<span class="codes">.*?</span>', '', _cal, flags=_r2.S))); _calt = ' '.join(_calt.split())
    _desc = _meta_desc(_calt)
    globals().setdefault('_STUDY_MOD', {})['/qia/study/' + _sl] = _ROWDATES.get(_sl) or _ROWDATES.get(_r2.sub(r'-\d+$', '', _sl)) or '2026-10-27'   # C-17: the row's last change, from matrix_page/row_dates.json
    _zip = f'{_sl}.zip'; _hasz = os.path.exists(os.path.join(_RUNS, _zip)) or os.path.exists(os.path.join(_RUNS, 'study-' + _sl + '.zip'))
    _zipname = _zip if os.path.exists(os.path.join(_RUNS, _zip)) else 'study-' + _sl + '.zip'
    _data = f'<p><a class="btn ghost" href="/qia/runs/{_zipname}">Download the data for this study (zip)</a></p>' if _hasz else ''
    _body = (f'<section class="legal"><p class="meta">Calibrated study. <a href="/qia">All QIA calibrated studies</a> &middot; <a href="/qia/key">Key</a></p>'
             f'<h2>Work</h2><p><b>{_org}</b></p><p>{_work}</p>'
             f'<h2>Published</h2><p>{_pub}</p><h2>Measured or recounted</h2><p>{_meas}</p>'
             f'<h2>QIA Calibration</h2><p>{_cal}</p><h2>How</h2><p>{_how}</p>{_data}'
             f'<p class="meta">A classification for indexing, not an assessment of the study or its authors. Names appear as published. To correct or remove this page, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
    _p = '/qia/study/' + _sl
    PAGES[_p] = page(_p, f'{_id} recount | QIA | Heuremen LLC', _desc, _body, hero_slim(f'Recount of {_id}'))
    _FEED.append((_p, f'{_id} recount (QIA)', _desc))
print('study pages', len(_pairs))

# 12 Nov 2026: SAGAR (Standards Audit of Gravitational and Astrophysical Research). One list page and one page per listed paper, built from the same table cells
# (sagar/site/sagar_list_body.html, written by sagar/site/make_sagar.py from the record), so a study page cannot drift from its row. No author names, no notice window.
_SG_DIR = os.path.join(HERE, '..', 'sagar', 'site'); _SG_PATH = os.path.join(_SG_DIR, 'sagar_list_body.html')
if os.path.exists(_SG_PATH):
    _SG_BODY = open(_SG_PATH, encoding='utf-8').read(); _SG_PAIRS = []
    for _m in _r2.finditer(r'<tr id="arxiv-(\d{4}\.\d{4,5})">(.*?)</tr>', _SG_BODY, _r2.S):
        _cs = _r2.findall(r'<td>(.*?)</td>', _m.group(2), _r2.S)
        if len(_cs) == 6: _SG_PAIRS.append((_m.group(0), _m.group(1), _cs))
    assert _SG_PAIRS, 'REFUSED: sagar_list_body.html gave no rows'
    _SGB = _SG_BODY
    for _old, _id, _cs in _SG_PAIRS:
        _SGB = _SGB.replace(_old, _old.replace(_cs[0] + '</td>', _cs[0] + '<br><span class="by"><a href="/sagar/study/' + _id + '">Study page</a></span></td>', 1), 1)
    _SG_DISC = '<section class="disclose"><p>Papers listed are for information only. Please <a href="/contact">click here to ask to be removed from our index</a>. Heuremen LLC is an independent, private company with no stake, value or interest in any paper listed here. All employees are required to <a href="/conflict-of-interest">certify</a> that they have no business interest in any work indexed here that could pose a conflict of interest.</p></section>'
    PAGES['/sagar'] = page('/sagar', 'SAGAR: Errata Index for Gravitational-Wave Papers | Heuremen LLC',
        'Checkable errata in gravitational-wave papers, each with a verbatim quote from the paper and where the paper shows otherwise, confirmed by two independent readers.',
        _SGB + _SG_DISC, hero_slim('SAGAR', 'Standards Audit of Gravitational and Astrophysical Research'))
    for _old, _id, _cs in _SG_PAIRS:
        _w, _vr, _pr, _sh, _ct, _hw = _cs
        _tx = ' '.join(_h2.unescape(_r2.sub(r'<[^>]+>', ' ', _sh)).split())
        _p = '/sagar/study/' + _id
        globals().setdefault('_STUDY_MOD', {})[_p] = '2026-11-12'
        _body = (f'<section class="legal"><p class="meta">Errata study page. <a href="/sagar">SAGAR</a></p>'
                 f'<h2>Work</h2><p>{_w}</p><h2>Version Read</h2><p>{_vr}</p>'
                 f'<h2>What the Paper Prints</h2>{_pr}<h2>What the Paper Shows Elsewhere</h2>{_sh}'
                 f'<h2>Code and Tier</h2><p>{_ct}</p><h2>How It Was Checked</h2><p>{_hw}</p>'
                 f'<p class="meta">A classification for indexing, not an assessment of the study or its authors. A correction you can check. To correct or remove this page, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
        PAGES[_p] = page(_p, f'arXiv {_id} errata | SAGAR | Heuremen LLC', _meta_desc(_tx), _body, hero_slim(f'Errata in arXiv {_id}'))
        _FEED.append((_p, f'arXiv {_id} errata (SAGAR)', _meta_desc(_tx)))
    _RC = os.path.join(HERE, '..', 'sagar', 'receipts')   # the one recompute receipt, text and script as written
    if os.path.exists(os.path.join(_RC, '2603.29019_sigma.md')):
        _rp = '/sagar/receipts/2603.29019_sigma'
        PAGES[_rp] = page(_rp, 'arXiv 2603.29019 recompute receipt | SAGAR | Heuremen LLC', 'Recompute of the sigma_global interval in arXiv 2603.29019 from the authors’ released posterior samples, with the script.',
            '<section class="legal"><p class="meta"><a href="/sagar/study/2603.29019">Study page</a> &middot; <a href="/sagar">SAGAR</a></p><h2>Receipt</h2><pre style="white-space:pre-wrap">' + _h2.escape(open(os.path.join(_RC, '2603.29019_sigma.md'), encoding='utf-8').read()) +
            '</pre><h2>Script</h2><pre style="white-space:pre-wrap">' + _h2.escape(open(os.path.join(_RC, '2603.29019_sigma.py'), encoding='utf-8').read()) + '</pre></section>', hero_slim('Recompute receipt for arXiv 2603.29019'))
    print('sagar pages', len(_SG_PAIRS))

PAGES['/qia'] = page('/qia', 'QIA: IBM hardware deviations and calibrated quantum studies | Heuremen LLC',
 'IBM processors measured against their published calibration, the studies QIA calibrated with the fix for each, and the List of every published study QIA has indexed, with a source for every row.',
 _QIA_BODY, hero_slim('QIA &middot; Quantum Idle Audit'))
# 25 Oct 2026: QIA sub-pages (the Key and the List; the grid was retired by his word the same day).
import json as _json
for _p, _v in _json.load(open(os.path.join(HERE, '..', 'qia_leads', 'matrix_page', 'qia_pages.json'), encoding='utf-8')).items():
    PAGES[_p] = page(_p, _v['title'], _v['desc'], _v['body'], hero_slim(_v['h1'], _v['sub']))

# 12 Nov 2026 (Wayfinder: "start with the qubit data"): QIA QUBIT DATA, the index of published qubit and quantum-device datasets beyond IBM that release
# raw measurement files (qdata_index/list.json, built by qdata_index/sweep/qdata_sweep.py, hand drops in qdata_index/hand_drops.json). The list is copied
# to /qia/data.json on every build. Funding screen: defence, military and intelligence funders out, civilian science funders kept.
def _index_list(path, src, dl, crumb, col):
    import html as _h
    d = _json.load(open(src, encoding='utf-8')); rows = sorted(d['studies'], key=lambda r: (r.get(col) or '', r['study'].lower()))
    shutil.copy(src, os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', dl.lstrip('/')))
    E_ = _h.escape
    tr = ''.join('<tr id="%s"><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td><details><summary>receipt</summary><ul>%s</ul></details></td></tr>'
                 % (E_(r.get('anchor') or ''), E_(r['link']), E_(r['study']), E_(r.get(col) or ''), E_(r.get('classification') or ''), E_(r.get('indexed') or ''), ''.join('<li>%s</li>' % E_(x) for x in r.get('receipt', [])))
                 for r in rows)
    return (crumb + ' &middot; <a href="%s">download</a></p><section><div class="scroll"><table class="mtx list"><thead><tr><th>Dataset</th><th>%s</th><th>Classification</th><th>Indexed</th><th>Receipt</th></tr></thead><tbody>%s</tbody></table></div></section>'
            % (dl, col.capitalize(), tr)), len(rows)
import shutil
_qd_body, _qd_n = _index_list('/qia/data', os.path.join(HERE, '..', 'qdata_index', 'list.json'), '/qia/data.json', '<p class="crumb"><a href="/qia">Quantum Idle Audit</a> &middot; <a href="/qia/list">The List</a>', 'platform')
_qd_intro = ('<section class="legal"><p>Published datasets from qubit and quantum-device experiments beyond IBM: superconducting qubits from other labs and vendors, trapped ions, '
             'neutral atoms, NV centers and spin qubits, quantum dots, photonics, sensing, and the raw output of quantum key distribution and random number generators. '
             'A dataset is listed when it releases measurement files. Records with code or figures only, simulations only, or no open files are left out. '
             'Studies funded by defence, military or intelligence agencies of any country are left out. Civilian science funders are kept. '
             'The classification is for indexing, not an assessment. IBM device studies are on <a href="/qia/list">The List</a>. Removal on request, any time.</p></section>')
PAGES['/qia/data'] = page('/qia/data', 'Qubit Data: Published Quantum-Device Datasets | QIA | Heuremen LLC', 'Published datasets from qubit and quantum-device experiments beyond IBM that release raw measurement files, with platform, classification and receipt.',
                          _qd_intro + _qd_body, hero_slim('Qubit Data', 'Published quantum-device datasets beyond IBM'))
_FEED.append(('/qia/data', 'QIA: Qubit Data, published quantum-device datasets beyond IBM', 'Published datasets from qubit and quantum-device experiments beyond IBM that release raw measurement files.'))

# 12 Nov 2026 (Wayfinder: "give it a once over and put it on the site, we'll work on it there"): HERMES DATA PAPERS, papers in four data journals
# indexed with the file list their repository serves (datapaper_index/list.json from datapaper_index/sweep/datapaper_sweep.py, headline from summary.json,
# ledger rows datapapers.zenodo.essd and .dib). Same funding screen as Qubit Data.
_dps = _json.load(open(os.path.join(HERE, '..', 'datapaper_index', 'summary.json'), encoding='utf-8'))['zenodo_by_journal']
_e, _d2 = _dps['Earth System Science Data'], _dps['Data in Brief']
_DPSLOT = ('<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%d percent</div><p class="hl-line">of the Earth System Science Data papers indexed here keep their released files on Zenodo, %d of %d. In Data in Brief it is %d percent, %d of %d.</p></section>'
           % (_e['pct'], _e['zenodo'], _e['indexed'], _d2['pct'], _d2['zenodo'], _d2['indexed']))
_dp_body, _dp_n = _index_list('/hermes/datapapers', os.path.join(HERE, '..', 'datapaper_index', 'list.json'), '/hermes/datapapers.json', '<p class="crumb"><a href="/hermes">HERMES</a>', 'journal')
_dp_intro = ('<section class="legal"><p>Papers published since January 2024 in Scientific Data, Earth System Science Data, Data in Brief and GigaScience, each listed with the files '
             'its repository serves: Zenodo, Figshare, Mendeley Data, PANGAEA and OSF, read through each repository\'s public interface. Files were listed, never downloaded. '
             'A paper is listed when its repository record returns a file list. Papers whose data sits where no public file list can be read, such as GitHub or Dataverse, wait for a hand look. '
             'Studies funded by defence, military or intelligence agencies of any country are left out. Civilian science funders are kept. '
             'The newest papers in each journal come first, and older ones are being added. The classification is for indexing, not an assessment. Removal on request, any time.</p></section>')
PAGES['/hermes/datapapers'] = page('/hermes/datapapers', 'Data Papers: Published Datasets and Their Files | HERMES | Heuremen LLC', 'Papers in Scientific Data, Earth System Science Data, Data in Brief and GigaScience, each listed with the files its repository serves.',
                                   _dp_intro + _dp_body, hero_slim('Data Papers', 'Published datasets and the files their repositories serve'))
_FEED.append(('/hermes/datapapers', 'HERMES: Data Papers, published datasets and their files', 'Papers in four data journals, each listed with the files its repository serves.'))

# 12 Nov 2026 (Wayfinder: "Standards V1 is fucking lit"): STANDARD, Faults and Guards version 1.0 (faultsguards/standard_v1, concept DOI 10.5281/zenodo.24164029, 1.0.1 is 24164207),
# rendered by faultsguards/standard_v1/web/build_page.py, files served at /standard/*.
# 13 Nov 2026 (Wayfinder: "just STANDARDS ... just list the standards without the explanation, a separate collapsed link for the process"):
# the page is the list, read straight from faultsguards/standard_v1/standard_v1.json; process and files sit in one collapsed block.
import html as _hS
_sd = _json.load(open(os.path.join(HERE, '..', 'faultsguards', 'standard_v1', 'standard_v1.json'), encoding='utf-8'))
_e = _hS.escape
def _sl(items, key):
    return '<ul class="stdlist">' + ''.join('<li id="%s"><b>%s</b> %s</li>' % (_e(x['id']), _e(x[key]), _e(x['name'])) for x in items) + '</ul>'
_fam = {f['id']: f['title'] for f in _sd['families']}; _gp = {g['id']: g['title'] for g in _sd['guard_parts']}
_flt = ''.join('<h3>%s</h3>%s' % (_e(_fam[k]), _sl([x for x in _sd['faults'] if x['family'] == k], 'id')) for k in _fam if any(x['family'] == k for x in _sd['faults']))
_grd = ''.join('<h3>%s</h3>%s' % (_e(_gp[k]), _sl([x for x in _sd['guards'] if x['part'] == k], 'id')) for k in _gp if any(x['part'] == k for x in _sd['guards']))
_codes = '<ul class="stdlist">' + ''.join('<li id="%s"><b>%s</b> %s. %s</li>' % (_e(x['id']), _e(x['code']), _e(x['name']), _e(x['definition'])) for x in _sd['claim_codes']) + '</ul>'
_reqs = _sl(_sd['recount_requirements'], 'id')
_proc = ('<details class="stdproc"><summary>Process</summary>'
         '<p>Each code and fault is read as ' + ', '.join(_e(x['id']) for x in _sd['statuses']) + '. Each reading is ' + ', '.join(_e(x['id']) for x in _sd['reading_outcomes']) + '.</p>'
         '<p>Full text with every test: <a href="/standard/STANDARD.md">STANDARD.md</a>. Machine-readable: <a href="/standard/standard_v1.json">standard_v1.json</a> (<a href="/standard/standard_v1.schema.json">schema</a>). '
         'NIST AI RMF crosswalk: <a href="/standard/CROSSWALK.md">CROSSWALK.md</a>. Version ' + _e(_sd['standard']['version']) + ', <a href="https://doi.org/' + _e(_sd['standard']['doi']) + '">doi:' + _e(_sd['standard']['doi']) + '</a>. '
         '<a href="/standard/SHA256SUMS.txt">Checksums</a>.</p></details>')
_std_body = ('<section class="legal std"><h2>Claim Codes</h2>' + _codes + '<h2>Faults</h2>' + _flt + '<h2>Guards</h2>' + _grd + '<h2>Recount Requirements</h2>' + _reqs + _proc + '</section>')
PAGES['/standard'] = page('/standard', 'Standards | Heuremen LLC', 'The standards Heuremen LLC holds its work to: claim codes, faults, guards and recount requirements.',
                          _std_body, hero_slim('STANDARDS'))
_FEED.append(('/standard', 'STANDARDS', 'The standards Heuremen LLC holds its work to.'))

# 12 Nov 2026 (Wayfinder: "go for all of it"): RECORD, what we recounted, what we found, and every public number of ours that changed after it went out.
# Built by trackrecord/build_trackrecord.py + trackrecord/build_page.py (codes from the QIA List, never the ledger's default outcome label). Ledger row record.f4.share.
_rp = _json.load(open(os.path.join(HERE, '..', 'trackrecord', 'record_page.json'), encoding='utf-8')); _RECSLOT = _rp['slot']
shutil.copy(os.path.join(HERE, '..', 'trackrecord', 'record.json'), os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', 'record.json'))
PAGES['/record'] = page('/record', 'Record: What We Recounted and What We Corrected | Heuremen LLC', 'Every published claim Heuremen LLC recounted, with the fault codes and the finding, and every public number of ours that was corrected after it went out. An open recount record for benchmark and hardware verification.',
                        _rp['body'], hero_slim('Record', 'What we recounted, what we found, and what we corrected'))
_FEED.append(('/record', 'RECORD: what we recounted and what we corrected', 'Every recount with its codes and finding, and every correction of our own numbers.'))

# 12 Nov 2026 (/tp catch, family I): headlines that got stronger under Faults and Guards 2.0, whose size that matters was named after the data
# had been read, say so on their own page, with the earlier reading on Corrections.
_POSTHOC = {'trials': 'The headline', 'hfsize': 'The headline', 'secrecords': 'The HSTS row', 'support': 'The row for products whose every tested cycle is unreleased', 'seat': 'The headline'}
for _ph, _what in _POSTHOC.items():
    _tag = '<script src="/%s/live.js" defer></script>' % _ph
    if '/' + _ph in PAGES and _tag in PAGES['/' + _ph]:
        PAGES['/' + _ph] = PAGES['/' + _ph].replace(_tag, _tag + '<p class="meta">%s is read under <a href="/standard">Standards 2.0</a> from 12 November 2026. The size that matters was named after these data were first read, so its outcome is defined after the data. The earlier reading is on <a href="/corrections">Corrections</a>.</p>' % _what, 1)

# 25 Oct 2026: the worker's policy for indahl.ai pages is style-src 'self' (no inline <style>), so matrix styles live in style.css,
# not in the page bodies. Any <style> block found in a page is moved here and stripped from the page.
_MOVED = []
for _p in list(PAGES):
    for _st in _re.findall(r'<style>(.*?)</style>', PAGES[_p], flags=_re.S):
        if _st not in _MOVED: _MOVED.append(_st)
    PAGES[_p] = _re.sub(r'<style>.*?</style>\n?', '', PAGES[_p], flags=_re.S)
CSS += """
section.tight{padding:8px 0;border-bottom:0}section.tight h2{margin:0 0 4px}section.tight p{margin:4px 0}section.tight+section.tight{padding-top:2px}
.bench{margin:0 0 18px}.bench h2{margin:0 0 8px}.bench-svg{width:100%;height:auto;max-width:760px;display:block}.bench-bg{fill:var(--paper2);stroke:var(--rule);stroke-width:.6}.bench-run{fill:var(--rule)}.bench-done{fill:var(--goldink)}.bench-h{font:600 12px sans-serif;fill:var(--mid)}.bench-m{font:600 13px sans-serif;fill:var(--ink)}.bench-n{font:700 13px sans-serif;fill:var(--goldink)}.bench-note{font-size:13px;color:var(--mid);margin:6px 0 0}.bench h3{margin:22px 0 6px}main .bench~section:not(.tight) h2{font-size:19px;line-height:1.2;margin:0 0 4px}main .bench~section .mtx th{padding:5px 8px;font-size:11.5px;line-height:1.25}main .bench~section .mtx td{padding:3px 8px;font-size:13.5px;line-height:1.3}main .bench~section .by{font-size:12px;line-height:1.3}main .bench~section .scroll+h2{margin-top:16px}main .bench{padding-bottom:6px}.bench>p{margin:6px 0}main .bench~section:not(.tight){padding-top:8px}main .bench~section{padding:12px 0}main .bench~section.tight{padding:6px 0}main section:has(+section.tight){border-bottom:0}main section.markguide{border-bottom:0;padding-bottom:2px}main section.markguide pre{margin:8px 0 0}main section.disclose{padding:8px 0 14px}.scroll+h2{margin-top:22px}.scroll{margin-bottom:2px}.markguide pre{background:var(--paper2);border:1px solid var(--rule);padding:10px 14px;overflow-x:auto;font-size:13.5px;line-height:1.45;margin:10px 0}.markguide ol{margin:6px 0 6px 22px;padding:0}.markguide li{margin:3px 0}.hint{font-size:13.5px;color:var(--mid);margin:-2px 0 16px;line-height:1.45}.row[hidden],.hint[hidden]{display:none}.mtx td .by a[href*="/study/"]{display:inline-block;padding:7px 0}.mtx td a.code{display:inline-block;padding:5px 7px;margin:2px 4px 2px 0}.foot .ai{font-size:12.5px;color:#cbbf9f;max-width:720px;margin:10px auto 0;line-height:1.5;text-align:center}.foot .ai a{display:inline;padding:0;font-size:inherit;color:#efe5cf;text-decoration:underline}.bench-f{font:500 11px sans-serif;fill:var(--mid)}.bench-ct{fill:var(--paper2);stroke:var(--mid);stroke-width:.6;stroke-dasharray:3 2}.bench-cn{font:500 10px sans-serif;fill:var(--mid)}.bench-v{font:600 10px sans-serif;fill:var(--ink)}.atlasmap{width:100%;height:auto;max-width:960px;display:block;margin:10px 0}.elmap path{stroke:var(--paper);stroke-width:.7}.elmap .s0{fill:var(--paper2)}.elmap .s1{fill:var(--goldink);fill-opacity:.1}.elmap .s2{fill:var(--goldink);fill-opacity:.25}.elmap .s3{fill:var(--goldink);fill-opacity:.4}.elmap .s4{fill:var(--goldink);fill-opacity:.55}.elmap .s5{fill:var(--goldink);fill-opacity:.72}.elmap .lb{font:600 9px sans-serif;fill:var(--ink);text-anchor:middle;pointer-events:none}.elmap .lgt{font:500 11px sans-serif;fill:var(--mid)}.elmap.lg{display:block;margin:2px 0 14px;max-width:100%;height:auto}.plmap .f-gas{fill:#c0782e}.plmap .f-coal{fill:#6b6b6b}.plmap .f-nuclear{fill:#7a4fa3}.plmap .f-hydro{fill:#2b78b4}.plmap .f-wind{fill:#2e9a8a}.plmap .f-solar{fill:#e0b000}.plmap .f-storage{fill:#d0408a}.plmap .f-oil{fill:#a65d57}.plmap .f-other{fill:#aaa}.plmap circle[class^=f-]{fill-opacity:.8;stroke:var(--paper);stroke-width:.3}.plmap .e{fill:none}.plmap .st{fill:var(--paper2);stroke:var(--mid);stroke-width:.6}.atlasmap .st{fill:var(--paper2);stroke:var(--mid);stroke-width:.6}.atlasmap .o{fill:var(--ink);opacity:.55}.atlasmap .e{fill:var(--goldink);fill-opacity:.25;stroke:var(--goldink);stroke-width:1}.losschart{width:100%;height:auto;max-width:700px;display:block;margin:10px 0 0}.losschart .gl{stroke:var(--rule);stroke-width:.6}.losschart .ax{font:500 10px sans-serif;fill:var(--mid)}.losschart .d1{fill:var(--mid);opacity:.55}.losschart .d2{fill:var(--goldink)}
"""
CSS += '\n'.join(_MOVED) + """
.mtx.grid{width:auto;min-width:640px}.mtx.grid th,.mtx.grid td{text-align:center;vertical-align:middle}.mtx.grid th[scope=row]{text-align:left;font-family:Lora,Georgia,serif;letter-spacing:0;font-size:16px;color:var(--ink)}
.mtx.grid thead th a{color:var(--ink);text-decoration:none;font-size:15px}.mtx.grid .def{display:block;font-family:Lora,Georgia,serif;letter-spacing:0;text-transform:none;font-size:12px;font-weight:400;color:var(--mid);margin-top:4px}
.mtx.grid a.c{display:block;padding:10px 0;font-size:20px;font-weight:600;color:var(--ink);text-decoration:none;border:1px solid #c9b994;background:#fffaf0}.mtx.grid a.c:hover{background:var(--ink);color:#fffaf0}
.mtx.grid .z{display:block;padding:10px 0;font-size:20px;color:#bfb08c}.mtx.grid tr.tot th,.mtx.grid tr.tot td{border-top:2px solid var(--ink)}
.mtx th a{color:inherit}.mtx a.code{font-family:Cinzel,Georgia,serif;font-weight:600;font-size:13px;letter-spacing:.04em;text-decoration:none;border:1px solid #c9b994;padding:1px 5px;margin-right:4px;white-space:nowrap}.mtx .codes{display:inline-block;margin-bottom:4px}.hero.slim{padding:22px 0 20px}.hero.slim h1{font-size:clamp(32px,3.9vw,44px);max-width:none;margin:0}.hero.slim .sub{font-size:16px;margin-top:6px}.crumb{margin:32px 0 0;font-size:15px}.mtx.gates{max-width:760px}.mtx.dev td:nth-child(4),.mtx.dev td:nth-child(5){font-size:14px}
"""
# 25 Oct 2026 (his word): smaller type and tighter spacing sitewide; these rules come last so they win.
CSS += """
.stdbar{background:var(--lit);color:var(--cave);font-size:15px;line-height:1.35;padding:7px 0}.stdbar a{color:var(--cave);text-decoration:none;display:inline-block;margin-right:1.6em}.stdbar a:hover{text-decoration:underline}.stdbar b{font-weight:700;letter-spacing:.08em}.stdlist{list-style:none;padding:0;margin:6px 0 18px}.stdlist li{padding:3px 0}.stdlist b{display:inline-block;min-width:5.2em}.stdproc{margin:28px 0}.stdproc summary{cursor:pointer;font-weight:600}
.hero.slim{padding:16px 0 14px}.hero.slim h1{font-size:clamp(22px,2.4vw,28px)}.hero.slim .sub{font-size:14px;margin-top:4px}
.mtx{font-size:13.5px;line-height:1.4}.mtx th{font-size:10.5px;letter-spacing:.06em;padding:6px 8px}.mtx td{padding:6px 8px}
/* 29 Oct 2026 (his word): home headlines stacked like data, the number and one line, the rest opens on hover */
main .hlgrid{display:block;border-top:2px solid var(--ink);margin:4px 0 10px}
main .hlcard{display:grid;grid-template-columns:minmax(150px,360px) 1fr 84px;align-items:center;gap:0 16px;border-top:0;border-bottom:1px solid var(--rule);padding:2px 0}
main .hlcard .hl-big{font-size:clamp(36px,6vw,70px);line-height:1;color:var(--ink);white-space:nowrap}
main .hlcard:hover .hl-big{color:var(--ink)}
main .hlcard .hl-line{font-size:15px;line-height:1.35;margin:0;max-width:none;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
main .hlcard .hl-rest{display:none}
main .hlcard:hover .hl-line,main .hlcard:focus .hl-line{white-space:normal;overflow:visible}main .hlcard:hover .hl-rest,main .hlcard:focus .hl-rest{display:inline}
main .hlcard:hover{background:#fbf5e6}
main .hlcard .hl-more{margin:0;text-align:right;font-size:10.5px}
@media(max-width:700px){main .hlcard{grid-template-columns:1fr auto}main .hlcard .hl-line{grid-column:1/-1;order:3;white-space:normal}main .hlcard .hl-rest{display:inline}}
/* 29 Oct 2026 (his word): STACK picks two tests and shows how they stack */
main .hl.pick .pk-ctl{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;margin:8px 0 2px}
main .hl.pick select{font:400 14px Lora,Georgia,serif;color:var(--ink);background:#fffdf6;border:1px solid var(--ink);border-radius:2px;padding:5px 8px;max-width:100%;min-width:0;flex:1 1 280px}
main .hl.pick .pk-vs{font:600 11px Cinzel,Georgia,serif;letter-spacing:.14em;text-transform:uppercase;color:var(--mid)}
main .hl.pick .btn{margin:0;padding:6px 14px;cursor:pointer}
.foot .fs a{display:inline;padding:0;font-size:inherit}
/* 29 Oct 2026: reserved space for the script-filled blocks, so nothing jumps */
.hl-slot{min-height:0}.hl-slot.hl-home{min-height:616px}.hl-slot.hl-stack{min-height:344px}
main section.hl-slot:not(.hl):not(.hlgrid){border-bottom:0}
@media(max-width:700px){.hl-slot{min-height:0}.hl-slot.hl-home{min-height:891px}.hl-slot.hl-stack{min-height:340px}}
.bench-live{min-height:240px}#ibm-live{min-height:400px}.bench-live:not(:has(*)){min-height:0}
/* measured heights of each live block, 90 percent of them */
#airq-live{min-height:682px}#hosts-live{min-height:1836px}#trials-live{min-height:1789px}#hpt-live{min-height:1046px}#support-live{min-height:4871px}#fedsep-live{min-height:755px}#airline-live{min-height:1089px}#ailuminate-live{min-height:1764px}#hfsize-live{min-height:1042px}#hflicense-live{min-height:667px}#pkglicense-live{min-height:739px}#pkginstall-live{min-height:409px}#secrecords-live{min-height:3699px}#revise-live{min-height:308px}#change-live{min-height:561px}#cadence-live{min-height:939px}#linkrot-live{min-height:862px}#time-live{min-height:1725px}#uptime-live{min-height:911px}#forecast-live{min-height:508px}#cada-live{min-height:330px}#seat-live{min-height:1062px}#arxivdrift-live{min-height:397px}@media(max-width:700px){#airq-live{min-height:1637px}#hosts-live{min-height:3721px}#trials-live{min-height:3010px}#hpt-live{min-height:2434px}#support-live{min-height:9514px}#fedsep-live{min-height:2640px}#airline-live{min-height:2927px}#ailuminate-live{min-height:2602px}#hfsize-live{min-height:3066px}#hflicense-live{min-height:1242px}#pkglicense-live{min-height:2195px}#pkginstall-live{min-height:490px}#secrecords-live{min-height:6790px}#revise-live{min-height:809px}#change-live{min-height:1109px}#cadence-live{min-height:1801px}#linkrot-live{min-height:1965px}#time-live{min-height:2364px}#uptime-live{min-height:2035px}#forecast-live{min-height:1197px}#cada-live{min-height:683px}#seat-live{min-height:1230px}#arxivdrift-live{min-height:953px}}
.tape-top{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px 18px;margin:0 0 6px}.tape-card{border-top:2px solid var(--ink);padding-top:4px}.tape-card h3{margin:0 0 3px}
table.tape{width:100%}.tape .hashline{font-size:12.5px}.tape td{padding-top:3px;padding-bottom:3px}
.hl-tab{border-collapse:collapse;margin:8px 0 2px;font-variant-numeric:tabular-nums}.hl-tab th{font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:var(--mid);text-align:left;padding:0 22px 3px 0;border-bottom:1px solid var(--ink)}.hl-tab th.r{text-align:right}.hl-tab td{padding:3px 22px 1px 0;vertical-align:baseline}.hl-tab td.n{font:400 24px/1.05 "Abril Fatface",Georgia,serif;color:var(--lit);text-align:right}.hl-tab td.w{font-size:15px;text-align:right}.hl-tab tfoot td{border-top:1px solid var(--ink);padding-top:4px}.hl-tnote{font-size:12px;color:var(--mid);margin:3px 0 0}.hl-cta{font-size:16px;line-height:1.4;margin:8px 0 0}.hl-cta a:first-child{font:700 19px/1.3 inherit;color:var(--goldink)}@media(max-width:700px){.hl-tab th,.hl-tab td{padding-right:9px}.hl-tab th{font-size:10px;letter-spacing:.04em}.hl-tab td.n{font-size:20px}.hl-tab td.w{font-size:14px}}
.hl-receipt{font:400 12px/1.3 ui-monospace,Menlo,monospace;color:var(--mid);margin:4px 0 0}.hl-receipt a{color:var(--goldink)}
.mtx .by{font-size:12.5px}.mtx a.code{font-size:11px;padding:0 4px}
.crumb{margin:14px 0 0;font-size:13.5px}
.idx{margin:0 0 10px;gap:8px}.idx input[name=url]{font-size:15px;padding:7px 10px}.idx .btn{padding:7px 14px}
.addpdf{padding:14px 0 10px!important}.addpdf p{margin:0 0 6px;font-size:14px}
.disclose p{font-size:13.5px;color:var(--mid)}
.legal{max-width:100ch}.legal h2{font-size:17px;margin:14px 0 4px}.legal h3{font-size:15px;margin:10px 0 3px}.legal p,.legal li{font-size:14.5px;line-height:1.5;margin:0 0 7px}.legal ul,.legal ol{margin:0 0 7px;padding-left:20px}.legal .meta{margin:0 0 6px;font-size:13px}
main section.legal,main section.form-wrap{padding:14px 0}.legal-box{max-height:280px;font-size:14px;line-height:1.5;padding:4px 14px;margin:4px 0 8px}.legal-box p{margin:0 0 6px}.legal-box h3{font-size:14px;margin:8px 0 3px}
.form-wrap h2{font-size:17px;margin:12px 0 5px}.inq{gap:8px}.inq label{font-size:14px;gap:3px}.inq .check{margin:4px 0;font-size:14px}.ticks li{padding:5px 0 5px 22px;font-size:14.5px}
.hero{padding:16px 0 14px}.hero h1{font-size:clamp(22px,2.4vw,28px);max-width:none;margin:0}.hero .kicker{margin:0 0 4px;font-size:11px}.hero .sub{font-size:14px;margin-top:4px}.hero .actions{margin:12px 0 0}
.nowbox{font-size:14px}.nw-clock{opacity:.8;margin:4px 0 14px}.nw-sec h2{margin:22px 0 8px}.nw-row{display:grid;grid-template-columns:minmax(90px,140px) 1fr minmax(120px,30%);gap:4px 12px;align-items:center;padding:5px 0;border-bottom:1px solid rgba(127,127,127,.18)}.nw-row a{font-weight:700;letter-spacing:.04em}.nw-txt{overflow-wrap:anywhere}.nw-bar{display:block;height:8px;border-radius:4px;background:rgba(127,127,127,.22);overflow:hidden}.nw-fill{display:block;height:100%;width:0;background:var(--ink);transition:width .9s linear}.nw-wait .nw-fill{opacity:.45}.nw-run .nw-fill{background-image:linear-gradient(45deg,rgba(255,255,255,.28) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.28) 50%,rgba(255,255,255,.28) 75%,transparent 75%);background-size:16px 16px;animation:lspmove 1s linear infinite}.nw-ind .nw-fill{width:30%!important;animation:lspslide 1.4s ease-in-out infinite}.nw-note{opacity:.75;font-size:12.5px}@media (max-width:640px){.nw-row{grid-template-columns:1fr}}@media (prefers-reduced-motion:reduce){.nw-fill{animation:none}}p.oneliner{font-size:17px;margin:6px 0 4px}details.runbox{margin:4px 0 22px}details.runbox>summary{cursor:pointer;font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.75;padding:4px 0}details.runbox>summary:hover{opacity:1}details.runbox[open]>summary{margin-bottom:10px}.livetag.lt-eval:before,.livetag.lt-train:before{background:#2f7a3d;animation:none}#livestrip{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;margin:10px 0 20px;font-size:13px;line-height:1.4}#livestrip .lsp-dot{width:8px;height:8px;border-radius:50%;background:#c9302c;animation:livepulse 1.6s ease-in-out infinite;flex:0 0 auto}#livestrip.lsp-wait .lsp-dot{background:#8a8a8a;animation:livepulse 3s ease-in-out infinite}#livestrip .lsp-bar{flex:1 1 220px;min-width:160px;height:8px;border-radius:4px;background:rgba(127,127,127,.22);overflow:hidden}#livestrip .lsp-fill{display:block;height:100%;width:0;background:var(--ink);transition:width .9s linear}#livestrip.lsp-wait .lsp-fill{opacity:.45}#livestrip.lsp-reading .lsp-fill{background-image:linear-gradient(45deg,rgba(255,255,255,.28) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.28) 50%,rgba(255,255,255,.28) 75%,transparent 75%);background-size:16px 16px;animation:lspmove 1s linear infinite}#livestrip.lsp-indet .lsp-fill{width:30%;animation:lspslide 1.4s ease-in-out infinite,lspmove 1s linear infinite}@keyframes lspmove{from{background-position:0 0}to{background-position:16px 0}}@keyframes lspslide{0%{margin-left:-30%}100%{margin-left:100%}}@media (prefers-reduced-motion:reduce){#livestrip .lsp-dot,#livestrip .lsp-fill{animation:none}}.livetag.lt-read{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1px currentColor;letter-spacing:.06em}.livetag.lt-read:before{background:#8a8a8a;animation:none}.livetag.lt-train:before{animation:livepulse 1.6s ease-in-out infinite}.livetag{display:inline-block;margin-left:7px;padding:1px 7px 1px 6px;border-radius:9px;background:var(--ink);color:var(--paper);font:700 9px/1.5 Cinzel,Georgia,serif;letter-spacing:.12em;text-transform:uppercase;vertical-align:middle;text-decoration:none;border:0}.livetag:before{content:"";display:inline-block;width:6px;height:6px;margin-right:5px;border-radius:50%;background:#c9302c;animation:livepulse 1.6s ease-in-out infinite}@keyframes livepulse{0%,100%{opacity:1}50%{opacity:.25}}@media (prefers-reduced-motion:reduce){.livetag:before{animation:none}}.hdesks a .livetag,.links a .livetag,.ddpanel a .livetag{border-bottom:0}
.ac{font-weight:400;-webkit-text-stroke:.045em currentColor;paint-order:stroke fill}.hero .ac{color:var(--lit)}.hl{margin:0;padding:6px 0 10px;border-bottom:3px solid var(--ink)}.hl-big{font:400 clamp(36px,6vw,70px)/.95 "Abril Fatface",Georgia,serif;color:var(--lit);letter-spacing:-.01em}.hl+section,.hl+.wrap,.hl+section.legal{padding-top:6px}.hl+section>h1:first-child,.hl+section>h2:first-child,.hl+.wrap>h2:first-child{margin-top:0}.hl-line{margin:6px 0 0;max-width:34em;font:400 clamp(18px,2.1vw,23px)/1.4 Lora,Georgia,serif;color:var(--deep)}.hlgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:26px 30px;margin:6px 0 36px}.hlcard{display:block;text-decoration:none;color:var(--ink);border-top:4px solid var(--ink);padding-top:12px}.hlcard:hover .hl-big{color:var(--ink)}.hlcard .hl-big{font-size:clamp(31px,4vw,48px)}.hlcard .hl-line{font-size:17px;line-height:1.4;max-width:none;margin-top:8px}.hl-more{display:block;margin-top:9px;font:600 11px/1 Cinzel,Georgia,serif;letter-spacing:.14em;color:var(--mid)}
.tabbar{display:none}@media (display-mode:standalone) and (max-width:860px){.top .links{display:none}.tabbar{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:9;background:var(--paper);border-top:2px solid var(--rule);padding:0 0 env(safe-area-inset-bottom)}.tabbar a{flex:1;text-align:center;padding:13px 2px 12px;font:600 11px/1 Cinzel,Georgia,serif;letter-spacing:.1em;color:var(--mid);text-decoration:none;border-top:3px solid transparent;margin-top:-2px}.tabbar a[aria-current]{color:var(--ink);border-top-color:var(--ink)}body{padding-bottom:calc(58px + env(safe-area-inset-bottom))}.bar{height:58px;padding-top:0;padding-bottom:0}}
.hdivs{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:22px;margin:6px 0 26px}.hdiv{border-top:3px solid var(--ink);padding:12px 2px 6px}.hdiv h2{margin:0 0 4px;font:400 clamp(26px,3vw,34px)/1.1 "Abril Fatface",Georgia,serif}.hdiv h2 a{color:var(--ink);text-decoration:none;border-bottom:2px solid var(--rule)}.hdiv h2 a:hover{color:var(--goldink)}.hdiv .hsub{margin:0 0 8px;font:600 12px/1.4 Cinzel,Georgia,serif;letter-spacing:.07em;color:var(--mid);text-transform:uppercase}.hdiv .hwhat{margin:0 0 10px;font:400 16px/1.45 Lora,Georgia,serif}.hdesks{display:flex;flex-wrap:wrap;gap:6px 14px;margin:0}.hdesks a{font:600 13px/1.3 Cinzel,Georgia,serif;letter-spacing:.06em;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}.hdesks a:hover{color:var(--goldink)}.hmore{display:flex;flex-wrap:wrap;gap:10px 26px;border-top:1px solid var(--rule);padding-top:14px;margin-bottom:10px}.hmore a{font:400 18px/1.3 "Abril Fatface",Georgia,serif;color:var(--ink);text-decoration:none;border-bottom:2px solid var(--rule)}.hmore a:hover{color:var(--goldink)}
.home3 p{margin:0 0 14px;font:400 clamp(19px,2vw,24px)/1.3 "Abril Fatface",Georgia,serif}.home3 a{color:var(--ink);text-decoration:none;border-bottom:2px solid var(--rule)}.home3 a:hover{color:var(--goldink)}
.addpdf+section{padding-top:14px}
.btn.ghost{background:transparent;color:var(--ink);border:1px solid var(--ink);margin-left:0}.btn.ghost:hover{background:var(--ink);color:var(--paper)}.notice{margin:0 0 12px;padding:8px 12px;background:#fffaf0;border:1px solid #c9b994;border-left:3px solid var(--rule);font-size:14.5px;font-weight:600;color:var(--ink)}
.foot{padding:16px 0 14px;border-top-width:2px}.foot .fl{display:flex;flex-wrap:wrap;gap:4px 22px;margin:0 0 4px}.foot .fl a{display:inline;padding:0;font-size:13px}.foot .fl{justify-content:center}.foot .fs{margin:6px 0 0;font-size:13px;color:#d8ccb0;text-align:center}.foot .fs+.fs{margin-top:0;font-size:12px;color:#b9ad90}
main section{padding:24px 0}main section:first-child{padding-top:16px}
.data{font-size:13.5px;margin:0 0 10px;color:var(--mid)}
h2{margin:0 0 .35em}
/* 29 Oct 2026 (his word): dense, data-site spacing everywhere */
body{line-height:1.45}.bar{height:auto;min-height:48px;flex-wrap:wrap;padding-top:3px;padding-bottom:3px;gap:2px 24px}.links{flex-wrap:wrap;gap:4px 22px}main p{margin-top:0;margin-bottom:5px}main h2{margin:0 0 3px}main h3{margin:6px 0 2px}
main section{padding:7px 0}main section:first-child{padding-top:6px}.hl{padding:0 0 6px}.hl-line{margin:3px 0 0}.hl+.meta{margin:6px 0 0}.meta+section{padding-top:6px}.hl+section{padding-top:6px}
.hl+section,.hl+.wrap,.hl+section.legal{padding-top:6px}.meta{margin:0 0 4px}p.meta{margin-top:0}
.addpdf{padding:6px 0 4px!important}.addpdf+section{padding-top:8px}.disclose,main section.disclose{padding:8px 0}
.desklist li{padding:5px 0}.hero.slim{padding:10px 0 8px}.foot{padding:8px 0 6px}.foot .fs{margin:3px 0 0}.foot .fl{margin:0 0 2px}
.hdivs{gap:14px;margin:4px 0 14px}.hdiv{padding:8px 2px 2px}.hlgrid{gap:16px 24px;margin:4px 0 16px}
.mtx td,.mtx th{padding-top:4px;padding-bottom:4px}
.mtx .by{font-family:Lora,Georgia,serif;letter-spacing:0;text-transform:none;font-variant:normal;margin-top:0}
"""

# 28 Oct 2026 (his word): the response door. One PDF link per unit (a school, a study, a vendor post), shown with the host it came from. Anything else goes through the inquiry form.
# 30 Oct 2026 (his word: "go for correction or removal option"): an open door for corrections and removals. No agreement, no sign-in, no work
# email. Nothing sent here is posted. indahl-ai/correctreq.js stores it (24 months, as the privacy notice states) and emails us a copy.
PAGES['/correction'] = page('/correction', 'Correction or Removal | Heuremen LLC', 'Ask for a correction or a removal on indahl.ai or heuremen.org. Open to anyone, no agreement and no work email needed.',
 '<section class="legal"><h2>Ask for a correction or a removal</h2>'
 '<p>Anyone can use this form: a person or organisation named on one of our pages, an author, or anyone who finds an error. It needs no agreement, no sign-in and no work email. Nothing you send here is posted.</p>'
 '<p>We read every request in full and answer by email. A correction is made at the source and the page says what changed. For a removal of a name or a page, we may write back to confirm that the request comes from the person or organisation named.</p>'
 '<form class="inq" method="post" action="/correction-request"><div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>'
 '<div class="row"><label>What would you like us to do<select name="kind" required><option value="correct">Correct a number, a quote or a claim</option><option value="name">Remove my name</option><option value="page">Remove a page or a study row</option><option value="privacy">Another privacy request</option></select></label></div>'
 '<div class="row"><label>Your name<input name="name" required maxlength="120" autocomplete="name"></label> <label>Email we can answer<input name="email" type="email" required maxlength="160" autocomplete="email"></label></div>'
 '<div class="row"><label>The page (a link on indahl.ai or heuremen.org)<input name="link" type="url" maxlength="500" placeholder="https://indahl.ai/&hellip;"></label></div>'
 '<div class="row"><label>Your request<textarea name="details" required maxlength="3000" rows="6"></textarea></label></div>'
 '<button class="btn" type="submit">Send</button></form>'
 '<p class="meta">What this form keeps and for how long is in the <a href="/privacy">privacy notice</a>. To add a public response to a page instead, use the Respond link at the foot of that page.</p></section>',
 hero_slim('Correction or Removal'))
# 10 Nov 2026: the public corrections log at /corrections, with corrections.xml (Atom) and corrections.csv in the worker's public folder.
# Generator and rows live in corrections.py and corrections_rows.json. The build stops if a row's source, commit, link or receipt is not real.
import corrections as _corr; _corr.build(PAGES, page, hero_slim, _FEED); CSS += _corr.CSS
# 10 Nov 2026: the newsletter on the web, /newsletter and /newsletter/<N>, one Markdown file per issue in ~/bones-forge/newsletter (newsletter_pages.py)
import newsletter_pages as _nlp; _nlp.build(PAGES, page, hero_slim); CSS += _nlp.CSS
# 10 Nov 2026: FORECASTERS at /forecasters, every forecaster desk on one axis, built in forecasters.py (members in ../forecasters/members.json, its own trace gate).
import forecasters as _fcs; CSS += _fcs.CSS

PAGES['/respond'] = page('/respond', 'Respond | Heuremen LLC', 'Add a response to a page: a PDF on your own site, posted as received with its date and host.',
 '<section class="legal"><h2>Add a response</h2>'
 '<p>A company, school or author named on a page may add a response to it. Paste a direct link to a PDF on your own site. It is posted as received, never edited, with its date and the host it came from. When it disputes a figure, we recount that figure from the same files and add one line with the result.</p>'
 '<form class="idx" method="post" action="/respond-request"><div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>'
 '<label>Reference <input name="unit" type="text" required maxlength="80" value="__UNIT__" placeholder="from the Respond link"></label>'
 '<input name="url" type="url" required maxlength="2000" placeholder="https://&hellip;.pdf" aria-label="Link to a PDF"><button class="btn" type="submit">Send</button></form>'
 '<p class="meta">Stored: the reference, the link, its host and the time. Nothing else. <a href="/privacy">Privacy</a> &middot; <a href="/terms#responses">Terms</a></p>'
 '<h2>Anything else</h2><p>For anything that does not fit a PDF, use the <a href="/contact">inquiry form</a> and quote the reference above.</p></section>',
 hero_slim('Respond'))

# Posted responses live in indahl-ai/responses.json: {unit: [{"date": "14 Nov 2026", "host": "ibm.com", "url": "https://...pdf", "line": "Recount 20 Nov: unchanged."}]}. Empty until one is read and posted. Verbatim, dated, host shown, one line of ours.
_RESP = _oj.load(open(os.path.join(HERE, 'responses.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'responses.json')) else {}
def _resp_html(unit):
    return ' '.join(f'Response {_e(r["date"])}: <a href="{_e(r["url"])}">PDF from {_e(r["host"])}</a>.' + (f' {_e(r["line"])}' if r.get('line') else '') for r in _RESP.get(unit, []))
# division pages: the Respond link sits next to the Add a PDF box (QIA, IRIS, OY), in the SAD header line, and under the IBM and Braket headings
def _rl(u, lead='Named here and want to answer a row?'): return f'<p class="meta">{lead} <a href="/respond?u={u}">Respond</a></p>'
for _dp, _du in (('/qia', 'qia-all'), ('/iris', 'iris-all'), ('/oy', 'oy-all')):
    assert '</form></section>' in PAGES[_dp]; PAGES[_dp] = PAGES[_dp].replace('</form></section>', '</form>' + _rl(_du) + '</section>', 1)
_lh = '<h2>What vendors state and what the results files show</h2>'; assert _lh in PAGES['/hermes/model']
PAGES['/hermes/model'] = PAGES['/hermes/model'].replace(_lh, '<h2>Model claims against the models (rounds ended 30 Oct)</h2><p>Open-weight models state results in their own cards. Each round reruns one model\'s stated results with EleutherAI lm-evaluation-harness 0.4.13 through mlx-lm 0.32.2 on Apple silicon, on the original bf16 weights, with the shots the card gives. Where the card does not say whether the prompt uses the chat template or the few-shot examples as turns, we run the variants and read the stated value against every one. The &plusmn; after a value is 1.96 harness standard errors plus the rounding of the card\'s printed figure, a 95% interval. A variant is marked CANNOT_TELL (parser) when more than 1 of 10 replies read in full disagree with what the harness extracted, and it no longer counts toward the outcome. The rules and the claim list are committed before the first run. A card row that the round did not run is listed as not run, with the reason. The plans, full reads, claim lists, scorers and raw outputs of every round are in the <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/iris/claims_stack">claims_stack folder</a> on GitHub.</p><div id="model-live" class="bench-live">Loading.</div><script src="/hermes/model/live.js" defer></script>' + _lh, 1)
_k = '&middot; Stated Against Delivered</p>'; assert _k in PAGES['/hermes/model']
PAGES['/hermes/model'] = PAGES['/hermes/model'].replace(_k, '&middot; Stated Against Delivered &middot; <a href="/respond?u=model-all">Respond</a></p>', 1)
for _h, _u in (('Hardware Deviations from IBM&rsquo;s Published Calibration</h2>', 'qia-ibm'), ('Hardware Deviations from Amazon Braket&rsquo;s Published Calibration</h2>', 'qia-braket')):
    assert _h in PAGES['/qia'], _h; PAGES['/qia'] = PAGES['/qia'].replace(_h, _h + _rl(_u, 'Answer this table:'), 1)

# QIA: IBM's published calibration, mirrored live (28 Oct, his word: a system, not a check when we feel like it)
_dv = '<h3>Deviations</h3>'; assert _dv in PAGES['/qia']
PAGES['/qia'] = PAGES['/qia'].replace(_dv, '<h3>IBM&rsquo;s published calibration, mirrored</h3><div id="ibm-live" class="bench-live">Loading.</div><script src="/qia/ibm.js" defer></script>' + _dv, 1)

# QIA is long: ids on its four tables and a jump line at the top (28 Oct rotation)
for _a, _i in (('<h2>Hardware Deviations from IBM', 'ibm'), ('<h2>Hardware Deviations from Amazon Braket', 'braket'), ('<h2>Calibrated Studies: Corporate', 'corporate'), ('<h2>Calibrated Studies: Research', 'research'), ('<h2>Inventory of Published Studies', 'inventory')):
    assert _a in PAGES['/qia'], _a; PAGES['/qia'] = PAGES['/qia'].replace(_a, _a.replace('<h2>', f'<h2 id="{_i}">'), 1)
for _m, _u in (('<h2 id="braket">', 'qia-ibm'), ('<h2 id="corporate">', 'qia-braket')):
    assert _m in PAGES['/qia'], _m
    PAGES['/qia'] = PAGES['/qia'].replace(_m, '<p class="meta">Named here and want to answer a row? <a href="/respond?u=' + _u + '">Respond</a></p>' + _m, 1)
_aq = '<section class="addpdf">'; assert _aq in PAGES['/qia']
PAGES['/qia'] = PAGES['/qia'].replace(_aq, ('<section id="audit"><h2>IBM&rsquo;s published calibration, checked against itself</h2>'
  '<p>We read the calibration IBM publishes for each processor and check every record against itself. No QPU time is used. The rules were committed before the fresh read and the counts were recomputed by a second script that shares no code with the first. Boston qubit 85 and fez qubit 148 were noticed in a first look before the rules were written, and the two and a half threshold was set after that look. Every other row was read under the committed rules.</p>'
  '<p>A single qubit cannot have T2 above twice its T1. IBM publishes one T1 and one T2 for each qubit with no fit uncertainty, so the ratio of the two has no interval and every one of these readings is CANNOT_TELL (NO_INTERVAL_FORMABLE). We count the qubits whose published ratio is above two and a half and the qubits between two and two and a half, as counts of published ratios and not as outcomes. We also compare the date IBM gives for each qubit&rsquo;s T1 with the date it gives for its T2, the age of every entry in the record, and whether a restamped record changed any qubit entry at all. We name no cause.</p>'
  '<p>To measure T1 and T2 together on a flagged qubit yourself, with your own IBM account, use <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/t1t2-check">the check in our public repository</a>. It prints its cost first and submits nothing until you say so.</p>'
  '<div id="audit-live" class="bench-live">Loading.</div><script src="/qia/audit.js" defer></script><h3>Stability over time</h3><p>Every saved record of each processor, compared with the others: how often T1 and T2 are measured again, how far apart their dates are, and which qubits are ever flagged. The plan was committed before the first table.</p><div id="stability-live" class="bench-live">Loading.</div><script src="/qia/stability.js" defer></script><h3>Queue at each processor</h3><p>How many jobs IBM reports waiting at each processor, read about every 12 minutes, beside how long our own jobs waited there. The plan was committed before the first read, and <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/qia-queue">the reader and every row it has saved</a> are public. It runs on the IBM Quantum Platform through <a href="https://pypi.org/project/qiskit-ibm-runtime/">qiskit-ibm-runtime</a>.</p><div id="queue-live" class="bench-live">Loading.</div><script src="/qia/queue.js" defer></script><h3>T1 and T2 measured together</h3><p>For the qubits the audit flags, we measured T1 and T2 on the same qubit in one job on the processor, with a control qubit in the same job, and read the ratio against the physical limit of 2. The plan was committed before the results were read. Notes 3, 4 and 6 were written after some results were read. Run it yourself: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/t1t2-check">the check in our public repository</a>.</p><div id="t1t2-live" class="bench-live">Loading.</div><script src="/qia/t1t2.js" defer></script><p class="meta">Named here and want to answer a row? <a href="/respond?u=qia-audit">Respond</a></p></section><section id="cal"><h2>IBM&rsquo;s calibration, measured when it changes</h2><p>We run one job on each IBM processor we can reach whenever IBM publishes new readout or T1 figures for it, and at least every 6 hours, and read every qubit: readout at rest, readout after an X, and T1. The first runs on 30 October went every hour. In about 40 hours of IBM records, IBM changed those figures between 0 and 9 times per processor, so most hourly runs read a record that had not changed, and the rule moved to plan Note 4 the same day. Each reading is set against the calibration IBM had in force when our job ran, with both figures and their dates. If your job ran near one of ours, this is what your qubits were doing. One job per processor is kept in flight, so a processor with a job waiting in IBM&rsquo;s queue shows its older reading beside the time the newer job was sent. The two interval rules were set after the first aachen run was read and before any US run was read. A third rule, the shot count behind IBM&rsquo;s readout figures, was set on 30 October after fez and marrakesh readings were published. The count is read from the record each run used: 1,024 when every readout figure in it is a multiple of 1/1024, otherwise 4,096. Every earlier fez and marrakesh run was re-read under it, and each correction was added to the chain. The first four marrakesh runs (30 October, 02:12 to 05:22 UTC) were re-read at 4,096, because their records were not all on the 1/1024 grid. The other 20 were re-read at 1,024. Across the 24 runs the readout calls went from 1,043 to 754. 289 of them (28 %) withdrew to consistent. None changed direction, no T1 call changed and all 24 runs still pass the known-good check. The code and the plan are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/qia-cal">qia-cal</a>.</p><div id="cal-live" class="bench-live">Loading.</div><script src="/qia/cal.js" defer></script></section><section id="offchain"><h2>When IBM&rsquo;s calibration was off: the chain</h2><p>Every time one of our own jobs measured a qubit against the calibration IBM published for it and found IBM&rsquo;s figure outside what the qubit delivered, the reading goes here as one entry: processor, qubits, IBM&rsquo;s figure and the date IBM gives for it, what we measured with its interval, the time our job ran, and the job id. Check your own job: pick the processor, type your qubits and the time your job ran. Entries are hashed and chained, append only, so the record cannot change without showing it. Every calibration run above adds one entry too. Everything is free: <a href="/qia/offchain.json">the whole chain</a> and <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/qia-offchain">the script that verifies it</a>.</p><div id="offchain-live" class="bench-live">Loading.</div><script src="/qia/offchain.js" defer></script></section>'
  '<p class="meta">On this page: <a href="#audit">Audit</a> &middot; <a href="#cal">Calibration</a> &middot; <a href="#offchain">Off-record chain</a> &middot; <a href="#ibm">IBM</a> &middot; <a href="#braket">Amazon Braket</a> &middot; <a href="#corporate">Corporate studies</a> &middot; <a href="#research">Research, institution, individual</a> &middot; <a href="#inventory">Inventory</a></p>') + _aq, 1)

# 29 Oct 2026 (his word): QIA order is headline, jump line, the IBM and Braket deviation tables, then the audit data, the studies, and last the PDF box, notices and links.
def _qia_reorder(b):
    def cut(b, start_pat, end_pat='</section>'):
        i = b.index(start_pat); j = b.index(end_pat, i) + len(end_pat); return b[:i] + b[j:], b[i:j]
    # each Respond line ends the section it answers instead of opening the next one
    for _u, _h in (('qia-ibm', '<h2 id="braket">'), ('qia-braket', '<h2 id="corporate">')):
        _rp = '<p class="meta">Named here and want to answer a row? <a href="/respond?u=' + _u + '">Respond</a></p>'
        assert _rp + _h in b; b = b.replace(_rp + _h, _h, 1)
        _k = b.index(_h); _e = b.rindex('</section>', 0, _k); b = b[:_e] + _rp + b[_e:]
    b, audit = cut(b, '<section id="audit">')
    b, addpdf = cut(b, '<section class="addpdf">')
    _ji = b.index('<p class="meta">On this page:'); _je = b.index('</p>', _ji) + 4
    b = b[:_ji] + b[_je:]
    jump = ('<p class="meta">On this page: <a href="#ibm">IBM</a> &middot; <a href="#braket">Amazon Braket</a> &middot; <a href="#audit">Audit</a> &middot; '
            '<a href="#corporate">Corporate studies</a> &middot; <a href="#research">Research, institution, individual</a> &middot; <a href="#inventory">Inventory</a></p>')
    _m = '<main class="wrap">'; _mi = b.index(_m) + len(_m)
    _sm = b.find('</section>', _mi)
    if b.startswith(_SLOT[:20], _mi) and _sm > 0: _mi = _sm + len('</section>')
    b = b[:_mi] + jump + b[_mi:]
    _k = b.index('<h2 id="corporate">'); _s = b.rindex('<section', 0, _k); b = b[:_s] + audit + b[_s:]
    _d = b.index('<section class="disclose">'); b = b[:_d] + addpdf + b[_d:]
    return b
PAGES['/qia'] = _qia_reorder(PAGES['/qia'])

# the Respond link on every school page, QIA study page and IRIS study page, from the same sentence they already end with
_CORR = 'use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>'
for _rp in list(PAGES):
    _m = _re.match(r'^/(oy/school|qia/study|iris/study)/([A-Za-z0-9._-]+)$', _rp)
    if _m and _CORR in PAGES[_rp]:
        _unit = {'oy/school': 'oy', 'qia/study': 'qia', 'iris/study': 'iris'}[_m.group(1)] + '-' + _re.sub(r'[^a-z0-9._-]+', '-', _m.group(2).lower()).strip('-')
        PAGES[_rp] = PAGES[_rp].replace(_CORR, f'use the <a href="/correction">correction or removal form</a>, open to anyone. ' + (_resp_html(_unit) + ' ' if _RESP.get(_unit) else '') + f'To add a response, <a href="/respond?u={_unit}">respond here</a>.</p></section>', 1)



# 28 Oct 2026 (his word): an "On this page" jump line on every long page, built from its own headings. Hand-set short labels where a heading is long.
_JUMPS = {
 '/iris': ('h2', {'Running Now in the IRIS Lab': 'Running now', 'Live From Our Lab: A Falcon Trained on the Standards': 'Falcon training', 'Live From Our Lab: The Two Finalists, Head to Head': 'Finalists',
                  'Live From Our Lab: How Different Models Handle Standards': 'Models', 'Models as judges in our own pipeline': 'Judges', 'Our own fine-tuning runs': 'Our fine-tuning', 'Inventory of Published Studies': 'Inventory', 'Marking your own work': 'Mark your own work'}, 'Findings'),
 '/iris/lab': ('h2', {'STAN: Training Live': 'STAN', 'A Small Model Trained on the House&rsquo;s Own Answers': 'House training', 'A Falcon Trained on the Standards': 'Falcon training', 'The Two Finalists, Head to Head': 'Finalists', 'How Different Models Handle Standards': 'Models'}, 'Runs'),
 '/oy': ('h2', {'Table of findings': 'Table of findings', 'The list': 'The list', 'Private baccalaureate colleges': 'Private baccalaureate colleges'}, 'Findings'),
 '/atlas': ('h2', {'Cost to scale': 'Cost to scale', 'How the cost is worked': 'How it is worked', 'Annual cost by site': 'By site', 'Sites with a stated power that are not in the total': 'Not in the total', 'State prices used': 'State prices', 'Data centers in the United States': 'Data centers', 'Sources': 'Sources', 'AI data centers from Epoch AI': 'AI data centers'}, None),
 '/hermes/model': ('h2', {'Model claims against the models (rounds ended 30 Oct)': 'Model claims', 'What vendors state and what the results files show': 'Vendor statements', 'Sources': 'Sources', 'Results by accelerator': 'Accelerators', 'Sources and rerun': 'Rerun', 'Notices': 'Notices', 'Independence': 'Independence'}, None),
 '/atlas/electricity': ('h2', {'*': 1, 'What electricity costs by state, and where it comes from': 'Overview', 'Where United States electricity comes from': 'Where it comes from', 'Largest utilities by commercial and industrial sales': 'Largest utilities'}, None),
 '/atlas/carbon': ('h2', {'*': 1, 'Carbon dioxide per megawatthour of electricity, by state': 'Overview', 'Stated against delivered: Google Cloud regions': 'Google Cloud regions'}, None),
 '/atlas/planned-plants': ('h2', {'*': 1, 'Power plants that owners have reported as planned': 'Overview', 'The twenty largest planned plants': 'Largest planned plants'}, None),
 '/atlas/power-plants': ('h2', {'*': 1, 'Operating power plants in the United States': 'Overview', 'The twenty largest plants': 'Largest plants'}, None),
 '/api': ('h3', {}, None),
}
_JPRE = {'/iris': [('Reverse the order', 'Findings')], '/oy': [('Chatbot cited', 'Findings')]}
def _jump(path, level, labels, first):
    b = PAGES.get(path)
    if not b or 'On this page' in b: return
    mi = b.find('<main class="wrap">')
    if mi < 0: return
    _cut = mi + len('<main class="wrap">')
    if b.startswith('<section id="hl-slot"', _cut): _cut = b.index('</section>', _cut) + len('</section>')
    head, seg = b[:_cut], b[_cut:]
    out, last, used, links = [], 0, set(), []
    for m in _re.finditer(r'<%s(\s[^>]*)?>(.*?)</%s>' % (level, level), seg, flags=_re.S):
        txt = html.unescape(_re.sub(r'<[^>]+>', '', m.group(2))).strip()
        lab = labels.get(txt) if labels else txt
        if lab is None and labels.get('*'): lab = txt
        for pre, pl in _JPRE.get(path, []):
            if lab is None and txt.startswith(pre) and not any(l == pl for _, l in links): lab = pl
        if lab is None: continue
        attrs = m.group(1) or ''; mid = _re.search(r'id="([^"]+)"', attrs)
        if mid: hid = mid.group(1)
        else:
            hid = _re.sub(r'[^a-z0-9]+', '-', lab.lower()).strip('-') or 'sec'
            while hid in used: hid += '-2'
            out.append(seg[last:m.start()]); out.append('<%s%s id="%s">%s</%s>' % (level, attrs, hid, m.group(2), level)); last = m.end()
        used.add(hid); links.append((hid, lab))
    out.append(seg[last:]); seg = ''.join(out)
    if len(links) < 3: return
    line = '<p class="meta">On this page: ' + ' &middot; '.join('<a href="#%s">%s</a>' % (i, html.escape(l)) for i, l in links) + '</p>'
    PAGES[path] = head + line + seg
for _jp, (_lv, _lb, _f) in _JUMPS.items(): _jump(_jp, _lv, _lb, _f)

# 28 Oct 2026: COIN page layout (the worker allows no inline styles)
CSS += """
.coin-top{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:8px 32px;align-items:start;margin:4px 0 10px}
.coin-three{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 28px;margin:4px 0 10px}
@media(max-width:700px){.coin-top,.coin-three{grid-template-columns:1fr}}
.hashline{font:500 14px/1.3 ui-monospace,Menlo,monospace;color:var(--ink);word-break:break-all;margin:2px 0}
.hashline s{text-decoration:none;color:#8a7860}
.coin-svg{width:100%;height:auto;display:block;max-width:420px}
.coin-svg .tr{fill:var(--paper2);stroke:var(--rule);stroke-width:.6}.coin-svg .fl{fill:var(--goldink)}
.coin-top h3,.coin-three h3{margin:0 0 4px}.coin-three .mtx td{font-size:13.5px;padding:4px 8px}
.o-CONSISTENT,.o-ABOVE,.o-BELOW,.o-CANNOT_TELL,.o-NOTHING_RETURNED{font-family:Cinzel,Georgia,serif;font-weight:600;font-size:12px;letter-spacing:.06em}
.o-CONSISTENT{color:#2a6a4a}.o-ABOVE,.o-BELOW{color:#9a2b1e}.o-CANNOT_TELL,.o-NOTHING_RETURNED{color:var(--mid)}
"""



# 29 Oct 2026 (his word: live link the public builds on every site): one line per corner pointing at its plan, code and trend history on GitHub.

# 29 Oct 2026 (his word: git and PyPI links wherever the site references code or comparison software). Every link was checked to resolve.
_SW = {'pip': ('pip', 'https://github.com/pypa/pip', 'https://pypi.org/project/pip/'), 'qiskit': ('Qiskit', 'https://github.com/Qiskit/qiskit', 'https://pypi.org/project/qiskit/'), 'qiskit-aer': ('Qiskit Aer', 'https://github.com/Qiskit/qiskit-aer', 'https://pypi.org/project/qiskit-aer/'),
       'qiskit-ibm-runtime': ('Qiskit IBM Runtime', 'https://github.com/Qiskit/qiskit-ibm-runtime', 'https://pypi.org/project/qiskit-ibm-runtime/'), 'numpy': ('NumPy', 'https://github.com/numpy/numpy', 'https://pypi.org/project/numpy/'),
       'scipy': ('SciPy', 'https://github.com/scipy/scipy', 'https://pypi.org/project/scipy/'), 'mlx': ('MLX', 'https://github.com/ml-explore/mlx', 'https://pypi.org/project/mlx/'), 'mlx-lm': ('MLX LM', 'https://github.com/ml-explore/mlx-lm', 'https://pypi.org/project/mlx-lm/'),
       'ollama': ('Ollama', 'https://github.com/ollama/ollama', 'https://pypi.org/project/ollama/'), 'lm-eval': ('lm-evaluation-harness', 'https://github.com/EleutherAI/lm-evaluation-harness', 'https://pypi.org/project/lm-eval/'),
       'mlperf': ('MLPerf Inference', 'https://github.com/mlcommons/inference', 'https://pypi.org/project/mlcommons-loadgen/'), 'hf-hub': ('huggingface_hub', 'https://github.com/huggingface/huggingface_hub', 'https://pypi.org/project/huggingface-hub/'),
       'faultsguards': ('faultsguards (ours)', 'https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/faultsguards', 'https://pypi.org/project/faultsguards/'), 'ravencoin': ('Ravencoin core', 'https://github.com/RavenProject/Ravencoin', None),
       'pypdf': ('pypdf', 'https://github.com/py-pdf/pypdf', 'https://pypi.org/project/pypdf/'), 'tectonic': ('Tectonic', 'https://github.com/tectonic-typesetting/tectonic', None),
       'lighteval': ('lighteval', 'https://github.com/huggingface/lighteval', 'https://pypi.org/project/lighteval/'),
       'ots': ('OpenTimestamps client', 'https://github.com/opentimestamps/opentimestamps-client', 'https://pypi.org/project/opentimestamps-client/'), 'drand': ('drand', 'https://github.com/drand/drand', None)}   # 9 Nov 2026 (site pass L4)   # 9 Nov 2026 (site pass M13)
_SWMAP = {'pkginstall': ['pip'], 'hfsize': ['hf-hub'], 'change': [], 'qia': ['qiskit', 'qiskit-ibm-runtime', 'qiskit-aer', 'numpy', 'scipy', 'pypdf'], 'iris': ['mlx-lm', 'mlx', 'ollama', 'hf-hub', 'faultsguards'], 'model': ['mlperf', 'lm-eval', 'mlx-lm', 'lighteval'], 'tape': ['ots', 'drand'], 'coin': ['ravencoin']}
_GH = 'https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/'
_CODE = {'predictions': [('now', 'now')], 'time': [('time', 'time')], 'coin': [('coin', 'coin')], 'cada': [('cada', 'cada')], 'uptime': [('uptime', 'uptime')], 'forecast': [('forecast', 'forecast')], 'cadence': [('cadence', 'cadence')],
         'trials': [('trials', 'trials')], 'launch': [('launch', 'launch')], 'linkrot': [('linkrot', 'linkrot')], 'tape': [('tape', 'tape')], 'hosts': [('hosts', 'hosts')], 'campus': [('campus', 'campus')], 'airq': [('airq', 'airq')], 'ailuminate': [('ailuminate', 'ailuminate')], 'hpt': [('hpt', 'hpt')], 'weights': [('weights', 'weights')], 'airline': [('airline', 'airline')], 'fedsep': [('fedsep', 'fedsep')], 'revise': [('revise', 'revise')], 'stack': [('stack', 'stack')], 'pkginstall': [('pkginstall', 'pkginstall')], 'seat': [('seat', 'seat')], 'secrecords': [('secrecords', 'secrecords')], 'change': [('change', 'change')], 'hfsize': [('hfsize', 'hfsize')], 'hflicense': [('hflicense', 'hflicense')], 'pkglicense': [('pkglicense', 'pkglicense')], 'support': [('support', 'support')], 'arxivdrift': [('arxivdrift', 'arxivdrift')], 'iris': [('iris', 'iris')], 'model': [('model', 'model')], 'atlas': [('atlas', 'atlas')],
         'qia': [('mirror', 'audit, mirror and stability index'), ('t1t2-check', 'T1 and T2 check')]}
_SRC = {'predictions': [('Long Bets', 'https://longbets.org'), ('Manifold API', 'https://docs.manifold.markets/api'), ('Internet Archive Wayback Machine', 'https://web.archive.org'), ('OpenTimestamps', 'https://opentimestamps.org')], 'support': [('endoflife.date', 'https://endoflife.date')], 'pkglicense': [('PyPI', 'https://pypi.org'), ('Top PyPI Packages', 'https://hugovk.github.io/top-pypi-packages/')], 'pkginstall': [('PyPI', 'https://pypi.org'), ('Top PyPI Packages', 'https://hugovk.github.io/top-pypi-packages/')], 'hflicense': [('Hugging Face', 'https://huggingface.co')], 'hfsize': [('Hugging Face', 'https://huggingface.co')], 'weights': [('Hugging Face', 'https://huggingface.co')], 'secrecords': [('Tranco list', 'https://tranco-list.eu'), ('HSTS preload list', 'https://hstspreload.org'), ('Cloudflare DNS over HTTPS', 'https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/')], 'linkrot': [('arXiv', 'https://arxiv.org')], 'trials': [('ClinicalTrials.gov', 'https://clinicaltrials.gov')], 'revise': [('Bureau of Labor Statistics', 'https://www.bls.gov'), ('BLS revisions between over-the-month estimates', 'https://www.bls.gov/web/empsit/cesnaicsrev.htm'), ('BLS total nonfarm employment series', 'https://download.bls.gov/pub/time.series/ce/ce.data.00a.TotalNonfarm.Employment')], 'hpt': [('CMS hospital price transparency', 'https://www.cms.gov/priorities/key-initiatives/hospital-price-transparency'), ('Wikidata', 'https://www.wikidata.org')], 'hosts': [('OpenRouter', 'https://openrouter.ai')], 'airq': [('EPA Air Quality System', 'https://aqs.epa.gov'), ('PurpleAir', 'https://www2.purpleair.com'), ('AirNow', 'https://www.airnow.gov')], 'ailuminate': [('MLCommons AILuminate', 'https://mlcommons.org/ailuminate/')], 'airline': [('BTS TranStats', 'https://www.transtats.bts.gov'), ('FAA National Airspace System status', 'https://nasstatus.faa.gov')], 'fedsep': [('Federal Reserve', 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'), ('BEA real GDP', 'https://www.bea.gov/data/gdp/gross-domestic-product'), ('BEA PCE price index', 'https://www.bea.gov/data/personal-consumption-expenditures-price-index'), ('BLS unemployment rate (LNS14000000)', 'https://data.bls.gov/timeseries/LNS14000000'), ('Federal Reserve Board H.15', 'https://www.federalreserve.gov/releases/h15/'), ('FOMC target range changes', 'https://www.federalreserve.gov/monetarypolicy/openmarket.htm')], 'time': [('NTP Pool', 'https://www.ntppool.org')], 'forecast': [('National Weather Service API', 'https://www.weather.gov/documentation/services-web-api'), ('Iowa Environmental Mesonet ASOS archive', 'https://mesonet.agron.iastate.edu/request/download.phtml')], 'cadence': [('CMS data.json', 'https://data.cms.gov/data.json'), ('CDC data.json', 'https://data.cdc.gov/data.json'), ('HealthData.gov data.json', 'https://healthdata.gov/data.json'), ('Veterans Affairs data.json', 'https://data.va.gov/data.json'), ('Energy data.json', 'https://www.energy.gov/data.json'), ('Labor data.json', 'https://www.dol.gov/data.json'), ('HealthCare.gov data.json', 'https://data.healthcare.gov/data.json'), ('BLS data.json', 'https://data.bls.gov/data.json')], 'launch': [('The Space Devs Launch Library', 'https://thespacedevs.com')], 'arxivdrift': [('arXiv API', 'https://info.arxiv.org/help/api/index.html')], 'change': [('Claude Platform', 'https://platform.claude.com'), ('OpenAI developers', 'https://developers.openai.com'), ('Google AI', 'https://ai.google.dev'), ('Cloudflare developers', 'https://developers.cloudflare.com')], 'seat': [('GitHub Actions', 'https://docs.github.com/actions')],
        'coin': [('Ravencoin whitepaper, 3 April 2018', 'https://ravencoin.org/assets/documents/Ravencoin.pdf'), ('Ravencoin Insight explorer', 'https://explorer.rvn.zelcore.io'), ('mempool.space mining pools, for the Bitcoin control', 'https://mempool.space/mining')],
        'cada': [('Phishing.Database active domain list', 'https://github.com/mitchellkrogza/Phishing.Database'), ('CERT Polska domain list for blocking', 'https://hole.cert.pl/domains/'), ('Cloudflare 1.1.1.1', 'https://one.one.one.one'), ('Quad9', 'https://www.quad9.net'), ('Google Public DNS', 'https://developers.google.com/speed/public-dns')],
        'campus': [('The documents cited on OY', 'https://indahl.ai/oy')]}
# 30 Oct 2026 (site pass H-18, I-17): one sentence after the source line says how often the page reads its sources. Rider cadences are ticks of the tick bus, about 5.75 minutes each.
_SRCNOTE = {'time': 'Read about every 17 minutes.', 'coin': 'Read about every 12 minutes.', 'cada': 'Read about every 17 minutes.', 'forecast': 'Each station&rsquo;s forecast is fetched at most once in 6 hours.', 'trials': 'Read about every 5 hours.', 'launch': 'Read about every half hour.',
            'linkrot': 'Links are checked about every half hour, each at least 7 days after its last check.', 'hosts': 'Read about every 12 minutes.', 'campus': 'Read about every 7 hours.', 'airq': 'The live panel is read about every hour. Each window comparison was read once.',
            'ailuminate': 'Read about every 2 hours.', 'hpt': 'Read about once a week.', 'cadence': 'Each portal is read once in 24 hours. FEMA&rsquo;s data.json could not be read on the first pass, so FEMA is not in the table.'}
def _swline(keys):   # 30 Oct 2026: also used for the LAB desk. Parts are joined with commas, not semicolons.
    parts = []
    for k in keys:
        nm, git, pypi = _SW[k]
        parts.append(f'<a href="{git}">{nm}</a> (<a href="{git}">git</a>' + (f' &middot; <a href="{pypi}">PyPI</a>' if pypi else '') + ')')
    return '<p class="meta">Software this page uses or compares against: ' + ', '.join(parts) + '.</p>'
def _codeline(c):
    if c not in _CODE: return ''
    links = ' &middot; '.join(f'<a href="{_GH}{d}">{l}</a>' for d, l in _CODE[c])
    extra = ''
    if c == 'iris': extra = ' &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/faultsguards">Standards package (git)</a> &middot; <a href="https://pypi.org/project/faultsguards/">PyPI</a> &middot; <a href="https://huggingface.co/datasets/indahl/faultsguards">Standards dataset</a>'
    sw = ''
    if c in _SWMAP: sw = _swline(_SWMAP[c])
    src = ('<p class="meta">Data read from: ' + ' &middot; '.join(f'<a href="{u}">{n}</a>' for n, u in _SRC[c]) + '.' + (' ' + _SRCNOTE[c] if c in _SRCNOTE else '') + '</p>') if c in _SRC else ''
    return f'<p class="meta">Plan, code and trend history for this page are public: {links}{extra}. Every plan was committed before the data it describes.</p>' + src + sw
# 29 Oct 2026: right of reply block on each corner page (replies/PLAN.md). Shows nothing until a reply is posted.
for _p, _c in (('/predictions','predictions'),('/time','time'),('/cada','cada'),('/uptime','uptime'),('/forecast','forecast'),('/cadence','cadence'),('/trials','trials'),('/launch','launch'),('/linkrot','linkrot'),('/tape','tape'),('/hosts','hosts'),('/campus','campus'),('/airq','airq'),('/ailuminate','ailuminate'),('/hpt','hpt'),('/weights','weights'),('/airline','airline'),('/fedsep','fedsep'),('/revise','revise'),('/stack','stack'),('/pkginstall','pkginstall'),('/seat','seat'),('/secrecords','secrecords'),('/change','change'),('/hfsize','hfsize'),('/hflicense','hflicense'),('/pkglicense','pkglicense'),('/support','support'),('/arxivdrift','arxivdrift'),('/qia','qia'),('/iris','iris'),('/atlas','atlas'),('/hermes/model','model'),('/oy','oy')):
    if _p in PAGES and '</main>' in PAGES[_p]:
        PAGES[_p] = PAGES[_p].replace('</main>', _codeline(_c) + f'<section id="replies" data-prefix="{_c}"></section><script src="/replies.js" defer></script></main>', 1)
if '/iris/lab' in PAGES and '</main>' in PAGES['/iris/lab']:   # 30 Oct 2026: the LAB desk runs the bench on Ollama, trains with MLX LM and uses the Standards package
    PAGES['/iris/lab'] = PAGES['/iris/lab'].replace('</main>', _swline(['ollama', 'mlx-lm', 'mlx', 'faultsguards']) + '</main>', 1)



# 29 Oct 2026: DIVISIONS. Each live page has one home division. A division page lists its desks, and a desk page shows its division.
DESKS = {'/census': [('/census/revisions', 'REVISIONS', 'Stated Census intervals against the revisions that followed'), ('/census/coverage', 'COVERAGE', 'The 2020 Census state counts against the Census Bureau\'s own survey'), ('/census/fidelity', 'FIDELITY', 'State marriage and divorce counts from the CDC against the Census survey estimates'), ('/census/vintages', 'VINTAGES', 'State population estimates across Vintages and against the 2020 Census count')],
         '/oy': [('/campus', 'CAMPUS', 'The documents behind the OY page, kept over time'), ('/rank', 'RANK', 'US News education rankings against the public record')],
         '/iris': [('/iris/lab', 'LAB', 'Our own model runs: STAN training live, the house training, Falcon training, the finalists, Standards across models'), ('/yo', 'YO', 'Our small language model trained on IBM calibration records: live reads and every test'), ('/hfsize', 'HFSIZE', 'Model names against the weights'), ('/hflicense', 'HFLICENSE', 'Stated licenses against license files'), ('/pkglicense', 'PKGLICENSE', 'Package licenses against repository licenses'), ('/pkginstall', 'PKGINSTALL', 'Install commands against pip resolution'), ('/weights', 'WEIGHTS', 'Model names against their weight files, pass after pass'), ('/ailuminate', 'AILUMINATE', 'MLCommons AILuminate Safety results, kept and checked'), ('/hosts', 'HOSTS', 'One open-weight model, many hosts, stated uptime and quantization')],
         '/atlas': [('/atlas/electricity', 'ELECTRICITY', 'Prices, providers and generation by state'), ('/atlas/power-plants', 'POWER PLANTS', 'Every operating plant by fuel and capacity'), ('/atlas/carbon', 'CARBON', 'Pounds of CO2 per megawatthour by state and grid region'), ('/atlas/planned-plants', 'PLANNED PLANTS', 'What is coming, by fuel, stage and year'), ('/petrol', 'PETROL', 'OPEC+ required production against delivered output'), ('/water', 'WATER', 'Reservoir forecasts against measured levels'), ('/neo', 'NEO', 'Stated asteroid close-approach distances against the later record'), ('/solar', 'SOLAR', 'Stated flare and storm chances against what happened'), ('/quake', 'QUAKE', 'Stated aftershock odds against the aftershocks that followed'), ('/cone', 'CONE', 'The hurricane forecast cone against where storms went'),
                    ('/uptime', 'UPTIME', 'Vendor status pages against independent probes'), ('/time', 'TIME', 'Public time servers, stated against delivered'), ('/cada', 'CADA', 'Public DNS filters against fresh abuse reports'), ('/secrecords', 'SECRECORDS', 'Security records against their own rules'),
                    ('/seat', 'SEAT', 'An outside seat reads our own pages'), ('/support', 'SUPPORT', 'Stated support windows against release activity'), ('/change', 'CHANGE', 'Announced shutdown dates, kept over time')],
         '/hermes': [('/hermes/datapapers', 'DATA PAPERS', 'Papers in four data journals, each listed with the files its repository serves'), ('/hermes/model', 'MODEL', 'Models and the hardware they run on: vendor statements against published results, model claims rerun, studies against their released data'), ('/trials', 'TRIALS', 'Results due against results posted, and stopped trials'), ('/hpt', 'HPT', 'Hospital price files against the rule'), ('/airline', 'AIRLINE', 'Scheduled flight time against flown time'), ('/airq', 'AIRQ', 'Air sensors against the EPA\'s own targets'), ('/revise', 'REVISE', 'Stated margin against later revision'), ('/fedsep', 'FEDSEP', 'The Fed\'s stated ranges against outcomes'), ('/cadence', 'CADENCE', 'Stated update schedules against delivered'),
                  ('/forecast', 'FORECAST', 'Stated chance against what happened'), ('/seasonal', 'SEASONAL', 'Stated seasonal outlook chances against what was observed'), ('/steo', 'STEO', 'Stated energy price intervals against the spot price'), ('/flu', 'FLU', 'Stated flu forecast intervals against reported admissions'), ('/tornado', 'TORNADO', 'Stated tornado chances and warning goals against the tornadoes that came'), ('/credit', 'CREDIT', 'Stated complaint responses and card terms against the public record'), ('/forecasters', 'FORECASTERS', 'Every forecaster desk on one axis, stated against delivered'), ('/launch', 'LAUNCH', 'Stated launch time against the time it flew'), ('/tape', 'TAPE', 'Every page and live feed, hashed and chained, with a beacon'), ('/vault', 'VAULT', 'A receipt for any file, or a file sealed until a date, no file stored'),  ('/arxivdrift', 'ARXIVDRIFT', 'Studies read, then revised'), ('/linkrot', 'LINKROT', 'Stated code links against live'), ('/wiki', 'WIKI', 'Cited figures against their source'), ('/social', 'SOCIAL', 'Platform reports against the filings'), ('/predictions', 'NOW', 'Public predictions against their deadline, and FORTUNE'), ('/stack', 'STACK', 'Every test side by side'), ('/oy', 'OY', 'Education policy studies and school data against the public record'), ('/census', 'CENSUS', 'Census Bureau statements about the uncertainty of its first estimates, against the revisions that followed')]}   # 10 Nov (Wayfinder): STACK moves from the banner into HERMES; SOCIAL takes its banner slot. 12 Nov (Wayfinder): SAGAR leads the banner; OY, SOCIAL and CENSUS fold under HERMES
_DNAME = {'/iris': 'IRIS', '/atlas': 'ATLAS', '/hermes': 'HERMES', '/oy': 'OY', '/census': 'CENSUS'}
for _d, _ds in DESKS.items():
    if _d == '/hermes': continue
    _ds = [x for x in _ds if x[0] in PAGES]
    if _d in PAGES and _ds and '<main class="wrap">' in PAGES[_d]:
        _li = ''.join(f'<li><a href="{h}">{n}</a> <span class="deskwhat">{w}</span> <span class="deskread" data-page="{n}"></span></li>' for h, n, w in _ds)
        PAGES[_d] = PAGES[_d].replace('<main class="wrap">' + _hlslot(_d), '<main class="wrap">' + _hlslot(_d) + '<section class="desks"><h2>Desks</h2><p>The live pages that belong to ' + _DNAME[_d] + '. Each keeps its own plan, code and trend history.</p><ul class="desklist">' + _li + '</ul></section><script src="/desks.js" defer></script>', 1)
for _p, _d in list(HOME.items()) + [(k, '/hermes') for k in PAGES if k.startswith('/hermes/')]:
    if _p in PAGES and '<main class="wrap">' in PAGES[_p]:
        PAGES[_p] = PAGES[_p].replace('<main class="wrap">' + _hlslot(_p), '<main class="wrap">' + _hlslot(_p) + '<p class="meta crumb">Division: <a href="' + _d + '">' + _DNAME[_d] + '</a></p>', 1)
# 29 Oct 2026 (his word): the home page is organised under the five divisions, desks listed inside each, built from DESKS so it cannot drift from the menu.
def _deskline(d):
    return ''.join(f'<a href="{h}">{n}</a>' for h, n, w in DESKS.get(d, []) if h in PAGES)
_DIVS = [('/sagar', 'SAGAR', 'Standards Audit of Gravitational and Astrophysical Research', 'Checkable errata in gravitational-wave papers, each with a verbatim quote and where the paper shows otherwise.', '<a href="/sagar">Errata list</a>'),
         ('/qia', 'QIA', 'Quantum Idle Audit', 'IBM&rsquo;s published calibration checked against itself, line by line.', '<a href="/qia#audit">QIA Audit</a><a href="/qia">Studies and key</a>'),
         ('/iris', 'IRIS', 'Inorganic Research &amp; Intelligence Systems', 'Language models and the software around them, against what is stated about them.', _deskline('/iris')),
         ('/hermes', 'HERMES', 'Held Every Record, Measured Every Statement', 'Public claims by vendors and institutions against the record, with the OY, SOCIAL and CENSUS desks.', _deskline('/hermes')),
         ('/atlas', 'ATLAS', 'Built Infrastructure', 'Data centers, power plants, electricity and carbon mapped from open sources, and servers, time, DNS, status pages and security records against their own rules.', _deskline('/atlas'))]
_cards = ''.join(f'<div class="hdiv"><h2><a href="{h}">{n}</a></h2><p class="hsub">{full}</p><p class="hwhat">{what}</p><p class="hdesks">{desks}</p></div>' for h, n, full, what, desks in _DIVS)
PAGES['/'] = page('/', 'Heuremen LLC',
 'Heuremen LLC recounts published claims about AI benchmarks, quantum hardware and public data from the material released with them, with receipts anyone can rerun. Open benchmark verification and an open record of every correction.',
 '<section class="hdivs">' + _cards + '</section><section class="hmore"><a href="/standard">STANDARDS</a><a href="/connect">CONNECT &middot; Connectors, plugins and skills</a><a href="/record">RECORD &middot; What we recounted and corrected</a><a href="/stack">STACK &middot; Every test, side by side</a><a href="/api">API &middot; Data and MCP</a><a href="https://github.com/Heuremen-LLC/indahl.ai">Plans, code and trend history &middot; GitHub</a><a href="https://huggingface.co/indahl">Datasets and models &middot; Hugging Face</a></section>',
 hero_slim('Heuremen LLC'))

# 29 Oct 2026 (his word): HERMES is the menu of everything. The old SAD material is the MODEL desk at /hermes/model.
_HUB = '<h2>The menu of everything</h2><p>HERMES holds every division and every desk in one place. The name is a goal and not a coverage claim, and each desk states what it covers. Each desk keeps its own plan, code and trend history, and a reading shown below comes from the desk\'s own feed.</p>'
for _name, _path, _what, _dk in (('QIA', '/qia', 'IBM calibration audited against itself, T1 and T2 runs, the processor queue and the quantum studies indexed', None), ('IRIS', '/iris', 'Language-model evaluations and the studies indexed, with the desks for models and packages', '/iris'),
                                 ('OY', '/oy', 'What colleges publish about measuring their own AI policies', '/oy'), ('ATLAS', '/atlas', 'Built infrastructure, mapped from open sources, with the desks listed below', '/atlas'),
                                 ('HERMES', '/hermes', 'Claims by vendors and public institutions against the record', '/hermes'), ('CENSUS', '/census', 'Census Bureau statements about the uncertainty of its first estimates, against the revisions that followed', '/census')):
    _items = [x for x in DESKS.get(_dk, []) if x[0] in PAGES] if _dk else []
    _HUB += '<h3><a href="' + _path + '">' + _name + '</a></h3><p>' + _what + '.</p>' + (('<ul class="desklist">' + ''.join(f'<li><a href="{h}">{n}</a> <span class="deskwhat">{w}</span> <span class="deskread" data-page="{n}"></span></li>' for h, n, w in _items) + '</ul>') if _items else '')
_HUB += '<h3><a href="/stack">STACK</a></h3><p>Every test side by side, with a random stack.</p><script src="/desks.js" defer></script>'
# 31 Oct 2026 (his "hell yeah go"): NOW, everything moving on the site from the live feeds. The installed app opens here.
PAGES['/now'] = page('/now', 'NOW: Everything Moving | Heuremen LLC',
 'Everything moving on indahl.ai right now: desks being read, training, live reads of IBM records, processor queues and the newest studies on the Lists, from the live feeds.',
 '<section><div id="now" class="nowbox">Loading the live feeds.</div><script src="/now.js" defer></script></section>', hero_slim('NOW', 'Everything moving right now'))
PAGES['/hermes'] = page('/hermes', 'HERMES | Held Every Record, Measured Every Statement | Heuremen LLC', 'HERMES: the menu of everything. Every division and every desk of Heuremen LLC, with the reading a desk publishes.', '<section class="legal">' + _HUB + '</section>', hero_slim('HERMES &middot; Held Every Record, Measured Every Statement'))
_FEED.append(('/hermes', 'HERMES: Held Every Record, Measured Every Statement', 'The menu of every division and desk, with the live reading where a desk has one.'))


# 1 Nov 2026 (his word: "Keep the darkwave as a separate tab on indahl.ai, and have a link to it on heuremen.org"): the Darkwave page lives
# here, built from the one source (arxiv_keystone/site/darkwave.html), under the DARKWAVE tab. heuremen.org links to it.
_dw = open(os.path.expanduser('~/bones-forge/arxiv_keystone/site/darkwave.html'), encoding='utf-8').read()
_dw_desc = _re.search(r'name="description" content="(.*?)"', _dw).group(1)
_dw_body = _dw[_dw.index('<h1>Darkwave</h1>') + len('<h1>Darkwave</h1>'):_dw.index('<p class="foot">')]
_dw_sub = _re.search(r'<p class="sub">(.*?)</p>', _dw_body, _re.S).group(1)
_dw_body = _dw_body.replace('<p class="sub">' + _dw_sub + '</p>', '', 1).replace('/media/darkwave_fig1.png', '/darkwave/fig1.png').replace('class="sub"', 'class="dwnote"').replace('class="lede"', 'class="dwlede"')
assert 'href="/' not in _dw_body.replace('href="/darkwave', ''), 'relative heuremen.org link left in the Darkwave body'
PAGES['/darkwave'] = page('/darkwave', 'Darkwave | A Readout’s Kick Is a Turn | Heuremen LLC', html.unescape(_dw_desc), '<section class="dwpage">' + _dw_body + '</section>', hero_slim('DARKWAVE', _dw_sub))
CSS += ".dwpage table{border-collapse:collapse;font-size:14.5px;margin:12px 0;display:block;overflow-x:auto}.dwpage th{text-align:left;font-weight:600;border-bottom:1px solid currentColor;padding:5px 20px 5px 0}.dwpage td{padding:4px 20px 4px 0;border-bottom:1px solid rgba(127,127,127,.25);font-variant-numeric:tabular-nums}.dwpage img{max-width:100%;height:auto;margin:14px 0}.dwpage .dwnote{opacity:.8;font-size:14px}.dwpage .dwlede{font-size:18px;line-height:1.55}\n"

# 29 Oct 2026: main menu = five divisions and STACK (10 Nov: SOCIAL replaced STACK in the banner); a division with desks gets a dropdown of what is beneath it (hover or focus, no script). QIA stays a plain link.
# 10 Nov 2026 (Wayfinder: "can the headers get a drop-down menu too?"): every banner header has a dropdown. The panel opens on hover and on
# keyboard focus with no script, and nav.js makes the first tap on a touch screen open it. The first panel entry is the division's own page,
# so a touch reader reaches it from the panel too. Filled once in main(), after the package and data-pack pages exist.
_NAVEXTRA = {'/qia': [('/qia/list', 'The List', ''), ('/qia/data', 'Qubit Data', ''), ('/qia/key', 'Key', ''), ('/qia/package', 'Research package', '')],
             '/oy': [('/oy/data-pack', 'Data pack', ''), ('/campus', 'CAMPUS', '')],
             '/social': [('/social#social-dsa', 'DSA reports', ''), ('/social#adspend', 'Political ad spend', ''), ('/social#social-tiktok', 'TikTok', ''), ('/social#bluesky', 'Bluesky', ''), ('/social/social-data-pack.zip', 'Data pack (zip)', '')]}
def _navfor(path):
    home = _menuhome(path, HOME.get(path) or ('/hermes' if path == '/hermes' or path.startswith('/hermes/') else path))
    out = []
    for h, t in NAV:
        if h not in ('/sagar', '/qia', '/iris', '/atlas', '/hermes'): continue   # 12 Nov: SAGAR leads, OY SOCIAL and CENSUS live inside the HERMES dropdown
        cur = ' aria-current=page' if h == home else ''
        ds = [x for x in DESKS.get(h, []) + _NAVEXTRA.get(h, []) if (x[0].split('#')[0] in PAGES or (x[0].endswith('.zip') and os.path.isfile(os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public', x[0].lstrip('/'))))) and x[0] != h]
        _seen = set(); ds = [x for x in ds if not (x[0] in _seen or _seen.add(x[0]))]
        if ds or h == '/sagar': out.append('<span class="dd"><a href="' + h + '"' + cur + '>' + t + '</a><span class="ddpanel"><a href="' + h + '">' + t + ' main page</a>' + ''.join('<a href="' + a + '">' + b + '</a>' for a, b, c in ds) + '</span></span>')
        else: out.append('<a href="' + h + '"' + cur + '>' + t + '</a>')
    out.append('<a class="dw" href="/darkwave"' + (' aria-current=page' if path == '/darkwave' else '') + '>DARKWAVE</a>')   # 31 Oct: the Darkwave page on heuremen.org (countdown, then the paper page)
    return ''.join(out)

CSS += """
.links a.dw,.links a.dw:hover{background:linear-gradient(90deg,#0891b2,#7c3aed,#c026d3,#0891b2);background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:dwshift 6s linear infinite}@keyframes dwshift{to{background-position:300% 0}}@media (prefers-reduced-motion:reduce){.links a.dw{animation:none}}
.dd{position:relative;display:inline-block}.ddpanel{display:none;position:absolute;left:0;top:100%;margin-top:6px;background:var(--paper);border:1px solid var(--rule);padding:10px 16px;flex-direction:column;gap:8px;min-width:190px;z-index:7}.dd:hover .ddpanel,.dd:focus-within .ddpanel{display:flex}.ddpanel::before{content:'';position:absolute;left:-1px;right:-1px;top:-10px;height:10px}.dd.open .ddpanel{display:flex}.dd.shut .ddpanel{display:none!important}@media (min-width:861px){.links .dd:last-of-type .ddpanel{left:auto;right:0}}@media (max-width:860px){.links{position:relative}.links .dd{position:static}.links .dd.open .ddpanel,.links .dd:has(a:focus-visible) .ddpanel{display:flex!important;left:0;right:0;top:100%;margin-top:2px;flex-flow:row wrap;gap:10px 20px;min-width:0;max-height:62vh;overflow-y:auto}.links .dd.shut .ddpanel{display:none!important}.links .ddpanel a{white-space:normal;padding:4px 0}.dd.open .ggpanel,.ggdd:focus-within .ggpanel{display:flex!important}.ggdd.shut .ggpanel{display:none!important}}\n.share{margin:30px 0 8px;padding-top:14px;border-top:1px solid var(--rule)}.share h3{margin:12px 0 6px}.embedcode{display:block;width:100%;box-sizing:border-box;font:13px/1.45 ui-monospace,Menlo,monospace;padding:8px 10px;border:1px solid var(--rule);background:var(--paper2);color:var(--ink);resize:vertical}.ddpanel a{white-space:nowrap}
.desklist{list-style:none;padding:0;margin:0}.desks{padding-bottom:6px}.desks+script+.meta,.desks+.meta{margin-top:8px}.desklist li{padding:8px 0;border-bottom:1px solid var(--rule)}.desklist a{font-family:Cinzel,Georgia,serif;font-weight:600;letter-spacing:.12em;margin-right:10px}.deskwhat{color:var(--mid)}.deskread{display:block;font-size:14px;color:var(--mid);margin-top:2px}.crumb{margin:0 0 14px}
.livemenu{position:relative}.livemenu summary{list-style:none;cursor:pointer;font-family:Cinzel,Georgia,serif;font-weight:600;letter-spacing:.16em;text-transform:uppercase;font-size:12px;color:var(--mid);padding:6px 0;border-bottom:2px solid transparent}
.livemenu summary::-webkit-details-marker{display:none}.livemenu summary::after{content:" \\25BE"}.livemenu summary:hover,.livemenu summary[aria-current]{color:var(--ink);border-bottom-color:var(--rule)}
.livepanel{position:absolute;right:0;top:100%;margin-top:10px;background:var(--paper);border:1px solid var(--rule);padding:12px 18px;display:flex;flex-direction:column;gap:10px;min-width:170px;z-index:6}
.livepanel a{white-space:nowrap}
.livetag.lt-own{background:#1f7a3a;color:#fff;box-shadow:0 0 0 1px #1f7a3a}.livetag.lt-own:before{background:#9be7b0;animation:livepulse 1.6s ease-in-out infinite}@media (prefers-color-scheme:dark){.livetag.lt-own{background:#4cc27a;color:#08210f;box-shadow:0 0 0 1px #4cc27a}.livetag.lt-own:before{background:#08210f}}@media (prefers-reduced-motion:reduce){.livetag.lt-own:before{animation:none}}
#livestrip .livetag.lt-own{margin-left:0}
"""

def _page_dates(docs):
    # 30 Oct 2026 (site pass A-13): the time a page last changed = the first build whose page differs from the build before. State: page_dates.json (path -> [sha, UTC time]).
    # 10 Nov 2026 (cold read row 16): the sha is taken over the page's <main> only, with ?v= version stamps removed, so a change to the shared nav,
    # footer or stylesheet no longer stamps every page as changed (716 of 727 feed entries carried one build time). A page with no entry under this
    # rule is seeded from the public mirror's history: the oldest commit in the newest run of versions whose <main> matches this build.
    import json as _j, hashlib as _h2, subprocess as _sp, datetime as _dt
    def ck(doc):
        a = doc.find('<main'); b = doc.rfind('</main>'); m = doc[a:b] if a >= 0 and b > a else doc
        m = _re.sub(r'(?s)<!--emb-->.*?<!--/emb-->', '', m)   # 10 Nov 2026 (findable pass): the embed and data links block carries a read time, not content
        return _h2.sha256(_re.sub(r'\?v=[0-9a-f]{6,}', '', m).encode('utf-8')).hexdigest()[:16]
    sf = os.path.join(HERE, 'page_dates.json'); st = _j.load(open(sf)) if os.path.exists(sf) else {}
    if st.get('_rule') != 'main-v1': st = {}
    now = _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); out = {'_rule': 'main-v1'}; mirror = os.path.join(HERE, '..', 'public_mirror', 'indahl.ai')
    hs = {p: ck(doc) for p, doc in docs.items()}
    need = {('index.html' if p == '/' else p.strip('/') + '.html'): p for p in docs if not (st.get(p) and st[p][0] == hs[p]) and not st.get(p)}
    seeds = {}
    if need and os.path.isdir(mirror):
        try:
            log = _sp.run(['git', '-C', mirror, 'log', '--format=C %cI', '--raw', '--no-abbrev', '--', '*.html'], capture_output=True, text=True).stdout
            vers = {}; t = None
            for ln in log.splitlines():
                if ln.startswith('C '): t = _dt.datetime.fromisoformat(ln[2:].strip()).astimezone(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                elif ln.startswith(':') and '\t' in ln:
                    meta, path = ln.split('\t', 1); f = meta.split()
                    if path in need and f[3].strip('0'): vers.setdefault(path, []).append((t, f[3]))
            cat = _sp.Popen(['git', '-C', mirror, 'cat-file', '--batch'], stdin=_sp.PIPE, stdout=_sp.PIPE)
            def blob(sha):
                cat.stdin.write((sha + '\n').encode()); cat.stdin.flush(); hdr = cat.stdout.readline().split()
                if len(hdr) < 3: return ''
                data = cat.stdout.read(int(hdr[2])); cat.stdout.read(1); return data.decode('utf-8', 'replace')
            for path, vs in vers.items():
                want = hs[need[path]]; seen = None
                for t, sha in vs:   # newest first
                    if ck(blob(sha)) != want: break
                    seen = t
                if seen: seeds[need[path]] = seen
            cat.stdin.close(); cat.wait()
        except Exception: pass
    for p in docs:
        e = st.get(p); h = hs[p]
        out[p] = e if e and e[0] == h else [h, (seeds.get(p) if not e else None) or now]
    _j.dump(out, open(sf, 'w'))
    return {p: v[1] for p, v in out.items() if p != '_rule'}

CSS += ".lablead,.yolead{padding-bottom:4px}.svlive .tablewrap{overflow-x:auto;margin:4px 0 10px}.svlive td{padding:3px 18px 3px 0;border-bottom:1px solid rgba(127,127,127,.2)}.svlive h3{margin:22px 0 6px}.svlive .sv-ph{margin:16px 0 2px;font-weight:600}\n"
# 10 Nov 2026: receipt links (a small arrow after a number, ledger/receipts.py) and the receipt pages /r/ (body class rp)
CSS += ".rcpt{display:inline-block;text-decoration:none;color:var(--goldink);font-size:.72em;line-height:1;vertical-align:super;padding:0 .12em;margin-left:.05em;opacity:.75}.rcpt::after{content:'\\2197'}.rcpt:hover,.rcpt:focus-visible{opacity:1;text-decoration:none}@media (pointer:coarse){.rcpt{padding:.15em .3em;margin-left:0}}@media print{.rcpt{display:none}}\n" \
       ".rp-main{padding-bottom:28px}.rp-sec{margin:22px 0}.rp-sec h2{margin:0 0 8px}.rp-num{font-size:1.25em;font-weight:600;margin:6px 0;overflow-wrap:anywhere}.rp-kv{border-collapse:collapse;margin:8px 0}.rp-kv th{text-align:left;font-weight:600;padding:3px 18px 3px 0;vertical-align:top;white-space:nowrap}.rp-kv td{padding:3px 0;overflow-wrap:anywhere}.rp-h{font-size:.85em;word-break:break-all}.rp-pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.88em;background:var(--paper2);padding:8px 10px;border-left:3px solid var(--rule);max-width:100%}.rp-q{margin:6px 0 12px;padding:6px 12px;border-left:3px solid var(--rule);background:var(--paper2);overflow-wrap:anywhere}.rp-status{padding:8px 12px;border:1px solid var(--rule);background:var(--paper2)}.rp-hist{padding-left:18px}.rp-d{display:inline-block;min-width:7.5em;font-variant-numeric:tabular-nums;opacity:.8}.rp-t{border-collapse:collapse;width:100%}.rp-t th,.rp-t td{text-align:left;padding:4px 14px 4px 0;border-bottom:1px solid rgba(127,127,127,.25);vertical-align:top;overflow-wrap:anywhere}.rp-t .r{text-align:right}.rp-find{margin:14px 0 4px}.rp-find button{font:inherit;padding:4px 14px;border:1px solid var(--rule);background:var(--paper2);cursor:pointer}.rp-nav{margin-top:26px}@media (max-width:640px){.rp-kv th{white-space:normal}.rp-num{font-size:1.1em}}\n"
# 1 Nov 2026: QIA Research Package box (top right of /qia) and download button, added before the stylesheet version stamp is taken
CSS += ".rc-field{display:inline-block;margin:0 16px 10px 0;vertical-align:top}.rc-field label{display:block;font-size:14px;margin-bottom:4px}.rc-field input,.rc-field select{font:inherit;padding:4px 6px;border:1px solid var(--rule);background:var(--paper)}\n"
CSS += ".pkgbox{float:right;width:280px;margin:8px 0 16px 24px;padding:14px 16px;border:2px solid var(--rule);background:var(--paper2);font-size:15px;line-height:1.45}.pkgbox p{margin:8px 0}.pkghead{display:flex;align-items:center;gap:8px;font:400 19px/1.2 \"Abril Fatface\",Georgia,serif;color:var(--ink);text-decoration:none}.pkghead .mark{width:28px;height:28px;flex:none}.pkgbtn{display:inline-block;padding:6px 14px;background:var(--ink);color:var(--paper)!important;text-decoration:none;border-radius:2px;margin-right:10px}.pkgbtn:hover{background:var(--goldink)}.pkgget{margin:18px 0}.pkgalso{font-size:14px;margin:6px 0 0}.pkgtested{font-size:14px;margin:6px 0;color:var(--goldink)}@media (max-width:700px){.pkgbox{float:none;width:auto;margin:8px 0 16px}}\n"
# 10 Nov 2026: the Data pack link at the top right of the heading band (placed in main() on every page with data)
CSS += """
.dpk{float:right;display:inline-flex;align-items:center;gap:6px;margin:2px 0 6px 16px;padding:6px 11px;border:1px solid var(--lit);border-radius:2px;color:#efe5cf!important;text-decoration:none;font-family:Cinzel,Georgia,serif;font-weight:600;font-size:12px;letter-spacing:.14em;text-transform:uppercase;line-height:1.2;white-space:nowrap}
.dpk svg{width:13px;height:13px;flex:none}.dpk:hover{background:var(--lit);color:var(--cave)!important}.dpk:focus-visible{outline:2px solid var(--lit);outline-offset:2px}
.dpkrow{display:flex;justify-content:flex-end;margin:0 0 6px}.dpk-l{float:none;margin:0;color:var(--ink)!important;border-color:var(--rule)}.dpk-l:hover{background:var(--rule);color:var(--paper)!important}
@media (max-width:640px){.dpk{font-size:11px;padding:5px 8px;margin-left:10px;letter-spacing:.1em}}
@media print{.dpk{display:none}}
.dpkdd{float:right;position:relative}.dpkdd .dpk{float:none;background:none;cursor:pointer}.dpkdd .ggpanel{right:0;left:auto;min-width:min(520px,92vw);text-transform:none;letter-spacing:0}.ggtxt{display:block;font-size:14px;line-height:1.4;color:var(--ink);margin:4px 0 2px}.ggcal{padding-bottom:8px}.dd.dpkdd:hover .ggpanel,.dd.dpkdd:focus-within .ggpanel{display:flex!important}.dpkdd .ggpanel{color:var(--ink);font-family:Lora,Georgia,serif;font-size:15px;font-weight:400}.dpkdd .ggpanel a{color:var(--goldink)!important}
.gg{margin:10px 0 2px}.ggbtn{font:inherit;font-family:Cinzel,Georgia,serif;font-weight:600;font-size:12px;letter-spacing:.14em;text-transform:uppercase;background:var(--paper);color:var(--ink);border:1px solid var(--rule);border-radius:2px;padding:6px 12px;cursor:pointer}
.ggbtn::after{content:" \\25BE"}.ggbtn:focus-visible{outline:2px solid var(--rule);outline-offset:2px}
.ggdd{display:block}.dd.ggdd:hover .ggpanel,.dd.ggdd:focus-within .ggpanel{display:flex!important}.ggpanel{left:auto;right:0;width:min(600px,calc(100vw - 32px));min-width:0;padding:12px 16px;gap:6px}.ggpanel ul{list-style:none;margin:0;padding:0}.ggpanel li{padding:6px 0;border-bottom:1px solid rgba(200,144,42,.35);line-height:1.4}
.ggpanel li:last-child{border-bottom:0}.ggpanel a{white-space:normal;font-family:Cinzel,Georgia,serif;font-weight:600;letter-spacing:.1em;margin-right:8px}.ggw{color:var(--mid)}.ggs{font-size:13px;color:var(--mid);white-space:nowrap}
@media (max-width:640px){.mtx{display:block;max-width:100%;overflow-x:auto}.bench-live{max-width:100%;overflow-x:auto}}
.ggs::before{content:"\\00b7\\00a0"}.ggr{display:block;font-size:13px;color:var(--goldink)}.ggnote{display:block;font-size:14px;color:var(--mid);margin-bottom:4px}.ggall a{font-size:15px}
@media (max-width:640px){.ggpanel{position:static;margin-top:8px;width:auto}}
"""
import alerts as _alr; CSS += _alr.CSS   # 10 Nov 2026: the one sign-up form in every footer, and /alerts (alerts.py, alerts.js, newsletter.js, alerts_send.py)
import notify as _ntf; CSS += _ntf.CSS   # 10 Nov 2026: /follow, /webhooks, /changelog, calendars, feeds, device notifications (notify.py, notify.js, webhooks_send.py, push_send.py)
import weekly as _wk; CSS += _wk.CSS   # 10 Nov 2026: /week pages (weekly.py); placed in main() below
def main():
    names = {}
    import hashlib as _hh
    _cv = _hh.sha256(CSS.encode()).hexdigest()[:8]
    for _pp in PAGES: PAGES[_pp] = PAGES[_pp].replace('@@CSSV@@', _cv)
    _pub = os.path.join(HERE, '..', 'cloudflare-workers', 'heuremen-door', 'public')
    # 31 Oct 2026 (his "when the training runs finish can they be collapsed into oneliners?"): a finished run keeps its title and one plain
    # sentence with its result, and its tables, method and data sit behind a click. Live runs stay open. The one-liners carry no new numbers.
    def _collapse(doc, rules):
        for _h, _one in rules:
            _k = doc.find(_h); _i = doc.rfind('<h2', 0, _k) if _k >= 0 else -1
            if _i < 0 or doc.find('</h2>', _i) < _k: raise SystemExit('collapse: section not found: ' + _h[:60])
            _e = doc.index('</h2>', _i) + 5; _end = doc.index('</section>', _e)
            doc = doc[:_e] + ('<p class="oneliner">' + _one + '</p>' if _one else '') + '<details class="runbox"><summary>Tables, method and data</summary>' + doc[_e:_end] + '</details>' + doc[_end:]
        return doc
    # 9 Nov 2026: the YO reads section moved from /qia to the YO desk (/yo, YO_READS).
    PAGES['/iris'] = _collapse(PAGES['/iris'], [
        ('reversing the order of the options changes 27% to 50%', None),   # 10 Nov 2026: the IRIS headline was reworded (newsletter audit), key follows it
        ('Models as judges in our own pipeline', 'Most of our own judge&rsquo;s recorded verdicts were holds with no decision, and the harness had to force most of the orchestrator&rsquo;s asks.'),
        ('Our own fine-tuning runs', 'In our own LoRA runs, some training sessions reached a loss that was not a number, and no candidate adapter cleared our promotion bar.')])
    PAGES['/iris/lab'] = _collapse(PAGES['/iris/lab'], [
        ('A Falcon Trained on the Standards', 'Against the untouched model, training on the Standards shows no gain in any Fault family. One training run per model, one seed.'),
        ('The Two Finalists, Head to Head', 'Every Fault family reads cannot tell in both head-to-head rounds, and no winner is named.'),
        ('A Small Model Trained on the House&rsquo;s Own Answers', 'Trained on answers the code scored right, the model got fewer answers wrong on held-out rounds, by amounts that differ between seeds, and much worse at naming the highest of a list of values.')])
    # 9 Nov 2026: the YO record (every version and the YO Read checks) sits inside the YO desk's training section, behind one click.
    _YO_RECORD = 'YO v7 is the model at work. In YO v4&rsquo;s planned test on IBM records held out from training, it found 905 of 928 qubits stale by one to two days in records whose eight qubits all sat near that line, where YO v2 found 403. YO v5, trained further on same-date items (8 qubits from one record that share a calibration date), found 2,312 (seed 47) and 2,297 (seed 48) of 2,320 stale qubits in such items, where YO v4 found 2,240. Seed 47&rsquo;s gain is above zero and seed 48&rsquo;s cannot be told from zero. Seed 47 was below YO v4 on the share of its flags that were right and seed 48 on the verdicts, so YO v4 stays at work. YO v6, trained further on young groups, flagged 2 and 1 of the 1,974 young qubits sitting beside a stale one with its two seeds, where YO v4 flagged 94, but neither seed&rsquo;s gain on older same-date stale qubits was clear, one seed was below YO v4 on whole-window recall and the other found fewer stale neighbours, so YO v4 stays at work. YO v7, trained again with YO v4&rsquo;s whole-window and band items restored, found 0.993 to 1.000 of the 2,320 older same-date stale qubits across the three retest seeds, where YO v4 found 0.969, without being shown to flag more young qubits, so by the rule written before training YO v7 seed 51 now does the live reads (one of the first two seeds failed). YO v8, trained further on verdicts near the edges of the rule, scored higher on exact border verdicts than YO v7 in all three seeds (0.754 to 0.769 against 0.729, one seed&rsquo;s band reaching zero) but each of its three seeds did worse on another reading, so by the rule written before training YO v7 stays at work. YO Read, a second adapter trained to read quantum-hardware papers, was scored again on its 148 held-out papers under a rule fixed and timestamped before the run, after 22 of those papers were found to have been given the wrong text (the answers it is scored against did not change). That check, and the decision to rescore, were made after we had seen the first scores, so the rescore is a correction defined after the data, under a rule fixed before it ran. On whether a paper prints the dates of its hardware runs, two of its three seeds beat always answering no (0.919 and 0.939 of papers right, against 0.804), and the third does not (0.831), because it says yes too readily: it catches 28 of the 29 papers that print dates but also says yes on 24 of the 119 that do not. On whether a paper links its own data or code, all three seeds beat always answering no (0.811, 0.757 and 0.811, against 0.514), which is a low bar, and 5 of the 148 answers it is scored against there are still wrong: our code read them as yes where the List entry says the paper prints no link. On whether a paper says its data are available on request, the seeds score 0.980, 0.959 and 0.966 against 0.912 for always answering no, but none survives the correction for testing several questions at once, and with only 13 papers that say so, this test is too small to show a gain reliably. Each paper counts once per question, and three seeds are a count of trained copies, not a rate. Two further checks of YO Read were planned and timestamped before they ran. In the first, three copies were trained on the same papers with the yes and no answers shuffled between papers. None of the three beat always answering no on dates or on data links, so three adapters trained on shuffled answers did not reproduce the gain. On data links two of them scored below always answering no (63 and 69 of the 148 papers right, against 76). In the second, three copies were trained on the base model&rsquo;s own answers instead of the real labels. On dates YO Read beat two of them and not the third, which was paired with seed 63, the seed that also did not beat always answering no. On data links YO Read was ahead of all three by 7 to 16 of the 148 papers, but no gap survives the correction for testing several comparisons at once. On dates and data links YO Read was right on more papers than its partner in all six pairs, a reading defined after the data. So on dates and data links the gain is not shown to need the real labels, and three seeds may be too few to show a gap this size. On data available on request YO Read beat all three, and this is not evidence that the real labels matter. Before training, the base model&rsquo;s own answers said yes on 28% of the training papers where the real share is 11%, so that comparison was marked a weak test, and the three copies trained on those answers fell below always answering no (95 to 105 of the 148 papers right, against 135). YO Read itself did not beat always answering no on that question with any of its three seeds. On dates the base model&rsquo;s answers were close to the real share in the 497 training papers (25% against 22%) and not in the 43 validation papers (37% against 16%). The plan did not say which of those two sets decides the flag, so both are shown, and no conclusion depends on which. All of these results measure how well YO Read matches the List reader&rsquo;s notes, which record what a paper leaves out, not whether it reads each paper correctly. On data links 5 of the 148 answers it is scored against are known to be wrong, because our code read the note as yes where it says no link is printed (arXiv 2210.17548, 2304.04666, 2306.01639, 2401.10293 and 2406.09316), and 7 of the answers it was trained on have the same fault. A third check was planned and timestamped, and has now run once. The same nine adapters answered 288 papers on the List that were not in their training or test sets. The result is read on 88 of them, papers screened for same work: the List reader read them in full and wrote a note on each, and papers that are the same work as one already used were taken out. That is too few papers to show a small gain, so this test is underpowered. On those 88 papers, YO Read agreed with the List reader on data available on request better than the best fixed answer and better than the copies trained on the base model&rsquo;s own answers, on all three seeds. That result rests on the 12 papers whose answer is yes: YO Read found 10 to 11 of them (86, 87 and 87 of the 88 papers right, against 76 for always answering no), and it never got wrong a paper that always answering no got right. On run dates the result depends on four labels: it holds on the 88 papers and not when the four labels we already knew were wrong or doubtful are taken out, so by the rule fixed before the run it is not shown. On data links the result was not shown: YO Read was right on 69, 67 and 70 of the 88 papers, against 70 for always answering yes, and these data cannot rule out a useful effect. The run dates reading is sensitive to which papers are included. With the one same-work paper described below taken out, run dates replicates under the same rule, against depends on four labels with it in. The stamped verdict, depends on four labels, stands. One paper moving one seed across the threshold is the fragility, not evidence for run dates. Including that paper lowers run dates, so depends on four labels is the conservative call. Its answers are no on all three questions, and so are the answers on the paper it was translated from, in the training file. YO Read said yes on its run dates with one seed and on its data links with all three, against both papers&rsquo; answers, so those answers are not memory of the trained paper. The 88 still contain one known version of a trained paper (zenodo.18154889, a Turkish translation of a paper YO Read was trained on) and one borderline later edition (LCL-833, the same programme in a later edition). The 88 stay the headline as planned, and the readings without them are published beside it. Every check fixed before the results were opened gives the same verdict on data available on request. On the full 288, which include 5 papers whose own text was in training, no verdict is read. One of the three copies trained on shuffled answers said no to every item, so that seed of the check collapsed into always answering no. It was scored as it is, and a collapsed check is weaker evidence than a working one. The plan was stamped in a Bitcoin block before the run, and the answers in a later block when it ended. The run happened once. Six notes added to the plan (A7 to A12) were written after the answers were stamped. A7 is in Bitcoin block 974624 and A8 to A12 are in block 974635, both before the results were opened, but that the answers were unread until then is our own word. Every sentence in the training files is fixed by Bitcoin block 974519, and the training files of the first seed, with their answers, are vouched for by its stamped adapter, reproduced bit for bit. The answers used for the base-model and shuffled copies are kept in git only. The spreads around these differences were worked out after the data. As before, this measures how well YO Read matches the List reader&rsquo;s notes, not whether it reads the papers correctly. The list of limits is published with the plan. YO Read is not in use yet: using it as a second reading of each paper before a QIA notice goes out waits on our word. YO v7 reads each new IBM record live on the QIA page.'
    PAGES['/yo'] = PAGES['/yo'].replace('<h2>How YO Was Trained and Tested</h2>', '<h2>How YO Was Trained and Tested</h2><p>' + _YO_RECORD + '</p>', 1)
    PAGES['/yo'] = _collapse(PAGES['/yo'], [('How YO Was Trained and Tested', 'Every version of YO, the planned test each one passed or failed, and the checks on YO Read, in full.')])
    # 1 Nov 2026 (his "a box in the top right corner that has a research package"): the QIA Research Package page, its box at the top right
    # of /qia, and the download (built by ~/bones-forge/qia_package/build_package.py into public/qia/qia-research-package.zip).
    _pk_sha = open(os.path.join(_pub, 'qia', 'qia-research-package.zip.sha256')).read().split()[0]
    _pk_body = """<p class="lede">Check the IBM Quantum calibration record your run depends on, before the run and after it. One download. Your files are opened read-only and never changed. Reports go to their own folder. Run on saved files, the checker sends nothing anywhere.</p>
<p class="pkgget"><a class="pkgbtn" href="/qia/qia-research-package.zip" download>Download the package (zip)</a> <span class="meta">sha256 <code>{SHA}</code> &middot; version 1.0.0 &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/qia-package">code (git)</a></span></p>@@QIA_CITE@@
<h2>Before a run</h2>
<ol>
<li>Save the record you are about to run under, or let the checker pull it with your own saved IBM account (needs <code>pip install qiskit-ibm-runtime</code>): <code>python qia_check.py before --pull ibm_kingston</code></li>
<li>Check it: <code>python qia_check.py before record.json --qubits 0,1,5</code>. It flags T1 or T2 measured more than 24 hours before the record&rsquo;s stamp, error values of exactly 0, T2 above 2 &times; T1, and T1 and T2 measured more than 24 hours apart.</li>
<li>Read the Guards before the work: <code>python -m faultsguards guards</code> (<a href="https://pypi.org/project/faultsguards/">PyPI</a> &middot; <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/faultsguards">git</a>).</li>
<li>Measure a T1 and T2 pair yourself in one job: <code>t1t2-check/</code> prints the QPU seconds before it submits anything.</li>
</ol>
<h2>After a run</h2>
<ol>
<li>Save the record again into the same folder. Keep reports in a different folder.</li>
<li><code>python qia_check.py after records/ --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --qubits 0,1,5</code> names the latest record in the folder stamped at or before the start, lists every newer record stamped up to the end, and shows each change in the T1, T2 and readout-error figures on your qubits. Times are UTC. If IBM recalibrated between your last saved record and the run, the record in force is not in the folder, so save one right before you submit.</li>
<li>Read the write-up against the Faults: <code>python -m faultsguards faults</code>. Give each reading a check block: <code>check-block/</code>.</li>
</ol>
<h2>What is in it</h2>
<ul>
<li><code>qia_check.py</code>: the before and after checks, Python standard library only.</li>
<li><code>yo/</code>: the reader for <a href="/yo">YO</a>, our small language model trained on IBM calibration records (<a href="https://huggingface.co/indahl/YO">Hugging Face</a>). On each run, the exact answer computed by code is printed beside YO&rsquo;s.</li>
<li><code>faultsguards/</code>: the <a href="/standard">Standards</a> package and both PDFs.</li>
<li><code>t1t2-check/</code>: T1 and a Hahn echo T2 on the same qubit in one job, on your account.</li>
<li><code>check-block/</code>: the check block and its commit gate.</li>
<li><code>papers/</code>: A Readout Is Not an Idle.</li>
<li><code>START_HERE.html</code>, <code>README.md</code>, <code>LICENSE.txt</code>, <code>CITATION.cff</code>.</li>
</ul>
<p class="meta">Heuremen LLC permits anyone to run, copy and change the code in this package, for any purpose, with attribution to Heuremen LLC and https://indahl.ai/qia. Your results remain yours. The text, papers and data follow the license file in the package, and their use to train, fine-tune or build AI models is not permitted. <a href="/qia">QIA</a> &middot; <a href="/qia/list">List</a> &middot; <a href="/qia/key">Key</a></p>""".replace('{SHA}', _pk_sha)
    PAGES['/qia/package'] = page('/qia/package', 'QIA Research Package | Quantum Idle Audit | Heuremen LLC',
        'Checks on IBM Quantum calibration records before and after a run: a record checker, YO, the <a href="/standard">Standards</a>, and a same-job T1 and T2 check. One download.',
        '<main class="wrap">' + _pk_body + '@@QIA_TESTED@@</main>', hero_slim('QIA Research Package', 'Heuremen LLC'))
    _pk_box = ('<aside class="pkgbox"><a class="pkghead" href="/qia/package"><svg class="mark" viewBox="0 0 200 200" aria-hidden="true"><polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5"/></svg>QIA Research Package</a>'
               '<p><a href="/yo">YO</a> is our small language model, Qwen3-1.7B tuned with LoRA on IBM&rsquo;s calibration records to flag stale qubit data. For runs on IBM quantum hardware, check the calibration record your run depends on, before the run and after it. The package holds a record checker, YO, the <a href="/standard">Standards</a>, and a same-job T1 and T2 check.</p>'
               '<p class="pkgtested">Tested on real IBM records and a live run. <a href="/qia/package#tested">How it was tested</a></p>'
               '<p class="pkgalso">Checker alone: <code>pip install qia-check</code> (<a href="https://pypi.org/project/qia-check/">PyPI</a>)</p>'
               '<p><a class="pkgbtn" href="/qia/qia-research-package.zip" download>Download</a> <a href="/qia/package">What is in it</a></p></aside>')
    assert PAGES['/qia'].count(_SLOT) == 1, 'QIA headline slot'
    PAGES['/qia'] = PAGES['/qia'].replace(_SLOT, _pk_box + _SLOT, 1)   # before the headline, so it floats at the top right
    # 2 Nov 2026: Check a Run against the record in force (qia_runcheck/, records from the mirror in KV, refreshed by the mirror cycle)
    _RC = open(os.path.join(HERE, '..', 'qia_runcheck', 'fragment_runcheck.html'), encoding='utf-8').read().strip()
    _cal = '<section id="cal">'; assert PAGES['/qia'].count(_cal) == 1, 'qia cal section'
    PAGES['/qia'] = PAGES['/qia'].replace(_cal, _RC + _cal, 1)
    # 2 Nov 2026 (his "do it all and make it prominent like we did for QIA"): the same box, page and download for each division. A package
    # shows only once its zip and sha256 are in public/, so each one ships when its referee is done.
    import html as _ph, re as _pr
    _MARK = '<svg class="mark" viewBox="0 0 200 200" aria-hidden="true"><polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5"/></svg>'
    # 2 Nov 2026: Zenodo DOIs for every package (zenodo_packs/dois.json), shown where the download is
    try: _DOI = _jsonld.load(open(os.path.join(HERE, '..', 'zenodo_packs', 'dois.json')))
    except Exception: _DOI = {}
    def _cite(name):
        d = (_DOI.get(name) or {}).get('concept_doi') or (_DOI.get(name) or {}).get('doi')   # 10 Nov 2026: the concept DOI, which always resolves to the newest version
        return f'<p class="pkgalso">Cite: <a href="https://doi.org/{d}">doi:{d}</a> (Zenodo)</p>' if d else ''
    def _md_body(md):
        out = []
        for blk in md.split('\n\n'):
            b = _ph.escape(blk.strip()); b = _pr.sub(r'`([^`]+)`', r'<code>\1</code>', b)
            b = _pr.sub(r'(?<![\w/"])(https://[^\s<·]*[^\s<·.,;:)])', r'<a href="\1">\1</a>', b)
            if not b or b.startswith('# ') or b.startswith('Heuremen LLC &middot;') or b.startswith('Heuremen LLC ·'): continue
            if b.startswith('## '): out.append(('<h2 id="tested">' if b[3:].startswith('Tested on') else '<h2>') + b[3:] + '</h2>')
            elif _pr.match(r'^(-|\d\.) ', b): out.append('<ul>' + ''.join('<li>' + _pr.sub(r'^(-|\d\.) ', '', l.strip()) + '</li>' for l in _pr.split(r'\n(?=(?:-|\d\.) )', b)) + '</ul>')
            else: out.append('<p>' + b.replace('\n', ' ') + '</p>')
        return '\n'.join(out)
    def _sha(rel):
        f = os.path.join(_pub, rel + '.sha256')
        return open(f).read().split()[0] if os.path.exists(f) else None
    def _box(title, href, text, zip_rel, extra='', tested=''):
        return (f'<aside class="pkgbox"><a class="pkghead" href="{href}">{_MARK}{title}</a><p>{text}</p>' + (f'<p class="pkgtested">{tested} <a href="{href}#tested">How it was tested</a></p>' if tested else '') +
                f'<p><a class="pkgbtn" href="/{zip_rel}" download>Download</a> <a href="{href}">What is in it</a></p>{extra}</aside>')
    def _tested(dist_md):
        f = os.path.join(HERE, '..', dist_md)
        return ('<section id="tested"><h2>How it was tested</h2>' + _md_body(open(f, encoding='utf-8').read()) + '</section>') if os.path.exists(f) else ''
    PAGES['/qia/package'] = PAGES['/qia/package'].replace('@@QIA_CITE@@', _cite('QIA Research Package'), 1).replace('@@QIA_TESTED@@', _tested('qia_package/dist/qia-research-package/TESTED.md'), 1)
    def _place(path, box):
        i = PAGES[path].index('<main class="wrap">') + len('<main class="wrap">'); PAGES[path] = PAGES[path][:i] + box + PAGES[path][i:]
    _LISTP = {'/qia': ('qia/qia-list-pack.zip', 'QIA List Pack'), '/iris': ('iris/iris-list-pack.zip', 'IRIS List Pack')}
    for _lp, (_lz, _lt) in _LISTP.items():
        _ls = _sha(_lz)
        if not _ls: continue
        _lbox = (f'<aside class="pkgbox"><span class="pkghead">{_MARK}{_lt}</span><p>Every study on this List as CSV, BibTeX and RIS, with the key to the codes. '
                 f'Ready for Zotero, a reference manager or a spreadsheet.</p><p class="pkgtested">Tested: every study on this List is in every file.</p><p><a class="pkgbtn" href="/{_lz}" download>Download</a> '
                 f'<span class="meta">sha256 <code>{_ls[:12]}</code></span></p>' + _cite(_lt) + '</aside>')
        _place(_lp + '/list', _lbox)
        if _lp == '/qia': PAGES['/qia'] = PAGES['/qia'].replace('<a href="/qia/package">What is in it</a></p></aside>', f'<a href="/qia/package">What is in it</a></p><p class="pkgalso">Also: <a href="/{_lz}" download>{_lt}</a> (every study on the List, CSV and BibTeX)</p></aside>', 1)
    _PKGS = [('/darkwave', '/darkwave/kit', 'darkwave/darkwave-correction-kit.zip', 'Darkwave Correction Kit', 'darkwave_kit/src/README.md',
              'For runs on IBM quantum hardware. Measure the turn a mid-circuit readout gives the untouched qubits next to it on your own account, and add the matching virtual-Z correction to your circuits.',
              'Darkwave Correction Kit | A Readout&rsquo;s Kick Is a Turn | Heuremen LLC', 'Measure the phase turn a mid-circuit readout gives untouched qubits on your own IBM account, and add the matching virtual-Z correction to your circuits.'),
             ('/iris', '/iris/package', 'iris/iris-research-package.zip', 'IRIS Research Package', 'iris_package/src/README.md',
              'For language-model evaluations. Read replies before trusting a parser, count flips between repeated runs, and compare two systems with four outcomes. With the Standards.',
              'IRIS Research Package | Recount Matrix: Language Models | Heuremen LLC', 'Checks for language-model evaluations before and after a run: reading sheets, repeat floors, paired comparisons, the Standards.'),
             ('/atlas', '/atlas/data-pack', 'atlas/atlas-data-pack.zip', 'ATLAS Data Pack', 'atlas_package/src/README.md',
              'Every ATLAS dataset in one download: data centers, power plants, planned plants, electricity, carbon and water, with the files of the other ATLAS desks, as JSON, CSV and GeoJSON with sources and pull dates.',
              'ATLAS Data Pack | Built Infrastructure | Heuremen LLC', 'Every ATLAS dataset as JSON, CSV and GeoJSON with sources and pull dates.'),
             ('/oy', '/oy/data-pack', 'oy/oy-data-pack.zip', 'OY Data Pack', 'oy_package/src/README.md',
              'For learning research. Every OY table in one download: the school policy list, the findings and the colleges, as JSON and CSV with the source of every row.',
              'OY Data Pack | Learning Research | Heuremen LLC', 'Every OY table as JSON and CSV, with the source of every row.'),
             ('/hermes/model', '/hermes/model/data-pack', 'hermes/model-data-pack.zip', 'MODEL Data Pack', 'model_package/src/README.md',
              'For AI hardware claims. Every statement on this desk with the MLCommons result it was held against, the per-accelerator results, and the file hashes, as JSON and CSV.',
              'MODEL Data Pack | Stated Against Delivered | Heuremen LLC', 'Every MODEL statement and the MLCommons results it was held against, as JSON and CSV.')]
    _TESTED = {'/darkwave/kit': ('Tested on ibm_kingston under plans published before each job.', None),
               '/iris/package': ('Tested on our own published two-machine runs, and it reproduced every flip count.', 'iris_package/dist/iris-research-package/TESTED.md'),
               '/atlas/data-pack': ('Tested in mapping and spreadsheet tools, and every count matches these pages.', 'atlas_package/dist/atlas-data-pack/TESTED.md'),
               '/oy/data-pack': ('Tested in a spreadsheet tool, and every count matches the OY pages.', 'oy_package/dist/oy-data-pack/TESTED.md'),
               '/hermes/model/data-pack': ('Tested in a spreadsheet tool, and every count matches this desk.', 'model_package/dist/model-data-pack/TESTED.md')}
    for _home, _pg, _z, _t, _src, _txt, _ttl, _dsc in _PKGS:
        _zs = _sha(_z)
        if not _zs: continue
        # 10 Nov 2026 (cold read BLOCK 1): the page shows the BUILT README (values filled), never the src template with its {TOKEN} slots
        _dist = os.path.join(HERE, '..', os.path.dirname(os.path.dirname(_src)), 'dist', _z.rsplit('/', 1)[-1][:-4], 'README.md')
        _md = open(_dist if os.path.exists(_dist) else os.path.join(HERE, '..', _src), encoding='utf-8').read()
        if _re.search(r'\{[A-Z][A-Z0-9_]{2,}\}', _md): raise SystemExit(f'BUILD REFUSED: {_pg} README has unfilled {{TOKEN}} slots; rebuild the package first')
        _body = (f'<main class="wrap"><p class="pkgget"><a class="pkgbtn" href="/{_z}" download>Download (zip)</a> <span class="meta">sha256 <code>{_zs}</code> &middot; '
                 f'<a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/' + {'/darkwave/kit': 'darkwave-kit', '/iris/package': 'iris-package', '/atlas/data-pack': 'atlas-data-pack', '/oy/data-pack': 'oy-data-pack', '/hermes/model/data-pack': 'model-data-pack'}[_pg] + '">code (git)</a></span></p>' + _cite({'/darkwave/kit': 'Darkwave Correction Kit', '/iris/package': 'IRIS Research Package', '/atlas/data-pack': 'ATLAS Data Pack', '/oy/data-pack': 'OY Data Pack', '/hermes/model/data-pack': 'MODEL Data Pack'}[_pg]) + _md_body(_md) + (_tested(_TESTED[_pg][1]) if _TESTED[_pg][1] else '') + (open(os.path.join(HERE, '..', 'darkwave_daily', 'fragment_tables.html'), encoding='utf-8').read() if _pg == '/darkwave/kit' else '') + '</main>')
        PAGES[_pg] = page(_pg, _ttl, _dsc, _body, hero_slim(_t, 'Heuremen LLC'))
        _place(_home, _box(_t, _pg, _txt, _z, tested=_TESTED[_pg][0]))
    if _sha('iris/iris-list-pack.zip') and '/iris/package' in PAGES:
        PAGES['/iris'] = PAGES['/iris'].replace('<a href="/iris/package">What is in it</a></p></aside>', '<a href="/iris/package">What is in it</a></p><p class="pkgalso">Also: <a href="/iris/iris-list-pack.zip" download>IRIS List Pack</a> (every study on the List, CSV and BibTeX)</p><p class="pkgalso">Checker alone: <code>pip install iris-check</code> (<a href="https://pypi.org/project/iris-check/">PyPI</a>)</p></aside>', 1)
    for _js, _pat in (('headline.js', r'/headline\.js\?v=[0-9a-f]{8}'), ('nav.js', r'/nav\.js\?v=[0-9a-f]{8}'), ('live-tags.js', r'/live-tags\.js\?v=[0-9a-f]{8}'), ('stack/live.js', r'/stack/live\.js\?v=[0-9a-f]{8}')):
        _hv = _hh.sha256(open(os.path.join(_pub, _js), 'rb').read()).hexdigest()[:8]
        for _pp in PAGES: PAGES[_pp] = _re.sub(_pat, '/' + _js + '?v=' + _hv, PAGES[_pp])
    for _pp in PAGES: PAGES[_pp] = PAGES[_pp].replace('@@CSSV@@', _cv)   # 9 Nov 2026 (site pass L14): the package pages are built after the first replace
    # 9 Nov 2026 (his word: "link the site to HF, that's kinda the point"): each page whose data or method has a dataset or model under
    # huggingface.co/indahl names it, at the foot of the page next to the code links.
    _HFD = 'https://huggingface.co/datasets/indahl/'
    _HF = {'/qia': ['qia-calibrated-studies', 'qia-run-data', 'readout-run-data', 'model:YO'], '/qia/list': ['qia-list'], '/qia/package': ['qia-calibrated-studies', 'qia-run-data'],
           '/darkwave': ['darkwave-run-data', 'readout-run-data'], '/darkwave/kit': ['darkwave-run-data'],
           '/iris': ['iris-list', 'iris-run-data', 'iris-judge-counts', 'iris-training-runs', 'iris-faults-guards-bench', 'faultsguards'], '/iris/list': ['iris-list'],
           '/iris/package': ['iris-list', 'faultsguards'], '/iris/lab': ['iris-training-runs', 'iris-faults-guards-bench', 'iris-house-training'], '/yo': ['model:YO'],
           '/atlas': ['atlas-datacenters', 'atlas-data-pack'], '/atlas/data-pack': ['atlas-data-pack'], '/oy': ['oy-schools', 'oy-data-pack'], '/oy/data-pack': ['oy-data-pack'],
           '/hermes/model': ['model-data-pack'], '/hermes/model/data-pack': ['model-data-pack']}
    for _pp, _rs in _HF.items():
        if _pp not in PAGES or '</main>' not in PAGES[_pp]: continue
        _ln = '<p class="meta">Data on Hugging Face: ' + ' &middot; '.join((f'<a href="https://huggingface.co/indahl/{r[6:]}">indahl/{r[6:]}</a> (model)' if r.startswith('model:') else f'<a href="{_HFD}{r}">indahl/{r}</a>') for r in _rs) + '.</p>'
        _i = PAGES[_pp].rfind('</main>'); PAGES[_pp] = PAGES[_pp][:_i] + _ln + PAGES[_pp][_i:]
    # 10 Nov 2026 (Wayfinder: "a data pack at the top right of every page"): every page with data carries a small Data pack link at the top
    # right of its heading band. Desk pages link their own pack (tools/desk_pack.py, built and checked against the live feed), division pages and
    # their sub-pages link the division pack, SOCIAL links the SOCIAL pack. Pages without data (policies, API, forms, the menu) get none.
    # A link is placed only when its zip and .sha256 are in public/, so a page never points at a pack that is not served.
    def _dpk_for(p):
        if p in ('/qia/list',) or p.startswith('/qia/study/'): return 'qia/qia-list-pack.zip', 'QIA List Pack'
        if p in ('/iris/list',) or p.startswith('/iris/study/'): return 'iris/iris-list-pack.zip', 'IRIS List Pack'
        if p == '/qia' or p.startswith('/qia/'): return 'qia/qia-research-package.zip', 'QIA Research Package'
        if p in ('/iris', '/yo') or p.startswith('/iris/'): return 'iris/iris-research-package.zip', 'IRIS Research Package'
        if p == '/atlas' or p.startswith('/atlas/'): return 'atlas/atlas-data-pack.zip', 'ATLAS Data Pack'
        if p == '/oy' or p.startswith('/oy/'): return 'oy/oy-data-pack.zip', 'OY Data Pack'
        if p == '/hermes/model' or p.startswith('/hermes/model/'): return 'hermes/model-data-pack.zip', 'MODEL Data Pack'
        if p == '/darkwave' or p.startswith('/darkwave/'): return 'darkwave/darkwave-correction-kit.zip', 'Darkwave Correction Kit'
        if p == '/census/revisions': return 'census/census-data-pack.zip', 'CENSUS Data Pack'
        s = p.strip('/')
        if s and '/' not in s: return f'{s}/{s}-data-pack.zip', s.upper() + ' Data Pack'
        return None
    _DPK_NONE = {'/', '/agree', '/contact', '/inquiry', '/privacy', '/terms', '/conflict-of-interest', '/media', '/community', '/changes', '/vault', '/security',
                 '/inquire-ok', '/inquire-error', '/404', '/api', '/correction', '/respond', '/now', '/hermes', '/request'}
    for _pp in list(PAGES):
        if _pp in _DPK_NONE or _pp.startswith('/media/'): continue
        _d = _dpk_for(_pp)
        if not _d or not _sha(_d[0]): continue
        _a = (f'<a class="dpk" href="/{_d[0]}" download aria-label="Data pack: download the {_d[1]} (zip)" title="{_d[1]} (zip)">'
              '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1v9M4 6.5 8 10.5 12 6.5M2 14h12" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>Data pack</a>')
        pass   # 13 Nov 2026 (Wayfinder): no per-page Data pack button; every pack is in the GRAB AND GO menu in the header and on /downloads
    # 10 Nov 2026 (Wayfinder): on each division page, where the division pack sits, a "grab and go" list of every pack in that division: the
    # division pack first, then one line per desk with its zip and size. Same no-script dropdown as the banner (.dd/.ddpanel, hover or focus).
    # Sizes come from tools/desk_packs/pack_sizes.json (tools/desk_pack.py sizes), the file the ledger rows pack.size.* cite.
    try: _PS = _jsonld.load(open(os.path.join(HERE, '..', 'tools', 'desk_packs', 'pack_sizes.json')))
    except Exception: _PS = {}
    def _ggline(name, label, z, note=''):
        if z not in _PS: return ''
        r = _PS[z]; ro = ' <span class="ggr">Results only: our counts, outcomes and intervals, no source data</span>' if r['licence'] == 'results' else ''
        return (f'<li><a href="/{z}" download>{name}</a> <span class="ggw">{label}</span> <span class="ggs">' + (note or r['size']) + f'</span>{ro}</li>')
    _DIVPK = {'/atlas': 'atlas/atlas-data-pack.zip', '/iris': 'iris/iris-research-package.zip', '/oy': 'oy/oy-data-pack.zip', '/qia': 'qia/qia-research-package.zip',
              '/hermes': 'hermes/model-data-pack.zip', '/social': 'social/social-data-pack.zip'}
    _SECT = [('DSA', 'EU moderation reports against the DSA Transparency Database', ''), ('AD SPEND', "Google's political ad library against FEC filings", 'results'),
             ('TIKTOK', "TikTok's quarterly report against its EU filings", 'results'), ('BLUESKY', "Bluesky's transparency report against its signed label stream", 'results')]
    _GRAB = []
    for _dv, _top in _DIVPK.items():
        if _dv not in PAGES: continue
        _li = []
        if _dv == '/hermes': _li.append('')   # HERMES is the menu: no division pack, the list holds every HERMES desk
        else:
            _t = _PS.get(_top)
            if not _t: continue
            _li.append(f'<li class="ggall"><a href="/{_top}" download>All of {_DNAME.get(_dv, _dv.strip("/").upper())}</a> <span class="ggw">{_t["title"]}</span> <span class="ggs">{_t["size"]}</span></li>')
        if _dv == '/qia': _li.append(_ggline('QIA LIST', 'Every study on the QIA List', 'qia/qia-list-pack.zip'))
        if _dv == '/iris': _li.append(_ggline('IRIS LIST', 'Every study on the IRIS List', 'iris/iris-list-pack.zip'))
        if _dv == '/social':
            for _n, _w, _l in _SECT:
                _li.append(f'<li><a href="/{_top}" download>{_n}</a> <span class="ggw">{_w}</span> <span class="ggs">in the SOCIAL pack</span>' + (' <span class="ggr">Results only: our counts, outcomes and intervals, no source data</span>' if _l else '') + '</li>')
        for _h, _n, _w in DESKS.get(_dv, []):
            if _h not in PAGES or _h == '/vault': continue
            _d = _dpk_for(_h)
            if not _d or _d[0] not in _PS: continue
            _li.append(_ggline(_n, _w, _d[0], '' if _d[0].endswith(_h.strip('/') + '-data-pack.zip') or _h in ('/hermes/model', '/social') else 'in the ' + _PS[_d[0]]['title']))
        _li = [x for x in _li if x]
        if not _li: continue
        _gid = 'gg-' + _dv.strip('/')
        _box = (f'<div class="gg"><span class="dd ggdd"><button type="button" class="ggbtn" aria-haspopup="true" aria-controls="{_gid}">Grab and go</button>'
                f'<span class="ddpanel ggpanel" id="{_gid}"><span class="ggnote">Every pack in {_DNAME.get(_dv, _dv.strip("/").upper())}, each a zip with its README, sources and tests.</span><ul>' + ''.join(_li) + '</ul></span></span></div>')
        # 10 Nov 2026 (Zenodo packs): the Zenodo record that holds this division's desk packs, cited under the list
        _zr = {'/hermes': 'HERMES Desk Packs', '/iris': 'IRIS Desk Packs', '/social': 'SOCIAL Data Pack', '/atlas': 'ATLAS Desk Packs', '/oy': 'OY Desk Packs'}.get(_dv)   # 10 Nov evening: ATLAS and OY desk records
        if _zr and _cite(_zr): _box += _cite(_zr).replace('Cite: ', ('Desk packs on Zenodo: ' if _dv != '/social' else 'Cite: '), 1)
        _doc = PAGES[_dv]; _hd = f'<a class="pkghead" href="{ {"/atlas": "/atlas/data-pack", "/iris": "/iris/package", "/oy": "/oy/data-pack", "/qia": "/qia/package"}.get(_dv, "") }">'
        # 13 Nov 2026 (Wayfinder): the package box is gone; every pack is in the GRAB AND GO menu and on /downloads
        PAGES[_dv] = _pr.sub(r'<aside class="pkgbox[^"]*">.*?</aside>', '', _doc, flags=_pr.S)
        if _zr and _cite(_zr):   # each division page still cites its Zenodo record (ledger rows zenodo.*_desks.concept, zenodo.social.concept)
            _m = '<main class="wrap">' + _hlslot(_dv); _m = _m if _m in PAGES[_dv] else '<main class="wrap">'
            PAGES[_dv] = PAGES[_dv].replace(_m, _m + _cite(_zr).replace('Cite: ', ('Desk packs on Zenodo: ' if _dv != '/social' else 'Cite: '), 1), 1)
        if _zr and _cite(_zr): _li.append('<li class="ggnote">' + _cite(_zr)[len('<p class="pkgalso">'):-len('</p>')] + '</li>')
        _GRAB.append((_dv, _DNAME.get(_dv, _dv.strip('/').upper()), _li, {'/atlas': '/atlas/data-pack', '/iris': '/iris/package', '/oy': '/oy/data-pack', '/qia': '/qia/package'}.get(_dv)))
    # 13 Nov 2026 (Wayfinder): GRAB AND GO, one page with every pack, division by division (the header menu links here)
    _gb = ''.join(f'<h2>{_n}</h2><ul class="desklist">' + ''.join(_l) + (f'<li><a href="{_w}">What is in each pack</a></li>' if _w else '') + '</ul>' for _d0, _n, _l, _w in _GRAB)
    PAGES['/downloads'] = page('/downloads', 'Grab and Go: Every Data Pack | Heuremen LLC', 'Every Heuremen LLC data pack and research package, division by division, each a zip with its README, sources and tests.',
                               '<section class="legal grab">' + _gb + '<h2>Claude Code plugins</h2><ul class="desklist"><li><a href="/plugins">Standards check, readcheck gate and QIA calibration check</a> <span class="ggw">install inside Claude Code</span></li></ul></section>', hero_slim('GRAB AND GO'))
    # 13 Nov 2026 (Wayfinder: "full dicks on the plugins"): the Claude Code plugins, from github.com/Heuremen-LLC/indahl.ai (claude-plugins/; 13 Nov: the separate repo was a mistake, now private)
    # 13 Nov 2026 (Wayfinder: "make sure all the paths to all our connectors are prominent on our site"): CONNECT, built from
    # claude-plugins/.claude-plugin/marketplace.json and the GROUPS in api.js, so a new plugin or connector group shows up on the next build.
    _cr = '<section class="legal"><p>Every way to use our measurements and checks from Claude, Claude Code or any MCP client. Everything is free, read-only where it touches our data, and the code is public in <a href="https://github.com/Heuremen-LLC/indahl.ai">github.com/Heuremen-LLC/indahl.ai</a>.</p>'
    _cr += ('<h2>Connectors (MCP servers)</h2><p>Remote MCP servers over HTTP, no key, nothing to install. In Claude: Settings, Connectors, Add custom connector, and paste the address. In Claude Code: <code>claude mcp add --transport http indahl &lt;address&gt;</code>.</p>'
            '<table class="mtx"><thead><tr><th>Address</th><th>What it holds</th></tr></thead><tbody>'
            '<tr><td><code>https://indahl.ai/mcp</code></td><td>Every tool over every live desk. Tool list on the <a href="/api">API page</a>.</td></tr>'
            + ''.join('<tr><td><code>https://indahl.ai/mcp/' + _g + '</code></td><td>' + _chtml.escape(_t) + '. ' + _chtml.escape(_nt) + '</td></tr>' for _g, _t, _nt in _MCPG)
            + '</tbody></table><p>The same tools as plain JSON: <a href="/api/v1">/api/v1</a>, with the OpenAPI description at <a href="/api/openapi.json">/api/openapi.json</a>.</p>')
    _cr += ('<h2>Claude Code plugins and skills</h2><p>Add the marketplace once, then install what you want, or everything with <code>indahl-full</code>.</p>'
            '<pre><code>/plugin marketplace add Heuremen-LLC/indahl.ai\n/plugin install indahl-full@heuremen</code></pre>'
            '<table class="mtx"><thead><tr><th>Install</th><th>What it does</th></tr></thead><tbody>'
            + ''.join('<tr><td><code>' + _x['name'] + '@heuremen</code></td><td>' + _chtml.escape(_x.get('description', '').replace('; ', ', ')) + '</td></tr>' for _x in _MKT if _x['name'] != 'indahl')
            + '</tbody></table><p>Details for the checks with scripts are on <a href="/plugins">Plugins</a>. Source and READMEs: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins">claude-plugins</a> in the public repository, mirrored at <a href="https://github.com/Heuremen-LLC/claude-plugins">github.com/Heuremen-LLC/claude-plugins</a>.</p>')
    _cr += ('<h2>Data and packs</h2><ul class="desklist"><li><a href="/downloads">Grab and Go</a> <span class="ggw">every data pack and research package</span></li>'
            '<li><a href="https://huggingface.co/indahl">Hugging Face</a> <span class="ggw">datasets and models</span></li>'
            '<li><code>pip install qia-check</code> <span class="ggw">the QIA calibration record checker</span></li></ul>'
            '<p>Terms: retrieval and answering with attribution, no use as training data (<a href="/terms#ai-training">terms</a>).</p></section>')
    PAGES['/connect'] = page('/connect', 'Connect: Claude Connectors, Plugins and Skills | Heuremen LLC', 'Every way to use Heuremen LLC measurements and checks from Claude, Claude Code or any MCP client: the indahl.ai MCP connectors, the Claude Code plugin marketplace and the skills.', _cr, hero_slim('CONNECT'))
    _FEED.append(('/connect', 'Connect: Claude connectors, plugins and skills', 'Every indahl.ai MCP connector address and every Claude Code plugin and skill, in one place.'))
    # 13 Nov 2026 (Wayfinder: "do it all"): HOW, the practice behind the skills, each linked to the free skill that runs it. Refereed by Sage before release.
    _HOWS = [('Before the run', [('controls', 'A test that cannot fail tells you nothing when it passes. Check the controls before the run, while it is cheap.'),
                                 ('margin', 'A prediction that breaks when one input moves by less than that input&rsquo;s own uncertainty is not a prediction yet. Find the margin first.'),
                                 ('prereg', 'Seal the plan in git, and read from the git host&rsquo;s own push record whether it came before the first run you supply.')]),
             ('Reading the result', [('cannot-tell', 'A guess dressed as an answer costs more than a plain &ldquo;not yet&rdquo;. Four outcomes, never two: above, below, consistent, cannot tell.'),
                                     ('both', 'Most bad conclusions come from a second explanation dropped too early. Keep two readings open until the evidence separates them.'),
                                     ('triangulate', 'One reading is a perspective. Two give a difference. Three independent readings, run blind, show where they agree and where they split. Agreement is not proof.')]),
             ('Before it goes out', [('outside-ruler', 'The person who made the work cannot be its only check. A referee gets the raw material, not the summary.'),
                                     ('number-check', 'Every number read back against where it came from.'),
                                     ('quote-check', 'A paraphrase inside quotation marks is a misquote, however close.'),
                                     ('source-check', 'Each citation opened and read for whether it says what the text says it says.'),
                                     ('clause', 'The sentences that claim more than the comparison behind them, found before a reviewer finds them.')]),
             ('After it goes out', [('trust-but-verify', 'Quiet is not success. After any push, deploy, sync or job, the effect is read back from where it should have landed, not from the exit code or an &ldquo;ok&rdquo; line.'),
                                    ('correct', 'A correction goes beside the original, with who caught it and when. Ours are on the <a href="/corrections">Corrections</a> page.'),
                                    ('readcheck', 'The skill refuses to write a reading without its check block. The commit gate that enforces it ships in the version from our own marketplace, not in the directory copy.')]),
             ('Big jobs', [('batch', 'Work too large for one context window is split into batches, each done by a fresh worker against the same written checks.')]),
             ('Checking other people&rsquo;s claims', [('standards', 'A paper or claim checked against the <a href="/standard">Standards</a> claim codes, with quotes and four-state statuses.'),
                                                       ('eval-check', 'A language-model evaluation claim, or your own eval run, checked against the house eval checks.')])]
    _hw = ('<section class="legal"><p>These are the checks we hold our results to. Each one is also a free skill for Claude Code, so anyone can run it on their own work. Several were written after a mistake of ours. Our corrections are listed on the <a href="/corrections">Corrections</a> page.</p>'
           '<pre><code>/plugin marketplace add Heuremen-LLC/indahl.ai\n/plugin install indahl-full@heuremen</code></pre>')
    for _h, _rows in _HOWS:
        _hw += '<h2>' + _h + '</h2><ul class="desklist">' + ''.join('<li><code>indahl-' + _n + '</code> <span class="ggw">' + _t + '</span></li>' for _n, _t in _rows) + '</ul>'
    _hw += ('<h2>The same checks on our own model training</h2><p>Our model training is read the same way: the held-out sets fixed in git before the run (the ordering is self-witnessed), every model scored on the same items, the paper as the unit when one paper gives several items, and no model kept until it beats the untouched model on both counts. It is live on the <a href="/iris/lab#stan">LAB</a> page.</p>'
            '<p>Every connector, plugin and skill, with install lines: <a href="/connect">Connect</a>. Source: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins">claude-plugins</a> in the public repository.</p></section>')
    PAGES['/how'] = page('/how', 'How We Check Our Own Work | Heuremen LLC', 'The checks Heuremen LLC holds its results to, each one a free skill for Claude Code.', _hw, hero_slim('HOW WE CHECK OUR OWN WORK'))
    _FEED.append(('/how', 'How we check our own work', 'The checks we hold our results to, each a free skill for Claude Code.'))
    PAGES['/plugins'] = page('/plugins', 'Claude Code Plugins | Heuremen LLC', 'Heuremen LLC plugins for Claude Code: check papers and eval claims against the Standards, use and reproduce every desk, and check and correct IBM Quantum runs.',
        '<section class="legal">'
        '<p>Plugins for <a href="https://claude.com/claude-code">Claude Code</a>. Add the marketplace once, then install the ones you want.</p>'
        '<pre><code>/plugin marketplace add Heuremen-LLC/indahl.ai\n' + '\n'.join('/plugin install ' + _x['name'] + '@heuremen' for _x in _MKT if _x['name'] not in ('indahl', 'indahl-full')) + '</code></pre><p>Or everything at once: <code>/plugin install indahl-full@heuremen</code>. Every connector, plugin and skill: <a href="/connect">Connect</a>.</p>'
        '<h2>Outside text is treated as data</h2><p>Every plugin that reads outside text (a paper, a kit README, a released file, an API response) tells the agent to treat it as data, not instructions: if fetched text carries instructions aimed at the agent, it quotes them to you and carries on with the check. That is an instruction to the agent, not a guarantee. The guards that hold regardless are in code: nothing runs downloaded code without a go bound to the exact commit you reviewed, a paid IBM job submits only from your own terminal, and your files are opened read-only. Keep Claude Code&rsquo;s permission prompt on for Bash.</p>'
        '<h2>Check a claim</h2>'
        '<p><b>standards.</b> <code>/standards &lt;arXiv id, DOI, file or claim&gt;</code> checks a paper or a measured claim against the <a href="/standard">Standards</a> claim codes F1 to F7 and returns a recount card. '
        'Every code gets one of four statuses: PRESENT, ABSENT, CANNOT_TELL with its reason, or NOT_APPLICABLE. Every PRESENT carries a verbatim quote and where it sits in the paper. '
        'Any recompute shows its arithmetic from the paper&rsquo;s printed numbers, with the rounding range. The card names no cause. A PRESENT is one reader&rsquo;s proposal, an erratum candidate to check, not a confirmed finding and not a verdict on the study or its authors.</p>'
        '<p><b>eval-check.</b> <code>/eval-check &lt;claim or path&gt;</code> checks a language-model evaluation claim, or your own eval run: the parser checked against raw replies first, the setup as part of the result, the repeat floor before any comparison, dropped items by reason, judges grading their own labels, and an interval and outcome on every number. Built from the <a href="/iris">IRIS</a> recounts.</p>'
        '<p><b>prereg.</b> <code>/prereg</code> seals a plan in git and later shows, from your git host&rsquo;s own record of the push, whether the plan was pushed before the first run, and which files that ran the plan did not cover. No outside timestamp chain: the witness is the host&rsquo;s push record, never a commit date. BEFORE means before the first run in the record you supply; too-close-to-call reads CANNOT_TELL. It never pushes for you.</p>'
        '<p><b>readcheck.</b> A gate for research repositories. When Claude Code commits a reading (a results, outcomes or readings file), the commit is refused unless a complete check block, <code>CHECK.json</code>, sits beside it, with one answer for each of the Standards recount requirements REQ-01 to REQ-13. It checks that every answer is there, not that it is right, and it gates commits that Claude Code runs.</p>'
        '<h2>Use our data</h2>'
        '<p><b>indahl-data.</b> Every live desk inside Claude Code, through the read-only <a href="/mcp">indahl.ai MCP server</a>. <code>/indahl &lt;question&gt;</code> answers with the count, interval, outcome and the time it was read. With no question it prints every desk&rsquo;s headline test side by side. Questions are sent to indahl.ai. Answers are measurements of public data at the time read, not legal advice and not a verdict on any vendor, model, package or author.</p>'
        '<p><b>reproduce.</b> <code>/reproduce &lt;desk&gt;</code> fetches that desk&rsquo;s <a href="/reproduce">reproduce kit</a>, shows you the commit and the command, and on your go runs it with the desk&rsquo;s own code and checks its output against the published sha256. A match shows the kit reproduces its published output, not that the measurement is right.</p>'
        '<h2>Quantum runs</h2>'
        '<p><b>qia-calibration.</b> <code>/qia-check</code> runs the QIA calibration checker on IBM Quantum calibration records: before a run (stale figures, zero error values, T2 above 2 &times; T1, T1 and T2 measured apart) and after it (the record in force and what changed during the run). '
        'Flags come in two categories: T1 and T2, and error figures. Your files are opened read-only. <code>/qia-t1t2</code> goes one step further and measures T1 and T2 together on the qubits you choose, in one job on your own IBM Quantum account, and compares the ratio with IBM&rsquo;s published pair. The self-test needs no device, the estimate submits nothing, and the paid run starts only from your own terminal.</p>'
        '<p><b>darkwave-correction.</b> <code>/darkwave</code> runs the <a href="/darkwave">Darkwave Correction Kit</a>: it measures the phase turn on untouched qubits after a mid-circuit readout, on your own IBM Quantum account and runtime allotment, and adds the matching virtual-Z correction to your circuits. The self-test needs no account. A hardware job submits only when you run the command yourself in your own terminal. Tested on the simulator and once on ibm_kingston.</p>'
        '<p>Not affiliated with or endorsed by IBM. IBM Quantum and Qiskit are IBM marks, used only to name what the tools work with. The plugins are free to use under their licenses, which are not open-source licenses.</p>'
        '<p>Source, licenses and README: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins">github.com/Heuremen-LLC/indahl.ai, folder claude-plugins</a>.</p>'
        '</section>', hero_slim('CLAUDE CODE PLUGINS'))
    globals()['_PS'] = _PS; globals()['_dpk_for'] = _dpk_for   # the header menu (_navfor) reads these
    # 13 Nov 2026 (Wayfinder: "grab and go was supposed to be individualized for each desk"): each page's own downloads, in its title banner
    _GD = {d: l for d, n, l, w in _GRAB}; _GW = {d: w for d, n, l, w in _GRAB}
    for _pp in list(PAGES):
        if _pp in _DPK_NONE or _pp.startswith('/media/') or _pp == '/downloads': continue
        _doc = PAGES[_pp]; _items = []
        if _pp in _GD: _items = list(_GD[_pp]) + ([f'<li class="ggnote"><a href="{_GW[_pp]}">What is in each pack</a></li>'] if _GW.get(_pp) else [])
        if _pp == '/qia':   # 13 Nov 2026 (Wayfinder): QIA in the spotlight, the calibration pack first with the text of the former package box
            _qz = _PS.get('qia/qia-research-package.zip', {}).get('size', '')
            _items = [x for x in _items if 'All of QIA' not in x]
            _items.insert(0, '<li class="ggcal"><a href="/qia/qia-research-package.zip" download>QIA Calibration Pack</a> <span class="ggs">' + _qz + '</span>'
                '<span class="ggtxt">For runs on IBM quantum hardware, check the calibration record your run depends on, before the run and after it. The pack holds a record checker, '
                '<a href="/yo">YO</a> (our small language model, Qwen3-1.7B tuned with LoRA on IBM&rsquo;s calibration records to flag stale qubit data), the <a href="/standard">Standards</a>, and a same-job T1 and T2 check. '
                'Tested on real IBM records and a live run (<a href="/qia/package#tested">how</a>). Checker alone: <code>pip install qia-check</code>.</span></li>')
        else:
            _d = _dpk_for(_pp)
            if _d and _d[0] in _PS:
                _r = _PS[_d[0]]; _items.append(f'<li><a href="/{_d[0]}" download>{_r["title"]}</a> <span class="ggs">{_r["size"]}</span>' + (' <span class="ggr">Results only: our counts, outcomes and intervals, no source data</span>' if _r['licence'] == 'results' else '') + '</li>')
            _sl = _pp.strip('/')
            if _sl and '/' not in _sl:
                for _fn, _lab in ((f'{_sl}/{_sl}_outcomes.csv', 'Outcomes (CSV)'), (f'{_sl}/live.json', 'Live feed (JSON)'), (f'{_sl}/changes.xml', 'Changes to the headline (Atom)')):
                    if os.path.isfile(os.path.join(_pub, _fn)): _items.append(f'<li><a href="/{_fn}"' + (' download' if _fn.endswith('.csv') else '') + f'>{_lab}</a></li>')
                if os.path.isdir(os.path.join(HERE, '..', 'reproduce_kits', 'kits', _sl)): _items.append(f'<li><a href="/reproduce#kit-{_sl}">Reproduce kit</a> <span class="ggw">code, inputs and one command</span></li>')
        if _pp in ('/standard', '/qia', '/plugins', '/iris', '/darkwave', '/reproduce', '/mcp'):   # 13 Nov 2026: the Claude Code plugins in the banner menus they belong to
            _items.append('<li><a href="/plugins">Claude Code plugins</a> <span class="ggw">' + ({'/qia': 'QIA calibration check and Darkwave correction inside Claude Code', '/darkwave': 'the Darkwave Correction Kit inside Claude Code', '/iris': 'eval check inside Claude Code', '/reproduce': 'run any kit inside Claude Code', '/mcp': 'every desk inside Claude Code'}.get(_pp, 'Standards check, eval check and readcheck gate inside Claude Code')) + '</span></li>')
        if not _items: continue
        _gid = 'grab-' + (_pp.strip('/').replace('/', '-') or 'home')
        _dd = (f'<span class="dd dpkdd"><button type="button" class="dpk" aria-haspopup="true" aria-controls="{_gid}">'
               '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1v9M4 6.5 8 10.5 12 6.5M2 14h12" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>Grab and go</button>'
               f'<span class="ddpanel ggpanel" id="{_gid}"><ul>' + ''.join(_items) + '</ul></span></span>')
        _h = '<section class="hero slim"><div class="wrap">'
        if _h in _doc: PAGES[_pp] = _doc.replace(_h, _h + _dd, 1)
    # 10 Nov 2026 (Zenodo packs): each desk page whose pack is deposited on Zenodo says where, under the page, from ledger/zenodo_dois.json.
    # 10 Nov evening: the ATLAS version that holds the ATLAS desks is published (10.5281/zenodo.24110654), so those desks say their data is inside it.
    try: _ZD = _jsonld.load(open(os.path.join(HERE, '..', 'ledger', 'zenodo_dois.json')))['desks']
    except Exception: _ZD = {}
    for _zs, _ze in _ZD.items():
        _zp = '/' + _zs
        if _zs == 'social' or _zp not in PAGES or not _ze.get('concept_doi') or _ze.get('record') is None or '</main>' not in PAGES[_zp]: continue   # SOCIAL cites in its pack box
        _zl = (f'<p class="pkgalso">Data pack on Zenodo: <a href="https://doi.org/{_ze["concept_doi"]}">doi:{_ze["concept_doi"]}</a>'
               + ('' if _ze['record'] == _zs.upper() + ' Data Pack' else (', inside the ATLAS Data Pack' if _ze['record'] == 'ATLAS Data Pack' else f', one file of the {_ze["record"]} record')) + '</p>')
        _zi = PAGES[_zp].rindex('</main>'); PAGES[_zp] = PAGES[_zp][:_zi] + _zl + PAGES[_zp][_zi:]
    # 10 Nov 2026 (findable pass, findable.py): the banner is filled here for every page, package pages included (they were built after the old
    # fill and shipped an empty banner). Then the data links and embed box, the page dates, the share cards, Dataset JSON-LD and the change feeds.
    _wk.apply(PAGES, page, hero_slim, DESKS)   # 10 Nov 2026: /week and every past week
    # 10 Nov 2026 (brand pages): /brand and /brand/<slug>, every desk row about one organisation, built in brands.py (its own module and gate).
    import brands as _brd; _bb = _brd.add_pages(PAGES, page, hero_slim, HOME, desks=DESKS); [PAGES.__setitem__(_p, PAGES[_p].replace('@@CSSV@@', _cv)) for _p in PAGES if _p.startswith('/brand') or _p.startswith('/e/')]   # 10 Nov evening: and the entity index and pages (entities.py)
    # 10 Nov 2026 (outcome alerts): the desks and organisations that can send alerts, and /alerts with the one sign-up form (alerts.py)
    _fcs.add_pages(PAGES, page, hero_slim, HOME); PAGES['/forecasters'] = PAGES['/forecasters'].replace('@@CSSV@@', _cv)   # 10 Nov 2026: /forecasters, and a link to it on each member desk
    _alr.apply(PAGES, page, hero_slim, HOME, _bb, _jsonld.load(open(_brd.ROWS))['rows'], desks=DESKS); PAGES['/alerts'] = PAGES['/alerts'].replace('@@CSSV@@', _cv)
    _ntf.apply(PAGES, page, hero_slim, HOME, _cv, _FEED)   # 10 Nov 2026: follow page, webhooks, changelog, the device button and the footer Follow link (notify.py)
    import accountability as _acc; _acc.apply(PAGES, page, hero_slim, HOME, _cv)   # 10 Nov 2026: /verify, /reproduce, /transparency, /security/self, /security/policy, /security/thanks, /mydata (accountability.py, security.js)
    import reproduce_kits as _rk; _rk.apply(PAGES)   # 10 Nov 2026: the per-desk reproduce table on /reproduce and a Reproduce this number link on each desk page (reproduce_kits.py)
    _alr.footer(PAGES)   # 10 Nov 2026 (owner's word): ONE sign-up form in every footer, newsletter, new desks and new data, every desk, and this desk or organisation
    for _pp in PAGES: PAGES[_pp] = _re.sub(r'@@NAV:[^@]*@@', lambda _m, _pp=_pp: _navfor(_pp), PAGES[_pp])
    import findable as _fd
    _packs = _fd.packs(PAGES, DESKS)
    _fd.version_zips(PAGES)
    _fdi = _fd.apply_main(PAGES, DESKS, _packs)
    _lm = _page_dates(PAGES)
    _fd.apply_head(PAGES, DESKS, _lm, _fdi, _packs)
    _bad = [(p, e) for p, d in PAGES.items() for e in _fd.check_doc(d)]
    if _bad: raise SystemExit('BUILD REFUSED: JSON-LD: ' + '; '.join('%s %s' % x for x in _bad[:8]))
    print('findable: %d desk pages with data links or embed, %d change feeds' % (len(_fdi), _fd.write_changes()))
    # 10 Nov 2026 ("receipts available to anyone"): every number with a live ledger row gets a small receipt link to /r/<row>, placed right after
    # the snippet the ledger matches on that page (ledger/receipts.py). check_ledger strips these links, so they never change what a snippet reads.
    _sys.path.insert(0, os.path.join(HERE, '..', 'ledger')); import receipts as _rcp
    _rcp.link_pages(PAGES)
    # 11 Nov 2026 night (owner: "let's go back to just desk follows"): the end-of-page entity Index is off; bell_gate checks no page carries one
    # import entities as _ent; _ent.bell_pass(PAGES)   # 10 Nov 2026 evening: Follow beside the names of companies and other named things, last, on final pages (entities.py; its gate proves nothing else moved)
    for path, doc in PAGES.items():
        name = 'index.html' if path == '/' else path.strip('/') + '.html'
        os.makedirs(os.path.dirname(os.path.join(HERE, name)), exist_ok=True)
        open(os.path.join(HERE, name), 'w', encoding='utf-8').write(doc); names[path] = name
    open(os.path.join(HERE, 'model_all.html'), 'w', encoding='utf-8').write('\n'.join(doc for pth, doc in PAGES.items() if pth == '/hermes/model' or pth.startswith('/hermes/model/')))   # 28 Oct: the ledger surface for SAD (every SAD page in one file, never served)
    open(os.path.join(HERE, 'style.css'), 'w').write(CSS)
    open(os.path.join(HERE, 'gate-ui.txt'), 'w', encoding='utf-8').write(GATE_JS)
    imports = '\n'.join(f"import P{i} from './{n}';" for i, n in enumerate(names.values()))
    table = ',\n'.join(f"  '{p}': P{i}" for i, p in enumerate(names))
    # 9 Nov 2026 (site pass M10): llms.txt is built here from the division and desk lists (DESKS), so it names every live desk, and the worker
    # serves the LLMS string from pages.js. The fixed sections below are the ones the worker used to carry, with "every live desk" for the tools.
    import html as _lh
    _ll = ['# Heuremen LLC', '',
           "> Heuremen LLC measures published claims against the data behind them. Quantum hardware studies are recounted against IBM's published calibration (QIA). "
           "Language-model evaluation studies are recounted from their own released files (IRIS). University AI policy documents are indexed against their own published numbers (OY). "
           "Built infrastructure is mapped from public data, with a source for every dot (ATLAS). Vendor statements about AI hardware are held against published MLPerf® results "
           "(the MODEL desk of HERMES). Every live desk is listed below with one line. Every row has a source. Data downloads are free.", '',
           '## Recount record and verification',
           '- [RECORD](https://indahl.ai/record): every published claim we recounted, with fault codes and the finding, and every public number of ours corrected after it went out. Open benchmark and hardware verification with receipts.',
           '- [Corrections](https://indahl.ai/corrections): each catch and fix, with what was wrong, what it is now and who caught it.',
           '- [Key](https://indahl.ai/qia/key): the claim-level fault codes F1 to F7 used in every recount.',
           '- [STANDARDS](https://indahl.ai/standard): an open standard for checking measurement claims, with a conformance checklist, a NIST AI RMF crosswalk and a JSON version. DOI 10.5281/zenodo.24164029 (all versions).', '',
           '## API and MCP',
           '- [MCP server](https://indahl.ai/mcp): read-only tools over every live desk, for Claude and other agents. Add it as a remote MCP server at https://indahl.ai/mcp.',
           '- [REST API](https://indahl.ai/api): the same tools as JSON at /api/v1, with an OpenAPI file at /api/openapi.json. Retrieval and answering are permitted, training is not.', '',
           '## Divisions',
           '- [QIA](https://indahl.ai/qia): IBM processors measured against their published calibration, the studies calibrated, and the List of every indexed study with its receipt.',
           '- [IRIS](https://indahl.ai/iris): Recount Matrix for language models, live Standards runs on open models, and the List of indexed evaluation studies.',
           '- [OY](https://indahl.ai/oy): A HERMES desk. Learning research, school AI policy and data, recounted with a source per row.',
           '- [ATLAS](https://indahl.ai/atlas): Built infrastructure. A map of United States data centers from OpenStreetMap and Epoch AI, with a source and pull date for every dot.',
           '- [HERMES](https://indahl.ai/hermes): Held Every Record, Measured Every Statement. The menu of every division and desk.',
           '- [STACK](https://indahl.ai/stack): Every test side by side, live.', '',
           '## Desks']
    for _dv in ('/qia', '/iris', '/oy', '/atlas', '/hermes'):
        _dd = [x for x in DESKS.get(_dv, []) if x[0] in PAGES]
        if not _dd: continue
        _ll.append('### ' + _DNAME.get(_dv, _dv.strip('/').upper()))
        _ll += ['- [%s](https://indahl.ai%s): %s.' % (_lh.unescape(n), h, _lh.unescape(w).rstrip('.')) for h, n, w in _dd]
    _ll += ['', '## Data', '- [Feed of new studies and bench rounds (Atom)](https://indahl.ai/feed.xml)', '- [QIA List (JSON)](https://indahl.ai/qia/list.json)', '- [IRIS List (JSON)](https://indahl.ai/iris/list.json)',
            '- [MODEL claims (JSON)](https://indahl.ai/hermes/model/claims.json) and [per-accelerator results (CSV)](https://indahl.ai/hermes/model/accelerators.csv)', '- [Datasets on Hugging Face](https://huggingface.co/indahl)',
            '- [QIA key (codes Q1 to Q23, F1 to F7)](https://indahl.ai/qia/key)', '- [IRIS key (codes L1 to L9)](https://indahl.ai/iris/key)', '',
            '## Free downloads (each tested, with a TESTED.md inside)',
            '- [QIA Research Package](https://indahl.ai/qia/package): for runs on IBM quantum hardware. Checks the calibration record a run depends on, before and after the run. The checker alone: pip install qia-check (https://pypi.org/project/qia-check/).',
            '- [Darkwave Correction Kit](https://indahl.ai/darkwave/kit): measures the phase turn a mid-circuit readout gives untouched qubits on your own IBM account and adds the matching virtual-Z correction. Tested on ibm_kingston.',
            '- [IRIS Research Package](https://indahl.ai/iris/package): for language-model evaluations. Reading sheets for parsers, flip counts between repeated runs, paired comparisons with four outcomes. The checker alone: pip install iris-check (https://pypi.org/project/iris-check/).',
            '- [ATLAS Data Pack](https://indahl.ai/atlas/data-pack): every ATLAS dataset as JSON, CSV and GeoJSON with sources.',
            '- [QIA List Pack](https://indahl.ai/qia/qia-list-pack.zip) and [IRIS List Pack](https://indahl.ai/iris/iris-list-pack.zip): every listed study as CSV, BibTeX and RIS.', '',
            '## Research', '- [A Readout Is Not an Idle (paper, PDF)](https://heuremen.org/a-readout-is-not-an-idle.pdf)', '- [Faults (PDF)](https://heuremen.org/faults.pdf) and [Guards (PDF)](https://heuremen.org/guards.pdf)',
            '- [Zenodo record](https://doi.org/10.5281/zenodo.23662284)', '- [heuremen.org](https://heuremen.org/)', '',
            '## Usage', '- Free to read, download and cite with attribution. Text and data mining and use as AI training data are not permitted: https://indahl.ai/terms#ai-training', '',
            '## Policies', '- [Privacy](https://indahl.ai/privacy), [Terms](https://indahl.ai/terms), [Security](https://indahl.ai/security), [Conflict of interest](https://indahl.ai/conflict-of-interest)', '']
    _llms = '\n'.join(_ll)
    open(os.path.join(HERE, 'pages.js'), 'w').write(
        "// GENERATED by build_site.py -- do not edit. The indahl.ai pages the worker serves.\n" + imports +
        "\nimport FEED_STATIC from './feed-entries.html';\nimport GATE_UI from './gate-ui.txt';\nimport CSS from './style.css';\nexport const PAGES = {\n" + table + "\n};\nexport const STYLE = CSS;\nexport const GATE_JS = GATE_UI;\nexport const FEED = FEED_STATIC;\nexport const NDA = { version: '" + NDA_VERSION + "' };\nexport const PRIVACY = { version: '" + PRIVACY_VERSION + "' };\nexport const BUILT = '" + __import__('datetime').date.today().isoformat() + "';\nexport const LASTMOD = " + __import__('json').dumps(_lm, separators=(',', ':')) + ";\nexport const OY_FILES = {};  // kids files held 25 Oct\nexport const LLMS = " + __import__('json').dumps(_llms) + ";\n")
    import html as _hf
    _SPC, _COL, _ROOT = ' : ', ': ', '/'   # 11 Nov: no same-quote string inside an f-string, so /usr/bin/python3 (3.9, the auto-ship path) can parse this file
    _fe = ''.join(f'<entry><id>tag:indahl.ai,2026:{_hf.escape(p)}</id><title>{_hf.escape(t.replace(_SPC, _COL))}</title><link href="https://indahl.ai{_hf.escape(p)}"/><updated>{_lm.get(p) or _lm.get(_ROOT)}</updated><summary>{_hf.escape(d)}</summary></entry>' for p, t, d in _FEED)
    open(os.path.join(HERE, 'feed-entries.html'), 'w', encoding='utf-8').write(_fe)
    print('built', len(names), 'pages + style.css + pages.js')

if __name__ == '__main__':
    main()

