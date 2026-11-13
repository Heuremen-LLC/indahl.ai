"""THE HOLD RUN (Bones, by hand, 2026-10-02). Wayfinder: "you better not just be re-creating an actual clock... make them show you how to make time
our little bitch." Not a dial. This run ACTS on a bit's time and reads what the bit says passed.
Every arm: START ON, then 300 us of OUR time, then the last look. What differs is what we do inside the 300:
  N0             nothing
  L1 / L3 / L9   LOOK at it 1 / 3 / 9 times on the way (evenly spaced)               -- the observer's act
  P1 / P3 / P9   PUSH it over 1 / 3 / 9 times on the way and once more at the end   -- park it on the far side for alternate stretches
  rulers:        OFF with nine looks; OFF with ten pushes; lone looks of OFF and ON at no wait (the frame)
Read: what is left at the last look in each arm, each against the other two families, and "how much time the bit says passed" using N0 as the yardstick.
ibm_pittsburgh, every bit, blind submit path. THREE reads four minutes apart; each = 11 circuits x 330 shots. No number of ours is written for it.
Brake: 3.0 s overhead + sequence, 1.25 margin, every job capped at 12 s; stops on the first job that does not land.
  python hold.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 70; SHOTS_J = 330; CAP_S = 12; TOTAL = 300
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261710 + k
common.code_files = lambda r: ['common.py', 'live.py', 'hold.py', 'analyze.py']


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real


def specs():
    sp = [{'key': 'ON|N0', 'start': 'ON', 'pre_waits_us': [TOTAL], 'pushes': 0}]
    sp += [{'key': f'ON|L{n}', 'start': 'ON', 'pre_waits_us': [TOTAL / (n + 1)] * (n + 1), 'pushes': 0} for n in (1, 3, 9)]
    sp += [{'key': f'ON|P{n}', 'start': 'ON', 'pre_waits_us': [TOTAL], 'pushes': n} for n in (1, 3, 9)]
    sp += [{'key': 'OFF|L9', 'start': 'OFF', 'pre_waits_us': [TOTAL / 10] * 10, 'pushes': 0}, {'key': 'OFF|P9', 'start': 'OFF', 'pre_waits_us': [TOTAL], 'pushes': 9}]
    return sp + [{'key': 'OFF|w0', 'start': 'OFF', 'pre_waits_us': [0], 'pushes': 0}, {'key': 'ON|w0', 'start': 'ON', 'pre_waits_us': [0], 'pushes': 0}]


def _build_circuit(n_qubits, dt, all_q, sp):
    """looks: START, then (WAIT, LOOK) per entry. pushes n: START, then n+1 equal stretches with a full push after each (n inside + 1 at the end), then ONE look."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key']); regs = [ClassicalRegister(len(all_q), f'L{k + 1}') for k in range(len(sp['pre_waits_us']))]
    for r in regs: qc.add_register(r)
    qs = list(all_q)
    if sp['start'] == 'ON': qc.x(qs)
    real = []
    if sp['pushes']:
        n = sp['pushes']; seg, us = _realize(dt, sp['pre_waits_us'][0] / (n + 1))
        for _ in range(n + 1): qc.delay(seg, qs, unit='dt'); qc.x(qs)
        real.append(us * (n + 1))
        for j, q in enumerate(qs): qc.measure(q, regs[0][j])
        return qc, real
    for k, w in enumerate(sp['pre_waits_us']):
        if w:
            n, us = _realize(dt, w); real.append(us); qc.delay(n, qs, unit='dt')
        else: real.append(0.0)
        for j, q in enumerate(qs): qc.measure(q, regs[k][j])
    return qc, real


def _check_ledger(T, ledger, nq):      # the push arms hold several delays inside one WAIT entry: check looks and registers; delays are checked against the spec here
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    by = {s['key']: s for s in specs()}
    for c in ledger['circuits']:
        qc = T[c['key']]; nm = sum(1 for i in qc.data if i.operation.name == 'measure'); nd = sum(1 for i in qc.data if i.operation.name == 'delay'); s = by[c['key']]
        want_d = nq * ((s['pushes'] + 1) if s['pushes'] else sum(1 for w in s['pre_waits_us'] if w)); nx = sum(1 for i in qc.data if i.operation.name == 'x')
        want_x = nq * ((1 if s['start'] == 'ON' else 0) + ((s['pushes'] + 1) if s['pushes'] else 0))
        if nm != nq * c['n_looks'] or nd != want_d or nx != want_x or [r.name for r in qc.cregs] != [f'L{k + 1}' for k in range(c['n_looks'])]:
            raise RuntimeError(f"ledger mismatch in {c['key']}: measures {nm}, delays {nd} (want {want_d}), pushes {nx} (want {want_x})")


common.build_circuit = _build_circuit
common.check_ledger_vs_circuits = _check_ledger


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the hold run fires on {CHIP} only, blind path.')


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
        live.log_read('HOLD RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('hold read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN reads 1-3', info['frozen_at'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_dryhold', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
