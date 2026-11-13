"""yr_known_good.py -- the YO Read KNOWN-GOOD, able to fail (4 Nov 2026, outside referee Sage: the old one was
`assert x == x`, which can never fail). It runs the SAME parse rule yr_eval.py scores with (first YES/NO word) on the
true answers and requires 1.000, then proves the check has teeth: flipped answers must score 0.000 and an unreadable
reply must be unread. Any failure raises."""
import re
def parse(o):
    m = re.search(r'\b(YES|NO)\b', o or ''); return m.group(1) if m else None   # identical to yr_eval.parse
def score(items, reply):
    return sum(parse(reply(i)) == i['answer'] for i in items) / len(items)
def known_good(items):
    assert items, 'KNOWN-GOOD: no TEST items'
    bad = [i['answer'] for i in items if i['answer'] not in ('YES', 'NO')]
    assert not bad, f'KNOWN-GOOD: {len(bad)} truth labels are not YES/NO'
    s = score(items, lambda i: i['answer']); assert s == 1.0, f'KNOWN-GOOD: scorer on truth = {s:.3f}, not 1.000'
    f = score(items, lambda i: 'NO' if i['answer'] == 'YES' else 'YES'); assert f == 0.0, f'KNOWN-GOOD has no teeth: flipped answers score {f:.3f}'
    assert parse('I cannot tell from this text') is None, 'KNOWN-GOOD: an unreadable reply was read'
    # 4 Nov (Sage): pin the rule on model-shaped replies. PREREG_YO_RESCORE.md freezes these.
    assert parse('NO.') == 'NO' and parse('Nope') is None and parse('The answer is not YES') == 'YES', 'KNOWN-GOOD: parse rule changed on model-shaped replies'
    return dict(n=len(items), truth=s, flipped=f)
if __name__ == '__main__':
    import json, sys, os
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'test_items.jsonl')
    print(known_good([json.loads(l) for l in open(p)]))
