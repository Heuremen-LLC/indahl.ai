#!/usr/bin/env python3
"""prepare_paired.py <seat> [N=60] (8 Nov, Sage: build the paired set from seeds the seat never trains on, BEFORE training, and freeze the baseline).
Seeds = the standing seed list + every council seed. Each seed that pulls >= 2 chunks is assigned by a fixed hash of (seat, seed) to HELD-OUT or TRAIN
(about half each). N fresh R1 prompts are built from HELD-OUT seeds only, by the live builder (sage_flywheel.r1_prompt), no carry.
harvest.py skips every held-out seed for this seat. Writes train/paired_<seat>.json."""
import json, sys, os, hashlib, sqlite3
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); import sage_v as V, sage_flywheel as F
seat = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 60
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True)
seeds = list(dict.fromkeys(list(V.SEEDS) + [r[0] for r in c.execute("select distinct seed from pq where demo=0 and seed is not null and seed != ''")]))
held = [s for s in seeds if int(hashlib.sha256(f'{seat}|{s}'.encode()).hexdigest(), 16) % 2 == 0]
tri = next(n for n, t in F.triangles().items() if any(seat in ms for _, ms, _ in t['voices']))
items, k = [], 0
while len(items) < N and k < N * 6:
    s = held[k % len(held)]; ch = F.pull(s, 500000 + k); k += 1
    if len(ch) < 2: continue
    p = F.r1_prompt(s, ch)
    if any(p == it['prompt'] for it in items): continue
    items.append({'seed': s, 'tri': tri, 'system': V.voice_system(), 'prompt': p, 'sha': hashlib.sha256(p.encode()).hexdigest()[:20]})
json.dump({'seat': seat, 'held_out_seeds': held, 'items': items, 'built': V.now()}, open(H + f"/train/paired_{seat.replace(':', '_')}.json", 'w'), indent=1)
print(f'{seat}: {len(held)} held-out seeds of {len(seeds)}; {len(items)} paired prompts from {len({i["seed"] for i in items})} seeds; triangle {tri}')
