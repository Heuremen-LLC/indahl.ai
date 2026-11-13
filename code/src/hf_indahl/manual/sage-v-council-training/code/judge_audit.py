#!/usr/bin/env python3
"""judge_audit.py (8 Nov, Sage's review: "score each judge on the plants first; if its plant accuracy is mediocre, its q on real rows is noise").
Runs every judge in seats.json on N held-out plants (known truth), same prompt shape the flywheel judge uses, and writes judge_audit.json:
per judge model, accuracy (q >= 0.5 vs truth == SUPPORTS), AUC of q, mean q, n. The scoreboard and calib_train read it to decide how far
to trust each judge's q. Fixed set (the first N holdout ids), so the audit does not move. Usage: judge_audit.py [N=60]"""
import json, os, re, sys, sqlite3, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import sage_flywheel as F, sage_v as V
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True)
ids = json.load(open(H + '/holdout_plants.json'))['ids'][:N]
LIBDB = json.load(open(H + '/local.json')).get('libdb')
lib = sqlite3.connect(f'file:{LIBDB}?mode=ro', uri=True)
items = []
for pid, claim, truth, cid in c.execute('select id, planted, truth, chunk_id from calib where id in (%s)' % ','.join('?' * len(ids)), ids):
    t = (lib.execute('select text from chunks where id=?', (cid,)).fetchone() or [None])[0]
    if t: items.append((pid, claim, truth, t))
judges = {tuple(t['judge']) for t in F.triangles().values()}
out = {}
for jm, jh in judges:
    res = []
    for k in range(0, len(items), 6):
        ch = items[k:k + 6]
        lines = '\n'.join(f"[{i}] CLAIM: {cl}\n    CHUNK: {t[:700]}" for i, (_, cl, _, t) in enumerate(ch))
        user = ("You are an EXTERNAL JUDGE. For each numbered claim, judge only from its chunk: is the claim right? q is your probability (0 to 1) that it is right.\n\n" + lines +
                '\n\nJSON {"scores": [{"k": 0, "q": 0.0, "why": "one short reason"}]}')
        j, raw, ms, cause = F.ask(jh, jm, "You are a strict external judge of claims against source text. Answer only JSON.", user, 700)
        qs = {}
        for r in (j or {}).get('scores', []) if isinstance(j, dict) else []:
            try: qs[int(r.get('k'))] = max(0.0, min(1.0, float(r.get('q'))))
            except Exception: pass
        for i, (pid, cl, truth, t) in enumerate(ch): res.append((qs.get(i), 1 if truth == 'SUPPORTS' else 0))
    sc = [(q, y) for q, y in res if q is not None]
    pos = [q for q, y in sc if y]; neg = [q for q, y in sc if not y]
    auc = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg)) if pos and neg else None
    out[jm] = {'n': len(res), 'scored': len(sc), 'accuracy': round(sum((q >= 0.5) == bool(y) for q, y in sc) / len(sc), 3) if sc else None,
               'auc': round(auc, 3) if auc is not None else None, 'mean_q': round(sum(q for q, _ in sc) / len(sc), 3) if sc else None,
               'trusted': bool(sc and auc is not None and auc >= 0.7 and len(sc) >= 0.8 * len(res)), 'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    print(jm, out[jm], flush=True)
json.dump(out, open(H + '/judge_audit.json', 'w'), indent=1)
