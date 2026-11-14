import json, sys
fl = set(json.load(open('live_floor.json'))['allowed_to_differ'])
A = {(r['method'], r['path']): r for r in json.load(open('live_before2.json'))}; B = {(r['method'], r['path']): r for r in json.load(open('live_after.json'))}
k = lambda r: (r['status'], r['location'], r['ctype'], r['sha'])
diff = [x for x in A if x in B and k(A[x]) != k(B[x])]; bad = [x for x in diff if x[1] not in fl]
print('after deploy: %d urls, %d differ, %d inside the stated floor, %d outside it' % (len(A), len(diff), len(diff) - len(bad), len(bad)))
for x in bad[:20]: print('  OUTSIDE FLOOR', x, A[x]['status'], '->', B[x]['status'])
sys.exit(1 if bad else 0)
