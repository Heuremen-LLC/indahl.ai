"""readwitness.py -- THE STOPWATCH RUN. By hand, outside the freeze. All bits, no cut, no two-way sort, no verdict word.
Frame per bit = F0 (everyone OFF) and F1 (everyone ON), looked at with no wait.
A CLOCK's hand = (2 X - 1) - i (2 Y - 1) from its two readings: its LENGTH says how well it still ticks together; its ANGLE is what it counted.
THREE TIMES on one 60 us event: OURS (how long we told the emitter to stay ON: 0 / 20 / 40 / 60), THE BIT'S (the emitter's own last look),
THE WITNESS'S (how far the hand of each clock wired to that emitter turned, against its own reading with the emitter OFF)."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); med = lambda v: float(np.nanmedian(v))
RO = json.load(open(os.path.join(HERE, 'data', 'reads', 'witness_roles.json'))); EM = RO['emitters']; WOF = {int(k): v for k, v in RO['witness_of'].items()}; FAR = RO['far']; W = sorted(WOF)
print(f"ROLES from: {RO['source']}; {len(EM)} emitters, {len(W)} witness clocks (wired to an emitter), {len(FAR)} far clocks, {len(RO['edges'])} links")
wang = lambda a: (a + np.pi) % (2 * np.pi) - np.pi
ALL = []
for k in (1, 2, 3):
    mp = os.path.join(D, f'run{80 + k}_meta.json')
    if not os.path.exists(mp): print(f'read {k}: NOT FIRED / NOT LANDED (a row)'); continue
    m = json.load(open(mp)); z = np.load(os.path.join(D, f'run{80 + k}_results.npz')); L = lambda key: np.asarray(z[f'{key}__L1']).astype(complex); ns = L('F0').shape[0]
    m0 = L('F0').mean(0); d = L('F1').mean(0) - m0; al = lambda x: np.real((x - m0) * np.conj(d)) / np.abs(d) ** 2
    sep = np.abs(d) / np.sqrt((np.abs(L('F0') - m0) ** 2).mean(0) / 2)
    P = {key: al(L(key)) for key in [f'A{a}|{h}' for a in range(4) for h in 'XY'] + ['B1', 'B2']}
    lev = {key: v.mean(0) for key, v in P.items()}; hand = {a: (2 * lev[f'A{a}|X'] - 1) - 1j * (2 * lev[f'A{a}|Y'] - 1) for a in range(4)}
    rng = np.random.default_rng(20261820 + k); BH = []
    for _ in range(200):
        i = rng.integers(0, ns, ns); BH.append({a: (2 * P[f'A{a}|X'][i].mean(0) - 1) - 1j * (2 * P[f'A{a}|Y'][i].mean(0) - 1) for a in range(4)})
    print(f"\n######## read {k}: fired {m['start_time'][11:19]}, {ns} shots; middle separation/width of all bits {med(sep):.1f}")
    print('\n== THE CLOCKS, how long the hand still is (1 = ticking together, 0 = smeared), middle clock:   emitter OFF     ON 20 us     ON 40 us     ON 60 us')
    for nm, grp in (('witness clocks (wired to an emitter)', W), ('far clocks (wired to none)', FAR)):
        print(f'   {nm:<40} ' + '        '.join(f'{med(np.abs(hand[a][grp])):.3f}' for a in range(4)))
    print('\n== THE WITNESS\'S TIME: how far each clock\'s hand TURNED against its own reading with the emitter OFF (degrees; middle of |turn| and the spread across clocks)')
    turn = {a: np.degrees(wang(np.angle(hand[a] / hand[0]))) for a in (1, 2, 3)}; bturn = {a: np.array([np.degrees(wang(np.angle(b[a] / b[0]))) for b in BH]) for a in (1, 2, 3)}
    for nm, grp in (('witness clocks', W), ('far clocks', FAR)):
        print(f'   {nm:<16} ON 20: {med(np.abs(turn[1][grp])):6.1f}   ON 40: {med(np.abs(turn[2][grp])):6.1f}   ON 60: {med(np.abs(turn[3][grp])):6.1f}     one clock\'s own shot width (middle): {med(bturn[1].std(0)[grp]):.1f} / {med(bturn[2].std(0)[grp]):.1f} / {med(bturn[3].std(0)[grp]):.1f}')
    # signed, per clock: steps per 20 us of emitter-ON, each against the other two
    good = [w for w in W if abs(hand[0][w]) > 0.15 and sep[w] > 3]; st = np.array([[turn[1][w], wang(np.radians(turn[2][w] - turn[1][w])) * 180 / np.pi, wang(np.radians(turn[3][w] - turn[2][w])) * 180 / np.pi] for w in good])
    sg = np.sign(turn[2][good]); sg[sg == 0] = 1; sts = st * sg[:, None]
    print(f"   {len(good)} witness clocks with a readable hand (length > 0.15 with the emitter OFF). Each clock's own direction taken as +:")
    print(f'      the turn added by the FIRST / SECOND / THIRD 20 us of emitter-ON (middle clock): {med(sts[:, 0]):+6.1f}  {med(sts[:, 1]):+6.1f}  {med(sts[:, 2]):+6.1f} deg     quarter points: ' + '  '.join(f'[{np.percentile(sts[:, j], 25):+.0f} {np.percentile(sts[:, j], 75):+.0f}]' for j in range(3)))
    r21 = sts[:, 1] / sts[:, 0]; r32 = sts[:, 2] / sts[:, 1]; print(f'      second / first: middle {med(r21):.2f};  third / second: middle {med(r32):.2f}   (a stopwatch that counts ON-time evenly reads 1 and 1, less whatever of the emitter has already faded)')
    rate = np.abs(turn[2][good]) / 360 / 40e-6 / 1e3; print(f'      the hand\'s turning rate while its neighbour is ON, from the 40 us arm: middle {med(rate):.1f} kHz, quarter points {np.percentile(rate, 25):.1f} {np.percentile(rate, 75):.1f}')
    wt40 = 20 * (sts[:, 0] + sts[:, 1]) / sts[:, 0]; wt60 = 20 * sts.sum(1) / sts[:, 0]; print(f'      WITNESS TIME = total turn / (its own turn per us from the first 20 us): told ON for 40 -> middle {med(wt40):.1f} us;  told ON for 60 -> middle {med(wt60):.1f} us   (ours: 40 and 60)')
    print('\n== THE BIT\'S OWN TIME: the emitter\'s last look, middle emitter')
    e = lambda key: med(lev[key][EM])
    print(f"   told ON for 60, neighbours CLOCKS: X-hand job {e('A3|X'):.4f}, Y-hand job {e('A3|Y'):.4f}   | neighbours OFF: {e('B1'):.4f}   | neighbours ON: {e('B2'):.4f}")
    a3 = (lev['A3|X'][EM] + lev['A3|Y'][EM]) / 2; print(f"   bit by bit: watched by clocks minus neighbours OFF: {med(a3 - lev['B1'][EM]):+.4f} +- {1.2533 * np.std(a3 - lev['B1'][EM]) / np.sqrt(len(EM)):.4f};   neighbours ON minus neighbours OFF: {med(lev['B2'][EM] - lev['B1'][EM]):+.4f} +- {1.2533 * np.std(lev['B2'][EM] - lev['B1'][EM]) / np.sqrt(len(EM)):.4f}")
    print(f"   parked after 20 (reads what had already gone): {e('A1|X'):.4f} {e('A1|Y'):.4f}   parked after 40: {e('A2|X'):.4f} {e('A2|Y'):.4f}   never ON: {e('A0|X'):+.4f} {e('A0|Y'):+.4f}")
    yard = med(lev['B1'][EM]); print(f"   the bit's own count of the three stretches, using its neighbours-OFF fading as the yardstick: left after 60 = {yard:.4f}; lost by 20 = {e('A1|X'):.4f}, by 40 = {e('A2|X'):.4f}; plain fading from the yardstick alone says {1 - yard ** (1 / 3):.4f} and {1 - yard ** (2 / 3):.4f} (a ruler row)")
    print('\n== THE NEIGHBOURS THEMSELVES when they were not clocks: N held ON for 60 (B2), middle witness %.4f, middle far %.4f;  N left OFF (B1): %+.4f / %+.4f' % (med(lev['B2'][W]), med(lev['B2'][FAR]), med(lev['B1'][W]), med(lev['B1'][FAR])))
    print('\n== ROWS: emitters whose clocks did not turn, clocks with no hand, bits that cannot be told apart')
    dead = [w for w in W if abs(hand[0][w]) <= 0.15]; print(f'   witness clocks with no readable hand even with the emitter OFF: {len(dead)} of {len(W)}: {dead[:30]}')
    print(f'   bits with separation/width under 3: {[int(b) for b in np.where(sep < 3)[0]]}')
    big = sorted(good, key=lambda w: -abs(turn[3][w]))[:8]; print('   the eight clocks that turned most (clock<-emitter: turn at 20/40/60 deg, hand length OFF->60): ' + '; '.join(f'q{w}<-q{WOF[w]}: {turn[1][w]:+.0f}/{turn[2][w]:+.0f}/{turn[3][w]:+.0f}, {abs(hand[0][w]):.2f}->{abs(hand[3][w]):.2f}' for w in big))
    ALL.append({'time': m['start_time'], 'turn_deg': {str(w): [float(turn[a][w]) for a in (1, 2, 3)] for w in W}, 'len': {str(w): [float(abs(hand[a][w])) for a in range(4)] for w in W + FAR}, 'emitter_left': {str(q): [float(lev[x][q]) for x in ('A0|X', 'A1|X', 'A2|X', 'A3|X', 'B1', 'B2')] for q in EM}})
json.dump(ALL, open(os.path.join(HERE, 'data', 'reads', 'witness_run.json'), 'w'))
