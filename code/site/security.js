// security.js -- accountability and security layers for indahl.ai (10 Nov 2026). Called from worker.js:
//   handleSecurity(req, env, u, ctx)   once per indahl.ai request, before the page map. Returns null for any path that is not its own.
//   finalize(req, env, res)            on every indahl.ai answer: security headers, and an Ed25519 signature on every feed, every /api/ JSON
//                                      answer, every alert receipt, /transparency.json and /build.json.
//   mtaSts(host)                       the MTA-STS policy files for mta-sts.heuremen.com and mta-sts.indahl.ai (RFC 8461).
// Routes
//   /.well-known/security.txt (RFC 9116), /.well-known/indahl-signing-key (PEM), /.well-known/jwks.json (RFC 7517 / 8037)
//   <feed or JSON path>.sig      the detached signature (base64url) of that answer's exact body
//   /r/alert/, /r/alert/<id>, /r/alert/<id>.json     alert receipts, from KV IRIS_BENCH alert_r_* (alert_receipts.py writes them). No script.
//   /transparency, /transparency.json                aggregate numbers, KV IRIS_BENCH transparency (transparency.py writes it, cells under 5
//                                                     already shown as "fewer than 5")
//   /build.json                  the last release record (ship.sh writes KV IRIS_BENCH build_json after the public mirror step)
//   /canary/hook                 our own webhook receiver (the canary). Answers the registration challenge. Stores a delivery in KV
//                                IRIS_BENCH canary_hook_log only when its Ed25519 signature verifies, so nobody else can fill it.
//   /mydata/webhook, /mydata/push, /mydata/alerts    download what we hold (JSON) or delete everything now, with a deletion receipt
//   /mydata/receipt/<id>(.json)  a deletion receipt: the kind of record and the time, nothing else
//   /mydata.js                   the two buttons for this device's notification record (the token lives in this browser only)
// The private key is the worker secret SIGNING_KEY_PEM. It is never logged or returned.
export const SIGNING_KEY = {
  kid: 'f0c0aac503f8211c', alg: 'EdDSA', crv: 'Ed25519', x: "0oTA2BSs50d4B22ZKEKRlAreYyj4VXRy4aoxrlh4hQ0",
  pem: "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA0oTA2BSs50d4B22ZKEKRlAreYyj4VXRy4aoxrlh4hQ0=\n-----END PUBLIC KEY-----\n",
};
const SITE = 'https://indahl.ai';
const enc = new TextEncoder();
const esc = t => String(t == null ? '' : t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const b64u = b => { let s = ''; const a = new Uint8Array(b); for (let i = 0; i < a.length; i++) s += String.fromCharCode(a[i]); return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); };
const unb64u = s => { s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; const r = atob(s); const a = new Uint8Array(r.length); for (let i = 0; i < r.length; i++) a[i] = r.charCodeAt(i); return a; };
const hex = n => [...crypto.getRandomValues(new Uint8Array(n))].map(x => x.toString(16).padStart(2, '0')).join('');
async function sha(s) { const b = await crypto.subtle.digest('SHA-256', enc.encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
const J = (o, status, extra) => new Response(JSON.stringify(o, null, 1), { status: status || 200, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...(extra || {}) } });
const T = (t, extra) => new Response(t, { headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'public, max-age=3600', ...(extra || {}) } });

// ------------------------------------------------------------------------------------------------ signing
let KEY = null;
async function privKey(env) {
  if (KEY) return KEY;
  const pem = env && env.SIGNING_KEY_PEM; if (!pem) return null;
  const der = unb64u(pem.replace(/-----[^-]+-----/g, '').replace(/\s+/g, '').replace(/\+/g, '-').replace(/\//g, '_'));
  try { KEY = await crypto.subtle.importKey('pkcs8', der, { name: 'Ed25519' }, false, ['sign']); }
  catch (e) { KEY = await crypto.subtle.importKey('pkcs8', der, { name: 'NODE-ED25519', namedCurve: 'NODE-ED25519' }, false, ['sign']); }
  return KEY;
}
export async function signBytes(env, bytes) {
  const k = await privKey(env); if (!k) return null;
  return b64u(await crypto.subtle.sign(k.algorithm.name === 'NODE-ED25519' ? { name: 'NODE-ED25519' } : { name: 'Ed25519' }, k, bytes));
}
export async function verifyBytes(bytes, sig) {
  try {
    const k = await crypto.subtle.importKey('raw', unb64u(SIGNING_KEY.x), { name: 'Ed25519' }, false, ['verify']);
    return await crypto.subtle.verify({ name: 'Ed25519' }, k, unb64u(sig), bytes);
  } catch (e) {
    try { const k = await crypto.subtle.importKey('raw', unb64u(SIGNING_KEY.x), { name: 'NODE-ED25519', namedCurve: 'NODE-ED25519' }, false, ['verify']); return await crypto.subtle.verify({ name: 'NODE-ED25519' }, k, unb64u(sig), bytes); }
    catch (e2) { return false; }
  }
}
const SIGNED_JSON = /^\/(api\/.+|r\/alert\/[A-Za-z0-9._~-]+\.json|transparency\.json|build\.json|mydata\/receipt\/d[0-9a-f]{20}\.json)$/;
function wantsSig(path, ct) {
  ct = (ct || '').toLowerCase();
  if (/atom\+xml|rss\+xml|feed\+json/.test(ct)) return true;
  if (/json/.test(ct) && SIGNED_JSON.test(path)) return true;
  if (/json/.test(ct) && path === '/feed.json') return true;
  return false;
}
const SIG_BASE = /^\/(.+\.(xml|json))\.sig$/;

// ------------------------------------------------------------------------------------------------ headers
const CSP = "default-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'";
const BASE_H = { 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'x-content-type-options': 'nosniff', 'referrer-policy': 'strict-origin-when-cross-origin',
  'permissions-policy': 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()', 'x-frame-options': 'DENY' };
export async function finalize(req, env, res) {
  if (!res || res.status === 101) return res;
  const u = new URL(req.url); const h = new Headers(res.headers);
  for (const [k, v] of Object.entries(BASE_H)) if (k === 'strict-transport-security' || !h.has(k)) h.set(k, v);
  if (!h.has('tdm-reservation')) { h.set('tdm-reservation', '1'); h.set('tdm-policy', SITE + '/terms#ai-training'); }
  const ct = h.get('content-type') || '';
  if (/text\/html/i.test(ct) && !h.has('content-security-policy')) h.set('content-security-policy', CSP);
  let body = res.body;
  if (req.method === 'GET' && res.status === 200 && wantsSig(u.pathname, ct) && env && env.SIGNING_KEY_PEM) {
    const buf = new Uint8Array(await res.arrayBuffer()); body = buf;
    const s = await signBytes(env, buf);
    if (s) { h.set('x-indahl-signature-ed25519', s); h.set('x-indahl-key-id', SIGNING_KEY.kid); h.set('link', '<' + SITE + u.pathname + '.sig>; rel="signature"' + (h.get('link') ? ', ' + h.get('link') : ''));
      if (h.has('access-control-allow-origin')) h.set('access-control-expose-headers', 'x-indahl-signature-ed25519, x-indahl-key-id, link'); }
  }
  return new Response(body, { status: res.status, statusText: res.statusText, headers: h });
}

// ------------------------------------------------------------------------------------------------ MTA-STS
const MTA = {
  'mta-sts.heuremen.com': 'version: STSv1\nmode: testing\nmx: aspmx.l.google.com\nmx: *.aspmx.l.google.com\nmax_age: 86400\n',
  'mta-sts.indahl.ai': 'version: STSv1\nmode: testing\nmx: route1.mx.cloudflare.net\nmx: route2.mx.cloudflare.net\nmx: route3.mx.cloudflare.net\nmax_age: 86400\n',
};
export function mtaSts(req, host, u) {
  if (!MTA[host]) return null;
  if (u.pathname === '/.well-known/mta-sts.txt') return new Response(MTA[host], { headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'public, max-age=3600', 'strict-transport-security': 'max-age=31536000', 'x-content-type-options': 'nosniff' } });
  return new Response('Not found\n', { status: 404, headers: { 'content-type': 'text/plain; charset=utf-8', 'x-content-type-options': 'nosniff' } });
}

// ------------------------------------------------------------------------------------------------ shell for worker-rendered pages
function shell(ctx, title, h1, inner) {
  let doc = ctx.PAGES['/inquire-ok'].replace(/<main[\s\S]*<\/main>/, () => '<main class="wrap rp-main">' + inner + '</main>')
    .replace(/<title>[^<]*<\/title>/, () => '<title>' + esc(title) + ' | Heuremen LLC</title>')
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '').replace(/<meta name="robots"[^>]*>/, '');
  if (h1) doc = doc.replace(/<section class="hero[^"]*">[\s\S]*?<\/section>/, () => '<section class="hero slim"><div class="wrap"><h1>' + esc(h1) + '</h1></div></section>');
  return doc;
}
const htmlRes = (doc, status, extra) => new Response(doc, { status: status || 200, headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=60', ...(extra || {}) } });

// ------------------------------------------------------------------------------------------------ alert receipts
const CH = { email: 'email alert', push: 'device notification', webhook: 'webhook' };
const side = s => s ? esc(s.display) + (s.outcome ? ' (' + esc(s.outcome) + ')' : '') : '';
export function renderReceipt(r) {
  const rows = [['Desk', `<a href="/${esc(r.desk)}">${esc(r.desk_name)}</a>`], ['Question', esc(r.question)], ['Before', side(r.before)], ['Now', side(r.now)]];
  if (r.interval) rows.push(['Interval', esc(r.interval[0]) + ' to ' + esc(r.interval[1])]);
  rows.push(['Ledger row', /^\/r\/[A-Za-z0-9._~-]+$/.test(r.ledger_receipt || '') ? `<a href="${esc(r.ledger_receipt)}">${esc(r.ledger_row)}</a>` : esc(r.ledger_row)], ['Row sha256', `<code class="rp-h">${esc(r.ledger_row_sha256)}</code>`],
    ['Found', esc(r.found_at)], ['First sent', esc(r.first_sent_at)], ['Channels', esc((r.channels || []).map(c => CH[c] || c).join(', '))], ['Chain hash', `<code class="rp-h">${esc(r.chain_hash)}</code>`]);
  return '<table class="rp-t">' + rows.map(x => `<tr><th scope="row">${x[0]}</th><td>${x[1]}</td></tr>`).join('') + '</table>';
}
async function alertReceipt(req, env, u, ctx) {
  const KV = env.IRIS_BENCH; if (!KV) return null;
  if (u.pathname === '/r/alert') return Response.redirect(SITE + '/r/alert/', 301);
  if (u.pathname === '/r/alert/') {
    let ix = { receipts: [] }; try { ix = JSON.parse((await KV.get('alert_r_index')) || '{"receipts":[]}'); } catch (e) {}
    const li = (ix.receipts || []).map(r => `<li><a href="/r/alert/${esc(r.id)}">${esc(r.desk_name)}</a>, found ${esc(String(r.found_at || '').slice(0, 16).replace('T', ' '))} UTC, sent by ${esc((r.channels || []).map(c => CH[c] || c).join(', '))}</li>`).join('');
    return htmlRes(shell(ctx, 'Alert receipts', 'Alert receipts', `<section class="legal"><p>Every alert we send by email, device notification or webhook has a public receipt here. A receipt names the desk, the value before and now, the ledger row and its hash, when the change was found and which kinds of channel carried it. It never holds anything about the people who receive it.</p><p>Each receipt is a line in a hash chain that our archive stamps with OpenTimestamps. The JSON copy of each receipt is signed with our <a href="/verify">published key</a>.</p>${li ? '<ul class="ticks">' + li + '</ul>' : '<p>No alert has gone out since receipts began.</p>'}<p class="meta"><a href="/r/">Ledger receipts</a> &middot; <a href="/transparency">Transparency</a></p></section>`));
  }
  const m = /^\/r\/alert\/([A-Za-z0-9._~-]{1,160}?)(\.json)?$/.exec(u.pathname); if (!m) return null;
  if (m[1] === 'index') return htmlRes(ctx.PAGES['/404'], 404);
  const v = await KV.get('alert_r_' + m[1]);
  if (!v) return m[2] ? J({ error: 'no such receipt' }, 404) : htmlRes(ctx.PAGES['/404'], 404);
  if (m[2]) return new Response(v, { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=60', 'access-control-allow-origin': '*' } });
  let r; try { r = JSON.parse(v); } catch (e) { return htmlRes(ctx.PAGES['/404'], 404); }
  return htmlRes(shell(ctx, 'Alert receipt ' + r.id, 'Alert receipt', `<section class="legal"><p>One alert, as it went out. Nothing here is about the people who received it.</p>${renderReceipt(r)}<p class="meta"><a href="/r/alert/${esc(r.id)}.json">JSON</a> (signed, <a href="/verify">how to check</a>) &middot; <a href="/r/alert/">All alert receipts</a></p></section>`));
}

// ------------------------------------------------------------------------------------------------ transparency
const MET = { alerts: 'Alert events', email: 'Alert emails sent', confirm: 'Confirmation emails sent', push: 'Device notifications sent', webhook: 'Webhook deliveries accepted',
  bounces: 'Emails not delivered', unsub_alerts: 'Alert sign-ups removed (unsubscribed, deleted or expired)', unsub_newsletter: 'Newsletter sign-ups removed (unsubscribed or deleted)', deletions: 'Deletions through Your data (also counted in the removals above)',
  webhooks_off: 'Webhooks turned off after failures', webhooks_deleted: 'Webhooks removed (deleted by their owner)', push_removed: 'Device subscriptions removed (turned off, gone or deleted)', refused_signups: 'Sign-ups refused' };
function trTable(head, rows) { return '<div class="tablewrap"><table class="rp-t"><thead><tr>' + head.map(x => `<th scope="col">${esc(x)}</th>`).join('') + '</tr></thead><tbody>' + rows.map(r => '<tr>' + r.map(c => `<td>${esc(c)}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>'; }
export function renderTransparency(d) {
  if (!d || !d.updated) return '<p>The first count has not been written yet.</p>';
  let o = `<p class="meta">Counted ${esc(d.updated.replace('T', ' ').replace('Z', ' UTC'))}, over the last ${esc(d.window_days)} days. Days are UTC.</p>`;
  o += '<h2>Alerts by desk</h2>' + ((d.by_desk || []).length ? trTable(['Day', 'Desk', 'Alert events'], d.by_desk.map(r => [r.day, r.desk_name || r.desk, r.n])) : '<p>No alert events in this window.</p>');
  o += '<h2>Totals in the window</h2><p>Channel totals are not split by day, and each is shown only when it covers at least 5 events and at least 5 different recipients.</p>' + trTable(['What', 'Count'], Object.entries(d.totals || {}).map(([k, v]) => [MET[k] || k, v]));
  if ((d.not_recorded || []).length) o += '<p>Not recorded yet: ' + esc(d.not_recorded.map(k => (MET[k] || k).toLowerCase()).join(', ')) + '. These stay off the table until a count exists.</p>';
  if (d.canary) o += '<h2>Our own test subscriptions</h2>' + trTable(['Channel', 'Last check', 'Result'], d.canary.map(c => [c.channel, c.checked || '', c.result]));
  return o;
}
async function transparency(req, env, u, ctx) {
  const KV = env.IRIS_BENCH; let v = KV ? await KV.get('transparency') : null;
  if (u.pathname === '/transparency.json') return new Response(v || '{}', { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=300', 'access-control-allow-origin': '*' } });
  let d = null; try { d = v ? JSON.parse(v) : null; } catch (e) {}
  const page = ctx.PAGES['/transparency']; if (!page) return null;
  return htmlRes(page.replace('<!--TRANSPARENCY-->', () => renderTransparency(d)), 200, { 'cache-control': 'public, max-age=300' });
}

// ------------------------------------------------------------------------------------------------ canary webhook receiver
async function canaryHook(req, env) {
  if (req.method !== 'POST') return J({ error: 'POST only' }, 405);
  if (parseInt(req.headers.get('content-length') || '0', 10) > 65536) return J({ error: 'too large' }, 413);
  const raw = new Uint8Array(await req.arrayBuffer()); if (raw.length > 65536) return J({ error: 'too large' }, 413);
  let b = {}; try { b = JSON.parse(new TextDecoder().decode(raw)) || {}; } catch (e) { return J({ error: 'json' }, 400); }
  if (typeof b !== 'object') return J({ error: 'json' }, 400);
  if (b.type === 'url_verification' && typeof b.challenge === 'string' && b.challenge.length <= 64) return J({ challenge: b.challenge });
  const ts = req.headers.get('x-indahl-timestamp') || '', sig = req.headers.get('x-indahl-signature-ed25519') || '';
  if (!/^\d{9,11}$/.test(ts) || Math.abs(Date.now() / 1000 - +ts) > 300) return J({ ok: false, stored: false, why: 'timestamp outside five minutes' }, 401);   // a replayed delivery is refused
  const msg = new Uint8Array([...enc.encode(ts + '.'), ...raw]);
  const ed = sig ? await verifyBytes(msg, sig) : false;
  if (!ed) return J({ ok: false, stored: false, why: 'signature does not verify' }, 401);
  let hm = null;
  if (env.CANARY_WH_SECRET) {
    const k = await crypto.subtle.importKey('raw', enc.encode(env.CANARY_WH_SECRET), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const want = 'v1=' + [...new Uint8Array(await crypto.subtle.sign('HMAC', k, msg))].map(x => x.toString(16).padStart(2, '0')).join('');
    hm = want === (req.headers.get('x-indahl-signature') || '');
  }
  const KV = env.IRIS_BENCH; if (!KV) return J({ ok: false, stored: false }, 503); let log = []; try { log = JSON.parse((await KV.get('canary_hook_log')) || '[]'); } catch (e) {}
  const dv = String(req.headers.get('x-indahl-delivery') || '').slice(0, 40);
  if (log.some(x => x.sig === sig.slice(0, 24) || (dv && x.delivery === dv))) return J({ ok: true, stored: false, why: 'already stored' });   // the same delivery twice writes nothing
  if (log.filter(x => Date.now() - Date.parse(x.at) < 60000).length >= 6) return J({ ok: false, stored: false, why: 'at most 6 deliveries a minute' }, 429);   // a hard cap on writes
  log.unshift({ at: new Date().toISOString().replace(/\.\d+Z$/, 'Z'), ts: +ts, delivery: dv, sig: sig.slice(0, 24), events: (Array.isArray(b.events) ? b.events : []).map(e => String((e && e.id) || '').slice(0, 120)).slice(0, 50), ed25519: ed, hmac: hm });
  await KV.put('canary_hook_log', JSON.stringify(log.slice(0, 100)));
  return J({ ok: true });
}

// ------------------------------------------------------------------------------------------------ your data: download or delete
async function delReceipt(env, kind, what) {
  const id = 'd' + hex(10), at = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  await env.INDAHL_INQUIRIES.put('delr:' + id, JSON.stringify({ id, kind, at, what }), { metadata: { kind, at }, expirationTtl: 400 * 86400 });
  return { id, at };
}
async function bumpDown(KV, key) { const n = Math.max(0, parseInt((await KV.get(key)) || '0', 10) - 1); await KV.put(key, String(n)); }
const KIND = { webhook: 'webhook', push: 'device notification', alerts: 'email (alerts and newsletter)' };
async function mydata(req, env, u, ctx) {
  const KV = env.INDAHL_INQUIRIES;
  const rm = /^\/mydata\/receipt\/(d[0-9a-f]{20})(\.json)?$/.exec(u.pathname);
  if (rm) {
    const v = KV && await KV.get('delr:' + rm[1]); if (!v) return rm[2] ? J({ error: 'no such receipt' }, 404) : htmlRes(ctx.PAGES['/404'], 404);
    const r = JSON.parse(v);
    if (rm[2]) return new Response(v, { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
    return htmlRes(shell(ctx, 'Deletion receipt', 'Deletion receipt', `<section class="legal"><p>Receipt <code>${esc(r.id)}</code>. At ${esc(r.at.replace('T', ' ').replace('Z', ' UTC'))} we deleted everything we held for one ${esc(KIND[r.kind] || r.kind)} record: ${esc(r.what)}.</p><p>This receipt holds the kind of record and the time, nothing else. <a href="/mydata/receipt/${esc(r.id)}.json">JSON</a> (signed, <a href="/verify">how to check</a>).</p></section>`), 200, { 'cache-control': 'no-store', 'x-robots-tag': 'noindex', 'referrer-policy': 'no-referrer' });
  }
  if (u.pathname === '/mydata.js') return new Response(MYDATA_JS, { headers: { 'content-type': 'text/javascript; charset=utf-8', 'cache-control': 'no-cache' } });
  const m = /^\/mydata\/(webhook|push|alerts)$/.exec(u.pathname); if (!m) return null;
  if (req.method !== 'POST') return Response.redirect(SITE + '/mydata', 302);
  const org = req.headers.get('Origin'); if (org && org !== SITE) return J({ error: 'origin' }, 403);
  let t = '', a = '';
  if ((req.headers.get('content-type') || '').includes('application/json')) { try { const b = await req.json(); t = String(b.t || ''); a = String(b.a || ''); } catch (e) {} }
  else { try { const f = await req.formData(); t = String(f.get('t') || ''); a = String(f.get('a') || ''); } catch (e) {} }
  const isJ = m[1] === 'push';
  const fail = (msg, st) => isJ ? J({ ok: false, msg }, st) : htmlRes(shell(ctx, 'Your data', 'Your data', `<section class="legal"><p>${esc(msg)}</p></section>`), st, { 'cache-control': 'no-store', 'x-robots-tag': 'noindex', 'referrer-policy': 'no-referrer' });
  if (!/^[0-9a-f]{32,64}$/.test(t) || !['export', 'delete'].includes(a)) return fail('This link is not complete. Use the manage link or the button you were given.', 400);
  const pre = { webhook: 'wh:', push: 'ps:', alerts: 'al:' }[m[1]];
  const v = await KV.get(pre + t); if (!v) return fail('We hold no record for this link. It was deleted, or never made.', 404);
  let r = {}; try { r = JSON.parse(v); } catch (e) {}
  const extra = {};
  if (m[1] === 'alerts' && r.e) { const nt = await KV.get('nlh:' + (await sha('nladdr|' + String(r.e).toLowerCase())).slice(0, 32)); if (nt) { const nv = await KV.get('nl:' + nt); if (nv) { try { extra.newsletter = JSON.parse(nv); } catch (e) {} } } }
  if (a === 'export') {
    const out = { what: 'Everything Heuremen LLC holds for this ' + KIND[m[1]] + ' record, as stored', exported_at: new Date().toISOString(), record: r, ...extra,
      also: m[1] === 'webhook' ? 'A lookup key (a one-way hash of the URL) points to this record. Delivery logs name only the first 8 characters of the token.' : m[1] === 'push' ? 'A lookup key (a one-way hash of the endpoint) points to this record. Logs name only the first 8 characters of the token.' : 'A lookup key (a one-way hash of the address) points to this record. Send logs name only the first 12 characters of the token.' };
    return new Response(JSON.stringify(out, null, 1), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'content-disposition': 'attachment; filename="indahl-' + m[1] + '-data.json"', 'x-robots-tag': 'noindex', 'referrer-policy': 'no-referrer' } });
  }
  let what = '';
  if (m[1] === 'webhook') { await KV.delete('wh:' + t); if (r.u) await KV.delete('whh:' + (await sha('whurl|' + r.u)).slice(0, 32)); await bumpDown(KV, 'whn'); what = 'the address, its secret, its desk choices and its lookup key'; }
  if (m[1] === 'push') { await KV.delete('ps:' + t); if (r.e) await KV.delete('psh:' + (await sha('psend|' + r.e)).slice(0, 32)); await bumpDown(KV, 'psn'); what = 'the device endpoint, its keys, its desk choices and its lookup key'; }
  if (m[1] === 'alerts') {
    await KV.delete('al:' + t); if (r.e) { await KV.delete('alh:' + (await sha('aladdr|' + String(r.e).toLowerCase())).slice(0, 32)); const nk = 'nlh:' + (await sha('nladdr|' + String(r.e).toLowerCase())).slice(0, 32); const nt = await KV.get(nk); if (nt) await KV.delete('nl:' + nt); await KV.delete(nk); }
    what = 'the email address, its alert and newsletter choices and their lookup keys';
  }
  const d = await delReceipt(env, m[1], what);
  if (isJ) return J({ ok: true, gone: true, receipt: d.id, at: d.at, url: SITE + '/mydata/receipt/' + d.id, msg: 'Deleted at ' + d.at + '. Receipt ' + d.id + '.' });
  return htmlRes(shell(ctx, 'Deleted', 'Deleted', `<section class="legal"><p>Deleted at ${esc(d.at.replace('T', ' ').replace('Z', ' UTC'))}: ${esc(what)}. Nothing more will be sent.</p><p>Your deletion receipt: <a href="/mydata/receipt/${esc(d.id)}">${esc(d.id)}</a>. It holds the kind of record and the time, nothing else.</p></section>`), 200, { 'cache-control': 'no-store', 'x-robots-tag': 'noindex', 'referrer-policy': 'no-referrer' });
}
// the device record's token is kept in this browser only (notify.js stores it as hlc_push_t), so the two buttons need a few lines of script
const MYDATA_JS = `(function () {
  var box = document.getElementById('md-push'); if (!box) return;
  var t = null; try { t = localStorage.getItem('hlc_push_t'); } catch (e) {}
  var msg = box.querySelector('.md-msg');
  if (!t) { msg.textContent = 'This browser holds no notification record from indahl.ai.'; return; }
  box.querySelectorAll('button').forEach(function (b) { b.disabled = false; b.addEventListener('click', function () {
    var a = b.getAttribute('data-a'); b.disabled = true;
    fetch('/mydata/push', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ t: t, a: a }) }).then(function (r) {
      if (a === 'export') return r.blob().then(function (x) { var l = document.createElement('a'); l.href = URL.createObjectURL(x); l.download = 'indahl-push-data.json'; document.body.appendChild(l); l.click(); l.remove(); b.disabled = false; });
      return r.json().then(function (j) { msg.textContent = j.msg || ''; if (j.ok) { try { localStorage.removeItem('hlc_push_t'); } catch (e) {} try { caches.open('hlc-push').then(function (c) { c.delete('/push/token'); }); } catch (e) {} if (j.url) { var l = document.createElement('a'); l.href = j.url; l.textContent = ' Open the receipt.'; msg.appendChild(l); } } });
    }).catch(function () { msg.textContent = 'That did not go through. Please try again.'; b.disabled = false; });
  }); });
})();`;

// ------------------------------------------------------------------------------------------------ entry
const SECURITY_TXT = 'Contact: https://indahl.ai/contact\nExpires: 2027-10-31T00:00:00.000Z\nPolicy: https://indahl.ai/security/policy\nAcknowledgments: https://indahl.ai/security/thanks\nCanonical: https://indahl.ai/.well-known/security.txt\nPreferred-Languages: en\n';
export async function handleSecurity(req, env, u, ctx) {
  const p = u.pathname;
  if (p === '/.well-known/security.txt' || p === '/security.txt') return T(SECURITY_TXT);
  if (p === '/.well-known/indahl-signing-key') return T(SIGNING_KEY.pem, { 'access-control-allow-origin': '*' });
  if (p === '/.well-known/jwks.json') return J({ keys: [{ kty: 'OKP', crv: 'Ed25519', alg: 'EdDSA', use: 'sig', kid: SIGNING_KEY.kid, x: SIGNING_KEY.x }] }, 200, { 'cache-control': 'public, max-age=3600', 'access-control-allow-origin': '*' });
  const sm = SIG_BASE.exec(p);
  if (sm && req.method === 'GET') {
    const base = '/' + sm[1]; const ir = await ctx.handle(new Request(SITE + base + u.search, { headers: req.headers }), env);
    const ct = ir.headers.get('content-type') || '';
    if (ir.status !== 200 || !wantsSig(base, ct)) return new Response('No signature for this path.\n', { status: 404, headers: { 'content-type': 'text/plain; charset=utf-8' } });
    const s = await signBytes(env, new Uint8Array(await ir.arrayBuffer())); if (!s) return new Response('Signing is not available.\n', { status: 503, headers: { 'content-type': 'text/plain' } });
    return new Response(s + '\n', { headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store', 'x-indahl-key-id': SIGNING_KEY.kid, 'access-control-allow-origin': '*' } });
  }
  if (p === '/r/alert' || p.startsWith('/r/alert/')) return alertReceipt(req, env, u, ctx);
  if (p === '/transparency' || p === '/transparency.json') return transparency(req, env, u, ctx);
  if (p === '/build.json') { const v = env.IRIS_BENCH ? await env.IRIS_BENCH.get('build_json') : null; return new Response(v || '{}', { status: v ? 200 : 404, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=60', 'access-control-allow-origin': '*' } }); }
  if (p === '/canary/hook') return canaryHook(req, env);
  if (p === '/mydata.js' || p.startsWith('/mydata/')) return mydata(req, env, u, ctx);
  return null;
}
// the webhook and alert manage pages (notify.js, alerts.js) get the two Your data buttons, added to their answer here so those files stay as they are
export async function decorate(req, u, res) {
  const kind = u.pathname === '/webhooks/manage' ? 'webhook' : u.pathname === '/alerts/manage' ? 'alerts' : null;
  if (!kind || res.status !== 200 || !/text\/html/.test(res.headers.get('content-type') || '')) return res;
  let t = u.searchParams.get('t') || '';
  let doc = await res.text();
  if (!/^[0-9a-f]{40}$/.test(t)) { const mm = /name="t" value="([0-9a-f]{40})"/.exec(doc); t = mm ? mm[1] : ''; }
  if (/^[0-9a-f]{40}$/.test(t) && doc.includes('action="' + u.pathname + '"')) {
    const what = kind === 'webhook' ? 'this webhook' : 'this email address (alerts and newsletter)';
    const box = `<form method="post" action="/mydata/${kind}" class="md"><input type="hidden" name="t" value="${t}"><p><strong>Your data.</strong> Download everything we hold for ${what} as JSON, or delete it all now and get a deletion receipt.</p><p><button class="btn" type="submit" name="a" value="export">Download what we hold</button> <button class="btn" type="submit" name="a" value="delete">Delete everything now</button></p></form>`;
    const i = doc.lastIndexOf('</form>'); if (i > 0) doc = doc.slice(0, i + 7) + box + doc.slice(i + 7);
  }
  const hh = new Headers(res.headers); hh.delete('content-length'); hh.set('cache-control', 'no-store'); hh.set('referrer-policy', 'no-referrer');
  return new Response(doc, { status: res.status, headers: hh });
}
