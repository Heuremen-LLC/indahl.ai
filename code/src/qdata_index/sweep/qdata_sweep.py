#!/usr/bin/env python3
"""qdata_sweep.py: index published non-IBM qubit and quantum-device datasets.

Run:  python3 -I ~/bones-forge/qdata_index/sweep/qdata_sweep.py [--max-per-source N] [--sources zenodo,figshare,dryad,osf] [--no-crossref]
Standard library only. Resumable: every HTTP response is cached under sweep/cache/.
Polite: 2.5 s between live API calls. Never downloads data files, listings only.
arXiv is not queried (its API often returns empty bodies). Crossref is used only to read
the funder list of a linked paper for records that would otherwise be listed.
"""
import json, os, re, sys, time, hashlib, html, urllib.request, urllib.parse, urllib.error
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
UA = "qdata-index-sweep/0.1 (index of public quantum datasets; read-only)"
DELAY = 2.5
INDEXED = "2026-11-12"
CAP = {"zenodo": 1000, "figshare": 450, "dryad": 250, "osf": 200}

TERMS = ("Free to download and cite with attribution. All rights reserved. Text and data mining and use as "
         "AI training data are not permitted: https://indahl.ai/terms#ai-training")

QUERIES = [
    "transmon", "fluxonium", "superconducting qubit", "qubit coherence T1 T2", "randomized benchmarking",
    "Rigetti", "IQM", "Oxford Quantum Circuits", "Google Sycamore", "Amazon Braket", "quantum processor raw data",
    "trapped ion", "ion trap qubit", "neutral atom tweezer", "optical tweezer array", "Rydberg atom array",
    "nitrogen-vacancy", "NV center", "spin qubit", "silicon quantum dot", "quantum dot qubit", "germanium hole spin",
    "photonic quantum", "single photon source", "boson sampling", "quantum sensing magnetometry",
    "two-level system loss", "TLS superconducting resonator", "qubit materials loss tangent",
    "quantum key distribution", "quantum random number generator", "QRNG raw", "quantum device calibration",
    "Josephson parametric amplifier", "qubit readout", "Ramsey T2 echo", "quantum gate fidelity data",
    "cat qubit", "bosonic mode cavity", "Majorana nanowire", "quantum annealer D-Wave",
]

PLATFORMS = [  # order matters, first match wins
    ("neutral atom", r"neutral[- ]atom|tweezer|rydberg|optical lattice clock|atom array|ultracold atom"),
    ("trapped ion", r"trapped[- ]ion|ion[- ]trap|\bytterbium ion|\bcalcium ion|\bbarium ion|quantinuum|\bionq\b"),
    ("NV center and spin qubit", r"nitrogen[- ]vacancy|\bNV[- ]?cent|\bNV\b|diamond defect|spin qubit|silicon vacancy|donor spin|electron spin resonance qubit"),
    ("quantum dot", r"quantum dot|singlet[- ]triplet|hole spin|\bSi/SiGe|\bMOS qubit"),
    ("superconducting qubit", r"transmon|fluxonium|superconducting qubit|josephson|rigetti|\biqm\b|oxford quantum circuits|sycamore|\bsquid\b|cat qubit|parametric amplifier|coplanar waveguide|superconducting (resonator|circuit|processor)|flux qubit|charge qubit|phase qubit|xmon|gatemon|capacitively shunted"),
    ("two-level-system and materials", r"two[- ]level[- ]system|\bTLS\b|loss tangent|dielectric loss"),
    ("photonic", r"photonic|single[- ]photon|boson sampling|squeezed light|entangled photon|photon pair|spdc"),
    ("quantum sensing", r"quantum sens|magnetometr|atomic clock|quantum metrolog"),
    ("QKD and QRNG", r"quantum key distribution|\bqkd\b|quantum random number|\bqrng\b"),
    ("quantum annealer", r"quantum anneal|d-wave"),
    ("vendor calibration record", r"calibration (record|data|log)|device properties"),
]
PLAT_RE = [(n, re.compile(p, re.I)) for n, p in PLATFORMS]

IBM_RE = re.compile(r"\bibm[ _-]?(quantum|q\b|brisbane|kyoto|osaka|sherbrooke|torino|fez|marrakesh|heron|eagle|kingston|cleveland|nazca|strasbourg|aachen|pittsburgh|miami|boston|peekskill|washington|cusco|lagos)|\bqiskit\b|ibmq|ibm_", re.I)
OTHER_VENDOR_RE = re.compile(r"rigetti|\biqm\b|oxford quantum|\boqc\b|sycamore|google quantum|braket|quantinuum|\bionq\b|d-wave|quera|pasqal|xanadu|psiquantum|alpine quantum|zurich instruments", re.I)

DEFENSE_RE = re.compile(
    r"\bdarpa\b|\biarpa\b|\bdod\b|department of defen[cs]e|ministry of defen[cs]e|\bmod\b(?= uk)|\bonr\b|office of naval|\bafosr\b|air force office|\bafrl\b|air force research|"
    r"army research|\bamry\b|\barl\b|\baro\b|laboratory for physical sciences|\blps\b|\bnsa\b|national security agency|u\.?s\.? army|u\.?s\.? navy|u\.?s\.? air force|"
    r"naval research|\bdstl\b|defen[cs]e science and technology|armasuisse|israel(i)? ministry of defen|\bidf\b|military|defen[cs]e advanced research|intelligence advanced research|"
    r"\bnrl\b|\bsandia\b(?=.*defen)|office of scientific research.*(air|navy)|\bdtra\b|defen[cs]e threat|\bnavsea\b|\bonrg\b|\bdefen[cs]e innovation|\bdiu\b|\bcdao\b|joint quantum institute.*(army|lps)|\bdgist\b(?=.*defen)|\badd\b(?= korea)|agency for defense development|\bbmvg\b|german federal ministry of defen|\bdga\b|direction g[eé]n[eé]rale de l.armement|\bdefence\b|\bdefense\b", re.I)

COMPANY_RE = re.compile(r"rigetti|\biqm\b|iqm quantum|oxford quantum circuits|google (quantum|llc|research)|google quantum ai|quantinuum|\bionq\b|amazon|aws|quera|pasqal|atom computing|alice\s*&\s*bob|xanadu|psiquantum|id quantique|quantum machines|zurich instruments|d-wave|microsoft|infleqtion|oxford ionics|alpine quantum technologies|quantware|bluefors|qblox|toshiba|nvidia|intel corp|ibm", re.I)

DATA_EXT = {"h5", "hdf5", "hdf", "npz", "npy", "csv", "tsv", "json", "mat", "txt", "dat", "parquet", "nc", "feather", "jsonl", "ndjson"}
ARCHIVE_EXT = {"zip", "gz", "tgz", "tar", "bz2", "xz", "7z"}
OTHER_DATA_EXT = {"xlsx", "xls", "pkl", "pickle", "bin", "cdf", "asc", "dta", "sav", "zarr", "tdms", "raw", "sqlite", "db", "cbf", "edf", "lvm", "opj"}
CODE_EXT = {"py", "ipynb", "m", "r", "jl", "c", "cpp", "h", "java", "sh", "yml", "yaml", "toml", "tex", "md", "bib", "cfg", "ini", "whl", "rs"}
FIG_EXT = {"png", "jpg", "jpeg", "gif", "svg", "pdf", "eps", "tif", "tiff", "mp4", "avi", "mov", "pptx", "docx", "doc", "ppt"}

ENG_WORDS = set("the of and in to a for with is we are on by from this that measured data qubit quantum device using as an at be were was which".split())
SIM_RE = re.compile(r"\b(simulat|numerical|theoretical|theory|monte carlo|ab initio|dft|machine[- ]learning model|synthetic data)", re.I)
MEAS_RE = re.compile(r"\b(measure|experiment|device|raw data|spectroscop|time[- ]trace|fabricat|cryogenic|dilution|sample|counts|acquired|recorded)", re.I)

removed_ids = set()
try:
    removed_ids = {x.lower() for x in json.load(open(os.path.expanduser("~/bones-forge/ledger/removed_at_request.json")))["ids"]}
except Exception as e:
    print("warn: removed_at_request.json not read:", e)
dnc_text = ""
try:
    dnc_text = open(os.path.expanduser("~/bones-forge/rolodex/DO_NOT_CONTACT.txt")).read().lower()
except Exception:
    pass

_last = [0.0]
dead = {"dryad": 0}
stats = {"live_calls": 0, "cache_hits": 0, "errors": 0}


def fetch(url, data=None, headers=None, tries=3):
    key = hashlib.sha1((url + (json.dumps(data, sort_keys=True) if data else "")).encode()).hexdigest()
    path = os.path.join(CACHE, key + ".json")
    if os.path.exists(path):
        stats["cache_hits"] += 1
        try:
            return json.load(open(path))
        except Exception:
            os.remove(path)
    if "datadryad" in url and dead["dryad"] >= 1:
        return None
    for attempt in range(tries):
        wait = (8.0 if "datadryad" in url else DELAY) - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        h = {"User-Agent": UA, "Accept": "application/json"}
        if headers:
            h.update(headers)
        body = None
        if data is not None:
            body = json.dumps(data).encode()
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=h)
        stats["live_calls"] += 1
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                txt = r.read().decode("utf-8", "replace")
            if not txt.strip():
                stats["errors"] += 1
                return None
            obj = json.loads(txt)
            json.dump(obj, open(path, "w"))
            return obj
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = int(e.headers.get("Retry-After", "60") or 60)
                print("  429, waiting", min(ra, 120), "s", url[:90], flush=True)
                time.sleep(min(ra, 120) + 1)
                continue
            if e.code in (404, 410):
                stats["errors"] += 1
                return None
            if e.code == 400:
                stats["errors"] += 1
                return None
            time.sleep(5)
        except Exception:
            time.sleep(5)
    stats["errors"] += 1
    if "datadryad" in url:
        dead["dryad"] += 1
    return None


def strip(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def ext_of(name):
    n = name.lower()
    return n.rsplit(".", 1)[-1] if "." in n else ""


def classify_files(files):
    """files: list of (name,size). Returns dict summary."""
    c = Counter()
    total = 0
    for name, size in files:
        e = ext_of(name)
        total += size or 0
        if e in DATA_EXT:
            c["data:" + e] += 1
        elif e in ARCHIVE_EXT:
            c["archive:" + e] += 1
        elif e in OTHER_DATA_EXT:
            c["otherdata:" + e] += 1
        elif e in CODE_EXT:
            c["code"] += 1
        elif e in FIG_EXT:
            c["figure"] += 1
        else:
            c["other:" + (e or "none")] += 1
    return c, total


def is_english(text, lang=None):
    if lang and lang.lower() not in ("eng", "en", "english"):
        return False
    t = text.lower()
    letters = [ch for ch in t if ch.isalpha()]
    if not letters:
        return False
    ascii_ratio = sum(1 for ch in letters if ord(ch) < 128) / len(letters)
    words = re.findall(r"[a-z]+", t)
    hit = sum(1 for w in words if w in ENG_WORDS) / max(1, len(words))
    return ascii_ratio > 0.92 and hit > 0.06


def platform_of(title, tags, desc):
    head = (title + " " + tags)
    for n, rx in PLAT_RE:
        if rx.search(head):
            return n, "strong"
    for n, rx in PLAT_RE:
        if rx.search(desc):
            return n, "weak"
    if re.search(r"qubit", head + " " + desc, re.I):
        return "qubit (platform unclear)", "weak"
    return None, None


def norm_ids(*vals):
    out = set()
    for v in vals:
        if not v:
            continue
        v = v.lower()
        out.add(v)
        m = re.search(r"10\.\d{4,9}/\S+", v)
        if m:
            out.add(m.group(0).rstrip(".,;)"))
        m = re.search(r"arxiv[:./ ]*(\d{4}\.\d{4,5})", v)
        if m:
            out.add("arxiv-" + m.group(1))
    return out


def slug(link):
    s = re.sub(r"^https?://(dx\.)?(doi\.org/)?", "", link.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def crossref_funders(doi):
    d = fetch("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    if not d:
        return None
    m = d.get("message", {})
    return [f.get("name", "") for f in m.get("funder", [])] if "funder" in m else []


def make_rec(src, rid, title, link, version, desc, tags, creators, affils, files, funders, funding_text,
             access_open, lang, rel_dois, license_, created):
    return dict(src=src, rid=rid, title=title, link=link, version=version, desc=desc, tags=tags,
                creators=creators, affils=affils, files=files, funders=funders, funding_text=funding_text,
                access_open=access_open, lang=lang, rel_dois=rel_dois, license=license_, created=created)


def screen(r, use_crossref=True):
    """Return (decision, reason, row_or_None). decision in listed/dropped/review."""
    title, desc = r["title"], r["desc"]
    text = title + " " + desc + " " + r["tags"]
    ids = norm_ids(r["link"], r["rid"], *r["rel_dois"])
    if ids & removed_ids or any(i in dnc_text for i in ids if len(i) > 8):
        return "dropped", "removed at request", None
    if not is_english(title + " " + desc, r["lang"]):
        return "dropped", "not English", None
    if not r["access_open"]:
        return "dropped", "files not openly accessible", None
    if r["files"] is None:
        return "review", "file list not reachable (source rate limit), not screened further", dict(r, platform=platform_of(title, r["tags"], desc)[0] or "unclassified")
    summ, total = classify_files(r["files"])
    n_data = sum(v for k, v in summ.items() if k.startswith("data:"))
    n_arch = sum(v for k, v in summ.items() if k.startswith("archive:"))
    n_oth = sum(v for k, v in summ.items() if k.startswith("otherdata:"))
    if not r["files"]:
        return "dropped", "no files listed", None
    if n_data + n_arch + n_oth == 0:
        return "dropped", "code or figures only, no measurement files", None
    plat, strength = platform_of(title, r["tags"], desc)
    if not plat:
        return "dropped", "out of scope (no qubit or quantum-device platform term)", None
    # IBM only
    n_ibm = len(IBM_RE.findall(text)) + len(re.findall(r"\bibm\b", text, re.I))
    n_oth = len(OTHER_VENDOR_RE.findall(text))
    if n_ibm and n_ibm > n_oth:
        return "dropped", "IBM device (belongs to the QIA List)", None
    ibm_soft = bool(n_ibm) and n_ibm <= n_oth and n_ibm > 0 and False
    # simulation/theory
    if SIM_RE.search(text) and not MEAS_RE.search(text):
        return "dropped", "simulation or theory only", None
    # funding
    fund_blob = " ; ".join(r["funders"]) + " " + r["funding_text"]
    m = DEFENSE_RE.search(fund_blob)
    if m:
        return "dropped", "defense, military or intelligence funder (" + m.group(0).lower() + ")", None
    m = DEFENSE_RE.search(desc)
    if m and re.search(r"fund|support|grant|sponsor|acknowledg|award|contract", desc, re.I):
        # only drop when the term sits near a funding word
        for mm in DEFENSE_RE.finditer(desc):
            ctx = desc[max(0, mm.start() - 120): mm.end() + 120]
            if re.search(r"fund|support|grant|sponsor|acknowledg|award|contract", ctx, re.I):
                return "dropped", "defense, military or intelligence funder in description (" + mm.group(0).lower() + ")", None
    reasons = []
    if ibm_soft:
        reasons.append("IBM named in the record without another vendor, device unclear")
    if strength == "weak":
        reasons.append("platform term only in the description, scope unclear")
    if n_data + n_oth == 0:
        reasons.append("only archive files, contents not opened")
    elif n_data == 0:
        reasons.append("only spreadsheet or binary formats, measurement content unconfirmed (" + ", ".join(k for k in summ if k.startswith("otherdata:")) + ")")
    if re.search(r"restricted|embargo|on request|upon request|available from the author", desc, re.I) and re.search(r"data.{0,40}(on request|upon request|available from)", desc, re.I):
        reasons.append("description says some data are on request")
    # company
    company = bool(COMPANY_RE.search(" ".join(r["affils"])))
    # crossref funder read
    cr_note = None
    if use_crossref and not reasons and r["rel_dois"]:
        fl = crossref_funders(r["rel_dois"][0])
        if fl is None:
            cr_note = "linked paper funder list not reachable"
        else:
            if DEFENSE_RE.search(" ; ".join(fl)):
                return "dropped", "defense, military or intelligence funder (Crossref: " + DEFENSE_RE.search(" ; ".join(fl)).group(0).lower() + ")", None
            if fl:
                cr_note = "linked paper funders via Crossref: " + "; ".join(fl[:6]).replace(";", ",")
            else:
                cr_note = "linked paper has no funder list in Crossref"
    if reasons:
        return "review", "; ".join(reasons).replace(";", ","), dict(r, platform=plat)
    ftypes = ", ".join(sorted({k.split(":", 1)[1] for k in summ if not k.startswith(("code", "figure", "other:"))}))
    nrel = n_data + n_arch + n_oth
    if r["funders"] or r["funding_text"].strip():
        shown = (", ".join(r["funders"]) or r["funding_text"].strip())[:300].replace(";", ",")
        fund_line = "Funding: " + shown + " (no defense, military or intelligence funder found)"
    else:
        fund_line = "Funding: funding not stated in the record (no defense, military or intelligence funder found)"
    if cr_note:
        fund_line += ". " + cr_note
    rec_line = "Read: record metadata and file list, " + r["src"] + " " + (r["version"] or "version not stated")
    row = {
        "study": title,
        "link": r["link"],
        "classification": "Indexed (company)" if company else "Indexed",
        "indexed": INDEXED,
        "platform": plat,
        "receipt": [
            rec_line + ", created " + (r["created"] or "date not stated"),
            "Released files: %d (%s), total %.1f MB listed, not downloaded" % (nrel, ftypes, total / 1e6),
            fund_line,
        ],
        "anchor": slug(r["link"]),
        "source": r["src"],
    }
    if r["license"]:
        row["receipt"].append("License: " + str(r["license"]).replace(";", ","))
    return "listed", "", dict(row=row, rec=r)


# ---------------- sources ----------------

def z_records(max_n):
    seen = 0
    for typ in ("dataset", "software"):
        for q in QUERIES:
            for page in range(1, 9):
                url = "https://zenodo.org/api/records?" + urllib.parse.urlencode(
                    {"q": '"%s"' % q, "type": typ, "size": 25, "page": page, "sort": "bestmatch"})
                d = fetch(url)
                if not d:
                    break
                hits = d.get("hits", {}).get("hits", [])
                if not hits:
                    break
                for h in hits:
                    yield h
                if len(hits) < 25:
                    break


def z_to_rec(h):
    m = h.get("metadata", {})
    files = [(f.get("key", ""), f.get("size", 0)) for f in h.get("files", [])]
    grants = m.get("grants", []) or []
    funders = []
    for g in grants:
        fn = (g.get("funder") or {}).get("name", "")
        funders.append((fn + " " + (g.get("title", "") or "") + " " + (g.get("acronym", "") or "")).strip())
    creators = [c.get("name", "") for c in m.get("creators", [])]
    affils = [c.get("affiliation") or "" for c in m.get("creators", [])]
    rel = []
    for ri in m.get("related_identifiers", []) or []:
        if ri.get("scheme") == "doi" and ri.get("relation") in ("isSupplementTo", "isReferencedBy", "isCitedBy", "isDocumentedBy", "isSupplementedBy", "cites", "isDescribedBy"):
            rel.append(ri.get("identifier", ""))
    rel = [x for x in rel if x and "zenodo" not in x.lower()]
    tags = " ".join(m.get("keywords", []) or [])
    lic = (m.get("license") or {}).get("id")
    return make_rec("Zenodo", h.get("doi") or str(h.get("id")), strip(m.get("title", "")),
                    "https://doi.org/" + h["doi"] if h.get("doi") else h.get("links", {}).get("html", ""),
                    ("version " + str(m["version"])) if m.get("version") else None,
                    strip(m.get("description", "")), tags, creators, affils, files, funders,
                    "", m.get("access_right") == "open", (m.get("language") or "eng"), rel, lic, (h.get("created") or "")[:10])


def f_records(_=None):
    for q in QUERIES:
        for page in range(1, 4):
            d = fetch("https://api.figshare.com/v2/articles/search",
                      data={"search_for": q, "item_type": 3, "page": page, "page_size": 50})
            if not d:
                break
            for a in d:
                yield a
            if len(d) < 50:
                break


def f_to_rec(a):
    d = fetch("https://api.figshare.com/v2/articles/%d" % a["id"])
    if not d:
        return None
    files = [(f.get("name", ""), f.get("size", 0)) for f in d.get("files", [])]
    funders = [f.get("title", "") for f in (d.get("funding_list") or [])]
    ftxt = d.get("funding") or ""
    authors = [x.get("full_name", "") for x in d.get("authors", [])]
    tags = " ".join(d.get("tags", []) or [])
    cats = " ".join(c.get("title", "") for c in d.get("categories", []) or [])
    return make_rec("Figshare", d.get("doi", ""), strip(d.get("title", "")),
                    "https://doi.org/" + d["doi"] if d.get("doi") else d.get("url_public_html", ""),
                    "v" + str(d.get("version", "")), strip(d.get("description", "")), tags + " " + cats, authors, [],
                    files, funders, ftxt, not d.get("is_confidential") and not d.get("embargo_date") and d.get("is_public", True),
                    "eng", [d["resource_doi"]] if d.get("resource_doi") else [], (d.get("license") or {}).get("name"),
                    (d.get("created_date") or "")[:10])


def dryad_records(_=None):
    for q in QUERIES:
        for page in range(1, 4):
            d = fetch("https://datadryad.org/api/v2/search?" + urllib.parse.urlencode({"q": q, "per_page": 50, "page": page}))
            if not d:
                break
            items = d.get("_embedded", {}).get("stash:datasets", [])
            for it in items:
                yield it
            if len(items) < 50:
                break


def dryad_to_rec(it):
    vhref = it.get("_links", {}).get("stash:version", {}).get("href")
    files = []
    if vhref:
        fd = fetch("https://datadryad.org" + vhref + "/files?per_page=100")
        if fd is None:
            files = None
        if fd:
            for f in fd.get("_embedded", {}).get("stash:files", []):
                files.append((f.get("path", ""), f.get("size", 0)))
    funders = []
    for f in it.get("funders", []) or []:
        funders.append(" ".join(str(f.get(k, "")) for k in ("organization", "awardNumber", "awardDescription")).strip())
    authors = [(a.get("firstName", "") + " " + a.get("lastName", "")).strip() for a in it.get("authors", [])]
    affs = [a.get("affiliation") or "" for a in it.get("authors", [])]
    rel = [w.get("identifier", "").replace("https://doi.org/", "") for w in it.get("relatedWorks", []) or [] if w.get("identifierType") == "DOI"]
    ident = it.get("identifier", "").replace("doi:", "")
    return make_rec("Dryad", ident, strip(it.get("title", "")), "https://doi.org/" + ident,
                    "version " + str(it.get("versionNumber", "")), strip(it.get("abstract", "")),
                    " ".join(it.get("keywords", []) or []), authors, affs, files, funders,
                    "", True, "eng", rel, it.get("license"), (it.get("publicationDate") or "")[:10])


def osf_records(_=None):
    for q in QUERIES:
        for page in range(1, 3):
            u = "https://api.osf.io/v2/nodes/?" + urllib.parse.urlencode(
                {"filter[title][icontains]": q, "page[size]": 50, "page": page})
            d = fetch(u)
            if not d:
                break
            for n in d.get("data", []):
                yield n
            if not d.get("links", {}).get("next"):
                break


def osf_to_rec(n):
    a = n["attributes"]
    nid = n["id"]
    fd = fetch("https://api.osf.io/v2/nodes/%s/files/osfstorage/?page[size]=100" % nid)
    files = []
    if fd:
        for f in fd.get("data", []):
            at = f["attributes"]
            if at.get("kind") == "file":
                files.append((at.get("name", ""), at.get("size") or 0))
            else:
                files.append((at.get("name", "") + ".folder", 0))
    lic = None
    return make_rec("OSF", nid, strip(a.get("title", "")), "https://osf.io/%s/" % nid, "modified " + (a.get("date_modified") or "")[:10],
                    strip(a.get("description", "")), " ".join(a.get("tags", []) or []), [], [], files, [], "",
                    bool(a.get("public")), "eng", [], lic, (a.get("date_created") or "")[:10])


SOURCES = {
    "zenodo": (z_records, z_to_rec),
    "figshare": (f_records, f_to_rec),
    "dryad": (dryad_records, dryad_to_rec),
    "osf": (osf_records, osf_to_rec),
}


def main():
    args = sys.argv[1:]
    srcs = list(SOURCES)
    use_cr = "--no-crossref" not in args
    caps = dict(CAP)
    if "--sources" in args:
        srcs = args[args.index("--sources") + 1].split(",")
    if "--max-per-source" in args:
        n = int(args[args.index("--max-per-source") + 1])
        caps = {k: n for k in caps}
    listed, dropped, review = [], [], []
    seen = set()
    per_src = Counter()
    for s in srcs:
        gen, conv = SOURCES[s]
        print("== source", s, flush=True)
        for raw in gen(caps[s]):
            if per_src[s] >= caps[s] or sum(per_src.values()) >= 1500:
                break
            key = s + ":" + str(raw.get("id") if isinstance(raw, dict) else raw)
            if key in seen:
                continue
            seen.add(key)
            # cheap prefilter on figshare/dryad/osf titles to save detail calls: none (screen all up to cap)
            if s == "osf":
                at = raw["attributes"]
                if not (at.get("public") and PLAT_RE and any(rx.search((at.get("title", "") + " " + at.get("description", "") + " ".join(at.get("tags", [])))) for _, rx in PLAT_RE)):
                    continue
            try:
                rec = conv(raw)
            except Exception as e:
                print("  conv error", key, e)
                continue
            if rec is None:
                continue
            per_src[s] += 1
            dec, reason, out = screen(rec, use_cr)
            brief = {"source": rec["src"], "id": rec["rid"], "title": rec["title"], "link": rec["link"]}
            if dec == "listed":
                listed.append(out["row"])
            elif dec == "review":
                review.append(dict(brief, reason=reason, platform=out["platform"]))
            else:
                dropped.append(dict(brief, reason=reason))
            if sum(per_src.values()) % 25 == 0:
                print("  screened", dict(per_src), "listed", len(listed), "review", len(review), "dropped", len(dropped), flush=True)
                write(listed, dropped, review, per_src)
    write(listed, dropped, review, per_src)
    print("done", dict(per_src), "listed", len(listed), "review", len(review), "dropped", len(dropped), stats)


def dedupe(rows):
    out, seen = [], set()
    for r in rows:
        k = r.get("link") or r.get("id")
        t = re.sub(r"\W+", "", (r.get("study") or r.get("title") or "").lower())
        if k in seen or t in seen:
            continue
        seen.add(k); seen.add(t)
        out.append(r)
    return out


def write(listed, dropped, review, per_src):
    listed = dedupe(listed)
    # 12 Nov 2026: hand drops (Bones read the list): records that are not quantum-device measurements stay out of every re-run
    _hd = json.load(open(os.path.join(OUT, "hand_drops.json"))) if os.path.exists(os.path.join(OUT, "hand_drops.json")) else {}
    dropped = list(dropped) + [dict(link=k, reason="hand drop: " + v["why"], title=v["study"]) for k, v in _hd.items() if any(r.get("link") == k for r in listed)]
    listed = [r for r in listed if r.get("link") not in _hd]
    for r in listed:
        r.pop("source", None) if False else None
    note = ("The Index of published qubit and quantum-device datasets beyond IBM: records that release raw measurement files, "
            "with a classification for indexing, not an assessment. Companion to the QIA List of IBM quantum studies. First version, built 2026-11-12.")
    json.dump({"note": note, "terms": TERMS, "studies": [{k: v for k, v in r.items() if k != "source"} for r in listed]},
              open(os.path.join(OUT, "list.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(dropped, open(os.path.join(HERE, "dropped.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(review, open(os.path.join(HERE, "needs_review.json"), "w"), indent=1, ensure_ascii=False)
    plat = Counter(r["platform"] for r in listed)
    srcc = Counter(r["source"] for r in listed)
    dr = Counter(re.sub(r"\s*\(.*\)$", "", r["reason"]) for r in dropped)
    rv = Counter(r["reason"][:70] for r in review)
    comp = sum(1 for r in listed if r["classification"] == "Indexed (company)")
    L = ["# Sweep report, qdata index first version", "",
         "Run date 2026-11-12. Screened per source: " + ", ".join("%s %d" % kv for kv in per_src.items()) + ".",
         "Listed %d (company %d), needs_review %d, dropped %d." % (len(listed), comp, len(review), len(dropped)),
         "arXiv was not queried (its API often returns empty bodies). Crossref was read only for the funder list of a linked paper.", "",
         "## Listed by platform"] + ["- %s: %d" % kv for kv in plat.most_common()] + ["", "## Listed by source"] + \
        ["- %s: %d" % kv for kv in srcc.most_common()] + ["", "## Dropped by reason"] + ["- %s: %d" % kv for kv in dr.most_common()] + \
        ["", "## Needs review by reason"] + ["- %s: %d" % kv for kv in rv.most_common()]
    open(os.path.join(OUT, "SWEEP_REPORT.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
