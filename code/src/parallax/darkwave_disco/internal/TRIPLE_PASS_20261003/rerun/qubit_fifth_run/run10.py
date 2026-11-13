"""RUN 10 -- THE SHORT-WAIT COLUMN AGAIN, TWO CHIPS (Bones, by hand, 2026-10-02). Pulls "we opened it" apart from "a night passed" as far as 10 s allows. A THREE:
  Pittsburgh last night -> this morning : opened AND a night AND maintenance   (already read, run 2 -> run 9)
  Pittsburgh this morning -> now        : neither (same day, already opened)    (run 9 -> THIS)
  Kingston last night -> now            : a night only (it was looked at all along) (run 2 -> THIS)
Circuits = exact copies of Run 2's short-wait column: START, LOOK, WAIT 60 us, LOOK for OFF / MID / ON, laid THREE times (copies), 195 shots each (585 per start).
Each chip on its own nine bits (Pittsburgh: the blind nine; Kingston: the nine from its run-1 freeze). Blind path on both (no calibration read today).
No number written beforehand; what we expect is unsealed and is a ruler. Brake: 3.0 s overhead, 1.25 margin, the other chip counted as still to come.
  python run10.py --print-estimate | --freeze --chip C | --dry-run --chip C | --fire --chip C [--confirm-submit]"""
import argparse, json, os, sys
import numpy as np
import common
from common import *

RUN = 10
COPIES = [1, 2, 3]
WAITS5 = [SHORT]                 # NONE (no wait at all), short, medium, long
SHOTS5 = 195                                  # per circuit; 3 copies = 636 per (start, wait). Largest count whose guard (1.25 x per-job estimate) fits 10 s.
SEED_ORDER5 = 20261102                        # WRITTEN seed: circuit order across all 36
USED = ('ibm_phoenix', 'ibm_boston', 'ibm_marrakesh', 'ibm_fez')
KINGSTON_GROUPS = [[82, 139, 154], [38, 92, 96], [25, 109, 135]]        # copied from qubit_three_runs/freeze_ibm_kingston_run1.json
_blind = common.blind_groups
OTHER = {'ibm_pittsburgh': 'ibm_kingston', 'ibm_kingston': 'ibm_pittsburgh'}   # the four chips of the earlier runs: refused here

common.SHOTS = SHOTS5
common.SEED_ORDER[RUN] = SEED_ORDER5
common.DRY_TAU['blank'] = 350.0


def specs():
    return [{'key': f'{s}|w{w}|c{c}', 'start': s, 'pre_waits_us': [0, w], 'copy': c} for c in COPIES for s in STARTS for w in WAITS5]


def _check_chip_box(chip, box):
    if chip in USED: sys.exit(f'REFUSED: {chip} has already been looked at. Run 10 fires on ibm_pittsburgh and ibm_kingston only.')
    if box != 'blank': sys.exit('REFUSED: run 10 has one box: no prediction, blind bits (code name: blank).')


def _est_now():
    sp = specs(); return estimate(sp, nominal_real(sp), SHOTS5)


common.check_chip_box = _check_chip_box
common.earlier_unlanded = lambda chip, run, fire_dir=None: []
common.jobs_to_come = lambda chip, run, fire_dir=None, dt=NOMINAL_DT: (_est_now()['per_job_total_s'], [] if os.path.exists(os.path.join(HERE, 'data', 'fire', OTHER[chip], 'run10_meta.json')) else [{'chip': OTHER[chip], 'run': 10, 'est_s': _est_now()['per_job_total_s']}])


def freeze(chip):
    _check_chip_box(chip, 'blank')
    p = freeze_path(RUN, chip)
    if os.path.exists(p): sys.exit(f'{p} exists')
    info = freeze_info(RUN, specs(), chip, 'blank')
    info.update({'source': 'none (BLIND: code and seed only; no account contact)', 'frozen_at': now_iso(), 'shots_per_circuit': SHOTS5, 'order_seed': SEED_ORDER5,
                 'run10_sha256': sha256_file(os.path.join(HERE, 'run10.py')), 'prediction': 'NONE. No number was written for this run by anyone.'})
    json.dump(info, open(p, 'w'), indent=1)
    print('FROZEN run 10', chip, info['frozen_at'], info['combined_sha256']); [print(' ', k, v) for k, v in info['files'].items()]


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for f in ('names', 'usage', 'list-circuits', 'print-estimate', 'freeze', 'dry-run', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--chip'); ap.add_argument('--out-dir', default=None)
    a = ap.parse_args(); sp = specs()
    if a.chip == 'ibm_kingston': common.blind_groups = lambda n: {'groups': KINGSTON_GROUPS, 'all_q': sorted(q for g in KINGSTON_GROUPS for q in g), 'seed': None, 'how': 'the nine bits of the Kingston runs (from its run-1 freeze); not redrawn, not rechecked today'}
    if a.names or a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service()
        if a.names: print('backend names:', sorted(live.list_backend_names(svc)))
        if a.usage: print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('RUN 10: account-level read (' + ('backend NAMES ' if a.names else '') + ('usage' if a.usage else '') + '); no chip named')
    elif a.list_circuits: list_circuits(RUN, sp)
    elif a.print_estimate: print_est('run10', _est_now()); print('guard needs', SAFETY * _est_now()['per_job_total_s'], 's')
    elif a.freeze: freeze(a.chip)
    elif a.dry_run: dry_run(RUN, sp, a.chip, 'blank', SHOTS5, None, 0.95, a.out_dir, None)
    elif a.fire: fire(RUN, sp, a.chip, 'blank', None, a.confirm_submit)
    else: ap.print_help()
