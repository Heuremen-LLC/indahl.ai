// YO reads each new IBM calibration record: YO's flags beside the answer computed by code from the same record. Reads /qia/yo.json.
// The section stays hidden until YO has read a record (the reader runs only after YO's test reading beat its baselines).
(function () {
  var sec = document.getElementById('yo'), box = document.getElementById('yo-reads'); if (!sec || !box) return;
  function h(tag, txt, cls) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function flags(x) { if (!x) return 'no readable answer'; var s = (x.stale || []).join(', '), z = (x.zero || []).join(', '); return 'stale: ' + (s || 'none') + ' · zero: ' + (z || 'none'); }
  function draw(d) {
    if (!d || !d.n) return; sec.hidden = false; box.textContent = '';
    box.appendChild(h('p', 'Records read: ' + d.n + '. Average agreement with the code: ' + (d.mean == null ? '-' : d.mean.toFixed(3)) + ' (1 = the same flags). Exact matches: ' + d.exact + '.', 'bench-note'));
    var t = h('table', null, 'hl-tab'), hd = h('tr'); ['Processor', 'Record stamp', 'YO flagged', 'The code found', 'Agreement'].forEach(function (c) { hd.appendChild(h('th', c)); });
    var th = h('thead'); th.appendChild(hd); t.appendChild(th); var tb = h('tbody');
    (d.latest || []).forEach(function (r) { var tr = h('tr'); [r.backend, r.stamp, flags(r.yo), flags(r.code), r.score.toFixed(2)].forEach(function (c) { tr.appendChild(h('td', c)); }); tb.appendChild(tr); });
    t.appendChild(tb); box.appendChild(t);
    box.appendChild(h('p', 'Updated ' + String(d.updated || '').replace('T', ' ').replace('Z', '') + ' UTC.', 'bench-note'));
  }
  function load() { fetch('/qia/yo.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(draw).catch(function () {}); }
  load(); setInterval(load, 30000);
})();
