#!/usr/bin/env python3 -I
"""IRIS sweep: find LLM-evaluation papers that release per-item model outputs.

Re-run weekly:  python3 -I ~/bones-forge/iris_index/sweep/iris_sweep.py [--max-screen N] [--refresh-queries]
Resumable: every arXiv result page and every screened id is cached under sweep/cache.
Writes only inside iris_index/sweep/. Reads SCAN_register.json and removed_at_request.json (never edits).
Downloaded text is data only; nothing from it is executed.
"""
import json, os, re, sys, time, subprocess, urllib.request, urllib.parse, urllib.error, datetime
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "cache")
QCACHE = os.path.join(CACHE, "queries")
PCACHE = os.path.join(CACHE, "papers")
for d in (QCACHE, PCACHE):
    os.makedirs(d, exist_ok=True)
SCAN = os.path.join(ROOT, "SCAN_register.json")
REMOVED = os.path.expanduser("~/bones-forge/ledger/removed_at_request.json")
TODAY = datetime.date.today().isoformat()
UA = "iris-sweep/1.0 (research index; contact via indahl.ai)"
ARXIV_DELAY = 3.0
_last = {}


def polite(host, delay):
    t = _last.get(host, 0)
    w = delay - (time.time() - t)
    if w > 0:
        time.sleep(w)
    _last[host] = time.time()


def http_get(url, host=None, delay=0.0, timeout=40, tries=3, binary=False):
    host = host or urllib.parse.urlparse(url).netloc
    for i in range(tries):
        if delay:
            polite(host, delay)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read()
                return r.status, (b if binary else b.decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(15 * (i + 1))
                continue
            return e.code, ""
        except Exception:
            time.sleep(5 * (i + 1))
    return 0, ""


# ---------- step 1: candidates ----------
TOPICS = [
    'evaluation', 'benchmark', '"LLM-as-a-judge"', 'leaderboard', '"red teaming"', 'hallucination',
    '"human evaluation"', '"model outputs"', 'reproducibility', 'robustness', 'contamination',
    '"prompt sensitivity"', 'calibration', 'factuality', 'safety', 'reasoning',
]
RELEASE_WORDS = ['release', 'outputs', 'generations', 'predictions', 'responses', 'completions', 'judgments']
CATS = ['cs.CL', 'cs.AI', 'cs.LG']
PAGE = 100
MAX_PAGES = 3  # per query; 300 newest-first per query


def build_queries():
    qs = []
    for cat in CATS:
        for t in TOPICS:
            for rw in RELEASE_WORDS[:4]:
                qs.append(f'cat:{cat} AND abs:{t} AND abs:{rw}')
    return qs


NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}


def parse_feed(xml):
    out = []
    root = ET.fromstring(xml)
    for e in root.findall("a:entry", NS):
        idurl = e.findtext("a:id", "", NS)
        m = re.search(r"abs/(.+)$", idurl)
        if not m:
            continue
        full = m.group(1)
        vm = re.match(r"(.+?)(v\d+)$", full)
        out.append({
            "id": full,
            "arxiv_id": vm.group(1) if vm else full,
            "version": vm.group(2) if vm else "v1",
            "title": " ".join(e.findtext("a:title", "", NS).split()),
            "authors": [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)],
            "abstract": " ".join(e.findtext("a:summary", "", NS).split()),
            "comment": " ".join(e.findtext("x:comment", "", NS).split()),
            "submitted": e.findtext("a:published", "", NS)[:10],
            "primary_category": (e.find("x:primary_category", NS).get("term") if e.find("x:primary_category", NS) is not None else ""),
        })
    return out


def gather_candidates(refresh=False):
    cands = {}
    end = datetime.date.today().strftime("%Y%m%d") + "2359"
    for qi, q in enumerate(build_queries()):
        for p in range(MAX_PAGES):
            key = re.sub(r"[^A-Za-z0-9]+", "_", q)[:120] + f"_p{p}"
            fn = os.path.join(QCACHE, key + ".json")
            if os.path.exists(fn) and not refresh:
                items = json.load(open(fn))
            elif "--cached-queries-only" in sys.argv:
                break
            else:
                params = urllib.parse.urlencode({
                    "search_query": f"({q}) AND submittedDate:[202501010000 TO {end}]",
                    "start": p * PAGE, "max_results": PAGE,
                    "sortBy": "submittedDate", "sortOrder": "descending"})
                st, body = http_get("https://export.arxiv.org/api/query?" + params, "arxiv-api", ARXIV_DELAY, timeout=90)
                if st != 200:
                    print(f"[query] fail {st} {q} p{p}", flush=True)
                    break
                try:
                    items = parse_feed(body)
                except ET.ParseError:
                    print("[query] parse error", q, flush=True)
                    break
                json.dump(items, open(fn, "w"))
            for it in items:
                cands.setdefault(it["arxiv_id"], it)
            if len(items) < PAGE:
                break
        if qi % 10 == 0:
            print(f"[query] {qi+1}/{len(build_queries())} candidates={len(cands)}", flush=True)
    return cands


# ---------- text helpers ----------
class TextExtract(HTMLParser):
    """Collects visible text with heading markers and affiliation spans."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0
        self.aff = []
        self._aff_depth = None
        self._stack = []
        self._cur_aff = []

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "") or ""
        if tag in ("br", "img", "meta", "link", "input", "hr", "wbr", "source", "col", "area", "base", "embed"):
            return
        self._stack.append((tag, "ltx_role_affiliation" in cls))
        if tag in ("script", "style", "math"):
            self.skip += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "p", "div", "li", "section"):
            self.parts.append("\n")
        if tag == "a":
            href = dict(attrs).get("href")
            if href and href.startswith("http"):
                self.parts.append(f" {href} ")
        if "ltx_role_affiliation" in cls:
            self._aff_depth = len(self._stack)
            self._cur_aff = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "math") and self.skip:
            self.skip -= 1
        if self._stack:
            if self._aff_depth == len(self._stack):
                t = " ".join("".join(self._cur_aff).split())
                if t:
                    self.aff.append(t)
                self._aff_depth = None
            self._stack.pop()

    def handle_data(self, data):
        if self.skip:
            return
        self.parts.append(data)
        if self._aff_depth is not None:
            self._cur_aff.append(data)


def html_to_text(html):
    p = TextExtract()
    try:
        p.feed(html)
    except Exception:
        pass
    text = "".join(p.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    affs = [re.sub(r"^Affiliation:\s*", "", a).strip() for a in p.aff]
    return text, [a for a in dict.fromkeys(affs) if a]


GH_RE = re.compile(r"github\.com/([A-Za-z0-9][A-Za-z0-9_.-]*)/([A-Za-z0-9_.-]+)", re.I)
HF_RE = re.compile(r"huggingface\.co/(datasets/|spaces/)?([A-Za-z0-9][A-Za-z0-9_.-]*)/([A-Za-z0-9_.-]+)", re.I)
ZEN_RE = re.compile(r"(?:zenodo\.org/(?:records?|deposit)/|10\.5281/zenodo\.)(\d+)", re.I)
HF_NOT_REPO = {"docs", "blog", "papers", "collections", "organizations", "spaces", "models", "datasets", "login", "join", "settings", "api", "learn", "posts", "pricing", "tasks", "new"}
GH_NOT_USER = {"features", "sponsors", "orgs", "topics", "marketplace", "settings", "about", "pricing", "login", "join", "apps", "collections", "enterprise", "security", "site", "contact", "customer-stories"}
TOOL_REPOS = {"eleutherai/lm-evaluation-harness", "vllm-project/vllm", "huggingface/transformers", "openai/evals", "openai/simple-evals",
              "huggingface/datasets", "huggingface/lighteval", "stanford-crfm/helm", "tatsu-lab/alpaca_eval", "lm-sys/fastchat",
              "meta-llama/llama", "pytorch/pytorch", "huggingface/trl", "huggingface/peft", "lm-sys/arena-hard-auto", "hendrycks/test",
              "openai/human-eval", "google/bigbench", "sylinrl/truthfulqa", "microsoft/lora", "unslothai/unsloth"}
RELEASE_CTX = re.compile(r"(we|our|authors?)\b.{0,160}\b(releas|open[- ]?sourc|publicly|public(ly)? avail|made available|available (at|on|in)|code|data|dataset|repositor|artifact|materials)|"
                         r"(code|data|dataset|outputs?|generations?|predictions?|responses?|repositor|artifacts?|materials|annotations?|logs?)\b.{0,120}\b(available|released|can be found|is at|are at|hosted|at:)", re.I | re.S)


def clean_url_part(s):
    s = s.rstrip(".,;:)]}'\">")
    if s.endswith(".git"):
        s = s[:-4]
    return s


def extract_links(text):
    gh, hf, zen = [], [], []
    for m in GH_RE.finditer(text):
        u, r = m.group(1), clean_url_part(m.group(2))
        if u.lower() in GH_NOT_USER or not r:
            continue
        gh.append((u, r, m.start()))
    for m in HF_RE.finditer(text):
        kind, u, r = (m.group(1) or ""), m.group(2), clean_url_part(m.group(3))
        if u.lower() in HF_NOT_REPO or kind == "spaces/":
            continue
        if not kind and not r:
            continue
        hf.append(("datasets" if kind else "models", u, r, m.start()))
    for m in ZEN_RE.finditer(text):
        zen.append((m.group(1), m.start()))
    return gh, hf, zen


def pick_links(abstract, comment, fulltext):
    """Return dict of unique links with provenance. Full-text links must sit near release language."""
    found = {}
    def add(kind, key, src):
        if key not in found:
            found[key] = {"kind": kind, "src": src}
    for src, txt in (("abstract", abstract), ("comment", comment)):
        g, h, z = extract_links(txt)
        for u, r, _ in g:
            add("gh", f"{u}/{r}", src)
        for k, u, r, _ in h:
            add("hf_" + k, f"{u}/{r}", src)
        for zid, _ in z:
            add("zenodo", zid, src)
    if fulltext:
        # cut references
        cut = re.search(r"\n\s*(References|Bibliography)\s*\n", fulltext)
        body = fulltext[:cut.start()] if cut and cut.start() > len(fulltext) * 0.4 else fulltext
        g, h, z = extract_links(body)
        def near(pos):
            ctx = body[max(0, pos - 220):pos + 60]
            return bool(RELEASE_CTX.search(ctx))
        for u, r, pos in g:
            if f"{u}/{r}".lower() in TOOL_REPOS:
                continue
            if near(pos):
                add("gh", f"{u}/{r}", "fulltext")
        for k, u, r, pos in h:
            if near(pos):
                add("hf_" + k, f"{u}/{r}", "fulltext")
        for zid, pos in z:
            if near(pos):
                add("zenodo", zid, "fulltext")
    return found


# ---------- step 2: released outputs ----------
DATA_EXT = re.compile(r"\.(jsonl|json|csv|tsv|parquet|jsonl\.gz|json\.gz|csv\.gz|jsonl\.zst|arrow)$", re.I)
KEYWORD = re.compile(r"(output|generation|prediction|response|completion|judg|verdict|answers?|samples?|transcript|rollout|trajector|annotation|ratings?|grad(ed|ing)|results?|inference|eval)", re.I)
BAD_PATH = re.compile(r"(node_modules/|^\.github/|package(-lock)?\.json$|tsconfig|\.vscode/|requirements|config[^/]*\.json$|/configs?/|^configs?/|\.eslintrc|composer\.json|manifest\.json|dataset_info\.json|dataset_infos\.json|^\.|/\.[^/]+$|state\.json$|tokenizer|special_tokens|vocab|merges|generation_config|model\.safetensors)", re.I)


MODEL_TOK = re.compile(r"(gpt|chatgpt|llama|qwen|qwq|mistral|mixtral|gemma|claude|deepseek|phi-?\d|olmo|gemini|falcon|vicuna|grok|glm|internlm|baichuan|smollm|granite|nemotron|zephyr|tulu|pythia|bloom|opt-?\d|yi-?\d|command-?r|palm|o[134]-?(mini|preview)?|haiku|sonnet|opus|kimi|minimax|ernie|hunyuan|aya|solar|starcoder|codellama|wizardlm|openchat|dbrx|jamba|mamba|t5|bart|r1)", re.I)
MODEL_TOK_STRICT = re.compile(r"(^|[^a-z])(gpt|chatgpt|llama|qwen|qwq|mistral|mixtral|gemma|claude|deepseek|phi|olmo|gemini|falcon|vicuna|grok|glm|internlm|baichuan|smollm|granite|nemotron|zephyr|tulu|pythia|bloom|haiku|sonnet|opus|kimi|ernie|hunyuan|aya|dbrx|jamba|starcoder|codellama|wizardlm|openchat|o1|o3|o4|r1)(?=$|[^a-z])", re.I)
OUT_WORD = re.compile(r"(generation|completion|response|prediction|output|judg|verdict|rollout|transcript)", re.I)
OUT_DIR = re.compile(r"^(outputs?|generations?|predictions?|responses?|completions?|models?|model_outputs?|judg\w*|raw)$", re.I)
EXCL_TOK = re.compile(r"(^|[^a-z])(gold|labels?|metrics?|timing|splits?|train(ing)?|dev|test[-_ ]?set|annotation[-_ ]?guidelines)(?=$|[^a-z])", re.I)


def classify_files(paths):
    """Return (accepted, rejected_data_files). Accepted: data ext, not excluded, and either a model
    name in the path, or an output word in the file name inside a per-model folder under an output-like dir."""
    kw, other = [], []
    for p in paths:
        if not DATA_EXT.search(p) or BAD_PATH.search(p):
            continue
        if EXCL_TOK.search(p):
            other.append(p)
            continue
        parts = p.split("/")
        base = parts[-1]
        model_in_path = bool(MODEL_TOK_STRICT.search(p))
        per_model_folder = any(OUT_DIR.match(d) for d in parts[:-2]) and len(parts) >= 3
        if model_in_path or (OUT_WORD.search(base) and per_model_folder):
            kw.append(p)
        else:
            other.append(p)
    return kw, other


# ---------- outputs_checked ----------
OUT_KEY = re.compile(r"^(.*(output|generat|response|completion|prediction|model_answer|answer|judg|rationale|reasoning|verdict|reply|explanation).*)$", re.I)
SECRET_PATH = re.compile(r"(secret|credential|password|passwd|\.env|apikey|api_key|token|private_key|\.pem|\.key$|keys?\.json)", re.I)
SECRET_TXT = re.compile(r"(sk-[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|xox[bp]-|-----BEGIN [A-Z ]*PRIVATE KEY)")


def raw_url(src, path):
    kind, rest = src
    if kind == "gh":
        o, r = rest.split("/", 1)
        return f"https://raw.githubusercontent.com/{o}/{r}/HEAD/{urllib.parse.quote(path)}"
    if kind == "hf":
        return f"https://huggingface.co/{rest[0]}/{rest[1]}/resolve/main/{urllib.parse.quote(path)}"
    return f"https://zenodo.org/records/{rest}/files/{urllib.parse.quote(path)}?download=1"


def fetch_head(url, n=4096):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": f"bytes=0-{n-1}"})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read(n)
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:
        return 0, b""


def parse_prefixed(pf):
    """'gh:o/r:path' | 'hf:datasets/o/r:path' | 'zenodo:id:path' -> (src, path)"""
    kind, rest = pf.split(":", 1)
    key, path = rest.split(":", 1)
    if kind == "hf":
        k, o, r = key.split("/", 2)
        return ("hf", (k, f"{o}/{r}")), path
    return (kind, key), path


def check_outputs(files):
    """Open first KB of up to 3 accepted jsonl/json/csv files. Return (verdict, text) where verdict in yes/no/unreadable."""
    tried = []
    cands = [f for f in files if re.search(r"\.(jsonl|json|csv|tsv)$", f, re.I)]
    if not cands:
        return "unreadable", "only parquet/compressed/other formats; not opened"
    for pf in cands[:3]:
        src, path = parse_prefixed(pf)
        if SECRET_PATH.search(path):
            tried.append(f"{path}: skipped (credential-like name)")
            continue
        if src[0] == "hf":
            pre = "datasets/" if src[1][0] == "datasets" else ""
            url = f"https://huggingface.co/{pre}{src[1][1]}/resolve/main/{urllib.parse.quote(path)}"
        else:
            url = raw_url(src, path)
        st, b = fetch_head(url)
        if st not in (200, 206) or not b:
            tried.append(f"{path}: http {st}")
            continue
        txt = b.decode("utf-8", "replace")
        if SECRET_TXT.search(txt):
            tried.append(f"{path}: sample held a token-like string; discarded unread")
            continue
        if txt.startswith("version https://git-lfs"):
            tried.append(f"{path}: git-lfs pointer, content not served")
            continue
        base = path.lower()
        if base.endswith((".csv", ".tsv")):
            import csv, io
            first = txt.split("\n")[0]
            try:
                hdr = next(csv.reader(io.StringIO(first), delimiter="," if base.endswith(".csv") else "\t"))
                rows = list(csv.reader(io.StringIO(txt.rsplit("\n", 1)[0] if "\n" in txt else txt), delimiter="," if base.endswith(".csv") else "\t"))
            except Exception:
                tried.append(f"{path}: csv unparsable")
                continue
            ocols = [i for i, h in enumerate(hdr) if OUT_KEY.match(h or "")]
            lens = [len(r[i]) for r in rows[1:4] for i in ocols if i < len(r)]
            if ocols and lens and max(lens) >= 20:
                return "yes", f"{path}: csv columns {hdr[:8]}; output column '{hdr[ocols[0]]}' holds text up to {max(lens)} chars in first rows"
            tried.append(f"{path}: csv cols {hdr[:8]} no output-like text column")
            continue
        found = {}
        for m in re.finditer(r'"([^"\\]{1,40})"\s*:\s*"((?:[^"\\]|\\.){20,})', txt):
            if OUT_KEY.match(m.group(1)):
                found.setdefault(m.group(1), len(m.group(2)))
        keys = sorted(set(re.findall(r'"([^"\\]{1,40})"\s*:', txt)))[:10]
        if found:
            k = next(iter(found))
            return "yes", f"{path}: json keys {keys}; '{k}' holds text (>= {found[k]} chars) in first records"
        tried.append(f"{path}: json keys {keys} no output-like text field")
    return "no", "; ".join(tried)[:400]


def gh_tree(owner, repo):
    try:
        r = subprocess.run(["gh", "api", f"repos/{owner}/{repo}/git/trees/HEAD?recursive=1"],
                           capture_output=True, text=True, timeout=60)
    except Exception as e:
        return None, f"gh error {e}"
    if r.returncode != 0:
        msg = (r.stdout + r.stderr)[:120]
        return None, "gh " + ("not found" if "404" in msg or "Not Found" in msg else "fail: " + msg.strip())
    try:
        j = json.loads(r.stdout)
    except Exception:
        return None, "gh bad json"
    paths = [t["path"] for t in j.get("tree", []) if t.get("type") == "blob"]
    return (paths, "truncated" if j.get("truncated") else "ok"), None


def hf_tree(kind, owner, repo):
    url = f"https://huggingface.co/api/{kind}/{owner}/{repo}/tree/main?recursive=true"
    st, body = http_get(url, "hf", 0.4)
    if st != 200:
        return None, f"hf http {st}"
    try:
        j = json.loads(body)
    except Exception:
        return None, "hf bad json"
    return ([t["path"] for t in j if t.get("type") == "file"], "ok"), None


def zenodo_files(rid):
    st, body = http_get(f"https://zenodo.org/api/records/{rid}", "zenodo", 1.0)
    if st != 200:
        return None, f"zenodo http {st}"
    try:
        j = json.loads(body)
        files = j.get("files") or []
        if isinstance(files, dict):
            files = files.get("entries", [])
            names = list(files.keys()) if isinstance(files, dict) else []
        else:
            names = [f.get("key") or f.get("filename") or "" for f in files]
    except Exception:
        return None, "zenodo bad json"
    return (names, "ok"), None


def check_release(links):
    out_kw, out_other, errs, used = [], [], [], []
    for key, meta in links.items():
        kind = meta["kind"]
        if kind == "gh":
            o, r = key.split("/", 1)
            res, err = gh_tree(o, r)
            pre = f"gh:{key}:"
        elif kind.startswith("hf_"):
            o, r = key.split("/", 1)
            res, err = hf_tree(kind[3:], o, r)
            if err and kind == "hf_models":  # bare huggingface.co/x/y may be a dataset
                pass
            pre = f"hf:{kind[3:]}/{key}:"
        else:
            res, err = zenodo_files(key)
            pre = f"zenodo:{key}:"
        if err:
            errs.append(f"{key}: {err}")
            continue
        paths, note = res
        kw, other = classify_files(paths)
        used.append(key)
        out_kw += [pre + p for p in kw]
        out_other += [pre + p for p in other]
        if note == "truncated":
            errs.append(f"{key}: tree truncated, count is a floor")
    return out_kw, out_other, errs, used


# ---------- step 3: language ----------
EN_STOP = set("the of and to in a is for we on that with as are this by from an be our can it which".split())


def looks_english(title, abstract, comment):
    txt = (title + " " + abstract).lower()
    words = re.findall(r"[a-z]+", txt)
    if len(words) < 20:
        return None
    ratio = sum(w in EN_STOP for w in words) / len(words)
    nonascii = sum(ord(c) > 127 for c in txt) / max(1, len(txt))
    if re.search(r"\b(in|written in)\s+(chinese|japanese|korean|russian|german|french|spanish|portuguese)\b.*\bpaper\b", comment.lower()):
        return False
    if re.search(r"(in chinese|chinese version|in german|in french|in spanish|in portuguese|in russian)", comment.lower()):
        return False
    return ratio > 0.18 and nonascii < 0.05


# ---------- step 4: funding ----------
ACK_HEAD = re.compile(r"^\s*(?:[A-Z]?\d*\.?\s*)?(acknowledg?e?ments?|acknowledgement|funding|funding and acknowledgm?ents?|funding statement|financial support|support|disclosure of funding|sources of funding)\s*:?\s*$", re.I)
NEXT_HEAD = re.compile(r"^\s*(?:[A-Z]|\d+(\.\d+)*)?\.?\s*(references|bibliography|appendix|appendices|limitations|ethics statement|ethical considerations|broader impacts?|impact statement|reproducibility( statement)?|author contributions?|supplementary|a\s+[A-Z][a-z]+)\b.*$", re.I)

FUNDERS = [  # owner rule 11 Nov 2026: drop defence, military and intelligence funders only; civilian science funders are kept
    (r"\bDARPA\b|Defen[cs]e Advanced Research", "DARPA"), (r"\bIARPA\b|Intelligence Advanced Research", "IARPA"),
    (r"\bDoD\b|Department of Defen[cs]e|Department of War\b|\bOSD\b|Defen[cs]e Innovation Unit|\bDIU\b", "DoD"),
    (r"\bONR\b|Office of Naval Research|Naval Research Lab|Naval (Air|Sea|Surface|Undersea)|\bNRL\b", "ONR/Navy"),
    (r"\bAFOSR\b|Air Force Office of Scientific", "AFOSR"), (r"\bAFRL\b|Air Force Research", "AFRL"),
    (r"\bARL\b|Army Research (Laboratory|Lab|Office)|\bDEVCOM\b", "ARL/ARO"), (r"\bARO\b(?! ?[a-z])", "ARO"),
    (r"\bNSA\b|National Security Agency|\bNGA\b|National Geospatial-Intelligence|\bDIA\b|Defen[cs]e Intelligence Agency", "NSA/intelligence"),
    (r"\bODNI\b|\bCIA\b|Intelligence Community|Office of the Director of National Intelligence|\bIC Postdoctoral", "intelligence"),
    (r"\bNNSA\b|National Nuclear Security|Sandia|Los Alamos|Lawrence Livermore", "NNSA weapons lab"),
    (r"\bU\.?S\.? (Army|Navy|Air Force|Space Force|Marine)\b|\bArmy (Contract|Grant|Research)|\bNavy (Contract|Grant)|\bAir Force (Contract|Grant)|\bSpace Force\b", "Army/Navy/Air Force"),
    (r"Ministry of Defen[cs]e|\bMoD\b|armasuisse|\bDSTL\b|Defen[cs]e Science and Technology|\bADF\b|Australian Defen[cs]e|Defen[cs]e Science|Israel(i)? (Ministry of )?Defen[cs]e|\bIDF\b|\bIMOD\b|\bDGA\b|Direction G.n.rale de l.Armement|Bundeswehr|\bBAAINBw\b|\bDRDO\b|\bDRDC\b|Defen[cs]e Research and Development|European Defen[cs]e Fund|\bEDF\b|\bADA\b|\bKAIST.{0,20}defen|Agency for Defense Development|\bNATO\b|Dutch Ministry of Defen[cs]e|Swedish Armed Forces|\bFOI\b|\bFFI\b|Norwegian Defen[cs]e|Chief Scientific Adviser.{0,20}Defen|\bNCIA\b",
     "defence/military"),
]
FUNDER_RE = [(re.compile(p), n) for p, n in FUNDERS]


def find_ack(text):
    lines = [l.strip() for l in text.split("\n")]
    start = None
    for i, l in enumerate(lines):
        if len(l) < 70 and ACK_HEAD.match(l):
            start = i
    if start is None:
        # inline "Acknowledgments. text" style
        m = re.search(r"\n\s*(Acknowledg\w*|Funding)[.:]\s+(.{40,1500})", text, re.I | re.S)
        if m:
            return m.group(2)
        return None
    buf = []
    for l in lines[start + 1:start + 40]:
        if not l:
            continue
        if len(l) < 60 and NEXT_HEAD.match(l) and buf:
            break
        buf.append(l)
        if sum(len(x) for x in buf) > 2500:
            break
    return " ".join(buf) if buf else None


def funder_screen(ack):
    hits = []
    for rx, name in FUNDER_RE:
        m = rx.search(ack)
        if m:
            hits.append(f"{name} ('{m.group(0)}')")
    return hits


# ---------- step 5: companies ----------
VENDORS = re.compile(r"\b(openai|google|deepmind|anthropic|meta ai|meta platforms|facebook|fair\b|microsoft|amazon|aws|apple|nvidia|xai|x\.ai|mistral|cohere|alibaba|qwen|baidu|bytedance|tencent|deepseek)\b|^meta$|, meta\b|\bmeta,", re.I)
COMPANY = re.compile(r"\b(inc\.?|ltd\.?|llc|corp\.?|corporation|gmbh|co\.|company|technologies|technology co|labs?\b(?<!laboratory)|ai$|startup|samsung|huawei|ibm|intel|adobe|salesforce|snap|bloomberg|jpmorgan|j\.p\. morgan|bosch|siemens|sony|ntt|naver|kakao|lg ai|toyota|nec|hitachi|fujitsu|cisco|oracle|uber|netflix|spotify|twitter|linkedin|zhipu|moonshot|minimax|sensetime|xiaomi|meituan|huggingface|hugging face|together ai|scale ai|databricks|snowflake|perplexity|stability ai|ai21|allen institute|ai2\b|sakana|preferred networks|cyberagent|rakuten|line corp|shanghai ai lab|01\.ai|stepfun|ant group|jd\.com|kuaishou|didi|iflytek|sea ai|grab|shopee|lenovo|dell|hp\b|vmware|qualcomm|arm\b|amd\b|wix|booking|zalando|ebay|paypal|stripe|airbnb|walmart|capital one|morgan stanley|goldman|ubs|deutsche bank|bbva|santander|mckinsey|accenture|deloitte|pwc|kpmg|ernst|capgemini|thoughtworks|elevenlabs|runway|midjourney|character\.ai|inflection|reka|writer|glean|harvey|replit|cursor|cognition|scaleai|surge ai|labelbox|appen|prolific|mturk|surveymonkey)", re.I)
ACADEMIC = re.compile(r"(universit|universid|université|università|universität|hochschule|college|institut|school of|academy|polytechnic|\beth\b|\bepfl\b|\bmit\b|caltech|\bmila\b|max planck|riken|cnrs|inria|kaist|a\*star|vector institute|national lab|department of|faculty|cs dept|computer science|center for|centre for|laborator|research center|hospital|medical|clinic|school|tsinghua|peking|fudan|zhejiang|sjtu|ucl|oxford|cambridge|stanford|berkeley|cmu|carnegie|ucla|ucsd|nyu|cornell|princeton|harvard|yale|columbia|uiuc|uw\b|tu\s?(munich|darmstadt|berlin|wien|delft)|technion|weizmann|iit\b|iiit|nus\b|ntu\b|hkust|cuhk|hku\b|kth|epfl|chinese academy|cas\b|iisc|tata institute|nlp group|lab at|foundation|nonprofit|non-profit|society|council|cohere for ai|eleutherai|ai2|allen institute)", re.I)
# Allen Institute / EleutherAI / Cohere for AI / Hugging Face are non-profit or ambiguous: treated as unknown for review below.
AMBIG = re.compile(r"(allen institute|ai2\b|eleutherai|cohere for ai|hugging ?face|foundation|non-?profit|society|council|alan turing|mila|vector institute|ai singapore|shanghai ai lab|beijing academy|zhipu|baai|riken|a\*star|national lab)", re.I)


def classify_aff(a):
    if VENDORS.search(a):
        return "vendor"
    if AMBIG.search(a):
        return "ambiguous"
    if ACADEMIC.search(a) and not COMPANY.search(a):
        return "academic"
    if COMPANY.search(a) and not re.search(r"universit|institut|college|school", a, re.I):
        return "company"
    if ACADEMIC.search(a):
        return "ambiguous"
    return "unknown"


# ---------- screening one paper ----------
SCREEN_V = 3
LLM_RE = re.compile(r"\b(LLMs?|large language models?|language models?|LMs?|GPT-?\d\S*|ChatGPT|Llama\S*|Qwen\S*|Mistral|Mixtral|Gemma\S*|Claude|Gemini|DeepSeek\S*|Phi-\d|OLMo|chatbots?|instruction-tuned|MLLMs?|VLMs?|vision-language models?|reasoning models?|foundation models?|frontier models?|AI assistants?)\b", re.I)
EVAL_RE = re.compile(r"(evaluat|benchmark|assess|judge|judging|audit|red[- ]?team|leaderboard|hallucinat|robustness|probe|probing|measur|test(s|ed|ing) (of|on)|compar)", re.I)
HCACHE = os.path.join(CACHE, "html")
os.makedirs(HCACHE, exist_ok=True)


def screen(c):
    aid = c["arxiv_id"]
    fn = os.path.join(PCACHE, aid.replace("/", "_") + ".json")
    if os.path.exists(fn):
        old = json.load(open(fn))
        if old.get("v") == SCREEN_V and "funder_hits" not in old:  # funder drops re-run under the 11 Nov rule
            return old
    rec = {"v": SCREEN_V, "id": c["id"], "arxiv_id": aid, "title": c["title"], "submitted": c["submitted"],
           "authors": c["authors"], "version": c["version"], "comment": c["comment"]}
    # language
    en = looks_english(c["title"], c["abstract"], c["comment"])
    rec["english"] = en
    if en is False:
        rec["verdict"] = {"bucket": "dropped", "reason": "NOT_ENGLISH"}
        json.dump(rec, open(fn, "w"))
        return rec
    # LLM + evaluation gate (title/abstract)
    ta = c["title"] + " " + c["abstract"]
    if not (LLM_RE.search(ta) and EVAL_RE.search(ta)):
        rec["verdict"] = {"bucket": "dropped", "reason": "NOT_LLM_EVAL (title/abstract names no LLM or no evaluation)"}
        json.dump(rec, open(fn, "w"))
        return rec
    # full text (cached as gz)
    import gzip
    hfn = os.path.join(HCACHE, aid.replace("/", "_") + ".json.gz")
    if os.path.exists(hfn):
        hj = json.load(gzip.open(hfn, "rt"))
        st, text, affs = hj["st"], hj["text"], hj["affs"]
    else:
        st, html = http_get(f"https://arxiv.org/html/{c['id']}", "arxiv-html", 2.0, timeout=60)
        text, affs = ("", [])
        if st == 200 and html:
            text, affs = html_to_text(html)
        with gzip.open(hfn, "wt") as f:
            json.dump({"st": st, "text": text, "affs": affs}, f)
    rec["html_status"] = st
    rec["full_text_chars"] = len(text)
    links = pick_links(c["abstract"], c["comment"], text)
    rec["link_candidates"] = {k: v for k, v in links.items()}
    if not links:
        rec["verdict"] = {"bucket": "dropped", "reason": "NO_RELEASE_LINK" + ("" if text else " (no full text, abstract/comment only)")}
        json.dump(rec, open(fn, "w"))
        return rec
    kw, other, errs, used = check_release(links)
    rec["release_errors"] = errs
    rec["links_checked"] = used
    rec["output_files_all"] = len(kw)
    if not kw:
        if other:
            rec["other_data_files"] = other[:20]
            rec["verdict"] = {"bucket": "dropped", "reason": f"NO_MODEL_OUTPUT_FILES (data files present, none pass the model-name/per-model-folder test; {len(other)} rejected)"}
        elif not used:
            rec["verdict"] = {"bucket": "needs_review", "reason": "release links found but none could be listed: " + "; ".join(errs)[:200]}
        else:
            rec["verdict"] = {"bucket": "dropped", "reason": "NO_OUTPUT_FILES (links listed, no per-item data files)"}
        json.dump(rec, open(fn, "w"))
        return rec
    rec["output_files"] = kw[:20]
    rec["n_output_files"] = len(kw)
    # funding
    if not text:
        rec["verdict"] = {"bucket": "needs_review", "reason": "outputs released but no arXiv HTML full text; acknowledgments and affiliations unread"}
        json.dump(rec, open(fn, "w"))
        return rec
    ack = find_ack(text)
    if ack is None:
        rec["ack_read"] = "no acknowledgments section found"
    else:
        rec["ack_read"] = ack[:400]
        hits = funder_screen(ack)
        if hits:
            rec["funder_hits"] = hits
            rec["verdict"] = {"bucket": "dropped", "reason": "DROPPED_FUNDER: " + "; ".join(hits)[:300]}
            json.dump(rec, open(fn, "w"))
            return rec
    # outputs_checked: open the first KB of listed files
    oc, desc = check_outputs(kw)
    if oc == "yes":
        rec["outputs_checked"] = "yes, " + desc
    elif oc == "no":
        rec["outputs_checked"] = "no, " + desc
        rec["verdict"] = {"bucket": "dropped", "reason": "OUTPUTS_NOT_CONFIRMED: " + desc[:250]}
        json.dump(rec, open(fn, "w"))
        return rec
    else:
        rec["outputs_checked"] = "not checked, " + desc
        rec["verdict"] = {"bucket": "needs_review", "reason": "outputs_checked unreadable: " + desc[:250]}
        json.dump(rec, open(fn, "w"))
        return rec
    # affiliations
    rec["affiliations"] = affs[:12]
    if not affs:
        rec["verdict"] = {"bucket": "needs_review", "reason": "outputs released, funder clear, but no affiliations parsed from HTML"}
        json.dump(rec, open(fn, "w"))
        return rec
    classes = [(a, classify_aff(a)) for a in affs]
    rec["aff_classes"] = classes
    kinds = {k for _, k in classes}
    if "vendor" in kinds:
        rec["verdict"] = {"bucket": "MATRIX_ONLY_COMPANY", "vendor": True}
    elif "company" in kinds:
        rec["verdict"] = {"bucket": "MATRIX_ONLY_COMPANY", "vendor": False}
    elif kinds <= {"academic"}:
        rec["verdict"] = {"bucket": "INDEXED"}
    else:
        amb = [a for a, k in classes if k in ("ambiguous", "unknown")]
        rec["verdict"] = {"bucket": "needs_review", "reason": "affiliation not classifiable as university or company: " + " | ".join(amb)[:300]}
    json.dump(rec, open(fn, "w"))
    return rec


def norm_id(s):
    s = s.strip()
    s = re.sub(r"^arxiv[-:]", "", s, flags=re.I)
    return re.sub(r"v\d+$", "", s)


def main():
    maxscreen = None
    if "--max-screen" in sys.argv:
        maxscreen = int(sys.argv[sys.argv.index("--max-screen") + 1])
    refresh = "--refresh-queries" in sys.argv
    skip = set()
    try:
        for r in json.load(open(SCAN)):
            skip.add(norm_id(r["id"]))
    except Exception as e:
        print("warn: SCAN_register unreadable", e)
    try:
        for i in json.load(open(REMOVED)).get("ids", []):
            skip.add(norm_id(i))
    except Exception as e:
        print("warn: removed_at_request unreadable", e)
    cands = gather_candidates(refresh)
    todo = [c for k, c in cands.items() if norm_id(k) not in skip]
    print(f"[sweep] candidates={len(cands)} skipped(existing/removed)={len(cands)-len(todo)} to_screen={len(todo)}", flush=True)
    todo.sort(key=lambda c: c["submitted"], reverse=True)
    recs, n = [], 0
    for c in todo:
        fnc = os.path.join(PCACHE, c["arxiv_id"].replace("/", "_") + ".json")
        try:
            cached = os.path.exists(fnc) and (lambda o: o.get("v") == SCREEN_V and "funder_hits" not in o)(json.load(open(fnc)))
        except Exception:
            cached = False
        if maxscreen is not None and n >= maxscreen and not cached:
            continue
        try:
            rec = screen(c)
        except Exception as e:
            rec = {"id": c["id"], "arxiv_id": c["arxiv_id"], "title": c["title"], "submitted": c["submitted"],
                   "verdict": {"bucket": "needs_review", "reason": f"screen error: {type(e).__name__}: {e}"[:200]}}
        recs.append(rec)
        if not cached:
            n += 1
            if n % 20 == 0:
                print(f"[screen] {n} new, {len(recs)} total; last={rec['verdict']}", flush=True)
                write_outputs(recs, len(cands), len(skip))
    write_outputs(recs, len(cands), len(skip))
    print("[sweep] done", flush=True)


def write_outputs(recs, ncands, nskip):
    rows, dropped, review = [], [], []
    for r in recs:
        v = r["verdict"]
        b = v["bucket"]
        if b in ("INDEXED", "MATRIX_ONLY_COMPANY"):
            links = []
            for k in r.get("links_checked", []):
                meta = r["link_candidates"].get(k, {})
                kind = meta.get("kind", "")
                links.append(f"https://github.com/{k}" if kind == "gh" else f"https://huggingface.co/{'datasets/' if kind == 'hf_datasets' else ''}{k}" if kind.startswith("hf_") else f"https://zenodo.org/records/{k}")
            row = {"id": r["id"], "title": r["title"], "submitted": r["submitted"], "links": links,
                   "status": b, "authors_affil": "; ".join(r.get("affiliations", []))[:300],
                   "ack_read": r.get("ack_read", ""), "output_files": r.get("output_files", []),
                   "n_output_files": r.get("n_output_files", 0), "outputs_checked": r.get("outputs_checked", ""), "swept": TODAY,
                   "link_sources": sorted({r["link_candidates"][k]["src"] for k in r.get("links_checked", []) if k in r["link_candidates"]}),
                   "seat": "sweep (automatic; not hand-read)"}
            if b == "MATRIX_ONLY_COMPANY":
                row["vendor"] = bool(v.get("vendor"))
            rows.append(row)
        elif b == "dropped":
            reason = v["reason"]
            dropped.append({"id": r["id"], "title": r["title"], "reason": reason,
                            "status": "DROPPED_FUNDER" if reason.startswith("DROPPED_FUNDER") else "OFF"})
        else:
            review.append({"id": r["id"], "title": r["title"], "reason": v["reason"], "submitted": r.get("submitted"),
                           "links": r.get("links_checked", []), "n_output_files": r.get("n_output_files", 0)})
    json.dump({"generated": TODAY, "rows": rows, "dropped": dropped, "needs_review": review},
              open(os.path.join(HERE, "sweep_rows.json"), "w"), indent=1)
    from collections import Counter
    sc = Counter(x["status"] for x in rows)
    dc = Counter(re.split(r"[:( ]", x["reason"])[0] if not x["reason"].startswith("DROPPED_FUNDER") else "DROPPED_FUNDER" for x in dropped)
    fc = Counter()
    for x in dropped:
        if x["reason"].startswith("DROPPED_FUNDER"):
            for part in x["reason"][16:].split("; "):
                fc[part.split(" (")[0]] += 1
    rc = Counter(re.split(r"[:(;]", x["reason"])[0].strip()[:90] for x in review)
    vend = sum(1 for x in rows if x.get("vendor"))
    L = [f"# IRIS sweep report, {TODAY}", "",
         f"Candidates from arXiv: {ncands}. Skipped (already in SCAN_register or removed at request): {nskip} ids on skip list.",
         f"Screened: {len(recs)}.", "",
         "## Counts by status"]
    for k, v in sc.items():
        L.append(f"- {k}: {v}")
    L.append(f"- (of MATRIX_ONLY_COMPANY, vendor-authored: {vend})")
    L.append(f"- rows with outputs_checked = yes: {sum(1 for x in rows if x.get('outputs_checked','').startswith('yes'))}")
    L.append(f"- dropped total: {len(dropped)}")
    L.append(f"- needs_review: {len(review)}")
    L.append(f"- rows that would be listed (INDEXED + MATRIX_ONLY_COMPANY): {len(rows)}")
    L += ["", "## Dropped by reason"] + [f"- {k}: {v}" for k, v in dc.most_common()]
    L += ["", "## DROPPED_FUNDER by funder class (a paper can hit several)"] + [f"- {k}: {v}" for k, v in fc.most_common()]
    L += ["", "## needs_review by reason"] + [f"- {k}: {v}" for k, v in rc.most_common()]
    L += ["", "## Rules not applied automatically",
          "- Acknowledgments are read only from arXiv HTML (pdftotext is not installed, so there is no PDF fallback). Funding that sits only in a first-page footnote is not seen.",
          "- 'Per-item outputs': accepted files need a model name in the path (or an output word inside a per-model folder); then the first 4 KB of up to 3 jsonl/json/csv files are read for an output-like text field. Parquet is never opened (needs_review). A heuristic key match is not proof the text is model text. Repos linked from full text count only when release language sits within ~200 characters of the link.",
          "- Affiliation class (university / company / vendor) is keyword based. Anything ambiguous goes to needs_review.",
          "- Language is a stop-word heuristic on title and abstract.",
          "- Funder matching is a keyword list over the ack text; a generic mention (for example 'EU') can over-drop and a funder written in an unusual way can slip through. Every row is flagged 'not hand-read'."]
    open(os.path.join(HERE, "SWEEP_REPORT.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
