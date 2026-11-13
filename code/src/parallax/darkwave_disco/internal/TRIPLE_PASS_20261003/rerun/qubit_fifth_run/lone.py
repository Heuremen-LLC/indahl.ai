"""THE LONE-LOOK RUN (Bones, by hand, 2026-10-02). The third corner for the tail run: the same waits with NO first look.
ibm_pittsburgh, every bit, blind path. ONE read (11 s were on the clock) = 11 circuits x 400 shots: START, WAIT, ONE LOOK with
  ON  and MID at waits  none / 6.7 / 20 / 60 / 300 us,  OFF at none.
Laid against the tail run (START, LOOK, WAIT, LOOK at the same waits) it gives, with no clock and no fit:  what the bit keeps after a wait with one earlier look
over what it keeps after the same wait with none = what the first look cost, at each wait. No number of ours is written for it.
  python lone.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read 1 [--confirm-submit]"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1]; RUN0 = 30      # stored as run 31
TW = [0, 6.7, 20, 60, 300]


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real
SHOTS_J = 400; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261310 + k
common.code_files = lambda r: ['common.py', 'live.py', 'lone.py', 'analyze.py']
_nine = common.blind_groups


def specs():
    sp = [{'key': f'{s}|w{w}', 'start': s, 'pre_waits_us': [w]} for s in ('ON', 'MID') for w in TW]
    return sp + [{'key': 'OFF|w0', 'start': 'OFF', 'pre_waits_us': [0]}]


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the lone-look run fires on {CHIP} only, blind path.')


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
        live.log_read('LONE-LOOK RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('lone read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN read 1', info['frozen_at'], info['files'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drylone', 'blank', 60, None, 0.95, None, None)      # nine bits, local simulator: proves the circuits and the save/parse path only
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
