"""synth_hebrew.py -- planted worlds through the SAME readings() as the real data (hebrew.py). Binomial shots per circuit, SHOTS each,
two copies analysed separately and pooled exactly as the real run. Worlds: none / linear / saturating / ringdown / below.
A FALSE CALL = a reading that resolves (ABOVE or BELOW) where the planted value is inside +-S, or resolves with the wrong sign.
A MISS = a planted resolvable value not resolved (reported as power, not as a false call)."""
import sys, json, numpy as np
sys.path.insert(0, '.'); import hebrew as H
DT = 4e-9
def dur(arm, N): return N * (H.LM + (H.LG if arm in ('MD', 'DD') else 0)) * DT
def world_kick(world, arm, N, kq):
    ro = arm in ('M', 'MD')
    if not ro: return np.zeros_like(kq)
    if world == 'none': return np.zeros_like(kq)
    if world == 'linear': return kq * N
    if world == 'saturating': return np.full_like(kq, -2.0)
    if world == 'ringdown': return kq * N if arm == 'M' else np.zeros_like(kq)
    if world == 'below': return np.full_like(kq, -0.02) * N
def coh_loss(world, arm, N): return np.exp(-0.004 * N) if (world == 'linear' and arm in ('M', 'MD')) else 1.0
def sim(world, rng, meta):
    nq = len(H.NB); th = rng.uniform(-np.pi, np.pi, nq); om = rng.normal(0, 2 * np.pi * 30e3, nq); r0 = rng.uniform(0.75, 0.95, nq); T2 = rng.uniform(60e-6, 200e-6, nq)
    kq = rng.normal(-0.5, 0.15, nq)
    bits = []
    for m in meta:
        if m['kind'] == 'kg':
            ns = len(H.S117); kk = rng.normal(-1.6, 0.4, ns) if m['arm'] == 'M' else np.zeros(ns); ph = np.radians(kk * 8) + 0.3
            p = (1 - 0.85 * (np.cos(ph) if m['setting'] == 'X' else np.sin(ph))) / 2; bits.append(rng.random((H.SHOTS, ns)) < p); continue
        t = dur(m['arm'], m['N']); ph = th + om * t + np.radians(world_kick(world, m['arm'], m['N'], kq)); r = r0 * np.exp(-t / T2) * coh_loss(world, m['arm'], m['N'])
        p = (1 - r * (np.cos(ph) if m['setting'] == 'X' else np.sin(ph))) / 2
        p1 = np.full(len(H.ONE), 0.97)
        bits.append(np.concatenate([rng.random((H.SHOTS, nq)) < p, rng.random((H.SHOTS, len(H.ONE))) < p1], axis=1))
    return bits, kq
EXPECT = {  # sign of the planted value per reading, 0 = inside +-S
    'none': dict(R1=0, R2=0, R2b=0, R3=0, R3b=0), 'linear': dict(R1=-1, R2=-1, R2b=0, R3=-1, R3b=-1),
    'saturating': dict(R1=-1, R2=-1, R2b=0, R3=0, R3b=0), 'ringdown': dict(R1=-1, R2=0, R2b=-1, R3=0, R3b=0),
    'below': dict(R1=0, R2=0, R2b=0, R3=0, R3b=0)}
KEYS = {'R1': 'R1 kick M-D (deg/readout)', 'R2': 'R2 kick MD-DD (deg/readout)', 'R2b': 'R2b delay effect (R1-R2 per neighbour)',
        'R3': 'R3 coherence ln(rM/rD) per readout', 'R3b': 'R3b coherence with delay'}
def final(r0, r1, rp):
    """two copies + pooled, as the real run: pooled outcome if the copies agree, else CANNOT_TELL"""
    return rp[3] if r0[3] == r1[3] else 'CANNOT_TELL'
if __name__ == '__main__':
    circs, meta = H.build(); rng = np.random.default_rng(20261024); DRAWS = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    tot = {}; kgp = 0
    for w in EXPECT:
        fc = miss = n = 0; out = {k: {} for k in KEYS}
        for d in range(DRAWS):
            b0, _ = sim(w, rng, meta); b1, _ = sim(w, rng, meta)
            r0 = H.readings(meta, b0, rng); r1 = H.readings(meta, b1, rng); rp = H.readings(meta + meta, b0 + b1, rng)
            if w == 'none': kgp += H.kg_reading(meta, b0, rng)['PASS']
            for k, name in KEYS.items():
                o = final(r0[name], r1[name], rp[name]); out[k][o] = out[k].get(o, 0) + 1; e = EXPECT[w][k]; n += 1
                if e == 0 and o in ('ABOVE', 'BELOW'): fc += 1
                elif e == -1 and o == 'ABOVE': fc += 1
                elif e == -1 and o != 'BELOW': miss += 1
        tot[w] = (fc, miss, n); print(f'{w:11s} false calls {fc}/{n}  misses {miss}  ' + '  '.join(f'{k}:{dict(sorted(v.items()))}' for k, v in out.items()), flush=True)
    F = sum(v[0] for v in tot.values()); N_ = sum(v[2] for v in tot.values())
    print(f'TOTAL false calls {F}/{N_} = {100 * F / N_:.1f} %   (worst world {max(100 * v[0] / v[2] for v in tot.values()):.1f} %)')
    print(f'KNOWN-GOOD rule on planted -1.6 deg/readout pack: PASS {kgp}/{DRAWS}')
