"""THE PUSH RUN (Bones, by hand, 2026-10-02). Settles the leftover of TRIANGLE III: a bit pushed ten times from OFF ends 2.2% more ON than its own clock
allows (+0.0217 +- 0.0016, three reads); pushed the same ten times from ON it does not (+0.0014 +- 0.0014). THREE BOXES, read against each other:
  the PUSH owns it   -> it shows with NO time between the pushes (back-to-back trains)
  the TIME owns it   -> it shows only when the pushes are spread over 300 us
  blank
The in-between start is the third start: a push's shortfall shows there first (turns run: the in-between starts ~0.03 lower per whole extra turn).
ibm_pittsburgh, every bit, blind submit path. THREE reads; each = 14 circuits x 400 shots, ONE look at the end:
  starts OFF / ON / MID(one half-push)  x  pushes 0 / 2 back-to-back / 10 back-to-back / 10 spread (a push every 30 us over 300 us)
  rulers: ON with 300 us and nothing done; OFF with 300 us and nothing done.
No number of ours is written for it. Brake: 3.0 s overhead + sequence, 1.25 margin, capped at 12 s; stops on the first job that does not land.
  python push.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 90; SHOTS_J = 400; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261910 + k
common.code_files = lambda r: ['common.py', 'live.py', 'push.py', 'analyze.py']
PREP = {'OFF': [], 'ON': ['x'], 'MID': ['sx']}


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real


def specs():
    sp = []
    for s in ('OFF', 'ON', 'MID'):
        sp += [{'key': f'{s}|p0', 'start': s, 'pre_waits_us': [0], 'pushes': 0, 'spread': False},
               {'key': f'{s}|p2', 'start': s, 'pre_waits_us': [0], 'pushes': 2, 'spread': False},
               {'key': f'{s}|p10', 'start': s, 'pre_waits_us': [0], 'pushes': 10, 'spread': False},
               {'key': f'{s}|s10', 'start': s, 'pre_waits_us': [300], 'pushes': 10, 'spread': True}]
    return sp + [{'key': 'ON|n300', 'start': 'ON', 'pre_waits_us': [300], 'pushes': 0, 'spread': False},
                 {'key': 'OFF|n300', 'start': 'OFF', 'pre_waits_us': [300], 'pushes': 0, 'spread': False}]


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key']); reg = ClassicalRegister(len(all_q), 'L1'); qc.add_register(reg); qs = list(all_q)
    for g in PREP[sp['start']]: getattr(qc, g)(qs)
    if sp['spread']:
        seg, us = _realize(dt, sp['pre_waits_us'][0] / sp['pushes'])
        for _ in range(sp['pushes']): qc.delay(seg, qs, unit='dt'); qc.x(qs)
        real = [us * sp['pushes']]
    else:
        for _ in range(sp['pushes']): qc.x(qs)
        w = sp['pre_waits_us'][0]
        if w:
            n, us = _realize(dt, w); qc.delay(n, qs, unit='dt'); real = [us]
        else: real = [0.0]
    for j, q in enumerate(qs): qc.measure(q, reg[j])
    return qc, real


def _check_ledger(T, ledger, nq):
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    by = {s['key']: s for s in specs()}
    for c in ledger['circuits']:
        qc = T[c['key']]; s = by[c['key']]; cnt = lambda n: sum(1 for i in qc.data if i.operation.name == n)
        want_x = nq * (s['pushes'] + (1 if s['start'] == 'ON' else 0)); want_sx = nq * (1 if s['start'] == 'MID' else 0)
        want_d = nq * (s['pushes'] if s['spread'] else (1 if s['pre_waits_us'][0] else 0))
        if cnt('measure') != nq or cnt('x') != want_x or cnt('sx') != want_sx or cnt('delay') != want_d or [r.name for r in qc.cregs] != ['L1']:
            raise RuntimeError(f"ledger mismatch in {c['key']}: measure {cnt('measure')} x {cnt('x')} (want {want_x}) sx {cnt('sx')} (want {want_sx}) delay {cnt('delay')} (want {want_d})")


common.build_circuit = _build_circuit
common.check_ledger_vs_circuits = _check_ledger


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the push run fires on {CHIP} only, blind path.')


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
        live.log_read('PUSH RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('push read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN push reads 1-3', info['frozen_at'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drypush', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
