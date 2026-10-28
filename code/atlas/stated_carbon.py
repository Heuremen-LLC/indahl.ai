#!/usr/bin/env python3
"""Google Cloud region carbon intensity against EPA's state record, per PLAN.md. Writes stated_carbon_rows.txt (ledger source lines), stated_carbon.html (page fragment), stated_carbon.json."""
import csv, json, os
H = os.path.dirname(os.path.abspath(__file__)); LB = 0.45359237
REG = {'us-central1': 'IA', 'us-central2': 'OK', 'us-east1': 'SC', 'us-east2': 'GA', 'us-east4': 'VA', 'us-east5': 'OH', 'us-south1': 'TX', 'us-west1': 'OR', 'us-west2': 'CA', 'us-west3': 'UT', 'us-west4': 'NV'}
_C = json.load(open(os.path.join(H, '..', 'electricity', 'carbon.json'))); epa = _C['states']; yr = _C['data_year']
def load(y): return {r['Google Cloud Region']: r for r in csv.DictReader(open(os.path.join(H, f'google_{y}.csv')))}
G = {2023: load(2023), 2024: load(2024)}
def oc(r): return 'consistent' if 0.75 <= r <= 1.25 else ('above' if r > 1.25 else 'below')
rows, lines = [], []; out = []
for reg, st in REG.items():
    e = epa[st]['co2_lb_mwh'] * LB; K = 'Grid carbon intensity (gCO2eq / kWh)'
    g3 = float(G[2023][reg][K]) if reg in G[2023] else None; g4 = float(G[2024][reg][K]); loc = G[2024][reg]['Location']
    r3 = g3 / e if g3 is not None else None; r4 = g4 / e
    f1 = lambda x: 'not published' if x is None else f'{x:.1f}'; f2 = lambda x: 'not published' if x is None else f'{x:.2f}'; o3 = 'cannot tell' if r3 is None else oc(r3)
    place = epa[st]['name'] if loc == epa[st]['name'] else f"{loc}, {epa[st]['name']}"
    line = f"{reg} {place} {f1(g3)} {f1(g4)} {e:.1f} {f2(r3)} {f2(r4)} {o3}, {oc(r4)}"
    lines.append(line); out.append(dict(region=reg, location=loc, state=st, google_2023=g3, google_2024=g4, epa_g_kwh=round(e, 1), ratio_2023=None if r3 is None else round(r3, 2), ratio_2024=round(r4, 2), outcome_2023=o3, outcome_2024=oc(r4)))
    rows.append(f"<tr><td>{reg}</td><td>{place}</td><td class=\"n\">{f1(g3)}</td><td class=\"n\">{f1(g4)}</td><td class=\"n\">{e:.1f}</td><td class=\"n\">{f2(r3)}</td><td class=\"n\">{f2(r4)}</td><td>{o3}, {oc(r4)}</td></tr>")
open(os.path.join(H, 'stated_carbon_rows.txt'), 'w').write('\n'.join(lines) + '\n'); json.dump(dict(eGRID_year=yr, rows=out), open(os.path.join(H, 'stated_carbon.json'), 'w'), indent=1)
excl = [r for r in G[2024] if r not in REG]
html = ('<h2>Stated against delivered: Google Cloud regions</h2><p>Google states a grid carbon intensity for each Cloud region, defined as the average operational gross emissions per unit of energy from the grid. EPA records CO2 per megawatthour of electricity generated in each state. Both are in grams of CO2 per kilowatthour here. The ratio is Google\'s figure divided by EPA\'s. The rule was committed before the comparison: consistent from 0.75 to 1.25, above over 1.25, below under 0.75. The band is wide because Google\'s figure is CO2 equivalent, EPA\'s is CO2 only, and a data center buys power across state lines.</p>'
        '<div class="scroll"><table class="mtx"><thead><tr><th>Google region</th><th>Location</th><th>Google 2023</th><th>Google 2024</th><th>EPA ' + str(yr) + '</th><th>Ratio 2023</th><th>Ratio 2024</th><th>Outcome 2023, 2024</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
        '<p class="bench-note">Left out: regions outside the United States and Google\'s carbon free energy percentages, which EPA has no counterpart for. Named here and want to answer a row? <a href="/respond?u=atlas-carbon">Respond</a></p>')
open(os.path.join(H, 'stated_carbon.html'), 'w').write(html); print('\n'.join(lines)); print('left out:', len(excl), 'non-US regions')
