import io, sys, urllib.request, zipfile
URL=sys.argv[1]
class RF(io.RawIOBase):
    def __init__(s,url):
        s.url=url; s.pos=0
        req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'Mozilla/5.0'})
        r=urllib.request.urlopen(req,timeout=60); s.size=int(r.headers['Content-Length'])
        s.cache={}
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s,off,wh=0):
        s.pos = off if wh==0 else (s.pos+off if wh==1 else s.size+off); return s.pos
    def read(s,n=-1):
        if n<0 or s.pos+n>s.size: n=s.size-s.pos
        if n<=0: return b''
        # chunk fetch with cache of 1MB blocks
        out=b''; pos=s.pos; end=pos+n
        while pos<end:
            blk=pos//(1<<20); 
            if blk not in s.cache:
                a=blk<<20; b=min(s.size-1,a+(1<<20)-1)
                req=urllib.request.Request(s.url,headers={'Range':f'bytes={a}-{b}','User-Agent':'Mozilla/5.0'})
                s.cache[blk]=urllib.request.urlopen(req,timeout=120).read()
            data=s.cache[blk]; off=pos-(blk<<20)
            take=data[off:off+(end-pos)]; out+=take; pos+=len(take)
            if not take: break
        s.pos=pos; return out
    def readinto(s,b):
        d=s.read(len(b)); b[:len(d)]=d; return len(d)
rf=RF(URL)
z=zipfile.ZipFile(io.BufferedReader(rf,buffer_size=1<<20))
names=z.namelist()
print('entries',len(names), 'size',rf.size)
import json
json.dump([(i.filename,i.file_size) for i in z.infolist()], open(sys.argv[2],'w'))
