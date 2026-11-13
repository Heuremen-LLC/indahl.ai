"""Referee: sequence numbers used per UTC day (S(next day) - S(day)), last 8 days, own in-order test. Usage: python3 -I seq_used_check.py DB"""
import sqlite3, sys, numpy as np, calendar, time
con = sqlite3.connect('file:%s?mode=ro' % sys.argv[1], uri=True)
t0 = calendar.timegm((2026, 10, 1, 0, 0, 0)) * 1000
a = np.array(con.execute('SELECT seq, cts FROM label WHERE sup = 0 AND seq > (SELECT MIN(seq) FROM label WHERE cts >= ?) - 200000 ORDER BY seq', (t0,)).fetchall(), dtype=np.int64)
s, c = a[:, 0], a[:, 1]
from numpy.lib.stride_tricks import sliding_window_view
med = np.partition(sliding_window_view(c, 21), 10, axis=1)[:, 10]; s2, c2 = s[10:-10], c[10:-10]; ok = np.abs(c2 - med) <= 86400000
D = 86400000; days = [calendar.timegm((2026, 11, d, 0, 0, 0)) * 1000 for d in range(2, 11)]
S = [int(s2[ok & (c2 >= t)].min()) for t in days]
for i in range(len(days) - 1): print(time.strftime('%Y-%m-%d', time.gmtime(days[i] / 1000)), S[i + 1] - S[i])
