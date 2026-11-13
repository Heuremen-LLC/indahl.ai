"""yr_rescore_build.py -- PREREG_YO_RESCORE.md (sha256 fe751109...). Corrected source text for the 22 TEST papers whose YO input was under half the
size of the file the List reader read (verify_20261103/texts.py rule, build-time List list.json.pre-removal-20261102). For those papers the prompt
is rebuilt from the reader's own text file with yr_data's candidates/prompt/regex unchanged (1900-token cap as before). Every other TEST item and
every answer label is copied unchanged from data/test_items.jsonl. Writes data/test_items_rescore.jsonl. Run before any reader."""
import sys, json, os, glob
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import yr_data as Y
from transformers import AutoTokenizer
Q = Y.Q; M = Q + 'matrix_page/'; ro = open
Y.open = lambda p, *a, **k: ro(M + 'list.json.pre-removal-20261102' if p.endswith('matrix_page/list.json') else p, *a, **k)
P = Y.papers(); used = {}
for f in sorted(glob.glob(Q + 'sweep_20261101/out/*.json') + glob.glob(Q + 'backfill_20261101/out/*.json')):
    try: d = json.load(ro(f))
    except Exception: continue
    for o in d if isinstance(d, list) else []: used.setdefault(Y.norm(o.get('link')), o.get('text_file') or '')
test = [json.loads(l) for l in ro(H + '/data/test_items.jsonl')]; byid = {t['id']: t for t in test}
fix = {}
for k, r, p in P:
    if Y.split(k) != 'TEST': continue
    tf = used.get(k, ''); rp = next((x for x in (tf, Q + tf, Q + 'sweep_20261101/' + tf) if x and os.path.isfile(x)), None)
    if rp and os.path.realpath(rp) != os.path.realpath(p) and os.path.getsize(p) < os.path.getsize(rp) / 2: fix[k] = rp
tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-1.7B'); out = []; changed = 0
for t in test:
    if t['paper'] in fix:
        text = ro(fix[t['paper']], errors='replace').read(); c, _ = Y.candidates(text, t['q']); pr = Y.prompt(t['q'], c); n = len(tok(pr)['input_ids'])
        while n > 1900 and c: c = c[:-1]; pr = Y.prompt(t['q'], c); n = len(tok(pr)['input_ids'])
        t = dict(t, prompt=pr, regex=Y.regex(t['q'], c), n_tok=n, text_source=fix[t['paper']].replace(Q, ''), corrected=True); changed += 1
    out.append(t)
with open(H + '/data/test_items_rescore.jsonl', 'w') as f:
    for t in out: f.write(json.dumps(t) + '\n')
print('papers corrected', len(fix), 'items rebuilt', changed, 'of', len(out), '| answers unchanged:', all(a['answer'] == byid[a['id']]['answer'] for a in out))
