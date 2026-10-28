// TRIALS: ClinicalTrials.gov results posted against the one year due date. Reads /trials/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('trials-live'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  function pct(x) { return x == null ? '' : (100 * x).toFixed(1) + '%'; }
  function table(title, rows, first) {
    var h = document.createElement('h3'); h.textContent = title;
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>' + first + '</th><th>Records</th><th>Results posted</th><th>No results on the record</th><th>Share with no results, 95% interval</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    rows.forEach(function (r) {
      var g = r[1], tr = document.createElement('tr'); tr.appendChild(td(r[0])); tr.appendChild(td(g.n, 1)); tr.appendChild(td(g.posted, 1)); tr.appendChild(td(g.no_results, 1));
      tr.appendChild(td(pct(g.share_no_results) + ' [' + pct(g.lo) + ', ' + pct(g.hi) + ']', 1)); tr.appendChild(td(W(g.outcome))); b.appendChild(tr);
    });
    t.appendChild(b); var f = document.createDocumentFragment(); f.appendChild(h); f.appendChild(t); return f;
  }
  fetch('/trials/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.all) { box.textContent = 'Waiting for the first read.'; return; }
    var top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = d.all.n + ' records read from ClinicalTrials.gov at ' + d.read + ', primary completion up to ' + d.cutoff + ', after leaving out ' + d.excluded + ' Phase 1 drug-only records.';
    box.textContent = ''; box.appendChild(top);
    var cls = { INDUSTRY: 'Industry', NIH: 'NIH', FED: 'Other federal', OTHER_GOV: 'Other government', NETWORK: 'Network', OTHER: 'Other (universities, hospitals, nonprofits)', INDIV: 'Individual', UNKNOWN: 'Unknown' };
    box.appendChild(table('By sponsor class', Object.keys(d.by_class).map(function (k) { return [cls[k] || k, d.by_class[k]]; }), 'Sponsor class'));
    box.appendChild(table('By product', [['Drugs', d.by_kind.drug], ['Devices only', d.by_kind.device_only], ['Drugs and devices', d.by_kind.both]], 'Product'));
    box.appendChild(table('By primary completion year', Object.keys(d.by_year).map(function (k) { return [k, d.by_year[k]]; }), 'Year'));
    var det = document.createElement('details'), sm = document.createElement('summary'); sm.textContent = 'Lead sponsors with at least 20 records'; det.appendChild(sm);
    det.appendChild(table('', Object.keys(d.sponsors).map(function (k) { var p = k.split('|'); return [p[0], d.sponsors[k]]; }), 'Lead sponsor')); box.appendChild(det);
  }).catch(function () { box.textContent = 'The read could not be loaded just now.'; });
})();
