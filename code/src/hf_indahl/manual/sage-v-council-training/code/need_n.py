# need_n.py <seat> <ts>: prints need_n(seat, ts) by the scheduler's definition (read-only): the smallest live n at which the 95% half-width
# of (live - pre) grounded rate is <= DROP, from the seat's last 100 recorded rows before ts.
import sys, math, sqlite3, os
H = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv[0].endswith('need_n.py') else os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if a != '--need']; seat, ts = args[0], args[1]; DROP = 0.15
g = [r[0] for r in sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True).execute("select grounded from pq where model=? and demo=0 and (? is null or ts <= ?) order by id desc limit 100", (seat, ts, ts))]
if len(g) < 20: print(100); sys.exit()
p = min(0.95, max(0.05, sum(g) / len(g))); se0 = math.sqrt(p * (1 - p) / len(g))
print(400 if 1.96 * se0 >= DROP else next(n for n in range(5, 400) if 1.96 * math.sqrt(se0 ** 2 + p * (1 - p) / n) <= DROP))
