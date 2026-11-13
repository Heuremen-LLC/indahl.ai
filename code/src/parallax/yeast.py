"""YEAST -- 2026-09-28, Wayfinder's hat: recursive growth, the outcome picks the next move. No outcomes written, only the budding
rule: a stone (qubit) in superposition, its pond = every qubit within 3 hops. Pond read first, stone read LAST. Whichever pond qubit
tilts most with the stone's answer (in its own noise units) becomes the next stone. Stops when nobody in the pond knows (< 3 noise
units), or at the QPU brake. The chip draws its own path."""
import sys, os, json, math, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import parallax_ibm as P
BAD = {0, 72, 113}; SHOTS = 4000; WAIT_NS = 5000; BRAKE = 15
def pond_of(t, stone, used):
    E = {}
    for a, b in t['cz'].keys(): E.setdefault(a, set()).add(b); E.setdefault(b, set()).add(a)
    seen = {stone: 0}; frontier = [stone]
    for h in (1, 2, 3):
        nxt = []
        for x in frontier:
            for y in E.get(x, ()):
                if y not in seen: seen[y] = h; nxt.append(y)
        frontier = nxt
    return sorted([q for q in seen if q != stone and q not in BAD], key=lambda q: (seen[q], q))[:14], seen
def circ(n, kind):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(n + 1, 'q'); s = ClassicalRegister(1, 's'); b = ClassicalRegister(n, 'b'); c = QuantumCircuit(q, s, b)   # q[0] = stone
    if kind in ('P0', 'P1'):
        if kind == 'P1': c.x(q)
        c.measure(q[0], s[0]); c.measure(q[1:], b); return c
    c.h(q); c.barrier(); c.delay(WAIT_NS, q, unit='ns'); c.barrier()
    if kind == 'Y': c.sdg(q[1:])
    c.h(q[1:]); c.measure(q[1:], b); c.barrier(); c.measure(q[0], s[0]); return c
def cut(z0, z1):
    H = len(z0) // 2; c0 = complex(np.median(z0[:H].real), np.median(z0[:H].imag)); c1 = complex(np.median(z1[:H].real), np.median(z1[:H].imag)); a = c1 - c0
    f = lambda z: ((z - c0) * np.conj(a)).real / abs(a) ** 2 > .5
    return f, max(float(np.mean(f(z0[H:]))), float(np.mean(~f(z1[H:]))))
def main(keyfile, backend, stone):
    from qiskit_ibm_runtime import SamplerV2; from qiskit import transpile
    sv, be = P.chip(keyfile, backend); t = be.target; used = []; d = os.path.join(P.HERE, 'out', 'yeast_' + time.strftime('%H%M%S')); os.makedirs(d); log = []
    while True:
        left = sv.usage().get('usage_remaining_seconds', 0)
        if left < BRAKE: print('BRAKE: stopping with', left, 's left', flush=True); break
        used.append(stone); pond, hops = pond_of(t, stone, used); L = [stone] + pond; n = len(pond)
        circs = [transpile(circ(n, k), backend=be, initial_layout=L, optimization_level=0) for k in ('P0', 'P1', 'X', 'Y')]
        sm = SamplerV2(mode=be); sm.options.execution.meas_type = 'kerneled'; sm.options.max_execution_time = 30
        j = sm.run(circs, shots=SHOTS); r = j.result()
        S0, S1 = np.asarray(r[0].data.s)[:, 0], np.asarray(r[1].data.s)[:, 0]; fs, cs = cut(S0, S1)
        sX, sY = fs(np.asarray(r[2].data.s)[:, 0]), fs(np.asarray(r[3].data.s)[:, 0])
        gen = {'gen': len(used), 'stone': stone, 'job': j.job_id(), 'stone_cut_check': cs, 'pond': []}
        for k, q in enumerate(pond):
            fb, ck = cut(np.asarray(r[0].data.b)[:, k], np.asarray(r[1].data.b)[:, k])
            if ck > 0.10: gen['pond'].append({'q': q, 'hops': hops[q], 'ruler_broken': ck}); continue
            v = {}
            for s_ in (0, 1):
                bx = fb(np.asarray(r[2].data.b)[:, k])[sX == s_]; by = fb(np.asarray(r[3].data.b)[:, k])[sY == s_]
                v[s_] = (complex(1 - 2 * bx.mean(), 1 - 2 * by.mean()), min(len(bx), len(by)))
            (v0, n0), (v1, n1) = v[0], v[1]
            ang = math.degrees(np.angle(v1 / v0)) if abs(v0) > .05 and abs(v1) > .05 else float('nan')
            sig = math.degrees(math.sqrt(1 / (n0 * max(abs(v0), .05) ** 2) + 1 / (n1 * max(abs(v1), .05) ** 2)))
            gen['pond'].append({'q': q, 'hops': hops[q], 'tilt_deg': ang, 'noise_deg': sig, 'knows': abs(ang) / sig if sig else 0, 'len0': abs(v0), 'len1': abs(v1)})
        live = [p for p in gen['pond'] if 'knows' in p and not math.isnan(p['knows']) and p['q'] not in used]
        best = max(live, key=lambda p: p['knows'], default=None); log.append(gen); json.dump(log, open(os.path.join(d, 'yeast.json'), 'w'), indent=1)
        print(f"gen {gen['gen']}: stone q{stone} -> " + ', '.join(f"q{p['q']}({p['hops']}h) {p['tilt_deg']:+.1f}deg/{p['knows']:.1f}" for p in sorted(live, key=lambda p: -p['knows'])[:5]), flush=True)
        if best is None or best['knows'] < 3: print('the yeast stops: nobody in this pond knows the stone', flush=True); break
        stone = best['q']
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'), flush=True)
if __name__ == "__main__":
    for seed in sys.argv[3].split(","): print("SEED", seed, flush=True); main(sys.argv[1], sys.argv[2], int(seed))
