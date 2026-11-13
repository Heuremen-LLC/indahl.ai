"""yf_textrecord.py -- Sage 5 Nov: for each of the 540 trained papers, does the text file training read belong to that DOI's own record?
Compares the trained key with the id encoded in the text file name. Inputs only."""
import os, re, builtins, json
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); Q = os.path.expanduser('~/bones-forge/qia_leads/')
src = open(H + '/yf_primary.py').read().split('\n'); exec('\n'.join(src[5:14]).replace('__file__', repr(H + '/yf_primary.py')))
_o = builtins.open
def _op(p, *a, **k): return _o(Q + 'matrix_page/list.json.pre-removal-20261102' if p == Q + 'matrix_page/list.json' else p, *a, **k)
builtins.open = _op; P = {k: p for k, _, p in yd.papers()}; builtins.open = _o
def key_of(fn):
    b = os.path.basename(fn)[:-4]
    if b.startswith('arxiv_'): return 'ax:' + b[6:]
    if b.startswith('doi_'): return 'doi:' + b[4:].replace('_', '/', 1)
    if re.match(r'^\d{4}\.\d{4,5}$', b): return 'ax:' + b
    return '?' + b
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
trained = {k: p for k, p in P.items() if yd.split(k) in ('TRAIN', 'VALID')}
mis = [(k, os.path.basename(p)) for k, p in sorted(trained.items()) if norm(key_of(p)) != norm(k)]
print(f'trained papers: {len(trained)}; text file not named for its own DOI: {len(mis)}')
for k, f in mis: print(f'  {k}  <- read {f}')
