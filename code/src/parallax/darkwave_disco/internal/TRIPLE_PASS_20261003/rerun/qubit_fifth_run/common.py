"""Shared plumbing for the THREE RUNS on THREE CHIPS (spec: ../../QUBIT_THREE_RUNS_APPROVED_20261001.md incl. the night amendments;
v4 = the fixed list A-L after the mechanical fire-code check: pinned sampler options, the machine's reset in the ledger, raw payload first,
MAKER read once, blind submit path for MAKER and BLANK, run-major fire order enforced). Earlier versions are kept as *_v3.py / *_v2.py / *_v1.py.

THIS FILE SUBMITS NOTHING unless a run script is called with --fire --confirm-submit AND the freeze/guards pass AND the account has the
seconds. The build agent never calls --fire. Dry runs use the saved FakeKingston snapshot only (no account contact).
THE DRY RUN PROVES THE CODE PATH ONLY, NOT THE PHYSICS: local simulation has no raw I/Q, so dry-run I/Q is SYNTHETIC.

BOXES ARE WHOLE CHIPS (owner, 2026-10-01): OURS = ibm_kingston (sealed predictions with numbers + widths); MAKER = a never-touched chip whose
published calibration, read ONCE at freeze time, is the only prediction (at fire time it is submitted to BLIND, exactly like BLANK); BLANK = a never-touched chip with NO prediction, NO calibration read, NO
properties fetched. Which two of ibm_boston / ibm_phoenix / ibm_pittsburgh are MAKER and BLANK is drawn by the written seed SEED_CHIPS; the
third is never touched. A prediction, or any read of a chip's numbers, is a look at that chip.

Vocabulary: START (OFF / MID = both-and-neither / ON), LOOK (one reading, raw I/Q kept), WAIT (time between events).
A circuit is described by pre_waits_us: for each look, the wait immediately BEFORE it (0 = none).
  Run 1: [w]  START, WAIT w, LOOK   Run 2: [0, w]  START, LOOK, WAIT w, LOOK   Run 3: [0, a, b]  START, LOOK, WAIT a, LOOK, WAIT b, LOOK
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')          # single process, one thread: another long job owns this Mac
import argparse, datetime, hashlib, importlib, json, math, sys, time, warnings
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

STARTS = ['OFF', 'MID', 'ON']                           # OFF = nothing put in / MID = both-and-neither (one sx) / ON = x
# FIX 1: THE WAITS CLOSE. short + medium = long, so the twin (short,medium)/(medium,short) lands its third look at exactly the LONG elapsed wait.
WAITS_US = [60, 240, 300]                               # short / medium / long (requested)
WAIT_NAMES = {60: 'short', 240: 'medium', 300: 'long'}
assert WAITS_US[0] + WAITS_US[1] == WAITS_US[2]
SHORT, MEDIUM, LONG = WAITS_US
TWINS = [(SHORT, MEDIUM), (SHORT, LONG), (MEDIUM, LONG)]  # each listed short-then-long; its mirror is (b, a)
RUN3_LAYOUTS = [(a, b) for (a, b) in TWINS] + [(b, a) for (a, b) in TWINS]
MATCHED_TWIN = (SHORT, MEDIUM)                          # the ONLY twin whose third look sits at the LONG elapsed wait (matched to runs 1 and 2)
GRID_DT = 16                                            # waits are laid as whole multiples of 16 dt (acquire alignment safe on real Heron)
NOMINAL_DT = 4e-9                                       # ibm_kingston dt as READ LIVE 2026-10-01 (live_kingston_readonly_20261001.json)

# ---- chips and boxes
CHIP_OURS = 'ibm_kingston'
CHIP_CANDIDATES = ['ibm_boston', 'ibm_phoenix', 'ibm_pittsburgh']
SEED_CHIPS = 20261061                                   # WRITTEN seed: which never-touched chip is MAKER, which BLANK, which is left alone
SEED_BLIND = 20261051                                   # WRITTEN seed: BLANK qubit indices, drawn blind from 0..N-1
SEED_QUBITS = 20261001                                  # OURS / MAKER: shuffle of the live qubit list
BOXES = ['ours', 'maker', 'blank']
SEED_ORDER = {1: 20261011, 2: 20261012, 3: 20261013}    # circuit order: a different written seed per run
SEED_SYNTH = 20261021                                   # synthetic I/Q (dry run only)
N_GROUPS = 3                                            # groups of three per chip (9 qubits; qubits run in parallel, no QPU cost)


def chip_assignment():
    """{'ours': kingston, 'maker': ?, 'blank': ?, 'left_alone': ?} from the written seed. No account contact."""
    perm = np.random.default_rng(SEED_CHIPS).permutation(3)
    return {'ours': CHIP_OURS, 'maker': CHIP_CANDIDATES[int(perm[0])], 'blank': CHIP_CANDIDATES[int(perm[1])], 'left_alone': CHIP_CANDIDATES[int(perm[2])]}


def box_of_chip(chip):
    a = chip_assignment()
    for b in ('ours', 'maker', 'blank'):
        if a[b] == chip: return b
    return 'left_alone' if a['left_alone'] == chip else None


def check_chip_box(chip, box):
    """Refuse a chip/box pair that disagrees with the written-seed assignment, and refuse the left-alone chip outright."""
    a = chip_assignment()
    if chip == a['left_alone']: sys.exit(f'REFUSED: {chip} is the left-alone chip: it is never touched in any way.')
    if box not in BOXES: sys.exit(f'REFUSED: --box must be one of {BOXES}')
    if a[box] != chip: sys.exit(f'REFUSED: by the written seed {SEED_CHIPS} the {box.upper()} chip is {a[box]}, not {chip}.')


# ---- run / shot sizing (fix 4 + the nine-jobs change). ONE shot count for all nine jobs.
SHOTS = 839                                             # see size_shots(): largest S with the nine-job PER-JOB estimate <= PER_JOB_BUDGET_S
ACCOUNT_S = 133.0                                       # the instance's seconds
PER_JOB_BUDGET_S = 100.0                                # per-job estimate (3.0 s per job + sequence) for all nine <= this: margin 33 s, and 1.25 x it <= 133
SAFETY = 1.25                                           # fire guard: remaining seconds must hold SAFETY x (per-job estimates of this job + every job still to come)
REP_DELAY_S = 500e-6                                    # fixed for all runs; recorded
READOUT_US = 2.2                                        # per-look readout duration (ibm_kingston measure read live: 2.18 us)
GATE_US = 0.05
OVERHEAD_S = 42.0 / 14.0                                # 3.0 s per job, measured from the real echo run (sealed_disco2)
FIRE_ORDER = [(r, b) for r in (1, 2, 3) for b in ('ours', 'maker', 'blank')]   # run-major: see the build report for why

SEEN_LEVELS = {'none': [], 'maker': [], 'run1': [1], 'runs1+2': [1, 2]}      # data a prediction (OURS) may have been written from
ALLOWED_SEEN = {1: ['none', 'maker'], 2: ['none', 'maker', 'run1'], 3: ['none', 'maker', 'run1', 'runs1+2']}
DRY_MAX_QUBITS = 12

# FIX A: THE MACHINE'S RESET IS A LOOK. The maker's own action before our START, counted as a look by the machine, identical on all three chips.
MACHINE_RESET_WHAT = ("THE MACHINE'S RESET (init_qubits): the maker's own action before our START; counted as a look by the machine; identical on all three chips; "
                      "whether it reads the bit cannot be confirmed from code.")
MACHINE_RESET_WHEN = 'at the start of each shot, before our START'
ZERO_EARLIER = "zero earlier looks of ours (after the machine's reset)"
# FIX A: the SamplerV2 server-side options we PIN (qiskit-ibm-runtime 0.49). Every other option stays Unset; the list of what exists is in the build report.
PINNED_OPTIONS = {'execution.init_qubits': True, 'execution.meas_type': 'kerneled', 'execution.rep_delay': REP_DELAY_S,
                  'dynamical_decoupling.enable': False, 'twirling.enable_gates': False, 'twirling.enable_measure': False}
WORST_PER_CIRCUIT_S = 3.0                               # the code's own worst case: 3.0 s charged to every circuit (FIX I)


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')


def parse_iso(s):
    return datetime.datetime.fromisoformat(s)


# ----------------------------------------------------------------------------------------------- timing grid (fix 1)
def wait_dt_counts(dt, grid=GRID_DT):
    """dt counts for the three waits, all whole multiples of `grid`, with short + medium == long EXACTLY (medium = long - short)."""
    n_long = int(round(LONG * 1e-6 / dt / grid)) * grid
    n_short = int(round(SHORT * 1e-6 / dt / grid)) * grid
    n_med = n_long - n_short
    assert n_med % grid == 0 and n_short > 0 and n_med > 0 and n_short + n_med == n_long
    return {SHORT: n_short, MEDIUM: n_med, LONG: n_long}


def realize_wait(dt, w_us):
    n = wait_dt_counts(dt)[w_us]
    return n, n * dt * 1e6


def nominal_real(specs, dt=NOMINAL_DT):
    c = wait_dt_counts(dt)
    return {sp['key']: [(c[w] * dt * 1e6 if w else 0.0) for w in sp['pre_waits_us']] for sp in specs}


# ----------------------------------------------------------------------------------------------- qubit groups (fix 7 + BLANK)
def groups_from_list(cand, seed=SEED_QUBITS):
    """Seeded draw of 3 groups of three from a LIST of qubit numbers (the live backend's current list at freeze time)."""
    pool = sorted(int(q) for q in cand)
    rng = np.random.default_rng(seed); rng.shuffle(pool)
    groups = [sorted(int(q) for q in pool[3 * i: 3 * i + 3]) for i in range(N_GROUPS)]
    return {'groups': groups, 'all_q': sorted(q for g in groups for q in g), 'seed': seed, 'n_candidates': len(pool), 'how': 'seeded shuffle of the chip\'s current qubit list'}


def blind_groups(n_qubits):
    """BLANK: indices drawn BLIND by the written seed from 0..N-1. No calibration, no usability check beforehand: if a drawn qubit is dead,
    that is a row in the results."""
    pool = [int(q) for q in np.random.default_rng(SEED_BLIND).permutation(int(n_qubits))[:3 * N_GROUPS]]
    groups = [sorted(pool[3 * i: 3 * i + 3]) for i in range(N_GROUPS)]
    return {'groups': groups, 'all_q': sorted(pool), 'seed': SEED_BLIND, 'n_candidates': int(n_qubits), 'how': 'BLIND draw 0..N-1 (no calibration read, no usability check)'}


class FaultyLookupFailed(RuntimeError):
    pass


def candidates_from_backend(be, strict=True, info=None):
    """Qubits of a backend (live or fake) that have measure, x, sx in the target and are not listed faulty. Reads the target (calibration).
    FIX K: if the faulty-qubit lookup FAILS, strict (OURS) REFUSES with FaultyLookupFailed instead of passing the list unfiltered. strict=False (MAKER at its
    one freeze-time read) records the failure in `info` loudly and returns the unfiltered list. info receives {'faulty_lookup': 'ok' | 'FAILED: ...', 'faulty': [...]}."""
    t = be.target
    cand = [q for q in range(be.num_qubits) if all(t[op].get((q,)) is not None for op in ('measure', 'x', 'sx'))]
    try:
        bad = set(int(q) for q in be.properties().faulty_qubits())
        if info is not None: info.update({'faulty_lookup': 'ok', 'faulty': sorted(bad)})
    except Exception as ex:
        why = f'{type(ex).__name__}: {str(ex)[:200]}'
        if info is not None: info.update({'faulty_lookup': f'FAILED: {why}', 'faulty': None})
        if strict: raise FaultyLookupFailed(f'the faulty-qubit lookup failed ({why}): refusing to pass an unfiltered qubit list')
        bad = set()
    return [q for q in cand if q not in bad]


def maker_clock(be, qubits):
    """The maker's published clock values (T1/T2 from backend properties) = the OUTSIDE reading. Seconds -> us. FIX K: a value that cannot be read is None AND
    its reason is kept in out['reasons'] (printed as CAN'T READ with the reason by the report); nothing is dropped silently."""
    p = be.properties()
    out = {'T1_us': {}, 'T2_us': {}, 'readout_error': {}, 'reasons': {}}
    for q in qubits:
        for k, f in (('T1_us', p.t1), ('T2_us', p.t2)):
            try:
                v = float(f(q)) * 1e6
                if not math.isfinite(v) or v <= 0: raise ValueError(f'published value {v!r} is not a positive finite number')
                out[k][str(q)] = v
            except Exception as ex:
                out[k][str(q)] = None; out['reasons'][f'{k}.{q}'] = f'{type(ex).__name__}: {str(ex)[:120]}'
        try: out['readout_error'][str(q)] = float(p.readout_error(q))
        except Exception as ex: out['readout_error'][str(q)] = None; out['reasons'][f'readout_error.{q}'] = f'{type(ex).__name__}: {str(ex)[:120]}'
    lu = getattr(p, 'last_update_date', None)
    if lu is None: out['reasons']['calibration_timestamp'] = 'the properties carry no last_update_date'
    return out, (lu.isoformat() if lu is not None else None)


def maker_values(clock, key):
    """(array of the usable published values, number of qubits asked, plain reason text for the ones that are missing). Used by the report: never silent."""
    d = (clock or {}).get(key) or {}
    vals = np.array([v for v in d.values() if v], float)
    miss = [q for q, v in d.items() if not v]
    rs = (clock or {}).get('reasons') or {}
    why = '; '.join(f"q{q}: {rs.get(f'{key}.{q}', 'value missing in the file')}" for q in miss[:4]) + (' ...' if len(miss) > 4 else '')
    return vals, len(d), why


# ----------------------------------------------------------------------------------------------- the LOOK LEDGER (fix 5)
PRE_RUN1_STATIC = [
    {'date': '2026-10-01', 'what': 'read-only account check: REMAINING TIME (usage) -- by the v1 build pass; it then read 0 seconds left until 2026-10-22 on the old instance',
     'touched_a_bit': False, 'time_of_day': 'not on file'},
    {'date': '2026-10-01', 'what': 'read-only account check: WHICH KEYS SEE THE INSTANCE (keys tried against the instance; none printed)', 'touched_a_bit': False, 'time_of_day': 'not on file'},
    {'date': '2026-10-01', 'what': 'read-only account check: THE BACKEND LIST (names)', 'touched_a_bit': False, 'time_of_day': 'not on file'},
    {'date': '2026-10-01', 'what': "ONE read of the maker's published calibration numbers (T1/T2/readout of the drawn qubits, ibm_kingston) by an earlier build pass (v1 live_probe.py)",
     'touched_a_bit': False, 'time_of_day': 'not on file'},
    {'date': '2026-10-01', 'what': "ledger line: the instance's COST LIMIT was noted (the amount is not on file in this folder)", 'touched_a_bit': False, 'time_of_day': 'not on file'},
]


def pre_run1_section():
    """THE OPENING SECTION of every look ledger: LOOKS TAKEN BEFORE RUN 1. Static list + every read logged by live.log_read before run 1 began
    (any further read-only account or calibration read gets appended to account_reads_log.jsonl and shows up here). None touched a bit."""
    dyn = []
    p = os.environ.get('QTR_READ_LOG') or os.path.join(HERE, 'account_reads_log.jsonl')
    if os.path.exists(p):
        r1 = []
        for d in (os.path.join(HERE, 'data', 'fire'),):
            if os.path.isdir(d):
                for c in os.listdir(d):
                    mp = os.path.join(d, c, 'run1_meta.json')
                    if os.path.exists(mp):
                        try: r1.append(parse_iso(json.load(open(mp))['start_time']))
                        except Exception: pass
        cut = min(r1) if r1 else None
        for line in open(p):
            try: rec = json.loads(line)
            except Exception: continue
            if cut is None or parse_iso(rec['at']) < cut:
                dyn.append({'date': rec['at'][:10], 'time_of_day': rec['at'][11:19], 'what': rec['what'], 'touched_a_bit': rec.get('touched_a_bit', False),
                            'requests': [f"{q['method']} {q.get('path', q.get('host'))}" + (f" REFUSED({q['REFUSED']})" if q.get('REFUSED') else '') for q in rec.get('requests', [])]})
    return {'title': 'LOOKS TAKEN BEFORE RUN 1', 'none_touched_a_bit': all(not e['touched_a_bit'] for e in PRE_RUN1_STATIC + dyn),
            'entries': PRE_RUN1_STATIC + dyn}


def plain_words(sp, real=None):
    ev = [f"MACHINE RESET (init_qubits, the maker's own action) {MACHINE_RESET_WHEN}", f"START {sp['start']}"]
    for k, w in enumerate(sp['pre_waits_us']):
        if w: ev.append(f'WAIT {w} us' + (f' (realized {real[k]:.3f} us)' if real else ''))
        ev.append(f'LOOK {k + 1} [{k} look(s) of ours before it' + (" (after the machine's reset)" if k == 0 else '') + ']')
    return '; '.join(ev)


def build_ledger(run_no, specs, real=None, include_pre=True, shots=None):
    """THE LOOK LEDGER: opens with 'LOOKS TAKEN BEFORE RUN 1', then every circuit, its count of looks and where each look sits.
    real = {key: [realized pre-wait us per look]} (None = requested values only; freeze.py hashes that form with include_pre=False)."""
    circuits = []
    for sp in specs:
        pw = sp['pre_waits_us']; n = len(pw); rl = real[sp['key']] if real else None
        looks = []
        for k, w in enumerate(pw):
            after = pw[k + 1] if k + 1 < n else None
            looks.append({'look': k + 1, 'looks_before': k, 'wait_just_before_us': w, 'wait_just_before_realized_us': (rl[k] if rl else None), 'wait_just_after_us': after,
                          'sits': ("after the machine's reset and START" if k == 0 else f'after look {k}') + (f' and a WAIT of {w} us' if w else ' (no wait)')
                                  + (f', before a WAIT of {after} us' if after else ', last look')})
        circuits.append({'key': sp['key'], 'start': sp['start'], 'n_looks': n, 'pre_waits_us': list(pw),
                         'pre_waits_realized_us': list(rl) if rl else None, 'looks': looks, 'plain': plain_words(sp, rl),
                         'machine_reset': {'when': MACHINE_RESET_WHEN, 'what': MACHINE_RESET_WHAT, 'counted_as_a_look_by': 'the machine', 'ours': False}})
    led = {}
    if include_pre: led['looks_taken_before_run_1'] = pre_run1_section()
    sh = SHOTS if shots is None else int(shots)
    led.update({'run': run_no, 'n_circuits': len(circuits), 'n_looks_total': int(sum(c['n_looks'] for c in circuits)),
                'n_machine_resets_per_shot': len(circuits), 'machine_reset_events_total': len(circuits) * sh,
                'machine_reset_statement': 'Every circuit on every chip begins each shot with ' + MACHINE_RESET_WHAT + " Our looks are counted separately; Run 1 has " + ZERO_EARLIER + '.',
                'looks_per_circuit': sorted({c['n_looks'] for c in circuits}), 'calibration_or_test_circuits': 0,
                'statement': 'Every circuit of this run is listed here. There are no separate calibration or test circuits: the OFF and ON starts are the calibration and the data at once.',
                'circuits': circuits})
    return led


def ledger_self_check(ledger):
    bad = [c['key'] for c in ledger['circuits'] if c['start'] not in STARTS]
    if bad: raise RuntimeError(f'circuits outside the three starts (a calibration/test circuit?): {bad}')
    if ledger['n_looks_total'] != sum(len(c['looks']) for c in ledger['circuits']): raise RuntimeError('ledger look count mismatch')
    # FIX A: the machine's reset is counted: every circuit carries exactly one reset entry per shot, and the totals agree.
    bad = [c['key'] for c in ledger['circuits'] if (c.get('machine_reset') or {}).get('what') != MACHINE_RESET_WHAT]
    if bad: raise RuntimeError(f"circuits with no machine's-reset entry in the ledger: {bad[:4]}")
    if ledger.get('n_machine_resets_per_shot') != len(ledger['circuits']): raise RuntimeError("ledger count of the machine's resets per shot does not match the circuits")
    if not isinstance(ledger.get('machine_reset_events_total'), int) or ledger['machine_reset_events_total'] % len(ledger['circuits']): raise RuntimeError("ledger total of the machine's resets is missing or not a whole number of shots per circuit")


# ----------------------------------------------------------------------------------------------- circuits (built directly on PHYSICAL qubits: no transpile, no target needed)
ISA_OPS = {'x', 'sx', 'delay', 'measure'}


def build_circuit(n_qubits, dt, all_q, sp):
    """START on every chosen qubit, then per look: (WAIT if any) then LOOK. One classical register per look so each look's raw I/Q comes back
    separately. The circuit is already in the chip's native gates (x, sx, delay, measure) on PHYSICAL qubit numbers: width = the chip's qubit
    count, ops only on the nine chosen qubits. No transpile, so no target (no calibration) is needed to BUILD it. Returns (circuit, realized pre-waits us)."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qc = QuantumCircuit(QuantumRegister(n_qubits, 'q'), name=sp['key'])
    regs = [ClassicalRegister(len(all_q), f'L{k + 1}') for k in range(len(sp['pre_waits_us']))]
    for r in regs: qc.add_register(r)
    qs = list(all_q)
    if sp['start'] == 'MID': qc.sx(qs)
    elif sp['start'] == 'ON': qc.x(qs)
    elif sp['start'] != 'OFF': raise ValueError(sp['start'])
    real = []
    for k, w in enumerate(sp['pre_waits_us']):
        if w:
            n, us = realize_wait(dt, w); real.append(us); qc.delay(n, qs, unit='dt')
        else:
            real.append(0.0)
        for j, q in enumerate(qs): qc.measure(q, regs[k][j])
    return qc, real


def build_all(n_qubits, dt, all_q, specs):
    T, real = {}, {}
    for sp in specs:
        T[sp['key']], real[sp['key']] = build_circuit(n_qubits, dt, all_q, sp)
    return T, real


def check_structure(T, all_q, n_qubits):
    """Structural ISA check that needs NO target: only x/sx/delay/measure, only the chosen physical qubits, width = the chip's qubit count."""
    for k, qc in T.items():
        if qc.num_qubits != n_qubits: raise RuntimeError(f'{k}: width {qc.num_qubits} != chip qubit count {n_qubits}')
        for inst in qc.data:
            if inst.operation.name not in ISA_OPS: raise RuntimeError(f'{k}: non-native op {inst.operation.name}')
            for q in inst.qubits:
                if qc.find_bit(q).index not in all_q: raise RuntimeError(f'{k}: op on qubit {qc.find_bit(q).index} outside the chosen set')


def check_ledger_vs_circuits(T, ledger, nq):
    if set(T) != {c['key'] for c in ledger['circuits']}: raise RuntimeError('circuit set differs from the ledger')
    for c in ledger['circuits']:
        qc = T[c['key']]
        nm = sum(1 for i in qc.data if i.operation.name == 'measure'); nd = sum(1 for i in qc.data if i.operation.name == 'delay')
        want_d = nq * sum(1 for w in c['pre_waits_us'] if w); regs = [r.name for r in qc.cregs]
        if nm != nq * c['n_looks'] or nd != want_d or regs != [f'L{k + 1}' for k in range(c['n_looks'])]:
            raise RuntimeError(f"ledger mismatch in {c['key']}: measures {nm} (want {nq * c['n_looks']}), delays {nd} (want {want_d}), registers {regs}")


# ----------------------------------------------------------------------------------------------- estimate, sizing, guards (fix 4)
def estimate(specs, real_waits, shots, rep_delay_s=REP_DELAY_S):
    """ONE job per (chip, run). per-job estimate = 3.0 s + sequence time. Worst case charges 3.0 s to every circuit (pub)."""
    seq = 0.0
    for sp in specs:
        per_shot_us = rep_delay_s * 1e6 + len(sp['pre_waits_us']) * READOUT_US + GATE_US + sum(real_waits[sp['key']])
        seq += shots * per_shot_us * 1e-6
    n = len(specs)
    return {'pubs': n, 'shots_per_pub': shots, 'rep_delay_us': rep_delay_s * 1e6, 'overhead_per_job_s': OVERHEAD_S, 'sequence_s': seq,
            'per_job_total_s': OVERHEAD_S + seq, 'per_pub_worst_s': OVERHEAD_S * n + seq}


def run_specs(r):
    return importlib.import_module(f'run{r}').specs()


def all_estimates(shots, dt=NOMINAL_DT):
    """{run: estimate} for one chip at the nominal dt."""
    return {r: estimate(run_specs(r), nominal_real(run_specs(r), dt), shots) for r in (1, 2, 3)}


def nine_job_totals(shots, dt=NOMINAL_DT):
    e = all_estimates(shots, dt)
    return {'per_job_s': 3 * sum(x['per_job_total_s'] for x in e.values()), 'worst_s': 3 * sum(x['per_pub_worst_s'] for x in e.values()),
            'per_run_per_job': {r: e[r]['per_job_total_s'] for r in e}, 'per_run_worst': {r: e[r]['per_pub_worst_s'] for r in e},
            'circuits_total': 3 * sum(x['pubs'] for x in e.values())}


def size_shots(budget=PER_JOB_BUDGET_S, dt=NOMINAL_DT):
    """Largest ONE shot count for all nine jobs whose PER-JOB estimate total is <= budget."""
    lo, hi = 1, 100000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if nine_job_totals(mid, dt)['per_job_s'] <= budget: lo = mid
        else: hi = mid - 1
    return lo


def landed(chip, r, fire_dir=None):
    d = os.path.join(fire_dir or os.path.join(HERE, 'data', 'fire'), chip)
    mp = os.path.join(d, f'run{r}_meta.json')
    try: return json.load(open(mp)).get('complete') is True
    except Exception: return False


def earlier_unlanded(this_chip, this_run, fire_dir=None):
    """FIX H. Every job EARLIER than this one in the fixed run-major order (run 1: kingston, phoenix, pittsburgh; then run 2 in that order; then run 3)
    that has not landed (complete marker). A job may fire only when this list is empty."""
    a = chip_assignment(); out = []
    for (r, b) in FIRE_ORDER:
        if (a[b], r) == (this_chip, this_run): return out
        if not landed(a[b], r, fire_dir): out.append((a[b], r))
    return out


def jobs_to_come(this_chip, this_run, fire_dir=None, dt=NOMINAL_DT):
    """Per-job estimates of THIS job and every job (all three chips, all three runs) not yet landed, this one counted once."""
    a = chip_assignment(); e = all_estimates(SHOTS, dt); out = []
    for (r, b) in FIRE_ORDER:
        chip = a[b]
        if (chip, r) == (this_chip, this_run): continue
        if not landed(chip, r, fire_dir): out.append({'chip': chip, 'run': r, 'est_s': e[r]['per_job_total_s']})
    return e[this_run]['per_job_total_s'], out


def budget_guard(usage, this_est_s, later):
    """FIX 4 GUARD. A job may start only if the account's remaining seconds cover SAFETY x (this job's per-job estimate + the estimates of every job still to
    come). The worst case (3.0 s per circuit) cannot fit nine jobs in 133 s at ANY shot count, so the per-job estimate is the basis; the worst case is printed
    beside it. If the usage answer has no remaining-seconds field (or it is not a finite number) the guard REFUSES. Returns (ok, need_s, remaining, reason)."""
    rem = usage.get('usage_remaining_seconds') if isinstance(usage, dict) else None
    need = SAFETY * (this_est_s + sum(x['est_s'] for x in later))
    if rem is None or isinstance(rem, bool) or not isinstance(rem, (int, float)) or not math.isfinite(rem):
        return False, need, rem, 'the usage call returned NO remaining-seconds field: refusing (cannot confirm the account holds the seconds)'
    if rem < need: return False, need, rem, f'only {rem:.1f} s remain; {need:.1f} s needed for this job and every job still to come'
    return True, need, rem, 'ok'


def exec_cap(remaining, this_worst_s, later_est_sum, this_est_s=None):
    """FIX I. max_execution_time (system seconds) = the code's OWN worst case for this job (3.0 s per circuit + the sequence time, est['per_pub_worst_s']),
    but never more than the remaining seconds minus the per-job estimates of the jobs still to come. Returns (cap, parts). If the cap would fall below this job's own
    per-job estimate the caller refuses (a cap under the estimate would cancel the job and bill the time for nothing)."""
    room = math.floor(remaining - later_est_sum)
    cap = int(min(math.ceil(this_worst_s), room))
    parts = {'worst_case_s': this_worst_s, 'remaining_minus_later_s': room, 'binding': 'worst case of this job' if math.ceil(this_worst_s) <= room else 'remaining minus the later jobs'}
    if this_est_s is not None and cap < this_est_s: parts['too_small'] = True
    return cap, parts


def print_est(tag, est):
    print(f"QPU-second estimate {tag}: {est['per_job_total_s']:.1f} s per-job basis (3.0 overhead + {est['sequence_s']:.2f} sequence) | "
          f"{est['per_pub_worst_s']:.1f} s worst case (3.0 s per circuit; {est['pubs']} circuits, {est['shots_per_pub']} shots, rep_delay {est['rep_delay_us']:.0f} us)")


# ----------------------------------------------------------------------------------------------- FREEZE (the hash before any prediction)
def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def freeze_path(run_no, chip):
    return os.path.join(HERE, f'freeze_{chip}_run{run_no}.json')


def code_files(run_no):
    return ['common.py', 'live.py', f'run{run_no}.py', 'analyze.py']


def freeze_info(run_no, specs, chip, box, groups=None, maker=None):
    """OURS / MAKER: hash of the code (common.py, live.py, run{N}.py, analyze.py) + the look ledger (requested form, circuits only) + the qubit groups
    (+ for MAKER the published calibration read at freeze time = its prediction). BLANK: the code and the SEED only (no ledger, no groups, no chip data)."""
    files = {n: sha256_file(os.path.join(HERE, n)) for n in code_files(run_no)}
    if box == 'blank':
        body = {'files': files, 'seed_blind': SEED_BLIND, 'seed_chips': SEED_CHIPS, 'chip': chip, 'box': box}
        return {'run': run_no, 'chip': chip, 'box': box, 'files': files, 'seed_blind': SEED_BLIND, 'ledger_sha256': None,
                'combined_sha256': hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()}
    ledger_sha = hashlib.sha256(json.dumps(build_ledger(run_no, specs, include_pre=False), sort_keys=True).encode()).hexdigest()
    mk = {k: maker.get(k) for k in ('calibration_timestamp', 'T1_us', 'T2_us', 'readout_error')} if maker else None     # stable parts only (not the read time)
    body = {'files': files, 'ledger': ledger_sha, 'groups': groups, 'maker': mk, 'chip': chip, 'box': box}
    return {'run': run_no, 'chip': chip, 'box': box, 'files': files, 'ledger_sha256': ledger_sha, 'groups': groups,
            'combined_sha256': hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()}


def recompute_hash_from_freeze(fz, specs):
    """The hash of the code on disk NOW, using the groups / maker numbers stored in the freeze file itself."""
    return freeze_info(fz['run'], specs, fz['chip'], fz['box'], fz.get('groups'), fz.get('maker_calibration'))['combined_sha256']


def load_prediction_header(path):
    j = json.load(open(path))
    ents = {n: {'written_at': e.get('written_at'), 'data_seen': e.get('data_seen'), 'filled': (e.get('predicted') is not None and e.get('width') is not None)}
            for n, e in j.get('predictions', {}).items()}
    return {'run': j.get('_run'), 'written_at': j.get('_written_at'), 'entries': ents}


def check_freeze(run_no, specs, chip, box, prediction_file=None):
    """Fire-path guard. Returns list of problems. Every box needs a live-source freeze whose hash matches the code now. OURS needs a prediction file
    written after the freeze; MAKER and BLANK must have NONE of ours."""
    probs = []
    fp = freeze_path(run_no, chip)
    if not os.path.exists(fp): return [f'no freeze file {os.path.basename(fp)}: run freeze.py --run {run_no} --chip {chip} --box {box} first']
    fz = json.load(open(fp))
    if fz.get('source') != 'live' and box != 'blank': probs.append(f"the freeze was written from source {fz.get('source')!r}, not the live chip")
    if fz.get('chip') != chip or fz.get('box') != box: probs.append('freeze file is for a different chip/box')
    if recompute_hash_from_freeze(fz, specs) != fz['combined_sha256']: probs.append('freeze hash does not match the code (or ledger) on disk: code changed after the freeze')
    if box == 'ours':
        if not prediction_file or not os.path.exists(prediction_file): return probs + ['OURS needs --prediction-file (the sealed, posted prediction)']
        h = load_prediction_header(prediction_file)
        if h['run'] != run_no: probs.append(f"prediction file says _run={h['run']}, this is run {run_no}")
        try:
            fz_t = parse_iso(fz['frozen_at'])
            if not h['written_at'] or parse_iso(h['written_at']) < fz_t: probs.append('prediction _written_at is earlier than (or missing from) the freeze')
            elif parse_iso(h['written_at']) > datetime.datetime.now().astimezone(): probs.append('prediction _written_at is in the future')
            for n, e in h['entries'].items():
                if not e['filled']: continue
                if not e['written_at'] or parse_iso(e['written_at']) < fz_t: probs.append(f'{n}: entry written_at earlier than the freeze (or missing)')
                elif parse_iso(e['written_at']) > datetime.datetime.now().astimezone(): probs.append(f'{n}: entry written_at is in the future (later than this fire)')
                if e['data_seen'] not in ALLOWED_SEEN[run_no]: probs.append(f"{n}: data_seen={e['data_seen']!r} not allowed for run {run_no} ({ALLOWED_SEEN[run_no]})")
        except Exception as ex:
            probs.append(f'could not read timestamps: {ex}')
    elif prediction_file:
        probs.append(f'a {box.upper()} chip takes NO prediction file of ours (MAKER: its published calibration is the only prediction; BLANK: none at all)')
    return probs[:20]


# ----------------------------------------------------------------------------------------------- results I/O (fix 3: job id on disk first; complete marker LAST)
def verify_arrays(arrays, ledger, shots, nq):
    want = {f"{c['key']}__L{k + 1}" for c in ledger['circuits'] for k in range(c['n_looks'])}
    if set(arrays) != want: raise RuntimeError(f'result arrays differ from the ledger: missing {sorted(want - set(arrays))[:3]}, extra {sorted(set(arrays) - want)[:3]}')
    for k, a in arrays.items():
        a = np.asarray(a)
        if a.shape != (shots, nq) or not np.iscomplexobj(a) or not np.all(np.isfinite(a)):
            raise RuntimeError(f'{k}: shape {a.shape} dtype {a.dtype} (want complex ({shots},{nq}), all finite)')


def save_results(out_dir, run_no, arrays, meta, ledger, shots, nq):
    """npz, ledger, maker clock (if any), and ONLY THEN the meta with complete=True (atomic). analyze.py refuses any run whose meta is not complete."""
    os.makedirs(out_dir, exist_ok=True)
    mp = os.path.join(out_dir, f'run{run_no}_meta.json')
    if os.path.exists(mp): os.remove(mp)
    verify_arrays(arrays, ledger, shots, nq)
    npz = os.path.join(out_dir, f'run{run_no}_results.npz'); tmp = npz[:-4] + '.tmp.npz'
    np.savez_compressed(tmp, **{k: np.asarray(v) for k, v in arrays.items()}); os.replace(tmp, npz)
    json.dump(ledger, open(os.path.join(out_dir, f'run{run_no}_look_ledger.json'), 'w'), indent=1)
    if meta.get('maker_clock'):
        json.dump({'what': "THE MAKER'S PUBLISHED CLOCK = the OUTSIDE reading (T1/T2 from backend properties)", 'source': meta['maker_clock_source'],
                   'calibration_timestamp': meta['calibration_timestamp'], 'saved_at': meta['maker_clock_read_at'], **meta['maker_clock']},
                  open(os.path.join(out_dir, f'run{run_no}_maker_clock.json'), 'w'), indent=1)
    meta = dict(meta, ledger=ledger, circuits=ledger['circuits'], results_sha256=sha256_file(npz), complete=True, completed_at=now_iso())
    json.dump(meta, open(mp + '.tmp', 'w'), indent=1, default=str); os.replace(mp + '.tmp', mp)


def _atomic_write(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=1, default=str); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def pending_path(out_dir, run_no): return os.path.join(out_dir, f'run{run_no}_pending.json')
def job_path(out_dir, run_no): return os.path.join(out_dir, f'run{run_no}_job.json')


def record_job_id(out_dir, run_no, job, extra=None):
    """FIX 3: the very first thing after the submit call returns -- the job id goes to disk (fsync'd) before anything is printed or awaited."""
    jid = job.job_id()
    _atomic_write(job_path(out_dir, run_no), dict({'job_id': jid, 'run': run_no, 'recorded_at': now_iso()}, **(extra or {})))
    return jid


# ----------------------------------------------------------------------------------------------- FIX E: THE RAW PAYLOAD IS SAVED FIRST
def payload_path(out_dir, run_no): return os.path.join(out_dir, f'run{run_no}_payload_raw.json')
def payload_meta_path(out_dir, run_no): return os.path.join(out_dir, f'run{run_no}_payload_meta.json')
def fire_reads_path(out_dir, run_no): return os.path.join(out_dir, f'run{run_no}_fire_reads.json')
PARSER_FILE = 'parse_payload.py'     # NOT in any freeze hash (see code_files): the parser can be repaired after the fact without breaking the freeze


def _raw_text(job):
    """The returned job payload, untouched, as text. Preferred: the service's own raw JSON text for this job's results (what job.result() would decode).
    Fallback (a handle without an api client): the result object serialized by the SDK's own RuntimeEncoder, which is lossless for the arrays."""
    ac = getattr(job, '_api_client', None)
    if ac is not None and hasattr(ac, 'job_results'):
        raw = ac.job_results(job_id=job.job_id())
        if raw is None: raise RuntimeError('the service returned an empty results payload')
        return (raw if isinstance(raw, str) else json.dumps(raw)), 'the service\'s raw results JSON text, untouched'
    from qiskit_ibm_runtime import RuntimeEncoder
    res = job.result()
    if res is None: raise RuntimeError('job.result() returned None (empty result)')
    return json.dumps(res, cls=RuntimeEncoder), 'the result object serialized by RuntimeEncoder (lossless), because the handle has no api client'


def fetch_and_save_payload(job, out_dir, run_no):
    """THE FIRST THING AFTER THE JOB COMPLETES: wait once for the final state, save the raw payload (fsync'd, atomic) with its sha256 and the job's own metadata
    (its timestamps and usage). NOTHING is parsed here. Raises with the service's own explanation if the job did not finish DONE."""
    os.makedirs(out_dir, exist_ok=True)
    if hasattr(job, 'wait_for_final_state'): job.wait_for_final_state()
    st = str(job.status())
    if 'DONE' not in st and 'COMPLETED' not in st.upper():
        job.result()                                            # raises the SDK's own explanation (e.g. max_execution_time, reason 1305)
        raise RuntimeError(f'job ended with status {st}; no payload saved')
    raw, how = _raw_text(job)
    pp = payload_path(out_dir, run_no); tmp = pp + '.tmp'
    with open(tmp, 'w') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, pp)
    try: metrics, merr = job.metrics(), None
    except Exception as ex: metrics, merr = None, f'{type(ex).__name__}: {str(ex)[:200]}'
    _atomic_write(payload_meta_path(out_dir, run_no), {'run': run_no, 'job_id': job.job_id(), 'saved_at': now_iso(), 'how': how, 'bytes': len(raw.encode()),
                                                       'sha256': hashlib.sha256(raw.encode()).hexdigest(), 'job_metrics': metrics, 'job_metrics_error': merr,
                                                       'note': 'the raw payload, saved before any parsing. Rebuild the results with: python recover.py --reparse --run N --chip C --box B'})
    return pp


def _job_times(metrics):
    """FIX K: end_time and the running-start time from the JOB'S OWN METADATA, never from the client clock. None (with the reason) when absent."""
    ts = ((metrics or {}).get('timestamps') or {}) if isinstance(metrics, dict) else {}
    return {'end_time': ts.get('finished'), 'job_running_at': ts.get('running'), 'job_created_at': ts.get('created'),
            'end_time_source': ('the job\'s own metadata (metrics.timestamps.finished)' if ts.get('finished') else
                                "CAN'T READ: the job metadata has no 'finished' timestamp (the client clock is NOT used instead)")}


def finalize_from_saved_payload(out_dir, run_no, specs):
    """Read the SAVED raw payload (never the network), parse it with parse_payload.py (a separate file, outside the freeze), verify against the ledger and
    save with the complete marker LAST. Used by the fire path (right after fetch_and_save_payload) and by `recover.py --reparse`."""
    import importlib
    pend = json.load(open(pending_path(out_dir, run_no))); pm = json.load(open(payload_meta_path(out_dir, run_no)))
    raw = open(payload_path(out_dir, run_no)).read()
    if hashlib.sha256(raw.encode()).hexdigest() != pm['sha256']: raise RuntimeError('the saved raw payload no longer matches its recorded sha256: refusing to parse')
    pf = os.path.join(HERE, PARSER_FILE)
    if not os.path.exists(pf): raise RuntimeError(f'{PARSER_FILE} is missing')
    if HERE not in sys.path: sys.path.insert(0, HERE)
    parser = importlib.import_module('parse_payload'); importlib.reload(parser)
    order = pend['order']; shots = pend['shots']; nq = len(pend['meta']['all_q'])
    arrays = parser.parse(raw, order, specs, shots, nq)
    ledger = build_ledger(run_no, specs, pend['real'], shots=shots)
    fr = fire_reads_path(out_dir, run_no)
    if os.path.exists(fr): ledger['reads_at_fire'] = json.load(open(fr))
    ledger_self_check(ledger)
    jt = _job_times(pm.get('job_metrics'))
    meta = dict(pend['meta'], job_id=pm['job_id'], result_read_at=now_iso(), payload_file=os.path.basename(payload_path(out_dir, run_no)), payload_sha256=pm['sha256'],
                payload_how=pm['how'], parser_file=PARSER_FILE + ' (OUTSIDE the freeze: not in any freeze hash)', parser_sha256=sha256_file(pf), job_metrics=pm.get('job_metrics'), **jt)
    save_results(out_dir, run_no, arrays, meta, ledger, shots, nq)
    return meta


def finalize_from_job(job, out_dir, run_no, specs, wait=True):
    """Shared by fire and recover.py: (1) save the raw payload, untouched, as the first thing after the job completes; (2) parse FROM THE SAVED PAYLOAD."""
    fetch_and_save_payload(job, out_dir, run_no)
    return finalize_from_saved_payload(out_dir, run_no, specs)


# ----------------------------------------------------------------------------------------------- FIX A: pinned sampler options
def options_dump(o, prefix=''):
    """Every option that is NOT Unset, as {dotted name: value} (what is actually sent to the server)."""
    import dataclasses
    out = {}
    for f in dataclasses.fields(o):
        v = getattr(o, f.name)
        if dataclasses.is_dataclass(v): out.update(options_dump(v, prefix + f.name + '.'))
        elif type(v).__name__ != 'UnsetType': out[prefix + f.name] = v
    return out


def pin_sampler_options(sm, cap=None, tags=None):
    """FIX A: THE MACHINE'S RESET IS A LOOK, so no server-side default is left to chance. Pins every SamplerV2 option that could add a look or an extra action:
    execution.init_qubits = True (the machine's own reset, stated), dynamical decoupling OFF, twirling OFF (gates and measure). SamplerV2 in qiskit-ibm-runtime 0.49 has NO
    measurement-mitigation / resilience option at all (SamplerOptions has no such field), so there is none to switch off. Returns the dump of what is set."""
    o = sm.options
    o.execution.init_qubits = True; o.execution.meas_type = 'kerneled'; o.execution.rep_delay = REP_DELAY_S
    o.dynamical_decoupling.enable = False
    o.twirling.enable_gates = False; o.twirling.enable_measure = False
    if cap is not None: o.max_execution_time = int(cap)
    if tags: o.environment.job_tags = list(tags)
    d = options_dump(o)
    for k, v in PINNED_OPTIONS.items():
        if d.get(k) != v: raise RuntimeError(f'sampler option {k} is {d.get(k)!r}, not the pinned {v!r}')
    return d


def synthetic_payload(arrays, order, specs):
    """DRY RUN ONLY: serialize synthetic I/Q the way the SDK serializes a real result (RuntimeEncoder of a PrimitiveResult), so the dry run exercises the
    raw-payload -> parse_payload path. The arrays are fabricated; this proves the path, not the physics."""
    from qiskit.primitives.containers import PrimitiveResult, SamplerPubResult, DataBin
    from qiskit_ibm_runtime import RuntimeEncoder
    pubs = []
    for key in order:
        nl = len(next(sp for sp in specs if sp['key'] == key)['pre_waits_us'])
        pubs.append(SamplerPubResult(DataBin(shape=(), **{f'L{k + 1}': arrays[f'{key}__L{k + 1}'] for k in range(nl)}), metadata={}))
    return json.dumps(PrimitiveResult(pubs, metadata={}), cls=RuntimeEncoder)


# ----------------------------------------------------------------------------------------------- DRY RUN
SIM_BREAKS = []


def _brk(where, why, means):
    SIM_BREAKS.append({'where': where, 'why': why, 'means': means})
    print(f'[SIM BREAK] {where}: {why}', file=sys.stderr)


def synth_iq(bits, qubits, ro_err, rng, centers):
    shots, nq = bits.shape
    out = np.zeros((shots, nq), dtype=complex)
    for j, q in enumerate(qubits):
        c0, c1 = centers[j]; s = 0.35 + 5.0 * (ro_err.get(q) or 0.02)
        out[:, j] = np.where(bits[:, j], c1, c0) + rng.normal(0, s, shots) + 1j * rng.normal(0, s, shots)
    return out


DRY_TAU = {'ours': 300.0, 'maker': 250.0, 'blank': 350.0}   # SYNTHETIC fades, one per box so the side-by-side has something to show


def dry_run(run_no, specs, chip, box, shots, synth_tau_us=None, synth_mark=0.95, out_dir=None, prediction_file=None):
    """Simulates on FakeKingston ONLY (local). chip/box are labels + seeds: the dry run touches no account and no chip. For a BLANK box the qubits are
    drawn blind from 0..N-1 of the simulated chip and NO calibration is read from it (the synthetic readout noise uses a flat default)."""
    from qiskit_ibm_runtime import SamplerV2
    from qiskit_ibm_runtime.fake_provider import FakeKingston
    from qiskit_ibm_runtime.utils import validate_isa_circuits
    SIM_BREAKS.clear(); t_start = now_iso()
    synth_tau_us = DRY_TAU[box] if synth_tau_us is None else synth_tau_us
    sim = FakeKingston()
    N = sim.num_qubits; dt = sim.dt
    if box == 'blank':
        qs = blind_groups(N); clock, cal_ts, ro = None, None, {}
        plan_label = 'BLANK: no calibration read (synthetic readout noise = flat default)'
    else:
        qs = groups_from_list(candidates_from_backend(sim)); clock, cal_ts = maker_clock(sim, qs['all_q'])
        ro = {q: clock['readout_error'].get(str(q)) for q in qs['all_q']}
        plan_label = 'FakeKingston (saved local snapshot, 2026-04; NOT today, NOT the chip). NO IBM ACCOUNT CONTACT.'
    all_q = qs['all_q']; nq = len(all_q)
    if nq > DRY_MAX_QUBITS: raise SystemExit(f'dry run capped at {DRY_MAX_QUBITS} qubits')
    try: sim.set_options(max_memory_mb=2048, max_parallel_threads=1)
    except Exception as e: _brk('set_options on FakeKingston', repr(e), 'could not cap local sim threads/memory')
    T, real = build_all(N, dt, all_q, specs); check_structure(T, all_q, N)
    for k, qc in T.items(): validate_isa_circuits([qc], sim.target)          # proves the hand-built circuits are ISA against the (fake) target
    ledger = build_ledger(run_no, specs, real, shots=shots); ledger_self_check(ledger); check_ledger_vs_circuits(T, ledger, nq)
    est = estimate(specs, real, SHOTS)
    order = [specs[i]['key'] for i in np.random.default_rng(SEED_ORDER[run_no]).permutation(len(specs))]
    pinned = pin_sampler_options(SamplerV2(mode=sim), cap=None, tags=[f'qtr-{chip}-run{run_no}'])      # the options a real fire would send (local object, nothing sent)
    try:
        sm = SamplerV2(mode=sim); sm.options.execution.meas_type = 'kerneled'
        pr = sm.run([T[order[0]]], shots=10).result(); _ = np.asarray(getattr(pr[0].data, 'L1'))
        _brk('meas_type="kerneled" ran locally WITHOUT raising', f'returned dtype {_.dtype}, shape {_.shape}', 'if complex, the sim models kerneled; substitution still used')
    except Exception as e:
        _brk('meas_type="kerneled" (raw I/Q) via SamplerV2 on FakeKingston, local testing mode', f'{type(e).__name__}: {e}',
             'no kerneled-measurement model locally. SUBSTITUTION: same circuits, bitstring measurement; each 0/1 placed in a SYNTHETIC Gaussian cloud.')
    sm = SamplerV2(mode=sim); t0 = time.time()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always'); sm.options.execution.rep_delay = REP_DELAY_S
        res = sm.run([T[k] for k in order], shots=shots).result()
        noop = any('no effect in local testing mode' in str(x.message) for x in w)
    sim_secs = time.time() - t0
    if noop: _brk('rep_delay on SamplerV2 local testing mode', 'accepted and silently ignored', 'no between-shot thermal model locally; rep-rate effects testable only on hardware')
    rng = np.random.default_rng(SEED_SYNTH + BOXES.index(box))
    centers = []
    for j, q in enumerate(all_q):
        c0 = complex(rng.normal(0, 1.5), rng.normal(0, 1.5)); ang = rng.uniform(0, 2 * np.pi); sep = rng.uniform(3.0, 6.0)
        centers.append((c0, c0 + sep * np.exp(1j * ang)))
    arrays, obs = {}, {}
    for pi, key in enumerate(order):
        data = res[pi].data; nl = len(next(sp for sp in specs if sp['key'] == key)['pre_waits_us'])
        obs[key] = []; alive = np.ones((shots, nq), dtype=bool)
        for k in range(nl):
            bits = getattr(data, f'L{k + 1}').to_bool_array(); obs[key].append(float(bits.mean()))
            w_k = real[key][k]
            if synth_tau_us and w_k > 0: alive = alive & (rng.random(bits.shape) < np.exp(-w_k / synth_tau_us))
            if synth_mark < 1.0 and k >= 1: alive = alive & (rng.random(bits.shape) < synth_mark)
            arrays[f'{key}__L{k + 1}'] = synth_iq(bits & alive, all_q, ro, rng, centers)
    t1s = [v for v in (clock or {}).get('T1_us', {}).values() if v]          # break probe 3: does the simulated qubit fade across a WAIT at all?
    for sp in specs:
        k = sp['key']
        if sp['start'] == 'ON' and sp['pre_waits_us'] == [LONG] and t1s:
            exp_loss = float(1 - np.exp(-real[k][0] / np.median(t1s)))
            if obs[k][0] > 1 - 0.5 * exp_loss:
                _brk(f'delay instruction vs noise model ({k}: long wait before the one look)',
                     f'simulated mean bit {obs[k][0]:.3f} after a {real[k][0]:.0f} us wait; the maker T1 median ({np.median(t1s):.0f} us) alone would give about {1 - exp_loss:.3f} or below',
                     'the local Aer noise model attaches relaxation to gates, not to delay(): no fading during a WAIT locally. The dry run injects a labelled synthetic fade instead.')
    t_end = now_iso()
    raw = synthetic_payload(arrays, order, specs)                                   # DRY RUN: round-trip through the raw-payload parser (the real path), synthetic data
    import parse_payload
    arr2 = parse_payload.parse(raw, order, specs, shots, nq)
    if set(arr2) != set(arrays) or not all(np.array_equal(arr2[k], arrays[k]) for k in arrays): raise RuntimeError('dry run: the payload round trip changed the arrays')
    arrays = arr2
    fz_groups = qs['groups']
    meta = {'run': run_no, 'chip': chip, 'box': box, 'synthetic_iq': True,
            'WARNING': 'DRY RUN. I/Q is SYNTHETIC (fabricated from local simulated 0/1). Proves the code path only, not the physics. The chip name is a label only.',
            'shots': shots, 'backend_simulated': 'FakeKingston (local)', 'backend_planning': plan_label, 'qubit_seed': qs['seed'], 'qubit_how': qs['how'], 'order_seed': SEED_ORDER[run_no],
            'synth_seed': SEED_SYNTH + BOXES.index(box), 'synthetic_fade_tau_us_INJECTED': synth_tau_us, 'synthetic_look_mark_survival_INJECTED': synth_mark,
            'groups_of_three': fz_groups, 'all_q': all_q, 'n_chip_qubits': N, 'rep_delay_us': REP_DELAY_S * 1e6, 'pub_order_seeded': order,
            'code_hash': freeze_info(run_no, specs, chip, box, fz_groups if box != 'blank' else None, ({'calibration_timestamp': cal_ts, **clock} if box == 'maker' else None))['combined_sha256'],
            'start_time': t_start, 'end_time': t_end, 'sim_seconds': sim_secs, 'calibration_timestamp': cal_ts, 'maker_clock_source': plan_label,
            'maker_clock_read_at': t_start, 'maker_clock': clock, 'est': est, 'account_seconds_left_at_dry_run': 'NOT READ (no account contact)',
            'sim_mean_bit_per_look': obs, 'simulator_breaks': list(SIM_BREAKS), 'realized_waits_us': {str(w): realize_wait(dt, w)[1] for w in WAITS_US},
            'shot_order_note': 'dry run: synthetic shots are iid, so no carry-over exists to find', 'sampler_options_pinned': pinned,
            'prediction_file': prediction_file, 'prediction_sha256': (sha256_file(prediction_file) if prediction_file else None),
            'end_time_source': 'DRY RUN local stamp (not hardware time)', 'payload_file': f'run{run_no}_payload_raw.json (SYNTHETIC, written by the dry run)',
            'parser_file': PARSER_FILE + ' (OUTSIDE the freeze)', 'parser_sha256': sha256_file(os.path.join(HERE, PARSER_FILE)), 'payload_sha256': hashlib.sha256(raw.encode()).hexdigest()}
    out_dir = out_dir or os.path.join(HERE, 'data', 'dryrun', chip)
    save_results(out_dir, run_no, arrays, meta, ledger, shots, nq)
    with open(payload_path(out_dir, run_no), 'w') as f: f.write(raw)
    print(f'DRY RUN run{run_no} {chip} [{box}] OK: {len(specs)} circuits, {ledger["n_looks_total"]} looks, {nq} qubits ({qs["how"]}), {shots} shots -> {out_dir}')
    print_est(f'run{run_no}', est); print(f'{len(SIM_BREAKS)} simulator break(s):'); [print('  -', b['where']) for b in SIM_BREAKS]
    return out_dir


def list_circuits(run_no, specs):
    T, real = build_all(156, NOMINAL_DT, list(range(9)), specs)
    led = build_ledger(run_no, specs, real); ledger_self_check(led)
    print(f"RUN {run_no}: {led['n_circuits']} circuits, {led['n_looks_total']} looks in all, calibration/test circuits: {led['calibration_or_test_circuits']}")
    print('  waits laid on the 16-dt grid at dt = %.1f ns: ' % (NOMINAL_DT * 1e9) + ', '.join(f'{WAIT_NAMES[w]} {w} -> {realize_wait(NOMINAL_DT, w)[1]:.3f} us' for w in WAITS_US))
    for c in led['circuits']:
        print(f"  {c['key']:<18} {c['n_looks']} look(s): {c['plain']}")
    return led


# ----------------------------------------------------------------------------------------------- FIRE and RECOVER (never called by the builder)
class _BlindService:
    """BLANK submit path. SamplerV2(mode=<IBMBackend>) reads backend.target (= the chip's PROPERTIES, i.e. calibration) and check_faulty() at run time.
    For a BLANK chip that is forbidden, so the primitive is built around a stub service: it forwards the call with the backend given as a NAME; the
    service then fetches only the static configuration and the status (never properties). The circuits are ISA by construction (check_structure)."""
    def __init__(self, svc, name, crn): self._svc, self._name, self._crn = svc, name, crn
    def _run(self, program_id, options, inputs, calibration_id=None):
        options = dict(options); options['backend'] = self._name; options['instance'] = self._crn
        return self._svc._run(program_id=program_id, options=options, inputs=inputs, calibration_id=calibration_id)


def make_sampler(svc, be, blind, crn):
    from qiskit_ibm_runtime import SamplerV2
    sm = SamplerV2(mode=be)
    if blind:
        sm._backend = None; sm._service = _BlindService(svc, be.name if hasattr(be, 'name') else be, crn)
    return sm


def chip_config(be):
    """Static configuration only (n_qubits, dt, rep_delay range, dynamic_reprate flag). Reading these never triggers the calibration fetch."""
    c = be.configuration()
    return {'n_qubits': int(c.n_qubits), 'dt': float(c.dt), 'rep_delay_range': list(getattr(c, 'rep_delay_range', None) or []) or None,
            'dynamic_reprate_enabled': getattr(c, 'dynamic_reprate_enabled', None)}


class _Reads:
    """FIX D / G: every account or chip read made by fire() is written to the read log (account_reads_log.jsonl) AT THE MOMENT it has happened, and to this
    run's `run{N}_fire_reads.json` (which goes into the look ledger as `reads_at_fire`), whether the fire is later refused, fails, or is run without --confirm-submit."""
    def __init__(self, live, run_no, chip, box, out_dir, keep):
        self.live, self.run_no, self.chip, self.box, self.out_dir, self.keep = live, run_no, chip, box, out_dir, keep
        self.mark = len(live.GUARD_LOG); self.entries = []; self.submitted = False
    def flush(self, label, detail=None, force=False):
        new = self.live.GUARD_LOG[self.mark:]
        if not new and not force: return
        self.live.log_read(f'FIRE run{self.run_no} {self.chip} [{self.box}] {label}', dict(detail or {}), touched_a_bit=self.submitted, guard_from=self.mark)
        self.entries += self.live.ledger_reads(new, self.chip); self.mark = len(self.live.GUARD_LOG)
        if self.keep:
            os.makedirs(self.out_dir, exist_ok=True); _atomic_write(fire_reads_path(self.out_dir, self.run_no), self.entries)


def fire(run_no, specs, chip, box, prediction_file, confirm, data_root=None):
    """NEVER CALLED BY THE BUILDER. Guards (no account) -> account (read) -> budget -> [pending file] -> submit ONE job -> JOB ID TO DISK -> wait ONCE ->
    RAW PAYLOAD TO DISK -> parse from the saved payload -> verify against the ledger -> save with the complete marker. No outcome data is read, printed or polled before the job is final.
    MAKER and BLANK both go through the BLIND submit path (no properties, no target, no faulty-qubit check): their groups (and the maker clock) come from the
    freeze file / the blind draw. OURS may read its own properties."""
    import live
    check_chip_box(chip, box)
    fire_dir = data_root or os.path.join(HERE, 'data', 'fire')
    miss = earlier_unlanded(chip, run_no, fire_dir)                                       # FIX H: the fixed run-major order is enforced
    if miss: sys.exit('REFUSED: every earlier job in the fixed order must have landed first. Not landed: ' + ', '.join(f'run {r} on {c}' for c, r in miss) +
                      '.  Order: run 1 (' + ', '.join(chip_assignment()[b] for b in BOXES) + '), then run 2 in that order, then run 3.')
    probs = check_freeze(run_no, specs, chip, box, prediction_file)
    if probs: sys.exit('REFUSED by the freeze/prediction guard:\n  - ' + '\n  - '.join(probs))
    fz = json.load(open(freeze_path(run_no, chip)))
    blind = box in ('maker', 'blank')
    out_dir = os.path.join(fire_dir, chip)
    if os.path.exists(os.path.join(out_dir, f'run{run_no}_meta.json')) or os.path.exists(pending_path(out_dir, run_no)):
        sys.exit(f'REFUSED: run {run_no} on {chip} already has a pending or finished record in {out_dir}; a run is fired once. Lost a result? python recover.py --run {run_no} --chip {chip} --box {box}   (no job id file? add --find, then --use-id ID; payload saved but unparsed? add --reparse)')
    live.install_guard({chip}, blind={chip} if blind else (), allow_submit=bool(confirm))
    rd = _Reads(live, run_no, chip, box, out_dir, keep=bool(confirm))
    try:
        _fire_body(live, rd, run_no, specs, chip, box, prediction_file, confirm, fz, blind, out_dir, fire_dir)
    finally:
        rd.flush('final requests' + (' (job submitted)' if rd.submitted else ' (NO job submitted: refused, failed, or no --confirm-submit)'), {'submitted': rd.submitted}, force=True)


def _fire_body(live, rd, run_no, specs, chip, box, prediction_file, confirm, fz, blind, out_dir, fire_dir):
    crn = open(live.CRN_FILE).read().strip()
    svc, tokname = live.open_service()
    usage = svc.usage()                                              # account read: seconds
    rd.flush('account reads (identity, instance, backend NAMES, usage); no chip read yet')
    this_est0, later0 = jobs_to_come(chip, run_no, fire_dir)
    ok, need, rem, why = budget_guard(usage, this_est0, later0)
    print(f'BUDGET GUARD run{run_no} {chip}: remaining={rem} need={need:.1f}s (= {SAFETY} x per-job estimate of this job {this_est0:.1f}s + {len(later0)} more job(s) {sum(x["est_s"] for x in later0):.1f}s)')
    if not ok: sys.exit(f'BRAKE: {why}. REFUSED.')
    if blind and not confirm:
        print(f'Guards passed. NOT submitted (no --confirm-submit). The {box.upper()} chip {chip} was NOT contacted: its configuration and status are read only at the instant of firing (a read is a look).')
        sys.exit(0)
    be = svc.backend(chip)                                           # static configuration only (for blind chips the guard allows nothing else)
    cfg = chip_config(be)
    rd.flush('chip configuration read (size and timing tick)' + (' at the instant of firing' if blind else ''))
    N, dt = cfg['n_qubits'], cfg['dt']
    if cfg['dynamic_reprate_enabled'] is not True: sys.exit('REFUSED: the chip configuration does not say dynamic_reprate_enabled (rep_delay would be rejected)')
    rr = cfg['rep_delay_range']
    if rr and not (rr[0] <= REP_DELAY_S <= rr[1]): sys.exit(f'REFUSED: rep_delay {REP_DELAY_S} outside the chip range {rr}')
    cal_fire = None
    if box == 'blank':
        qs = blind_groups(N); clock, cal_ts = None, None
        prev = [json.load(open(os.path.join(out_dir, f'run{r}_meta.json')))['groups_of_three'] for r in (1, 2, 3) if os.path.exists(os.path.join(out_dir, f'run{r}_meta.json'))]
        if any(p != qs['groups'] for p in prev): sys.exit('REFUSED: the BLIND groups differ from those an earlier run on this chip used (chip qubit count changed?)')
        clock_src = None
    elif box == 'maker':
        # FIX F: the MAKER chip was read ONCE, at freeze time. Its groups and its clock come from the FREEZE FILE; nothing about its calibration is read now.
        saved = fz['groups']; mc = fz['maker_calibration']
        if fz.get('n_chip_qubits') not in (None, N): sys.exit(f"REFUSED: the chip reports {N} qubits now, the freeze read {fz['n_chip_qubits']}")
        if not set(q for g in saved for q in g) <= set(range(N)): sys.exit('REFUSED: a frozen qubit is outside the chip')
        qs = {'groups': saved, 'all_q': sorted(q for g in saved for q in g), 'seed': fz['draw']['seed'], 'how': fz['draw']['how'] + ' (from the freeze file; the chip was not asked again)'}
        clock = {k: mc.get(k) for k in ('T1_us', 'T2_us', 'readout_error', 'reasons') if k in mc}; cal_ts = mc.get('calibration_timestamp')
        clock_src = f"FREEZE FILE (read once, at freeze time {mc.get('read_at')}); not read at fire time"
    else:
        try: cand = candidates_from_backend(be, strict=True)         # calibration read of OURS, by design; FIX K: a failed faulty lookup REFUSES
        except FaultyLookupFailed as ex: sys.exit(f'REFUSED: {ex}')
        saved = fz['groups']; unusable = [q for g in saved for q in g if q not in cand]
        if unusable: sys.exit(f'REFUSED: saved qubits {unusable} are not in the live qubit list for {chip} now (faulty or gone). A decision is needed.')
        qs = {'groups': saved, 'all_q': sorted(q for g in saved for q in g), 'seed': fz['draw']['seed'], 'how': fz['draw']['how']}
        clock, cal_ts = maker_clock(be, qs['all_q']); cal_fire = cal_ts; clock_src = f'{chip} backend properties (read at fire time)'
        print(f"CALIBRATION TIMESTAMPS for {chip}: at the freeze {fz.get('calibration_timestamp')} | at fire time {cal_ts}")
        rd.flush('chip calibration/properties read (OURS, by design)')
    all_q = qs['all_q']; nq = len(all_q)
    T, real = build_all(N, dt, all_q, specs); check_structure(T, all_q, N)
    if not set(all_q) <= set(range(N)): sys.exit('REFUSED: qubit outside chip')
    ledger = build_ledger(run_no, specs, real); ledger_self_check(ledger); check_ledger_vs_circuits(T, ledger, nq)
    est = estimate(specs, real, SHOTS); print_est(f'run{run_no} {chip} [{box}]', est)
    this_est, later = jobs_to_come(chip, run_no, fire_dir)
    this_est = est['per_job_total_s']; later_sum = sum(x['est_s'] for x in later)
    ok, need, rem, why = budget_guard(usage, this_est, later)
    print(f'BUDGET GUARD (real dt) run{run_no} {chip}: remaining={rem} need={need:.1f}s (= {SAFETY} x per-job estimate of this job {this_est:.1f}s + {len(later)} more job(s) {later_sum:.1f}s); '
          f'the 3.0-s-per-circuit worst case for THIS job is {est["per_pub_worst_s"]:.0f} s')
    if not ok: sys.exit(f'BRAKE: {why}. REFUSED.')
    cap, cparts = exec_cap(rem, est['per_pub_worst_s'], later_sum, this_est)
    if cparts.get('too_small'): sys.exit(f'REFUSED: max_execution_time would be {cap} s, below this job\'s own per-job estimate {this_est:.1f} s ({cparts})')
    pred_hash = sha256_file(prediction_file) if prediction_file else None
    print(f'max_execution_time = {cap} s = min(the code\'s own worst case for this job {cparts["worst_case_s"]:.1f} s [3.0 s x {est["pubs"]} circuits + sequence], remaining {rem} s minus the per-job estimates of the {len(later)} jobs still to come {later_sum:.1f} s = {cparts["remaining_minus_later_s"]} s); '
          f'binding: {cparts["binding"]}; this job\'s per-job estimate {this_est:.1f} s; prediction file sha256 = {pred_hash}')
    if not confirm: sys.exit('Guards passed and circuits built; NOT submitted (no --confirm-submit).')
    order = [specs[i]['key'] for i in np.random.default_rng(SEED_ORDER[run_no]).permutation(len(specs))]
    t_start = now_iso(); os.makedirs(out_dir, exist_ok=True)
    sm = make_sampler(svc, be, blind, crn)
    opts = pin_sampler_options(sm, cap=cap, tags=[f'qtr-{chip}-run{run_no}'])
    print('sampler options pinned (everything else Unset):', opts)
    meta = {'run': run_no, 'chip': chip, 'box': box, 'synthetic_iq': False, 'shots': SHOTS, 'real_fire_backend': chip, 'qubit_seed': qs['seed'], 'qubit_how': qs['how'], 'order_seed': SEED_ORDER[run_no],
            'groups_of_three': qs['groups'], 'all_q': all_q, 'n_chip_qubits': N, 'chip_dt_s': dt, 'rep_delay_us': REP_DELAY_S * 1e6, 'pub_order_seeded': order, 'start_time': t_start,
            'calibration_timestamp': cal_ts, 'calibration_timestamp_at_freeze': fz.get('calibration_timestamp'), 'calibration_timestamp_at_fire': cal_fire,
            'maker_clock_source': (clock_src if clock else None), 'maker_clock_read_at': (fz['maker_calibration'].get('read_at') if box == 'maker' else t_start), 'maker_clock': clock, 'est': est,
            'usage_before': {k: v for k, v in usage.items() if k.startswith('usage')}, 'max_execution_time_s': cap, 'max_execution_time_parts': cparts, 'code_hash': fz['combined_sha256'],
            'sampler_options_pinned': opts, 'blind_submit_path': blind,
            'prediction_file': prediction_file, 'prediction_sha256': pred_hash, 'freeze_frozen_at': fz.get('frozen_at'), 'token_file_used': tokname,
            'maker_prediction_from_freeze': fz.get('maker_calibration') if box == 'maker' else None}
    _atomic_write(pending_path(out_dir, run_no), {'run': run_no, 'chip': chip, 'box': box, 'shots': SHOTS, 'order': order, 'real': real, 'meta': meta, 'written_at': now_iso()})
    if prediction_file:
        import shutil; shutil.copyfile(prediction_file, os.path.join(out_dir, f'run{run_no}_prediction_sealed_copy.json'))
    job = sm.run([T[k] for k in order], shots=SHOTS)                 # for a blind chip the SDK reads its status here (and nothing else): written to the ledger just below
    rd.submitted = True
    jid = record_job_id(out_dir, run_no, job, {'chip': chip, 'box': box, 'submitted_at': now_iso(), 'tag': f'qtr-{chip}-run{run_no}'})   # FIRST thing after submit
    print('submitted; job id saved to', job_path(out_dir, run_no), flush=True)
    rd.flush('requests at the instant of firing (for a blind chip: the status read the SDK makes at submit = "is it up")')
    try:
        meta = finalize_from_job(job, out_dir, run_no, specs)
    except Exception as e:
        _atomic_write(job_path(out_dir, run_no), {'job_id': jid, 'run': run_no, 'chip': chip, 'box': box, 'failed_at': now_iso(), 'error': f'{type(e).__name__}: {str(e)[:500]}',
                                                  'payload_saved': os.path.exists(payload_path(out_dir, run_no)),
                                                  'what_to_do': ('python recover.py --reparse --run %d --chip %s --box %s   (the raw payload IS saved: rebuild the results from it after repairing parse_payload.py; no network)' if os.path.exists(payload_path(out_dir, run_no))
                                                                 else 'python recover.py --run %d --chip %s --box %s   (re-reads the finished job by this id; nothing is re-run)') % (run_no, chip, box)})
        sys.exit(f'job {jid} did not yield results: {type(e).__name__}: {str(e)[:300]}\nThe id is saved' + (' and so is the raw payload (recover.py --reparse).' if os.path.exists(payload_path(out_dir, run_no)) else
                 f'. If it hit max_execution_time ({cap} s) the service cancelled it and returns nothing; recover.py will say so.'))
    try: after = {k: v for k, v in svc.usage().items() if k.startswith('usage')}
    except Exception as e: after = f'unreadable: {e}'
    print('saved (complete marker written last):', out_dir, '| usage after:', after)


def recover(svc, run_no, chip, box, specs, data_root=None):
    """FIX 3: fetch a finished job's results by the SAVED id and write the normal results file. Read-only; submits nothing. `svc` is any object
    with .job(id) (a QiskitRuntimeService, or a fake in tests)."""
    out_dir = os.path.join(data_root or os.path.join(HERE, 'data', 'fire'), chip)
    if os.path.exists(os.path.join(out_dir, f'run{run_no}_meta.json')): sys.exit('this run already has a finished results file; nothing to recover')
    jp = job_path(out_dir, run_no)
    if os.path.exists(payload_path(out_dir, run_no)): sys.exit(f'the raw payload for run {run_no} is already saved in {out_dir}: use  python recover.py --reparse --run {run_no} --chip {chip} --box {box}  (no network)')
    if not os.path.exists(jp) or not os.path.exists(pending_path(out_dir, run_no)): sys.exit(f'no saved job id / pending file in {out_dir}')
    jid = json.load(open(jp))['job_id']
    job = svc.job(jid)
    st = str(job.status())
    print(f'job {jid}: status {st}')
    if st not in ('DONE', 'JobStatus.DONE'): sys.exit(f'job is not DONE ({st}); if the status is ERROR/CANCELLED (e.g. ran longer than max_execution_time) there are no results to fetch')
    meta = finalize_from_job(job, out_dir, run_no, specs)
    print('recovered and saved (complete marker last):', out_dir)
    return meta


def reparse(run_no, chip, box, specs, data_root=None):
    """FIX E: rebuild the results file from the SAVED raw payload with parse_payload.py (a separate file, outside every freeze hash). NO NETWORK, no account.
    An existing results set is moved aside (never deleted); the new meta records the parser's sha256 and the payload's sha256."""
    out_dir = os.path.join(data_root or os.path.join(HERE, 'data', 'fire'), chip)
    for need in (payload_path(out_dir, run_no), payload_meta_path(out_dir, run_no), pending_path(out_dir, run_no)):
        if not os.path.exists(need): sys.exit(f'REFUSED: {os.path.basename(need)} is missing in {out_dir}: nothing to reparse')
    stamp = now_iso().replace(':', '').replace('+', 'p')
    for f in (f'run{run_no}_meta.json', f'run{run_no}_results.npz', f'run{run_no}_look_ledger.json', f'run{run_no}_maker_clock.json'):
        fp = os.path.join(out_dir, f)
        if os.path.exists(fp): os.replace(fp, fp + f'.before_reparse_{stamp}')
    meta = finalize_from_saved_payload(out_dir, run_no, specs)
    print('reparsed from the saved raw payload and saved (complete marker last):', out_dir, '| parser sha256', meta['parser_sha256'][:16])
    return meta


def run_main(run_no, specs_fn, doc):
    ap = argparse.ArgumentParser(description=doc)
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--fire', action='store_true'); ap.add_argument('--confirm-submit', action='store_true')
    ap.add_argument('--chip', default=CHIP_OURS, help='chip name (ibm_kingston, or the written-seed MAKER / BLANK chip)')
    ap.add_argument('--box', choices=BOXES, default='ours')
    ap.add_argument('--prediction-file', default=None, help='OURS only')
    ap.add_argument('--dry-shots', type=int, default=SHOTS)
    ap.add_argument('--synth-tau-us', type=float, default=None); ap.add_argument('--synth-mark', type=float, default=0.95)
    ap.add_argument('--out-dir', default=None)
    ap.add_argument('--print-estimate', action='store_true'); ap.add_argument('--list-circuits', action='store_true')
    a = ap.parse_args(); specs = specs_fn()
    if a.dry_run: dry_run(run_no, specs, a.chip, a.box, a.dry_shots, a.synth_tau_us, a.synth_mark, a.out_dir, a.prediction_file)
    elif a.fire: fire(run_no, specs, a.chip, a.box, a.prediction_file, a.confirm_submit)
    elif a.list_circuits: list_circuits(run_no, specs)
    elif a.print_estimate: print_est(f'run{run_no}', all_estimates(SHOTS)[run_no])
    else: ap.print_help()
