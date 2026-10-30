// TRIALS: ClinicalTrials.gov results posted against the one year due date. Reads /trials/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('trials-live'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function fmt(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = (n && typeof t === 'number') ? fmt(t) : t; return c; }
  // 30 Oct 2026 (site pass H-14): a cannot tell row says which kind it is, a share resolved between the two thresholds or an interval that reaches a threshold or too few records.
  function WC(o, lo, hi, lowT, highT, n) {
    if (o !== 'CANNOT_TELL') return W(o);
    if (n != null && n < 30) return 'cannot tell, fewer than 30 records';
    if (lo != null && hi != null && lo >= lowT && hi <= highT) return 'cannot tell, the whole interval sits between the thresholds';
    return 'cannot tell, the interval reaches a threshold';
  }
  var SIX = ['Never started or never approved', 'Registration replaced or withdrawn', 'Pandemic or logistics', 'Sponsor or partner decided', 'Resources or staff', 'Design or outcome changed'];
  function pct(x) { return x == null ? '' : (100 * x).toFixed(1) + '%'; }
  function table(title, rows, first, plain) {   // plain: the sponsor table keeps its plain outcome words (Wayfinder's call, 30 Oct 2026)
    var h = document.createElement('h3'); h.textContent = title;
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>' + first + '</th><th>Records</th><th>Results posted</th><th>No results on the record</th><th>Share with no results, 95% interval</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    rows.forEach(function (r) {
      var g = r[1], tr = document.createElement('tr'); tr.appendChild(td(r[0])); tr.appendChild(td(g.n, 1)); tr.appendChild(td(g.posted, 1)); tr.appendChild(td(g.no_results, 1));
      tr.appendChild(td(pct(g.share_no_results) + ' [' + pct(g.lo) + ', ' + pct(g.hi) + ']', 1)); tr.appendChild(td(plain ? W(g.outcome) : WC(g.outcome, g.lo, g.hi, 0.10, 0.25, g.posted + g.no_results))); b.appendChild(tr);
    });
    t.appendChild(b); var f = document.createDocumentFragment(); f.appendChild(h); f.appendChild(t); return f;
  }
  function gtable(title, rows, first, cols) {
    var h = document.createElement('h3'); h.textContent = title; var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>' + first + '</th>' + cols.map(function (c) { return '<th>' + c[0] + '</th>'; }).join('') + '</tr></thead>'; var b = document.createElement('tbody');
    rows.forEach(function (r) { var tr = document.createElement('tr'); tr.appendChild(td(r[0])); cols.forEach(function (c) { var v = r[1][c[1]]; tr.appendChild(c[2] === 'pct' ? td(v == null ? '' : pct(v) + ' [' + pct(r[1][c[1] + '_lo']) + ', ' + pct(r[1][c[1] + '_hi']) + ']', 1) : (c[2] === 'oc' ? td(WC(v, r[1].share_lo, r[1].share_hi, 0.05, 0.10, r[1].of)) : td(v == null ? '' : v, c[2] === 'n'))); }); b.appendChild(tr); });
    t.appendChild(b); var f = document.createDocumentFragment(); f.appendChild(h); f.appendChild(t); return f;
  }
  function cancelled(c) {
    if (!c) return; var s = document.createElement('h2'); s.textContent = 'Stopped trials, last two years'; box.appendChild(s);
    var n = document.createElement('p'); n.className = 'bench-note'; n.textContent = 'Interventional studies with a start date from ' + c.window.start + ' to ' + c.window.end + ' (a withdrawn study can carry an anticipated start). A recent quarter has had less time to be stopped, so shares are not compared across quarters. Reasons are sorted by the first matching word and carry no outcome.'; box.appendChild(n);
    var k = function (o) { return Object.keys(o).map(function (x) { return [x, o[x]]; }); };
    box.appendChild(gtable('Started and since stopped', [['Interventional studies started in the window', c.headline]], 'Group', [['Studies started', 'studies', 'n'], ['Withdrawn', 'withdrawn', 'n'], ['Terminated', 'terminated', 'n'], ['Suspended', 'suspended', 'n'], ['Share stopped', 'share_text', 't']]));
    var cl = { INDUSTRY: 'Industry', NIH: 'NIH', FED: 'Other federal', OTHER_GOV: 'Other government', NETWORK: 'Network', OTHER: 'Other (universities, hospitals, nonprofits)', INDIV: 'Individual', UNKNOWN: 'Unknown' };
    box.appendChild(gtable('By sponsor class', k(c.by_class).map(function (r) { return [cl[r[0]] || r[0], r[1]]; }), 'Sponsor class', [['Studies started', 'population', 'n'], ['Withdrawn', 'withdrawn', 'n'], ['Terminated', 'terminated', 'n'], ['Suspended', 'suspended', 'n'], ['Share stopped', 'share_text', 't']]));
    box.appendChild(gtable('Reasons given', k(c.reasons).map(function (r) { return [r[0] + (SIX.indexOf(r[0]) >= 0 ? ' (defined after the data)' : ''), r[1]]; }), 'Reason', [['Records', 'n', 'n'], ['Share', 'share_text', 't']]));
    var rn = document.createElement('p'); rn.className = 'bench-note'; rn.textContent = 'The six classes marked defined after the data were added after the first read left 31 percent of the stopped records in one unsorted class. They are tried in order after the first five, so no record already in a class moved. The texts that match none of the words are published in the public data folder.'; box.appendChild(rn);
    box.appendChild(gtable('Two tests against the registry\'s own rules', k(c.tests), 'Test', [['Records', 'of', 'n'], ['Failing', 'n', 'n'], ['Share, 95% interval', 'share', 'pct'], ['Outcome', 'outcome', 'oc']]));
    var tn = document.createElement('p'); tn.className = 'bench-note'; var t1 = (c.tests || {})['Stopped records with no reason given'] || {};
    tn.textContent = 'For these two tests above means the lower end of the 95% interval is above 10 percent, consistent means the upper end is below 5 percent, and fewer than 30 records reads cannot tell. The intervals treat records as independent although sponsors and programs cluster, so they are narrower than the records justify.' + (t1.largest_sponsor_n ? ' Of the ' + t1.n + ' records in the first test, ' + t1.largest_sponsor_n + ' have the same lead sponsor.' : ''); box.appendChild(tn);
    if (c.hand_check && c.hand_check.length) {
      var hh = document.createElement('h3'); hh.textContent = 'Ten records of the first test, read in full'; box.appendChild(hh);
      var ht = document.createElement('table'); ht.className = 'mtx'; ht.innerHTML = '<thead><tr><th>Record</th><th>Status</th><th>Lead sponsor</th><th>What the record says</th></tr></thead>'; var hb = document.createElement('tbody');
      c.hand_check.forEach(function (x) { var tr = document.createElement('tr'), cc = td(''), a = document.createElement('a'); a.href = 'https://clinicaltrials.gov/study/' + encodeURIComponent(x.id); a.textContent = x.id; cc.appendChild(a); tr.appendChild(cc); tr.appendChild(td(x.status ? x.status.charAt(0) + x.status.slice(1).toLowerCase() : '')); tr.appendChild(td(x.sponsor || '')); tr.appendChild(td(x.record_says)); hb.appendChild(tr); });
      ht.appendChild(hb); box.appendChild(ht);
    }
    box.appendChild(gtable('Stopped, by start quarter', k(c.by_quarter), 'Start quarter', [['Stopped', 'n', 'n']]));
    var r = document.createElement('h2'); r.textContent = 'Results due against results posted'; box.appendChild(r);
  }
  fetch('/trials/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.all) { box.textContent = 'Waiting for the first read.'; return; }
    var top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = d.all.n + ' records read from ClinicalTrials.gov at ' + d.read + ', primary completion up to ' + d.cutoff + ', after leaving out ' + d.excluded + ' Phase 1 drug-only records.';
    box.textContent = ''; cancelled(d.cancelled); box.appendChild(top);
    var cls = { INDUSTRY: 'Industry', NIH: 'NIH', FED: 'Other federal', OTHER_GOV: 'Other government', NETWORK: 'Network', OTHER: 'Other (universities, hospitals, nonprofits)', INDIV: 'Individual', UNKNOWN: 'Unknown' };
    box.appendChild(table('By sponsor class', Object.keys(d.by_class).map(function (k) { return [cls[k] || k, d.by_class[k]]; }), 'Sponsor class'));
    box.appendChild(table('By product', [['Drugs', d.by_kind.drug], ['Devices only', d.by_kind.device_only], ['Drugs and devices', d.by_kind.both]], 'Product'));
    box.appendChild(table('By primary completion year', Object.keys(d.by_year).map(function (k) { return [k, d.by_year[k]]; }), 'Year'));
    var det = document.createElement('details'), sm = document.createElement('summary'); sm.textContent = 'Lead sponsors with at least 20 records'; det.appendChild(sm);
    det.appendChild(table('', Object.keys(d.sponsors).map(function (k) { var p = k.split('|'); return [p[0], d.sponsors[k]]; }), 'Lead sponsor', true)); box.appendChild(det);
  }).catch(function () { box.textContent = 'The read could not be loaded just now.'; });
})();
