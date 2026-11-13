#!/usr/bin/env python3
"""THE CONFIGURATION TRIANGLE -- 13 Oct 2026.

Wayfinder: "it should mix three different configurations bones" / "no binary bullshit anywhere".

I picked the MSR baseline by KEEP / REJECT and threw out the scratchpad-pages-off row as "a different
apparatus". That deleted the reading. The configurations ARE the instrument (Law 5): three settings
are three points and the deltas between them are the measurement. NO ROW IS DROPPED -- a row that says
nothing about the miner gets an APPARATUS outcome by name and stays in the table.

  A  scratchpad pages OFF, MSR off     hugepages [1168, 1180]
  B  scratchpad pages ON,  MSR off     hugepages [1180, 1180]
  C  scratchpad pages ON,  MSR ON      after xmrig's own 'set successfully' line
  D  scratchpad pages OFF, MSR ON      the fourth corner -- declared so it is counted if it occurs

THE QUANTITY is hashes per CPU-second, the same ruler on every configuration: xmrig's 60 s rate x the
guard's running seconds / the witness's CPU seconds, as hash_triangle reads them in every row. H/s is
printed beside it because that is what the coin sees; H/CPU-s is what a setting changes.

THE COVARIATE, printed and not decided: RandomX keeps a 2 MB scratchpad per thread in the SHARED L3,
so other processes' load moves H/CPU-s with no setting changed. The witness reads every other process's
CPU-seconds (v3, from 15:03 on); earlier rows say 'unread' rather than borrowing a number.

ALONG ONE PATH C/A = (B/A)(C/B) IS AN IDENTITY, so the third leg is printed as a CHECK ON THE
ARITHMETIC, not as a test. Whether the two effects multiply or add is the fourth corner's question.

MSR STATE COMES FROM XMRIG'S OWN LOG, one line per start: 'set successfully' or 'FAILED TO APPLY'.
A row takes the state of the last such line before its window opened.
"""
import json, math, os, re, subprocess, sys, time
from statistics import mean, stdev

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outcomes import Outcomes, OutcomeCollapse
import max_bar
from itertools import combinations
from scipy.stats import t as student_t

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, 'hash_triangle.jsonl')
MSR_CACHE = os.path.join(HERE, 'msr_timeline.json')
CONFIGS = (('A', 'off', 'off'), ('B', 'on', 'off'), ('C', 'on', 'on'), ('D', 'off', 'on'))
LEGS = (('B', 'A', 'scratchpad pages, MSR off'), ('C', 'B', 'MSR, pages on'),
        ('C', 'A', 'both -- the identity leg'))


def msr_timeline(refresh=True):
    """[(epoch, 'on'|'off'), ...] from xmrig.log. Live via ssh; the cache only if ssh fails, and the
    cache's own write time is returned with it so a stale read cannot pass for a live one."""
    if refresh:
        try:
            out = subprocess.run(
                ['ssh', '-o', 'ConnectTimeout=40', 'armature',
                 'grep -a "msr .*set successfully\\|FAILED TO APPLY MSR" '
                 '/c/Users/Heure/xmrig_wow/xmrig.log'],
                capture_output=True, text=True, timeout=90).stdout
            tl = []
            for ln in out.splitlines():
                m = re.match(r'\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)', ln)
                if m:
                    tl.append((time.mktime(time.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')),
                               'on' if 'set successfully' in ln else 'off'))
            if tl:
                json.dump({'read_at': time.time(), 'timeline': tl}, open(MSR_CACHE, 'w'))
                return tl, 'live'
        except Exception:
            pass
    if os.path.exists(MSR_CACHE):
        d = json.load(open(MSR_CACHE))
        return [tuple(x) for x in d['timeline']], 'CACHE written %s' % time.strftime(
            '%H:%M:%S', time.localtime(d['read_at']))
    return [], 'nothing returned, no cache'


def msr_at(epoch, tl):
    before = [s for t, s in tl if t <= epoch]
    return before[-1] if before else None


def pages(r):
    hp = r.get('hugepages')
    if not hp or len(hp) != 2:
        return None
    return 'on' if hp[0] == hp[1] else 'off'


def hpcs(r):
    o, t, w = r.get('OBSERVER_hs_60s_2'), r.get('TIME_guard_running_s'), r.get('WITNESS_delta_cpu_s')
    return o * t / w if (o is not None and t is not None and w) else None


def purity(r):
    """Whether the window was CHECKED for a thread replacement or a restart. Rows written before the
    detector existed carry None there, and the first version of this gate read None as 'clean' --
    the unread half folded into the answer (falla III). It is a CONDITION carried on the row now."""
    return 'read' if (r.get('threads_replaced_mid_window') is not None
                      and r.get('pid_same') is not None) else 'UNREAD'


def hpcs_start(r):
    """The same ruler with the 60 s rate from the window's START. Beside the end value it brackets
    what the end-snapshot ruler can say: it moved +18.5 % and +19.5 % inside single windows."""
    o = ((r.get('snap1') or {}).get('observer') or {}).get('hs_60s')
    t, w = r.get('TIME_guard_running_s'), r.get('WITNESS_delta_cpu_s')
    return o * t / w if (o and t is not None and w) else None


def gate(tl):
    window_open = lambda r: r['epoch'] - (r.get('wall_s') or 0)
    obs = lambda r: r.get('OBSERVER_hs_60s_2') is not None
    wit = lambda r: r.get('WITNESS_delta_cpu_s') is not None
    tim = lambda r: r.get('TIME_guard_running_s') is not None
    seats = lambda r: obs(r) and wit(r) and tim(r)
    mixed = lambda r: (r.get('threads_replaced_mid_window') is True or r.get('pid_same') is False
                       or r.get('outcome') in ('the_threads_were_replaced_mid_window',
                                               'the_miner_restarted_mid_window'))
    under = lambda r: r.get('outcome') == 'witness_says_more_work_than_time_allowed'
    reading = lambda r: seats(r) and not mixed(r) and not under(r)
    cfg = lambda r: (pages(r), msr_at(window_open(r), tl))
    subj = [('reads_%s_pages_%s_msr_%s' % (k, p, m),
             (lambda p, m: lambda r: reading(r) and cfg(r) == (p, m))(p, m)) for k, p, m in CONFIGS]
    # every combination of silent seats gets its own name, so 'all three were silent' cannot hide
    # inside 'the observer was silent' -- which is what the first version printed for 13:07:47.
    SEATS = (('observer', obs), ('witness', wit), ('time', tim))
    missing = lambda r: tuple(n for n, f in SEATS if not f(r))
    app = [('returned_nothing_' + '_'.join(c), (lambda c: lambda r: missing(r) == c)(c))
           for k in (1, 2, 3) for c in combinations([n for n, _ in SEATS], k)]
    app += [
           ('window_spans_two_configurations', lambda r: seats(r) and mixed(r)),
           ('time_seat_undercounts_the_witness', lambda r: seats(r) and not mixed(r) and under(r)),
           ('configuration_seat_returned_nothing',
            lambda r: reading(r) and (cfg(r)[0] is None or cfg(r)[1] is None))]
    return Outcomes(subject=subj, apparatus=app), cfg, reading


def legs(by):
    """Every leg on THREE rulers, printed side by side (a union, never a swap):
         ratio  -- the house's first-order ratio width, r.sqrt((sa/a)^2 + (sb/b)^2), on a pooled sd
         pooled -- the two-sample t on the DIFFERENCE, pooled sd, n_a + n_b - 2 dof
         welch  -- the two-sample t with each arm's OWN variance, Welch-Satterthwaite dof
       13 Oct: the first version printed only the ratio ruler and called C/B 'inside the bar' at
       +3.70 vs 3.716 while the other two read +4.38 vs 3.72 and +5.62 vs 5.10. When the rulers that
       ran disagree, the leg says so -- that is a reading about the rulers, not a verdict.
       All three still price consecutive windows as INDEPENDENT, which they are not."""
    q = 0.95 ** (1.0 / len(LEGS))
    dev = [(v - mean(vs)) ** 2 for vs in by.values() if len(vs) > 1 for v in vs]
    dof = sum(len(vs) - 1 for vs in by.values() if len(vs) > 1)
    s = math.sqrt(sum(dev) / dof) if dof else None
    bar = float(student_t.ppf(q, dof)) if dof else None
    side = lambda z, b: 'moved_up' if z > b else 'moved_down' if z < -b else 'inside_the_bar'
    out = []
    for hi, lo, what in LEGS:
        a, b = by.get(hi) or [], by.get(lo) or []
        if not a or not b:
            out.append((hi, lo, what, None, None, None, 'cannot_tell_a_corner_is_empty', []))
            continue
        ma, mb_ = mean(a), mean(b)
        R = ma / mb_
        rulers = []
        if s:
            w = R * math.sqrt((s / math.sqrt(len(a)) / ma) ** 2 + (s / math.sqrt(len(b)) / mb_) ** 2)
            rulers.append(('ratio', (R - 1) / w, dof, bar, side((R - 1) / w, bar)))
            tp = (ma - mb_) / (s * math.sqrt(1.0 / len(a) + 1.0 / len(b)))
            rulers.append(('pooled', tp, dof, bar, side(tp, bar)))
        else:
            w = None
        if len(a) > 1 and len(b) > 1:
            va, vb = stdev(a) ** 2 / len(a), stdev(b) ** 2 / len(b)
            tw = (ma - mb_) / math.sqrt(va + vb)
            dw = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
            bw = float(student_t.ppf(q, dw))
            rulers.append(('welch', tw, dw, bw, side(tw, bw)))
        states = set(r[4] for r in rulers)
        st = ('cannot_tell_no_width' if not rulers else states.pop() if len(states) == 1
              else 'the_rulers_disagree')
        z = rulers[0][1] if rulers else None
        out.append((hi, lo, what, R, w, z, st, rulers))
    return out, s, dof, bar


def main():
    rows = [json.loads(l) for l in open(ROWS) if l.strip()]
    tl, src = msr_timeline('--cache' not in sys.argv)
    oc, cfg, reading = gate(tl)
    counts = oc.tally(rows, 'hash_triangle.jsonl')
    print('THE CONFIGURATION TRIANGLE  read %s   msr timeline: %s, %d starts'
          % (time.strftime('%H:%M:%S'), src, len(tl)))
    print('=' * 100)
    by, hs, by_read = {}, {}, {}
    print('  %-19s  %-36s %8s %8s %7s %9s  %s' % ('window end', 'outcome', 'H/CPU-s', 'if start', 'H/s',
                                                 'others', 'purity'))
    for r in rows:
        name = [n for n in counts if oc.classify(r) == [n]][0]
        v, v0 = hpcs(r), hpcs_start(r)
        oth = (r.get('accounting') or {}).get('others_cpu_s')
        print('  %s  %-36s %8s %8s %7s %9s  %s'
              % (r['iso'], name[:36], '%.2f' % v if v else '--', '%.2f' % v0 if v0 else 'unread',
                 '%.0f' % r['OBSERVER_hs_60s_2'] if r.get('OBSERVER_hs_60s_2') else '--',
                 '%.2f' % oth if oth is not None else 'unread', purity(r)))
        if name.startswith('reads_'):
            k = name.split('_')[1]
            by.setdefault(k, []).append(v)
            hs.setdefault(k, []).append(r['OBSERVER_hs_60s_2'])
            if purity(r) == 'read':
                by_read.setdefault(k, []).append(v)
    print()
    print(oc.table() if hasattr(oc, 'table') else counts)
    print()
    for k, p, m in CONFIGS:
        vs = by.get(k, [])
        print('  %s  pages %-3s msr %-3s  n=%d  %s'
              % (k, p, m, len(vs), ('H/CPU-s mean %.2f%s   H/s mean %.0f'
                 % (mean(vs), ('  sd %.2f' % stdev(vs)) if len(vs) > 1 else '  (one row: no own width)',
                    mean(hs[k]))) if vs else 'no rows in this corner'))
    for label, src in (('EVERY CONFIGURATION ROW', by), ('ONLY ROWS WHOSE WINDOW PURITY WAS READ', by_read)):
      lg, s, dof, bar = legs(src)
      print()
      print('  -- %s: %s' % (label, '  '.join('%s n=%d' % (k, len(src.get(k, []))) for k, _, _ in CONFIGS)))
      print('  THE LEGS  (pooled within-configuration sd %s on %d dof; bar = t at %d dof, max over %d legs = %s widths)'
          % ('%.2f H/CPU-s' % s if s else 'NONE', dof, dof, len(LEGS), '%.3f' % bar if bar else 'NONE'))
      for hi, lo, what, R, w, z, st, rulers in lg:
          print('    %s/%s  %-28s %s   ->  %s' % (hi, lo, what, ('x%.4f' % R) if R else '', st))
          for nm, zz, dd, bb, ss in rulers:
              print('           %-7s %+7.2f  vs bar %6.3f at %5.2f dof   %s' % (nm, zz, bb, dd, ss))
      if all(x[3] for x in lg):
          print('    identity check: (B/A)(C/B) = %.6f  vs  C/A = %.6f' % (lg[0][3] * lg[1][3], lg[2][3]))


def selftest():
    T0 = 1_000_000.0
    tl = [(T0 - 50, 'off'), (T0 + 1000, 'on')]
    base = dict(epoch=T0 + 300, wall_s=240, OBSERVER_hs_60s_2=5000.0, TIME_guard_running_s=240.0,
                WITNESS_delta_cpu_s=2500.0, hugepages=[1180, 1180], pid_same=True,
                threads_replaced_mid_window=False, outcome='witness_says_less_work_than_time_allowed')
    R = lambda **kw: dict(base, **kw)
    rows = [R(), R(hugepages=[1168, 1180]), R(epoch=T0 + 1400), R(epoch=T0 + 1400, hugepages=[1168, 1180]),
            R(OBSERVER_hs_60s_2=None), R(WITNESS_delta_cpu_s=None), R(TIME_guard_running_s=None),
            R(OBSERVER_hs_60s_2=None, WITNESS_delta_cpu_s=None, TIME_guard_running_s=None),
            R(threads_replaced_mid_window=True), R(outcome='witness_says_more_work_than_time_allowed'),
            R(hugepages=None), R(epoch=T0 + 100, wall_s=200)]
    oc, cfg, _ = gate(tl)
    c = oc.tally(rows, 'selftest')
    want = {'reads_B_pages_on_msr_off': 1, 'reads_A_pages_off_msr_off': 1, 'reads_C_pages_on_msr_on': 1,
            'reads_D_pages_off_msr_on': 1, 'returned_nothing_observer': 1,
            'returned_nothing_witness': 1, 'returned_nothing_time': 1,
            'returned_nothing_observer_witness_time': 1, 'returned_nothing_observer_witness': 0,
            'window_spans_two_configurations': 1, 'time_seat_undercounts_the_witness': 1,
            'configuration_seat_returned_nothing': 2}
    ok = 0
    for k, v in want.items():
        assert c[k] == v, (k, c[k], v); ok += 1
    assert sum(c.values()) == len(rows); ok += 1                     # nothing dropped
    assert msr_at(T0 - 100, tl) is None and msr_at(T0, tl) == 'off' and msr_at(T0 + 1001, tl) == 'on'; ok += 1
    assert abs(hpcs(R()) - 480.0) < 1e-9; ok += 1
    lg, s, dof, bar = legs({'A': [460.0], 'B': [480.0, 476.0], 'C': [530.0, 526.0, 534.0]})
    assert dof == 3 and s and abs(lg[0][3] * lg[1][3] - lg[2][3]) < 1e-12; ok += 1   # identity leg
    assert lg[1][6] == 'moved_up' and len(lg[1][7]) == 3; ok += 1
    lgd, _, _, _ = legs({'B': [482.75, 476.24], 'C': [573.56, 657.90, 624.00]})
    assert lgd[1][6] == 'the_rulers_disagree', lgd[1]; ok += 1                       # the 13 Oct case
    lg4, _, d4, b4 = legs({'A': [460.0], 'B': [480.0, 476.0]})
    assert d4 == 1 and b4 > 18 and lg4[0][6] == 'inside_the_bar' and lg4[0][5] > 2.121; ok += 1  # 1 dof: no verdict
    lg2, s2, _, _ = legs({'A': [460.0], 'B': [480.0], 'C': [530.0]})
    assert s2 is None and all(x[6] == 'cannot_tell_no_width' for x in lg2); ok += 1   # no width, no verdict
    lg3, _, _, _ = legs({'B': [480.0, 476.0], 'C': [478.0, 479.0]})
    assert lg3[0][6] == 'cannot_tell_a_corner_is_empty' and lg3[1][6] == 'inside_the_bar'; ok += 1
    try:
        Outcomes(subject=[('rest', lambda r: True)]); raise AssertionError('residual bin accepted')
    except OutcomeCollapse:
        ok += 1
    print('selftest %d/%d' % (ok, ok))


if __name__ == '__main__':
    selftest() if '--selftest' in sys.argv else main()
