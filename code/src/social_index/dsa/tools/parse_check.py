"""parse_check.py: parse every report directory on disk; print period, publication date, sheets found and problems (no values)."""
import sys, os, glob
sys.path.insert(0, '/Users/heuremen/bones-forge/social_index/dsa')
import dsa_tick as T, dsa_reports as R, dsa_db
for r in T.find_reports():
    tmpl = [f for f in r['files'] if f.lower().endswith(('.zip', '.csv', '.xlsx', '.xls'))]
    if not tmpl: print('%-18s %-40s NO TEMPLATE FILE %s' % (r['service'], os.path.relpath(r['dir'], T.H)[-40:], [os.path.basename(f) for f in r['files']][:3])); continue
    rep = R.read_report(r['dir'], [r['service'], dsa_db.NAMES.get(r['service'], '')]); idn = rep.get('identification', {})
    have = sorted(k for k, v in rep['values'].items() if isinstance(v, dict) and v.get('value') is not None and not k.startswith('spam'))
    print('%-18s %s..%s pub=%s sheets=%s have=%s problems=%s' % (r['service'], (idn.get('start') or {}).get('iso'), (idn.get('end') or {}).get('iso'), (idn.get('published') or {}).get('iso'), ''.join(sorted(rep['sheets'])), len(have), rep['problems']))
