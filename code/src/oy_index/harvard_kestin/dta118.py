# Minimal Stata 118 (.dta) reader, stdlib only. Returns (names, labels, rows, value_labels).
import struct
def read(path):
    b=open(path,'rb').read()
    K=struct.unpack('<H',b[b.index(b'<K>')+3:][:2])[0]
    N=struct.unpack('<Q',b[b.index(b'<N>')+3:][:8])[0]
    m=b.index(b'<map>')+5; off=struct.unpack('<14Q',b[m:m+112])
    vt=b.index(b'<variable_types>')+16; types=struct.unpack('<%dH'%K,b[vt:vt+2*K])
    vn=b.index(b'<varnames>')+10; names=[b[vn+129*i:vn+129*(i+1)].split(b'\0')[0].decode() for i in range(K)]
    vl=b.index(b'<variable_labels>')+17; labels=[b[vl+321*i:vl+321*(i+1)].split(b'\0')[0].decode('utf-8','replace') for i in range(K)]
    ln=b.index(b'<value_label_names>')+19; lnames=[b[ln+129*i:ln+129*(i+1)].split(b'\0')[0].decode() for i in range(K)]
    fmt={65526:('<d',8),65527:('<f',4),65528:('<i',4),65529:('<h',2),65530:('<b',1)}
    miss={65526:8.98846567431158e307,65527:1.7014118e38,65528:2147483620,65529:32740,65530:100}
    p=b.index(b'<data>')+6; rows=[]
    for _ in range(N):
        r=[]
        for t in types:
            if t in fmt:
                f,w=fmt[t]; v=struct.unpack(f,b[p:p+w])[0]; p+=w
                r.append(None if (v>=miss[t]) else v)
            elif t<=2045:
                r.append(b[p:p+t].split(b'\0')[0].decode('utf-8','replace')); p+=t
            else: raise ValueError('strL not supported')
        rows.append(r)
    vals={}
    q=b.find(b'<value_labels>')
    while True:
        q=b.find(b'<lbl>',q)
        if q<0: break
        q+=5; L=struct.unpack('<i',b[q:q+4])[0]; nm=b[q+4:q+133].split(b'\0')[0].decode(); t=b[q+136:q+136+L]
        n=struct.unpack('<i',t[:4])[0]; tl=struct.unpack('<i',t[4:8])[0]
        offs=struct.unpack('<%di'%n,t[8:8+4*n]); vv=struct.unpack('<%di'%n,t[8+4*n:8+8*n]); txt=t[8+8*n:]
        vals[nm]={vv[i]:txt[offs[i]:].split(b'\0')[0].decode('utf-8','replace') for i in range(n)}; q+=136+L
    return names,labels,rows,dict(zip(names,lnames)),vals
if __name__=='__main__':
    import sys; n,l,r,ln,v=read(sys.argv[1])
    print('vars',len(n),'rows',len(r))
    for i,(a,c) in enumerate(zip(n,l)): print(' ',a,'|',c,'| labelset',ln[a],'| first',[x[i] for x in r[:3]])
    for k,d in v.items(): print(' value labels',k,d)
