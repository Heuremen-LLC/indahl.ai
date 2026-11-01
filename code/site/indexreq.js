// indexreq.js -- the open door under each Matrix (QIA 24 Oct; OY 25 Oct) (24 Oct 2026, Wayfinder): "doors wide open for Kumar's next idea ... just a box that
// only accepts links to pdfs". One field. Indexing is only considered; nothing is promised, nothing is labelled, nothing is calibrated.
// Stores only the URL and the time (no name, no email, no IP); a hashed address is kept 1 hour for the rate limit, then expires.
const OK = 'Thank you. The link has been received for consideration for indexing.';
const isPdfUrl = s => /^https:\/\/[^\s]+\.pdf([?#][^\s]*)?$/i.test(s) || /^https:\/\/arxiv\.org\/pdf\/[^\s]+$/i.test(s);
async function sha(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
export async function handleIndexRequest(req, env, page) {
  if (req.method !== 'POST') return page('Use the box under the index.', 405);
  const f = await req.formData(); const url = String(f.get('url') || '').trim();
  const m = ['qia', 'iris', 'oy'].includes(String(f.get('m') || '')) ? String(f.get('m')) : 'qia';   // 25 Oct: which matrix the box sat under
  if (String(f.get('website') || '')) return page(OK, 200);                       // honeypot: bots get the same answer, nothing stored
  if (url.length > 2000 || !isPdfUrl(url)) return page('Please paste a direct https link to a PDF.', 400);
  const ip = req.headers.get('cf-connecting-ip') || ''; const rk = 'idxrl:' + (await sha('qia-idx|' + ip)).slice(0, 32);
  const n = parseInt((await env.INDAHL_INQUIRIES.get(rk)) || '0', 10);
  if (n >= 5) return page('Several links have arrived from you this hour. Please try again later.', 429);
  let isPdf = false;                                                              // the link must really serve a PDF
  try {
    const r = await fetch(url, { method: 'GET', headers: { Range: 'bytes=0-7' }, redirect: 'follow', cf: { cacheTtl: 0 } });
    const ct = (r.headers.get('content-type') || '').toLowerCase(); const head = new Uint8Array(await r.arrayBuffer()).slice(0, 5);
    isPdf = ct.includes('application/pdf') || String.fromCharCode(...head) === '%PDF-';
  } catch (e) { isPdf = false; }
  if (!isPdf) return page('That link did not return a PDF. Please paste a direct link to the PDF file.', 400);
  const ts = new Date().toISOString();
  await env.INDAHL_INQUIRIES.put(`idx:${ts}:${crypto.randomUUID().slice(0, 8)}`, JSON.stringify({ url, m, received: ts }));
  await env.INDAHL_INQUIRIES.put(rk, String(n + 1), { expirationTtl: 3600 });
  return page(OK, 200);
}
