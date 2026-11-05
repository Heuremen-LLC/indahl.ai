"""yf_minus.py -- the sensitivity analyses of Addendum 7 (Sage, 5 Nov). Usage: yf_minus.py TAG
Scores PRIMARY minus a named set of papers with the stamped scorer, unchanged: yf_score.py's bytes must equal its Addendum 3 hash
(26194d1a...). The scorer is run as written, with two redirects only: the primary items file it opens is replaced by the filtered
items file, and its two results files are written under new names (results_fresh_primary_minus_TAG.*) so primary is never overwritten.
Reported regardless of how they read; primary stays the headline."""
import sys, os, json, hashlib, builtins
H = os.path.dirname(os.path.abspath(__file__))
MINUS = {   # Addendum 7: written before the output block, listed by id
    'pktron': ['doi:10.2139/ssrn.7358502'],        # same-author sibling of a trained paper (rs-10838198); shares boilerplate only
    'text90': ['doi:10.5281/zenodo.18209070'],     # primary papers whose full-text share with one trained paper exceeds the floor's 90th percentile (0.121)
}
SCORER_SHA = '26194d1af29b1ab18b9d573d1213846e258b4c683b3d5a790dcf87c5a0ebad2d'
tag = sys.argv[1]; drop = set(MINUS[tag])
src = open(H + '/yf_score.py', 'rb').read()
assert hashlib.sha256(src).hexdigest() == SCORER_SHA, 'yf_score.py is not the stamped scorer'
prim = [json.loads(l) for l in open(H + '/data/test_items_primary.jsonl')]
keep = [i for i in prim if i['paper'] not in drop]
assert len({i['paper'] for i in prim}) - len({i['paper'] for i in keep}) == len(drop), 'a listed paper is not in primary'
mf = H + f'/data/test_items_primary_minus_{tag}.jsonl'
with open(mf, 'w') as f:
    for i in keep: f.write(json.dumps(i) + '\n')
_open = builtins.open
def _op(p, *a, **k):
    p = str(p)
    if p == H + '/data/test_items_primary.jsonl': p = mf
    elif p in (H + '/results_fresh_primary.text', H + '/results_fresh_primary.json'): p = p.replace('results_fresh_primary', f'results_fresh_primary_minus_{tag}')
    return _open(p, *a, **k)
builtins.open = _op; sys.argv = [H + '/yf_score.py', 'primary']
try: exec(compile(src, H + '/yf_score.py', 'exec'), {'__file__': H + '/yf_score.py', '__name__': '__main__'})
finally: builtins.open = _open
t = H + f'/results_fresh_primary_minus_{tag}.text'
body = open(t).read()
open(t, 'w').write(f'SENSITIVITY (Addendum 7): PRIMARY minus {tag} = {sorted(drop)}; {len({i["paper"] for i in keep})} papers, {len(keep)} items. '
                   f'The scorer header below says PRIMARY because it is the stamped scorer, unchanged.\n' + body)
