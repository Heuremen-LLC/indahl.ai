"""fetch_job1.py -- zero QPU: pulls job dbeecdvgdj9s73flkcn0's results, metrics and the backend record at its creation time from IBM,
because the duplicate attempt (another seat, 13:44 EDT) overwrote raw/job/props files in the run folder.  Writes job1_dbeecdvgdj9s73flkcn0/."""
import sys, os, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); RUN = os.path.dirname(HERE); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
from fire import build, CHIP
JID = 'dbeecdvgdj9s73flkcn0'; OUT = f'{RUN}/job1_{JID}'
s = service(); job = s.job(JID); b = s.backend(CHIP); res = job.result(); mt = job.metrics(); circs, meta = build()
raw = [dict(m, counts={str(k): int(v) for k, v in pr.data.meas.get_counts().items()}) for m, pr in zip(meta, res)]
json.dump(raw, open(f'{OUT}/raw_2603.13536.json', 'w'))
j2 = json.load(open(f'{RUN}/job2_dbeesuom94ac738rmbs0/job_2603.13536.json'))
rec = {k: v for k, v in j2.items() if k not in ('attempts', 'next_attempt', 'remaining_before')}
rec['attempts'] = [dict(attempt=1, job_id=JID, submitted_utc='2026-10-24T17:09:12Z', status=str(job.status()), usage=mt.get('usage'), timestamps=mt.get('timestamps'))]
rec['remaining_before'] = 2701; rec['note'] = 'rebuilt from IBM job record by fetch_job1.py; ring/meta/circuit hash identical to job 2 (same committed code, same ring printed in both logs)'
json.dump(rec, open(f'{OUT}/job_2603.13536.json', 'w'), default=str)
t = datetime.datetime(2026, 10, 24, 17, 9, 0, tzinfo=datetime.timezone.utc)
json.dump(b.properties(datetime=t).to_dict(), open(f'{OUT}/props_2603.13536_before_1.json', 'w'), default=str)
print(JID, job.status(), mt.get('usage', {}).get('qpu_charge_time_seconds'), mt.get('timestamps'), 'pubs', len(raw))
