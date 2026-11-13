"""THE GIVE-BACK RUN (Bones, by hand, 2026-10-02). Settles the leftover of TRIANGLE II: is a lone look given back? Within one job a single look
150 us before the end cost 1.0 +- 1.4 us by the end (three reads), against 3.5 us for each of three or nine looks; the cross-read curve sat inside the chip's
read-to-read wander. THREE BOXES:  given back with time (the cost shrinks the earlier the look)  /  never given back (3.5 us wherever it sits)  /  blank.
ibm_pittsburgh, every bit, blind submit path. THREE reads; each = 6 circuits x 1000 shots, all in ONE job (the same moment):
  ON, 300 us of our time, last look:  nothing on the way  /  one look at 0 us (right after the start)  /  at 150 us  /  at 270 us (30 us before the end)
  frame: lone looks of OFF and ON at no wait.
No number of ours is written for it. Brake: 3.0 s overhead + sequence, 1.25 margin, capped at 12 s.
  python giveback.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 110; SHOTS_J = 1000; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20262110 + k
common.code_files = lambda r: ['common.py', 'live.py', 'giveback.py', 'analyze.py']


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real


def specs():
    return [{'key': 'ON|none', 'start': 'ON', 'pre_waits_us': [300]},
            {'key': 'ON|at0', 'start': 'ON', 'pre_waits_us': [0, 300]},
            {'key': 'ON|at150', 'start': 'ON', 'pre_waits_us': [150, 150]},
            {'key': 'ON|at270', 'start': 'ON', 'pre_waits_us': [270, 30]},
            {'key': 'OFF|w0', 'start': 'OFF', 'pre_waits_us': [0]},
            {'key': 'ON|w0', 'start': 'ON', 'pre_waits_us': [0]}]


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the give-back run fires on {CHIP} only, blind path.')


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
        live.log_read('GIVE-BACK RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('give-back read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN give-back reads 1-3', info['frozen_at'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drygive', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
