// alerts.js -- outcome alerts door (10 Nov 2026). A reader picks desks (and, on a brand page, an organisation) and gets one email when an outcome
// changes on them. Double opt-in: nothing is sent but the confirmation link until the reader opens it and presses Confirm.
// Storage in the private KV INDAHL_INQUIRIES (the same namespace and guards as newsletter.js):
//   alp:<ptoken>   pending sign-up {e, d, o, all, up, at, v}, metadata {e, d, o, all, up, at}, expires after 2 days. alerts_send.py emails the confirmation link.
//   al:<token>     confirmed subscriber {e, d, o, all, up, at, c, v}, metadata {e, d, o, all, up}. Listing the prefix gives the send list in one call.
//                  all = 1: outcome changes on every desk. up = 1: new desks and first values under the change rule (site updates).
//   alh:<hash>     the token of a confirmed address, so a second confirmation merges into one record.
//   alrl:<iphash>  sign-ups from one network address this hour (5 at most), a truncated one-way hash, kept 1 hour.
//   alpc:<hash>    confirmation emails asked for one address today (3 at most), so the field cannot be used to flood someone.
// /alerts/confirm?t=  GET one button, POST confirms.   /alerts/manage?t=  GET the desk list, POST saves or unsubscribes.
// /alerts/unsubscribe?t=  GET one button, POST (the button, or a mail program's one-click List-Unsubscribe-Post) deletes the record.
// /signup (10 Nov 2026): the one sign-up form in every footer and on /alerts. Boxes nl (weekly newsletter, subscribed at once through
// newsletter.js subscribeNewsletter, single opt-in as before), up, all, d=<desk>, o=<organisation>. Any box but nl goes through the double
// opt-in above. /signup.js is the form's script.
// Nothing here is logged, posted or emailed. Addresses never leave the private KV except to Cloudflare Email Sending at send time.
import { ALERT_DESKS, ALERT_BRANDS } from './alerts_list.js';
import { PRIVACY } from './pages.js';
import { subscribeNewsletter, NL_OK, nlHas, nlAdd, nlRemove } from './newsletter.js';
const EMAIL = /^[^\s@<>"(),;:\\[\]]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?)*\.[A-Za-z]{2,24}$/;
const OK = 'Thank you. We are emailing a confirmation link to this address. Alerts start only after you open it and press Confirm. The link works for two days.';
const MAX_O = 8;
const JS = `(function () {
  document.querySelectorAll('form.al, form.su').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      if (!window.fetch || !window.FormData) return;
      ev.preventDefault(); var m = f.querySelector('.al-msg, .su-msg'), b = f.querySelector('button'); b.disabled = true;
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
function what(d, o, all, up) {
  const p = [];
  if (all) p.push('every desk');
  if (d.length && !all) p.push((d.length === 1 ? 'the desk ' : 'the desks ') + list(deskNames(d)));
  if (o.length && !all) p.push('the desks with rows about ' + list(brandNames(o)));
  return list(p);
}
// the sentence for a record: outcome changes on what it follows, and site updates when up is set
function says(d, o, all, up) {
  const w = what(d, o, all, up); const p = [];
  if (w) p.push('when an outcome changes on ' + w);
  if (up) p.push('when a new desk goes live or a desk publishes its first value');
  return p.join(', and ');
}
const meta = (e, d, o, all, up) => { const m = { e, d, o }; if (all) m.all = 1; if (up) m.up = 1; return m; };
const fits = (e, d, o, all, up) => JSON.stringify({ ...meta(e, d, o, all, up), at: new Date().toISOString() }).length <= 1000;
const flag = (f, k) => String(f.get(k) || '') === '1' ? 1 : 0;
const json = (ok, msg, status) => new Response(JSON.stringify({ ok, msg }), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

// The double opt-in step for one sign-up: rate limits, then a pending record that alerts_send.py emails a confirmation link for.
// Returns {ok, msg, status}. A third confirmation email in a day answers ok and stores nothing, as before.
async function pendAlerts(KV, em, d, o, all, up, ip) {
  const rk = 'alrl:' + (await sha('al|' + ip)).slice(0, 32);
  const n = parseInt((await KV.get(rk)) || '0', 10);
  if (n >= 5) return { ok: false, msg: 'Several sign-ups have come from your connection this hour. Please try again later.', status: 429 };
  await KV.put(rk, String(n + 1), { expirationTtl: 3600 });
  const norm = em.toLowerCase(); const ah = (await sha('aladdr|' + norm)).slice(0, 32);
  if (!fits(norm, d, o, all, up)) return { ok: false, msg: 'That is more than one sign-up can hold. Please tick fewer desks.', status: 400 };
  const pc = parseInt((await KV.get('alpc:' + ah)) || '0', 10);
  if (pc >= 3) return { ok: true, msg: OK, status: 200 };                               // three confirmation emails a day per address at most
  await KV.put('alpc:' + ah, String(pc + 1), { expirationTtl: 86400 });
  const at = new Date().toISOString();
  const rec = { e: norm, d, o, at, v: PRIVACY.version }; if (all) rec.all = 1; if (up) rec.up = 1;
  await KV.put('alp:' + tok(), JSON.stringify(rec), { metadata: { ...meta(norm, d, o, all, up), at }, expirationTtl: 172800 });
  return { ok: true, msg: OK, status: 200 };
}
const BOTH = 'Thank you. The weekly newsletter will come to this address every Tuesday, starting now. For the alerts and updates, we are emailing a confirmation link. They start only after you open it and press Confirm. The link works for two days.';

export async function handleAlerts(req, env, u, html, PAGES) {
  const p = u.pathname.replace(/\/+$/, '') || '/';
  if (p === '/alerts.js' || p === '/signup.js') return new Response(JS, { headers: { 'content-type': 'text/javascript; charset=utf-8', 'cache-control': 'public, max-age=3600', 'x-content-type-options': 'nosniff' } });
  if (!p.startsWith('/alerts/') && p !== '/signup') return null;
  const KV = env.INDAHL_INQUIRIES;
  const shell = inner => PAGES['/inquire-ok'].replace(/<main[\s\S]*<\/main>/, () => `<main class="wrap"><section class="closing">${inner}</section></main>`);
  const page = (msg, status) => html(shell(`<p>${msg}</p><p class="actions"><a class="btn" href="/alerts">Email updates</a></p>`), status);
  const T = /^[0-9a-f]{40}$/;
  const readT = async () => { let t = u.searchParams.get('t') || ''; if (req.method === 'POST') { try { const f = await req.formData(); return [String(f.get('t') || t), f]; } catch (e) {} } return [t, null]; };
  const ip = req.headers.get('cf-connecting-ip') || '';

  if (p === '/signup' || p === '/alerts/subscribe') {   // /alerts/subscribe stays for pages cached before the combined form
    const wantJson = (req.headers.get('accept') || '').includes('application/json');
    const out = (ok, msg, status) => wantJson ? json(ok, msg, status) : page(esc(msg), status);
    if (req.method !== 'POST') return Response.redirect('https://indahl.ai/alerts', 303);
    let f; try { f = await req.formData(); } catch (e) { return out(false, 'Please enter an email address.', 400); }
    const nl = p === '/signup' && flag(f, 'nl');
    const d = [...new Set(f.getAll('d').map(String))].filter(s => ALERT_DESKS[s]).sort();
    const o = [...new Set(f.getAll('o').map(String))].filter(s => ALERT_BRANDS[s]).sort().slice(0, MAX_O);
    const all = flag(f, 'all'), up = flag(f, 'up');
    const alerts = d.length || o.length || all || up;
    if (String(f.get('website') || '')) return out(true, nl && alerts ? BOTH : nl ? NL_OK : OK, 200);   // the bot trap: same answer, nothing stored
    const em = String(f.get('email') || '').trim();
    if (!em || em.length > 160 || !EMAIL.test(em)) return out(false, 'Please enter a full email address, like name@example.org.', 400);
    if (!nl && !alerts) return out(false, p === '/signup' ? 'Please tick at least one box.' : 'Please tick at least one desk.', 400);
    let a = null, n = null;
    if (nl) n = await subscribeNewsletter(env, em, ip);                                  // single opt-in, at once, the same path as /newsletter/subscribe
    if (alerts) a = await pendAlerts(KV, em, d, o, all, up, ip);   // with every desk ticked, the desks and organisations are kept but not needed
    if (n && a) {
      if (n.ok && a.ok) return out(true, BOTH, 200);
      if (n.ok) return out(false, 'The weekly newsletter will come to this address every Tuesday, starting now. The alerts and updates did not go through: ' + a.msg, a.status);
      if (a.ok) return out(false, 'The newsletter did not go through: ' + n.msg + ' ' + a.msg, n.status);
      return out(false, a.msg, a.status);
    }
    const r = n || a; return out(r.ok, r.msg, r.status);
  }

  if (p === '/alerts/confirm') {
    const [t] = await readT();
    if (!T.test(t)) return page('This confirmation link is not complete. Use the link in the confirmation email.', 400);
    const v = await KV.get('alp:' + t);
    if (!v) return page('This confirmation link has expired or was already used. You can sign up again at the foot of any page.', 200);
    let r; try { r = JSON.parse(v); } catch (e) { return page('This confirmation link could not be read. Please sign up again.', 400); }
    if (req.method !== 'POST')
      return html(shell(`<p>Confirm email alerts ${esc(says(r.d || [], r.o || [], r.all, r.up))}.</p><form method="post" action="/alerts/confirm"><input type="hidden" name="t" value="${esc(t)}"><button class="btn" type="submit">Confirm</button></form>`), 200);
    const hk = 'alh:' + (await sha('aladdr|' + r.e)).slice(0, 32);
    let ct = await KV.get(hk), cur = null;
    if (ct) { const cv = await KV.get('al:' + ct); if (cv) { try { cur = JSON.parse(cv); } catch (e) {} } }
    if (!cur) { ct = tok(); cur = { e: r.e, d: [], o: [], at: r.at, v: r.v }; }
    const all = cur.all || r.all ? 1 : 0, up = cur.up || r.up ? 1 : 0;
    let d = [...new Set([...(cur.d || []), ...(r.d || [])])].filter(s => ALERT_DESKS[s]).sort();
    let o = [...new Set([...(cur.o || []), ...(r.o || [])])].filter(s => ALERT_BRANDS[s]).sort().slice(0, MAX_O);
    if (!fits(r.e, d, o, all, up)) { d = r.d || []; o = r.o || []; }
    const rec = { e: r.e, d, o, at: cur.at, c: new Date().toISOString(), v: r.v }; if (all) rec.all = 1; if (up) rec.up = 1;
    await KV.put('al:' + ct, JSON.stringify(rec), { metadata: meta(r.e, d, o, all, up) });
    await KV.put(hk, ct);
    await KV.delete('alp:' + t);
    return html(shell(`<p>Confirmed. We will email this address ${esc(says(d, o, all, up))}.</p><p class="actions"><a class="btn" href="/alerts/manage?t=${ct}">Manage your email</a></p>`), 200);
  }

  if (p === '/alerts/manage') {
    const [t, f] = await readT();
    if (!T.test(t)) return page('This link is not complete. Use the manage link at the foot of any of our alert emails.', 400);
    const v = await KV.get('al:' + t);
    if (!v) return page('This address has no alerts. Nothing more will be sent to it.', 200);
    let r; try { r = JSON.parse(v); } catch (e) { return page('This record could not be read.', 400); }
    const drop = async () => { await KV.delete('al:' + t); await KV.delete('alh:' + (await sha('aladdr|' + r.e)).slice(0, 32)); };
    let note = '';
    if (req.method === 'POST' && f) {
      if (String(f.get('a') || '') === 'unsubscribe') { await drop(); await nlRemove(env, r.e); return page('You are unsubscribed from every alert and from the weekly newsletter. Your address has been deleted and no further email will come.', 200); }
      // the address in this record is confirmed, so ticking the newsletter here adds it at once
      const nl = flag(f, 'nl'); if (nl) await nlAdd(env, r.e); else await nlRemove(env, r.e);
      const all = flag(f, 'all'), up = flag(f, 'up');
      const d = [...new Set(f.getAll('d').map(String))].filter(s => ALERT_DESKS[s]).sort();
      const o = [...new Set(f.getAll('o').map(String))].filter(s => (r.o || []).includes(s) && ALERT_BRANDS[s]).sort();
      if (!d.length && !o.length && !all && !up) {
        await drop();
        return page('No alert was ticked, so your alerts are deleted and no further alert will come. ' + (nl ? 'The weekly newsletter still comes every Tuesday.' : 'You are not on the weekly newsletter.'), 200);
      }
      if (fits(r.e, d, o, all, up)) {
        r.d = d; r.o = o; delete r.all; delete r.up; if (all) r.all = 1; if (up) r.up = 1;
        await KV.put('al:' + t, JSON.stringify(r), { metadata: meta(r.e, d, o, all, up) }); note = '<p><strong>Saved.</strong></p>';
      }
    }
    const onNl = await nlHas(env, r.e);
    const box = (n, s, label, on) => `<li><label><input type="checkbox" name="${n}" value="${esc(s)}"${on ? ' checked' : ''}> ${label}</label></li>`;
    const desks = Object.keys(ALERT_DESKS).sort((a, b) => ALERT_DESKS[a][0].localeCompare(ALERT_DESKS[b][0]))
      .map(s => box('d', s, `<strong>${esc(ALERT_DESKS[s][0])}</strong> <span class="meta">${esc(ALERT_DESKS[s][1])}</span>`, (r.d || []).includes(s))).join('');
    const orgs = (r.o || []).filter(s => ALERT_BRANDS[s]).map(s => box('o', s, `<strong>${esc(ALERT_BRANDS[s][0])}</strong> <span class="meta">on ${esc(list(deskNames(ALERT_BRANDS[s][1])))}</span>`, true)).join('');
    const top = box('nl', '1', 'Weekly newsletter, every Tuesday', onNl) + box('up', '1', 'New desks and new data', !!r.up) + box('all', '1', 'Outcome changes on every desk', !!r.all);
    return html(shell(`${note}<p>Your email from indahl.ai. Tick what you want and press Save. With every desk ticked, the desk list below is not needed.</p><form method="post" action="/alerts/manage" class="al-manage"><input type="hidden" name="t" value="${esc(t)}">`
      + `<ul class="al-list">${top}</ul><p>Outcome changes on these desks</p>`
      + `<ul class="al-list">${desks}</ul>` + (orgs ? `<p>Organisations</p><ul class="al-list">${orgs}</ul>` : '')
      + `<p><button class="btn" type="submit" name="a" value="save">Save</button> <button class="btn" type="submit" name="a" value="unsubscribe">Unsubscribe from everything</button></p></form>`), 200);
  }

  if (p === '/alerts/unsubscribe') {
    const [t] = await readT();
    if (!T.test(t)) return page('This unsubscribe link is not complete. Use the link at the foot of any of our alert emails.', 400);
    const v = await KV.get('al:' + t);
    if (req.method === 'POST') {
      if (v) { let e = ''; try { e = JSON.parse(v).e; } catch (x) {} await KV.delete('al:' + t); if (e) await KV.delete('alh:' + (await sha('aladdr|' + e)).slice(0, 32)); }
      return page('You are unsubscribed from every alert. Your address has been deleted from the alerts list and no further alert will come. The weekly newsletter has its own unsubscribe link in each issue.', 200);
    }
    if (!v) return page('This address has no alerts. Nothing more will be sent to it.', 200);
    return html(shell(`<p>Unsubscribe from every alert and update email.</p><form method="post" action="/alerts/unsubscribe"><input type="hidden" name="t" value="${esc(t)}"><button class="btn" type="submit">Unsubscribe</button></form>`), 200);
  }
  return null;
}
