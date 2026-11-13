import sys,re,collections
rows=collections.defaultdict(dict)
for l in open(sys.argv[1]):
    l=l.rstrip('\n')
    if '\t' not in l: continue
    ref,v=l.split('\t',1); m=re.match(r'([A-Z]+)(\d+)',ref)
    rows[int(m.group(2))][m.group(1)]=v
for r in sorted(rows):
    d=rows[r]
    print("\t".join([d.get(c,'') for c in 'BDEFHIJKLMNO']))
