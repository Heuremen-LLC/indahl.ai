"""heuremen_kit.py: shared instrument pieces for the live corners of indahl.ai. See PLAN.md. Never touches the network itself (opener() only builds one). Run `python3 -I heuremen_kit.py` for the self-test."""
import math, subprocess, os, sys, random, urllib.request, warnings
ABOVE, BELOW, CONSISTENT, CANNOT_TELL, NOTHING_RETURNED = 'ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED'
OUTCOMES = (ABOVE, BELOW, CONSISTENT, CANNOT_TELL)
# Faults and Guards 2.0, section 6.3: the closed reasons for a CANNOT_TELL on a reading (12 Nov 2026).
STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE, NO_INTERVAL_FORMABLE = 'STRADDLES_EDGE', 'TOO_WIDE_TO_RESOLVE', 'NO_INTERVAL_FORMABLE'
REASONS = (STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE, NO_INTERVAL_FORMABLE)
STATUS_REASONS = ('NOT_RELEASED', 'UNREADABLE', 'METHOD_UNSTATED')   # for a status on a code, fault or guard, never on a reading

def wilson(k, n, z=1.96):
    """Wilson interval for a share k/n. n == 0 returns the full range."""
    if n <= 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))

def classify(lo, hi, bound_lo, bound_hi=None):
    """DEPRECATED 12 Nov 2026 (Faults and Guards 2.0): use read(). Kept unchanged so no desk breaks mid-migration. It has no reason, no both-alternatives
    test, and prints CONSISTENT for a lone bound, which 2.0 does not allow. The claim is that the true value lies in [bound_lo, bound_hi] (bound_hi None: at least bound_lo is not claimed, only bound_lo as a point).
    ABOVE: the whole interval is above bound_hi (or above bound_lo when no bound_hi). BELOW: the whole interval is below bound_lo.
    CONSISTENT: the whole interval is inside the bounds. CANNOT_TELL: otherwise, including a missing interval."""
    warnings.warn('heuremen_kit.classify() is deprecated; use read() (Faults and Guards 2.0)', DeprecationWarning, stacklevel=2)
    if lo is None or hi is None or (isinstance(lo, float) and math.isnan(lo)) or (isinstance(hi, float) and math.isnan(hi)): return CANNOT_TELL
    top = bound_hi if bound_hi is not None else bound_lo
    if lo > top: return ABOVE
    if hi < bound_lo: return BELOW
    if bound_hi is not None and lo >= bound_lo and hi <= bound_hi: return CONSISTENT
    if bound_hi is None and hi <= bound_lo: return CONSISTENT
    return CANNOT_TELL

def _bad(x): return x is None or (isinstance(x, float) and math.isnan(x))

def _edges(edge):
    """Edge convention as (lo_closed, hi_closed). 'closed' or '[]' both closed, '[)' open at hi, '(]' open at lo, '()' or 'open' both open.
    'open_hi' and 'open_lo' are accepted too. A plan states it before the read (standard 6.1)."""
    e = {'closed': (True, True), '[]': (True, True), '[)': (True, False), 'open_hi': (True, False), '(]': (False, True), 'open_lo': (False, True), '()': (False, False), 'open': (False, False)}
    if edge not in e: raise ValueError('unknown edge convention %r' % (edge,))
    return e[edge]

def read(lo, hi, band=None, bound=None, matters=None, edge='closed', null=0.0, direction='up'):
    """Faults and Guards 2.0, section 6.4, exactly. Returns (outcome, reason). reason is None unless the outcome is CANNOT_TELL, and then it is one of
    STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE, NO_INTERVAL_FORMABLE.
      [lo, hi]   the interval of the reading (same edge convention as the band).
      band       (band_lo, band_hi), two-sided. Only a band can give CONSISTENT. A point figure is a band: pass (figure - tol, figure + tol).
      bound      a single number: a one-sided threshold, or a point figure with no tolerance. Gives only ABOVE, BELOW or CANNOT_TELL.
      matters    the size that matters (a number above zero). With null it gives the alternative null + matters (direction 'up'), null - matters ('down'),
                 or both ('both'). If matters is None the both-alternatives test cannot be applied and is skipped (the plan has to say why).
      edge       'closed' (default), '[)' open at the upper edge, '(]' open at the lower edge, '()' both open.
    Order: 1 no interval; 2 both-alternatives test (the interval holds the null and the null plus or minus the size); 3 ABOVE, BELOW, CONSISTENT; 4 STRADDLES_EDGE."""
    if (band is None) == (bound is None): raise ValueError('give exactly one of band or bound')
    if _bad(lo) or _bad(hi) or lo > hi: return CANNOT_TELL, NO_INTERVAL_FORMABLE
    if matters is not None:
        if matters <= 0: raise ValueError('matters must be above zero')
        if direction not in ('up', 'down', 'both'): raise ValueError('direction is up, down or both')
        alts = ([null + matters] if direction in ('up', 'both') else []) + ([null - matters] if direction in ('down', 'both') else [])
        if lo <= null <= hi and any(lo <= a <= hi for a in alts): return CANNOT_TELL, TOO_WIDE_TO_RESOLVE
    lc, hc = _edges(edge)
    if band is not None:
        bl, bh = band
        if bl > bh: raise ValueError('band is (low, high)')
        above = lo > bh if hc else lo >= bh
        below = hi < bl if lc else hi <= bl
        inside = (lo >= bl if lc else lo > bl) and (hi <= bh if hc else hi < bh)
        if above: return ABOVE, None
        if below: return BELOW, None
        if inside: return CONSISTENT, None
        return CANNOT_TELL, STRADDLES_EDGE
    if lo > bound or (lo == bound and not hc): return ABOVE, None
    if hi < bound or (hi == bound and not lc): return BELOW, None
    return CANNOT_TELL, STRADDLES_EDGE

def read_exact(value, band=None, bound=None, edge='closed'):
    """O1 (owner, 12 Nov 2026): an exact row-level read with no sampling is an interval of zero width. Returns (outcome, reason, signed_difference).
    With a band it reads ABOVE, BELOW or inside it (CONSISTENT) and never STRADDLES_EDGE or TOO_WIDE. With only a bound and no tolerance there is no outcome:
    outcome is None, reason None, and the signed difference from the bound is returned for the page to print. A value that cannot be read gives NO_INTERVAL_FORMABLE."""
    if _bad(value): return CANNOT_TELL, NO_INTERVAL_FORMABLE, None
    if band is not None:
        o, r = read(value, value, band=band, edge=edge); mid = (band[0] + band[1]) / 2.0
        return o, r, value - mid
    if bound is None: raise ValueError('give band or bound')
    d = value - bound
    if d > 0: return ABOVE, None, d
    if d < 0: return BELOW, None, d
    return None, None, 0.0

def req13(readings, nothing_returned=0, status=False):
    """REQ-13 (standard 6.7). readings: the readings that count, each an (outcome, reason) pair from read() or a dict with 'outcome' and 'reason'.
    nothing_returned: the failed reads, as a count or a list. They are outside the headline numerator and denominator.
    Returns a dict: nothing_returned, n_readings, cannot_tell, cannot_tell_by_reason (adds up to cannot_tell), cannot_tell_share ('k of n'), line (text for the page).
    A CANNOT_TELL with no reason is counted under MISSING_REASON so it shows and the counts still add up."""
    nr = len(nothing_returned) if hasattr(nothing_returned, '__len__') else int(nothing_returned)
    by = {}; n = 0; ct = 0
    for r in readings:
        o, why = (r.get('outcome'), r.get('reason')) if isinstance(r, dict) else (r[0], r[1])
        n += 1
        if o == CANNOT_TELL: ct += 1; why = why or 'MISSING_REASON'; by[why] = by.get(why, 0) + 1
    split = ', '.join('%d %s' % (v, k) for k, v in sorted(by.items())) if by else 'none'
    line = '%d NOTHING_RETURNED. CANNOT_TELL %d of %d (%s).' % (nr, ct, n, split)
    return dict(nothing_returned=nr, n_readings=n, cannot_tell=ct, cannot_tell_by_reason=by, cannot_tell_share='%d of %d' % (ct, n), line=line)

def _pct(sorted_vals, q):
    i = q * (len(sorted_vals) - 1); a = int(math.floor(i)); b = min(a + 1, len(sorted_vals) - 1); return sorted_vals[a] + (sorted_vals[b] - sorted_vals[a]) * (i - a)

def bootstrap(units, stat, draws=2000, seed=0, level=0.95):
    """Seeded percentile bootstrap over units (a list: rows, storms, years, days). stat(list) -> number. Returns (lo, hi, method) where method is the
    string a plan names (unit count, draws, seed, level). Fewer than 2 units: (None, None, method) so read() gives NO_INTERVAL_FORMABLE."""
    method = 'percentile bootstrap over %d units, %d draws, seed %s, %g percent' % (len(units), draws, seed, level * 100)
    if len(units) < 2: return None, None, method
    rng = random.Random(seed); n = len(units); vals = []
    for _ in range(draws):
        try: vals.append(stat([units[rng.randrange(n)] for _ in range(n)]))
        except ZeroDivisionError: pass
    vals = sorted(v for v in vals if not _bad(v))
    if len(vals) < max(2, draws // 2): return None, None, method
    a = (1 - level) / 2.0; return _pct(vals, a), _pct(vals, 1 - a), method

def block_bootstrap(units, stat, block, draws=2000, seed=0, level=0.95):
    """Seeded moving-block bootstrap over an ordered list (weeks, months, days). Blocks of `block` consecutive units are drawn with replacement and joined,
    cut to the original length. Returns (lo, hi, method)."""
    n = len(units); method = 'moving-block bootstrap over %d ordered units, blocks of %d, %d draws, seed %s, %g percent' % (n, block, draws, seed, level * 100)
    if n < 2 or block < 1: return None, None, method
    block = min(block, n); rng = random.Random(seed); starts = n - block + 1; need = -(-n // block); vals = []
    for _ in range(draws):
        s = []
        for _ in range(need):
            i = rng.randrange(starts); s.extend(units[i:i + block])
        try: vals.append(stat(s[:n]))
        except ZeroDivisionError: pass
    vals = sorted(v for v in vals if not _bad(v))
    if len(vals) < max(2, draws // 2): return None, None, method
    a = (1 - level) / 2.0; return _pct(vals, a), _pct(vals, 1 - a), method

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

class _Follow308(urllib.request.HTTPRedirectHandler):
    """9 Nov 2026 (site pass M14): urllib before Python 3.11 has no handler for HTTP 308 and returns it as an error. A 308 is followed the way a 307 is
    (RFC 9110: same method, same body), so a desk reads the same thing on every Python."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return super().redirect_request(req, fp, 307 if code == 308 else code, msg, headers, newurl)
    http_error_308 = urllib.request.HTTPRedirectHandler.http_error_302

def opener(*handlers):
    """An urllib opener that follows 301, 302, 303, 307 and 308 on every Python version. Use opener().open(request, timeout=...)."""
    return urllib.request.build_opener(_Follow308(), *handlers)

def _planted_308():
    """Self-test: a local server answers /a with a 308 to /b, and /b with 200. opener() must land on /b."""
    import http.server, threading
    class Hd(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/a': self.send_response(308); self.send_header('Location', '/b')
            else: self.send_response(200)
            self.send_header('Content-Length', '0'); self.end_headers()
        def log_message(self, *a): pass
    s = http.server.HTTPServer(('127.0.0.1', 0), Hd); threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        r = opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:%d/a' % s.server_port, timeout=10); return r.status == 200 and r.geturl().endswith('/b')
    except Exception: return False
    finally: s.shutdown(); s.server_close()

def floor(false_flags, n_tests, threshold_rate=0.0027):
    """What a null world gives: expected false flags and the count above which a result exceeds chance (expected + 2 sqrt(expected))."""
    exp = n_tests * threshold_rate; return dict(expected=exp, exceeds=exp + 2 * math.sqrt(exp), observed=false_flags, above_chance=false_flags > exp + 2 * math.sqrt(exp))

def estimate_then_yes(estimate_text, yes):
    """Prints the estimate. Returns True only when yes is truthy. Nothing paid should run on False."""
    print(estimate_text)
    if not yes: print('not submitted (add --yes)'); return False
    return True

def _raises(fn):
    try: fn()
    except ValueError: return True
    return False

def selftest():
    warnings.simplefilter('ignore', DeprecationWarning)
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
    check('a 308 redirect is followed (local server)', _planted_308())
    # Faults and Guards 2.0 read(): planted cases (12 Nov 2026)
    C = lambda name, got, want: check('read: %s -> %s' % (name, want[0] if want[1] is None else '%s %s' % want), got == want)
    B = (0.0, 0.15)
    C('worked example 6.8, [0, 0.125] holds 0 and 0.05, band [0,0.15) matters 0.05', read(0.0, 0.125, band=B, matters=0.05, edge='[)'), (CANNOT_TELL, TOO_WIDE_TO_RESOLVE))
    C('both-alternatives wins even wholly inside the band', read(0.0, 0.14, band=B, matters=0.05), (CANNOT_TELL, TOO_WIDE_TO_RESOLVE))
    C('inside band, holds size but not null', read(0.06, 0.12, band=B, matters=0.05), (CONSISTENT, None))
    C('inside band, holds neither', read(0.01, 0.04, band=B, matters=0.05), (CONSISTENT, None))
    C('interval over the band', read(0.20, 0.30, band=B, matters=0.05), (ABOVE, None))
    C('interval under a band', read(0.01, 0.04, band=(0.10, 0.20)), (BELOW, None))
    C('straddles the upper band edge', read(0.10, 0.20, band=B, matters=0.05), (CANNOT_TELL, STRADDLES_EDGE))
    C('straddles the lower band edge', read(0.05, 0.25, band=(0.10, 0.20)), (CANNOT_TELL, STRADDLES_EDGE))
    C('closed edge: l equal to band_hi is not above', read(0.15, 0.30, band=B), (CANNOT_TELL, STRADDLES_EDGE))
    C('open hi: l equal to band_hi is above', read(0.15, 0.30, band=B, edge='[)'), (ABOVE, None))
    C('closed edge: u equal to band_hi is inside', read(0.05, 0.15, band=B), (CONSISTENT, None))
    C('open hi: u equal to band_hi is not inside', read(0.05, 0.15, band=B, edge='[)'), (CANNOT_TELL, STRADDLES_EDGE))
    C('closed edge: u equal to band_lo is not below', read(0.0, 0.10, band=(0.10, 0.20)), (CANNOT_TELL, STRADDLES_EDGE))
    C('open lo: u equal to band_lo is below', read(0.0, 0.10, band=(0.10, 0.20), edge='(]'), (BELOW, None))
    C('open lo: l equal to band_lo is not inside', read(0.10, 0.15, band=(0.10, 0.20), edge='(]'), (CANNOT_TELL, STRADDLES_EDGE))
    C('one-sided: above the bound', read(0.30, 0.40, bound=0.25), (ABOVE, None))
    C('one-sided: below the bound is BELOW, never CONSISTENT', read(0.01, 0.04, bound=0.05), (BELOW, None))
    C('one-sided: straddling the bound', read(0.03, 0.07, bound=0.05), (CANNOT_TELL, STRADDLES_EDGE))
    C('one-sided: both alternatives still applies', read(0.0, 0.08, bound=0.25, matters=0.05), (CANNOT_TELL, TOO_WIDE_TO_RESOLVE))
    C('point figure, no tolerance, inside the interval: never CONSISTENT', read(0.40, 0.60, bound=0.50), (CANNOT_TELL, STRADDLES_EDGE))
    C('point figure, no tolerance, interval above', read(0.55, 0.60, bound=0.50), (ABOVE, None))
    C('point figure, no tolerance, interval below', read(0.40, 0.45, bound=0.50), (BELOW, None))
    C('point figure with tolerance, inside', read(0.48, 0.52, band=(0.45, 0.55)), (CONSISTENT, None))
    C('point figure with tolerance, wide interval', read(0.30, 0.70, band=(0.45, 0.55)), (CANNOT_TELL, STRADDLES_EDGE))
    C('no interval (None)', read(None, None, band=B), (CANNOT_TELL, NO_INTERVAL_FORMABLE))
    C('no interval (NaN)', read(float('nan'), 0.3, bound=0.1), (CANNOT_TELL, NO_INTERVAL_FORMABLE))
    C('no interval beats the both-alternatives test', read(None, 0.3, band=B, matters=0.05), (CANNOT_TELL, NO_INTERVAL_FORMABLE))
    C('zero-width interval inside a band', read(0.10, 0.10, band=B), (CONSISTENT, None))
    C('direction down: holds null and null minus size', read(-0.08, 0.02, band=(-0.20, 0.20), matters=0.05, direction='down'), (CANNOT_TELL, TOO_WIDE_TO_RESOLVE))
    C('direction down: size above is not reached', read(0.0, 0.08, band=(-0.20, 0.20), matters=0.05, direction='down'), (CONSISTENT, None))
    C('direction both: either side counts', read(-0.07, 0.01, band=(-0.20, 0.20), matters=0.05, direction='both'), (CANNOT_TELL, TOO_WIDE_TO_RESOLVE))
    check('read refuses band and bound together', _raises(lambda: read(0, 1, band=B, bound=0.5)))
    check('read refuses an unknown edge', _raises(lambda: read(0, 1, band=B, edge='x')))
    # read_exact (owner O1)
    check('exact read inside a band is CONSISTENT', read_exact(0.10, band=B)[:2] == (CONSISTENT, None))
    check('exact read over a band is ABOVE', read_exact(0.30, band=B)[:2] == (ABOVE, None))
    check('exact equality with no tolerance has no outcome word', read_exact(5, bound=5) == (None, None, 0.0))
    check('exact read with no tolerance reports the signed difference', read_exact(7, bound=5) == (ABOVE, None, 2) and read_exact(3, bound=5)[2] == -2)
    check('exact read of nothing is NO_INTERVAL_FORMABLE', read_exact(None, band=B)[:2] == (CANNOT_TELL, NO_INTERVAL_FORMABLE))
    # REQ-13
    q = req13([(ABOVE, None), (CANNOT_TELL, TOO_WIDE_TO_RESOLVE), (CANNOT_TELL, STRADDLES_EDGE), (CANNOT_TELL, TOO_WIDE_TO_RESOLVE), (CONSISTENT, None)], nothing_returned=['a', 'b'])
    check('req13 counts the failed reads apart', q['nothing_returned'] == 2 and q['n_readings'] == 5)
    check('req13 reasons add up to the CANNOT_TELL count', q['cannot_tell'] == 3 and sum(q['cannot_tell_by_reason'].values()) == 3 and q['cannot_tell_by_reason'] == {STRADDLES_EDGE: 1, TOO_WIDE_TO_RESOLVE: 2})
    check('req13 line', q['line'] == '2 NOTHING_RETURNED. CANNOT_TELL 3 of 5 (1 STRADDLES_EDGE, 2 TOO_WIDE_TO_RESOLVE).')
    check('req13 shows a CANNOT_TELL with no reason', req13([dict(outcome=CANNOT_TELL)])['cannot_tell_by_reason'] == {'MISSING_REASON': 1})
    check('req13 on nothing', req13([])['cannot_tell_share'] == '0 of 0' and req13([])['nothing_returned'] == 0)
    # bootstraps: seeded, repeatable, cover the truth
    _r = random.Random(99); data = [_r.random() * 10 for _ in range(70)]; mean = lambda v: sum(v) / len(v)
    a = bootstrap(data, mean, draws=500, seed=11); b = bootstrap(data, mean, draws=500, seed=11); c = bootstrap(data, mean, draws=500, seed=12)
    check('bootstrap same seed same interval, other seed differs', a == b and a[:2] != c[:2])
    check('bootstrap interval holds the sample mean', a[0] < mean(data) < a[1] and 'seed 11' in a[2] and '500 draws' in a[2])
    a = block_bootstrap(data, mean, 7, draws=500, seed=5); b = block_bootstrap(data, mean, 7, draws=500, seed=5)
    check('block bootstrap repeatable and holds the mean', a == b and a[0] < mean(data) < a[1] and 'blocks of 7' in a[2] and 'seed 5' in a[2])
    check('one unit has no interval, so read() says NO_INTERVAL_FORMABLE', read(*bootstrap([1.0], mean, 10, 1)[:2], band=B) == (CANNOT_TELL, NO_INTERVAL_FORMABLE))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always'); classify(0.1, 0.2, 0.0, 0.3); check('classify still works and warns it is deprecated', any(issubclass(x.category, DeprecationWarning) for x in w))
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); return ok
if __name__ == '__main__': sys.exit(0 if selftest() else 1)
