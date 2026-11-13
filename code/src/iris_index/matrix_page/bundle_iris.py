"""IRIS evaluation data, one public zip per set (25 Oct, his word: everything we have on the website; Pub #2 locked).
Our files only. Credential-pattern lines blanked; author surnames replaced with 'author'; local paths -> ~."""
import os, re, zipfile, json
B = os.path.expanduser('~/bones-forge/'); I = B + 'iris_index/'
OUT = B + 'cloudflare-workers/heuremen-door/public/iris/runs/'
MAP = {'matrix-round-1': ['matrix/results', 'matrix/results_synth', 'matrix/PLAN.md', 'matrix/run_matrix.py', 'matrix/score_matrix.py', 'matrix/synth_matrix.py', 'matrix/CODE.sha256', 'matrix/MATRIX.md', 'matrix/matrix_results.json', 'matrix/matrix_results_synth.json', 'matrix/synth_results.text', 'matrix/inputs', 'matrix/rebuild_inputs.md'],
       'matrix-round-2': ['matrix/results_v2', 'matrix/results_v2_synth', 'matrix/PLAN_v2.md', 'matrix/run_matrix_v2.py', 'matrix/score_matrix_v2.py', 'matrix/synth_matrix_v2.py', 'matrix/CODE_v2.sha256', 'matrix/MATRIX_v2.md', 'matrix/matrix_v2_results_v2.json', 'matrix/matrix_v2_results_v2_synth.json', 'matrix/synth_v2_results.text', 'matrix/score_v2_run_20261025.txt'],
       'frontier': ['matrix/frontier'],
       # 'pub2-experiments' HELD 26 Oct (his word: Pub #2 waits)
       'recounts': ['recounts']}
for _m in sorted(os.listdir(I + 'matrix/results_v2')):
    MAP['model-' + _m.replace('_', '-')] = ['matrix/results_v2/' + _m] + (['matrix/results/' + _m] if os.path.isdir(I + 'matrix/results/' + _m) else [])
for _r in sorted(os.listdir(I + 'recounts')):
    if os.path.isdir(I + 'recounts/' + _r) and _r != 'seed_faults_guards': MAP['study-' + _r] = ['recounts/' + _r]
R = json.load(open(I + 'IRIS_BOOK_register.json')); rows = R if isinstance(R, list) else R.get('rows', list(R.values()))
names = set()
for r in rows:
    for n in re.findall(r"[A-Z][a-z]+(?:[A-Z][a-z]+)?", re.sub(r'\([^)]*\)', '', r['authors'])):
        if n not in ('Bangladesh', 'Nepal', 'Utah', 'Florida', 'State', 'University'): names.add(n)
NRE = re.compile(r'\b(' + '|'.join(sorted(names, key=len, reverse=True)) + r')\b')
SEC = re.compile(r'(?i)api[_-]?key|apikey|bearer\s|secret|token\s*[=:]\s*["\'][A-Za-z0-9_\-.]{16,}|sk-[A-Za-z0-9]{20,}')
TEXT = ('.py', '.md', '.json', '.text', '.txt', '.sh', '.csv', '.jsonl', '.sha256', '.log')
def scrub(t):
    t = t.replace('/Users/heuremen', '~')
    t = '\n'.join('# (credential line removed)' if SEC.search(l) else l for l in t.split('\n'))
    return NRE.sub('author', t)
rep = {}
for pub, srcs in MAP.items():
    zp = OUT + pub + '.zip'; n = 0
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('TERMS.txt', open('/Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/public/TERMS_DATA.txt').read())
        for s in srcs:
            p = I + s
            files = [p] if os.path.isfile(p) else [os.path.join(a, f) for a, ds, fs in os.walk(p) for f in fs if '__pycache__' not in a and 'seed_faults_guards' not in a]
            for f in sorted(files):
                rel = os.path.relpath(f, I)
                if f.endswith(('.pyc', '.pkl', '.pt')): continue
                if f.endswith(TEXT): z.writestr(rel, scrub(open(f, errors='replace').read()))
                else: z.write(f, rel)
                n += 1
    rep[pub] = (n, round(os.path.getsize(zp) / 1e6, 2))
print(rep, 'names scrubbed:', len(names))
