#!/usr/bin/env python3
"""assemble.py: turns the refereed research files into log rows.
  python3 assemble.py draft   -> data/draft_rows.json (nothing written to the log; the referee reads this)
  python3 assemble.py commit  -> appends the draft rows to data/log.jsonl (refused if the log already has entries) and stamps it
Drops listed in data/research/drop.json ({"short_id or lb_number": "why"}) are left out and counted. Fixes the referee asks for are made in the
research files before commit, so the first log rows already carry them."""
import os, sys, json, time, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import now_log as NL
RS = os.path.join(H, 'data', 'research')
NOW = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); NOWD = D.datetime.now(D.timezone.utc)


def j(f, d=None):
    p = os.path.join(RS, f)
    return json.load(open(p)) if os.path.exists(p) else d


def dl(s):
    if not s: return None
    if len(s) == 10: return D.datetime.fromisoformat(s).replace(hour=23, minute=59, second=59, tzinfo=D.timezone.utc)
    return D.datetime.fromisoformat(s.replace('Z', '+00:00'))


DROP = j('drop.json', {}) or {}
import re as _re
def plain(t):
    """Our own words keep the house copy rule: no semicolons (a semicolon becomes a full stop)."""
    if not isinstance(t, str): return t
    return _re.sub(r';\s*(\w)', lambda m: '. ' + m.group(1).upper(), t)
rows, nid, dropped = [], [0], []


def add(set_, it, kind=None, extra=None):
    key = str(it.get('short_id') or it.get('lb_number') or it.get('id'))
    if key in DROP or ('%s:%s' % (set_, key)) in DROP: dropped.append((set_, key, DROP.get(key) or DROP.get('%s:%s' % (set_, key)))); return
    nid[0] += 1; eid = 'NOW-%04d' % nid[0]
    k = kind or it.get('kind') or ('probability' if isinstance(it.get('probability'), (int, float)) else 'binary')
    d = it.get('deadline')
    e = dict(kind='entry', id=eid, set=set_, ref=key, who=it.get('who'), who_kind=it.get('who_kind'), speaker=it.get('speaker'), role=it.get('role'),
             quote=it.get('quote'), source_url=it.get('source_url'), source_title=it.get('source_title'), source_kind=it.get('source_kind'), outlet=it.get('outlet'),
             archive_url=it.get('archive_url'), archive_date=it.get('archive_date'), said=it.get('said'), deadline=d, event=plain(it.get('event')), criterion=plain(it.get('criterion')),
             criterion_written=NOW, criterion_before_deadline=bool(d and dl(d) > NOWD), probability=it.get('probability'), kind_of_claim=k, topic=it.get('topic'),
             raw_file=it.get('raw_file'))
    e['kind_of_claim'] = k
    if extra: e.update(extra)
    rows.append(e)
    rd = it.get('reading') or {}
    if k != 'pdoom' and rd.get('outcome') and d and dl(d) <= NOWD:
        rows.append(dict(kind='outcome', entry=eid, outcome=rd['outcome'], read_by=it.get('read_by', 'Bones, checked by the referee'), evidence=[dict(v, what=plain(v.get('what'))) for v in (rd.get('evidence') or [])], reason=plain(rd.get('reason', ''))))


for it in j('longbets.json', []):
    if it.get('said_note') and str(it.get('said', '')).endswith('-01-01'): it = dict(it, said=it['said'][:4])   # Long Bets prints the start year only
    add('longbets', it, 'binary', dict(challenger=it.get('challenger'), stake=it.get('stake'), lb_result=it.get('lb_result'), lb_type=it.get('lb_type')))
for it in j('onrecord.json', []): add('onrecord', it, 'binary')
for it in j('ai.json', []): add('ai', it)
mr = j('manifold_resolved.json', {'rows': []})
for m in mr['rows']:
    add('manifold_resolved', dict(id=m['id'], who='Manifold market (community forecast)', who_kind='community forecast', quote=m['question'], source_url=m['url'], source_kind='platform record',
                                  said=m['stated_at'], deadline=m['reference'], event=m['question'], criterion="Resolves as the market's creator resolves it under the market's own description.",
                                  probability=m['probability'], topic='AI', raw_file='data/raw/manifold/bets_%s_*.json' % m['id'],
                                  reading=dict(outcome='HAPPENED' if m['resolution'] == 'YES' else 'DID_NOT_HAPPEN', evidence=[dict(url=m['url'], what='market resolved %s at %s' % (m['resolution'], m['resolution_time']))],
                                               reason='the market resolved %s' % m['resolution']), read_by='Manifold API, resolved set'),
        'probability', dict(platform_id=m['id'], bettors=m['bettors'], last_bet_before=m['last_bet_before']))
mo = j('manifold_open.json', {'rows': []})
for m in mo['rows']:
    add('manifold_open', dict(id=m['id'], who='Manifold market (community forecast)', who_kind='community forecast', quote=m['question'], source_url=m['url'], source_kind='platform record',
                              said=m['read_at'], deadline=m['close'], event=m['question'], criterion="Resolves as the market's creator resolves it under the market's own description.",
                              probability=m['probability'], topic='AI', raw_file='data/raw/manifold/market_%s.json' % m['id']),
        'probability', dict(platform_id=m['id'], bettors=m['bettors']))

# the log's own field for the claim kind is 'kind' on the entry view; the row kind stays 'entry'
for r in rows:
    if r['kind'] == 'entry': r['claim'] = r.pop('kind_of_claim')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'draft'
    json.dump(rows, open(os.path.join(H, 'data', 'draft_rows.json'), 'w'), indent=1, ensure_ascii=False)
    ne = sum(1 for r in rows if r['kind'] == 'entry'); no = sum(1 for r in rows if r['kind'] == 'outcome')
    print('entries', ne, 'outcome rows', no, 'dropped', len(dropped))
    for d in dropped: print('  dropped', *d)
    F = j('fortune.json', [])
    for f in F:
        f['summary'] = plain(f.get('summary'))
        if f.get('primary'): f['primary']['note'] = plain(f['primary'].get('note'))
        if f.get('landed'): f['landed']['record'] = plain(f['landed'].get('record'))
    F = [f for f in F if ('fortune:' + str(f.get('short_id'))) not in DROP]
    json.dump(F, open(os.path.join(H, 'data', 'fortune_draft.json'), 'w'), indent=1, ensure_ascii=False); print('fortune', len(F))
    if mode == 'commit':
        import shutil; shutil.copy2(os.path.join(H, 'data', 'fortune_draft.json'), os.path.join(H, 'data', 'fortune.json'))
        if any(r['kind'] == 'entry' for r in NL.load()): raise SystemExit('the log already has entries: new entries go in with a new assemble run that skips them')
        print('appended', NL.append(rows), 'stamp', NL.stamp())
