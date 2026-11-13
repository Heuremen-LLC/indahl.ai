#!/usr/bin/env python3
"""Tests of daily_table.py, push_tables.py, the worker route and tables.js without IBM. Run: ../../qvenv/bin/python -I tests/test_pipeline.py
FakeKingston and FakeMarrakesh supply the targets (156 qubits, durations, dt). Aer (matrix product state) stands in for the chip, with a turn
planted per target on every readout step the way darkwave_kit.py selftest plants it. Nothing here touches IBM."""
import os, sys, json, shutil, tempfile, subprocess, hashlib, re, datetime as dt
T = os.path.dirname(os.path.abspath(__file__)); H = os.path.dirname(T); sys.path.insert(0, H)
import numpy as np
import daily_table as D, darkwave_kit as DK
from qiskit_ibm_runtime.fake_provider import FakeKingston, FakeMarrakesh
from qiskit_aer import AerSimulator
from qiskit.primitives import BackendSamplerV2
from qiskit import qpy
PY = sys.executable; FAIL = []
def check(name, ok, detail=''):
    print(('ok    ' if ok else 'FAIL  ') + name + (' ' + detail if detail else ''), flush=True)
    if not ok: FAIL.append(name)
class Svc:
    def __init__(self, rem): self.rem = rem
    def usage(self): return {'usage_remaining_seconds': self.rem, 'usage_limit_seconds': 14000}
class Sim:
    """sampler factory; counts the jobs submitted and wraps the Aer-backed BackendSamplerV2 job so it reports an id and metrics like IBM's"""
    def __init__(self): self.jobs = 0; self.shots = []; self.circuits = 0
    def __call__(self, b):
        outer = self; smp = BackendSamplerV2(backend=AerSimulator(method='matrix_product_state'))
        class S:
            def run(self, pubs):
                outer.jobs += 1; outer.circuits = len(pubs); outer.shots = sorted({p[2] for p in pubs}); j = smp.run(pubs)
                class J:
                    def job_id(self): return f'simjob{outer.jobs:04d}'
                    def result(self): return j.result()
                    def status(self): return 'DONE'
                    def metrics(self): return {'usage': {'qpu_charge_time_seconds': 0}, 'timestamps': {}}
                return J()
        return S()
def plant_for(S, seed):
    rng = np.random.default_rng(seed); v = {int(q): float(np.round(rng.uniform(-20, 20), 2)) for q in S}
    for q in list(v)[:6]: v[q] = 0.0
    return v
def write_mirror(d, chip, names):
    os.makedirs(os.path.join(d, chip), exist_ok=True)
    for n in names: open(os.path.join(d, chip, n), 'wb').write(b'x')
tmp = tempfile.mkdtemp(prefix='dwd_test_'); rows = []
mirror = os.path.join(tmp, 'mirror')
for chip, Fake in (('ibm_kingston', FakeKingston), ('ibm_marrakesh', FakeMarrakesh)):
    print('---', chip, flush=True)
    b = Fake(); E, S, _ = D.pack(chip); plant = plant_for(S, 11 if chip == 'ibm_kingston' else 12)
    builder = lambda n, R, Tg, L, N, arm, basis, plant=plant: DK.build(n, R, Tg, L, N, arm, basis, synth=plant)
    write_mirror(mirror, chip, ['2026-11-01T18-39-04-05-00.json.gz', '2026-11-01T19-39-17-05-00.json.gz', '2026-11-01T20-34-25-05-00.json.gz'])
    out = os.path.join(tmp, chip); pub = os.path.join(out, 'public'); os.makedirs(out)
    check(f'{chip}: pack is the study pack', len(E) == 39 and len(S) == 117 and max(E + S) < b.num_qubits, f'E {len(E)} S {len(S)}')
    sim = Sim()
    r = D.run(chip, False, Svc(1800), b, sim, out_root=out, public=pub, builder=builder, records_dir=mirror)
    check(f'{chip}: dry run submits nothing and passes', sim.jobs == 0 and r['code'] == 0 and r['remaining'] == 1800 and not os.listdir(out))
    r = D.run(chip, True, Svc(59), b, sim, out_root=out, public=pub, builder=builder, records_dir=mirror)
    check(f'{chip}: refuses at 59 s left', sim.jobs == 0 and r['code'] == 3 and not os.listdir(out))
    r = D.run(chip, True, Svc(None), b, sim, out_root=out, public=pub, builder=builder, records_dir=mirror)
    check(f'{chip}: refuses when the seconds cannot be read', sim.jobs == 0 and r['code'] == 3)
    # the record is on disk before the job: a sampler that fails after the record was written leaves a PLANNED record
    class Boom:
        def __call__(self, b):
            class S:
                def run(self, pubs):
                    d = [x for x in os.listdir(out) if x.startswith('day_')]; rec = json.load(open(os.path.join(out, d[0], 'job_daily_table.json')))
                    check(f'{chip}: record saved before the job', rec['jobs'][0]['status'] == 'PLANNED' and os.path.exists(os.path.join(out, d[0], 'circuits.qpy')))
                    raise RuntimeError('stop here')
            return S()
    try: D.run(chip, True, Svc(1800), b, Boom(), out_root=out, public=pub, builder=builder, records_dir=mirror)
    except RuntimeError: pass
    shutil.rmtree(out); os.makedirs(out)
    r = D.run(chip, True, Svc(60), b, sim, out_root=out, public=pub, builder=builder, records_dir=mirror)
    check(f'{chip}: fires at exactly 60 s left, one job of 8 circuits at 4,000 shots', r['code'] == 0 and sim.jobs == 1 and sim.circuits == 8 and sim.shots == [4000], f'jobs {sim.jobs} circuits {sim.circuits} shots {sim.shots}')
    day = [x for x in os.listdir(out) if x.startswith('day_')][0]; dd = os.path.join(out, day); files = sorted(os.listdir(dd))
    check(f'{chip}: day folder holds record, raw arrays, circuits, kit table', {'job_daily_table.json', 'raw.npz', 'circuits.qpy', 'record_info.json'} <= set(files) and any(f.startswith('kick_table_') for f in files), str(files))
    rec = json.load(open(os.path.join(dd, 'job_daily_table.json')))
    check(f'{chip}: job record has job id, status DONE, usage, DD and twirling off', rec['jobs'][0]['status'] == 'DONE' and rec['jobs'][0]['job_id'] == 'simjob0001' and 'usage' in rec['jobs'][0] and rec['dd'] == 'off' and rec['twirling'] == 'off')
    raw = np.load(os.path.join(dd, 'raw.npz')); check(f'{chip}: raw arrays for all 8 keys', len(raw.files) == 8 and all(raw[f].shape[0] == 4000 for f in raw.files))
    kp = os.path.join(dd, [f for f in files if f.startswith('kick_table_')][0]); kt = json.load(open(kp))
    # planted turns come back
    err = max(abs(kt['kicks'][str(q)]['deg_per_readout'] - plant[q]) for q in S)
    check(f'{chip}: measured turns match the planted turns on all 117 targets', err < 1.5, f'largest error {err:.3f} deg')
    # the kit table equals what the kit itself makes from the same raw counts: re-run the kit path from the raw arrays
    from_raw = {}
    for f in raw.files:
        k = tuple(int(x) if x.isdigit() else x for x in f.split('|')); a = raw[f]
        bits = np.unpackbits(a, axis=1, bitorder='big')[:, a.shape[1] * 8 - len(S):][:, ::-1]   # BitArray: last bit of the last byte is clbit 0
        from_raw[k] = (bits.sum(axis=0).astype(float), a.shape[0])
    tab2 = DK.analyse(from_raw, S, D.MARGIN)
    check(f'{chip}: raw arrays reproduce the kit table through DK.analyse', all(tab2[q] == kt['kicks'][str(q)] for q in S))
    pj = os.path.join(pub, 'darkwave', 'tables', chip); day_s = kt['measured_utc'][:10]; P = json.load(open(os.path.join(pj, f'{day_s}.json')))
    check(f'{chip}: published JSON kicks equal the kit table kicks', P['kicks'] == kt['kicks'] and P['targets'] == kt['targets'] and P['readout'] == kt['readout'] and P['job_id'] == kt['job_id'] and P['measured_utc'] == kt['measured_utc'])
    per = {q: (v['deg_per_readout'], v['band95'], v['outcome'], v['coherence_kept'], v['coherence_idle']) for q, v in P['kicks'].items()}
    check(f'{chip}: every target carries deg_per_readout, band95, outcome, coherence_kept, coherence_idle', len(per) == 117 and all(len(x) == 5 and x[2] in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') for x in per.values()))
    check(f'{chip}: the .kit.json download is the kit file byte for byte', open(os.path.join(pj, f'{day_s}.kit.json'), 'rb').read() == open(kp, 'rb').read() and P['kit_table_sha256'] == hashlib.sha256(open(kp, 'rb').read()).hexdigest())
    ri = P['calibration_record_in_force']
    check(f'{chip}: record in force is the newest mirror record at or before the run start', ri is not None and ri['stamp_utc'] == '2026-11-02T01:34:25Z', str(ri))
    rows.append((chip, kp, os.path.join(pj, f'{day_s}.kit.json'), P, E, S, b))
    # apply accepts the downloaded table
    circ = DK.build(b.num_qubits, E, S, 570, 4, 'M', 'X'); qin = os.path.join(out, 'in.qpy'); qout = os.path.join(out, 'out.qpy'); qpy.dump([circ], open(qin, 'wb'))
    r = subprocess.run([PY, '-I', os.path.join(DK.__file__ if False else D.KIT_SRC, 'darkwave_kit.py'), 'apply', '--table', os.path.join(pj, f'{day_s}.kit.json'), qin, qout], capture_output=True, text=True)
    added = re.search(r'rz added per circuit: \[(\d+)\]', r.stdout)
    check(f'{chip}: darkwave_kit.py apply --table accepts the downloaded table', r.returncode == 0 and added and int(added.group(1)) == 4 * len(S) and 'WARNING' not in r.stdout, (r.stdout.strip().splitlines() or [r.stderr[-200:]])[-3] if r.stdout else r.stderr[-300:])
    c2 = qpy.load(open(qout, 'rb'))[0]; check(f'{chip}: corrected circuit carries rz(-kick) for the first target', c2.count_ops().get('rz', 0) - circ.count_ops().get('rz', 0) == 4 * len(S))

# record in force on the real stamp rule: 2026-11-01T19-39-17-05-00 is 2026-11-02T00:39:17Z
st = D.mirror_stamps('ibm_kingston', mirror); check('mirror file name -> UTC stamp', D.iso(st[1][0]) == '2026-11-02T00:39:17Z', D.iso(st[1][0]))
t = dt.datetime(2026, 11, 2, 0, 50, tzinfo=dt.timezone.utc)
ri = D.record_info('ibm_kingston', t, t + dt.timedelta(minutes=60), mirror)
check('record in force and the stamp during the run', ri['in_force']['stamp_utc'] == '2026-11-02T00:39:17Z' and ri['stamped_during_run'] == ['2026-11-02T01:34:25Z'] and ri['mirror_newest_stamp_utc'] == '2026-11-02T01:34:25Z', str(ri))
real = D.mirror_stamps('ibm_kingston'); mf = json.load(open(os.path.expanduser('~/bones-forge/qia_runcheck/public/qia/records/ibm_kingston/manifest.json')))['records']
sys.path.insert(0, os.path.expanduser('~/bones-forge/qia_package/src')); import qia_check as qc
rs = {D.iso(x[0]) for x in real}; check('real mirror: every run-check manifest stamp of the last 20 is a file-name stamp', real and all(s_ in rs for s_, _, _ in mf[-20:]), f'{len(real)} records')
rd = os.path.expanduser('~/bones-forge/qia_mirror/records/ibm_kingston')
check('real mirror: file-name stamp equals the stamp inside the record (qia_check.load) for the newest 5 files', all(D.iso(qc.load(os.path.join(rd, n))[1]) == D.iso(t_) for t_, n in real[-5:]))

# publish: latest.json, index.json, push script
chip, kp, kitpub, P, E, S, b = rows[0]
pubroot = os.path.join(tmp, 'allpub')
for chip, kp, kitpub, P, E, S, b in rows:
    D.publish(pubroot, kp, json.load(open(kp)), dict(kit_file_sha256=P['kit_file_sha256']), dict(in_force=P['calibration_record_in_force'], stamped_during_run=P['records_stamped_during_run'], mirror_newest_stamp_utc=P['mirror_newest_stamp_utc']), 0)
L = json.load(open(os.path.join(pubroot, 'darkwave', 'tables', 'latest.json')))
check('latest.json holds both chips', set(L['chips']) == set(D.CHIPS) and all(L['chips'][c]['n_targets'] == 117 and len(L['chips'][c]['readout']) == 39 for c in L['chips']))
# push script: dry run lists, bulk file has the keys and the kit file bytes
ps = subprocess.run([PY, '-I', os.path.join(H, 'push_tables.py'), '--dry-run', '--src', pubroot, '--ledger', os.path.join(tmp, 'led.json'), '--bulk-out', os.path.join(tmp, 'bulk.json')], capture_output=True, text=True)
bulk = json.load(open(os.path.join(tmp, 'bulk.json'))); keys = {x['key']: x['value'] for x in bulk}
want = {'dwt/latest.json'} | {f'dwt/{c}/{n}' for c in D.CHIPS for n in ('index.json', P['date_utc'] + '.json', P['date_utc'] + '.kit.json')}
check('push dry run lists the keys and sends nothing', ps.returncode == 0 and set(keys) == want and not os.path.exists(os.path.join(tmp, 'led.json')), ps.stdout.strip())
for chip, kp, kitpub, P, E, S, b in rows:
    served = keys[f'dwt/{chip}/{P["date_utc"]}.kit.json']; sp = os.path.join(tmp, f'served_{chip}.json'); open(sp, 'w', encoding='utf-8').write(served)
    check(f'{chip}: the value pushed for the download is the kit file', served == open(kp, encoding='utf-8').read())
    q = os.path.join(tmp, f'q_{chip}.qpy'); circ = DK.build(b.num_qubits, E, S, 570, 4, 'M', 'X'); qpy.dump([circ], open(q, 'wb'))
    r = subprocess.run([PY, '-I', os.path.join(D.KIT_SRC, 'darkwave_kit.py'), 'apply', '--table', sp, q, q + '.out'], capture_output=True, text=True)
    check(f'{chip}: apply accepts the table as served from the pushed key', r.returncode == 0 and f'rz added per circuit: [{4 * len(S)}]' in r.stdout)
# worker route and the page script in node
nr = subprocess.run(['node', os.path.join(T, 'node_tests.js'), os.path.join(H, 'worker_tables.patch'), os.path.join(H, 'tables.js'), os.path.join(tmp, 'bulk.json'), os.path.join(pubroot, 'darkwave', 'tables', 'latest.json')], capture_output=True, text=True)
print(nr.stdout.strip(), nr.stderr.strip()[-500:])
check('worker route and tables.js tests (node)', nr.returncode == 0 and 'NODE ALL OK' in nr.stdout)
shutil.rmtree(tmp)
print('ALL PASSED' if not FAIL else 'FAILED: ' + ', '.join(FAIL)); sys.exit(1 if FAIL else 0)
