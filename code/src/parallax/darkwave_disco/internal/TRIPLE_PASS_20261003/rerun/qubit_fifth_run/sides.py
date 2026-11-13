"""THE SIDES RUN (Bones, by hand, 2026-10-02). The half-push run showed the un-looked in-between carries a SIGN set by the side it was reached from
(one side loses early, the far side holds; a mirror, not quite even). Two sides are a two. This run reaches the in-between from THREE sides, a third of a
turn apart (0 / 120 / 240 degrees), plus the known far side (full push + half-push) as the check, so the three are read against each other.
CAUGHT BEFORE FIRING: in the circuit's own bookkeeping the three "sides" are the SAME state (turning the frame before the first push on a resting bit
changes nothing a later look can see by itself). They differ only against the bit's own carrier (the drive's reference): the push is played with its
phase turned. So the three boxes are:  the early term FOLLOWS THE ANGLE (it is tied to the carrier)  /  it FOLLOWS THE PATH (only the in-between that
went through ON shows it; S180 sits on FAR's side by angle but got there with one half-push)  /  neither.
ibm_pittsburgh, every bit, blind submit path. ONE read (12 s were on the clock) = 19 circuits x 360 shots: START, WAIT, ONE LOOK with
  S0 / S120 / S240 / S180 = turn the frame by that angle, then one half-push        FAR = a full push then a half-push
  ON = one full push, each at waits none / 6.7 / 20 us;   OFF = nothing, at none.
No number of ours is written for it. Brake: 3.0 s overhead + sequence, 1.25 margin, capped at 12 s.
  python sides.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3; reads 2 and 3 wait for seconds)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 50      # read K is stored as run 50+K
PREP = {'S0': ('MID', [('rz', 0.0), 'sx']), 'S120': ('MID', [('rz', 2 * math.pi / 3), 'sx']), 'S240': ('MID', [('rz', 4 * math.pi / 3), 'sx']), 'S180': ('MID', [('rz', math.pi), 'sx']), 'FAR': ('MID', ['x', 'sx']), 'ON': ('ON', ['x']), 'OFF': ('OFF', [])}
common.ISA_OPS = set(common.ISA_OPS) | {'rz'}
TW = [0, 6.7, 20]


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real
SHOTS_J = 360; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261510 + k
common.code_files = lambda r: ['common.py', 'live.py', 'sides.py', 'analyze.py']
_nine = common.blind_groups


def specs():
    sp = [{'key': f'{n}|w{w}', 'start': PREP[n][0], 'prep': PREP[n][1], 'pre_waits_us': [w]} for n in ('S0', 'S120', 'S240', 'S180', 'FAR', 'ON') for w in TW]
    return sp + [{'key': f'{n}|w0', 'start': 'OFF', 'prep': PREP[n][1], 'pre_waits_us': [0]} for n in ('OFF',)]


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key']); regs = [ClassicalRegister(len(all_q), f'L{k + 1}') for k in range(len(sp['pre_waits_us']))]
    for r in regs: qc.add_register(r)
    qs = list(all_q)
    for g in sp['prep']:
        if isinstance(g, tuple): qc.rz(g[1], qs)
        else: getattr(qc, g)(qs)
    real = []
    for k, w in enumerate(sp['pre_waits_us']):
        if w:
            n, us = common.realize_wait(dt, w); real.append(us); qc.delay(n, qs, unit='dt')
        else: real.append(0.0)
        for j, q in enumerate(qs): qc.measure(q, regs[k][j])
    return qc, real


common.build_circuit = _build_circuit


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the sides run fires on {CHIP} only, blind path.')


def _est():
    sp = specs(); return estimate(sp, nominal_real(sp), SHOTS_J)


def _cap(remaining, this_worst_s, later_est_sum, this_est_s=None):
    cap = int(min(CAP_S, math.floor(remaining))); parts = {'worst_case_s': this_worst_s, 'remaining_minus_later_s': math.floor(remaining), 'binding': f'fixed cap {CAP_S} s'}
    if this_est_s is not None and cap < this_est_s + 2: parts['too_small'] = True
    return cap, parts


common.check_chip_box = _check
common.earlier_unlanded = lambda chip, run, fire_dir=None: []
common.jobs_to_come = lambda chip, run, fire_dir=None, dt=NOMINAL_DT: (_est()['per_job_total_s'], [])
common.exec_cap = _cap

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for f in ('print-estimate', 'freeze-all', 'dry-run', 'usage', 'look-length', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--read', type=int, choices=READS)
    a = ap.parse_args(); sp = specs()
    if a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service(); print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('SIDES RUN: account-level usage read; no chip named')
    elif a.look_length:
        import live
        live.install_guard({CHIP}, allow_submit=False); svc, tok = live.open_service(); be = svc.backend(CHIP); t = be.target; dt = t.dt
        d = [t['measure'][(q,)].duration for q in range(t.num_qubits) if (q,) in t['measure'] and t['measure'][(q,)] is not None and t['measure'][(q,)].duration]
        print('MAKER LOOK LENGTH', CHIP, 'us: min %.3f  middle %.3f  max %.3f  (%d bits)' % (min(d) * 1e6, sorted(d)[len(d) // 2] * 1e6, max(d) * 1e6, len(d)))
        json.dump({'chip': CHIP, 'read_at': now_iso(), 'measure_duration_us': [x * 1e6 for x in d]}, open(os.path.join(HERE, 'data', 'reads', 'maker_look_length_pittsburgh.json'), 'w'))
        live.log_read(f"SIDES RUN: the maker's published numbers for {CHIP} READ (its target: the stated length of one look); a look at the chip's published numbers", {'chip': CHIP})
    elif a.print_estimate: print_est('sides read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN reads 1-3', info['frozen_at'], info['files'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drysides', 'blank', 60, None, 0.95, None, None)      # nine bits, local simulator: proves the circuits and the save/parse path only
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
