import sys, json, os, glob, collections
sys.path.insert(0, os.path.expanduser('~/bones-forge/yo/read'))
import yr_data as Y
Q = Y.Q; M = Q + 'matrix_page/'; snap = sys.argv[1]
ro = open
Y.open = lambda p, *a, **k: ro(M + snap if p.endswith('matrix_page/list.json') else p, *a, **k)
P = Y.papers()
# reader's own text_file per key (first out record that the builder used)
used = {}
for f in sorted(glob.glob(Q + 'sweep_20261101/out/*.json') + glob.glob(Q + 'backfill_20261101/out/*.json')):
    try: d = json.load(ro(f))
    except Exception: continue
    for o in d if isinstance(d, list) else []:
        k = Y.norm(o.get('link'))
        used.setdefault(k, o.get('text_file') or '')
test = {json.loads(l)['id']: json.loads(l) for l in ro(os.path.expanduser('~/bones-forge/yo/read/data/test_items.jsonl'))}
bad = []; kinds = collections.Counter(); nofile = 0
for k, r, p in P:
    tf = used[k]; cand = [tf, Q + tf, Q + 'sweep_20261101/' + tf if not tf.startswith('/') else tf]
    rp = next((x for x in cand if x and os.path.isfile(x)), None)
    if not rp: nofile += 1; continue
    a, b = os.path.getsize(p), os.path.getsize(rp)
    if os.path.realpath(rp) != os.path.realpath(p) and a < b / 2:
        bad.append((k, Y.split(k), a, b, p.replace(Q,''), rp.replace(Q,'')))
        kinds['empty' if a <= 1 else 'short'] += 1
print('papers', len(P), 'reader file not found', nofile)
print('wrong/short text:', len(bad), dict(kinds), 'by split', collections.Counter(b[1] for b in bad))
tb = [b for b in bad if b[1] == 'TEST']
# DATES TEST items for those papers
dd = [(b[0], test[b[0]+'|DATES']['answer']) for b in tb]
print('TEST DATES labels on wrong-text papers:', collections.Counter(x[1] for x in dd))
nm = sum('(no sentence matched)' in test[b[0]+'|DATES']['prompt'] for b in tb)
print('TEST wrong-text papers whose DATES prompt is "(no sentence matched)":', nm)
for b in tb: print(' ', b[0], b[2], 'bytes vs', b[3], b[4], '->', b[5])
json.dump(bad, ro('/tmp/yrv/bad_%s.json' % snap, 'w'))
