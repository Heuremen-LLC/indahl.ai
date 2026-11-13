"""full_slice.py -- paper numbers for 'Papers Against Themselves' from everything read under the pipeline procedure.
Unit: paper. Counted codes: F2 (non-convention), F3, F5, F6, confirmed by both pipeline readers (verdict match, high/medium).
Sources (pipeline procedure only, one rule set): batch_11+ (reachable), full_*, control_02/03, redraft_00..10 (= control_01 + batch_01..10).
Repeat floor: repeat_11/12 against batch_11/12. Hand lane comparison: redraft_* against verified.jsonl (Bones re-read).
Writes analysis/full_slice.json and prints a summary. Run any time; it reads only what has merged."""
import json, os, re, glob, collections
from math import sqrt
I = '/Users/heuremen/bones-forge/sagar/index'
OUT = '/Users/heuremen/bones-forge/sagar/analysis/full_slice.json'
MATCH = {'F2': 'SELECTED_HEADLINE', 'F3': 'UNSUPPORTED_CLAIM', 'F5': 'INCONSISTENT', 'F6': 'INCONSISTENT'}

def rows(f):
    out = []
    if not os.path.exists(f): return out
    for l in open(f):
        try: out.append(json.loads(l))
        except Exception: pass
    return out

def wilson(k, n, z=1.959964):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 3), round((c + h) / d, 3))

def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2); d = p1 - p2
    return round(d, 3), round(d - sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), 3), round(d + sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2), 3)

seed = {r['arxiv']: r for r in json.load(open('/Users/heuremen/bones-forge/sagar/data/index_seed.json')) if r.get('arxiv')}
names = sorted(os.path.basename(f)[:-len('_draft.jsonl')] for f in glob.glob(f'{I}/*_draft.jsonl'))
pipe_batches = [b for b in names if re.match(r'(batch_(1[1-9]|[2-9]\d)|full_\d+|control_0[23]|redraft_\d+)$', b)]
merged = {b for b, v in json.load(open('/Users/heuremen/bones-forge/sagar/pipeline/state.json'))['batches'].items() if v.get('stage') == 'merged'}
pipe_batches = [b for b in pipe_batches if b in merged]   # a drafted but unmerged batch has no confirmed findings yet

# drafts: one row per paper; a paper may appear in a redraft and nowhere else in the pipeline lane
draft = {}; conv = set(); unread = set(); batch_of = {}
for b in pipe_batches:
    for r in rows(f'{I}/{b}_draft.jsonl'):
        a = r.get('arxiv')
        if not a: continue
        draft[a] = r; batch_of[a] = b
        codes = r.get('codes') or {}
        if (codes.get('F2') or {}).get('convention'): conv.add(a)
        if 'UNREADABLE' in json.dumps(codes).upper(): unread.add(a)

ver = [x for f in ('verified_auto.jsonl', 'verified_full.jsonl', 'verified_redraft.jsonl') for x in rows(f'{I}/{f}')]
found = collections.defaultdict(set)
for x in ver:
    if x.get('batch') not in pipe_batches: continue
    if x['code'] == 'F2' and x['arxiv'] in conv: continue
    found[x['arxiv']].add(x['code'])

def arm(a): return 'control' if seed.get(a, {}).get('arm', '').startswith('control') else 'outside'
tab = collections.defaultdict(lambda: collections.Counter())
for a, r in draft.items():
    k = (arm(a), r.get('type') or '?')
    tab[k]['read'] += 1; tab[k]['found'] += a in found; tab[k]['unreadable'] += a in unread
res = {'batches_merged': pipe_batches, 'by_arm_type': {}, 'by_arm': {}}
for (ar, ty), c in sorted(tab.items()):
    res['by_arm_type'][f'{ar}/{ty}'] = dict(c, rate=round(c['found'] / c['read'], 3), ci=wilson(c['found'], c['read']))
for ar in ('outside', 'control'):
    n = sum(c['read'] for (a, _), c in tab.items() if a == ar); k = sum(c['found'] for (a, _), c in tab.items() if a == ar)
    u = sum(c['unreadable'] for (a, _), c in tab.items() if a == ar)
    if n: res['by_arm'][ar] = {'read': n, 'found': k, 'rate': round(k / n, 3), 'ci': wilson(k, n), 'unreadable': u}
if all(ar in res['by_arm'] for ar in ('outside', 'control')):
    o, c = res['by_arm']['outside'], res['by_arm']['control']
    res['control_minus_outside'] = newcombe(c['found'], c['read'], o['found'], o['read'])
res['codes_per_paper'] = dict(collections.Counter(cd for s in found.values() for cd in s))
seed_arm = collections.Counter(r['arm'] for r in json.load(open('/Users/heuremen/bones-forge/sagar/data/index_seed.json')))
res['slice'] = {'total': dict(seed_arm), 'with_arxiv': dict(collections.Counter(r['arm'] for r in seed.values())), 'read_pipeline': len(draft)}

# paper-by-paper: hand lane (Bones re-read, batches 1-10 + control_01) vs pipeline redraft of the same papers
hand = collections.defaultdict(set)
for x in rows(f'{I}/verified.jsonl'):
    if x.get('bones') == 'PRESENT' and x['code'] in MATCH and not (x['code'] == 'F2' and 'convention' in (x.get('basis') or '').lower()):
        hand[x['arxiv']].add(x['code'])
rules_named = set(re.findall(r'\d{4}\.\d{5}', open('/Users/heuremen/bones-forge/sagar/RULES.md').read()))
red = [a for a, b in batch_of.items() if b.startswith('redraft_') and a not in rules_named]
both = sum(1 for a in red if a in hand and a in found); hand_only = sum(1 for a in red if a in hand and a not in found)
pipe_only = sum(1 for a in red if a not in hand and a in found); neither = len(red) - both - hand_only - pipe_only
res['hand_vs_pipeline'] = {'papers': len(red), 'both': both, 'hand_only': hand_only, 'pipeline_only': pipe_only, 'neither': neither,
                           'excluded_named_in_rules': sorted(rules_named & set(batch_of))}

# repeat floor: same papers, same procedure, run twice
rep = {}
for b in ('11', '12'):
    if f'repeat_{b}' not in merged: continue
    first = {a for a in (r.get('arxiv') for r in rows(f'{I}/batch_{b}_draft.jsonl')) if a}
    again = {a for a in (r.get('arxiv') for r in rows(f'{I}/repeat_{b}_draft.jsonl')) if a}
    if not again: continue
    f1 = {x['arxiv'] for x in rows(f'{I}/verified_auto.jsonl') if x.get('batch') == f'batch_{b}'}
    f2 = {x['arxiv'] for x in rows(f'{I}/verified_repeat.jsonl') if x.get('batch') == f'repeat_{b}'}
    ps = first & again
    rep[b] = {'papers': len(ps), 'both': len(ps & f1 & f2), 'first_only': len((ps & f1) - f2), 'repeat_only': len((ps & f2) - f1)}
res['repeat_floor'] = rep
json.dump(res, open(OUT, 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'batches_merged'}, indent=1))
print('merged pipeline batches:', len(pipe_batches))
