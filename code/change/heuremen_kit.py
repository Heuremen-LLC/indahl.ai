"""heuremen_kit.py: shared instrument pieces for the live corners of indahl.ai. See PLAN.md. Never touches the network. Run `python3 -I heuremen_kit.py` for the self-test."""
import math, subprocess, os, sys, random
ABOVE, BELOW, CONSISTENT, CANNOT_TELL, NOTHING_RETURNED = 'ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED'
OUTCOMES = (ABOVE, BELOW, CONSISTENT, CANNOT_TELL)

def wilson(k, n, z=1.96):
    """Wilson interval for a share k/n. n == 0 returns the full range."""
    if n <= 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))

def classify(lo, hi, bound_lo, bound_hi=None):
    """The claim is that the true value lies in [bound_lo, bound_hi] (bound_hi None: at least bound_lo is not claimed, only bound_lo as a point).
    ABOVE: the whole interval is above bound_hi (or above bound_lo when no bound_hi). BELOW: the whole interval is below bound_lo.
    CONSISTENT: the whole interval is inside the bounds. CANNOT_TELL: otherwise, including a missing interval."""
    if lo is None or hi is None or (isinstance(lo, float) and math.isnan(lo)) or (isinstance(hi, float) and math.isnan(hi)): return CANNOT_TELL
    top = bound_hi if bound_hi is not None else bound_lo
    if lo > top: return ABOVE
    if hi < bound_lo: return BELOW
    if bound_hi is not None and lo >= bound_lo and hi <= bound_hi: return CONSISTENT
    if bound_hi is None and hi <= bound_lo: return CONSISTENT
    return CANNOT_TELL

def known_good(gate_fn, controls):
    """gate_fn(controls) -> True when the instrument reads the controls correctly. Returns (passed, message)."""
    try: ok = bool(gate_fn(controls))
    except Exception as e: return False, 'gate raised ' + type(e).__name__
    return ok, ('passed' if ok else 'FAILED: every reading in this run is CANNOT_TELL')

def apply_gate(passed, readings):
    """readings: list of dicts with an 'outcome'. When the gate failed, every outcome becomes CANNOT_TELL and the original is kept."""
    if passed: return readings
    out = []
    for r in readings:
        r = dict(r); r['outcome_before_gate'] = r.get('outcome'); r['outcome'] = CANNOT_TELL; out.append(r)
    return out

def plan_committed(plan_path, first_data_time=None):
    """True only if the plan file is tracked in git, unmodified, and (if first_data_time given, epoch seconds) its last commit is older than it."""
    d = os.path.dirname(os.path.abspath(plan_path)); f = os.path.basename(plan_path)
    try:
        if subprocess.run(['git', 'ls-files', '--error-unmatch', f], cwd=d, capture_output=True).returncode: return False
        if subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', f], cwd=d).returncode: return False
        t = int(subprocess.run(['git', 'log', '-1', '--format=%ct', '--', f], cwd=d, capture_output=True, text=True).stdout.strip())
    except Exception: return False
    return True if first_data_time is None else t <= first_data_time

def floor(false_flags, n_tests, threshold_rate=0.0027):
    """What a null world gives: expected false flags and the count above which a result exceeds chance (expected + 2 sqrt(expected))."""
    exp = n_tests * threshold_rate; return dict(expected=exp, exceeds=exp + 2 * math.sqrt(exp), observed=false_flags, above_chance=false_flags > exp + 2 * math.sqrt(exp))

def estimate_then_yes(estimate_text, yes):
    """Prints the estimate. Returns True only when yes is truthy. Nothing paid should run on False."""
    print(estimate_text)
    if not yes: print('not submitted (add --yes)'); return False
    return True

def selftest():
    ok = True; rng = random.Random(3)
    def check(name, cond): 
        nonlocal ok; ok &= bool(cond); print(('OK   ' if cond else 'FAIL ') + name)
    check('wilson empty is the full range', wilson(0, 0) == (0.0, 1.0))
    lo, hi = wilson(50, 100); check('wilson 50 of 100 contains 0.5', lo < 0.5 < hi)
    for name, p, bound_lo, bound_hi, want in (('share well above the bound', 0.5, 0.10, 0.25, ABOVE), ('share at the bound', 0.25, 0.10, 0.25, CANNOT_TELL), ('share well inside', 0.15, 0.10, 0.25, CONSISTENT), ('share well below', 0.02, 0.10, 0.25, BELOW)):
        right = 0
        for s in range(30):
            k = sum(1 for _ in range(400) if rng.random() < p); a, b = wilson(k, 400); right += classify(a, b, bound_lo, bound_hi) == want
        check('%s reads %s in %d of 30' % (name, want, right), right >= (27 if want != CANNOT_TELL else 15))
    check('missing interval is CANNOT_TELL', classify(None, None, 0.1, 0.2) == CANNOT_TELL and classify(float('nan'), 0.3, 0.1, 0.2) == CANNOT_TELL)
    p, msg = known_good(lambda c: c[0] < 2, [3]); out = apply_gate(p, [dict(outcome=ABOVE)]); check('failed gate turns ABOVE into CANNOT_TELL and keeps the original', (not p) and out[0]['outcome'] == CANNOT_TELL and out[0]['outcome_before_gate'] == ABOVE)
    p, _ = known_good(lambda c: c[0] < 2, [1]); check('passed gate leaves readings alone', p and apply_gate(p, [dict(outcome=ABOVE)])[0]['outcome'] == ABOVE)
    check('a gate that raises fails', known_good(lambda c: 1 / 0, [1])[0] is False)
    check('plan not in git is refused', plan_committed('/nonexistent/PLAN.md') is False)
    check('estimate without yes refuses', estimate_then_yes('cost about 10 s', False) is False and estimate_then_yes('cost about 10 s', True) is True)
    f = floor(5, 1000); check('floor expected 2.7 and 5 flags is not above chance', abs(f['expected'] - 2.7) < 1e-9 and not f['above_chance'])
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); return ok
if __name__ == '__main__': sys.exit(0 if selftest() else 1)
