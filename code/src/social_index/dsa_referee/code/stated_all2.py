"""Referee second pass: independent stated-side read of every report, now including the Ads templates (8a, 6a), spam rows,
order items and trusted-flagger items. File choice from sources.json, values from the referee's own readers. Output: out2/stated_all2.json"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stated_all as S
DSA = '/Users/heuremen/bones-forge/social_index/dsa'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out2', 'stated_all2.json')
SVC_OK = ['snap', 'xvideos', 'xnxx', 'app store', 'appstore']

def svc_match(cell, words):
    c = S.norm(cell)
    return (not c) or any(w in c or c in w for w in words + SVC_OK)

def read8(rows, words):
    hi = S.hdr_idx(rows, 'indicator'); hdr = rows[hi]
    ii, sc, vi, si = S.col(hdr, 'indicator'), S.col(hdr, 'scope'), S.col(hdr, 'value'), S.col(hdr, 'service')
    out = {}
    for r in rows[hi + 1:]:
        if len(r) <= max(ii, sc, vi): continue
        if si is not None and not svc_match(r[si], words): continue
        if S.norm(r[sc]) not in ('total number', 'total'): continue
        ind = S.norm(r[ii])
        if ind.startswith('number of measures solely taken by automated means') and 'solely' not in out: out['solely'] = S.num(r[vi])
        if ind.startswith('number of measures not taken by automated means') and 'not' not in out: out['not'] = S.num(r[vi])
    return out

def read56(rows, words):
    hi = S.hdr_idx(rows, 'applicability'); hdr = rows[hi]
    ci = S.col(hdr, 'category'); fi = S.col(hdr, "number of measures taken at the provider's own initiative"); gi = S.col(hdr, 'number of measures taken after detection')
    di = next((j for j, h in enumerate(hdr) if S.norm(h).startswith('description of the sub-category')), None); si = S.col(hdr, 'service')
    tot = None; spam = 0; cols = {}
    for r in rows[hi + 1:]:
        if si is not None and len(r) > si and not svc_match(r[si], words): continue
        if len(r) > ci and S.norm(r[ci]) == 'total' and tot is None: tot = r
        if di is not None and len(r) > max(di, fi) and re.search(r'spam|high.?volume', r[di] or '', re.I):
            v = S.num(r[fi])
            if v is not None: spam += v
    for j, h in enumerate(hdr):
        hn = S.norm(h)
        if hn.startswith(('visibility restriction', 'monetary restriction', 'provision of the service', 'account restriction')):
            cols[h.strip()] = S.num(tot[j]) if tot is not None and j < len(tot) else None
    F = S.num(tot[fi]) if tot is not None and len(tot) > fi else None
    G = S.num(tot[gi]) if tot is not None and gi is not None and len(tot) > gi else None
    return dict(F=F, G=G, cols=cols, spam=spam)

def read4(rows, words):
    hi = S.hdr_idx(rows, 'applicability'); hdr = rows[hi]; ci = S.col(hdr, 'category'); si = S.col(hdr, 'service')
    r = None
    for x in rows[hi + 1:]:
        if len(x) > ci and S.norm(x[ci]) == 'total' and (si is None or len(x) <= si or svc_match(x[si], words)): r = x; break
    def exact(name):
        return next((j for j, h in enumerate(hdr) if S.norm(h) == name), None)
    names = dict(H='number of specific items of information included in the total number of notices',
                 I='number of specific items of information included in the total number of notices by trusted flaggers (trusted flagger notices)',
                 L='number of actions taken on the basis of the law', M='number of actions taken on the basis of the law (trusted flagger notices)',
                 N='number of actions taken on the basis of the terms and conditions of the service', O='number of actions taken on the basis of the terms and conditions of the service (trusted flagger notices)')
    out = {}
    for k, nm in names.items():
        j = exact(nm)
        if j is None: j = next((jj for jj, h in enumerate(hdr) if S.norm(h).startswith(nm)), None)
        out[k] = S.num(r[j]) if r is not None and j is not None and len(r) > j else None
    return out

def read3(rows, words):
    hi = S.hdr_idx(rows, 'applicability'); hdr = rows[hi]; ci = S.col(hdr, 'category'); sc = S.col(hdr, 'scope'); si = S.col(hdr, 'service')
    j = next((jj for jj, h in enumerate(hdr) if S.norm(h).startswith('number of specific items of information included in the total number of orders')), None)
    for x in rows[hi + 1:]:
        if j is None or len(x) <= max(ci, j): continue
        if si is not None and len(x) > si and not svc_match(x[si], words): continue
        if S.norm(x[ci]) == 'total' and (sc is None or S.norm(x[sc]) == 'total'): return S.num(x[j])
    return None

if __name__ == '__main__':
    srcs = json.load(open(os.path.join(DSA, 'data', 'sources.json')))
    out = {}
    for s in srcs:
        if s.get('status') != 'read': continue
        svc, per, sh = s['service'], s['period'], s['sheets']; words = [S.norm(svc), S.norm(svc).split()[0]]
        res = {}
        try:
            res.update(read8(S.load_sheet(s['dir'], sh['8']['container'], sh['8']['member']), words))
            for k in ('5', '6'):
                v = read56(S.load_sheet(s['dir'], sh[k]['container'], sh[k]['member']), words); res['s' + k] = v
            v4 = read4(S.load_sheet(s['dir'], sh['4']['container'], sh['4']['member']), words); res.update({'n' + k: x for k, x in v4.items()})
            res['orders'] = read3(S.load_sheet(s['dir'], sh['3']['container'], sh['3']['member']), words) if '3' in sh else None
            if '8a' in sh:
                a = read8(S.load_sheet(s['dir'], sh['8a']['container'], sh['8a']['member']), words); res['ads_solely'], res['ads_not'] = a.get('solely'), a.get('not')
            if '6a' in sh:
                res['s6a'] = read56(S.load_sheet(s['dir'], sh['6a']['container'], sh['6a']['member']), words)
        except Exception as e:
            res['error'] = '%s: %s' % (type(e).__name__, e)
        out['%s|%s' % (svc, per)] = res
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), indent=1)
    print(len(out), 'reports;', sum(1 for v in out.values() if 'error' in v), 'errors')
    for k, v in out.items():
        if 'error' in v: print('  ERR', k, v['error'])
