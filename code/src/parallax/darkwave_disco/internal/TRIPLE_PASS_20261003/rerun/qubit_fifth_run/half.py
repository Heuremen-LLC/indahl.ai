"""THE HALF-PUSH RUN (Bones, by hand, 2026-10-02). Closes one leftover of the standoff puzzle: BOTH-AND-NEITHER, left un-looked, drops fast in its
first 20 us (first-stretch clock 123 us against 208 for ON; one read). Whose is that drop? THREE BOXES, read against each other:
  it belongs to BEING IN BETWEEN  -> both in-betweens show it, neither ON does
  it belongs to THE HALF-PUSH     -> everything built with a half-push shows it, including an ON made of two half-pushes
  blank
ibm_pittsburgh, every bit, blind submit path. THREE reads, four minutes apart; each read = 14 circuits x 360 shots: START, WAIT, ONE LOOK with
  MIDa = one half-push            MIDb = a full push then a half-push (the in-between reached from the far side)
  ONa  = one full push            ONb  = two half-pushes
  each at waits none / 6.7 / 20 us;   OFFa = nothing, OFFb = two full pushes, at none.
No number of ours is written for it. Brake: 3.0 s overhead + sequence, 1.25 margin, every job capped at 12 s; stops on the first job that does not land.
ALSO, once, at the first fire: the maker's stated length of one look on this chip is READ (a look at the chip's published numbers, logged) -- the missing
outside leg of puzzle cell O-1.
  python half.py --print-estimate | --freeze-all | --dry-run | --usage | --look-length | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 40      # read K is stored as run 40+K
PREP = {'MIDa': ('MID', ['sx']), 'MIDb': ('MID', ['x', 'sx']), 'ONa': ('ON', ['x']), 'ONb': ('ON', ['sx', 'sx']), 'OFFa': ('OFF', []), 'OFFb': ('OFF', ['x', 'x'])}
TW = [0, 6.7, 20]


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real
SHOTS_J = 360; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261410 + k
common.code_files = lambda r: ['common.py', 'live.py', 'half.py', 'analyze.py']
_nine = common.blind_groups


def specs():
    sp = [{'key': f'{n}|w{w}', 'start': PREP[n][0], 'prep': PREP[n][1], 'pre_waits_us': [w]} for n in ('MIDa', 'MIDb', 'ONa', 'ONb') for w in TW]
    return sp + [{'key': f'{n}|w0', 'start': 'OFF', 'prep': PREP[n][1], 'pre_waits_us': [0]} for n in ('OFFa', 'OFFb')]


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
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the half-push run fires on {CHIP} only, blind path.')


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
        live.log_read('HALF-PUSH RUN: account-level usage read; no chip named')
    elif a.look_length:
        import live
        live.install_guard({CHIP}, allow_submit=False); svc, tok = live.open_service(); be = svc.backend(CHIP); t = be.target; dt = t.dt
        d = [t['measure'][(q,)].duration for q in range(t.num_qubits) if (q,) in t['measure'] and t['measure'][(q,)] is not None and t['measure'][(q,)].duration]
        print('MAKER LOOK LENGTH', CHIP, 'us: min %.3f  middle %.3f  max %.3f  (%d bits)' % (min(d) * 1e6, sorted(d)[len(d) // 2] * 1e6, max(d) * 1e6, len(d)))
        json.dump({'chip': CHIP, 'read_at': now_iso(), 'measure_duration_us': [x * 1e6 for x in d]}, open(os.path.join(HERE, 'data', 'reads', 'maker_look_length_pittsburgh.json'), 'w'))
        live.log_read(f"HALF-PUSH RUN: the maker's published numbers for {CHIP} READ (its target: the stated length of one look); a look at the chip's published numbers", {'chip': CHIP})
    elif a.print_estimate: print_est('half-push read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN reads 1-3', info['frozen_at'], info['files'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_dryhalf', 'blank', 60, None, 0.95, None, None)      # nine bits, local simulator: proves the circuits and the save/parse path only
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
