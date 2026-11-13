"""analyze_tara.py -- reads raw_tara.json through tara.analyze(); prints the planned readings. Record check: the chosen pair's stated
cz and readout figures before vs after the job (a changed record during the window -> R1 CANNOT_TELL, per plan)."""
import json, sys, os; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
import tara; from sweep import stated
ents = [(k, tuple(l) if isinstance(l, list) else l, c) for k, l, c in json.load(open(f'{HERE}/raw_tara.json'))]
r = tara.analyze(ents); rec = json.load(open(f'{HERE}/job_tara.json')); pair = rec['pair']
qa, ga = stated(json.load(open(f'{HERE}/props_tara_before.json'))); qb, gb = stated(json.load(open(f'{HERE}/props_tara_after.json')))
changed = any(qa[p].get(k) != qb[p].get(k) for p in pair for k in ('readout_error', 'prob_meas0_prep1', 'prob_meas1_prep0')) or ga.get(('cz', tuple(pair))) != gb.get(('cz', tuple(pair)))
R1 = 'CANNOT_TELL' if changed else r['R1']
print(f"pair {pair}; record changed during window: {changed}")
print(f"E00 {r['E'][0][0]:+.4f} E01 {r['E'][0][1]:+.4f} E10 {r['E'][1][0]:+.4f} E11 {r['E'][1][1]:+.4f}")
print(f"R1 S_fez {r['S']:.4f} +- {r['se']:.4f} vs their table 2.7320 +- 0.0119: D {r['D']:+.4f} (99% half-width {tara.Z99*r['D_sd']:.4f}) -> {R1}")
print(f"R2 S - 2 = {r['S']-2:+.4f} (99% half-width {tara.Z99*r['se']:.4f}) -> {r['R2']}")
print(f"R3 cycle spread / shot noise {r['spread_ratio']:.2f} (CANNOT_TELL on R1 if > {tara.SPREAD_MAX}); cycle S {[round(x,3) for x in r['cycle_S']]}")
print(f"DESCRIPTIVE (not scored): bracket flip sums {r.get('bracket_flip_sum')}; bracket-corrected S {r.get('S_bracket_corrected')}")
print(f"their printed S 2.725 +- 0.042 for reference (Table 1); this is a RE-TEST on ibm_fez, not a calibration of their ibm_torino data")
