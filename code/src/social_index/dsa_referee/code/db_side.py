"""Referee: compute delivered counts from my own reduction (out/red.parquet) and compare with dsa.json."""
import sys, os, site, json, collections as C
sys.path.append(site.getusersitepackages())
import pyarrow.parquet as pq
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
DSA = '/Users/heuremen/bones-forge/social_index/dsa'
PER = {'2025H2': ('2025-07-01', '2025-12-31'), '2026H1': ('2026-01-01', '2026-06-30')}
NAMES = {'Facebook': 'Facebook', 'Instagram': 'Instagram', 'TikTok': 'TikTok', 'YouTube': 'YouTube', 'X': 'X', 'LinkedIn': 'LinkedIn',
         'Snapchat': 'Snapchat', 'Pinterest': 'Pinterest', 'Amazon Store': 'Amazon', 'AliExpress': 'AliExpress', 'Temu': 'Temu', 'Shein': 'Shein',
         'Zalando': 'Zalando', 'Booking.com': 'Booking.com', 'Apple App Store': 'App Store', 'Google Maps': 'Google Maps', 'Google Play': 'Google Play',
         'Google Shopping': 'Google Shopping', 'Pornhub': 'Pornhub', 'XVideos': 'XVideos', 'XNXX': 'XNXX', 'Stripchat': 'Stripchat', 'WhatsApp Channels': 'WhatsApp Channels'}

def load():
    df = pq.read_table(os.path.join(OUT, 'red.parquet')).to_pandas()
    df['cre'] = df['cre'].astype(str); df['app'] = df['app'].astype(str)
    return df

FU, PA, NA = 'AUTOMATED_DECISION_FULLY', 'AUTOMATED_DECISION_PARTIALLY', 'AUTOMATED_DECISION_NOT_AUTOMATED'
VOL, A16, TF, OTH = 'SOURCE_VOLUNTARY', 'SOURCE_ARTICLE_16', 'SOURCE_TRUSTED_FLAGGER', 'SOURCE_TYPE_OTHER_NOTIFICATION'
ILL, INC = 'DECISION_GROUND_ILLEGAL_CONTENT', 'DECISION_GROUND_INCOMPATIBLE_CONTENT'

def masks(d):
    return {
        'total': pd.Series(True, index=d.index), 'solely': d.ad == FU, 'not': d.ad == NA, 'PA': d.ad == PA,
        'own': d.src == VOL, 'own_illegal': (d.src == VOL) & (d.gr == ILL), 'own_tc': (d.src == VOL) & (d.gr == INC),
        'own_auto': (d.src == VOL) & (d.ad == FU), 'notice': d.src.isin([A16, TF]), 'notice_tf': d.src == TF,
        'OTH': d.src == OTH, 'OTH_ILL': (d.src == OTH) & (d.gr == ILL), 'OTH_INC': (d.src == OTH) & (d.gr == INC),
        'VOL_DET': (d.src == VOL) & (d.det == 'Yes'), 'VOL_FUPA': (d.src == VOL) & d.ad.isin([FU, PA]), 'A16': d.src == A16,
    }

def counts(df, dbn, per):
    a, b = PER[per]
    d = df[df.platform == dbn]
    app = d[(d.app >= a) & (d.app <= b)]
    cre = d[(d.cre >= a) & (d.cre <= b)]
    out = {}
    ma, mc = masks(app), masks(cre)
    for k in ma:
        out[k] = dict(app=int(app.n[ma[k]].sum()), cre=int(cre.n[mc[k]].sum()), app_noneu=int(app.n[ma[k] & (app.sc == 'NONEU_ONLY')].sum()),
                      app_empty=int(app.n[ma[k] & (app.sc == 'EMPTY')].sum()))
    return out

if __name__ == '__main__':
    df = load()
    rows = json.load(open(os.path.join(DSA, 'data', 'dsa.json')))
    mism = []
    allc = {}
    for svc, dbn in NAMES.items():
        for per in PER:
            c = counts(df, dbn, per); allc['%s|%s' % (svc, per)] = c
            for r in rows:
                if r['platform'] != svc or r['period'] != per or r['measure'] in ('share',) or 'delivered' not in r: continue
                m = r['measure']; dv = r['delivered']
                if m == 'own_auto':
                    continue
                mine_app, mine_cre = c[m]['app'], c[m]['cre']
                if mine_app != dv['D_app'] or mine_cre != dv['D_cre'] or c[m]['app_noneu'] != dv['eea_only']:
                    mism.append((svc, per, m, dv['D_app'], mine_app, dv['D_cre'], mine_cre, dv['eea_only'], c[m]['app_noneu']))
    print('mismatches D_app/D_cre/eea_only:', len(mism))
    for x in mism[:40]: print(x)
    json.dump(allc, open(os.path.join(OUT, 'mycounts.json'), 'w'), indent=0)
