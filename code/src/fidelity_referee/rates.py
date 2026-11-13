import zipfile,re,json
F='/Users/heuremen/bones-forge/fidelity_index/raw/state-%s-rates-90-95-00-24.xlsx'
def rows(f):
    z=zipfile.ZipFile(f); ss=[re.sub('<[^>]+>','',m) for m in re.findall(r'<si>(.*?)</si>',z.read('xl/sharedStrings.xml').decode(),re.S)]
    out=[]
    for row in re.findall(r'<row.*?</row>',z.read('xl/worksheets/sheet1.xml').decode(),re.S):
        r=[]
        for a,b in re.findall(r'<c ([^>]*?)(?:/>|>(.*?)</c>)',row,re.S):
            v=re.search(r'<v>(.*?)</v>',b or ''); r.append('' if not v else (ss[int(v.group(1))] if 't="s"' in a else v.group(1)))
        out.append(r)
    return out
for ev in('divorce','marriage'):
    R=rows(F%ev); h=next(r for r in R if r[1:2]==['2024']); print(ev,h[:6],h[-6:])
    for r in R[R.index(h)+1:]:
        if r and r[0].strip() in('Louisiana','Georgia','Hawaii','Texas','California'): print(' ',r[0],dict(zip(h[1:],r[1:])) if r[0].strip() in ('Louisiana','Georgia') else r[1:6])
    foot=[r[0] for r in R if r and r[0] and len(r)<3]; print(foot[:12])
