"""context_dump.py: the contextual-information cells attached to every stated row the plan reads (sheet 8 Total rows, sheets 5/6/4 TOTAL rows)."""
import sys, os, json
sys.path.insert(0, '/Users/heuremen/bones-forge/social_index/dsa')
import dsa_tick as T, dsa_reports as R, dsa_db
out = {}
for r in T.find_reports():
    if not [f for f in r['files'] if f.lower().endswith(('.zip', '.csv', '.xlsx', '.xls'))]: continue
    sh = R.collect(r['dir']); want = [r['service'], dsa_db.NAMES.get(r['service'], '')]
    rep = R.read_report(r['dir'], want); per = (rep.get('identification', {}).get('start') or {}).get('iso')
    key = '%s %s' % (r['service'], per); out[key] = {}
    for k in ('8', '5', '6', '4'):
        if k not in sh: continue
        rows = sh[k]['rows']; hi = R.header_index(rows, 'applicability') or R.header_index(rows, 'indicator') or 0; hdr = rows[hi]
        ctx = [j for j, h in enumerate(hdr) if 'contextual' in R.norm(h)]
        for i in range(hi + 1, len(rows)):
            row = rows[i]; n = ' '.join(R.norm(c) for c in row[:7])
            hit = (k == '8' and ('number of measures solely' in n or 'number of measures not taken' in n) and (' total number' in n or ' total ' in n + ' ')) or (k != '8' and any(R.norm(c) == 'total' for c in row[3:4]))
            if not hit: continue
            for j in ctx:
                if j < len(row) and row[j].strip(): out[key]['%s|%s|%s' % (k, row[4][:40] if k == '8' else 'TOTAL', hdr[j][:70])] = row[j].strip()
json.dump(out, open('/Users/heuremen/bones-forge/social_index/dsa/data/context_notes.json', 'w'), indent=1)
for key, v in sorted(out.items()):
    if not v: continue
    print('=====', key)
    for kk, txt in v.items(): print('  [%s]\n    %s' % (kk, txt[:700].replace('\n', ' ')))
