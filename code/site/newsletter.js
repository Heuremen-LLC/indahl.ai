// newsletter.js -- the weekly changes email door and the /week pages (10 Nov 2026).
// One email field. POST /newsletter/subscribe validates the address, drops bots that fill the hidden "website" box (same answer, nothing stored),
// limits each network address to 5 tries an hour (a truncated one-way hash of it, kept 1 hour, never the address itself) and stores in the private
// KV INDAHL_INQUIRIES:
//   nl:<token>        value {e, at, v}, metadata {e, at}   (the subscriber; listing the prefix gives the send list in one call)
//   nlh:<hash>        the token, so a second sign-up of the same address stores nothing new
// /newsletter/unsubscribe?t=<token>: GET shows one button, POST (the button, or a mail program's one-click List-Unsubscribe-Post) deletes both keys.
// /week and /week/<yyyy-ww>: the copy weekly.py tick put in IRIS_BENCH (week_current, week_<slug>) when there is one, else the built page.
// Nothing here is logged, posted or emailed to anyone. Addresses never leave the private KV except to Cloudflare Email Sending at send time.
const EMAIL = /^[^\s@<>"(),;:\\[\]]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?)*\.[A-Za-z]{2,24}$/;
const OK = 'Thank you. The weekly changes page will come to this address every Tuesday. Every email has a one-click unsubscribe.';
import { PRIVACY } from './pages.js';
const PRIVACY_V = PRIVACY.version;   // 10 Nov: follows the notice version build_site.py sets, so a sign-up records the notice in force
const JS = `(function () {
  document.querySelectorAll('form.nl').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      if (!window.fetch || !window.FormData) return;
      ev.preventDefault(); var m = f.querySelector('.nl-msg'), b = f.querySelector('button'); b.disabled = true;
      fetch(f.action, { method: 'POST', body: new FormData(f), headers: { 'accept': 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (d) { m.textContent = d.msg; if (d.ok) { f.querySelector('input[type=email]').value = ''; } b.disabled = false; })
        .catch(function () { m.textContent = 'That did not go through. Please try again.'; b.disabled = false; });
    });
  });
})();
`;
async function sha(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
const esc = t => String(t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export async function handleWeekly(req, env, u, html, PAGES) {
  const p = u.pathname.replace(/\/+$/, '') || '/';
  if (p === '/newsletter.js') return new Response(JS, { headers: { 'content-type': 'text/javascript; charset=utf-8', 'cache-control': 'public, max-age=3600', 'x-content-type-options': 'nosniff' } });
  if (p === '/week' || /^\/week\/\d{4}-\d{2}$/.test(p)) {
    if (req.method !== 'GET' && req.method !== 'HEAD') return null;
    const v = env.IRIS_BENCH ? await env.IRIS_BENCH.get(p === '/week' ? 'week_current' : 'week_' + p.slice(6)) : null;
    if (!v) return null;   // the built page
    return new Response(v, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=300', 'x-content-type-options': 'nosniff', 'referrer-policy': 'strict-origin-when-cross-origin',
      'x-frame-options': 'DENY', 'tdm-reservation': '1', 'tdm-policy': 'https://indahl.ai/terms#ai-training',
      'content-security-policy': "default-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'" } });
  }
  const page = (msg, status) => html(PAGES['/inquire-ok'].replace(/<main[\s\S]*<\/main>/, () => `<main class="wrap"><section class="closing"><p>${msg}</p><p class="actions"><a class="btn" href="/week">Weekly changes</a></p></section></main>`), status);
  if (p === '/newsletter/subscribe') {
    const json = (req.headers.get('accept') || '').includes('application/json');
    const out = (ok, msg, status) => json ? new Response(JSON.stringify({ ok, msg }), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } }) : page(esc(msg), status);
    if (req.method !== 'POST') return Response.redirect('https://indahl.ai/week', 303);
    let f; try { f = await req.formData(); } catch (e) { return out(false, 'Please enter an email address.', 400); }
    if (String(f.get('website') || '')) return out(true, OK, 200);                       // the bot trap: same answer, nothing stored
    const em = String(f.get('email') || '').trim();
    if (!em || em.length > 160 || !EMAIL.test(em)) return out(false, 'Please enter a full email address, like name@example.org.', 400);
    const ip = req.headers.get('cf-connecting-ip') || ''; const rk = 'nlrl:' + (await sha('nl|' + ip)).slice(0, 32);
    const n = parseInt((await env.INDAHL_INQUIRIES.get(rk)) || '0', 10);
    if (n >= 5) return out(false, 'Several sign-ups have come from your connection this hour. Please try again later.', 429);
    await env.INDAHL_INQUIRIES.put(rk, String(n + 1), { expirationTtl: 3600 });
    const norm = em.toLowerCase(); const hk = 'nlh:' + (await sha('nladdr|' + norm)).slice(0, 32);
    if (await env.INDAHL_INQUIRIES.get(hk)) return out(true, OK, 200);                  // already on the list: nothing new stored
    const tok = crypto.randomUUID().replace(/-/g, '') + crypto.randomUUID().replace(/-/g, '').slice(0, 8);
    const at = new Date().toISOString();
    await env.INDAHL_INQUIRIES.put('nl:' + tok, JSON.stringify({ e: norm, at, v: PRIVACY_V }), { metadata: { e: norm, at } });
    await env.INDAHL_INQUIRIES.put(hk, tok);
    return out(true, OK, 200);
  }
  if (p === '/newsletter/unsubscribe') {
    let t = u.searchParams.get('t') || '';
    if (req.method === 'POST') { try { const f = await req.formData(); t = String(f.get('t') || t); } catch (e) {} }
    if (!/^[0-9a-f]{40}$/.test(t)) return page('This unsubscribe link is not complete. Use the link at the foot of any of our emails.', 400);
    const v = await env.INDAHL_INQUIRIES.get('nl:' + t);
    if (req.method === 'POST') {
      if (v) { let e = ''; try { e = JSON.parse(v).e; } catch (x) {} await env.INDAHL_INQUIRIES.delete('nl:' + t); if (e) await env.INDAHL_INQUIRIES.delete('nlh:' + (await sha('nladdr|' + e)).slice(0, 32)); }
      return page('You are unsubscribed. Your address has been deleted from the list and no further email will come.', 200);
    }
    if (!v) return page('This address is not on the list. Nothing more will be sent to it.', 200);
    return html(PAGES['/inquire-ok'].replace(/<main[\s\S]*<\/main>/, () => `<main class="wrap"><section class="closing"><p>Unsubscribe from the weekly changes email.</p><form method="post" action="/newsletter/unsubscribe"><input type="hidden" name="t" value="${esc(t)}"><button class="btn" type="submit">Unsubscribe</button></form></section></main>`), 200);
  }
  return null;
}
