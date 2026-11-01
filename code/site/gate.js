// gate.js -- the indahl.ai engagement gate (24 Oct 2026). Wayfinder: the contact gate "should have an acknowledged NDA form with
// authenticated identity before it ever lands internally."
// Flow: /auth/start -> WorkOS AuthKit (Google, Microsoft or a one-time email code) -> /auth/callback -> a signed session cookie
// -> the verified contact page (NDA acceptance + engagement fields) -> /inquire. Personal email domains are refused after sign-in.
// Secrets (worker config only, never in source): WORKOS_CLIENT_ID, WORKOS_API_KEY, GATE_SECRET. WORKOS_API overrides the API base
// for local tests only.

export const FREEMAIL = new Set(('gmail.com googlemail.com yahoo.com yahoo.co.uk ymail.com outlook.com hotmail.com hotmail.co.uk live.com msn.com ' +
  'icloud.com me.com mac.com aol.com proton.me protonmail.com pm.me gmx.com gmx.net gmx.de mail.com yandex.com yandex.ru ' +
  'qq.com 163.com 126.com sina.com zoho.com tutanota.com tuta.io hey.com fastmail.com mail.ru web.de').split(' '));
const SESSION_S = 45 * 60, STATE_S = 10 * 60;
const METHOD = { GoogleOAuth: 'Google work account', MicrosoftOAuth: 'Microsoft work account', MagicAuth: 'one-time email code', SSO: 'company single sign-on' };

const b64u = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
async function key(env) {
  if (!env.GATE_SECRET || env.GATE_SECRET.length < 32) throw new Error('GATE_SECRET missing');
  return crypto.subtle.importKey('raw', new TextEncoder().encode(env.GATE_SECRET), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
}
export async function sign(env, obj) {
  const body = b64u(new TextEncoder().encode(JSON.stringify(obj)));
  return body + '.' + b64u(await crypto.subtle.sign('HMAC', await key(env), new TextEncoder().encode(body)));
}
export async function verify(env, tok) {
  if (!tok || tok.split('.').length !== 2) return null;
  const [body, mac] = tok.split('.');
  let ok = false;
  try { ok = await crypto.subtle.verify('HMAC', await key(env), unb64u(mac), new TextEncoder().encode(body)); } catch (e) { return null; }
  if (!ok) return null;
  const o = JSON.parse(new TextDecoder().decode(unb64u(body)));
  return o.exp && o.exp > Math.floor(Date.now() / 1000) ? o : null;
}
const cookie = (req, name) => ((req.headers.get('cookie') || '').split(/;\s*/).find(c => c.startsWith(name + '=')) || '').slice(name.length + 1) || null;
const setCookie = (name, val, maxAge, path = '/') => `${name}=${val}; Max-Age=${maxAge}; Path=${path}; HttpOnly; Secure; SameSite=Lax`;
const api = env => env.WORKOS_API || 'https://api.workos.com';
const redirectUri = (req, env) => (env.GATE_ORIGIN ? env.GATE_ORIGIN.replace(/\/$/, '') + '/auth/callback' : new URL('/auth/callback', req.url).toString());

export async function session(req, env) {
  try { return await verify(env, cookie(req, 'ig_s')); } catch (e) { return null; }
}

// The /agree step: both documents read to the end and both boxes checked. Kept in a signed cookie (2 hours) and written into the
// inquiry record only when the inquiry is submitted; nothing is stored at this step.
const AGREE_S = 2 * 60 * 60;
export async function agreement(req, env) {
  try { const a = await verify(env, cookie(req, 'ig_a')); return a && a.k === 'agree' ? a : null; } catch (e) { return null; }
}
export async function agree(req, env, versions, fail) {
  if (req.method !== 'POST') return null;
  let f; try { f = await req.formData(); } catch (e) { return fail('That could not be read. Please try again.'); }
  if (f.get('nda') !== 'yes' || f.get('privacy') !== 'yes' || f.get('terms') !== 'yes') return fail('The agreements and the Terms must be read and checked to continue.');
  if (f.get('nda_read') !== '1' || f.get('privacy_read') !== '1') return fail('Please read both agreements to the end before checking them.');
  const now = Math.floor(Date.now() / 1000);
  const tok = await sign(env, { k: 'agree', nda: versions.nda, privacy: versions.privacy, terms: '2026-10-30b', at: now, read: true, exp: now + AGREE_S });
  return new Response(null, { status: 303, headers: { location: '/inquiry', 'set-cookie': setCookie('ig_a', tok, AGREE_S), 'cache-control': 'no-store' } });
}

// GET /auth/start: a fresh random state, bound to this browser by a short cookie, then off to AuthKit.
export async function start(req, env) {
  if (!env.WORKOS_CLIENT_ID) return new Response('Sign-in is not configured yet.', { status: 503 });
  const state = b64u(crypto.getRandomValues(new Uint8Array(24)));
  const q = new URLSearchParams({ response_type: 'code', client_id: env.WORKOS_CLIENT_ID, redirect_uri: redirectUri(req, env), state, provider: 'authkit' });
  return new Response(null, { status: 302, headers: { location: `${api(env)}/user_management/authorize?${q}`, 'set-cookie': setCookie('ig_state', state, STATE_S, '/auth'), 'cache-control': 'no-store' } });
}

// GET /auth/callback: check the state, exchange the code server-side, refuse personal domains, then set the signed session.
// fail(message) renders the site's error page; nothing is stored on any failure.
export async function callback(req, env, fail) {
  const u = new URL(req.url), state = u.searchParams.get('state'), code = u.searchParams.get('code');
  if (u.searchParams.get('error')) return fail('Sign-in was cancelled. You can try again from the contact page.');
  if (!state || !code || state !== cookie(req, 'ig_state')) return fail('That sign-in link has expired. Please start again from the contact page.');
  let r;
  try {
    r = await fetch(`${api(env)}/user_management/authenticate`, { method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ client_id: env.WORKOS_CLIENT_ID, client_secret: env.WORKOS_API_KEY, grant_type: 'authorization_code', code }) });
  } catch (e) { return fail('Sign-in could not be completed. Please try again shortly.'); }
  if (!r.ok) return fail('Sign-in could not be completed. Please start again from the contact page.');
  const a = await r.json(), user = a.user || {};
  const email = String(user.email || '').toLowerCase(), m = email.match(/^[^\s@]+@([a-z0-9.-]+\.[a-z]{2,})$/);
  if (!m || user.email_verified !== true) return fail('We could not confirm an email address for that account.');
  if (FREEMAIL.has(m[1])) return fail('Inquiries need an organisation account. Personal email services are not accepted.');
  const now = Math.floor(Date.now() / 1000);
  const s = { e: email, d: m[1], n: [user.first_name, user.last_name].filter(Boolean).join(' ').slice(0, 120), u: String(user.id || ''),
    m: METHOD[a.authentication_method] || String(a.authentication_method || 'verified sign-in'), o: String(a.organization_id || ''), iat: now, exp: now + SESSION_S };
  const h = new Headers({ location: '/inquiry', 'cache-control': 'no-store' });
  h.append('set-cookie', setCookie('ig_s', await sign(env, s), SESSION_S));
  h.append('set-cookie', setCookie('ig_state', '', 0, '/auth'));
  return new Response(null, { status: 302, headers: h });
}

// GET /auth/out: forget this browser's session.
export function out() {
  return new Response(null, { status: 302, headers: { location: '/inquiry', 'set-cookie': setCookie('ig_s', '', 0), 'cache-control': 'no-store' } });
}
