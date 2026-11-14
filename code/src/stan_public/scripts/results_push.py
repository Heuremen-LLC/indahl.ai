#!/usr/bin/env python3
"""results_push.py (12 Nov 2026, "ANY training we do is live on the lab page and full public repo accessible"): copies STAN's public files to
GitHub Heuremen-LLC/stan and Hugging Face dataset indahl/stan-results when they changed, at most once every 20 minutes. Copy of council/results_push.py.
Only an allow-list is copied: code, the plan and its stamps, README, LICENSE, CHECKS.md, and results files that hold numbers only.
Never copied: data/, teachers/, runs/, review_queue/, gold labels, wall-flag lists (they name gold items), logs.  python3 results_push.py [--dry] [--force]"""
import hashlib, json, os, shutil, subprocess, sys, time
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PUB = os.path.expanduser('~/bones-forge/stan_public'); ST = S + '/results/.results_push_state.json'
GAP = 20 * 60; HF_REPO = 'indahl/stan-results'; HF_PY = os.path.expanduser('~/bones-forge/venv/bin/python')
TOP = ['PLAN.md', 'PLAN.sha256', 'PLAN.sha256.ots', 'PLAN_ADDENDUM_1.md', 'PLAN_ADDENDUM_1.sha256', 'PLAN_ADDENDUM_1.sha256.ots', 'README.md', 'LICENSE', 'CHECKS.md']
RES_OK = ['baseline_dev.json', 'baseline_dev.md', 'bench.json', 'live.json', 'paired_test.json', 'stan_dev_stratified.json', 'silver_summary.json', 'silver_summary_v1.json', 'slice_log.json']
LICENSE = open(os.path.expanduser('~/bones-forge/faultsguards/LICENSE.txt')).read()


def wanted():
    out = {}
    for f in TOP:
        if os.path.exists(S + '/' + f): out[f] = S + '/' + f
    for f in sorted(os.listdir(S + '/scripts')):
        if f.endswith(('.py', '.sh')): out['scripts/' + f] = S + '/scripts/' + f
    for f in RES_OK:
        if os.path.exists(S + '/results/' + f): out['results/' + f] = S + '/results/' + f
    for f in ('train_e/results/clustered_read.json', 'train_e/clustered_read.py', 'chain/NIGHT.md'):   # 13 Nov: the STAN-E LoRA ladder and its paper-clustered read (summaries only, no item rows)
        if os.path.exists(S + '/' + f): out[f] = S + '/' + f
    pr = S + '/results/public_rows'
    if os.path.isdir(pr):
        for f in sorted(os.listdir(pr)): out['results/public_rows/' + f] = pr + '/' + f
    return out


import re
SCRUB = re.compile(r'the council lane(?![A-Za-z])|sage[-_]v(?![a-z])|council', re.I)

def main():
    dry = '--dry' in sys.argv; st = json.load(open(ST)) if os.path.exists(ST) else {}
    if time.time() - st.get('at', 0) < GAP and '--force' not in sys.argv: print('stan results_push: last push under 20 min ago'); return 0
    if not ('--publish' in sys.argv or os.environ.get('HEUREMEN_PUBLISH') == '1' or dry): print('publish guard: stan results not pushed (run with --publish, or from the tick bus)', file=sys.stderr); return 0
    files = wanted(); files['LICENSE'] = None
    h = hashlib.sha256()
    for k in sorted(files): h.update(k.encode()); h.update(LICENSE.encode() if k == 'LICENSE' else open(files[k], 'rb').read())
    # live.json carries the clock, so the change test ignores its own 'updated' line
    dig = hashlib.sha256(); import re
    for k in sorted(files):
        b = LICENSE.encode() if k == 'LICENSE' else open(files[k], 'rb').read()
        if k == 'results/live.json': b = re.sub(rb'"updated": "[^"]*"', b'', b)
        dig.update(k.encode()); dig.update(b)
    if dig.hexdigest() == st.get('digest') and '--force' not in sys.argv: print('stan results_push: nothing new'); return 0
    if dry: print('stan results_push: would push %d files' % len(files)); return 0
    os.makedirs(PUB, exist_ok=True)
    keep = set(files)
    for root, ds, fs in os.walk(PUB):
        ds[:] = [d for d in ds if d != '.git']
        for f in fs:
            rel = os.path.relpath(os.path.join(root, f), PUB)
            if rel not in keep: os.remove(os.path.join(root, f))
    for k, src in files.items():
        dst = os.path.join(PUB, k); os.makedirs(os.path.dirname(dst), exist_ok=True)
        if k == 'LICENSE': open(dst, 'w').write(LICENSE)
        else:
            shutil.copyfile(src, dst)
            try:   # 13 Nov 2026 (Wayfinder): the council lane full scrub from anything public; the public copy only, house originals untouched
                t = open(dst, encoding='utf-8').read()
                if SCRUB.search(t):
                    t = re.sub(r'the council lane(?![A-Za-z])', 'the council lane', t); t = re.sub(r'sage[-_]v(?![a-z])|council', 'council', t, flags=re.I)
                    if k == 'PLAN.md': t += '\n\n---\nPublic copy edited 13 November 2026 to remove the name of a retired project. PLAN.sha256 covers the original plan, which is kept privately.\n'
                    open(dst, 'w', encoding='utf-8').write(t)
            except UnicodeDecodeError: pass
    g = lambda *a: subprocess.run(['git', '-C', PUB] + list(a), capture_output=True, text=True)
    g('add', '-A'); cm = g('commit', '-m', 'results and code, %s' % time.strftime('%Y-%m-%d %H:%MZ', time.gmtime()))
    staged = g('diff', '--cached', '--name-only').stdout.strip()   # 13 Nov: a refused commit (readcheck gate) used to read as GitHub ok
    if staged: p = subprocess.CompletedProcess([], 1, '', 'commit refused: ' + (cm.stdout + cm.stderr)[-300:]); ok_gh = False
    else: p = g('push', 'origin', 'HEAD'); ok_gh = p.returncode == 0
    hf = subprocess.run([HF_PY, '-c', 'import sys;from huggingface_hub import HfApi;HfApi().upload_folder(folder_path=sys.argv[1],repo_id=sys.argv[2],repo_type="dataset",allow_patterns=["results/*","results/**","README.md","LICENSE","PLAN*","CHECKS.md"],commit_message="results: live training rows")', PUB, HF_REPO],
                        capture_output=True, text=True, timeout=300); ok_hf = hf.returncode == 0
    if ok_gh and ok_hf: st['digest'] = dig.hexdigest()
    st.update(at=time.time(), last={'github': ok_gh, 'hf': ok_hf}); json.dump(st, open(ST, 'w'))
    print('stan results_push: GitHub %s, HF %s' % ('ok' if ok_gh else 'FAILED ' + (p.stderr or '')[-160:], 'ok' if ok_hf else 'FAILED ' + (hf.stderr or '')[-160:]))
    return 0 if (ok_gh and ok_hf) else 1


if __name__ == '__main__':
    sys.exit(main())
