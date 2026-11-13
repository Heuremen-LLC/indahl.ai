#!/usr/bin/env python3
"""pps_pull.py -- read the Pi's GPSDO watch ON HER TICKS. (Bones, 9 Oct 2026.)

No crons, by standing order: periodic work rides her ticks. But the watch lives on the Pi and her
ticks live here, so this PULLS rather than the Pi pushing -- one ssh per tick, which costs nothing
against a ~250 s interval.

WHAT IT IS WATCHING FOR, and it is the fault that cost today: a GPSDO that stops steering reports
NOTHING. chrony's Reference ID quietly changes, root dispersion climbs, and every clock downstream
degrades while every log says fine. Silence read as health. The laptop sat like that for days with
the device plugged in, locked, and verified.

So this writes a flag HERE, where I read flags at session start, and the flag file existing always
means NOW -- it is deleted the moment the Pi reports OK again. A flag that only ever goes up
teaches you to ignore it.
"""
import json, os, subprocess, time

W = os.path.expanduser('~/bones-forge/watch/')
FLAG = os.path.join(W, 'PPS_FLAG.txt')
LOG = os.path.join(W, 'pps_pull.jsonl')


def main():
    try:
        p = subprocess.run(['ssh', '-o', 'ConnectTimeout=15', 'flock-pi',
                            'sudo -n /usr/local/bin/pps_watch.sh >/dev/null 2>&1; '
                            'tail -1 /var/log/pps_watch.log'],
                           capture_output=True, text=True, timeout=60)
        line = p.stdout.strip()
    except Exception as e:
        line = f'UNREACHABLE {type(e).__name__}: {e}'
    ok = ' OK ' in f' {line} '
    row = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'ok': ok, 'line': line}
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps(row) + '\n')
    except Exception:
        pass
    if ok:
        # cleared on the first good read, so the flag's presence always means now
        try:
            os.unlink(FLAG)
        except Exception:
            pass
    else:
        with open(FLAG, 'w') as f:
            f.write(f"GPSDO WATCH, {row['at']}\n{line}\n\n"
                    f"The Pi is the house's stratum-1 clock. If its reference is not PPS, every\n"
                    f"clock downstream is on network NTP and nothing else will tell you.\n")
    print(line)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
