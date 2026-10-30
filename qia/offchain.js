// QIA off-record chain: every reading where one of our jobs found IBM's published calibration outside what the device delivered, hashed and chained.
(function () {
  var box = document.getElementById('offchain-live'); if (!box) return;
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  // The rule an entry was called under, named beside the reading (two rules meet in this chain: the T1 and T2 check with no margin, the hourly run with a 25% margin on T1).
  function rule(e) { var r = e.rule || '', m = /(Notes?) (\d+(?: and \d+)*)/.exec(r), k = m ? m[1] + ' ' + m[2] : ''; if (/t1t2/.test(r)) return 'T1 and T2 check' + (k ? ', ' + k : '') + (e.quantity === 'T1' ? ', no margin' : ''); if (/qia_cal/.test(r)) return 'hourly run' + (k ? ', ' + k : '') + (e.quantity && /^T1/.test(e.quantity) ? ', 25% margin on T1' : ''); return ''; }
  function W(o) { return { ABOVE: 'IBM figure above what the device delivered', BELOW: 'IBM figure below what the device delivered', CANNOT_TELL: 'cannot tell' }[o] || o; }
  // 30 Oct: every interval says its level (the levels differ by entry: 99.9% readout, 99.99% T1, 95% in the T1 and T2 check).
  function lvl(m) { var x = m && m.level; if (!x && m && m.what) { var g = /(\d+(?:\.\d+)?%)/.exec(m.what); x = g ? g[1] + ' interval' : ''; } return x || ''; }
  function meas(m) { if (m && m.interval == null && m.bound == null) return String(m.value); var L = lvl(m); return m.interval ? m.value + ' [' + m.interval[0] + ', ' + m.interval[1] + ']' + (L ? ', ' + L : '') : (m.bound != null ? 'at most ' + m.bound + ' (2 x the top of the T1 interval); echo T2 ' + m.t2_echo + ' [' + m.t2_echo_interval[0] + ', ' + m.t2_echo_interval[1] + '], ' + (L || '95% interval') : ''); }
  fetch('/qia/offchain.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (c) {
    var raw = c.entries || []; box.textContent = '';
    // 30 Oct: hourly calibration runs are chain entries too; each run lists its off-record qubits in 'off'. Flatten them for the lookup.
    function num(v, u) { return v == null ? '' : (u === 'us' ? Number(v).toFixed(1) : Number(v).toPrecision(3)); }
    // 30 Oct: an entry that another entry names in 'corrects' is superseded. It stays in the whole-chain table, marked, and is left out of the lookup.
    var sup = {}; raw.forEach(function (e) { if (e.corrects != null) sup[e.corrects] = e.n; });
    var es = [];
    raw.forEach(function (e) {
      if (sup[e.n] != null || !e.window_utc || (e.type !== 'calibration run' && !e.qubits)) return;   // a note entry (no qubits, no window) has no readings to look up
      if (e.type === 'calibration run') {
        (e.off || []).forEach(function (o) { var t1 = /^T1/.test(o.quantity); es.push({ n: e.n, processor: e.processor, qubits: [o.qubit], quantity: o.quantity, ibm_stated: num(o.ibm, o.unit), unit: o.unit || '', ibm_date: o.ibm_date, measured: { value: num(o.measured, o.unit), interval: o.interval ? [num(o.interval[0], o.unit), num(o.interval[1], o.unit)] : null, level: t1 ? '99.99% interval' : '99.9% interval' }, outcome: o.outcome, rule: e.rule, window_utc: e.window_utc, job_id: e.job_id, hash: e.hash }); });
      } else es.push(e);
    });
    function summary(e) {
      // 30 Oct: an entry with no qubits or no window (type 'correction' today) is a note row: its type is the quantity, its note the measured cell, and it names the entry it corrects.
      if (e.type !== 'calibration run' && (!e.qubits || !e.window_utc)) return { n: e.n, processor: e.processor || '', qubits: [], quantity: e.type || 'note', ibm_stated: '', unit: '', ibm_date: '', measured: { value: e.note || '' }, outcome: '', corrects: e.corrects, added: e.added, window_utc: null, job_id: e.job_id || '', hash: e.hash || '' };
      if (e.type !== 'calibration run') return e;
      var k = e.counts || {}, off = (e.off || []).length, by = {};
      (e.off || []).forEach(function (o) { by[o.quantity] = (by[o.quantity] || 0) + 1; });
      return { n: e.n, processor: e.processor, qubits: [e.qubits_read + ' read'], quantity: 'hourly calibration run', ibm_stated: '', unit: '', ibm_date: 'record in force', measured: { value: off + ' off (' + Object.keys(by).map(function (q) { return q + ' ' + by[q]; }).join(', ') + ')' }, outcome: 'known-good ' + (e.known_good || '') + (rule(e) ? ' (' + rule(e) + ')' : ''), corrects: e.corrects, window_utc: e.window_utc, job_id: e.job_id, hash: e.hash };
    }
    var f = el('div', 'pk-ctl'); var sel = el('select'); sel.setAttribute('aria-label', 'Processor');
    var procs = {}; es.forEach(function (e) { procs[e.processor] = 1; }); ['ibm_boston', 'ibm_fez', 'ibm_kingston', 'ibm_marrakesh', 'ibm_pittsburgh', 'ibm_phoenix', 'ibm_aachen'].forEach(function (p) { procs[p] = 1; });
    Object.keys(procs).sort().forEach(function (p) { var o = el('option', null, p); o.value = p; sel.appendChild(o); });
    var qs = el('input'); qs.placeholder = 'your qubits, e.g. 85, 86'; qs.setAttribute('aria-label', 'Qubits');
    var tm = el('input'); tm.type = 'datetime-local'; tm.setAttribute('aria-label', 'When your job ran (UTC)');
    var go = el('button', 'btn ghost', 'Check my job'); go.type = 'button';
    f.appendChild(sel); f.appendChild(qs); f.appendChild(tm); f.appendChild(go); box.appendChild(f);
    var res = el('div'); box.appendChild(res);
    function reading(e) {
      var r = e.type === 'calibration run' ? '' : rule(e), w = e.outcome ? W(e.outcome) + (r ? ' (' + r + ')' : '') : '';
      if (e.corrects != null) w += (w ? ' ' : '') + '(corrects entry ' + e.corrects + ')';
      if (sup[e.n] != null) w += (w ? ' ' : '') + '(superseded by entry ' + sup[e.n] + ')';
      return w;
    }
    function when(e) { return e.window_utc ? e.window_utc[0].replace('T', ' ').slice(0, 16) + ' to ' + e.window_utc[1].slice(11, 16) : 'entry added ' + String(e.added || '').replace('T', ' ').slice(0, 16); }
    function table(rows, t0) {
      var t = el('table', 'mtx'); t.innerHTML = '<thead><tr><th>#</th><th>Processor</th><th>Qubits</th><th>Quantity</th><th>IBM published, date IBM gives (US Eastern)</th><th>Measured by our job</th><th>Reading</th><th>Our job ran (UTC)</th>' + (t0 ? '<th>From your job</th>' : '') + '<th>Job id</th><th>Hash</th></tr></thead>';
      var b = el('tbody');
      rows.forEach(function (e) {
        var r = el('tr'); [e.n, e.processor, (e.qubits || []).join(', '), e.quantity, (e.ibm_stated === '' ? '' : e.ibm_stated + (e.unit ? ' ' + e.unit : '') + ', ') + e.ibm_date, meas(e.measured), reading(e), when(e)].forEach(function (x) { r.appendChild(el('td', null, x)); });
        if (t0) { var h = e.window_utc ? (Date.parse(e.window_utc[0]) - t0) / 3600000 : 0; r.appendChild(el('td', null, (h >= 0 ? '+' : '') + h.toFixed(1) + ' h')); }
        r.appendChild(el('td', null, e.job_id || '')); r.appendChild(el('td', null, String(e.hash || '').slice(0, 12) + '…')); b.appendChild(r);
      });
      t.appendChild(b); return t;
    }
    function show() {
      res.textContent = ''; var p = sel.value, want = (qs.value.match(/\d+/g) || []).map(Number), t0 = tm.value ? Date.parse(tm.value + 'Z') : null;
      var rows = es.filter(function (e) { return e.processor === p && (!want.length || e.qubits.some(function (q) { return want.indexOf(q) > -1; })); });
      if (t0) rows.sort(function (a, b) { return Math.abs(Date.parse(a.window_utc[0]) - t0) - Math.abs(Date.parse(b.window_utc[0]) - t0); });
      if (!rows.length) { res.appendChild(el('p', 'bench-note', 'No entry on ' + p + (want.length ? ' for qubits ' + want.join(', ') : '') + '. No entry means none of our readings of it was off. Every usable qubit is read in each hourly run, and every reading is in the run file linked in the hourly table above.')); return; }
      res.appendChild(table(rows, t0));
    }
    go.onclick = show;
    // 30 Oct (his "it buries the headline"): the newest entry shows, the whole chain sits one click away with every row and hash.
    var sm = raw.map(summary).reverse();
    box.appendChild(el('h4', null, 'Newest entry')); box.appendChild(table(sm.slice(0, 1), null));
    var det = el('details'); det.appendChild(el('summary', null, 'Show the whole chain, newest first')); det.appendChild(table(sm, null)); box.appendChild(det);
    box.appendChild(el('p', 'bench-note', 'Head of the chain: ' + c.head + '. Each hash is sha256 of the entry with the previous hash inside it, so no entry can change without breaking every one after it. Append only: a correction is a new entry. Updated ' + c.updated.replace('T', ' ').slice(0, 16) + ' UTC.'));
  }).catch(function () { box.textContent = 'The chain could not be read just now.'; });
})();
