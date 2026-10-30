"""signcheck.py -- settle the sign of the chain-C phase error (Jt=4/3, lane 3 = qubits [69,68,67]). Zero QPU, nothing fired, committed files untouched.
Run: ~/bones-forge/qvenv/bin/python -I signcheck.py   (reads fetch_ours.py output ours_chainC_bitarrays_t3.npz, his raw/005 files, zhukov.py as a module)"""
import io, gzip, json, os, sys, itertools, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RUN = os.path.dirname(HERE); sys.path.insert(0, RUN)
import zhukov as Z
from qiskit import qpy, QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime import RuntimeDecoder
HIS = '/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_q3/2609.15411/data/IBM_DM_data_v2/raw/005'
P = lambda *a: print(*a, flush=True)
LANE = 3; PATH = [69, 68, 67]; EIG1 = Z.EIG1

# ---- the two decoders under test
def decode_ours(v):          # fire_zhukov.decode, copied verbatim: SamplerV2 BitArray integer (bit j = clbit j) -> code, clbit0 = MSB
    v = v.astype(np.uint8); return ((v & 1) << 2) | (v & 2) | ((v >> 2) & 1)
def decode_counts_path(counts):   # SamplerV2 get_counts keys: string, clbit 0 RIGHTMOST. -> histogram over codes (x1 = clbit0 = MSB) by reversing the string
    h = np.zeros(8)
    for k, n in counts.items(): h[int(k[::-1], 2)] += n
    return h
def encode_his(bits_by_pos):      # re-encode physical per-shot bits (position 0,1,2 = path[0..2]) into HIS shot code: spin1 = path[0] = MSB  (DATA_FORMAT / basis_order)
    return (bits_by_pos[0].astype(np.uint8) << 2) | (bits_by_pos[1].astype(np.uint8) << 1) | bits_by_pos[2].astype(np.uint8)
def decode_his_format(codes):     # his format -> physical bits by position, as Z.EIG1 / his analysis read it: position 0 = bit 2 of the code
    return [(codes >> 2) & 1, (codes >> 1) & 1, codes & 1]

# ---- 1. circuits: his copy and ours, measure maps vs his experiment.json lane paths
def meas_map(qc):
    d = {}
    for ins in qc.data:
        if ins.operation.name == 'measure':
            q = qc.find_bit(ins.qubits[0]).index; cb = qc.find_bit(ins.clbits[0]); (reg, pos), = [(r.name, p) for r, p in cb.registers]; d[(reg, pos)] = q
    return d
his_lib = qpy.load(open(HIS + '/circuits.qpy', 'rb')); our_lib = qpy.load(open(RUN + '/circuits_zhukov.qpy', 'rb'))
rec = json.load(open(RUN + '/job_zhukov.json')); SID = rec['set_ids']
CC = {}   # (method, basis) -> list of (our set index, his pub row)
for i, sid in enumerate(SID):
    if sid.startswith('005:'):
        row = int(sid.split(':')[1]); s = his_lib[row].metadata['spec']; CC.setdefault((s['method'], s['basis']), []).append((i, row))
exp_paths = json.load(open(HIS + '/experiment.json'))['paths']
P('== 1. MEASURE MAPS (clbit position -> physical qubit)')
P(f'his experiment.json lane paths: lane3 = {exp_paths[3]}; zhukov.py PATH[3] = {Z.PATH[3]}')
allsame = True
for key, lst in sorted(CC.items()):
    for i, row in lst:
        mh, mo = meas_map(his_lib[row]), meas_map(our_lib[i]); lane3 = [mh[('t3', k)] for k in range(3)]
        same_circ = (his_lib[row] == our_lib[i]); ok = (mh == mo) and lane3 == exp_paths[3] == PATH
        allsame &= ok and same_circ
        P(f'  {key} set {i} (his pub {row}): his t3[0..2] -> {lane3}; ours t3[0..2] -> {[mo[("t3",k)] for k in range(3)]}; all 18 measure maps equal: {mh==mo}; circuit objects equal: {same_circ}')
P(f'  -> measure map identical in both copies and equal to the lane path: {allsame}')
# every lane path against the measure map
for lane in Z.LANES:
    m = meas_map(his_lib[80]); assert [m[(f't{lane}', k)] for k in range(3)] == exp_paths[lane] == Z.PATH[lane]
P('  all six lane registers: tK[j] <- path[j] confirmed on the qpy (his == ours == zhukov.PATH)')

# ---- 2. my own statevector for the lane-3 part of a circuit
def ideal_lane3(qc):
    """reduce the 156-qubit circuit to qubits 69,68,67 (instruction order kept), check nothing couples them to other qubits, simulate. returns p over codes (x1 = q69 = MSB)."""
    idx = {q: k for k, q in enumerate(PATH)}; r = QuantumCircuit(3); n2 = 0
    for ins in qc.data:
        nm = ins.operation.name; qs = [qc.find_bit(x).index for x in ins.qubits]
        if nm in ('barrier', 'measure'): continue
        if any(q in idx for q in qs):
            assert all(q in idx for q in qs), f'{nm} couples lane-3 qubit to {qs}'
            getattr(r, nm)(*ins.operation.params, *[idx[q] for q in qs]) if ins.operation.params else getattr(r, nm)(*[idx[q] for q in qs]); n2 += (len(qs) == 2)
    sv = Statevector.from_label('000').evolve(r); pr = sv.probabilities()      # index bit k = reduced qubit k = path[k]
    p = np.zeros(8)
    for a in range(8):
        b = [(a >> k) & 1 for k in range(3)]; p[(b[0] << 2) | (b[1] << 1) | b[2]] += pr[a]
    return p, n2
rows5 = json.load(open(Z.TH + '/counts_005.json'))['rows']
def ref_h(row): return np.array(rows5[row]['lanes']['3']['hamiltonian_probabilities'])
def his_ideal(row): return np.array(rows5[row]['lanes']['3']['ideal_probabilities'])
def c1(p_x, p_y, ref_x, ref_y):
    x, y = p_x @ EIG1, p_y @ EIG1; rx, ry = ref_x @ EIG1, ref_y @ EIG1
    return x, y, rx, ry, float(np.degrees(np.angle((x + 1j*y) * np.conj(rx + 1j*ry))))
P('\n== 2. IDEAL (noiseless) VALUE FROM MY OWN STATEVECTOR, lane 3, Jt=4/3')
IDEAL = {}
for method in ('strang8', 'exact'):
    pr = {}
    for b in ('XXX', 'YYY'):
        i, row = CC[(method, b)][0]; p, n2 = ideal_lane3(his_lib[row]); pr[b] = (p, row)
        P(f'  {method} {b} pub {row}: {n2} CZ on lane 3; max|my p - his stored ideal_probabilities| = {np.abs(p - his_ideal(row)).max():.2e}')
    x, y, rx, ry, e = c1(pr['XXX'][0], pr['YYY'][0], ref_h(pr['XXX'][1]), ref_h(pr['YYY'][1]))
    IDEAL[method] = (x, y, rx, ry, e)
    P(f'  {method}: ideal <X1>={x:+.4f} <Y1>={y:+.4f}; exact-H reference <X1>={rx:+.4f} <Y1>={ry:+.4f}; ideal signed phase error vs exact H = {e:+.2f} deg')

# ---- 3. the two decode paths on REAL data
P('\n== 3a. HIS data: his runtime_result BitArrays pushed through OUR decoders, against his shots_codes.npz')
with gzip.open(HIS + '/runtime_result.json.gz', 'rt') as f: raw = json.load(f, cls=RuntimeDecoder)
hc = np.load(HIS + '/shots_codes.npz')['codes']; ok_all = True
for key, lst in sorted(CC.items()):
    for i, row in lst:
        ba = raw[row].data.t3; v = ba.array[:, 0]; d1 = decode_ours(v); same1 = np.array_equal(d1, hc[row, :, 3])
        cnt = ba.get_counts(); h = decode_counts_path(cnt); same2 = np.array_equal(h, np.bincount(hc[row, :, 3], minlength=8)); bitsB = decode_his_format(hc[row, :, 3])
        reenc = np.array_equal(encode_his(bitsB), hc[row, :, 3]); ok_all &= same1 and same2 and reenc
        P(f'  {key} pub {row}: our decode(BitArray) == his codes: {same1}; get_counts-string path histogram == his counts: {same2}; his-code re-encode round trip: {reenc}')
P(f'  -> our decoders reproduce his shot codes bit for bit on all 8 circuits: {ok_all}')

P('\n== 3b. OUR data: true SamplerV2 output (re-fetched, read-only) through BOTH paths, against the codes zhukov.py used (raw_zhukov_*.npz)')
oz = np.load(HERE + '/ours_chainC_bitarrays_t3.npz'); jobs = Z.ORDER; ours_codes = {j: np.load(RUN + f'/raw_zhukov_{j}.npz')['codes'] for j in jobs}; ok2 = True
HC = {}   # (job, method, basis) -> histogram via counts path
for j in jobs:
    for key, lst in CC.items():
        h = np.zeros(8)
        for i, row in lst:
            v = oz[f'{j}|{i}|v']; counts = json.loads(str(oz[f'{j}|{i}|counts']))
            a = np.array_equal(decode_ours(v), ours_codes[j][i, :, 3]); hh = decode_counts_path(counts); b = np.array_equal(hh, np.bincount(ours_codes[j][i, :, 3], minlength=8))
            # path 2: re-encode the physical bits (position = clbit order) into his convention and read them with his-format bit order
            bits = [(v >> k) & 1 for k in range(3)]; his_codes = encode_his(bits); c = np.array_equal(his_codes, ours_codes[j][i, :, 3]); ok2 &= a and b and c; h += hh
        HC[(j,) + key] = h
P(f'  all 32 circuit-job pairs: decode(BitArray)==npz codes, counts path==npz histogram, re-encode(his format)==npz codes: {ok2}')
P('  example get_counts keys (clbit0 rightmost), job A1 set %d: %s' % (CC[("strang8","XXX")][0][0], list(json.loads(str(oz["A1|%d|counts" % CC[("strang8","XXX")][0][0]])).items())[:4]))

# ---- 4. the estimator on each path, signed, vs ideal
def phase(hx, hy, method):
    x, y = (hx / hx.sum()) @ EIG1, (hy / hy.sum()) @ EIG1
    ref = IDEAL[method]; return x, y, float(np.degrees(np.angle((x + 1j*y) * np.conj(ref[2] + 1j*ref[3]))))
P('\n== 4. SIGNED PHASE ERROR (zhukov.c1_from_counts estimator, same function, same exact-H reference), by data source')
his_h = {}; 
for method in ('strang8', 'exact'):
    hx = sum(np.array(rows5[r]['lanes']['3']['counts'], float) for _, r in CC[(method, 'XXX')]); hy = sum(np.array(rows5[r]['lanes']['3']['counts'], float) for _, r in CC[(method, 'YYY')])
    e = Z.c1_from_counts(hx, hy, Z.chainC_ref(method)); x, y, e2 = phase(hx, hy, method)
    ours_h = {b: sum(HC[(j, method, b)] for j in jobs) for b in ('XXX', 'YYY')}
    eo = Z.c1_from_counts(ours_h['XXX'], ours_h['YYY'], Z.chainC_ref(method)); xo, yo, e2o = phase(ours_h['XXX'], ours_h['YYY'], method)
    P(f'  {method}: IDEAL {IDEAL[method][4]:+7.2f} | HIS data <X1>={x:+.3f} <Y1>={y:+.3f} -> {e[0]:+7.2f} (zhukov.py) {e2:+7.2f} (this script) | OURS (counts path, 4 jobs pooled) <X1>={xo:+.3f} <Y1>={yo:+.3f} -> {eo[0]:+7.2f} (zhukov.py) {e2o:+7.2f} (this script)')
    for j in jobs:
        a = Z.c1_from_counts(HC[(j, method, 'XXX')], HC[(j, method, 'YYY')], Z.chainC_ref(method)); P(f'      job {j}: {a[0]:+7.2f} deg (se {a[1]:.2f}), |C1| {a[2]:.3f}')
    his_h[method] = (hx, hy); 
P('\n== 5. BIT-ORDER SCAN: total-variation distance of each data set from the MY-statevector ideal histogram under all 6 bit permutations of the code (strang8 and exact, XXX and YYY pooled)')
perms = list(itertools.permutations(range(3)))
def permute(h, pm): 
    o = np.zeros(8)
    for c in range(8):
        b = [(c >> 2) & 1, (c >> 1) & 1, c & 1]; nb = [b[pm[0]], b[pm[1]], b[pm[2]]]; o[(nb[0] << 2) | (nb[1] << 1) | nb[2]] += h[c]
    return o
res = {}
for src in ('HIS', 'OURS'):
    P(f'  {src}:')
    for pm in perms:
        tv = []
        for method in ('strang8', 'exact'):
            for b in ('XXX', 'YYY'):
                p, _ = ideal_lane3(his_lib[CC[(method, b)][0][1]])
                h = sum(np.array(rows5[r]['lanes']['3']['counts'], float) for _, r in CC[(method, b)]) if src == 'HIS' else sum(HC[(j, method, b)] for j in jobs)
                tv.append(0.5 * np.abs(permute(h / h.sum(), pm) - p).sum())
        res[(src, pm)] = np.mean(tv); P(f'     bit order {pm}{"  <- as decoded" if pm == (0,1,2) else ""}: mean TV {np.mean(tv):.4f}')
    best = min(perms, key=lambda pm: res[(src, pm)]); P(f'     best fit: {best}')
# bit-flip-to-sign: what if ours were read with the order reversed
P('\n== 6. WHAT A DECODE FLIP WOULD DO (control): our strang8 data decoded with the code bits reversed (x1<->x3) and with the clbit order reversed')
for lab, f in (('reversed code bits (x1<->x3)', lambda h: permute(h, (2, 1, 0))), ('identity', lambda h: h)):
    ours_h = {b: f(sum(HC[(j, 'strang8', b)] for j in jobs)) for b in ('XXX', 'YYY')}
    e = Z.c1_from_counts(ours_h['XXX'], ours_h['YYY'], Z.chainC_ref('strang8')); P(f'  ours strang8, {lab}: {e[0]:+.2f} deg, |C1| {e[2]:.3f}')
    hh = {b: f(sum(np.array(rows5[r]['lanes']['3']['counts'], float) for _, r in CC[('strang8', b)])) for b in ('XXX', 'YYY')}
    e = Z.c1_from_counts(hh['XXX'], hh['YYY'], Z.chainC_ref('strang8')); P(f'  his  strang8, {lab}: {e[0]:+.2f} deg, |C1| {e[2]:.3f}')
