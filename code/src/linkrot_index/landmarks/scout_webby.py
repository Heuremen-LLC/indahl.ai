#!/usr/bin/env python3
"""scout_webby.py: builds the list of Webby Award winners for ceremony years 1997 to 2008, each with the website address
the Webby Awards printed for it. It writes data/landmarks/frame_webby.json, a list of {year, award, category, name, url,
source}, plus frame_webby_detail.json (same rows, more fields), frame_webby_noaddress.json (winners with no usable address)
and frame_webby_report.json (counts per year and page). Run it with python3 -I; --offline reads the cache only.

Sources: only pages of webbyawards.com as archived by the Wayback Machine (web.archive.org, raw id_ form), pinned in
SOURCES by exact URL and capture time and cached under data/landmarks/cache_webby/, so a rerun fetches nothing. The current
winners archive (winners.webbyawards.com) is not used: it is a script-rendered app whose data calls sit under /api/, which
its robots.txt disallows, and its sitemap lists person profiles only. The script refuses every host except archive.org and
webbyawards.com (no winner's own site is ever requested), waits 3.2 s between archive.org requests and 1.2 s between
webbyawards.com requests, sends the user agent HeuremenLLC-linkrot/1.0, backs off 60 s after a 429 or 5xx, and stops for
5 minutes after any connection failure (kept in a small state file, so the next run honours it). The robots.txt of
webbyawards.com is read before any live request to it.

Pages by year (capture time in brackets). 1997, 1998: the 1999 "Best - Archives" page of that year (winner starred) and the
"Winners List" (Jul 2001, Oct 2002). 1999: arch_noms_1999 (Jul 2001) and the Winners List. 2000: the Winners List. 2001:
the awards-event winners page (20 Jul 2001), nominees.html and the Winners List (Aug 2001). 2002: the Winners List (Oct
2002), nominees.html (Feb 2003), arch_noms_2002 (Apr 2004). 2003: main/event/winners.html and main/webby_awards/winners.html
(8 Jun 2003), nominees.html (Aug 2003), the Winners List (Dec 2003). 2004: nominees.html and the Winners List (5 Jun 2004).
2005 to 2008: the "Nominees & Winners" page of the year (current.php: 13 May and 1 Jun 2005; 12 Jun 2006; 3 May 2007 and
10-12 Jun 2008, one page per medium in those two years).

Rule. Only entries the page itself labels as winners are read: "Webby Award Winner" gives award Webby, "People's Voice
Winner" gives People's Voice; on the Winners List the sections "YYYY Webby Award Winners" and "YYYY People's Voice Winners";
on the 1999 archive pages the starred entry; on the 2001 event page the left column (Webby) and the right column (People's
Voice). Nominees, honorees and special-achievement lines are never read. url is the target of the winner's link (the
argument of winLaunch() when the link is a script call), else the printed text. The winners of a year are the union of its
pinned pages in capture order: two entries are the same winner when award and (name or address) agree, and the earliest
page that lists a winner supplies its category, name, address and source. A winner without an address, or whose link points
to webbyawards.com, goes to frame_webby_noaddress.json and not into frame_webby.json.
"""
import fcntl
import gzip
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

UA = "HeuremenLLC-linkrot/1.0 (https://indahl.ai)"
BASE = "/Users/heuremen/bones-forge/linkrot_index"
DATA = BASE + "/data/landmarks"
CACHE = DATA + "/cache_webby"
OUT = DATA + "/frame_webby.json"
OUT_DETAIL = DATA + "/frame_webby_detail.json"
OUT_NOADDR = DATA + "/frame_webby_noaddress.json"
OUT_REPORT = DATA + "/frame_webby_report.json"
RATE_STATE = DATA + "/.scout_webby_ratelimit.json"
RATE_LOCK = DATA + "/.scout_webby_ratelimit.lock"
GAP = {"archive.org": 3.2, "webbyawards.com": 1.2}   # seconds between requests to one host family
BACKOFF = 60        # seconds to wait after a 429 or 5xx answer
FAIL_PAUSE = 300    # seconds to stay away after a connection failure
MAX_TRIES = 3
OFFLINE = False


class Paused(RuntimeError):
    """A host is on hold (connection failure or a pause marker): stop, do not retry now."""


class NotCached(RuntimeError):
    """Offline run and the page is not in the cache."""


# ---------------------------------------------------------------------------------------------
# network layer: only archive.org and webbyawards.com, paced, cached
# ---------------------------------------------------------------------------------------------
def bucket_for(url):
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host == "archive.org" or host.endswith(".archive.org"):
        return "archive.org"
    if host == "webbyawards.com" or host.endswith(".webbyawards.com"):
        return "webbyawards.com"
    raise RuntimeError("refused: host not allowed: " + host)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _state_load():
    try:
        return json.load(open(RATE_STATE))
    except Exception:
        return {}


def _acquire(bucket):
    """Take the shared lock, refuse if the host is on hold, otherwise wait out the gap since its last request."""
    os.makedirs(DATA, exist_ok=True)
    lock = open(RATE_LOCK, "a+")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        state = _state_load()
        until = state.get(bucket + "_pause_until", 0)
        if until > time.time():
            raise Paused("%s is on hold until %s" % (bucket, time.strftime("%H:%M:%S", time.localtime(until))))
        wait = state.get(bucket, 0) + GAP[bucket] - time.time()
        if wait > 0:
            time.sleep(wait)
        return lock
    except BaseException:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
        raise


def _release(bucket, lock, hold=0):
    try:
        state = _state_load()
        state[bucket] = time.time()
        if hold:
            state[bucket + "_pause_until"] = time.time() + hold
        with open(RATE_STATE, "w") as f:
            json.dump(state, f)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


_ROBOTS = {}


def robots_ok(url):
    """webbyawards.com only: read its robots.txt once per run (cached for a day) and ask it."""
    host = urllib.parse.urlsplit(url).netloc.lower()
    if host not in _ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        path = os.path.join(CACHE, "robots_" + host.replace(":", "_") + ".txt")
        text = None
        if os.path.exists(path) and time.time() - os.path.getmtime(path) < 86400:
            text = open(path).read()
        if text is None:
            status, body, _, _ = http_get("https://%s/robots.txt" % host, check_robots=False)
            if status == 200:
                text = decode(body)
                os.makedirs(CACHE, exist_ok=True)
                open(path, "w").write(text)
            elif status in (401, 403):
                rp.disallow_all = True
            elif 400 <= status < 500:
                rp.allow_all = True
            else:
                rp.disallow_all = True
        if text is not None:
            rp.parse(text.splitlines())
        _ROBOTS[host] = rp
    return _ROBOTS[host].can_fetch(UA, url)


def http_get(url, timeout=90, max_hops=6, check_robots=True):
    """One GET with the study's user agent. Redirects are followed by hand, each hop paced and host-checked.
    Returns (status, body, headers, final_url). Raises Paused after a connection failure."""
    if OFFLINE:
        raise NotCached(url)
    cur, hops, tries = url, 0, 0
    while True:
        bucket = bucket_for(cur)
        if bucket == "webbyawards.com" and check_robots and not robots_ok(cur):
            raise RuntimeError("robots.txt of webbyawards.com does not allow " + cur)
        lock = _acquire(bucket)
        status, body, headers, failed = None, b"", None, False
        try:
            req = urllib.request.Request(cur, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip, identity"})
            try:
                resp = _OPENER.open(req, timeout=timeout)
                status, body, headers = resp.status, resp.read(), resp.headers
            except urllib.error.HTTPError as e:
                status, body, headers = e.code, e.read(), e.headers
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            failed, body = True, str(e).encode()
        finally:
            _release(bucket, lock, hold=FAIL_PAUSE if failed else 0)
        if failed:
            raise Paused("connection failure on %s (%s): %s held for %d s" % (cur, body.decode("utf-8", "replace")[:80], bucket, FAIL_PAUSE))
        if status in (429, 503) or status >= 500:
            tries += 1
            if tries >= MAX_TRIES:
                return status, body, headers, cur
            sys.stderr.write("  back-off %d s after %s on %s\n" % (BACKOFF, status, cur))
            time.sleep(BACKOFF)
            continue
        if status in (301, 302, 303, 307, 308) and headers is not None and headers.get("Location"):
            hops += 1
            if hops > max_hops:
                return status, body, headers, cur
            cur = urllib.parse.urljoin(cur, headers["Location"])
            continue
        if headers is not None and (headers.get("Content-Encoding") or "").lower() == "gzip":
            try:
                body = gzip.decompress(body)
            except Exception:
                pass
        return status, body, headers, cur


def _cache_name(url):
    """File name for a cached URL: Wayback timestamp (or live), short hash, readable tail."""
    h = hashlib.sha1(url.encode()).hexdigest()[:12]
    m = re.search(r"/web/(\d{14})id_/(.*)$", url)
    stamp, rest = (m.group(1), m.group(2)) if m else ("live", url)
    sp = urllib.parse.urlsplit(rest)
    tail = (sp.path.strip("/") + ("_" + sp.query if sp.query else "")).replace("/", "_")[-70:]
    tail = "".join(c if (c.isalnum() or c in "._-=") else "_" for c in tail)
    return "%s_%s_%s" % (stamp, h, tail)


def fetch_cached(url):
    """Return (status, body_bytes, final_url). Successful (200) fetches are cached and never refetched."""
    os.makedirs(CACHE, exist_ok=True)
    name = _cache_name(url)
    bpath = os.path.join(CACHE, name + ".body")
    mpath = os.path.join(CACHE, name + ".meta.json")
    if os.path.exists(bpath) and os.path.exists(mpath):
        meta = json.load(open(mpath))
        return meta["status"], open(bpath, "rb").read(), meta.get("final_url", url)
    status, body, headers, final = http_get(url)
    if status == 200:
        with open(bpath, "wb") as f:
            f.write(body)
        meta = {"url": url, "final_url": final, "status": status,
                "content_type": (headers.get("Content-Type") if headers is not None else None),
                "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with open(mpath, "w") as f:
            json.dump(meta, f)
    return status, body, final


def cdx(**params):
    """Wayback CDX API (cached). Returns a list of dicts. Used only to look for captures, not by the build."""
    q = {"output": "json"}
    q.update({k: v for k, v in params.items() if v is not None})
    url = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(q, doseq=True)
    status, body, _ = fetch_cached(url)
    if status != 200:
        raise RuntimeError("CDX %s for %s" % (status, url))
    text = body.decode("utf-8", "replace").strip()
    rows = json.loads(text) if text else []
    if not rows:
        return []
    head = rows[0]
    return [dict(zip(head, r)) for r in rows[1:] if len(r) == len(head)]


# ---------------------------------------------------------------------------------------------
# page reading (no network below this line)
# ---------------------------------------------------------------------------------------------
def decode(b):
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass
    return b.decode("latin-1", "replace")


def squash(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def norm(s):
    return squash(s).lower().replace("’", "'").replace("`", "'").rstrip(":")


class Events(HTMLParser):
    """Flatten a page into events in document order:
    ('head', text)  text of an h1-h4 heading     ('bold', text)  text inside b or strong
    ('th', text)    text inside a header cell    ('text', text)  other text outside a link
    ('img', alt, src)  image outside a link      ('cell', tag, attrs)  start of a tr, td or th
    ('a', href, text, alts)  a finished link: href, text, and alt texts of images inside it
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ev, self.skip, self.bold, self.head, self.th = [], 0, 0, 0, 0
        self.a = None
        self.buf = []

    def _flush(self):
        t = squash("".join(self.buf))
        self.buf = []
        if t:
            self.ev.append(("head" if self.head else "bold" if self.bold else "th" if self.th else "text", t))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "a":
            self._flush()
            self.a = {"href": a.get("href") or "", "text": [], "alts": []}
        elif tag == "img":
            alt = squash(a.get("alt") or "")
            if self.a is not None:
                if alt:
                    self.a["alts"].append(alt)
            else:
                self._flush()
                if alt:
                    self.ev.append(("img", alt, a.get("src") or ""))
        elif tag in ("b", "strong"):
            self._flush()
            self.bold += 1
        elif re.fullmatch(r"h[1-4]", tag):
            self._flush()
            self.head += 1
        elif tag in ("br", "p", "div", "li"):
            if self.a is not None:
                self.a["text"].append(" ")
            elif self.head and tag == "br":
                self.buf.append(" ")
            else:
                self._flush()
        elif tag in ("tr", "td", "th"):
            if self.a is None:
                self._flush()
            self.ev.append(("cell", tag, a))
            if tag == "th":
                self.th += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "a":
            if self.a is not None:
                self.ev.append(("a", self.a["href"], squash("".join(self.a["text"])), self.a["alts"]))
                self.a = None
            else:
                self._flush()
        elif tag in ("b", "strong"):
            self._flush()
            self.bold = max(0, self.bold - 1)
        elif re.fullmatch(r"h[1-4]", tag):
            self._flush()
            self.head = max(0, self.head - 1)
        elif tag in ("td", "th", "tr"):
            if self.a is None:
                self._flush()
            if tag == "th":
                self.th = max(0, self.th - 1)

    def handle_data(self, d):
        if self.skip:
            return
        if self.a is not None:
            self.a["text"].append(d)
        else:
            self.buf.append(d)

    def close(self):
        super().close()
        self._flush()


def events(html_text):
    p = Events()
    p.feed(html_text)
    p.close()
    return p.ev


WINLAUNCH = re.compile(r"""winLaunch\(\s*['"]?([^'")]+)""")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
LOOKS_LIKE_ADDRESS = re.compile(r"^(https?://)?([a-z0-9-]+\.)+[a-z]{2,}(:\d+)?(/\S*)?$", re.I)


def link_target(href):
    """The address a link really points to: the argument of javascript:winLaunch('...') if there is one, else the href."""
    m = WINLAUNCH.search(href or "")
    return (m.group(1) if m else (href or "")).strip()


def real_href(h):
    h = (h or "").strip()
    return bool(h) and not h.startswith("#") and not h.lower().startswith(("mailto:", "javascript:void"))


def clean_name(s):
    return squash(s.replace("]]", "").replace("-->", ""))


def row(award, category, name, href, link_text, credit=None, note=None, anomaly=False):
    return {"award": award, "category": category, "name": name, "href": href, "link_text": link_text,
            "credit": credit, "note": note, "anomaly": anomaly}


SECTION = re.compile(r"^(\d{4})\s+(webby\s+awards?|people.?s\s+voice)\s+winners?$", re.I)
NOADDR = re.compile(r"only lives in our cache|no longer (exists|available|online)|site (is )?(gone|closed)|not (currently )?available", re.I)
TEXTY = ("head", "bold", "text", "th", "img")


def parse_winner_list(html_text):
    """The 'Winners List' page: a section per year and award, then category (bold), winner name (text) and address
    (a winLaunch link). Returns (rows by (year), sections seen, number of placeholder rows dropped)."""
    ev = events(html_text)
    rows, sections, dropped = [], [], 0
    year = award = cur = None

    def close():
        nonlocal cur, dropped
        if cur is not None and cur["parts"]:
            r = row(cur["award"], cur["category"], clean_name(" ".join(cur["parts"])), cur["href"], cur["link_text"],
                    note=cur["note"], anomaly=cur["anomaly"])
            r["year"] = cur["year"]
            if cur["internal"]:
                dropped += 1
            else:
                rows.append(r)
        cur = None

    for e in ev:
        kind = e[0]
        if kind in TEXTY:
            m = SECTION.match(squash(e[1]))
            if m:
                close()
                year = int(m.group(1))
                award = "Webby" if m.group(2).lower().startswith("webby") else "People's Voice"
                sections.append((year, award))
                continue
        if year is None:
            continue
        if kind == "bold":
            close()
            cur = {"year": year, "award": award, "category": clean_name(e[1]), "parts": [], "href": None,
                   "link_text": None, "note": None, "anomaly": False, "internal": False}
        elif kind == "text" and cur is not None:
            t = clean_name(e[1])
            if not t or cur["href"] is not None:
                continue            # text after the address is page furniture
            if NOADDR.search(t):
                cur["note"] = t
            elif cur["note"]:
                cur["anomaly"] = True   # more text after a no-address remark: markup is broken, do not trust a later link
            else:
                cur["parts"].append(t)
        elif kind == "a" and cur is not None and cur["parts"] and cur["href"] is None and not cur["note"] and not cur["anomaly"]:
            target = link_target(e[1])
            if real_href(e[1]) and target:
                if SCHEME.match(target) or target.lower().startswith("www."):
                    cur["href"], cur["link_text"] = target, e[2]
                else:
                    cur["internal"] = True      # relative link such as nominees.html: a notice, not a winner
    close()
    return rows, sections, dropped


WIN_LABELS = {
    "webby award winner": "Webby", "webby award winners": "Webby", "webby winner": "Webby", "webby winners": "Webby",
    "people's voice winner": "People's Voice", "people's voice winners": "People's Voice",
    "peoples voice winner": "People's Voice", "peoples voice winners": "People's Voice",
}
STOP_LABELS = {"nominees", "nominee", "official honorees", "honorees", "webby honorees", "webby honoree",
               "webby worthy", "webby worthy selections", "special achievement honorees"}
FOOTER = re.compile(r"^(this site powered by|site developed|\u00a9|copyright|all rights reserved)", re.I)
HEADER_TEXT = re.compile(r"^(agency\s*/?\s*)?(credited\s+)?organi[sz]ations?$|^agency\s*/\s*credited\s+organi[sz]ation$|^credited\s+organi[sz]ation$", re.I)


def parse_season_page(html_text):
    """Pages that show nominees and winners per category (current.php, nominees.html, winners.html, arch_noms_YYYY):
    a block per category with labels Webby Award Winner, People's Voice Winner, Nominees; each entry a name and an
    address link, sometimes a credit. Only entries under a winner label are returned."""
    ev = events(html_text)
    out = []
    cat = mode = pend = None

    def flush():
        nonlocal pend
        if pend is not None and pend["name"]:
            out.append(row(pend["award"], pend["cat"], pend["name"], pend["href"], pend["link_text"],
                           credit=" / ".join(pend["credits"]) or None))
        pend = None

    for e in ev:
        kind = e[0]
        if kind in TEXTY:
            t = squash(e[1])
            n = norm(t)
            if n in WIN_LABELS:
                flush()
                mode = WIN_LABELS[n]
                continue
            if n in STOP_LABELS or FOOTER.match(t):
                flush()
                mode = None
                continue
            if kind == "img":
                src = e[2] if len(e) > 2 else ""
                if "/subhead/" in src and not re.search(r"winner|nominee|pv_|winners_are|th_", src, re.I):
                    flush()
                    mode = None
                    cat = clean_name(t)       # a category heading drawn as an image, not wrapped in a named link
                continue
            if mode is None or not t or HEADER_TEXT.match(t) or n == "back to top":
                continue
            if pend is None or pend["row_closed"]:
                flush()
                pend = {"name": clean_name(t), "credits": [], "href": None, "link_text": None, "row_closed": False,
                        "award": mode, "cat": cat}
            else:
                pend["credits"].append(t)
        elif kind == "a":
            raw, text, alts = e[1], e[2], e[3]
            if not raw.strip() and (text or alts):
                flush()
                mode = None
                cat = clean_name(text or alts[0])
                continue
            if mode is None or pend is None or pend["href"] is not None:
                continue
            if real_href(raw) and link_target(raw):
                pend["href"], pend["link_text"] = link_target(raw), text
        elif kind == "cell" and e[1] == "tr" and pend is not None:
            if pend["href"] is not None:
                flush()
            else:
                pend["row_closed"] = True
    flush()
    return out


def parse_star(html_text):
    """The 1999 'Best - Archives' pages: a heading link without address per category, then the nominees, the winner
    marked by a star in the cell before its name. Returns the starred entries only."""
    ev = events(html_text)
    out = []
    cat = pend = None
    star = False

    def flush():
        nonlocal pend
        if pend is not None and pend["star"] and pend["name"]:
            out.append(row("Webby", pend["cat"], pend["name"], pend["href"], pend["link_text"]))
        pend = None

    for e in ev:
        kind = e[0]
        if kind == "a":
            raw, text = e[1].strip(), e[2]
            if not raw:
                if text and not norm(text).startswith("back to top"):
                    flush()
                    cat = clean_name(text)
                continue
            if pend is not None and pend["href"] is None and not raw.startswith("#") and real_href(raw):
                pend["href"], pend["link_text"] = link_target(raw), text
        elif kind in ("text", "bold", "th", "head"):
            t = squash(e[1])
            if t == "*":
                flush()
                star = True
                continue
            if cat is None or not t or norm(t).startswith(("*indicates", "the best sites", "back to top", "indicates winner")):
                continue
            if pend is None or pend["href"] is not None:
                flush()
                pend = {"name": clean_name(t), "href": None, "link_text": None, "star": star, "cat": cat}
                star = False
            else:
                pend["name"] = clean_name(pend["name"] + " " + t)
    flush()
    return out


def parse_webcast_winners(html_text):
    """The 2001 awards-event 'Winners List' page: a table whose left cells (background bgbar1) hold the Webby Award
    winners and right cells (bgbar3) the People's Voice winners; a cell is bold category, name, address link."""
    ev = events(html_text)
    out = []
    cell = None

    def close():
        nonlocal cell
        if cell and cell["award"] and cell["cat"] and cell["parts"]:
            out.append(row(cell["award"], cell["cat"], clean_name(" ".join(cell["parts"])), cell["href"], cell["link_text"]))
        cell = None

    for e in ev:
        if e[0] == "cell":
            close()
            if e[1] == "td":
                bg = (e[2].get("background") or "").lower()
                cell = {"award": "Webby" if "bgbar1" in bg else "People's Voice" if "bgbar3" in bg else None,
                        "cat": None, "parts": [], "href": None, "link_text": None}
        elif cell is not None and cell["award"]:
            if e[0] == "bold" and cell["cat"] is None:
                cell["cat"] = clean_name(e[1])
            elif e[0] == "a" and not e[1].strip() and cell["cat"] is None and e[2]:
                cell["cat"] = clean_name(e[2])
            elif e[0] == "text" and cell["cat"] and cell["href"] is None:
                cell["parts"].append(clean_name(e[1]))
            elif e[0] == "a" and cell["cat"] and cell["href"] is None and real_href(e[1]) and link_target(e[1]):
                cell["href"], cell["link_text"] = link_target(e[1]), e[2]
    close()
    return out


def page_event_year(html_text):
    m = re.search(r"\d+(?:st|nd|rd|th) Annual Webby Awards Webcast (\d{4})", html_text)
    return int(m.group(1)) if m else None


def page_annual(html_text):
    """The N of the first 'Nth Annual Webby Awards Nominees ...' heading on a page, or None."""
    m = re.search(r"(\d+)(?:st|nd|rd|th)\s+Annual\s+Webby\s+Awards\s+Nominees", html_text, re.I)
    return int(m.group(1)) if m else None


def page_best_sites_year(html_text):
    m = re.search(r"The Best Sites of (\d{4})", html_text)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------------------------
# the pinned pages
# ---------------------------------------------------------------------------------------------
H = "http://www.webbyawards.com:80"
NW = H + "/main/webby_awards/nominees.html"
WL = H + "/main/webby_awards/winner_list.html"
CUR = H + "/webbys/current.php"


def wb(ts, url):
    return "https://web.archive.org/web/%sid_/%s" % (ts, url)


# Not examined (archive.org refused connections on 9 Nov 2026 before these could be read): captures of current.php
# between 28 Apr and 13 May 2005; current.php without a season in Jun 2006; the no-season media_id pages of Apr 2007
# and May 2008; any 2002 awards-event winners page; the per-category winner pages of 1999 and 2000.
# id, parser, years the page is read for, pages [(capture time, original url, media label)], season number check
SOURCES = [
    ("archives-1997", "star", [1997], [("19990508133705", H + "/best/archives/archives1997.html", None)], None),
    ("archives-1998", "star", [1998], [("19990428224838", H + "/best/archives/archives1998.html", None)], None),
    ("arch_noms-1999", "season", [1999], [("20010710051432", H + "/main/webby_awards/arch_noms_1999.html", None)], None),
    ("nominees-2001", "season", [2001], [("20010801150944", NW, None)], None),
    ("winner_list-2001-07", "list", [1997, 1998, 1999, 2000], [("20010711204931", WL, None)], None),
    ("webcast_winners-2001-07", "webcast", [2001], [("20010720113108", H + "/main/webcast/winners.html", None)], None),
    ("winner_list-2001-08", "list", [2001], [("20010801151610", WL, None)], None),
    ("winner_list-2002-10", "list", [1997, 1998, 1999, 2000, 2001, 2002], [("20021014184450", WL, None)], None),
    ("nominees-2003-02", "season", [2002], [("20030206213725", NW, None)], None),
    ("arch_noms-2002", "season", [2002], [("20040426005039", H + "/main/webby_awards/arch_noms_2002.html", None)], None),
    ("event_winners-2003-06", "season", [2003], [("20030608075132", H + "/main/event/winners.html", None)], None),
    ("winners-2003-06", "season", [2003], [("20030608141747", H + "/main/webby_awards/winners.html", None)], None),
    ("nominees-2003-08", "season", [2003], [("20030801074320", NW, None)], None),
    ("winner_list-2003-12", "list", [2003], [("20031203015700", WL, None)], None),
    ("nominees-2004-06", "season", [2004], [("20040605194516", NW, None)], None),
    ("winner_list-2004-06", "list", [2004], [("20040605200822", WL, None)], None),
    ("current-2005-05", "season", [2005], [("20050513211136", CUR, "Websites")], 9),
    ("current-2005-06", "season", [2005], [("20050601015308", CUR, "Websites")], 9),
    ("current-2006", "season", [2006], [("20060612205727", CUR + "?season=10", "Websites")], 10),
    ("current-2007", "season", [2007], [
        ("20070503011046", CUR + "?media_id=96&season=11", "Websites"),
        ("20070503011110", CUR + "?media_id=98&season=11", "Interactive Advertising"),
        ("20070503011002", CUR + "?media_id=97&season=11", "Online Film & Video"),
        ("20070503011123", CUR + "?media_id=127&season=11", "Mobile")], 11),
    ("current-2008", "season", [2008], [
        ("20080610074942", CUR + "?media_id=96&season=12", "Websites"),
        ("20080610074952", CUR + "?media_id=98&season=12", "Interactive Advertising"),
        ("20080610074948", CUR + "?media_id=97&season=12", "Online Film & Video"),
        ("20080612201137", CUR + "?media_id=127&season=12", "Mobile")], 12),
]


# ---------------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------------
def nkey(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def akey(u):
    u = (u or "").strip().lower()
    u = re.sub(r"^[a-z][a-z0-9+.-]*:/{1,2}", "", u)
    u = re.sub(r"^www\d*\.", "", u)
    u = re.sub(r"[?#].*$", "", u)
    u = re.sub(r"/(index|default|home)\.(html?|php\d?|asp|aspx|cfm|jsp)$", "", u)
    return u.rstrip("/")


def final_address(r):
    """Address as listed: the link target, else the printed text if that looks like an address."""
    if r["href"] and real_href(r["href"]):
        return r["href"].strip()
    t = (r["link_text"] or "").strip()
    return t if LOOKS_LIKE_ADDRESS.match(t) else None


def host_of(u):
    u = re.sub(r"^[a-z][a-z0-9+.-]*:/{0,2}", "", (u or "").strip(), flags=re.I)
    m = re.match(r"([^/?#:\s]*)", u)
    return (m.group(1) if m else "").lower()


def address_flags(u):
    """Facts about an address as listed (used for the caveats, none of them changes the address)."""
    if not u:
        return ["none"]
    flags = []
    if re.match(r"^https?:/[^/]", u, re.I):
        flags.append("malformed_scheme")
    elif not SCHEME.match(u):
        flags.append("no_scheme")
    elif not re.match(r"^https?://", u, re.I):
        flags.append("not_http")
    host = host_of(u)
    if host == "webbyawards.com" or host.endswith(".webbyawards.com"):
        flags.append("webby_internal")
    elif not host or "." not in host:
        flags.append("relative")
    if re.search(r"[<>\"'\s\\]", u):
        flags.append("odd_chars")
    if host.startswith(("wwww.", ".")) or host.endswith(".") or ".." in host:
        flags.append("odd_host")
    if re.search(r"[.,;:)\]]$", u):
        flags.append("trailing_punct")
    if (re.search(r"(?i)https?(://|%3a%2f%2f).*https?(://|%3a%2f%2f)", u) or re.search(r"(?i)[?&](u|url|goto|redirect|target|link)=(https?|%2f|/)", u)
            or re.search(r"(?i)/(redirect|click|track|out|go|r)\.(php|asp|aspx|cgi|jsp)\b", u)):
        flags.append("wrapped")
    return flags


def wayback_stamp(url):
    m = re.search(r"/web/(\d{14})id_/", url)
    return m.group(1) if m else None


def read_pages(log):
    """Fetch (from cache or network) and parse every pinned page. Returns the list of page records."""
    pages = []
    for sid, parser, years, plist, annual in SOURCES:
        for ts, orig, media in plist:
            url = wb(ts, orig)
            rec = {"id": sid, "media": media, "pinned": url, "url": None, "ts": None, "parser": parser, "years": years,
                   "rows": [], "error": None, "dropped": 0}
            try:
                status, body, final = fetch_cached(url)
            except NotCached:
                rec["error"] = "not in cache (offline run)"
                pages.append(rec)
                continue
            if status != 200:
                rec["error"] = "HTTP %s" % status
                pages.append(rec)
                continue
            rec["url"], rec["ts"], rec["bytes"] = final, wayback_stamp(final) or ts, len(body)
            h = decode(body)
            if parser == "list":
                rows, secs, dropped = parse_winner_list(h)
                rows = [r for r in rows if r["year"] in years]
                rec["dropped"] = dropped
            elif parser == "season":
                rows = parse_season_page(h)
                for r in rows:
                    r["year"] = years[0]
                if annual is not None:
                    got = page_annual(h)
                    if got != annual:
                        rec["error"] = "page says annual %s, expected %s" % (got, annual)
                        rows = []
            elif parser == "webcast":
                rows = parse_webcast_winners(h)
                for r in rows:
                    r["year"] = years[0]
                got = page_event_year(h)
                if got != years[0]:
                    rec["error"] = "page says year %s, expected %s" % (got, years[0])
                    rows = []
            else:
                rows = parse_star(h)
                for r in rows:
                    r["year"] = years[0]
                got = page_best_sites_year(h)
                if got != years[0]:
                    rec["error"] = "page says year %s, expected %s" % (got, years[0])
                    rows = []
            for r in rows:
                r["media"] = media
                r["source_id"] = sid
                r["source"] = rec["url"]
                r["source_ts"] = rec["ts"]
            rec["rows"] = rows
            pages.append(rec)
            log("  %-22s %s %-24s rows %3d%s" % (sid, rec["ts"], media or "", len(rows), "  ERROR " + rec["error"] if rec["error"] else ""))
    return pages


def merge_year(year, pages):
    """Union of the pages that carry this year, earliest capture first."""
    cands = []
    for rec in pages:
        if rec["error"] or year not in rec["years"]:
            continue
        rows = [r for r in rec["rows"] if r["year"] == year]
        if rows:
            cands.append((rec["ts"], rec["id"], rows))
    cands.sort(key=lambda c: (c[0], c[1]))
    # group multi-page sources (same id) so media pages of one capture act as one candidate
    grouped = []
    for ts, sid, rows in cands:
        if grouped and grouped[-1][1] == sid:
            grouped[-1][2].extend(rows)
        else:
            grouped.append((ts, sid, list(rows)))
    accepted = []
    for ts, sid, rows in grouped:
        used = set()
        for r in rows:
            idx = None
            for strict in (True, False):
                for i, a in enumerate(accepted):
                    if i in used or a["award"] != r["award"]:
                        continue
                    same_name = nkey(a["name"]) == nkey(r["name"])
                    same_addr = bool(akey(final_address(a))) and akey(final_address(a)) == akey(final_address(r))
                    if (same_name and same_addr) if strict else (same_name or same_addr):
                        idx = i
                        break
                if idx is not None:
                    break
            if idx is None:
                a = dict(r)
                a["seen_in"], a["variants"], a["name_variants"], a["order"] = [sid], [], [], len(accepted)
                accepted.append(a)
                used.add(len(accepted) - 1)
            else:
                used.add(idx)
                a = accepted[idx]
                a["seen_in"].append(sid)
                ra, aa = final_address(r), final_address(a)
                if ra and not aa:      # the earlier page had no address: take it from this page and cite this page
                    a["href"], a["link_text"], a["source"], a["source_ts"] = r["href"], r["link_text"], r["source"], r["source_ts"]
                elif ra and aa and akey(ra) != akey(aa):
                    a["variants"].append({"source_id": sid, "url": ra})
                if nkey(r["name"]) != nkey(a["name"]):
                    a["name_variants"].append({"source_id": sid, "name": r["name"]})
                a["anomaly"] = a["anomaly"] and r["anomaly"]      # a clean listing on a later page clears a markup anomaly
    return accepted, [(ts, sid, len(rows)) for ts, sid, rows in grouped]


def drop_combined(accepted):
    """A page may print two people in one cell (a combined name with no address) that another page lists one by one;
    keep the single entries and drop the combined one."""
    bare = [a for a in accepted if not final_address(a)]
    gone = set()
    for a in bare:
        for b in bare:
            for c in bare:
                if len({id(a), id(b), id(c)}) == 3 and a["award"] == b["award"] == c["award"] and nkey(a["name"]) == nkey(b["name"]) + nkey(c["name"]):
                    gone.add(id(a))
    return [a for a in accepted if id(a) not in gone], len(gone)


def build(log=print):
    pages = read_pages(log)
    frame, detail, noaddr, excluded = [], [], [], []
    report = {"built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pages": [], "years": {}}
    missing_years = []
    for rec in pages:
        report["pages"].append({"id": rec["id"], "media": rec["media"], "url": rec["url"] or rec["pinned"], "capture": rec["ts"],
                                "parser": rec["parser"], "rows": len(rec["rows"]), "error": rec["error"],
                                "placeholder_rows_dropped": rec["dropped"],
                                "anomalies": sum(1 for r in rec["rows"] if r["anomaly"])})
    for year in range(1997, 2009):
        accepted, order = merge_year(year, pages)
        accepted, combined = drop_combined(accepted)
        if not accepted:
            missing_years.append(year)
            report["years"][year] = {"error": "no page could be read"}
            continue
        y = {"winners": len(accepted), "webby": 0, "people_voice": 0, "with_address": 0, "no_address": 0,
             "excluded_internal": 0, "pages": [{"id": sid, "capture": ts, "rows": n} for ts, sid, n in order],
             "added_by_later_pages": 0, "address_variants": 0, "name_variants": 0, "anomalies": 0,
             "flags": {}, "combined_entries_dropped": combined,
             "categories": len({(a["award"], nkey(a["category"])) for a in accepted})}
        first_id = order[0][1]
        for a in accepted:
            addr = final_address(a)
            flags = address_flags(addr)
            y["webby" if a["award"] == "Webby" else "people_voice"] += 1
            for f in flags:
                y["flags"][f] = y["flags"].get(f, 0) + 1
            if a["seen_in"][0] != first_id:
                y["added_by_later_pages"] += 1
            y["address_variants"] += 1 if a["variants"] else 0
            y["name_variants"] += 1 if a["name_variants"] else 0
            y["anomalies"] += 1 if a["anomaly"] else 0
            base = {"year": year, "award": a["award"], "category": a["category"], "name": a["name"], "url": addr, "source": a["source"]}
            extra = dict(base, media=a["media"], credit=a["credit"], link_text=a["link_text"], note=a["note"], anomaly=a["anomaly"],
                         flags=flags, seen_in=a["seen_in"], other_addresses=a["variants"], other_names=a["name_variants"])
            if addr is None:
                noaddr.append(extra)
                y["no_address"] += 1
            elif "webby_internal" in flags or "relative" in flags:
                excluded.append(dict(extra, reason="address points to webbyawards.com or is relative"))
                y["excluded_internal"] += 1
            else:
                frame.append(base)
                detail.append(extra)
                y["with_address"] += 1
        report["years"][year] = y
    for year, yrs in report["years"].items():
        if "error" not in yrs:
            yrs["distinct_addresses"] = len({akey(r["url"]) for r in frame if r["year"] == year})
    report["total_with_address"] = len(frame)
    report["total_distinct_addresses"] = len({akey(r["url"]) for r in frame})
    key = lambda r: (r["year"], 0 if r["award"] == "Webby" else 1, r["category"].lower(), r["name"].lower())
    frame.sort(key=key)
    detail.sort(key=key)
    noaddr.sort(key=key)
    excluded.sort(key=key)
    return frame, detail, noaddr, excluded, report, missing_years


def main(argv):
    global OFFLINE
    if "--offline" in argv or os.environ.get("SCOUT_WEBBY_OFFLINE") == "1":
        OFFLINE = True
    try:
        frame, detail, noaddr, excluded, report, missing = build()
    except Paused as e:
        print("stopped: %s. Run again after that time (the cache keeps what was fetched)." % e)
        return 3
    print()
    print("year  webby  pv  with-address  no-address  excluded  added-later  pages")
    for year in range(1997, 2009):
        y = report["years"][year]
        if "error" in y:
            print("%d  NO PAGE READ" % year)
            continue
        print("%d  %5d %3d  %12d  %10d  %8d  %11d  %s" % (year, y["webby"], y["people_voice"], y["with_address"], y["no_address"],
              y["excluded_internal"], y["added_by_later_pages"], ", ".join("%s:%d" % (p["id"], p["rows"]) for p in y["pages"])))
    print("total with address:", len(frame), " no address:", len(noaddr), " excluded:", len(excluded))
    bad = [p for p in report["pages"] if p["error"]]
    if missing or bad:
        print("NOT WRITTEN: %d pinned pages unreadable, years without a page: %s" % (len(bad), missing))
        for p in bad:
            print("  ", p["id"], p["capture"], p["error"])
        return 2
    os.makedirs(DATA, exist_ok=True)
    for path, data in ((OUT, frame), (OUT_DETAIL, detail), (OUT_NOADDR, noaddr + excluded), (OUT_REPORT, report)):
        with open(path, "w") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
    print("wrote", OUT, "and", OUT_DETAIL, OUT_NOADDR, OUT_REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
