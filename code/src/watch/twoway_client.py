"""two-way from THIS machine to a time echo. Run on the WIRED host to drop a radio hop."""
import socket, sys, time, json, statistics as st, math
ip=sys.argv[1]; n=int(sys.argv[2]) if len(sys.argv)>2 else 300
sk=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sk.settimeout(0.5)
rs=[]
for _ in range(n):
    try:
        t1=time.time(); sk.sendto(b'?',(ip,8769)); d,_=sk.recvfrom(128); t4=time.time()
        t2,t3=(float(x) for x in d.split())
        rs.append({'d':(t4-t1)-(t3-t2),'o':((t2-t1)+(t3-t4))/2.0})
    except Exception: pass
if len(rs)<3:
    print(json.dumps({'err':f'only {len(rs)} answered'})); raise SystemExit
rs.sort(key=lambda r:r['d']); keep=max(3,len(rs)//10)
offs=[r['o'] for r in rs[:keep]]
ds=sorted(r['d'] for r in rs)
p5=ds[max(0,int(0.05*len(ds))-1)]
print(json.dumps({'n':len(rs),'offset_s':st.mean(offs),
                  'scatter_s':st.stdev(offs)/math.sqrt(len(offs)) if len(offs)>1 else 0,
                  'min_rtt_s':ds[0],'p5_rtt_s':p5,'bound_s':p5/2.0}))
