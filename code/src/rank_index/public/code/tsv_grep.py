# usage: tsv_grep.py file regex -> TAPR download (names line, codes line, values line; names may contain stray newlines). prints name [code] => value
import sys,re
t=open(sys.argv[1],encoding='latin1').read().replace('\r','')
i=t.index('\nCAMPUS\t'); j=t.index('\n',i+1); 
names=t[:i].replace('\n',' ').split('\t'); codes=t[i+1:j].split('\t'); vals=t[j+1:].strip('\n').split('\n')[-1].split('\t')
assert len(names)==len(codes)==len(vals),(len(names),len(codes),len(vals))
for a,c,v in zip(names,codes,vals):
    if re.search(sys.argv[2],a): print(f"{a} [{c}] => {v}")
