"""Third-date reading for the Zhukov repeat (plan PLAN_ZHUKOV_R2.md.text): today's chain-C signed phase vs 24 Oct and vs his 16-17 Sep, and q16 today.
Run after zhukov.py --real has today's raw files: python3 -I date_reading.py"""
import json, os, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import zhukov as Z
O = os.path.expanduser('~/bones-forge/qia_runs/2026-10-24-fill-zhukov')
def load(d):
    return np.array([np.load(f'{d}/raw_zhukov_{l}.npz')['codes'] for l in Z.ORDER])
def ours(codes, method):
    ev, ses = [], []
    for j in range(len(codes)):
        cc = Z.chainC_counts(codes[j], method); e, se, _ = Z.c1_from_counts(cc['XXX'], cc['YYY'], Z.chainC_ref(method)); ev.append(e); ses.append(se)
    sep = float(np.sqrt(np.sum(np.square(ses))) / len(ev)); m, lo, hi = Z.combine(ev, sep); return m, (hi - lo) / 2, ev
if __name__ == '__main__':
    today, oct24 = load(H), load(O); out = {}
    for method in ('strang8', 'exact'):
        mt, ht, et = ours(today, method); m4, h4, e4 = ours(oct24, method); hv = Z.his_phase(method)[0]
        d = mt - m4; hw = float(np.hypot(ht, h4)); o = Z.outcome_vs_zero(d - hw, d + hw, Z.SCALE_C)
        out[method] = dict(today=mt, today_half=ht, today_jobs=et, oct24=m4, oct24_half=h4, his_sep=hv[0], his_se=hv[1], today_minus_oct24=d, half=hw, outcome=o)
        print('%-8s signed phase error at Jt=4/3: his Sep %+.1f (se %.1f) | ours 24 Oct %+.1f +- %.1f | ours today %+.1f +- %.1f (jobs %s) | today - 24 Oct %+.1f +- %.1f -> %s' % (method, hv[0], hv[1], m4, h4, mt, ht, ' '.join('%+.1f' % x for x in et), d, hw, o))
    json.dump(out, open(H + '/readings_date.json', 'w'), indent=1)
