#!/usr/bin/env python3
"""newsletter_pages.py (10 Nov 2026): the newsletter on the web, /newsletter (every issue) and /newsletter/<N> (one issue).

Each issue is one Markdown file, ~/bones-forge/newsletter/issue_<N>.md, written by hand. The same file is the email edition:
newsletter_send.py --edition newsletter/issue_<N>.md sends text() and email_html() of it. Nothing else is read.

The Markdown is the small set the issues use: '# ' title (first line), '## ' section heading, '- ' list item, '**bold**', blank-line paragraphs.
indahl.ai/<path> becomes a link. A bare indahl.ai stays text. The second paragraph (date and byline) is set as the issue's meta line.

  build_site.py calls build(PAGES, page, hero_slim) once per build.
  newsletter_pages.py text N | html N | selftest
Python 3.9, standard library only."""
import os, re, sys, html, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISSUES = os.path.join(ROOT, 'newsletter')
SITE = 'https://indahl.ai'
e = lambda s: html.escape(str(s), quote=True)


def issues():
    """[(N, path)] of every issue file, newest first."""
    out = []
    for p in glob.glob(os.path.join(ISSUES, 'issue_*.md')):
        m = re.match(r'issue_(\d+)\.md$', os.path.basename(p))
        if m: out.append((int(m.group(1)), p))
    return sorted(out, reverse=True)


def number_of(path):
    m = re.search(r'issue_(\d+)\.md$', path); return int(m.group(1)) if m else None


def parse(md):
    """(title, meta, blocks) where a block is ('h', text) | ('p', text) | ('ul', [text])."""
    lines = md.replace('\r\n', '\n').strip().split('\n'); title = ''
    if lines and lines[0].startswith('# '): title = lines[0][2:].strip(); lines = lines[1:]
    blocks = []
    for raw in re.split(r'\n\s*\n', '\n'.join(lines).strip()):
        b = raw.strip('\n')
        if not b.strip(): continue
        if b.startswith('## '): blocks.append(('h', b[3:].strip()))
        elif all(l.startswith('- ') for l in b.split('\n')): blocks.append(('ul', [l[2:].strip() for l in b.split('\n')]))
        else: blocks.append(('p', ' '.join(l.strip() for l in b.split('\n'))))
    meta = ''
    if blocks and blocks[0][0] == 'p': meta = blocks.pop(0)[1]
    return title, meta, blocks


LINK = re.compile(r'\bindahl\.ai(/[A-Za-z0-9_\-/]*(?:#[A-Za-z0-9_\-]+)?)')   # a bare indahl.ai in a sentence stays text


def inline(t, absolute=False):
    s = e(t)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return LINK.sub(lambda m: '<a href="%s">indahl.ai%s</a>' % ((SITE if absolute else '') + (m.group(1) or '/'), m.group(1)), s)


def body_html(blocks, absolute=False):
    o = []
    for k, v in blocks:
        if k == 'h': o.append('<h2>%s</h2>' % inline(v, absolute))
        elif k == 'ul': o.append('<ul>' + ''.join('<li>%s</li>' % inline(x, absolute) for x in v) + '</ul>')
        else: o.append('<p>%s</p>' % inline(v, absolute))
    return ''.join(o)


def text(md, n=None):
    """The plain-text email edition: links written out in full, the web address of the issue at the top."""
    title, meta, blocks = parse(md); L = [title, meta, '']
    if n is not None: L += ['On the web: %s/newsletter/%d' % (SITE, n), '']
    plain = lambda t: LINK.sub(lambda m: SITE + (m.group(1) or '/'), re.sub(r'\*\*(.+?)\*\*', r'\1', t))
    for k, v in blocks:
        if k == 'h': L += [plain(v), '']
        elif k == 'ul': L += ['- ' + plain(x) for x in v] + ['']
        else: L += [plain(v), '']
    return '\n'.join(L).rstrip() + '\n'


def email_html(md, n=None):
    """The HTML part of the email (newsletter_send.py adds the footer and the unsubscribe link)."""
    title, meta, blocks = parse(md)
    web = ('<p style="font-size:14px;color:#555"><a href="%s/newsletter/%d">On the web</a></p>' % (SITE, n)) if n is not None else ''
    return '<h1 style="font-size:24px">%s</h1><p style="font-style:italic;color:#555">%s</p>%s%s' % (inline(title, True), inline(meta, True), web, body_html(blocks, True))


CSS = """
.nlissue h2{font-size:22px;margin:1.3em 0 .4em}.nlissue p,.nlissue li{font-size:17px;line-height:1.6}.nlissue ul{padding-left:20px}.nlissue .meta{font-size:15px}
.nlnav{margin-top:1.6em;font-size:15px}.nlnav a{margin-right:16px}.nllist{padding-left:18px}.nllist li{margin:8px 0;line-height:1.5}
"""


def build(PAGES, page, hero_slim):
    """/newsletter/<N> for every issue file, and /newsletter listing them. Returns the issue numbers built."""
    built = []; items = []
    for n, p in issues():
        title, meta, blocks = parse(open(p, encoding='utf-8').read())
        lead = next((v for k, v in blocks if k == 'p'), '')
        desc = 'Issue %d of the Heuremen LLC weekly newsletter. %s' % (n, re.sub(r'\*\*', '', lead))[:300]
        nav = '<p class="nlnav"><a href="/newsletter">Every issue</a><a href="/week">Weekly changes</a><a href="/corrections">Corrections</a></p>'
        b = '<section class="legal nlissue"><p class="meta">%s</p>%s%s</section>' % (inline(meta), body_html(blocks), nav)
        PAGES['/newsletter/%d' % n] = page('/newsletter/%d' % n, '%s | Heuremen LLC' % title, desc, b, hero_slim(e(title)))
        items.append('<li><a href="/newsletter/%d">%s</a>. %s</li>' % (n, e(title), inline(meta)))
        built.append(n)
    if built:
        b = ('<section class="legal nlissue"><p>The Heuremen LLC weekly newsletter. Every issue is kept here as it was published.</p>'
             '<ul class="nllist">' + ''.join(items) + '</ul>'
             '<p class="nlnav"><a href="/week">Weekly changes</a><a href="/corrections">Corrections</a></p></section>')
        PAGES['/newsletter'] = page('/newsletter', 'Newsletter | Heuremen LLC', 'Every issue of the Heuremen LLC weekly newsletter, as published.', b, hero_slim('Newsletter'))
    return built


def selftest():
    md = '# T, Issue 9\n\nTuesday. By A.\n\n## Head\n\n**Bold.** See indahl.ai/qia#gates and indahl.ai/oy.\n\n- one indahl.ai/corrections\n- two\n\nindahl.ai is ours.'
    t, m, b = parse(md)
    assert t == 'T, Issue 9' and m == 'Tuesday. By A.' and b[0] == ('h', 'Head') and b[2][0] == 'ul' and len(b[2][1]) == 2
    h = body_html(b)
    assert '<a href="/qia#gates">indahl.ai/qia#gates</a>' in h and '<a href="/oy">indahl.ai/oy</a>.' in h and '<p>indahl.ai is ours.</p>' in h and '<b>Bold.</b>' in h
    tx = text(md, 9)
    assert 'https://indahl.ai/qia#gates' in tx and '**' not in tx and 'https://indahl.ai/newsletter/9' in tx and 'indahl.ai is ours' in tx and 'https://indahl.ai/ is' not in tx
    assert number_of('/x/newsletter/issue_12.md') == 12
    print('newsletter_pages selftest: parse, links, text and number read as planted')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']: selftest()
    elif a[:1] in (['text'], ['html']):
        n = int(a[1]); p = os.path.join(ISSUES, 'issue_%d.md' % n); md = open(p, encoding='utf-8').read()
        print(text(md, n) if a[0] == 'text' else email_html(md, n), end='')
    else: print(__doc__)
