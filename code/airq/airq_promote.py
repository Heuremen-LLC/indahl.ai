#!/usr/bin/env python3
"""airq_promote.py (addendum 4, 9 Nov 2026): puts the newest window's read at the top of summary_airq.json and keeps the 2025 read as the previous reading. The live block written by airq_live_tick.py is kept as it is."""
import os, json, fcntl
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
_l = open('data/.live.lock', 'w'); fcntl.flock(_l, fcntl.LOCK_EX)   # the live tick reads and writes summary_airq.json under the same lock
new = json.load(open('summary_airq_w2026.json')); old = json.load(open('summary_airq_w2025.json')); S = json.load(open('summary_airq.json'))
top = dict(new); top['source_line'] = new.get('source_line', '')
top['previous'] = {k: old[k] for k in ('updated', 'window', 'monitors_read', 'monitors_with_sensor', 'sensors', 'pairs', 'days_kept', 'days_removed_ab', 'comparison', 'medians', 'headline')}
for k in ('live', 'live_line'):
    if k in S: top[k] = S[k]
json.dump(top, open('summary_airq.json', 'w'), indent=1); print('airq-promote: top', top['window'], '| previous', old['window'])
