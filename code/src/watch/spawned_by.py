#!/usr/bin/env python3
"""spawned_by.py -- WHO STARTED THIS RUN: the tick bus, or anyone else. (Bones, 13 Oct 2026, asked for by the rider-liveness track.)

The bus (watch/tick_bus.py) spawns its riders on her ticks, and the same rider run by hand writes the same rows into the same logs. For a
rider that fires every tick (wire_watch) the firing windows overlap, so time alone cannot tell a hand run from the bus's own. A run
therefore names its parent process, through outcomes.py:
    tick_bus       the parent's command line names tick_bus.py
    not_tick_bus   it does not (a shell, a hand run, launchd after the bus died)
    unread         ps could not be read -- an unread parent is a state, never a guess
Only the label is kept. The parent's command text is never stored or printed.

    import spawned_by; spawned_by.label()        # one ps call, 5 s at most
    python3 spawned_by.py --selftest             # offline; run it under BOTH Pythons
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outcomes import Outcomes   # noqa: E402

LABELS = ('tick_bus', 'not_tick_bus', 'unread')


def parent_outcomes():
    return Outcomes(subject=[('tick_bus', lambda c: isinstance(c, str) and 'tick_bus.py' in c),
                             ('not_tick_bus', lambda c: isinstance(c, str) and 'tick_bus.py' not in c)],
                    apparatus=[('unread', lambda c: not isinstance(c, str))])


def classify(cmd):
    """cmd: the parent's command line, or None when it could not be read"""
    counts = parent_outcomes().tally([cmd], "this run's parent")
    return [k for k, v in counts.items() if v][0]


def label(ppid=None, run=None):
    run = subprocess.run if run is None else run
    try:
        r = run(['ps', '-o', 'command=', '-p', str(os.getppid() if ppid is None else ppid)],
                capture_output=True, text=True, timeout=5)
        cmd = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    except Exception:          # no ps, a timeout, no such process: the parent was not read, and says so
        cmd = None
    return classify(cmd)


def selftest():
    n = 0

    class R:
        def __init__(self, rc, out):
            self.returncode, self.stdout = rc, out

    def fake(rc, out=None, exc=None):
        def f(cmd, **k):
            assert cmd[:3] == ['ps', '-o', 'command='] and k.get('timeout') == 5, (cmd, k)
            if exc:
                raise exc
            return R(rc, out)
        return f
    bus = '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/' \
          'MacOS/Python /Users/heuremen/bones-forge/watch/tick_bus.py\n'
    assert label(123, fake(0, bus)) == 'tick_bus'; n += 1
    assert label(123, fake(0, '-zsh\n')) == 'not_tick_bus' and label(1, fake(0, '/sbin/launchd\n')) == 'not_tick_bus'; n += 1
    assert label(123, fake(1, '')) == 'unread' and label(123, fake(0, '  \n')) == 'unread'; n += 1
    assert label(123, fake(0, exc=subprocess.TimeoutExpired('ps', 5))) == 'unread'; n += 1
    assert label(123, fake(0, exc=FileNotFoundError('ps'))) == 'unread'; n += 1
    assert label() in LABELS; n += 1                              # the real ps, on this very process's parent
    assert set(LABELS) == {k for k, _ in parent_outcomes().subject + parent_outcomes().apparatus}; n += 1
    print('spawned_by selftest PASS: %d checks  (python %s; this run: %s)' % (n, sys.version.split()[0], label()))
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        raise SystemExit(selftest())
    print(label())
