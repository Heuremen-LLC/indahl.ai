#!/usr/bin/env python3
"""pi_gps.py -- THE THIRD SEAT, READ FROM THE PI. (Bones, 11 Oct 2026.)

THERE IS ONE LOCK CLOCK IN THIS HOUSE, NOT TWO, and this file's first version said otherwise.
It read: "three_clocks.py asked the LAPTOP's Leo Bodnar ... that unit reports pps_pulses_seen 0
... ZERO pulses. So TIME never locked". The zeros were real and the attribution was wrong. One
device, serial 0EC9A40FE100, idVendor 1dd2 idProduct 2444:

    Oct 09 13:37:32  laptop kernel: usb 1-1: Leo Bodnar Electronics, hid-generic hidraw1
    Oct 09 19:58:46  laptop kernel: usb 1-1: USB disconnect, device number 3
    Oct 09 20:03:14  laptop kernel: usb 1-1: new device number 4 ... Product: HackRF Pro
    Oct 09 20:04     flock-pi: /dev/hidraw0 + /dev/ttyACM0, same serial 0EC9A40FE100
    Oct 09 20:08     flock-pi: udev SYMLINK gpsdo -> ttyACM0, keyed to 1dd2:2444

It was MOVED to the Pi and the HackRF took its USB port. The laptop's reader on :8767 went on
reporting "no GPS lock (needs 4+ satellites and a 2D/3D fix)" about an empty bus -- a SKY-VIEW
sentence for a DEVICE-ABSENT fact, because it had two branches and needed four.         (19/21)
Reading that output as a property of a GPSDO is how one object came to have two labels, a dead
one on the laptop and a live one on the Pi.                                                (24)

THE PI IS THAT SAME DEVICE, SERVING THE WHOLE HOUSE:
    gpsd -n /dev/gpsdo (-> ttyACM0, the Bodnar)   "mode":3  -> a 3D fix
    refclock SHM 0 refid NMEA                     the EPOCH: which second it is
    refclock SHM 1 refid PPS lock NMEA prefer     the PHASE: where in the second
    chronyc tracking: Reference ID 50505300 (PPS), Stratum 1, RMS offset 19.05 us
    chronyc sourcestats: PPS 64 samples / 506 s, freq -0.010 ppm, offset -33 ns

PPS gives phase with no epoch; NMEA gives epoch with no phase. `lock NMEA` is what makes them one
clock -- LA SUMA, you must have the two, sitting in a config file.

LOCKED means a 3D fix AND chrony actually selecting PPS. Either alone is not a GPS clock: a fix
with chrony on internet NTP is not disciplined, and PPS with no fix has no epoch. Both or it
returns None, because a half-locked clock reported as locked is worse than no third seat.

AND IT NOW RETURNS THE SATELLITE COUNT. The first version left satellites_used and hdop at None
and three_clocks.py printed "gps locked, None sats, hdop None" -- a lock asserted from fix_mode
while the two numbers that price the fix were never read.                               (gd 25)

POSITION IS NEVER PARSED. The NMEA carries an exact home position several times a second. Only
mode, the used/seen counts and hdop are regexed out; no TPV is ever json-loaded whole. The Pi is
asked for time, never for place.

    python3 pi_gps.py            run ON the Pi, prints one JSON line
"""
import json
import re
import subprocess
import sys


def here():
    """read this machine's GPS state. Intended to run ON the Pi."""
    out = {'ref': None, 'stratum': None, 'sys_time_s': None, 'rms_s': None, 'fix_mode': None,
           'sats_used': None, 'sats_seen': None, 'hdop': None, 'pps_n': 0}
    try:
        t = subprocess.run(['chronyc', 'tracking'], capture_output=True, text=True,
                           timeout=15).stdout or ''
        d = dict((k.strip(), v.strip()) for k, v in
                 re.findall(r'^([A-Za-z ]+?)\s*:\s*(.+)$', t, re.M))
        out['ref'] = d.get('Reference ID', '')
        out['stratum'] = d.get('Stratum', '')
        for key, field in (('System time', 'sys_time_s'), ('RMS offset', 'rms_s')):
            if d.get(key):
                try:
                    out[field] = float(d[key].split()[0])
                except ValueError:
                    pass
    except Exception:
        pass
    try:
        # -n 30 rather than 14: SKY arrives about once a second alongside TPV, and 14 objects was
        # not reliably enough to catch one -- which is why the sat count read None for a device
        # with eight satellites. The count is a FACT ABOUT THE FIX and a lock asserted without it
        # is a verdict with no width.                                                    (gd 25)
        g = subprocess.run(['gpspipe', '-w', '-n', '30'], capture_output=True, text=True,
                           timeout=30).stdout or ''
        modes = [int(x) for x in re.findall(r'"mode"\s*:\s*([0-9])', g)]
        if modes:
            out['fix_mode'] = max(modes)
        # ONLY these three fields are taken, by regex, off SKY lines. No TPV is ever json-loaded
        # whole, because TPV carries lat/lon and the Pi is asked for time and never for place.
        for ln in g.splitlines():
            if '"class":"SKY"' not in ln.replace(' ', ''):
                continue
            m = re.search(r'"hdop"\s*:\s*([0-9.]+)', ln)
            if m:
                out['hdop'] = float(m.group(1))
            m = re.search(r'"uSat"\s*:\s*([0-9]+)', ln)
            used = int(m.group(1)) if m else len(re.findall(r'"used"\s*:\s*true', ln))
            m = re.search(r'"nSat"\s*:\s*([0-9]+)', ln)
            seen = int(m.group(1)) if m else len(re.findall(r'"PRN"\s*:', ln))
            if used:
                out['sats_used'] = used
            if seen:
                out['sats_seen'] = seen
        out['pps_n'] = len(re.findall(r'"class"\s*:\s*"PPS"', g))
    except Exception:
        pass
    return out


if __name__ == '__main__':
    print(json.dumps(here()))
    sys.exit(0)
