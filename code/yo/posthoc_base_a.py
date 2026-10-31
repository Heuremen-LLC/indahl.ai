"""posthoc_base_a.py -- the lenient Job A reading of POSTHOC_BASE_A.md (defined after the base replies were read). Writes nulls_extra.json."""
import json, re, os
H = os.path.dirname(os.path.abspath(__file__))
items = {json.loads(l)['id']: json.loads(l) for l in open(H + '/data2/test_items.jsonl')}
rows = [json.loads(l) for l in open(H + '/eval2_base.jsonl') if '"job": "A"' in l]
def f1(p, t):
    p, t = set(p), set(t)
    if not p and not t: return 1.0
    if not p or not t: return 0.0
    tp = len(p & t); return 0.0 if tp == 0 else 2 * tp / (len(p) + len(t))
def lenient(out):
    m = re.search(r'"stale"\s*:\s*\[(.*?)\]', out, re.S); z = re.search(r'"zero"\s*:\s*\[(.*?)\]', out, re.S)
    return ([int(x) for x in re.findall(r'q?(\d+)', m.group(1))] if m else []), ([re.sub(r'^q', '', x) for x in re.findall(r'"(q?\d+:[A-Za-z_0-9]+)"', z.group(1))] if z else [])
sc = []
for r in rows:
    t = json.loads(items[r['id']]['answer']); st, zr = lenient(r['out']); sc.append((f1(st, t['stale']) + f1(zr, t['zero'])) / 2)
d = dict(A_base_lenient=round(sum(sc) / len(sc), 3), A_base_unparsed=sum(r['pred'] == 'unparsed' for r in rows), A_n=len(rows))
json.dump(d, open(H + '/nulls_extra.json', 'w')); print(d)
