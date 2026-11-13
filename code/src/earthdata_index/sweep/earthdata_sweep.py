#!/usr/bin/env python3
"""Earth and station dataset sweep (Zenodo). Run: python3 -I earthdata_sweep.py [--fetch-only|--classify-only]
Resumable: every API page is cached under ../cache/. Listings and sizes only, no data files are downloaded."""
import os, sys, re, json, time, hashlib, html, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "cache")
UA = "heuremen-index/0.1 (https://indahl.ai)"
INDEXED = "2026-11-12"
CAP_TOTAL = 2000
PER_TOPIC = 250
PAGE = 25
DELAY = 1.0
TERMS = "Free to download and cite with attribution. All rights reserved. Text and data mining and use as AI training data are not permitted: https://indahl.ai/terms#ai-training"

TOPICS = {
    "earthquakes": ['earthquake catalog', 'earthquake', 'seismicity catalogue'],
    "seismic waveforms": ['seismic waveform', 'miniSEED', 'seismograms'],
    "GNSS and GPS stations": ['GNSS stations', 'GPS stations time series', 'RINEX'],
    "weather and climate stations": ['weather station data', 'climate station observations', 'meteorological station'],
    "hydrology gauges": ['streamflow gauge', 'river discharge gauge', 'hydrological station'],
    "ocean buoys": ['ocean buoy', 'moored buoy', 'wave buoy'],
    "air quality monitors": ['air quality monitoring stations', 'PM2.5 monitor', 'air pollution sensors'],
}

_last = [0.0]
def get(url, retries=6):
    for a in range(retries):
        wait = DELAY - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                ra = e.headers.get("Retry-After")
                time.sleep(min(int(ra), 120) if ra and ra.isdigit() else 10 * (a + 1))
                continue
            if e.code == 400:
                return None
            raise
        except Exception:
            time.sleep(5 * (a + 1))
    return None

def cached(key, url):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, hashlib.sha1(key.encode()).hexdigest() + ".json")
    if os.path.exists(p):
        with open(p) as f: return json.load(f)
    d = get(url)
    if d is None: return None
    with open(p + ".tmp", "w") as f: json.dump(d, f)
    os.replace(p + ".tmp", p)
    return d

def fetch():
    cands = {}  # id -> (topic, hit)
    counts = {t: 0 for t in TOPICS}
    for topic, qs in TOPICS.items():
        for q in qs:
            for page in range(1, 41):
                if counts[topic] >= PER_TOPIC or len(cands) >= CAP_TOTAL: break
                params = urllib.parse.urlencode({"q": q, "type": "dataset", "access_status": "open", "size": PAGE, "page": page, "sort": "bestmatch"})
                d = cached("zen|%s|%d" % (q, page), "https://zenodo.org/api/records?" + params)
                if not d: break
                hits = d.get("hits", {}).get("hits", [])
                if not hits: break
                for h in hits:
                    rid = str(h["id"])
                    if rid in cands or counts[topic] >= PER_TOPIC or len(cands) >= CAP_TOTAL: continue
                    cands[rid] = (topic, h); counts[topic] += 1
                print("fetch", topic, q, page, counts[topic], len(cands), flush=True)
    return cands

# ---------- classification ----------
DEFENSE = [r"\bDARPA\b", r"\bIARPA\b", r"\bDoD\b", r"\bU\.?S\.? Department of Defen[cs]e\b", r"\bDepartment of Defen[cs]e\b",
 r"\bOffice of Naval Research\b", r"\bONR\b", r"\bAFOSR\b", r"\bAir Force Office of Scientific Research\b", r"\bAFRL\b",
 r"\bAir Force Research Laborator", r"\bArmy Research (Office|Laborator)", r"\bARO\b", r"\bARL\b", r"\bNational Security Agency\b", r"\bNSA\b",
 r"\bSERDP\b", r"\bESTCP\b", r"\bArmy Corps of Engineers\b", r"\bUSACE\b", r"\bERDC\b", r"\bNaval Research Laborator", r"\bNRL\b",
 r"\bUS Navy\b", r"\bU\.S\. Navy\b", r"\bUnited States Navy\b", r"\bUS Air Force\b", r"\bU\.S\. Air Force\b", r"\bUnited States Air Force\b",
 r"\bUS Army\b", r"\bU\.S\. Army\b", r"\bUnited States Army\b", r"\bMinistry of Defen[cs]e\b", r"\bDefen[cs]e Science and Technology\b", r"\bDSTL\b",
 r"\barmasuisse\b", r"\bIsrael(i)? Defen[cs]e Forces\b", r"\bIDF\b", r"\bDefen[cs]e Advanced Research\b", r"\bIntelligence Advanced Research\b",
 r"\bDefen[cs]e Threat Reduction\b", r"\bMissile Defen[cs]e Agency\b", r"\bNaval Postgraduate\b", r"\bDefen[cs]e Innovation\b", r"\bBundeswehr\b",
 r"\bDGA\b", r"\bDRDO\b", r"\bMinistry of National Defen[cs]e\b", r"\bDepartment of the (Navy|Army|Air Force)\b"]
DEF_RE = re.compile("|".join(DEFENSE))
FUND_CTX = re.compile(r"fund|grant|support|award|sponsor|contract|financ|acknowledg", re.I)
STOP = set("the of and in to a is for with on by this are from as that at an be data was were which or has have been these it its".split())

def strip(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()

def english(md, text):
    lang = (md.get("language") or "").lower()
    if lang:
        return (lang in ("eng", "en"), "language field " + lang)
    words = re.findall(r"[a-zA-Z']+", text.lower())
    allw = re.findall(r"\w+", text.lower())
    if len(allw) < 8: return (None, "too little text to judge language")
    frac = sum(w in STOP for w in words) / max(1, len(allw))
    nonascii = sum(ord(c) > 127 for c in text) / max(1, len(text))
    if frac >= 0.12 and nonascii < 0.05: return (True, "")
    if frac < 0.05: return (False, "text is not English")
    return (None, "language unclear from text")

DATA_EXT = {"csv","tsv","txt","dat","nc","nc4","cdf","h5","hdf5","hdf","mseed","miniseed","sac","seed","dataless","xml","qml","rnx","rinex","crx","obs","nav","pos","tenv","tenv3","enu","json","geojson","shp","gpkg","kml","kmz","parquet","mat","npy","npz","sqlite","db","xlsx","xls","ods","zip","gz","tgz","tar","bz2","xz","7z","z","grd","tif","tiff","asc","segy","sgy","evt","gse","css","wfdisc","hyp","pha","sta","stations","csvz","feather","rds","rdata","nmea","ubx","sp3","clk","bin","grib","grb","grib2","ascii","log","tbl","out","cat","lst"}
def ext(name):
    n = name.lower()
    if n.endswith(".tar.gz"): return "tar.gz"
    if "." not in n: return "(none)"
    return n.rsplit(".", 1)[1]

COMPANY = re.compile(r"\b(Inc\.?|LLC|Ltd\.?|GmbH|Pty|PLC|S\.r\.l|B\.V\.|Limited)(?=\W|$)")
COMPANY_NAMES = re.compile(r"\b(Google|Microsoft|IBM|Shell|Chevron|ExxonMobil|Schlumberger|Trimble|Septentrio|Guralp|Nanometrics|Kinemetrics|PurpleAir|Vaisala|Campbell Scientific|Airly|Sensirion|Bosch|Siemens)\b")
COMPANY_WEAK = re.compile(r"\b(Technologies|Consulting|Company|Corporation|AG|S\.A\.|Oy|A/S)(?=\W|$)")
def company_flag(affs):
    if COMPANY.search(affs) or COMPANY_NAMES.search(affs): return "yes"
    a = re.sub(r"University Corporation|Department of [^,]*Technologies|Institute of [^,]*Technologies|Technologies? \(|of Technology", "", affs)
    m = COMPANY_WEAK.search(a)
    return ("weak:" + m.group(0)) if m else ""

def funding(md, text):
    """returns (kept, drops[list], review[list], names[list], desc)"""
    names, struct = [], []
    for g in md.get("grants") or []:
        f = (g.get("funder") or {}).get("name") or ""
        t = g.get("title") or ""
        if isinstance(t, dict): t = t.get("en") or ""
        names.append(f.strip() or t.strip()); struct.append(" ".join([f, t, g.get("acronym") or "", g.get("program") or ""]))
    notes = strip(md.get("notes"))
    desc = strip(md.get("description"))
    drops, review = [], []
    for s in struct:
        m = DEF_RE.search(s)
        if m: drops.append("funder field names " + m.group(0))
    if not drops:
        for label, blob in (("notes", notes), ("description", desc)):
            for m in DEF_RE.finditer(blob):
                ctx = blob[max(0, m.start() - 150): m.end() + 150]
                if FUND_CTX.search(ctx):
                    drops.append("%s state funding or support from %s" % (label, m.group(0))); break
                else:
                    review.append("%s mention %s without a funding statement" % (label, m.group(0))); break
    snippet = ""
    for blob in (notes, desc):
        m = re.search(r"[^.]{0,160}(funded by|funding (was )?(provided|from)|supported by|grant (no|number))[^.]{0,200}\.?", blob, re.I)
        if m:
            snippet = re.sub(r"https?://\S*|Crossref Funder Registry ID:?", "", m.group(0)).strip(" .,")
            break
    return drops, review, [n for n in names if n], snippet

def build():
    cands = fetch()
    studies, dropped, review = [], [], []
    for rid, (topic, h) in cands.items():
        md = h.get("metadata", {})
        title = strip(md.get("title")) or h.get("title", "")
        doi = h.get("doi") or md.get("doi") or ""
        link = "https://doi.org/" + doi if doi else h.get("links", {}).get("self_html", "")
        text = title + " " + strip(md.get("description"))
        base = {"id": rid, "title": title, "link": link, "topic": topic}
        files = h.get("files") or []
        ok, why = english(md, text)
        if ok is False:
            dropped.append(dict(base, reason="not English", detail=why)); continue
        if not files:
            dropped.append(dict(base, reason="no files listed")); continue
        exts = {}
        for f in files:
            e = ext(f.get("key", "")); exts[e] = exts.get(e, 0) + 1
        datalike = sum(n for e, n in exts.items() if e in DATA_EXT)
        if datalike == 0:
            dropped.append(dict(base, reason="no data-like files", detail=",".join(sorted(exts)))); continue
        drops, rev, names, snippet = funding(md, text)
        if drops:
            dropped.append(dict(base, reason="defense, military or intelligence funding", detail="; ".join(drops).replace(";", ","))); continue
        affs = " ".join(c.get("affiliation") or "" for c in md.get("creators", []))
        cf = company_flag(affs)
        company = cf == "yes"
        if cf.startswith("weak:"): rev_extra = ["affiliation may be a company (" + cf[5:] + ")"]
        else: rev_extra = []
        rev = rev + rev_extra
        if ok is None: rev.append(why)
        if company and rev is not None and False: pass
        if rev:
            review.append(dict(base, reason="; ".join(rev).replace(";", ","), files=len(files), exts=exts, affiliations=affs[:300])); continue
        if company:
            # company detection is pattern based, send ambiguous affiliations to review only if pattern is a bare word
            pass
        total = sum(f.get("size", 0) for f in files)
        types = ", ".join("%s x%d" % (e, n) for e, n in sorted(exts.items(), key=lambda x: -x[1])[:6])
        if names:
            fund = "Funding: " + ", ".join(dict.fromkeys(names)).replace(";", ",")
            fund += ". No defense, military or intelligence funder found in the record fields or description."
        elif snippet:
            fund = "Funding: stated in the record text only, " + snippet.replace(";", ",")[:280] + ". No defense, military or intelligence funder found."
        else:
            fund = "Funding: funding not stated."
        studies.append({
            "study": title,
            "link": link,
            "classification": "Indexed (company)" if company else "Indexed",
            "indexed": INDEXED,
            "topic": topic,
            "repository": "Zenodo",
            "receipt": ["Read: record metadata and file list",
                        "Released files: %d (%s), %.1f MB listed" % (len(files), types, total / 1e6),
                        fund],
            "anchor": "zenodo-" + rid,
        })
    return studies, dropped, review, cands

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    studies, dropped, review, cands = build()
    # remove-at-request gate
    try:
        rem = json.load(open(os.path.expanduser("~/bones-forge/ledger/removed_at_request.json")))["ids"]
    except Exception: rem = []
    studies = [s for s in studies if s["anchor"] not in rem and s["link"].replace("https://doi.org/", "") not in rem]
    json.dump({"note": "Earth and station datasets on Zenodo with released files, indexed from the record metadata and file list. A classification for indexing, not an assessment. Records with defense, military or intelligence funding are not listed.",
               "terms": TERMS, "studies": studies}, open(os.path.join(ROOT, "list.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(dropped, open(os.path.join(HERE, "dropped.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(review, open(os.path.join(HERE, "needs_review.json"), "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    topics = list(TOPICS)
    L = ["# Earth and station index sweep report", "", "Source: Zenodo API, type dataset, open access, listings and sizes only. Screened %d records." % len(cands), "",
         "| Topic | Screened | Indexed | Dropped | Needs review |", "|---|---|---|---|---|"]
    for t in topics:
        sc = sum(1 for v in cands.values() if v[0] == t)
        L.append("| %s | %d | %d | %d | %d |" % (t, sc, sum(s["topic"] == t for s in studies), sum(d["topic"] == t for d in dropped), sum(r["topic"] == t for r in review)))
    L += ["", "Total indexed %d, dropped %d, needs review %d." % (len(studies), len(dropped), len(review)), "", "## Drop reasons", ""]
    for r, n in Counter(d["reason"] for d in dropped).most_common(): L.append("- %s: %d" % (r, n))
    L += ["", "## Needs review reasons", ""]
    for r, n in Counter(x["reason"][:90] for x in review).most_common(15): L.append("- %s: %d" % (r, n))
    L += ["", "## Classification", "", "- Indexed (company): %d" % sum(s["classification"] != "Indexed" for s in studies),
          "- Funding not stated: %d" % sum("funding not stated" in s["receipt"][2] for s in studies),
          "", "## Method notes", "",
          "- Funding is read from the Zenodo grants field, notes and description. A defense funder in a funder field or in a funding sentence drops the record. A defense name in text without a funding sentence goes to needs review.",
          "- Linked paper acknowledgments and Earth System Science Data papers were not read in this first version.",
          "- Company detection uses affiliation patterns and is conservative.",
          "- Cache: %s" % CACHE, "- Re-run: python3 -I %s" % os.path.join(HERE, "earthdata_sweep.py")]
    open(os.path.join(ROOT, "SWEEP_REPORT.md"), "w").write("\n".join(L) + "\n")
    print("indexed", len(studies), "dropped", len(dropped), "review", len(review))

if __name__ == "__main__":
    main()
