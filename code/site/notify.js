// notify.js -- the ways to follow indahl.ai besides email (10 Nov 2026): calendar, feeds, webhooks and device notifications.
// Called from worker.js once per request on indahl.ai (handleNotify). Returns null for any path that is not its own.
//   /feed.json                      JSON Feed 1.1 mirror of /feed.xml (built from the worker's own /feed.xml answer, so the two never drift)
//   /calendar.ics, /<desk>/calendar.ics, /newsletter/feed.xml, /changelog.xml, /feeds.opml   files notify.py writes at build time
//   /brand/<org>/changes.xml        Atom: the change entries of every desk with rows about that organisation (alerts.py brand_desks), read live
//                                   from the same desk feeds as /<desk>/changes.xml (KV changes_<desk>, else the copy built with the site)
//   /notify.js                      the "Notify me on this device" button and nothing else
//   /push/key, /push/subscribe, /push/state, /push/update, /push/unsubscribe     Web Push sign-up (VAPID). The sender is push_send.py.
//   /webhooks/register, /webhooks/manage                                         webhook sign-up. The sender is webhooks_send.py.
// Storage in the private KV INDAHL_INQUIRIES, beside the email lists:
//   wh:<token>    webhook {u, k, d, all, s, at, v} (k = signed|slack|discord|teams, s = signing secret, signed only), metadata the same
//                 without s and v (the secret stays in the value). webhooks_send.py adds off (when it turned the webhook off) and f (failed attempts in a row). The token is the
//                 manage link. whh:<hash of url> holds the token, so one URL is registered once. whrl:<ip hash> sign-ups this hour (5).
//   ps:<token>    push subscription {e, k: {p, a}, d, all, at, v} (endpoint, the browser's two public keys, desks), metadata the same
//                 without v. psh:<hash of endpoint> holds the token. psrl:<ip hash> sign-ups this hour (20).
//   whn, psn      running counts, so the lists stay under their caps (2,000 webhooks, 20,000 devices).
// Nothing here logs, posts or emails anything. A webhook URL receives one challenge (signed) or one "connected" message (chat) at
// registration, from this worker, and nothing else until an outcome changes.
import { ALERT_DESKS, ALERT_BRANDS } from './alerts_list.js';
const SITE = 'https://indahl.ai', HUB = 'https://pubsubhubbub.appspot.com/', UA = 'indahl.ai-webhooks/1.0 (+https://indahl.ai/webhooks)';
export const VAPID_PUBLIC = 'BEalaeY6-3MQjKz6jtXAyJT4gkFBK6aQbmA-QhXEDrC9b2d9mAz78AtNkh9tfE44451yttCRvuJoQ1houIzmlfQ';
const PRIVACY_V = '2026-11-10e';
const MAX_WH = 2000, MAX_PS = 20000;
const PUSH_HOSTS = /^(fcm\.googleapis\.com|android\.googleapis\.com|updates\.push\.services\.mozilla\.com|push\.services\.mozilla\.com|web\.push\.apple\.com|[a-z0-9-]+\.push\.apple\.com|[a-z0-9-]+\.notify\.windows\.com|[a-z0-9-]+\.push\.samsungbrowser\.com)$/;

const enc = new TextEncoder();
async function sha(s) { const b = await crypto.subtle.digest('SHA-256', enc.encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
const hex = n => [...crypto.getRandomValues(new Uint8Array(n))].map(x => x.toString(16).padStart(2, '0')).join('');
const esc = t => String(t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const xesc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const unx = t => String(t).replace(/&#(\d+);/g, (m, n) => String.fromCodePoint(+n)).replace(/&#x([0-9a-f]+);/gi, (m, n) => String.fromCodePoint(parseInt(n, 16)))
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&');
const list = xs => xs.length < 2 ? xs.join('') : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];
const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
const deskNames = d => d.filter(s => own(ALERT_DESKS, s)).map(s => ALERT_DESKS[s][0]);
const T = /^[0-9a-f]{40}$/;
const J = (o, status) => new Response(JSON.stringify(o), { status: status || 200, headers: { 'content-type': 'application/json', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' } });

// ------------------------------------------------------------------------------------------------ feeds
function entries(xml) {
  return (String(xml).match(/<entry>[\s\S]*?<\/entry>/g) || []).map(e => ({ xml: e, updated: ((/<updated>([^<]+)<\/updated>/.exec(e) || [])[1] || '') }));
}
async function deskFeed(env, slug) {
  const v = env.IRIS_BENCH ? await env.IRIS_BENCH.get('changes_' + slug) : null;
  if (v) return v;
  if (!env.ASSETS) return '';
  const r = await env.ASSETS.fetch(new Request(SITE + '/' + slug + '/changes.xml'));
  return r.status === 200 ? await r.text() : '';
}
export async function brandFeed(env, slug) {
  if (!own(ALERT_BRANDS, slug)) return null; const b = ALERT_BRANDS[slug];
  const [name, desks] = b;
  const all = [];
  for (const d of desks) for (const e of entries(await deskFeed(env, d))) all.push(e);
  all.sort((a, c) => (a.updated < c.updated ? 1 : a.updated > c.updated ? -1 : 0));
  const upd = (all[0] && all[0].updated) || '2026-11-10T12:04:08Z';
  return '<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><id>tag:indahl.ai,2026:brand:' + xesc(slug) + '</id>'
    + '<title>' + xesc(name) + ': changes on the desks with rows about it</title>'
    + '<subtitle>An entry is posted when the headline of ' + xesc(list(deskNames(desks))) + ' makes a material change under the desk\'s rule.</subtitle>'
    + '<link href="' + SITE + '/brand/' + xesc(slug) + '/changes.xml" rel="self"/><link href="' + HUB + '" rel="hub"/><link href="' + SITE + '/brand/' + xesc(slug) + '" rel="alternate"/>'
    + '<updated>' + upd + '</updated><author><name>Heuremen LLC</name></author>' + all.map(e => e.xml).join('') + '</feed>\n';
}
export function atomToJsonFeed(xml) {
  const head = String(xml).split('<entry>')[0];
  const title = unx((/<title>([^<]*)<\/title>/.exec(head) || [])[1] || 'Heuremen LLC');
  const items = entries(xml).map(({ xml: e, updated }) => {
    const id = unx((/<id>([^<]+)<\/id>/.exec(e) || [])[1] || '');
    const t = unx((/<title>([^<]*)<\/title>/.exec(e) || [])[1] || '');
    const href = unx((/<link href="([^"]+)"\s*\/>/.exec(e) || /<link [^>]*href="([^"]+)"/.exec(e) || [])[1] || SITE + '/');
    const sm = /<summary>([\s\S]*?)<\/summary>/.exec(e), ct = /<content type="html">([\s\S]*?)<\/content>/.exec(e);
    const it = { id, url: href, title: t, date_modified: updated };
    if (ct) it.content_html = unx(ct[1]); else it.content_text = sm ? unx(sm[1]) : t;
    if (sm && ct) it.summary = unx(sm[1]);
    return it;
  });
  return { version: 'https://jsonfeed.org/version/1.1', title, home_page_url: SITE + '/', feed_url: SITE + '/feed.json',
    description: 'New studies, desks and bench rounds on indahl.ai. The same entries as https://indahl.ai/feed.xml.', language: 'en',
    authors: [{ name: 'Heuremen LLC', url: SITE + '/' }], hubs: [{ type: 'WebSub', url: HUB }], items };
}

// ------------------------------------------------------------------------------------------------ webhooks
// The address rules: https only, a host name on the public internet (no IP literal, no localhost or private suffix), the standard port,
// no user name or password in it, at most 500 characters. Workers cannot reach private networks in any case.
export function checkUrl(raw) {
  const s = String(raw || '').trim(), bad = msg => ({ ok: false, msg });
  if (!s) return bad('Please enter the address that should receive the webhook.');
  if (s.length > 500) return bad('That address is longer than 500 characters.');
  let x; try { x = new URL(s); } catch (e) { return bad('That is not a full web address. It should start with https://.'); }
  if (x.protocol !== 'https:') return bad('The address must start with https://.');
  if (x.username || x.password) return bad('Please leave the user name and password out of the address.');
  if (x.port && x.port !== '443') return bad('Please use an address on the standard HTTPS port.');
  const h = x.hostname.toLowerCase().replace(/\.$/, '');
  if (h.startsWith('[') || h.includes(':') || /^[0-9.]+$/.test(h) || /\.\d+$/.test(h)) return bad('Please use a host name, not an IP address.');
  if (h === 'localhost' || !h.includes('.') || /\.(localhost|local|localdomain|internal|intranet|lan|home|corp|private|arpa|test|invalid|example|onion)$/.test(h)) return bad('That host is not on the public internet.');
  if (h === 'indahl.ai' || h.endsWith('.indahl.ai')) return bad('That address is on indahl.ai itself.');
  let k = 'signed';
  if (h === 'hooks.slack.com' && /^\/services\/[A-Za-z0-9]+\/[A-Za-z0-9]+\/[A-Za-z0-9]+$/.test(x.pathname)) k = 'slack';
  else if (/^(discord\.com|discordapp\.com|ptb\.discord\.com|canary\.discord\.com)$/.test(h) && /^\/api\/webhooks\/\d+\/[A-Za-z0-9_-]+$/.test(x.pathname)) k = 'discord';
  else if (h.endsWith('.webhook.office.com') && /^\/webhookb2\//.test(x.pathname)) k = 'teams';
  else if (h === 'hooks.slack.com' || /(^|\.)discord(app)?\.com$/.test(h) || h.endsWith('.webhook.office.com')) return bad('That looks like a Slack, Discord or Teams address, but not a complete incoming-webhook address. Copy it again from the app.');
  return { ok: true, url: x.toString(), kind: k, host: h };
}
export const KIND_NAME = { signed: 'signed JSON', slack: 'Slack', discord: 'Discord', teams: 'Microsoft Teams' };
// The native message for each chat app (the same shapes webhooks_send.py posts)
export function chatBody(kind, text) {
  if (kind === 'discord') return { content: text.slice(0, 1900), allowed_mentions: { parse: [] } };
  if (kind === 'slack') return { text: text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') };   // no mention or link markup from our text
  return { text };   // Slack incoming webhooks and Teams incoming webhooks both take {text}
}
async function post(fetcher, url, body, headers) {
  return fetcher(url, { method: 'POST', redirect: 'manual', headers: { 'content-type': 'application/json', 'user-agent': UA, ...(headers || {}) }, body: JSON.stringify(body), signal: AbortSignal.timeout(10000) });
}
// Ownership check for a signed webhook: one POST with a random challenge, which the address must echo back (the raw text, or {"challenge": ...}).
export async function challenge(url, fetcher) {
  const c = hex(16); let r;
  try { r = await post(fetcher || fetch, url, { type: 'url_verification', challenge: c }, { 'x-indahl-event': 'url_verification' }); }
  catch (e) { return { ok: false, msg: 'We could not reach that address within 10 seconds.' }; }
  if (r.status < 200 || r.status > 299) return { ok: false, msg: 'That address answered with status ' + r.status + ', not 200. It must answer the challenge with status 200.' };
  let t = '';   // at most 4,000 bytes of the answer are read
  try { const rd = r.body.getReader(); let n = 0; const ch = []; while (n < 4000) { const { done, value } = await rd.read(); if (done) break; ch.push(value); n += value.length; } rd.cancel().catch(() => {}); t = new TextDecoder().decode(new Uint8Array(ch.flatMap(c => [...c])).slice(0, 4000)).trim(); } catch (e) {}
  if (t === c) return { ok: true };
  try { if (JSON.parse(t).challenge === c) return { ok: true }; } catch (e) {}
  return { ok: false, msg: 'That address answered, but did not echo the challenge back. See "Ownership check" on this page.' };
}
async function chatHello(kind, url, d, all, fetcher) {
  const text = 'Connected to indahl.ai. This channel will get a message when an outcome changes on ' + (all ? 'any desk' : (d.length === 1 ? 'the desk ' : 'the desks ') + list(deskNames(d))) + '. Heuremen LLC, https://indahl.ai/webhooks';
  let r; try { r = await post(fetcher || fetch, url, chatBody(kind, text)); } catch (e) { return { ok: false, msg: 'We could not reach that address within 10 seconds.' }; }
  if (r.status < 200 || r.status > 299) return { ok: false, msg: KIND_NAME[kind] + ' answered with status ' + r.status + '. Check that the incoming webhook still exists.' };
  return { ok: true };
}
const masked = u => { try { const x = new URL(u); const p = x.pathname; return esc(x.host) + (p.length > 18 ? esc(p.slice(0, 14)) + '&hellip;' : esc(p)); } catch (e) { return ''; } };
const whMeta = r => { const m = { u: r.u, k: r.k, d: r.d, at: r.at }; if (r.all) m.all = 1; if (r.off) m.off = r.off; if (r.f) m.f = r.f; return m; };
async function bump(KV, key, by) { const n = Math.max(0, parseInt((await KV.get(key)) || '0', 10) + by); await KV.put(key, String(n)); return n; }
async function limited(KV, prefix, ip, max) {
  const rk = prefix + (await sha(prefix + '|' + ip)).slice(0, 32); const n = parseInt((await KV.get(rk)) || '0', 10);
  if (n >= max) return true; await KV.put(rk, String(n + 1), { expirationTtl: 3600 }); return false;
}
function pickDesks(f) {
  const all = String(f.get('all') || '') === '1' ? 1 : 0;
  let d = all ? [] : [...new Set(f.getAll('d').map(String))].filter(s => own(ALERT_DESKS, s)).sort();
  if (!all && d.length === Object.keys(ALERT_DESKS).length) return { d: [], all: 1 };
  return { d, all };
}
function deskBoxes(d, all) {
  const box = (n, v, label, on) => `<li><label><input type="checkbox" name="${n}" value="${esc(v)}"${on ? ' checked' : ''}> ${label}</label></li>`;
  return '<ul class="nt-list">' + box('all', '1', '<strong>Every desk</strong>', !!all) + Object.keys(ALERT_DESKS).sort((a, b) => ALERT_DESKS[a][0].localeCompare(ALERT_DESKS[b][0]))
    .map(s => box('d', s, `<strong>${esc(ALERT_DESKS[s][0])}</strong> <span class="meta">${esc(ALERT_DESKS[s][1])}</span>`, (d || []).includes(s))).join('') + '</ul>';
}

async function webhooks(req, env, u, p, ctx, fetcher) {
  const KV = env.INDAHL_INQUIRIES;
  const html0 = ctx.html; ctx = { ...ctx, html: (b, st) => { const r = html0(b, st); const h = new Headers(r.headers); h.set('x-robots-tag', 'noindex'); h.set('referrer-policy', 'no-referrer'); h.set('cache-control', 'no-store'); return new Response(r.body, { status: r.status, headers: h }); } };
  const shell = inner => ctx.PAGES['/inquire-ok'].replace(/<main[\s\S]*<\/main>/, () => `<main class="wrap"><section class="closing">${inner}</section></main>`);
  const page = (msg, status) => ctx.html(shell(`<p>${msg}</p><p class="actions"><a class="btn" href="/webhooks">Webhooks</a></p>`), status);
  const ip = req.headers.get('cf-connecting-ip') || '';
  if (p === '/webhooks/register') {
    if (req.method !== 'POST') return Response.redirect(SITE + '/webhooks', 303);
    let f; try { f = await req.formData(); } catch (e) { return page('Please fill in the form on the webhooks page.', 400); }
    if (String(f.get('website') || '')) return page('Thank you.', 200);   // the bot trap: nothing stored, nothing sent
    const c = checkUrl(f.get('url'));
    if (!c.ok) return page(esc(c.msg), 400);
    const { d, all } = pickDesks(f);
    if (!d.length && !all) return page('Please tick at least one desk, or every desk.', 400);
    if (await limited(KV, 'whrl:', ip, 5)) return page('Several webhooks have been registered from your connection this hour. Please try again later.', 429);
    const hk = 'whh:' + (await sha('whurl|' + c.url)).slice(0, 32);
    if (await KV.get(hk)) return page('This address is already registered. Use the manage link you were given to change or delete it.', 409);
    if (parseInt((await KV.get('whn')) || '0', 10) >= MAX_WH) return page('The webhook list is full for now. Please try again later or use a feed.', 503);
    const chk = c.kind === 'signed' ? await challenge(c.url, fetcher) : await chatHello(c.kind, c.url, d, all, fetcher);
    if (!chk.ok) return page(esc(chk.msg), 400);
    const t = hex(20), at = new Date().toISOString();
    const rec = { u: c.url, k: c.kind, d, at, v: ctx.privacy || PRIVACY_V }; if (all) rec.all = 1; if (c.kind === 'signed') rec.s = 'whsec_' + hex(24);
    if (JSON.stringify(whMeta(rec)).length > 1000) return page('That is more than one webhook can hold. Please tick fewer desks, or every desk.', 400);
    await KV.put('wh:' + t, JSON.stringify(rec), { metadata: whMeta(rec) }); await KV.put(hk, t); await bump(KV, 'whn', 1);
    const manage = SITE + '/webhooks/manage?t=' + t;
    const sec = rec.s ? `<p>Your signing secret. It is shown once, here. Keep it with your receiver and use it to check the <code>X-Indahl-Signature</code> header of each delivery.</p><p><code class="whsec">${esc(rec.s)}</code></p>` : '';
    return ctx.html(shell(`<p><strong>Registered.</strong> ${esc(c.kind === 'signed' ? 'Your address echoed the challenge.' : KIND_NAME[c.kind] + ' accepted our test message.')} It will get a POST when an outcome changes on ${esc(all ? 'any desk' : list(deskNames(d)))}.</p>${sec}`
      + `<p>Your manage link. Keep it private. It is the only way to change or delete this webhook.</p><p><a href="${manage}">${manage}</a></p><p class="actions"><a class="btn" href="/webhooks">Webhooks</a></p>`), 200);
  }
  if (p === '/webhooks/manage') {
    let t = u.searchParams.get('t') || '', f = null;
    if (req.method === 'POST') { try { f = await req.formData(); t = String(f.get('t') || t); } catch (e) {} }
    if (!T.test(t)) return page('This manage link is not complete. Use the link you were given at registration.', 400);
    const v = await KV.get('wh:' + t);
    if (!v) return page('There is no webhook for this link. It was deleted, or never registered.', 404);
    let r; try { r = JSON.parse(v); } catch (e) { return page('This record could not be read.', 400); }
    const hk = 'whh:' + (await sha('whurl|' + r.u)).slice(0, 32);
    let note = '';
    if (req.method === 'POST' && f) {
      const a = String(f.get('a') || '');
      if (a === 'delete') { await KV.delete('wh:' + t); await KV.delete(hk); await bump(KV, 'whn', -1); return page('Deleted. The address and its secret are erased, and nothing more will be sent to it.', 200); }
      const { d, all } = pickDesks(f);
      if (!d.length && !all) note = '<p><strong>Not saved.</strong> Tick at least one desk, or every desk. To stop every delivery, press Delete.</p>';
      else {
        if (a === 'enable' && r.off && await limited(KV, 'whrl:', ip, 5)) note = '<p><strong>Still off.</strong> Several checks have come from your connection this hour. Please try again later. Your desk choices were saved.</p>';
        else if (a === 'enable' && r.off) {
          const chk = r.k === 'signed' ? await challenge(r.u, fetcher) : await chatHello(r.k, r.u, d, all, fetcher);
          if (!chk.ok) note = '<p><strong>Still off.</strong> ' + esc(chk.msg) + '</p>'; else { delete r.off; delete r.f; }
        }
        r.d = d; delete r.all; if (all) r.all = 1;
        if (JSON.stringify(whMeta(r)).length <= 1000) { await KV.put('wh:' + t, JSON.stringify(r), { metadata: whMeta(r) }); if (!note) note = '<p><strong>Saved.</strong></p>'; }
      }
    }
    const status = r.off ? `<p><strong>This webhook is turned off.</strong> Deliveries failed ${esc(String(r.f || 'several'))} times in a row, the last on ${esc(String(r.off).slice(0, 16).replace('T', ' '))} UTC. Fix the receiver, then press Turn back on. ${r.k === 'signed' ? 'We send the challenge again first.' : 'We send one test message first.'}</p>` : '<p>This webhook is on.</p>';
    return ctx.html(shell(`${note}<p>Webhook to <code>${masked(r.u)}</code>, ${esc(KIND_NAME[r.k] || r.k)}, registered ${esc(String(r.at).slice(0, 10))}.</p>${status}`
      + `<form method="post" action="/webhooks/manage"><input type="hidden" name="t" value="${esc(t)}"><p>Send a POST when an outcome changes on</p>${deskBoxes(r.d, r.all)}`
      + `<p><button class="btn" type="submit" name="a" value="save">Save</button> ${r.off ? '<button class="btn" type="submit" name="a" value="enable">Turn back on</button> ' : ''}<button class="btn" type="submit" name="a" value="delete">Delete</button></p></form>`), 200);
  }
  return null;
}

// ------------------------------------------------------------------------------------------------ device notifications (Web Push)
export function checkSub(s) {
  if (!s || typeof s !== 'object') return null;
  const e = String(s.endpoint || ''), k = s.keys || {};
  if (e.length > 600) return null;
  let x; try { x = new URL(e); } catch (er) { return null; }
  if (x.protocol !== 'https:' || x.port || !PUSH_HOSTS.test(x.hostname.toLowerCase())) return null;
  const p = String(k.p256dh || ''), a = String(k.auth || '');
  if (!/^[A-Za-z0-9_-]{80,100}={0,2}$/.test(p) || !/^[A-Za-z0-9_-]{16,32}={0,2}$/.test(a)) return null;
  return { e, k: { p: p.replace(/=+$/, ''), a: a.replace(/=+$/, '') } };
}
const psMeta = r => { const m = { e: r.e, k: r.k, d: r.d }; if (r.all) m.all = 1; return m; };
async function push(req, env, p, ctx) {
  const KV = env.INDAHL_INQUIRIES;
  if (p === '/push/key') return J({ key: VAPID_PUBLIC });
  if (req.method !== 'POST') return J({ ok: false, msg: 'Use POST.' }, 405);
  let b; try { b = await req.json(); } catch (e) { return J({ ok: false, msg: 'That request could not be read.' }, 400); }
  const ip = req.headers.get('cf-connecting-ip') || '';
  const desks = x => [...new Set((Array.isArray(x) ? x : []).map(String))].filter(s => own(ALERT_DESKS, s)).sort();
  const t = String(b.t || '');
  if (p === '/push/subscribe') {
    const s = checkSub(b.sub);
    if (!s) return J({ ok: false, msg: 'This browser gave a subscription we cannot use.' }, 400);
    let d = desks(b.d), all = b.all ? 1 : 0;
    if (!d.length && !all) return J({ ok: false, msg: 'Pick a desk first.' }, 400);
    if (await limited(KV, 'psrl:', ip, 20)) return J({ ok: false, msg: 'Several sign-ups have come from your connection this hour. Please try again later.' }, 429);
    const hk = 'psh:' + (await sha('psend|' + s.e)).slice(0, 32);
    let tok = await KV.get(hk), cur = null;
    if (tok) { const v = await KV.get('ps:' + tok); if (v) { try { cur = JSON.parse(v); } catch (e) {} } }
    if (!cur) { if (parseInt((await KV.get('psn')) || '0', 10) >= MAX_PS) return J({ ok: false, msg: 'The device list is full for now. Please use a feed or email.' }, 503); tok = hex(20); }
    all = all || (cur && cur.all) ? 1 : 0;
    d = all ? [] : [...new Set([...(cur ? cur.d || [] : []), ...d])].sort();
    const rec = { e: s.e, k: s.k, d, at: cur ? cur.at : new Date().toISOString(), v: ctx.privacy || PRIVACY_V }; if (all) rec.all = 1;
    if (JSON.stringify(psMeta(rec)).length > 1000) return J({ ok: false, msg: 'This device follows too many desks to add one more. Choose every desk on /follow instead.' }, 400);
    await KV.put('ps:' + tok, JSON.stringify(rec), { metadata: psMeta(rec) }); await KV.put(hk, tok);
    if (!cur) await bump(KV, 'psn', 1);
    return J({ ok: true, t: tok, d, all });
  }
  if (!T.test(t)) return J({ ok: false, msg: 'This device has no notifications on.' }, 404);
  const v = await KV.get('ps:' + t); let r = null; if (v) { try { r = JSON.parse(v); } catch (e) {} }
  if (!r) return J({ ok: false, gone: true, msg: 'This device has no notifications on.' }, 404);
  const hk = 'psh:' + (await sha('psend|' + r.e)).slice(0, 32);
  const drop = async () => { await KV.delete('ps:' + t); await KV.delete(hk); await bump(KV, 'psn', -1); };
  if (p === '/push/state') return J({ ok: true, d: r.d || [], all: r.all ? 1 : 0 });
  if (p === '/push/resubscribe') {   // the service worker's pushsubscriptionchange: the browser replaced the subscription, the desks stay
    const s = checkSub(b.sub);
    if (!s) return J({ ok: false, msg: 'This browser gave a subscription we cannot use.' }, 400);
    if (await limited(KV, 'psrl:', ip, 20)) return J({ ok: false, msg: 'Too many requests this hour.' }, 429);
    const nh = 'psh:' + (await sha('psend|' + s.e)).slice(0, 32);
    const other = await KV.get(nh); if (other && other !== t && await KV.get('ps:' + other)) return J({ ok: false, msg: 'This subscription belongs to another record.' }, 409);
    r.e = s.e; r.k = s.k;
    if (JSON.stringify(psMeta(r)).length > 1000) return J({ ok: false, msg: 'That subscription is too long to keep.' }, 400);
    if (nh !== hk) await KV.put(nh, t);   // the new index first, so a failure part way never leaves a record without one
    await KV.put('ps:' + t, JSON.stringify(r), { metadata: psMeta(r) });
    if (nh !== hk) await KV.delete(hk);
    return J({ ok: true, d: r.d || [], all: r.all ? 1 : 0 });
  }
  if (p === '/push/unsubscribe') { await drop(); return J({ ok: true, gone: true, msg: 'Notifications are off on this device, and its subscription is deleted.' }); }
  if (p === '/push/update') {
    const d = desks(b.d), all = b.all ? 1 : 0;
    if (!d.length && !all) { await drop(); return J({ ok: true, gone: true, d: [], all: 0 }); }
    r.d = all ? [] : d; delete r.all; if (all) r.all = 1;
    await KV.put('ps:' + t, JSON.stringify(r), { metadata: psMeta(r) });
    return J({ ok: true, d: r.d, all: r.all ? 1 : 0 });
  }
  return null;
}

// The button script. A button carries data-desk="<desk>" or data-desk="all". The device's token is kept in this browser only (localStorage).
export const JS = `(function () {
  var bs = document.querySelectorAll('.np-btn'); if (!bs.length) return;
  var K = 'hlc_push_t', st = null;
  function say(b, t) { var m = b.parentNode.querySelector('.np-msg'); if (m) m.textContent = t; }
  function gt() { try { return localStorage.getItem(K) || ''; } catch (e) { return ''; } }
  function pt(t) { try { if (t) localStorage.setItem(K, t); else localStorage.removeItem(K); } catch (e) {}
    try { caches.open('hlc-push').then(function (c) { return t ? c.put('/push/token', new Response(t)) : c.delete('/push/token'); }); } catch (e) {} }   // the service worker reads it on pushsubscriptionchange
  var ok = 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
  bs.forEach(function (b) { b.hidden = false; if (!ok) { b.disabled = true; say(b, /iP(hone|ad|od)/.test(navigator.userAgent) ? 'On an iPhone or iPad, add indahl.ai to your Home Screen first, then open it from there and press this button.' : 'This browser does not offer notifications.'); } });
  if (!ok) return;
  function post(u, o) { return fetch(u, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(o) }).then(function (r) { return r.json(); }); }
  function on(b) { var d = b.getAttribute('data-desk'); return !!st && (st.all ? true : d !== 'all' && st.d.indexOf(d) >= 0); }
  function draw() { bs.forEach(function (b) { var d = b.getAttribute('data-desk'); b.textContent = on(b) ? (d === 'all' || st.all ? 'Turn off notifications on this device' : 'Stop notifications for this desk on this device') : (d === 'all' ? 'Notify me on this device about every desk' : 'Notify me on this device'); }); }
  function key(s) { var p = '='.repeat((4 - s.length % 4) % 4), r = atob((s + p).replace(/-/g, '+').replace(/_/g, '/')), a = new Uint8Array(r.length); for (var i = 0; i < r.length; i++) a[i] = r.charCodeAt(i); return a; }
  function sub() {
    return navigator.serviceWorker.register('/sw.js', { scope: '/' }).then(function () { return navigator.serviceWorker.ready; }).then(function (reg) {
      return reg.pushManager.getSubscription().then(function (s) { return s || fetch('/push/key').then(function (r) { return r.json(); }).then(function (k) { return reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key(k.key) }); }); });
    });
  }
  function off() { return navigator.serviceWorker.getRegistration('/').then(function (reg) { return reg ? reg.pushManager.getSubscription() : null; }).then(function (s) { return s ? s.unsubscribe() : null; }).catch(function () {}); }
  bs.forEach(function (b) {
    b.addEventListener('click', function () {
      var d = b.getAttribute('data-desk'); b.disabled = true;
      var done = function (m) { b.disabled = false; draw(); if (m) say(b, m); };
      if (on(b)) {
        var rest = (d === 'all' || st.all) ? [] : st.d.filter(function (x) { return x !== d; });
        post(rest.length ? '/push/update' : '/push/unsubscribe', { t: gt(), d: rest }).then(function (r) {
          if (r.gone || !rest.length) { pt(''); st = null; off(); done('Notifications are off on this device.'); } else { st = { d: r.d, all: r.all }; done('This desk is off. Others you picked stay on.'); }
        }).catch(function () { done('That did not go through. Please try again.'); });
        return;
      }
      Notification.requestPermission().then(function (p) {
        if (p !== 'granted') return done('Notifications are blocked for indahl.ai in this browser. Allow them in the site settings to turn them on.');
        return sub().then(function (s) { return post('/push/subscribe', { sub: s.toJSON(), d: d === 'all' ? [] : [d], all: d === 'all' ? 1 : 0, t: gt() }); })
          .then(function (r) { if (!r.ok) return done(r.msg); pt(r.t); st = { d: r.d, all: r.all }; done('On. This device will show a notification when an outcome changes.'); });
      }).catch(function () { done('That did not go through. Please try again.'); });
    });
  });
  var t = gt();
  if (t) post('/push/state', { t: t }).then(function (r) { if (r.ok) { st = { d: r.d, all: r.all }; pt(t); } else if (r.gone) pt(''); draw(); }).catch(draw); else draw();
})();
`;

// ------------------------------------------------------------------------------------------------ the door
const STATIC = { '/calendar.ics': 'text/calendar; charset=utf-8', '/newsletter/feed.xml': 'application/atom+xml; charset=utf-8', '/changelog.xml': 'application/atom+xml; charset=utf-8',
  '/feeds.opml': 'text/x-opml; charset=utf-8' };
export async function handleNotify(req, env, u, ctx, fetcher) {
  const p = u.pathname;
  const H = ctx.H || {};
  const file = async (ct, cc) => { if (!env.ASSETS) return null; const r = await env.ASSETS.fetch(new Request(SITE + p)); if (r.status !== 200) return null; return new Response(r.body, { headers: { ...H, 'content-type': ct, 'cache-control': cc || 'public, max-age=3600', 'access-control-allow-origin': '*' } }); };
  if (STATIC[p]) return file(STATIC[p], p === '/feeds.opml' ? 'public, max-age=3600' : 'public, max-age=600');
  if (/^\/[a-z0-9]+\/calendar\.ics$/.test(p)) return file('text/calendar; charset=utf-8');
  if (p === '/feed.json') {
    const r = await ctx.handle(new Request(SITE + '/feed.xml'), env); const x = await r.text();
    return new Response(JSON.stringify(atomToJsonFeed(x)), { headers: { ...H, 'content-type': 'application/feed+json; charset=utf-8', 'cache-control': 'public, max-age=300', 'access-control-allow-origin': '*' } });
  }
  { const bm = /^\/brand\/([a-z0-9-]{1,80})\/changes\.xml$/.exec(p); if (bm) { const x = await brandFeed(env, bm[1]); if (!x) return null; return new Response(x, { headers: { ...H, 'content-type': 'application/atom+xml; charset=utf-8', 'cache-control': 'public, max-age=300', 'access-control-allow-origin': '*' } }); } }
  if (p === '/notify.js') return new Response(JS, { headers: { 'content-type': 'text/javascript; charset=utf-8', 'cache-control': 'public, max-age=3600', 'x-content-type-options': 'nosniff' } });
  if (p.startsWith('/push/')) return push(req, env, p, ctx);
  if (p.startsWith('/webhooks/')) return webhooks(req, env, u, p.replace(/\/+$/, ''), ctx, fetcher);
  return null;
}
