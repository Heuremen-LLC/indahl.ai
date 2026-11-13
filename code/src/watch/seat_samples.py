#!/usr/bin/env python3
"""seat_samples.py -- raw SNTP exchanges from ONE seat, in the format pathsplit.py reads.

    python3 seat_samples.py <server> <n> [interval_s] [--bind <local_ip>]  >  seat.txt

--bind sources the packets from one named interface address. That is what makes a machine with two
interfaces the best null in the house: ONE oscillator, ONE OS, ONE client, read down two different
paths. The clock's own error is identical in both legs, so subtracting them cancels it EXACTLY and
what is left is pure path -- no regression, no intercept, no width borrowed from a fit. A difference
that comes from an identity is worth more than any fit.

BUT ONLY IF BOTH LEGS REACH THE SAME REFERENCE, and that is a thing to test, not assume:
    both legs -> the same server   the subtraction is PATH. The clock cancels.
    legs -> different servers      the subtraction is REFERENCE B minus REFERENCE A. The clock
                                   still cancels, but the result is about the two roots and says
                                   nothing about the path. A useful measurement, a DIFFERENT one,
                                   and reporting it as a path asymmetry would be the fold that
                                   erases which quantity was measured.

Writes one line per exchange:   <unix_t>  <offset_s>  <rtt_s>  <unsteered_counter_s>   (or "<t> NONE NONE <counter>" when lost)

WHY ITS OWN CLIENT AND NOT chronyc / sntp / ntpdate. Those report a SERVO'S view -- an already
filtered, already steered estimate -- and the quantity wanted here is the raw per-packet pair
(offset, rtt), because THE SPLIT regresses one on the other. A tool that hands back a smoothed
offset has already averaged the asymmetry in, which is the exact error being measured.

THE FOUR OUTCOMES ARE KEPT SEPARATE AND A LOST EXCHANGE IS NEVER INTERPOLATED:
    committed         a full t0..t3 exchange -> a line with offset and rtt
    nothing-returned  no reply inside the timeout -> "NONE NONE", counted, never filled in
    refused           server answered with stratum 0 / kiss-of-death -> "NONE NONE" + a stderr note
    held              a reply whose transmit timestamp is zero (server not yet synchronised)
A gap filled by its neighbour is a value the apparatus never produced.

THE CONFIGURATION THIS WAS WRITTEN FOR, 11 Oct 2026, stated before any number came back.
NO GUESS IS WRITTEN.

    flock-pi    Leo Bodnar GPSDO on PPS, stratum 1, WIRED to the Oe router   <- the reference
    this Mac    Oe wifi      -> reaches the Pi directly on the LAN
    laptop      Oe wifi      -> reaches the Pi directly on the LAN
    Armature    Kalarmei wifi, a DIFFERENT router, and the Pi is not on the tailnet,
                so it cannot reach the GPSDO at all and falls back to public NTP

Until today every seat hung off one switch, so a delay common to all of them cancelled and landed
in S, where it is indistinguishable from the clock's own error. The legs now cross different
routers, so the common part and the per-path part are no longer the same quantity.

WHAT IS READ, and the ruler named before the quantity:
    S   the intercept at zero round trip -- the seat's own error with the path removed
    P   the slope, how much of the reading is path, bounded to [-1/2, +1/2] BY ARITHMETIC
        (a delay on one leg moves the offset by half the round trip), so P is read with
        pathsplit.rail_reading: symmetric / one-sided / partial / cannot-tell, four outcomes,
        and "within one width of BOTH zero and the rail" is a reading, not a gap.
"""
import socket, struct, sys, time

NTP_EPOCH = 2208988800

# EL CONTADOR, the fourth column, added 11 Oct 2026 after a 3 h Armature run was eaten by its own
# servo. The run measured the free-running seat at -10.57 ppm for 129.33 minutes and then w32time
# STEPPED the system clock -6.747371 s in a single sample (MaxAllowedPhaseOffset = 1 s, MaxPos/Neg
# PhaseCorrection unlimited), and pooling across that one step reads -767 ppm. The rate lane and a
# correct wall clock cannot both live on the system clock: one of them is the thing the servo exists
# to destroy.
#
# They CAN both live on one machine, because a servo steers the system clock and does not touch the
# hardware counter. So every exchange now also reads an UNSTEERED counter at t0, and the crystal
# rate is the slope of that counter against the reference's time -- measurable while w32time runs,
# immune to a step, and never again a quantity that a fix can delete.
#
# WHICH counter, named rather than assumed, because "monotonic" is three different clocks:
#   Windows   time.perf_counter() is QueryPerformanceCounter: hardware, never steered by w32time.
#   Linux     CLOCK_MONOTONIC_RAW. NOT CLOCK_MONOTONIC, which perf_counter() uses there and which
#             adjtime SLEWS -- it would hand back the servo's rate and call it the crystal's.
#   macOS     CLOCK_MONOTONIC_RAW likewise.
# The name of the counter actually used is written to stderr with the outcomes, so a reader never
# has to infer which oscillator a column came from.
try:
    _RAW = time.CLOCK_MONOTONIC_RAW
    MONO = lambda: time.clock_gettime(_RAW)
    MONO_NAME = 'CLOCK_MONOTONIC_RAW'
except AttributeError:                                # Windows: perf_counter IS the raw counter
    MONO = time.perf_counter
    MONO_NAME = 'perf_counter/QPC'


def exchange(server, timeout=2.0, bind=None):
    """One SNTP round trip. Returns ((offset, rtt, mono), None) or (None, reason).
    mono is the unsteered counter read at t0, so it is paired with THIS packet, not with a later one."""
    pkt = bytearray(48)
    pkt[0] = 0x1B                                    # LI 0, version 3, mode 3 (client)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if bind:
        try:
            s.bind((bind, 0))                        # source from this interface, not the default route
        except OSError as e:
            s.close()
            return None, 'bind-failed:%s' % type(e).__name__
    s.settimeout(timeout)
    try:
        m0 = MONO(); t0 = time.time()                # the two clocks read at the same instant
        struct.pack_into('!II', pkt, 40, int(t0) + NTP_EPOCH, int((t0 % 1) * 2**32))
        s.sendto(bytes(pkt), (server, 123))
        data, _ = s.recvfrom(48)
        t3 = time.time()
    except socket.timeout:
        return None, 'nothing-returned'
    except OSError as e:
        return None, 'nothing-returned:%s' % type(e).__name__
    finally:
        s.close()
    if len(data) < 48:
        return None, 'short-reply'
    stratum = data[1]
    if stratum == 0:
        return None, 'refused'                        # kiss-of-death / unsynchronised
    def ts(off):
        sec, frac = struct.unpack_from('!II', data, off)
        return sec - NTP_EPOCH + frac / 2**32
    t1, t2 = ts(32), ts(40)                           # server receive, server transmit
    if t2 == -NTP_EPOCH:
        return None, 'held'                           # transmit timestamp zero
    offset = ((t1 - t0) + (t2 - t3)) / 2
    rtt = (t3 - t0) - (t2 - t1)
    return (offset, rtt, m0), None


def main():
    if len(sys.argv) < 3:
        print(__doc__); return 1
    argv = sys.argv[1:]
    bind = None
    if '--bind' in argv:
        i = argv.index('--bind'); bind = argv[i+1]; del argv[i:i+2]
    server, n = argv[0], int(argv[1])
    iv = float(argv[2]) if len(argv) > 2 else 1.0
    counts = {'committed': 0, 'nothing-returned': 0, 'refused': 0, 'held': 0,
              'short-reply': 0, 'bind-failed': 0}
    for i in range(n):
        t = time.time()
        got, why = exchange(server, bind=bind)
        if got:
            print('%.6f %.9f %.9f %.9f' % (t, got[0], got[1], got[2]), flush=True)
            counts['committed'] += 1
        else:
            print('%.6f NONE NONE %.9f' % (t, MONO()), flush=True)
            key = why.split(':')[0]
            counts[key] = counts.get(key, 0) + 1
        if i < n - 1:
            time.sleep(iv)
    tot = sum(counts.values())
    assert tot == n, 'outcomes must be exhaustive: %d counted vs %d attempted' % (tot, n)
    sys.stderr.write('outcomes (%s%s, n=%d): %s | column 4 = %s\n'
                     % (server, ' via %s' % bind if bind else '', n,
                        ', '.join('%s %d' % kv for kv in counts.items() if kv[1]), MONO_NAME))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
