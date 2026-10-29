#!/usr/bin/env python3
"""hflicense_tick.py: HFLICENSE rider per PLAN.md. Top 500 Hugging Face models and datasets by downloads: the license tag a repository states against the license file it carries.
Detaches into the background. DISAGREE rows are listed only after they are in data/hand_checked.json (id -> reason). Publishes KV hflicense_live. HFLICENSE_SUMMARY_ONLY=1 rebuilds the summary from stored data."""
import os, sys, re, json, time, collections as C, subprocess, fcntl, urllib.request, urllib.error
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
if not os.environ.get('HF_FORKED'):
    subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__)], env=dict(os.environ, HF_FORKED='1'), stdout=open('data/last_run.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True); print('hflicense: started in the background'); sys.exit(0)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('hflicense: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('hflicense: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-hflicense/0.1 (+https://indahl.ai/hflicense)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); SUMMARY_ONLY = bool(os.environ.get('HFLICENSE_SUMMARY_ONLY'))
def fam_tag(t):
    t = (t or '').lower().strip()
    if not t or t in ('other', 'unknown', 'none') or re.search(r'openrail|llama|gemma|bigscience|creativeml|falcon|deepseek|qwen|license|agreement', t): return 'OTHER'
    if t.startswith('cc0'): return 'CC0'
    if t.startswith('cc-by'): return 'CC-BY' + ('-NC' if '-nc' in t else '') + ('-SA' if '-sa' in t else '') + ('-ND' if '-nd' in t else '')
    if t.startswith('agpl'): return 'AGPL'
    if t.startswith('lgpl'): return 'LGPL'
    if t.startswith('gpl'): return 'GPL-3.0' if '3' in t else ('GPL-2.0' if '2' in t else 'GPL')
    if t.startswith('apache'): return 'Apache-2.0'
    if t.startswith('bsd') or t == '0bsd': return 'BSD'
    if t == 'mit': return 'MIT'
    if t == 'isc': return 'ISC'
    if t.startswith('mpl'): return 'MPL-2.0'
    if t == 'unlicense': return 'Unlicense'
    return 'OTHER'
def fam_text(txt):
    t = re.sub(r'\s+', ' ', txt.lower())
    hd6 = t[:600]                                         # addendum 2: the CC family is read from the title region; the legal text's trailer mentions CC0
    if re.match(r'\s*(attribution|cc0|creative commons)', hd6) or 'creative commons' in hd6 or re.search(r'attribution[\w\- ]*\s\d\.\d|\bcc by\b|\bcc-by\b', hd6):      # addendum 4
        if 'cc0' in hd6 or ('zero' in hd6 and 'universal' in hd6): return 'CC0'
        if 'attribution' in hd6:
            u = hd6.replace('-', '').replace(' ', ''); return 'CC-BY' + ('-NC' if 'noncommercial' in u else '') + ('-SA' if 'sharealike' in u else '') + ('-ND' if 'noderivatives' in u else '')
    if 'apache license' in t and 'version 2.0' in t: return 'Apache-2.0'
    if 'mozilla public license' in t: return 'MPL-2.0'
    hd = t[:400]                                          # addendum 1: the GNU licenses are read from their title, the GPL-3.0 body mentions the Affero license
    if 'gnu affero' in hd: return 'AGPL'
    if 'gnu lesser general public' in hd: return 'LGPL'
    if 'gnu general public license' in hd: return 'GPL-3.0' if 'version 3' in hd else ('GPL-2.0' if 'version 2' in hd else 'GPL')
    if 'permission is hereby granted, free of charge' in t: return 'MIT'
    if 'redistribution and use in source and binary forms' in t: return 'BSD'
    if 'permission to use, copy, modify, and/or distribute this software for any purpose with or without fee' in t: return 'ISC'
    if 'this is free and unencumbered software' in t: return 'Unlicense'
    return 'OTHER'
def compare(s, f):
    if s == 'OTHER' or f == 'OTHER' or not s or not f: return 'NOT_COMPARABLE'
    return 'AGREE' if (s == f or (s == 'GPL' and f in ('GPL-2.0', 'GPL-3.0')) or (f == 'GPL' and s in ('GPL-2.0', 'GPL-3.0'))) else 'DISAGREE'
def get(u, raw=False, n=3):
    for a in range(n):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60); b = r.read(30000 if raw else None)
            return b.decode('utf8', 'replace') if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404): return None
            time.sleep(2 * (a + 1))
        except Exception: time.sleep(2 * (a + 1))
# gate: planted pairs, planted texts, live controls
PAIRS = [('MIT', 'MIT', 'AGREE'), ('Apache-2.0', 'Apache-2.0', 'AGREE'), ('BSD', 'BSD', 'AGREE'), ('MIT', 'Apache-2.0', 'DISAGREE'), ('CC-BY', 'CC-BY-NC', 'DISAGREE'), ('OTHER', 'MIT', 'NOT_COMPARABLE'), ('GPL', 'GPL-3.0', 'AGREE'), ('GPL-2.0', 'GPL-3.0', 'DISAGREE')]
gate_pairs = all(compare(a, b) == w for a, b, w in PAIRS) and all(fam_tag(t) == f for t, f in (('mit', 'MIT'), ('apache-2.0', 'Apache-2.0'), ('bsd-3-clause', 'BSD'), ('cc-by-4.0', 'CC-BY'), ('cc-by-nc-sa-4.0', 'CC-BY-NC-SA'), ('openrail', 'OTHER'), ('llama3', 'OTHER'), ('gpl-3.0', 'GPL-3.0'), ('cc0-1.0', 'CC0')))
gate_texts = True
if not SUMMARY_ONLY:
    for spdx, want in (('MIT', 'MIT'), ('Apache-2.0', 'Apache-2.0'), ('BSD-3-Clause', 'BSD'), ('CC-BY-4.0', 'CC-BY'), ('CC-BY-NC-4.0', 'CC-BY-NC'), ('GPL-3.0-only', 'GPL-3.0')):
        t = get('https://raw.githubusercontent.com/spdx/license-list-data/main/text/%s.txt' % spdx, raw=True); gate_texts &= bool(t) and fam_text(t) == want
    gate_texts &= fam_text('Our very own custom terms of use apply to this model.') == 'OTHER'
    for spdx, want in (('CC-BY-NC-SA-4.0', 'CC-BY-NC-SA'), ('CC0-1.0', 'CC0'), ('CC-BY-SA-4.0', 'CC-BY-SA')):
        t = get('https://raw.githubusercontent.com/spdx/license-list-data/main/text/%s.txt' % spdx, raw=True); gate_texts &= bool(t) and fam_text(t) == want
    cc = get('https://raw.githubusercontent.com/spdx/license-list-data/main/text/CC-BY-4.0.txt', raw=True) or ''
    gate_texts &= fam_text(cc + '\n\nThe text of the Creative Commons public licenses is dedicated to the public domain under the CC0 Public Domain Dedication.') == 'CC-BY'
    gate_texts &= fam_text('FSD50K as a whole is released under license: Attribution 4.0 International (CC BY 4.0). You can find a human-readable summary of the license at https://creativecommons.org/licenses/by/4.0/') == 'CC-BY'
    gate_texts &= fam_text('Model license. The model weights are licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0). Terms follow.') == 'CC-BY-NC'
def repo_fam(kind, rid, files):
    def lf_ok(f):          # addendum 3: LICENSE, LICENCE, COPYING with an optional -suffix; the last extension must be none, md, txt, rst or a version number
        if not re.match(r'^(license|licence|copying)([-_.][\w.-]*)?$', f, re.I): return False
        tail = f.rsplit('.', 1)[1].lower() if '.' in f else ''
        return tail in ('', 'md', 'txt', 'rst') or tail.isdigit() or ('.' not in f)
    lf = next((f for f in files if lf_ok(f)), None)
    if lf is None: return None, None, 'no license file in the repository root'
    t = get('https://huggingface.co/%s%s/resolve/main/%s' % ('datasets/' if kind == 'datasets' else '', rid, lf), raw=True)
    if t is None: return lf, None, 'license file not readable'
    return lf, fam_text(t), None
store = json.load(open('data/repos.json')) if os.path.exists('data/repos.json') else {}
now = time.time(); live_ok = True
if not SUMMARY_ONLY:
    for rid, kind in (('microsoft/phi-2', 'models'), ('Qwen/Qwen2.5-7B-Instruct', 'models')):
        m = get('https://huggingface.co/api/%s/%s' % (kind, rid)); files = [s['rfilename'] for s in (m or {}).get('siblings', []) if '/' not in s['rfilename']]; tag = next((t.split(':', 1)[1] for t in (m or {}).get('tags', []) if t.startswith('license:')), None)
        lf, ff, why = repo_fam(kind, rid, files); live_ok &= bool(m) and compare(fam_tag(tag), ff) == 'AGREE'
gate = bool(gate_pairs and gate_texts and live_ok) if not SUMMARY_ONLY else bool(gate_pairs and json.load(open('summary_hflicense.json')).get('gate') == 'passed'); print('hflicense: gate', 'passed' if gate else 'FAILED', gate_pairs, gate_texts, live_ok, flush=True)
if gate and not SUMMARY_ONLY and os.environ.get('HFLICENSE_RECHECK'):
    n_fix = 0
    for key, rec in list(store.items()):
        if rec.get('why') != 'no license file in the repository root': continue
        full = get('https://huggingface.co/api/%s/%s' % (rec['kind'], rec['id'])); time.sleep(0.4)
        if full is None: rec.update(cls='NOT_COMPARABLE', why='file list could not be read'); n_fix += 1; continue
        files = [x['rfilename'] for x in (full.get('siblings') or []) if '/' not in x['rfilename']]
        if files != [] and any(re.match(r'^(license|licence|copying)', f, re.I) for f in files):
            lf, ff, why = repo_fam(rec['kind'], rec['id'], files); rec.update(file=lf, file_family=ff, why=why, cls='NOT_COMPARABLE' if (why or rec.get('tag_family') == 'OTHER' or ff == 'OTHER') else compare(rec['tag_family'], ff)); n_fix += 1
    json.dump(store, open('data/repos.json.tmp', 'w')); os.replace('data/repos.json.tmp', 'data/repos.json'); print('hflicense: recheck changed', n_fix, 'rows', flush=True)
if gate and not SUMMARY_ONLY:
    for kind in ('models', 'datasets'):
        lst = get('https://huggingface.co/api/%s?sort=downloads&direction=-1&limit=500&full=true' % kind) or []
        for m in lst:
            rid = m['id']; key = kind + '|' + rid
            if key in store and now - store[key]['read'] < 30 * 86400: continue
            sib = m.get('siblings') or []
            if not sib and m.get('tags') and any(t.startswith('license:') for t in m['tags']) or (kind == 'datasets' and not sib):
                full = get('https://huggingface.co/api/%s/%s' % (kind, rid)); time.sleep(0.4); sib = (full or {}).get('siblings') or []; list_failed = full is None   # 29 Oct (audit): a failed call is not an empty repository
            list_failed = locals().get('list_failed', False); files = [s['rfilename'] for s in sib if '/' not in s['rfilename']]; tag = next((t.split(':', 1)[1] for t in m.get('tags', []) if t.startswith('license:')), None) or next((('' + (m.get('cardData') or {}).get('license')) for _ in [0] if isinstance((m.get('cardData') or {}).get('license'), str)), None)
            rec = dict(read=now, kind=kind, id=rid, tag=tag, rank=lst.index(m) + 1)
            if not tag: rec.update(cls='NOT_COMPARABLE', why='no stated license tag')
            elif list_failed: rec.update(cls='NOT_COMPARABLE', why='file list could not be read')
            else:
                lf, ff, why = repo_fam(kind, rid, files); time.sleep(0.4); rec.update(file=lf, file_family=ff, tag_family=fam_tag(tag), why=why)
                rec['cls'] = 'NOT_COMPARABLE' if (why or fam_tag(tag) == 'OTHER' or ff == 'OTHER') else compare(fam_tag(tag), ff)
                if rec['cls'] == 'NOT_COMPARABLE' and not why: rec['why'] = 'either side is a custom or named license'
            store[key] = rec
    json.dump(store, open('data/repos.json.tmp', 'w')); os.replace('data/repos.json.tmp', 'data/repos.json')
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
def grp(kind):
    rs = [r for r in store.values() if r['kind'] == kind]; cnt = C.Counter(r['cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
    oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    stated = [r for r in rs if r.get('tag')]; nofile = [r for r in stated if r.get('why') == 'no license file in the repository root']; sl, sh = K.wilson(len(nofile), len(stated))
    return rs, cnt, dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, awaiting=len([r for r in rs if r['cls'] == 'DISAGREE' and r['kind'] + '|' + r['id'] not in hc and r['id'] not in hc])), dict(stated=len(stated), no_file=len(nofile), share=round(len(nofile) / len(stated), 4) if stated else None, share_lo=round(sl, 4), share_hi=round(sh, 4))
M, cm, cmp_m, nf_m = grp('models'); D, cd, cmp_d, nf_d = grp('datasets')
why = C.Counter((r['kind'], r.get('why')) for r in store.values() if r['cls'] == 'NOT_COMPARABLE')
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed' if gate else 'FAILED', models=len(M), datasets=len(D), comparison={'Models': cmp_m, 'Datasets': cmp_d},
           classes={c: dict(models=cm[c], datasets=cd[c]) for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}, not_comparable_reasons={w: dict(models=why[('models', w)], datasets=why[('datasets', w)]) for w in sorted({w for _, w in why})},
           stated_without_file={'Models': nf_m, 'Datasets': nf_d},
           mixed={'Tag names a standard license, file is a custom or unnamed text': dict(models=len([r for r in M if r.get('tag_family') not in (None, 'OTHER') and r.get('file_family') == 'OTHER']), datasets=len([r for r in D if r.get('tag_family') not in (None, 'OTHER') and r.get('file_family') == 'OTHER'])),
                  'Tag is other or a custom name, file is a standard license': dict(models=len([r for r in M if r.get('tag_family') == 'OTHER' and r.get('file_family') not in (None, 'OTHER')]), datasets=len([r for r in D if r.get('tag_family') == 'OTHER' and r.get('file_family') not in (None, 'OTHER')]))},
           mixed_list=[dict(repo=r['id'], kind=r['kind'][:-1], tag=r['tag'], file=r.get('file'), note=hc.get('mixed|' + r['id'])) for r in store.values() if r.get('tag_family') not in (None, 'OTHER') and r.get('file_family') == 'OTHER' and ('mixed|' + r['id']) in hc],
           disagree_list=[dict(repo=r['id'], kind=r['kind'][:-1], tag=r['tag'], file=r.get('file'), file_family=r.get('file_family'), reason=hc.get(r['kind'] + '|' + r['id']) or hc.get(r['id'])) for r in store.values() if r['cls'] == 'DISAGREE' and (r['kind'] + '|' + r['id'] in hc or r['id'] in hc)])
json.dump(out, open('summary_hflicense.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'hflicense_live', '--path', os.path.join(H, 'summary_hflicense.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('hflicense:', len(M), 'models,', len(D), 'datasets;', dict(cm), dict(cd), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
