"""keystone.py -- circuits, corrections, analysis and synthetic for the keystone run (PLAN_KEYSTONE.md.text). 31 Oct 2026.
Question: of what a mid-circuit readout of a 39-qubit pack costs the untouched qubits next to it, how much is a phase that a per-qubit
virtual-Z correction gives back, and how much is lost. Three setups from the work of the groups we cite, two chips (ibm_kingston, ibm_marrakesh):
  S  spectators: all 117 untouched qubits on the equator, N = 8 looks (the Hebrew University / UChicago question: do the untouched qubits stay put?)
  P  Bell pairs: 48 untouched pairs + 21 singles, N = 4 looks (the X-part concurrence cost of our earlier paper)
  C  clock: a Page-Wootters history state (2 clock qubits, 4 ticks) with the look in the MIDDLE of the build, N = 4 looks, 27 settings
Arms (same job, interleaved): D idle (the pack idles exactly L per step) | DE idle + the same echo as ME (the none for ME) | M look (the pack is
read out each step) | MC look + correction from the committed 21 Oct table | MF look + correction measured minutes before in calibration job C |
ME look + symmetric echo (X on the untouched targets after step N/2 and after step N).
Correction = rz(-kick_q) on every untouched qubit after every look step (virtual, zero duration). No qubit is selected or dropped by its kick."""
import json, os, sys, itertools
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pooters as PW
CR = os.path.expanduser('../earlier_runs/control_run'); sys.path.insert(0, CR)
from analyze import bits, wrap, conc

ARMS = ['D', 'DE', 'M', 'MC', 'MF', 'ME']
NONE = {'M': 'D', 'MC': 'D', 'MF': 'D', 'ME': 'DE'}   # the like-for-like none of each readout arm
N_S, N_P, N_C = 8, 4, 4
SET_S = ['X', 'Y', 'Z0']
SET_P = ['ZZ', 'XX', 'YY', 'XY', 'YX']
SET_C = PW.SETTINGS                       # 27, letter i = basis of (c0, c1, s)
SHOTS = {'S': 2000, 'P': 2500, 'C': 1000, 'CAL': 4000}
CLOCK = {'ibm_kingston': (3, 16, 23)}     # (c0, s, c1); marrakesh chosen by choose_clock() under the plan's rule
THETA = PW.THETA

def table(chip):
    return json.load(open(f'{HERE}/committed_kicks_{chip}.json'))
def committed_corr(chip, N):
    """deg per step: the committed unwrapped kick at the dose used (N=4 -> field 8, N=8 -> field 6)"""
    K = table(chip)['kicks_deg_per_readout']; f = 8 if N == 4 else 6
    return {int(q): v[f] for q, v in K.items()}
def fresh_corr(chip, N):
    F = json.load(open(f'{HERE}/fresh_kicks_{chip}.json'))['kicks']; return {int(q): v[f'k{N}'] for q, v in F.items()}

def choose_clock(chip, coupling_edges, rec_ok, edge_ok=lambda a, b: True):
    """Rule fixed in the plan before any job: paths c0 - s - c1 of untouched qubits (two coupled edges), each of the three with a resolved
    committed kick (95 % band excludes 0) and N=2/N=4/N=8 kicks within 2 deg of each other, |kick| <= 20 deg/readout, record gates passed
    (rec_ok: readout_error < 0.05 in today's record; edge_ok: CZ gate_error < 0.01 on both edges). c0 = the endpoint with the smaller |kick|. Pick the path with the largest |kick(c1)| - |kick(c0)|; ties -> lowest (s, c0, c1)."""
    K = table(chip)['kicks_deg_per_readout']; S = set(int(q) for q in K)
    def good(q):
        v = K[str(q)]; ks = (v[6], v[7], v[8])
        return (v[2] < 0 or v[1] > 0) and max(ks) - min(ks) <= 2 and abs(v[6]) <= 20 and rec_ok(q)
    adj = {}
    for a, b in coupling_edges: adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    best = None
    for s in sorted(S):
        if not good(s): continue
        nb = sorted(x for x in adj.get(s, ()) if x in S and good(x))
        for a, b in itertools.combinations(nb, 2):
            if not (edge_ok(a, s) and edge_ok(s, b)): continue
            c0, c1 = (a, b) if abs(K[str(a)][6]) <= abs(K[str(b)][6]) else (b, a)
            score = abs(K[str(c1)][6]) - abs(K[str(c0)][6]); key = (-score, s, c0, c1)
            if best is None or key < best[0]: best = (key, (c0, s, c1))
    if best is None or -best[0][0] < 5.0: return None   # HOLD (referee 31 Oct): never fall silently to a near-kick-free triple
    return best[1]

def rot(qc, q, b):
    if b == 'X': qc.h(q)
    elif b == 'Y': qc.sdg(q); qc.h(q)
    elif b == 'Z0': qc.sxdg(q)

def look_block(qc, E, N, arm, targets, corr, L_dt, regs):
    """one block of N steps. corr: {qubit: deg per step} used in MC/MF; echo X on targets after step N/2 and N in ME."""
    for k in range(N):
        if arm in ('D', 'DE'):
            for q in E: qc.delay(L_dt, q, unit='dt')
        else: qc.measure(E, regs[k])
        qc.barrier()
        if arm in ('MC', 'MF'):
            for q in targets: qc.rz(-np.radians(corr[q]), q)
        if arm in ('ME', 'DE') and (k + 1) in (N // 2, N): qc.x(targets)
        qc.barrier()

def circ_S(n, E, S, arm, st, corr, L_dt, N=N_S):
    regs = [ClassicalRegister(len(E), f'm{k}') for k in range(N)]; fin = ClassicalRegister(len(S), 'fin'); qc = QuantumCircuit(n)
    for r in regs: qc.add_register(r)
    qc.add_register(fin)
    for q in S: qc.sx(q)
    qc.barrier(); look_block(qc, E, N, arm, S, corr, L_dt, regs)
    for q in S: rot(qc, q, st)
    for i, q in enumerate(S): qc.measure(q, fin[i])
    return qc

def circ_P(n, E, pairs, singles, arm, st, corr, L_dt, N=N_P):
    regs = [ClassicalRegister(len(E), f'm{k}') for k in range(N)]; fin = ClassicalRegister(2 * len(pairs) + len(singles), 'fin'); qc = QuantumCircuit(n)
    for r in regs: qc.add_register(r)
    qc.add_register(fin)
    for a, c in pairs: qc.h(a); qc.cx(a, c)
    for q in singles: qc.sx(q)
    qc.barrier(); tg = [q for p in pairs for q in p] + list(singles); look_block(qc, E, N, arm, tg, corr, L_dt, regs)
    for a, c in pairs: rot(qc, a, st[0]); rot(qc, c, st[1])
    for q in singles: rot(qc, q, st[0])
    for i, (a, c) in enumerate(pairs): qc.measure(a, fin[2 * i]); qc.measure(c, fin[2 * i + 1])
    for i, q in enumerate(singles): qc.measure(q, fin[2 * len(pairs) + i])
    return qc

def circ_C(n, E, clock, arm, st, corr, L_dt, N=N_C):
    """history state with the look in the MIDDLE: H c0, H c1, CRY(theta) c0->s, [look block], CRY(2 theta) c1->s, tomography.
    fin bits: 0 = c0, 1 = c1, 2 = s (as the 24 Oct run)."""
    c0, s, c1 = clock
    regs = [ClassicalRegister(len(E), f'm{k}') for k in range(N)]; fin = ClassicalRegister(3, 'fin'); qc = QuantumCircuit(n)
    for r in regs: qc.add_register(r)
    qc.add_register(fin)
    qc.h(c0); qc.h(c1); qc.cry(THETA, c0, s); qc.barrier()
    look_block(qc, E, N, arm, [c0, s, c1], corr, L_dt, regs)
    qc.cry(2 * THETA, c1, s); qc.barrier()
    for q, b in zip((c0, c1, s), st): rot(qc, q, b)
    qc.measure(c0, fin[0]); qc.measure(c1, fin[1]); qc.measure(s, fin[2])
    return qc

def keys_main():
    """job order A: per setting, arms in ARMS order; parts S, P, C interleaved setting by setting"""
    ks = []
    for st in SET_S:
        for a in ARMS: ks.append(('S', a, st))
    for st in SET_P:
        for a in ARMS: ks.append(('P', a, st))
    for st in SET_C:
        for a in ARMS: ks.append(('C', a, st))
    return ks
def keys_cal(): return [('CAL', a, st, N) for N in (4, 8) for st in ('X', 'Y') for a in ('D', 'M')]

# ---------------- analysis ----------------
def outcome(lo, hi, ref=0.0, ok=True):
    if not ok or not (np.isfinite(lo) and np.isfinite(hi)): return 'CANNOT_TELL'
    return 'ABOVE' if lo > ref else 'BELOW' if hi < ref else 'CONSISTENT'
def boot_med(x, rng, B=2000, band=(0.5, 99.5)):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if len(x) < 8: return np.nan, np.nan, np.nan, len(x)
    b = np.median(rng.choice(x, (B, len(x))), axis=1); lo, hi = np.percentile(b, band); return float(np.median(x)), float(lo), float(hi), len(x)

def spect_expect(arrs, nq):
    """arrs: list of packed fin arrays (shots x bytes) -> per-qubit <1 - 2 b>"""
    a = np.concatenate(arrs); return np.array([(1 - 2 * bits(a, k)).mean() for k in range(nq)])
def spect_p1(arrs, nq):
    a = np.concatenate(arrs); return np.array([bits(a, k).mean() for k in range(nq)])

def fresh_from_cal(chip, Z, Scal):
    """Z: {('CAL', arm, st, N): [packed arrays]} from job C. Branch rule (plan): t4 nearest 4 x committed N=4 kick; t8 nearest 2 x t4."""
    K = table(chip)['kicks_deg_per_readout']; out = {}
    ph = {}
    for N in (4, 8):
        for a in ('D', 'M'):
            x = spect_expect(Z[('CAL', a, 'X', N)], len(Scal)); y = spect_expect(Z[('CAL', a, 'Y', N)], len(Scal)); ph[(a, N)] = (np.arctan2(y, x), np.hypot(x, y))
    near = lambda x, ref: x + 2 * np.pi * np.round((ref - x) / (2 * np.pi))
    for i, q in enumerate(Scal):
        t4 = near(wrap(ph[('M', 4)][0][i] - ph[('D', 4)][0][i]), np.radians(4 * K[str(q)][8]))
        t8 = near(wrap(ph[('M', 8)][0][i] - ph[('D', 8)][0][i]), 2 * t4)
        out[int(q)] = dict(k4=round(float(np.degrees(t4) / 4), 4), k8=round(float(np.degrees(t8) / 8), 4), cohD8=round(float(ph[('D', 8)][1][i]), 4))
    return out

def read_S(Zc, S, rng):
    """Zc: {(arm, st): [arrays]} for the copies being read. Per-qubit phase per readout vs D, |residual|, P1 excess, coherence."""
    nq = len(S); r = {}
    ph, co, p1 = {}, {}, {}
    for a in ARMS:
        x = spect_expect(Zc[(a, 'X')], nq); y = spect_expect(Zc[(a, 'Y')], nq); ph[a] = np.arctan2(y, x); co[a] = np.hypot(x, y)
        p1[a] = spect_p1(Zc[(a, 'Z0')], nq)
    for a, nn in NONE.items():
        r[a] = dict(kick=np.degrees(wrap(ph[a] - ph[nn])) / N_S, abskick=np.abs(np.degrees(wrap(ph[a] - ph[nn]))) / N_S,
                    p1=p1[a] - p1[nn], coh=co[a] - co[nn])
    for a in ('D', 'DE'): r[a] = dict(p1abs=p1[a], coh=co[a], ph=ph[a])
    return r

def read_P(Zc, pairs, rng):
    np_ = len(pairs); out = {}
    for a in ARMS:
        e = {}
        for st in SET_P:
            arr = np.concatenate(Zc[(a, st)])
            if st == 'ZZ':
                e['ZZ'] = [np.array([((bits(arr, 2 * i) == u) & (bits(arr, 2 * i + 1) == v)).mean() for (u, v) in ((0, 0), (0, 1), (1, 0), (1, 1))]) for i in range(np_)]
            else:
                e[st] = [((1 - 2 * bits(arr, 2 * i)) * (1 - 2 * bits(arr, 2 * i + 1))).mean() for i in range(np_)]
        C = np.array([conc({k: e[k][i] for k in SET_P}) for i in range(np_)])
        PHI = np.array([np.arctan2(e['XY'][i] + e['YX'][i], e['XX'][i] - e['YY'][i]) for i in range(np_)])   # phase of the 00-11 coherence
        Fb = np.array([(e['ZZ'][i][0] + e['ZZ'][i][3] + (e['XX'][i] - e['YY'][i]) / 2) / 2 for i in range(np_)])   # <Phi+|rho|Phi+>
        out[a] = dict(conc=C, fbell=Fb, phi=PHI)
    return out

def counts3(arrs):
    a = np.concatenate(arrs); c = {}
    b0, b1, b2 = bits(a, 0), bits(a, 1), bits(a, 2)
    for x0, x1, xs in itertools.product((0, 1), repeat=3):
        n = int(((b0 == x0) & (b1 == x1) & (b2 == xs)).sum())
        if n: c[f'{xs}{x1}{x0}'] = n
    return c

def ideal_mid_E(theta=THETA):
    return PW.E_IDEAL   # the look is in the middle but the ideal final state is the same history state

def end_correct(E, tot_deg):
    """apply the TOTAL committed phase back at the END (tomography frame), c0, c1, s order: the pre-registered K7 comparison"""
    M = PW.kron3(PW.qmap(np.radians(-tot_deg[0]), 1), PW.qmap(np.radians(-tot_deg[1]), 1), PW.qmap(np.radians(-tot_deg[2]), 1)); return M @ E

def read_C(Cc, tot_end):
    """Cc: {arm: {setting: counts}}. Returns F per arm, and F of M with the committed total phase put back at the end (K7)."""
    F = {a: PW.fidelity(PW.evec(PW.to_P(Cc[a]))) for a in ARMS}
    F['M_endcorr'] = PW.fidelity(end_correct(PW.evec(PW.to_P(Cc['M'])), tot_end))
    return F
