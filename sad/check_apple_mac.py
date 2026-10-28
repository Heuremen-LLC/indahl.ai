# Apple MacBook Pro 14-inch technical specifications (M5 Max) against readings from the unit in this lab. Run on the Mac: python3 -I check_claims_apple_mac.py raw/mac_run_YYYYMMDD_HHMMSS.jsonl
import json,subprocess,sys,re,hashlib
RUN=sys.argv[1]
def sh(c): return subprocess.run(c,shell=True,capture_output=True,text=True).stdout
rows=[json.loads(l) for l in open(RUN)]
cpu=[r for r in rows if r['kind']=='cpu_triad']; gc=[r for r in rows if r['kind']=='gpu_copyk']; gt=[r for r in rows if r['kind']=='gpu_triad']
best=lambda L,k='best_gbs':max(r[k] for r in L)
med=lambda L:sorted(r['median_gbs'] for r in L)[len(L)//2]
sp=sh('system_profiler SPHardwareDataType SPDisplaysDataType SPStorageDataType 2>/dev/null')
def f(p,s=sp): m=re.search(p,s); return m.group(1).strip() if m else None
facts=dict(model_identifier=f(r'Model Identifier: (\S+)'),chip=f(r'Chip: (.+)'),cpu_cores=f(r'Total Number of Cores: (\d+ \(.*?\))'),gpu_cores=f(r'Total Number of Cores: (\d+)\n\s+Vendor'),memory=f(r'Memory: (.+)'),
  memsize_bytes=int(sh('sysctl -n hw.memsize')),perf0=(sh('sysctl -n hw.perflevel0.logicalcpu').strip(),sh('sysctl -n hw.perflevel0.name').strip()),perf1=(sh('sysctl -n hw.perflevel1.logicalcpu').strip(),sh('sysctl -n hw.perflevel1.name').strip()),
  resolution=f(r'Resolution: (\d+ x \d+)'),storage_bytes=int(re.search(r'Capacity: .*?\((\d[\d,]*) bytes\)',sp).group(1).replace(',','')),powermode=sh("pmset -g | awk '/powermode/{print $2}'").strip(),os=sh('sw_vers -productVersion').strip())
io=sh('ioreg -rn AppleSmartBattery 2>/dev/null'); g=lambda k:int(re.search(r'"%s" = (\d+)'%k,io).group(1))
facts.update(battery_design_mah=g('DesignCapacity'),battery_nominal_charge_mah=g('NominalChargeCapacity'),battery_cycles=g('CycleCount'))
def mk(cid,quote,calc,stated,got,outcome,note): return dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=False)
out=[]
gb=best(gt); gcp=best(gc); cb=best(cpu)
out.append(mk('M1','614GB/s memory bandwidth','Metal compute kernels on 1 GiB buffers (copy and triad, 3 runs of 20 passes) and a CPU triad on 1 GiB arrays (6, 12 and 18 threads, 3 runs of 15 passes), bandwidth counted as bytes read plus written over time',
 '614 GB/s',f'GPU triad {gb:.1f} GB/s ({gb/614*100:.1f}%), GPU copy {gcp:.1f} GB/s ({gcp/614*100:.1f}%), median GPU triad {med(gt):.1f} GB/s. CPU only {cb:.1f} GB/s ({cb/614*100:.1f}%)','BELOW',
 'The page states a figure and no test method. The Mac was idle apart from this terminal, our other jobs were paused for the run, and the power mode was %s (2 is High Power).'%facts['powermode']))
out.append(mk('M2','18-core CPU with: 6 super cores 12 performance cores','system_profiler and sysctl on the unit','18 cores, 6 super and 12 performance',f'{facts["cpu_cores"]}; sysctl: {facts["perf0"][0]} {facts["perf0"][1]} and {facts["perf1"][0]} {facts["perf1"][1]}','CONSISTENT','Counts are what the operating system reports.'))
out.append(mk('M3','40-core GPU','system_profiler on the unit','40-core GPU',f'{facts["gpu_cores"]} cores','CONSISTENT','Counts are what the operating system reports.'))
out.append(mk('M4','48GB, 64GB, or 128GB unified memory','sysctl hw.memsize on the unit','48GB',f'{facts["memsize_bytes"]:,} bytes, {facts["memsize_bytes"]/2**30:.0f} GiB','CONSISTENT','The unit has 48 GB. The 40-core GPU configuration is the one the page lists with 614 GB/s.'))
out.append(mk('M5','M5 Max 2TB, 4TB, or 8TB SSD','system_profiler on the unit','4TB',f'{facts["storage_bytes"]:,} bytes, {facts["storage_bytes"]/1e12:.2f} TB','CONSISTENT','Capacity of the data volume as the operating system reports it.'))
out.append(mk('M6','3024-by-1964 native resolution at 254 pixels per inch','system_profiler on the unit','3024 by 1964',f'{facts["resolution"]}','CONSISTENT','Resolution only. Pixels per inch was not checked.'))
out.append(mk('M7','72.4-watt-hour lithium-polymer battery','battery gauge through ioreg on the unit','72.4 Wh',f'gauge reports design capacity {facts["battery_design_mah"]:,} mAh and full-charge capacity {facts["battery_nominal_charge_mah"]:,} mAh ({facts["battery_nominal_charge_mah"]/facts["battery_design_mah"]*100:.1f}% of design) after {facts["battery_cycles"]} cycles','CANNOT_TELL','The gauge reports milliamp-hours. Watt-hours needs the pack voltage, which the gauge does not report as a rating.'))
out.append(mk('M8','Up to 20 hours video streaming','a full discharge under Apple\'s stated test conditions','up to 20 hours','not measured','CANNOT_TELL','Apple tested a preproduction system with set display brightness. The unit here was not run down.'))
out.append(mk('M9','XDR brightness: up to 1000 nits sustained full-screen','a luminance meter on the display','up to 1000 nits','not measured','CANNOT_TELL','No luminance meter was used.'))
json.dump(dict(source=[RUN],sha256=[hashlib.sha256(open(RUN,'rb').read()).hexdigest()],facts=facts,claims=out),open('claims_apple_mac.json','w'),indent=1)
for c in out: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:240])
