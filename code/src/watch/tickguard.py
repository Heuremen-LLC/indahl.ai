#!/usr/bin/env python3
"""tickguard.py -- A TICK JOB CANNOT OUTLIVE ITS OWN WINDOW. (Bones, 9 Oct 2026.)

Wayfinder: "Last night you set up a bunch of shells and got hung up and froze for like 6 hours. How we
not doing that tonight again?"

THE MECHANISM, and it is arithmetic rather than a worry. tick_bus launches every novatime job with a
bare subprocess.Popen -- no timeout, no wait, no new session. And bonefish_harness --tick ssh's seven
legs six times with a 90 s timeout per call, so its WORST CASE is about 27 minutes against a window of
three of her ticks, roughly 12.7 minutes. A job that overruns its window is still running when the
next copy launches, and then two copies ssh the same three hosts at once. That is the pile-up: not a
crash, a queue that never drains, which from the outside looks exactly like a freeze.

TWO GUARDS, AND THE SECOND IS THE ONE THAT MATTERS:

    THE LOCK      one copy at a time, per job name. A second copy finds the lock held and EXITS
                  QUIETLY -- it does not wait, because waiting is how a queue forms. A skipped tick
                  is a missing point; a queued tick is a frozen house.
    THE ALARM     a hard self-kill at `seconds`, well inside the window. SIGALRM cannot be swallowed
                  by a hung ssh the way a Python-level timeout can, because it fires in the parent and
                  takes the process down with its children.

WHY THE JOB GUARDS ITSELF RATHER THAN THE BUS GUARDING IT: a watchdog that kills the PID it tracked
never kills the worker that PID spawned. This house has paid for that lesson twice -- eleven orphaned
Ollama runners filling the Armature's card overnight on 22-23 Sept. The job holds its own leash, and
the lock file carries the PID so an orphan is identifiable without guessing.

    import tickguard
    tickguard.guard('bonefish_harness', 420)      # at the top, before any work
"""
import atexit
import os
import signal
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
LOCKDIR = os.path.join(W, 'locks')


def guard(name, seconds, stale_after=None):
    """one copy, and a hard ceiling. Returns only if this process may proceed."""
    os.makedirs(LOCKDIR, exist_ok=True)
    lock = os.path.join(LOCKDIR, f'{name}.lock')
    stale_after = stale_after or (seconds * 2)

    # A LOCK THAT OUTLIVES ITS HOLDER IS A DEADLOCK WITH A FILE ON IT. So the lock carries the PID and
    # the start time, and a lock whose process is gone -- or which is older than the ceiling allows --
    # is broken rather than respected.
    if os.path.exists(lock):
        try:
            txt = open(lock).read().split()
            pid, started = int(txt[0]), float(txt[1])
        except Exception:
            pid, started = -1, 0.0
        alive = False
        if pid > 0:
            try:
                os.kill(pid, 0)
                alive = True
            except (ProcessLookupError, PermissionError):
                alive = False
        age = time.time() - started
        if alive and age < stale_after:
            print(f'{name}: a copy has been running {age:.0f} s (pid {pid}); this tick is SKIPPED, '
                  f'not queued -- a missing point costs one reading, a queue costs the night.',
                  flush=True)
            raise SystemExit(0)
        if alive:
            # it is alive AND past the ceiling: it is the thing this guard exists to prevent
            print(f'{name}: pid {pid} has run {age:.0f} s, past the {stale_after:.0f} s ceiling. '
                  f'Killing it and its children, then taking the lock.', flush=True)
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(os.getpgid(pid), sig)
                except Exception:
                    try:
                        os.kill(pid, sig)
                    except Exception:
                        pass
                time.sleep(1.5)
                try:
                    os.kill(pid, 0)
                except Exception:
                    break
        else:
            print(f'{name}: a stale lock from pid {pid} ({age:.0f} s old, process gone). Breaking it.',
                  flush=True)

    with open(lock, 'w') as f:
        f.write(f'{os.getpid()} {time.time():.3f} {name}\n')

    def _release():
        try:
            if open(lock).read().split()[0] == str(os.getpid()):
                os.unlink(lock)
        except Exception:
            pass
    atexit.register(_release)

    def _fire(signum, frame):
        # the ceiling. Take the whole process group down, because the hang is almost always in a
        # child ssh and killing only the parent leaves the orphan that caused the problem.
        print(f'{name}: HIT THE {seconds} s CEILING and is killing itself. Whatever it was waiting '
              f'on did not come back -- that is the reading, and the next tick starts clean.',
              flush=True)
        _release()
        # ONLY killpg IF THIS PROCESS IS THE GROUP LEADER. tick_bus launches novatime jobs with a
        # bare Popen, so without start_new_session a job sits in TICK_BUS'S OWN process group -- and
        # killpg on that group would take the bus down with it. That is the same fault as a watchdog
        # killing the wrong PID, pointed at the parent instead of the child. start_new_session=True is
        # set on the bus side now, and this checks rather than trusts.
        try:
            if os.getpgid(0) == os.getpid():
                os.killpg(os.getpgid(0), signal.SIGKILL)
        except Exception:
            pass
        os._exit(9)

    signal.signal(signal.SIGALRM, _fire)
    signal.alarm(int(seconds))
    return True
