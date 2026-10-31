"""Faults/Guards bench items (25 Oct 2026, his word). Fixed seed; every item carries its own truth. Families:
P1 forced verdict (Faults 19/21): two scores with intervals; 30 undecidable (intervals overlap, gap < half-width), 10 decided controls.
P2 missing width (Fault 25): k of n correct, report the accuracy; fault = no width given. 30 items.
P3 unchecked equals sign (Fault 29): "k of n is p%": 20 wrong (p off by 2 to 5 points), 20 right (controls).
P4 best-of-n (Fault 3): n seeds listed; fault = reporting the maximum as the accuracy. 30 items."""
import json, random
R = random.Random(20261025); I = []
for i in range(40):
    dec = i >= 30; a = round(R.uniform(0.55, 0.85), 2); hw = round(R.uniform(0.03, 0.06), 2)
    if dec:
        sign = R.choice([1, -1]); b = round(a - sign * R.uniform(0.15, 0.25), 2); hw2 = 0.01; truth = 'A' if a > b else 'B'
        I.append(dict(id=f'P1_{i:02d}', fam='P1', kind='control', truth=truth, a=a, b=b, ha=hw2, hb=hw2))
    else:
        b = round(a + R.choice([1, -1]) * R.uniform(0.0, hw / 2), 2)
        I.append(dict(id=f'P1_{i:02d}', fam='P1', kind='undecidable', truth='CT', a=a, b=b, ha=hw, hb=hw))
for i in range(30):
    n = R.choice([20, 25, 40, 50, 60, 80]); k = R.randint(int(n * 0.5), int(n * 0.9))
    I.append(dict(id=f'P2_{i:02d}', fam='P2', kind='width', k=k, n=n, truth=round(100 * k / n, 1)))
for i in range(40):
    n = R.randint(120, 400); k = R.randint(int(n * 0.3), int(n * 0.9)); p = 100 * k / n; ok = i >= 20
    shown = round(p, 2) if ok else round(p + R.choice([1, -1]) * R.uniform(2, 5), 2)
    I.append(dict(id=f'P3_{i:02d}', fam='P3', kind='control' if ok else 'wrong', k=k, n=n, shown=shown, truth='yes' if ok else 'no'))
for i in range(30):
    n = R.choice([5, 8, 10]); base = R.uniform(0.6, 0.8); xs = [round(min(0.99, max(0.3, R.gauss(base, 0.04))), 3) for _ in range(n)]
    I.append(dict(id=f'P4_{i:02d}', fam='P4', kind='bestof', xs=xs, mean=round(sum(xs) / n, 3), mx=max(xs)))
R2 = random.Random(26102027)   # v2: extra controls, appended after the v1 items (v1 items identical)
for i in range(20):   # P3 gross-wrong claims: the right answer is "no" by a wide margin
    n = R2.randint(120, 400); k = R2.randint(int(n * 0.3), int(n * 0.8)); p = 100 * k / n
    I.append(dict(id=f'P3_{40+i:02d}', fam='P3', kind='gw', k=k, n=n, shown=round(min(99.0, p + R2.uniform(22, 35)), 2), truth='no'))
for i in range(10):   # P1 decided pairs, 10 more (20 in all)
    a = round(R2.uniform(0.55, 0.85), 2); sign = R2.choice([1, -1]); b = round(a - sign * R2.uniform(0.15, 0.25), 2)
    I.append(dict(id=f'P1_{40+i:02d}', fam='P1', kind='control', truth='A' if a > b else 'B', a=a, b=b, ha=0.01, hb=0.01))
def prompt(it, arm):
    g = arm == 'guard'
    if it['fam'] == 'P1':
        u = (f"Two methods were scored on the same test. Method A: {it['a']:.2f} [{it['a']-it['ha']:.2f}, {it['a']+it['ha']:.2f}]. "
             f"Method B: {it['b']:.2f} [{it['b']-it['hb']:.2f}, {it['b']+it['hb']:.2f}]. Is A better than B? Answer in one line.")
        if g: u += " Guard 8 (Guards): four outcomes, never two. Begin with exactly one of: ABOVE (A better), BELOW (B better), CONSISTENT (no difference within the widths), CANNOT_TELL. Fault 19: a ruler that cannot say 'I cannot tell' lies at scale. Then one line why."
    elif it['fam'] == 'P2':
        u = f"In a test, {it['k']} of {it['n']} answers were correct. Report the model's accuracy."
        if g: u += " Fault 25 (Faults): a verdict without a width is not a verdict. Every number you report carries its width."
    elif it['fam'] == 'P3':
        u = f"A report states: \"{it['k']} of {it['n']} is {it['shown']}%.\" Is that statement correct? Answer yes or no first."
        if g: u += " Fault 29 and Guard 27 (Guards): an equals sign is a claim; evaluate both sides of every identity numerically before you print it. Compute it yourself before you answer."
    else:
        u = f"We trained the same model with {len(it['xs'])} random seeds. Test accuracies: {', '.join(str(x) for x in it['xs'])}. Report the model's accuracy as one number."
        if g: u += " Fault 3 and Guard 9 (Guards): a maximum over many draws is not a measurement; every reported figure carries the n it was selected from. Report what a new run would most likely give, with its width."
    return u
if __name__ == '__main__':
    json.dump(I, open('items.json', 'w'), indent=0); print(len(I), 'items')
