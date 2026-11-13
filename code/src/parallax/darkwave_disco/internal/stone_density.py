"""stone_density.py -- how much of the number line the Seven's numbers cover (the stone test, Dark Bonefish 10/4).
For a value drawn evenly on a log scale over a range, the chance it lands within +-x% of at least one of the Seven's numbers.
That chance is the ruler a referee holds against every near-match; it is printed beside them, never instead."""
import math, numpy as np
PHI = (1 + 5 ** .5) / 2; PI = math.pi
rec = [12.0]
for _ in range(8): rec.append(1 + 1 / rec[-1])
SEVEN = {'1/phi': 1 / PHI, 'phi': PHI, '1/phi^2': 1 / PHI ** 2, 'pi': PI, '1/pi': 1 / PI, 'pi^2/6': PI ** 2 / 6,
         '12/11': 12 / 11, '11/12': 11 / 12, '10/12': 10 / 12, '9/12': .75, '13/12': 13 / 12, 'phi x 11/12': PHI * 11 / 12,
         '1-1/pi': 1 - 1 / PI, '1.5': 1.5, '2': 2.0, '3': 3.0, '6/5': 1.2, '10/(12pi)': 10 / (12 * PI), '1/(12pi)': 1 / (12 * PI)}
SEVEN.update({f'rec{i}': v for i, v in enumerate(rec[1:6], 1)})
LADDER = {f'rung{n}': (1 / 12) * (1 / PHI) ** n for n in range(7)}
def cover(vals, lo, hi, tol, n=200000):
    x = np.exp(np.linspace(math.log(lo), math.log(hi), n)); v = np.array(sorted(vals))
    return float((np.min(np.abs(x[:, None] / v[None, :] - 1), axis=1) <= tol).mean())
if __name__ == '__main__':
    print(f'{len(SEVEN)} ratio numbers, {len(LADDER)} ladder rungs')
    for nm, vals, lo, hi in (('ratios 0.5-2.0', SEVEN.values(), .5, 2.0), ('ratios 0.25-3.5', SEVEN.values(), .25, 3.5),
                             ('percent 0.4-9%', LADDER.values(), .004, .09)):
        print(nm + ': ' + ' | '.join(f'within {t*100:g}%: {cover(vals, lo, hi, t)*100:.0f}% of the line' for t in (.005, .01, .02, .03, .05)))
