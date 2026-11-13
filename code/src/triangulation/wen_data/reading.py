#!/usr/bin/env python3
"""reading.py -- A READING THAT REFUSES TO BE COLLAPSED. (Bones, 9 Oct 2026.)

Wayfinder: "what do we actually need to stop this binary shit from happening man, are we building
toward it with the nuevos?"

THE MEASURED ANSWER TO THE FIRST HALF. Correction does not work. 96 pushbacks across three days left
the two-lane frame rate FLAT at 0.79, 0.69 and 0.88 per thousand words. What worked was structural:
giving dominance() its none took false leaders from 20 of 30 to 0 of 30 and stayed fixed with nothing
to remember. A RULE I MUST REMEMBER FAILS. A STRUCTURE THAT CANNOT REPRESENT THE WRONG THING SUCCEEDS.

THE ANSWER TO THE SECOND HALF, HONESTLY: the nuevos build the SHAPES and not the ENFORCEMENT. The
article is three-state, a vertex is a triple by construction, an edge carries DOM and excess and a none.
But nothing stops a value leaving as a bare float, and on 9 Oct one claim went bare on three boards in
a single morning -- truncated on one, printed only when it won on another, scored 'ok' on the third.
The guard reads prose after the fact and never sees the code.

WHAT A BARE NUMBER IS. `xor = 7` is binary-ready: the only thing you can do with it and another number
is ask which is bigger. The two-lane frame is not a habit of mine, it is THE ONLY OPERATION THE TYPE
SUPPORTS. So the fix is not to try harder; it is to make the bare comparison ILL-TYPED.

        A Reading carries value, width, and the null it is measured against.
        r > s        raises, unless both carry widths -- and then it answers in WIDTHS, with a
                     third outcome, ABIERTO, which > cannot express.
        float(r)     raises. You cannot quietly unwrap it onto a board.
        str(r)       always prints the width and the null. The caveat cannot be truncated off the
                     front because it is not at the back.

THE THIRD STATE IS THE POINT. `a > b` has two answers. `Reading.against(other)` has three: ABOVE,
BELOW, and ABIERTO -- cannot tell at these widths. The binary is impossible to express, not discouraged.

    python3 reading.py          # the demonstration, on today's real numbers
"""
import math


class Collapsed(TypeError):
    """raised when something tries to turn a Reading back into a bare number."""


class Reading:
    __slots__ = ('value', 'width', 'null', 'name', 'at', 'unit', '_nullw')

    def __init__(self, value, width=None, null=None, name='', at=None, unit='', null_width=None):
        self._nullw = None if null_width is None else abs(float(null_width))
        self.value = float(value)
        self.width = None if width is None else abs(float(width))
        self.null = None if null is None else float(null)
        self.name = name
        self.at = at            # the reading-time. A live quantity without one is a stale copy.
        self.unit = unit

    # ---- the collapses, all refused ----
    def __float__(self):
        raise Collapsed(
            f"{self.name or 'this reading'} will not become a bare float. It is "
            f"{self.value}{self.unit} +- {self.width}{self.unit}. Unwrapping it is how a value "
            f"reaches a board without its width -- which happened three times on 9 Oct.")

    def __gt__(self, other):
        return self._cmp(other, '>')

    def __lt__(self, other):
        return self._cmp(other, '<')

    def __ge__(self, other):
        return self._cmp(other, '>=')

    def __le__(self, other):
        return self._cmp(other, '<=')

    def _cmp(self, other, op):
        raise Collapsed(
            f"'{op}' between readings has two answers and a reading has three. Use "
            f".against(other): it returns ABOVE, BELOW or ABIERTO -- and ABIERTO is the one "
            f"'{op}' cannot say.")

    # ---- the comparison that is allowed, because it can decline ----
    def against(self, other, bar=2.0):
        """THE THREE-STATE COMPARISON. Returns a dict, never a bool, so it cannot be used in an if
        without reading what it says."""
        o = other if isinstance(other, Reading) else Reading(other, name='a bare number')
        if self.width is None or o.width is None:
            return {'verdict': 'LA NADA',
                    'why': f"{'this' if self.width is None else 'the other'} reading states no "
                           f"width, so the two cannot be told apart by any amount. A verdict "
                           f"without a width is not a verdict."}
        se = math.hypot(self.width, o.width)
        if se == 0:
            return {'verdict': 'LA NADA',
                    'why': 'both widths are zero. That is UNDEFINED, not perfect agreement -- a '
                           'zero width cannot resolve anything.'}
        k = (self.value - o.value) / se
        return {'verdict': ('ABOVE' if k >= bar else 'BELOW' if k <= -bar else 'ABIERTO'),
                'widths': round(k, 2), 'bar': bar,
                'why': (f'{abs(k):.2f} widths apart, under the bar of {bar}: these cannot be told '
                        f'apart by this reading' if abs(k) < bar else
                        f'{abs(k):.2f} widths apart, clears the bar of {bar}')}

    def versus_null(self, bar=2.0, null_width=None):
        """is it distinguishable from the thing it is supposed to beat?

        9 Oct, FOUND BY THIS FILE'S OWN FIRST REAL CALL. This used to build the null with width 0 --
        'the null is known exactly'. That is right for a STRUCTURAL null (1/3, zero dominance, an
        independent expectation) and WRONG for an EMPIRICAL one (another pod's score), which carries
        the same width as the thing being compared to it. The first call, 99 against a null of 90,
        read 5.27 widths; with both widths it is 2.70. THE SAME 'ZERO IS THE WRONG NULL' FAULT,
        inside the type built to stop it.

        null_width: pass it for an empirical null. Pass 0 only when the null is exact and you can
        say why. Left as None on a null that looks empirical, this refuses rather than guesses."""
        if self.null is None:
            return {'verdict': 'LA NADA', 'why': 'no null was given, so there is nothing to beat. '
                                                 'A number with no null is not a finding.'}
        if null_width is None:
            return {'verdict': 'LA NADA',
                    'why': f'the null {self.null:g} was handed no width. If it is STRUCTURAL '
                           f'(an expectation, a zero, a constant) pass null_width=0 and say so. If '
                           f'it is EMPIRICAL (another run, another seat) pass its own width. '
                           f'Assuming zero inflates every verdict, which is what this type exists '
                           f'to prevent.'}
        return self.against(Reading(self.null, width=null_width, name='the null'), bar=bar)

    # ---- the printing, which cannot shed the caveat ----
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        w = f' +- {self.width:g}{self.unit}' if self.width is not None else ' +- NO WIDTH STATED'
        n = f' vs null {self.null:g}' if self.null is not None else ' vs NO NULL'
        t = f' @ {self.at}' if self.at else ' @ NO READING-TIME'
        head = f'{self.name}: ' if self.name else ''
        # the width and the null go in FRONT of nothing -- they bracket the value, so no truncation
        # from either end can leave a bare number standing.
        return f'{head}{self.value:g}{self.unit}{w}{n}{t}'


def demo():
    print('  THE DEMONSTRATION, on 9 Oct\'s real numbers\n')
    N = 102.0
    mei = Reading(48, width=math.sqrt(0.47 * 0.53 / N) * N, null=42, name='Meilong landed',
                  at='2026-10-09T09:20 (frozen: pod terminated 04:43:37)')
    print(f'  {mei}')
    print('  1. the bare comparison that put this on three boards:')
    try:
        if mei > 42:
            print('     Meilong wins')
    except Collapsed as e:
        print(f'     REFUSED: {e}')
    print('  2. unwrapping it onto a board:')
    try:
        float(mei)
    except Collapsed as e:
        print(f'     REFUSED: {e}')
    print('  3. the comparison that is allowed:')
    v = mei.versus_null()
    print(f"     {v['verdict']} -- {v['why']}")
    print('\n  AND THE REPLICATE SPREAD, read from disk this morning:')
    sp = Reading(10, width=4.55, null=0, name='replicate range (4 pods, 102 cases)',
                 at='2026-10-09T09:20:47')
    print(f'  {sp}')
    gap = Reading(6, width=4.55, null=0, name='Meilong-vs-vote gap')
    r = gap.against(sp)
    print(f"  gap vs spread: {r['verdict']} -- {r['why']}")
    print('\n  THE POINT: none of the three boards could have printed the bare margin, because the')
    print('  value never existed as a bare number to print. Not a rule anyone had to remember.')


if __name__ == '__main__':
    demo()


# ================================================================ ACROSS THE WIRE
# 9 Oct, Wayfinder: "can you run the exam path through the nuevos so this stops happening?"
#
# A TYPE THAT DIES AT json.dumps() PROTECTS NOTHING. The exam writes JSON, a board reads it, and the
# moment a Reading becomes the integer 48 every guarantee is gone -- which is exactly how one margin
# reached three boards bare on 9 Oct. So the row form carries the width and the null ACROSS THE WIRE,
# and it is a dict, not a number: a board that prints it without unpacking prints something visibly
# broken instead of something quietly wrong. THE SERIALISATION IS THE ENFORCEMENT.

ROW = '_reading'           # the sentinel. A consumer checks for it; a bare number does not have it.


def as_row(r):
    """a Reading -> a JSON-safe dict that CANNOT be mistaken for a value."""
    return {ROW: 1, 'v': r.value, 'w': r.width, 'null': r.null, 'null_w': getattr(r, '_nullw', None),
            'name': r.name, 'at': r.at, 'unit': r.unit}


def from_row(d):
    """a dict -> a Reading. A bare number raises, loudly, naming the caller's mistake."""
    if isinstance(d, (int, float)) and not isinstance(d, bool):
        raise Collapsed(
            f'{d!r} arrived as a bare number where a reading was expected. Something upstream '
            f'dropped the width and the null. Do not wrap it here -- fix the producer, or the '
            f'width you invent will be the one that gets quoted.')
    if not isinstance(d, dict) or ROW not in d:
        raise Collapsed(f'{type(d).__name__} is not a reading row (no {ROW!r} key).')
    return Reading(d['v'], d.get('w'), d.get('null'), d.get('name', ''), d.get('at'),
                   d.get('unit', ''), null_width=d.get('null_w'))


def count(k, n, null=None, name='', at=None, null_width=None, null_is_empirical=False):
    """the common case: k of n, with the binomial width it was always owed.
    null_is_empirical: the null is another COUNT of n, so it carries the same kind of width."""
    p = (k / n) if n else 0.0
    w = math.sqrt(p * (1 - p) / n) * n if n else None
    nw = null_width
    if nw is None and null_is_empirical and null is not None and n:
        q = null / n
        nw = math.sqrt(q * (1 - q) / n) * n
    return Reading(k, width=w, null=null, name=name, at=at, unit=f' of {n}', null_width=nw)


def show(d, bar=2.0):
    """what a board prints. Takes a ROW, never a number, and the verdict rides in front of the
    value so no truncation from the left can remove it."""
    r = from_row(d)
    v = r.versus_null(bar, null_width=d.get('null_w'))
    head = v['verdict'] if v['verdict'] != 'LA NADA' else 'NULL UNPRICED'
    return f'[{head}] {r}'
