#!/Users/heuremen/bones-forge/qvenv/bin/python
"""provenance_check_20261005.py -- three seats per run for the 26 IBM jobs fired on 5 Oct 2026 (Bones, 2026-10-05).

READ-ONLY. Submits nothing. Never passes --fire / --confirm-submit to any script. Never edits any .py file. The only IBM calls are
QiskitRuntimeService(...) [token + resources search], service.job(id), job.inputs, job.metrics(), job.status(); live.install_guard(set(), allow_submit=False)
is installed first, so any request that names a chip (or any submission) is refused and logged. No token is printed.

  python provenance_check_20261005.py                 -> fetch IBM job inputs, rebuild from the on-disk fired scripts, write the table
  python provenance_check_20261005.py --cache-dir D   -> keep/reuse the fetched IBM canonical forms in D (skip re-fetching)
  python provenance_check_20261005.py --build RUN --out F    (child mode: rebuild one run from its fired script, no network)

THE THREE SEATS (no pass/fail word is printed anywhere; each is a reading beside the others):
  1 FREEZE   ruler: sha256 of the file the freeze record NAMES, as it is on disk now, against the hash written in freeze_<chip>_run<N>.json
  2 TIME     ruler: mtime of the fired script (the one whose RUN0/CHIP/READS cover the run), against freeze_frozen_at and the job's own created stamp
  3 CIRCUITS ruler: canonical form per pub (physical qubits touched, ordered gate/delay/measure sequence with durations and classical bits, shots)
             rebuilt from the ON-DISK fired script through the script's own build path (common.build_all with the script's patched build_circuit,
             specs(), SEED_ORDER, SHOTS, the chip's n_qubits/dt/all_q from the run's meta, the wiring from the cached roles file written at fire time)
       (a) against the local meta: pub order (pub_order_seeded), circuit design (meta['circuits']), realized waits (run<N>_pending.json)
       (b) against IBM's stored job inputs (service.job(job_id).inputs, token from meta['token_file_used'])
"""
import sys
sys.dont_write_bytecode = True
import os, re, json, glob, hashlib, difflib, datetime, subprocess, tempfile, argparse, importlib.util

HERE = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run'
OUT_DIR = '/Users/heuremen/bones-forge/parallax/darkwave_disco'
OUT_TXT = os.path.join(OUT_DIR, 'data_provenance_20261005.txt')
FIRE = os.path.join(HERE, 'data', 'fire')
DAY = '2026-10-05'
OTHERS = ('common.py', 'live.py', 'analyze.py')
OPT_KEYS = ['dynamical_decoupling.enable', 'execution.init_qubits', 'execution.meas_type', 'execution.rep_delay', 'twirling.enable_gates', 'twirling.enable_measure']


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def parse_t(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))


def loc(dt):
    return dt.astimezone().strftime('%H:%M:%S')


# ------------------------------------------------------------------------------------------------ canonical form (used on rebuilt AND on IBM circuits)
def _pcanon(op):
    if op.name == 'delay':
        return [round(float(op.params[0]), 9), str(getattr(op, 'unit', 'dt'))]
    out = []
    for p in op.params:
        try: out.append(round(float(p), 12))
        except Exception: out.append(str(p))
    return out


def canon_circuit(qc, shots):
    """{'name','width','cregs','qubits','ops','perq','shots'}. ops = ordered list of runs; a run = [name, params, [[qubit indices], [[creg, idx], ...]], ...]
    (consecutive instructions with the same name and params are folded into one run; the order is kept). perq = per physical qubit, its own ordered sequence."""
    runs, perq, touched = [], {}, set()
    for inst in qc.data:
        op = inst.operation
        qs = [qc.find_bit(q).index for q in inst.qubits]
        cb = []
        for c in inst.clbits:
            b = qc.find_bit(c); r = b.registers[0] if b.registers else (None, b.index)
            cb.append([r[0].name if r[0] is not None else None, r[1]])
        par = _pcanon(op)
        if runs and runs[-1][0] == op.name and runs[-1][1] == par: runs[-1][2].append([qs, cb])
        else: runs.append([op.name, par, [[qs, cb]]])
        for i, q in enumerate(qs):
            touched.add(q); perq.setdefault(q, []).append([op.name, par, (cb[i] if cb else None)])
    return {'name': qc.name, 'width': qc.num_qubits, 'cregs': [[r.name, r.size] for r in qc.cregs], 'qubits': sorted(touched),
            'ops': runs, 'perq': {str(q): perq[q] for q in sorted(perq)}, 'shots': int(shots) if shots is not None else None}


def _j(x):
    return json.dumps(x, sort_keys=True, default=str)


def pub_exact(a, b):
    return all(_j(a[k]) == _j(b[k]) for k in ('name', 'width', 'cregs', 'qubits', 'ops', 'shots'))


def pub_perq(a, b):
    return all(_j(a[k]) == _j(b[k]) for k in ('width', 'cregs', 'qubits', 'perq', 'shots'))


def _run_desc(r):
    nq = len(r[2]); first = r[2][0][0]
    return f"{r[0]}{r[1] if r[1] else ''} x{nq} on q{first}" + (f"..q{r[2][-1][0][-1] if r[2][-1][0] else ''}" if nq > 1 else '')


def describe_diff(a, b, la='rebuilt', lb='other'):
    """how pub a differs from pub b, in plain words (first difference only)."""
    for k in ('shots', 'width', 'cregs', 'name'):
        if _j(a[k]) != _j(b[k]): return f"{k}: {la} {_j(a[k])[:90]} vs {lb} {_j(b[k])[:90]}"
    if a['qubits'] != b['qubits']:
        sa, sb = set(a['qubits']), set(b['qubits'])
        return f"physical qubits touched: {la} {len(sa)} vs {lb} {len(sb)}; only in {la}: {sorted(sa - sb)[:8]}, only in {lb}: {sorted(sb - sa)[:8]}"
    ra, rb = a['ops'], b['ops']
    for i in range(max(len(ra), len(rb))):
        x = ra[i] if i < len(ra) else None; y = rb[i] if i < len(rb) else None
        if _j(x) != _j(y):
            dx = _run_desc(x) if x else '(none)'; dy = _run_desc(y) if y else '(none)'
            extra = ''
            if x and y and x[0] == y[0] and x[1] == y[1]:
                extra = ' (same op, different qubits/classical bits: ' + _j(x[2][0])[:60] + ' vs ' + _j(y[2][0])[:60] + ')'
            return f"op run #{i}: {la} {dx} vs {lb} {dy}{extra}; runs {len(ra)} vs {len(rb)}"
    return 'same op runs; per-qubit or other field differs'


# ------------------------------------------------------------------------------------------------ which script fired which run (RUN0 / CHIP / READS read from the source text)
def script_table():
    tab = []
    for p in sorted(glob.glob(os.path.join(HERE, '*.py'))):
        src = open(p).read()
        m0 = re.search(r"^CHIPS?\s*=\s*\[?\s*'(ibm_\w+)'.*?RUN0\s*=\s*(\d+)", src, re.M)
        if not m0: continue
        mr = re.search(r"READS\s*=\s*(\[[^\]]*\]|list\(range\([^)]*\)\))", src)
        reads = eval(mr.group(1)) if mr else []
        mc = re.search(r"common\.code_files\s*=\s*lambda r:\s*\[([^\]]*)\]", src)
        named = re.findall(r"'([^']+)'", mc.group(1)) if mc else None
        tab.append({'script': os.path.basename(p), 'chip': m0.group(1), 'run0': int(m0.group(2)), 'reads': reads, 'named': named})
    return tab


def fired_script_for(tab, chip, run):
    c = [t for t in tab if t['chip'] == chip and any(t['run0'] + k == run for k in t['reads'])]
    return c


# ------------------------------------------------------------------------------------------------ CHILD: rebuild one run from its on-disk fired script (no network)
def build_one(run, out):
    sys.path.insert(0, HERE)
    import numpy as np
    chip = next(os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(FIRE, '*', f'run{run}_meta.json')))
    meta = json.load(open(os.path.join(FIRE, chip, f'run{run}_meta.json'))); pend = json.load(open(os.path.join(FIRE, chip, f'run{run}_pending.json')))
    cands = fired_script_for(script_table(), chip, run)
    res = {'run': run, 'chip': chip, 'candidates': [c['script'] for c in cands]}
    if len(cands) != 1:
        res['error'] = f'cannot tell the fired script: {len(cands)} scripts cover run {run} on {chip}'; json.dump(res, open(out, 'w')); return
    script = cands[0]['script']; res['script'] = script
    try:
        import common
        spec = importlib.util.spec_from_file_location('fired_script', os.path.join(HERE, script))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        N, dt, all_q = meta['n_chip_qubits'], meta['chip_dt_s'], meta['all_q']
        res['all_q_equals_script_all_bits'] = (mod._all_bits(N)['all_q'] == all_q) if hasattr(mod, '_all_bits') else None
        specs = mod.specs()
        res['wiring'] = 'none needed (every bit, no roles)'
        if hasattr(mod, 'set_roles'):
            fam = 'lookwide' if script.startswith('look_wide') else 'countwide'
            rf = os.path.join(HERE, 'data', 'reads', f'{fam}_roles_{chip}.json'); saved = json.load(open(rf))
            mod.set_roles(N, saved['edges'], 'cached wiring file (provenance check)')
            same = (mod.ROLES['emitters'] == saved['emitters'] and mod.ROLES['far'] == saved['far'] and
                    {str(k): v for k, v in mod.ROLES['witness_of'].items()} == {str(k): v for k, v in saved['witness_of'].items()})
            res['wiring'] = f"cached {os.path.basename(rf)} (written {datetime.datetime.fromtimestamp(os.path.getmtime(rf)).strftime('%m-%d %H:%M:%S')}, n={saved['n']}, {len(saved['edges'])} edges); roles recomputed from its edges {'same as' if same else 'DIFFER from'} the roles stored in it"
        shots = common.SHOTS
        seed = common.SEED_ORDER[run]
        order = [specs[i]['key'] for i in np.random.default_rng(seed).permutation(len(specs))]
        T, real = common.build_all(N, dt, all_q, specs)
        ledger = common.build_ledger(run, specs, real, shots=shots)
        res.update({'seed_script': seed, 'seed_meta': meta['order_seed'], 'shots_script': shots, 'shots_meta': meta['shots'], 'n_specs': len(specs), 'order': order})
        # (a) local meta: order, design, realized waits
        mo = meta['pub_order_seeded']
        res['order_pos_same_as_meta'] = sum(1 for x, y in zip(order, mo) if x == y); res['n_meta_order'] = len(mo)
        res['order_same_as_pending'] = (order == pend['order'])
        res['order_first_diff'] = next(({'pos': i, 'rebuilt': x, 'meta': y} for i, (x, y) in enumerate(zip(order, mo)) if x != y), None)
        mc = meta['circuits']; rc = ledger['circuits']
        res['n_meta_circuits'] = len(mc); res['n_rebuilt_circuits'] = len(rc)
        same_design, first = 0, None
        mby = {c['key']: c for c in mc}
        for c in rc:
            o = mby.get(c['key'])
            if o is not None and _j(o) == _j(c): same_design += 1
            elif first is None:
                if o is None: first = {'key': c['key'], 'what': 'key absent from the local meta'}
                else:
                    f = next((k for k in sorted(set(o) | set(c)) if _j(o.get(k)) != _j(c.get(k))), '?')
                    first = {'key': c['key'], 'what': f"field {f}: rebuilt {_j(c.get(f))[:100]} vs meta {_j(o.get(f))[:100]}"}
        res['design_same'] = same_design; res['design_first_diff'] = first
        preal = pend['real']; rr = {k: list(v) for k, v in real.items()}
        res['real_same_as_pending'] = _j({k: list(v) for k, v in preal.items()}) == _j(rr)
        res['pending_shots'] = pend['shots']
        # canonical rebuilt pubs, in the script's order
        res['pubs'] = [canon_circuit(T[k], shots) for k in order]
        try:
            common.check_ledger_vs_circuits(T, ledger, len(all_q)); res['script_own_ledger_check'] = 'ran without raising'
        except Exception as ex:
            res['script_own_ledger_check'] = f'raised {type(ex).__name__}: {str(ex)[:160]}'
    except Exception as ex:
        import traceback
        res['error'] = f'{type(ex).__name__}: {str(ex)[:300]}'; res['trace'] = traceback.format_exc()[-1200:]
    json.dump(res, open(out, 'w'), default=str)


# ------------------------------------------------------------------------------------------------ PARENT
def runs_of_the_day():
    out = []
    for f in sorted(glob.glob(os.path.join(FIRE, 'ibm_*', 'run*_meta.json'))):
        m = json.load(open(f))
        if m.get('start_time', '')[:10] == DAY:
            out.append((int(m['run']), m['chip']))
    return sorted(out)


def fetch_ibm(svc, jid):
    job = svc.job(jid)
    inp = job.inputs
    pubs = inp['pubs']
    m = job.metrics()
    try: st = str(job.status())
    except Exception as ex: st = f'unreadable: {type(ex).__name__}'
    b = getattr(job, '_backend', None); bn = getattr(b, 'name', None) if b is not None else None
    if callable(bn): bn = bn()
    o = inp.get('options') or {}
    flat = {}
    for g, v in o.items():
        if isinstance(v, dict):
            for k, x in v.items(): flat[f'{g}.{k}'] = x
        else: flat[g] = v
    return {'job_id': jid, 'status': st, 'backend': (str(bn) if bn else None), 'n_pubs': len(pubs), 'pubs': [canon_circuit(p[0], p[2]) for p in pubs],
            'pub_params': [(list(map(float, p[1])) if hasattr(p[1], '__len__') else p[1]) for p in pubs], 'options': flat,
            'timestamps': m.get('timestamps'), 'usage': m.get('usage'), 'support_qiskit': inp.get('support_qiskit'), 'version': inp.get('version')}


def mtime_dt(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).astimezone()


def order_words(items):
    """items = [(label, datetime)]; ties within 1 s are written '='."""
    its = sorted(items, key=lambda x: x[1]); out = [its[0][0]]
    for a, b in zip(its, its[1:]):
        out.append(('=' if abs((b[1] - a[1]).total_seconds()) <= 1.0 else '<')); out.append(b[0])
    return ' '.join(out)


def seat1(run, chip, script, fz, meta):
    files = fz['files']; named = [n for n in files if n not in OTHERS]
    nm = named[0] if len(named) == 1 else ','.join(named)
    now = {n: sha256_file(os.path.join(HERE, n)) for n in files}
    named_same = all(now[n] == files[n] for n in named)
    others_diff = [n for n in OTHERS if n in files and now[n] != files[n]]
    # recompute the combined hash from the CURRENT files (blank box: files, seed_blind, seed_chips, chip, box)
    import importlib
    sys.path.insert(0, HERE)
    body = {'files': now, 'seed_blind': fz.get('seed_blind'), 'seed_chips': 20261061, 'chip': fz['chip'], 'box': fz['box']}
    comb_now = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    fired_sha = sha256_file(os.path.join(HERE, script))
    in_freeze = script in files
    ndiff = None
    if script != nm and nm in files:
        a = open(os.path.join(HERE, script)).read().splitlines(); b = open(os.path.join(HERE, nm)).read().splitlines()
        ndiff = sum(1 for l in difflib.unified_diff(b, a, lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++', '---')) // 1
    return {'named': nm, 'named_record12': files[named[0]][:12], 'named_now12': now[named[0]][:12], 'named_same': named_same, 'others_differ': others_diff,
            'fired_sha12': fired_sha[:12], 'fired_in_freeze': in_freeze, 'fired_is_named': (script == nm), 'line_changes_fired_vs_named': ndiff,
            'combined_now_eq_record': comb_now == fz['combined_sha256'], 'record_eq_meta_code_hash': fz['combined_sha256'] == meta.get('code_hash'),
            'fz_files_sha_n': len(files)}


def seat2(run, chip, script, fz, meta, ibm, named):
    sm = mtime_dt(os.path.join(HERE, script)); nm = mtime_dt(os.path.join(HERE, named)) if named in fz['files'] else None
    fa = parse_t(fz['frozen_at']); fa_meta = meta.get('freeze_frozen_at')
    cr = parse_t(ibm['timestamps']['created']) if ibm and ibm.get('timestamps') else None
    cr_meta = meta.get('job_created_at')
    st = parse_t(meta['start_time'])
    items = [('script_mtime', sm), ('frozen_at', fa), ('meta_start', st)]
    if cr: items.append(('job_created(IBM)', cr))
    return {'script_mtime': sm, 'named_mtime': nm, 'frozen_at': fa, 'frozen_meta_same': (fa_meta == fz['frozen_at']), 'meta_start': st, 'created': cr,
            'created_meta_same': (cr_meta == (ibm['timestamps']['created'] if ibm and ibm.get('timestamps') else None)), 'order': order_words(items),
            'd_mtime_to_frozen': (fa - sm).total_seconds(), 'd_frozen_to_created': ((cr - fa).total_seconds() if cr else None), 'd_mtime_to_created': ((cr - sm).total_seconds() if cr else None)}


def seat3(ch, ibm, meta):
    r = {}
    if 'error' in ch:
        return {'rebuilt': False, 'why': ch['error']}
    pubs = ch['pubs']; n = len(pubs); r['rebuilt'] = True; r['n_rebuilt'] = n
    # (a)
    r['a_order'] = f"{ch['order_pos_same_as_meta']}/{ch['n_meta_order']}"; r['a_order_seed'] = (ch['seed_script'] == ch['seed_meta']); r['a_shots'] = (ch['shots_script'] == ch['shots_meta'] == ch['pending_shots'])
    r['a_design'] = f"{ch['design_same']}/{ch['n_meta_circuits']}"; r['a_real'] = ch['real_same_as_pending']
    r['a_first'] = ch.get('order_first_diff') or ch.get('design_first_diff')
    # (b)
    if not ibm:
        r['b'] = None; return r
    ip = ibm['pubs']; r['n_ibm'] = len(ip)
    pos = sum(1 for a, b in zip(pubs, ip) if pub_exact(a, b)); posq = sum(1 for a, b in zip(pubs, ip) if pub_perq(a, b))
    by = {p['name']: p for p in pubs}
    name = sum(1 for b in ip if b['name'] in by and pub_exact(by[b['name']], b)); nameq = sum(1 for b in ip if b['name'] in by and pub_perq(by[b['name']], b))
    r['b_pos'] = pos; r['b_posq'] = posq; r['b_name'] = name; r['b_nameq'] = nameq
    ibm_names = [p['name'] for p in ip]; r['b_order_vs_meta'] = sum(1 for x, y in zip(ibm_names, meta['pub_order_seeded']) if x == y)
    r['b_order_vs_script'] = sum(1 for x, y in zip(ibm_names, [p['name'] for p in pubs]) if x == y)
    r['b_params_empty'] = all(len(x) == 0 for x in ibm['pub_params'] if isinstance(x, list))
    pin = meta.get('sampler_options_pinned', {}); dif = [k for k in OPT_KEYS if ibm['options'].get(k) != pin.get(k)]
    r['b_opts'] = 'same' if not dif else 'differs: ' + ', '.join(f"{k} IBM {ibm['options'].get(k)!r} meta {pin.get(k)!r}" for k in dif)
    r['b_job_id_same'] = (ibm['job_id'] == meta['job_id'])
    first = None
    for i, (a, b) in enumerate(zip(pubs, ip)):
        if not pub_exact(a, b):
            first = {'pos': i, 'rebuilt_name': a['name'], 'ibm_name': b['name'], 'how': describe_diff(a, b, 'rebuilt', 'IBM'), 'perq_same': pub_perq(a, b)}; break
    if first is None and len(pubs) != len(ip): first = {'pos': min(len(pubs), len(ip)), 'how': f'pub counts differ: rebuilt {len(pubs)} vs IBM {len(ip)}'}
    r['b_first'] = first
    return r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--build', type=int); ap.add_argument('--out'); ap.add_argument('--cache-dir'); ap.add_argument('--no-ibm', action='store_true'); ap.add_argument('--note', default='')
    a = ap.parse_args()
    if a.build: return build_one(a.build, a.out)
    sys.path.insert(0, HERE)
    runs = runs_of_the_day(); tab = script_table(); tmp = tempfile.mkdtemp(prefix='prov_')
    t_begin = datetime.datetime.now().astimezone()
    svc = None; guard_log = []
    if not a.no_ibm:
        import live
        live.install_guard(set(), allow_submit=False)
        svc, tokname = live.open_service()
        guard = live.GUARD_LOG
    # token file named in each meta must be the one used: open_service tries key_3 first (the file the fires used)
    rows = []; details = []; ibm_cache = a.cache_dir
    if ibm_cache: os.makedirs(ibm_cache, exist_ok=True)
    for run, chip in runs:
        meta = json.load(open(os.path.join(FIRE, chip, f'run{run}_meta.json')))
        fz = json.load(open(os.path.join(HERE, f'freeze_{chip}_run{run}.json')))
        cands = fired_script_for(tab, chip, run); script = cands[0]['script'] if len(cands) == 1 else '?'
        out = os.path.join(tmp, f'build_{run}.json')
        subprocess.run([sys.executable, os.path.abspath(__file__), '--build', str(run), '--out', out], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ch = json.load(open(out)) if os.path.exists(out) else {'error': 'child produced nothing'}
        ibm = None; ibm_err = None
        cp = os.path.join(ibm_cache, f'ibm_{run}.json') if ibm_cache else None
        if cp and os.path.exists(cp): ibm = json.load(open(cp))
        elif svc is not None:
            try:
                ibm = fetch_ibm(svc, meta['job_id'])
                if cp: json.dump(ibm, open(cp, 'w'))
            except Exception as ex: ibm_err = f'{type(ex).__name__}: {str(ex)[:200]}'
        s1 = seat1(run, chip, script, fz, meta) if script != '?' else None
        s2 = seat2(run, chip, script, fz, meta, ibm, s1['named'] if s1 else '') if script != '?' else None
        s3 = seat3(ch, ibm, meta)
        rows.append({'run': run, 'chip': chip, 'script': script, 'meta': meta, 'fz': fz, 's1': s1, 's2': s2, 's3': s3, 'ch': ch, 'ibm': ibm, 'ibm_err': ibm_err, 'cands': [c['script'] for c in cands]})
    t_end = datetime.datetime.now().astimezone()
    write_report(rows, tab, t_begin, t_end, (guard if svc is not None else []), (tokname if svc is not None else None), a)


def yn(b, y='same', n='differs'):
    return y if b else n


def write_report(rows, tab, t_begin, t_end, guard, tokname, args):
    L = []
    add = L.append
    add('DATA PROVENANCE, THE 26 IBM JOBS FIRED ON 5 OCTOBER 2026   (Bones; built 2026-10-05; script: provenance_check_20261005.py beside this file)')
    add('Folder read: ~/bones-forge/parallax/out/qubit_fifth_run   (no .py file there was edited; no job submitted; no --fire / --confirm-submit used)')
    add('')
    add('THE THREE SEATS, each with its ruler. No verdict word is printed; "same" / "differs" and counts are readings, side by side.')
    add('  SEAT 1  FREEZE    ruler: sha256 of the file the freeze record NAMES (the third entry of its files{}), as it is on disk now, against the hash written in')
    add('                    freeze_<chip>_run<N>.json. Also printed: whether that named file IS the fired script, the fired script\'s own sha256, how many lines the fired script')
    add('                    differs from the named file by (when they are different files), common.py/live.py/analyze.py against their recorded hashes, and the combined hash')
    add('                    recomputed from the files on disk now against the record and against meta.code_hash.')
    add('  SEAT 2  TIME      ruler: mtime of the fired script against freeze_frozen_at and the job\'s own created stamp (IBM metrics.timestamps.created, UTC shown in local time).')
    add('                    Also the meta start_time. Ties within 1 s are written "=".')
    add('  SEAT 3  CIRCUITS  ruler: canonical form per pub = physical qubits touched + ordered gate/delay/measure/rz/barrier sequence (delay durations in dt, measure -> classical')
    add('                    register+bit) + shot count, rebuilt from the ON-DISK fired script by its own build path (common.build_all with the script\'s patched build_circuit;')
    add('                    specs(), SEED_ORDER[run], SHOTS from the script; n_qubits, dt, all_q from the run\'s meta; wiring for the roles scripts from the cached roles file the fire')
    add('                    wrote). "exact" = ordered sequence identical; "per-qubit" = each qubit\'s own sequence identical (ignores interleave order across qubits).')
    add('        (a) against the LOCAL meta: pub order vs meta.pub_order_seeded, circuit design (meta.circuits: key/start/waits/looks/plain) and realized waits (run<N>_pending.json real).')
    add('        (b) against IBM\'s STORED job inputs (service.job(meta.job_id).inputs, token = meta.token_file_used): pub by position, and by circuit name.')
    add('')
    from collections import Counter as _C
    cc = _C(r['chip'] for r in rows)
    add(f"RUNS: every run on disk whose meta start_time is {DAY}: {len(rows)} jobs ({', '.join(f'{k} {v}' for k, v in sorted(cc.items()))}); runs {', '.join(str(r['run']) for r in rows)}.")
    add('TIME NOTE: frozen_at is written in whole seconds (truncated), script mtime has fractions; a difference under 1 s between them is the same instant. mtime->frozen = frozen_at minus mtime.')
    add('')
    add('FIRED SCRIPT per run is read from each script\'s RUN0 / CHIP / READS (text), and must be the only script covering the run; the job tag (qtr-<chip>-run<N>) carries no script name.')
    add('')
    # ---- table
    hdr = ['RUN', 'CHIP', 'FIRED SCRIPT', 'JOB', 'TOKEN',
           'S1 FREEZE hashed file | its sha now vs record | fired script in freeze? | combined now vs record vs meta',
           'S2 TIME order (script mtime, frozen_at, meta start, job created) | mtime->frozen | frozen->created | mtime->created',
           'S3a LOCAL META order / design / real waits / seed / shots',
           'S3b IBM STORED INPUTS pubs exact(pos) / per-qubit(pos) / exact(by name) / name order vs meta / options']
    add('TABLE  (one row per run; fields separated by " || ")')
    add(' || '.join(hdr)); add('-' * 200)
    for r in rows:
        m, s1, s2, s3 = r['meta'], r['s1'], r['s2'], r['s3']
        tok = m.get('token_file_used')
        if s1 is None: f1 = 'no single fired script'
        else:
            f1 = (f"{s1['named']} | {s1['named_now12']} vs {s1['named_record12']} {yn(s1['named_same'])}"
                  f" | {'fired script IS the named file' if s1['fired_is_named'] else 'fired script NOT hashed (sha ' + s1['fired_sha12'] + ', ' + str(s1['line_changes_fired_vs_named']) + ' changed lines vs named)'}"
                  f" | now/record {yn(s1['combined_now_eq_record'])}, record/meta {yn(s1['record_eq_meta_code_hash'])}"
                  + (f" | files differing from record: {s1['others_differ']}" if s1['others_differ'] else ''))
        if s2 is None: f2 = '-'
        else:
            dfc = f"{s2['d_frozen_to_created']:+.1f}s" if s2['d_frozen_to_created'] is not None else '?'
            dmc = f"{s2['d_mtime_to_created']:+.1f}s" if s2['d_mtime_to_created'] is not None else '?'
            f2 = (f"{s2['order']} || {loc(s2['script_mtime'])} {loc(s2['frozen_at'])} {loc(s2['meta_start'])} {loc(s2['created']) if s2['created'] else '?'}"
                  f" | {s2['d_mtime_to_frozen']:+.1f}s | {dfc} | {dmc}")
        if not s3.get('rebuilt'): f3a = 'NOT REBUILT: ' + s3.get('why', '?'); f3b = 'n/a (no rebuild); IBM pubs: ' + (str(r['ibm']['n_pubs']) if r['ibm'] else 'not read')
        else:
            f3a = f"order {s3['a_order']} / design {s3['a_design']} / realized waits {yn(s3['a_real'])} / seed {yn(s3['a_order_seed'])} / shots {yn(s3['a_shots'])}"
            if r['ibm'] is None: f3b = 'IBM not read' + (f" ({r['ibm_err']})" if r['ibm_err'] else '')
            else:
                n = s3['n_rebuilt']
                f3b = (f"{s3['b_pos']}/{n} / {s3['b_posq']}/{n} / {s3['b_name']}/{n} / IBM name order vs meta {s3['b_order_vs_meta']}/{len(r['meta']['pub_order_seeded'])}"
                       f" / options {s3['b_opts'] if s3['b_opts'] == 'same' else 'DIFFER'}" + (f" / IBM pubs {s3['n_ibm']}" if s3['n_ibm'] != n else ''))
        add(' || '.join([str(r['run']), r['chip'], r['script'], m['job_id'], str(tok), f1, f2, f3a, f3b]))
    add('')
    # ---- seat notes
    add('SEAT 1 NOTES: runs whose freeze names a file that is NOT the fired script')
    for r in rows:
        s1 = r['s1']
        if s1 and not s1['fired_is_named']:
            add(f"  run {r['run']} ({r['chip']}): fired {r['script']} (sha {s1['fired_sha12']}); freeze hashed {s1['named']} ({s1['named_record12']}); {s1['line_changes_fired_vs_named']} changed lines between them")
    add('')
    seen = set()
    add('  the lines that differ, fired script (+) against the file the freeze hashed (-), first 120 characters each, one listing per distinct pair:')
    for r in rows:
        s1 = r['s1']
        if s1 and not s1['fired_is_named'] and (r['script'], s1['named']) not in seen:
            seen.add((r['script'], s1['named']))
            a = open(os.path.join(HERE, r['script'])).read().splitlines(); b = open(os.path.join(HERE, s1['named'])).read().splitlines()
            add(f"    {r['script']} vs {s1['named']}:")
            for l in difflib.unified_diff(b, a, lineterm='', n=0):
                if l[:1] in '+-' and l[:3] not in ('+++', '---'): add('      ' + l[:120])
    add('')
    add('SEAT 2 NOTES: times (local, EDT); sibling file mtime shown where the freeze named a different file')
    for r in rows:
        s2 = r['s2']
        if not s2: continue
        add(f"  run {r['run']}: script mtime {s2['script_mtime'].strftime('%m-%d %H:%M:%S.%f')[:-3]} | frozen_at {s2['frozen_at'].strftime('%H:%M:%S')}"
            f" (freeze file and meta {yn(s2['frozen_meta_same'])}) | meta start {s2['meta_start'].strftime('%H:%M:%S')} | job created {s2['created'].astimezone().strftime('%H:%M:%S') if s2['created'] else '?'}"
            f" (meta job_created_at {yn(s2['created_meta_same'])}); frozen->created {s2['d_frozen_to_created']:+.1f}s"
            + (f" | named file mtime {s2['named_mtime'].strftime('%m-%d %H:%M:%S')}" if s2['named_mtime'] and r['s1'] and not r['s1']['fired_is_named'] else ''))
    add('')
    add('SEAT 3 NOTES: wiring and own-checks per run')
    for r in rows:
        ch = r['ch']
        if 'error' in ch: add(f"  run {r['run']}: could not rebuild. {ch['error']}"); continue
        add(f"  run {r['run']}: {ch['script']} | all_q (meta) equals script _all_bits: {ch.get('all_q_equals_script_all_bits')} | wiring: {ch['wiring']} | script's own ledger check {ch['script_own_ledger_check']}"
            f" | script order == pending order: {ch['order_same_as_pending']}")
    add('')
    # ---- anything that differs, in plain words
    add('WHERE A SEAT DISAGREES (plain words; nothing summarized away)')
    any_ = False
    for r in rows:
        s1, s2, s3, ch, ibm = r['s1'], r['s2'], r['s3'], r['ch'], r['ibm']
        notes = []
        if s1 is None: notes.append(f"seat 1/2: cannot tell the fired script; candidates {r['cands']}")
        else:
            if not s1['fired_is_named']: notes.append(f"seat 1: the freeze hashed {s1['named']}, but the fired script is {r['script']}; the freeze record holds NO hash of the fired file (fired sha {s1['fired_sha12']}; {s1['line_changes_fired_vs_named']} changed lines against the hashed file)")
            if not s1['named_same']: notes.append(f"seat 1: the hashed file {s1['named']} on disk now ({s1['named_now12']}) is not what the freeze recorded ({s1['named_record12']})")
            if s1['others_differ']: notes.append(f"seat 1: {s1['others_differ']} on disk now differ from their recorded hashes")
            if not s1['combined_now_eq_record']: notes.append('seat 1: combined hash recomputed from the files now differs from the freeze record')
            if not s1['record_eq_meta_code_hash']: notes.append('seat 1: freeze combined hash differs from meta.code_hash')
        if s2:
            if s2['d_mtime_to_frozen'] < -1: notes.append(f"seat 2: fired script mtime is {-s2['d_mtime_to_frozen']:.1f}s AFTER frozen_at ({loc(s2['script_mtime'])} vs {loc(s2['frozen_at'])})")
            if s2['d_mtime_to_created'] is not None and s2['d_mtime_to_created'] < -1: notes.append(f"seat 2: fired script mtime is {-s2['d_mtime_to_created']:.1f}s AFTER the job was created ({loc(s2['script_mtime'])} vs {loc(s2['created'])}): the file on disk was written after the job fired")
            if s2['d_frozen_to_created'] is not None and s2['d_frozen_to_created'] < 0: notes.append('seat 2: frozen_at is after the job created stamp')
            if not s2['frozen_meta_same']: notes.append('seat 2: meta.freeze_frozen_at differs from the freeze file frozen_at')
            if not s2['created_meta_same']: notes.append('seat 2: IBM created stamp differs from meta.job_created_at')
        if not s3.get('rebuilt'): notes.append('seat 3: not rebuilt: ' + s3.get('why', '?'))
        else:
            n = s3['n_rebuilt']
            if s3['a_order'].split('/')[0] != s3['a_order'].split('/')[1]: notes.append(f"seat 3a: pub order differs from meta at first position {ch['order_first_diff']}")
            if s3['a_design'].split('/')[0] != s3['a_design'].split('/')[1]: notes.append(f"seat 3a: circuit design differs from meta: first {ch['design_first_diff']}")
            if not s3['a_real']: notes.append('seat 3a: realized waits differ from run pending file')
            if not (s3['a_order_seed'] and s3['a_shots']): notes.append(f"seat 3a: seed/shots differ (script seed {ch['seed_script']} meta {ch['seed_meta']}; shots script {ch['shots_script']} meta {ch['shots_meta']} pending {ch['pending_shots']})")
            if ibm is not None:
                if s3['n_ibm'] != n or s3['b_pos'] != n: notes.append(f"seat 3b: {s3['b_pos']}/{n} pubs exact by position ({s3['b_posq']} per-qubit; {s3['b_name']} by name); first difference: {s3['b_first']}")
                if s3['b_opts'] != 'same': notes.append('seat 3b: sampler options ' + s3['b_opts'])
                if not s3['b_job_id_same']: notes.append('seat 3b: IBM job id differs from meta job id')
                if s3['b_order_vs_meta'] != len(r['meta']['pub_order_seeded']): notes.append(f"seat 3b: IBM pub name order equals meta order at {s3['b_order_vs_meta']}/{len(r['meta']['pub_order_seeded'])} positions")
            else: notes.append('seat 3b: IBM inputs not read: ' + str(r['ibm_err']))
        if notes:
            any_ = True; add(f"  run {r['run']} ({r['chip']}, {r['script']}):")
            for x in notes: add('     - ' + x)
    if not any_: add('  (none)')
    add('')
    # ---- the ruler checked against itself
    add('RULER CHECK (seat 3 can see a difference: controls run on the same canonical form, from the data already read; nothing new fetched)')
    byrun = {r['run']: r for r in rows}
    def cnt(A, B):
        return sum(1 for x, y in zip(A, B) if pub_exact(x, y)), sum(1 for x, y in zip(A, B) if pub_perq(x, y))
    try:
        A = byrun[471]['ch']['pubs']; B = byrun[472]['ibm']['pubs']
        e, q = cnt(A, B); bn = {p['name']: p for p in A}; nm = sum(1 for b in B if b['name'] in bn and pub_exact(bn[b['name']], b))
        add(f"  control 1: run 471 rebuilt against IBM's run 472 inputs (same 50 circuits, different seeded order): exact by position {e}/{len(B)}, per-qubit by position {q}/{len(B)}, exact by name {nm}/{len(B)}")
        A = byrun[541]['ch']['pubs']; B = byrun[551]['ibm']['pubs']
        e, q = cnt(A, B); add(f"  control 2: run 541 rebuilt against IBM's run 551 inputs (different design, same chip): exact by position {e}/{min(len(A), len(B))} ({len(A)} vs {len(B)} pubs)")
        import copy
        A = copy.deepcopy(byrun[471]['ch']['pubs']); B = byrun[471]['ibm']['pubs']
        k = next(i for i, p in enumerate(A) if any(o[0] == 'delay' for o in p['ops']))
        d = next(o for o in A[k]['ops'] if o[0] == 'delay'); d[1][0] += 16
        for q, seq in A[k]['perq'].items():
            nd = next((o for o in seq if o[0] == 'delay'), None)
            if nd: nd[1][0] += 16
        e, q = cnt(A, B); add(f"  control 3: run 471 rebuilt with ONE delay lengthened by 16 dt in pub {k} ('{A[k]['name']}'): exact {e}/{len(B)}, per-qubit {q}/{len(B)}; read as: {describe_diff(A[k], B[k], 'altered', 'IBM')}")
        A = copy.deepcopy(byrun[471]['ch']['pubs']); k = 3
        A[k]['ops'][-1][2].pop(); A[k]['perq'][str(max(int(x) for x in A[k]['perq']))].pop()
        e, q = cnt(A, B); add(f"  control 4: run 471 rebuilt with ONE measure removed in pub {k} ('{A[k]['name']}'): exact {e}/{len(B)}, per-qubit {q}/{len(B)}; read as: {describe_diff(A[k], B[k], 'altered', 'IBM')}")
    except Exception as ex:
        add(f"  controls could not run: {type(ex).__name__}: {str(ex)[:160]}")
    add('')
    # ---- our looks (we are hats too)
    add('OUR LOOKS (the observer, this script):')
    add(f"  run {t_begin.strftime('%Y-%m-%d %H:%M:%S %Z')} to {t_end.strftime('%H:%M:%S')}; IBM jobs read: {sum(1 for r in rows if r['ibm'])} of {len(rows)} (job inputs + metrics + status); token file used by open_service: {tokname}"
        f" (meta.token_file_used = {sorted({r['meta'].get('token_file_used') for r in rows})}); no token printed; no chip configuration/calibration read.")
    if args.cache_dir: add(f"  NOTE: --cache-dir {args.cache_dir} was given: IBM canonical forms may have been reused from an earlier fetch rather than fetched in this run.")
    if args.note: add('  ' + args.note)
    if guard:
        refused = [g for g in guard if g.get('REFUSED')]
        from collections import Counter
        kinds = Counter((g['method'], re.sub(r'[0-9a-f-]{20,}|db[0-9a-z]{18}', '<id>', g['path'])) for g in guard if not g.get('REFUSED'))
        add(f"  guard installed (no chip allowed, no submission allowed). Requests that went out: {sum(kinds.values())}; refused by the guard: {len(refused)} (each a chip-configuration fetch the SDK attempts when it builds a backend object for a retrieved job; refused before leaving the machine).")
        for (me, pa), c in sorted(kinds.items()): add(f"     {c:4d} x {me} {pa}")
    add('')
    open(OUT_TXT, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
