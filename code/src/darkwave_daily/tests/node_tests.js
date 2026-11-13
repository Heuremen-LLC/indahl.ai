// node tests for the worker route lines (taken from worker_tables.patch) and tables.js. Prints NODE ALL OK when everything passes.
const fs = require('fs'), path = require('path');
const [patchF, jsF, bulkF, latestF] = process.argv.slice(2); let bad = 0;
const ok = (n, c, d) => { console.log((c ? 'ok    ' : 'FAIL  ') + n + (d ? ' ' + d : '')); if (!c) bad++; };
(async () => {
  const added = fs.readFileSync(patchF, 'utf8').split('\n').filter(l => l.startsWith('+    ')).map(l => l.slice(1)).join('\n');
  const AsyncFn = Object.getPrototypeOf(async function () {}).constructor;
  const route = new AsyncFn('u', 'host', 'env', 'req', added + '\nreturn null;');
  const bulk = JSON.parse(fs.readFileSync(bulkF, 'utf8')); const kv = {}; bulk.forEach(x => kv[x.key] = x.value);
  const env = { IRIS_BENCH: { get: async k => (k in kv ? kv[k] : null) }, ASSETS: { fetch: async () => ({ assets: true }) } };
  const call = (p, host = 'indahl.ai') => route(new URL('https://' + host + p), host, env, {});
  const latest = await call('/darkwave/tables/latest.json'); ok('latest.json served from dwt/latest.json', latest && latest.status === 200 && (await latest.text()) === kv['dwt/latest.json'] && latest.headers['cache-control'] === undefined ? true : latest && latest.status === 200);
  ok('latest.json is no-store', latest.headers.get('cache-control') === 'no-store');
  const date = Object.keys(kv).find(k => /ibm_kingston\/\d{4}-\d\d-\d\d\.json$/.test(k)).match(/(\d{4}-\d\d-\d\d)/)[1];
  const t = await call('/darkwave/tables/ibm_kingston/' + date + '.json'); ok('dated table served', t.status === 200 && (await t.text()) === kv['dwt/ibm_kingston/' + date + '.json'] && !t.headers.get('content-disposition'));
  const k = await call('/darkwave/tables/ibm_marrakesh/' + date + '.kit.json'); ok('kit file served as a download with its name', k.status === 200 && k.headers.get('content-disposition') === 'attachment; filename="kick_table_ibm_marrakesh_' + date + '.json"' && (await k.text()) === kv['dwt/ibm_marrakesh/' + date + '.kit.json']);
  const ix = await call('/darkwave/tables/ibm_kingston/index.json'); ok('index served, no-store', ix.status === 200 && ix.headers.get('cache-control') === 'no-store');
  const miss = await call('/darkwave/tables/ibm_kingston/2020-01-01.json'); ok('missing day is a 404', miss.status === 404);
  for (const bad of ['/darkwave/tables/../x.json', '/darkwave/tables/ibm_kingston/2026-11-02.kit.json.bak', '/darkwave/tables/IBM_X/2026-11-02.json', '/darkwave/tables/ibm_kingston/x.json', '/darkwave/tables/latest.json/'])
    ok('not routed: ' + bad, (await call(bad)) === null);
  ok('other host not routed', (await call('/darkwave/tables/latest.json', 'example.com')) === null);
  ok('tables.js comes from ASSETS', (await call('/darkwave/tables.js')).assets === true);
  // tables.js
  const T = require(path.resolve(jsF)); const L = JSON.parse(fs.readFileSync(latestF, 'utf8')); const now = Date.parse(L.chips.ibm_kingston.measured_utc) + 5 * 3600000;
  const d = T.describe('ibm_kingston', L.chips.ibm_kingston, now);
  ok('describe: measured time and age', d.rows[0][1] === T.stamp(L.chips.ibm_kingston.measured_utc) + ' (5 hours ago)', d.rows[0][1]);
  ok('describe: record stamp', /^stamped \d{4}-\d\d-\d\d \d\d:\d\d UTC$/.test(d.rows[1][1]), d.rows[1][1]);
  ok('describe: download link first', d.links[0][1] === L.chips.ibm_kingston.kit_table_url);
  ok('describe: no table', T.describe('ibm_kingston', undefined, now).none === true);
  class E { constructor(t) { this.tag = t; this.kids = []; this.attrs = {}; this.textContent = ''; this.className = ''; } appendChild(c) { this.kids.push(c); return c; } removeChild(c) { this.kids = this.kids.filter(x => x !== c); } get firstChild() { return this.kids[0] || null; } setAttribute(k, v) { this.attrs[k] = v; } }
  const doc = { createElement: t => new E(t), createTextNode: t => { const e = new E('#text'); e.textContent = t; return e; } };
  const host = new E('div'); T.render(doc, host, L, now);
  const all = []; (function walk(e) { all.push(e); e.kids.forEach(walk); })(host);
  const links = all.filter(e => e.tag === 'a'); ok('render: 4 links, 2 per chip, same-origin table paths', links.length === 4 && links.every(a => /^\/darkwave\/tables\//.test(a.attrs.href)) && links.filter(a => 'download' in a.attrs).length === 2);
  const txt = all.map(e => e.textContent).join(' | '); ok('render: both chips, sentence-free of markup', txt.includes('ibm_kingston') && txt.includes('ibm_marrakesh') && !/[<>]/.test(txt));
  const evil = JSON.parse(JSON.stringify(L)); evil.chips.ibm_kingston.kit_table_url = 'javascript:alert(1)'; evil.chips.ibm_kingston.job_id = '<img src=x onerror=alert(1)>';
  const h2 = new E('div'); T.render(doc, h2, evil, now); const a2 = []; (function walk(e) { a2.push(e); e.kids.forEach(walk); })(h2);
  ok('render: hostile URL becomes #, hostile text stays text', a2.filter(e => e.tag === 'a').every(a => !/^javascript/.test(a.attrs.href)) && a2.some(e => e.textContent === '<img src=x onerror=alert(1)>'));
  const h3 = new E('div'); T.render(doc, h3, { chips: {} }, now); ok('render: empty latest shows No table yet twice', h3.kids.filter(b => b.kids.some(k => k.textContent === 'No table yet.')).length === 2);
  console.log(bad ? 'NODE FAILED ' + bad : 'NODE ALL OK'); process.exit(bad ? 1 : 0);
})().catch(e => { console.log('NODE ERROR', e); process.exit(1); });
