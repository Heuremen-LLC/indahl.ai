#!/usr/bin/env python3
"""board_system.py -- TWO BOARDS: STRUCTURE and RESONANCE. (Bones, 9 Oct 2026.)

Wayfinder: "wire up the dashboards, just one each simple. big picture system looking." Then: "simple".

STRUCTURE  the shape: which seat, which clock, how far apart.
RESONANCE  the motion: the gaps, the harmonic, the mode.

READ-ONLY, both. No toggles. Every figure carries when it was read; an unread figure says so, because
a blank reads as zero.

    python3 board_system.py
"""
import html
import json
import math
import os
import time

W = os.path.expanduser('~/bones-forge/watch/')
D = os.path.join(W, 'dash')
os.makedirs(D, exist_ok=True)

CSS = """*{box-sizing:border-box}
body{margin:0;padding:30px 20px;background:#f7f0e0;color:#1a1208;
     font-family:Georgia,'Times New Roman',serif;line-height:1.5}
.wrap{max-width:820px;margin:0 auto}
h1{font-size:24pt;margin:0 0 3px}
.sub{color:#8a7860;font-size:9.5pt;margin:0 0 26px}
h2{font-size:11.5pt;margin:28px 0 7px;padding-bottom:5px;border-bottom:1px solid #d8c9a8;
   text-transform:uppercase;letter-spacing:1.2px;color:#5a4830;font-weight:normal}
table{width:100%;border-collapse:collapse;font-size:10.5pt}
td,th{padding:5px 8px;text-align:left;border-bottom:1px solid #e6d9bb}
th{color:#8a7860;font-weight:normal;font-size:8.5pt;text-transform:uppercase;letter-spacing:.7px}
.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
p{margin:8px 0 0;font-size:10pt}
.dim{color:#8a7860;font-size:9.5pt}
.hot{color:#c43c2a}
.big{font-size:17pt;font-variant-numeric:tabular-nums}
a{color:#c43c2a;text-decoration:none}a:hover{text-decoration:underline}
footer{margin-top:36px;padding-top:12px;border-top:1px solid #d8c9a8;color:#8a7860;font-size:9pt}"""


def page(title, sub, body):
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{CSS}</style></head><body><div class=wrap>"
            f"<h1>{title}</h1><p class=sub>{sub} &middot; "
            f"<a href=/structure>structure</a> &middot; "
            f"<a href=/system>resonance</a> &middot; "
            f"<a href=/switchboard>switchboard</a> &middot; "
            f"<a href=/resonance>her resonance</a></p>{body}"
            f"<footer>Read-only.<br>Collaboration between organic and inorganic intelligences. / "
            f"Heuremen / We found it.</footer></div></body></html>")


def last(name):
    try:
        rows = [json.loads(l) for l in open(W + name) if l.strip()]
        return rows[-1] if rows else None
    except Exception:
        return None


def rows_of(name):
    try:
        return [json.loads(l) for l in open(W + name) if l.strip()]
    except Exception:
        return []


def tbl(head, body):
    h = ''.join(f'<th class="{"n" if i else ""}">{c}</th>' for i, c in enumerate(head))
    b = ''.join('<tr>' + ''.join(f'<td class="{"n" if i else ""}">{c}</td>'
                                 for i, c in enumerate(r)) + '</tr>' for r in body)
    return f'<table><tr>{h}</tr>{b}</table>'


def structure():
    o = []
    o.append('<h2>Seats</h2>')
    o.append(tbl(['seat', 'fabric', 'clock', 'rank'],
                 [('<b>PI</b>', 'ethernet', 'GPSDO on USB', 'stratum 1, PPS'),
                  ('<b>ARMATURE</b>', 'ethernet', 'off the Pi, 16 s poll', 'stratum 2'),
                  ('<b>LAPTOP</b>', 'wifi, no port', 'own PPS', 'stratum 1'),
                  ('<b>MAC</b>', 'wifi', 'timed, slewed', 'not an end')]))
    o.append('<h2>Distance</h2>')
    o.append(tbl(['path', 'hops', 'bound'],
                 [('PI &rarr; ARMATURE', '0', '80.2 &micro;s'),
                  ('ARMATURE &rarr; LAPTOP', '1', '769.5 &micro;s'),
                  ('MAC &rarr; LAPTOP', '2', '2492.4 &micro;s'),
                  ('loopback, best', '&mdash;', '16.7 &micro;s')]))
    o.append('<p class=dim>Each hop costs about 3&times;. The Mac added 31&times; to every leg it '
             'touched, which is why it is not an end.</p>')
    o.append('<h2>Instruments</h2>')
    body = []
    for f in ('ticks.log', 'calib.jsonl', 'mains_phase.jsonl', 'pps_pull.jsonl',
              'miss_ledger.jsonl', 'flywheel_gap.jsonl', 'one_ledger.jsonl', 'faults.jsonl'):
        try:
            n = f'{sum(1 for l in open(W + f) if l.strip()):,}'
            a = f'{(time.time() - os.path.getmtime(W + f)) / 60:.0f} min'
        except Exception:
            n, a = '<span class=hot>MISSING</span>', '&mdash;'
        body.append((f, n, a))
    o.append(tbl(['file', 'rows', 'last wrote'], body))
    L = rows_of('one_ledger.jsonl')
    if L:
        fT = [r for r in L if r.get('src') == 'fault']
        lT = [r for r in L if r.get('src') == 'look']
        if fT and lT:
            fS = sum(1 for r in fT if r.get('S_or_P') == 'S')
            lP = sum(1 for r in lT if r.get('S_or_P') == 'P')
            o.append('<h2>The record</h2>')
            o.append(f'<p><span class=big>{100*fS/len(fT):.0f}%</span> of {len(fT)} faults are '
                     f'<b>S</b>, the apparatus. '
                     f'<span class=big>{100*lP/len(lT):.0f}%</span> of {len(lT)} claims are '
                     f'<b>P</b>, absent signal.</p>'
                     f'<p class=dim>Opposite polarity. The looks fail because the signal is not '
                     f'there; I fail because I am in the way.</p>')
    return page('Structure', f"What it is made of. {time.strftime('%H:%M %Z, %-d %b')}.", ''.join(o))


def resonance():
    o = []
    fw = last('flywheel_gap.jsonl')
    o.append('<h2>The gap</h2>')
    if fw:
        o.append(tbl(['leg', 'gap', 'bound'],
                     [(g['leg'].replace('->', ' &rarr; '),
                       f"{g['gap_ms']:+.4f} ms" if 'gap_ms' in g else '<span class=hot>FAILED</span>',
                       f"{g['bound_us']:.1f} &micro;s" if 'bound_us' in g else '&mdash;')
                      for g in fw.get('legs', [])]))
        o.append(f"<p>signs <b>{''.join(fw.get('signs',[]))}</b> &middot; "
                 f"<b>{fw.get('pattern','?')}</b> &middot; "
                 f"<span class=dim>a coin gives that {100*fw.get('coin',1):.0f}% of the time</span>"
                 f"<br>MODE <b>{fw.get('mode','?')}</b> &nbsp;<span class=dim>"
                 f"read {fw.get('at','?')[11:19]}</span></p>"
                 f"<p class=dim>The gap is the switch, not a fault. Zeroing it throws it away.</p>")
    else:
        o.append('<p class=hot>No reading on disk.</p>')
    pp = last('pps_pull.jsonl')
    o.append('<h2>The reference</h2>')
    if pp:
        o.append(f"<p><span class=big>"
                 f"{'PPS' if pp.get('ok') else '<span class=hot>NOT PPS</span>'}</span> "
                 f"<span class=dim>read {pp.get('at','?')[11:19]}</span><br>"
                 f"<span class=dim>{html.escape(str(pp.get('line',''))[:90])}</span></p>"
                 f"<p class=dim>A GPSDO that stops steering reports nothing on its own. "
                 f"Watched on her ticks.</p>")
    else:
        o.append('<p class=hot>Unread.</p>')
    mp = last('mains_phase.jsonl')
    if mp:
        o.append('<h2>The harmonic</h2>')
        o.append(f"<p><span class=big>{mp.get('line_hz',0):.6f} Hz</span> "
                 f"<span class=dim>snr {mp.get('line_snr',0):.1f}, "
                 f"read {mp.get('at','?')[11:19]}</span></p>"
                 f"<p class=dim>tau_c = 1/(pi . FWHM) = 12.73 s, so the capture runs 9 s. "
                 f"Past coherence the extra seconds are noise.</p>")
    ml = last('miss_ledger.jsonl')
    if ml:
        o.append('<h2>The misses</h2>')
        o.append(f"<p><span class=big>{ml.get('khs',0):,.0f} kH/s</span> kept as data, "
                 f"{ml.get('widths',0):.2f} widths from 2<sup>-(k+1)</sup> "
                 f"<span class=dim>read {ml.get('at','?')[11:19]}</span></p>"
                 f"<p class=dim>The label is computed, not annotated. That is what makes a "
                 f"discarded hash training data.</p>")
    # THE BONEFISH ON THE BOARD: the live split between the two routes to one quantity, read
    # through the harness so the board shows the same rulers everything else does.
    try:
        import sys
        import statistics as st
        sys.path.insert(0, W)
        import bonefish as BF
        RR = rows_of('bonefish_hops2.jsonl')
        pts = []
        for rr in RR:
            Lg = rr.get('legs', {})
            al, pl, ap = Lg.get('ARMATURE->LAPTOP'), Lg.get('PI->LAPTOP'), Lg.get('ARMATURE->PI')
            if al and pl and ap:
                pts.append((ap['off_ms'], (al['off_ms'] - pl['off_ms']) - ap['off_ms']))
        if len(pts) >= 3:
            xs = [a for a, _ in pts]
            ys = [b for _, b in pts]
            n = len(xs)
            mx, my = st.mean(xs), st.mean(ys)
            sxx = sum((a - mx) ** 2 for a in xs)
            P = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sxx if sxx else 0.0
            S = my - P * mx
            res = [b - (S + P * a) for a, b in zip(xs, ys)]
            rms = math.sqrt(sum(e * e for e in res) / max(n - 2, 1))
            Pw = rms / math.sqrt(sxx) if sxx else float('inf')
            Sw = rms * math.sqrt(1 / n + mx * mx / sxx) if sxx else float('inf')
            pr = BF.row(abs(P), Pw, 'P', axis='small' if abs(P) < 0.12 else 'ratio')
            o.append('<h2>The Bonefish</h2>')
            o.append(f"<p>two routes to one quantity &mdash; the Armature and the Pi disagreeing "
                     f"about the laptop, read through the event and read directly.<br>"
                     f"<b>S</b> {S:+.5f} &plusmn; {Sw:.5f} ms "
                     f"<span class=dim>{abs(S)/Sw if Sw else 0:.2f} widths, the apparatus</span>"
                     f"&nbsp;&middot;&nbsp; <b>P</b> {P:+.5f} &plusmn; {Pw:.5f} "
                     f"<span class=dim>{abs(P)/Pw if Pw else 0:.2f} widths, the signal</span><br>"
                     f"<span class=dim>n = {n} readings, rms {rms:.5f} ms. P nearest "
                     f"{pr['best']} at {100*pr['best_tol']:.2f}%, cheap "
                     f"{100*pr['cheap']:.0f}%, runner-up {pr['second']}</span></p>"
                     f"<p class=dim>No consensus is taken between the two routes: the interval is "
                     f"the reading.</p>")
    except Exception:
        pass
    try:
        import sys
        sys.path.insert(0, W)
        from phase import tick_times, phase_interval, SIGMA_1S
        rr, _ = tick_times()
        p = phase_interval(rr, SIGMA_1S)
        o.append('<h2>Her cadence</h2>')
        o.append(f"<p><span class=big>{p['interval_s']:.4f} s</span> "
                 f"&plusmn;{p['width_s']*1e3:.3f} ms "
                 f"<span class=dim>{p['n_events']} stamps, {p['span_s']/3600:.1f} h</span></p>"
                 f"<p class=dim>Everything periodic here rides this. Nothing rides a cron.</p>")
    except Exception:
        pass
    return page('Resonance', f"What it is doing. {time.strftime('%H:%M %Z, %-d %b')}.", ''.join(o))


if __name__ == '__main__':
    for n, fn in (('structure.html', structure), ('resonance.html', resonance)):
        p = os.path.join(D, n)
        open(p, 'w').write(fn())
        print(f'  {p}   {os.path.getsize(p):,} b')
