# Referee loader: parses the raw ADSPEND inputs independently of adspend_tick.py and pickles them.
# Reads only committee-level FEC files (cm, webk, weball, oppexp, independent expenditures) and the Google bundle.
# The cm treasurer field (index 2) is never read. Individual contributor files are never opened.
# Payee names are kept only for rows a broad Google-ish net catches. A row coded to an individual (entity IND) keeps its name
# only when the plan's Google rule matches it (Google entities typed into name fields), so no personal name is stored.
import os, io, re, csv, sys, zipfile, pickle, datetime as D, collections as C

RAW = '/Users/heuremen/bones-forge/social_index/adspend/data/raw'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'raw_cache.pkl')
CYC = (2020, 2022, 2024, 2026)

def pipe_lines(path):
    z = zipfile.ZipFile(path)
    with z.open(z.namelist()[0]) as fh:
        for line in io.TextIOWrapper(fh, encoding='latin-1', newline=''):
            yield line.rstrip('\r\n').split('|')

def mdy(s):
    m = re.fullmatch(r'(\d\d)/(\d\d)/(\d{4})', s or '')
    if not m: return None
    try: return D.date(int(m.group(3)), int(m.group(1)), int(m.group(2))).toordinal()
    except ValueError: return None

MONS = 'JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split()
def ie_date(s):
    s = (s or '').strip().upper()
    m = re.fullmatch(r'(\d{1,2})-([A-Z]{3})-(\d\d)', s)
    if m and m.group(2) in MONS:
        try: return D.date(2000 + int(m.group(3)), MONS.index(m.group(2)) + 1, int(m.group(1))).toordinal()
        except ValueError: return None
    return mdy(s)

def num(s):
    try: return float(s)
    except (TypeError, ValueError): return 0.0

def norm(s):
    s = (s or '').upper().replace('&', ' AND ')
    return ' '.join(re.sub(r'[^A-Z0-9]', ' ', s).split())

# broad net for anything that could be a Google entity, wider than the builder's payee rule, for the payee audit
PLAN_G = re.compile(r'GOOGLE|YOUTUBE|YOU ?TUBE|ADWORDS|DOUBLECLICK|ALPHABET INC|\bG ?-?SUITE\b|\bGSUITE\b')
BROAD = re.compile(r'GOOG|GOGL|GOOLG|GOGOLE|GOGGLE|GOOGEL|GOOOG|GOOGL|YOUTU|YOU TUBE|ALPHABET|DOUBLE ?CLICK|ADWORD|ADWRD|G ?-?SUITE|GSUITE|ADSENSE|ADMOB|FIREBASE|\bWAZE\b|FITBIT|DV ?360|DISPLAY ?& ?VIDEO|SEARCH ADS 360|CHROMEBOOK|GMAIL|GOODLE|GOOFLE|GOOGE\b|GOOLE\b|GOGLE\b|\bGOOG\b')

def ref_match(gstats, cm):
    """Referee's own reading of the plan's matching rule plus Addendum 2."""
    us = [g for g in gstats if g['regions'].strip() == 'US']
    principal = C.defaultdict(set); names = C.defaultdict(set)
    for cid, recs in cm.items():
        for c, r in recs.items():
            names[norm(r['name'])].add(cid)
            if r['dsgn'] == 'P' and r['cand']: principal[r['cand']].add(cid)
    adv = {}; why = {}
    for g in us:
        items = [s.strip() for s in (g['ids'] or '').split(',') if s.strip()]
        fec = [s[len('FEC ID'):].strip().upper() for s in items if s.upper().startswith('FEC ID')]
        if fec:
            cids = []; ok = True; has_c = any(re.fullmatch(r'C\d{8}', t) for t in fec)
            for t in fec:
                if re.fullmatch(r'C\d{8}', t) and t in cm: cids.append(t)
                elif re.fullmatch(r'[HSP][0-9A-Z]{8}', t) and principal.get(t): cids += sorted(principal[t])
                else: ok = False
            if ok and cids: adv[g['id']] = ('id' if has_c else 'candidate id', list(dict.fromkeys(cids)))
            else: why[g['id']] = 'fec id not in cm'
            continue
        if any(s.startswith('Registered in') for s in items): why[g['id']] = 'state registration'; continue
        hit = names.get(norm(g['name']), set())
        if len(hit) == 1: adv[g['id']] = ('name', list(hit))
        elif len(hit) > 1: why[g['id']] = 'ambiguous name'
        else: why[g['id']] = 'no id no name'
    return us, adv, why, principal, names

def main():
    cache = {}
    cm = {}
    for c in CYC:
        for f in pipe_lines(f'{RAW}/fec/{c}/cm{str(c)[2:]}.zip'):
            if len(f) < 15: continue
            cm.setdefault(f[0], {})[c] = dict(name=f[1].strip(), state=f[6], dsgn=f[8], tp=f[9], party=f[10], org=f[13].strip(), cand=f[14].strip())
    cache['cm'] = cm
    wk, wa = {}, {}
    for c in CYC:
        wk[c] = {}; wa[c] = {}
        for f in pipe_lines(f'{RAW}/fec/{c}/webk{str(c)[2:]}.zip'):
            if len(f) != 27: continue
            wk[c][f[0]] = dict(name=f[1], tp=f[2], dsgn=f[3], ttl_disb=num(f[12]), tr_aff=num(f[13]), ref_ind=num(f[14]), ref_cmte=num(f[15]),
                               loan_rep=num(f[17]), contrib_other=num(f[22]), ie=num(f[23]), coord=num(f[24]), nonfed_share=num(f[25]), cvg=mdy(f[26]))
        for f in pipe_lines(f'{RAW}/fec/{c}/weball{str(c)[2:]}.zip'):
            if len(f) != 30: continue
            wa[c][f[0]] = dict(ttl_disb=num(f[7]), tr_auth=num(f[8]), cand_loan_rep=num(f[14]), oth_loan_rep=num(f[15]), ref_ind=num(f[28]), ref_cmte=num(f[29]),
                               party=f[4], cvg=mdy(f[27]))
    cache['wk'] = wk; cache['wa'] = wa
    x = f'{RAW}/google/x/'
    st = list(csv.DictReader(open(x + 'google-political-ads-advertiser-stats.csv', newline='', encoding='utf-8')))
    weekly = C.defaultdict(list)
    for r in csv.DictReader(open(x + 'google-political-ads-advertiser-weekly-spend.csv', newline='', encoding='utf-8')):
        y, m, d = map(int, r['Week_Start_Date'].split('-'))
        weekly[r['Advertiser_ID']].append((D.date(y, m, d).toordinal(), float(r['Spend_USD'] or 0)))
    for k in weekly: weekly[k].sort()
    gstats = [dict(id=r['Advertiser_ID'], name=r['Advertiser_Name'], ids=r['Public_IDs_List'], regions=r['Regions'], total=float(r['Spend_USD'] or 0)) for r in st]
    cache['gstats'] = gstats; cache['weekly'] = dict(weekly)
    us, adv, why, principal, names = ref_match(gstats, cm)
    keep = {c for _, cids in adv.values() for c in cids}
    cache['keep'] = keep
    hdr = open(f'{RAW}/fec/dict/oppexp_header_file.csv').read().strip().split(',')
    I = {k: i for i, k in enumerate(hdr)}
    rows = C.defaultdict(list); months = C.Counter(); nlines = 0; bad = C.Counter(); broad = []; itm = C.Counter(); anyrow = set()
    intern = sys.intern
    for c in CYC:
        for f in pipe_lines(f'{RAW}/fec/{c}/oppexp{str(c)[2:]}.zip'):
            nlines += 1
            if len(f) != 26: bad['fields'] += 1; continue
            o = mdy(f[I['TRANSACTION_DT']])
            if o is None: bad['date'] += 1; continue
            dt = D.date.fromordinal(o); months[(dt.year, dt.month)] += 1
            cid = f[I['CMTE_ID']]; nm = f[I['NAME']].upper(); isb = bool(BROAD.search(nm))
            nmc = ' '.join(nm.split())
            if isb and f[I['ENTITY_TP']] == 'IND' and not PLAN_G.search(nmc): nmc = '<IND>'
            if isb:
                broad.append((cid, c, o, num(f[I['TRANSACTION_AMT']]), intern(nmc), intern(' '.join(f[I['PURPOSE']].upper().split())), f[I['MEMO_CD']].strip(), f[I['ENTITY_TP']]))
            if cid not in keep: continue
            anyrow.add((cid, c))
            amt = num(f[I['TRANSACTION_AMT']]); memo = f[I['MEMO_CD']].strip()
            if not memo: itm[(cid, c)] += amt
            ent = f[I['ENTITY_TP']]
            rows[cid].append((c, o, amt, intern(nmc) if isb else '', intern(' '.join(f[I['PURPOSE']].upper().split())), memo, intern(ent),
                              f[I['RPT_YR']], intern(f[I['RPT_TP']]), f[I['TRAN_ID']], f[I['FILE_NUM']], f[I['BACK_REF_TRAN_ID']], intern(f[I['LINE_NUM']]), intern(f[I['FORM_TP_CD']]),
                              intern(f[I['AMNDT_IND']]), f[I['SUB_ID']], f[I['IMAGE_NUM']]))
    cache['opp'] = dict(rows); cache['months'] = months; cache['opp_lines'] = nlines; cache['opp_bad'] = bad; cache['broad'] = broad
    cache['itm_raw'] = dict(itm); cache['anyrow'] = anyrow
    ie = C.defaultdict(list); ie_total = 0
    for c in CYC:
        for r in csv.DictReader(open(f'{RAW}/fec/{c}/independent_expenditure_{c}.csv', newline='', encoding='latin-1')):
            ie_total += 1
            ie[(r.get('spe_id') or '').strip()].append(dict(c=c, exp=ie_date(r.get('exp_date')), dis=ie_date(r.get('dissem_dt')), amt=num(r.get('exp_amo')), pay=r.get('pay') or '',
                                                          pur=r.get('pur') or '', fn=r.get('file_num') or '', cand=r.get('cand_id') or '', so=r.get('sup_opp') or '', amndt=r.get('amndt_ind') or '',
                                                          tran=r.get('tran_id') or '', prev=r.get('prev_file_num') or '', yr=r.get('fec_election_yr') or ''))
    cache['ie'] = dict(ie); cache['ie_total'] = ie_total
    pickle.dump(cache, open(OUT, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    print('lines', nlines, 'bad', dict(bad), 'kept committees', len(keep), 'with rows', len(rows), 'rows kept', sum(len(v) for v in rows.values()),
          'broad google-ish rows (all committees)', len(broad), 'ie rows', ie_total)

if __name__ == '__main__': main()
