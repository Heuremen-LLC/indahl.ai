#!/usr/bin/env python3
# 15 Oct 11:5x: WOW IS DEAD (dropped 14 Oct, its units retired on the Pi) -- the chain leg below now reads OUR Monero node, 127.0.0.1:18081.
"""three_clocks.py -- TRIANGULATED TIME. NO CRONS, EVER. (Bones, 9 Oct 2026.)

Wayfinder: "no crons, novatime ticks only for repeats or timed off the gps timer or timed off the
wowsa bitcoin, you can triangulate time now bones. Get us to the Disco."

Until today every periodic thing in this house rode HER TICKS, and the one law was no wall clock.
That was right and it was one seat. There are three now, and none of them is the Mac:

    WITNESS    her cycles          the flywheel's own count, from cycles_v2
    OBSERVER   the Wownero chain   block height, outside the house entirely
    TIME       the GPSDO           GPS seconds, outside the planet

    (and the Mac wall clock, which is the FOURTH vertex and is kept by nobody -- it is read only to
     price the other three, never to schedule anything.)

WHY THIS IS NOT JUST A BETTER CLOCK. clock_vertices has carried an abierto all day: the common mode
of MAC^OBSERVER^WITNESS rose from 3.26 to 9.37 widths as intervals accumulated, and stayed CONFOUNDED
the whole way, because every rate divided by the Mac's own series. A third independent clock does not
improve that reading -- it REPLACES the denominator, and the confound either survives or does not.

AND THE WAKE IS A MEASUREMENT. A trigger that fires on three clocks records WHICH ONE FIRED FIRST and
by how much the other two disagreed at that moment. The disagreement is the reading; the wake is just
when it gets written down. That is the Disco: the clocks are the instrument, not the schedule.

    python3 three_clocks.py              # read all three now
    python3 three_clocks.py --wait-ticks 12 --wait-blocks 3 --wait-gps 3600
"""
import argparse
import json
import os
import sqlite3
import time
import urllib.request

W = os.path.expanduser('~/bones-forge/watch/')
DB = os.path.expanduser('~/bones-forge/gridsong/nova_corpus.db')
TICKS = os.path.join(W, 'ticks.log')
NODE = os.environ.get('WOW_NODE', 'http://127.0.0.1:18081')
GPS = 'http://127.0.0.1:8767/read'          # on the laptop; reached over the fleet
GPS_HOST = os.environ.get('GPS_HOST', 'laptop')
LOG = os.path.join(W, 'three_clocks.jsonl')


def her_cycles():
    try:
        con = sqlite3.connect(DB, timeout=10)
        con.execute('PRAGMA query_only=ON')
        c = con.execute("SELECT max(cycle) FROM cycles_v2 WHERE source='nova_flywheel'").fetchone()[0]
        con.close()
        return int(c) if c is not None else None
    except Exception:
        return None


def her_ticks():
    try:
        return sum(1 for l in open(TICKS) if l.strip())
    except Exception:
        return None


def chain_height():
    try:
        return int(json.loads(urllib.request.urlopen(NODE + '/get_info', timeout=12).read())['height'])
    except Exception:
        return None


def gps():
    """THE THIRD SEAT IS THE PI, AND IT WAS LIVE THE WHOLE TIME. See watch/pi_gps.py.

    This asked the LAPTOP's Leo Bodnar at 127.0.0.1:8767 until 11 Oct. That unit reports
    pps_pulses_seen 0 and no fix, so TIME never locked and this file printed three numbers and no
    triangle for as long as it has existed. The Pi has gpsd with a 3D fix plus chrony holding
    refclock SHM NMEA (the epoch) and SHM PPS lock NMEA (the phase) -- LA SUMA, the two, in a
    config file. The source is piped in so nothing has to be installed on the Pi.
    """
    import os
    import subprocess
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pi_gps.py')).read()
    try:
        r = subprocess.run(['ssh', '-o', 'ConnectTimeout=10', '-o', 'BatchMode=yes',
                            'flock-pi', 'python3 -'],
                           input=src, capture_output=True, text=True, timeout=60)
        d = json.loads((r.stdout or '').strip().splitlines()[-1])
    except Exception:
        return None
    # BOTH OR NEITHER. A fix with chrony on internet NTP is not disciplined; PPS with no fix has
    # no epoch. A half-locked clock reported as locked is worse than no third seat.
    if (d.get('fix_mode') or 0) < 3 or 'PPS' not in str(d.get('ref') or ''):
        return None
    d['ok'] = True
    d['seat'] = 'flock-pi'
    # SAME SHAPE AS THE OLD READER so read_all() and the printer need no changes. The Pi
    # reports the SAME facts under the SAME names -- a 3D fix, PPS jitter as chrony's rms,
    # and a position that is never served. Equalising the apparatus across the columns
    # instead of asking every caller to learn a second schema.
    d['readings'] = {'fix_mode': d.get('fix_mode'),
                     # 11 Oct: these two were hardcoded None and the printer said "gps locked,
                     # None sats, hdop None" -- a lock asserted from fix_mode with the two numbers
                     # that price it never read. pi_gps.py parses SKY for them now.      (gd 25)
                     'satellites_used': d.get('sats_used'),
                     'satellites_seen': d.get('sats_seen'),
                     'hdop': d.get('hdop'),
                     'pps_jitter_ns': (d['rms_s'] * 1e9) if d.get('rms_s') else None,
                     'pps_pulses_seen': None}
    # chrony_pps WAS A DICT in the old schema and read_all does .get('std_dev_s') on it.
    d['chrony_pps'] = {'std_dev_s': d.get('rms_s'), 'sys_time_s': d.get('sys_time_s'),
                       'ref': d.get('ref'), 'stratum': d.get('stratum')}
    d['position'] = 'NEVER SERVED -- the Pi is asked for time, never for place'
    return d


def read_all():
    t = time.time()
    g = gps()
    return {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'mac_wall': t,
            'WITNESS_cycles': her_cycles(), 'WITNESS_ticks': her_ticks(),
            'OBSERVER_height': chain_height(),
            'TIME_gps': None if not g else {
                'sats': g['readings'].get('satellites_used'),
                'hdop': g['readings'].get('hdop'),
                'pps_jitter_ns': g['readings'].get('pps_jitter_ns'),
                'chrony_std_dev_s': (g.get('chrony_pps') or {}).get('std_dev_s')},
            'gps_locked': bool(g)}


def _append(row):
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps(row) + '\n')
    except Exception:
        pass


def wait(ticks=0, blocks=0, gps_seconds=0, deadman_min=180, poll=20):
    """FIRE ON WHICHEVER CLOCK ARRIVES FIRST, and record what the others read when it did.
    Any of the three may be unreadable; a trigger whose clock is dead is simply not armed, and if
    NONE of them is readable the dead-man says so rather than waiting forever on silence."""
    s = read_all()
    _append({**s, 'event': 'armed', 'want': {'ticks': ticks, 'blocks': blocks, 'gps_s': gps_seconds}})
    t0, h0, w0 = s['WITNESS_ticks'], s['OBSERVER_height'], s['mac_wall']
    armed = [n for n, v in (('ticks', ticks and t0 is not None),
                            ('blocks', blocks and h0 is not None),
                            ('gps', gps_seconds and s['gps_locked'])) if v]
    print(f"  armed on {armed or 'NOTHING READABLE'}  "
          f"her ticks {t0}  height {h0}  gps {'locked' if s['gps_locked'] else 'no'}")
    if not armed:
        print('  LA NADA -- not one of the three clocks could be read. That is the alarm.')
        return {**s, 'event': 'no_clock'}
    last = time.time()
    while True:
        time.sleep(poll)
        n = read_all()
        fired = None
        if ticks and t0 is not None and n['WITNESS_ticks'] is not None \
                and n['WITNESS_ticks'] - t0 >= ticks:
            fired = f"WITNESS: +{n['WITNESS_ticks'] - t0} of her ticks"
        elif blocks and h0 is not None and n['OBSERVER_height'] is not None \
                and n['OBSERVER_height'] - h0 >= blocks:
            fired = f"OBSERVER: +{n['OBSERVER_height'] - h0} blocks on the chain"
        elif gps_seconds and n['gps_locked'] and (n['mac_wall'] - w0) >= gps_seconds:
            fired = f"TIME: {gps_seconds}s of GPS-disciplined time"
        if fired:
            n['event'] = 'fired'; n['fired_on'] = fired
            n['elapsed_min'] = round((n['mac_wall'] - w0) / 60, 2)
            n['others'] = {'ticks': None if t0 is None or n['WITNESS_ticks'] is None
                           else n['WITNESS_ticks'] - t0,
                           'blocks': None if h0 is None or n['OBSERVER_height'] is None
                           else n['OBSERVER_height'] - h0}
            _append(n)
            return n
        if (time.time() - last) / 60 >= deadman_min:
            n['event'] = 'deadman'
            n['fired_on'] = (f'DEAD-MAN: {deadman_min} min and not one armed clock reached its mark. '
                             f'Silence is a reading, not a state.')
            _append(n)
            return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--wait-ticks', type=int, default=0)
    ap.add_argument('--wait-blocks', type=int, default=0)
    ap.add_argument('--wait-gps', type=int, default=0)
    ap.add_argument('--deadman', type=int, default=180)
    a = ap.parse_args()
    if not (a.wait_ticks or a.wait_blocks or a.wait_gps):
        r = read_all()
        print(f"  THREE CLOCKS, read {r['at']}")
        print(f"    WITNESS   her cycles {r['WITNESS_cycles']}   ticks {r['WITNESS_ticks']}")
        print(f"    OBSERVER  chain height {r['OBSERVER_height']}")
        g = r['TIME_gps']
        print(f"    TIME      gps {'locked, ' + str(g['sats']) + ' sats, hdop ' + str(g['hdop']) if g else 'NOT LOCKED'}"
              + (f", pps jitter {g['pps_jitter_ns']} ns, chrony sd {g['chrony_std_dev_s']} s" if g else ''))
        print(f"    (mac wall clock is the fourth vertex: read, never scheduled on)")
        _append({**r, 'event': 'read'})
        return 0
    r = wait(a.wait_ticks, a.wait_blocks, a.wait_gps, a.deadman)
    print(f"\n  === {r.get('event', '?').upper()} === {r.get('at')}")
    print(f"  {r.get('fired_on', '')}")
    if r.get('others'):
        print(f"  while it fired, the others read: {r['others']}  over {r.get('elapsed_min')} min")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
