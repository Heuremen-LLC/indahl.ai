"""yr_data.py -- builds YO Read items per PLAN_YO_READ.md: papers joined to the QIA List, three questions per paper, candidates picked by
code, the REGEX and MAJORITY arms, the TEST / VALID / TRAIN split by sha256 of the normalised id. Writes data/{train,valid}.jsonl
(prompt, completion) and data/test_items.jsonl. Asserts every prompt is under 1,900 tokens and the truth scorer gives 1.000."""
import json, glob, os, re, hashlib, collections, sys
H = os.path.dirname(os.path.abspath(__file__)); Q = os.path.expanduser('~/bones-forge/qia_leads/')
def norm(l):
    l = (l or '').lower()
    m = re.search(r'arxiv\.org/(?:abs|pdf|html)/([0-9]{4}\.[0-9]{4,5})', l)
    if m: return 'ax:' + m.group(1)
    m = re.search(r'(10\.\d{4,9}/[^\s?#]+)', l)
    return 'doi:' + m.group(1).rstrip('/.') if m else l
MON = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan\.|Feb\.|Mar\.|Apr\.|Jun\.|Jul\.|Aug\.|Sep\.|Sept\.|Oct\.|Nov\.|Dec\.)'
PAT = {
 'DATES': (re.compile(rf'{MON}|\b20\d\d-\d\d-\d\d\b'), re.compile(r'\b(?:201[6-9]|202[0-6])\b')),
 'LINK': (re.compile(r'https?://|www\.', re.I), re.compile(r'\bdoi\b|github|gitlab|zenodo|figshare|osf\.io|repositor|availab|supplementa', re.I)),
 'REQUEST': (re.compile(r'request', re.I), re.compile(r'availab|contact', re.I)),
}
ASK = {
 'DATES': 'Does the paper print a date or date range of its own quantum hardware runs (not a publication, citation or calibration-data date)?',
 'LINK': 'Does the paper print a URL, DOI or repository for its own data or code (not a citation of another work)?',
 'REQUEST': 'Does the paper say its data or code are available on request?',
}
def cut_refs(t):
    hs = [m.start() for m in re.finditer(r'^\s*(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*$', t, re.M)]
    hs = [h for h in hs if h > len(t) / 2]
    return t[:hs[-1]] if hs else t
def sents(t): return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n\s*\n', re.sub(r'[ \t]+', ' ', t)) if s.strip()]
def clip(s, m):
    s = s.replace('\n', ' ')
    if len(s) <= 240: return s
    a = max(0, m.start() - 100); return s[a:a + 240]
def candidates(text, q):
    strong, weak = PAT[q]; S = sents(cut_refs(text)); A, B = [], []
    for s in S:
        m = strong.search(s)
        if m: A.append(clip(s, m)); continue
        m = weak.search(s)
        if m: B.append(clip(s, m))
    c = A + B; return c[:20], len(c) > 20
def prompt(q, cands):
    body = '\n'.join(f'{i + 1}. {c}' for i, c in enumerate(cands)) if cands else '(no sentence matched)'
    return (f'You read sentences picked from a quantum-hardware paper (reference list removed). {ASK[q]} Answer only YES or NO.\n'
            f'Sentences:\n{body}')
def regex(q, cands):
    j = ' \n '.join(cands)
    if q == 'DATES': return 'YES' if re.search(rf'{MON}\s*(?:\d{{1,2}},?\s*)?(?:20\d\d)|\b20\d\d-\d\d-\d\d\b|\d{{1,2}}\s+{MON}\s+20\d\d', j) else 'NO'
    if q == 'LINK':
        if re.search(r'(?:github\.com|gitlab\.com|zenodo\.org|figshare\.com|osf\.io)', j, re.I): return 'YES'
        return 'YES' if any(re.search(r'availab', c, re.I) and re.search(r'https?://', c) for c in cands) else 'NO'
    return 'YES' if re.search(r'(?:up)?on\s+(?:reasonable\s+)?request', j, re.I) else 'NO'
def truth(entry):
    f4 = [x.lower() for x in entry.get('basis', {}).get('F4', [])]
    return {'DATES': 'NO' if any('run dates not printed' in x for x in f4) else 'YES',
            'LINK': 'NO' if any(re.search(r'no data link printed|no data or code (?:url|link|repositor)', x) for x in f4) else 'YES',
            'REQUEST': 'YES' if any('request' in x for x in f4) else 'NO'}
def split(k):
    d = hashlib.sha256(k.encode()).hexdigest()[0]
    return 'TEST' if d in '012' else 'VALID' if d == '3' else 'TRAIN'
def papers():
    L = json.load(open(Q + 'matrix_page/list.json')); rows = L if isinstance(L, list) else next(v for v in L.values() if isinstance(v, list))
    by = {}
    for r in rows: by.setdefault(norm(r['link']), r)
    out, seen = [], set()
    for f in sorted(glob.glob(Q + 'sweep_20261101/out/*.json') + glob.glob(Q + 'backfill_20261101/out/*.json')):
        try: d = json.load(open(f))
        except Exception: continue
        for o in d if isinstance(d, list) else []:
            r = by.get(norm(o.get('link')))
            if not r or r.get('read') != 'Full text': continue
            k = norm(r['link'])
            if k in seen: continue
            tf = os.path.basename(o.get('text_file') or '')
            p = next((x for x in (Q + 'sweep_20261101/texts/' + tf, Q + 'backfill_20261101/texts/' + tf) if tf and os.path.exists(x)), None)
            if not p: continue
            seen.add(k); out.append((k, r, p))
    return out
if __name__ == '__main__':
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-1.7B')
    P = papers(); items = []; capped = collections.Counter()
    for k, r, p in P:
        text = open(p, errors='replace').read(); t = truth(r)
        for q in ('DATES', 'LINK', 'REQUEST'):
            c, cap = candidates(text, q); capped[q] += cap
            pr = prompt(q, c); n = len(tok(pr)['input_ids'])
            while n > 1900 and c: c = c[:-1]; pr = prompt(q, c); n = len(tok(pr)['input_ids'])
            items.append(dict(id=f'{k}|{q}', paper=k, q=q, split=split(k), prompt=pr, answer=t[q], regex=regex(q, c), n_tok=n))
    maj = {q: collections.Counter(i['answer'] for i in items if i['q'] == q and i['split'] == 'TRAIN').most_common(1)[0][0] for q in ASK}
    for i in items: i['majority'] = maj[i['q']]
    assert all(i['n_tok'] <= 1900 for i in items)
    os.makedirs(H + '/data', exist_ok=True)
    for s, fn in (('TRAIN', 'train.jsonl'), ('VALID', 'valid.jsonl')):
        with open(f'{H}/data/{fn}', 'w') as f:
            for i in items:
                if i['split'] == s: f.write(json.dumps({'prompt': i['prompt'], 'completion': i['answer']}) + '\n')
    with open(f'{H}/data/test_items.jsonl', 'w') as f:
        for i in items:
            if i['split'] == 'TEST': f.write(json.dumps(i) + '\n')
    te = [i for i in items if i['split'] == 'TEST']
    from yr_known_good import known_good; print('known-good', known_good(te))  # 4 Nov: was `assert x == x` (could never fail); now runs the real parse and must fail on flipped answers
    print('papers', len(P), 'by split', collections.Counter(split(k) for k, _, _ in P), 'capped at 20 by question', dict(capped),
          'majority', maj, 'max tokens', max(i['n_tok'] for i in items))
