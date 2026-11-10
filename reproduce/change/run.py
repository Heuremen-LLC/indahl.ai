#!/usr/bin/env python3
"""run.py: recompute the CHANGE headline from this kit, offline. Heuremen LLC, https://indahl.ai/reproduce

  python3 run.py                  recompute and print the headline as one line of JSON
  python3 run.py --check          also compare with expected.json and exit 1 on any difference
  python3 run.py --inputs DIR     read the input files from DIR instead of ./inputs (fetch-and-verify kits: the files you fetched)

The desk's own scripts in code/ run in a fresh temporary folder laid out like the desk folder, with the inputs beside them, with no network
(the proxy settings point at a closed local port). The headline is read from the output with the same field paths the ledger uses.
Standard library only, Python 3.9 or later."""
import gzip, hashlib, json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
K = json.load(open(os.path.join(HERE, 'kit.json')))
_MISS = object()
def dig(o, path):
    """Follow a path. Returns _MISS when any step is absent. '*' maps over the rest and returns a list."""
    for i, k in enumerate(path):
        if k == '*':
            vals = list(o.values()) if isinstance(o, dict) else (o if isinstance(o, list) else None)
            if vals is None: return _MISS
            out = [dig(v, path[i + 1:]) for v in vals]
            return _MISS if not out or any(x is _MISS for x in out) else out
        if isinstance(k, dict):
            if not isinstance(o, list): return _MISS
            o = next((x for x in o if isinstance(x, dict) and all(x.get(a) == b for a, b in k.items())), _MISS)
            if o is _MISS: return _MISS
            continue
        if isinstance(o, dict) and k in o: o = o[k]
        elif isinstance(o, list) and isinstance(k, int) and -len(o) <= k < len(o): o = o[k]
        else: return _MISS
    return o

def _f(n): return '{:,}'.format(int(n))

def display(spec, d):
    v = dig(d, spec['field']); s = spec['show']
    if s == 'pct': return '%.0f%%' % (100 * v)
    if s == 'pct1': return '%.1f%%' % (100 * v)
    if s == 'n_of': return '%s of %s' % (_f(dig(d, spec['n'])), _f(dig(d, spec['of'])))
    if s == 'of_minus_n': return '%s of %s' % (_f(dig(d, spec['of']) - dig(d, spec['n'])), _f(dig(d, spec['of'])))
    if s == 'count': return _f(v)
    if s == 'range': return '%g to %g' % (min(v), max(v))
    if s == 'years': return '%.1f years (%s days)' % (v / 365.25, _f(v))
    if s == 'age':
        a = max(0, 0 - (stamp_epoch(v) or 0)); return '%d min' % round(a / 60) if a < 5400 else '%.1f h' % (a / 3600)
    return str(v)


def reading(spec, d):
    g = lambda k: (None if not spec.get(k) else (lambda x: None if x is _MISS else x)(dig(d, spec[k])))
    v = dig(d, spec['field'])
    return dict(value=None if v is _MISS else v, display=display(spec, d), outcome=g('outcome'), lo=g('lo'), hi=g('hi'), n=g('n'), of=g('of'),
                keys=[(lambda x: None if x is _MISS else x)(dig(d, k)) for k in (spec.get('keys') or [])])

def main(a):
    src = a[a.index('--inputs') + 1] if '--inputs' in a else os.path.join(HERE, 'inputs')
    man = json.load(open(os.path.join(HERE, 'MANIFEST.json')))
    tmp = tempfile.mkdtemp(prefix='kit-'); work = os.path.join(tmp, 'work')
    try:
        os.makedirs(work)
        for f in man['inputs']:   # every input is checked against the sha256 the desk's scoring read, before anything runs
            p = os.path.join(src, f['stored'])
            if not os.path.exists(p): p = os.path.join(src, f['path'])
            if not os.path.exists(p): sys.exit('missing input: ' + f['path'])
            b = open(p, 'rb').read()
            if f.get('gzip_added') and p.endswith('.gz'): b = gzip.decompress(b)
            if hashlib.sha256(b).hexdigest() != f['sha256']: sys.exit('input differs from the one the desk read: %s (sha256 %s, expected %s)' % (f['path'], hashlib.sha256(b).hexdigest(), f['sha256']))
            d = os.path.join(work, f['path']); os.makedirs(os.path.dirname(d), exist_ok=True); open(d, 'wb').write(b)
        for f in man['code']:
            d = os.path.join(work, f['path']); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(os.path.join(HERE, 'code', f['path']), d)
        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': tmp, 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC', 'PYTHONHASHSEED': '0',
               'http_proxy': 'http://127.0.0.1:9', 'https_proxy': 'http://127.0.0.1:9', 'HTTP_PROXY': 'http://127.0.0.1:9', 'HTTPS_PROXY': 'http://127.0.0.1:9', 'no_proxy': '', 'NO_PROXY': ''}
        for st in K['steps']:
            r = subprocess.run([sys.executable, '-I'] + st, cwd=os.path.join(work, K.get('cwd', '')), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
            if r.returncode: sys.exit('step %s failed (exit %d): %s' % (' '.join(st), r.returncode, r.stderr.decode('utf-8', 'replace')[-600:]))
        out = json.load(open(os.path.join(work, K['output']), encoding='utf-8'))
        h = dict(desk=K['name'], **reading(K['headline'], out))
        line = json.dumps(h, sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n'
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.stdout.write(line)
    if '--check' in a:
        exp = open(os.path.join(HERE, 'expected.json'), encoding='utf-8').read()
        got = hashlib.sha256(line.encode('utf-8')).hexdigest(); want = open(os.path.join(HERE, 'expected.sha256')).read().split()[0]
        if line != exp or got != want: sys.stderr.write('DIFFERS from expected.json (sha256 %s, expected %s)\n' % (got, want)); return 1
        sys.stderr.write('matches expected.json, sha256 %s\n' % got)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
