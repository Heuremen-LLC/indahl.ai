#!/usr/bin/env python3
"""score_errata.py -- STAN-E leaderboard (12 Nov 2026). Grades every local-model errata run (out_*.jsonl) against two-reader verified
SAGAR rows (sagar/index/verified.jsonl PRESENT F5/F6 + verified_auto.jsonl). Paper-level: a model flags a paper if any chunk lists an
error; a hit is a flagged paper that has a verified F5 or F6 finding AND the model quoted a number that appears in the verified evidence.
Writes leaderboard.json. Rider on the tick bus; cheap."""
import json, os, re, glob, math
E = os.path.dirname(os.path.abspath(__file__)); I = '/Users/heuremen/bones-forge/sagar/index'
def rows(f): return [json.loads(l) for l in open(f) if l.strip()] if os.path.exists(f) else []
ver = {}
for v in rows(I + '/verified.jsonl'):
    if v.get('bones') == 'PRESENT' and v['code'][:2] in ('F5', 'F6'): ver.setdefault(v['arxiv'], '') ; ver[v['arxiv']] += ' ' + v['basis']
for v in rows(I + '/verified_auto.jsonl'):
    if v['code'] in ('F5', 'F6'): ver.setdefault(v['arxiv'], ''); ver[v['arxiv']] += ' ' + (v.get('draft_quote') or '') + ' ' + json.dumps(v.get('reader_quotes'))
nums = lambda s: set(re.findall(r'\d+\.\d+|\d{2,}', s or ''))
def wil(k, n):
    if not n: return None
    z = 1.96; p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [round(max(0, c - h), 3), round(min(1, c + h), 3)]
board = []
for f in sorted(glob.glob(E + '/out_*.jsonl')):
    R = rows(f); papers = {r['arxiv'] for r in R}; flagged = {}
    for r in R:
        if r.get('errors'): flagged.setdefault(r['arxiv'], []).extend(r['errors'])
    pos = [p for p in papers if p in ver]
    hits = [p for p in pos if p in flagged and (nums(json.dumps(flagged[p])) & nums(ver[p]))]
    board.append({'run': os.path.basename(f)[4:-6], 'papers_seen': len(papers), 'chunks': len(R), 'papers_flagged': len(flagged),
                  'verified_positive_papers_seen': len(pos), 'hits': len(hits), 'recall': [len(hits), len(pos), wil(len(hits), len(pos))],
                  'flag_rate': [len(flagged), len(papers), wil(len(flagged), len(papers))],
                  'parse_fail': sum(1 for r in R if r.get('errors') is None), 'hit_papers': hits})
board.sort(key=lambda b: (-(b['hits'] / b['verified_positive_papers_seen'] if b['verified_positive_papers_seen'] else 0), b['papers_flagged']))
json.dump({'verified_positive_papers': len(ver), 'board': board}, open(E + '/leaderboard.json', 'w'), indent=1)
for b in board: print(b['run'], 'recall', b['recall'][:2], b['recall'][2], '| flagged', b['flag_rate'][:2], '| parse_fail', b['parse_fail'])
