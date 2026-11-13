"""Referee verbatim check of rank-claim quotes against saved pages, plus edition words on each page."""
import html, json, os, re, sys

ROOT = os.path.expanduser('~/bones-forge/rank_index/public/nj_claims')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def text(raw, sep):
    raw = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', raw)
    raw = re.sub(r'(?s)<!--.*?-->', ' ', raw)
    t = re.sub(r'(?s)<[^>]+>', sep, raw)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t.replace('\xa0', ' '))


def norm(s):
    return re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip()


claims = json.load(open(os.path.join(ROOT, 'claims.json')))
out = []
for i, c in enumerate(claims):
    p = os.path.join(ROOT, c['saved_copy'])
    if not os.path.exists(p):
        out.append((i, c['school'], 'NO SAVED COPY', p))
        continue
    raw = open(p, encoding='utf-8', errors='replace').read()
    tight = text(raw, '')      # tags removed with nothing: rendered inline text
    loose = text(raw, ' ')     # tags replaced by space
    q = norm(c['quote'])
    where = 'tight' if q in tight else ('loose' if q in loose else None)
    if where is None:
        # try with straight/curly quote and dash normalisation
        tr = str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"', '–': '-', '—': '-'})
        if q.translate(tr) in tight.translate(tr):
            where = 'tight-after-quote-normalising'
        elif q.translate(tr) in loose.translate(tr):
            where = 'loose-after-quote-normalising'
    eds = sorted(set(re.findall(r'\b(20(?:2[4-8])(?:[-–]20?2[5-9])?)\b', tight)))
    ctx = ''
    if where:
        src = tight if where.startswith('tight') else loose
        k = src.find(q[:40])
        ctx = src[max(0, k - 250):k + len(q) + 250] if k >= 0 else ''
    out.append(dict(i=i, school=c['school'], found=where, edition_named=c.get('edition_named'), date=c.get('date_on_page'),
                    years_on_page=eds, quote=q, ctx=ctx, artifacts=bool(re.search(r' [,.’]|U \.S', q))))
json.dump(out, open(os.path.join(HERE, 'out', 'claims_check.json'), 'w'), indent=1, ensure_ascii=False)
for o in out:
    if isinstance(o, tuple):
        print(o)
        continue
    print(f"[{o['i']}] {o['school'][:30]} | found={o['found']} | artifacts={o['artifacts']} | ed={o['edition_named']} | date={o['date']} | years={o['years_on_page']}")
