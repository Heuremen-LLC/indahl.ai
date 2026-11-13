# Builds web_walls.json for the WEB page: pages that returned a wall to one plain request. python3 -I web_walls.py
import json,collections,os
H=os.path.dirname(os.path.abspath(__file__)); r=json.load(open(os.path.join(H,'reach.json')))
no=sorted((d,v['code'],int(v.get('bytes') or 0)) for d,v in r.items() if not v['reached'])
codes=collections.Counter(c for d,c,b in no)
vend=[
 ('Dell Info Hub, MLPerf Inference v6.0 on PowerEdge with AMD Instinct MI355X','infohub.delltechnologies.com','bot check','16 Apr 2026 post, tried 28 Oct 2026','Text supplied and checked'),
 ('Dell Info Hub, three MLPerf posts (R770 and R770AP v6.1, overview, YOLO)','infohub.delltechnologies.com','bot check','tried 28 Oct 2026','Text supplied and checked'),
 ('Dell Info Hub, MLPerf Training v5.0 test results overview','infohub.delltechnologies.com','bot check','tried 28 Oct 2026','Not reached'),
 ('Dell, three MLPerf posts (XE9780 Inference v6.0, XE9712 Training v6.0, Training v6.0 overview)','www.dell.com','403','tried 28 Oct 2026','Not reached'),
 ('Azure, Llama 3.1 405B MLPerf Training at 8K+ GPU scale','azurefeeds.com','404','tried 28 Oct 2026','Text supplied and checked'),
 ('Intel newsroom, Intel software optimizations boost AI inference in MLPerf v6.1','www.intel.com','403','tried 28 Oct 2026','Text supplied and checked'),
 ('Intel newsroom, Intel Arc Pro B-Series GPUs and Xeon 6 in MLPerf Inference v5.1','newsroom.intel.com','403','second request 28 Oct 2026','Read on the first request'),
 ('Azure, Azure Delivers Strong MLPerf Inference v6.1 Results (mirror)','argonsys.com','202','tried 28 Oct 2026','Text supplied and checked'),
 ('Cisco, white paper on the UCS C845A M8 with NVIDIA GPUs','www.cisco.com','403','tried 28 Oct 2026','Text supplied and checked'),
 ('Cisco, white paper on the UCS X210c M8 with Intel Xeon 6','www.cisco.com','403','tried 28 Oct 2026','Text supplied and checked'),
 ('HPE, HPE delivers several world records in latest MLPerf Inference','community.hpe.com','403','tried 28 Oct 2026','Text supplied and checked'),
 ('Supermicro, press release on HGX B200 and MLPerf Inference v5.0','www.supermicro.com','403','tried 28 Oct 2026','Text supplied and checked'),
]
out=dict(tested=len(r),reached=len(r)-len(no),not_reached=len(no),by_code=dict(codes),under_2000_bytes=sum(1 for d,c,b in no if b<2000),vendor_pages=len(vend),vendor_text_supplied=sum(1 for v in vend if v[4].startswith('Text supplied')),vendor=[dict(page=a,host=b,code=c,date=d,status=e) for a,b,c,d,e in vend],schools=[dict(domain=d,code=c,bytes=b) for d,c,b in no])
json.dump(out,open(os.path.join(H,'web_walls.json'),'w'),indent=1)
print({k:out[k] for k in ('tested','reached','not_reached','by_code','under_2000_bytes','vendor_pages','vendor_text_supplied')})
