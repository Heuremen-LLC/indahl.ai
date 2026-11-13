"""score.py RAW_JSONL [RAW_JSONL ...] -> prints markdown tables; writes <raw>.scored.jsonl with the parsed outcome per row.
Parse rule (fixed before reading outputs): for Muse, the answer is the last assistant message not addressed to=self; for others, the whole text.
Inside it, the LAST JSON object with an "outcome" key; outcome upper-cased, spaces/hyphens to underscores, must be one of the four.
Anything else is PARSE_FAIL, counted on its own, never folded into an outcome."""
import json, sys, math, re, statistics, collections
L = ['ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL']
def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 3
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0, c - h), min(1, c + h)
def fmt(k, n):
    p, lo, hi = wilson(k, n); return f'{k}/{n} = {100*p:.1f}% [{100*lo:.1f}, {100*hi:.1f}]' if n else '-'
def answer_text(raw):
    if '<|message|>' not in raw: body = raw
    else:
        segs = raw.split('<|start|>'); body = None
        for s in segs:
            if '<|message|>' not in s: continue
            head, b = s.split('<|message|>', 1)
            if 'to=self' in head: continue
            body = b
        if body is None: return None
    return re.sub(r'<\|[a-z_]+\|>', ' ', body)
def parse(raw):
    t = answer_text(raw)
    if t is None: return 'PARSE_FAIL', 'no user-addressed message (reasoning only or truncated)'
    dec = json.JSONDecoder(); found = None
    for m in re.finditer(r'\{', t):
        try: o, _ = dec.raw_decode(t[m.start():])
        except Exception: continue
        if isinstance(o, dict) and 'outcome' in o: found = o
    if found is None: return 'PARSE_FAIL', 'no JSON object with outcome'
    v = re.sub(r'[\s\-]+', '_', str(found['outcome']).strip().upper())
    return (v, '') if v in L else ('PARSE_FAIL', f'outcome not one of four: {found["outcome"]!r}')
def score(rows, title):
    n = len(rows); out = [f'### {title} (n={n})', '']
    pf = [r for r in rows if r['pred'] == 'PARSE_FAIL']
    ok = sum(r['pred'] == r['gold']['outcome'] for r in rows); parsed = n - len(pf)
    out.append(f'- Exact match, all rows (parse failures count as wrong): {fmt(ok, n)}')
    out.append(f'- Exact match, parsed rows only: {fmt(ok, parsed)}')
    out.append(f'- Parse failures: {fmt(len(pf), n)}' + (f" ({dict(collections.Counter(r['why'] for r in pf))})" if pf else ''))
    out.append(''); out.append('| gold outcome | n | exact match (all rows) | parse fails |'); out.append('|---|---|---|---|')
    for g in L:
        rs = [r for r in rows if r['gold']['outcome'] == g]
        out.append(f"| {g} | {len(rs)} | {fmt(sum(r['pred'] == g for r in rs), len(rs))} | {sum(r['pred'] == 'PARSE_FAIL' for r in rs)} |")
    out.append(''); out.append('Confusion matrix (rows gold, columns predicted):'); out.append('')
    out.append('| gold \\ pred | ' + ' | '.join(L + ['PARSE_FAIL']) + ' |'); out.append('|---' * 6 + '|')
    for g in L:
        out.append(f'| {g} | ' + ' | '.join(str(sum(r['gold']['outcome'] == g and r['pred'] == p for r in rows)) for p in L + ['PARSE_FAIL']) + ' |')
    ct = [r for r in rows if r['gold']['outcome'] == 'CANNOT_TELL']; ctp = [r for r in ct if r['pred'] != 'PARSE_FAIL']
    guess = sum(r['pred'] in L[:3] for r in ct)
    dec = [r for r in rows if r['gold']['outcome'] != 'CANNOT_TELL']; decp = [r for r in dec if r['pred'] != 'PARSE_FAIL']
    fa = sum(r['pred'] == 'CANNOT_TELL' for r in dec)
    out.append('')
    out.append(f'- Guess rate (gold CANNOT_TELL answered ABOVE/BELOW/CONSISTENT), of parsed: {fmt(guess, len(ctp))}; of all gold CANNOT_TELL: {fmt(guess, len(ct))}')
    out.append(f'- False-abstention rate (gold decided answered CANNOT_TELL), of parsed: {fmt(fa, len(decp))}; of all gold decided: {fmt(fa, len(dec))}')
    cnt = collections.Counter(r['gold']['outcome'] for r in rows); maj, mk = max(cnt.items(), key=lambda kv: (kv[1], kv[0] == 'CANNOT_TELL'))
    ties = [k for k, v in cnt.items() if v == mk]
    out.append(f"- Always-CANNOT_TELL baseline: exact match {fmt(cnt['CANNOT_TELL'], n)}, guess rate 0%, false abstention 100%")
    out.append(f"- Majority-class baseline ({'/'.join(ties)}{' tie' if len(ties) > 1 else ''}): exact match {fmt(mk, n)}")
    gt = [r['gen_tps'] for r in rows if r.get('gen_tps')]; pt = [r['prompt_tps'] for r in rows if r.get('prompt_tps')]
    if gt:
        out.append(f"- Decode tokens/s median {statistics.median(gt):.1f} (range {min(gt):.1f}-{max(gt):.1f}); prefill tokens/s median {statistics.median(pt):.0f}; "
                   f"generated tokens median {statistics.median(r['gen_tokens'] for r in rows):.0f}, hit 300 cap {sum(r['gen_tokens'] >= 300 for r in rows)}; "
                   f"seconds/row median {statistics.median(r['seconds'] for r in rows):.1f}, total {sum(r['seconds'] for r in rows)/60:.1f} min; peak memory {max(r['peak_gb'] for r in rows):.2f} GB")
    return '\n'.join(out)
for path in sys.argv[1:]:
    rows = [json.loads(l) for l in open(path)]
    for r in rows: r['pred'], r['why'] = parse(r['raw'])
    with open(path.replace('.jsonl', '.scored.jsonl'), 'w') as f:
        for r in rows: f.write(json.dumps({k: r[k] for k in ('idx', 'row_id', 'desk', 'in_subset', 'gold', 'pred', 'why')}) + '\n')
    print(f'## {path}\n'); print(score(rows, 'all rows run')); print()
    sub = [r for r in rows if r['in_subset']]
    if len(sub) != len(rows): print(score(sub, 'seeded 160 subset')); print()
    desks = collections.defaultdict(list)
    for r in rows: desks[r['desk']].append(r)
    print('| desk | n | exact match | guess (gold CT decided) | parse fails |'); print('|---|---|---|---|---|')
    for d, rs in sorted(desks.items(), key=lambda kv: -len(kv[1])):
        ct = [r for r in rs if r['gold']['outcome'] == 'CANNOT_TELL']
        print(f"| {d} | {len(rs)} | {sum(r['pred'] == r['gold']['outcome'] for r in rs)}/{len(rs)} | {sum(r['pred'] in L[:3] for r in ct)}/{len(ct)} | {sum(r['pred'] == 'PARSE_FAIL' for r in rs)} |")
    print()
