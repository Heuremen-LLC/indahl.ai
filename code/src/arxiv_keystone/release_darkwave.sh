#!/bin/bash
# release_darkwave.sh -- at the arXiv submission (his word, 31 Oct): Zenodo publish, the Darkwave page + front-page door, ledger rows, ship.
set -euo pipefail
B="$HOME/bones-forge"; A="$B/arxiv_keystone"; L="$B/ledger"
python3 "$A/zenodo_publish.py"
grep -q darkwave-countdown "$A/site/darkwave.html" && { echo "final page is the countdown, stopping"; exit 1; }
cp "$A/site/darkwave.html" "$B/heuremen.org/darkwave.html"; cp "$A/site/darkwave_fig1.png" "$B/heuremen.org/media/darkwave_fig1.png"
python3 - <<'PY'
p='/Users/heuremen/bones-forge/heuremen.org/index.html'; s=open(p).read()
a='<p class="paper"><a href="/a-readout-is-not-an-idle.pdf">Paper (PDF)</a></p>'
c='\n<p class="paper"><a href="/darkwave.html">Darkwave: midnight Eastern, 1 November 2026</a></p>'   # the countdown door
b=a+'\n<p class="paper"><a href="/darkwave.html">Darkwave: the readout&rsquo;s kick, given back (31 October 2026)</a></p>'
s=s.replace(a+c, a); assert s.count(a)==1 and 'darkwave.html' not in s; open(p,'w').write(s.replace(a,b)); print('front-page door: countdown swapped for the page')
PY
grep -q "'darkwave'" "$L/ledger.py" || python3 - <<'PY'
p='/Users/heuremen/bones-forge/ledger/ledger.py'; s=open(p).read()
a="    'iris_lab': 'indahl-ai/iris/lab.html',"
assert s.count(a)==1; open(p,'w').write(s.replace(a, "    'darkwave': 'heuremen.org/darkwave.html',   # 1 Nov: the Darkwave page (paper + clock)\n"+a, 1)); print('surface added')
PY
KC="$B/the_show/runs/2026-10-31-keystone/CHECKS.md"; CC="$B/the_show/runs/2026-10-31-darkwave-clock/CHECKS.md"
cd "$L"
python3 - "$KC" "$CC" <<'PY'
import subprocess, sys
KC, CC = sys.argv[1], sys.argv[2]; KR = 'the_show/runs/2026-10-31-keystone/results_keystone_ibm_%s.text'; CR = 'the_show/runs/2026-10-31-darkwave-clock/%s'
def add(i, claim, v, lo, hi, oc, src, grep, snip, checks):
    r = subprocess.run(['python3', 'ledger.py', 'add', i, '--claim', claim, '--value', v, '--lo', lo, '--hi', hi, '--outcome', oc, '--source', src, '--grep', grep, '--on', 'darkwave', snip, '--checks', checks], capture_output=True, text=True)
    print(i, 'added' if r.returncode == 0 else 'ADD FAILED ' + (r.stderr or r.stdout)[-300:]); assert r.returncode == 0
def on(i, snip):
    r = subprocess.run(['python3', 'ledger.py', 'on', i, 'darkwave', snip], capture_output=True, text=True); print(i, 'on' if r.returncode == 0 else 'ON FAILED ' + r.stderr[-200:]); assert r.returncode == 0
# paper cells not yet in the ledger
add('pub3.p4.marrakesh.mc', 'marrakesh share of Bell-pair phase given back, ten-day table', '0.396', '0.155', '0.642', 'CONSISTENT', KR % 'marrakesh', 'P4 pair-phase share given back MC vs 0.5             +0.3958', '0.40 [0.16, 0.64]', KC)
add('pub3.p4.kingston.me', 'kingston share of Bell-pair phase given back, echo', '0.986', '0.972', '0.991', 'ABOVE', KR % 'kingston', 'P4 pair-phase share given back ME vs 0.5             +0.9856', '0.99 [0.97, 0.99]', KC)
add('pub3.c4.kingston.me', 'kingston clock distance share given back, echo', '1.000', '0.996', '1.004', 'ABOVE', KR % 'kingston', 'C4 distance share given back ME vs 0.5               +0.9998', '1.00 [0.996, 1.004]', KC)
add('pub3.s7.marrakesh.me', 'marrakesh share of spectator kick given back, echo', '0.906', '0.838', '0.945', 'ABOVE', KR % 'marrakesh', 'S7 share given back ME vs 0.5 (ABOVE = more than half) +0.9059', '0.91 [0.84, 0.95]', KC)
add('pub3.p4.marrakesh.me', 'marrakesh share of Bell-pair phase given back, echo', '0.959', '0.922', '0.982', 'ABOVE', KR % 'marrakesh', 'P4 pair-phase share given back ME vs 0.5             +0.9588', '0.96 [0.92, 0.98]', KC)
add('pub3.c4.marrakesh.mf', 'marrakesh clock distance share given back, fresh table (copies disagree)', '0.770', '0.646', '0.882', 'CANNOT_TELL', KR % 'marrakesh', 'C4 distance share given back MF vs 0.5               +0.7703', '0.77, copies disagree', KC)
add('pub3.c4.marrakesh.me', 'marrakesh clock distance share given back, echo (copies disagree)', '0.848', '0.713', '0.942', 'CANNOT_TELL', KR % 'marrakesh', 'C4 distance share given back ME vs 0.5               +0.8479', '0.85, copies disagree', KC)
# the clock, first fire
add('clock.d1.kingston.m31', 'kingston 31 Oct table share given back, clock fire 1 (3 h old)', '0.915', '0.871', '0.954', 'ABOVE', CR % 'day_20261031_2206_ibm_kingston/results_clock.text', 'share given back M31 vs 0.5: +0.915', '0.92 [0.87, 0.95], 0.93 [0.89, 0.96]', CC)
add('clock.d1.kingston.diff', 'kingston 31 Oct table minus fresh table, clock fire 1 (CANNOT_TELL across bootstrap draws, readings_after_referee)', '-0.013', '-0.043', '0.031', 'CANNOT_TELL', CR % 'readings_after_referee.text', "kingston CANNOT_TELL at the plan's margin", '&minus;0.01 [&minus;0.04, +0.03]: cannot tell', CC)
add('clock.d1.kingston.mc', 'kingston ten-day table share given back, clock fire 1', '0.897', '0.849', '0.939', 'ABOVE', CR % 'day_20261031_2206_ibm_kingston/results_clock.text', 'share given back MC vs 0.5: +0.897', '0.90 [0.85, 0.94]', CC)
add('clock.d1.kingston.mcdiff', 'kingston ten-day table minus fresh table, clock fire 1', '-0.031', '-0.069', '0.010', 'CANNOT_TELL', CR % 'day_20261031_2206_ibm_kingston/results_clock.text', 'share MC minus share MT (margin 0.05): -0.031', '&minus;0.03 [&minus;0.07, +0.01]', CC)
add('clock.d1.marrakesh.m31', 'marrakesh 31 Oct table share given back, clock fire 1 (3 h old)', '0.829', '0.689', '0.874', 'ABOVE', CR % 'day_20261031_2207_ibm_marrakesh/results_clock.text', 'share given back M31 vs 0.5: +0.829', '0.83 [0.69, 0.87], 0.85 [0.74, 0.90]', CC)
add('clock.d1.marrakesh.diff', 'marrakesh 31 Oct table minus fresh table, clock fire 1', '-0.021', '-0.104', '0.036', 'CANNOT_TELL', CR % 'day_20261031_2207_ibm_marrakesh/results_clock.text', 'share M31 minus share MT (margin 0.05): -0.021', '&minus;0.02 [&minus;0.10, +0.04]: cannot tell', CC)
add('clock.d1.marrakesh.mc', 'marrakesh ten-day table share given back, clock fire 1', '0.346', '-0.048', '0.510', 'CONSISTENT', CR % 'day_20261031_2207_ibm_marrakesh/results_clock.text', 'share given back MC vs 0.5: +0.346', '0.35 [&minus;0.05, 0.51]', CC)
add('clock.d1.marrakesh.mcdiff', 'marrakesh ten-day table minus fresh table, clock fire 1', '-0.504', '-0.819', '-0.337', 'BELOW', CR % 'day_20261031_2207_ibm_marrakesh/results_clock.text', 'share MC minus share MT (margin 0.05): -0.504', '0.50 [0.34, 0.82] less than the fresh table', CC)
# paper rows already in the ledger
for i, sn in (('pub3.s7.kingston.mc', '0.92 [0.87, 0.95]'), ('pub3.s7.kingston.mf', '0.93 [0.87, 0.95]'), ('pub3.s7.kingston.me', '0.95 [0.91, 0.97]'),
              ('pub3.p4.kingston.mc', '0.93 [0.84, 0.96]'), ('pub3.p4.kingston.mf', '0.96 [0.92, 0.97]'), ('pub3.c4.kingston.mc', '0.76 [0.73, 0.78]'),
              ('pub3.c4.kingston.mf', '1.00 [0.997, 1.005]'), ('pub3.s7.marrakesh.mc', '0.24 [&minus;0.14, 0.44]'), ('pub3.s7.marrakesh.mf', '0.80 [0.67, 0.88]'),
              ('pub3.p4.marrakesh.mf', '0.92 [0.83, 0.96]'), ('pub3.c4.marrakesh.mc', '&minus;0.51 [&minus;1.13, &minus;0.09]'),
              ('pub3.kg.marrakesh', '&minus;1.68 [&minus;2.34, &minus;1.02] degrees per readout'), ('pub3.p2.kingston.mc', '0.014 [0.002, 0.023]'),
              ('pub3.s4.kingston.m', 'by 0.006 without correction')):
    on(i, sn)
PY
python3 check_ledger.py | tail -3
python3 - <<'PY'
import json
P='/Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/public/'
json.dump({'rows': [{'chip': 'ibm_kingston', 'text': '31 Oct table, 3 hours old: 0.92 against 0.93 fresh, cannot tell at the 0.05 margin'},
                    {'chip': 'ibm_marrakesh', 'text': '31 Oct table, 3 hours old: 0.83 against 0.85 fresh, cannot tell at the 0.05 margin'}]}, open(P + 'darkwave/clock.json', 'w'))
m=json.load(open(P + 'manifest.webmanifest'))
if not any(x['name'] == 'Darkwave' for x in m['shortcuts']): m['shortcuts'].insert(1, {'name': 'Darkwave', 'url': '/darkwave'})
json.dump(m, open(P + 'manifest.webmanifest', 'w'), indent=2); print('clock feed + Darkwave shortcut')
PY
bash "$L/ship.sh" "Darkwave: the readout's kick, given back (paper submitted to arXiv, data and code on Zenodo doi:10.5281/zenodo.23843468, first point on the clock)"
# 1 Nov: the same bundles on Hugging Face beside readout-run-data (one place: the indahl account). After the ship, and never blocks the release.
~/bones-forge/venv/bin/python "$A/upload_darkwave_hf.py" || echo "Darkwave Hugging Face upload FAILED (the release itself is done); rerun: ~/bones-forge/venv/bin/python $A/upload_darkwave_hf.py"
