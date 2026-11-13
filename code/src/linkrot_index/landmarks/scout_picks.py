#!/usr/bin/env python3
"""scout_picks.py: builds the frame of sites featured by Yahoo Picks and by Cool Site of the Day, from Wayback Machine copies of the two columns' own archive pages. Writes data/landmarks/frame_picks.json (a list of {column, date, name, url, source}); beside it frame_picks_run.json (what was read, what was not) and frame_picks_pages.json (every page read, with its capture timestamp). Requests go only to web.archive.org (the CDX index and raw id_ captures). A picked site is never requested.

Yahoo Picks pages: weekly pages www.yahoo.com/picks/YYMMDD.html and YYYYMMDD.html (Aug 1995 to Jul 2001), the same weeks re-hosted at picks.yahoo.com/YYYYMMDD.html and picks.yahoo.com/picks/YYYYMMDD.html (from 2002 each holds a seven-day window of daily picks), one-day pages picks.yahoo.com/picks/i/YYYYMMDD.html (2002 to 2008) and People of the Web pages picks.yahoo.com/picks/potw/YYYYMMDD.html (2007). Category, most-popular and What's New pages repeat or sit beside the picks and are not read.
Cool Site of the Day pages: the Still Cool Archive, one page per month from Aug 1994, at cool.infi.net/cgi-bin/stillcool.pl?month=MM&year=YYYY and www.coolsiteoftheday.com/cgi-bin/stillcool.pl?month=MM&year=YYYY (year as two or four digits, "&" spelled plainly).

Read order: Yahoo weekly pages, a 20-page audit of the one-day-page rule, Still Cool months (in date order; reading would stop after 12 months in a row that list no pick, which never happened), People of the Web pages, Yahoo one-day pages. Frame version 1 was built with --stop-before-day-pages: the one-day pages for days that no weekly or window page gave (672 pages) are listed in the run log as not read. The frame file is rewritten every 50 pages and after each group, so a stopped run is usable.
Capture rule. A Yahoo page is the date-named page whatever its host or path, and we read its earliest 200 capture; a capture that answers 4xx is replaced by the next 200 capture of the same address. One-day pages are read only for days that no weekly or window page already gave (the audit reads one per quarter to check that they repeat the window picks). A Still Cool month page grows while the month runs, so we read its earliest 200 capture taken on or after the first of the next month (earliest of the hosts and the two or four digit year spellings; a capture that is not a Still Cool page at all is skipped for the next one).
Pick rule. Weekly pages (1995 to 2001): the first link of each list item in the "sites featured" list, or, if a page has no list, its bold links. Year-end recap pages take each pick's date from its "(Featured Month D)" note. Dated pages (2002 on): after each dated heading, the first bold link (the write-up's other links are inside the same site). Still Cool: in each table row whose first cell is a bold date like "Jan 02, 1995:", the row's link. Navigation, sponsor, mailto and the column's own links are not picks, and neither are Yahoo's own sites (yahoo, yahooligans, yimg). Yahoo click-tracking wrappers (/picks/?http://..., rd.yahoo.com) and archive.org wrappers are unwrapped to the target address. An address is kept as printed, including a ":80" port, a missing "//" or a missing scheme.

Politeness: User-Agent below, one request at a time over one keep-alive connection, 6 s between this script's requests (and 1.2 s from any scout's), 10 minutes of waiting after a refused connection or a 429/503 (the pause is published in the shared rate file so the other scouts wait too), and a halt after two connection failures or two 429/503 answers in a row, or five failed pages in a row. The rate file is shared with scout_webby.py and its pause key is honored. Standard library only. Pages and listings are cached in data/landmarks/cache_picks, so a rerun fetches nothing it already has.
Usage: python3 -I scout_picks.py [--plan] [--cache-only] [--only yahoo|csotd] [--max-fetch N] [--retry-failed] [--stop-before-day-pages]
"""
import argparse
import collections
import datetime
import fcntl
import gzip
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.parse
from html.parser import HTMLParser

UA = "HeuremenLLC-linkrot/1.0 (https://indahl.ai)"
HOST = "web.archive.org"                       # the ONLY host this script may ever request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../linkrot_index
DATA = ROOT + "/data/landmarks"
CACHE = DATA + "/cache_picks"
OUT = DATA + "/frame_picks.json"
RUNLOG = DATA + "/frame_picks_run.json"
PAGES = DATA + "/frame_picks_pages.json"       # every page read, with its capture timestamp
MANIFEST = CACHE + "/manifest.jsonl"
FAILURES = CACHE + "/failures.json"
# Shared with scout_webby.py on purpose: one lock, one last-request clock and one pause key for every scout
# that talks to archive.org, so all scouts together stay under the pace the pause key asks for.
RATE_STATE = DATA + "/.scout_webby_ratelimit.json"
RATE_LOCK = DATA + "/.scout_webby_ratelimit.lock"
RATE_BUCKET = "archive.org"
PAUSE_KEY = RATE_BUCKET + "_pause_until"
OWN_KEY = RATE_BUCKET + "_picks_last"   # when this script's last request ended (the shared key says when anyone's did)
MIN_GAP = 6.0          # seconds from the end of this script's last request to the start of its next
SHARED_GAP = 1.2       # seconds that must separate any two requests from any scouts
BACKOFF = 600          # seconds to wait after a refused connection or a 429/503
SERVER_FAULT_WAIT = 60 # seconds to wait after another 5xx
MAX_TRIES = 4          # other 5xx answers tolerated for one address before it is given up for this run
MAX_RATE_ANSWERS = 2   # 429/503 answers for one address before the whole run halts
MAX_FAILED_IN_A_ROW = 5  # pages in a row that fail on the archive's side (no answer, 429, 5xx) before the run halts
MAX_CONN_FAILS = 2     # connection failures in a row before the whole run halts
HALT_PAUSE = 1800      # pause published when the run halts
CDX_FL = "timestamp,original,statuscode,mimetype"
FLUSH_EVERY = 50       # pages between rewrites of the frame file
CSOTD_EMPTY_STOP = 12  # Still Cool months in a row with no pick after which the later months are not read

YAHOO = "Yahoo Picks"
CSOTD = "Cool Site of the Day"


class ArchiveUnreachable(Exception):
    pass


# ---------------------------------------------------------------- network (web.archive.org only)

_CONN = None            # one keep-alive HTTPS connection, reused for every request of this run


def _check_host(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or (p.hostname or "").lower() != HOST:
        raise RuntimeError("refused: only https://%s may be requested, not %s" % (HOST, url))


def _load_state():
    try:
        with open(RATE_STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(state):
    with open(RATE_STATE, "w") as f:
        json.dump(state, f)


def _rate_wait():
    """Returns with the shared lock held once this script's own gap, the gap since anyone's last request and any
    published pause are all over. A long wait never holds the lock."""
    os.makedirs(DATA, exist_ok=True)
    while True:
        lock = open(RATE_LOCK, "a+")
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            state = _load_state()
            wait = max(state.get(OWN_KEY, 0) + MIN_GAP, state.get(RATE_BUCKET, 0) + SHARED_GAP, state.get(PAUSE_KEY, 0)) - time.time()
        except Exception:
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()
            raise
        if wait <= 0:
            return lock
        if wait <= SHARED_GAP + 0.5:
            time.sleep(wait)
            return lock
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
        time.sleep(min(wait, 60))


def _rate_done(lock):
    try:
        state = _load_state()
        state[RATE_BUCKET] = state[OWN_KEY] = time.time()
        _save_state(state)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


def _set_pause(seconds):
    """Publish a pause for every scout that shares the rate file."""
    os.makedirs(DATA, exist_ok=True)
    lock = open(RATE_LOCK, "a+")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        state = _load_state()
        state[PAUSE_KEY] = max(state.get(PAUSE_KEY, 0), time.time() + seconds)
        _save_state(state)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


def _make_conn(timeout):
    return http.client.HTTPSConnection(HOST, timeout=timeout)


def _drop_conn():
    global _CONN
    if _CONN is not None:
        try:
            _CONN.close()
        except Exception:
            pass
        _CONN = None


def _once(cur, timeout):
    """One GET on the keep-alive connection. Returns (status, body, headers). status None: the connection failed.
    status -1: an idle connection the server had already closed (the caller asks again after the usual gap)."""
    global _CONN
    sp = urllib.parse.urlsplit(cur)
    target = sp.path + (("?" + sp.query) if sp.query else "")
    reused = _CONN is not None and getattr(_CONN, "sock", None) is not None
    if _CONN is None:
        _CONN = _make_conn(timeout)
    else:
        _CONN.timeout = timeout
        if getattr(_CONN, "sock", None) is not None:
            _CONN.sock.settimeout(timeout)
    try:
        _CONN.request("GET", target, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip, identity", "Connection": "keep-alive"})
        resp = _CONN.getresponse()
        body = resp.read()
        status, hdrs = resp.status, resp.msg
        if resp.will_close:
            _drop_conn()
        return status, body, hdrs
    except (http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError, http.client.CannotSendRequest, http.client.ResponseNotReady) as e:
        _drop_conn()
        if reused:
            return -1, str(e).encode(), None
        return None, str(e).encode(), None
    except (http.client.HTTPException, OSError, ValueError) as e:       # refused, timed out, TLS trouble
        _drop_conn()
        return None, str(e).encode(), None


def http_get(url, timeout=90, max_hops=6):
    """One GET with the study's user agent, over one keep-alive connection. Only web.archive.org. Each redirect
    hop is checked, paced and counted as its own request. A refused or failed connection waits 10 minutes and
    halts the run (ArchiveUnreachable) on the second one in a row. 429/503 wait 10 minutes and halt the run on
    the second; other 5xx wait one minute. Returns (status, body_bytes, headers, final_url)."""
    cur, hops, tries, conn, stale = url, 0, 0, 0, 0
    while True:
        _check_host(cur)
        lock = _rate_wait()
        try:
            status, body, headers = _once(cur, timeout)
        finally:
            _rate_done(lock)
        if status == -1 and stale < 3:             # idle connection closed by the server: ask again on a fresh one
            stale += 1
            continue
        if status in (None, -1):                   # the connection itself failed
            conn += 1
            if conn >= MAX_CONN_FAILS:
                _set_pause(HALT_PAUSE)
                raise ArchiveUnreachable("connection failed %d times in a row (last: %s on %s)" % (conn, body.decode("utf-8", "replace")[:120], cur))
            _set_pause(BACKOFF)
            sys.stderr.write("  connection failed on %s (%s); waiting %ss\n" % (cur, body.decode("utf-8", "replace")[:80], BACKOFF))
            sys.stderr.flush()
            continue
        conn = 0
        if status in (429, 503):                   # the archive asks us to slow down: wait once, then stop
            tries += 1
            if tries >= MAX_RATE_ANSWERS:
                _set_pause(HALT_PAUSE)
                raise ArchiveUnreachable("answer %s %d times in a row (last on %s)" % (status, tries, cur))
            _set_pause(BACKOFF)
            sys.stderr.write("  answer %s on %s; waiting %ss\n" % (status, cur, BACKOFF))
            sys.stderr.flush()
            continue
        if status >= 500:
            tries += 1
            if tries >= MAX_TRIES:
                return status, body, headers, cur
            _set_pause(SERVER_FAULT_WAIT)
            sys.stderr.write("  answer %s on %s; waiting %ss\n" % (status, cur, SERVER_FAULT_WAIT))
            sys.stderr.flush()
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


def _cdx_page(params):
    """One CDX request (cached on disk by its exact URL). Returns (rows as dicts, resume key or None)."""
    url = "https://%s/cdx/search/cdx?%s" % (HOST, urllib.parse.urlencode(params, doseq=True))
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "cdx_" + hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")
    if os.path.exists(path):
        with open(path) as f:
            d = json.load(f)
        return d["rows"], d.get("resume")
    status, body, _, final = http_get(url, timeout=120)
    if status != 200:
        raise RuntimeError("CDX %s for %s" % (status, url))
    text = body.decode("utf-8", "replace").strip()
    raw = json.loads(text) if text else []
    rows, resume = [], None
    if raw:
        head = raw[0]
        for i, r in enumerate(raw[1:], 1):
            if r == []:                      # separator before the resume key
                if i + 1 < len(raw) and raw[i + 1]:
                    resume = raw[i + 1][0]
                break
            if len(r) == len(head):
                rows.append(dict(zip(head, r)))
    if rows:                                 # an empty answer is never cached, so a rerun asks again
        with open(path + ".tmp", "w") as f:
            json.dump({"query": url, "rows": rows, "resume": resume}, f)
        os.replace(path + ".tmp", path)
    return rows, resume


def cdx_all(page=5000, max_pages=None, **params):
    """All rows of a CDX query, following resume keys (at most max_pages listing pages when given). Every page of the
    listing is cached."""
    q = {"output": "json", "limit": page, "showResumeKey": "true"}
    q.update({k: v for k, v in params.items() if v is not None})
    out, seen, n = [], set(), 0
    while True:
        rows, resume = _cdx_page(q)
        out.extend(rows)
        n += 1
        if not resume or resume in seen or (max_pages and n >= max_pages):
            break
        seen.add(resume)
        q = dict(q)
        q["resumeKey"] = resume
    return out


def capture_url(ts, original):
    return "https://%s/web/%sid_/%s" % (HOST, ts, urllib.parse.quote(original, safe=":/?&=%#+~@!$'()*,;[]"))


_MAN = None


def _manifest():
    global _MAN
    if _MAN is None:
        _MAN = {}
        if os.path.exists(MANIFEST):
            with open(MANIFEST) as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        _MAN[d["file"]] = d
                    except Exception:
                        pass
    return _MAN


def _failures():
    if os.path.exists(FAILURES):
        try:
            with open(FAILURES) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_failures(d):
    with open(FAILURES + ".tmp", "w") as f:
        json.dump(d, f, indent=1)
    os.replace(FAILURES + ".tmp", FAILURES)


def decode(b):
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


class Fetcher:
    """Cached reader of archive captures. A capture already on disk is never requested again. A capture that
    answered with a permanent error (4xx) is remembered and skipped unless --retry-failed is given."""

    def __init__(self, max_fetch=None, retry_failed=False, cache_only=False):
        self.max_fetch, self.retry_failed, self.cache_only = max_fetch, retry_failed, cache_only
        self.network = 0
        self.failed_in_a_row = 0
        self.fail = _failures()

    @staticmethod
    def _name(ts, original):
        return "%s_%s.html" % (ts, hashlib.sha1(original.encode()).hexdigest()[:12])

    def peek(self, ts, original):
        """The cached page or None. Never touches the network."""
        path = os.path.join(CACHE, self._name(ts, original))
        if os.path.exists(path):
            with open(path, "rb") as f:
                return decode(f.read())
        return None

    @staticmethod
    def alternates(original, after_ts, limit=2):
        """The next 200 captures of the same address after a capture that could not be read (one CDX listing,
        cached): the rule is the earliest 200 capture that can be read."""
        rows = cdx_all(page=200, max_pages=1, fl=CDX_FL, filter="statuscode:200", url=original, matchType="exact")
        return [r for r in sorted(rows, key=lambda r: r["timestamp"]) if r["timestamp"] > after_ts][:limit]

    def read(self, ts, original):
        """Returns (text, source_url, from_cache) or (None, reason, False)."""
        name = self._name(ts, original)
        path = os.path.join(CACHE, name)
        url = capture_url(ts, original)
        man = _manifest()
        if os.path.exists(path):
            with open(path, "rb") as f:
                return decode(f.read()), man.get(name, {}).get("final", url), True
        if self.cache_only:
            return None, "not in cache (--cache-only)", False
        f = self.fail.get(name)
        if f and not self.retry_failed and 400 <= f.get("status", 0) < 500 and f.get("status") != 429:
            return None, "skipped, earlier answer %s" % f["status"], False
        if self.max_fetch is not None and self.network >= self.max_fetch:
            return None, "not fetched (--max-fetch reached)", False
        self.network += 1
        status, body, headers, final = http_get(url)
        if status != 200 or not body:
            self.fail[name] = {"status": status, "ts": ts, "original": original, "when": int(time.time())}
            _save_failures(self.fail)
            if status == 0 or status == 429 or status >= 500:
                self.failed_in_a_row += 1
                if self.failed_in_a_row >= MAX_FAILED_IN_A_ROW:
                    _set_pause(HALT_PAUSE)
                    raise ArchiveUnreachable("%d pages in a row failed on the archive's side (last answer %s)" % (self.failed_in_a_row, status))
            return None, "answer %s" % status, False
        self.failed_in_a_row = 0
        os.makedirs(CACHE, exist_ok=True)
        with open(path + ".tmp", "wb") as fh:
            fh.write(body)
        os.replace(path + ".tmp", path)
        rec = {"file": name, "ts": ts, "original": original, "final": final, "bytes": len(body)}
        with open(MANIFEST, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        man[name] = rec
        if name in self.fail:
            del self.fail[name]
            _save_failures(self.fail)
        return decode(body), final, False


# ---------------------------------------------------------------- reading a page

MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DATE_TEXT = re.compile(r"^\s*([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})\s*:?\s*$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def norm(t):
    return re.sub(r"\s+", " ", (t or "").replace("\xa0", " ")).strip()


def iso(y, m, d):
    try:
        return datetime.date(int(y), int(m), int(d)).isoformat()
    except ValueError:
        return None


def month_number(name):
    return MONTHS.get((name or "")[:3].lower())


def date_from_text(t):
    m = DATE_TEXT.match(t or "")
    if not m or not month_number(m.group(1)):
        return None
    return iso(m.group(3), month_number(m.group(1)), m.group(2))


class Walker(HTMLParser):
    """Flat events in document order: ('a', {href, name, text, bold, li}) per anchor, ('b', text) per outermost
    bold run, ('li', n) per list item, ('tr',) per table row. li_text[n] is the text of list item n and
    tr_text[n] the text of table row n."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ev, self.base, self.li_text, self.tr_text = [], None, {}, {0: []}
        self._bold, self._btxt, self._a = 0, [], None
        self._li, self._lin, self._skip, self._tr = None, 0, 0, 0

    def _close_a(self):
        if self._a is not None:
            a = self._a
            a["text"] = norm("".join(a["text"]))
            self.ev.append(("a", a))
            self._a = None

    def handle_starttag(self, tag, attrs):
        at = {k.lower(): v for k, v in attrs}
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "base" and at.get("href"):
            self.base = at["href"].strip()
        elif tag in ("b", "strong"):
            if self._bold == 0:
                self._btxt = []
            self._bold += 1
            if self._a is not None:
                self._a["bold"] = True
        elif tag == "li":
            self._lin += 1
            self._li = self._lin
            self.li_text[self._lin] = []
            self.ev.append(("li", self._lin))
        elif tag == "tr":
            self._tr += 1
            self.tr_text[self._tr] = []
            self.ev.append(("tr",))
        elif tag == "a":
            self._close_a()
            self._a = {"href": at.get("href"), "name": at.get("name"), "text": [], "bold": self._bold > 0, "li": self._li, "tr": self._tr}

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag == "a":
            self._close_a()
        elif tag in ("b", "strong") and self._bold > 0:
            self._bold -= 1
            if self._bold == 0:
                self.ev.append(("b", norm("".join(self._btxt))))
        elif tag in ("ul", "ol"):
            self._li = None

    def handle_data(self, d):
        if self._skip:
            return
        if self._a is not None:
            self._a["text"].append(d)
        if self._bold > 0:
            self._btxt.append(d)
        if self._li is not None:
            self.li_text[self._li].append(d)
        self.tr_text[self._tr].append(d)

    def finish(self):
        try:
            self.close()
        except Exception:
            pass
        self._close_a()
        self.li_text = {k: norm("".join(v)) for k, v in self.li_text.items()}
        self.tr_text = {k: norm("".join(v)) for k, v in self.tr_text.items()}
        return self.ev


def walk(html):
    w = Walker()
    try:
        w.feed(html)
    except Exception as e:                      # keep what was read before the markup broke
        sys.stderr.write("  parser stopped early: %s\n" % e)
    ev = w.finish()
    return ev, w.base, w.li_text, w.tr_text


YAHOO_HOST = re.compile(r"(^|\.)yahoo\.[a-z.]+$|(^|\.)(yahooligans|yahoo-inc|yimg)\.com$", re.I)
CSOTD_HOST = re.compile(r"(^|\.)(cool\.infi\.net|coolsiteoftheday\.com|csotd\.com)$", re.I)
WRAP_ARCHIVE = re.compile(r"^/web/\d+[a-z_]*/(https?:.+)$", re.I)
WRAP_QUERY = re.compile(r"[?*=](https?(?::|%3A)(?://|%2F%2F).+)$", re.I)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
KEEP_SCHEMES = ("http", "https", "ftp", "gopher")
BARE_HOST = re.compile(r"^www\d*\.[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?:[/?#:]|$)")


def resolve(href, base, own):
    """(address, how). address is None when the link is not a pick; how says why or how it was got:
    direct, unwrapped, or the reason for dropping it."""
    if not href:
        return None, "no-href"
    u = re.sub(r"[\r\n\t]+", "", href.strip())
    if not u or u.startswith("#"):
        return None, "fragment"
    scheme_less = False
    if not SCHEME.match(u):
        if BARE_HOST.match(u):                    # "www.example.com" printed without a scheme: kept as listed
            scheme_less = True
        elif base:
            u = urllib.parse.urljoin(base, u)
    how = "direct"
    for _ in range(0 if scheme_less else 3):
        try:
            sp = urllib.parse.urlsplit(u)
        except ValueError:
            return None, "unparseable"
        host = (sp.hostname or "").lower() if sp.scheme.lower() in KEEP_SCHEMES else ""
        inner = None
        if host == HOST:
            m = WRAP_ARCHIVE.match(sp.path + (("?" + sp.query) if sp.query else ""))
            inner = m.group(1) if m else None
        elif host and (YAHOO_HOST.search(host) or CSOTD_HOST.search(host)):
            rest = u[u.index(sp.netloc) + len(sp.netloc):] if sp.netloc and sp.netloc in u else ""
            m = WRAP_QUERY.search(rest)
            inner = m.group(1) if m else None
        if not inner:
            break
        u = urllib.parse.unquote(inner) if re.match(r"https?%3A", inner, re.I) else inner
        how = "unwrapped"
    try:
        sp = urllib.parse.urlsplit(u)
    except ValueError:
        return None, "unparseable"
    if scheme_less:
        host = re.split(r"[/?#:]", u, 1)[0].lower()
        how = "no-scheme"
    elif sp.scheme.lower() not in KEEP_SCHEMES:
        return None, "scheme-" + (sp.scheme.lower() or "none")
    else:
        host = (sp.hostname or "").lower()
    if not host and sp.scheme.lower() in ("http", "https") and re.match(r"^https?:[^/]", u, re.I):
        host = re.split(r"[/?#:]", u.split(":", 1)[1], 1)[0].lower()      # "http:www.example.com/x", kept as printed
    if not host:
        return None, "no-host"
    if own.search(host):
        return None, "own-host"
    if EMAIL.search(u):
        return None, "email-in-address"
    return u, how


def url_key(u):
    sp = urllib.parse.urlsplit(u)
    try:
        port = sp.port
    except ValueError:
        port = None
    default = {"http": 80, "https": 443, "ftp": 21, "gopher": 70}.get(sp.scheme.lower())
    host = (sp.hostname or "").lower() + ((":%d" % port) if port and port != default else "")
    return "%s://%s%s%s" % (sp.scheme.lower(), host, sp.path or "/", ("?" + sp.query) if sp.query else "")


def clean_name(n):
    return norm(EMAIL.sub("", n or ""))


def dated_entries(ev, base, own, need_bold, same_row=False):
    """Walks the page. After a dated heading, the first link that passes resolve() (and is bold when need_bold)
    is that day's pick; further links up to the next heading are not picks. Returns (items, drops)."""
    items, drops = [], collections.Counter()
    cur, got = None, False
    for e in ev:
        if e[0] == "tr":
            if same_row:
                cur, got = None, False
        elif e[0] == "b":
            d = date_from_text(e[1])
            if d:
                cur, got = d, False
        elif e[0] == "a":
            a = e[1]
            nm = (a.get("name") or "").strip()
            if re.fullmatch(r"\d{8}", nm):
                d = iso(nm[:4], nm[4:6], nm[6:])
                if d:
                    cur, got = d, False
                    continue
            if cur is None or got or not a.get("href"):
                continue
            if need_bold and not a["bold"]:
                continue
            addr, how = resolve(a["href"], base, own)
            if addr is None:
                drops[how] += 1
                continue
            items.append({"date": cur, "name": clean_name(a["text"]), "url": addr, "how": how})
            got = True
    return items, drops


FEATURED = re.compile(r"\(\s*Featured\s+([A-Za-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?\s*\)", re.I)
RECAP_HEAD = re.compile(r"Picks\s+of\s+the\s+Year\s*\(", re.I)
RECAP_YEAR = re.compile(r"(?:featured\s+in|our)\s+((?:19|20)\d\d)\b", re.I)


def weekly_list(ev, base, own, date, li_text, tr_text, recap_year=None):
    """Weekly pages: the first link of each list item; if the page has no usable list, its bold links. On a
    year-end recap page each pick's date comes from the "(Featured Month D)" note in its list item or table row."""
    drops = collections.Counter()
    items, seen = [], set()

    def dated(note_text):
        if not recap_year:
            return date
        m = FEATURED.search(note_text or "")
        dd = iso(recap_year, month_number(m.group(1)), m.group(2)) if m and month_number(m.group(1)) else None
        if not dd:
            drops["recap-item-without-note"] += 1
        return dd or date

    for e in ev:
        if e[0] == "a" and e[1].get("li") is not None and e[1]["li"] not in seen:
            seen.add(e[1]["li"])
            addr, how = resolve(e[1].get("href"), base, own)
            if addr is None:
                drops[how] += 1
                continue
            items.append({"date": dated(li_text.get(e[1]["li"])), "name": clean_name(e[1]["text"]), "url": addr, "how": how})
    if items:
        return "list", items, drops
    for e in ev:
        if e[0] == "a" and e[1]["bold"] and e[1].get("href"):
            addr, how = resolve(e[1]["href"], base, own)
            if addr is None:
                drops[how] += 1
                continue
            items.append({"date": dated(tr_text.get(e[1].get("tr"))), "name": clean_name(e[1]["text"]), "url": addr, "how": how})
    return ("bold" if items else "none"), items, drops


PRINTED_WEEK = re.compile(r"Picks\s+of\s+the\s+(?:Week|Year|Ages)\s*\(\s*(\d{1,2})\s*-\s*(\d{1,2})\s*-\s*(\d{2,4})\s*\)", re.I)


def printed_week_date(text):
    m = PRINTED_WEEK.search(text)
    if not m:
        return None
    y = int(m.group(3))
    y = y + (1900 if y >= 90 else 2000) if y < 100 else y
    return iso(y, m.group(1), m.group(2))


def read_yahoo_page(html, original, url_date):
    """-> (rule, items, drops, printed_date_if_it_differs)"""
    ev, base, li_text, tr_text = walk(html)
    base = base or original
    has_headers = any((e[0] == "b" and date_from_text(e[1])) or (e[0] == "a" and re.fullmatch(r"\d{8}", (e[1].get("name") or "").strip())) for e in ev)
    if has_headers:
        items, drops = dated_entries(ev, base, YAHOO_HOST, need_bold=True)
        return "dated", items, drops, None
    text = norm(re.sub(r"<[^>]+>", " ", html))
    recap_year = None
    if RECAP_HEAD.search(text) or len(FEATURED.findall(text)) >= 5:    # a year-end recap re-lists picks with "(Featured Month D)"
        m = RECAP_YEAR.search(text)
        pd = printed_week_date(text) or url_date
        recap_year = int(m.group(1)) if m else (int(pd[:4]) - 1 if pd[5:7] == "01" else int(pd[:4]))
    rule, items, drops = weekly_list(ev, base, YAHOO_HOST, url_date, li_text, tr_text, recap_year)
    pd = printed_week_date(text)
    return ("recap-" if recap_year else "weekly-") + rule, items, drops, (pd if pd and pd != url_date else None)


def read_csotd_page(html, original):
    ev, base, _, _ = walk(html)
    items, drops = dated_entries(ev, base or original, CSOTD_HOST, need_bold=False, same_row=True)
    return ("stillcool" if (items or re.search(r"stillcool\.pl\?month=", html, re.I)) else "not-a-stillcool-page"), items, drops


# ---------------------------------------------------------------- plans (which pages to read)

def _iso_from_digits(d):
    if len(d) == 6:
        yy = int(d[:2])
        return iso(1900 + yy if yy >= 90 else 2000 + yy, d[2:4], d[4:6])
    return iso(d[:4], d[4:6], d[6:])


def yahoo_identity(original):
    """(kind, iso date) for a Yahoo Picks archive page URL, else None. kind: week, day, potw."""
    p = urllib.parse.urlsplit(original)
    host = (p.hostname or "").lower()
    if p.query or not re.search(r"(^|\.)yahoo\.com$", host):
        return None
    path = re.sub(r"/{2,}", "/", p.path)
    if host.startswith("picks."):
        m = re.fullmatch(r"/(?:picks/)?(?:(i|potw)/)?(\d{6}|\d{8})\.html", path)
    else:
        m = re.fullmatch(r"/picks/(?:(i|potw)/)?(\d{6}|\d{8})\.html", path)
    if not m:
        return None
    d = _iso_from_digits(m.group(2))
    return ({None: "week", "i": "day", "potw": "potw"}[m.group(1)], d) if d else None


def plan_yahoo():
    rows = []
    for u in ("www.yahoo.com/picks/", "picks.yahoo.com/"):
        rows += cdx_all(fl=CDX_FL, filter="statuscode:200", url=u, matchType="prefix", collapse="urlkey")
    best, listed = {}, collections.Counter()
    for r in rows:
        ident = yahoo_identity(r["original"])
        if not ident:
            continue
        listed[ident[0]] += 1
        if ident not in best or r["timestamp"] < best[ident]["timestamp"]:
            best[ident] = r
    return best, listed


RX_MY = re.compile(r"stillcool\.pl\?month=(\d{1,2})&year=(\d{2}|\d{4})$")      # the canonical spelling only: "&amp;" and "%26" spellings return empty pages


def plan_csotd():
    rows = []
    for h in ("cool.infi.net", "coolsiteoftheday.com"):
        rows += cdx_all(fl=CDX_FL, filter="statuscode:200", url=h + "/cgi-bin/stillcool.pl", matchType="prefix", collapse="timestamp:6")
    pages = collections.defaultdict(list)
    for r in rows:
        m = RX_MY.search(r["original"])
        if not m:
            continue
        mo, yr = int(m.group(1)), int(m.group(2))
        yr = yr + (1900 if yr >= 90 else 2000) if yr < 100 else yr
        if 1 <= mo <= 12 and (yr, mo) >= (1994, 8):
            pages[(yr, mo)].append(r)
    plan = {}
    for (yr, mo), cands in sorted(pages.items()):
        cut = "%04d%02d01000000" % ((yr, mo + 1) if mo < 12 else (yr + 1, 1))
        cands.sort(key=lambda r: r["timestamp"])
        after = [r for r in cands if r["timestamp"] >= cut]
        pool = after if after else [cands[-1]]
        plan[(yr, mo)] = dict(pool[0], partial=not after, alts=pool[1:3])
    return plan


# ---------------------------------------------------------------- the run

def show(msg):
    print(msg)
    sys.stdout.flush()


class Frame:
    """Collects picks as pages are read, and writes the frame file and the run log (also part-way)."""

    def __init__(self, fetch):
        self.fetch, self.out, self.order = fetch, [], 0
        self.groups = collections.OrderedDict()
        self.extra = {}
        self.started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.halted = None
        self.since_flush = 0
        self.pages = []

    def group(self, name, planned):
        self.groups[name] = {"pages_planned": planned, "pages_read": 0, "pages_read_from_cache": 0, "complete": False,
                             "pages_without_picks": [], "unread": [], "rules": collections.Counter(), "dropped_links": collections.Counter()}
        return self.groups[name]

    def add(self, g, column, items, source):
        for it in items:
            self.order += 1
            self.out.append({"column": column, "date": it["date"], "name": it["name"], "url": it["url"], "source": source,
                             "_o": self.order, "_how": it["how"], "_g": g})

    def tick(self):
        self.since_flush += 1
        if self.since_flush >= FLUSH_EVERY:
            self.flush()

    def flush(self):
        self.since_flush = 0
        seen, final = set(), []
        for r in sorted(self.out, key=lambda r: (0 if r["column"] == YAHOO else 1, r["date"], r["_o"])):
            k = (r["column"], r["date"], url_key(r["url"]))
            if k in seen:
                continue
            seen.add(k)
            final.append(r)
        per = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
        for r in final:
            per[r["_g"]][r["column"]][r["date"][:4]] += 1
        public = [{k: r[k] for k in ("column", "date", "name", "url", "source")} for r in final]
        if EMAIL.search(json.dumps(public)):
            raise RuntimeError("an email-like string reached the output; refusing to write it")
        os.makedirs(DATA, exist_ok=True)
        with open(OUT + ".tmp", "w") as f:
            json.dump(public, f, indent=1, ensure_ascii=False)
        os.replace(OUT + ".tmp", OUT)
        log = {"started": self.started, "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "pace": {"min_gap_s": MIN_GAP, "keep_alive_connection": True, "wait_after_connection_failure_s": BACKOFF},
               "halted": self.halted, "network_fetches_this_run": self.fetch.network,
               "picks_total": len(final), "duplicates_removed": len(self.out) - len(final),
               "unwrapped_addresses": sum(1 for r in final if r["_how"] == "unwrapped"),
               "picks_per_year_by_group": {g: {c: dict(sorted(v.items())) for c, v in cols.items()} for g, cols in per.items()},
               "picks_per_year": {}, "groups": {}}
        py = collections.defaultdict(collections.Counter)
        for r in final:
            py[r["column"]][r["date"][:4]] += 1
        log["picks_per_year"] = {c: dict(sorted(v.items())) for c, v in py.items()}
        for name, g in self.groups.items():
            log["groups"][name] = dict(g, rules=dict(g["rules"]), dropped_links=dict(g["dropped_links"]),
                                       unread_count=len(g["unread"]), unread=g["unread"][:200],
                                       pages_without_picks_count=len(g["pages_without_picks"]), pages_without_picks=g["pages_without_picks"][:300])
        log.update(self.extra)
        with open(RUNLOG + ".tmp", "w") as f:
            json.dump(log, f, indent=1, ensure_ascii=False)
        os.replace(RUNLOG + ".tmp", RUNLOG)
        with open(PAGES + ".tmp", "w") as f:
            json.dump(self.pages, f, indent=0, ensure_ascii=False)
        os.replace(PAGES + ".tmp", PAGES)
        return final


def run(args):
    fetch = Fetcher(args.max_fetch, args.retry_failed, args.cache_only)
    fr = Frame(fetch)
    ybest = ycov = cplan = None
    window_keys = collections.defaultdict(set)     # day -> address keys given by the window pages
    covered = set()
    if args.only in (None, "yahoo"):
        ybest, ylisted = plan_yahoo()
        kinds = collections.Counter(k for k, _ in ybest)
        show("YAHOO plan: %d date-named archive pages %s (raw URLs listed %s)" % (len(ybest), dict(kinds), dict(ylisted)))
        fr.extra["yahoo_urls_listed"] = dict(ylisted)
    if args.only in (None, "csotd"):
        cplan = plan_csotd()
        partial = ["%04d-%02d" % k for k, v in cplan.items() if v["partial"]]
        show("CSOTD plan: %d month pages from %04d-%02d to %04d-%02d; %d without a capture after month end" % (len(cplan), cplan and min(cplan)[0], min(cplan)[1], max(cplan)[0], max(cplan)[1], len(partial)))
        fr.extra["csotd_months_without_capture_after_month_end"] = partial
    if args.plan:
        show("plan only: nothing fetched, nothing written")
        return 0
    until = _load_state().get(PAUSE_KEY, 0)
    if until > time.time() and not args.cache_only:
        show("a pause is published in the shared rate file until %s; no request is sent before then" % time.strftime("%H:%M:%S", time.localtime(until)))

    def read_one(g, gname, tag, ts, original, reader, column, ident, alts=(), accept=None, skipped=()):
        html, src, cached = fetch.read(ts, original)
        first_ts, first_why = ts, src
        if html is None and not args.cache_only and re.search(r"answer 4\d\d", src) and not src.endswith("429"):
            for r2 in fetch.alternates(original, ts):         # the earliest capture that can be read
                h2, s2, c2 = fetch.read(r2["timestamp"], r2["original"])
                if h2 is not None:
                    html, src, cached, ts, original = h2, s2, c2, r2["timestamp"], r2["original"]
                    g["pages_read_on_a_later_capture"] = g.get("pages_read_on_a_later_capture", 0) + 1
                    break
        if html is None:
            g["unread"].append([ident, ts, original, src])
            fr.pages.append({"group": gname, "page": ident, "capture": ts, "original": original, "read": False, "reason": src})
            if not args.cache_only:
                show("  [%s %s] %s" % (tag, ident, src))
            return None
        res = reader(html)
        if accept is not None and not accept(res) and alts:         # not a page of this archive at all: the next capture
            g["pages_read_on_a_later_capture"] = g.get("pages_read_on_a_later_capture", 0) + 1
            return read_one(g, gname, tag, alts[0]["timestamp"], alts[0]["original"], reader, column, ident, alts[1:], accept,
                            list(skipped) + [[ts, res[0]]])
        rule, items, drops = res[0], res[1], res[2]
        rec = {"group": gname, "page": ident, "capture": ts, "original": original, "source": src, "read": True,
               "rule": rule, "picks": len(items), "fetched_this_run": not cached}
        if ts != first_ts:
            rec["earlier_capture_not_readable"] = [first_ts, first_why]
        if skipped:
            rec["earlier_captures_not_a_stillcool_page"] = [list(x) for x in skipped]
        fr.pages.append(rec)
        g["pages_read"] += 1
        g["pages_read_from_cache"] += 1 if cached else 0
        g["rules"][rule] += 1
        g["dropped_links"].update(drops)
        if not items:
            g["pages_without_picks"].append([ident, ts, original])
        fr.add(gname, column, items, src)
        fr.tick()
        if g["pages_read"] % 25 == 0:
            show("  %s: %d of %d pages read, %d picks so far, %d network fetches" % (gname, g["pages_read"], g["pages_planned"], len(fr.out), fetch.network))
        return res

    try:
        if ybest is not None:
            weeks = sorted((i for i in ybest if i[0] == "week"), key=lambda i: i[1])
            g = fr.group("yahoo-week", len(weeks))
            mism = []
            for ident in weeks:
                r = ybest[ident]
                res = read_one(g, "yahoo-week", "week", r["timestamp"], r["original"],
                               lambda h, o=r["original"], d=ident[1]: read_yahoo_page(h, o, d), YAHOO, ident[1])
                if res:
                    if res[3]:
                        mism.append([ident[1], res[3]])
                    if res[0] == "dated":
                        for it in res[1]:
                            covered.add(it["date"])
                            window_keys[it["date"]].add(url_key(it["url"]))
            g["printed_date_differs_from_page_date"] = mism
            g["complete"] = not g["unread"]
            fr.flush()
            show("group yahoo-week done: %d of %d read, %d days covered by window pages" % (g["pages_read"], len(weeks), len(covered)))

            # Audit of the gap-fill rule: do one-day pages repeat what the window pages give for the same day?
            # Sample rule: for each calendar quarter from 2002 Q1 to 2006 Q4, the earliest day that a window page gave
            # and that has a one-day page in the archive listing. Their picks join the frame like any other page's.
            sample, seen_q = [], set()
            for d in sorted(covered):
                q = (d[:4], (int(d[5:7]) - 1) // 3)
                if "2002" <= d[:4] <= "2006" and q not in seen_q and ("day", d) in ybest:
                    seen_q.add(q)
                    sample.append(("day", d))
            g = fr.group("yahoo-day-audit", len(sample))
            ov = {"sample_rule": "for each calendar quarter from 2002 Q1 to 2006 Q4, the earliest day that a window page gave and that has a one-day page in the listing",
                  "pages_compared": 0, "same_address": 0, "different": [], "one_day_pages_without_a_pick": []}
            for ident in sample:
                r = ybest[ident]
                res = read_one(g, "yahoo-day-audit", "audit", r["timestamp"], r["original"],
                               lambda h, o=r["original"], d=ident[1]: read_yahoo_page(h, o, d), YAHOO, ident[1])
                if res is None:
                    continue
                day_keys = {url_key(it["url"]) for it in res[1] if it["date"] == ident[1]}
                if not day_keys:
                    ov["one_day_pages_without_a_pick"].append(ident[1])
                    continue
                ov["pages_compared"] += 1
                if day_keys == window_keys[ident[1]]:
                    ov["same_address"] += 1
                else:
                    ov["different"].append([ident[1], sorted(window_keys[ident[1]]), sorted(day_keys)])
            fr.extra["yahoo_day_vs_window_overlap"] = ov
            g["complete"] = not g["unread"]
            fr.flush()
            show("audit: %d one-day pages compared with the window pages, %d gave the same address, %d differed" % (ov["pages_compared"], ov["same_address"], len(ov["different"])))

        if cplan is not None:
            g = fr.group("csotd-months", len(cplan))
            off, empty_run, seen_picks, stopped = collections.Counter(), 0, False, None
            for (yr, mo), r in sorted(cplan.items()):
                ym = "%04d-%02d" % (yr, mo)
                if stopped:                                  # the archive has stopped listing picks
                    g.setdefault("months_not_read_after_the_stop", []).append(ym)
                    continue
                res = read_one(g, "csotd-months", "stillcool", r["timestamp"], r["original"],
                               lambda h, o=r["original"]: read_csotd_page(h, o), CSOTD, ym,
                               alts=r["alts"], accept=lambda res: res[0] != "not-a-stillcool-page")
                if res:
                    for it in res[1]:
                        if it["date"][:7] != ym:
                            off[ym] += 1
                    if res[1]:
                        seen_picks, empty_run = True, 0
                    elif seen_picks:
                        empty_run += 1
                        if empty_run >= CSOTD_EMPTY_STOP:
                            stopped = ym
            g["rows_dated_outside_page_month"] = dict(off)
            if stopped:
                g["stopped_after_month"] = stopped
                g["stop_rule"] = "month pages are read in order and reading stops after %d months in a row that list no pick" % CSOTD_EMPTY_STOP
            g["complete"] = not g["unread"]
            fr.flush()
            show("group csotd-months done: %d of %d read%s" % (g["pages_read"], len(cplan), (", stopped after %s (%d empty months in a row)" % (stopped, CSOTD_EMPTY_STOP)) if stopped else ""))

        if ybest is not None:
            potw = sorted((i for i in ybest if i[0] == "potw"), key=lambda i: i[1])
            g = fr.group("yahoo-potw", len(potw))
            for ident in potw:
                r = ybest[ident]
                read_one(g, "yahoo-potw", "potw", r["timestamp"], r["original"],
                         lambda h, o=r["original"], d=ident[1]: read_yahoo_page(h, o, d), YAHOO, ident[1])
            g["complete"] = not g["unread"]
            fr.flush()
            show("group yahoo-potw done: %d of %d read" % (g["pages_read"], len(potw)))

            days = sorted((i for i in ybest if i[0] == "day"), key=lambda i: i[1])
            need = [i for i in days if i[1] not in covered]
            g = fr.group("yahoo-day", len(need))
            g["pages_listed"] = len(days)
            g["skipped_because_a_weekly_or_window_page_already_gave_the_day"] = len(days) - len(need)
            if args.stop_before_day_pages:
                dates = [i[1] for i in need]
                g["not_read"] = "not read, frame version 1 cutoff"
                g["not_read_count"] = len(dates)
                g["not_read_date_range"] = [dates[0], dates[-1]] if dates else None
                g["not_read_per_year"] = dict(sorted(collections.Counter(d[:4] for d in dates).items()))
                g["not_read_days"] = dates
                fr.extra["frame_version"] = 1
                fr.extra["frame_version_1_cutoff"] = ("one-day pages for days that no weekly or window page gave were not read: %d pages, %s to %s"
                                                      % (len(dates), dates[0] if dates else "-", dates[-1] if dates else "-"))
                show("group yahoo-day NOT READ (frame version 1 cutoff): %d one-day pages for days no weekly or window page gave" % len(dates))
            else:
                for ident in need:
                    r = ybest[ident]
                    read_one(g, "yahoo-day", "day", r["timestamp"], r["original"],
                             lambda h, o=r["original"], d=ident[1]: read_yahoo_page(h, o, d), YAHOO, ident[1])
                g["complete"] = not g["unread"]
                show("group yahoo-day done: %d of %d read" % (g["pages_read"], len(need)))
    except ArchiveUnreachable as e:
        fr.halted = str(e)
        show("HALTED: %s" % e)
    for name, wanted in (("yahoo-week", ybest is not None), ("yahoo-day-audit", ybest is not None), ("csotd-months", cplan is not None), ("yahoo-potw", ybest is not None), ("yahoo-day", ybest is not None)):
        if wanted and name not in fr.groups:
            fr.group(name, None)["not_started"] = True
    final = fr.flush()
    show("wrote %d picks to %s" % (len(final), OUT))
    show(json.dumps(json.load(open(RUNLOG))["picks_per_year"]))
    return 3 if fr.halted else 0


def main():
    ap = argparse.ArgumentParser(description="Build the Yahoo Picks and Cool Site of the Day frame from Wayback captures.")
    ap.add_argument("--plan", action="store_true", help="list the pages to read (cached CDX listings, or CDX requests if none) and stop")
    ap.add_argument("--cache-only", action="store_true", help="read only pages already in the cache; make no page request")
    ap.add_argument("--only", choices=("yahoo", "csotd"))
    ap.add_argument("--stop-before-day-pages", action="store_true", help="frame version 1: do not read one-day pages for days no weekly or window page gave; list them as not read")
    ap.add_argument("--max-fetch", type=int, default=None, help="stop fetching after this many page requests (testing); cached pages are still read")
    ap.add_argument("--retry-failed", action="store_true", help="ask again for captures that earlier answered 4xx")
    sys.exit(run(ap.parse_args()))


if __name__ == "__main__":
    main()
