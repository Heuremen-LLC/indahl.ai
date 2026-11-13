#!/usr/bin/env python3
"""build_page.py (12 Nov 2026): renders STANDARD.md, CHECKLIST.md and CROSSWALK.md into the /standard page body (standard_page.json) and copies the files to public/standard/."""
import os, re, json, html, shutil
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PUB = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door/public/standard')
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t); t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return re.sub(r'(https?://[^\s<)]+[^\s<).,])', r'<a href="\1">\1</a>', t)
def md(text, skip_h1=True):
    out, para, lst, tbl = [], [], [], []
    def flush():
        if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
        if lst: out.append('<ul>' + ''.join('<li>' + inline(x) + '</li>' for x in lst) + '</ul>'); lst.clear()
        if tbl:
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in tbl if not re.match(r'^\|[\s\-|]+\|$', r.strip())]
            out.append('<div class="scroll"><table class="mtx"><thead><tr>' + ''.join('<th>' + inline(c) + '</th>' for c in rows[0]) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'); tbl.clear()
    for l in text.split('\n'):
        if l.startswith('|'): para and flush(); tbl.append(l); continue
        elif tbl: flush()
        m = re.match(r'^(#{1,4}) (.*)', l)
        if m:
            flush(); n = len(m.group(1))
            if n == 1 and skip_h1: continue
            out.append('<h%d>%s</h%d>' % (min(n + 1, 4), inline(m.group(2)), min(n + 1, 4))); continue
        if re.match(r'^\s*[-*] ', l): (para and flush()); lst.append(re.sub(r'^\s*[-*] ', '', l)); continue
        if not l.strip(): flush(); continue
        if lst: lst[-1] += ' ' + l.strip()
        else: para.append(l.strip())
    flush(); return ''.join(out)
os.makedirs(PUB, exist_ok=True)
files = ['STANDARD.md', 'standard_v1.json', 'standard_v1.schema.json', 'CHECKLIST.md', 'CROSSWALK.md', 'SHA256SUMS.txt'] + (['SHA256SUMS.txt.ots'] if os.path.exists(os.path.join(H, 'SHA256SUMS.txt.ots')) else [])
for f in files: shutil.copy(os.path.join(H, f), os.path.join(PUB, f))
dl = '<p class="crumb">Download: ' + ' &middot; '.join('<a href="/standard/%s">%s</a>' % (f, f) for f in files) + ' &middot; <a href="https://doi.org/10.5281/zenodo.24164794">DOI 10.5281/zenodo.24164794</a> (version 2.0, <a href="https://doi.org/10.5281/zenodo.24164029">all versions</a>) &middot; <a href="https://github.com/Heuremen-LLC/faultsguards">Python package</a></p>'
body = dl + md(open(os.path.join(H, 'STANDARD.md')).read()) + '<h2>Conformance checklist</h2>' + md(open(os.path.join(H, 'CHECKLIST.md')).read()) + '<h2>Crosswalk to the NIST AI Risk Management Framework</h2>' + md(open(os.path.join(H, 'CROSSWALK.md')).read())
json.dump({'body': body}, open(os.path.join(H, 'web', 'standard_page.json'), 'w'), ensure_ascii=False)
print('standard page', len(body), 'chars')
