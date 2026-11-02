#!/usr/bin/env python3
"""iris_check.py -- IRIS Research Package, Heuremen LLC (https://indahl.ai/iris). Standard library only. Python 3.9 or later.

Checks that run on your own released model outputs (a JSONL file with one reply per line), before you trust a rate and when you compare two
runs. Your files are opened read-only and are never changed. Their sha256 is taken before and after and printed in the report. Reports go to a
separate folder (default ./heuremen_report/) that may not be inside a folder that holds an input. It sends nothing anywhere.

  SAMPLE   python iris_check.py sample RUN.jsonl --reply-field reply --extracted-field pred [--label-field family] [--id-field id] [-n 10] [--seed 1]
           Writes a reading sheet (HTML and CSV): n random replies per label, each beside what your parser extracted. Read the replies, mark the
           ones the parser got wrong in the misparsed column of the CSV, then run
           python iris_check.py sample --tally SHEET.csv
           Our rule: if more than 1 of 10 read replies is mis-parsed, that label's rate is "cannot tell (parser)".

  REPEAT   python iris_check.py repeat RUN1.jsonl RUN2.jsonl [RUN3.jsonl ...] --id-field id --correct-field correct
           python iris_check.py repeat A1.jsonl A2.jsonl --vs B1.jsonl B2.jsonl --id-field id --correct-field correct [--margin 0.02]
           Runs of the same items are matched by item id. The files before --vs are system A, the files after it are system B. For each system
           with two or more runs it counts the per-item flips in each direction between every pair of runs (right to wrong, wrong to right) and
           reports the repeat floor, the share of items that flip between repeats, beside the net change. With --vs it compares A with B,
           run 1 of each, run 2 of each, and so on: exact two-sided McNemar (sign) test on the discordant items, and a bootstrap 95% interval
           (seeded, 2000 resamples) for the accuracy difference A minus B. Outcome:
           ABOVE if the low end of the interval is above 0, BELOW if the high end is below 0, CONSISTENT if the whole interval is within
           plus or minus the margin (default 0.02), otherwise CANNOT_TELL.
           The correct field holds true/false, 1/0, yes/no or correct/incorrect.

The checks read the files you give them only. They make no claim about your results. Free to run and cite with attribution; see LICENSE.txt."""
import json, sys, os, csv, hashlib, argparse, html, random, itertools, datetime as dt
from math import comb
UTC = dt.timezone.utc
NAME = 'IRIS Research Package'; ORG = 'Heuremen LLC'; SITE = 'https://indahl.ai/iris'
LOGO = ('<svg viewBox="0 0 200 200" width="44" height="44" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="9">'
        '<polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5" fill="currentColor"/></svg>')
TRUE = {'true', '1', 'yes', 'correct', 't', 'y'}; FALSE = {'false', '0', 'no', 'incorrect', 'f', 'n'}

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def die(msg): sys.exit('iris_check: ' + msg)
def dig(row, path):
    cur = row
    for k in path.split('.'):
        if not isinstance(cur, dict) or k not in cur: return None, False
        cur = cur[k]
    return cur, True
def text(v): return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
def read_jsonl(p):
    rows = []
    with open(p, 'r', encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            if not line.strip(): continue
            try: r = json.loads(line)
            except json.JSONDecodeError: die(f'{p} line {n} is not JSON')
            if not isinstance(r, dict): die(f'{p} line {n} is not a JSON object')
            rows.append((n, r))
    if not rows: die(p + ' has no rows')
    return rows
def guard_out(out, inputs):
    od = os.path.realpath(out)
    for p in inputs:
        d = os.path.dirname(os.path.realpath(p))
        if od == d or od.startswith(d + os.sep): die(f'--out ({out}) is inside the folder of an input ({d}). Give --out a folder outside it.')

def page(title, meta, sections, inputs):
    css = ('body{font:16px/1.5 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:900px;margin:0 auto;padding:24px 16px}'
           'header{display:flex;gap:12px;align-items:center;border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:22px}'
           'table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #d8ccb4;padding:4px 6px;text-align:left;vertical-align:top}'
           'td.r{white-space:pre-wrap;word-break:break-word}.note{color:#5a4d3a;font-size:14px}footer{margin-top:28px;border-top:1px solid #d8ccb4;padding-top:10px;font-size:13px;color:#5a4d3a}')
    h = [f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style><main>',
         f'<header>{LOGO}<div><b>{NAME}</b><br><span class="note">{ORG} &middot; <a href="{SITE}">{SITE}</a></span></div></header>', f'<h1>{html.escape(title)}</h1>']
    h += [f'<p class="note">{html.escape(m)}</p>' for m in meta]
    for st, rows, cols in sections:
        h.append(f'<h2>{html.escape(st)}</h2>')
        if not rows: h.append('<p>Nothing to show.</p>'); continue
        h.append('<table><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in cols) + '</tr>' + ''.join(
            '<tr>' + ''.join(f'<td class="{"r" if c in ("reply", "extracted") else ""}">{html.escape(str(r.get(c, "")))}</td>' for c in cols) + '</tr>' for r in rows) + '</table>')
    h.append('<footer>Your files were opened read-only and not changed. sha256 before and after:<br>' + '<br>'.join(
        f'{html.escape(os.path.basename(p))}: {a[:16]}&hellip; / {b[:16]}&hellip; {"unchanged" if a == b else "CHANGED"}' for p, a, b in inputs) +
        f'<br>These checks read the files you gave them only and make no claim about your results. {ORG}, {SITE}</footer></main></html>')
    return '\n'.join(h)
def write(out, stem, title, meta, sections, inputs, data, csv_rows=None, csv_cols=None):
    os.makedirs(out, exist_ok=True); t = dt.datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ'); paths = {}
    paths['html'] = os.path.join(out, f'{stem}_{t}.html')
    with open(paths['html'], 'w', encoding='utf-8') as f: f.write(page(title, meta, sections, inputs))
    paths['json'] = os.path.join(out, f'{stem}_{t}.json')
    with open(paths['json'], 'w', encoding='utf-8') as f:
        json.dump(dict(package=NAME, by=ORG, site=SITE, title=title, meta=meta, inputs=[dict(file=os.path.basename(p), sha256_before=a, sha256_after=b) for p, a, b in inputs], **data), f, indent=1, default=str)
    if csv_rows is not None:
        paths['csv'] = os.path.join(out, f'{stem}_{t}.csv')
        with open(paths['csv'], 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=csv_cols); w.writeheader(); w.writerows(csv_rows)
    return paths

# ---------- sample ----------
RULE = 'Our rule: if more than 1 of 10 read replies is mis-parsed, that label\'s rate is "cannot tell (parser)".'
def mark(v): return bool(v.strip()) and v.strip().lower() not in ('0', 'no', 'n', 'false', 'ok', 'f')
def cmd_sample(a):
    if a.tally:
        a.out = a.out or 'heuremen_report_tally'   # the sheet itself sits in heuremen_report, so the tally goes beside it, not inside it
        if a.run: die('give either RUN.jsonl or --tally SHEET.csv, not both')
        h0 = sha(a.tally); guard_out(a.out, [a.tally])
        with open(a.tally, 'r', encoding='utf-8', newline='') as f: rows = list(csv.DictReader(f))
        if not rows or not {'label', 'id', 'misparsed'} <= set(rows[0]): die(a.tally + ' is not a reading sheet written by the sample command (needs label, id, misparsed columns)')
        by = {}
        for r in rows: by.setdefault(r['label'], []).append(r)
        res = []
        for lab, rs in by.items():
            bad = sum(mark(r['misparsed']) for r in rs)
            res.append(dict(label=lab, replies_read=len(rs), misparsed=bad, reading='cannot tell (parser)' if bad * 10 > len(rs) else 'rate can be read'))
        meta = [RULE, 'A label is "cannot tell (parser)" when the mis-parsed count is more than one tenth of the replies read. A blank in the misparsed column counts as read and correct.']
        paths = write(a.out, 'tally', 'Parser check tally', meta, [('Per label', res, ['label', 'replies_read', 'misparsed', 'reading'])], [(a.tally, h0, sha(a.tally))], dict(tally=res))
        for r in res: print(f"{r['label']}: {r['misparsed']} of {r['replies_read']} mis-parsed -> {r['reading']}")
        print(NAME, '|', ORG, '|', SITE); print('report:', paths['html']); print('data:  ', paths['json']); return
    a.out = a.out or 'heuremen_report'
    if not a.run or not a.reply_field or not a.extracted_field: die('sample needs RUN.jsonl, --reply-field and --extracted-field (or --tally SHEET.csv)')
    if a.n < 1: die('-n must be 1 or more')
    guard_out(a.out, [a.run]); h0 = sha(a.run); rows = read_jsonl(a.run); groups = {}; missing = 0
    for ln, r in rows:
        rep, ok1 = dig(r, a.reply_field); ext, ok2 = dig(r, a.extracted_field)
        if not (ok1 and ok2): missing += 1; continue
        lab = text(dig(r, a.label_field)[0]) if a.label_field and dig(r, a.label_field)[1] else ('(no label)' if a.label_field else 'all')
        rid = text(dig(r, a.id_field)[0]) if a.id_field and dig(r, a.id_field)[1] else f'line {ln}'
        groups.setdefault(lab, []).append(dict(label=lab, id=rid, reply=text(rep), extracted=text(ext)))
    if not groups: die(f'no row has both fields {a.reply_field!r} and {a.extracted_field!r}')
    sheet, sections, summary = [], [], []
    for lab in sorted(groups):
        g = groups[lab]; pick = random.Random(f'{a.seed}:{lab}').sample(g, min(a.n, len(g)))
        for r in pick: r['misparsed'] = ''
        sheet += pick; summary.append(dict(label=lab, replies_in_run=len(g), replies_sampled=len(pick)))
        sections.append((f'{lab}: {len(pick)} of {len(g)} replies', pick, ['id', 'reply', 'extracted', 'misparsed']))
    meta = [f'{a.run}: seed {a.seed}, up to {a.n} replies per label.', RULE,
            'Read each reply, compare it with the extracted value, and write x in the misparsed column of the CSV where they disagree. Then run the sample command with --tally and the CSV.'] + (
           [f'{missing} rows lacked one of the two fields and are not in the sample.'] if missing else [])
    cols = ['label', 'id', 'reply', 'extracted', 'misparsed']
    paths = write(a.out, 'sample', 'Reading sheet: replies beside what the parser extracted', meta, [('Labels', summary, ['label', 'replies_in_run', 'replies_sampled'])] + sections,
                  [(a.run, h0, sha(a.run))], dict(seed=a.seed, n=a.n, labels=summary), csv_rows=sheet, csv_cols=cols)
    print(NAME, '|', ORG, '|', SITE); print('sheet:', paths['html']); print('csv:  ', paths['csv']); print('data: ', paths['json'])

# ---------- repeat ----------
def to_bool(v, where):
    if isinstance(v, bool): return v
    s = str(v).strip().lower()
    if s in TRUE: return True
    if s in FALSE: return False
    die(f'{where}: the correct field holds {v!r}, which is not true/false, 1/0, yes/no or correct/incorrect')
def load_run(p, idf, cf):
    out = {}
    for ln, r in read_jsonl(p):
        i, ok1 = dig(r, idf); c, ok2 = dig(r, cf)
        if not (ok1 and ok2): die(f'{p} line {ln}: needs both {idf!r} and {cf!r}')
        k = text(i)
        if k in out: die(f'{p} line {ln}: item id {k!r} appears twice')
        out[k] = to_bool(c, f'{p} line {ln}')
    return out
def mcnemar_exact(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
def compare(x, y, ids, margin, boots, seed):
    n = len(ids); xa = [x[i] for i in ids]; ya = [y[i] for i in ids]
    b = sum(p and not q for p, q in zip(xa, ya)); c = sum(q and not p for p, q in zip(xa, ya)); d = (b - c) / n
    rng = random.Random(seed); cw = [b / n, (b + c) / n, 1.0]; diffs = []
    for _ in range(boots):
        s = rng.choices((1, -1, 0), cum_weights=cw, k=n); diffs.append(sum(s) / n)
    diffs.sort(); lo, hi = diffs[int(0.025 * boots)], diffs[min(boots - 1, int(0.975 * boots))]
    out = 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT' if (lo >= -margin and hi <= margin) else 'CANNOT_TELL'
    return dict(n_items=n, acc_A=round(sum(xa) / n, 4), acc_B=round(sum(ya) / n, 4), A_right_B_wrong=b, A_wrong_B_right=c, diff_A_minus_B=round(d, 4),
                ci95_low=round(lo, 4), ci95_high=round(hi, 4), mcnemar_exact_p=round(mcnemar_exact(b, c), 6), margin=margin, outcome=out)
def flips(runs, ids, names):
    rows = []
    for (i, ra), (j, rb) in itertools.combinations(enumerate(runs), 2):
        rw = sum(ra[k] and not rb[k] for k in ids); wr = sum(rb[k] and not ra[k] for k in ids)
        rows.append(dict(run_a=names[i], run_b=names[j], right_to_wrong=rw, wrong_to_right=wr, net=wr - rw, items_flipped=rw + wr, repeat_floor=round((rw + wr) / len(ids), 4)))
    return rows
def cmd_repeat(a):
    A = a.runs; B = a.vs or []
    if not B and len(A) < 2: die('give two or more runs, or one or more runs of A and --vs runs of B')
    allp = A + B; guard_out(a.out, allp); h0 = {p: sha(p) for p in allp}
    if len(set(os.path.realpath(p) for p in allp)) != len(allp): die('the same file was given twice')
    R = {p: load_run(p, a.id_field, a.correct_field) for p in allp}
    ids = set.intersection(*[set(R[p]) for p in allp]); union = set.union(*[set(R[p]) for p in allp])
    if not ids: die('no item id is in every run')
    ids = sorted(ids); meta = [f'Items matched by id across all runs: {len(ids)}. Items in some run but not in all, left out: {len(union) - len(ids)}.']
    sections = []; data = dict(items=len(ids), left_out=len(union) - len(ids))
    for nm, S in (('A', A), ('B', B)):
        if len(S) < 2: continue
        names = [os.path.basename(p) for p in S]; rows = flips([R[p] for p in S], ids, names)
        sections.append((f'System {nm}: flips between repeats and the repeat floor', rows, ['run_a', 'run_b', 'right_to_wrong', 'wrong_to_right', 'net', 'items_flipped', 'repeat_floor']))
        data['repeat_' + nm] = rows
        accs = [dict(run=n, accuracy=round(sum(R[p][k] for k in ids) / len(ids), 4)) for n, p in zip(names, S)]
        sections.append((f'System {nm}: accuracy per run', accs, ['run', 'accuracy'])); data['accuracy_' + nm] = accs
        meta.append(f'System {nm}: the repeat floor is the share of items whose right or wrong flips between two runs of the same system. Net change is wrong to right minus right to wrong.')
    if B:
        m = min(len(A), len(B)); comp = []
        for k in range(m):
            c = compare(R[A[k]], R[B[k]], ids, a.margin, a.boot, a.seed); c['pair'] = f'{os.path.basename(A[k])} vs {os.path.basename(B[k])}'; comp.append(c)
        if len(A) != len(B): meta.append(f'A has {len(A)} runs and B has {len(B)}. Compared run by run for the first {m}.')
        sections.append(('A against B, run by run (difference is A minus B)', comp, ['pair', 'n_items', 'acc_A', 'acc_B', 'A_right_B_wrong', 'A_wrong_B_right', 'diff_A_minus_B', 'ci95_low', 'ci95_high', 'mcnemar_exact_p', 'outcome']))
        data['comparison'] = comp
        meta.append(f'Outcome rule with margin {a.margin}: ABOVE if the low end of the 95% interval is above 0, BELOW if the high end is below 0, CONSISTENT if the whole interval is within plus or minus {a.margin}, otherwise CANNOT_TELL. Bootstrap: {a.boot} resamples of items, seed {a.seed}.')
    paths = write(a.out, 'repeat', 'Repeat floor and paired comparison', meta, sections, [(p, h0[p], sha(p)) for p in allp], data)
    for nm in ('A', 'B'):
        for r in data.get('repeat_' + nm, []): print(f"{nm}: {r['run_a']} vs {r['run_b']}: right->wrong {r['right_to_wrong']}, wrong->right {r['wrong_to_right']}, net {r['net']:+d}, repeat floor {r['repeat_floor']:.4f}")
    for c in data.get('comparison', []): print(f"A vs B: diff {c['diff_A_minus_B']:+.4f} [{c['ci95_low']:+.4f}, {c['ci95_high']:+.4f}] discordant {c['A_right_B_wrong']}/{c['A_wrong_B_right']} p={c['mcnemar_exact_p']} -> {c['outcome']}")
    print(NAME, '|', ORG, '|', SITE); print('report:', paths['html']); print('data:  ', paths['json'])

def main():
    ap = argparse.ArgumentParser(description=NAME + ', ' + ORG); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sample', help='reading sheet of replies beside the parser output'); s.add_argument('run', nargs='?'); s.add_argument('--reply-field'); s.add_argument('--extracted-field')
    s.add_argument('--label-field'); s.add_argument('--id-field'); s.add_argument('-n', type=int, default=10); s.add_argument('--seed', default='1'); s.add_argument('--tally', metavar='SHEET.csv'); s.add_argument('--out')
    r = sub.add_parser('repeat', help='flips between repeats, repeat floor, paired comparison'); r.add_argument('runs', nargs='+'); r.add_argument('--vs', nargs='+'); r.add_argument('--id-field', required=True)
    r.add_argument('--correct-field', required=True); r.add_argument('--margin', type=float, default=0.02); r.add_argument('--boot', type=int, default=2000); r.add_argument('--seed', type=int, default=20261101); r.add_argument('--out', default='heuremen_report')
    a = ap.parse_args(); cmd_sample(a) if a.cmd == 'sample' else cmd_repeat(a)
if __name__ == '__main__': main()
