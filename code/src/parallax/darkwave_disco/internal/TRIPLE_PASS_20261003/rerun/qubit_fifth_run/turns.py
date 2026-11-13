"""THE TURNS RUN (Bones, by hand, 2026-10-02). The half-push and sides runs: the un-looked in-between's early term follows the PATH (having gone a half
turn further, through ON), not the angle. Two paths are a two. This run reaches each place by THREE paths, each a whole turn longer than the last:
  the in-between by 1, 5 and 9 quarter-turns is the SAME place by the SAME side each time (a whole turn back on itself between them),
  and by 3 quarter-turns it is the far side (the one that held early);   ON by 2 and 6;   OFF by 0 and 4.
  T1 = half-push | T3 = full, half | T5 = full, full, half | T9 = four fulls, half | ON2 = full | ON6 = three fulls | OFF0 = nothing | OFF4 = two fulls
Does a whole extra turn bring it back to the same reading (1 = 5 = 9), or does each turn leave something?
ibm_pittsburgh, every bit, blind submit path. Up to THREE reads four minutes apart; each = 20 circuits x 330 shots: START, WAIT, ONE LOOK; in-betweens
and ONs at waits none / 6.7 / 20 us, OFFs at none. No number of ours is written for it. Brake: 3.0 s overhead + sequence, 1.25 margin, capped at 12 s.
  python turns.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 60      # read K is stored as run 60+K
PREP = {'T1': ('MID', ['sx']), 'T3': ('MID', ['x', 'sx']), 'T5': ('MID', ['x', 'x', 'sx']), 'T9': ('MID', ['x', 'x', 'x', 'x', 'sx']), 'ON2': ('ON', ['x']), 'ON6': ('ON', ['x', 'x', 'x']), 'OFF0': ('OFF', []), 'OFF4': ('OFF', ['x', 'x'])}
TW = [0, 6.7, 20]


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real
SHOTS_J = 330; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261610 + k
common.code_files = lambda r: ['common.py', 'live.py', 'turns.py', 'analyze.py']
_nine = common.blind_groups


def specs():
    sp = [{'key': f'{n}|w{w}', 'start': PREP[n][0], 'prep': PREP[n][1], 'pre_waits_us': [w]} for n in ('T1', 'T3', 'T5', 'T9', 'ON2', 'ON6') for w in TW]
    return sp + [{'key': f'{n}|w0', 'start': 'OFF', 'prep': PREP[n][1], 'pre_waits_us': [0]} for n in ('OFF0', 'OFF4')]


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key']); regs = [ClassicalRegister(len(all_q), f'L{k + 1}') for k in range(len(sp['pre_waits_us']))]
    for r in regs: qc.add_register(r)
    qs = list(all_q)
    for g in sp['prep']: getattr(qc, g)(qs)
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
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the turns run fires on {CHIP} only, blind path.')


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
        live.log_read('TURNS RUN: account-level usage read; no chip named')
    elif a.look_length:
        import live
        live.install_guard({CHIP}, allow_submit=False); svc, tok = live.open_service(); be = svc.backend(CHIP); t = be.target; dt = t.dt
        d = [t['measure'][(q,)].duration for q in range(t.num_qubits) if (q,) in t['measure'] and t['measure'][(q,)] is not None and t['measure'][(q,)].duration]
        print('MAKER LOOK LENGTH', CHIP, 'us: min %.3f  middle %.3f  max %.3f  (%d bits)' % (min(d) * 1e6, sorted(d)[len(d) // 2] * 1e6, max(d) * 1e6, len(d)))
        json.dump({'chip': CHIP, 'read_at': now_iso(), 'measure_duration_us': [x * 1e6 for x in d]}, open(os.path.join(HERE, 'data', 'reads', 'maker_look_length_pittsburgh.json'), 'w'))
        live.log_read(f"TURNS RUN: the maker's published numbers for {CHIP} READ (its target: the stated length of one look); a look at the chip's published numbers", {'chip': CHIP})
    elif a.print_estimate: print_est('turns read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN reads 1-3', info['frozen_at'], info['files'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_dryturns', 'blank', 60, None, 0.95, None, None)      # nine bits, local simulator: proves the circuits and the save/parse path only
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
