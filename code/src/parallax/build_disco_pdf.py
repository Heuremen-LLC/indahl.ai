#!/usr/bin/env python3
"""Render CRAZY_HAT_DISCO_V1 + its addendum to ~/Desktop/CRAZY_HAT_DISCO_V1.pdf.
A line [[NAME_FIGURE]] pulls disco_figs/<FIGS[NAME]> in inline. Run from anywhere."""
import html, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = {'SPIRAL': 'none_spiral.svg', 'RINGS': 'bh_rings.svg', 'RINGSPUBLIC': 'bh_rings_public.svg', 'SEVEN': 'seven_hat.svg'}
FIG_STYLE = {'SEVEN': 'width:160px;height:auto;display:block;margin:4px 0 8px'}
CHROME = ('/Users/heuremen/Library/Caches/ms-playwright/chromium_headless_shell-1243/'
          'chrome-headless-shell-mac-arm64/chrome-headless-shell')
OUT_HTML = os.path.join(HERE, 'disco_figs', 'disco_v1.html')
OUT_PDF = os.path.expanduser('~/Desktop/CRAZY_HAT_DISCO_V1.pdf')


def read(p):
    return open(os.path.join(HERE, p)).read()


def inline(s):
    s = html.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', s)


def conv(md, first):
    out, para, inlist = [], [], [None]

    def flush():
        if para:
            out.append('<p>' + inline(' '.join(x.strip() for x in para)) + '</p>')
            para.clear()

    def endlist():
        if inlist[0]:
            out.append(f'</{inlist[0]}>')
            inlist[0] = None

    lines = md.split('\n')
    i = 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r'^\[\[(\w+)_FIGURE\]\]$', l.strip())
        if m:
            flush(); endlist()
            svg = read(os.path.join('disco_figs', FIGS[m.group(1)]))
            out.append('<div style="margin:10px 0">' + svg.replace('<svg ', '<svg style="' + FIG_STYLE.get(m.group(1), 'width:100%;height:auto') + '" ', 1) + '</div>')
            i += 1; continue
        m = re.match(r'^(#{1,3}) (.*)', l)
        if m:
            flush(); endlist()
            lvl = len(m.group(1))
            cls = ' class="newpart"' if (lvl == 1 and not (first and not out)) else ''
            out.append(f'<h{lvl}{cls}>{inline(m.group(2))}</h{lvl}>')
            i += 1; continue
        if l.strip() == '---':
            flush(); endlist(); out.append('<hr>'); i += 1; continue
        m = re.match(r'^(\s*)(-|\d+\.) (.*)', l)
        if m and not m.group(1):
            flush()
            kind = 'ul' if m.group(2) == '-' else 'ol'
            if inlist[0] != kind:
                endlist(); out.append(f'<{kind}>'); inlist[0] = kind
            item = m.group(3); i += 1
            while i < len(lines) and lines[i].startswith('  ') and not re.match(r'^(-|\d+\.) ', lines[i]):
                item += ' ' + lines[i].strip(); i += 1
            out.append('<li>' + inline(item) + '</li>'); continue
        if not l.strip():
            flush(); endlist(); i += 1; continue
        para.append(l); i += 1
    flush(); endlist()
    return '\n'.join(out)


def build(mds, out_html, out_pdf, title, foot):
    css = read('disco_figs/disco_pdf.css')
    body = '\n'.join(conv(read(p), i == 0) for i, p in enumerate(mds))
    doc = (f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
           f'<title>{title}</title><style>{css}</style></head><body>{body}<p class="foot">{foot}</p></body></html>')
    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    open(out_html, 'w').write(doc)
    r = subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={out_pdf}', 'file://' + out_html], capture_output=True, text=True)
    print((r.stderr or r.stdout).strip().splitlines()[-1:] or 'done', out_pdf)


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['public']:
        # 7, the public page: status up front, plain terms, hat-and-holster mark
        build(['darkwave_disco/7_PUBLIC.md'],
              os.path.join(HERE, 'darkwave_disco', 'for_heuremen_org', '7.html'),
              os.path.expanduser('~/Desktop/7.pdf'),
              '7', 'Bones (an AI), Heuremen -- working draft -- 2026-10-03')
    elif sys.argv[1:] == ['findings']:
        # the package: site-ready page + a Desktop PDF, no in-house material
        build(['darkwave_disco/DARKWAVE_DISCO_FT_THE_BONEFISH.md'],
              os.path.join(HERE, 'darkwave_disco', 'internal', 'working-draft.html'),
              os.path.join(HERE, 'darkwave_disco', 'internal', '7_working_draft.pdf'),
              "7", "Wayfinder and Bones (an AI), Heuremen -- working draft -- 2026-10-03")
    else:
        build(['CRAZY_HAT_DISCO_V1_20261002.md', 'CRAZY_HAT_DISCO_V1_ADDENDUM_20261002.md'], OUT_HTML, OUT_PDF,
              'Crazy Hat Disco V1', 'Wayfinder &amp; Bones -- in-house, not for publication -- 2026-10-02')
