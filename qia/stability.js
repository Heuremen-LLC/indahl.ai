// QIA stability index: what IBM published about itself over time. Reads /qia/stability.json, written after every mirror pull.
(function () {
  var box = document.getElementById('stability-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  function sh(a) { return a[0] + ' of ' + a[1] + ' [' + (100 * a[2]).toFixed(0) + '%, ' + (100 * a[3]).toFixed(0) + '%]'; }
  fetch('/qia/stability.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ps = d.processors || []; if (!ps.length) { box.textContent = 'Waiting for the first records.'; return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Processor</th><th>Records held</th><th>Days spanned</th><th>T1 measured again since the first record, Wilson 95% interval</th><th>T2 measured again since the first record, Wilson 95% interval</th><th>T1 and T2 dated over a day apart, newest record, Wilson 95% interval</th><th>Median age of T1, hours</th><th>Median age of T2, hours</th><th>Ever above 2 times</th><th>Ever above 2.5 times</th><th>Never flagged</th><th>Reading</th></tr></thead>';
    var b = document.createElement('tbody');
    ps.forEach(function (p) {
      var r = document.createElement('tr'); r.appendChild(td(p.backend)); r.appendChild(td(p.records, 1)); r.appendChild(td(p.days, 1)); r.appendChild(td(sh(p.remeasured_t1), 1)); r.appendChild(td(sh(p.remeasured_t2), 1)); r.appendChild(td(sh(p.apart), 1));
      r.appendChild(td(p.median_age_t1_h, 1)); r.appendChild(td(p.median_age_t2_h, 1)); r.appendChild(td(p.flagged_over_2, 1)); r.appendChild(td(p.flagged_over_2_5, 1)); r.appendChild(td(p.clean_throughout, 1)); r.appendChild(td(p.too_few ? 'too few records' : 'read')); b.appendChild(r);
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(t);
    var p = document.createElement('p'); p.className = 'bench-note'; p.textContent = 'A row is read once 20 records and 14 days are held for that processor. A share is printed as a count, then its Wilson 95% interval in brackets. This table describes what IBM published about itself and tests no claim. Updated ' + d.updated + ' UTC.'; box.appendChild(p);
  }).catch(function () { box.textContent = 'The index could not be read just now.'; });
})();
