// alerts.js -- outcome alerts door (10 Nov 2026). A reader picks desks (and, on a brand page, an organisation) and gets one email when an outcome
// changes on them. Double opt-in: nothing is sent but the confirmation link until the reader opens it and presses Confirm.
// Storage in the private KV INDAHL_INQUIRIES (the same namespace and guards as newsletter.js):
//   alp:<ptoken>   pending sign-up {e, d, o, at, v}, metadata {e, d, o, at}, expires after 2 days. alerts_send.py emails the confirmation link.
//   al:<token>     confirmed subscriber {e, d, o, at, c, v}, metadata {e, d, o}. Listing the prefix gives the send list in one call.
//   alh:<hash>     the token of a confirmed address, so a second confirmation merges into one record.
//   alrl:<iphash>  sign-ups from one network address this hour (5 at most), a truncated one-way hash, kept 1 hour.
//   alpc:<hash>    confirmation emails asked for one address today (3 at most), so the field cannot be used to flood someone.
// /alerts/confirm?t=  GET one button, POST confirms.   /alerts/manage?t=  GET the desk list, POST saves or unsubscribes.
// /alerts/unsubscribe?t=  GET one button, POST (the button, or a mail program's one-click List-Unsubscribe-Post) deletes the record.
// Nothing here is logged, posted or emailed. Addresses never leave the private KV except to Cloudflare Email Sending at send time.
import { ALERT_DESKS, ALERT_BRANDS } from './alerts_list.js';
import { PRIVACY } from './pages.js';
const EMAIL = /^[^\s@<>"(),;:\\[\]]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?)*\.[A-Za-z]{2,24}$/;
const OK = 'Thank you. We are emailing a confirmation link to this address. Alerts start only after you open it and press Confirm. The link works for two days.';
const MAX_O = 8;
const JS = `(function () {
  document.querySelectorAll('form.al').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      if (!window.fetch || !window.FormData) return;
      ev.preventDefault(); var m = f.querySelector('.al-msg'), b = f.querySelector('button'); b.disabled = true;
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
const tok = () => crypto.randomUUID().replace(/-/g, '') + crypto.randomUUID().replace(/-/g, '').slice(0, 8);
const list = xs => xs.length < 2 ? xs.join('') : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];
const deskNames = d => d.filter(s => ALERT_DESKS[s]).map(s => ALERT_DESKS[s][0]);
const brandNames = o => o.filter(s => ALERT_BRANDS[s]).map(s => ALERT_BRANDS[s][0]);
function what(d, o) {
  const p = [];
  if (d.length) p.push((d.length === 1 ? 'the desk ' : 'the desks ') + list(deskNames(d)));
  if (o.length) p.push('the desks with rows about ' + list(brandNames(o)));
  return list(p);
}
const meta = (e, d, o) => ({ e, d, o });
const fits = (e, d, o) => JSON.stringify(meta(e, d, o)).length <= 1000;

export async function handleAlerts(req, env, u, html, PAGES) {
  const p = u.pathname.replace(/\/+$/, '') || '/';
  if (p === '/alerts.js') return new Response(JS, { headers: { 'content-type': 'text/javascript; charset=utf-8', 'cache-control': 'public, max-age=3600', 'x-content-type-options': 'nosniff' } });
  if (!p.startsWith('/alerts/')) return null;
  const KV = env.INDAHL_INQUIRIES;
  const shell = inner => PAGES['/inquire-ok'].replace(/<main[\s\S]*<\/main>/, () => `<main class="wrap"><section class="closing">${inner}</section></main>`);
  const page = (msg, status) => html(shell(`<p>${msg}</p><p class="actions"><a class="btn" href="/alerts">Outcome alerts</a></p>`), status);
  const T = /^[0-9a-f]{40}$/;
  const readT = async () => { let t = u.searchParams.get('t') || ''; if (req.method === 'POST') { try { const f = await req.formData(); return [String(f.get('t') || t), f]; } catch (e) {} } return [t, null]; };

  if (p === '/alerts/subscribe') {
    const json = (req.headers.get('accept') || '').includes('application/json');
    const out = (ok, msg, status) => json ? new Response(JSON.stringify({ ok, msg }), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } }) : page(esc(msg), status);
    if (req.method !== 'POST') return Response.redirect('https://indahl.ai/alerts', 303);
    let f; try { f = await req.formData(); } catch (e) { return out(false, 'Please enter an email address.', 400); }
    if (String(f.get('website') || '')) return out(true, OK, 200);                      // the bot trap: same answer, nothing stored
    const em = String(f.get('email') || '').trim();
    if (!em || em.length > 160 || !EMAIL.test(em)) return out(false, 'Please enter a full email address, like name@example.org.', 400);
    const d = [...new Set(f.getAll('d').map(String))].filter(s => ALERT_DESKS[s]).sort();
    const o = [...new Set(f.getAll('o').map(String))].filter(s => ALERT_BRANDS[s]).sort().slice(0, MAX_O);
    if (!d.length && !o.length) return out(false, 'Please tick at least one desk.', 400);
    const ip = req.headers.get('cf-connecting-ip') || ''; const rk = 'alrl:' + (await sha('al|' + ip)).slice(0, 32);
    const n = parseInt((await KV.get(rk)) || '0', 10);
    if (n >= 5) return out(false, 'Several sign-ups have come from your connection this hour. Please try again later.', 429);
    await KV.put(rk, String(n + 1), { expirationTtl: 3600 });
    const norm = em.toLowerCase(); const ah = (await sha('aladdr|' + norm)).slice(0, 32);
    const pc = parseInt((await KV.get('alpc:' + ah)) || '0', 10);
    if (pc >= 3) return out(true, OK, 200);                                               // three confirmation emails a day per address at most
    await KV.put('alpc:' + ah, String(pc + 1), { expirationTtl: 86400 });
    if (!fits(norm, d, o)) return out(false, 'That is more than one sign-up can hold. Please tick fewer desks.', 400);
    const at = new Date().toISOString();
    await KV.put('alp:' + tok(), JSON.stringify({ e: norm, d, o, at, v: PRIVACY.version }), { metadata: { e: norm, d, o, at }, expirationTtl: 172800 });
    return out(true, OK, 200);
  }

  if (p === '/alerts/confirm') {
    const [t] = await readT();
    if (!T.test(t)) return page('This confirmation link is not complete. Use the link in the confirmation email.', 400);
    const v = await KV.get('alp:' + t);
    if (!v) return page('This confirmation link has expired or was already used. You can sign up again on any desk page.', 200);
    let r; try { r = JSON.parse(v); } catch (e) { return page('This confirmation link could not be read. Please sign up again.', 400); }
    if (req.method !== 'POST')
      return html(shell(`<p>Confirm outcome alerts for ${esc(what(r.d, r.o))}.</p><form method="post" action="/alerts/confirm"><input type="hidden" name="t" value="${esc(t)}"><button class="btn" type="submit">Confirm</button></form>`), 200);
    const hk = 'alh:' + (await sha('aladdr|' + r.e)).slice(0, 32);
    let ct = await KV.get(hk), cur = null;
    if (ct) { const cv = await KV.get('al:' + ct); if (cv) { try { cur = JSON.parse(cv); } catch (e) {} } }
    if (!cur) { ct = tok(); cur = { e: r.e, d: [], o: [], at: r.at, v: r.v }; }
    let d = [...new Set([...(cur.d || []), ...r.d])].filter(s => ALERT_DESKS[s]).sort();
    let o = [...new Set([...(cur.o || []), ...r.o])].filter(s => ALERT_BRANDS[s]).sort().slice(0, MAX_O);
    if (!fits(r.e, d, o)) { d = r.d; o = r.o; }
    const rec = { e: r.e, d, o, at: cur.at, c: new Date().toISOString(), v: r.v };
    await KV.put('al:' + ct, JSON.stringify(rec), { metadata: meta(r.e, d, o) });
    await KV.put(hk, ct);
    await KV.delete('alp:' + t);
    return html(shell(`<p>Confirmed. We will email this address when an outcome changes on ${esc(what(d, o))}.</p><p class="actions"><a class="btn" href="/alerts/manage?t=${ct}">Manage your alerts</a></p>`), 200);
  }

  if (p === '/alerts/manage') {
    const [t, f] = await readT();
    if (!T.test(t)) return page('This link is not complete. Use the manage link at the foot of any of our alert emails.', 400);
    const v = await KV.get('al:' + t);
    if (!v) return page('This address has no outcome alerts. Nothing more will be sent to it.', 200);
    let r; try { r = JSON.parse(v); } catch (e) { return page('This record could not be read.', 400); }
    let note = '';
    if (req.method === 'POST' && f) {
      if (String(f.get('a') || '') === 'unsubscribe') { await KV.delete('al:' + t); await KV.delete('alh:' + (await sha('aladdr|' + r.e)).slice(0, 32)); return page('You are unsubscribed. Your address has been deleted and no further alert will come.', 200); }
      const d = [...new Set(f.getAll('d').map(String))].filter(s => ALERT_DESKS[s]).sort();
      const o = [...new Set(f.getAll('o').map(String))].filter(s => (r.o || []).includes(s) && ALERT_BRANDS[s]).sort();
      if (!d.length && !o.length) { await KV.delete('al:' + t); await KV.delete('alh:' + (await sha('aladdr|' + r.e)).slice(0, 32)); return page('No desk was ticked, so you are unsubscribed. Your address has been deleted and no further alert will come.', 200); }
      if (fits(r.e, d, o)) { r.d = d; r.o = o; await KV.put('al:' + t, JSON.stringify(r), { metadata: meta(r.e, d, o) }); note = '<p><strong>Saved.</strong></p>'; }
    }
    const box = (n, s, label, on) => `<li><label><input type="checkbox" name="${n}" value="${esc(s)}"${on ? ' checked' : ''}> ${label}</label></li>`;
    const desks = Object.keys(ALERT_DESKS).sort((a, b) => ALERT_DESKS[a][0].localeCompare(ALERT_DESKS[b][0]))
      .map(s => box('d', s, `<strong>${esc(ALERT_DESKS[s][0])}</strong> <span class="meta">${esc(ALERT_DESKS[s][1])}</span>`, (r.d || []).includes(s))).join('');
    const orgs = (r.o || []).filter(s => ALERT_BRANDS[s]).map(s => box('o', s, `<strong>${esc(ALERT_BRANDS[s][0])}</strong> <span class="meta">on ${esc(list(deskNames(ALERT_BRANDS[s][1])))}</span>`, true)).join('');
    return html(shell(`${note}<p>Outcome alerts. Tick the desks you want an email about and press Save.</p><form method="post" action="/alerts/manage" class="al-manage"><input type="hidden" name="t" value="${esc(t)}">`
      + `<ul class="al-list">${desks}</ul>` + (orgs ? `<p>Organisations</p><ul class="al-list">${orgs}</ul>` : '')
      + `<p><button class="btn" type="submit" name="a" value="save">Save</button> <button class="btn" type="submit" name="a" value="unsubscribe">Unsubscribe from all</button></p></form>`), 200);
  }

  if (p === '/alerts/unsubscribe') {
    const [t] = await readT();
    if (!T.test(t)) return page('This unsubscribe link is not complete. Use the link at the foot of any of our alert emails.', 400);
    const v = await KV.get('al:' + t);
    if (req.method === 'POST') {
      if (v) { let e = ''; try { e = JSON.parse(v).e; } catch (x) {} await KV.delete('al:' + t); if (e) await KV.delete('alh:' + (await sha('aladdr|' + e)).slice(0, 32)); }
      return page('You are unsubscribed. Your address has been deleted and no further alert will come.', 200);
    }
    if (!v) return page('This address has no outcome alerts. Nothing more will be sent to it.', 200);
    return html(shell(`<p>Unsubscribe from every outcome alert.</p><form method="post" action="/alerts/unsubscribe"><input type="hidden" name="t" value="${esc(t)}"><button class="btn" type="submit">Unsubscribe</button></form>`), 200);
  }
  return null;
}
