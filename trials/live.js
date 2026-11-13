// TRIALS: ClinicalTrials.gov results posted against the one year due date. Reads /trials/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('trials-live'); if (!box) return;
  function W(o, why) { return ({ CONSISTENT: 'consistent', ABOVE: 'above', BELOW: 'below', CANNOT_TELL: 'cannot tell' }[o] || o) + (o === 'CANNOT_TELL' && why ? ' (' + why + ')' : ''); }
  function fmt(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = (n && typeof t === 'number') ? fmt(t) : t; return c; }
  // 30 Oct 2026 (site pass H-14): a cannot tell row says which kind it is, a share resolved between the two thresholds or an interval that reaches a threshold or too few records.
  function WC(o, lo, hi, lowT, highT, n, why) {
    if (why || o !== 'CANNOT_TELL') return W(o, why);   // 12 Nov 2026 (Standards 2.0): the feed carries the reason, printed beside the word
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
      tr.appendChild(td(pct(g.share_no_results) + ' [' + pct(g.lo) + ', ' + pct(g.hi) + ']', 1)); tr.appendChild(td(plain ? W(g.outcome, g.reason) : WC(g.outcome, g.lo, g.hi, 0.10, 0.25, g.posted + g.no_results, g.reason))); b.appendChild(tr);
    });
    t.appendChild(b); var f = document.createDocumentFragment(); f.appendChild(h); f.appendChild(t); return f;
  }
  function gtable(title, rows, first, cols) {
    var h = document.createElement('h3'); h.textContent = title; var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>' + first + '</th>' + cols.map(function (c) { return '<th>' + c[0] + '</th>'; }).join('') + '</tr></thead>'; var b = document.createElement('tbody');
    rows.forEach(function (r) { var tr = document.createElement('tr'); tr.appendChild(td(r[0])); cols.forEach(function (c) { var v = r[1][c[1]]; tr.appendChild(c[2] === 'pct' ? td(v == null ? '' : pct(v) + ' [' + pct(r[1][c[1] + '_lo']) + ', ' + pct(r[1][c[1] + '_hi']) + ']', 1) : (c[2] === 'oc' ? td(WC(v, r[1].share_lo, r[1].share_hi, 0.05, 0.10, r[1].of, r[1].reason)) : td(v == null ? '' : v, c[2] === 'n'))); }); b.appendChild(tr); });
    t.appendChild(b); var f = document.createDocumentFragment(); f.appendChild(h); f.appendChild(t); return f;
  }
  function cancelled(c) {
    if (!c) return; var s = document.createElement('h2'); s.textContent = 'Stopped trials, last two years'; box.appendChild(s);
    var n = document.createElement('p'); n.className = 'bench-note'; n.textContent = 'Interventional studies with a start date from ' + c.window.start + ' to ' + c.window.end + ' (a withdrawn study can carry an anticipated start). A recent quarter has had less time to be stopped, so shares are not compared across quarters. Reasons are sorted by the first matching word and carry no outcome.'; box.appendChild(n);
    var k = function (o) { return Object.keys(o).map(function (x) { return [x, o[x]]; }); };
    box.appendChild(gtable('Started and since stopped', [['Interventional studies started in the window', c.headline]], 'Group', [['Studies started', 'studies', 'n'], ['Withdrawn', 'withdrawn', 'n'], ['Terminated', 'terminated', 'n'], ['Suspended', 'suspended', 'n'], ['Share stopped', 'share_text', 't']]));
    var cl = { INDUSTRY: 'Industry', NIH: 'NIH', FED: 'Other federal', OTHER_GOV: 'State, local and non-US public bodies (registry class Other government)', NETWORK: 'Network', OTHER: 'Other (universities, hospitals, nonprofits)', INDIV: 'Individual', UNKNOWN: 'Unknown' };
    box.appendChild(gtable('By sponsor class', k(c.by_class).map(function (r) { return [cl[r[0]] || r[0], r[1]]; }), 'Sponsor class', [['Studies started', 'population', 'n'], ['Withdrawn', 'withdrawn', 'n'], ['Terminated', 'terminated', 'n'], ['Suspended', 'suspended', 'n'], ['Share stopped', 'share_text', 't']]));
    box.appendChild(gtable('Reasons given', k(c.reasons).map(function (r) { return [r[0] + (SIX.indexOf(r[0]) >= 0 ? ' (defined after the data)' : ''), r[1]]; }), 'Reason', [['Records', 'n', 'n'], ['Share', 'share_text', 't']]));
    var rn = document.createElement('p'); rn.className = 'bench-note'; rn.textContent = 'The six classes marked defined after the data were added after the first read left 31 percent of the stopped records in one unsorted class. They are tried in order after the first five, so no record already in a class moved. The texts that match none of the words are published in the public data folder.'; box.appendChild(rn);
    box.appendChild(gtable('Two tests against the registry\'s own rules', k(c.tests), 'Test', [['Records', 'of', 'n'], ['Failing', 'n', 'n'], ['Share, 95% interval', 'share', 'pct'], ['Outcome', 'outcome', 'oc']]));
    var tn = document.createElement('p'); tn.className = 'bench-note'; var t1 = (c.tests || {})['Stopped records with no reason given'] || {};
    tn.textContent = (function () { var q = []; Object.keys(c.tests || {}).forEach(function (k) { var t = c.tests[k]; if (t.req13) q.push(k + ': ' + t.req13.line); }); return q.length ? q.join(' ') + ' ' : ''; })() + 'For these two tests the band is 0 to 5 percent, open at 5, and 10 percent is the size that matters. Above means the whole 95% interval lies at or above 5 percent, consistent means it sits inside the band and does not reach both 0 and 10 percent, and fewer than 30 records reads cannot tell (TOO_WIDE_TO_RESOLVE). The intervals treat records as independent although sponsors and programs cluster, so they are narrower than the records justify.' + (t1.largest_sponsor_n ? ' Of the ' + t1.n + ' records in the first test, ' + t1.largest_sponsor_n + ' have the same lead sponsor.' : ''); box.appendChild(tn);
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
    // 10 Nov 2026 (TRIALS Addendum 5, newsletter audit): the plan's lag zone is shown apart and not scored, and a sponsor-clustered interval sits beside the Wilson one
    if (d.lag_zone) { var lz = document.createElement('p'); lz.className = 'bench-note'; lz.textContent = 'Lag zone, not scored: ' + fmt(d.lag_zone.n) + ' records completed after ' + d.lag_zone.completed_after + ', 13 to 15 months before the read, as the plan sets apart. ' + fmt(d.lag_zone.no_results) + ' of them have no results on the record yet. Until 10 Nov 2026 these records were scored, which the plan never allowed.'; box.appendChild(lz); }
    if (d.all.req13) { var rq = document.createElement('p'); rq.className = 'bench-note'; rq.textContent = 'Headline share, REQ-13: ' + d.all.req13.line; box.appendChild(rq); }
    var sc = d.all.sponsor_clustered; if (sc) { var cn = document.createElement('p'); cn.className = 'bench-note'; cn.textContent = 'All scored records: ' + fmt(d.all.no_results) + ' of ' + fmt(d.all.n) + ' have no results on the record, ' + pct(d.all.share_no_results) + '. The plan\'s Wilson interval is ' + pct(d.all.lo) + ' to ' + pct(d.all.hi) + ' and treats each record as independent. Counting the ' + fmt(sc.sponsors) + ' lead sponsors as the units, the interval is ' + pct(sc.lo) + ' to ' + pct(sc.hi) + '. That second interval was defined on 10 Nov 2026, after the data. The outcome is read on the plan\'s interval.'; box.appendChild(cn); }
    var cls = { INDUSTRY: 'Industry', NIH: 'NIH', FED: 'Other federal', OTHER_GOV: 'State, local and non-US public bodies (registry class Other government)', NETWORK: 'Network', OTHER: 'Other (universities, hospitals, nonprofits)', INDIV: 'Individual', UNKNOWN: 'Unknown' };
    box.appendChild(table('By sponsor class', Object.keys(d.by_class).map(function (k) { return [cls[k] || k, d.by_class[k]]; }), 'Sponsor class'));
    if (d.by_class.OTHER_GOV && d.by_class.OTHER_GOV.sponsors) { var og = document.createElement('p'); og.className = 'bench-note'; og.textContent = 'The registry class Other government covers state, local and non-US public bodies. Here it is mostly public universities and hospitals outside the US. Its ' + fmt(d.by_class.OTHER_GOV.n) + ' records come from ' + fmt(d.by_class.OTHER_GOV.sponsors) + ' lead sponsors, so its interval treats a few sponsors as many units.'; box.appendChild(og); }
    box.appendChild(table('By product', [['Drugs', d.by_kind.drug], ['Devices only', d.by_kind.device_only], ['Drugs and devices', d.by_kind.both]], 'Product'));
    box.appendChild(table('By primary completion year', Object.keys(d.by_year).map(function (k) { return [k, d.by_year[k]]; }), 'Year'));
    var det = document.createElement('details'), sm = document.createElement('summary'); sm.textContent = 'Lead sponsors with at least 20 records'; det.appendChild(sm);
    det.appendChild(table('', Object.keys(d.sponsors).map(function (k) { var p = k.split('|'); return [p[0], d.sponsors[k]]; }), 'Lead sponsor', true)); box.appendChild(det);
  }).catch(function () { box.textContent = 'The read could not be loaded just now.'; });
})();
