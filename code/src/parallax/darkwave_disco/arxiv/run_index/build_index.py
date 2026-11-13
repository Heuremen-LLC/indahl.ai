"""build_index.py -- RUN_INDEX.csv: every quantum job (IBM) and task (Braket) on record since 1 Sep 2026, joined to the local file that holds it.
Sources: ibm_jobs_all_keys.json (all key files), braket_tasks.json (search_quantum_tasks), local run records. Experiment = the frozen run script (fifth-run
harness, by tag), else the folder or log the job ID first appears in. Nothing is dropped: cancelled, failed and queued jobs stay as rows."""
import csv, glob, json, os, re, collections as C
HOME = os.path.expanduser('~/bones-forge'); HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = ('venv', 'run_index', 'for_indahl_ai', '/internal/', 'THIRD_RUNG', '_2026093', 'THE_DISCO', 'THE_LINEUP', 'two_clocks/ibm_jobs', 'raw_repull', '/discards/', 'the_buzz', 'wire_map', 'later_sorts', 'three_holes')
def files(roots, pats, skip=None):
    skip = SKIP if skip is None else skip
    for r in roots:
        for p in pats:
            for f in glob.glob(os.path.join(HOME, r, '**', p), recursive=True):
                if not any(s in f for s in skip): yield f
FREEZE = {}
for f in glob.glob(os.path.join(HOME, 'parallax/out/qubit_fifth_run/freeze_*.json')):
    d = json.load(open(f)); m = re.search(r'freeze_(ibm_\w+?)_run(\d+)\.json', f)
    FREEZE[(m.group(1), int(m.group(2)))] = [x for x in (d['files'] if isinstance(d['files'], list) else d['files'].keys()) if x not in ('common.py', 'live.py')][0]
def home_of(ids, roots, pats, skip=None):
    where = {}
    for f in files(roots, pats, skip):
        try: t = open(f, errors='ignore').read()
        except Exception: continue
        for i in ids:
            if i not in where and i in t: where[i] = os.path.relpath(f, HOME)
    return where
def exp_name(path):
    p = path.split('/')
    if p[0] == 'standoff': return re.sub(r'(_tasks.*|_raw.*|\.json|\.txt|\.log)$', '', p[-1])
    if len(p) > 2 and p[1] == 'out': return p[2]
    return re.sub(r'^run_|\.log$', '', p[-1])
rows = []
ibm = json.load(open(os.path.join(HERE, 'ibm_jobs_all_keys.json')))
where = home_of({j['job_id'] for j in ibm}, ['parallax', 'qubits'], ['*.json', '*.log', '*.txt', '*.md'])
miss = {j['job_id'] for j in ibm} - set(where)
where.update({k: v + ' (raw only)' for k, v in home_of(miss, ['parallax'], ['*.meta.json'], ('venv',)).items()})
for j in sorted(ibm, key=lambda j: j['created']):
    tag = next((t for t in j['tags'] if '-run' in t), ''); m = re.search(r'qtr-(ibm_\w+?)-run(\d+)', tag)
    ex = FREEZE.get((m.group(1), int(m.group(2)))) if m else None
    w = where.get(j['job_id'], '')
    rows.append({'vendor': 'IBM', 'id': j['job_id'], 'chip': j['chip'], 'created': j['created'][:19], 'status': j['status'].replace('JobStatus.', ''),
                 'shots': '', 'experiment': (f'run{m.group(2)} {ex}' if ex else (exp_name(w) if w else 'not on disk')), 'local_record': w})
br = json.load(open(os.path.join(HERE, 'braket_tasks.json')))
uid = lambda a: a.split('/')[-1]
bw = home_of({uid(t['task']) for t in br}, ['standoff', 'parallax'], ['*tasks*.json', '*.log', 'state.json'])
for t in sorted(br, key=lambda t: t['created']):
    w = bw.get(uid(t['task']), '')
    rows.append({'vendor': 'Rigetti (Braket)', 'id': uid(t['task']), 'chip': t['device'], 'created': t['created'][:19], 'status': t['status'], 'shots': t['shots'],
                 'experiment': exp_name(w) if w else 'not on disk', 'local_record': w})
with open(os.path.join(HERE, 'RUN_INDEX.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
print('rows', len(rows))
for v in ('IBM', 'Rigetti (Braket)'):
    rs = [r for r in rows if r['vendor'] == v]
    print(v, len(rs), '| not on disk:', sum(r['experiment'] == 'not on disk' for r in rs), '|', C.Counter(r['status'] for r in rs))
    print('  ', C.Counter((r['created'][:10], r['chip'], r['experiment']) for r in rs).most_common(80))
