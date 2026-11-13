"""yf_translate_match.py -- Sage 5 Nov translation pass, step 2. The trained papers that yf_lang.py found not in English, with their titles
translated to English BY THE MODEL IN SESSION (Claude, 5 Nov; no translation service), matched against every fresh paper (288) on title-word
Jaccard and author surnames. The fresh non-English paper in primary/sensitivity (zenodo.18154889, Turkish) is already called SAME WORK.
Papers whose text is not English but whose recorded title is (Gilbert, Chatterjee theses; PSI framework; SIPwQNN) are matched on the title as recorded."""
import json, os, re, unicodedata
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); M = json.load(open(H + '/contam/meta_cache.json'))
TR = {
 'doi:10.59722/riic.v3i2.1233': 'Xander: a quantum-classical ensemble for detecting advanced intrusions in modern networks',
 'doi:10.47283/244670492023110147': 'Performance comparison of the Deutsch-Jozsa algorithm in the quantum languages Silq and Qasm',
 'doi:10.5281/zenodo.19583314': 'Precision temporal metrology in NISQ systems: post-selected telegraphy, RAW audit and control of methodological artifacts',
 'doi:10.70675/81f9c638z5867z40e4zaed8ze9824ff5a163': None, 'doi:10.70675/a5ad5ad8z217az422az9443zcb2788cbc504': None,
 'doi:10.5281/zenodo.19687906': None, 'doi:10.5281/zenodo.14784888': None, 'doi:10.5281/zenodo.20944059': None, 'doi:10.5281/zenodo.17625820': None,
}
STOP = set('the and for with from via into onto using use under over its our their this that are was were has have not but can quantum'.split())
def tw(t): return {w for w in re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()) if len(w) >= 3 and w not in STOP}
def sur(n):
    n = unicodedata.normalize('NFKD', n or '').encode('ascii', 'ignore').decode().lower(); n = n.split(',')[0] if ',' in n else (n.split() or [''])[-1]
    return re.sub(r'[^a-z]', '', n)
fresh = sorted({json.loads(l)['paper'] for l in open(H + '/data/test_items_fresh.jsonl')})
prim = set(open(H + '/primary_ids.txt').read().split()); sens = set(open(H + '/sensitivity_ids.txt').read().split())
for k, t in TR.items():
    title = t or M[k]['title']; a1 = {sur(x) for x in M[k].get('authors') or [] if x}; t1 = tw(title)
    best = sorted(((len(t1 & tw(M[f].get('title'))) / max(1, len(t1 | tw(M[f].get('title')))), len(a1 & {sur(x) for x in M[f].get('authors') or [] if x}), f) for f in fresh), reverse=True)[:2]
    print(f'{k} | {title[:90]}')
    for T, A, f in best: print(f'    top fresh {f} [{"P" if f in prim else ""}{"S" if f in sens else ""}]: title {T:.2f}, shared surnames {A} | {(M[f].get("title") or "")[:80]}')
