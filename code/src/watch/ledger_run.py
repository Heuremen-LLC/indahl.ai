#!/usr/bin/env python3
"""ledger_run.py -- THE SEAT THAT CAN REFUSE THE COIN CLAIM, AND NOTHING ELSE.
(Bones, 13 Oct 2026, his "Let the ledger run.")

coin_forward_claim.v2.json registers two hypotheses at one difficulty and a deadline of
2026-11-12. A claim with a deadline and no watcher is theatre -- falla VIII.40 inverted: the
registration becomes the whole transaction and nothing is ever in a position to kill it.

So this does ONE thing. It reads the balance the Pi's stop_watch already writes every 10
minutes -- no new source, no new poll of the chain -- turns the INCREASE into a block count,
and reports the running likelihood ratio between the two registered hypotheses at the time
elapsed so far. No fitting, no forecast, no dollars.

    LR(k, t) = P(k | lambda_claim . t) / P(k | lambda_rival . t)
    >= 10 favours the claim      <= 0.1 refutes it      between is CANNOT TELL

THE LR IS VALID AT EVERY t, which is why there is no "too early" fudge: early on it simply
sits near 1 and says CANNOT TELL, which is the truth rather than a placeholder.

A BALANCE CAN FALL. He can spend it; a reorg can take it. A fall is NOT a negative block
count -- it is its own outcome and it stops the count rather than corrupting it.

PLUS NONE, carried from the claim: shares 0/0. Nobody observes a hash. This seat observes
only WOW arriving, which is the one thing that is evidence.

    python3 ledger_run.py --tick        the novatime rider
    python3 ledger_run.py              print the state and exit
    python3 ledger_run.py --selftest
"""
import json, math, os, subprocess, sys, time

W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)
from outcomes import Outcomes, OutcomeCollapse

CLAIM  = os.path.join(W, 'coin_forward_claim.v2.json')
LEDGER = os.path.join(W, 'ledger_run.jsonl')
SEEN   = os.path.join(W, '.ledger_run_seen')
TICKS  = os.path.join(W, 'ticks.log')
EVERY  = 12                      # her ticks; the tally only moves every 10 min anyway
REWARD = 75.85241                # WOW/block at registration; falls -0.0001/block, negligible here


def tally():
    """The Pi's own stop_watch file. The house already writes it; this adds no source."""
    try:
        r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=12',
                            'flock-pi', 'cat ~/wownero/tally.json'],
                           timeout=40, capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            return None, 'ssh rc=%d' % r.returncode
        d = json.loads(r.stdout)
        wow = d.get('wow')
        if wow is None and isinstance(d.get('blocks'), list):
            wow = sum(float(b.get('balance_wow') or 0) for b in d['blocks'])
        return {'wow': float(wow), 'at': d.get('at')}, None
    except Exception as e:
        return None, '%s: %s' % (type(e).__name__, str(e)[:90])


def pois(k, mu):
    return math.exp(-mu) * mu ** k / math.factorial(k)


def gate():
    """THREE SUBJECT OUTCOMES on the claim and TWO APPARATUS ones. CANNOT TELL is a
    first-class answer here, not a gap between the other two."""
    ok = lambda r: r.get('readable') is True
    return Outcomes(
        subject=[('favours_the_claim',  lambda r: ok(r) and r['lr'] is not None and r['lr'] >= 10),
                 ('refuses_the_claim',  lambda r: ok(r) and r['lr'] is not None and r['lr'] <= 0.1),
                 ('cannot_tell',        lambda r: ok(r) and r['lr'] is not None
                                        and 0.1 < r['lr'] < 10),
                 ('balance_fell_a_spend_or_a_reorg',
                  lambda r: ok(r) and r['lr'] is None)],
        apparatus=[('tally_unreadable', lambda r: not ok(r))])


def her_cycle():
    try:
        with open(TICKS, 'rb') as f:
            f.seek(0, 2); f.seek(max(0, f.tell() - 4096))
            return int(f.read().decode('utf-8', 'replace').strip().splitlines()[-1].split()[0])
    except Exception:
        return 0


def read():
    c = json.load(open(CLAIM))
    h = c['TWO_HYPOTHESES_AT_THE_SAME_DIFFICULTY']
    lc, lr_ = h['claim_lambda_per_day'], h['rival_lambda_per_day']
    t0 = time.mktime(time.strptime(c['registered_iso'], '%Y-%m-%dT%H:%M:%S'))
    base = c['THE_LEDGER_SEAT']['wow_held']
    t, why = tally()
    row = {'iso': time.strftime('%Y-%m-%dT%H:%M:%S'), 'epoch': int(time.time()),
           'cycle': her_cycle(), 'days_elapsed': round((time.time() - t0) / 86400.0, 4),
           'claim_lambda': lc, 'rival_lambda': lr_, 'baseline_wow': base,
           'deadline': c['DEADLINE'], 'claim_sha256': c['sha256']}
    if t is None:
        row.update({'readable': False, 'why': why, 'lr': None})
    else:
        d = t['wow'] - base
        row.update({'readable': True, 'wow_now': t['wow'], 'tally_at': t['at'],
                    'wow_delta': round(d, 8)})
        if d < -1e-9:
            row['lr'] = None            # a fall is its own fact, never a negative count
            row['blocks'] = None
        else:
            k = int(round(d / REWARD))
            mu_c, mu_r = lc * row['days_elapsed'], lr_ * row['days_elapsed']
            pc, pr = pois(k, mu_c), pois(k, mu_r)
            row.update({'blocks': k, 'mu_claim': round(mu_c, 5), 'mu_rival': round(mu_r, 5),
                        'P_claim': pc, 'P_rival': pr,
                        'lr': (pc / pr) if pr > 0 else float('inf')})
    g = gate()
    hits = g.classify(row)
    row['outcome'] = hits[0] if len(hits) == 1 else 'GATE_ERROR:%s' % hits
    row['about'] = 'THE APPARATUS' if row['outcome'] == 'tally_unreadable' else 'the claim'
    return row


def tick(force=False):
    cyc = her_cycle()
    if not force and cyc and cyc % EVERY:
        return 0
    row = read()
    prev = None
    if os.path.exists(SEEN):
        try: prev = json.load(open(SEEN))
        except Exception: prev = None
    changed = (prev is None or prev.get('outcome') != row['outcome']
               or prev.get('blocks') != row.get('blocks'))
    row['wrote_ledger_row'] = changed
    if changed:
        with open(LEDGER, 'a') as f:
            f.write(json.dumps(row) + '\n')
    json.dump(row, open(SEEN, 'w'))          # the stamp moves on every poll
    if changed and prev is not None:
        print('LEDGER: %s -> %s  (k=%s, %.2f d, LR %s)'
              % (prev.get('outcome'), row['outcome'], row.get('blocks'),
                 row['days_elapsed'],
                 ('%.3g' % row['lr']) if row.get('lr') is not None else 'n/a'))
    return 0


def show():
    r = read()
    print('=' * 86)
    print('THE LEDGER, RUNNING -- claim %s' % r['claim_sha256'][:16])
    print('=' * 86)
    print('  days elapsed    %.4f   deadline %s' % (r['days_elapsed'], r['deadline']))
    if r['readable']:
        print('  baseline        %.8f WOW   now %.8f   delta %+.8f'
              % (r['baseline_wow'], r['wow_now'], r['wow_delta']))
        print('  tally written   %s' % r['tally_at'])
        if r.get('blocks') is not None:
            print('  BLOCKS SINCE    %d' % r['blocks'])
            print('  expected so far claim %.5f   rival %.5f' % (r['mu_claim'], r['mu_rival']))
            print('  P(k|claim) %.6f   P(k|rival) %.6f   LR %.4g'
                  % (r['P_claim'], r['P_rival'], r['lr']))
    else:
        print('  TALLY UNREADABLE: %s' % r.get('why'))
    print('  OUTCOME         %s   (%s)' % (r['outcome'], r['about']))
    print()
    print('  CANNOT TELL is the honest answer early on and this seat says so rather than')
    print('  holding a placeholder. The LR is valid at every elapsed time.')
    return 0


def selftest():
    ok = t = 0
    def chk(n_, got, want):
        nonlocal ok, t; t += 1
        g = got == want; ok += g
        print('   [%s] %-54s got %r want %r' % ('PASS' if g else 'FAIL', n_, got, want))
    print('=' * 86); print('SELFTEST'); print('=' * 86)
    g = gate()
    chk('LR 50 favours',  g.classify({'readable': True, 'lr': 50.0}), ['favours_the_claim'])
    chk('LR 0.01 refuses', g.classify({'readable': True, 'lr': 0.01}), ['refuses_the_claim'])
    chk('LR 1 cannot tell', g.classify({'readable': True, 'lr': 1.0}), ['cannot_tell'])
    chk('a FALL is its own outcome, not a negative count',
        g.classify({'readable': True, 'lr': None}), ['balance_fell_a_spend_or_a_reorg'])
    chk('unreadable tally is APPARATUS',
        g.classify({'readable': False, 'lr': None}), ['tally_unreadable'])
    try:
        g.tally([{'readable': True, 'lr': 50.0}, {'readable': True, 'lr': 0.01},
                 {'readable': True, 'lr': 1.0}, {'readable': True, 'lr': None},
                 {'readable': False, 'lr': None}])
        chk('exhaustive and disjoint', 1, 1)
    except OutcomeCollapse as e:
        print('  ', e); chk('exhaustive and disjoint', 0, 1)
    chk('poisson k=0 mu=0 is 1', pois(0, 0.0), 1.0)
    chk('poisson sums to 1 over k', round(sum(pois(k, 3.0) for k in range(60)), 9), 1.0)
    # the rails of the registered bands, recomputed here from the file not from memory
    c = json.load(open(CLAIM))
    h = c['TWO_HYPOTHESES_AT_THE_SAME_DIFFICULTY']
    lc, lr_ = h['claim_lambda_per_day'], h['rival_lambda_per_day']
    at30 = [pois(k, lc * 30) / pois(k, lr_ * 30) for k in range(5)]
    chk('k=0 at 30 d refutes', at30[0] <= 0.1, True)
    chk('k=3 at 30 d cannot tell', 0.1 < at30[3] < 10, True)
    chk('k=5 at 30 d favours', pois(5, lc * 30) / pois(5, lr_ * 30) >= 10, True)
    chk('registered bands match this arithmetic',
        c['FOUR_OUTCOMES_AFTER_30_DAYS']['CANNOT_TELL_k'], [2, 3, 4])
    print('\n   %d of %d pass' % (ok, t)); return ok == t


if __name__ == '__main__':
    if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
    if '--tick' in sys.argv:     sys.exit(tick())
    sys.exit(show())
