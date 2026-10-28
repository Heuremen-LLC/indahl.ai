// Read-only data API and MCP server for indahl.ai (28 Oct 2026). One tool list drives three surfaces: the MCP endpoint (POST /mcp), the REST endpoints (GET /api/v1/<tool>) and the OpenAPI file (/api/openapi.json).
// Nothing here writes. Every answer carries its source page, the time it was read and the terms (retrieval and answering permitted, training not).
const TERMS = 'https://indahl.ai/terms', USE = 'Retrieval and answering are permitted. Use as training data is not permitted.';
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'GET, POST, OPTIONS', 'access-control-allow-headers': 'content-type, mcp-protocol-version, mcp-session-id, accept' };
const kv = async (env, key) => { const v = env.IRIS_BENCH ? await env.IRIS_BENCH.get(key) : null; try { return v ? JSON.parse(v) : null; } catch (e) { return null; } };
const wrap = (source, data) => ({ source, read_at: new Date().toISOString(), terms: TERMS, use: USE, data });
async function studies(env, req, division) {
  const r = await env.ASSETS.fetch(new Request(new URL(`/${division}/list.json`, req.url))); const d = await r.json(); return d.studies || [];
}
const DIVISIONS = [
  { id: 'qia', url: 'https://indahl.ai/qia', what: 'IBM processors measured against their published calibration, calibrated studies, and the List of indexed quantum studies with receipts.' },
  { id: 'iris', url: 'https://indahl.ai/iris', what: 'Language-model evaluation studies recounted from their released files, live Faults and Guards runs on open models, and the trained Falcon results.' },
  { id: 'sad', url: 'https://indahl.ai/sad', what: 'Vendor statements about AI hardware held against published MLPerf results, with the quoted sentence, the entry and the outcome.' },
  { id: 'time', url: 'https://indahl.ai/time', what: 'Public time servers held against their own stated error bounds, measured live from a GPS-disciplined clock and a second network.' },
  { id: 'coin', url: 'https://indahl.ai/coin', what: 'Ravencoin whitepaper statements held against the chain\'s own block record, live.' },
  { id: 'cada', url: 'https://indahl.ai/cada', what: 'Public DNS filters held against fresh bad-domain listings, live: share blocked and time to block.' },
  { id: 'oy', url: 'https://indahl.ai/oy', what: 'Learning research and school AI policy indexed against their own published numbers.' },
  { id: 'atlas', url: 'https://indahl.ai/atlas', what: 'United States data centers, power plants and grid carbon with a source and pull date per row.' },
];
const OUTCOMES = 'Outcomes are ABOVE, BELOW, CONSISTENT or CANNOT_TELL, relative to what was stated. Nothing returned, refused and held are counted as their own outcomes.';
const TOOLS = [
  { name: 'list_divisions', description: 'List every division of indahl.ai with a one-line description and its page. Start here. ' + OUTCOMES, params: {}, run: async () => wrap('https://indahl.ai', DIVISIONS) },
  { name: 'time_servers', description: 'Public time servers (NTP) stated against delivered, live. Per server: stratum, its own stated error bound, measured offset from a GPS-disciplined reference, path half-delay and the outcome. Optional filter by server name. Offsets are shown from two networks; the offset common to all servers on one network belongs to that network\'s access link.', params: { server: { type: 'string', description: 'Substring of a server name, for example google or nist.' } },
    run: async (env, a) => { const d = await kv(env, 'time_live'); if (!d) return wrap('https://indahl.ai/time', null); if (a.server) d.servers = (d.servers || []).filter(s => s.server.includes(String(a.server).toLowerCase())); return wrap('https://indahl.ai/time', d); } },
  { name: 'dns_filters', description: 'Public DNS filtering resolvers held against freshly listed malware and phishing domains, live: for each resolver and checkpoint (first sight, 1 h, 6 h, 24 h) the share blocked with a 95% interval, and the counts behind it.', params: {},
    run: async (env) => wrap('https://indahl.ai/cada', await kv(env, 'caca_live')) },
  { name: 'coin_claims', description: 'Ravencoin whitepaper statements held against the chain\'s own block record, live: each statement quoted, the chain record, and the outcome, plus block-gap, signer and payout-address tables.', params: {},
    run: async (env) => { const d = await kv(env, 'coin_live'); if (d) delete d.hashes; return wrap('https://indahl.ai/coin', d); } },
  { name: 'ibm_calibration', description: 'The calibration IBM publishes for each processor, mirrored every few minutes: record stamp, qubit count, median T1, T2, readout error and two-qubit error, records saved, restamps and value changes in the last 7 days. Optional filter by processor.', params: { processor: { type: 'string', description: 'For example ibm_fez.' } },
    run: async (env, a) => { const d = await kv(env, 'qia_ibm'); if (d && a.processor) d.backends = (d.backends || []).filter(b => b.backend === String(a.processor)); return wrap('https://indahl.ai/qia', d); } },
  { name: 'find_study', description: 'Search the List of published studies that QIA (quantum hardware) or IRIS (language models) has read and indexed. Returns title, link, classification codes, date indexed and the receipt of what was read.', params: { query: { type: 'string', description: 'Words in the title.' }, division: { type: 'string', enum: ['qia', 'iris'], description: 'Which List. Default qia.' }, limit: { type: 'integer', description: 'Up to 25. Default 10.' } }, required: ['query'],
    run: async (env, a, req) => { const dv = a.division === 'iris' ? 'iris' : 'qia', q = String(a.query || '').toLowerCase().trim(), lim = Math.min(25, Math.max(1, parseInt(a.limit, 10) || 10)); const all = await studies(env, req, dv); const hit = q ? all.filter(s => (s.study || '').toLowerCase().includes(q)) : all; return wrap(`https://indahl.ai/${dv}/list`, { matches: hit.length, shown: Math.min(lim, hit.length), studies: hit.slice(0, lim) }); } },
  { name: 'bench_results', description: 'Faults and Guards bench on open models, per finished round: per model and Fault family, the share of readable replies that commit the Fault with a plain prompt and with the Guard wording, with 95% intervals.', params: {}, run: async (env) => wrap('https://indahl.ai/iris', await kv(env, 'results')) },
  { name: 'model_claims_round', description: 'The live round that reruns an open model\'s stated benchmark results with the published harness: each claim, our result and the outcome.', params: {}, run: async (env) => wrap('https://indahl.ai/sad', await kv(env, 'sad_live')) },
];
const schema = (t) => ({ type: 'object', properties: t.params || {}, required: t.required || [] });
const jsonR = (o, status = 200, extra = {}) => new Response(JSON.stringify(o), { status, headers: { 'content-type': 'application/json; charset=utf-8', ...CORS, ...extra } });
async function callTool(env, req, name, args) { const t = TOOLS.find(x => x.name === name); if (!t) return null; return t.run(env, args || {}, req); }
function openapi() {
  const paths = {}; for (const t of TOOLS) paths[`/api/v1/${t.name}`] = { get: { operationId: t.name, summary: t.description, parameters: Object.entries(t.params || {}).map(([n, p]) => ({ name: n, in: 'query', required: (t.required || []).includes(n), schema: { type: p.type, ...(p.enum ? { enum: p.enum } : {}) }, description: p.description })), responses: { 200: { description: 'JSON with source, read_at, terms, use and data.' } } } };
  return { openapi: '3.1.0', info: { title: 'indahl.ai data API', version: '1.0.0', description: 'Read-only. ' + OUTCOMES + ' ' + USE, termsOfService: TERMS }, servers: [{ url: 'https://indahl.ai' }], paths };
}
export async function handleApi(req, env, u) {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
  const p = u.pathname;
  if (p === '/api/openapi.json') return jsonR(openapi(), 200, { 'cache-control': 'public, max-age=600' });
  if (p === '/api/v1' || p === '/api/v1/') return jsonR({ api: 'indahl.ai data API', version: '1.0.0', tools: TOOLS.map(t => ({ name: t.name, endpoint: `https://indahl.ai/api/v1/${t.name}`, description: t.description })), mcp: 'https://indahl.ai/mcp', openapi: 'https://indahl.ai/api/openapi.json', terms: TERMS, use: USE }, 200, { 'cache-control': 'public, max-age=600' });
  let m = /^\/api\/v1\/([a-z_]+)$/.exec(p);
  if (m) {
    if (req.method !== 'GET') return jsonR({ error: 'GET only' }, 405, { allow: 'GET, OPTIONS' });
    const args = {}; for (const [k, v] of u.searchParams) if (k.length < 40 && v.length < 200) args[k] = v;
    const r = await callTool(env, req, m[1], args); if (!r) return jsonR({ error: 'unknown tool', see: 'https://indahl.ai/api/v1' }, 404);
    return jsonR(r, 200, { 'cache-control': 'public, max-age=60' });
  }
  if (p === '/mcp') {
    if (req.method === 'GET') return new Response('This is an MCP server. POST JSON-RPC to this URL.', { status: 405, headers: { allow: 'POST, OPTIONS', ...CORS } });
    if (req.method !== 'POST') return new Response(null, { status: 405, headers: { allow: 'POST, OPTIONS', ...CORS } });
    const raw = await req.text(); if (raw.length > 65536) return jsonR({ jsonrpc: '2.0', id: null, error: { code: -32600, message: 'request too large' } }, 413);
    let body; try { body = JSON.parse(raw); } catch (e) { return jsonR({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'parse error' } }, 400); }
    const one = async (msg) => {
      const id = msg.id, has = Object.prototype.hasOwnProperty.call(msg, 'id'); const ok = (result) => ({ jsonrpc: '2.0', id, result }), err = (code, message) => ({ jsonrpc: '2.0', id, error: { code, message } });
      if (!has) return null;
      switch (msg.method) {
        case 'initialize': { const pv = (msg.params && msg.params.protocolVersion) || '2025-06-18'; return ok({ protocolVersion: pv, capabilities: { tools: { listChanged: false } }, serverInfo: { name: 'indahl-ai', title: 'Heuremen LLC data', version: '1.0.0' }, instructions: 'Read-only measurements of published claims against the data behind them. Start with list_divisions. ' + OUTCOMES + ' ' + USE }); }
        case 'ping': return ok({});
        case 'tools/list': return ok({ tools: TOOLS.map(t => ({ name: t.name, description: t.description, inputSchema: schema(t), annotations: { readOnlyHint: true, openWorldHint: false } })) });
        case 'tools/call': { const n = msg.params && msg.params.name; const r = await callTool(env, req, n, (msg.params && msg.params.arguments) || {}).catch(() => 'ERR'); if (r === null) return err(-32602, 'unknown tool'); if (r === 'ERR') return ok({ content: [{ type: 'text', text: 'The source could not be read just now.' }], isError: true }); return ok({ content: [{ type: 'text', text: JSON.stringify(r) }], isError: false }); }
        default: return err(-32601, 'method not found');
      }
    };
    if (Array.isArray(body)) { const out = (await Promise.all(body.slice(0, 20).map(one))).filter(Boolean); return out.length ? jsonR(out) : new Response(null, { status: 202, headers: CORS }); }
    const r = await one(body); return r ? jsonR(r) : new Response(null, { status: 202, headers: CORS });
  }
  return null;
}
