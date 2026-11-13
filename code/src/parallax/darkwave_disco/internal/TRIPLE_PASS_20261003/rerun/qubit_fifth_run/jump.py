"""THE JUMP RUN (Bones, by hand, 2026-10-02). One chip (ibm_pittsburgh), EVERY bit on it, the same circuits fired again and again a few minutes apart,
so the bits' own jumping between a long clock and a short clock is the thing measured instead of the thing in the way.
Each READ is one job of 10 circuits, 400 shots each, every bit of the chip at once (no draw, so no chosen bits):
  ON  : START, LOOK, WAIT (none / 60 / 240 / 300 us), LOOK     -> each bit's clock in this read, and the no-time bite
  MID : the same four                                           -> does MID carry the same clock
  OFF : none and 300 only                                       -> the frame, and whether OFF stays flat
Blind path (the chip's calibration is not read). No number of ours is written for this run. The only numbers standing over it are the stone's two
(260/365 and 13/20; table hash 2308807b..., written 10/2 before any jump was seen) and they are rulers.
Brake: 3.0 s overhead + sequence, 1.25 margin, every job capped at 12 s.
  python jump.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..8)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = list(range(1, 9)); RUN0 = 10      # read K is stored as run 10+K
SHOTS_J = 400; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261110 + k
common.code_files = lambda r: ['common.py', 'live.py', 'jump.py', 'analyze.py']
_nine = common.blind_groups


def specs():
    sp = [{'key': f'{s}|w{w}', 'start': s, 'pre_waits_us': [0, w]} for s in ('ON', 'MID') for w in [0] + list(WAITS_US)]
    return sp + [{'key': f'OFF|w{w}', 'start': 'OFF', 'pre_waits_us': [0, w]} for w in (0, LONG)]


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the jump run fires on {CHIP} only, blind path.')


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
    for f in ('print-estimate', 'freeze-all', 'dry-run', 'usage', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--read', type=int, choices=READS)
    a = ap.parse_args(); sp = specs()
    if a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service(); print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('JUMP RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('jump read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN reads 1-8', info['frozen_at'], info['files'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_dryjump', 'blank', 60, None, 0.95, None, None)      # nine bits, local simulator: proves the circuits and the save/parse path only
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
