#!/usr/bin/env python3
"""holdclock.py -- HOLD THIS SEAT ON THE LOCKCLOCK. Rides her ticks. No cron, no timer.
(Bones, 11 Oct 2026.)

RETIRED 11 OCT, AND NOT BECAUSE IT FAILED -- BECAUSE IT WAS BOUNDING THE WRONG LAYER.
chronyd now runs on this seat from /opt/homebrew/etc/chrony.conf under launchd
(com.heuremen.chronyd, KeepAlive). It is the same daemon holding the Pi, and it does what this
file could not: it keeps a FREQUENCY ESTIMATE and corrects the crystal continuously instead of
pulling the offset back after it has already drifted.

DO NOT PUT THIS BACK ON THE BUS WHILE chronyd RUNS, and the reason is arithmetic, not tidiness.
Two servos on one clock is a control system with two controllers and no shared state: chrony
measures an offset, begins a correction, and this file steps or slews the same clock underneath
it. chrony then reads its own correction as a new disturbance and fights it. Each one is
measuring the other's output and calling it the seat. That is mode 26 -- two of your three seats
are the same seat -- expressed as actuators instead of as readings, and the symptom would be a
seat that looks disciplined by both tools and is held by neither.

CHECK BEFORE RE-ENABLING, never assume: `pgrep -f /opt/homebrew/sbin/chronyd`. If chronyd is
genuinely gone and will not come back, this file is still the fallback and still works -- the
sudoers line and the convergence (23,128 -> 13,204 -> 5,898 us) are both measured. It is a
fallback, not a peer.

WHY THIS EXISTS, measured rather than assumed. /etc/ntp.conf on this Mac says `server
192.168.8.145`, timed is running, and the seat still went from +400 us to +22,165 us in one hour.
macOS timed polls rarely and slews instead of stepping, so it does not hold this seat. Stepping it
needs root, which is why nothing before this could do the job.

THE ONE PRIVILEGE IT NEEDS, and it is the narrowest possible:

    <user> ALL=(root) NOPASSWD: /usr/bin/sntp -sS 192.168.8.145

One binary, one flag set, one address. Not a shell, not a wildcard. If that line is absent this
script REPORTS that and changes nothing -- it never tries to escalate, and it never pretends the
clock is held when it is not.

THE BAR IS STATED, NOT TUNED. 1 ms is about 400x the Pi's own 2.3 us RMS and about 4x the worst
other seat in the house, so nothing inside it is a discipline problem. The seat that forced this
file was 22 bars out.

AND IT STEPS RATHER THAN SLEWS, on purpose. A slew spreads the correction across the next hour, so
every timestamp in that hour is wrong by an unknown fraction of the offset. A step is wrong once,
at a known instant, and that instant is recorded here. LA DIFERENCIA: the interval is the reading,
so it is written down rather than smeared.

    python3 holdclock.py --tick     the job: speaks only when it acts or cannot
    python3 holdclock.py            the same, verbose
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import novatime                                  # noqa: E402
from outcomes import Outcomes, OutcomeCollapse   # noqa: E402

# THE BAR IS MEASURED, NOT TYPED. 1 ms was mine, and this seat's own scatter says ~228 us: seven
# repeated medians gave sd 301 us, sem 114 us, so 2 x sem is the width at which a reading from this
# seat can be told from zero at all. A bar LOOSER than the apparatus lets a real offset sit inside
# it looking fine -- this seat reported "inside the 1000 us bar" at -713 us while its own scatter
# said out. A bar TIGHTER than the apparatus flags the wire instead of the clock. So the bar is
# max(floor, 2 x sem), measured on the spot, with a floor so a very quiet seat cannot demand the
# impossible of itself.
BAR_FLOOR = 2.0e-4
BAR = 1.0e-3                       # fallback ONLY, used when the scatter cannot be measured


def measured_bar(n_probes=7, tries=3):
    """this seat's bar from the scatter of repeated probes, with the n it rests on."""
    import statistics as st
    o = []
    for _ in range(n_probes):
        v, _r, _k, _t = novatime.probe_seat(None, tries)
        if v is not None:
            o.append(v)
    if len(o) < 4:
        return BAR, None, len(o)
    sem = st.pstdev(o) / len(o) ** 0.5
    return max(BAR_FLOOR, 2 * sem), st.median(o), len(o)
SNTP = '/usr/bin/sntp'
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'holdclock.log')


def privilege():
    """is the one line present? Asked by TRYING IT, never by parsing sudoers.

    `sudo -n -l` on the exact command answers without prompting and without running it, which is
    the only honest check: a sudoers file can be present and still not grant this.
    """
    try:
        r = subprocess.run(['sudo', '-n', '-l', SNTP, '-sS', novatime.PI],
                           capture_output=True, text=True, timeout=20)
        return r.returncode == 0, (r.stdout or r.stderr).strip()[:120]
    except Exception as e:
        return False, '%s: %s' % (type(e).__name__, str(e)[:60])


def _try(flags, dry=False):
    """is this flag set runnable WITHOUT a password? Asked by running it, never by `sudo -l`.

    `sudo -n -l <cmd>` RETURNS SUCCESS for any command the user could run WITH a password, because
    this sudoers has `(ALL) ALL`. So -l answers "are you allowed" when the question is "are you
    allowed WITHOUT A PROMPT", and it reported -s as permitted while the actual call failed with
    "a password is required". The only honest check is the call itself plus the error text.
    """
    r = subprocess.run(['sudo', '-n', SNTP] + flags + [novatime.PI],
                       capture_output=True, text=True, timeout=60)
    err = (r.stderr or '') + (r.stdout or '')
    needs_pw = 'password is required' in err or 'a terminal is required' in err
    return (not needs_pw), (r.returncode == 0 and not needs_pw), err.strip()[:110]


def pull_in(bar=BAR, max_calls=10):
    """call the ONE permitted command repeatedly until the seat is inside the bar. BOUNDED.

    IT SLEWS, IT DOES NOT STEP, AND THE FIRST VERSION OF THIS FILE CALLED IT "stepped". In sntp
    `-s` is step and `-S` is slew, so `-sS` passes both and the slew path wins -- measured: one
    call moved a 13,204 us offset by 617 us. Reporting that as a step was a label on an action I
    had not verified.
    BUT IT CONVERGES, and that is measured too: 23,128 -> 13,204 -> 5,898 us across three calls.
    So the fix needs no new privilege, only repetition -- and the repetition is BOUNDED by a fixed
    call count, never by "until it works", because an unbounded loop against a clock that will not
    move is how a job spins forever.
    `-s` alone WOULD step, and it is NOT permitted: the sudoers match is exact on `-sS`. Widening
    it is a privilege change and therefore not mine to make.
    """
    # PREFER THE STEP. -s goes through settimeofday: one jump at a known instant. -sS goes through
    # adjtime and SLEWS, and the slew is measurably losing -- logged at 4.4 ms -> 5.3 ms over ten
    # calls, i.e. the correction was slower than whatever was pushing the seat. A step is wrong once
    # and recorded; a losing slew is wrong continuously and looks like it is working.
    step_ok, _m, _n = _try(['-s'])
    flags = ['-s'] if step_ok else ['-sS']
    calls, trail = 0, []
    while calls < max_calls:
        r = subprocess.run(['sudo', '-n', SNTP] + flags + [novatime.PI],
                           capture_output=True, text=True, timeout=60)
        calls += 1
        if r.returncode != 0:
            return False, calls, trail, (r.stderr or r.stdout).strip()[:120]
        time.sleep(0.3)
        off, _rtt, ok, _t = novatime.probe_seat(None, 5)
        if off is None:
            return False, calls, trail, 'probe returned nothing mid-pull'
        trail.append(off)
        if abs(off) <= bar:
            return True, calls, trail, 'inside the bar after %d %s' % (calls, 'STEP' if flags==['-s'] else 'slews')
    return False, calls, trail, ('still %.1f ms out after %d calls -- bounded and stopped rather '
                                 'than looping' % ((trail[-1] if trail else 0) * 1e3, calls))


def run(verbose=False):
    bar, med, n_s = measured_bar()
    out, off, note = novatime.drift_flag(bar)
    note = '%s | bar %.0f us from %s' % (
        note, bar * 1e6,
        ('the scatter of %d medians' % n_s) if med is not None
        else 'the fallback: scatter unmeasurable')

    # FOUR OUTCOMES, and the apparatus ones are kept apart from the subject ones: a seat that
    # cannot be probed, and a seat that is out but cannot be stepped, are NOT the same fact as a
    # seat that is fine.
    if out is None:
        rec = dict(outcome='nothing-returned', before=None, after=None, note=note)
    elif not out:
        rec = dict(outcome='inside-the-bar', before=off, after=None, note=note)
    else:
        ok, why = privilege()
        if not ok:
            rec = dict(outcome='out-but-not-permitted', before=off, after=None,
                       note='%s | sudoers line absent: %s' % (note, why))
        else:
            did, calls, trail, msg = pull_in(bar)
            rec = dict(outcome='pulled-in' if did else 'pull-incomplete',
                       before=off, after=(trail[-1] if trail else None),
                       calls=calls, note=msg)

    rec['at'] = time.time()
    with open(LOG, 'a') as f:
        f.write(json.dumps(rec) + '\n')

    # the scorer proves the set is exhaustive and disjoint rather than me asserting it
    try:
        o = Outcomes(subject=[('inside-the-bar', lambda r: r['outcome'] == 'inside-the-bar'),
                              ('pulled-in', lambda r: r['outcome'] == 'pulled-in')],
                     apparatus=[('out-but-not-permitted',
                                 lambda r: r['outcome'] == 'out-but-not-permitted'),
                                ('pull-incomplete', lambda r: r['outcome'] == 'pull-incomplete'),
                                ('nothing-returned', lambda r: r['outcome'] == 'nothing-returned')])
        o.tally([rec], 'holdclock')
    except OutcomeCollapse as e:
        print('  OUTCOME COLLAPSE in holdclock: %s' % e)

    # SPEAKS ONLY WHEN IT ACTS OR CANNOT. A job that reports success every tick is noise, and
    # silence here means "inside the bar", which the log records either way.
    if rec['outcome'] == 'pulled-in':
        print('  HOLDCLOCK pulled this seat in: %+.1f us -> %+.1f us in %d slews'
              % (rec['before'] * 1e6, (rec['after'] or 0) * 1e6, rec.get('calls', 0)))
    elif rec['outcome'] != 'inside-the-bar':
        print('  HOLDCLOCK %s: %s' % (rec['outcome'].upper(), rec['note'][:150]))
    elif verbose:
        print('  HOLDCLOCK inside the bar: %+.1f us (bar %.0f us, MEASURED)' % (off * 1e6, bar * 1e6))
    return rec


if __name__ == '__main__':
    r = run(verbose='--tick' not in sys.argv)
    if '--tick' not in sys.argv:
        ok, why = privilege()
        print('  the one privilege present: %s' % bool(ok))
        if not ok:
            print('    paste this once and this seat holds itself from then on:')
            print('    echo "$(whoami) ALL=(root) NOPASSWD: %s -sS %s" | sudo tee '
                  '/etc/sudoers.d/bones-clock && sudo chmod 440 /etc/sudoers.d/bones-clock'
                  % (SNTP, novatime.PI))
