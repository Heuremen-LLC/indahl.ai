import sys
sys.path.insert(0, '/Users/heuremen/bones-forge/social_index/tiktok_referee/code')
from stated import cells, EU, EFTA
tot_cmp = 0; diffs = []; only = []
for q in ['2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1']:
    own = q if q != '2023Q3' else '2023Q4'
    a, _ = cells(own, q); b, _ = cells('2026Q2', q)
    keys = [k for k in set(a) | set(b) if k[0] in EU + EFTA + ['GLOBAL']]
    for k in keys:
        if k in a and k in b:
            tot_cmp += 1
            if abs(a[k] - b[k]) > 1e-9: diffs.append((q, k, a[k], b[k]))
        else:
            only.append((q, k, 'own' if k in a else 'latest', a.get(k, b.get(k))))
print('cells compared', tot_cmp, 'differing', len(diffs), diffs[:10])
print('cells in only one release', len(only), only[:20])
