#!/usr/bin/env python3
"""trials_cancelled.py: TRIALS Addendum 3. Interventional studies that started in the last two years and are now withdrawn, terminated or suspended.
Writes data/cancelled.json for trials_tick.py to merge into the summary. Descriptive census plus two tests against the registry's own rules."""
import os, re, sys, json, time, random, datetime as D, collections as C, urllib.parse, urllib.request
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
           ('Safety or efficacy', r'safety|adverse|toxic|futil|efficacy|benefit'), ('Regulatory or supply', r'regulat|fda|approval|supply|availab|manufactur'), ('Investigator or site', r'investigator|pi left|site|staff|moved'),
           ('Never started or never approved', r'never start|not start|never initiat|not initiat|never approved|not approved|no participants|never opened'), ('Registration replaced or withdrawn', r'registration|registered|duplicate|isrctn|another registry'),
           ('Pandemic or logistics', r'covid|pandemic|logistic'), ('Sponsor or partner decided', r'partner|company|collaborator|decided|decision|discontinu|no longer|not to pursue|not proceed'),
           ('Resources or staff', r'resource|staff|personnel|faculty|human|lack of|insurance|unable to provide|\bfunds?\b'), ('Design or outcome changed', r'design|protocol|outcome measure|standard of care|inapplicab|amend')]
def reason(t):
    if not t: return 'No reason given'
    for n, rx in REASONS:
        if re.search(rx, t, re.I): return n
    return 'Matches none of the words'
# gate
known = next((r for r in R if r['id'] == 'NCT05935592'), None); gate = bool(known and known['status'] == 'TERMINATED' and known['why'] and known['enrolled'] == 40) and total > 10000 and len(R) > 500 and reason('') == 'No reason given' and reason('Slow recruitment') == 'Recruitment' and reason('Study was never started') == 'Never started or never approved' and reason('zzz qqq') == 'Matches none of the words' and reason('Sponsor decision') == 'Funding or sponsor decision'
print('trials cancelled: gate', 'passed' if gate else 'FAILED', 'population', total, 'stopped', len(R))
def wil(k, n):
    # 12 Nov 2026, PLAN_ADDENDUM_std2.md (Faults and Guards 2.0): size that matters 0.10, null 0, band [0, 0.05), edge '[)'. Under 30 records is TOO_WIDE_TO_RESOLVE, a failed known-good gate is NO_INTERVAL_FORMABLE.
    lo, hi = K.wilson(k, n); lo = 0.0 if k == 0 else lo; hi = 1.0 if k == n else hi   # exact ends of the Wilson interval, so zero events reaches the null
    if not gate: oc, why = K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    elif n < 30: oc, why = K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE
    else: oc, why = K.read(lo, hi, band=(0.0, 0.05), matters=0.10, edge='[)', null=0.0)
    return dict(of=n, n=k, share=round(k / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, reason=why, req13=K.req13([(oc, why)], nothing_returned=0))
bystat = C.Counter(r['status'] for r in R); cls = C.defaultdict(C.Counter)
for r in R: cls[r['cls']][r['status']] += 1
def quarter(d): return d[:4] + ' Q' + str((int(d[5:7]) - 1) // 3 + 1) if len(d) >= 7 else 'no date'
q = C.Counter(); qall = {}
for r in R: q[quarter(r['start'])] += 1
rc = C.Counter(reason(r['why']) for r in R)
open('data/unmatched_reasons.txt', 'w').write('\n'.join(r['id'] + '\t' + r['why'] for r in R if r['why'] and reason(r['why']) == 'Matches none of the words'))
blank = [r for r in R if not r['why']]; wd = [r for r in R if r['status'] == 'WITHDRAWN']; wd_pos = [r for r in wd if (r['enrolled'] or 0) > 0]
# 30 Oct (site pass H-14): the ten records of the first test that Addendum 3 says are read in full. The ten are drawn once (seed 7, sorted ids) and kept in data/hand_sample.json. A row is listed only when its note is in data/hand_checked.json.
if not os.path.exists('data/hand_sample.json'): json.dump(random.Random(7).sample(sorted(r['id'] for r in blank), min(10, len(blank))), open('data/hand_sample.json', 'w'))
_hs = json.load(open('data/hand_sample.json')); _hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}; _by = {r['id']: r for r in R}
hand = [dict(id=i, status=_by[i]['status'] if i in _by else None, sponsor=_by[i]['sponsor'] if i in _by else None, still_without_reason=bool(i in _by and not _by[i]['why']), record_says=_hc[i]) for i in _hs if i in _hc]
_sp = C.Counter(r['sponsor'] for r in blank); _top = _sp.most_common(1)[0][1] if _sp else 0
# the total by class for shares
tc = {}
for c in sorted({r['cls'] for r in R}):
    tc[c] = api({'filter.advanced': POP + ' AND AREA[LeadSponsorClass]' + c, 'pageSize': 1, 'countTotal': 'true', 'fields': 'NCTId'})['totalCount']
out = dict(window=dict(start=start, end=end), population=total, stopped=len(R), gate='passed' if gate else 'FAILED',
           headline=dict(withdrawn=bystat['WITHDRAWN'], terminated=bystat['TERMINATED'], suspended=bystat['SUSPENDED'], studies=total, share_text='%.1f%%' % (100 * len(R) / total)),
           by_class={c: dict(population=tc.get(c), withdrawn=cls[c]['WITHDRAWN'], terminated=cls[c]['TERMINATED'], suspended=cls[c]['SUSPENDED'], share_text='%.1f%%' % (100 * sum(cls[c].values()) / tc[c]) if tc.get(c) else '') for c in cls},
           reasons={k: dict(n=v, share_text='%.1f%%' % (100 * v / len(R))) for k, v in rc.most_common()},
           tests={'Stopped records with no reason given': dict(wil(len(blank), len(R)), largest_sponsor_n=_top), 'Withdrawn records that list participants enrolled': wil(len(wd_pos), len(wd))},
           by_quarter={k: dict(n=v) for k, v in sorted(q.items())},
           sample_for_hand_check=[dict(id=r['id'], status=r['status'], enrolled=r['enrolled'], sponsor=r['sponsor']) for r in wd_pos[:10]], hand_check=hand)
json.dump(out, open('data/cancelled.json', 'w'), indent=1); print(json.dumps(out['headline']), out['tests'])
