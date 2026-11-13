#!/usr/bin/env python3
"""TRIPLE PASS, seat A (the observer, LAID): index every IBM job fire record on disk (read-only).

Walks the fire records of the 10/1-10/2 runs (qubit_three_runs, qubit_stone_run, qubit_fifth_run),
the 9/24-9/28 IBM re-pull (out/raw_repull/*.meta.json) and the Rigetti/Braket re-pull
(~/bones-forge/standoff/raw_repull/*.json.gz). Writes ONLY into this directory.
Every time printed is the maker's stamp (LAID clock: what the service recorded), never a reading.
"""
import glob, gzip, hashlib, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PX = '/Users/heuremen/bones-forge/parallax'
OUT = os.path.join(PX, 'out')


def jload(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception as e:
        return {'_error': repr(e)}


def ibm_runs():
    rows = []
    for base in ['qubit_three_runs', 'qubit_stone_run', 'qubit_fifth_run']:
        root = os.path.join(OUT, base)
        for chipdir in sorted(glob.glob(os.path.join(root, 'data', 'fire', 'ibm_*'))):
            chip = os.path.basename(chipdir)
            for jobf in sorted(glob.glob(os.path.join(chipdir, 'run*_job.json'))):
                run = os.path.basename(jobf).split('_')[0][3:]
                pre = os.path.join(chipdir, f'run{run}_')
                job = jload(jobf)
                meta = jload(pre + 'meta.json')
                pend = jload(pre + 'pending.json')
                pm = jload(pre + 'payload_meta.json') if os.path.exists(pre + 'payload_meta.json') else {}
                frz = jload(os.path.join(root, f'freeze_{chip}_run{run}.json'))
                jm = (pm or {}).get('job_metrics') or {}
                ts = jm.get('timestamps') or {}
                us = jm.get('usage') or {}
                order = pend.get('order') if isinstance(pend, dict) else None
                real = pend.get('real') if isinstance(pend, dict) else None
                res = pre + 'results.npz'
                rows.append({
                    'base': base, 'chip': chip, 'run': int(run),
                    'job_id': job.get('job_id'), 'submitted_at': job.get('submitted_at'), 'box': job.get('box'),
                    'created_utc': ts.get('created'), 'running_utc': ts.get('running'), 'finished_utc': ts.get('finished'),
                    'qpu_charge_s': us.get('qpu_charge_time_seconds'), 'circ_exec_ns': jm.get('circuits_execution_time_ns'),
                    'payload_sha256': (pm or {}).get('sha256'), 'payload_bytes': (pm or {}).get('bytes'),
                    'payload_saved_at': (pm or {}).get('saved_at'),
                    'shots': meta.get('shots') if isinstance(meta, dict) else None,
                    'n_circuits': len(order) if order else None,
                    'order_seed': meta.get('order_seed') if isinstance(meta, dict) else None,
                    'qubit_how': meta.get('qubit_how') if isinstance(meta, dict) else None,
                    'qubit_seed': meta.get('qubit_seed') if isinstance(meta, dict) else None,
                    'n_qubits_laid': len(meta.get('all_q') or []) if isinstance(meta, dict) else None,
                    'groups': meta.get('groups_of_three') if (isinstance(meta, dict) and len(meta.get('all_q') or []) <= 12) else None,
                    'freeze_combined_sha256': frz.get('combined_sha256'), 'frozen_at': frz.get('frozen_at'),
                    'freeze_read': frz.get('read'), 'freeze_shots': frz.get('shots_per_circuit'),
                    'freeze_seed_blind': frz.get('seed_blind'), 'freeze_ledger_sha256': frz.get('ledger_sha256'),
                    'results_npz': os.path.exists(res),
                    'real_delays_us': real,
                })
    return rows


def ibm_unfired():
    """Freeze files with no job record: frozen, never fired (or pulled)."""
    out = []
    for base in ['qubit_three_runs', 'qubit_stone_run', 'qubit_fifth_run']:
        root = os.path.join(OUT, base)
        for fz in sorted(glob.glob(os.path.join(root, 'freeze_ibm_*_run*.json'))):
            name = os.path.basename(fz)[len('freeze_'):-len('.json')]
            chip, run = name.rsplit('_run', 1)
            if not os.path.exists(os.path.join(root, 'data', 'fire', chip, f'run{run}_job.json')):
                f = jload(fz)
                out.append({'base': base, 'chip': chip, 'run': int(run), 'frozen_at': f.get('frozen_at'),
                            'combined_sha256': f.get('combined_sha256')})
    return out


def repull_ibm():
    rows = []
    for p in sorted(glob.glob(os.path.join(OUT, 'raw_repull', '*.meta.json'))):
        d = jload(p)
        m = d.get('metrics') or {}
        ts = m.get('timestamps') or {}
        us = m.get('usage') or {}
        pubs = d.get('pub_metadata') or {}
        shots = [v.get('shots') for v in pubs.values()] if isinstance(pubs, dict) else []
        rows.append({'job_id': d.get('job_id'), 'backend': d.get('backend'), 'status': d.get('status'),
                     'caller': m.get('caller'), 'created_utc': ts.get('created'), 'finished_utc': ts.get('finished'),
                     'qpu_charge_s': us.get('qpu_charge_time_seconds'), 'n_pubs': len(pubs) if isinstance(pubs, dict) else None,
                     'shots_set': sorted(set(s for s in shots if s is not None)),
                     'npz': os.path.exists(p.replace('.meta.json', '.npz')), 'key_file': d.get('key_file')})
    rows.sort(key=lambda r: r['created_utc'] or '')
    return rows


def repull_braket():
    rows = []
    for p in sorted(glob.glob('/Users/heuremen/bones-forge/standoff/raw_repull/*.json.gz')):
        try:
            with gzip.open(p, 'rt') as f:
                d = json.load(f)
        except Exception as e:
            rows.append({'file': os.path.basename(p), '_error': repr(e)})
            continue
        task = d.get('task') or d.get('task_record') or d
        def g(*ks):
            for k in ks:
                if isinstance(task, dict) and k in task:
                    return task[k]
            return None
        res = d.get('results') or d.get('result') or {}
        meas = None
        if isinstance(res, dict):
            mm = res.get('measurements')
            if isinstance(mm, list):
                meas = (len(mm), len(mm[0]) if mm and isinstance(mm[0], list) else None)
        rows.append({'file': os.path.basename(p), 'arn': g('quantumTaskArn', 'taskArn', 'arn'),
                     'created': g('createdAt', 'created_at'), 'ended': g('endedAt', 'ended_at'),
                     'status': g('status'), 'shots': g('shots'), 'device': g('deviceArn', 'device_arn'),
                     'meas_shape': meas, 'top_keys': sorted(d.keys())[:12] if isinstance(d, dict) else None})
    rows.sort(key=lambda r: str(r.get('created')))
    return rows


def main():
    ibm = ibm_runs()
    unf = ibm_unfired()
    rp = repull_ibm()
    bk = repull_braket()
    json.dump({'ibm_fire_records': ibm, 'ibm_frozen_no_job': unf, 'ibm_repull_meta': rp, 'braket_repull': bk},
              open(os.path.join(HERE, 'index_firings.json'), 'w'), indent=1, default=str)
    L = []
    L.append('IBM FIRE RECORDS (10/1-10/2), maker stamps UTC; LAID clock')
    L.append('base | chip | run | job_id | submitted(local) | created / running / finished (UTC) | qpu s | exec ns | circuits x shots | qubits | freeze combined sha256 (12) | frozen_at')
    for r in sorted(ibm, key=lambda r: (r['created_utc'] or r['submitted_at'] or '')):
        L.append(' | '.join(str(x) for x in [r['base'], r['chip'], r['run'], r['job_id'], r['submitted_at'],
                 f"{r['created_utc']} / {r['running_utc']} / {r['finished_utc']}", r['qpu_charge_s'], r['circ_exec_ns'],
                 f"{r['n_circuits']} x {r['shots']}", r['n_qubits_laid'], (r['freeze_combined_sha256'] or '')[:12],
                 r['frozen_at']]))
    L.append('')
    L.append(f'IBM fire records: {len(ibm)}; with payload metrics: {sum(1 for r in ibm if r["created_utc"])}; qpu s total: {sum(r["qpu_charge_s"] or 0 for r in ibm)}')
    L.append('')
    L.append('FROZEN, NO JOB RECORD (not fired, or pulled):')
    for u in unf:
        L.append(f"  {u['base']} {u['chip']} run{u['run']} frozen {u['frozen_at']} {(u['combined_sha256'] or '')[:12]}")
    L.append('')
    L.append('IBM RE-PULL (9/24-9/28 jobs; out/raw_repull/*.meta.json)')
    for r in rp:
        L.append(f"  {r['created_utc']} {r['backend']} {r['job_id']} {r['status']} {r['caller']} pubs={r['n_pubs']} shots={r['shots_set']} qpu_s={r['qpu_charge_s']} npz={r['npz']}")
    L.append(f'IBM re-pull jobs: {len(rp)}; by backend: {dict(Counter(r["backend"] for r in rp))}')
    days = Counter((r['created_utc'] or '')[:10] for r in rp)
    L.append(f'by UTC day: {dict(sorted(days.items()))}')
    L.append('')
    L.append('BRAKET RE-PULL (standoff/raw_repull/*.json.gz)')
    for r in bk:
        L.append(f"  {r.get('created')} {r.get('status')} shots={r.get('shots')} meas={r.get('meas_shape')} {r.get('arn')}")
    L.append(f'Braket tasks: {len(bk)}')
    open(os.path.join(HERE, 'index_firings.txt'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L[:5]))
    print(f'ibm fire records {len(ibm)}, unfired {len(unf)}, repull {len(rp)}, braket {len(bk)}')


if __name__ == '__main__':
    main()
