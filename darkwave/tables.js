// Darkwave Correction Kit, "Today's tables": reads /darkwave/tables/latest.json and lists, per chip, when the table was measured, the calibration
// record in force, the readout set and a download of the table in the kit's format. Every time shown is UTC. Page text is set with textContent only.
(function (root) {
  'use strict';
  var CHIPS = ['ibm_kingston', 'ibm_marrakesh'];
  function stamp(s) { var m = /^(\d{4}-\d\d-\d\d)T(\d\d:\d\d)/.exec(String(s || '')); return m ? m[1] + ' ' + m[2] + ' UTC' : ''; }
  function age(s, now) {
    var t = Date.parse(s); if (!isFinite(t)) return '';
    var h = Math.floor((now - t) / 3600000); if (h < 0) return '';
    return h < 1 ? 'less than an hour ago' : h < 48 ? h + (h === 1 ? ' hour ago' : ' hours ago') : Math.floor(h / 24) + ' days ago';
  }
  function describe(name, c, now) {
    if (!c) return { name: name, none: true, rows: [], links: [], readout: [] };
    var rec = c.calibration_record_in_force, during = c.records_stamped_during_run || [], rows = [];
    rows.push(['Measured', stamp(c.measured_utc) + (age(c.measured_utc, now) ? ' (' + age(c.measured_utc, now) + ')' : '')]);
    rows.push(['Calibration record in force', rec && rec.stamp_utc ? 'stamped ' + stamp(rec.stamp_utc) : 'not held by our mirror']);
    if (during.length) rows.push(['Records stamped during the run', during.map(stamp).join(', ')]);
    rows.push(['Readout set', c.readout.length + ' qubits']);
    rows.push(['Targets', c.n_targets + ' qubits']);
    rows.push(['IBM job', c.job_id]);
    return { name: name, none: false, rows: rows, readout: c.readout,
             links: [['Download the table (kit format)', c.kit_table_url], ['Table with bands and coherence (JSON)', c.table_url]] };
  }
  function el(doc, tag, text, cls) { var e = doc.createElement(tag); if (text != null) e.textContent = text; if (cls) e.className = cls; return e; }
  function safeUrl(u) { return /^\/darkwave\/tables\/[a-z0-9_\/.\-]+\.json$/.test(String(u || '')) ? u : '#'; }
  function render(doc, host, data, now) {
    while (host.firstChild) host.removeChild(host.firstChild);
    var chips = (data && data.chips) || {};
    CHIPS.forEach(function (name) {
      var d = describe(name, chips[name], now), box = el(doc, 'div', null, 'dwt-chip'); box.appendChild(el(doc, 'h3', name));
      if (d.none) { box.appendChild(el(doc, 'p', 'No table yet.')); host.appendChild(box); return; }
      d.rows.forEach(function (r) { var p = el(doc, 'p'); p.appendChild(el(doc, 'strong', r[0] + ': ')); p.appendChild(doc.createTextNode(r[1])); box.appendChild(p); });
      var det = el(doc, 'details', null, 'runbox'); det.appendChild(el(doc, 'summary', 'Readout set, qubit numbers')); det.appendChild(el(doc, 'p', d.readout.join(', '))); box.appendChild(det);
      var p = el(doc, 'p');
      d.links.forEach(function (l, i) { var a = el(doc, 'a', l[0]); a.setAttribute('href', safeUrl(l[1])); if (i === 0) a.setAttribute('download', ''); if (i) p.appendChild(doc.createTextNode(' | ')); p.appendChild(a); });
      box.appendChild(p); host.appendChild(box);
    });
  }
  function start() {
    var host = root.document.getElementById('tables-live'); if (!host) return;
    root.fetch('/darkwave/tables/latest.json', { cache: 'no-store' }).then(function (r) { return r.json(); })
      .then(function (d) { render(root.document, host, d, Date.now()); })
      .catch(function () { host.textContent = 'The tables could not be loaded. Try again later.'; });
  }
  var api = { describe: describe, render: render, stamp: stamp, age: age };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else { root.DarkwaveTables = api; if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', start); else start(); }
})(typeof window !== 'undefined' ? window : globalThis);
