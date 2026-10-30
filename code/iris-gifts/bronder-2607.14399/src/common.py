"""Data-only loaders for the Bronder gift (our code). His inspect-ai .eval logs are zip files read as JSON; nothing of his is imported or run."""
import os, glob, json, zipfile, hashlib, collections
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'zenodo', 'extract', 'logs')
def pick(d, skin=None, render=None, disclose=None):
    """the closed (status success) log in a directory whose task arguments match; byte-identical copies collapse to one"""
    c = []
    for p in sorted(glob.glob(os.path.join(L, d, '*.eval'))):
        z = zipfile.ZipFile(p); h = json.loads(z.read('header.json')); ta = h['eval'].get('task_args_passed') or {}
        if h['status'] != 'success': continue
        if skin is not None and ta.get('skin') != skin: continue
        if render is not None and ta.get('budget_render') != render: continue
        c.append((hashlib.sha256(open(p, 'rb').read()).hexdigest(), p, h))
    assert len({x[0] for x in c}) == 1, (d, skin, render, [x[1] for x in c])
    return c[0][1], c[0][2]
def games(path):
    z = zipfile.ZipFile(path); out = []
    for n in sorted(z.namelist()):
        if not (n.startswith('samples/') and n.endswith('.json')): continue
        s = json.loads(z.read(n)); g = (s.get('store') or {}).get('game_log') or {}; inst = (s.get('metadata') or {}).get('instance') or {}
        ops = g.get('ops') or []; v = None
        if g.get('terminal') == 'HALT':
            v = (((ops[-1] if ops else {}).get('engine_validated_op') or {}).get('args') or {}).get('verdict')
        ev = collections.Counter(de.get('type') for o in ops for de in (o.get('delta_events') or []) if isinstance(de, dict))
        out.append({'inst': inst.get('id'), 'epoch': s.get('epoch'), 'solvable': inst.get('solvable', g.get('solvable')), 'error': bool(s.get('error')),
                    'terminal': g.get('terminal'), 'verdict': (str(v).lower() if v is not None else None), 'events': ev,
                    'flags': len((s.get('store') or {}).get('fidelity_flags') or [])})
    return out
def valid(g): return (not g['error']) and bool(g['terminal'])
def outcome(g): return ('HALT_' + g['verdict'].upper()) if g['terminal'] == 'HALT' else g['terminal']
def strong(g): return g['terminal'] == 'HALT' and g['verdict'] in ('complete', 'unreachable')
def won(g): return any(k in g['events'] for k in ('win', 'won', 'quest_complete'))
def false_verdict(g): return g['terminal'] == 'HALT' and ((g['verdict'] == 'complete' and not won(g)) or (g['verdict'] == 'unreachable' and g['solvable']))
