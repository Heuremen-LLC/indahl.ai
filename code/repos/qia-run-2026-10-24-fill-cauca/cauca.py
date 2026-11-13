"""cauca.py -- free calibration run for arXiv:2605.30676 (Univ. del Cauca; ibm_kingston). Analysis only (fire is fire_cauca.py).
Circuits: their SUBMITTED transpiled circuits, unchanged (theirs/job_metadata_L2.json = optimization level 2, identical to level 3; _L0.json = level 0),
N=2..9 on physical qubits 0..N-1 of ibm_kingston, first REPS=12 of their 20 identical repetitions per N, 2048 shots each. Target = all N bits one.
Arms: A = their L2 circuits, B = their L0 circuits. Jobs in ABBA order: 1=A, 2=B, 3=B, 4=A.  P_j(N) = fraction of shots reading the target.
Twin = THE PAPER's twin (twin_cauca.py: ZZ Pauli with probability = stated gate_error, per-qubit thermal relaxation, IBM-convention readout; reproduces their
Table A1 to <= 0.0035), fed from the backend record SAVED RIGHT BEFORE each job.
SCALE (fixed in advance from THEIR published numbers, Table A1 and figures_data): S_gap(N) = |published twin - hardware| at N = 0.093 0.105 0.095 0.069 0.025 0.032 0.114 0.160;
S_lvl(N) = |published raw(L2) - raw(L0)| from their figures_data_L2/L0. A reading is CANNOT_TELL at an N where its shot-noise null half-width exceeds that N's scale.
READINGS (four outcomes ABOVE / BELOW / CONSISTENT / CANNOT_TELL, 95 %, shot-noise null by binomial resampling of every target count, 2000 draws):
  R1 DRIFT  dA(N) = P_4(N) - P_1(N): the same circuits, the only difference is time. Scale S_gap (their own twin-vs-hardware gap is what drift is said to feed).
  R2 LEVEL  g(N) = mean(P_1,P_4) - mean(P_2,P_3) = L2 minus L0; ABBA cancels drift linear in job number and one step at the midpoint. Scale S_lvl.
  R3 KNOWN-GOOD their released counts must give their published raw means (L2 and L0, every N) to 1e-4 through this code.
  R4 TWIN   G(N) = mean over jobs 1,4 of [twin(record before job) - P_job(N)] against their published gap g0(N) (Table A1: twin - raw). ABOVE if today's gap interval is
            above g0, BELOW if below, CONSISTENT if g0 lies inside it. Scale S_gap. Also printed (no outcome): twin_4 - twin_1 (record movement), sign change N.
  R5 SHARE  max_N |dA|/S_gap and per-N |dA|/|G| printed, no outcome.
Every reading is the size of the term on THIS chip TODAY for THEIR circuits; none is a finding about their 29 Apr 2026 jobs."""
import json, sys, os, base64, zlib, io
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); NS = list(range(2, 10)); REPS = 12; SHOTS = 2048; NREP_THEIRS = 20
PUB_TWIN = np.array([0.8721, 0.8323, 0.8217, 0.8004, 0.7780, 0.7415, 0.7010, 0.6676])         # their Table A1 (L2), fixed
PUB_RAW = {L: np.array(json.load(open(f'{HERE}/theirs/figures_data_{L}.json'))['fidelity']['raw']['mean']) for L in ('L0', 'L2', 'L3')}
G0 = PUB_TWIN - PUB_RAW['L2']                                                                   # published twin - hardware
S_GAP = np.abs(G0); S_LVL = np.abs(PUB_RAW['L2'] - PUB_RAW['L0'])
ORDER = ['A', 'B', 'B', 'A']

def decode_counts(path):
    """their measurement_results.json -> per pub the number of shots reading all ones (data only: base64 + zlib + .npy, allow_pickle=False)."""
    d = json.load(open(path))['__value__']['pub_results']; out = []
    for pub in d:
        ba = pub['__value__']['data']['__value__']['fields']['c']['__value__']
        arr = np.load(io.BytesIO(zlib.decompress(base64.b64decode(ba['array']['__value__']))), allow_pickle=False)
        nb = int(ba['num_bits']); nbytes = arr.shape[1]
        v = np.zeros(arr.shape[0], dtype=np.int64)
        for i in range(nbytes): v = (v << 8) | arr[:, i].astype(np.int64)
        out.append((int((v == (1 << nb) - 1).sum()), arr.shape[0], nb))
    return out
def theirs_P(level):
    c = decode_counts(f'{HERE}/theirs/measurement_results_{level}.json'); P = []
    for i, N in enumerate(NS):
        rows = c[i * NREP_THEIRS:(i + 1) * NREP_THEIRS]; assert all(r[2] == N for r in rows)
        P.append(np.mean([z / n for z, n, _ in rows]))
    return np.array(P)
def known_good():
    out = {}
    for L in ('L2', 'L0'): out[L] = (theirs_P(L), PUB_RAW[L])
    ok = all(np.max(np.abs(a - b)) < 1e-4 for a, b in out.values()); return out, ok

# ---- a job = per-N target counts z and shot totals n (REPS circuits x 2048) ----
def job_from_raw(entries):
    """entries: list of dict(N, rep, counts{bitstring: count}) -> (z[8], n[8])"""
    z = np.zeros(8); n = np.zeros(8)
    for e in entries:
        k = e['N'] - 2; z[k] += e['counts'].get('1' * e['N'], 0); n[k] += sum(e['counts'].values())
    return z, n
def resample(z, n, rng, B=2000):
    p = z / n; return rng.binomial(n.astype(int)[None, :], p[None, :], size=(B, len(n))) / n[None, :]
def four(d, lo, hi, nlo, nhi, scale):
    cant = (nhi - nlo) / 2 > scale
    return np.where(cant, 'CANNOT_TELL', np.where(lo > nhi, 'ABOVE', np.where(hi < nlo, 'BELOW', 'CONSISTENT')))
def diff_reading(zx, nx, zy, ny, scale, rng, B=2000):
    """d = P_x - P_y; interval: resample each from its own p; null: both from the pooled p."""
    px, py = zx / nx, zy / ny; d = px - py
    s = resample(zx, nx, rng, B) - resample(zy, ny, rng, B); lo, hi = np.percentile(s - np.median(s, axis=0) + d, [2.5, 97.5], axis=0)
    pp = (zx + zy) / (nx + ny); null = resample(pp * nx, nx, rng, B) - resample(pp * ny, ny, rng, B); nlo, nhi = np.percentile(null, [2.5, 97.5], axis=0)
    return d, lo, hi, nlo, nhi, four(d, lo, hi, nlo, nhi, scale)
def pooled(jobs, idx):
    z = sum(jobs[i][0] for i in idx); n = sum(jobs[i][1] for i in idx); return z, n

def analyse(jobs, twins, rng):
    """jobs: 4 x (z, n) in submission order A B B A; twins: {1: twin(N)[8], 4: twin(N)[8]} built from the records saved before jobs 1 and 4."""
    P = [z / n for z, n in jobs]; L = []
    f = lambda a, w=7, p=4: ' '.join(f'{x:{w}.{p}f}' for x in a)
    L.append('N                  ' + ' '.join(f'{N:>7d}' for N in NS))
    for k in range(4): L.append(f'P job {k+1} ({ORDER[k]})      ' + f(P[k]))
    d, lo, hi, nlo, nhi, o = diff_reading(*jobs[3], *jobs[0], S_GAP, rng)
    L.append('R1 DRIFT dA=P4-P1  ' + f(d, 7, 4)); L.append('   interval lo     ' + f(lo)); L.append('   interval hi     ' + f(hi)); L.append('   null half-width ' + f((nhi - nlo) / 2)); L.append('   scale S_gap     ' + f(S_GAP))
    L.append('   outcome         ' + ' '.join(f'{x[:7]:>7s}' for x in o))
    zB, nB = pooled(jobs, [1, 2]); zA, nA = pooled(jobs, [0, 3])
    g, glo, ghi, gnlo, gnhi, go = diff_reading(zA, nA, zB, nB, S_LVL, rng)
    L.append('R2 LEVEL g=L2-L0    ' + f(g, 7, 4)); L.append('   interval lo     ' + f(glo)); L.append('   interval hi     ' + f(ghi)); L.append('   their published ' + f(PUB_RAW['L2'] - PUB_RAW['L0']))
    L.append('   outcome         ' + ' '.join(f'{x[:7]:>7s}' for x in go))
    # R4: today's twin-vs-hardware gap on arm A
    tw = (twins[1] + twins[4]) / 2; pA = zA / nA; G = tw - pA
    s = tw[None, :] - resample(zA, nA, rng); glo4, ghi4 = np.percentile(s, [2.5, 97.5], axis=0)
    cant = (ghi4 - glo4) / 2 > S_GAP; o4 = np.where(cant, 'CANNOT_TELL', np.where(glo4 > G0, 'ABOVE', np.where(ghi4 < G0, 'BELOW', 'CONSISTENT')))
    # (ABOVE means today's gap interval lies above theirs, BELOW below)
    L.append('R4 TWIN G=twin-hw   ' + f(G, 7, 3)); L.append('   interval lo     ' + f(glo4)); L.append('   interval hi     ' + f(ghi4)); L.append('   their g0        ' + f(G0))
    L.append('   outcome         ' + ' '.join(f'{x[:7]:>7s}' for x in o4))
    sc = lambda x: next((NS[i] for i in range(7) if x[i] < 0 <= x[i + 1]), None)
    L.append(f'   sign change of gap (neg to pos) between N = {sc(G)}-{(sc(G) or 0) + 1 if sc(G) else None}   (theirs: 6-7);  twin_4 - twin_1 (record movement): ' + f(twins[4] - twins[1], 7, 4))
    L.append('R5 SHARE |dA|/S_gap ' + f(np.abs(d) / S_GAP, 7, 3) + f'   max {np.max(np.abs(d) / S_GAP):.3f}')
    return L, dict(R1=list(o), R2=list(go), R4=list(o4))

def twins_from_records(paths):
    sys.path.insert(0, HERE); import twin_cauca as T
    circs = T.load_circuits('L2'); res = {}
    for k, p in paths.items():
        Pp = T.load_props(p); res[k] = np.array(T.target_prob_exact(circs, T.noise_model(Pp), Pp))
    return res
if __name__ == '__main__':
    out, ok = known_good()
    for L, (a, b) in out.items(): print(f'R3 KNOWN-GOOD {L}: mine', np.round(a, 4), 'published', np.round(b, 4), 'max|diff| %.1e' % np.max(np.abs(a - b)))
    print('R3 ->', 'PASS' if ok else 'FAIL')
    if len(sys.argv) > 1 and sys.argv[1] == '--real':
        rec = json.load(open(f'{HERE}/job_cauca.json')); rng = np.random.default_rng(24)
        jobs = [job_from_raw(json.load(open(f'{HERE}/raw_cauca_{j["label"]}.json'))) for j in rec['jobs']]
        tw = twins_from_records({1: f'{HERE}/props_cauca_before_1.json', 4: f'{HERE}/props_cauca_before_4.json'})
        print('\n'.join(analyse(jobs, tw, rng)[0]))
