#!/usr/bin/env python3
"""TRIALS collector. Reads ClinicalTrials.gov v2 per PLAN.md (+Addendum 1). Writes data/records.jsonl and data/read_at.txt."""
import json, sys, time, urllib.parse, urllib.request, datetime, os
BASE = "https://clinicaltrials.gov/api/v2/studies"
UA = "heuremen-trials/0.1 (+https://indahl.ai/trials)"
today = datetime.date.today()
cut = (today.replace(day=1) - datetime.timedelta(days=1))
m = today.month - 13
y = today.year + (m - 1) // 12
m = (m - 1) % 12 + 1
end = datetime.date(y, m, 1) - datetime.timedelta(days=1)
adv = ("AREA[StudyType]INTERVENTIONAL AND (AREA[IsFDARegulatedDrug]true OR AREA[IsFDARegulatedDevice]true) "
       f"AND AREA[PrimaryCompletionDate]RANGE[2018-01-01,{end.isoformat()}] AND AREA[PrimaryCompletionDateType]ACTUAL")
FIELDS = "NCTId,LeadSponsorName,LeadSponsorClass,Phase,PrimaryCompletionDate,ResultsFirstSubmitDate,ResultsFirstPostDate,IsFDARegulatedDrug,IsFDARegulatedDevice,OverallStatus,HasResults"
params = {"pageSize": "1000", "countTotal": "true", "filter.advanced": adv, "filter.overallStatus": "COMPLETED|TERMINATED", "fields": FIELDS}
os.makedirs("data", exist_ok=True)
out = open("data/records.jsonl.tmp", "w")
tok, n, total = None, 0, None
while True:
    p = dict(params)
    if tok: p["pageToken"] = tok
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA})
    for a in range(5):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=90)); break
        except Exception as e:
            print("retry", a, e, file=sys.stderr); time.sleep(5 * (a + 1))
    else:
        sys.exit("gave up")
    total = d.get("totalCount", total)
    for s in d["studies"]:
        ps = s["protocolSection"]; st = ps.get("statusModule", {}); sp = ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {})
        ov = ps.get("oversightModule", {})
        out.write(json.dumps({
            "nct": ps["identificationModule"]["nctId"], "sponsor": sp.get("name"), "class": sp.get("class"),
            "phases": ps.get("designModule", {}).get("phases", []),
            "pcd": st.get("primaryCompletionDateStruct", {}).get("date"),
            "submit": st.get("resultsFirstSubmitDate"), "post": (st.get("resultsFirstPostDateStruct") or {}).get("date"),
            "drug": bool(ov.get("isFdaRegulatedDrug")), "device": bool(ov.get("isFdaRegulatedDevice")),
            "status": st.get("overallStatus"), "has": bool(s.get("hasResults"))}) + "\n")
        n += 1
    tok = d.get("nextPageToken")
    print(n, "/", total, flush=True)
    if not tok: break
    time.sleep(0.5)
out.close()
os.replace("data/records.jsonl.tmp", "data/records.jsonl")
open("data/read_at.txt", "w").write(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + f"\ncutoff_pcd={end}\ntotal={total}\n")
