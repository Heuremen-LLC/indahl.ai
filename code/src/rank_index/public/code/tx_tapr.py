# usage: tx_tapr.py YEAR DSNAME OUTFILE  (campus 057905039 of Dallas ISD 057905, TAPR data download, public form)
import sys, re, urllib.request, urllib.parse
UA="HeuremenRANK/0.1 (+https://indahl.ai/oy)"
B="https://rptsvr1.tea.texas.gov/cgi/sas/broker"
def post(d):
    r=urllib.request.Request(B,urllib.parse.urlencode(d,doseq=True).encode(),headers={"User-Agent":UA})
    return urllib.request.urlopen(r,timeout=120).read().decode('latin1')
y,ds,out=sys.argv[1:4]
base=dict(_service="marykay",_program="perfrept.perfmast.sas",_debug="0",tapr="c_d",ccyy=y,level="Campus",sumlev="C",id="057905039")
h=post({**base,"dsname":ds,"prgopt":"reports/tapr/dd/dd_tapr_step_6.sas","bylev":"by Region","step":"5"})
keys=re.findall(r'name="key"[^>]*value="([^"]+)"',h)
vt=re.findall(r'name="var_type"[^>]*value="([^"]+)"',h)
print(len(keys),vt)
extra=dict(re.findall(r"<input[^>]*type=.hidden.[^>]*name=.(\w+).[^>]*value=.([^'\">]*)",h))
d={**base,"dsname":ds,"prgopt":"reports/tapr/dd/dd_tapr_step_7.sas","key":keys,"var_type":vt}
r=post(d)
open(out,"w").write(r)
print(len(r))
