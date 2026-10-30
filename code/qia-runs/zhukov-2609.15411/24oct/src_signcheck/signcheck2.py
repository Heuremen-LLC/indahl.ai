"""signcheck2.py -- follow-ups to signcheck.py: (i) pub pairing from SamplerV2 result metadata, (ii) per-round / per-job signed phase, (iii) all five science chains (does the sign flip on every chain or only on some?)."""
import gzip, json, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RUN = os.path.dirname(HERE); sys.path.insert(0, RUN)
import zhukov as Z
from qiskit import qpy, QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime import RuntimeDecoder
HIS = '/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_q3/2609.15411/data/IBM_DM_data_v2/raw/005'
P = lambda *a: print(*a, flush=True)
his_lib = qpy.load(open(HIS + '/circuits.qpy', 'rb')); rows5 = json.load(open(Z.TH + '/counts_005.json'))['rows']
rec = json.load(open(RUN + '/job_zhukov.json')); SID = rec['set_ids']; EIG1 = Z.EIG1
def ideal_lane(qc, path):
    idx = {q: k for k, q in enumerate(path)}; r = QuantumCircuit(3)
    for ins in qc.data:
        nm = ins.operation.name; qs = [qc.find_bit(x).index for x in ins.qubits]
        if nm in ('barrier', 'measure') or not any(q in idx for q in qs): continue
        assert all(q in idx for q in qs); (getattr(r, nm)(*ins.operation.params, *[idx[q] for q in qs]) if ins.operation.params else getattr(r, nm)(*[idx[q] for q in qs]))
    pr = Statevector.from_label('000').evolve(r).probabilities(); p = np.zeros(8)
    for a in range(8): b = [(a >> k) & 1 for k in range(3)]; p[(b[0] << 2) | (b[1] << 1) | b[2]] += pr[a]
    return p
# (i) pairing: our job results' circuit_metadata pub_index vs the set index we assumed (needs the full results -> re-fetch read-only)
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run')); from sweep import service
s = service(); bad = 0; n = 0
for j in rec['jobs']:
    res = s.job(j['job_id']).result()
    for pos, i in enumerate(j['order']):
        md = res[pos].metadata.get('circuit_metadata', {}) if hasattr(res[pos], 'metadata') else {}
        sid = SID[i]
        if sid.startswith('X:'): continue
        row = int(sid.split(':')[1]); got = md.get('pub_index'); spec_ok = md.get('spec') == his_lib[row].metadata['spec'] if sid.startswith('005') else True; n += 1
        if got != row or not spec_ok: bad += 1
P(f'(i) result-metadata pub_index (and spec for 005) equals the assumed set row for {n - bad} of {n} his-circuit results over 4 jobs (mismatches {bad})')
# (ii)+(iii) per chain, per round/job
ours = {j: np.load(RUN + f'/raw_zhukov_{j}.npz')['codes'] for j in Z.ORDER}
setidx = {}
for i, sid in enumerate(SID):
    if sid.startswith('005:'): row = int(sid.split(':')[1]); sp = his_lib[row].metadata['spec']; setidx.setdefault((sp['method'], sp['basis']), []).append((i, row, sp['round']))
def ph(hx, hy, refx, refy):
    x, y = (hx / hx.sum()) @ EIG1, (hy / hy.sum()) @ EIG1; return x, y, float(np.degrees(np.angle((x + 1j*y) * np.conj(refx + 1j*refy))))
P('\n(ii)/(iii) signed phase error (deg), strang8 r=8 and exact, Jt=4/3, every science chain: IDEAL(my statevector) | HIS round0 round1 | OURS jobs A1 B1 B2 A2')
for method in ('strang8', 'exact'):
    for lane in Z.SCI:
        k = Z.LANES.index(lane); path = Z.PATH[lane]
        refx = np.array(rows5[setidx[(method, 'XXX')][0][1]]['lanes'][str(lane)]['hamiltonian_probabilities']) @ EIG1; refy = np.array(rows5[setidx[(method, 'YYY')][0][1]]['lanes'][str(lane)]['hamiltonian_probabilities']) @ EIG1
        px = ideal_lane(his_lib[setidx[(method, 'XXX')][0][1]], path) @ EIG1; py = ideal_lane(his_lib[setidx[(method, 'YYY')][0][1]], path) @ EIG1
        ide = float(np.degrees(np.angle((px + 1j*py) * np.conj(refx + 1j*refy))))
        hr = []
        for rd in (0, 1):
            hx = sum(np.array(rows5[r]['lanes'][str(lane)]['counts'], float) for _, r, q in setidx[(method, 'XXX')] if q == rd); hy = sum(np.array(rows5[r]['lanes'][str(lane)]['counts'], float) for _, r, q in setidx[(method, 'YYY')] if q == rd)
            hr.append(ph(hx, hy, refx, refy)[2])
        orr = []
        for j in Z.ORDER:
            hx = sum(Z.counts8(ours[j][i, :, k]) for i, r, q in setidx[(method, 'XXX')]); hy = sum(Z.counts8(ours[j][i, :, k]) for i, r, q in setidx[(method, 'YYY')]); orr.append(ph(hx, hy, refx, refy)[2])
        P(f'  {method:7s} lane {lane} {path}: ideal {ide:+7.2f} | his {hr[0]:+7.2f} {hr[1]:+7.2f} | ours {orr[0]:+7.2f} {orr[1]:+7.2f} {orr[2]:+7.2f} {orr[3]:+7.2f}')
