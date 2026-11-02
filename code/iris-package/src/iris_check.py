#!/usr/bin/env python3
"""iris_check.py -- IRIS Research Package, Heuremen LLC (https://indahl.ai/iris). Standard library only. Python 3.9 or later.

Checks that run on your own released model outputs (a JSONL file with one reply per line), before you trust a rate and when you compare two
runs. Your files are opened read-only and are never changed. Their sha256 is taken before and after and printed in the report. Reports go to a
separate folder (default ./heuremen_report/) that may not be inside a folder that holds an input, so run from outside your data folder.
It sends nothing anywhere.

  SAMPLE   python iris_check.py sample RUN.jsonl --reply-field reply --extracted-field pred [--label-field family] [--id-field id] [-n 10] [--seed 1]
           Writes a reading sheet (HTML and CSV): n random replies per label, each beside what your parser extracted. Read each reply, write x
           in the read column, and write x in the misparsed column where the extracted value is not the answer the reply gives (parse fine: ok, y,
           yes, 0, no, n, false, f or blank. Mis-parsed: x, bad, 1, wrong). Then run
           python iris_check.py sample --tally SHEET.csv
           Rule: a label reads "cannot tell (not read)" if any row is unread, otherwise "cannot tell (parser)" when more than 10% of its read
           rows are mis-parsed (1 of 10 is fine, 2 of 10 is not, 1 of 9 is not), otherwise "rate can be read".

  REPEAT   python iris_check.py repeat RUN1.jsonl RUN2.jsonl [RUN3.jsonl ...] --id-field id --correct-field correct
           python iris_check.py repeat A1.jsonl A2.jsonl --vs B1.jsonl B2.jsonl --id-field id --correct-field correct [--margin 0.02]
           Item ids are turned into strings first (2 and 2.0 and "2" are one id). Each pair of runs is compared on the items both hold.
           For every pair of runs of one system it counts the per-item flips in each direction (right to wrong, wrong to right) and reports the
           repeat floor, the share of matched items that flip. There is one row per pair and no combined floor over three or more runs.
           With --vs, run k of A (command-line order) is paired with run k of B. Each pair gets an exact two-sided McNemar test on the discordant
           items and a seeded bootstrap 95% interval (2000 resamples) for the accuracy difference A minus B. Outcome, in this order:
           ABOVE if the interval's low end is above 0 and the McNemar p is below 0.05. BELOW if the high end is below 0 and p is below 0.05.
           If only one of the two says different, CANNOT_TELL. Then CONSISTENT if the whole interval is within plus or minus the margin
           (default 0.02), but only with at least 20 matched items and at least 1 discordant item. Otherwise CANNOT_TELL.
           ABOVE and BELOW are checked before CONSISTENT, so a resolved difference inside the margin reads ABOVE or BELOW.
           The correct field holds true/false, 1/0, yes/no or correct/incorrect.

The checks read the files you give them only. They make no claim about your results. Free to run and cite with attribution; see LICENSE.txt."""
import json, sys, os, csv, hashlib, argparse, html, random, itertools, math, datetime as dt
from math import comb
UTC = dt.timezone.utc
NAME = 'IRIS Research Package'; ORG = 'Heuremen LLC'; SITE = 'https://indahl.ai/iris'
LOGO = ('<svg viewBox="0 0 200 200" width="44" height="44" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="9">'
        '<polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5" fill="currentColor"/></svg>')
TRUE = {'true', '1', 'yes', 'correct', 't', 'y'}; FALSE = {'false', '0', 'no', 'incorrect', 'f', 'n'}
FINE = {'ok', 'y', 'yes', '0', 'no', 'n', 'false', 'f'}; BAD = {'x', 'bad', '1', 'wrong'}
MIN_ITEMS = 20; WARN_DROP = 0.05; EXACT_UP_TO = 2000

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
def norm_id(v):
    """ids become strings first: 2, 2.0 and "2" are one id"""
    if isinstance(v, bool): return str(v)
    if isinstance(v, int): return str(v)
    if isinstance(v, float): return str(int(v)) if v.is_integer() else repr(v)
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, sort_keys=True)
def read_jsonl(p):
    rows, blank = [], 0
    with open(p, 'r', encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            if not line.strip(): blank += 1; continue
            try: r = json.loads(line)
            except json.JSONDecodeError: die(f'{p} line {n} is not JSON')
            if not isinstance(r, dict): die(f'{p} line {n} is not a JSON object')
            rows.append((n, r))
    if not rows: die(p + ' has no rows')
    return rows, blank
def guard_out(out, inputs):
    if os.path.exists(out) and not os.path.isdir(out): die(f'--out ({out}) is a file. Give --out a folder.')
    od = os.path.realpath(out)
    for p in inputs:
        d = os.path.dirname(os.path.realpath(p))
        if od == d or od.startswith(d + os.sep): die(f'--out ({out}) is inside the folder of an input ({d}). Run from outside the data folder or give --out a folder outside it.')
def safe_cell(v):
    """spreadsheet programs run a cell that starts with = + - @ tab or CR as a formula, so a single quote goes in front"""
    v = '' if v is None else str(v)
    return "'" + v if v[:1] in ('=', '+', '-', '@', '\t', '\r') else v

def page(title, meta, sections, inputs, warnings=()):
    css = ('body{font:16px/1.5 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:900px;margin:0 auto;padding:24px 16px}'
           'header{display:flex;gap:12px;align-items:center;border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:22px}'
           'table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #d8ccb4;padding:4px 6px;text-align:left;vertical-align:top}'
           'td.r{white-space:pre-wrap;word-break:break-word}.note{color:#5a4d3a;font-size:14px}.warn{border:2px solid #9a2a1a;background:#f9e3dc;padding:8px 12px;font-weight:bold}'
           'footer{margin-top:28px;border-top:1px solid #d8ccb4;padding-top:10px;font-size:13px;color:#5a4d3a}')
    h = [f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style><main>',
         f'<header>{LOGO}<div><b>{NAME}</b><br><span class="note">{ORG} &middot; <a href="{SITE}">{SITE}</a></span></div></header>', f'<h1>{html.escape(title)}</h1>']
    h += [f'<p class="warn">WARNING: {html.escape(w)}</p>' for w in warnings]
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
def write(out, stem, title, meta, sections, inputs, data, csv_rows=None, csv_cols=None, warnings=()):
    os.makedirs(out, exist_ok=True); t = dt.datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ'); paths = {}
    paths['html'] = os.path.join(out, f'{stem}_{t}.html')
    with open(paths['html'], 'w', encoding='utf-8') as f: f.write(page(title, meta, sections, inputs, warnings))
    paths['json'] = os.path.join(out, f'{stem}_{t}.json')
    with open(paths['json'], 'w', encoding='utf-8') as f:
        json.dump(dict(package=NAME, by=ORG, site=SITE, title=title, meta=meta, warnings=list(warnings), inputs=[dict(file=os.path.basename(p), sha256_before=a, sha256_after=b) for p, a, b in inputs], **data), f, indent=1, default=str)
    if csv_rows is not None:
        paths['csv'] = os.path.join(out, f'{stem}_{t}.csv')
        with open(paths['csv'], 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=csv_cols); w.writeheader(); w.writerows([{k: safe_cell(r.get(k, '')) for k in csv_cols} for r in csv_rows])
    return paths

# ---------- sample ----------
RULE = ('Rule: a label reads "cannot tell (not read)" if any of its rows is unread. Otherwise it reads "cannot tell (parser)" when more than 10% of its read rows '
        'are mis-parsed (1 of 10 is fine, 2 of 10 is not, 1 of 9 is not). Otherwise the rate can be read.')
def verdict(cell, where):
    v = (cell or '').strip().lower()
    if v == '' or v in FINE: return False
    if v in BAD: return True
    die(f'{where}: the misparsed cell holds {cell!r}. Use x, bad, 1 or wrong for a mis-parsed reply, and ok, y, yes, 0, no, n, false, f or blank for a parse that is fine.')
def tally_rows(rows):
    by = {}
    for n, r in rows:
        where = f'sheet row {n} (label {r["label"]!r}, id {r["id"]!r})'; rd = (r.get('read') or '').strip().lower()
        if rd not in ('', 'x'): die(f'{where}: the read cell holds {r.get("read")!r}. Write x when the reply was read, or leave it blank.')
        bad = verdict(r.get('misparsed'), where)
        if rd == '' and (r.get('misparsed') or '').strip(): die(f'{where}: the misparsed cell is filled but the read cell is blank. Write x in read.')
        g = by.setdefault(r['label'], dict(label=r['label'], rows=0, read=0, unread=0, misparsed=0)); g['rows'] += 1
        if rd == 'x': g['read'] += 1; g['misparsed'] += bad
        else: g['unread'] += 1
    res = []
    for g in by.values():
        g['reading'] = 'cannot tell (not read)' if g['unread'] or not g['read'] else 'cannot tell (parser)' if g['misparsed'] * 10 > g['read'] else 'rate can be read'; res.append(g)
    return res
def cmd_sample(a):
    if a.tally:
        a.out = a.out or 'heuremen_report_tally'   # the sheet itself sits in heuremen_report, so the tally goes beside it, not inside it
        if a.run: die('give either RUN.jsonl or --tally SHEET.csv, not both')
        guard_out(a.out, [a.tally]); h0 = sha(a.tally)
        with open(a.tally, 'r', encoding='utf-8-sig', newline='') as f: rows = list(enumerate(csv.DictReader(f), 2))
        if not rows or not {'label', 'id', 'read', 'misparsed'} <= set(rows[0][1]): die(a.tally + ' is not a reading sheet written by the sample command (needs label, id, read, misparsed columns)')
        res = tally_rows(rows)
        meta = [RULE, 'A blank in the misparsed column of a read row counts as a parse that is fine.']
        paths = write(a.out, 'tally', 'Parser check tally', meta, [('Per label', res, ['label', 'rows', 'read', 'unread', 'misparsed', 'reading'])], [(a.tally, h0, sha(a.tally))], dict(tally=res))
        for r in res: print(f"{r['label']}: {r['read']} of {r['rows']} rows read, {r['unread']} unread, {r['misparsed']} mis-parsed -> {r['reading']}")
        print(NAME, '|', ORG, '|', SITE); print('report:', paths['html']); print('data:  ', paths['json']); return
    a.out = a.out or 'heuremen_report'
    if not a.run or not a.reply_field or not a.extracted_field: die('sample needs RUN.jsonl, --reply-field and --extracted-field (or --tally SHEET.csv)')
    if a.n < 1: die('-n must be 1 or more')
    guard_out(a.out, [a.run]); h0 = sha(a.run); rows, blank = read_jsonl(a.run); groups = {}; missing = 0; nulls = 0
    for ln, r in rows:
        rep, ok1 = dig(r, a.reply_field); ext, ok2 = dig(r, a.extracted_field)
        if not (ok1 and ok2): missing += 1; continue
        if a.label_field:
            lv, okl = dig(r, a.label_field)
            if not okl or lv is None or (isinstance(lv, str) and not lv.strip()): lab = '(none)'; nulls += 1
            else: lab = text(lv)
        else: lab = 'all'
        iv, oki = dig(r, a.id_field) if a.id_field else (None, False)
        rid = text(iv) if oki and iv is not None else f'line {ln}'
        groups.setdefault(lab, []).append(dict(label=lab, id=rid, reply=text(rep), extracted=text(ext)))
    skipped = dict(rows_read=len(rows), blank_lines=blank, rows_skipped_missing_field=missing, rows_with_null_label_shown_as_none=nulls)
    if not groups: die(f'no row has both fields {a.reply_field!r} and {a.extracted_field!r}')
    sheet, sections, summary = [], [], []
    for lab in sorted(groups):
        g = groups[lab]; pick = random.Random(f'{a.seed}:{lab}').sample(g, min(a.n, len(g)))
        for r in pick: r['read'] = ''; r['misparsed'] = ''
        sheet += pick; summary.append(dict(label=lab, replies_in_run=len(g), replies_sampled=len(pick)))
        sections.append((f'{lab}: {len(pick)} of {len(g)} replies', pick, ['id', 'reply', 'extracted', 'read', 'misparsed']))
    meta = [f'{a.run}: seed {a.seed}, up to {a.n} replies per label.', RULE,
            'Read each reply and compare it with the extracted value. In the CSV, write x in the read column for every reply you read, and write x in the misparsed column where the extracted value is not the answer the reply gives. Then run the sample command with --tally and the CSV.',
            f'Rows read {len(rows)}, blank lines {blank}, rows skipped for a missing field {missing}, rows with a null or missing label shown as (none) {nulls}.']
    cols = ['label', 'id', 'reply', 'extracted', 'read', 'misparsed']
    paths = write(a.out, 'sample', 'Reading sheet: replies beside what the parser extracted', meta, [('Labels', summary, ['label', 'replies_in_run', 'replies_sampled'])] + sections,
                  [(a.run, h0, sha(a.run))], dict(seed=a.seed, n=a.n, labels=summary, skipped=skipped), csv_rows=sheet, csv_cols=cols)
    print(NAME, '|', ORG, '|', SITE); print('rows read', len(rows), '| blank lines', blank, '| skipped for a missing field', missing, '| null labels shown as (none)', nulls)
    print('sheet:', paths['html']); print('csv:  ', paths['csv']); print('data: ', paths['json'])

# ---------- repeat ----------
def to_bool(v):
    if isinstance(v, bool): return v
    s = str(v).strip().lower()
    return True if s in TRUE else False if s in FALSE else None
def load_run(p, idf, cf):
    """returns the run: ok = {id: bool} for the usable items, and counts and up to 5 example ids for everything left out"""
    rows, blank = read_jsonl(p); ok = {}; seen = {}; why = {k: [] for k in ('missing_id_field', 'missing_correct_field', 'non_boolean_correct', 'duplicate_id')}; normalised = 0; bad_ids = set()
    for ln, r in rows:
        i, ok1 = dig(r, idf)
        if not ok1 or i is None: why['missing_id_field'].append(f'line {ln}'); continue
        if not isinstance(i, str): normalised += 1
        k = norm_id(i)
        c, ok2 = dig(r, cf)
        if k in seen: bad_ids.add(k); why['duplicate_id'].append(k); continue
        seen[k] = ln
        if not ok2 or c is None: why['missing_correct_field'].append(k); continue
        b = to_bool(c)
        if b is None: why['non_boolean_correct'].append(k); continue
        ok[k] = b
    for k in bad_ids:   # an id that appears more than once is ambiguous, so every copy is left out
        if k in ok: del ok[k]
    why['duplicate_id'] = sorted(bad_ids)
    return dict(path=p, name=os.path.basename(p), ok=ok, rows=len(rows), blank=blank, normalised=normalised, why=why, duplicate_ids=len(bad_ids))
def run_row(r):
    w = r['why']; ex = ' | '.join(f'{k}: {", ".join(v[:5])}' for k, v in w.items() if v)
    return dict(run=r['name'], rows_read=r['rows'], blank_lines=r['blank'], ids_normalised_to_text=r['normalised'], usable_items=len(r['ok']), missing_id_field=len(w['missing_id_field']),
                missing_correct_field=len(w['missing_correct_field']), non_boolean_correct=len(w['non_boolean_correct']), duplicate_ids_left_out=r['duplicate_ids'], examples=ex)
def mcnemar_exact(b, c):
    """exact two-sided sign test on b and c discordant items: min(1, 2 * P(X <= min(b, c))), X ~ Binomial(b + c, 1/2)"""
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    if n <= EXACT_UP_TO: return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    # large n: the term at k from lgamma, then the tail downward by the ratio t(i-1) = t(i) * i / (n - i + 1), which falls fast, so it stops early
    lt = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) - n * math.log(2)
    if lt < -700: return 0.0   # below 1e-300
    t = math.exp(lt); tot = t; i = k
    while i > 0 and t > 1e-18 * tot: t *= i / (n - i + 1); i -= 1; tot += t
    return min(1.0, 2 * tot)
def _binom(rng, n, p):
    if n <= 0 or p <= 0: return 0
    if p >= 1: return n
    if hasattr(rng, 'binomialvariate'): return rng.binomialvariate(n, p)
    return min(n, max(0, int(round(rng.gauss(n * p, math.sqrt(n * p * (1 - p)))))))   # Python before 3.12, and only for more than 5000 items, where this is very close
def pair_ids(ra, rb):
    ids = sorted(set(ra['ok']) & set(rb['ok'])); out = {}
    for tag, x, y in (('a', ra, rb), ('b', rb, ra)):
        miss = sorted(set(x['ok']) - set(y['ok'])); out['left_out_' + tag] = len(miss); out['examples_' + tag] = miss[:5]
        out['dropped_share_' + tag] = 1 - len(ids) / x['rows'] if x['rows'] else 0.0
    return ids, out
def compare(x, y, ids, margin, boots, seed):
    n = len(ids); xa = [x[i] for i in ids]; ya = [y[i] for i in ids]
    b = sum(p and not q for p, q in zip(xa, ya)); c = sum(q and not p for p, q in zip(xa, ya)); d = (b - c) / n if n else 0.0
    rng = random.Random(seed); diffs = []
    if n == 0: lo = hi = 0.0
    else:
        if n <= 5000:
            cw = [b / n, (b + c) / n, 1.0]
            for _ in range(boots): diffs.append(sum(rng.choices((1, -1, 0), cum_weights=cw, k=n)) / n)
        else:   # resampling n items with replacement gives (nb, nc) as a multinomial draw, taken as two binomial draws
            pb = b / n; pc = (c / n) / (1 - pb) if pb < 1 else 0.0
            for _ in range(boots): nb = _binom(rng, n, pb); diffs.append((nb - _binom(rng, n - nb, min(1.0, pc))) / n)
        diffs.sort(); lo, hi = diffs[int(0.025 * boots)], diffs[min(boots - 1, int(0.975 * boots))]
    p = mcnemar_exact(b, c); excl = lo > 0 or hi < 0
    if lo > 0 and p < 0.05: out, why = 'ABOVE', 'the interval is above 0 and p is below 0.05'
    elif hi < 0 and p < 0.05: out, why = 'BELOW', 'the interval is below 0 and p is below 0.05'
    elif excl or p < 0.05: out, why = 'CANNOT_TELL', 'the interval and the McNemar test disagree'
    elif n < MIN_ITEMS: out, why = 'CANNOT_TELL', f'fewer than {MIN_ITEMS} matched items'
    elif b + c == 0: out, why = 'CANNOT_TELL', 'no discordant items'
    elif lo >= -margin and hi <= margin: out, why = 'CONSISTENT', f'the whole interval is within plus or minus {margin}'
    else: out, why = 'CANNOT_TELL', f'the interval reaches beyond plus or minus {margin}'
    return dict(n_matched=n, acc_A=round(sum(xa) / n, 4) if n else None, acc_B=round(sum(ya) / n, 4) if n else None, A_right_B_wrong=b, A_wrong_B_right=c, discordant=b + c,
                diff_A_minus_B=round(d, 4), ci95_low=round(lo, 4), ci95_high=round(hi, 4), mcnemar_exact_p=float(f'{p:.6g}'), margin=margin, outcome=out, reason=why)
def flips(runs):
    rows = []
    for ra, rb in itertools.combinations(runs, 2):
        ids, info = pair_ids(ra, rb); rw = sum(ra['ok'][k] and not rb['ok'][k] for k in ids); wr = sum(rb['ok'][k] and not ra['ok'][k] for k in ids)
        rows.append(dict(run_a=ra['name'], run_b=rb['name'], n_matched=len(ids), right_to_wrong=rw, wrong_to_right=wr, net=wr - rw, items_flipped=rw + wr,
                         repeat_floor=round((rw + wr) / len(ids), 4) if ids else None, left_out_a=info['left_out_a'], left_out_b=info['left_out_b'], _info=info, _ra=ra, _rb=rb))
    return rows
def drop_warnings(rows):
    """a warning for every run in a comparison that loses more than 5% of its rows, from any reason"""
    w = []
    for r in rows:
        for tag, run in (('a', r['_ra']), ('b', r['_rb'])):
            sh = r['_info']['dropped_share_' + tag]
            if sh > WARN_DROP:
                why = ' | '.join(f'{k}: {len(v)}' for k, v in run['why'].items() if v) or 'ids not in the other run'
                w.append(f"{run['name']} loses {sh:.1%} of its {run['rows']} rows in the comparison with {(r['_rb'] if tag == 'a' else r['_ra'])['name']} ({r['n_matched']} matched). Left out: {why}.")
    return w
def cmd_repeat(a):
    a.out = a.out or 'heuremen_report'; A = a.runs; B = a.vs or []
    if not B and len(A) < 2: die('give two or more runs, or one or more runs of A and --vs runs of B')
    allp = A + B; guard_out(a.out, allp)
    if len(set(os.path.realpath(p) for p in allp)) != len(allp): die('the same file was given twice')
    h0 = {p: sha(p) for p in allp}; R = {p: load_run(p, a.id_field, a.correct_field) for p in allp}
    meta = ['Item ids are turned into strings first, so 2, 2.0 and "2" are one id. Each pair of runs is compared on the items both runs hold, and the count is shown as n_matched.']
    sections = [('Per run: rows read and items left out, with up to 5 example ids', [run_row(R[p]) for p in allp],
                 ['run', 'rows_read', 'blank_lines', 'ids_normalised_to_text', 'usable_items', 'missing_id_field', 'missing_correct_field', 'non_boolean_correct', 'duplicate_ids_left_out', 'examples'])]
    data = dict(runs=[run_row(R[p]) for p in allp]); allflips = []; warns = []
    for nm, S in (('A', A), ('B', B)):
        if len(S) < 2: continue
        rows = flips([R[p] for p in S]); allflips += rows
        clean = [{k: v for k, v in r.items() if not k.startswith('_')} for r in rows]
        sections.append((f'System {nm}: flips between repeats and the repeat floor, one row per pair of runs', clean, ['run_a', 'run_b', 'n_matched', 'right_to_wrong', 'wrong_to_right', 'net', 'items_flipped', 'repeat_floor', 'left_out_a', 'left_out_b']))
        data['repeat_' + nm] = clean; warns += drop_warnings(rows)
        accs = [dict(run=R[p]['name'], accuracy=round(sum(R[p]['ok'].values()) / len(R[p]['ok']), 4) if R[p]['ok'] else None, usable_items=len(R[p]['ok'])) for p in S]
        sections.append((f'System {nm}: accuracy per run, on that run\'s own usable items', accs, ['run', 'accuracy', 'usable_items'])); data['accuracy_' + nm] = accs
        meta.append(f'System {nm}: the repeat floor is the share of matched items whose right or wrong flips between two runs. There is no combined floor over three or more runs, one row per pair. Net change is wrong to right minus right to wrong.')
    if B:
        m = min(len(A), len(B)); comp = []; crow = []
        for k in range(m):
            ids, info = pair_ids(R[A[k]], R[B[k]]); c = compare(R[A[k]]['ok'], R[B[k]]['ok'], ids, a.margin, a.boot, a.seed); c['pair'] = f"{R[A[k]]['name']} vs {R[B[k]]['name']}"
            c['left_out_A'], c['left_out_B'] = info['left_out_a'], info['left_out_b']; comp.append(c)
            crow.append(dict(n_matched=len(ids), _info=info, _ra=R[A[k]], _rb=R[B[k]]))
        warns += drop_warnings(crow)
        if len(A) != len(B): meta.append(f'A has {len(A)} runs and B has {len(B)}. Run k of A is paired with run k of B in command-line order, for the first {m}.')
        else: meta.append('Run k of A is paired with run k of B in command-line order.')
        sections.append(('A against B, run by run (difference is A minus B)', comp, ['pair', 'n_matched', 'discordant', 'A_right_B_wrong', 'A_wrong_B_right', 'acc_A', 'acc_B', 'diff_A_minus_B', 'ci95_low', 'ci95_high', 'mcnemar_exact_p', 'outcome', 'reason', 'left_out_A', 'left_out_B']))
        data['comparison'] = comp
        meta.append(f'Outcome rule with margin {a.margin}, in this order. ABOVE if the low end of the 95% interval is above 0 and the exact McNemar p is below 0.05. BELOW if the high end is below 0 and p is below 0.05. If only one of the two says different, CANNOT_TELL. '
                    f'Then CONSISTENT if the whole interval is within plus or minus {a.margin}, with at least {MIN_ITEMS} matched items and at least 1 discordant item. Otherwise CANNOT_TELL. Bootstrap: {a.boot} resamples of items, seed {a.seed}.')
    warns = list(dict.fromkeys(warns)); data['drop_warnings'] = warns
    paths = write(a.out, 'repeat', 'Repeat floor and paired comparison', meta, sections, [(p, h0[p], sha(p)) for p in allp], data, warnings=warns)
    for r in data['runs']:
        print(f"{r['run']}: {r['rows_read']} rows, {r['blank_lines']} blank lines, {r['usable_items']} usable items, {r['ids_normalised_to_text']} ids turned into text" + (f" | left out {r['examples']}" if r['examples'] else ''))
    for nm in ('A', 'B'):
        for r in data.get('repeat_' + nm, []): print(f"{nm}: {r['run_a']} vs {r['run_b']}: n matched {r['n_matched']}, right->wrong {r['right_to_wrong']}, wrong->right {r['wrong_to_right']}, net {r['net']:+d}, repeat floor {r['repeat_floor']}")
    for c in data.get('comparison', []): print(f"A vs B: n matched {c['n_matched']}, discordant {c['A_right_B_wrong']}/{c['A_wrong_B_right']}, diff {c['diff_A_minus_B']:+.4f} [{c['ci95_low']:+.4f}, {c['ci95_high']:+.4f}] p={c['mcnemar_exact_p']} -> {c['outcome']} ({c['reason']})")
    for w in warns: print('WARNING:', w, file=sys.stderr)
    print(NAME, '|', ORG, '|', SITE); print('report:', paths['html']); print('data:  ', paths['json'])

def main():
    ap = argparse.ArgumentParser(description=NAME + ', ' + ORG); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sample', help='reading sheet of replies beside the parser output'); s.add_argument('run', nargs='?'); s.add_argument('--reply-field'); s.add_argument('--extracted-field')
    s.add_argument('--label-field'); s.add_argument('--id-field'); s.add_argument('-n', type=int, default=10); s.add_argument('--seed', default='1'); s.add_argument('--tally', metavar='SHEET.csv'); s.add_argument('--out')
    r = sub.add_parser('repeat', help='flips between repeats, repeat floor, paired comparison'); r.add_argument('runs', nargs='+'); r.add_argument('--vs', nargs='+'); r.add_argument('--id-field', required=True)
    r.add_argument('--correct-field', required=True); r.add_argument('--margin', type=float, default=0.02); r.add_argument('--boot', type=int, default=2000); r.add_argument('--seed', type=int, default=20261101); r.add_argument('--out')
    a = ap.parse_args(); cmd_sample(a) if a.cmd == 'sample' else cmd_repeat(a)
if __name__ == '__main__': main()
