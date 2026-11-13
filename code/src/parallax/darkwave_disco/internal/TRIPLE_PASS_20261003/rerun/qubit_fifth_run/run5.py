"""RUN 5 -- THE NONE (Bones, by hand, 2026-10-02). One job, one chip the four-chip run never fired on, NO prediction written by anyone, bits drawn blind.
The account holds two such chips (ibm_fez, ibm_marrakesh). NEITHER IS UNTOUCHED: both carry months of our earlier reads. Chosen: ibm_marrakesh, the chip the
three waits were cut FROM (see RULERS_AUDIT item 1), so the ruler is laid on its own source. Its calibration is not read today (blind path).
The run is its own ruler: the whole circuit set is laid THREE times in the one job (copies c1, c2, c3), so each copy is read against the other two.
Each circuit: START, LOOK, WAIT, LOOK. Three STARTS (OFF / MID / ON) x four WAITS (NONE = 0, 60, 240, 300 us) x three COPIES = 36 circuits.
The NONE wait is the new arm: look, then look again with no time between. Raw I/Q on both looks.
  python run5.py --names | --usage                       (account-level reads only; no chip is named)
  python run5.py --list-circuits | --print-estimate
  python run5.py --freeze --chip NAME
  python run5.py --dry-run --chip NAME
  python run5.py --fire --chip NAME [--confirm-submit]"""
import argparse, json, os, sys
import numpy as np
import common
from common import *

RUN = 5
COPIES = [1, 2, 3]
WAITS5 = [0] + list(WAITS_US)                 # NONE (no wait at all), short, medium, long
SHOTS5 = 212                                  # per circuit; 3 copies = 636 per (start, wait). Largest count whose guard (1.25 x per-job estimate) fits 10 s.
SEED_ORDER5 = 20261052                        # WRITTEN seed: circuit order across all 36
USED = ('ibm_kingston', 'ibm_phoenix', 'ibm_pittsburgh', 'ibm_boston')   # the four chips of the earlier runs: refused here

common.SHOTS = SHOTS5
common.SEED_ORDER[RUN] = SEED_ORDER5
common.DRY_TAU['blank'] = 350.0


def specs():
    return [{'key': f'{s}|w{w}|c{c}', 'start': s, 'pre_waits_us': [0, w], 'copy': c} for c in COPIES for s in STARTS for w in WAITS5]


def _check_chip_box(chip, box):
    if chip in USED: sys.exit(f'REFUSED: {chip} has already been looked at. Run 5 fires only on a chip the four-chip run never fired on.')
    if box != 'blank': sys.exit('REFUSED: run 5 has one box: no prediction, blind bits (code name: blank).')


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
                 'run5_sha256': sha256_file(os.path.join(HERE, 'run5.py')), 'prediction': 'NONE. No number was written for this run by anyone.'})
    json.dump(info, open(p, 'w'), indent=1)
    print('FROZEN run 5', chip, info['frozen_at'], info['combined_sha256']); [print(' ', k, v) for k, v in info['files'].items()]


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
        live.log_read('RUN 5: account-level read (' + ('backend NAMES ' if a.names else '') + ('usage' if a.usage else '') + '); no chip named')
    elif a.list_circuits: list_circuits(RUN, sp)
    elif a.print_estimate: print_est('run5', _est_now()); print('guard needs', SAFETY * _est_now()['per_job_total_s'], 's')
    elif a.freeze: freeze(a.chip)
    elif a.dry_run: dry_run(RUN, sp, a.chip, 'blank', SHOTS5, None, 0.95, a.out_dir, None)
    elif a.fire: fire(RUN, sp, a.chip, 'blank', None, a.confirm_submit)
    else: ap.print_help()
