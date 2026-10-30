#!/usr/bin/env python3
"""S4 live embedder arm (PLAN a1f47f8). Their scenario texts and rules.py exemplars through the same public embedder weights on our setup
(Mac CPU). rules.py is read as text with ast; nothing of theirs is imported or run. Writes runs/s4_<model>_r<rep>.json.
Usage: embvenv/bin/python run_s4.py <rep>"""
import ast, json, os, sys, glob, time, platform
import torch
from sentence_transformers import SentenceTransformer
torch.set_num_threads(4)
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(H, '..', 'theirs', 'tree_a2e47ae'); REP = int(sys.argv[1])
M = json.load(open(os.path.join(H, 's4_models.json')))
src = open(B + '/code/scrat-fca-crypto/src/scrat_fca_crypto/rules.py').read(); tree = ast.parse(src)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'uk_fca_principles'][0]
P = {}
for node in ast.walk(fn):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'Principle':
        kw = {k.arg: k.value for k in node.keywords}
        cl = []
        for c in kw['clusters'].elts:
            ck = {k.arg: k.value for k in c.keywords}
            cl.append({'cluster_id': ast.literal_eval(ck['cluster_id']), 'pos': ast.literal_eval(ck['positive_exemplars']),
                       'neg': ast.literal_eval(ck['negative_exemplars']), 'w': ast.literal_eval(ck['weight'])})
        P[ast.literal_eval(kw['principle_id'])] = {'tau': ast.literal_eval(kw['escalation_threshold']), 'clusters': cl}
TX = {}
for f in ('corpus_principle', 'paraphrases', 'boundaries', 'adversarial'):
    for l in open(B + '/benchmark/eval/%s.jsonl' % f):
        if l.strip(): r = json.loads(l); TX[r['id']] = r['text']
ex = sorted({e for p in P.values() for c in p['clusters'] for e in c['pos'] + c['neg']})
ids = sorted(TX)
os.makedirs(os.path.join(H, 'runs'), exist_ok=True)
for key, repo in (('minilm', 'sentence-transformers/all-MiniLM-L6-v2'), ('bge', 'BAAI/bge-base-en-v1.5')):
    t0 = time.time(); p = M[repo].get('path')
    m = SentenceTransformer(p, device='cpu') if p and os.path.isdir(p) else SentenceTransformer(repo, revision=M[repo]['revision'], device='cpu')   # local snapshot, else the pinned revision
    E = m.encode([TX[i] for i in ids] + ex, convert_to_tensor=True, normalize_embeddings=True, batch_size=16)
    xs, es = E[:len(ids)], E[len(ids):]; S = (xs @ es.T).tolist(); col = {e: k for k, e in enumerate(ex)}
    out = {}
    for n, i in enumerate(ids):
        out[i] = {}
        for pid, p in P.items():
            cs = []
            for c in p['clusters']:
                ap = sum(S[n][col[e]] for e in c['pos']) / len(c['pos']); an = sum(S[n][col[e]] for e in c['neg']) / len(c['neg'])
                cs.append({'cluster_id': c['cluster_id'], 'avg_positive_sim': ap, 'avg_negative_sim': an, 'w': c['w']})
            out[i][pid] = cs
    meta = {'model': repo, 'revision': M[repo]['revision'], 'rep': REP, 'device': 'cpu', 'threads': torch.get_num_threads(), 'torch': torch.__version__,
            'sentence_transformers': __import__('sentence_transformers').__version__, 'transformers': __import__('transformers').__version__,
            'python': platform.python_version(), 'machine': platform.platform(), 'max_seq_length': m.max_seq_length, 'n_texts': len(ids),
            'n_exemplars': len(ex), 'seconds': round(time.time() - t0, 2), 'at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    json.dump({'meta': meta, 'principles': {k: v['tau'] for k, v in P.items()}, 'sims': out}, open(os.path.join(H, 'runs', 's4_%s_r%d.json' % (key, REP)), 'w'))
    print(key, meta['seconds'], 's', len(ids), 'texts', len(ex), 'exemplars', 'max_seq_length', m.max_seq_length)
