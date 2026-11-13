"""THE STOPWATCH RUN (Bones, by hand, 2026-10-02). Wayfinder: "You had a stopwatch for a qubit this entire time... you've been measuring time with our
own ruler. Now do the opposite. What happens to time when one qubit looks at another? What happens to the measurement measuring time by the qubit and
time by the observer qubit and time by the witness measurement?"  (His standing order of 9/28: listen to the clocks INSIDE the system.)
THREE TIMES ON ONE EVENT, 60 us long:
  OURS      -- the 60 us we lay down from outside, and how long we TELL the emitter to stay ON (0 / 20 / 40 / 60 us: we park it OFF after that).
  THE BIT'S -- the emitter's own last look (what is left of it).
  THE WITNESS'S -- every bit wired to an emitter is held as a CLOCK (set half-way, left to tick, read on two hands a quarter-turn apart). Its hand turns
                   at a rate that depends on whether its neighbour is ON: it times the emitter's ON-ness from inside. Bits wired to no emitter are FAR clocks.
ARMS (emitters E; everyone else N):
  A0  E OFF the whole time                 N = clocks      A1  E ON for 20 us then parked      N = clocks
  A2  E ON for 40 us then parked           N = clocks      A3  E ON the whole 60 us            N = clocks      (each A arm twice: the clock's two hands)
  B1  E ON the whole 60 us                 N = OFF (nobody holding a clock)
  B2  E ON the whole 60 us                 N = ON
  F0 / F1  everyone OFF / everyone ON, looked at with no wait (the frame)
The chip's WIRING is read from its static configuration at the instant of firing (the same read that gives its size; logged). Emitters are drawn so no two
are within two links; ibm_pittsburgh, every bit plays a part. One read = 12 circuits x 300 shots. No number of ours is written for it.
Brake: 3.0 s overhead + sequence, 1.25 margin, capped at 12 s.
  python witness.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
from collections import deque
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 80; SHOTS_J = 300; CAP_S = 12; T_US = 60; SEED_ROLES = 20261810
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261810 + k
common.code_files = lambda r: ['common.py', 'live.py', 'witness.py', 'analyze.py']
common.ISA_OPS = set(common.ISA_OPS) | {'rz', 'barrier'}
ROLES = {}


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real


def set_roles(n, edges, source):
    """emitters: taken in a written-seed order, each at least 3 links from every earlier one. witnesses = bits wired to an emitter. the rest = far clocks."""
    nb = {q: set() for q in range(n)}
    for a, b in edges:
        if a < n and b < n: nb[a].add(b); nb[b].add(a)
    def near(s):
        d = {s: 0}; qd = deque([s])
        while qd:
            u = qd.popleft()
            if d[u] == 2: continue
            for v in nb[u]:
                if v not in d: d[v] = d[u] + 1; qd.append(v)
        return set(d)
    em, blocked = [], set()
    for q in np.random.default_rng(SEED_ROLES).permutation(n):
        q = int(q)
        if q in blocked or not nb[q]: continue
        em.append(q); blocked |= near(q)
    wit = {w: e for e in em for w in nb[e]}
    ROLES.clear(); ROLES.update({'n': n, 'source': source, 'emitters': sorted(em), 'witness_of': {int(k): int(v) for k, v in wit.items()}, 'far': sorted(set(range(n)) - set(em) - set(wit)), 'edges': sorted([sorted(e) for e in {tuple(sorted(e)) for e in edges}])})
    return ROLES


def _family_edges():
    return json.load(open(os.path.join(HERE, 'data', 'reads', 'layout_156_family.json')))['edges']


def specs():
    sp = [{'key': f'A{a}|{h}', 'start': 'OFF' if a == 0 else 'ON', 'pre_waits_us': [T_US], 'arm': f'A{a}', 'hand': h} for a in range(4) for h in ('X', 'Y')]
    sp += [{'key': 'B1', 'start': 'ON', 'pre_waits_us': [T_US], 'arm': 'B1', 'hand': None}, {'key': 'B2', 'start': 'ON', 'pre_waits_us': [T_US], 'arm': 'B2', 'hand': None}]
    return sp + [{'key': 'F0', 'start': 'OFF', 'pre_waits_us': [0], 'arm': 'F0', 'hand': None}, {'key': 'F1', 'start': 'ON', 'pre_waits_us': [0], 'arm': 'F1', 'hand': None}]


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    if not ROLES or ROLES.get('n') != n_qubits: set_roles(n_qubits, _family_edges(), 'family layout (local snapshot)')
    qs = list(all_q); E = [q for q in ROLES['emitters'] if q in qs]; N = [q for q in qs if q not in ROLES['emitters']]
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key']); reg = ClassicalRegister(len(qs), 'L1'); qc.add_register(reg); arm = sp['arm']
    d20, u20 = _realize(dt, 20); d40, u40 = _realize(dt, 40); d60, u60 = _realize(dt, 60); real = [0.0]
    if arm == 'F1': qc.x(qs)
    elif arm != 'F0':
        real = [u60]
        if E:
            if arm == 'A0': qc.delay(d60, E, unit='dt')
            elif arm == 'A1': qc.x(E); qc.delay(d20, E, unit='dt'); qc.x(E); qc.delay(d40, E, unit='dt')
            elif arm == 'A2': qc.x(E); qc.delay(d40, E, unit='dt'); qc.x(E); qc.delay(d20, E, unit='dt')
            else: qc.x(E); qc.delay(d60, E, unit='dt')
        if N:
            if arm.startswith('A'):
                qc.sx(N); qc.delay(d60, N, unit='dt')
                if sp['hand'] == 'Y': qc.rz(math.pi / 2, N)
                qc.sx(N)
            elif arm == 'B2': qc.x(N); qc.delay(d60, N, unit='dt')
            else: qc.delay(d60, N, unit='dt')
    qc.barrier(qs)
    for j, q in enumerate(qs): qc.measure(q, reg[j])
    return qc, real


def _check_ledger(T, ledger, nq):
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    for c in ledger['circuits']:
        qc = T[c['key']]; nm = sum(1 for i in qc.data if i.operation.name == 'measure')
        if nm != nq or [r.name for r in qc.cregs] != ['L1']: raise RuntimeError(f"ledger mismatch in {c['key']}: measures {nm}")


_orig_cfg = common.chip_config


def _cfg(be):
    c = be.configuration(); set_roles(int(c.n_qubits), [list(e) for e in c.coupling_map], f'{CHIP} static configuration, read at fire')
    json.dump(ROLES, open(os.path.join(HERE, 'data', 'reads', 'witness_roles.json'), 'w'))
    return _orig_cfg(be)


common.build_circuit = _build_circuit
common.check_ledger_vs_circuits = _check_ledger
common.chip_config = _cfg


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (roles by written seed from the wiring; no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the stopwatch run fires on {CHIP} only, blind path.')


def _est():
    sp = specs(); return estimate(sp, nominal_real(sp), SHOTS_J)


def _cap(remaining, this_worst_s, later_est_sum, this_est_s=None):
    cap = int(min(CAP_S, math.floor(remaining))); parts = {'worst_case_s': this_worst_s, 'remaining_minus_later_s': math.floor(remaining), 'binding': f'fixed cap {CAP_S} s'}
    if this_est_s is not None and cap < this_est_s + 1: parts['too_small'] = True
    return cap, parts


common.check_chip_box = _check
common.earlier_unlanded = lambda chip, run, fire_dir=None: []
common.jobs_to_come = lambda chip, run, fire_dir=None, dt=NOMINAL_DT: (_est()['per_job_total_s'], [])
common.exec_cap = _cap

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for f in ('print-estimate', 'freeze-all', 'dry-run', 'usage', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--read', type=int, choices=READS)
    a = ap.parse_args(); sp = specs()
    if a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service(); print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('STOPWATCH RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('stopwatch read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN reads 1-3', info['frozen_at'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drywit', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
