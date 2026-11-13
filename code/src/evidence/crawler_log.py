"""crawler_log.py: appends the last 24 h of AI-crawler requests to indahl.ai (user agent, status, count) to ~/Documents/Heuremen LLC/EVIDENCE/crawler_log.jsonl.
Shows which crawlers asked for reserved pages after the reservation existed and what they were answered. Token read from the wrangler config, never printed."""
import os, re, json, glob, urllib.request, datetime
E = os.path.expanduser('~/Documents/Heuremen LLC/EVIDENCE/')
tok = None
for p in glob.glob(os.path.expanduser('~/Library/Preferences/.wrangler/config/*.toml')):
    m = re.search(r'oauth_token\s*=\s*"([^"]+)"', open(p).read()); tok = m.group(1) if m else tok
H = {'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'}
def gql(q): return json.loads(urllib.request.urlopen(urllib.request.Request('https://api.cloudflare.com/client/v4/graphql', data=json.dumps({'query': q}).encode(), headers=H), timeout=40).read())
zid = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.cloudflare.com/client/v4/zones?name=indahl.ai', headers=H)).read())['result'][0]['id']
t1 = datetime.datetime.now(datetime.timezone.utc); t0 = t1 - datetime.timedelta(hours=24)
q = '{viewer{zones(filter:{zoneTag:"%s"}){httpRequestsAdaptiveGroups(limit:1000,orderBy:[count_DESC],filter:{datetime_geq:"%s",datetime_leq:"%s"}){count dimensions{userAgent edgeResponseStatus}}}}}' % (zid, t0.strftime('%Y-%m-%dT%H:%M:%SZ'), t1.strftime('%Y-%m-%dT%H:%M:%SZ'))
rows = gql(q)['data']['viewer']['zones'][0]['httpRequestsAdaptiveGroups']
BOT = re.compile(r'GPTBot|ChatGPT|OAI-|ClaudeBot|Claude-|anthropic|CCBot|Bytespider|Amazonbot|PerplexityBot|Google-Extended|Applebot|Meta-External|FacebookBot|cohere|Diffbot|DuckAssist|YouBot|ImagesiftBot|Omgilibot', re.I)
out = [dict(window_end=t1.isoformat(), user_agent=r['dimensions']['userAgent'][:160], status=r['dimensions']['edgeResponseStatus'], requests=r['count']) for r in rows if BOT.search(r['dimensions']['userAgent'] or '')]
with open(E + 'crawler_log.jsonl', 'a') as f:
    for o in out: f.write(json.dumps(o) + '\n')
os.chmod(E + 'crawler_log.jsonl', 0o600)
print('AI-crawler rows appended:', len(out), '| sample:', [(o['user_agent'][:30], o['status'], o['requests']) for o in out[:5]])
