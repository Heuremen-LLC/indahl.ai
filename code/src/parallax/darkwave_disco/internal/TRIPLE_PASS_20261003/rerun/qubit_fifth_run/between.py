"""THE IN-BETWEEN SHOT (Bones, by hand, 2026-10-02 evening). Wayfinder: "get on your horse and ride man, it closes never. Fire."
Leftover from Shuttle's review (ledger §146-§148): with ten pushes and 30 us between them, the in-between start lands 4 widths off the line through the
OFF and ON starts (raw -0.68% +- 0.17; push run, three reads). Starting from populations, every dynamics -- quantum or classical, with memory or without --
lands a mix ON that line, so only three things can move it off: (a) its own coherence against the push axis, (b) its neighbours' coherence (every bit gets
the same start, so in that arm every neighbour is a superposition too), (c) shots talking to each other across the 500-us gap.
With no time between pushes, (a) alone predicts the in-between's loss from the pushes' own measured shortfall with no free parameter (two pushes 0.0258
vs 0.0262, ten 0.128 vs 0.114). With time between, the state turns and fades between pushes at rates the blind path does not read -- so measure, don't predict.
ibm_pittsburgh, every bit, blind submit path. THREE reads; each = 14 circuits.
THE TRIANGLE, every arm ten pushes 30/30 like the push run:
   COHERENT    the in-between as before (sx)                                                      -- all its coherence on
   TWIRLED     the in-between started at a quarter / half / three-quarter turn (sx, rz(k pi/2));
               averaged with the coherent one, the bit's own coherence against the push axis cancels -- (a) removed, (b) kept
   LOOKED      the in-between looked at once right after it is made (sx, look): every bit, and so every neighbour, becomes a plain OFF or ON at random,
               shot by shot -- (a) and (b) removed, (c) kept. Its own line: OFF and ON looked at once the same way. Linearity puts it ON that line
               exactly, weighted by its own first look, with no free parameter (Shuttle's randomised preparation); shots sorted by their own and their
               neighbours' first looks also match the all-OFF / all-ON arms configuration by configuration.
   THREE BOXES: the twirl lands on the line (own coherence)  /  the twirl stays off but the look lands on (the neighbours')  /  the look stays off (shots talk)
   -- and blank. No number of ours is written for it.
FRAME and RULERS, same job: lone looks OFF / ON / in-between; ON left alone 30 and 300 us; the OFF and ON starts pushed the same way (the line).
Brake: 3.0 s overhead + sequence, 1.25 margin, every job capped at 12 s; stops on the first job that does not land.
  python between.py --print-estimate | --list | --check-full | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 130; SHOTS_J = 400; CAP_S = 12; SEG = 30; NP = 10
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20262410 + k
common.code_files = lambda r: ['common.py', 'live.py', 'between.py', 'analyze.py']
common.ISA_OPS = set(common.ISA_OPS) | {'rz'}


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


def _pushed_us(dt): return _realize(dt, SEG)[1] * NP


common.realize_wait = _realize


def _real(dt, sp):
    if sp['kind'] in ('frame',): return [0.0]
    if sp['kind'] == 'ruler': return [_realize(dt, sp['idle'])[1]]
    if sp['looked']: return [0.0, _pushed_us(dt)]
    return [_pushed_us(dt)]


common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: _real(dt, sp) for sp in specs}
nominal_real = common.nominal_real


def specs():
    sp = []
    for k, st in (('F0', 'OFF'), ('F1', 'ON'), ('FM', 'MID')):
        sp.append({'key': k, 'start': st, 'pre_waits_us': [0], 'kind': 'frame', 'turn': 0, 'looked': False, 'idle': 0})
    for L in (30, 300):
        sp.append({'key': f'R{L}', 'start': 'ON', 'pre_waits_us': [L], 'kind': 'ruler', 'turn': 0, 'looked': False, 'idle': L})
    for k, st in (('A', 'OFF'), ('B', 'ON'), ('M', 'MID')):
        sp.append({'key': k, 'start': st, 'pre_waits_us': [SEG * NP], 'kind': 'pushed', 'turn': 0, 'looked': False, 'idle': 0})
    for t in (1, 2, 3):
        sp.append({'key': f'T{t}', 'start': 'MID', 'pre_waits_us': [SEG * NP], 'kind': 'pushed', 'turn': t, 'looked': False, 'idle': 0})
    for k, st in (('LA', 'OFF'), ('LB', 'ON'), ('LM', 'MID')):
        sp.append({'key': k, 'start': st, 'pre_waits_us': [0, SEG * NP], 'kind': 'pushed', 'turn': 0, 'looked': True, 'idle': 0})
    return sp


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key']); qs = list(all_q)
    regs = [ClassicalRegister(len(qs), f'L{i + 1}') for i in range(len(sp['pre_waits_us']))]
    for r in regs: qc.add_register(r)
    if sp['start'] == 'ON': qc.x(qs)
    elif sp['start'] == 'MID': qc.sx(qs)
    if sp['turn']: qc.rz(sp['turn'] * math.pi / 2, qs)
    if sp['kind'] == 'ruler':
        n, us = _realize(dt, sp['idle']); qc.delay(n, qs, unit='dt'); real = [us]
    elif sp['kind'] == 'frame': real = [0.0]
    else:
        if sp['looked']:
            for j, q in enumerate(qs): qc.measure(q, regs[0][j])
        n, us = _realize(dt, SEG)
        for _ in range(NP): qc.delay(n, qs, unit='dt'); qc.x(qs)
        real = [0.0, us * NP] if sp['looked'] else [us * NP]
    for j, q in enumerate(qs): qc.measure(q, regs[-1][j])
    return qc, real


def _want(sp, nq):
    st = sp['start']
    if sp['kind'] == 'frame': return {'x': nq * (st == 'ON'), 'sx': nq * (st == 'MID'), 'rz': 0, 'delay': 0, 'measure': nq}
    if sp['kind'] == 'ruler': return {'x': nq * (st == 'ON'), 'sx': 0, 'rz': 0, 'delay': nq, 'measure': nq}
    return {'x': nq * (NP + (st == 'ON')), 'sx': nq * (st == 'MID'), 'rz': nq * bool(sp['turn']), 'delay': nq * NP, 'measure': nq * (2 if sp['looked'] else 1)}


def _check_ledger(T, ledger, nq):
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    by = {s['key']: s for s in specs()}
    for c in ledger['circuits']:
        qc = T[c['key']]; s = by[c['key']]; want = _want(s, nq)
        got = {k: sum(1 for i in qc.data if i.operation.name == k) for k in want}
        regs = [r.name for r in qc.cregs]
        if got != want or regs != [f'L{i + 1}' for i in range(c['n_looks'])]:
            raise RuntimeError(f"ledger mismatch in {c['key']}: got {got}, want {want}, registers {regs}")


common.build_circuit = _build_circuit
common.check_ledger_vs_circuits = _check_ledger


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the in-between shot fires on {CHIP} only, blind path.')


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


def check_full():
    sp = specs(); T, real = build_all(156, NOMINAL_DT, list(range(156)), sp); check_structure(T, list(range(156)), 156)
    led = build_ledger(RUN0 + 1, sp, real); ledger_self_check(led); _check_ledger(T, led, 156)
    print(f'FULL SIZE OK: {len(T)} circuits x 156 bits, {led["n_looks_total"]} looks per shot-set')
    for s in sp:
        ops = {}
        for i in T[s['key']].data: ops[i.operation.name] = ops.get(i.operation.name, 0) + 1
        print(f"  {s['key']:<4} {s['kind']:<7} start {s['start']:<3} turn {s['turn']}/4 looked-first {s['looked']!s:<5} laid {sum(real[s['key']]):8.3f} us  ops {ops}")
    print_est('in-between read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for f in ('print-estimate', 'list', 'check-full', 'freeze-all', 'dry-run', 'usage', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--read', type=int, choices=READS)
    a = ap.parse_args(); sp = specs()
    if a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service(); print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('IN-BETWEEN SHOT: account-level usage read; no chip named')
    elif a.print_estimate: print_est('in-between read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.list:
        for s in sp: print(f"  {s['key']:<4} {s['kind']:<7} start {s['start']:<3} turn {s['turn']}/4 looked-first {s['looked']}")
    elif a.check_full: check_full()
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN in-between reads 1-3', info['frozen_at'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drybetween', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
