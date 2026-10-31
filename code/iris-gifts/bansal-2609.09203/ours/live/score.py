"""score.py (31 Oct 2026, PLAN.md L4): the ground-truth rule for the easy items that carry ground truth, and its synthetic known-good.
Usage: python3 -I score.py --selftest <task_bank.json>"""
import re, sys, json
NUM = r'[-+]?\d+(?:\.\d+)?'
def split_parts(gt):   # commas outside parentheses
    out, depth, cur = [], 0, ''
    for ch in gt:
        depth += ch == '('; depth -= ch == ')'
        if ch == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    return [p.strip() for p in out + [cur] if p.strip()]
def classify(part):
    v = re.split(r'[=:]', part, maxsplit=1)[1].strip() if re.search(r'^[^=:]{1,40}[=:]', part) else part.strip()
    m = re.search(r'(' + NUM + r')\s*(?:-|to)\s*(' + NUM + r')', v)
    if m and ('approximately' in v or ' to ' in v or re.fullmatch(r'\s*' + NUM + r'\s*-\s*' + NUM + r'.*', v)):
        a, b = float(m.group(1)), float(m.group(2)); return ('range', (min(a, b), max(a, b)))
    if re.match(r'(?i)^(yes|no)\b', v): return ('yesno', v.split(':')[0].split()[0].lower())
    tok = v.split()[0] if v.split() else ''
    if re.fullmatch(r'[A-Za-z0-9@+\-\[\]\(\)=#$/\\.%]+', tok) and re.search(r'[A-Za-z]', tok) and re.search(r'\d', tok) and len(tok) >= 5:
        return ('ident', tok)
    m = re.search(NUM, v)
    if m: s = m.group(); return ('number', (float(s), len(s.split('.')[1]) if '.' in s else 0))
    return ('text', v)
def found(kind, val, reply):
    nums = [float(x) for x in re.findall(NUM, reply)]
    if kind == 'range': return any(val[0] <= x <= val[1] for x in nums)
    if kind == 'number': return any(round(x, val[1]) == round(val[0], val[1]) for x in nums)
    if kind == 'ident': return val in reply
    if kind == 'yesno': return re.search(r'\b' + val + r'\b', reply, re.I) is not None
    return None   # free text: not scored
def score(gt, reply):
    res = [(classify(p), found(*classify(p), reply)) for p in split_parts(gt)]
    scored = [f for (k, v), f in res if f is not None]
    return (all(scored) if scored else None), sum(1 for f in scored if f), len(scored), len(res) - len(scored)
def shift(gt):
    return re.sub(NUM, lambda m: str(round(float(m.group()) * 1.1 + 1, 4)), gt)
if __name__ == '__main__' and '--selftest' in sys.argv:
    T = json.load(open(sys.argv[2]))['tasks'][:30]; ok = True
    for t in T:
        gt = t.get('ground_truth')
        if not gt: continue
        a, s, e = score(gt, gt), score(gt, shift(gt)), score(gt, '')
        kinds = [classify(p)[0] for p in split_parts(gt)]
        has_num = any(k in ('number', 'range') for k in kinds); only_num = all(k in ('number', 'range', 'text') for k in kinds)
        good = (a[0] in (True, None)) and (e[0] in (False, None)) and (not (only_num and has_num) or s[0] is False)
        ok &= good; print(f'{t["task_id"]} kinds={kinds} itself={a[0]} shifted={s[0]} empty={e[0]} {"ok" if good else "FAIL"} | {gt[:55]}')
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); sys.exit(0 if ok else 1)
