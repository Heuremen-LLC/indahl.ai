#!/usr/bin/env python3
"""newsletter_send.py (10 Nov 2026): the weekly changes email, sent every Tuesday through Cloudflare Email Sending (heuremen.com: DKIM, SPF and
DMARC pass, bounces to cf-bounce.heuremen.com), the same path, pacing and guards as iris_index/notices/qia/cf_drafts_20261105/send_guarded.py.

  python3 -I newsletter_send.py                      dry run (the default): the edition, its subject and the count of subscribers. Nothing sent.
  python3 -I newsletter_send.py --send [--cap N]     send the edition to every subscriber not yet sent it
  --week YYYY-WW        the edition's week (default: the last complete Tuesday-to-Tuesday week, weekly.py)
  --edition FILE        a hand-written edition replacing the generated body (plain text). FILE.html beside it, if present, is the HTML part,
                        otherwise the HTML part is built from the text. The edition key is the file name, so it is never sent twice.
                        A web issue, --edition newsletter/issue_N.md (10 Nov 2026), is the same Markdown file that builds indahl.ai/newsletter/N
                        (newsletter_pages.py): the text and HTML parts come from it, with the web address at the top, and the subject is its title.
                        A relative FILE is read from the working folder, else from ~/bones-forge.
  --to-self             one email to the Heuremen inbox (the From address) and nobody else, with a dummy unsubscribe token

Guards (send_guarded.py): --cap N emails per run (default 60); 25 to 75 s apart; after every 20 sends it reads Cloudflare's own delivery records for
today and STOPS if more than 2 of the last 20 bounced; it stops on throttle, auth failure or any error (no retry through a throttle).
Every email: plain text plus simple HTML, a personal unsubscribe link in the body, List-Unsubscribe with List-Unsubscribe-Post (one click, RFC 8058).
Subscriber addresses are read from the private KV at send time and are never printed or written: the log and progress files name the token prefix.
Progress and log live in ~/bones-forge/newsletter/ (outside every repository)."""
import json, os, random, re, subprocess, sys, time, html, urllib.request, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); NS = '034b2ec99c3843099b3d5888d9e246d0'   # INDAHL_INQUIRIES
OUT = os.path.expanduser('~/bones-forge/newsletter'); PROG, LOG = os.path.join(OUT, 'sent.progress'), os.path.join(OUT, 'send.log')
FROM, FROM_NAME, SUBJECT = 'Indahl@heuremen.com', 'Heuremen LLC', 'Heuremen LLC weekly'   # subject: the owner's placeholder until the newsletter has a name
SITE = 'https://indahl.ai'
A = sys.argv[1:]
def arg(k, d=None): return A[A.index(k) + 1] if k in A else d
SEND, SELF = '--send' in A, '--to-self' in A; CAP = int(arg('--cap', 60))
ENV = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')


def log(s):
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, 'a') as f: f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + s + '\n')


def wr(*a):
    r = subprocess.run(['npx', 'wrangler', *a], cwd=W, env=ENV, capture_output=True, text=True, timeout=180)
    return r.returncode, re.sub(r'\x1b\[[0-9;]*m', '', r.stdout + r.stderr)


def subscribers():
    """[(token, address)] from the private KV, oldest first. Never printed."""
    rc, out = wr('kv', 'key', 'list', '--prefix', 'nl:', '--namespace-id', NS, '--remote')
    if rc: raise SystemExit('newsletter: the subscriber list could not be read (wrangler kv key list failed)')
    ks = json.loads(out[out.index('['):])
    subs = [(k['name'][3:], (k.get('metadata') or {}).get('e'), (k.get('metadata') or {}).get('at', '')) for k in ks]
    bad = [t for t, e, a in subs if not e]
    if bad: raise SystemExit('newsletter: %d subscriber record(s) carry no address in their metadata; nothing sent' % len(bad))
    return [(t, e) for t, e, a in sorted(subs, key=lambda x: x[2])]


def edition():
    """(key, text, html or None) of what goes out."""
    ef = arg('--edition')
    if ef and not os.path.isabs(ef) and not os.path.exists(ef): ef = os.path.join(os.path.expanduser('~/bones-forge'), ef)
    if ef and ef.endswith('.md'):   # a web issue: the file behind indahl.ai/newsletter/N
        import newsletter_pages as NP
        global SUBJECT
        md = open(ef, encoding='utf-8').read(); n = NP.number_of(ef); title = NP.parse(md)[0]
        if n is None: raise SystemExit('newsletter: a web issue file is named issue_N.md; nothing sent')
        if title: SUBJECT = title
        return 'edition-' + os.path.basename(ef), NP.text(md, n), NP.email_html(md, n)
    if ef:
        t = open(ef, encoding='utf-8').read(); hf = ef + '.html' if os.path.exists(ef + '.html') else (os.path.splitext(ef)[0] + '.html' if os.path.exists(os.path.splitext(ef)[0] + '.html') and not ef.endswith('.html') else None)
        return 'edition-' + os.path.basename(ef), t, (open(hf, encoding='utf-8').read() if hf else None)
    import weekly
    wk = arg('--week') or weekly.last_complete_slug()
    return 'week-' + wk, weekly.text(wk), None


def as_html(text):
    """Simple HTML from the plain text: one paragraph per block, links made clickable, nothing else."""
    out = []
    for blk in re.split(r'\n\s*\n', text.strip()):
        b = html.escape(blk).replace('\n', '<br>')
        b = re.sub(r'(https://[^\s<]+)', r'<a href="\1">\1</a>', b)
        out.append('<p>%s</p>' % b)
    return out


def compose(text, htm, tok):
    unsub = '%s/newsletter/unsubscribe?t=%s' % (SITE, tok)
    foot_t = '\n--\nHeuremen LLC\nYou are receiving this because this address was entered in the weekly changes field on indahl.ai.\nUnsubscribe with one click: %s\nPrivacy: %s/privacy\n' % (unsub, SITE)
    t = text.rstrip() + '\n' + foot_t
    body = htm if htm else '\n'.join(as_html(text))
    foot_h = ('<hr><p style="font-size:13px;color:#555">Heuremen LLC<br>You are receiving this because this address was entered in the weekly changes field on indahl.ai.<br>'
              '<a href="%s">Unsubscribe with one click</a> &middot; <a href="%s/privacy">Privacy</a></p>' % (html.escape(unsub), SITE))
    h = '<!doctype html><html><body style="font-family:Georgia,serif;font-size:16px;line-height:1.5;color:#1a1208;max-width:640px">%s%s</body></html>' % (body, foot_h)
    hdr = ['List-Unsubscribe:<%s>' % unsub, 'List-Unsubscribe-Post:List-Unsubscribe=One-Click']
    return t, h, hdr


def statuses(addrs):   # send_guarded.py's delivery check: Cloudflare's own records for today
    subprocess.run(['npx', 'wrangler', 'whoami'], cwd=W, env=ENV, capture_output=True, timeout=120)   # refreshes the hour-long sign-in token
    tok = re.search(r'oauth_token\s*=\s*"([^"]+)"', open(os.path.expanduser('~/Library/Preferences/.wrangler/config/default.toml')).read()).group(1)
    def api(u, b=None):
        r = urllib.request.Request(u, data=json.dumps(b).encode() if b else None, headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
        return json.load(urllib.request.urlopen(r, timeout=60))
    z = api('https://api.cloudflare.com/client/v4/zones?name=heuremen.com')['result'][0]['id']
    s = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT00:00:00Z'); e = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    q = 'query($z: string!, $s: Time!, $e: Time!) { viewer { zones(filter: {zoneTag: $z}) { emailSendingAdaptive(filter: {datetime_geq: $s, datetime_leq: $e}, limit: 10000) { to status errorDetail } } } }'
    for _ in range(2):
        res = api('https://api.cloudflare.com/client/v4/graphql', {'query': q, 'variables': {'z': z, 's': s, 'e': e}})
        if res.get('data'): break
        time.sleep(310)
    st = {}
    for x in res['data']['viewer']['zones'][0]['emailSendingAdaptive']:
        for a in x['to'].split(','): st[a.strip().lower()] = (x['status'], (x.get('errorDetail') or '')[:120])
    return {a: st.get(a, ('no record yet', '')) for a in addrs}


def send_one(to, t, h, hdr):
    cmd = ['send', '--from', FROM, '--from-name', FROM_NAME, '--subject', SUBJECT, '--text', t, '--html', h, '--to', to]
    for x in hdr: cmd += ['--header', x]
    rc, out = wr('email', 'sending', *cmd)
    if 'Authentication error' in out:
        wr('whoami'); time.sleep(5); rc, out = wr('email', 'sending', *cmd)
    ok = rc == 0 and 'Queued for' in out
    err = '' if ok else ' '.join(l.strip() for l in out.splitlines() if 'email.sending' in l or 'ERROR' in l or 'code:' in l)[:300].replace(to, '<to>')
    return ok, err


def main():
    key, text, htm = edition()
    if '@' in re.sub(r'\b(Indahl@heuremen\.com)\b', '', text): raise SystemExit('newsletter: the edition text holds an email address; nothing sent')
    if SELF:
        t, h, hdr = compose(text, htm, '0' * 40)
        if not SEND: print('DRY to-self: would send the %s edition (%d characters of text) to the From inbox only' % (key, len(t))); print(t); return
        ok, err = send_one(FROM, t, h, hdr); log('to-self %s %s %s' % (key, 'ok' if ok else 'STOPPED', err)); print('to-self:', 'queued' if ok else 'FAILED ' + err); return
    subs = subscribers()
    done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
    todo = [(tk, em) for tk, em in subs if '%s:%s' % (key, tk[:12]) not in done]
    print('newsletter: edition %s, subject %r, %d subscriber(s), %d not yet sent this edition; this run sends at most %d' % (key, SUBJECT, len(subs), len(todo), CAP))
    if not SEND:
        t, h, hdr = compose(text, htm, 'x' * 40)
        print('--- DRY RUN: nothing sent, nothing logged. Text part with a placeholder token:\n' + t)
        print('--- headers:', hdr, '\n--- HTML part: %d characters' % len(h)); return
    recent = []
    for n, (tk, em) in enumerate(todo[:CAP], 1):
        t, h, hdr = compose(text, htm, tk); ok, err = send_one(em, t, h, hdr); pk = '%s:%s' % (key, tk[:12])
        if not ok: log('STOPPED %s %s' % (pk, err)); print('STOPPED at', pk, err); sys.exit(2)
        with open(PROG, 'a') as f: f.write(pk + '\n')
        log('ok ' + pk); recent.append(em)
        if n % 20 == 0:
            time.sleep(90)
            try: st = statuses(recent[-20:])
            except Exception as ex: log('STOPPED: delivery check failed (%s)' % type(ex).__name__); print('STOPPED: delivery check failed'); sys.exit(4)
            counts = {}
            for v in st.values(): counts[v[0]] = counts.get(v[0], 0) + 1
            bad = sum(1 for v in st.values() if v[0] not in ('delivered', 'no record yet', 'queued', 'sent', 'pending'))
            log('CHECK last 20: ' + json.dumps(counts))
            if bad > 2: print('STOPPED: more than 2 of the last 20 bounced'); log('STOPPED on bounce guard'); sys.exit(3)
        if n < min(CAP, len(todo)): time.sleep(random.uniform(25, 75))
    if recent:   # the delivery check on the tail of the run
        time.sleep(90)
        try:
            st = statuses(recent[-20:]); counts = {}
            for v in st.values(): counts[v[0]] = counts.get(v[0], 0) + 1
            log('CHECK run end: ' + json.dumps(counts)); print('delivery check:', counts)
        except Exception as ex: log('delivery check failed at run end (%s)' % type(ex).__name__)
    log('run end: %d sent, edition %s' % (len(recent), key)); print('run end: %d sent' % len(recent))


if __name__ == '__main__': main()
