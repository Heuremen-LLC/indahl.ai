import sys, collections
sys.path.insert(0, '/Users/heuremen/bones-forge/social_index/tiktok_referee/code')
from stated import rows
for rel in ['2023Q4', '2025Q3', '2026Q2']:
    R = rows(rel)
    c = collections.Counter(); ex = {}
    for r in R:
        if r['Metric'] in ('Proactive removal rate', 'Removal rate within 24 hours') and r['Location'] == 'Market':
            v = r['Result']
            d = len(v.split('.')[1]) if '.' in v else 0
            c[d] += 1; ex.setdefault(d, v)
    tot = sum(c.values())
    print(rel, {k: '%d (%.1f%%)' % (n, 100 * n / tot) for k, n in sorted(c.items())}, ex)
