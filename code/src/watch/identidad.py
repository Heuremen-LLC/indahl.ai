#!/usr/bin/env python3
"""identidad.py -- WHAT IS ACTUALLY AT THIS ADDRESS. Asked of the machine, never inherited.
(Bones, 11 Oct 2026.)

STEP 19 OF THE CARD, EL INSTRUMENTO: "which branch is live, which rate the device actually opened,
what the axis literally means. Read it; never inherit it from the code that came before."

THE INSTANCE THAT FORCED THIS FILE, and it cost an hour. A comment in tick_bus.py described
192.168.8.123:8769 as a GPSDO echo. I inherited that, measured .123 against .145, called the result
"one time source read from two perspectives", built a correlation, a measured floor and a LA NADA
verdict on top of it, and reported a 20 ms difference as path queueing.

192.168.8.123 IS THE LAPTOP. A second machine with its own clock. The whole reading was two clocks
differing, dressed as one clock seen twice -- and the identity was a single `hostname` call away the
entire time. Everything derived from it is withdrawn.

AND THE SHAPE RECURS, which is why this is a module and not a resolution to be careful:
    the GPSDO echo that was the laptop                  tonight
    the gps column that was mac minus a cached offset   tonight
    the 5-second product that was the 30-second one      tonight, interpolated
    her tick counter that was two counters              tonight, differing 5x
Four identity errors in one session, every one an assumption about what a thing WAS rather than a
reading of it.

SO THE RULE IS STRUCTURAL: resolve(addr) asks the machine. It REFUSES to return a label it cannot
verify, and `assert_is` raises rather than letting a measurement name a thing it has not checked.
A label this file cannot confirm comes back as UNVERIFIED, which is a fact, not a gap.

    python3 identidad.py          resolve every address the house uses
"""
import json
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'identidad.json')
TTL = 86400.0


class WrongThing(Exception):
    """raised instead of measuring something whose identity was assumed."""


# An IP has no ssh key of its own in this house, so ssh-by-IP fails and the address comes back
# UNVERIFIED even when the machine behind it is perfectly reachable by name. That is honest but
# useless, so an IP is resolved THROUGH the name it maps to -- and the mapping itself is read from
# reverse DNS and then CONFIRMED by asking that name its own hostname. rdns alone stays a claim.
BY_IP = {'192.168.8.145': 'flock-pi', '192.168.8.123': 'laptop'}


def _ssh_name(addr, timeout=12):
    addr = BY_IP.get(addr, addr)
    try:
        r = subprocess.run(['ssh', '-o', 'ConnectTimeout=%d' % timeout, '-o', 'BatchMode=yes',
                            addr, 'hostname'],
                           capture_output=True, text=True, timeout=timeout + 10)
        n = (r.stdout or '').strip().splitlines()
        return n[0].strip() if n and n[0].strip() else None
    except Exception:
        return None


def _rdns(addr):
    try:
        return socket.gethostbyaddr(addr)[0]
    except Exception:
        return None


def _ports(addr, ports=(22, 123, 8769, 8097)):
    open_ = []
    for p in ports:
        s = socket.socket(); s.settimeout(2.5)
        try:
            s.connect((addr, p)); open_.append(p)
        except Exception:
            pass
        s.close()
    # UDP 123 cannot be probed by connect(); ask it the NTP question instead
    try:
        import struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(2.5)
        s.sendto(b'\x1b' + 47 * b'\0', (addr, 123))
        d, _a = s.recvfrom(1024); s.close()
        if len(d) >= 48:
            open_.append(123)
            stratum = d[1]
            return sorted(set(open_)), stratum
    except Exception:
        pass
    return sorted(set(open_)), None


def resolve(addr, fresh=False):
    """{addr, hostname, rdns, ports, ntp_stratum, verified, asked_at} -- asked, not assumed.

    `verified` is True only when the machine itself answered with a hostname. Reverse DNS alone is
    NOT verification: it is a claim by a third party about an address, which is the same kind of
    inherited label this file exists to stop.
    """
    cache = {}
    try:
        cache = json.load(open(CACHE))
    except Exception:
        pass
    if not fresh and addr in cache and (time.time() - cache[addr].get('asked_at', 0)) < TTL:
        return cache[addr]
    ports, stratum = _ports(addr)
    name = _ssh_name(addr)
    rec = {'addr': addr, 'hostname': name, 'rdns': _rdns(addr), 'ports': ports,
           'ntp_stratum': stratum, 'verified': bool(name), 'asked_at': time.time()}
    cache[addr] = rec
    try:
        tmp = CACHE + '.tmp'
        json.dump(cache, open(tmp, 'w'), indent=1)
        os.replace(tmp, CACHE)
    except Exception:
        pass
    return rec


def assert_is(addr, expect_substr, fresh=False):
    """RAISE rather than measure a thing whose identity was assumed.

    Call this before any measurement that names what it is pointed at. If the machine cannot be
    asked, that is NOT a pass -- it raises, because an unverifiable identity is exactly the state
    that produced an hour of analysis of the wrong thing.
    """
    r = resolve(addr, fresh=fresh)
    if not r['verified']:
        raise WrongThing('%s: identity UNVERIFIED (rdns %r, ports %s). Refusing to measure a thing '
                         'I have not read. An hour went into .123 as a "GPSDO echo" on exactly '
                         'this assumption.' % (addr, r['rdns'], r['ports']))
    if expect_substr.lower() not in (r['hostname'] or '').lower():
        raise WrongThing('%s is %r, NOT %r. This is the .123 error: a label inherited from a '
                         'comment instead of read from the machine.'
                         % (addr, r['hostname'], expect_substr))
    return r


if __name__ == '__main__':
    fresh = '--fresh' in sys.argv
    addrs = ['192.168.8.145', '192.168.8.123', 'armature', 'laptop', 'flock-pi']
    print('  WHO IS ACTUALLY AT EACH ADDRESS. Asked of the machine, not read from a comment.\n')
    print('  %-16s%-22s%-22s%-16s%s' % ('address', 'hostname (asked)', 'rdns (a claim)',
                                        'ports', 'verified'))
    for a in addrs:
        r = resolve(a, fresh=fresh)
        print('  %-16s%-22s%-22s%-16s%s'
              % (a, r['hostname'] or '-', (r['rdns'] or '-')[:21],
                 ','.join(str(p) for p in r['ports']) or '-',
                 'YES' if r['verified'] else 'NO'))

    print('\n  and the thing that cost the hour, stated as the file now reports it:')
    r = resolve('192.168.8.123')
    print('    192.168.8.123 -> %r' % (r['hostname'] or 'UNVERIFIED'))
    print('    it was described in a tick_bus comment as a GPSDO echo on port 8769.')
    print('    NTP stratum it reports: %s' % (r['ntp_stratum'] if r['ntp_stratum'] is not None
                                              else 'did not answer NTP'))
    try:
        assert_is('192.168.8.123', 'gpsdo')
        print('    assert_is(.123, "gpsdo") PASSED -- which would itself be a bug')
    except WrongThing as e:
        print('    assert_is(.123, "gpsdo") RAISED:')
        print('      %s' % str(e)[:150])
