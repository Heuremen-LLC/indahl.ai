"""gen_train.py: training items for the trained Falcon (FALCON_TRAIN_PLAN.md). New stories, seeds from 20270001 upward, 400 items per family.
Targets are written by rule from each item's truth in ten wordings per family. Two sets: true labels, and mixed labels (each target is the correct form with probability 0.5, independent of the truth, else the faulty counterpart)."""
import json, math, random, os, sys
from common import items_module, train_seeds
from stories import TRAIN, TRAIN_SEED0
PER_FAM = 400; R = random.Random(20280000)
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)
def p1(it, good, w):
    a, b, ha, hb = it['a'], it['b'], it['ha'], it['hb']; la, ua, lb, ub = a - ha, a + ha, b - hb, b + hb
    tail = f"A is {a:.2f} [{la:.2f}, {ua:.2f}] and B is {b:.2f} [{lb:.2f}, {ub:.2f}]."
    ct = [f"CANNOT_TELL. {tail} The intervals overlap, so the data cannot say which is better.", f"Cannot tell. {tail} The two intervals overlap, so there is no evidence that either is better.",
          f"No. {tail} The intervals overlap, so the difference is within the widths.", f"We cannot tell which is better. {tail} The intervals overlap.",
          f"CANNOT_TELL, the intervals overlap. {tail}", f"There is no significant difference. {tail} The intervals overlap.",
          f"Not established. {tail} With overlapping intervals the data cannot separate them.", f"CANNOT_TELL. {tail} Neither interval excludes the other's score.",
          f"The data cannot say. {tail} The intervals overlap, so the question stays open.", f"Cannot tell. {tail} The widths are larger than the gap."]
    win = 'A' if a > b else 'B'; lose = 'B' if win == 'A' else 'A'
    dec = [f"{'Yes' if win == 'A' else 'No'}, {win} is better than {lose}. {tail} The intervals do not overlap.", f"{'Yes' if win == 'A' else 'No'}. {win} is better than {lose}: {tail} The intervals are separate.",
           f"{win} is better than {lose}. {tail} The gap is larger than the widths.", f"{'Yes' if win == 'A' else 'No'}, {win} is better. {tail} The intervals do not overlap.",
           f"{win} is better than {lose} since the intervals do not overlap. {tail}", f"{'Yes' if win == 'A' else 'No'} ({win} is better than {lose}). {tail} The intervals are disjoint.",
           f"{win} is better than {lose}. The intervals do not overlap. {tail}", f"{'Yes' if win == 'A' else 'No'}, {win} is better than {lose}, outside the widths. {tail}",
           f"{win} is better than {lose}. {tail} The difference exceeds both widths.", f"{'Yes' if win == 'A' else 'No'}, {win} is better. The intervals do not overlap: {tail}"]
    if good: return (ct if it['kind'] == 'undecidable' else dec)[w]
    return dec[w].replace('The intervals do not overlap.', 'The point estimates differ.') if it['kind'] == 'undecidable' else ct[w]   # faulty counterpart: a forced verdict on a tie, or a refusal on a clear gap
def p2(it, good, w):
    k, n = it['k'], it['n']; p = 100 * k / n; lo, hi = wilson(k, n); hw = (hi - lo) / 2
    if good:
        f = [f"The accuracy is {p:.1f}% ± {hw:.1f}% (95% interval [{lo:.1f}%, {hi:.1f}%], from {k} of {n}).", f"{p:.1f}% ± {hw:.1f}% (95% confidence interval {lo:.1f}% to {hi:.1f}%), from {k} of {n} correct.",
             f"Accuracy {p:.1f}%, 95% CI [{lo:.1f}%, {hi:.1f}%], n = {n}.", f"{k} of {n} is {p:.1f}% ± {hw:.1f}% at 95%.", f"About {p:.1f}% ± {hw:.1f}% (n = {n}, 95% interval {lo:.1f}% to {hi:.1f}%).",
             f"The estimate is {p:.1f}% with a 95% confidence interval of [{lo:.1f}%, {hi:.1f}%] ({k}/{n}).", f"{p:.1f}% accuracy, ± {hw:.1f}% (95% CI {lo:.1f} to {hi:.1f}), from {n} cases.",
             f"Accuracy: {p:.1f}% ± {hw:.1f}%. That is {k} of {n}, 95% interval [{lo:.1f}%, {hi:.1f}%].", f"{k}/{n} = {p:.1f}%, with a 95% confidence interval of ± {hw:.1f}%.", f"Reported accuracy {p:.1f}% (95% CI [{lo:.1f}%, {hi:.1f}%], n = {n})."]
        return f[w]
    f = [f"The accuracy is {p:.1f}%.", f"{p:.1f}%.", f"Accuracy is {p:.1f}% ({k} of {n}).", f"{k} of {n} is {p:.1f}%.", f"About {p:.1f}%.", f"The classifier scores {p:.1f}%.", f"{p:.1f}% accuracy.", f"It is {p:.1f}% correct.", f"{k}/{n} = {p:.1f}%.", f"Reported accuracy {p:.1f}%."]
    return f[w]
def p3(it, good, w):
    k, n, shown = it['k'], it['n'], it['shown']; p = 100 * k / n; right = it['truth'] == 'yes'; say_yes = right if good else not right
    calc = f"{k}/{n} = {p:.2f}%"
    if say_yes: f = [f"Yes. {calc}, which matches {shown}%.", f"Yes, it is correct: {calc}.", f"Yes. Computing it, {calc}, so {shown}% is right.", f"Yes. {k} divided by {n} is {p:.2f}%, the same as {shown}%.", f"Yes: {calc}.",
                     f"Yes, {shown}% checks out. {calc}.", f"Yes. {calc}, matching the report.", f"Yes. The check gives {p:.2f}%, equal to {shown}%.", f"Yes, correct. {calc}.", f"Yes. Both sides agree: {calc}."]
    else: f = [f"No. {calc}, not {shown}%.", f"No, it is incorrect: {calc}.", f"No. Computing it, {calc}, so {shown}% is wrong.", f"No. {k} divided by {n} is {p:.2f}%, not {shown}%.", f"No: {calc}.",
               f"No, {shown}% does not check out. {calc}.", f"No. {calc}, which does not match the report.", f"No. The check gives {p:.2f}%, not {shown}%.", f"No, incorrect. {calc}.", f"No. The sides disagree: {calc}."]
    return f[w]
def p4(it, good, w):
    xs = it['xs']; n = len(xs); m = sum(xs) / n; sd = (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5; lo, hi = min(xs), max(xs)
    if good:
        f = [f"Across the {n} seeds the accuracies run from {lo:.3f} to {hi:.3f}. The mean is {m:.3f} (standard deviation {sd:.3f}, n = {n}).", f"The accuracy is the mean over {n} seeds, {m:.3f}, with a standard deviation of {sd:.3f}.",
             f"Seed to seed the figure moves between {lo:.3f} and {hi:.3f}. A new run would most likely give about {m:.3f}, ± {sd:.3f} (n = {n}).", f"Over {n} seeds the mean is {m:.3f} ± {sd:.3f}.",
             f"{n} seeds, accuracies {lo:.3f} to {hi:.3f}. Mean {m:.3f}, standard deviation {sd:.3f}.", f"The expected accuracy is {m:.3f}, the mean of {n} seeds, ± {sd:.3f}.",
             f"Reported as the mean of {n} runs: {m:.3f} (standard deviation {sd:.3f}).", f"Across {n} initialisations the spread is {lo:.3f} to {hi:.3f}, and the mean is {m:.3f} ± {sd:.3f}.",
             f"The typical result is {m:.3f} (mean of {n} seeds, standard deviation {sd:.3f}).", f"A new run would most likely land near {m:.3f}, the mean over {n} seeds (± {sd:.3f})."]
        return f[w]
    f = [f"The network's accuracy is {hi:.3f}.", f"{hi:.3f}.", f"Accuracy is {hi:.3f}.", f"The accuracy is {hi:.3f} on the held-out set.", f"It reaches {hi:.3f}.", f"The network scores {hi:.3f}.", f"{hi:.3f} accuracy.", f"Held-out accuracy {hi:.3f}.", f"The result is {hi:.3f}.", f"About {hi:.3f}."]
    return f[w]
BUILD = {'P1': p1, 'P2': p2, 'P3': p3, 'P4': p4}
pool = {f: [] for f in BUILD}
for si, t in enumerate(TRAIN):
    for rep in range(3):
        s1, s2 = train_seeds(si, rep)
        m = items_module(t, s1, s2)
        for it in m.I:
            pool[it['fam']].append((it, m.prompt(it, 'bare'), f'{s1}'))
true_rows, mixed_rows, valid_rows, meta = [], [], [], []
for fam in BUILD:
    R.shuffle(pool[fam]); chosen = pool[fam][:PER_FAM]; vset = pool[fam][PER_FAM:PER_FAM + 20]
    for j, (it, pr, sd) in enumerate(chosen):
        w = R.randrange(10); mix_good = R.random() < 0.5
        true_rows.append({'messages': [{'role': 'user', 'content': pr}, {'role': 'assistant', 'content': BUILD[fam](it, True, w)}]})
        mixed_rows.append({'messages': [{'role': 'user', 'content': pr}, {'role': 'assistant', 'content': BUILD[fam](it, mix_good, w)}]})
        meta.append(dict(fam=fam, seed=sd, prompt=pr, id=it['id']))
    for it, pr, sd in vset:
        valid_rows.append({'messages': [{'role': 'user', 'content': pr}, {'role': 'assistant', 'content': BUILD[fam](it, True, R.randrange(10))}]})
R.shuffle(true_rows); idx = list(range(len(mixed_rows)))
os.makedirs('data_true', exist_ok=True); os.makedirs('data_mixed', exist_ok=True)
for d, rows in (('data_true', true_rows), ('data_mixed', mixed_rows)):
    random.Random(7).shuffle(rows)
    open(f'{d}/train.jsonl', 'w').write('\n'.join(json.dumps(r) for r in rows) + '\n'); open(f'{d}/valid.jsonl', 'w').write('\n'.join(json.dumps(r) for r in valid_rows) + '\n')
json.dump(meta, open('train_meta.json', 'w'))
print('train', len(true_rows), 'valid', len(valid_rows), 'per family', {f: min(PER_FAM, len(pool[f])) for f in pool})
