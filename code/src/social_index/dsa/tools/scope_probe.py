"""scope_probe.py: distinct territorial_scope strings in one month (values only, no counts), and which contain no EU member state."""
import sys, glob, os, site
sys.path.append(site.getusersitepackages())
import pyarrow.parquet as pq, pyarrow.compute as pc
EU = set('AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK'.split())
vals = set()
for f in glob.glob(os.path.join(sys.argv[1], '**', '*.parquet'), recursive=True):
    if os.path.isfile(f) and not os.path.basename(f).startswith('.'):
        vals |= set(pc.unique(pq.read_table(f, columns=['territorial_scope'])['territorial_scope']).to_pylist())
print('distinct', len(vals)); print('examples', sorted(map(str, vals), key=len)[:25])
special = {'EU', 'EEA', 'EEA_no_IS'}
noeu = [v for v in vals if v is not None and v not in special and not (set(v.split('_')) & EU)]
print('no EU member state:', sorted(noeu)); print('None present:', None in vals)
print('odd tokens:', sorted({t for v in vals if v and v not in special for t in v.split('_')} - EU - {'IS', 'NO', 'LI'}))
