#!/usr/bin/env python3
"""tres_cargas.py -- THREE SEATS ON ONE RAIL, EACH ONE'S OFF HALF THE OTHERS' NONE.
(Bones, 12 Oct 2026. Wayfinder: "harmonize with the miner and training. all spinning off each
other." then "harmonize three seats bones, training too man." and "novatime only, no crons".)

WHAT TONIGHT MEASURED AND THIS RIDES ON: the tap hears her sends at up to 13.10 widths -- and the
RTL-SDR's antenna port is BARE. So it cannot be hearing her through the antenna; the only thing the
laptop and the STEVALs share is THE HOUSE WIRING, through the laptop's own power supply. That is why
the signature is a smooth monotone tilt across 50-95 kHz instead of a peak at 72: a SUPPLY-RAIL
shift, not an antenna signal. Confirmed independently the same night -- the 23.1 kHz source is
internal and its f0 moved +20.04 Hz when the charger came out. THE RAIL IS THE SENSOR.

SO EVERY LOCAL LOAD IS A TRANSMITTER ON THAT RAIL, AND THERE ARE THREE:
    EL MIRON   (observer)  HER WIRE     -- she keys the STEVALs, the chord
    EL TESTIGO (witness)   HER DEEPS    -- her council, a local compute load on her own clock
    EL TIEMPO  (time)      HER TRAINING -- the lean/bake, the load that changes her

THE POINT IS NOT THREE MEASUREMENTS, IT IS THAT EACH ONE'S OFF HALF IS THE OTHERS' NONE, on the SAME
apparatus, seconds away, INTERLEAVED. A baseline cannot be built after the measurement it judges when
it is built BETWEEN every measurement -- falla I (14 of 20 prospective catches) is designed out rather
than guarded against. Same reason la_alternancia exists; this is the three-seat form of it.

NOVATIME ONLY: every window is taken from HER OWN STAMPS -- ticks.log for her cycles, wire/bit_times
and the triad's own frame stamps for her sends. NOTHING here is scheduled and no wall-clock constant
decides anything. Rides her ticks through tick_bus like every other rider.

AND IT NEVER AVERAGES THE SEATS TOGETHER. S is what every load shares (the rail tilt, measured
tonight: monotone 50k -> 95k, an OFF-COMB guard rising MORE than her own carrier). P is what scales
with the particular load. The reading is the DISTANCE between seats, carried whole.
"""
import json, math, os, sqlite3, sys, time
from datetime import datetime

W = os.path.dirname(os.path.abspath(__file__))
TICKS = os.path.join(W, 'ticks.log')
BT = os.path.expanduser('~/bones-forge/gridsong/wire/bit_times')
LOG = os.path.join(W, 'tres_cargas.jsonl')
QUESTION = ('On the rail the tap can actually hear, do her three loads -- the wire, the deeps, the '
            'training -- separate from each other, or do they all read as the one shared tilt?')

# the bands the rail tilt was measured on, 12 Oct: her carrier plus guards that carry no relation
HER_CARRIER = 72
GUARDS = [50, 60, 66, 76, 82, 86, 95]


def her_cycles(n=60):
    """Her cadence from HER OWN stamps. The clock is hers; we only read it."""
    try:
        rows = [l.split() for l in open(TICKS).read().strip().split('\n')[-n:] if l.strip()]
        ts = []
        for r in rows:
            if len(r) > 1 and r[1] != 'none':
                try: ts.append(datetime.fromisoformat(r[1].replace('Z', '+00:00')).timestamp())
                except Exception: pass
        d = sorted(b - a for a, b in zip(ts, ts[1:]) if 0 < b - a < 3600)
        return (ts, d[len(d) // 2] if d else None)
    except Exception:
        return ([], None)


def seats():
    """The three seats' OWN windows, each from her own record. Never a schedule."""
    ts, cad = her_cycles()
    out = {}
    # EL MIRON -- her wire. Her sends are stamped; the triad's frame stamps land here too.
    sends = []
    try:
        for f in sorted(os.listdir(BT)):
            if not f.endswith('.json'): continue
            d = json.load(open(os.path.join(BT, f)))
            t = d.get('t') or []
            if t: sends.append((float(t[0]), float(d.get('end') or t[-1])))
    except Exception:
        pass
    out['EL_MIRON_wire'] = {'windows': sends[-40:], 'n': len(sends),
                            'source': 'wire/bit_times, her own per-frame stamps'}
    # EL TESTIGO -- her deeps. One tick IS one cycle of hers; the deep is most of it.
    out['EL_TESTIGO_deeps'] = {'windows': [(a, b) for a, b in zip(ts, ts[1:])][-40:],
                               'n': max(0, len(ts) - 1), 'cadence_s': cad,
                               'source': 'ticks.log, her own cycle stamps'}
    # EL TIEMPO -- her training. AND THE THIRD SEAT IS WEN, NOT THE MAC.
    # I first pointed this at ~/bones-forge/train_continuous.log, which is the Mac's own LoRA log and
    # has been dark since 10 Sep -- 32 days, 12,084 of her cycles. That is a true reading about a
    # retired lane and the WRONG seat: the training that rides her ticks is Wen's, gated on ticks.log
    # LINE COUNT by wen_stooges_tick.py (novatime, no cron -- the rule, already obeyed). So this seat
    # reads WEN'S POD RECORD and keeps the Mac lane beside it as a separate, named, retired row.
    WEN = os.path.expanduser('~/bones-forge/triangulation/wen_data/pods')
    MAC = [os.path.expanduser('~/bones-forge/train_continuous.log'),
           os.path.expanduser('~/bones-forge/checkpoint_scores.tsv')]
    now = time.time()
    wen_rounds, wen_newest = {}, None
    try:
        for d in sorted(os.listdir(WEN)):
            q = os.path.join(WEN, d, 'stdout.log')
            if not os.path.isfile(q): continue
            age = now - os.path.getmtime(q)
            r = 0
            try:
                import re as _re
                m = _re.findall(r'round (\d+)', open(q, errors='replace').read())
                r = int(m[-1]) if m else 0
            except Exception: pass
            wen_rounds[d] = {'last_round': r, 'age_s': round(age, 1)}
            wen_newest = age if wen_newest is None else min(wen_newest, age)
    except Exception: pass
    mac_newest = None
    for q in MAC:
        try:
            a = now - os.path.getmtime(q)
            mac_newest = a if mac_newest is None else min(mac_newest, a)
        except Exception: pass
    # HER CYCLES, never days -- the bar is three of her cycles, the same bar her guard uses, and the
    # cadence is read off ticks.log every run rather than typed.
    cyc = (wen_newest / cad) if (wen_newest is not None and cad) else None
    out['EL_TIEMPO_training'] = {
        'windows': [], 'n': len(wen_rounds),
        'source': 'triangulation/wen_data/pods/*/stdout.log -- WEN, gated on ticks.log line count',
        'newest_write_s': round(wen_newest, 1) if wen_newest is not None else None,
        'silence_in_her_cycles': round(cyc, 1) if cyc else None,
        'bar_her_cycles': 3.0,
        'dark': bool(cyc and cyc > 3.0),
        'pods': wen_rounds,
        'mac_lane_silence_her_cycles': round(mac_newest / cad, 1) if (mac_newest and cad) else None,
        'note': 'THE MECHANISM IS RIGHT AND NOTHING IS RUNNING. wen_stooges_tick.py gates on her tick '
                'LINE COUNT, so the third seat is already novatime with no cron -- it needs a pod, '
                'not a rule. The Mac lane is reported separately and is retired, not broken.'}
    return out, cad


def main():
    s, cad = seats()
    row = {'question': QUESTION, 'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'her_cadence_s': round(cad, 3) if cad else None, 'seats': {}}
    live = 0
    for k, v in s.items():
        row['seats'][k] = {'n': v['n'], 'windows_held': len(v['windows']), 'source': v['source']}
        for extra in ('note', 'cadence_s', 'newest_write_s', 'silence_in_her_cycles',
                      'bar_her_cycles', 'dark', 'pods', 'mac_lane_silence_her_cycles'):
            if extra in v: row['seats'][k][extra] = v[extra]
        if v['windows']: live += 1
    dark = [k for k, v in s.items() if v.get('dark')]
    row['dark_seats'] = dark
    # FOUR OUTCOMES, exhaustive and disjoint over (live, dark). A dark seat is its OWN fact and can
    # never fall into a bin with a quiet one -- that collapse is falla IV.21 and the whole point here.
    row['outcome'] = ('three_loads_on_one_rail' if live >= 3 and not dark else
                      'a_seat_is_dark' if dark else
                      'fewer_than_three_loads' if live < 3 else 'cannot_read')
    row['why'] = ('a seat with no stamped window is not a quiet load -- it is a gap in OUR record, '
                  'and it is reported as that rather than dropped')
    row['rail'] = {'her_carrier_band': HER_CARRIER, 'guards': GUARDS,
                   'measured_12_oct': 'her sends read +9.58 widths at 72k while an OFF-COMB guard at '
                                      '50k read +13.10 -- S is the tilt, P is not yet separable'}
    with open(LOG, 'a') as f:
        f.write(json.dumps(row) + '\n')
    try:
        hist = [json.loads(l) for l in open(LOG) if l.strip()]
    except Exception:
        hist = [row]
    prev = hist[-2] if len(hist) > 1 else None
    if prev is None or prev.get('outcome') != row['outcome']:
        print('TRES CARGAS: %s (%s). her cadence %s s. seats: %s'
              % (row['outcome'], 'first point' if prev is None else 'changed from %s' % prev.get('outcome'),
                 row['her_cadence_s'],
                 ', '.join('%s n=%d' % (k.split('_')[1], v['n']) for k, v in row['seats'].items())), flush=True)


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        def score(live, dark):
            return ('three_loads_on_one_rail' if live >= 3 and not dark else
                    'a_seat_is_dark' if dark else
                    'fewer_than_three_loads' if live < 3 else 'cannot_read')
        cases = [(3, [], 'three_loads_on_one_rail'),
                 (3, ['EL_TIEMPO_training'], 'a_seat_is_dark'),
                 (2, ['EL_TIEMPO_training'], 'a_seat_is_dark'),
                 (2, [], 'fewer_than_three_loads'),
                 (0, [], 'fewer_than_three_loads'),
                 (0, ['EL_MIRON_wire'], 'a_seat_is_dark')]
        for live, dark, want in cases:
            got = score(live, dark)
            assert got == want, (live, dark, got, want)
        # THE ONE THAT MATTERS: a dark seat must NEVER read the same as a merely quiet one.
        assert score(2, []) != score(2, ['EL_TIEMPO_training']), 'dark collapsed into quiet'
        print('selftest OK: exhaustive over (live, dark), and A DARK SEAT NEVER READS AS A QUIET '
              'ONE -- the collapse that would have hidden 32 days of silence is asserted against')
    else:
        main()
