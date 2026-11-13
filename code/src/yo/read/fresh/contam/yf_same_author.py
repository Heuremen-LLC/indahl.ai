"""Sage 5 Nov: the flag rule needs the title to survive; a retitled same-author version is untested. List every primary and sensitivity
paper whose top trained match BY AUTHOR OVERLAP has overlap >= 0.5, at any title score, for a hand read. Authors matched as first initial + surname. Inputs only."""
import json, os
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); ns = {}
exec(open(H + '/contam/yf_contam_meta.py').read().split("fresh = {json.loads")[0], ns)
TR, M = ns['TR'], ns['M']
import unicodedata, re
def fullnames(k):   # first initial + surname, so a common surname alone does not match (listing only; the hand read decides)
    out = set()
    for n in filter(None, M.get(k, {}).get('authors') or []):
        n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
        n = re.sub(r'\b(dr|prof|mr|mrs|ms|phd|md)\b\.?', ' ', n).strip(' ,')   # honorifics ('Dr. Zuhair Ahmed' missed PKTron)
        if ',' in n: last, first = [x.strip() for x in n.split(',', 1)]
        else: parts = n.split(); last, first = (parts[-1], parts[0]) if parts else ('', '')
        last = re.sub(r'[^a-z]', '', last); first = re.sub(r'[^a-z]', '', first)
        if last: out.add(last + ' ' + first[:1])
    return out
def tw(k): return ns['tw'](M.get(k, {}).get('title'))
FN = {j: fullnames(j) for j in TR}
prim = set(open(H + '/primary_ids.txt').read().split()); sens = set(open(H + '/sensitivity_ids.txt').read().split())
for k in sorted(prim | sens):
    a1, t1 = fullnames(k), tw(k); best = []
    for j in TR:
        a2, t2 = FN[j], tw(j)
        A = len(a1 & a2) / min(len(a1), len(a2)) if a1 and a2 else 0.0
        if A >= 0.5: best.append((A, len(t1 & t2) / len(t1 | t2) if t1 and t2 else 0.0, j))
    for A, T, j in sorted(best, reverse=True):
        print(f'{k} [{"P" if k in prim else ""}{"S" if k in sens else ""}] ~ {j}: authors {A:.2f} title {T:.2f}')
        print(f'    fresh:   {M[k].get("title")} | {", ".join((M[k].get("authors") or [])[:4])}')
        print(f'    trained: {M[j].get("title")} | {", ".join((M[j].get("authors") or [])[:4])}')
