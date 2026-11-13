#!/usr/bin/env python3
"""roadmap_sync.py (11 Nov 2026, Wayfinder: "if you're not going to have a hardcoded path to update shit like this don't do it").

The /changes page is built from public_mirror/indahl.ai/ROADMAP.md. Before this, ROADMAP.md was edited by hand and went stale
(new desks missing, waits that had already ended). ship.sh step 1 runs this before build_site.py:
  1. every desk in build_site.py DESKS that ROADMAP.md does not already link gets a shipped line, in an auto block
  2. each open item with a rule below gets its status recomputed from the record, and ticks when its rule says done
Items with no rule are left as written.  python3 roadmap_sync.py [--check]   (--check: exit 1 if the file would change)"""
import ast, json, os, re, sys, time

B = os.path.expanduser('~/bones-forge')
RM = B + '/public_mirror/indahl.ai/ROADMAP.md'
SITE = B + '/indahl-ai/build_site.py'
TODO = B + '/ledger/TODO_internal.md'   # 11 Nov (his word): the open to-do list is internal, never on /changes
HEAD = ('# Changes: what has shipped', '', 'Every item has its live page and its plan. A desk is added here automatically when its page goes live, with the date it first appeared in this repository.', '')
A0, A1 = '<!-- auto: desks from build_site.py DESKS (ledger/roadmap_sync.py) -->', '<!-- /auto -->'


def desks():
    s = open(SITE, encoding='utf-8').read()
    i = s.index('\nDESKS = {') + 1; j = s.index('\n_DNAME', i)
    return ast.literal_eval(s[i:j].split('=', 1)[1].strip())


def days_held(path):
    first = last = None
    for ln in open(path):
        m = re.search(r'"t": "([^"]+)"', ln)
        if m: first = first or m.group(1); last = m.group(1)
    if not first: return 0
    f = lambda t: time.mktime(time.strptime(t[:19], '%Y-%m-%dT%H:%M:%S'))
    return int((f(last) - f(first)) // 86400)


def r_queue():
    d = days_held(B + '/qia_queue/data/history.jsonl')
    if os.path.exists(B + '/qia_queue/analysis.json'):
        a = json.load(open(B + '/qia_queue/analysis.json'))
        return True, ('**Queue against wait, the analysis** ([rule](code/qia-queue/PLAN.md), Note 1, [analysis](code/qia-queue/ANALYSIS.md)). '
                      'Run on %d days of readings with the committed rule, read at run level, with a run-gap sensitivity added after the first reading.' % d)
    return False, '**Queue against wait, the analysis** ([rule committed](code/qia-queue/PLAN.md), Note 1). Needs 7 days of readings, %d held.' % d


def r_zenodo():
    if 'zenodo_sync.py' in open(B + '/ledger/ship.sh').read():
        return True, '**New Zenodo versions with every release** (ledger/zenodo_sync.py). Each release refreshes the Zenodo records whose files changed, at most once a day per record.'
    return False, None


def r_boston():
    import glob   # 11 Nov: the newest Boston run (repeat runs are saved as results_ibm_boston_<YYYYMMDD>.json)
    fs = glob.glob(B + '/t1t2_check/runs/results_ibm_boston*.json')
    if not fs: return False, None
    runs = sorted((json.load(open(x)) for x in fs), key=lambda d: d['ran']); d = runs[-1]; q = d['qubits'].get('85', {})
    sm = json.load(open(B + '/t1t2_check/summary_t1t2.json'))
    pub = [x['pub_t2'] for p in sm['processors'] if p['backend'] == 'ibm_boston' for x in p.get('qubits', []) if x['qubit'] == 85][0]
    return True, ('**Boston T1 and T2** ([results](https://indahl.ai/qia#t1t2-live), [code](code/t1t2-check)). Run %d times on qubit 85, newest %s (job %s): T1 %.2f microseconds, T2 %.2f, so no T2 of either kind '
                  'can exceed %.1f on that qubit, against %s published.' % (len(runs), d['ran'][:10], d['job_id'], q['t1_us'], q['t2_us'], 2 * q['t1_ci'][1], '%.1f' % pub))


RULES = [(re.compile(r'\*\*Queue against wait'), r_queue), (re.compile(r'\*\*New Zenodo versions'), r_zenodo), (re.compile(r'\*\*Boston T1 and T2'), r_boston)]


def first_seen(url):
    import subprocess
    M = os.path.dirname(RM); f = url.strip('/') + '.html'
    run = lambda *a: subprocess.run(['git', '-C', M] + list(a), capture_output=True, text=True).stdout.split()
    d = run('log', '--diff-filter=A', '--format=%cs', '--', f)
    base = run('log', '--reverse', '--format=%cs')
    if not d: return time.strftime('%Y-%m-%d')
    return '' if base and d[-1] == base[0] else d[-1]


def build(text):
    pre, _, rest = text.partition(A0) if A0 in text else (text, '', '')
    if rest: post = rest.split(A1, 1)[1]; text = pre.rstrip('\n') + '\n' + post.lstrip('\n')
    out, todo = [], []
    lines = text.splitlines()
    k0 = next((i for i, l in enumerate(lines) if l.startswith('- [')), len(lines))
    lines = list(HEAD) + lines[k0:]
    for ln in lines:
        m = re.match(r'- \[( |x)\] (.*)', ln)
        if m:
            for rx, fn in RULES:
                if rx.search(m.group(2)):
                    done, t = fn()
                    if t: ln = '- [%s] %s' % ('x' if done else ' ', t)
        if ln.startswith('- [ ]'): todo.append(ln); continue
        out.append(ln)
    if todo:
        have = open(TODO).read() if os.path.exists(TODO) else '# Internal to-do (moved off /changes, 11 Nov 2026)\n\n'
        add = [t for t in todo if t not in have]
        if add: open(TODO, 'w').write(have.rstrip('\n') + '\n' + '\n'.join(add) + '\n')
    body = '\n'.join(out)
    new = []
    for div, items in desks().items():
        for url, name, what in items:
            if re.search(r'indahl\.ai%s[)"#\s]' % re.escape(url), body): continue
            d = first_seen(url)
            new.append((d, '- [x] **%s** ([live](https://indahl.ai%s)). %s.%s' % (name, url, what.rstrip('.'), (' Live since %s.' % d) if d else '')))
    new = [t for d, t in sorted(new, key=lambda x: x[0], reverse=True)]
    if new:
        k = max(i for i, l in enumerate(out) if l.startswith('- [x]'))
        out = out[:k + 1] + [A0] + new + [A1] + out[k + 1:]
    return '\n'.join(out).rstrip('\n') + '\n', len(new)


def main():
    cur = open(RM, encoding='utf-8').read(); new, n = build(cur)
    if '--check' in sys.argv:
        print('roadmap gate: %s' % ('current' if new == cur else 'stale')); return 0 if new == cur else 1
    if new != cur: open(RM, 'w', encoding='utf-8').write(new)
    print('roadmap: %d live desks added from DESKS, open-item rules applied%s' % (n, '' if new != cur else ' (unchanged)')); return 0


if __name__ == '__main__':
    sys.exit(main())
