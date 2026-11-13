"""THE NO-NAME SHOT (Bones, by hand, 2026-10-02 evening). Wayfinder: "Fire at will bones, you know what targets we're trying not to look at.... Fire."
What is left with no name (ledger §139, the Disco's none): a bit started OFF and pushed ten times with 30 us between pushes ends 2.0% more ON than its own
fading allows (+0.0200 +- 0.0016, six reads, two runs); started ON or in-between it does not; with no time between the pushes OFF and ON mirror each other.
The discarded half of all six reads (listen_discarded.py): the extra sits ON the OFF->ON line, in the plain ON cloud, nothing across the line.
ibm_pittsburgh, every bit, blind submit path. THREE reads; each = 21 circuits, ONE look at the end. No number of ours is written for it.

LEVER 1, which stretch owns it (OFF start, ten pushes, ends OFF):
   OFF stretches 10 / 30 / 90 us with ON stretches 30          and          ON stretches 10 / 30 / 90 us with OFF stretches 30
   THREE BOXES: it follows the time spent OFF  /  it follows the time spent ON  /  blank
LEVER 2, where it ends:  OFF start, ten pushes, then ONE more push at once (ends ON);  ON start, ten pushes (ends ON);  ON start, ten pushes, ONE more (ends OFF)
   THREE BOXES: it moves with the bit (the extra flips with it)  /  it stays with ending OFF  /  blank
LEVER 3, how many:  OFF start, 2 / 6 / 10 pushes, 30 us stretches
RULERS, same job: lone looks OFF / ON (the frame); ON left alone 10 / 30 / 90 / 300 us (the fading at every stretch length used); OFF left alone 300 us.
THE WITNESSES (inside; the can't-read seat, frame held still): the stopwatch's roles by its written seed (emitters >= 3 links apart, a witness = a bit wired
to one emitter, the rest left alone). Emitters pushed ten times, 30 us stretches, started OFF or ON. Each witness is set half-way and pushed at the SAME instants
about the other axis (a Y push: rz(-pi/2) x rz(pi/2)), so its own frame turning cancels every round trip while its emitter's ON time keeps adding up. Read on
two hands a quarter turn apart. Inside (the witness's hand) and outside (the emitter's own end look) of the same pushes, in the same shots.
Brake: 3.0 s overhead + sequence, 1.25 margin, every job capped at 12 s; stops on the first job that does not land.
  python noname.py --print-estimate | --list | --check-full | --freeze-all | --dry-run | --usage | --fire --read K [--confirm-submit]      (K = 1..3)"""
import argparse, json, math, os, sys
from collections import deque
import numpy as np
import common
from common import *

CHIP = 'ibm_pittsburgh'; READS = [1, 2, 3]; RUN0 = 120; SHOTS_J = 216; CAP_S = 12; SEED_ROLES = 20261810     # the stopwatch's role seed: same roles
common.SHOTS = SHOTS_J
for k in READS: common.SEED_ORDER[RUN0 + k] = 20262310 + k
common.code_files = lambda r: ['common.py', 'live.py', 'noname.py', 'analyze.py']
common.ISA_OPS = set(common.ISA_OPS) | {'rz', 'barrier'}
ROLES = {}


def _realize(dt, w):
    n = int(round(w * 1e-6 / dt / GRID_DT)) * GRID_DT; return n, n * dt * 1e6


def _real_total(dt, sp):
    if sp.get('pushes') is not None and sp['kind'] in ('core', 'witness'): return sum(_realize(dt, d)[1] for d in sp['pushes'] if d)
    return _realize(dt, sp['pre_waits_us'][0])[1] if sp['pre_waits_us'][0] else 0.0


common.realize_wait = _realize
common.nominal_real = lambda specs, dt=NOMINAL_DT: {sp['key']: [_real_total(dt, sp)] for sp in specs}
nominal_real = common.nominal_real


def _arm(key, start, pushes, kind='core', flip=False, hand=None):
    return {'key': key, 'start': start, 'pre_waits_us': [sum(pushes)], 'pushes': list(pushes), 'flip': flip, 'kind': kind, 'hand': hand}


def specs():
    sp = [_arm('F0', 'OFF', [], 'frame'), _arm('F1', 'ON', [], 'frame')]
    for L in (10, 30, 90, 300):
        sp.append({'key': f'R{L}', 'start': 'ON', 'pre_waits_us': [L], 'pushes': None, 'flip': False, 'kind': 'ruler', 'hand': None})
    sp.append({'key': 'Z300', 'start': 'OFF', 'pre_waits_us': [300], 'pushes': None, 'flip': False, 'kind': 'ruler', 'hand': None})
    for off, on in ((30, 30), (10, 30), (90, 30), (30, 10), (30, 90)):
        sp.append(_arm(f'A{off}_{on}', 'OFF', [off, on] * 5))                      # OFF start: the first stretch is OFF
    sp.append(_arm('A30_30f', 'OFF', [30, 30] * 5, flip=True))
    sp.append(_arm('B30_30', 'ON', [30, 30] * 5))                                  # ON start: the first stretch is ON
    sp.append(_arm('B30_30f', 'ON', [30, 30] * 5, flip=True))
    sp.append(_arm('N2', 'OFF', [30, 30] * 1)); sp.append(_arm('N6', 'OFF', [30, 30] * 3))
    for st, lab in (('OFF', 'WA'), ('ON', 'WB')):
        for h in ('X', 'Y'): sp.append(_arm(f'{lab}|{h}', st, [30, 30] * 5, 'witness', hand=h))
    return sp


def set_roles(n, edges, source):
    """the stopwatch's rule, same seed: emitters in a written-seed order, each at least 3 links from every earlier one; witnesses = bits wired to an emitter;
    the rest are left alone."""
    nb = {q: set() for q in range(n)}
    for a, b in edges:
        if a < n and b < n: nb[a].add(b); nb[b].add(a)
    def near(s):
        d = {s: 0}; qd = deque([s])
        while qd:
            u = qd.popleft()
            if d[u] == 2: continue
            for v in nb[u]:
                if v not in d: d[v] = d[u] + 1; qd.append(v)
        return set(d)
    em, blocked = [], set()
    for q in np.random.default_rng(SEED_ROLES).permutation(n):
        q = int(q)
        if q in blocked or not nb[q]: continue
        em.append(q); blocked |= near(q)
    wit = {w: e for e in em for w in nb[e]}
    ROLES.clear(); ROLES.update({'n': n, 'source': source, 'emitters': sorted(em), 'witness_of': {int(k): int(v) for k, v in wit.items()},
                                 'alone': sorted(set(range(n)) - set(em) - set(wit)), 'edges': sorted([sorted(e) for e in {tuple(sorted(e)) for e in edges}])})
    return ROLES


def _pittsburgh_edges():
    """Pittsburgh's own wiring as read from its static configuration at the look-time fire (data/reads/looktime_roles.json)."""
    return json.load(open(os.path.join(HERE, 'data', 'reads', 'looktime_roles.json')))['edges']


def _build_circuit(n_qubits, dt, all_q, sp):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key']); reg = ClassicalRegister(len(all_q), 'L1'); qc.add_register(reg); qs = list(all_q)
    if sp['kind'] in ('frame', 'core', 'ruler'):
        if sp['start'] == 'ON': qc.x(qs)
        if sp['kind'] == 'ruler':
            n, us = _realize(dt, sp['pre_waits_us'][0]); qc.delay(n, qs, unit='dt'); real = [us]
        else:
            tot = 0.0
            for d in sp['pushes']:
                if d:
                    n, us = _realize(dt, d); qc.delay(n, qs, unit='dt'); tot += us
                qc.x(qs)
            if sp['flip']: qc.x(qs)
            real = [tot]
    else:
        if not ROLES or ROLES.get('n') != n_qubits: set_roles(n_qubits, _pittsburgh_edges() if n_qubits == 156 else [], 'Pittsburgh wiring (look-time fire snapshot)')
        E = [q for q in qs if q in set(ROLES['emitters'])]; W = [q for q in qs if q in ROLES['witness_of']]
        if sp['start'] == 'ON' and E: qc.x(E)
        if W: qc.sx(W)
        tot = 0.0
        for d in sp['pushes']:
            n, us = _realize(dt, d); qc.delay(n, qs, unit='dt'); tot += us
            if E: qc.x(E)
            if W: qc.rz(-math.pi / 2, W); qc.x(W); qc.rz(math.pi / 2, W)
        qc.barrier(qs)
        if W:
            if sp['hand'] == 'Y': qc.rz(math.pi / 2, W)
            qc.sx(W)
        qc.barrier(qs); real = [tot]
    for j, q in enumerate(qs): qc.measure(q, reg[j])
    return qc, real


def _want(sp, nq, nE, nW):
    P = len(sp['pushes'] or [])
    if sp['kind'] == 'frame': return {'x': nq * (sp['start'] == 'ON'), 'sx': 0, 'rz': 0, 'delay': 0, 'barrier': 0}
    if sp['kind'] == 'ruler': return {'x': nq * (sp['start'] == 'ON'), 'sx': 0, 'rz': 0, 'delay': nq, 'barrier': 0}
    if sp['kind'] == 'core':
        return {'x': nq * (P + (sp['start'] == 'ON') + bool(sp['flip'])), 'sx': 0, 'rz': 0, 'delay': nq * sum(1 for d in sp['pushes'] if d), 'barrier': 0}
    return {'x': nE * (P + (sp['start'] == 'ON')) + nW * P, 'sx': 2 * nW, 'rz': 2 * nW * P + nW * (sp['hand'] == 'Y'), 'delay': nq * P, 'barrier': 2}


def _check_ledger(T, ledger, nq):
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    by = {s['key']: s for s in specs()}
    for c in ledger['circuits']:
        qc = T[c['key']]; s = by[c['key']]; cnt = lambda n: sum(1 for i in qc.data if i.operation.name == n)
        qset = {qc.find_bit(q).index for i in qc.data if i.operation.name == 'measure' for q in i.qubits}
        nE = sum(1 for q in qset if ROLES and q in set(ROLES['emitters'])); nW = sum(1 for q in qset if ROLES and q in ROLES['witness_of'])
        want = _want(s, nq, nE, nW); got = {k: cnt(k) for k in want}
        if cnt('measure') != nq or got != want or [r.name for r in qc.cregs] != ['L1']:
            raise RuntimeError(f"ledger mismatch in {c['key']}: measures {cnt('measure')} (want {nq}); got {got}; want {want}")


common.build_circuit = _build_circuit
common.check_ledger_vs_circuits = _check_ledger
_orig_cfg = common.chip_config


def _cfg(be):
    c = be.configuration(); set_roles(int(c.n_qubits), [list(e) for e in c.coupling_map], f'{CHIP} static configuration, read at fire')
    json.dump(ROLES, open(os.path.join(HERE, 'data', 'reads', 'noname_roles.json'), 'w'))
    return _orig_cfg(be)


common.chip_config = _cfg


def _all_bits(n):
    g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    return {'groups': g, 'all_q': list(range(n)), 'seed': None, 'how': 'EVERY bit of the chip (roles by written seed from the wiring; no usability check)'}


def _dry_bits(n):
    """dry run only (12 bits max): one emitter, its witnesses, and bits left alone around them, so every role's code path runs."""
    set_roles(n, _pittsburgh_edges(), 'Pittsburgh wiring (look-time fire snapshot), dry run'); e = ROLES['emitters'][0]
    pick = [e] + [w for w, x in ROLES['witness_of'].items() if x == e]
    pick += [q for q in ROLES['alone'] if q not in pick][: 12 - len(pick) - (12 - len(pick)) % 3 if False else 12 - len(pick)]
    pick = sorted(pick[:12]); g = [pick[i:i + 3] for i in range(0, len(pick), 3)]
    return {'groups': g, 'all_q': pick, 'seed': None, 'how': f'DRY RUN: emitter {e}, its witnesses, and bits left alone'}


def _check(chip, box):
    if chip != CHIP or box != 'blank': sys.exit(f'REFUSED: the no-name shot fires on {CHIP} only, blind path.')


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


def check_full():
    """Every circuit at full size (156 bits, Pittsburgh's wiring, nominal tick): structure, ledger, op counts, roles, laid times. No account, no chip."""
    sp = specs(); set_roles(156, _pittsburgh_edges(), 'Pittsburgh wiring (look-time fire snapshot)')
    lt = json.load(open(os.path.join(HERE, 'data', 'reads', 'looktime_roles.json')))
    same = (ROLES['emitters'] == lt['emitters'] and {int(k): v for k, v in lt['witness_of'].items()} == ROLES['witness_of'])
    T, real = build_all(156, NOMINAL_DT, list(range(156)), sp); check_structure(T, list(range(156)), 156)
    led = build_ledger(RUN0 + 1, sp, real); ledger_self_check(led); _check_ledger(T, led, 156)
    print(f"FULL SIZE OK: {len(T)} circuits x 156 bits; roles: {len(ROLES['emitters'])} emitters, {len(ROLES['witness_of'])} witnesses, {len(ROLES['alone'])} left alone; "
          f"same roles as the look-time fire: {same}")
    for s in sp:
        qc = T[s['key']]; ops = {}
        for i in qc.data: ops[i.operation.name] = ops.get(i.operation.name, 0) + 1
        print(f"  {s['key']:<9} {s['kind']:<8} start {s['start']:<3} laid {real[s['key']][0]:8.3f} us  pushes {len(s['pushes'] or [])}{' +1 at once' if s['flip'] else ''}  ops {ops}")
    print_est('no-name read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for f in ('print-estimate', 'list', 'check-full', 'freeze-all', 'dry-run', 'usage', 'fire', 'confirm-submit'): ap.add_argument('--' + f, action='store_true')
    ap.add_argument('--read', type=int, choices=READS)
    a = ap.parse_args(); sp = specs()
    if a.usage:
        import live
        live.install_guard(set(), allow_submit=False); svc, tok = live.open_service(); print({k: v for k, v in svc.usage().items() if k.startswith('usage')})
        live.log_read('NO-NAME SHOT: account-level usage read; no chip named')
    elif a.print_estimate: print_est('no-name read', _est()); print('guard needs', common.SAFETY * _est()['per_job_total_s'], 's per read')
    elif a.list:
        for s in sp: print(f"  {s['key']:<9} {s['kind']:<8} start {s['start']:<3} stretches {s['pushes']} {'then one more push at once' if s['flip'] else ''} {('hand ' + s['hand']) if s['hand'] else ''}")
    elif a.check_full: check_full()
    elif a.freeze_all:
        for k in READS:
            p = freeze_path(RUN0 + k, CHIP)
            if os.path.exists(p): sys.exit(f'{p} exists')
            info = freeze_info(RUN0 + k, sp, CHIP, 'blank'); info.update({'source': 'none (BLIND: code only; no account contact)', 'frozen_at': now_iso(), 'read': k, 'shots_per_circuit': SHOTS_J})
            json.dump(info, open(p, 'w'), indent=1)
        print('FROZEN no-name reads 1-3', info['frozen_at'])
    elif a.dry_run:
        common.blind_groups = _dry_bits
        dry_run(RUN0 + 1, sp, 'ibm_drynoname', 'blank', 60, None, 0.95, None, None)
    elif a.fire:
        common.blind_groups = _all_bits
        fire(RUN0 + a.read, sp, CHIP, 'blank', None, a.confirm_submit)
    else: ap.print_help()
