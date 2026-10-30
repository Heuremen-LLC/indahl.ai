// QIA audit: IBM's published calibration checked against itself. Reads /qia/audit.json, written after every mirror pull.
(function () {
  var box = document.getElementById('audit-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  // 30 Oct: IBM's dates carry a US Eastern offset ('2026-10-27 15:13:14-04:00'). They are shown in UTC, like the times beside them.
  function dt(s) {
    var m = /^(\d{4})-(\d\d)-(\d\d)[ T](\d\d):(\d\d)(?::(\d\d))?(?:\.\d+)?([+-])(\d\d):?(\d\d)$/.exec(String(s));
    if (!m) return String(s).slice(0, 16).replace('T', ' ');
    var t = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)) - (m[7] === '-' ? -1 : 1) * (+m[8] * 60 + +m[9]) * 60000;
    return new Date(t).toISOString().slice(0, 16).replace('T', ' ');
  }
  fetch('/qia/audit.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ps = d.processors || []; if (!ps.length) { box.textContent = 'Waiting for the first read.'; return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Processor</th><th>Record stamped (UTC)</th><th>Qubits with T2 above 2.5 times T1</th><th>Qubits between 2 and 2.5 times</th><th>Qubits with T1 and T2 dated over a day apart</th><th>Longest gap, hours</th><th>Entries older than a day</th><th>Entries older than 7 days</th><th>Entries in record</th><th>Restamps with no qubit entry changed</th><th>Restamps with a change</th></tr></thead>';
    var b = document.createElement('tbody');
    ps.forEach(function (p) {
      var r = document.createElement('tr'); r.appendChild(td(p.backend)); r.appendChild(td(dt(p.stamp)));
      [p.above, p.cannot_tell, p.mismatch, p.max_gap_h, p.age24, p.age7d, p.entries, p.restamps_no_change, p.restamps_changed].forEach(function (v) { r.appendChild(td(v, 1)); }); b.appendChild(r);
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(t);
    if ((d.flagged || []).length) {
      var h = document.createElement('h3'); h.textContent = 'Qubits marked above, as IBM published them'; box.appendChild(h);
      var f = document.createElement('table'); f.className = 'mtx';
      f.innerHTML = '<thead><tr><th>Processor</th><th>Qubit</th><th>T1, µs and date (UTC)</th><th>T2, µs and date (UTC)</th><th>T2 over T1</th><th>Records marked, of saved</th></tr></thead>';
      var fb = document.createElement('tbody');
      d.flagged.forEach(function (x) {
        var r = document.createElement('tr'); r.appendChild(td(x.backend)); r.appendChild(td(x.qubit, 1)); r.appendChild(td(x.t1 + ', ' + dt(x.t1_date), 1)); r.appendChild(td(x.t2 + ', ' + dt(x.t2_date), 1)); r.appendChild(td(x.ratio, 1)); r.appendChild(td(x.records_seen + ' of ' + x.records, 1)); fb.appendChild(r);
      });
      f.appendChild(fb); box.appendChild(f);
    }
    var p = document.createElement('p'); p.className = 'bench-note';
    p.textContent = 'Counts are for each processor’s newest saved record. Restamps compare consecutive saved records entry by entry for value and date, for qubit entries only. Dates are in UTC. Updated ' + d.updated + ' UTC. Plan, script and recount: github.com/Heuremen-LLC/indahl.ai/tree/main/code/mirror';
    box.appendChild(p);
  }).catch(function () { box.textContent = 'The audit could not be read just now.'; });
})();
