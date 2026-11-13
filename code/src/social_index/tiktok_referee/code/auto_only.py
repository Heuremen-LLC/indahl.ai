import sys
sys.path.insert(0, '/Users/heuremen/bones-forge/social_index/tiktok_referee/code')
from stated import stated
for q in ('2025Q4', '2026Q1', '2026Q2'):
    o, d = stated(q, q)
    T = sum(v['T'] for v in d['market'].values()); A = sum(v.get('AUTO', 0) for v in d['market'].values()); I = sum(v.get('AI', 0) for v in d['market'].values())
    print(q, 'EU listed T=%d Automation=%d (%.2f%%) AI=%d (%.2f%%) Auto+AI=%.2f%%' % (T, A, 100*A/T, I, 100*I/T, 100*(A+I)/T))
