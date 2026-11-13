#!/usr/bin/env python3
"""public_progress.py: tick-bus rider (every 24 ticks). For each live corner of indahl.ai, reads the corner's public JSON, flattens its numbers into one row and appends the row to
code/<corner>/history.jsonl in the public tree, then pushes with ledger/push_public.sh. A row is skipped when nothing changed since the last one. The history is the trend, one commit at a time.
Reads only what the site already serves publicly. No keys, no raw data."""
import os, sys, json, time, urllib.request, subprocess, datetime as D
PUB = os.path.expanduser('~/bones-forge/public_mirror/indahl.ai/code')
CORNERS = [('time', '/time/live.json', 'history.jsonl'), ('cada', '/cada/live.json', 'history.jsonl'), ('uptime', '/uptime/live.json', 'history.jsonl'), ('forecast', '/forecast/live.json', 'history.jsonl'),
           ('cadence', '/cadence/live.json', 'history.jsonl'), ('trials', '/trials/live.json', 'history.jsonl'), ('launch', '/launch/live.json', 'history.jsonl'), ('iris', '/iris/live.json', 'history.jsonl'),
           ('arxivdrift', '/arxivdrift/live.json', 'history.jsonl'), ('support', '/support/live.json', 'history.jsonl'), ('pkglicense', '/pkglicense/live.json', 'history.jsonl'), ('hflicense', '/hflicense/live.json', 'history.jsonl'), ('hfsize', '/hfsize/live.json', 'history.jsonl'), ('change', '/change/live.json', 'history.jsonl'), ('secrecords', '/secrecords/live.json', 'history.jsonl'), ('seat', '/seat/live.json', 'history.jsonl'), ('pkginstall', '/pkginstall/live.json', 'history.jsonl'), ('stack', '/stack/live.json', 'history.jsonl'), ('revise', '/revise/live.json', 'history.jsonl'), ('fedsep', '/fedsep/live.json', 'history.jsonl'), ('airline', '/airline/live.json', 'history.jsonl'), ('weights', '/weights/live.json', 'history.jsonl'), ('hpt', '/hpt/live.json', 'history.jsonl'), ('ailuminate', '/ailuminate/live.json', 'history.jsonl'), ('airq', '/airq/live.json', 'history.jsonl'), ('campus', '/campus/live.json', 'history.jsonl'), ('hosts', '/hosts/live.json', 'history.jsonl'), ('tape', '/tape/live.json', 'history.jsonl'), ('water', '/water/live.json', 'history.jsonl'), ('mirror', '/qia/audit.json', 'audit_history.jsonl'), ('mirror', '/qia/ibm.json', 'ibm_history.jsonl')]
SKIP = {'servers', 'sponsors', 'most_overdue', 'incidents', 'flagged', 'heads', 'updated', 'read', 'reference', 'seats', 'running', 'next', 'done', 'since', 'last_read', 'stamp'}
IDK = ('portal', 'backend', 'name', 'vendor', 'bin', 'resolver')
def flat(d, pre, out, depth=0):
    if depth > 3 or len(out) > 400: return
    if isinstance(d, dict):
        for k, v in d.items():
            if k in SKIP: continue
            flat(v, pre + str(k).replace(' ', '_') + '.', out, depth + 1)
    elif isinstance(d, list):
        if d and all(isinstance(x, dict) for x in d):
            for x in d:
                key = next((str(x[i]) for i in IDK if i in x), None)
                if key: flat({k: v for k, v in x.items() if k not in IDK}, pre + key.replace(' ', '_') + '.', out, depth + 1)
    elif isinstance(d, bool): pass
    elif isinstance(d, (int, float)): out[pre.rstrip('.')] = d
    elif isinstance(d, str) and pre.endswith('outcome.'): out[pre.rstrip('.')] = d

LIVE = {'qia-queue': ('https://indahl.ai/qia', 'QIA: queue at each IBM processor, hourly'), 'archive': ('https://indahl.ai/', 'Hash chain of our records, OpenTimestamps proofs and the Zenodo copies'), 'time': ('https://indahl.ai/time', 'TIME: public time servers, stated against delivered'), 'coin': ('https://indahl.ai/coin', 'COIN: Ravencoin against its own whitepaper, with trends'), 'cada': ('https://indahl.ai/cada', 'CADA: public DNS filters against fresh abuse reports'),
        'uptime': ('https://indahl.ai/uptime', 'UPTIME: vendor status pages against independent probes'), 'forecast': ('https://indahl.ai/forecast', 'FORECAST: stated chance of precipitation against what happened'), 'cadence': ('https://indahl.ai/cadence', 'CADENCE: stated update schedules against delivered'),
        'trials': ('https://indahl.ai/trials', 'TRIALS: ClinicalTrials.gov results due against results posted'), 'launch': ('https://indahl.ai/launch', 'LAUNCH: stated launch time against the time it flew'), 'water': ('https://indahl.ai/water', 'WATER: 24-Month Study projections of Lake Mead and Lake Powell against measured levels'), 'linkrot': ('https://indahl.ai/linkrot', 'LINKROT: stated code links against live'),
        'mirror': ('https://indahl.ai/qia', 'QIA: IBM published calibration, mirrored, audited and tracked for stability'), 't1t2-check': ('https://indahl.ai/qia', 'QIA: the T1 and T2 joint-measurement check'), 'iris': ('https://indahl.ai/iris', 'IRIS: language-model evaluations, Faults and Guards bench, lab queue'),
        'model': ('https://indahl.ai/hermes/model', 'MODEL: vendor claims and model claims against published results'), 'atlas': ('https://indahl.ai/atlas', 'ATLAS: built infrastructure, stated against delivered'), 'arxivdrift': ('https://indahl.ai/arxivdrift', "ARXIVDRIFT: Indexed arXiv studies against the version that stands now, live."), 'support': ('https://indahl.ai/support', "SUPPORT: Stated support windows against release activity, live."), 'pkglicense': ('https://indahl.ai/pkglicense', "PKGLICENSE: Package licenses against repository licenses, live."), 'hflicense': ('https://indahl.ai/hflicense', "HFLICENSE: Hugging Face stated licenses against license files, live."), 'hfsize': ('https://indahl.ai/hfsize', "HFSIZE: Hugging Face model names against the weights, live."), 'change': ('https://indahl.ai/change', "CHANGE: Vendor shutdown dates, read over time, live."), 'secrecords': ('https://indahl.ai/secrecords', "SECRECORDS: Security headers and mail records against their own rules, live."), 'seat': ('https://indahl.ai/seat', "SEAT: An outside seat reads our own pages, live."), 'pkginstall': ('https://indahl.ai/pkginstall', "PKGINSTALL: PyPI install commands against resolution, live."), 'stack': ('https://indahl.ai/stack', "STACK: Every test side by side, live."), 'revise': ('https://indahl.ai/revise', "REVISE: Payroll first estimates against the stated margin, live."), 'fedsep': ('https://indahl.ai/fedsep', "FEDSEP: The Fed's stated projection ranges against outcomes, live."), 'airline': ('https://indahl.ai/airline', "AIRLINE: Scheduled flight time against flown flight time per airline, live."), 'weights': ('https://indahl.ai/weights', "WEIGHTS: Open-weight model names against their weight files, pass after pass, live."), 'hpt': ('https://indahl.ai/hpt', "HPT: Hospital price-transparency files against the rule, live."), 'ailuminate': ('https://indahl.ai/ailuminate', "AILUMINATE: MLCommons AILuminate Safety results, kept and checked, live."), 'airq': ('https://indahl.ai/airq', "AIRQ: Air sensors against the EPA's own targets, live."), 'campus': ('https://indahl.ai/campus', "CAMPUS: The documents behind the OY page, kept over time, live."), 'hosts': ('https://indahl.ai/hosts', "HOSTS: Open-weight models, their hosts, quantization and uptime, live."), 'tape': ('https://indahl.ai/tape', "TAPE: A public hash chain of every page and live feed, with a beacon value in each run."), 'api': ('https://indahl.ai/api', 'API and MCP server'), 'kit': ('https://indahl.ai/', 'The shared instrument pieces every corner uses'),
        'replies': ('https://indahl.ai/', 'Right of reply: posted responses beside the rows they answer'), 'progress': ('https://indahl.ai/', 'The trend-row rider that writes history.jsonl in each folder')}
def readmes():
    n = 0
    for d, (url, what) in LIVE.items():
        dd = os.path.join(PUB, d)
        if not os.path.isdir(dd): continue
        f = os.path.join(dd, 'README.md'); mark = '<!-- live-link: generated by public_progress.py -->'
        if os.path.exists(f) and mark not in open(f).read(): continue
        files = sorted(x for x in os.listdir(dd) if x != 'README.md' and not x.startswith('.'))
        body = f"{mark}\n# {what}\n\nLive page: {url}\n\nEverything here is public. Each plan (PLAN.md) was committed before the data it describes. A history.jsonl, where present, is one row of the published numbers each time they changed, so the commit history is the trend. Terms: free to read, run and cite with attribution, no use as training data (LICENSE.txt at the repository root, https://indahl.ai/terms).\n\nFiles: " + ', '.join('`%s`' % x for x in files) + "\n"
        if body != (open(f).read() if os.path.exists(f) else ''): open(f, 'w').write(body); n += 1
    idx = os.path.join(PUB, 'README.md'); t = open(idx).read(); mk = '<!-- live-index -->'
    block = mk + '\n## Live pages\n\n' + '\n'.join(f'- [{d}/]({d}/): {w} - {u}' for d, (u, w) in LIVE.items() if os.path.isdir(os.path.join(PUB, d))) + '\n- [faultsguards](https://github.com/Heuremen-LLC/faultsguards): the Faults and Guards as a Python package. Live: https://indahl.ai/iris\n<!-- /live-index -->\n'
    t = t[:t.index(mk)] + block if mk in t and '<!-- /live-index -->' not in t[t.index(mk):] else (t[:t.index(mk)] + block + t[t.index('<!-- /live-index -->') + len('<!-- /live-index -->\n'):] if mk in t else t.rstrip() + '\n\n' + block)
    if t != open(idx).read(): open(idx, 'w').write(t); n += 1
    return n
def main():
    readmes()
    now = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'); changed = []
    for corner, path, fn in CORNERS:
        try: d = json.load(urllib.request.urlopen(urllib.request.Request('https://indahl.ai' + path, headers={'User-Agent': 'heuremen-progress/0.1'}), timeout=40))
        except Exception as e: print('progress:', corner, 'NOTHING_RETURNED', type(e).__name__); continue
        row = {}; flat(d, '', row)
        if not row: continue
        dst = os.path.join(PUB, corner); os.makedirs(dst, exist_ok=True); f = os.path.join(dst, fn); last = None
        if os.path.exists(f):
            for l in open(f): last = json.loads(l)
        if last and {k: v for k, v in last.items() if k != 't'} == row: continue
        with open(f, 'a') as o: o.write(json.dumps(dict(t=now, **row), sort_keys=True) + '\n')
        changed.append(corner)
    print('progress: rows added for', sorted(set(changed)) or 'none')
    if changed:
        p = subprocess.run(['bash', os.path.expanduser('~/bones-forge/ledger/push_public.sh'), 'Trend rows: ' + ', '.join(sorted(set(changed)))], capture_output=True, text=True)
        print('progress:', (p.stdout.strip().splitlines() or ['no output'])[-1])
if __name__ == '__main__': main()
