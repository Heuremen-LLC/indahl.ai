import sys, json
n = sys.argv[1]
t = open(f'rendered_{n}.txt').read()
i = t.find('Division:'); s = t.find('\n', 0)
lines = t.split('\n')
start = 7
out = []
for l in lines[start:]:
    if l.strip() == 'Privacy': break
    out.append(l)
print('\n'.join(x for x in out if x.strip()))
