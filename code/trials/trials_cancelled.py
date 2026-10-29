#!/usr/bin/env python3
"""trials_cancelled.py: TRIALS Addendum 3. Interventional studies that started in the last two years and are now withdrawn, terminated or suspended.
Writes data/cancelled.json for trials_tick.py to merge into the summary. Descriptive census plus two tests against the registry's own rules."""
import os, re, sys, json, time, datetime as D, collections as C, urllib.parse, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K
BASE = 'https://clinicaltrials.gov/api/v2/studies'; UA = 'heuremen-trials/0.1 (+https://indahl.ai/trials)'
today = D.date.today(); start = today.replace(year=today.year - 2).isoformat(); end = today.isoformat()
POP = 'AREA[StudyType]INTERVENTIONAL AND AREA[StartDate]RANGE[%s,%s]' % (start, end)
def api(params, n=5):
    for a in range(n):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(BASE + '?' + urllib.parse.urlencode(params), headers={'User-Agent': UA}), timeout=90))
        except Exception: time.sleep(3 * (a + 1))
    raise RuntimeError('registry unreachable')
total = api({'filter.advanced': POP, 'pageSize': 1, 'countTotal': 'true', 'fields': 'NCTId'})['totalCount']
FIELDS = 'NCTId,OverallStatus,WhyStopped,StartDate,EnrollmentCount,EnrollmentType,LeadSponsorName,LeadSponsorClass,Phase'
recs = []; tok = None
while True:
    p = {'filter.advanced': POP, 'filter.overallStatus': 'WITHDRAWN|TERMINATED|SUSPENDED', 'pageSize': 1000, 'countTotal': 'true', 'fields': FIELDS}
    if tok: p['pageToken'] = tok
    d = api(p); recs += d.get('studies', []); tok = d.get('nextPageToken')
    if not tok: break
def flat(s):
    p = s['protocolSection']; st = p.get('statusModule', {}); sp = p.get('sponsorCollaboratorsModule', {}).get('leadSponsor', {}); dm = p.get('designModule', {})
    return dict(id=p['identificationModule']['nctId'], status=st.get('overallStatus'), why=(st.get('whyStopped') or '').strip(), start=(st.get('startDateStruct') or {}).get('date', ''),
                enrolled=(dm.get('enrollmentInfo') or {}).get('count'), cls=sp.get('class', 'UNKNOWN'), sponsor=sp.get('name', ''), phase='/'.join(dm.get('phases') or ['none']))
R = [flat(s) for s in recs]
REASONS = [('Funding or sponsor decision', r'funding|funder|financ|budget|business|strateg|sponsor|portfolio|priorit|commercial'), ('Recruitment', r'enrol|recruit|accrual|participants|feasib'),
           ('Safety or efficacy', r'safety|adverse|toxic|futil|efficacy|benefit'), ('Regulatory or supply', r'regulat|fda|approval|supply|availab|manufactur'), ('Investigator or site', r'investigator|pi left|site|staff|moved')]
def reason(t):
    if not t: return 'No reason given'
    for n, rx in REASONS:
        if re.search(rx, t, re.I): return n
    return 'Other text'
# gate
known = next((r for r in R if r['id'] == 'NCT05935592'), None); gate = bool(known and known['status'] == 'TERMINATED' and known['why'] and known['enrolled'] == 40) and total > 10000 and len(R) > 500 and reason('') == 'No reason given' and reason('Slow recruitment') == 'Recruitment' and reason('Sponsor decision') == 'Funding or sponsor decision'
print('trials cancelled: gate', 'passed' if gate else 'FAILED', 'population', total, 'stopped', len(R))
def wil(k, n):
    lo, hi = K.wilson(k, n); oc = K.CANNOT_TELL if (n < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return dict(of=n, n=k, share=round(k / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
bystat = C.Counter(r['status'] for r in R); cls = C.defaultdict(C.Counter)
for r in R: cls[r['cls']][r['status']] += 1
def quarter(d): return d[:4] + ' Q' + str((int(d[5:7]) - 1) // 3 + 1) if len(d) >= 7 else 'no date'
q = C.Counter(); qall = {}
for r in R: q[quarter(r['start'])] += 1
rc = C.Counter(reason(r['why']) for r in R)
blank = [r for r in R if not r['why']]; wd = [r for r in R if r['status'] == 'WITHDRAWN']; wd_pos = [r for r in wd if (r['enrolled'] or 0) > 0]
# the total by class for shares
tc = {}
for c in sorted({r['cls'] for r in R}):
    tc[c] = api({'filter.advanced': POP + ' AND AREA[LeadSponsorClass]' + c, 'pageSize': 1, 'countTotal': 'true', 'fields': 'NCTId'})['totalCount']
out = dict(window=dict(start=start, end=end), population=total, stopped=len(R), gate='passed' if gate else 'FAILED',
           headline=dict(withdrawn=bystat['WITHDRAWN'], terminated=bystat['TERMINATED'], suspended=bystat['SUSPENDED'], studies=total, share_text='%.1f%%' % (100 * len(R) / total)),
           by_class={c: dict(population=tc.get(c), withdrawn=cls[c]['WITHDRAWN'], terminated=cls[c]['TERMINATED'], suspended=cls[c]['SUSPENDED'], share_text='%.1f%%' % (100 * sum(cls[c].values()) / tc[c]) if tc.get(c) else '') for c in cls},
           reasons={k: dict(n=v, share_text='%.1f%%' % (100 * v / len(R))) for k, v in rc.most_common()},
           tests={'Stopped records with no reason given': wil(len(blank), len(R)), 'Withdrawn records that list participants enrolled': wil(len(wd_pos), len(wd))},
           by_quarter={k: dict(n=v) for k, v in sorted(q.items())},
           sample_for_hand_check=[dict(id=r['id'], status=r['status'], enrolled=r['enrolled'], sponsor=r['sponsor']) for r in wd_pos[:10]])
json.dump(out, open('data/cancelled.json', 'w'), indent=1); print(json.dumps(out['headline']), out['tests'])
