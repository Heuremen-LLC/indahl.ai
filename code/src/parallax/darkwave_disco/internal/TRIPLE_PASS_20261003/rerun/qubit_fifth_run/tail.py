"""THE TAIL RUN (Bones, by hand, 2026-10-02). The object: what a look costs, and WHEN the cost lands. From the jump run, three rulers on one look:
the maker's stated length (outside), the drop with no wait after it (inside), the drop the fading curve points back to once there is a wait (inside) -- each about
twice the last. The second half of the cost lands somewhere between no wait and 60 us. This run puts looks INSIDE that gap.
ibm_pittsburgh, every bit, blind path. Each READ = 11 circuits x 400 shots: START, LOOK, WAIT, LOOK with
  ON  and MID at waits  none / 6.7 / 20 / 60 / 300 us   (steps of three inside the gap; 60 and 300 tie it to every earlier run)
  OFF at none.
Three reads, four minutes apart. No number of ours is written for it. Brake: 3.0 s overhead + sequence, 1.25 margin, every job capped at 12 s.
  python tail.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 20      # read K is stored as run 20+K
TW = [0, 6.7, 20, 60, 300]


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [(_realize(dt, w)[1] if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}
nominal_real = common.nominal_real
SHOTS_J = 400; CAP_S = 12
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20261210 + k
common.code_files = lambda r: ['common.py', 'live.py', 'tail.py', 'analyze.py']
_nine = common.blind_groups


def specs():
    sp = [{'key': f'{s}|w{w}', 'start': s, 'pre_waits_us': [0, w]} for s in ('ON', 'MID') for w in TW]
    return sp + [{'key': 'OFF|w0', 'start': 'OFF', 'pre_waits_us': [0, 0]}]


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (no draw, no usability check)'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the tail run fires on {CHIP} only, blind path.')


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
        live.log_read('TAIL RUN: account-level usage read; no chip named')
    elif a.print_estimate: print_est('tail read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN reads 1-3', info['frozen_at'], info['files'])
    elif a.dry_run: dry_run(RUN0 + 1, sp, 'ibm_drytail', 'blank', 60, None, 0.95, None, None)      # nine bits, local simulator: proves the circuits and the save/parse path only
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
