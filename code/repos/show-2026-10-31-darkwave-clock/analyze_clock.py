"""analyze_clock.py DAYDIR -- reads one chip-fire of the Darkwave clock run per PLAN_CLOCK.md.text (committed before this fire's jobs ran).
Writes DAYDIR/results_clock.text: known-good, R1 shares, R2 clock, R3/R4, copies A/B and FINAL, and each table's age at job A."""
import json, os, sys, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, clock as C
D = os.path.abspath(sys.argv[1]); rec = json.load(open(f'{D}/job_clock.json')); chip = rec['chip']; S = rec['S']; keys = [tuple(k) for k in rec['keys']]
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')) if 'T' in s and ('Z' in s or '+' in s[10:] or '-' in s[19:]) else dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%z')
tA = ts([j for j in rec['jobs'] if j['label'] == 'A' and j['status'] == 'DONE'][-1]['submitted_utc'])
ks = json.load(open(os.path.join(HERE, '..', '2026-10-31-keystone', f'job_keystone_{chip}.json'))); t31 = ts([j for j in ks['jobs'] if j['label'] == 'C'][-1]['submitted_utc'])
t21 = dt.datetime.strptime(K.table(chip)['source_submitted'], '%Y-%m-%dT%H:%M:%S%z')
age = lambda t: (tA - t).total_seconds() / 3600
def Z(lab):
    z = np.load(f'{D}/raw_{lab}.npz'); order = list(range(len(keys))) if lab == 'A' else list(range(len(keys)))[::-1]
    return {keys[i]: z[f'fin_{i}'] for i in order}
ZA, ZB = Z('A'), Z('B'); rng = np.random.default_rng(31); res = {}
for lab, Zc in (('A', {k: [v] for k, v in ZA.items()}), ('B', {k: [v] for k, v in ZB.items()}), ('pooled', {k: [ZA[k], ZB[k]] for k in ZA})):
    res[lab] = C.read(Zc, len(S), rng)[0]
fin = C.final(res); kg = C.kg_pass(fin, chip)
L = [f'DARKWAVE CLOCK, {chip}, fire {rec["day_utc"]} UTC. Code and plan: PLAN_CLOCK.md.text (committed before the jobs). Copies A and B, FINAL = pooled if they agree.',
     f'Table ages at job A: 31 Oct table (M31) {age(t31):.1f} h | 21 Oct table (MC) {age(t21):.1f} h | today\'s table (MT) minutes.',
     f'KNOWN-GOOD (pooled median signed kick of M, 99 %): {fin["KG kick M (deg/readout)"]["v"]:.3f} [{fin["KG kick M (deg/readout)"]["lo"]:.3f}, {fin["KG kick M (deg/readout)"]["hi"]:.3f}] deg/readout -> {"PASS" if kg else "FAIL: chip-fire not decided"}']
for k, v in fin.items():
    if k.startswith('KG'): continue
    L.append(f'{k}: {v["v"]:+.3f} [{v["lo"]:+.3f}, {v["hi"]:+.3f}] n={v["n"]} | A {v["A"]} B {v["B"]} | FINAL {v["final"] if kg else "not decided (known-good)"}')
# ADDENDUM 1: the copy gap of the clock reading with its width (FINAL rule unchanged)
def _ab(Zc):
    ph = {a: np.arctan2(K.spect_expect(Zc[(a, 'Y')], len(S)), K.spect_expect(Zc[(a, 'X')], len(S))) for a in C.ARMS}
    return {a: np.abs(np.degrees(K.wrap(ph[a] - ph['D'])) / C.N) for a in ('M', 'M31', 'MT')}
_x = {'A': _ab({k: [v] for k, v in ZA.items()}), 'B': _ab({k: [v] for k, v in ZB.items()})}
def _d(c, ix): x = _x[c]; return (1 - np.median(x['M31'][ix]) / np.median(x['M'][ix])) - (1 - np.median(x['MT'][ix]) / np.median(x['M'][ix]))
_g = _d('A', np.arange(len(S))) - _d('B', np.arange(len(S))); _r = np.random.default_rng(31); _bs = []
for _ in range(20000):   # addendum 2
    _ix = _r.integers(0, len(S), len(S)); _bs.append(_d('A', _ix) - _d('B', _ix))
_lo, _hi = np.percentile(_bs, [0.5, 99.5])
L.append(f'copy gap of the clock reading (A minus B, addendum 1): {_g:+.3f} [{_lo:+.3f}, {_hi:+.3f}] -> {"resolves" if (_lo > 0 or _hi < 0) else "does not resolve"}')
open(f'{D}/results_clock.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
