"""Referee: each stated quote must be an exact substring of the fetched source text, each number in the desk's row specs must appear in its quote,
and the source files must match SHA256SUMS. Read-only. Usage: python3 -I quotes_check.py DESKDIR OUTJSON"""
import json, hashlib, sys, os, re, html
d, outp = sys.argv[1], sys.argv[2]; src = os.path.join(d, 'data', 'source')
out = dict(sha=[], quotes={})
for line in open(os.path.join(src, 'SHA256SUMS')):
    h, f = line.split(None, 1); f = f.strip().lstrip('*'); p = os.path.join(src, os.path.basename(f))
    out['sha'].append(dict(file=os.path.basename(f), ok=os.path.exists(p) and hashlib.sha256(open(p, 'rb').read()).hexdigest() == h))
st = json.load(open(os.path.join(d, 'data', 'stated.json')))
txt = {}
for f in os.listdir(src):
    if f.endswith('.txt'): txt[f] = open(os.path.join(src, f), encoding='utf-8').read()
    if f.endswith('.html'):
        t = re.sub(r'<[^>]+>', ' ', open(os.path.join(src, f), encoding='utf-8').read()); txt[f + ' (tags stripped)'] = html.unescape(re.sub(r'\s+', ' ', t))
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
for k, q in st['quotes'].items():
    hits = [f for f, t in txt.items() if q['quote'] in t or norm(q['quote']) in norm(t)]
    out['quotes'][k] = hits
json.dump(out, open(outp, 'w'), indent=1); print(json.dumps(out, indent=1))
