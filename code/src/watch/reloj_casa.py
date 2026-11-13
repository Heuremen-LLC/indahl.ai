#!/usr/bin/env python3
"""reloj_casa.py -- HOW MANY CLOCKS DOES THIS HOUSE ACTUALLY HAVE? Asked of every machine.
(Bones, 11 Oct 2026. Rewritten the same day, because the first version was wrong about the
one object it was built to find.)

THE QUESTION THAT COST TWO DAYS: not "is this clock good" but "how many INDEPENDENT clocks are
there". The Bonefish needs three corners. Counting boxes gives six. Counting SYNC ROOTS gives the
real number, and nothing in the house computed it until this file.

                        EL TIEMPO
                           /\\
                EL MIRON -- EL TESTIGO

=============================================================================================
WITHDRAWN, 11 Oct, AND KEPT HERE BESIDE THE CORRECTION (guard 16). The first version of this
file printed, every twelve ticks:

    GPSDO (Leo Bodnar LBE-1421)   NOT A ROOT   BLIND: pps_pulses_seen 0, fix_mode None,
                                  satellites None -- antenna/sky view, not the clock
    THE LOCK CLOCK IS THE MISSING CORNER

EVERY WORD OF THAT WAS FALSE, and this is what the machines say instead:

    flock-pi  chronyc tracking   Reference ID 50505300 (PPS)   Stratum 1   RMS offset 19.05 us
    flock-pi  /dev/gpsdo -> ttyACM0, ID_VENDOR_ID=1dd2  ID_MODEL_ID=2444  (the Bodnar)
    flock-pi  gpsd -n /dev/gpsdo -> SHM 0 NMEA / SHM 1 PPS -> chrony refclock, prefer
    the device itself, via that gpsd:  fix_mode 3 (3D), 8 of 10 satellites used, hdop 0.6

THE LOCK CLOCK IS NOT THE MISSING CORNER. IT IS CORNER ONE. It is the oscillator the whole
house has been running on since 9 Oct 20:04, and it has a better sky view than anything else
here. "Why the fuck did I buy it?" -- because it is the reason this house has stratum-1 time.

HOW THE FIRST VERSION GOT IT WRONG, because the shape will come back:
  * It asked a MACHINE, not the DEVICE. the_gpsdo() curled the laptop's reader on :8767. The
    kernel log says the device left the laptop at 9 Oct 19:58:46 and appeared on the Pi at
    20:04. The reader was pinned to a host, so it answered about the host.                (37)
  * The reader it trusted CANNOT SAY "NO DEVICE". gps_clock_service.py had two branches, and
    printed "no GPS lock (needs 4+ satellites and a 2D/3D fix)" -- a SKY-VIEW diagnosis -- for
    a device that was not on the bus. A ruler that cannot say I CANNOT TELL lies at scale, and
    this one lied in the direction of a cheap physical excuse.                         (19/21)
  * I read the reader's output and never re-read through the consuming path.           (gd 31)
=============================================================================================

SO THE ROOT OF A SEAT IS A PHYSICAL OSCILLATOR, NOT THE MACHINE THAT SERVES IT. Each seat
declares its UPSTREAM -- the thing disciplining it -- and the roots are found by following those
chains to the end. That is the only structure that cannot double-count: the first version gave
one object two labels ('GPS (its own)' from the Pi, 'flock-pi' from its children) and reported 3
independent roots where there were 2. Terminal names are objects, so a chain cannot disagree
with itself.                                                                              (24)

MEASURED 11 Oct, every link READ from the machine and not inherited from a comment:

    Leo Bodnar LBE-1421   its own    GPS 3D fix, 8/10 sats, hdop 0.6, PPS -33 ns / 0.592 skew
      flock-pi            <- Bodnar  stratum 1, Reference ID PPS, via gpsd on /dev/gpsdo
        the Mac           <- Pi      stratum 2, Reference ID C0A80891 (flock-pi.lan)
        Armature          <- Pi      stratum 2, Source 192.168.8.145
        laptop            <- Pi      stratum 2, Reference ID C0A80891 (flock-pi.lan)
      HackRF Pro          <- Bodnar  CLKIN: clock signal detected; udev forces p1=p22_clkin
    Supabase              its own    Postgres created_at -- the only clock not downstream

ONE PHYSICAL OSCILLATOR AND ONE CLOUD CLOCK. The count of 2 was right all along; every
attribution under it was wrong, and so was the prescription.

AND THE HACKRF IS THE TRAP THIS BUILDS NEXT. Its sample clock is the Bodnar's 10 MHz, so every
timing a radio sweep yields is the SAME oscillator the Pi serves. Anyone who later compares
HackRF-derived timing to Pi-derived timing is reading one oscillator twice and will get a ratio
of 1 with a tight width.                                                                   (26)

SO A THIRD CORNER IS STILL MISSING AND IT IS NOT THE LOCK CLOCK. It has to be a clock that is
downstream of neither the Bodnar nor Supabase. What is already in the house and qualifies: the
RTL2838's own crystal on the laptop (the RTL-SDR, unlike the HackRF, is NOT fed from CLKIN), and
Armature's crystal if w32time is ever stopped and let free-run. Both are oscillators we own,
cabled, needing no antenna and no sky.

    python3 reloj_casa.py            every link asked, independent roots counted
    python3 reloj_casa.py --tick     the job: speaks only when the count changes
"""
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'reloj_casa.jsonl')
SSH = ['ssh', '-o', 'ConnectTimeout=12', '-o', 'BatchMode=yes']

# The Bodnar's USB identity, as the kernel reports it. Matched on this, never on a machine name,
# because the device moved hosts once already and the house did not notice for 35 hours.
GPSDO_VID, GPSDO_PID = '1dd2', '2444'
GPSDO = 'Leo Bodnar LBE-1421'
HOSTS = ('flock-pi', 'laptop')          # the machines we can ask with lsusb


def _sh(host, cmd, t=30):
    try:
        r = subprocess.run(SSH + [host, cmd], capture_output=True, text=True, timeout=t)
        return (r.stdout or '') + (r.stderr or '')
    except Exception as e:
        return 'ERR %s' % type(e).__name__


def _chrony_text(host=None, t=20):
    if host is None:
        try:
            return subprocess.run(['chronyc', 'tracking'], capture_output=True, text=True,
                                  timeout=15).stdout or ''
        except Exception as e:
            return 'ERR %s' % type(e).__name__
    return _sh(host, 'chronyc tracking', t)


def _refid(text):
    """(Reference ID, Stratum) out of `chronyc tracking`, raw. None when it did not answer."""
    ref = strat = None
    for ln in text.splitlines():
        if ln.startswith('Reference ID'):
            ref = ln.split(':', 1)[1].strip()
        elif ln.startswith('Stratum'):
            strat = ln.split(':', 1)[1].strip().split()[0]
    return ref, strat


def _upstream_from_refid(ref):
    """The name of the thing disciplining a chrony client, or 'SELF' for a hardware refclock.

    'SELF' is resolved by the CALLER to that seat's own upstream, which for the Pi is the Bodnar.
    Returning a label here instead is what produced one object under two names.            (24)
    """
    if not ref:
        return None
    low = ref.lower()
    if 'flock-pi' in low or 'c0a80891' in low:
        return 'flock-pi'
    if re.search(r'\b(pps|nmea|gps)\b', low):
        return 'SELF'
    return ref.split()[-1].strip('()')


# ----------------------------------------------------------------- the lock clock, located first

def locate_gpsdo():
    """WHICH MACHINE IS THE LOCK CLOCK ON? Asked of each host, never remembered.

    Four outcomes and they stay four: found / absent everywhere / no host answered / and the
    host list itself is partial (the Mac and Armature cannot be asked with lsusb), which is
    reported rather than folded into 'absent'.                                             (21)
    """
    asked, silent = [], []
    for h in HOSTS:
        t = _sh(h, 'lsusb 2>/dev/null')
        if t.startswith('ERR') or not t.strip():
            silent.append(h)
            continue
        asked.append(h)
        if '%s:%s' % (GPSDO_VID, GPSDO_PID) in t.lower():
            return {'host': h, 'asked': asked, 'silent': silent, 'outcome': 'found'}
    if not asked:
        return {'host': None, 'asked': asked, 'silent': silent, 'outcome': 'nothing-returned'}
    return {'host': None, 'asked': asked, 'silent': silent, 'outcome': 'absent-where-asked'}


def gpsdo_fix(host):
    """fix mode, satellites and hdop from that host's gpsd. POSITION IS NEVER REQUESTED.

    The NMEA carries an exact home position several times a second. The Pi is asked for time and
    never for place, and that is a filter in this code rather than a habit in whoever reads it.
    """
    prog = (
        'python3 - <<"PYEOF"\n'
        'import json, socket, time\n'
        'o={"mode":None,"sats_used":None,"sats_seen":None,"hdop":None,"pps_n":0}\n'
        'try:\n'
        '    s=socket.create_connection(("127.0.0.1",2947),timeout=5)\n'
        '    s.sendall(b\'?WATCH={"enable":true,"json":true};\\n\'); s.settimeout(5.0)\n'
        '    buf=b""; t0=time.time()\n'
        '    while time.time()-t0 < 5.0:\n'
        '        try: b=s.recv(8192)\n'
        '        except socket.timeout: break\n'
        '        if not b: break\n'
        '        buf+=b\n'
        '        for ln in buf.split(b"\\n")[:-1]:\n'
        '            try: d=json.loads(ln)\n'
        '            except Exception: continue\n'
        '            c=d.get("class")\n'
        '            if c=="SKY":\n'
        '                if d.get("hdop") is not None: o["hdop"]=d["hdop"]\n'
        '                if d.get("satellites"):\n'
        '                    o["sats_seen"]=len(d["satellites"])\n'
        '                    o["sats_used"]=sum(1 for x in d["satellites"] if x.get("used"))\n'
        '            elif c=="TPV": o["mode"]=d.get("mode")\n'
        '            elif c=="PPS": o["pps_n"]+=1\n'
        '        buf=buf.split(b"\\n")[-1]\n'
        '    s.close()\n'
        'except Exception as e: o["err"]="%s: %s"%(type(e).__name__,e)\n'
        'print(json.dumps(o))\n'
        'PYEOF'
    )
    t = _sh(host, prog, t=30)
    try:
        return json.loads(t[t.rindex('{'):t.rindex('}') + 1])
    except Exception:
        return {'err': 'gpsd on %s did not answer' % host}


def gpsdo_serves_time(host):
    """Does that host's chrony actually USE this device, or is it only drawing power there?

    This is the difference between a clock and a USB load, and it is read from the two config
    lines that make it true rather than assumed from the device being present.
    """
    dev = _sh(host, 'grep -h DEVICES /etc/default/gpsd 2>/dev/null; readlink -f /dev/gpsdo '
                    '2>/dev/null; udevadm info -q property -n /dev/gpsdo 2>/dev/null '
                    '| grep -E "ID_VENDOR_ID|ID_MODEL_ID"')
    wired = (GPSDO_VID in dev and GPSDO_PID in dev)
    ref, _ = _refid(_chrony_text(host))
    serving = bool(wired and ref and re.search(r'\b(PPS|NMEA)\b', ref))
    return {'wired_to_gpsd': wired, 'host_refid': ref, 'serving_time': serving}


def the_gpsdo():
    loc = locate_gpsdo()
    if loc['outcome'] != 'found':
        note = {'absent-where-asked': 'NOT ON THE BUS of %s -- and this is NOT a sky-view '
                                      'reading. Hosts not askable with lsusb: the Mac, Armature'
                                      % ', '.join(loc['asked']),
                'nothing-returned': 'NO HOST ANSWERED (%s silent) -- absence of an answer is '
                                    'not absence of the device' % ', '.join(loc['silent'])
                }[loc['outcome']]
        return {'name': GPSDO, 'upstream': None, 'stratum': None,
                'how': 'READ: lsusb %s:%s on each host' % (GPSDO_VID, GPSDO_PID),
                'note': note, 'outcome': loc['outcome']}

    h = loc['host']
    fix = gpsdo_fix(h)
    srv = gpsdo_serves_time(h)
    mode, used = fix.get('mode'), fix.get('sats_used')
    locked = mode in (2, 3) and (used or 0) >= 4
    bits = ['on %s' % h,
            'fix %s, %s of %s sats, hdop %s' % (mode, used, fix.get('sats_seen'), fix.get('hdop')),
            'SERVING TIME as that host\'s refclock' if srv['serving_time']
            else 'present but NOT wired into a time service (powered, not serving)']
    if not locked and 'err' not in fix:
        bits.append('NO FIX -- this one IS a sky-view reading, and it is read from the device')
    if 'err' in fix:
        bits.append('fix quality UNREAD: %s' % str(fix['err'])[:60])
    return {'name': GPSDO, 'upstream': 'SELF', 'stratum': '1' if locked else None,
            'how': 'READ: lsusb + that host\'s gpsd + chronyc',
            'note': ' | '.join(bits),
            'outcome': 'committed' if locked else 'held', 'host': h, 'fix': fix, 'serves': srv}


# --------------------------------------------------------------------------------- the machines

def a_pi(gpsdo_seat=None):
    """The Pi is a SERVER of a clock, and only its own root when nothing feeds it.

    11 Oct: it reads Reference ID 50505300 (PPS) stratum 1, and that PPS is the Bodnar's, via
    gpsd on /dev/gpsdo. So its upstream is the Bodnar -- naming the Pi as the root here is what
    hid an entire physical oscillator from the house's own inventory for a day.
    """
    ref, strat = _refid(_chrony_text('flock-pi'))
    up = _upstream_from_refid(ref)
    note = None
    if up == 'SELF':
        g = gpsdo_seat or {}
        if g.get('host') == 'flock-pi' and (g.get('serves') or {}).get('serving_time'):
            up = GPSDO
            note = 'its stratum 1 IS the Bodnar: gpsd /dev/gpsdo -> SHM PPS -> chrony refclock'
        else:
            note = 'serving a hardware refclock (%s) that this file could not attribute to a '
            note = (note % ref) + 'device -- NOT assumed to be its own oscillator'
    return {'name': 'flock-pi', 'upstream': up, 'stratum': strat,
            'how': 'READ: chronyc tracking over ssh', 'note': note}


def here_mac():
    t = _chrony_text(None)
    if t.startswith('ERR'):
        return {'name': 'the Mac', 'upstream': None, 'how': 'UNREAD: %s' % t}
    ref, strat = _refid(t)
    return {'name': 'the Mac', 'upstream': _upstream_from_refid(ref), 'stratum': strat,
            'how': 'READ: chronyc tracking, on this seat'}


def a_laptop():
    ref, strat = _refid(_sh('laptop', 'chronyc tracking 2>/dev/null'))
    return {'name': 'laptop', 'upstream': _upstream_from_refid(ref), 'stratum': strat,
            'how': 'READ: chronyc tracking over ssh'}


def a_armature():
    t = _sh('armature', 'cmd //c "w32tm /query /status"')
    up = strat = None
    for ln in t.splitlines():
        if ln.startswith('Stratum'):
            strat = ln.split(':', 1)[1].strip().split()[0]
        elif ln.startswith('Source') or ln.startswith('ReferenceId'):
            if '192.168.8.145' in ln or 'C0A80891' in ln.upper():
                up = 'flock-pi'
            elif up is None and ':' in ln:
                up = ln.split(':', 1)[1].strip()[:40]
    return {'name': 'Armature', 'upstream': up, 'stratum': strat,
            'how': 'READ: w32tm /query /status over ssh'}


def the_hackrf():
    """THE RADIO IS A CLOCK TOO, and it is not a spare one.

    Its P1 SMA is forced to p22_clkin by /etc/udev/rules.d/99-hackrf-clkin.rules, so when a clock
    arrives there the sample clock is that reference and not the HackRF's crystal. On 11 Oct CLKIN
    reports a signal while the Bodnar's USB is on the PI -- which is consistent, because the USB
    carries only power and configuration and the 10 MHz leaves by SMA regardless.

    It is listed so that nobody later puts a radio-derived timing beside a Pi-derived one and
    reads a ratio of 1 as agreement between two clocks.                                     (26)
    """
    t = _sh('laptop', 'timeout 20 hackrf_clock -i 2>&1')
    if 'clock signal detected' in t and 'no clock' not in t:
        return {'name': 'HackRF Pro (sample clock)', 'upstream': GPSDO, 'stratum': None,
                'how': 'READ: hackrf_clock -i over ssh',
                'note': 'CLKIN: clock signal detected, P1 routed to p22_clkin by udev -- SAME '
                        'OSCILLATOR AS THE PI, never a second seat'}
    if 'no clock signal' in t:
        return {'name': 'HackRF Pro (sample clock)', 'upstream': 'SELF', 'stratum': None,
                'how': 'READ: hackrf_clock -i over ssh',
                'note': 'CLKIN: no clock signal -- running on its OWN crystal, which makes it a '
                        'genuinely independent oscillator and a third-corner candidate'}
    return {'name': 'HackRF Pro (sample clock)', 'upstream': None, 'stratum': None,
            'how': 'READ attempted: hackrf_clock -i over ssh',
            'note': 'UNREAD: %s' % t.strip().splitlines()[-1][:70] if t.strip() else 'UNREAD'}


def the_codec():
    """EL TERCER RINCON: the laptop's ALC257 audio codec crystal. watch/cristal.py measures it.

    THE THIRD ROOT, and it needed no antenna, no cable and no purchase. Pooled over 6 runs of
    120-180 s, ~900 in-band points each off the codec's own hw_ptr counter:

        codec vs the LAPTOP's own clock  -3.930 ppm  sd 0.2965  sem 0.121  (n=6, NO network)
        codec vs the Bodnar              -3.934 ppm  +- 0.190   = 0.121 stat (+) 0.146 skew

    The first figure is what makes this a ROOT rather than a relabelled seat: a counter that
    differs from the Bodnar-disciplined system clock cannot BE that clock, and that comparison
    uses no path, no peer and no cable. The two impostors were named before the reading and both
    are excluded -- slaved to the corrected system clock (predicts 0.000, 20.7 widths) and
    derived from the platform oscillator (predicts -12.068, 42.9 widths, since chronyc reports
    the laptop's own oscillator 12.068 ppm slow while holding residual freq to -0.004).    (26)

    The ~0.3 ppm run-to-run spread IS this corner's stability, not noise: an earlier n=3 batch
    read sd 0.023 and I quoted +-0.013 ppm off it, which is reading three dice.      (fa 3, gd 9)

    IT IS NOT RE-MEASURED HERE. A reading costs 180 s and this file runs every 12 ticks, so the
    seat carries the LAST reading WITH ITS AGE -- a live quantity carries the moment it was read,
    and a cached rate presented as current is how a clock inventory starts lying again.   (fa 37)
    """
    try:
        import cristal
        d = cristal.last()
    except Exception as e:
        return {'name': 'ALC257 codec (laptop)', 'upstream': None, 'stratum': None,
                'how': 'UNREAD: %s' % type(e).__name__}
    if not d or d.get('outcome') != 'committed' or d.get('rate_ppm') is None:
        return {'name': 'ALC257 codec (laptop)', 'upstream': None, 'stratum': None,
                'how': 'READ: watch/cristal.py log',
                'note': 'NO COMMITTED READING ON FILE -- run `python3 cristal.py`. Rootless is '
                        'the honest state: an unmeasured oscillator is not a corner.'}
    try:
        age = (time.time() - time.mktime(time.strptime(d['at'][:19], '%Y-%m-%dT%H:%M:%S'))) / 60.0
    except Exception:
        age = float('nan')
    return {'name': 'ALC257 codec (laptop)', 'upstream': 'SELF', 'stratum': None,
            'how': 'READ: cristal.py, hw_ptr in band',
            'note': '%+.3f ppm vs the Bodnar (leg from chrony, not my echo), and %+.3f ppm vs '
                    'the laptop clock it would have to BE -- measured %.0f min ago, sweep %.3f ppm'
                    % (d.get('rate_ppm_via_chrony', d['rate_ppm']),
                       d.get('codec_vs_laptop_ppm',
                             d['rate_ppm'] + d.get('laptop_vs_pi_ppm', 0.0)),
                       age, d.get('sweep_spread_ppm') or float('nan'))}


def the_cloud():
    """the one clock we have that is not downstream of the Bodnar. DECLARED, and labelled so."""
    return {'name': 'Supabase (Postgres created_at)', 'upstream': 'SELF', 'stratum': None,
            'how': 'DECLARED, not read: a cloud host cannot be downstream of our Bodnar, and we '
                   'have no way to ask it what its root is. Independence from our tree is sound; '
                   'its absolute accuracy is UNMEASURED and nothing rests on it.',
            'note': 'ticks.log field 9, via nova_stamp.py'}


# --------------------------------------------------------------------- chains resolved to objects

def resolve(seats):
    """Follow every upstream to its end. The terminal name is a PHYSICAL OSCILLATOR.

    A chain that leaves the house (an upstream nobody here declares, e.g. a public NTP name) ends
    at that name, which is correct: it is a root we do not own and cannot read.
    """
    by = {s['name']: s for s in seats}
    for s in seats:
        if s.get('upstream') == 'SELF':
            s['upstream'] = s['name']
    roots = {}
    for s in seats:
        up, seen, hops = s.get('upstream'), {s['name']}, 0
        while up and up in by and up not in seen and hops < 12:
            seen.add(up)
            up = by[up].get('upstream')
            hops += 1
        s['root'] = up
        if up:
            roots.setdefault(up, []).append(s['name'])
    return roots


def read():
    g = the_gpsdo()
    seats = [g, a_pi(g), here_mac(), a_armature(), a_laptop(), the_hackrf(), the_codec(),
             the_cloud()]
    roots = resolve(seats)
    return {'at': time.time(), 'seats': seats, 'roots': roots,
            'n_independent': len(roots),
            'rootless': [s['name'] for s in seats if not s.get('root')]}


def main(tick=False):
    d = read()
    prev = None
    try:
        prev = json.loads(open(LOG).read().strip().splitlines()[-1])
    except Exception:
        pass
    with open(LOG, 'a') as f:
        f.write(json.dumps(d) + '\n')

    changed = (prev is None or prev.get('n_independent') != d['n_independent']
               or sorted(prev.get('roots') or {}) != sorted(d['roots']))
    if tick and not changed:
        return 0

    print('  HOW MANY CLOCKS DOES THIS HOUSE HAVE? Every link asked, none inherited.')
    print('  A ROOT IS A PHYSICAL OSCILLATOR, never the machine that serves it.\n')
    print('  %-30s%-22s%-9s%s' % ('seat', 'disciplined by', 'stratum', 'how'))
    for s in d['seats']:
        print('  %-30s%-22s%-9s%s'
              % (s['name'][:29], (s.get('upstream') or 'NOTHING (rootless)')[:21],
                 (s.get('stratum') or '-'), str(s.get('how'))[:30]))
        if s.get('note'):
            print('      %s' % str(s['note'])[:110])
    print('\n  INDEPENDENT ROOTS: %d' % d['n_independent'])
    for r, members in sorted(d['roots'].items()):
        print('    %-24s <- %s' % (r, ', '.join(members)))
    if d['rootless']:
        print('    ROOTLESS (upstream unread): %s' % ', '.join(d['rootless']))
    if d['n_independent'] < 3:
        print('\n  THE BONEFISH NEEDS THREE CORNERS AND THIS HOUSE HAS %d. A parent and its child'
              % d['n_independent'])
        print('  are not two clocks: a servo FORCES their rates equal, so no conversion can show')
        print('  through that pair. They do not agree, they are made to agree.')
        if GPSDO in d['roots']:
            print('  AND THE LOCK CLOCK IS CORNER ONE, NOT THE MISSING ONE -- it is the root of')
            print('  %d of these seats. A third corner has to be an oscillator downstream of'
                  % len(d['roots'][GPSDO]))
            print('  neither it nor Supabase: the RTL2838 crystal, or Armature free-running.')
    return 0


if __name__ == '__main__':
    sys.exit(main(tick='--tick' in sys.argv))
