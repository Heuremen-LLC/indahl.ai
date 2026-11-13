"""RUN 7 -- THE NONE ARM ON KINGSTON (Bones, by hand, 2026-10-02). Makes the none arm a THREE: Marrakesh (old house chip, no prediction), Pittsburgh (was the blank),
Kingston (the chip our sealed predictions sat on). ibm_kingston only, the SAME nine bits its three runs used (from its run-1 freeze), submitted on the blind path
(its calibration is not read today). Each circuit: START, LOOK, LOOK (no wait). Three STARTS x three COPIES = 9 circuits, 212 shots each (636 per start, as on Marrakesh). No number written beforehand;
the expectations we carry are unsealed and are rulers. Brake: 3.0 s overhead, 1.25 margin.
  python run7.py --print-estimate | --freeze | --dry-run | --fire [--confirm-submit]"""
import argparse, json, os, sys
import numpy as np
import common
from common import *

RUN = 7
COPIES = [1, 2, 3]
WAITS5 = [0]                                  # NONE only
SHOTS5 = 212                                  # per circuit; 3 copies = 636 per (start, wait). Largest count whose guard (1.25 x per-job estimate) fits 10 s.
SEED_ORDER5 = 20261072                        # WRITTEN seed: circuit order across all 36
USED = ('ibm_pittsburgh', 'ibm_phoenix', 'ibm_boston', 'ibm_marrakesh', 'ibm_fez')   # the four chips of the earlier runs: refused here

common.SHOTS = SHOTS5
KINGSTON_GROUPS = [[82, 139, 154], [38, 92, 96], [25, 109, 135]]        # copied from qubit_three_runs/freeze_ibm_kingston_run1.json
common.blind_groups = lambda n: {'groups': KINGSTON_GROUPS, 'all_q': sorted(q for g in KINGSTON_GROUPS for q in g), 'seed': None, 'how': 'the nine bits of the Kingston runs (from its run-1 freeze); not redrawn, not rechecked today'}

common.SEED_ORDER[RUN] = SEED_ORDER5
common.DRY_TAU['blank'] = 350.0


def specs():
    return [{'key': f'{s}|w{w}|c{c}', 'start': s, 'pre_waits_us': [0, w], 'copy': c} for c in COPIES for s in STARTS for w in WAITS5]


def _check_chip_box(chip, box):
    if chip in USED: sys.exit(f'REFUSED: {chip} has already been looked at. Run 7 fires on ibm_kingston only.')
    if box != 'blank': sys.exit('REFUSED: run 7 has one box: no prediction, blind bits (code name: blank).')


def _est_now():
    sp = specs(); return estimate(sp, nominal_real(sp), SHOTS5)


common.check_chip_box = _check_chip_box
common.earlier_unlanded = lambda chip, run, fire_dir=None: []
common.jobs_to_come = lambda chip, run, fire_dir=None, dt=NOMINAL_DT: (_est_now()['per_job_total_s'], [])


def freeze(chip):
    _check_chip_box(chip, 'blank')
    p = freeze_path(RUN, chip)
    if os.path.exists(p): sys.exit(f'{p} exists')
    info = freeze_info(RUN, specs(), chip, 'blank')
    info.update({'source': 'none (BLIND: code and seed only; no account contact)', 'frozen_at': now_iso(), 'shots_per_circuit': SHOTS5, 'order_seed': SEED_ORDER5,
                 'run7_sha256': sha256_file(os.path.join(HERE, 'run7.py')), 'prediction': 'NONE. No number was written for this run by anyone.'})
    json.dump(info, open(p, 'w'), indent=1)
    print('FROZEN run 7', chip, info['frozen_at'], info['combined_sha256']); [print(' ', k, v) for k, v in info['files'].items()]


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for f in ('names', 'usage', 'list-circuits', 'print-estimate', 'freeze', 'dry-run', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--chip'); ap.add_argument('--out-dir', default=None)
    a = ap.parse_args(); sp = specs()
    if a.names or a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service()
        if a.names: print('backend names:', sorted(live.list_backend_names(svc)))
        if a.usage: print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('RUN 7: account-level read (' + ('backend NAMES ' if a.names else '') + ('usage' if a.usage else '') + '); no chip named')
    elif a.list_circuits: list_circuits(RUN, sp)
    elif a.print_estimate: print_est('run7', _est_now()); print('guard needs', common.SAFETY * _est_now()['per_job_total_s'], 's')
    elif a.freeze: freeze(a.chip)
    elif a.dry_run: dry_run(RUN, sp, a.chip, 'blank', SHOTS5, None, 0.95, a.out_dir, None)
    elif a.fire: fire(RUN, sp, a.chip, 'blank', None, a.confirm_submit)
    else: ap.print_help()
