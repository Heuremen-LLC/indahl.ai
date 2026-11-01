// inquire.js -- the indahl.ai engagement inquiry gate (23 Oct 2026; his: "it's your turn to jump through hoops").
// POST /inquire from the form on /contact. 24 Oct 2026: engagement inquiries need the signed WorkOS session from gate.js and an
// accepted NDA (the version and SHA-256 served at /nda.txt); without both, nothing is stored. Privacy requests and security reports
// now use the same form and the same checks. Filters: organisational email only (personal mail
// domains refused), a honeypot field, a minimum fill time, field length limits, and a per-visitor rate limit. Accepted inquiries are
// stored in the private KV namespace INDAHL_INQUIRIES (key inq:<ISO time>:<random>); only the country is kept, never the raw IP.
// Read them on the Mac with: python3 ~/bones-forge/indahl-ai/inquiries.py

import { EmailMessage } from 'cloudflare:email';
import { session, agreement, FREEMAIL } from './gate.js';

const FIELDS = { reason: 20, name: 120, email: 160, organisation: 160, role: 120, scope: 3000, budget: 40, timeline: 40, referral: 300 };
const REASONS = new Set(['engagement', 'privacy', 'security']);

async function sha(s) {
  const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(b)].slice(0, 12).map(x => x.toString(16).padStart(2, '0')).join('');
}

export async function handleInquiry(req, env, render) {
  const reject = (msg, status = 400) => render(msg, status);
  if (req.method !== 'POST') return reject('Please use the inquiry form on the contact page.', 405);
  if (!env.INDAHL_INQUIRIES) return reject('Inquiries are temporarily unavailable. Please try again later.', 503);
  const len = Number(req.headers.get('content-length') || 0);
  if (len > 20000) return reject('That submission is too long.', 413);
  let f;
  try { f = await req.formData(); } catch (e) { return reject('That submission could not be read.'); }
  if ((f.get('website') || '').trim()) return render(null, 200);                 // honeypot: look accepted, store nothing
  const started = Number(f.get('t') || 0);
  if (!started || Date.now() - started < 3000) return reject('That went through too quickly. Please wait a moment and submit again.');
  const rec = {};
  for (const [k, max] of Object.entries(FIELDS)) {
    const v = String(f.get(k) || '').trim();
    if (v.length > max) return reject(`The ${k} field is too long.`);
    rec[k] = v;
  }
  if (!REASONS.has(rec.reason)) rec.reason = 'engagement';
  const engagement = true;   // 26 Oct 2026 (his word): one inquiry form for everything; every reason goes through the agreements and the identity check
  let who = null, ag = null;
  if (engagement) {
    ag = await agreement(req, env);
    if (!ag) return reject('The agreements have not been accepted in this browser, or have expired. Please start again from the contact page.', 401);
    who = await session(req, env);
    if (!who) return reject('Please verify your identity before submitting.', 401);
    rec.email = who.e;                                                                     // the verified address, never the form's
  }
  // 23 Oct full pass: privacy requests and security reports must be possible from any address and without NDA authority.
  for (const k of (engagement ? ['name', 'email', 'organisation', 'role', 'scope'] : ['name', 'email', 'scope'])) if (!rec[k]) return reject('Please complete every required field.');
  if (!engagement && f.get('privacy') !== 'yes') return reject('Please confirm you have read the privacy notice.');
  const m = rec.email.toLowerCase().match(/^[^\s@]+@([a-z0-9.-]+\.[a-z]{2,})$/);
  if (!m) return reject('Please give a valid email address.');
  if (engagement && FREEMAIL.has(m[1])) return reject('Please write from your organisation’s email address. Inquiries from personal email services are not reviewed.');
  const ip = req.headers.get('cf-connecting-ip') || '';
  const rk = 'rate:' + await sha(ip + '|' + new Date().toISOString().slice(0, 13));
  const n = Number(await env.INDAHL_INQUIRIES.get(rk) || 0);
  if (n >= 3) return reject('We have received several inquiries from you recently. Please wait before sending another.', 429);
  await env.INDAHL_INQUIRIES.put(rk, String(n + 1), { expirationTtl: 3600 });
  rec.received = new Date().toISOString();
  rec.country = (req.cf && req.cf.country) || '';
  rec.domain = m[1];
  const key = `inq:${rec.received}:${crypto.randomUUID().slice(0, 8)}`;
  rec.nda_confirmed = engagement;
  if (engagement) {
    rec.identity = { verified_email: who.e, domain: who.d, method: who.m, workos_user: who.u, workos_org: who.o || null, verified_at: new Date(who.iat * 1000).toISOString() };
    const at = new Date(ag.at * 1000).toISOString();
    rec.agreements = { nda: { version: ag.nda, accepted_at: at, accepted_by: rec.name, title: rec.role, organisation: rec.organisation, authority_confirmed: true },
      privacy: { version: ag.privacy, agreed_at: at }, terms: { version: ag.terms || null, agreed_at: at }, both_read_to_end: ag.read === true };   // 30 Oct site pass: the Terms version accepted is kept too
  }
  await env.INDAHL_INQUIRIES.put(key, JSON.stringify(rec), { expirationTtl: 63072000 });   // 24 months, as the privacy notice states
  try { await notify(env, rec, key); } catch (e) { await env.INDAHL_INQUIRIES.put('notify-failed:' + key, String(e && e.message || e)); }
  return render(null, 200);
}

// Email notice of an accepted inquiry. The destination lives only in the worker's private config (send_email binding + vars);
// it never appears on a page or in this source. Header values are stripped of line breaks so form text cannot inject headers.
async function notify(env, rec, key) {
  if (!env.INQUIRY_MAIL || !env.INQUIRY_TO || !env.INQUIRY_FROM) return;
  const h = v => String(v || '').replace(/[\r\n]+/g, ' ').slice(0, 200);
  const body = [
    `New engagement inquiry (${rec.received}, ${rec.country || 'country unknown'})`, '',
    `Name: ${rec.name}`, `Role: ${rec.role}`, `Organisation: ${rec.organisation} (${rec.domain})`, `Email: ${rec.email}`,
    `Reason: ${rec.reason}`, `Referred by: ${rec.referral || '-'}`, (rec.agreements ? `AGREEMENTS: NDA v${rec.agreements.nda.version} and Privacy Notice ${rec.agreements.privacy.version} read to the end (Terms ${rec.agreements.terms.version}) and checked at ${rec.agreements.nda.accepted_at} by ${rec.agreements.nda.accepted_by}, ${rec.agreements.nda.title}, for ${rec.agreements.nda.organisation} (authority confirmed). Identity verified: ${rec.identity.verified_email} via ${rec.identity.method}.` : 'Agreements: not required for this reason'), '',
    'Scope, in their words:', rec.scope, '',
    `Approximate budget: ${rec.budget || 'not stated'}`, `Timeline: ${rec.timeline || 'not stated'}`, '',
    `Stored as ${key}. Read all with: python3 ~/bones-forge/indahl-ai/inquiries.py`,
  ].join('\r\n');
  const raw = [
    `From: Indahl inquiries <${env.INQUIRY_FROM}>`, `To: <${env.INQUIRY_TO}>`, `Reply-To: ${h(rec.email)}`,
    `Subject: ${rec.reason === 'engagement' ? 'Inquiry' : rec.reason === 'privacy' ? 'PRIVACY REQUEST' : 'SECURITY REPORT'}: ${h(rec.organisation || rec.name)} (${h(rec.domain)})`, `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${crypto.randomUUID()}@indahl.ai>`, 'MIME-Version: 1.0', 'Content-Type: text/plain; charset=utf-8',
    'Content-Transfer-Encoding: 8bit', '', body,
  ].join('\r\n');
  await env.INQUIRY_MAIL.send(new EmailMessage(env.INQUIRY_FROM, env.INQUIRY_TO, raw));
}
