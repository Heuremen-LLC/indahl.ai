#!/usr/bin/env python3
"""live_status.py (12 Nov 2026): writes stan/results/live.json, the public live feed of STAN's training (KV stan_live, served at /iris/lab/stan.json).
Standard library only. Read-only on the pipeline. Numbers and fixed words only, built here from an allow-list:
  stage (fixed words), per-teacher and per-slice labelled counts (line counts), silver counts, the baseline table on gold dev, the laptop scoreboard,
  training and paired-test numbers when they exist, the time, the plan sha256 and its stamp status.
Never a title, abstract, quote, raw model output, path, host or gold label. A final guard refuses to write if any string is not a fixed word,
a model name, a code, a hex digest or a timestamp.   python3 live_status.py [--print]"""
import json, os, re, sys, time

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = S + '/results'; B = os.path.dirname(S)
OUT = R + '/live.json'
STAGES = ('teachers', 'crosstalk', 'silver', 'training', 'paired test', 'kept', 'not kept')
FIXED = set(STAGES) | {'submitted', 'confirmed', 'ABOVE', 'BELOW', 'CANNOT_TELL STRADDLES_EDGE', 'base', 'Qwen3-1.7B', 'Apache-2.0', 'gold dev', 'gold test', 'closed', 'sagar', 'brands', 'quant', 'arm', 'mac', 'CONSISTENT', 'CANNOT_TELL', 'test_hand', 'test_pipeline'}
CODES = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
KEY_RE = re.compile(r'^[A-Za-z0-9_.:\-]{1,60}$'); MODEL_RE = re.compile(r'^[a-z0-9][a-z0-9.:_\-]{0,40}$')
HEX_RE = re.compile(r'^[0-9a-f]{64}$'); TS_RE = re.compile(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')
NUMKEYS = {'n', 'agree', 'rate', 'wilson95', 'majority_class_rate', 'decided_share', 'gold_present', 'pooled', 'mean', 'ci95', 'n_items', 'labelled'}


def jload(p, tries=3):
    for i in range(tries):
        try: return json.load(open(p))
        except FileNotFoundError: return None
        except Exception: time.sleep(0.5)
    return None


def num(o):
    if isinstance(o, bool): return o
    if isinstance(o, (int, float)) or o is None: return o
    if isinstance(o, list): return [num(x) for x in o]
    if isinstance(o, dict): return {k: num(v) for k, v in o.items() if k in NUMKEYS or re.match(r'^F[1-7]$', k) or k in ('per_code', 'base', 'stan', 'paired_stan_minus_base', 'pooled')}
    return None   # strings are dropped here, never copied


def lines(p, by_id=False):
    ids = set(); n = 0
    try:
        with open(p) as f:
            for l in f:
                m = re.search(r'"id": "([0-9a-f]{6,16})"', l[:80])
                if m: ids.add(m.group(1)); n += 1
    except FileNotFoundError: pass
    return ids if by_id else n


def sha_of(name):
    try: return open(S + '/' + name).read().split()[0]
    except Exception: return None


def stamp(name):
    try: b = open(S + '/' + name, 'rb').read()
    except Exception: return None
    return 'confirmed' if b'\x05\x88\x96\x0d\x73\xd7\x19\x01' in b else 'submitted'   # OpenTimestamps Bitcoin block attestation tag


def teachers():
    cfg = (jload(S + '/teachers/config.json') or {}).get('teachers') or {}
    names = sorted(k for k in cfg if MODEL_RE.match(k))
    sl = {1: {x['id'] for x in (jload(S + '/data/pool.json') or [])[:100]}}
    try:
        for fn in sorted(os.listdir(S + '/data/slices')):
            m = re.match(r'slice_(\d+)\.json$', fn); d = jload(S + '/data/slices/' + fn)
            if m and d: sl[int(m.group(1))] = {x['id'] for x in d}
    except FileNotFoundError: pass
    per = {}
    for t in names:
        per[t] = {}
        for r in (1, 2):
            per[t]['round%d' % r] = {'labelled': lines(S + '/teachers/%s_round%d.jsonl' % (t, r))}
    ids = {(t, r): lines(S + '/teachers/%s_round%d.jsonl' % (t, r), True) for t in names for r in (1, 2)}
    slices = [{'slice': k, 'items': len(v), 'labelled_round1': {t: len(v & ids[(t, 1)]) for t in names}, 'labelled_round2': {t: len(v & ids[(t, 2)]) for t in names}} for k, v in sorted(sl.items())]
    return names, per, slices


def baseline():
    d = jload(R + '/baseline_dev.json')
    if not d: return None
    out = {}
    for m, v in d.items():
        if not MODEL_RE.match(m): continue
        pc = v.get('per_code') or {}; tot = sum(pc[c]['n'] for c in CODES if c in pc)
        maj = round(sum(pc[c]['n'] * pc[c]['majority_class_rate'] for c in CODES if c in pc) / tot, 3) if tot else None
        out[m] = {'pooled': num(v.get('pooled')), 'majority_class_rate': maj, 'per_code': {c: num({k: pc[c].get(k) for k in ('n', 'agree', 'rate', 'wilson95', 'majority_class_rate', 'decided_share')}) for c in CODES if c in pc}}
    return out


def bench():
    d = jload(R + '/bench.json')
    if not d: return None
    out = {}
    for m, v in d.items():
        if not MODEL_RE.match(m): continue
        out[m] = {'pooled': num(v.get('pooled')), 'n_items': v.get('n_items'), 'labelled': v.get('labelled'),
                  'per_code': {c: num({k: x.get(k) for k in ('n', 'agree', 'rate', 'wilson95', 'majority_class_rate')}) for c, x in (v.get('per_code') or {}).items() if re.match(r'^F[1-7]$', c)}}
    return out


def ladder():
    """13 Nov 2026: the STAN-E LoRA ladder (Qwen2.5-7B-Instruct 4-bit, MLX). Counts from train_e/results/<model>_<set>.json, the
    paper-clustered reading from train_e/results/clustered_read.json. Numbers and fixed words only."""
    T = S + '/train_e/results'; rows = []
    for m in ['base'] + ['lora_v%d' % i for i in range(1, 30)]:
        r = {}
        for st in ('test_hand', 'test_pipeline'):
            j = jload(T + '/%s_%s.json' % (m, st))
            if j and j.get('summary'):
                q = j['summary']; r[st] = {k: q.get(k) for k in ('pos', 'pos_flag', 'neg', 'neg_flag', 'parse_fail')}
        if r: rows.append({'model': m, **r})
    cr = jload(T + '/clustered_read.json') or {}; cl = []
    for m, sets in (cr.get('models') or {}).items():
        for x in sets:
            cl.append({'model': m, 'set': x['set'], 'papers': x['papers'], 'chunks': x['chunks'],
                       'recall_diff': x['recall']['diff'], 'recall_diff_ci95': x['recall']['diff_ci95_paper'], 'recall_outcome': x['recall']['outcome'],
                       'recall_flips_up': x['pos']['flips_base_miss_to_flag'], 'recall_flips_down': x['pos']['flips_flag_to_miss'],
                       'false_flag_diff': x['false_flag']['diff'], 'false_flag_diff_ci95': x['false_flag']['diff_ci95_paper'], 'false_flag_outcome': x['false_flag']['outcome'],
                       'false_flag_flips_up': x['neg']['flips_base_miss_to_flag'], 'false_flag_flips_down': x['neg']['flips_flag_to_miss']})
    return {'base_model': 'qwen2.5-7b-instruct-4bit', 'rows': rows, 'clustered': cl, 'kept': False} if rows else None


def build():
    names, per, slices = teachers(); ss = jload(R + '/silver_summary.json') or {}; items = ss.get('items')
    run = jload(S + '/runs/stan_v1/run.json'); pt = jload(R + '/paired_test.json'); st = jload(R + '/stan_dev_stratified.json')
    r1 = [per[t]['round1']['labelled'] for t in names]; r2 = [per[t]['round2']['labelled'] for t in names]
    if pt: stage = 'kept' if pt.get('kept') else 'not kept'
    elif os.path.exists(S + '/runs/stan_v1/CHECKPOINT.txt'): stage = 'paired test'
    elif run or os.path.exists(S + '/runs/train.log'): stage = 'training'
    elif r2 and min(r2) > 0 and min(r2) >= min(r1 or [0]) and (ss.get('silver_pairs') or 0) > 0: stage = 'silver'
    elif r2 and max(r2) > 0: stage = 'crosstalk'
    else: stage = 'teachers'
    silver = {k: ss.get(k) for k in ('items', 'silver_pairs', 'train_rows', 'valid_rows', 'review_queue_two_of_three', 'all_differ_or_parse_failed', 'items_all_seven_codes_unanimous')}
    silver['by_via'] = ss.get('silver_by_via'); silver['by_code'] = ss.get('silver_by_code')
    silver['items_not_yet_labelled_by_all_three'] = (ss.get('outcomes') or {}).get('item_not_yet_labelled_by_all_three')
    out = {'updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'stage': stage,
           'teachers': {'names': names, 'labelled': per, 'slices': slices, 'items_in_pool': items},
           'stan_a': {'stage': 'closed', 'cells_passed': 0, 'cells': 12}, 'stan_e': stan_e(), 'ladder': ladder(), 'pipelines': pipelines(),
           'silver': silver, 'baseline_gold_dev': baseline(), 'bench_gold_dev': bench(),
           'training': ({k: run.get(k) for k in ('iters', 'train_rows', 'seconds', 'lr', 'rank')} | {'base': 'Qwen3-1.7B', 'license': 'Apache-2.0'}) if run else None,
           'paired_test': ({'base_conversion': {k: v for k, v in jload(R + '/base_conversion.json').items() if k != 'note'}, 'n_items': pt.get('n_items'), 'base': num(pt.get('base')), 'stan': num(pt.get('stan')), 'paired_stan_minus_base': num(pt.get('paired_stan_minus_base')),
                            'band_reading': pt.get('band_reading'), 'kept': bool(pt.get('kept'))}) if pt else None,
           'stan_dev_by_teacher_agreement': num(st) if st else None,
           'plan': {'sha256': sha_of('PLAN.sha256'), 'stamp': stamp('PLAN.sha256.ots'), 'addendum_1_sha256': sha_of('PLAN_ADDENDUM_1.sha256'), 'addendum_1_stamp': stamp('PLAN_ADDENDUM_1.sha256.ots')}}
    return out


def stan_e():
    lb = jload(S + '/errata/leaderboard.json') or {}; runs = []
    for r in lb.get('board') or []:
        m = str(r.get('run'))
        if not MODEL_RE.match(m): continue
        rc = r.get('recall') or [None, None, [None, None]]; w = rc[2] if len(rc) > 2 and rc[2] else [None, None]
        runs.append({'model': m, 'papers_seen': r.get('papers_seen'), 'papers_flagged': r.get('papers_flagged'), 'hits': r.get('hits'),
                     'verified_positive_papers_seen': r.get('verified_positive_papers_seen'), 'recall_wilson95': [w[0], w[1]], 'parse_fail': r.get('parse_fail')})
    now = []; st = jload(S + '/hot/state.json') or {}
    for mach in ('arm', 'mac'):
        j = st.get(mach)
        if not j: continue
        mdl = str((j.get('env') or {}).get('MODEL', ''))
        if MODEL_RE.match(mdl): now.append({'machine': mach, 'model': mdl})
    return {'verified_positive_papers': lb.get('verified_positive_papers'), 'runs': runs, 'running_now': now}


def lines_any(p):
    try: return sum(1 for l in open(p) if l.strip())
    except FileNotFoundError: return 0


def pipelines():
    out = {}
    for key, d in (('sagar', 'sagar'), ('brands', 'brands'), ('quant', 'quant_desk')):
        st = jload('%s/%s/pipeline/state.json' % (B, d)) or {}; q = jload('%s/%s/index/queue_reachable.json' % (B, d)) or []
        merged = sum(1 for b in (st.get('batches') or {}).values() if b.get('stage') == 'merged')
        _va = '%s/%s/index/verified_auto.jsonl' % (B, d)   # 12 Nov: papers, not rows (same unit as the pages)
        _vp = set()
        try: _vp = {json.loads(l)['arxiv'] for l in open(_va) if l.strip()}
        except Exception: pass
        conf = len(_vp)
        if key == 'sagar':
            try:   # 12 Nov: same filter as the SAGAR pages: two-reader findings only (no F1/F4, no convention-F2, minus the row the second reader overruled), one per paper
                _conv = {('2409.16196', 'F2'), ('2503.09731', 'F2'), ('2410.16565', 'F2'), ('2507.21566', 'F6')}
                _ps = {json.loads(l)['arxiv'] for l in open(B + '/sagar/index/verified.jsonl') if l.strip() and json.loads(l).get('bones') == 'PRESENT'
                       and json.loads(l)['code'][:2] not in ('F1', 'F4') and (json.loads(l)['arxiv'], json.loads(l)['code']) not in _conv}
                conf += len(_ps - _vp)
            except FileNotFoundError: pass
        out[key] = {'batches_merged': merged, 'findings_confirmed': conf, 'queue_left': max(0, len(q) - ((st.get('next') or 1) - 1) * 12)}
    return out


def guard(o, path='$'):
    if isinstance(o, dict):
        for k, v in o.items():
            if not KEY_RE.match(str(k)): raise SystemExit('live_status: REFUSED, key %s failed the guard' % path)
            guard(v, path + '.' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): guard(v, path)
    elif isinstance(o, str):
        if not (o in FIXED or MODEL_RE.match(o) or HEX_RE.match(o) or TS_RE.match(o) or re.match(r'^F[1-7]$', o)): raise SystemExit('live_status: REFUSED, a string failed the guard at ' + path)
    elif not (o is None or isinstance(o, (bool, int, float))): raise SystemExit('live_status: REFUSED, odd type at ' + path)


if __name__ == '__main__':
    o = build(); guard(o)
    if '--print' in sys.argv: print(json.dumps(o, indent=1)[:6000]); raise SystemExit(0)
    tmp = OUT + '.tmp'; json.dump(o, open(tmp, 'w'), indent=1); os.replace(tmp, OUT); print('live_status: stage %s, written' % o['stage'])
