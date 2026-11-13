#!/usr/bin/env python3
"""daily_table.py CHIP [--fire] -- the Darkwave Correction Kit's daily published table (Heuremen LLC, https://indahl.ai/darkwave/kit).

One IBM job per chip per day: the kit's own 8 measure circuits (darkwave_kit.build, N = 1 and 4, arms D and M, bases X and Y), built and read by
the kit's own build and analyse, unchanged, on the study's readout pack E and untouched qubits S for that chip (committed_kicks_<chip>.json of
the Darkwave clock folder). No dynamical decoupling, no twirling, 4,000 shots, trivial layout, seed 31. The record is saved before the job.
Dry run (no --fire): builds and transpiles everything, runs the same checks as the kit, reads the remaining instance seconds and prints
"... checks PASS ... remaining N" (only the number, never the instance or the token). Nothing is submitted.
--fire: refuses below FLOOR remaining seconds, saves the record, submits one job, saves the raw arrays and the job record with its usage,
writes the table in the kit's own format (darkwave_kit.save_table) and the published JSON under public/darkwave/tables/.
Exit codes: 0 done or dry run passed, 2 IBM-side ERROR or cancel (held, never resubmitted), 3 refused (checks failed or seconds below the floor)."""
import os, sys, json, time, glob, re, hashlib, shutil, datetime as dt, warnings
warnings.filterwarnings('ignore')
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.expanduser('~/bones-forge')
CLOCK = os.path.join(ROOT, 'the_show/runs/2026-10-31-darkwave-clock'); KIT_SRC = os.path.join(ROOT, 'darkwave_kit/src')
RECORDS = os.path.join(ROOT, 'qia_mirror/records'); SWEEP = os.path.join(ROOT, 'arxiv_one_readout/sweep_run')
sys.path.insert(0, KIT_SRC)
import darkwave_kit as DK
CHIPS = ('ibm_kingston', 'ibm_marrakesh'); SHOTS = 4000; SEED = 31; MARGIN = 0.5; FLOOR = 60; EST_SECONDS = 12   # 6 Nov: was 600 (held back 4-5 Nov tables)
SCHEMA = 'darkwave-daily-table/1'
def utcnow(): return dt.datetime.now(dt.timezone.utc)
def iso(t): return t.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def sha_file(p): return DK.sha(p)
def pack(chip, clock_dir=CLOCK):
    T = json.load(open(os.path.join(clock_dir, f'committed_kicks_{chip}.json'), encoding='utf-8'))
    return [int(q) for q in T['E']], [int(q) for q in T['S']], T
def prepare(b, E, S, builder=None):
    """The kit's own measure() preparation: build, transpile (level 1, trivial layout, seed 31), check the layout and that arms D and M take the same time on every target."""
    from qiskit import transpile
    builder = builder or DK.build; n = b.num_qubits
    L_dt = max(int(round(b.target['measure'][(q,)].duration / b.dt)) for q in E)
    tc = {k: transpile(builder(n, E, S, L_dt, *k), b, optimization_level=1, initial_layout=list(range(n)), seed_transpiler=SEED) for k in DK.keys()}
    bad = []
    for k, t in tc.items():
        if t.layout is not None and list(t.layout.final_index_layout()) != list(range(n)): bad.append(('layout moved', k))
    dur = {}
    for N in DK.NS:
        d = {}
        for arm in DK.ARMS:
            sc = transpile(tc[(N, arm, 'X')], b, optimization_level=0, scheduling_method='alap', initial_layout=list(range(n)))
            d[arm] = [sc.qubit_duration(q) for q in S]
        if d['D'] != d['M']: bad.append(('arms differ in time', N))
        dur[N] = d['D'][0]
    return tc, L_dt, bad, dur
_FN = re.compile(r'(\d{4})-(\d\d)-(\d\d)T(\d\d)-(\d\d)-(\d\d)([+-])(\d\d)-(\d\d)')
def mirror_stamps(chip, records_dir=RECORDS):
    """Stamps (UTC) of the calibration records the QIA mirror holds, read from the file names the mirror writes (local time and offset)."""
    out = []
    for p in glob.glob(os.path.join(records_dir, chip, '*.json*')):
        m = _FN.match(os.path.basename(p))
        if not m: continue
        y, mo, d, h, mi, s = (int(x) for x in m.groups()[:6]); off = dt.timedelta(hours=int(m.group(8)), minutes=int(m.group(9))) * (1 if m.group(7) == '+' else -1)
        out.append((dt.datetime(y, mo, d, h, mi, s, tzinfo=dt.timezone(off)).astimezone(dt.timezone.utc), os.path.basename(p)))
    return sorted(set(out))
def parse_ts(x):
    try: return dt.datetime.fromisoformat(str(x).replace('Z', '+00:00')).astimezone(dt.timezone.utc)
    except Exception: return None
def record_info(chip, start, end, records_dir=RECORDS, now=None):
    st = mirror_stamps(chip, records_dir)
    if not st: return dict(in_force=None, stamped_during_run=[], mirror_newest_stamp_utc=None, note='no calibration record held by the mirror')
    before = [x for x in st if x[0] <= start]; during = [iso(t) for t, _ in st if start < t <= end]
    return dict(in_force=dict(stamp_utc=iso(before[-1][0]), file=before[-1][1]) if before else None, stamped_during_run=during,
                mirror_newest_stamp_utc=iso(st[-1][0]), mirror_read_utc=iso(now or utcnow()))
def default_sampler(b):
    from qiskit_ibm_runtime import SamplerV2
    smp = SamplerV2(mode=b)   # no dynamical decoupling and no twirling, as the kit's measure() and the 2 November check
    smp.options.dynamical_decoupling.enable = False; smp.options.twirling.enable_gates = False; smp.options.twirling.enable_measure = False
    return smp
def write_json(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True); tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(o, f, indent=1)
    os.replace(tmp, p)
def publish(public, kit_path, kit_table, rec, info, usage_s):
    """Writes public/darkwave/tables/<chip>/<date>.json (+ .kit.json, the kit-format file byte for byte), index.json and latest.json."""
    chip = kit_table['backend']; day = kit_table['measured_utc'][:10]; base = os.path.join(public, 'darkwave', 'tables'); cdir = os.path.join(base, chip)
    os.makedirs(cdir, exist_ok=True); kit_copy = os.path.join(cdir, f'{day}.kit.json'); shutil.copyfile(kit_path, kit_copy)
    pub = dict(schema=SCHEMA, kit=kit_table['kit'], by=kit_table['by'], site=kit_table['site'], chip=chip, date_utc=day, measured_utc=kit_table['measured_utc'],
               job_id=kit_table['job_id'], shots=kit_table['shots'], readout=kit_table['readout'], targets=kit_table['targets'],
               readout_duration_dt=kit_table['readout_duration_dt'], margin_deg=kit_table['margin_deg'], steps=kit_table['steps'],
               dd='off', twirling='off', kit_file_sha256=rec['kit_file_sha256'], calibration_record_in_force=info['in_force'],
               records_stamped_during_run=info['stamped_during_run'], mirror_newest_stamp_utc=info['mirror_newest_stamp_utc'], mirror_read_utc=info.get('mirror_read_utc'),
               qpu_seconds=usage_s, kit_table_url=f'/darkwave/tables/{chip}/{day}.kit.json', kit_table_sha256=sha_file(kit_path), kicks=kit_table['kicks'])
    write_json(os.path.join(cdir, f'{day}.json'), pub)
    days = sorted(re.match(r'(\d{4}-\d\d-\d\d)\.json$', os.path.basename(p)).group(1) for p in glob.glob(os.path.join(cdir, '*.json')) if re.match(r'\d{4}-\d\d-\d\d\.json$', os.path.basename(p)))
    write_json(os.path.join(cdir, 'index.json'), dict(chip=chip, dates=days))
    return refresh_latest(public)
def refresh_latest(public):
    base = os.path.join(public, 'darkwave', 'tables'); chips = {}
    for chip in CHIPS:
        fs = sorted(p for p in glob.glob(os.path.join(base, chip, '*.json')) if re.match(r'\d{4}-\d\d-\d\d\.json$', os.path.basename(p)))
        if not fs: continue
        d = json.load(open(fs[-1], encoding='utf-8'))
        chips[chip] = {k: d[k] for k in ('date_utc', 'measured_utc', 'job_id', 'calibration_record_in_force', 'records_stamped_during_run', 'mirror_newest_stamp_utc', 'kit_table_url', 'kit_table_sha256')}
        chips[chip].update(table_url=f'/darkwave/tables/{chip}/{d["date_utc"]}.json', readout=d['readout'], n_targets=len(d['targets']), shots=d['shots'])
    p = os.path.join(base, 'latest.json'); write_json(p, dict(schema=SCHEMA, chips=chips)); return p
def run(chip, fire, svc, b, make_sampler=default_sampler, out_root=H, public=None, builder=None, records_dir=RECORDS, shots=SHOTS, floor=FLOOR,
        clock_dir=CLOCK, poll_s=20, tries=400):
    E, S, T = pack(chip, clock_dir); public = public or os.path.join(out_root, 'public')
    tc, L_dt, bad, dur = prepare(b, E, S, builder)
    try: rem = svc.usage().get('usage_remaining_seconds')
    except Exception as ex: rem = None; print('usage read failed:', type(ex).__name__, flush=True)
    print(f'{chip}: circuits {len(tc)}; checks {"PASS" if not bad else "FAIL " + str(bad[:3])}; durations (dt) {dur}; est {EST_SECONDS} s, remaining {rem}', flush=True)
    if not fire: print('dry run: nothing submitted', flush=True); return dict(code=0 if not bad else 3, remaining=rem)
    if bad: print('STOP: checks failed, nothing submitted', flush=True); return dict(code=3)
    if rem is None or rem < floor: print(f'STOP: {rem} s left, floor {floor} s, nothing submitted', flush=True); return dict(code=3, remaining=rem)
    t0 = utcnow(); out = os.path.join(out_root, f'day_{t0:%Y%m%d_%H%M}_{chip}'); os.makedirs(out, exist_ok=True)
    keys = DK.keys(); circs = [tc[k] for k in keys]
    from qiskit import qpy
    with open(os.path.join(out, 'circuits.qpy'), 'wb') as f: qpy.dump(circs, f)
    try: json.dump(b.properties(refresh=True).to_dict(), open(os.path.join(out, 'props_before.json'), 'w'), default=str)
    except Exception as ex: print('properties not saved:', type(ex).__name__, flush=True)
    rec = dict(chip=chip, E=E, S=S, L_dt=L_dt, readout_pack_source_job=T.get('source_job'), shots=shots, seed_transpiler=SEED, dd='off', twirling='off',
               kit_file_sha256=sha_file(os.path.join(KIT_SRC, 'darkwave_kit.py')), keys=[list(map(str, k)) for k in keys], durations_dt=dur,
               remaining_seconds_at_start=rem, floor=floor, planned_utc=iso(t0), jobs=[{'label': 'table', 'status': 'PLANNED'}])
    rp = os.path.join(out, 'job_daily_table.json'); write_json(rp, rec)   # the record, before the job
    job = make_sampler(b).run([(c, None, shots) for c in circs]); sub = iso(utcnow()); jid = job.job_id()
    print(f'SUBMITTED table job {jid} {sub}', flush=True); rec['jobs'][0].update(job_id=jid, submitted_utc=sub, status='SUBMITTED'); write_json(rp, rec)
    res = None
    for _ in range(tries):
        try: res = job.result(); break
        except Exception as ex:
            try: st = str(job.status())
            except Exception: st = 'UNKNOWN'
            print(f'WAIT: {type(ex).__name__}; IBM status {st}', flush=True)
            if 'ERROR' in st or 'CANCEL' in st: rec['jobs'][0]['status'] = 'IBM ' + st; write_json(rp, rec); print('HOLD: not resubmitted', flush=True); return dict(code=2)
            time.sleep(poll_s)
    if res is None: rec['jobs'][0]['status'] = 'NO RESULT'; write_json(rp, rec); print('HOLD: no result, not resubmitted', flush=True); return dict(code=2)
    try: m = job.metrics()
    except Exception: m = {}
    use = m.get('usage') or {}; secs = use.get('qpu_charge_time_seconds') or use.get('quantum_seconds'); ts = m.get('timestamps') or {}
    rec['jobs'][0].update(status='DONE', usage=use, timestamps=ts); write_json(rp, rec)
    arrs = {k: np.asarray(r.data.fin.array) for k, r in zip(keys, res)}
    np.savez_compressed(os.path.join(out, 'raw.npz'), **{'|'.join(map(str, k)): v for k, v in arrs.items()})
    counts = {k: DK.p1_from(r.data.fin.get_counts(), len(S)) for k, r in zip(keys, res)}   # the kit's own path from counts to table
    tab = DK.analyse(counts, S, MARGIN)
    kp = DK.save_table(out, chip, E, S, L_dt, shots, jid, tab, MARGIN); kt = json.load(open(kp, encoding='utf-8'))
    start = parse_ts(ts.get('running')) or parse_ts(sub) or t0; end = parse_ts(ts.get('finished')) or utcnow()
    info = record_info(chip, start, end, records_dir)
    json.dump(info, open(os.path.join(out, 'record_info.json'), 'w'), indent=1)
    publish(public, kp, kt, rec, info, secs)
    print(f'DONE table {chip} usage {secs} s; table {os.path.basename(kp)}; record in force {info["in_force"]}', flush=True)
    return dict(code=0, out=out, kit_table=kp, remaining=rem)
def main(argv):
    if len(argv) < 2 or argv[1] not in CHIPS: sys.exit('usage: daily_table.py ibm_kingston|ibm_marrakesh [--fire]')
    sys.path.insert(0, SWEEP)
    from sweep import service
    s = service(); r = run(argv[1], '--fire' in argv, s, s.backend(argv[1])); sys.exit(r['code'])
if __name__ == '__main__': main(sys.argv)
