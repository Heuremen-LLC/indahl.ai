"""THE BAND RUN (Bones, by hand, 2026-10-02). Settles the leftover of the standoff puzzle: on Marrakesh (9/28 echo, one read) the chip's two inside clocks
(the ~64 us clustering clock A and the ~80 us drain B) saw each other where each bit's 0 and 1 clouds meet (readout cutoff 0.40-0.55) AND in a second band
deep inside the 1 cloud, 0.62-0.65, peaking at 0.65 and gone at 0.66 -- found on ONE record. THREE BOXES:  it repeats  /  it is gone  /  blank.
THE SAME RECORD, AGAIN, three times: the 9/28 echo exactly as it was laid (parallax_echo.py): on the SAME 78 bits of ibm_marrakesh, each shot = LOOK, (push
or not), LOOK; E0 = no push, E1 = a push between the looks; 1500 shots; the gap between shots (rep_delay) set per job. Only the gaps the band's own analysis
reads (out/the_middle/the_flash.py, three_times_visibility.py): 20 / 50 / 100 us (both clocks) and 2000 us (the floor and the clouds).
E0 and E1 are SEPARATE jobs, as on 9/28: the two clocks are shot-to-shot carries, and two kinds of shot in one job would sit between each other.
One read = 8 jobs, fired E1 then E0 at each gap, gaps ascending (the 9/28 order). Blind submit path (no calibration read). No number of ours is written for it.
Brake: 3.0 s overhead + sequence, 1.25 margin, capped at 12 s.
  python band.py --print-estimate | --freeze-all | --dry-run | --usage | --fire --read K --job J [--confirm-submit]      (K = 1..3, J = 0..7)"""
import argparse, json, math, os, sys
import numpy as np
import common
from common import *

CHIP = 'ibm_marrakesh'; READS = [1, 2, 3]; SHOTS_J = 1500; CAP_S = 12
JOBS = [(20, 'E1'), (20, 'E0'), (50, 'E1'), (50, 'E0'), (100, 'E1'), (100, 'E0'), (2000, 'E1'), (2000, 'E0')]
ECHO_META = os.path.expanduser('~/bones-forge/parallax/out/echo_20260928_122733/meta.json')
Q78 = list(json.load(open(ECHO_META))['qubits'])
common.SHOTS = SHOTS_J
common.code_files = lambda r: ['common.py', 'live.py', 'band.py', 'analyze.py']
run_no = lambda k, j: 200 + 10 * k + j
for k in READS:
    for j in range(8): common.SEED_ORDER[run_no(k, j)] = 20262200 + 10 * k + j
_orig_est = common.estimate
common.estimate = lambda specs, real_waits, shots, rep_delay_s=None: _orig_est(specs, real_waits, shots, common.REP_DELAY_S if rep_delay_s is None else rep_delay_s)
estimate = common.estimate


def set_gap(us):
    common.REP_DELAY_S = us / 1e6; common.PINNED_OPTIONS["execution.rep_delay"] = us / 1e6


def specs_for(pub):
    return [{'key': pub, 'start': 'OFF', 'pre_waits_us': [0, 0], 'flip': pub == 'E1'}]


SPEC = {'pub': 'E0'}
specs = lambda: specs_for(SPEC['pub'])


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qs = list(all_q); a, b = ClassicalRegister(len(qs), 'L1'), ClassicalRegister(len(qs), 'L2')
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), a, b, name=sp['key'])
    for j, q in enumerate(qs): qc.measure(q, a[j])
    if sp['flip']: qc.x(qs)
    for j, q in enumerate(qs): qc.measure(q, b[j])
    return qc, [0.0, 0.0]


def _check_ledger(T, ledger, nq):
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    for c in ledger['circuits']:
        qc = T[c['key']]; cnt = lambda n: sum(1 for i in qc.data if i.operation.name == n)
        if cnt('measure') != 2 * nq or cnt('x') != (nq if c['key'] == 'E1' else 0) or [r.name for r in qc.cregs] != ['L1', 'L2']:
            raise RuntimeError(f"ledger mismatch in {c['key']}")


def _echo_bits(n):
    if max(Q78) >= n: sys.exit(f'REFUSED: the 9/28 bits do not fit a {n}-bit chip')
    g = [Q78[i:i + 3] for i in range(0, len(Q78), 3)]
    return {'groups': g, 'all_q': sorted(Q78), 'seed': None, 'how': "the 78 bits of the 9/28 Marrakesh echo (from its own meta.json); not redrawn, not rechecked today"}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the band run fires on {CHIP} only, blind path.')


def _est():
    sp = specs(); return estimate(sp, nominal_real(sp), SHOTS_J)


def _cap(remaining, this_worst_s, later_est_sum, this_est_s=None):
    cap = int(min(CAP_S, math.floor(remaining))); parts = {'worst_case_s': this_worst_s, 'remaining_minus_later_s': math.floor(remaining), 'binding': f'fixed cap {CAP_S} s'}
    if this_est_s is not None and cap < this_est_s + 1: parts['too_small'] = True
    return cap, parts


common.build_circuit = _build_circuit
common.check_ledger_vs_circuits = _check_ledger
common.check_chip_box = _check
common.earlier_unlanded = lambda chip, run, fire_dir=None: []
common.jobs_to_come = lambda chip, run, fire_dir=None, dt=NOMINAL_DT: (_est()['per_job_total_s'], [])
common.exec_cap = _cap
common.DRY_MAX_QUBITS = 100

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for f in ('print-estimate', 'freeze-all', 'dry-run', 'usage', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--read', type=int, choices=READS); ap.add_argument('--job', type=int, choices=range(8))
    a = ap.parse_args()
    if a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service(); print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('BAND RUN: account-level usage read; no chip named')
    elif a.print_estimate:
        tot = 0
        for gap, pub in JOBS:
            set_gap(gap); SPEC['pub'] = pub; e = _est(); tot += e['per_job_total_s']; print(f'  gap {gap:>4} us {pub}: per-job estimate {e["per_job_total_s"]:.2f} s')
        print(f'one read = 8 jobs: {tot:.1f} s; three reads: {3 * tot:.1f} s')
    elif a.freeze_all:
        for k in READS:
            for j, (gap, pub) in enumerate(JOBS):
                set_gap(gap); SPEC['pub'] = pub; p = freeze_path(run_no(k, j), CHIP)
                if os.path.exists(p): sys.exit(f'{p} exists')
                info = freeze_info(run_no(k, j), specs(), CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'job': j, 'gap_us': gap, 'pub': pub, 'shots_per_circuit': SHOTS_J})
                json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN band reads 1-3 (24 jobs)', info['frozen_at'])
    elif a.dry_run:
        common.blind_groups = lambda n: {'groups': [Q78[0:3], Q78[3:6], Q78[6:9]], 'all_q': sorted(Q78[:9]), 'seed': None, 'how': 'DRY RUN: 9 of the 78 echo bits'}
        for gap, pub in JOBS[:2]:
            set_gap(gap); SPEC['pub'] = pub; dry_run(run_no(1, 0), specs(), 'ibm_dryband', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        gap, pub = JOBS[a.job]; set_gap(gap); SPEC['pub'] = pub
        common.blind_groups = _echo_bits
        fire(run_no(a.read, a.job), specs(), CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
