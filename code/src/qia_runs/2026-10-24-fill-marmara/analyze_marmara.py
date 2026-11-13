"""analyze_marmara.py -- the four jobs through marmara.analyze(); planned readings per arm and R4."""
import json, sys, os; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import marmara as M
J = {j: [(k, l, c) for k, l, c in json.load(open(f'{HERE}/raw_marmara_{j}.json'))] for j, _ in M.JOBS}
r = M.analyze(J)
for arm in ('off', 'on'):
    a = r[arm]
    print(f"DD {arm.upper():3s}: mean success {a['succ']:.4f}; raw shortfall {a['raw']:.3f} +- {a['sraw']:.3f} (plug-in {a['raw_plugin']:.3f}); mitigated {a['mit']:.3f} +- {a['smit']:.3f} (plug-in {a['mit_plugin']:.3f})")
    print(f"         R1 mitigated vs 1 bit -> {a['R_mit']};  R2 raw vs 1 bit -> {a['R_raw']};  copy gap raw {a['copy_gap']:+.3f} (99 % half-width {M.Z99*a['sgap']:.3f}){'  GATED' if a['gate'] else ''}")
    print(f"         R3 (descriptive, not like-for-like: ours 17 CZ per message vs theirs 8-22) raw today minus their raw 1.279 -> {a['R_vs_theirs_raw']}")
print(f"R4 mitigated shortfall DD ON minus DD OFF = {r['R4_value']:+.3f} +- {r['R4_sd']:.3f} -> {r['R4']}")
print(f"bracket flips (DD OFF arm) P(1|0) {[round(x,4) for x in r['off']['e0']]}  P(0|1) {[round(x,4) for x in r['off']['e1']]}")
