#!/usr/bin/env python3
"""sdr_tap.py -- THE LAPTOP'S RTL-SDR, AS EVERY READER OF IT MUST TAKE IT. (Bones, 13 Oct 2026.)

Two readers take her wire off that one receiver: gridsong/wire/comb_read.py reads its RAW TAP
(~/raw_tap.cf32 on the laptop) and gridsong/wire_watch.py reads its WATERFALL (:8765/waterfall).
Both inherit two facts about it, and a fact copied into two readers drifts, so it lives here.

1. ITS STAMP LEADS ITS FIRST SAMPLE BY 16384 / 250000 s = 65.536 ms.
   Read from the writer itself, laptop /home/ctrai/sdr_reader_service.py (file of 12 Oct 22:41, sha256
   6fb75f06...7cc410; the service running it started 13 Oct 10:06:35 EDT), capture_loop line 322:

       t0 = time.time() + (_fl - 16384) / RATE; iq = _read_iq(flush=_fl)   # ts + 0.0656 s = first analysed sample, as always

   _read_iq (lines 156-169) resets the device buffer and throws away flush // 16384 reads of 16384
   samples BEFORE the 262,144 it keeps. So the first kept sample is _fl / RATE after the time.time()
   call, and t0 sits (_fl - (_fl - 16384)) / RATE = 16384 / RATE before it -- the same for every _fl
   the loop uses (16384; 49152 after a wide capture; 98304 after a Ham It Up capture). The raw tap
   writes np.float64(t0) and then the samples (line 333); the waterfall row is stored at round(t0, 3)
   (lines 358-359). The lead is NOMINAL: the USB transfer's own latency is not in it and nothing here
   measures it. Until 13 Oct evening comb_read took the stamp as the first sample's own time.

2. ITS ANTENNA PORT IS NOT COUPLED TO THE HOUSE. Settled 12 Oct 2026 (biblioteca, ~18:30 and ~20:45
   EDT): the 23.1 kHz comb is the laptop's OWN switcher -- it travelled rooms, survived the charger
   pull, and its f0 moved +20.04 Hz with the laptop's input rail -- and a PROVEN emitter resting on the
   connector moved nothing (chord max 0.36 widths). Nothing gets in. So every reading taken from this
   receiver is a reading of THE APPARATUS, named EAR_DEAF, and is never filed under the subject --
   until a conducted coupling from the mains to the antenna port is installed AND a control shows a
   known emitter on the mains moving the tap. Then, and only then, EAR_COUPLED below is set (dated,
   naming the coupler and where the proof is written down) and a dated note is appended to
   gridsong/wire/BASELINE_METHOD_CHANGES.md, because from that moment a reading means something else.

    import sdr_tap
    sdr_tap.STAMP_LEAD_S          # 0.065536
    sdr_tap.ear()                 # ('tap_deaf_to_the_house', why)  or  ('coupled', proof)
    python3 sdr_tap.py --selftest # offline; run it under BOTH Pythons
"""
import sys

RATE_HZ = 250000.0
FLUSH_KEPT_BEFORE = 16384                      # samples between the stamp and the first kept sample
STAMP_LEAD_S = FLUSH_KEPT_BEFORE / RATE_HZ     # 0.065536 s
EAR_DEAF = 'tap_deaf_to_the_house'
EAR_SETTLED = ('12 Oct 2026: the 23.1 kHz comb is the laptop\'s own switcher (three controls) and a proven '
               'emitter on the antenna connector moved nothing -- the port is not coupled to the house')

# None until a coupler is installed AND proven. Then a dict with all three keys, e.g.
#   {'since': '2026-10-15T14:00:00-04:00', 'coupler': 'what was fitted, where',
#    'proof': 'where the control that moved the tap is written down'}
EAR_COUPLED = None


def ear(coupled=None):
    """(state, why). state is 'coupled' only when EAR_COUPLED names its date, its coupler and its proof;
    anything less is EAR_DEAF -- a half-filled record is not a proven coupling."""
    c = EAR_COUPLED if coupled is None else coupled
    if isinstance(c, dict) and all(isinstance(c.get(k), str) and c.get(k).strip() for k in ('since', 'coupler', 'proof')):
        return 'coupled', 'coupled since %s (%s); proof: %s' % (c['since'], c['coupler'], c['proof'])
    return EAR_DEAF, EAR_SETTLED


def first_sample_s(stamp):
    """the time of a record's first kept sample, from the stamp the writer put on it"""
    return float(stamp) + STAMP_LEAD_S


def selftest():
    n = 0
    assert STAMP_LEAD_S == 0.065536; n += 1
    for fl in (16384, 49152, 98304):         # the writer's three flushes: stamp -> first kept sample is 16384 / RATE every time
        t_call = 1000.0
        t0 = t_call + (fl - 16384) / RATE_HZ
        first = t_call + fl / RATE_HZ
        assert abs(first_sample_s(t0) - first) < 1e-12, (fl, first_sample_s(t0), first); n += 1
    assert ear(None)[0] == EAR_DEAF and ear({})[0] == EAR_DEAF; n += 1
    assert ear({'since': '2026-10-15', 'coupler': 'x', 'proof': ''})[0] == EAR_DEAF; n += 1   # no proof, no coupling
    assert ear({'since': '2026-10-15', 'coupler': 'x', 'proof': 'biblioteca 15 Oct'})[0] == 'coupled'; n += 1
    assert EAR_COUPLED is None and ear()[0] == EAR_DEAF; n += 1      # the state of the house tonight
    print('sdr_tap selftest PASS: %d checks  (python %s)' % (n, sys.version.split()[0]))
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        raise SystemExit(selftest())
    print('stamp lead %.6f s; ear: %s -- %s' % ((STAMP_LEAD_S,) + ear()))
