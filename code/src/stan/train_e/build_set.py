"""STAN-E training set from the SAGAR full read (12 Nov 2026 night).
Labels: two-reader pipeline findings (F5, F6; verdict INCONSISTENT, confidence high/medium) on every paper the pipeline drafted.
Unit of training: a ~6000-character chunk, the same chunking and prompt as stan/errata/errata_drafter.py, so a trained model is
scored exactly like the untrained ones on the leaderboard.
  positive chunk: contains a confirmed finding's draft quote (whitespace-normalised substring) -> target lists that finding
  negative chunk: from a paper whose drafted F5 and F6 are both ABSENT or NOT_APPLICABLE and which has no confirmed finding -> {"errors": []}
Split by PAPER, never by chunk: sha1(arxiv) decides train/valid/test (80/10/10). A second test set, HAND, holds every paper the Bones
re-read covered (sagar/index/verified.jsonl); those papers never enter train or valid.
Writes data/{train,valid}.jsonl (mlx chat format), data/test_pipeline.jsonl, data/test_hand.jsonl, data/manifest.json."""
import json, os, re, glob, hashlib, random, collections
S = '/Users/heuremen/bones-forge/sagar/index'; D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(D, exist_ok=True)
P = open('/Users/heuremen/bones-forge/stan/errata/errata_drafter.py').read().split('P=(', 1)[1].split('\ndef call', 1)[0]
P = eval('(' + P)   # the drafter's own prompt string, byte for byte
norm = lambda s: re.sub(r'\s+', ' ', s or '').strip()

def rows(f):
    out = []
    if not os.path.exists(f): return out
    for l in open(f):
        try: out.append(json.loads(l))
        except Exception: pass
    return out

drafts = {}
for f in glob.glob(f'{S}/*_draft.jsonl'):
    b = os.path.basename(f)[:-len('_draft.jsonl')]
    if not re.match(r'(batch_(1[1-9]|[2-9]\d)|full_\d+|control_0[23]|redraft_\d+)$', b): continue
    for r in rows(f):
        if r.get('arxiv'): drafts[r['arxiv']] = r
found = collections.defaultdict(list)
for fn in ('verified_auto.jsonl', 'verified_full.jsonl', 'verified_redraft.jsonl'):
    for x in rows(f'{S}/{fn}'):
        if x['code'] in ('F5', 'F6') and x.get('reader_verdict') == 'INCONSISTENT' and x.get('reader_confidence') in ('high', 'medium'):
            found[x['arxiv']].append(x)
hand = {x['arxiv'] for x in rows(f'{S}/verified.jsonl')}
def split(a):
    if a in hand: return 'hand'
    h = int(hashlib.sha1(a.encode()).hexdigest(), 16) % 10
    return 'test' if h == 0 else 'valid' if h == 1 else 'train'
def absent(r):
    c = r.get('codes') or {}
    return all((c.get(k) or {}).get('status', '') in ('ABSENT', 'NOT_APPLICABLE') for k in ('F5', 'F6'))

out = collections.defaultdict(list); stats = collections.Counter()
rng = random.Random(20261112)
for a, r in drafts.items():
    tf = f'{S}/text/{a}.txt'
    if not os.path.exists(tf): stats['no_text'] += 1; continue
    t = re.sub(r'[ \t]+', ' ', open(tf, errors='replace').read())
    chunks = [t[i:i + 6000] for i in range(0, len(t), 5400)]
    sp = split(a); fs = found.get(a, [])
    if fs:
        for k, c in enumerate(chunks):
            nc = norm(c)
            hits = [x for x in fs if len(norm(x['draft_quote'])) > 15 and norm(x['draft_quote']) in nc]
            if not hits: continue
            tgt = {'errors': [{'quote_a': norm(x['draft_quote'])[:250], 'quote_b': norm((x.get('reader_quotes') or [''])[-1])[:250],
                               'arithmetic': (x.get('reader_arithmetic') or '')[:400], 'why': x['code']} for x in hits]}
            out[sp].append({'arxiv': a, 'chunk': k, 'label': 1, 'messages': [{'role': 'user', 'content': P + c}, {'role': 'assistant', 'content': json.dumps(tgt)}]})
            stats[f'{sp}_pos'] += 1
    elif absent(r):
        for k in rng.sample(range(len(chunks)), min(3, len(chunks))):
            out[sp].append({'arxiv': a, 'chunk': k, 'label': 0, 'messages': [{'role': 'user', 'content': P + chunks[k]}, {'role': 'assistant', 'content': '{"errors": []}'}]})
            stats[f'{sp}_neg'] += 1
    else:
        stats['excluded_ambiguous_papers'] += 1   # CANNOT_TELL cells or unconfirmed drafts: neither label is trustworthy
for sp, fn in (('train', 'train.jsonl'), ('valid', 'valid.jsonl'), ('test', 'test_pipeline.jsonl'), ('hand', 'test_hand.jsonl')):
    with open(os.path.join(D, fn), 'w') as f:
        for x in out[sp]:
            f.write(json.dumps({'messages': x['messages']} if sp in ('train', 'valid') else x) + '\n')
man = {'papers_drafted': len(drafts), 'papers_with_finding': len(found), 'stats': dict(stats),
       'split_papers': dict(collections.Counter(split(a) for a in drafts))}
json.dump(man, open(os.path.join(D, 'manifest.json'), 'w'), indent=1); print(json.dumps(man, indent=1))
