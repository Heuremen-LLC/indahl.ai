import re, html, sys
def show(slug, maxc=230):
    t = open(f'pages/hermes__model__source__{slug}.html', encoding='utf-8').read()
    i = t.find('<main'); j = t.find('<h2>Notices</h2>')
    b = t[i:j]
    h = re.findall(r'<h2>(.*?)</h2>', b); src = re.search(r'<p class="meta">Source:(.*?)</p>', b, re.S)
    print('=== ', slug, '| h1:', html.unescape(re.sub('<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S).group(1))), '| h2:', h)
    print('SRC:', html.unescape(re.sub('<[^>]+>', '', src.group(1))).strip()[:400])
    for r in re.findall(r'<tr>(.*?)</tr>', b[b.find('<tbody>'):], re.S):
        c = [html.unescape(re.sub('<[^>]+>', '', x)).strip() for x in re.findall(r'<td>(.*?)</td>', r, re.S)]
        print(' -', c[4], '|', c[0][:maxc], '|| stated:', c[2][:80], '|| file:', c[3][:maxc], '|| note:', c[5][:maxc])
for s in sys.argv[1:]: show(s)
