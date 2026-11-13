// WATER: projected reservoir levels against measured levels, and a live panel. Reads /water/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('water-live'); if (!box) return;
  var NAME = { mead: 'Lake Mead', powell: 'Lake Powell' };
  var OC = { CONSISTENT: 'consistent', ABOVE: 'above', BELOW: 'below', CANNOT_TELL: 'cannot tell', NOTHING_RETURNED: 'nothing returned' };
  var TEST = { band: 'band', mp: 'Most Probable' };
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function td(t, n) { return el('td', n ? 'n' : null, t == null ? '' : String(t)); }
  function ft(x) { return x == null ? '' : Number(x).toFixed(2); }
  function sg(x) { return x == null ? '' : (x > 0 ? '+' : '') + Number(x).toFixed(2); }
  function pc(x) { return x == null ? '' : (100 * x).toFixed(1) + '%'; }
  function fmt(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function ow(o, r) { var w = OC[o] || o; return (o === 'CANNOT_TELL' && r) ? w + ' (' + r + ')' : w; }   // the reading word with its Standards 2.0 reason beside cannot tell
  function note(t) { box.appendChild(el('p', 'bench-note', t)); }
  function table(head, rows) {
    var t = el('table', 'mtx'), h = el('thead'), tr = el('tr'); head.forEach(function (x) { tr.appendChild(el('th', null, x)); }); h.appendChild(tr); t.appendChild(h);
    var b = el('tbody'); rows.forEach(function (r) { var row = el('tr'); r.forEach(function (c) { row.appendChild(c); }); b.appendChild(row); }); t.appendChild(b); return t;
  }
  function cell(d, k, lead) { return (d.cells || []).filter(function (x) { return x.res === k && x.lead === lead; })[0]; }
  fetch('/water/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.updated) { box.textContent = 'Waiting for the first reading.'; return; }
    box.textContent = '';
    if (d.stale_sources && d.stale_sources.length) note('Some sources could not be read on the last run and their previous copy is shown: ' + d.stale_sources.join(', ') + '.');
    var L = d.live || {}, X = d.measured_cross_checks || {};
    // live panel
    box.appendChild(el('h3', null, 'Lake Mead and Lake Powell now'));
    var lr = [];
    ['mead', 'powell'].forEach(function (k) {
      var x = L[k]; if (!x) return; var r60 = x.largest_rise_60d || {};
      function rs(n) { var z = r60[n]; return z ? sg(z.rise_ft) + ' (' + z.start + ' to ' + z.end + ')' : ''; }
      lr.push([td(x.name), td(ft(x.daily_ft) + ' on ' + x.daily_date, 1), td(x.hourly_ft == null ? '' : ft(x.hourly_ft) + ' at ' + x.hourly_time.replace('T', ' ') + ':00', 1), td(sg(x.change_1d), 1), td(sg(x.change_7d), 1), td(sg(x.change_30d), 1), td(rs('1'), 1), td(rs('2'), 1), td(rs('7'), 1)]);
    });
    box.appendChild(table(['Reservoir', 'End of day, ft', 'Latest hour, ft', '1 day', '7 days', '30 days', 'Largest 1 day rise, last 60 days (added after the plan)', 'Largest 2 day rise (added after the plan)', 'Largest 7 day rise (added after the plan)'], lr));
    var n1 = 'Elevations in feet from Reclamation\'s HDB, daily end-of-day and hourly readings, Mountain Standard Time. Changes are end of day against end of day. For Lake Mead ' + ((L.datum || {}).mead || '') + ' ' + ((L.datum || {}).powell || '');
    var P = X.powell_usgs_daily_mean_minus_hdb_end_of_day;
    if (L.powell_usgs) n1 += ' USGS 09379900 at Glen Canyon Dam read ' + ft(L.powell_usgs.ft) + ' ft (NGVD 1929, ' + (L.powell_usgs.qualifiers || []).join(' ') + ') at ' + L.powell_usgs.time + '.' + (P ? ' Over ' + fmt(P.days) + ' days the USGS daily mean minus the HDB end-of-day reading has a median of ' + sg(P.median) + ' ft.' : '');
    ['mead', 'powell'].forEach(function (k) { var x = L[k]; if (x && x.lowest_daily_since_dec_1999) n1 += ' Added after the plan: the lowest ' + x.name + ' end-of-day reading in the HDB daily record we read, which starts in December 1999, is ' + ft(x.lowest_daily_since_dec_1999.ft) + ' ft on ' + x.lowest_daily_since_dec_1999.date + '.'; });
    note(n1);
    box.appendChild(el('h3', null, 'Elevations named in the 2007 Interim Guidelines and the 2027-2028 Operating Guidelines'));
    var tr = (L.thresholds || []).map(function (t) {
      return [td(NAME[t.res]), td(fmt(t.ft) + ' ft', 1), td(t.current_minus_threshold_ft == null ? '' : sg(t.current_minus_threshold_ft), 1), td(t.doc + ', section ' + t.section + ' (' + t.governs + ')'), td('"' + t.quote + '"')];
    });
    box.appendChild(table(['Reservoir', 'Elevation', 'Latest end of day minus it, ft', 'Document', 'Quoted text'], tr));
    (L.threshold_notes || []).forEach(function (n) { note(n.doc + ', ' + n.section + ', ' + n.what + ': "' + n.quote + '"'); });
    var oth = (L.others || []).map(function (o) { return [td(o.name), td(o.agency), td(o.date), td(fmt(o.storage_af), 1), td(fmt(o.stated_capacity_af), 1), td(pc(o.share), 1), td(o.capacity_label)]; });
    if (oth.length) { box.appendChild(el('h3', null, 'Reservoir storage against stated capacity')); box.appendChild(table(['Reservoir', 'Agency', 'Date', 'Storage, acre-feet', 'Stated capacity, acre-feet', 'Share', 'What the capacity figure is'], oth)); note('A share of stated capacity is a reading, not a test. Capacity is the figure the operating agency prints in the report named.'); }
    // the study test
    var c = d.coverage || {};
    box.appendChild(el('h3', null, '24-Month Study projections against the measured level'));
    note('Reports read: ' + fmt(c.reports || 0) + ' (issued ' + c.first_issue + ' to ' + c.last_issue + '). Issue months with both a Probable Minimum and a Probable Maximum report: ' + (c.band_months || 0) + '. Rows scored or waiting: ' + fmt(c.rows || 0) + '. Values left unreadable: ' + fmt(c.unreadable_values || 0) + '. Measured through ' + ((c.measured_last || {}).mead || '') + '. Known-good checks: ' + d.gate + '. Updated ' + d.updated + ' UTC.');
    var inv = c.inverted_detail || {}, z0 = c.zero_width_lead0 || {};
    note('Band rows where the Probable Minimum projection sits above the Probable Maximum projection: ' + fmt(c.inverted_band_rows || 0) + ' (' + (inv.powell || 0) + ' Lake Powell, ' + (inv.powell_leads_0_to_5 || 0) + ' of them 0 to 5 months ahead, and ' + (inv.mead || 0) + ' Lake Mead). Band rows with zero width, where the two projections agree to 0.005 ft: ' + fmt(c.zero_width_band_rows || 0) + ', including ' + ((z0.mead || [])[0] || 0) + ' of ' + ((z0.mead || [])[1] || 0) + ' Lake Mead and ' + ((z0.powell || [])[0] || 0) + ' of ' + ((z0.powell || [])[1] || 0) + ' Lake Powell bands at 0 months ahead. Most Probable values outside their own band: ' + fmt(c.mp_outside_own_band_rows || 0) + '. Every band is tested as printed.');
    var er = (d.misread_by_era || []).filter(function (e) { return e.months_compared; }).map(function (e) { return e.era + ': ' + e.misread + ' of ' + fmt(e.months_compared) + ' (' + (100 * e.rate).toFixed(2) + '%), ' + fmt(e.print_only_values) + ' values read from print only'; });
    if (er.length) note('Where an HDB run agrees with the print, our reading of the print differed from HDB on: ' + er.join('. ') + '. Values read only from print carry about the same rate for their era, unchecked. A misread of a whole digit, such as 10 ft, can pass the neighbour rule.');
    ['mead', 'powell'].forEach(function (k) {
      var rows = (d.cells || []).filter(function (x) { return x.res === k; }).map(function (x) {
        var b = x.band, m = x.mp;
        return [td(x.lead, 1), td(b.n ? b.inside + ' of ' + b.n + ' (' + pc(b.inside / b.n) + ')' : '', 1), td(b.n ? b.above + ' / ' + b.below : '', 1), td(b.n_wy ? '[' + pc(b.lo) + ', ' + pc(b.hi) + '] on ' + b.n_wy + ' water years' : '', 1), td(ow(b.outcome, b.reason)), td(b.median_width_ft == null ? '' : ft(b.median_width_ft), 1), td(b.zero_width, 1),
                td(m.n ? m.above + ' of ' + m.n : '', 1), td(sg(m.median_error), 1), td(m.p10 == null ? '' : sg(m.p10) + ' to ' + sg(m.p90), 1), td(m.n_wy ? '[' + pc(m.lo) + ', ' + pc(m.hi) + '] on ' + m.n_wy + ' water years' : '', 1), td(ow(m.outcome, m.reason))];
      });
      box.appendChild(el('h3', null, NAME[k] + ', by months ahead'));
      box.appendChild(table(['Months ahead', 'Inside the Min to Max band', 'Above / below the band', 'Inside share, 95% interval', 'Band outcome', 'Median band width, ft (defined after the data)', 'Zero-width bands', 'Ended above Most Probable', 'Median error, ft', 'Middle 80% of errors, ft', 'Above share, 95% interval', 'Most Probable outcome'], rows));
    });
    var F = d.flagged || {};
    var fl = (F.groups || []).map(function (g) { return NAME[g.res] + ' ' + TEST[g.test] + ' ' + OC[g.outcome] + ' at ' + (g.n === 1 ? 'lead ' : 'leads ') + g.leads; });
    note('Cells reading above or below: ' + F.flagged + ' of ' + F.cells + '. ' + fl.join('. ') + '. ' + (F.note || ''));
    note('No cell can read consistent at this sample size. With about 20 water years in a cell, a 95% interval is about 0.33 wide, and fitting inside 70 to 90 percent would need about 61 water years (inside 40 to 60 percent, about 96). The desk can read a miss or cannot tell.');
    note('How a cell reads: above if the lower bound of its interval is above the stated figure (80 percent for the band, 50 percent for the Most Probable test), below if the upper bound is under it, consistent if the whole interval lies inside 70 to 90 percent (40 to 60 percent for the Most Probable test), otherwise cannot tell with the reason STRADDLES_EDGE. Fewer than 10 water years is cannot tell with the reason TOO_WIDE_TO_RESOLVE, and no water years is NO_INTERVAL_FORMABLE. Edges are closed. No size that matters is named for these cells, so the check for an interval that holds both zero and a size that matters is not applied.');
    var rq = []; ['mead', 'powell'].forEach(function (k) { var x = cell(d, k, 6); if (!x) return; if (x.band.req13) rq.push(NAME[k] + ' band at 6 months: ' + x.band.req13.line); if (x.mp.req13) rq.push(NAME[k] + ' Most Probable at 6 months: ' + x.mp.req13.line); });
    if (rq.length) note('Rows behind the six-month cells, with the rows not yet measured set apart. ' + rq.join(' '));
    var s6 = [];
    ['mead', 'powell'].forEach(function (k) {
      var x = cell(d, k, 6); if (!x) return; var ch = x.band.checks_after_data || {};
      function r(nm, lab) { var z = ch[nm]; if (!z) return ''; var t = lab + ' [' + pc(z.lo) + ', ' + pc(z.hi) + '] on ' + z.n + ', ' + ow(z.outcome, z.reason); if (nm !== 'rows_as_independent' && z.outcome_unrounded !== z.outcome) t += ' (without rounding the count, [' + pc(z.lo_unrounded) + ', ' + pc(z.hi_unrounded) + '], ' + ow(z.outcome_unrounded, z.reason_unrounded) + ')'; return t; }
      s6.push(NAME[k] + ' band at 6 months: plan ruler [' + pc(x.band.lo) + ', ' + pc(x.band.hi) + '] on ' + x.band.n_wy + ' water years, ' + ow(x.band.outcome, x.band.reason) + '. ' + [r('kish_weighted_water_years', 'Water years weighted by row count'), r('two_water_year_blocks', 'Pairs of water years'), r('rows_as_independent', 'Rows as independent')].join('. '));
    });
    note('Checks added after the data, never used for the outcome. ' + s6.join('. ') + '. The plan ruler treats water years as independent. Correlation of the inside share between neighbouring water years: ' + ['mead', 'powell'].map(function (k) { var a = cell(d, k, 6), b = cell(d, k, 12); return NAME[k] + ' ' + (a ? a.band.wy_lag1_corr : '') + ' at 6 months and ' + (b ? b.band.wy_lag1_corr : '') + ' at 12 months'; }).join(', ') + '.');
    var S = d.band_sentence_months || {}, sc = (S.cells || []).filter(function (x) { return x.lead === 6; });
    if (sc.length) note('Added after the data: on the ' + (S.months || []).length + ' issue months whose two band reports both print the 80 percent sentence, the band at 6 months reads ' + sc.map(function (x) { return NAME[x.res] + ' ' + x.inside + ' of ' + x.n + ', [' + pc(x.lo) + ', ' + pc(x.hi) + '] on ' + x.n_wy + ' water years, ' + ow(x.outcome, x.reason); }).join(', ') + '.');
    var M = X.mead_hdb_vs_lc_table;
    if (M) note('Measured-side cross-check, not used for scoring: Reclamation\'s HDB monthly table and its Lower Colorado end-of-month web table differ for Lake Mead in ' + M.differ_since_1990 + ' months since 1990 (' + M.differ_since_2000 + ' since 2000). The largest gap since 2000 is ' + (M.largest_since_2000 ? M.largest_since_2000.month + ', HDB ' + ft(M.largest_since_2000.hdb) + ' ft against ' + ft(M.largest_since_2000.lc_table) + ' ft' : 'none') + '. Scoring uses HDB, as planned.');
    var nb = (d.notable || []).map(function (n) { return [td(NAME[n.res]), td(n.kind), td(n.issue), td(n.target), td(n.lead, 1), td(ft(n.pmin), 1), td(ft(n.mp), 1), td(ft(n.pmax), 1), td(ft(n.measured), 1), td(sg(n.mp_error), 1), td(ow(n.outcome, n.reason))]; });
    if (nb.length) { box.appendChild(el('h3', null, 'Rows to read')); box.appendChild(table(['Reservoir', 'Row', 'Issued', 'Month', 'Months ahead', 'Probable Minimum', 'Most Probable', 'Probable Maximum', 'Measured', 'Measured minus Most Probable', 'Band outcome'], nb)); note('These rows are the five largest Most Probable misses at 1 to 12 months ahead for each lake, and every projection of the latest measured month made 0 to 12 months ahead. The selection is not in the plan.'); }
    var vr = (d.variants || []).filter(function (v) { return v.measured != null; }).map(function (v) { return [td(NAME[v.res]), td(v.report), td(v.target), td(v.lead, 1), td(ft(v.mp), 1), td(ft(v.measured), 1), td(sg(v.mp_error), 1)]; });
    var vw = (d.variants || []).length;
    if (vw) { box.appendChild(el('h3', null, 'The 6.0 maf Most Probable runs, shown apart')); if (vr.length) box.appendChild(table(['Reservoir', 'Report', 'Month', 'Months ahead', '6.0 maf Most Probable', 'Measured', 'Measured minus it'], vr)); note('From August 2026 Reclamation issues two official Most Probable runs, one with a 6.0 maf and one with a 7.0 maf Lake Powell release. The cells above use the 7.0 maf run, as the plan says. Rows from the 6.0 maf runs: ' + vw + ', of which ' + vr.length + ' have a measured month so far.'); }
    var u = d.usgs_revisions || {};
    var ur = (u.gauges || []).map(function (g) { return [td('USGS ' + g.site), td(g.parameter === '62614' ? 'elevation' : 'discharge'), td(fmt(g.provisional_days_stored), 1), td(fmt(g.approved_since), 1), td(g.approved_since ? g.revised_beyond_threshold + ' (more than ' + g.threshold + ')' : '', 1)]; });
    if (ur.length) { box.appendChild(el('h3', null, 'USGS provisional values against approved values')); box.appendChild(table(['Gauge', 'Measure', 'Provisional days stored', 'Approved since', 'Revised beyond the threshold'], ur)); note('Stored from ' + u.first_read + '. A day counts only if we stored it as provisional before USGS approved it. No history before our first read is claimed.'); }
  }).catch(function () { box.textContent = 'The reading could not be loaded just now.'; });
})();
