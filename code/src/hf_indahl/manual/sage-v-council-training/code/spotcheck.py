#!/usr/bin/env python3
"""spotcheck.py (Flight Mode v2, item 8): 10 random judged claims from the last 24 h for a person to grade by eye.
Writes spotcheck_<date>.md: claim, seat, p (inside), q (judge), grounded, the quote, and the start of the chunk it cites. Grade each RIGHT / WRONG / CAN'T TELL."""
import json, os, sqlite3, random, time
H = os.path.dirname(os.path.abspath(__file__))
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True)
LIBDB = json.load(open(H + '/local.json')).get('libdb') if os.path.exists(H + '/local.json') else H + '/library.db'
cut = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 86400))
rows = c.execute("select id, triangle, seat, model, claim, quote, chunk, grounded, p, q_judge, judge_why from pq where ts > ?", (cut,)).fetchall()
random.Random(time.strftime('%Y%m%d')).shuffle(rows)
lib = sqlite3.connect(f'file:{LIBDB}?mode=ro', uri=True)
out = [f"# Spot-check {time.strftime('%Y-%m-%d')} · 10 of {len(rows)} judged claims (last 24 h). Grade each: RIGHT / WRONG / CAN'T TELL\n"]
for r in rows[:10]:
    pid, tri, seat, model, claim, quote, chunk, g, p, q, why = r
    t = (lib.execute('select text from chunks where id=?', (chunk,)).fetchone() or [''])[0]
    out.append(f"## pq {pid} · {tri}/{seat} ({model})\n- CLAIM: {claim}\n- inside p = {p} · judge q = {q} · grounded = {bool(g)} · judge: {why}\n- QUOTE: \"{quote}\"\n- CHUNK {chunk}: {t[:600]}\n- GRADE: \n")
open(os.path.join(H, f"spotcheck_{time.strftime('%Y%m%d')}.md"), 'w').write('\n'.join(out)); print(f'{min(10, len(rows))} claims -> spotcheck_{time.strftime("%Y%m%d")}.md')
