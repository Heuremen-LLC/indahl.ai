#!/usr/bin/env python3
"""wire_extras.py: tick-bus riders, live-headline entries and desk-pack entries for FLU, STEO and SEASONAL (10 Nov 2026). Backs up each file as
<file>.bak-20261110-fcdesks, compiles tick_bus.py with /usr/bin/python3 after the edit. Idempotent. Run while holding ledger/.site_edit.lock."""
import os, shutil, subprocess, sys
SLUG = sys.argv[1]
B = os.path.expanduser('~/bones-forge')
def patch(rel, fn):
    p = os.path.join(B, rel); t = open(p).read(); n = fn(t)
    if n == t: print('  unchanged', rel); return
    if not os.path.exists(p + '.bak-20261110-' + SLUG): shutil.copy2(p, p + '.bak-20261110-' + SLUG)
    open(p, 'w').write(n); print('  patched', rel)
RIDERS = """                                     (66, ['/opt/homebrew/bin/python3', '-P', os.path.expanduser('~/bones-forge/flu_index/flu_tick.py'), '--publish']),   # 10 Nov: FLU (HERMES), every 66 ticks (about 6 h): CDC FluSight ensemble intervals vs reported admissions; git pull of the hub at most once in 6 h; KV flu_live
                                     (264, [os.path.expanduser('~/bones-forge/steo_index/venv/bin/python'), '-P', os.path.expanduser('~/bones-forge/steo_index/steo_tick.py'), '--publish']),   # 10 Nov: STEO (HERMES), every 264 ticks (about a day): EIA STEO 95% intervals vs monthly spot; spot once a day, archive copies once a week; KV steo_live
                                     (264, ['/opt/homebrew/bin/python3', '-P', os.path.expanduser('~/bones-forge/seasonal_index/seasonal_tick.py'), '--publish']),   # 10 Nov: SEASONAL (HERMES), every 264 ticks (about a day): CPC 3-month outlook chances vs observed tercile + Heidke recompute; files once a day; KV seasonal_live
"""
def tb(t):
    line = next(l for l in RIDERS.splitlines(True) if '%s_index/%s_tick.py' % (SLUG, SLUG) in l)
    if '%s_index/%s_tick.py' % (SLUG, SLUG) in t: return t
    i = t.index("neo_index/neo_tick.py'), '--publish'])"); j = t.index('\n', i) + 1
    return t[:j] + line + t[j:]
patch('watch/tick_bus.py', tb)
r = subprocess.run(['/usr/bin/python3', '-m', 'py_compile', os.path.join(B, 'watch/tick_bus.py')], capture_output=True, text=True)
print('  tick_bus compile', 'ok' if r.returncode == 0 else 'FAILED ' + r.stderr[-300:])
if r.returncode: shutil.copy2(os.path.join(B, 'watch/tick_bus.py.bak-20261110-' + SLUG), os.path.join(B, 'watch/tick_bus.py')); sys.exit('tick_bus restored from backup')
LH = """ 'flu': dict(name='FLU', field=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'share'), n=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'inside'), of=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'scored'), show='n_of', stamp=P('updated'), cadence_h=12.0, kind='interval',
   outcome=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'outcome'), lo=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'lo'), hi=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'hi'),
   cadence_why='The flu_tick.py rider runs every 66 ticks (median 0.0917 h a tick, about 6 h) and pulls the hub at most every 6 hours. Doubled to 12 h so one late tick does not read stale. The count moves when the hub posts a new ensemble or a new release of the target data, about weekly.',
   rule_why='PLAN.md (Rules) states a moving-block bootstrap 95 percent interval over target weeks and the outcome rule against the stated 95 percent. The value rows flu.cell.all95 and flu.cell.h0_95 to flu.cell.h3_95 hold the shipped reading.'),
 'steo': dict(name='STEO', field=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'share'), n=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'inside'), of=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'scored'), show='n_of', stamp=P('updated'), cadence_h=48.0, kind='interval',
   outcome=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'outcome'), lo=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'lo'), hi=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'hi'),
   cadence_why='The steo_tick.py rider runs every 264 ticks (about a day) and reads EIA monthly spot prices at most once a day. Doubled to 48 h. The count moves when EIA posts a new month, about monthly.',
   rule_why='PLAN.md (Rules) states a moving-block bootstrap 95 percent interval over outcome months and the outcome rule against the stated 95 percent. The value rows steo.cell.wti.all and steo.cell.hh.all hold the shipped reading.'),
 'seasonal': dict(name='SEASONAL', field=P('cells', {'cell': 'temperature, leaning'}, 'observed'), n=P('cells', {'cell': 'temperature, leaning'}, 'hits'), of=P('cells', {'cell': 'temperature, leaning'}, 'rows'), show='pct', stamp=P('updated'), cadence_h=48.0, kind='interval',
   outcome=P('cells', {'cell': 'temperature, leaning'}, 'outcome'), lo=P('cells', {'cell': 'temperature, leaning'}, 'lo'), hi=P('cells', {'cell': 'temperature, leaning'}, 'hi'),
   cadence_why='The seasonal_tick.py rider runs every 264 ticks (about a day) and reads the CPC files at most once a day. Doubled to 48 h. The share moves when CPC adds a verified season, monthly.',
   rule_why='PLAN.md (Rules) states a moving-block bootstrap 95 percent interval over seasons and the outcome rule against the mean stated chance. The value rows seasonal.lean.temp and seasonal.lean.prec hold the shipped reading.'),
"""
def block(src):
    parts = {}; cur = None
    for l in src.splitlines(True):
        if l.startswith(" '") and "': dict(name='" in l: cur = l.split("'")[1]
        parts[cur] = parts.get(cur, '') + l
    return parts[SLUG]
def lh(t):
    if "'%s': dict(name=" % SLUG in t: return t
    i = t.index(" 'neo': dict(name='NEO'"); t = t[:i] + block(LH) + t[i:]
    Q = {'flu': 'When the CDC flu forecast states an interval, how often does the reported count land inside it?', 'steo': 'When EIA states a price interval, how often does the price land inside it?', 'seasonal': 'When the seasonal outlook states a chance, how often does it happen?'}
    a = "'neo': 'When JPL states how close an object will pass, where does the latest solution put it?'"
    t = t.replace(a, a + ", '%s': %r" % (SLUG, Q[SLUG]), 1)
    return t
patch('ledger/live_headlines.py', lh)
DP = """ 'flu': dict(name='FLU', folder='flu_index', lic='full', q='Stated flu forecast intervals against reported admissions',
     src=[('CDC FluSight Forecast Hub (FluSight-ensemble, FluSight-baseline, NHSN target data)', 'https://github.com/cdcepi/FluSight-forecast-hub', 'repository MIT licence, FluSight-ensemble CC BY 4.0 (credit the CDC FluSight team and UMass Amherst), NHSN data U.S. government work')]),
 'steo': dict(name='STEO', folder='steo_index', lic='full', q='Stated energy price intervals against the spot price',
     src=[('EIA Short-Term Energy Outlook chart gallery workbooks (Internet Archive copies)', 'https://www.eia.gov/outlooks/steo/', PD + '. Interval inputs credited by EIA to CME Group, Bloomberg, L.P., and Refinitiv an LSEG Business'),
          ('EIA monthly spot prices RWTC and RNGWHHD', 'https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=M', PD)]),
 'seasonal': dict(name='SEASONAL', folder='seasonal_index', lic='full', q='Stated seasonal outlook chances against what was observed',
     src=[('NOAA Climate Prediction Center 3-month outlook verification files', 'https://www.cpc.ncep.noaa.gov/products/predictions/long_range/tools/briefing/seas_veri.grid.php', 'NOAA/NWS, public domain, https://www.weather.gov/disclaimer')]),
"""
def dp(t):
    if "'%s': dict(name=" % SLUG in t: return t
    i = t.index(" 'neo': dict(name='NEO'"); return t[:i] + block(DP) + t[i:]
patch('tools/desk_pack.py', dp)
