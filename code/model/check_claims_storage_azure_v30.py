# Azure Managed Lustre MLPerf Storage v3.0 page held against storage/storage_v30_results.json and the Azure summary files. python3 -I check_claims_storage_azure_v30.py
import json, hashlib, re, glob, os, datetime as dt, statistics as st
FILES = ['storage/storage_v30_results.json']; RAW = {f: open(f, 'rb').read() for f in FILES}
R = json.loads(RAW[FILES[0]])['rows']; A = [r for r in R if r['submitter'] == 'Azure' and r['division'] == 'closed']
def mk(i, q, calc, st_, got, out, note): return dict(id=i, quote=q, calc=calc, stated=st_, delivered=got, outcome=out, note=note, label_mismatch=False)
tr = [r for r in A if r['category'] == 'training']; ck = [r for r in A if r['category'] == 'checkpointing']
def parse(r):
    m = re.match(r'AMLFS-Durable-Premium-(\d+)-(\d+)TiB-(\d+)-', r['system']); return int(m.group(1)), int(m.group(2))
INC = {20: 96, 40: 48, 125: 16, 250: 8, 500: 4}
for r in tr: r['tier'], r['cap'] = parse(r)
K = []
K.append(mk('AL1', 'All 17 Azure results use Azure Managed Lustre as a shared remote file system through the POSIX protocol.', 'Azure Closed rows in the results repository and their system descriptions', '17 results, remote shared file system, POSIX',
            f'{len(A)} Azure rows ({len(tr)} training, {len(ck)} checkpointing). storage_location {sorted({r["storage_location"] for r in A})}, benchmark API {sorted({r["benchmark_API"] for r in A})}', 'CONSISTENT' if len(A) == 17 and {r['storage_location'] for r in A} == {'remote'} and {r['benchmark_API'] for r in A} == {'file'} else 'BELOW',
            'The system files list a file API, not the word POSIX.'))
base = os.path.join('storage', 'v3.0', 'closed', 'Azure', 'results'); mins = []; hrs = []
for r in tr:
    fs = sorted(glob.glob(os.path.join(base, r['system'], 'training', 'unet3d', 'run', '*', 'summary.json'))); S = [json.load(open(f)) for f in fs][1:]
    hrs.append(sum((dt.datetime.fromisoformat(s['end']) - dt.datetime.fromisoformat(s['start'])).total_seconds() for s in S) / 3600)
K.append(mk('AL2', 'The Azure runs maintained more than 90% simulated accelerator utilization for five consecutive hours.', 'accelerator utilization (mean of runs 2 to 6) and the start and end times of those five runs, all 13 training entries', 'more than 90% utilization for five consecutive hours',
            f'lowest utilization {min(r["au_pct"] for r in tr):.1f}% of 13 entries. The five timed runs add up to {min(hrs):.2f} to {max(hrs):.2f} hours', 'CONSISTENT' if min(r['au_pct'] for r in tr) > 90 and min(hrs) >= 4.75 else 'BELOW',
            'Each run lasts about an hour and the five scored runs are consecutive with a few minutes between them. The sum of run time is 4.82 hours in the shortest entry, 3.6 percent under five hours. The rule used on MODEL for a rounded figure is up to 5 percent.'))
r3 = [r for r in tr if r['accelerators'] == 3]; r16 = [r for r in tr if r['accelerators'] == 16]
K.append(mk('AL3', 'Across the configurations with three simulated accelerators, measured read bandwidth was between 17.3 and 17.4 GiB/s.', '3 accelerator entries, mean of runs 2 to 6, MiB/s divided by 1,024', '17.3 to 17.4 GiB/s', f'{min(r["io_GiB_per_s"] for r in r3):.2f} to {max(r["io_GiB_per_s"] for r in r3):.2f} GiB/s over {len(r3)} entries', 'CONSISTENT' if round(min(r['io_GiB_per_s'] for r in r3), 1) == 17.3 and round(max(r['io_GiB_per_s'] for r in r3), 1) == 17.4 else 'BELOW', ''))
K.append(mk('AL4', 'At 16 simulated accelerators, measured read bandwidth was between 89.0 and 90.6 GiB/s across all five Azure Managed Lustre service tiers.', '16 accelerator entries', '89.0 to 90.6 GiB/s', f'{min(r["io_GiB_per_s"] for r in r16):.2f} to {max(r["io_GiB_per_s"] for r in r16):.2f} GiB/s over {len(r16)} entries', 'CONSISTENT' if round(min(r['io_GiB_per_s'] for r in r16), 1) == 89.0 and round(max(r['io_GiB_per_s'] for r in r16), 1) == 90.6 else 'BELOW', ''))
eff = []
for r in r16:
    nominal = r['cap'] / INC[r['tier']] * 2000 / 1073.741824; eff.append(100 * r['io_GiB_per_s'] / nominal)
K.append(mk('AL5', 'Across the five tested tiers, demonstrated density was between 95.6% and 97.3% of nominal.', 'measured GiB/s over nominal GiB/s = capacity / increment x 2,000 / 1,073.741824, the page formula, for the five 16 accelerator entries', '95.6% to 97.3%', f'{min(eff):.1f}% to {max(eff):.1f}% ({", ".join(f"{e:.1f}" for e in sorted(eff))})', 'CONSISTENT' if round(min(eff), 1) == 95.6 and round(max(eff), 1) == 97.3 else 'BELOW', 'Density over nominal density is the same ratio as bandwidth over nominal bandwidth.'))
a125 = {r['accelerators']: r for r in tr if r['tier'] == 125}
K.append(mk('AL6', 'The AMLFS 125 configurations increased from 3 simulated accelerators and 17.4 GiB/s (18.6 GB/s) to 70 simulated accelerators and 379.1 GiB/s (407.1 GB/s).', 'AMLFS 125 entries at 3 and 70 accelerators, GB/s = GiB/s x 1.073741824', '17.4 (18.6) at 3 and 379.1 (407.1) at 70', f'{a125[3]["io_GiB_per_s"]:.2f} GiB/s ({a125[3]["io_GiB_per_s"]*1.073741824:.2f} GB/s) at 3 and {a125[70]["io_GiB_per_s"]:.2f} ({a125[70]["io_GiB_per_s"]*1.073741824:.2f}) at 70',
            'CONSISTENT' if (round(a125[3]['io_GiB_per_s'], 1), round(a125[70]['io_GiB_per_s'], 1), round(a125[70]['io_GiB_per_s'] * 1.073741824, 1)) == (17.4, 379.1, 407.1) and abs(a125[3]['io_GiB_per_s'] * 1.073741824 - 18.6) < 0.1 else 'BELOW', 'The GB/s figure at 3 accelerators computes to 18.65, which the page prints as 18.6.'))
a20 = [r for r in tr if r['tier'] == 20 and r['accelerators'] == 70][0]
K.append(mk('AL7', 'In addition to the AMLFS 125 result, the AMLFS 20 configuration measured 378.0 GiB/s.', 'AMLFS 20 entry at 70 accelerators', '378.0 GiB/s', f'{a20["io_GiB_per_s"]:.2f} GiB/s', 'CONSISTENT' if round(a20['io_GiB_per_s'], 1) == 378.0 else 'BELOW', ''))
POST_T = [(20, 960, 3, 17.4), (40, 480, 3, 17.3), (125, 160, 3, 17.4), (250, 80, 3, 17.4), (500, 40, 3, 17.4), (20, 4800, 16, 90.3), (40, 2400, 16, 89.0), (125, 800, 16, 90.5), (250, 400, 16, 90.6), (500, 200, 16, 90.3), (125, 2400, 46, 251.6), (20, 25632, 70, 378.0), (125, 4096, 70, 379.1)]
bad = []
for tier, cap, acc, gib in POST_T:
    m = [r for r in tr if r['tier'] == tier and r['cap'] == cap and r['accelerators'] == acc]
    if len(m) != 1 or abs(m[0]['io_GiB_per_s'] - gib) > 0.05 + 1e-9: bad.append((tier, cap, acc, gib, round(m[0]['io_GiB_per_s'], 3) if m else None))
K.append(mk('AL8', 'Complete training results', 'the 13 rows of the page table matched to entries by tier, capacity and accelerator count in the system name', 'read bandwidth in GiB/s for 13 entries', f'{len(POST_T) - len(bad)} of {len(POST_T)} rows match to one decimal' + (f'. Differences: {bad}' if bad else ''), 'CONSISTENT' if not bad else 'BELOW', 'Boundary values such as 90.35 and 90.25 round either way at one decimal, so a difference of up to 0.05 is accepted.'))
POST_C = [('llama3-8b', 13.3, 14.8, 7.86, 7.10), ('llama3-70b', 105.5, 123.6, 8.65, 7.38), ('llama3-405b', 457.0, 438.1, 11.76, 12.39), ('llama3-1t', 642.2, 489.6, 24.63, 32.27)]
badc = []
def ckmetric(wl):
    fs = glob.glob(os.path.join(base, '*', 'checkpointing', wl, '*', 'summary.json')); S = [json.load(open(f))['metric'] for f in fs]
    return st.fmean([s['save_checkpoint_duration_mean_seconds'] for s in S if 'save_checkpoint_duration_mean_seconds' in s]), st.fmean([s['load_checkpoint_duration_mean_seconds'] for s in S if 'load_checkpoint_duration_mean_seconds' in s])
for wl, w, rd, wd, rdd in POST_C:
    r = [x for x in ck if x['workload'] == wl][0]; d = ckmetric(wl)
    if abs(r['write_GiB_per_s'] - w) > 0.05 + 1e-9 or abs(r['read_GiB_per_s'] - rd) > 0.05 + 1e-9 or abs(d[0] - wd) > 0.005 + 1e-9 or abs(d[1] - rdd) > 0.005 + 1e-9: badc.append((wl, round(r['write_GiB_per_s'], 3), round(r['read_GiB_per_s'], 3), round(d[0], 3), round(d[1], 3)))
K.append(mk('AL9', 'The largest result, representing the 1250B model, measured 642.2 GiB/s (689.6 GB/s) for checkpoint writes and 489.6 GiB/s (525.7 GB/s) for recovery reads.', 'the four checkpointing entries: write and read GiB/s and durations compared with the page table', 'four rows: 8B, 70B, 405B and 1250B', f'{len(POST_C) - len(badc)} of 4 rows match. The 642.2 and 489.6 values are the llama3-1t entry' + (f'. Differences: {badc}' if badc else ''), 'CONSISTENT' if not badc else 'BELOW',
            'The results repository names the largest checkpoint workload llama3-1t, with a checkpoint of 15,426 GB. The page labels it 1250B. The file holds no parameter count, so the label is not checked.'))
K.append(mk('AL10', 'Public ID', 'public entry IDs are on the MLCommons results page, not in the results repository', 'entries v3.0-0031 to v3.0-0047', 'the repository holds no entry IDs', 'CANNOT_TELL', 'The 17 entries match the page table by tier, capacity, accelerators and values; the ID column is not checked.'))
json.dump(dict(source=FILES + ['raw/storage_azure_lustre_v30.txt'], sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES], claims=K), open('claims_storage_azure_v30.json', 'w'), indent=1)
for c in K: print(c['id'], c['outcome'], '|', c['delivered'][:200])
