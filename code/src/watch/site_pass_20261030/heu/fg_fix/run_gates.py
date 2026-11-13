"""House wording gates on the edited Faults/Guards sources, the way site_gate.py calls them (read only)."""
import importlib.util as u, json, re, sys
B = '/Users/heuremen/bones-forge/'
def load(name, path):
    s = u.spec_from_file_location(name, path); m = u.module_from_spec(s); s.loader.exec_module(m); return m
files = [B + 'ligera/FAULTS.html', B + 'ligera/GUARDS.html']
cs = load('count_scan', B + 'heuremen-specbook/count_scan.py')
h = cs.scan(files); print('count_scan (0b.5) hits:', len(h)); [print('  ', x) for x in h]
R = json.load(open(B + 'heuremen-specbook/site_rules.json'))
for f in files:
    s = open(f, encoding='utf-8').read()
    for r in R['forbid']:
        if re.search(r['pattern'], s): print('  FORBID', r['rule'], f.split('/')[-1], r['why'])
HANDS = re.compile(r'(?i)\bby hand\b|\bhand[- ](?:read|check|count)|\bhand-?checked\b|hand-labelled')
for f in files:
    for m in HANDS.finditer(open(f, encoding='utf-8').read()): print('  0b.9 HANDS', f.split('/')[-1], m.group(0))
print('forbid patterns + 0b.9 hand wording: checked')
ts = load('tone_scan', B + 'heuremen-specbook/tone_scan.py')
for f in files:
    hits = ts.scan(f); print(f'tone_scan (0b.8, business pages only; run here for information) {f.split("/")[-1]}: {len(hits)} hits', hits[:12])
pre = [B + 'ligera/FAULTS.pre-heu2-20261030.html', B + 'ligera/GUARDS.pre-heu2-20261030.html']
for f in pre:
    hits = ts.scan(f); print(f'  same scan on the pre-edit backup {f.split("/")[-1]}: {len(hits)} hits', hits[:12])
