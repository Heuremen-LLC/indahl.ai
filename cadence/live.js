// CADENCE: stated update cadence against delivered. Reads /cadence/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('cadence-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  function sh(a) { return a ? a[0] + '% [' + a[1] + ', ' + a[2] + ']' : ''; }
  fetch('/cadence/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ps = d.portals || []; if (!ps.length) { box.textContent = 'Waiting for the first portal.'; return; }
    var top = document.createElement('p'); top.className = 'bench-note'; top.textContent = 'Each portal is read once a day. Records that share a landing page are one series, read through the newest record. Updated ' + d.updated + ' UTC.';
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Portal</th><th>Records stating a cadence</th><th>Series</th><th>On schedule</th><th>Behind</th><th>Cannot tell</th><th>Behind, 95% interval</th><th>Download date agrees with listed date</th><th>Read</th></tr></thead>';
    var b = document.createElement('tbody');
    ps.forEach(function (p) { var r = document.createElement('tr'), h = p.heads || {}; r.appendChild(td(p.portal)); r.appendChild(td(p.stating_cadence, 1)); r.appendChild(td(p.series, 1)); r.appendChild(td(p.consistent, 1)); r.appendChild(td(p.below, 1)); r.appendChild(td(p.cannot_tell, 1)); r.appendChild(td(sh(p.below_share), 1)); r.appendChild(td(h.comparable ? h.agree + ' of ' + h.comparable : 'sampling', 1)); r.appendChild(td(p.read)); b.appendChild(r); });
    t.appendChild(b); box.textContent = ''; box.appendChild(top); box.appendChild(t);
    var h3 = document.createElement('h3'); h3.textContent = 'The series furthest past their stated cadence'; box.appendChild(h3);
    var t2 = document.createElement('table'); t2.className = 'mtx'; t2.innerHTML = '<thead><tr><th>Series</th><th>Portal</th><th>States</th><th>Last modified</th><th>Days since</th><th>Times its cadence</th></tr></thead>'; var b2 = document.createElement('tbody');
    (d.most_overdue || []).forEach(function (x) { var r = document.createElement('tr'), c = document.createElement('td'); if (x.link && /^https?:\/\//.test(x.link)) { var a = document.createElement('a'); a.href = x.link; a.textContent = x.title; c.appendChild(a); } else c.textContent = x.title; r.appendChild(c); r.appendChild(td(x.portal)); r.appendChild(td(x.cadence)); r.appendChild(td(x.modified)); r.appendChild(td(x.age_days, 1)); r.appendChild(td(x.ratio, 1)); b2.appendChild(r); });
    t2.appendChild(b2); box.appendChild(t2);
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
