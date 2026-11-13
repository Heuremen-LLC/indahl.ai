#!/usr/bin/env python3
"""dsa_tick.py: SOCIAL section 1, two filings, one platform. Per PLAN.md (committed before any comparison count) and its dated addenda.
Reads each VLOP's harmonised DSA transparency report against the same platform's statements of reasons in the EU DSA Transparency
Database (Commission monthly aggregates, CC BY 4.0). Rerunnable: refreshes aggregates whose sha1 changed, re-reads every report file
on disk, rewrites data/dsa.json, data/automation_*.json, data/sources.json, data/context_notes.json, summary_dsa.json, section_dsa.html
and the trimmed public files in public/.
Run: /usr/bin/python3 -I dsa_tick.py [--no-refresh]. No timers, no network writes."""
import os, sys, site, json, time, math, glob, re, collections as C
sys.path.append(site.getusersitepackages())
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); sys.path.insert(1, os.path.expanduser('~/bones-forge/launch_index'))
import dsa_db, dsa_reports
import heuremen_kit as K
import pyarrow.parquet as pq

PERIODS = {'2025H2': ('2025-07-01', '2025-12-31'), '2026H1': ('2026-01-01', '2026-06-30')}
PLABEL = {'2025H2': 'July to December 2025', '2026H1': 'January to June 2026'}
LO_B, HI_B = 0.90, 1.10        # PLAN.md: agreement band for the ratio
SH_B = 0.05                    # PLAN.md: agreement band for shares (5 points)
FLOOR = 100                    # Addendum 6.8: an edge must be cleared by at least 100 statements
SLUG = {'facebook': 'Facebook', 'instagram': 'Instagram', 'whatsapp_channels': 'WhatsApp Channels', 'tiktok': 'TikTok', 'x': 'X', 'snapchat': 'Snapchat',
        'linkedin': 'LinkedIn', 'pinterest': 'Pinterest', 'amazon': 'Amazon Store', 'aliexpress': 'AliExpress', 'temu': 'Temu', 'shein': 'Shein', 'zalando': 'Zalando',
        'booking': 'Booking.com', 'apple_app_store': 'Apple App Store', 'wikipedia': 'Wikipedia', 'pornhub': 'Pornhub', 'xvideos': 'XVideos', 'xnxx': 'XNXX',
        'stripchat': 'Stripchat', 'youtube': 'YouTube', 'google_maps': 'Google Maps', 'google_play': 'Google Play', 'google_shopping': 'Google Shopping'}
VLOPS = list(dsa_db.NAMES) + ['Wikipedia']
ADS_SERVICES = ('YouTube', 'Google Maps', 'Google Play')          # Addendum 6.1: reports with separate ads templates
COMBINED = ('Facebook and Instagram', ('Facebook', 'Instagram'))   # Addendum 6.3
MEASURES = ['total', 'solely', 'not', 'own', 'own_illegal', 'own_tc', 'own_auto', 'notice', 'notice_tf']
ADS_MEASURES = ['total', 'solely', 'not', 'own_tc']
COMBINED_MEASURES = ['total', 'solely', 'not', 'own', 'own_tc', 'own_auto']
MLABEL = {'total': 'All measures', 'solely': 'Solely automated', 'not': 'Not automated', 'own': 'Own initiative', 'own_illegal': 'Own initiative, illegal content',
          'own_tc': 'Own initiative, terms and conditions', 'own_auto': 'Own initiative, solely automated', 'notice': 'Actions on notices', 'notice_tf': 'Actions on trusted flagger notices',
          'share': 'Solely automated share'}
FILTER = {'total': 'all statements', 'solely': 'automated_decision fully automated (partially automated added to the upper edge)',
          'not': 'automated_decision not automated (partially automated added to the upper edge)',
          'own': 'source_type own voluntary initiative (other type of notification, and notice-labelled statements beyond the items notified, added to the upper edge)',
          'own_illegal': 'own voluntary initiative and ground illegal content (other type of notification with the same ground, own initiative with the other ground, and notice-labelled statements beyond the items notified, added to the upper edge)',
          'own_tc': 'own voluntary initiative and ground incompatible with terms and conditions (other type of notification with the same ground, own initiative with the other ground, and notice-labelled statements beyond the items notified, added to the upper edge)',
          'own_auto': 'own voluntary initiative and fully automated decision. Band from the lesser of that and own initiative with automated detection to the greater of own initiative fully or partially automated and own initiative with automated detection',
          'notice': 'source_type Article 16 notice or trusted flagger. Band from zero to every statement the platform filed, ads included (Addendum 6.2)', 'notice_tf': 'source_type trusted flagger. Band from zero to every statement the platform filed, ads included (Addendum 6.2)',
          'share': 'fully automated over all statements. Band to fully plus partially automated over all statements'}
SCOPE_TEXT = {'all': 'all statements', 'nonads': 'statements not flagged as ads (CONTENT_TYPE_AD false)', 'ads': 'statements flagged as ads (CONTENT_TYPE_AD true)'}

FU, PA, NA = 'AUTOMATED_DECISION_FULLY', 'AUTOMATED_DECISION_PARTIALLY', 'AUTOMATED_DECISION_NOT_AUTOMATED'
VOL, A16, TF, OTH = 'SOURCE_VOLUNTARY', 'SOURCE_ARTICLE_16', 'SOURCE_TRUSTED_FLAGGER', 'SOURCE_TYPE_OTHER_NOTIFICATION'
ILL, INC = 'DECISION_GROUND_ILLEGAL_CONTENT', 'DECISION_GROUND_INCOMPATIBLE_CONTENT'
PRED = {'all': lambda k: True, 'FU': lambda k: k[0] == FU, 'PA': lambda k: k[0] == PA, 'NA': lambda k: k[0] == NA, 'FUPA': lambda k: k[0] in (FU, PA),
        'VOL': lambda k: k[2] == VOL, 'OTH': lambda k: k[2] == OTH, 'VOL_ILL': lambda k: k[2] == VOL and k[3] == ILL, 'OTH_ILL': lambda k: k[2] == OTH and k[3] == ILL,
        'VOL_INC': lambda k: k[2] == VOL and k[3] == INC, 'OTH_INC': lambda k: k[2] == OTH and k[3] == INC, 'VOL_FU': lambda k: k[2] == VOL and k[0] == FU,
        'VOL_FUPA': lambda k: k[2] == VOL and k[0] in (FU, PA), 'VOL_DET': lambda k: k[2] == VOL and k[1] == 'Yes', 'NOT': lambda k: k[2] in (A16, TF), 'TF': lambda k: k[2] == TF,
        'NOT_ILL': lambda k: k[2] in (A16, TF) and k[3] == ILL, 'NOT_INC': lambda k: k[2] in (A16, TF) and k[3] == INC,
        'DET': lambda k: k[1] == 'Yes', 'FU_NODET': lambda k: k[0] == FU and k[1] == 'No', 'NA_DET': lambda k: k[0] == NA and k[1] == 'Yes'}
def cnt(c, pred, eea=False):
    f = PRED[pred]
    return sum(v for k, v in c.items() if f(k) and (k[4] if eea else True))

LATE_DAYS = ('2026-10-31', '2026-11-03')   # Addendum 1.2: neighbours of the two missing dump days (1 and 2 Nov 2026)
BASES = ('app', 'cre')
def load_db(refresh):
    st = dsa_db.run() if refresh else json.load(open(os.path.join(H, 'data', 'db_status.json')))
    t = pq.read_table(os.path.join(H, 'data', 'db_reduced.parquet')).to_pydict()
    rows = list(zip(t['platform_name'], t['cre'], t['app'], t['automated_decision'], t['automated_detection'], t['source_type'], t['decision_ground'], t['eea_only'], t['is_ad'], t['count']))
    return st, rows

def accumulate(rows):
    """acc[(key, period, basis, scope)][(ad, det, src, ground, eea)] = statements. key: database platform name, or 'META' for Facebook plus Instagram.
    basis app = application_date in period, cre = created_at in period, late:<day> = created that day with application_date in period. scope: all, nonads, ads."""
    acc = C.defaultdict(C.Counter); meta = set(dsa_db.NAMES[x] for x in COMBINED[1])
    for (p, cre, app, ad, det, src, gr, eea, isad, n) in rows:
        keys = [p] + (['META'] if p in meta else [])
        scopes = ('all', 'ads' if isad else 'nonads')
        k5 = (ad, det, src, gr, eea)
        for per, (a, b) in PERIODS.items():
            ina = app is not None and a <= app <= b; inc = a <= cre <= b
            if not (ina or inc): continue
            for key in keys:
                for sc in scopes:
                    if ina:
                        acc[(key, per, 'app', sc)][k5] += n
                        if cre in LATE_DAYS: acc[(key, per, 'late:' + cre, sc)][k5] += n
                    if inc: acc[(key, per, 'cre', sc)][k5] += n
    return acc

SHORTFALL = {}   # Addendum 3: per-platform statements in the published dumps of 30 Sep to 2 Oct 2026 not in the aggregate
BASE = {'total': 'all', 'solely': 'FU', 'not': 'NA', 'own': 'VOL', 'own_illegal': 'VOL_ILL', 'own_tc': 'VOL_INC', 'own_auto': 'VOL_FU', 'notice': 'NOT', 'notice_tf': 'TF'}
ADD_PLAN = {'solely': ['PA'], 'not': ['PA'], 'own': ['OTH'], 'own_illegal': ['OTH_ILL'], 'own_tc': ['OTH_INC'], 'notice': ['OTH']}
ADD_FINAL = {'solely': ['PA'], 'not': ['PA'], 'own': ['OTH'], 'own_illegal': ['OTH_ILL', 'VOL_INC'], 'own_tc': ['OTH_INC', 'VOL_ILL']}   # Addendum 6.6 ground allowance
SRC_EXTRA = {'own': 'NOT', 'own_illegal': 'NOT_ILL', 'own_tc': 'NOT_INC'}                                        # Addendum 6.6 source allowance (own, own illegal, own T&C, as committed)

def delivered(acc, key, per, m, scope, sf, final=True, items=None):
    cs = {b: acc.get((key, per, b, scope), C.Counter()) for b in BASES}
    lates = [acc.get((key, per, 'late:' + d_, scope), C.Counter()) for d_ in LATE_DAYS]
    a, c = cs['app'], cs['cre']; base = BASE[m]
    d_app, d_cre = cnt(a, base), cnt(c, base)
    out = dict(D_app=d_app, D_cre=d_cre, scope=scope, partial_app=cnt(a, 'PA'))
    if final and m in ('notice', 'notice_tf'):   # Addendum 6.2(b): the two filings label notice sources differently
        ha = {b: acc.get((key, per, b, 'all'), C.Counter()) for b in BASES}; hl = [acc.get((key, per, 'late:' + d_, 'all'), C.Counter()) for d_ in LATE_DAYS]   # every statement, ads included
        hi = max(cnt(ha['app'], 'all'), cnt(ha['cre'], 'all')); lt = max(cnt(l, 'all') for l in hl)
        out.update(eea_only=cnt(a, base, eea=True), D_lo=0, D_hi=hi + 2 * lt + sf, missing_days_allowance=2 * lt, short_days_allowance=sf, all_statements_app=cnt(ha['app'], 'all'),
                   notice_label_rule=True, D_lo_labelled=max(0, min(d_app, d_cre) - cnt(a, base, eea=True)))
        return out
    if m == 'own_auto':
        lo_c = min((cnt(a, 'VOL_FU'), 'VOL_FU'), (cnt(a, 'VOL_DET'), 'VOL_DET'))[1]
        eea = cnt(a, lo_c, eea=True)
        lo = min(cnt(a, 'VOL_FU'), cnt(a, 'VOL_DET'), cnt(c, 'VOL_FU'), cnt(c, 'VOL_DET')) - eea
        his = [max(cnt(x, 'VOL_FUPA'), cnt(x, 'VOL_DET')) for x in (a, c)]
        lt = max(max(cnt(l, 'VOL_FUPA'), cnt(l, 'VOL_DET')) for l in lates)
        extra = 0
        hi = max(his)
    else:
        adds = (ADD_FINAL if final else ADD_PLAN).get(m, [])
        eea = cnt(a, base, eea=True)
        lo = min(d_app, d_cre) - eea
        ex = {b: 0 for b in BASES}
        if final and m in SRC_EXTRA and items is not None:
            ex = {b: max(0, cnt(cs[b], SRC_EXTRA[m]) - items) for b in BASES}
        hi = max(cnt(cs[b], base) + sum(cnt(cs[b], x) for x in adds) + ex[b] for b in BASES)
        lt = max(cnt(l, base) + sum(cnt(l, x) for x in adds) for l in lates)
        extra = max(ex.values())
        out['added_app'] = sum(cnt(a, x) for x in adds)
    out.update(eea_only=eea, D_lo=max(0, lo), D_hi=hi + 2 * lt + sf, missing_days_allowance=2 * lt, short_days_allowance=sf, source_allowance=extra)
    return out

def stated(vals, m):
    """Returns (S, how, parts). parts: list of value dicts quoted (components for combined rows)."""
    def g(k): return vals.get(k)
    def flat(xs):
        out = []
        for x in xs:
            if x is None: continue
            out += x.get('components', [x])
        return out
    pairs = {'total': ('solely', 'not', 'the report leaves solely or not automated blank', 'solely plus not automated, summed by us'),
             'own': ('own_illegal', 'own_tc', 'the report leaves sheet 5 or sheet 6 TOTAL blank', 'sheet 5 TOTAL plus sheet 6 TOTAL, summed by us'),
             'own_auto': ('own_auto_illegal', 'own_auto_tc', 'the report leaves sheet 5 or sheet 6 TOTAL blank', 'sheet 5 TOTAL plus sheet 6 TOTAL, summed by us'),
             'notice': ('notice_law', 'notice_tc', 'the report leaves the actions on notices blank', 'actions on the basis of the law plus on the basis of the terms and conditions, summed by us'),
             'notice_tf': ('notice_tf_law', 'notice_tf_tc', 'the report leaves the actions on notices blank', 'actions on the basis of the law plus on the basis of the terms and conditions, summed by us')}
    if m in pairs:
        k1, k2, blank, how = pairs[m]; a, b = g(k1), g(k2)
        if not a or not b or a.get('value') is None or b.get('value') is None: return None, blank, flat([a, b])
        return a['value'] + b['value'], how, flat([a, b])
    a = g(m)
    if not a or a.get('value') is None: return None, 'the report leaves this field blank', flat([a])
    return a['value'], None, flat([a])

def fr(x):
    if x is None: return None
    if x == math.inf: return 'unbounded'
    return float('%.5g' % x)

RC = {'last': None}
def classify_floor(S, S_lo, S_hi, D_lo, D_hi, D_app, floor=True):
    """Plan ratio rule, with the Addendum 6.8 floor when floor is True. Returns (outcome, r, rlo, rhi, floored)."""
    # 12 Nov 2026, Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md): K.read with the closed band 0.90 to 1.10. A stated zero has the band 0 to 0, since 10 percent of zero is zero.
    # RC['last'] holds the closed reason of a CANNOT_TELL: STRADDLES_EDGE for a range crossing an edge or clearing it by less than the floor.
    RC['last'] = None
    if S == 0:
        oc, rc = K.read(D_lo, D_hi, band=(0.0, 0.0))
        if oc == K.ABOVE and floor and D_lo < FLOOR: RC['last'] = K.STRADDLES_EDGE; return K.CANNOT_TELL, None, None, None, True
        RC['last'] = rc; return oc, None, None, None, False
    r = D_app / S; rlo = D_lo / S_hi if S_hi > 0 else math.inf; rhi = (D_hi / S_lo) if S_lo > 0 else math.inf
    oc, rc = K.read(rlo, rhi, band=(LO_B, HI_B))
    if floor and oc == K.ABOVE and D_lo - HI_B * S_hi < FLOOR: RC['last'] = K.STRADDLES_EDGE; return K.CANNOT_TELL, r, rlo, rhi, True
    if floor and oc == K.BELOW and LO_B * S_lo - D_hi < FLOOR: RC['last'] = K.STRADDLES_EDGE; return K.CANNOT_TELL, r, rlo, rhi, True
    RC['last'] = rc; return oc, r, rlo, rhi, False

def fmt_r(x):
    if x is None: return 'none'
    if x == math.inf: return 'unbounded'
    if x == 0: return '0'
    if abs(x - LO_B) < 0.005 or abs(x - HI_B) < 0.005: return '%.5g' % x
    if x >= 100: return '{:,.0f}'.format(x)
    if x >= 10: return '%.1f' % x
    if x >= 0.1: return '%.2f' % x
    return '%.2g' % x

RULE_TEXT = {'6.1': 'This row counts only statements not flagged as ads, against the main report files. The ads are read on their own rows.',
             '6.4': 'The stated lower edge is the largest restriction column, because the TOTAL equals the sum of its columns or the report says it is a column sum.',
             '6.5': 'The report’s all-measures total equals its column-sum TOTALs (plus notice actions), so it carries the same lower edge.',
             '6.6': 'Own-initiative statements of the other ground, and notice-labelled statements beyond the notified items, are added to the upper edge.',
             '6.8': 'The band clears an agreement edge by fewer than 100 statements.'}
BELOW_UNSIZED = ('Neither source sizes some differences: statements are not required where the recipient’s contact details are unknown, or for deceptive high-volume commercial content that a report does not label as spam (DSA Article 17(2)), a filing can count one decision per item, per account or per restriction type '
                 '(a TOTAL built as a column sum counts a decision once in each column), a report can count content filtered at upload, and statements filed after the newest aggregate are not counted.')
ABOVE_UNSIZED = ('Neither source sizes some differences: each filing decides which decisions concern the EU, and one decision filed as more than one statement is counted more than once, since the aggregates cannot detect re-filings.')
def reason_text(oc, rlo, rhi, S, floored=False):
    if S == 0:
        if floored: return 'The report states zero and the database holds fewer than %d matching statements across the whole band, too few to decide (Addendum 6.8, defined after the data).' % FLOOR
        return {K.CONSISTENT: 'The report states zero and the database holds no matching statements.', K.ABOVE: 'The report states zero and the database holds at least %d matching statements across the whole band. ' % FLOOR + ABOVE_UNSIZED,
                K.CANNOT_TELL: 'The report states zero and the band reaches zero.'}[oc]
    band = 'The ratio band runs from %s to %s.' % (fmt_r(rlo), fmt_r(rhi))
    if floored: return band + ' It clears an agreement edge by fewer than %d statements, too few to decide (Addendum 6.8, defined after the data).' % FLOOR
    if oc == K.CONSISTENT: return band + ' It lies inside 0.90 to 1.10, so the database count agrees with the stated figure within a tenth.'
    if oc == K.ABOVE: return band + ' Its lower edge is above 1.10. The database holds more statements than the report states measures, beyond every scope difference we can size. ' + ABOVE_UNSIZED
    if oc == K.BELOW: return band + ' Its upper edge is below 0.90. The database holds fewer statements than the report states measures, beyond every scope difference we can size. ' + BELOW_UNSIZED
    edge = []
    if rlo < LO_B <= rhi: edge.append('0.90')
    if rlo <= HI_B < rhi: edge.append('1.10')
    return band + (' It crosses %s, so we cannot tell.' % ' and '.join(edge) if edge else ' We cannot tell.')

# Addendum 4 and 6.3 (defined after the data): platform-declared scope notes. inflated: BELOW/CONSISTENT -> CT; deflated: ABOVE/CONSISTENT -> CT; both: any -> CT.
POSTHOC = [
    dict(platform='Snapchat', periods=('2025H2', '2026H1'), measures=('total', 'solely', 'not', 'share'), direction='inflated', sheet='8', contains='content approvals'),
    dict(platform='Snapchat', periods=('2026H1',), measures=('total', 'not', 'share'), direction='inflated', sheet='8', contains='human-processed notices'),
    dict(platform='Snapchat', periods=('2025H2', '2026H1'), measures=('notice_tf',), direction='deflated', sheet='4', contains="single 'action'"),
    dict(platform='Snapchat', periods=('2025H2',), measures=('notice', 'notice_tf'), direction='deflated', sheet='4', contains='reclassified to the', addendum='6.3'),
    dict(platform='X', periods=('2025H2', '2026H1'), measures=('own_auto',), direction='inflated', sheet='6', contains='auto-closed moderation cases'),
    dict(platform='Amazon Store', periods=('2025H2', '2026H1'), measures=('own_illegal',), direction='deflated', sheet='5', contains='report 100% of actions'),
    dict(platform='Amazon Store', periods=('2025H2', '2026H1'), measures=('own_tc',), direction='inflated', sheet='5', contains='report 100% of actions'),
    dict(platform='Booking.com', periods=('2025H2', '2026H1'), measures=('notice', 'notice_tf'), direction='inflated', sheet='4', contains='global scale'),
    dict(platform='Facebook', periods=('2025H2', '2026H1'), measures=('total', 'solely', 'not', 'own', 'own_tc', 'own_auto', 'share'), direction='both', sheet='6', contains='for Facebook and Instagram combined', addendum='6.3'),
    dict(platform='Instagram', periods=('2025H2', '2026H1'), measures=('total', 'solely', 'not', 'own', 'own_tc', 'own_auto', 'share'), direction='both', sheet='6', contains='for Facebook and Instagram combined', addendum='6.3'),
]
# Addendum 5 note triggers (6.4 adds the arithmetic trigger)
COLSUM_NOTE = [dict(platform='TikTok', periods=('2025H2', '2026H1'), mode='sum', contains='sum all of the enforcement actions'),
               dict(platform='X', periods=('2025H2', '2026H1'), mode='sum', contains='Represents the sum of all own initiative measures'),
               dict(platform='Snapchat', periods=('2026H1',), mode='sum', contains='counts two measures'),
               dict(platform='Snapchat', periods=('2025H2',), mode='outside', contains='warnings issued without content removal')]

def ival(vals, k):
    v = vals.get(k)
    return v.get('value') if isinstance(v, dict) else v
def cols_of(vals, k):
    return [v for v in ((vals.get('cols_' + k) or {}).get('value') or {}).values() if isinstance(v, int)]

def colsum_info(vals, sheet, note_mode):
    """Addendum 5 / 6.4 per sheet: returns (qualifies, lo_edge, colsum, mode). lo_edge is the largest column when the TOTAL qualifies."""
    total = ival(vals, {'5': 'own_illegal', '6': 'own_tc'}[sheet]); cols = cols_of(vals, sheet)
    if total is None: return False, None, None, None
    arith = bool(cols) and sum(cols) == total and total > 0
    if vals.get('_combined_maxcol_' + sheet) is not None:   # combined Meta rows: larger of the two services' largest columns
        q = vals.get('_combined_qualifies_' + sheet)
        return q, (vals['_combined_maxcol_' + sheet] if q else total), None, 'sum'
    if note_mode == 'outside' and cols: return True, max(cols), sum(cols), 'outside'
    if (arith or note_mode == 'sum') and cols: return True, max(cols), sum(cols), 'arithmetic' if arith else 'note'
    return False, total, sum(cols) if cols else None, None

def find_reports():
    base = os.path.join(H, 'data', 'raw', 'reports'); out = []
    for d in sorted(glob.glob(os.path.join(base, '*', '*'))):
        if not os.path.isdir(d): continue
        slug = os.path.basename(os.path.dirname(d))
        if slug == 'google':
            svc = os.path.basename(d).split('__')[0].replace('_', ' ')
            if svc not in SLUG.values(): continue
        else:
            svc = SLUG.get(slug)
            if not svc: continue
        files = [f for f in glob.glob(os.path.join(d, '**', '*'), recursive=True) if os.path.isfile(f) and 'unzipped' not in f.split(os.sep) and f.lower().endswith(('.zip', '.csv', '.xlsx', '.xls', '.pdf', '.html'))]
        src = open(os.path.join(d, 'source_url.txt')).read().strip() if os.path.exists(os.path.join(d, 'source_url.txt')) else None
        pg = open(os.path.join(d, 'page_url.txt')).read().strip() if os.path.exists(os.path.join(d, 'page_url.txt')) else None
        out.append(dict(service=svc, dir=d, files=files, source_url=src, page_url=pg))
    return out

def context_notes(path):
    sh = dsa_reports.collect(path); out = {}
    for k in ('8', '5', '6', '4', '8a', '6a'):
        if k not in sh: continue
        rows = sh[k]['rows']; hi = dsa_reports.header_index(rows, 'applicability') or dsa_reports.header_index(rows, 'indicator') or 0; hdr = rows[hi]
        ctx = [j for j, h in enumerate(hdr) if 'contextual' in dsa_reports.norm(h)]
        for i in range(hi + 1, len(rows)):
            row = rows[i]; nn = ' '.join(dsa_reports.norm(c) for c in row[:7])
            hit = (k in ('8', '8a') and ('number of measures solely' in nn or 'number of measures not taken' in nn) and (' total number' in nn or ' total ' in nn + ' ')) or (k not in ('8', '8a') and any(dsa_reports.norm(c) == 'total' for c in row[3:4]))
            if not hit: continue
            for j in ctx:
                if j < len(row) and row[j].strip(): out['%s|%s|%s' % (k, row[4][:40] if k in ('8', '8a') else 'TOTAL', hdr[j].strip())] = row[j].strip()
    return out
def note_sentence(notes, sheet, contains):
    for fk, txt in notes.items():
        if fk.startswith(sheet + '|') and contains.lower() in txt.lower():
            parts = re.split(r'(?<=[.!?])\s+', txt)
            hit = [x for x in parts if contains.lower() in x.lower()]
            return (' '.join(hit) if hit else txt), fk
    return None, None

def ads_vals(v):
    """The Ads template read as a report of its own (Addendum 6.1)."""
    m = {'solely': 'ads_solely', 'not': 'ads_not', 'own_tc': 'ads_own_tc', 'own_auto_tc': 'ads_own_auto_tc', 'cols_6': 'cols_6a', 'spam_6': 'spam_6a', 'colsum_equal_6': 'colsum_equal_6a'}
    out = {k: v.get(src) for k, src in m.items() if v.get(src) is not None}
    return out

def combined_vals(vs):
    """Facebook plus Instagram, summed key by key; components keep each service's verbatim quote (Addendum 6.3)."""
    out = {}
    for k in ('solely', 'not', 'own_illegal', 'own_tc', 'own_auto_illegal', 'own_auto_tc', 'orders_items', 'spam_5', 'spam_6'):
        xs = [v.get(k) for v in vs]
        if any(x is None or not isinstance(x, dict) or x.get('value') is None for x in xs): continue
        comps = [dict(x, service=s) for x, s in zip(xs, COMBINED[1]) if 'quote' in x]
        out[k] = dict(value=sum(x['value'] for x in xs), components=comps)
    for sh in ('5', '6'):
        cs = [cols_of(v, sh) for v in vs]; tots = [ival(v, {'5': 'own_illegal', '6': 'own_tc'}[sh]) for v in vs]
        if all(cs) and all(t is not None for t in tots):
            out['_combined_maxcol_' + sh] = max(max(c) for c in cs)
            out['_combined_qualifies_' + sh] = all(sum(c) == t for c, t in zip(cs, tots))
            out['cols_' + sh] = dict(value={'largest single column, either service': max(max(c) for c in cs)})
    return out

def main(refresh=True):
    st, dbrows = load_db(refresh)
    acc = accumulate(dbrows)
    sfs = st.get('shortfall_addendum3', {})
    sf_ok = bool(sfs) and all(v.get('status') == 'OK' and not v.get('days_without_published_row') for v in sfs.values())
    SHORTFALL.update({k: v.get('shortfall', 0) for k, v in sfs.items()}); SHORTFALL['META'] = sum(SHORTFALL.get(dsa_db.NAMES[x], 0) for x in COMBINED[1])
    newest = st.get('newest_created_day')
    reps = find_reports(); sources = []; parsed = {}
    for r in reps:
        tmpl = [f for f in r['files'] if f.lower().endswith(('.zip', '.csv', '.xlsx', '.xls'))]
        rec = dict(service=r['service'], dir=os.path.relpath(r['dir'], H), source_url=r['source_url'], page_url=r['page_url'],
                   files=[dict(path=os.path.relpath(f, H), sha256=dsa_reports.sha256(f), bytes=os.path.getsize(f)) for f in r['files']])
        if not tmpl:
            rec['status'] = 'no template file (PDF or HTML only)'; sources.append(rec); continue
        want = [r['service'], dsa_db.NAMES.get(r['service'], '')]
        try: rep = dsa_reports.read_report(r['dir'], want)
        except Exception as e:
            rec['status'] = 'did not parse: %s' % type(e).__name__; sources.append(rec); continue
        idn = rep.get('identification', {}); start = (idn.get('start') or {}).get('iso'); end = (idn.get('end') or {}).get('iso')
        per = next((k for k, (a, b) in PERIODS.items() if start == a and end == b), None)
        rec.update(status='read' if per else 'period not one of the two read', period=per, start=start, end=end, published=(idn.get('published') or {}).get('iso') or (idn.get('published') or {}).get('value'),
                   published_verbatim=(idn.get('published') or {}).get('value'), published_quote=(idn.get('published') or {}).get('quote'), sheets=rep['sheets'], problems=rep['problems'])
        if per and rec.get('published') and rec['published'] < PERIODS[per][1]: rec['published_display'] = rec.get('published_verbatim'); rec['published_note'] = 'the cell reads %s, which as month/day falls before the period ends' % rec.get('published_verbatim')
        sources.append(rec)
        if per:
            if (r['service'], per) in parsed:
                old = parsed[(r['service'], per)]
                if (rec['published'] or '') < (old['rec']['published'] or ''): rec['status'] = 'earlier version, not read'; continue
                old['rec']['status'] = 'earlier version, not read'
            parsed[(r['service'], per)] = dict(rep=rep, rec=rec, notes=context_notes(r['dir']))
    kg3 = parsed.get(('YouTube', '2026H1'))
    kg3_ok = bool(kg3) and kg3['rep']['values'].get('solely', {}).get('value') == 34496297 and kg3['rec']['published'] == '2026-08-28'
    KG_plan = dict(KG1=st['KG1']['passed'], KG2=st['KG2']['passed'], KG3=kg3_ok, KG4=st['KG4']['passed'])
    failed_days = set(r['day'] for r in st.get('KG1all', {}).get('failures', []))
    handled = set(dsa_db.SHORT_DAYS) if sf_ok else set()
    KG = dict(KG1=st['KG1']['passed'], KG1all=bool(st.get('KG1all')) and failed_days <= handled and not st['KG1all'].get('published_days_missing_in_aggregate'), KG3=kg3_ok)
    months_bad = [m for m, v in st['months'].items() if v.get('complete') != 'OK']

    # views: (display name, service, period) -> how to read both sides
    views = []
    for svc in VLOPS:
        for per in PERIODS:
            pr = parsed.get((svc, per)); dbn = dsa_db.NAMES.get(svc)
            views.append(dict(name=svc, svc=svc, per=per, kind='main', key=dbn, scope='nonads' if svc in ADS_SERVICES else 'all', pr=pr, measures=MEASURES,
                              vals=(pr['rep']['values'] if pr else None), sf=SHORTFALL.get(dbn, 0) if dbn else 0))
    for per in PERIODS:   # combined Meta view
        prs = [parsed.get((s, per)) for s in COMBINED[1]]
        if all(prs):
            views.append(dict(name=COMBINED[0], svc=COMBINED[0], per=per, kind='combined', key='META', scope='all', pr=dict(rec=prs[0]['rec'], notes={}, parts=prs), measures=COMBINED_MEASURES,
                              vals=combined_vals([p['rep']['values'] for p in prs]), sf=SHORTFALL['META']))
    for svc in ADS_SERVICES:   # ads views
        for per in PERIODS:
            pr = parsed.get((svc, per))
            if pr and pr['rep']['values'].get('ads_solely') is not None:
                views.append(dict(name=svc + ' (ads)', svc=svc, per=per, kind='ads', key=dsa_db.NAMES[svc], scope='ads', pr=pr, measures=ADS_MEASURES,
                                  vals=ads_vals(pr['rep']['values']), sf=SHORTFALL.get(dsa_db.NAMES[svc], 0)))

    out_rows = []
    for v in views:
        svc, per, pr, vals, key = v['svc'], v['per'], v['pr'], v['vals'], v['key']
        main = v['kind'] == 'main'
        for m in v['measures'] + ['share']:
            if m == 'share' and not (pr and key): continue
            row = dict(platform=v['name'], db_name=(key if main else None), db_names=([dsa_db.NAMES[x] for x in COMBINED[1]] if v['kind'] == 'combined' else ([key] if key else [])),
                       view=v['kind'], db_scope=SCOPE_TEXT[v['scope']], period=per, period_label=PLABEL[per], measure=m, measure_label=MLABEL[m], filter=FILTER[m])
            if v['kind'] != 'main': row['defined_after_data'] = 'Addendum 6.1' if v['kind'] == 'ads' else 'Addendum 6.3'
            if not pr:
                if m == 'share': continue
                here = [s_ for s_ in sources if s_['service'] == svc and os.path.basename(s_['dir']) == per]
                if any(s_['status'].startswith('no template file') for s_ in here): why = 'The report for this half-year is published as a web page, not in the template files.'
                elif svc == 'WhatsApp Channels' and per == '2025H2': why = 'No report as a very large platform covers this half-year. The January to June 2026 report gives 26 January 2026 as the start of that period.'
                else: why = 'No report for this half-year was found without a key or a login.'
                row.update(outcome=K.CANNOT_TELL, reason_code=K.NO_INTERVAL_FORMABLE, reason=why, status='no stated figure, read succeeded'); out_rows.append(row); continue
            row['source_url'] = pr['rec']['source_url']; row['published'] = pr['rec']['published']
            if m == 'share':
                out_rows.append(share_row(row, acc, v, vals)); continue
            S, how, parts = stated(vals, m)
            row['stated_parts'] = [dict(value=p.get('value'), quote=p.get('quote'), file=p.get('member'), container=p.get('container'), field=p.get('field'), note=p.get('note'),
                                        category_sum=p.get('category_sum'), service=p.get('service')) for p in parts]
            row['stated_how'] = how
            items = ival(vals, 'notice_items') if v['kind'] == 'main' else None
            if key is None:
                d = dict(D_app=0, D_cre=0, eea_only=0, D_lo=0, D_hi=0, partial_app=0, scope='all'); dplan = d
                row['db_note'] = 'No platform name containing "wiki" exists in the database in any month of the window.'
            else:
                d = delivered(acc, key, per, m, v['scope'], v['sf'], final=True, items=items)
                dplan = delivered(acc, key, per, m, 'all', v['sf'], final=False) if main else None
            row['delivered'] = d
            if m in ('notice', 'notice_tf') and v['kind'] == 'main': row['items_notified'] = ival(vals, 'notice_items' if m == 'notice' else 'notice_tf_items')
            if S is None:
                row.update(stated=None, outcome=K.CANNOT_TELL, reason_code=K.NO_INTERVAL_FORMABLE, reason='No stated figure: %s.' % how); out_rows.append(row); continue
            O = ival(vals, 'orders_items') or 0 if v['kind'] != 'ads' else 0
            M5 = ival(vals, 'spam_5') or 0; M6 = ival(vals, 'spam_6') or 0
            sub = {'total': O + M5 + M6, 'solely': O + M5 + M6, 'not': O + M5 + M6, 'own': M5 + M6, 'own_auto': M5 + M6, 'own_illegal': M5, 'own_tc': M6}.get(m, 0)
            S_lo_plan = max(0, S - sub)
            # plan rule outcome (PLAN.md bands with Addenda 1 to 3 only), kept as outcome_rule
            if main:
                oc_plan, _, _, _, _ = classify_floor(S, S_lo_plan, S, dplan['D_lo'], dplan['D_hi'], dplan['D_app'], floor=False)
            S_lo, S_hi = S_lo_plan, S; rules = []
            if v['kind'] == 'main' and v['scope'] == 'nonads': rules.append('6.1')
            if main and m in ('own', 'own_illegal', 'own_tc') and d['D_hi'] > dplan['D_hi'] and v['scope'] == 'all': rules.append('6.6')
            # Addendum 5 and 6.4: restriction-column bound for own initiative
            note_mode = next((cs['mode'] for cs in COLSUM_NOTE if cs['platform'] == svc and per in cs['periods'] and v['kind'] == 'main'), None)
            if m in ('own', 'own_tc'):
                sheets = ['6'] if m == 'own_tc' else ['5', '6']; lo_sum = 0; hi_sum = 0; fired = []; ok = True
                for sh in sheets:
                    if sh == '5' and v['kind'] == 'ads': ok = False; break
                    q, lo_e, csum, mode = colsum_info(vals, sh, note_mode if sh == '6' else None)
                    if lo_e is None: ok = False; break
                    lo_sum += lo_e; hi_sum += (csum if (mode == 'outside' and csum is not None) else (ival(vals, {'5': 'own_illegal', '6': 'own_tc'}[sh]) or 0))
                    if q: fired.append((sh, mode))
                if ok and fired:
                    S_lo = max(0, lo_sum - sub); S_hi = min(S, hi_sum) if any(md == 'outside' for _, md in fired) else S
                    qn = [note_sentence(pr['notes'], '6', cs['contains'])[0] for cs in COLSUM_NOTE if cs['platform'] == svc and per in cs['periods']] if v['kind'] == 'main' else []
                    row['addendum5'] = dict(sheets=fired, largest_column_total=lo_sum, mode=','.join(md for _, md in fired), quote=(qn[0] if qn and qn[0] else None)); rules.append('6.4')
                    if qn and qn[0]: row.setdefault('platform_notes', []).append(dict(quote=qn[0], sheet='6', direction='column sum'))
            # Addendum 6.5: sheet 8 built from the sheet 5 and 6 TOTALs inherits their lower edge
            if m in ('total', 'solely', 'not') and v['kind'] in ('main', 'combined', 'ads'):
                inh = sheet8_inheritance(vals, note_mode if v['kind'] == 'main' else None, v['kind'])
                if inh:
                    R = S_total_of(vals) - max(0, min(S_total_of(vals) - O - M5 - M6, inh['lo_total'] - O - M5 - M6))
                    if m == 'total': S_lo = max(0, S - R)
                    else: S_lo = max(0, S - R)
                    row['addendum6_5'] = dict(inh, removed=R); rules.append('6.5')
            # Addendum 6.2(a): notified items as the upper edge of the stated band
            if m in ('notice', 'notice_tf') and v['kind'] == 'main':
                it = ival(vals, 'notice_items' if m == 'notice' else 'notice_tf_items')
                if it is not None and it > S: S_hi = it
                row['items_notified'] = it
            oc, r, rlo, rhi, floored = classify_floor(S, S_lo, S_hi, d['D_lo'], d['D_hi'], d['D_app'], floor=True); row['reason_code'] = RC['last']
            if v['kind'] in ('ads', 'combined') and ('6.4' in rules or '6.5' in rules):   # second referee pass: the reading without the column-sum bound
                oc_nb = classify_floor(S, S_lo_plan, S, d['D_lo'], d['D_hi'], d['D_app'], floor=True)[0]
                if oc_nb != oc: row['outcome_without_column_bound'] = oc_nb
            row.update(stated=S, stated_lo=S_lo, stated_hi=S_hi, orders_items=O, spam_measures={'own_illegal': M5, 'own_tc': M6}.get(m, M5 + M6 if m in ('total', 'solely', 'not', 'own', 'own_auto') else 0),
                       ratio=fr(r), ratio_lo=fr(rlo), ratio_hi=fr(rhi), gap_signed=d['D_app'] - S, outcome=oc, reason=reason_text(oc, rlo, rhi, S, floored), floored=floored,
                       interval='Ratio band from the date basis (decision date against submission date), statements naming only Iceland, Liechtenstein or Norway, %s, the allowances for missing database days, and measures the law does not require in the database (%s).' % (
                           {'solely': 'the partially automated category', 'not': 'the partially automated category', 'own': 'statements filed as other type of notification and notice-labelled statements beyond the items notified',
                            'own_illegal': 'other type of notification, own initiative on the other ground and notice-labelled statements beyond the items notified',
                            'own_tc': 'other type of notification, own initiative on the other ground and notice-labelled statements beyond the items notified', 'notice': 'every statement the platform filed as the upper edge and zero as the lower edge',
                            'notice_tf': 'every statement the platform filed as the upper edge and zero as the lower edge', 'own_auto': 'the two automation fields'}.get(m, 'no category added'),
                           {'total': 'items in orders and spam rows', 'solely': 'items in orders and spam rows', 'not': 'items in orders and spam rows', 'notice': 'none, and the notified items as the stated upper edge',
                            'notice_tf': 'none, and the notified items as the stated upper edge'}.get(m, 'spam rows' if m.startswith('own') else 'none')))
            if floored: rules.append('6.8')
            row['rules_after_data'] = rules
            if main: row['outcome_plan_rule'] = oc_plan
            if m in ('notice', 'notice_tf') and v['kind'] == 'main':
                row['reason'] = ('Defined after the data (Addendum 6.2). The two filings label notice sources differently, so the database band runs from zero to every statement the platform filed, and the report’s notified items set the stated upper edge. ' + row['reason'])
            if m == 'total':
                ds = delivered(acc, key, per, 'solely', v['scope'], v['sf']) if key else None; dn = delivered(acc, key, per, 'not', v['scope'], v['sf']) if key else None
                row['items'] = dict(solely_gap=(ds['D_app'] if ds else 0) - ival(vals, 'solely'), not_gap=(dn['D_app'] if dn else 0) - ival(vals, 'not'), partial_no_report_field=d['partial_app'])
            if months_bad:
                row['outcome_before_gate'] = row['outcome']; row['outcome'] = K.CANNOT_TELL; row['reason_code'] = K.NO_INTERVAL_FORMABLE; row['reason'] = 'Database months missing: %s.' % ', '.join(months_bad)
            out_rows.append(row)

    # Addendum 4 and 6.3: platform notes
    for r in out_rows:
        for ph in POSTHOC:
            if r['platform'] != ph['platform'] or r['period'] not in ph['periods'] or r['measure'] not in ph['measures']: continue
            pr = parsed.get((r['platform'], r['period']))
            q, fk = note_sentence(pr['notes'], ph['sheet'], ph['contains']) if pr else (None, None)
            if not q: r.setdefault('posthoc_problems', []).append('note not found: %s' % ph['contains']); continue
            r.setdefault('platform_notes', []).append(dict(quote=q, field=fk, sheet=ph['sheet'], direction=ph['direction']))
            hit = r['outcome'] in {'inflated': (K.BELOW, K.CONSISTENT), 'deflated': (K.ABOVE, K.CONSISTENT), 'both': (K.ABOVE, K.BELOW, K.CONSISTENT)}[ph['direction']]
            if hit:
                was = r['outcome']; r['outcome'] = K.CANNOT_TELL; r['reason_code'] = K.NO_INTERVAL_FORMABLE; r['note_rule'] = ph.get('addendum', '4')
                more = {'inflated': 'higher', 'deflated': 'lower', 'both': 'higher or lower'}[ph['direction']]
                r['reason'] = ('Defined after the data (Addendum %s). The report’s own note says: “%s” The stated figure can be %s than the database count for that reason alone, by an amount the report does not give. Without this note the row reads %s.'
                               % (ph.get('addendum', '4'), q, more, was.replace('_', ' ').lower()))
    # Addendum 6.7: opposite readings on one split
    labels = []
    by = {(r['platform'], r['period'], r['measure']): r for r in out_rows}
    for (p, per, m), r in list(by.items()):
        for a_, b_, split in (('solely', 'not', 'automation'), ('own_illegal', 'own_tc', 'ground')):
            if m != a_: continue
            rb = by.get((p, per, b_))
            if not rb: continue
            if {r['outcome'], rb['outcome']} == {K.ABOVE, K.BELOW}:
                mem = []
                for x in (r, rb):
                    mem.append(dict(measure=x['measure'], measure_label=x['measure_label'], stated=x.get('stated'), D_app=x['delivered']['D_app'], ratio=x.get('ratio'), ratio_lo=x.get('ratio_lo'), ratio_hi=x.get('ratio_hi'), reading_before=x['outcome']))
                    x['label_split'] = split; was = x['outcome']; x['outcome'] = K.CANNOT_TELL; x['reason_code'] = K.NO_INTERVAL_FORMABLE
                    x['reason'] = 'Defined after the data (Addendum 6.7). The two filings label this split differently: the other half of the same split reads the opposite way. Without this rule the row reads %s.' % was.replace('_', ' ').lower()
                labels.append(dict(platform=p, period=per, period_label=PLABEL[per], measure='label_split', measure_label='Split labelled differently in the two filings', split=split, members=mem,
                                   reading='LABELLED_DIFFERENTLY', reading_text='labelled differently in the two filings', outcome=None, defined_after_data='Addendum 6.7',
                                   reason='One half of the %s split reads above and the other below, so the two filings put the same decisions on different sides of the split.' % ('automation' if split == 'automation' else 'ground')))
    # outcome_rule: the plan rule's outcome, where the final outcome differs (main rows); new rows carry their addendum label
    for r in out_rows:
        if 'outcome_plan_rule' in r and r['outcome_plan_rule'] != r['outcome']:
            r['outcome_rule'] = r['outcome_plan_rule']
            rs = [x for x in r.get('rules_after_data', []) if x in RULE_TEXT and x != '6.8']
            if rs and not (r.get('reason') or '').startswith('Defined after the data'):
                r['reason'] = 'Defined after the data (Addendum %s). %s Under the plan’s rule this row reads %s. ' % (', '.join(rs), ' '.join(RULE_TEXT[x] for x in rs), r['outcome_rule'].replace('_', ' ').lower()) + r['reason']
        elif r.get('outcome_without_column_bound') and r['outcome_without_column_bound'] != r['outcome']:
            rs = [x for x in r.get('rules_after_data', []) if x in ('6.4', '6.5')]
            r['reason'] = 'Defined after the data (Addendum %s). %s The column-sum bound alone makes this row cannot tell. Without it the row reads %s. ' % (', '.join(rs), ' '.join(RULE_TEXT[x] for x in rs), r['outcome_without_column_bound'].replace('_', ' ').lower()) + r['reason']
    gate_ok = all(KG.values()); plan_gate_ok = all(KG_plan.values())
    for r in out_rows:
        r['outcome_plan_as_committed'] = r['outcome'] if plan_gate_ok else K.CANNOT_TELL; r['reason_code_plan_as_committed'] = r.get('reason_code') if plan_gate_ok else K.NO_INTERVAL_FORMABLE
        if not plan_gate_ok: r['plan_as_committed_reason'] = 'Known-good %s failed under the plan as committed. Addendum 1 replaces KG2 and handles KG4.' % ' and '.join(k for k, v in KG_plan.items() if not v)
    if not gate_ok:
        out_rows = K.apply_gate(False, out_rows)
        for r in out_rows: r['reason_code'] = K.NO_INTERVAL_FORMABLE
    all_rows = out_rows + labels

    # second reading A: automation fields per platform per created_at month and per period (ads split for the three services)
    inv = {v: k for k, v in dsa_db.NAMES.items()}
    mon = C.defaultdict(C.Counter); autoper = C.defaultdict(C.Counter)
    for (p, cre, app, ad, det, src, gr, eea, isad, nn) in dbrows:
        name = inv.get(p, p)
        if name in ADS_SERVICES and isad: name = name + ' (ads)'
        keys = [(name, 'm', cre[:7])] + [(name, 'p', per) for per, (a_, b_) in PERIODS.items() if a_ <= cre <= b_]
        for k in keys:
            c = (mon if k[1] == 'm' else autoper)[(k[0], k[2])]; c['n'] += nn
            if ad == FU: c['fully'] += nn
            if ad == PA: c['partially'] += nn
            if ad == NA: c['not'] += nn
            if det == 'Yes': c['detection_yes'] += nn
            if ad == FU and det == 'No': c['fully_no_detection'] += nn
            if ad == NA and det == 'Yes': c['not_with_detection'] += nn
    KS = ('fully', 'partially', 'not', 'detection_yes', 'fully_no_detection', 'not_with_detection')
    auto = [dict(platform=nm, scope=('ads only' if nm.endswith('(ads)') else ('excluding ads' if nm in ADS_SERVICES else 'all statements')), month=mth,
                 partial_month=(newest is not None and mth == newest[:7] and newest[8:] < '28'), statements=c['n'], **{k: round(c[k] / c['n'], 4) for k in KS}) for (nm, mth), c in sorted(mon.items())]
    auto_period = [dict(platform=nm, scope=('ads only' if nm.endswith('(ads)') else ('excluding ads' if nm in ADS_SERVICES else 'all statements')), period=per, period_label=PLABEL[per], statements=c['n'],
                        counts={k: c[k] for k in KS}, **{k: round(c[k] / c['n'], 4) for k in KS}) for (nm, per), c in sorted(autoper.items()) if c['n']]

    comp = [r for r in out_rows]
    orig = [r for r in comp if r.get('view') == 'main']
    summ = dict(updated_utc=(json.load(open(os.path.join(H, 'summary_dsa.json')))['updated_utc'] if '--std2-rewrite' in sys.argv else time.strftime('%Y-%m-%d %H:%M', time.gmtime())), plan_commit=os.popen('cd "%s" && git log -1 --format=%%H -- PLAN.md 2>/dev/null' % H).read().strip(),
                rows=len(all_rows), comparison_rows=len(comp), label_split_rows=len(labels),
                outcomes_original_rows=dict(C.Counter(r['outcome'] for r in orig)), outcomes_ads_rows=dict(C.Counter(r['outcome'] for r in comp if r.get('view') == 'ads')),
                outcomes_combined_rows=dict(C.Counter(r['outcome'] for r in comp if r.get('view') == 'combined')), outcomes=dict(C.Counter(r['outcome'] for r in comp)),
                cannot_tell_by_reason=dict(C.Counter(r.get('reason_code') for r in comp if r['outcome'] == K.CANNOT_TELL)), req13=K.req13([(r['outcome'], r.get('reason_code')) for r in comp], nothing_returned=0),
                outcomes_plan_rule_original_rows=dict(C.Counter(r.get('outcome_plan_rule', r['outcome']) for r in orig)),
                known_good=KG, gate_passed=gate_ok, known_good_plan_as_committed=KG_plan, plan_gate_passed=plan_gate_ok, newest_created_day=newest,
                platforms_with_template_report=sorted({k[0] for k in parsed}), periods_read=sorted({k for k in parsed}, key=str), shortfall_addendum3=sfs,
                KG_detail=dict(KG1=st['KG1'], KG1all={k: v for k, v in st.get('KG1all', {}).items() if k != 'failures'} | dict(failures=st.get('KG1all', {}).get('failures', [])[:20]),
                               KG2=dict(passed=st['KG2']['passed'], rows=st['KG2']['rows'], failures=st['KG2']['failures'][:50]), KG4=st['KG4']))
    json.dump(all_rows, open(os.path.join(H, 'data', 'dsa.json'), 'w'), indent=1, default=str)
    json.dump(auto, open(os.path.join(H, 'data', 'automation_monthly.json'), 'w'), indent=1)
    json.dump(auto_period, open(os.path.join(H, 'data', 'automation_period.json'), 'w'), indent=1)
    json.dump(sources, open(os.path.join(H, 'data', 'sources.json'), 'w'), indent=1)
    json.dump({'%s %s' % k: v['notes'] for k, v in parsed.items()}, open(os.path.join(H, 'data', 'context_notes.json'), 'w'), indent=1)
    json.dump(summ, open(os.path.join(H, 'summary_dsa.json'), 'w'), indent=1, default=str)
    write_public(all_rows, auto, summ, sources)
    import dsa_html
    open(os.path.join(H, 'section_dsa.html'), 'w').write(dsa_html.render(all_rows, auto_period, sources, summ))
    print('dsa: %d comparison rows (%d original), %d label-split rows; original outcomes %s; known-good %s' % (len(comp), len(orig), len(labels), dict(C.Counter(r['outcome'] for r in orig)), KG))

def S_total_of(vals):
    a, b = ival(vals, 'solely'), ival(vals, 'not')
    return (a or 0) + (b or 0)

def sheet8_inheritance(vals, note_mode, kind):
    """Addendum 6.5: sheet 8 total equal (within 0.1%) to sheet 5 and 6 TOTALs [+ notice actions] [+ order items], with at least one TOTAL a column sum."""
    T8 = S_total_of(vals)
    if not T8 or ival(vals, 'solely') is None or ival(vals, 'not') is None: return None
    t5 = ival(vals, 'own_illegal'); t6 = ival(vals, 'own_tc')
    if t6 is None: return None
    t5 = t5 or 0
    q5, lo5, _, _ = colsum_info(vals, '5', None) if ival(vals, 'own_illegal') is not None and kind != 'ads' else (False, 0, None, None)
    q6, lo6, _, _ = colsum_info(vals, '6', note_mode)
    if not (q5 or q6): return None
    Nn = (ival(vals, 'notice_law') or 0) + (ival(vals, 'notice_tc') or 0); O = ival(vals, 'orders_items') or 0
    for label, cand, extra in (('sheets 5 and 6', t5 + t6, 0), ('sheets 5 and 6 plus notice actions', t5 + t6 + Nn, Nn), ('sheets 5 and 6 plus notice actions and order items', t5 + t6 + Nn + O, Nn + O)):
        if cand and abs(T8 - cand) / T8 <= 0.001:
            return dict(identity=label, sheet8_total=T8, built_from=cand, relative_difference=round((T8 - cand) / T8, 7), lo_total=(lo5 or 0) + (lo6 or 0) + extra,
                        sheet5_column_sum=bool(q5), sheet6_column_sum=bool(q6))
    return None

def share_row(row, acc, v, vals):
    row = dict(row); row['measure'] = 'share'; row['measure_label'] = MLABEL['share']; row['filter'] = FILTER['share']
    a, b = vals.get('solely'), vals.get('not')
    if not a or not b or ival(vals, 'solely') is None or ival(vals, 'not') is None or (ival(vals, 'solely') + ival(vals, 'not')) == 0:
        row.update(outcome=K.CANNOT_TELL, reason_code=K.NO_INTERVAL_FORMABLE, reason='No stated share: the report leaves solely or not automated blank.'); return row
    so, no = ival(vals, 'solely'), ival(vals, 'not'); T = so + no; s = so / T
    O = (ival(vals, 'orders_items') or 0) if v['kind'] != 'ads' else 0
    E = O + (ival(vals, 'spam_5') or 0) + (ival(vals, 'spam_6') or 0)
    note_mode = next((cs['mode'] for cs in COLSUM_NOTE if cs['platform'] == v['svc'] and v['per'] in cs['periods'] and v['kind'] == 'main'), None)
    inh = sheet8_inheritance(vals, note_mode, v['kind']); E_nb = E
    if inh:
        E = max(E, T - max(0, min(T - E, inh['lo_total'] - E))); row['addendum6_5'] = inh; row['rules_after_data'] = ['6.5']
    cand = [s]
    if 0 < E < T: cand += [(so - min(E, so)) / (T - E), (so - max(0, E - no)) / (T - E)]
    s_lo, s_hi = min(cand), max(cand)
    ca, cc = acc.get((v['key'], v['per'], 'app', v['scope']), C.Counter()), acc.get((v['key'], v['per'], 'cre', v['scope']), C.Counter())
    ta, tc = cnt(ca, 'all'), cnt(cc, 'all')
    if ta == 0 or tc == 0:
        row.update(stated_share=s, outcome=K.CANNOT_TELL, reason_code=K.NO_INTERVAL_FORMABLE, reason='The database holds no statements for this platform and period on one date basis.'); return row
    d_c = cnt(ca, 'FU') / ta; d_lo = min(cnt(ca, 'FU') / ta, cnt(cc, 'FU') / tc); d_hi = max(cnt(ca, 'FUPA') / ta, cnt(cc, 'FUPA') / tc)
    lo, hi = d_lo - s_hi, d_hi - s_lo; oc, rcs = K.read(lo, hi, band=(-SH_B, SH_B)); row['reason_code'] = rcs
    if inh and v['kind'] in ('ads', 'combined'):   # second referee pass: the reading without the column-sum bound
        cn = [s] + ([(so - min(E_nb, so)) / (T - E_nb), (so - max(0, E_nb - no)) / (T - E_nb)] if 0 < E_nb < T else [])
        oc_nb = K.read(d_lo - max(cn), d_hi - min(cn), band=(-SH_B, SH_B))[0]
        if oc_nb != oc: row['outcome_without_column_bound'] = oc_nb
    if v['kind'] == 'main':   # plan rule share (all statements, orders and spam only)
        cap, ccp = acc.get((v['key'], v['per'], 'app', 'all'), C.Counter()), acc.get((v['key'], v['per'], 'cre', 'all'), C.Counter())
        E0 = O + (ival(vals, 'spam_5') or 0) + (ival(vals, 'spam_6') or 0); c0 = [s] + ([(so - min(E0, so)) / (T - E0), (so - max(0, E0 - no)) / (T - E0)] if 0 < E0 < T else [])
        tap, tcp = cnt(cap, 'all'), cnt(ccp, 'all')
        if tap and tcp:
            l0 = min(cnt(cap, 'FU') / tap, cnt(ccp, 'FU') / tcp) - max(c0); h0 = max(cnt(cap, 'FUPA') / tap, cnt(ccp, 'FUPA') / tcp) - min(c0)
            row['outcome_plan_rule'] = K.read(l0, h0, band=(-SH_B, SH_B))[0]
    txt = 'The difference band runs from %+.1f to %+.1f points.' % (lo * 100, hi * 100)
    txt += {K.CONSISTENT: ' It lies inside 5 points either way, so the shares agree.', K.ABOVE: ' Its lower edge is above +5 points. The filings show a larger fully automated share than the report states.',
            K.BELOW: ' Its upper edge is below -5 points. The filings show a smaller automated share than the report states, even counting partially automated statements.', K.CANNOT_TELL: ' It crosses a 5 point edge, so we cannot tell.'}[oc]
    row.update(stated_share=round(s, 4), stated_share_lo=round(s_lo, 4), stated_share_hi=round(s_hi, 4), delivered_share=round(d_c, 4), delivered_share_lo=round(d_lo, 4), delivered_share_hi=round(d_hi, 4),
               diff_points=round((d_c - s) * 100, 1), diff_lo_points=round(lo * 100, 1), diff_hi_points=round(hi * 100, 1), outcome=oc, reason=txt,
               stated_parts=[dict(value=x.get('value'), quote=x.get('quote'), file=x.get('member'), container=x.get('container'), field=x.get('field')) for x in (a, b) if 'components' not in x] +
                            [dict(value=c.get('value'), quote=c.get('quote'), file=c.get('member'), container=c.get('container'), field=c.get('field'), service=c.get('service')) for x in (a, b) for c in x.get('components', [])],
               interval='Points band from the date basis, the partially automated category, and orders and spam rows the database does not require.')
    return row

def write_public(rows, auto, summ, sources):
    """Trimmed public files: one row per reading, the stated value cell and indicator instead of the whole verbatim record."""
    pd_ = os.path.join(H, 'public'); os.makedirs(pd_, exist_ok=True)
    keep = ('platform', 'view', 'period', 'measure', 'stated', 'stated_lo', 'stated_hi', 'items_notified', 'ratio', 'ratio_lo', 'ratio_hi', 'gap_signed',
            'outcome', 'reason_code', 'status', 'outcome_rule', 'outcome_without_column_bound', 'defined_after_data', 'rules_after_data', 'reason', 'stated_share', 'stated_share_lo', 'stated_share_hi',
            'delivered_share', 'delivered_share_lo', 'delivered_share_hi', 'diff_points', 'diff_lo_points', 'diff_hi_points', 'split', 'reading_text', 'members')
    out = []; srcmap = {}
    for r in rows:
        x = {k: r[k] for k in keep if r.get(k) not in (None, [], '')}
        if x.get('reason'): x['reason'] = x['reason'].replace(BELOW_UNSIZED, '[unsized differences, below: see legend]').replace(ABOVE_UNSIZED, '[unsized differences, above: see legend]')
        if r.get('source_url'): srcmap['%s|%s' % (r['platform'].replace(' (ads)', ''), r['period'])] = dict(url=r['source_url'], published=r.get('published'))
        if r.get('delivered'): x['database'] = {k: r['delivered'].get(k) for k in ('D_app', 'D_cre', 'D_lo', 'D_hi') if k in r['delivered']}
        if r.get('stated_parts'):
            x['stated_from'] = [dict(file=p.get('file'), field=p.get('field'), value=p.get('value'), service=p.get('service')) for p in r['stated_parts']]
        if r.get('platform_notes'): x['platform_notes'] = [dict(quote=n['quote'][:600]) for n in r['platform_notes']]
        out.append(x)
    legend = dict(measures={k: dict(label=MLABEL[k], database_filter=FILTER[k]) for k in MLABEL}, scopes=SCOPE_TEXT, rules_after_data=RULE_TEXT,
                  unsized_below=BELOW_UNSIZED, unsized_above=ABOVE_UNSIZED, outcome_plan_as_committed='CANNOT_TELL on every row: known-good checks KG2 and KG4 failed under the plan as committed (PLAN.md, Addendum 1).',
                  band='Ratio band from the date basis (decision date against submission date), statements naming only Iceland, Liechtenstein or Norway, the categories added to the upper edge for each measure, the allowances for missing database days, and measures the law does not require in the database (items in orders and spam rows).',
                  agreement='CONSISTENT: band inside 0.90 to 1.10. ABOVE or BELOW: band beyond 1.10 or below 0.90 by at least 100 statements. Shares: 5 points either way.')
    json.dump(dict(note='SOCIAL, two filings, one platform. Heuremen LLC. Database: EU DSA Transparency Database monthly aggregates, European Commission, CC BY 4.0. Reports: each platform’s DSA transparency report.',
                   legend=legend, sources=srcmap, rows=out), open(os.path.join(pd_, 'dsa.json'), 'w'), indent=0, separators=(',', ':'))
    json.dump({k: summ[k] for k in ('updated_utc', 'comparison_rows', 'label_split_rows', 'outcomes_original_rows', 'outcomes_ads_rows', 'outcomes_combined_rows', 'known_good', 'known_good_plan_as_committed', 'newest_created_day')}, open(os.path.join(pd_, 'dsa_summary.json'), 'w'), indent=1)
    json.dump(auto, open(os.path.join(pd_, 'dsa_automation_monthly.json'), 'w'), indent=1)

if __name__ == '__main__':
    main(refresh='--no-refresh' not in sys.argv)
