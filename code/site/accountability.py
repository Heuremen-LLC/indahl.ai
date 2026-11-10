#!/usr/bin/env python3
"""accountability.py (10 Nov 2026): the accountability pages of indahl.ai, the SECRECORDS check on our own domains, and the release record.

Build hook (build_site.py, one line after notify.apply):
  apply(PAGES, page, hero_slim, HOME, cssv)
    /verify            the published Ed25519 key and copy-paste checks in Python and Node (security.js signs, sign.py signs webhooks)
    /reproduce         how to check a release against the public repository with /build.json
    /transparency      aggregate counts (the worker fills <!--TRANSPARENCY--> from KV transparency, written by transparency.py)
    /security/self     SECRECORDS's own checks run on indahl.ai, heuremen.com and heuremen.org, with the desk's outcome labels
    /security/policy   how to report, good-faith safe harbour, scope
    /security/thanks   people who reported a security issue and asked to be credited (security_thanks.json)
    /mydata            download what we hold about you, or delete everything now (security.js holds the handlers)
    and a short section with these links on /security

  python3 accountability.py selfcheck [--out FILE]   run the SECRECORDS checks on our domains, write security_self.json (or FILE)
  python3 accountability.py buildinfo                after a ship's public mirror step: write ledger/builds/build_<commit>.json and KV build_json
  python3 accountability.py pages-sha [DIR]          the pages hash of /build.json, from DIR (a clone of the public repo) or from this folder
  python3 accountability.py gate                     the pages exist, keep the public-copy rules, and /security/self matches security_self.json
Python 3.9, standard library only."""
import datetime as D, hashlib, html, json, os, re, ssl, subprocess, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE); sys.path.insert(0, HERE)
SELF = os.path.join(HERE, 'security_self.json'); THANKS = os.path.join(HERE, 'security_thanks.json'); KEY = json.load(open(os.path.join(HERE, 'signing_key.json')))
E = lambda s: html.escape(str(s), quote=True)
DOMAINS = ['indahl.ai', 'heuremen.com', 'heuremen.org']
HEADERS = [('strict-transport-security', 'Strict-Transport-Security'), ('content-security-policy', 'Content-Security-Policy'), ('x-content-type-options', 'X-Content-Type-Options'),
           ('referrer-policy', 'Referrer-Policy'), ('permissions-policy', 'Permissions-Policy'), ('x-frame-options', 'X-Frame-Options')]
UA = 'heuremen-secrecords/0.1 (+https://indahl.ai/secrecords)'


# ------------------------------------------------------------------ SECRECORDS on ourselves
def _desk_checks():
    """the desk's own hsts_class, spf_class and doh, taken from secrecords_tick.py as written (its top level starts a run, so only the defs are read)"""
    src = open(os.path.join(B, 'secrecords_index', 'secrecords_tick.py')).read()
    body = src[src.index('def hsts_class'):src.index('# gate')]
    g = {}
    exec('import os, re, json, time, ssl, urllib.request, urllib.error, urllib.parse\nUA = %r\n' % UA + body, g)
    return g


def _headers(dom):
    """headers of the first answer to https://DOMAIN/ (no redirect followed, as the desk reads), and of the final page after redirects"""
    g = _desk_checks(); out = {}
    try:
        st, hsts, loc = g['base_read']('https://%s/?door=1' % dom)   # ?door=1: the answer an outside visitor gets (our own network sees the house view)
        out['first'] = {'status': st, 'location': loc, 'hsts': hsts}
    except Exception as e: out['first'] = {'error': type(e).__name__}
    try:
        r = urllib.request.urlopen(urllib.request.Request('https://%s/?door=1' % dom, headers={'User-Agent': UA}), timeout=20, context=ssl.create_default_context())
        out['final'] = {'url': r.geturl(), 'status': r.status, 'headers': {k: r.headers.get(k) for k, _ in HEADERS}}
    except urllib.error.HTTPError as e: out['final'] = {'url': e.geturl(), 'status': e.code, 'headers': {k: e.headers.get(k) for k, _ in HEADERS}}
    except Exception as e: out['final'] = {'error': type(e).__name__}
    return out


def selfcheck(out=SELF):
    g = _desk_checks(); res = {'read_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'desk': 'SECRECORDS', 'plan': 'https://indahl.ai/secrecords', 'domains': {}}
    fetch = lambda n: g['doh'](n)
    for d in DOMAINS:
        h = _headers(d); hs = (h.get('first') or {}).get('hsts')
        hc, hwhy = g['hsts_class'](hs) if 'error' not in h.get('first', {}) else ('NOT_COMPARABLE', 'the request failed')
        sc, swhy, n = g['spf_class'](d, fetch)
        mail = {}
        for name, typ, pre in (('_dmarc.' + d, 'TXT', 'v=DMARC1'), ('_mta-sts.' + d, 'TXT', 'v=STSv1'), ('_smtp._tls.' + d, 'TXT', 'v=TLSRPTv1')):
            t = g['doh'](name); mail[name] = None if t is None else next((x for x in t if x.startswith(pre)), '')
        mx = g['doh'](d, 'MX')
        res['domains'][d] = {'hsts_header': hs, 'hsts_class': hc, 'hsts_note': hwhy, 'spf_class': sc, 'spf_note': swhy, 'spf_lookups': n, 'headers': h, 'mail_records': mail}
    json.dump(res, open(out, 'w'), indent=1, sort_keys=True); print('selfcheck: written', out)
    for d, v in res['domains'].items(): print('  %-14s HSTS preload %s (%s) | SPF %s (%s lookups)' % (d, v['hsts_class'], v['hsts_note'] or 'read', v['spf_class'], v['spf_lookups']))
    return res


def self_body(res):
    if not res: return '<p>The first self-check has not run yet.</p>'
    WORD = {'AGREE': 'AGREE', 'DISAGREE': 'DISAGREE', 'NOT_COMPARABLE': 'NOT_COMPARABLE'}
    o = ['<section class="legal">',
         '<p>We run the checks of our <a href="/secrecords">SECRECORDS desk</a> on our own domains, with the same code and the same outcome labels the desk prints for other domains. '
         'The desk reads two claims. A Strict-Transport-Security header that states preload is held against the preload list requirements (a max-age of at least 31,536,000 seconds and includeSubDomains). '
         'An SPF record is held against the limit of 10 DNS lookups. AGREE means the record can do what it states. DISAGREE means it cannot. NOT_COMPARABLE means there is no statement to read or the read failed.</p>',
         '<p class="meta">Read %s UTC, as a visitor from outside our network sees each domain.</p>' % E(res['read_at'].replace('T', ' ').replace('Z', '')),
         '<div class="tablewrap"><table class="rp-t sec-t"><thead><tr><th scope="col">Domain</th><th scope="col">HSTS preload</th><th scope="col">SPF</th></tr></thead><tbody>']
    for d, v in res['domains'].items():
        hs = WORD.get(v['hsts_class'], v['hsts_class']) + ((', ' + E(v['hsts_note'])) if v.get('hsts_note') else '')
        sp = WORD.get(v['spf_class'], v['spf_class']) + ((', ' + E(v['spf_note'])) if v.get('spf_note') else '') + (', DNS lookups counted: %d' % v['spf_lookups'] if v.get('spf_lookups') is not None else '')
        o.append('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (E(d), hs, sp))
    o.append('</tbody></table></div>')
    o.append('<h2>Response headers</h2><p>The headers of the page each domain serves at its address, after any redirect. heuremen.com redirects to indahl.ai before our server code runs, so its column shows the indahl.ai page. These are not desk claims. They show what each answer sends.</p>')
    o.append('<div class="tablewrap"><table class="rp-t sec-t"><thead><tr><th scope="col">Header</th>' + ''.join('<th scope="col">%s</th>' % E(d) for d in res['domains']) + '</tr></thead><tbody>')
    for k, lab in HEADERS:
        cells = []
        for d, v in res['domains'].items():
            f = (v['headers'].get('final') or {}); hv = (f.get('headers') or {}).get(k)
            cells.append('<td>%s</td>' % (('<code>%s</code>' % E(hv[:160])) if hv else ('not sent' if 'error' not in f else 'not read')))
        o.append('<tr><th scope="row">%s</th>%s</tr>' % (E(lab), ''.join(cells)))
    o.append('</tbody></table></div>')
    o.append('<h2>Mail policy records</h2><p>Whether each domain publishes a DMARC policy, an MTA-STS record and a TLS reporting record. Records are read through DNS over HTTPS.</p>')
    o.append('<div class="tablewrap"><table class="rp-t sec-t"><thead><tr><th scope="col">Record</th><th scope="col">Published</th></tr></thead><tbody>')
    for d, v in res['domains'].items():
        for name, val in v['mail_records'].items():
            o.append('<tr><th scope="row">%s</th><td>%s</td></tr>' % (E(name), ('<code>%s</code>' % E(re.sub(r'mailto:[^,;\s]+', '(a reporting address)', val))) if val else ('not published' if val == '' else 'not read')))
    o.append('</tbody></table></div>')
    o.append('<p>What we fix ourselves is what our own server code sends. Changes to DNS records and to heuremen.org, which is served by GitHub Pages, are decided by the owner of each domain and are listed in our records until they are made. '
             'The checks are rerun after every change to these headers.</p><p class="meta"><a href="/security">Security</a> &middot; <a href="/security/policy">Reporting policy</a> &middot; <a href="/verify">Signatures</a></p></section>')
    return ''.join(o)


# ------------------------------------------------------------------ pages
PY = '''import base64, urllib.request
from cryptography.hazmat.primitives.serialization import load_pem_public_key

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "verify"}))

key = load_pem_public_key(get("https://indahl.ai/.well-known/indahl-signing-key").read())
r = get("https://indahl.ai/feed.xml")
body = r.read()
sig = r.headers["x-indahl-signature-ed25519"]
key.verify(base64.urlsafe_b64decode(sig + "=" * (-len(sig) % 4)), body)
print("signature ok")'''
NODE = '''const crypto = require("crypto")

async function main() {
  const pem = await (await fetch("https://indahl.ai/.well-known/indahl-signing-key")).text()
  const r = await fetch("https://indahl.ai/feed.xml")
  const body = Buffer.from(await r.arrayBuffer())
  const sig = Buffer.from(r.headers.get("x-indahl-signature-ed25519"), "base64url")
  console.log(crypto.verify(null, body, crypto.createPublicKey(pem), sig) ? "signature ok" : "SIGNATURE FAILED")
}
main()'''
PYHOOK = '''# in your receiver, with the raw request body and headers
msg = headers["x-indahl-timestamp"].encode() + b"." + raw_body
sig = headers["x-indahl-signature-ed25519"]
key.verify(base64.urlsafe_b64decode(sig + "=" * (-len(sig) % 4)), msg)'''
NODEHOOK = '''// in your receiver, with the raw request body as a Buffer
const msg = Buffer.concat([Buffer.from(req.headers["x-indahl-timestamp"] + "."), rawBody])
const ok = crypto.verify(null, msg, crypto.createPublicKey(pem), Buffer.from(req.headers["x-indahl-signature-ed25519"], "base64url"))'''


def verify_body():
    return f'''<section class="legal">
<p>We sign what we publish with one Ed25519 key. A valid signature shows that a feed, an API answer, an alert receipt or a webhook came from us and was not changed on the way.</p>
<h2>The key</h2>
<p>Key id <code>{E(KEY["kid"])}</code>, created {E(KEY["created"][:10])}. Public key as PEM at <a href="/.well-known/indahl-signing-key">/.well-known/indahl-signing-key</a> and as a JSON Web Key Set at <a href="/.well-known/jwks.json">/.well-known/jwks.json</a>. The same key is printed here:</p>
<pre><code>{E(KEY["pem"].strip())}</code></pre>
<h2>What is signed</h2>
<ul class="ticks">
<li>Every feed: <a href="/feed.xml">feed.xml</a>, <a href="/feed.json">feed.json</a>, the corrections feed, each desk's changes feed, each organisation feed, the newsletter feed and the changelog feed.</li>
<li>Every JSON answer of the <a href="/api">API</a> under /api/.</li>
<li>Every <a href="/r/alert/">alert receipt</a> as JSON, <a href="/transparency.json">transparency.json</a>, <a href="/build.json">build.json</a> and each deletion receipt.</li>
<li>Every webhook delivery, beside the shared-secret signature it already carries.</li>
</ul>
<p>A signed answer carries the header <code>x-indahl-signature-ed25519</code> (the signature of the exact body bytes, base64url) and <code>x-indahl-key-id</code>. The same signature is also served on its own at the same address with <code>.sig</code> added, for example <a href="/feed.xml.sig">/feed.xml.sig</a>. A feed can change between two requests, so the header of the same answer is the exact pair.</p>
<h2>Check a feed in Python</h2>
<p>Needs the <a href="https://github.com/pyca/cryptography">cryptography</a> package (<a href="https://pypi.org/project/cryptography/">PyPI</a>).</p>
<pre><code>{E(PY)}</code></pre>
<h2>Check a feed in Node</h2>
<p>Node 18 or later, no packages.</p>
<pre><code>{E(NODE)}</code></pre>
<h2>Check a webhook delivery</h2>
<p>For a webhook the signed message is the timestamp header, a full stop and the raw body, the same message the shared-secret signature covers.</p>
<pre><code>{E(PYHOOK)}</code></pre>
<pre><code>{E(NODEHOOK)}</code></pre>
<p>If we ever replace this key, the new key is published here and in the JSON Web Key Set beside the old one, and the change is listed in the <a href="/corrections">corrections log</a>.</p>
</section>'''


def reproduce_body():
    return '''<section class="legal">
<p>Each release writes a record at <a href="/build.json">/build.json</a>: the commit of our site source, the commit of the public repository that holds the same release, a fingerprint of everything the release deployed, the result line of every gate it passed, the time it shipped and a hash of every served page. The record is signed with our <a href="/verify">published key</a>.</p>
<h2>Check a release against the public repository</h2>
<pre><code>curl -s https://indahl.ai/build.json -o build.json
git clone https://github.com/Heuremen-LLC/indahl.ai
cd indahl.ai
git checkout "$(python3 -c 'import json; print(json.load(open("../build.json"))["public_commit"])')"
python3 code/site/accountability.py pages-sha .
python3 -c 'import json; print(json.load(open("../build.json"))["pages_sha256"])'</code></pre>
<p>The two lines printed last are equal when every served page in the public repository is byte for byte the page that release built. The hash is SHA-256 over the sorted list of each page path and its own SHA-256.</p>
<h2>Compare the live site with the repository</h2>
<pre><code>python3 code/site/accountability.py compare-live .</code></pre>
<p>This fetches each page from indahl.ai and prints any page whose bytes differ from the file in the repository. Pages the server fills at the moment of the request (the weekly page, the transparency counts, receipts read from storage) are listed as filled live and are not compared.</p>
<h2>What cannot be rebuilt from the repository alone</h2>
<p>The pages are built from desk data folders that the desk code reads from the public sources each desk names. The repository holds the build code in code/site, the desk code in code/, and the pages it produced. Rerunning a desk reads its sources again on a later day, so a rebuild matches a release where the sources have not changed since. The comparison above needs no rerun.</p>
</section>'''


def policy_body():
    return '''<section class="legal">
<h2>How to report</h2>
<p>Use the <a href="/contact">inquiry form</a> and choose Security report as the reason. Tell us what you found, where, and how to see it again. We reply to every report, say when we have fixed it, and tell you before we publish anything about it.</p>
<h2>Scope</h2>
<p>In scope: indahl.ai and its pages, feeds, API and forms, heuremen.org, heuremen.com, and the public repositories of Heuremen LLC on GitHub and Hugging Face. Out of scope: denial of service and load tests, social engineering of anyone, physical access, spam, and the services we use (Cloudflare, GitHub, Google, Zenodo), which have their own programs.</p>
<h2>Good-faith safe harbour</h2>
<p>If you research in good faith within this policy, we will not take legal action against you and will not ask anyone else to. Good faith means you stop as soon as you can show the issue, you do not read, keep, change or delete data that is not yours, you do not degrade the service for others, and you give us reasonable time to fix the issue before you disclose it. We aim to fix within 90 days and will agree a date with you.</p>
<p>We do not pay rewards. With your permission we credit you on our <a href="/security/thanks">thanks page</a>, by the name you choose, the same way our <a href="/corrections">corrections log</a> credits outside readers who ask to be named.</p>
<h2>Contact file</h2>
<p>Our contact details for security reports are also published at <a href="/.well-known/security.txt">/.well-known/security.txt</a>.</p>
</section>'''


def thanks_body():
    try: rows = json.load(open(THANKS))
    except Exception: rows = []
    li = ''.join('<li>%s, %s: %s</li>' % (E(r['name']), E(r['date']), E(r['what'])) for r in rows if r.get('credit'))
    return ('<section class="legal"><p>People outside Heuremen LLC who reported a security issue to us and asked to be credited are listed here, newest first, with the date and a line on what they found. '
            'We list a name only when the person asks to be named, as our <a href="/corrections">corrections log</a> does.</p>'
            + ('<ul class="ticks">' + li + '</ul>' if li else '<p>No outside security report has been received yet.</p>')
            + '<p class="meta"><a href="/security/policy">How to report</a></p></section>')


def transparency_body():
    return ('<section class="legal"><p>Counts of what our alerts, newsletter and follow channels did, for everyone together. No count is about one person. Any number under 5 is shown as fewer than 5, and a channel total also needs at least 5 different recipients, so a small count cannot point to anyone. '
            'Our own test subscriptions, which we use to check that alerts arrive, are left out of every count and reported on their own at the end.</p>'
            '<!--TRANSPARENCY-->'
            '<p class="meta"><a href="/transparency.json">JSON</a> (signed, <a href="/verify">how to check</a>) &middot; <a href="/r/alert/">Alert receipts</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/mydata">Your data</a></p></section>')


def mydata_body():
    return ('<section class="legal"><p>You can download everything we hold for your sign-up as a JSON file, or delete all of it at once. Each deletion gives you a receipt with its time. The receipt holds the kind of record and the time, nothing else.</p>'
            '<h2>Email alerts and the newsletter</h2><p>Open the manage link in any alert email from us. The buttons are under the list of desks.</p>'
            '<h2>Webhooks</h2><p>Open the manage link you were given when you registered the webhook. The buttons are under the desk list.</p>'
            '<h2>Notifications on this device</h2><div class="md" id="md-push"><p><button class="btn" type="button" data-a="export" disabled>Download what we hold</button> <button class="btn" type="button" data-a="delete" disabled>Delete everything now</button></p><span class="md-msg" aria-live="polite"></span></div>'
            '<p>The device record is found by a token kept in this browser, so these two buttons work in the browser where you turned notifications on.</p>'
            '<p class="meta"><a href="/privacy">Privacy</a> &middot; <a href="/transparency">Transparency</a></p></section>')


def apply(PAGES, page, hero_slim, HOME=None, cssv=''):
    try: res = json.load(open(SELF))
    except Exception: res = None
    add = {
        '/verify': ('Verify Our Signatures | Heuremen LLC', 'The Ed25519 key that signs indahl.ai feeds, API answers, alert receipts and webhooks, and how to check a signature in Python and Node.', verify_body(), 'Verify', 'Check that what you received came from us'),
        '/reproduce': ('Reproduce a Release | Heuremen LLC', 'How to check an indahl.ai release against the public repository with the signed release record.', reproduce_body(), 'Reproduce', 'Check a release against the public repository'),
        '/transparency': ('Transparency: Alerts, Sign-ups and Deletions | Heuremen LLC', 'Aggregate counts of alerts sent by desk and channel, bounces, unsubscribes, deletions and our own test subscriptions.', transparency_body(), 'Transparency', 'What our alerts and sign-ups did, for everyone together'),
        '/security/self': ('Our Own Security Records | Heuremen LLC', 'The SECRECORDS desk checks run on indahl.ai, heuremen.com and heuremen.org, with the desk outcome labels.', self_body(res), 'Our Own Records', 'The SECRECORDS checks, run on our domains'),
        '/security/policy': ('Security Reporting Policy and Safe Harbour | Heuremen LLC', 'How to report a security issue to Heuremen LLC, what is in scope, and our good-faith safe harbour.', policy_body(), 'Reporting Policy', 'How to report, what is in scope, and safe harbour'),
        '/security/thanks': ('Security Thanks | Heuremen LLC', 'People who reported a security issue to Heuremen LLC and asked to be credited.', thanks_body(), 'Thanks', 'People who reported a security issue and asked to be named'),
        '/mydata': ('Your Data: Download or Delete | Heuremen LLC', 'Download everything indahl.ai holds for your alerts, newsletter, webhook or device notifications, or delete it all now.', mydata_body(), 'Your Data', 'Download what we hold, or delete it all now'),
    }
    for k, (t, d, body, h1, sub) in add.items():
        PAGES[k] = page(k, t, d, body, hero_slim(h1, sub)).replace('@@CSSV@@', cssv)
        if HOME is not None: HOME[k] = '/hermes'
    PAGES['/mydata'] = PAGES['/mydata'].replace('</body>', '<script src="/mydata.js" defer></script>\n</body>', 1)
    sec = ('<h2>Accountability</h2><ul class="ticks"><li><a href="/security/policy">Reporting policy and safe harbour</a></li><li><a href="/security/self">Our own security records</a>, checked with our SECRECORDS desk</li>'
           '<li><a href="/verify">Signatures</a> on feeds, API answers, alert receipts and webhooks</li><li><a href="/reproduce">Reproduce a release</a></li><li><a href="/transparency">Transparency counts</a></li>'
           '<li><a href="/mydata">Your data</a>: download or delete</li><li><a href="/security/thanks">Thanks</a></li></ul>')
    if '/security' in PAGES and 'href="/security/policy"' not in PAGES['/security']:
        d = PAGES['/security']; i = d.find('</section>', d.find('<section class="legal">'))
        if i > 0: PAGES['/security'] = d[:i] + sec + d[i:]
    return len(add)


# ------------------------------------------------------------------ release record
LIVE_FILLED = {'transparency.html', 'week.html', 'inquire-ok.html', 'inquire-error.html', 'inquiry.html', 'respond.html', '404.html'}
def served_pages(root):
    js = os.path.join(HERE, 'pages.js') if os.path.abspath(root) == HERE else os.path.join(root, 'code', 'site', 'pages.js')
    names = re.findall(r"from '\./([^']+\.html)'", open(js).read()) if os.path.exists(js) else []
    if not names: names = [os.path.relpath(os.path.join(dp, f), root) for dp, _, fs in os.walk(root) if '/.git' not in dp and '/code' not in dp for f in fs if f.endswith('.html')]
    return sorted(set(names))


def pages_sha(root=HERE):
    h = hashlib.sha256()
    for n in served_pages(root):
        p = os.path.join(root, n)
        if os.path.exists(p): h.update(('%s %s\n' % (n, hashlib.sha256(open(p, 'rb').read()).hexdigest())).encode())
    return h.hexdigest()


def compare_live(root):
    bad = 0; n = 0
    for name in served_pages(root):
        if name in LIVE_FILLED or name.startswith('week/'): continue
        path = '/' if name == 'index.html' else '/' + name[:-5]
        try: live = urllib.request.urlopen(urllib.request.Request('https://indahl.ai' + path, headers={'User-Agent': 'heuremen-reproduce/1'}), timeout=30).read()
        except Exception as e: print('NOT READ', path, type(e).__name__); bad += 1; continue
        n += 1
        if live != open(os.path.join(root, name), 'rb').read(): print('DIFFERS', path); bad += 1
    print('compare-live: %d pages compared, %d differ or were not read' % (n, bad)); return 1 if bad else 0


def _git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True).stdout.strip()


def buildinfo():
    L = os.path.join(B, 'ledger'); log = os.path.join(L, '.last_ship_gates.txt'); gates = []
    try:
        t = open(log, encoding='utf-8', errors='replace').read()
        sec = t.split('== 3 GATES', 1)[1].split('== 4 COMMIT', 1)[0]
        gates = [re.sub(r'\x1b\[[0-9;]*m', '', l).strip() for l in sec.splitlines() if l.strip()]
    except Exception: pass
    try: ps = json.load(open(os.path.join(L, 'public_push_status.json')))
    except Exception: ps = {}
    try: fp = subprocess.run(['bash', os.path.join(L, 'deploy_hash.sh')], capture_output=True, text=True, timeout=300).stdout.strip()
    except Exception: fp = None
    rec = {'released_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'indahl_ai_commit': _git(HERE, 'rev-parse', 'HEAD'),
           'public_repo': 'https://github.com/Heuremen-LLC/indahl.ai', 'public_commit': _git(os.path.join(B, 'public_mirror', 'indahl.ai'), 'rev-parse', 'HEAD'),
           'public_mirror_ok': bool(ps.get('ok')) and bool(ps.get('site_pages')), 'deploy_fingerprint': fp, 'deployed_fingerprint': (open(os.path.join(B, 'cloudflare-workers', 'heuremen-door', '.last_deploy.sha')).read().strip() if os.path.exists(os.path.join(B, 'cloudflare-workers', 'heuremen-door', '.last_deploy.sha')) else None),
           'pages_sha256': pages_sha(HERE), 'gates': gates, 'gates_passed': bool(gates), 'signing_key_id': KEY['kid'],
           'how_to_check': 'https://indahl.ai/reproduce'}
    os.makedirs(os.path.join(L, 'builds'), exist_ok=True)
    fp_ = os.path.join(L, 'builds', 'build_%s.json' % (rec['indahl_ai_commit'][:12] or 'unknown')); json.dump(rec, open(fp_, 'w'), indent=1)
    sys.path.insert(0, HERE); import alert_receipts as AR
    ok = AR.kv_put('build_json', json.dumps(rec, indent=1))
    print('buildinfo: %s, public %s, %d gate lines, KV %s' % (rec['indahl_ai_commit'][:9], rec['public_commit'][:9], len(gates), 'ok' if ok else 'FAILED'))
    return 0


# ------------------------------------------------------------------ gate
def gate():
    import corrections as C
    bad = []
    need = ['verify.html', 'reproduce.html', 'transparency.html', 'security/self.html', 'security/policy.html', 'security/thanks.html', 'mydata.html']
    for n in need:
        p = os.path.join(HERE, n)
        if not os.path.exists(p): bad.append('missing ' + n); continue
        s = open(p, encoding='utf-8').read()
        txt = re.sub(r'<pre>.*?</pre>|<code>.*?</code>|<script.*?</script>|<style.*?</style>|<head>.*?</head>', ' ', s, flags=re.S)
        txt = re.sub(r'<[^>]+>', ' ', txt); txt = html.unescape(txt)
        main = txt
        if ';' in re.sub(r'&[a-z]+;|&#\d+;', '', main.split('Heuremen LLC reserves')[0]): bad.append(n + ': semicolon in public copy')
        if C.DENY.search(main): bad.append(n + ': house word')
        if re.search(r'(?i)independent reviewer|\bAI assistant|Claude', main): bad.append(n + ': forbidden phrase')
        if n == 'transparency.html' and '<!--TRANSPARENCY-->' not in s: bad.append(n + ': fill marker missing')
    try:
        res = json.load(open(SELF)); s = open(os.path.join(HERE, 'security/self.html'), encoding='utf-8').read()
        for d, v in res['domains'].items():
            if v['hsts_class'] not in s or v['spf_class'] not in s: bad.append('security/self: %s labels not on the page' % d)
    except Exception as e: bad.append('security/self: ' + type(e).__name__)
    print('accountability gate: %d pages; breaches: %d' % (len(need), len(bad)))
    for b in bad: print('  ' + b)
    return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selfcheck']: selfcheck(a[a.index('--out') + 1] if '--out' in a else SELF)
    elif a[:1] == ['buildinfo']: sys.exit(buildinfo())
    elif a[:1] == ['pages-sha']: print(pages_sha(os.path.abspath(a[1]) if len(a) > 1 else HERE))
    elif a[:1] == ['compare-live']: sys.exit(compare_live(os.path.abspath(a[1]) if len(a) > 1 else HERE))
    elif a[:1] == ['gate']: sys.exit(gate())
    else: print(__doc__)
