"""THE WITNESS TIMES THE LOOK (Bones, by hand, 2026-10-02). Settles two leftovers:
  TRIANGLE II  -- the maker says one look lasts 2.18 us; the bit fades as if it lasted ~3.5 us (immediate pair 3.2-4.3, pile-up 3.5 +- 0.2).
  TRIANGLE I   -- can a neighbour clock tell ITS OWN emitter's fading from the chip's typical one (one read: can't read)?
THE WITNESS: every bit wired to an emitter is held as a CLOCK (set half-way, left to tick, read on two hands a quarter-turn apart). Its emitter is held ON
the whole time, so the clock's hand turns at a rate set by its emitter (and slows as the emitter fades: the emitter's own end look gives its fading in the
same job). The FAR bits (wired to no emitter) are the LOOKED-AT bits: held OFF, looked at back-to-back while every clock runs. Barriers make every clock's
free time span the far bits' looks, so a clock times the looks in the machine's own timeline.
  window arms: the clocks run 0 / 30 / 60 / 120 us of OUR laid time            (the clock's rate, and its curve as the emitter fades)
  look arms:   the clocks run while the far bits are looked at 3 / 9 times   (the looks' real length, read on each clock)
  frame:       everyone OFF / everyone ON, looked at with no wait.
THREE BOXES:  a look's slot is longer than its pulse (the clocks read ~3.5 us per look)  /  a look costs more than its slot (the clocks read ~2.2)  /  blank.
The look registers of the look arms are full width; only the far bits are written into them (the clocks and emitters are not looked at mid-window).
The chip's wiring and timing numbers are read from its static configuration at the instant of firing (the same read that gives its size; logged; saved).
ibm_pittsburgh, every bit plays a part. THREE reads; each = 14 circuits x 400 shots. No number of ours is written for it.
Brake: 3.0 s overhead + sequence, 1.25 margin, capped at 12 s.
  python looktime.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
from collections import deque
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 100; SHOTS_J = 400; CAP_S = 12; SEED_ROLES = 20261810     # the stopwatch's role seed: same roles
WINDOWS = [0, 30, 60, 120]; LOOKS = [3, 9]
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20262010 + k
common.code_files = lambda r: ['common.py', 'live.py', 'looktime.py', 'analyze.py']
common.ISA_OPS = set(common.ISA_OPS) | {'rz', 'barrier'}
ROLES = {}


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real


def set_roles(n, edges, source):
    """the stopwatch's rule, same seed: emitters in a written-seed order, each at least 3 links from every earlier one; witnesses = bits wired to an emitter;
    far = the rest (here: the looked-at bits)."""
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
    ROLES.clear(); ROLES.update({'n': n, 'source': source, 'emitters': sorted(em), 'witness_of': {int(k): int(v) for k, v in wit.items()},
                                 'far': sorted(set(range(n)) - set(em) - set(wit)), 'edges': sorted([sorted(e) for e in {tuple(sorted(e)) for e in edges}])})
    return ROLES


def _family_edges():
    return json.load(open(os.path.join(HERE, 'data', 'reads', 'layout_156_family.json')))['edges']


def specs():
    sp = [{'key': f'T{t}|{h}', 'start': 'MID', 'pre_waits_us': [t], 'hand': h, 'looks_far': 0} for t in WINDOWS for h in ('X', 'Y')]
    sp += [{'key': f'K{k}|{h}', 'start': 'MID', 'pre_waits_us': [0] * (k + 1), 'hand': h, 'looks_far': k} for k in LOOKS for h in ('X', 'Y')]
    return sp + [{'key': 'F0', 'start': 'OFF', 'pre_waits_us': [0], 'hand': None, 'looks_far': 0}, {'key': 'F1', 'start': 'ON', 'pre_waits_us': [0], 'hand': None, 'looks_far': 0}]


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    if not ROLES or ROLES.get('n') != n_qubits: set_roles(n_qubits, _family_edges(), 'family layout (local snapshot)')
    qs = list(all_q); E = [q for q in qs if q in set(ROLES['emitters'])]; Wt = [q for q in qs if q in ROLES['witness_of']]; Fr = [q for q in qs if q in set(ROLES['far'])]
    nreg = len(sp['pre_waits_us']); regs = [ClassicalRegister(len(qs), f'L{i + 1}') for i in range(nreg)]
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key'])
    for r in regs: qc.add_register(r)
    real = [0.0] * nreg
    if sp['key'] == 'F1': qc.x(qs)
    elif sp['key'] != 'F0':
        if E: qc.x(E)
        if Wt: qc.sx(Wt)
        qc.barrier(qs)
        if sp['looks_far'] == 0:
            t = sp['pre_waits_us'][0]
            if t:
                n, us = _realize(dt, t); qc.delay(n, qs, unit='dt'); real = [us]
        else:
            for i in range(sp['looks_far']):
                for q in Fr: qc.measure(q, regs[i][qs.index(q)])
        qc.barrier(qs)
        if Wt:
            if sp['hand'] == 'Y': qc.rz(math.pi / 2, Wt)
            qc.sx(Wt)
        qc.barrier(qs)
    for j, q in enumerate(qs): qc.measure(q, regs[-1][j])
    return qc, real


def _check_ledger(T, ledger, nq):
    """final register: every bit looked at once. look arms: each mid register holds the SAME set of bits, and every one of them is a far bit."""
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    by = {s['key']: s for s in specs()}; far = set(ROLES['far'])
    for c in ledger['circuits']:
        qc = T[c['key']]; s = by[c['key']]; regs = [r.name for r in qc.cregs]
        if regs != [f'L{k + 1}' for k in range(c['n_looks'])]: raise RuntimeError(f"{c['key']}: registers {regs}")
        per = {r: set() for r in regs}
        for i in qc.data:
            if i.operation.name == 'measure': per[qc.find_bit(i.clbits[0]).registers[0][0].name].add(qc.find_bit(i.qubits[0]).index)
        if len(per[regs[-1]]) != nq: raise RuntimeError(f"{c['key']}: final look reads {len(per[regs[-1]])} bits, want {nq}")
        mids = [per[r] for r in regs[:-1]]
        if len(mids) != s['looks_far'] or any(m != mids[0] for m in mids) or (mids and not mids[0] <= far):
            raise RuntimeError(f"{c['key']}: mid-window looks are not the same far bits every time")


_orig_cfg = common.chip_config


def _cfg(be):
    c = be.configuration(); set_roles(int(c.n_qubits), [list(e) for e in c.coupling_map], f'{CHIP} static configuration, read at fire')
    json.dump(ROLES, open(os.path.join(HERE, 'data', 'reads', 'looktime_roles.json'), 'w'))
    timing = {}
    for k in ('dt', 'dtm', 'rep_delay_range', 'default_rep_delay', 'meas_map', 'timing_constraints', 'measure_esp_enabled', 'dynamic_reprate_enabled', 'meas_levels', 'acquisition_latency', 'conditional_latency', 'parametric_pulses', 'processor_type', 'supported_instructions'):
        try:
            v = getattr(c, k, None); json.dumps(v, default=str); timing[k] = v
        except Exception as ex: timing[k] = f'unreadable: {ex}'
    json.dump({'chip': CHIP, 'read_at': now_iso(), 'what': "the maker's published timing numbers in the static configuration (read with the chip's size at the instant of firing; no extra request)", 'fields': timing},
              open(os.path.join(HERE, 'data', 'reads', 'pittsburgh_config_timing.json'), 'w'), indent=1, default=str)
    return _orig_cfg(be)


common.build_circuit = _build_circuit
common.check_ledger_vs_circuits = _check_ledger
common.chip_config = _cfg


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (roles by written seed from the wiring; no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the look-time run fires on {CHIP} only, blind path.')


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
        live.log_read('LOOK-TIME RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('look-time read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN look-time reads 1-3', info['frozen_at'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drylook', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
