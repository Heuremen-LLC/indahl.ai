import sys,json,re
sys.argv=['x']
S=open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read()
exec(S.split("# ---- intervals")[0])
exec(S.split("# ---- intervals")[1].split("BIN = [r for r in sc")[0])
BIN=[r for r in sc if r['kind']=='bin']
US=r'(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|Puerto Rico|Guam|Northern Mariana|American Samoa|Virgin Islands|Aleutian|Alaska Peninsula|Gulf of Alaska|Hubbard Glacier|Ridgecrest|CA\b|NV\b|AK\b|OK\b|TX\b)'
def isus(e):
    t=e['title']
    if e['net']!='us': return True
    return bool(re.search(US,t))
foreign=[(e['id'],e['title'],e['net']) for e in events.values() if not isus(e)]
usl=[(e['id'],e['title'],e['net']) for e in events.values() if isus(e) and e['net']=='us']
print('foreign',len(foreign),'us-net-in-US',len(usl))
for x in foreign[:200]: print(' F',x[1],x[2])
print('---- us-net-labelled-US (sample)'); 
for x in usl[:60]: print(' U',x[1])
