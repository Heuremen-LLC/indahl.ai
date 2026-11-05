"""yf_minus.py -- the sensitivity analyses of Addendum 10 (Sage, 5 Nov). Usage: yf_minus_a10.py TAG [primary|sensitivity] (yf_minus.py code, generalised to the sensitivity set)
Scores PRIMARY minus a named set of papers with the stamped scorer, unchanged: yf_score.py's bytes must equal its Addendum 3 hash
(26194d1a...). The scorer is run as written, with two redirects only: the primary items file it opens is replaced by the filtered
items file, and its two results files are written under new names (results_fresh_primary_minus_TAG.*) so primary is never overwritten.
Reported regardless of how they read; primary stays the headline."""
import sys, os, json, hashlib, builtins
H = os.path.dirname(os.path.abspath(__file__))
MINUS = {   # Addendum 10: the Addendum 9 lists, now on the SENSITIVITY set too
    'samework': ['doi:10.5281/zenodo.18154889'],
    'samework_border': ['doi:10.5281/zenodo.18154889', 'doi:10.5281/zenodo.19437054'],
}
SCORER_SHA = '26194d1af29b1ab18b9d573d1213846e258b4c683b3d5a790dcf87c5a0ebad2d'
tag = sys.argv[1]; SET = sys.argv[2] if len(sys.argv) > 2 else 'primary'; assert SET in ('primary', 'sensitivity'); drop = set(MINUS[tag])
src = open(H + '/yf_score.py', 'rb').read()
assert hashlib.sha256(src).hexdigest() == SCORER_SHA, 'yf_score.py is not the stamped scorer'
prim = [json.loads(l) for l in open(H + f'/data/test_items_{SET}.jsonl')]
keep = [i for i in prim if i['paper'] not in drop]
assert len({i['paper'] for i in prim}) - len({i['paper'] for i in keep}) == len(drop), f'a listed paper is not in {SET}'
mf = H + f'/data/test_items_{SET}_minus_{tag}.jsonl'
with open(mf, 'w') as f:
    for i in keep: f.write(json.dumps(i) + '\n')
_open = builtins.open
def _op(p, *a, **k):
    p = str(p)
    if p == H + f'/data/test_items_{SET}.jsonl': p = mf
    elif p in (H + f'/results_fresh_{SET}.text', H + f'/results_fresh_{SET}.json'): p = p.replace(f'results_fresh_{SET}', f'results_fresh_{SET}_minus_{tag}')
    return _open(p, *a, **k)
builtins.open = _op; sys.argv = [H + '/yf_score.py', SET]
try: exec(compile(src, H + '/yf_score.py', 'exec'), {'__file__': H + '/yf_score.py', '__name__': '__main__'})
finally: builtins.open = _open
t = H + f'/results_fresh_{SET}_minus_{tag}.text'
body = open(t).read()
open(t, 'w').write(f'SENSITIVITY (Addendum 10): {SET.upper()} minus {tag} = {sorted(drop)}; {len({i["paper"] for i in keep})} papers, {len(keep)} items. '
                   f'The scorer header below is from the stamped scorer, unchanged.\n' + body)
