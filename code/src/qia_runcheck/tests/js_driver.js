// node js_driver.js INDEX_ROOT CASES.json -> JSON on stdout. INDEX_ROOT holds index.json and <backend>/ (what is served at /qia/records/).
const fs = require('fs'), path = require('path'), R = require('../public/qia/runcheck.js');
const root = process.argv[2], cases = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const getJson = u => Promise.resolve(JSON.parse(fs.readFileSync(path.join(root, u.replace('/qia/records/', '')), 'utf8')));
(async () => {
  const out = {};
  for (const c of cases) {
    if (c.sweep) {   // every record of the processor: the flags for every qubit, and the whole-history changes
      const man = await getJson('/qia/records/' + c.backend + '/manifest.json'), days = [...new Set(man.records.map(r => r[2]))], flags = {}, recs = [];
      for (const d of days) { const j = await getJson('/qia/records/' + c.backend + '/' + d + '.json'); j.records.forEach(it => recs.push(R.toRecord(it, j.dates))); }
      recs.sort((a, b) => a.stamp - b.stamp);
      recs.forEach(r => { flags[r.iso] = R.checkRecord(r, Object.keys(r.Q).map(Number).sort((a, b) => a - b)); });
      out[c.name] = { flags: flags, n: recs.length };
      continue;
    }
    const s = R.parseWhen(c.start), e = R.parseWhen(c.end), q = R.parseQubits(c.qubits || '');
    const r = await R.load(getJson, c.backend, s, e, q);
    out[c.name] = { file: r.under ? r.under.file : null, stamp: r.under ? r.under.iso : null, during: r.during.map(x => x.iso), flags: r.flags, changes: r.changes.map(x => ({ record: x.record, qubit: x.qubit, field: x.field, before: x.before, after: x.after, date_before: x.date_before, date_after: x.date_after })), missing: r.missing };
  }
  process.stdout.write(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
