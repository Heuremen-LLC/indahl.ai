import re, json, os, html, glob
D = os.path.dirname(os.path.abspath(__file__))
def parse(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'<main class="wrap">(.*?)</main>', t, re.S)
    main = m.group(1) if m else ''
    sec = re.search(r'<section class="legal">(.*?)</section>', main, re.S)
    body = sec.group(1) if sec else ''
    parts = re.split(r'<h2>(.*?)</h2>', body)
    d = {'_head': parts[0]}
    for i in range(1, len(parts), 2):
        d[parts[i]] = parts[i+1]
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    h1 = re.search(r'<h1>(.*?)</h1>', t, re.S)
    desc = re.search(r'<meta name="description" content="(.*?)">', t, re.S)
    return {'raw': t, 'main': main, 'body': body, 'sections': d, 'title': title.group(1) if title else None, 'h1': h1.group(1) if h1 else None, 'desc': desc.group(1) if desc else None}
def text(h):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', h)).split())
if __name__ == '__main__':
    pages = {}
    for f in sorted(glob.glob(D + '/pages/*.html')):
        n = os.path.basename(f)[:-5]
        pages[n] = parse(f)
    print(len(pages))
    import collections
    c = collections.Counter()
    for n, p in pages.items():
        c[tuple(k for k in p['sections'])] += 1
    for k, v in c.most_common(): print(v, k)
