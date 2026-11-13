import numpy as np; from reddy import analyse
rng = np.random.default_rng(3)
def plant(F, xx=None):
    # a Werner-like planted state with all three correlators equal in magnitude: XX = -YY = ZZ = (4F-1)/3
    c = (4 * F - 1) / 3; out = {}
    for b, s in (('XX', 1), ('YY', -1), ('ZZ', 1)):
        p_same = (1 + s * c) / 2; k = rng.binomial(2000, p_same); out[b] = {'00': k // 2, '11': k - k // 2, '01': (2000 - k) // 2, '10': 2000 - k - (2000 - k) // 2}
    return out
lines = []
for name, F, want in (('IDEAL chip (F=1.0)', 1.0, 'ABOVE'), ('MODEL holds (F=0.9203)', 0.9203, 'CONSISTENT'), ('WORSE chip (F=0.85)', 0.85, 'BELOW'), ('BETTER chip (F=0.96)', 0.96, 'ABOVE'), ('NULL product state (F=0.25)', 0.25, 'BELOW')):
    r = analyse(plant(F)); lines.append('%-28s F %.4f se %.4f -> %s (want %s) %s' % (name, r['F'], r['se_F'], r['vs_sim']['outcome'], want, 'PASS' if r['vs_sim']['outcome'] == want else 'FAIL'))
# floor: how many CONSISTENT-world draws resolve falsely
fp = sum(analyse(plant(0.9203))['vs_sim']['outcome'] != 'CONSISTENT' for _ in range(400)); lines.append('FLOOR: model-true world, 400 draws: %d resolve ABOVE/BELOW (expect ~5%%)' % fp)
open('synth_results_reddy.text', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
