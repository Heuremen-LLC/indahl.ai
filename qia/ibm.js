// IBM's published calibration, mirrored. Reads /qia/ibm.json, written by the mirror on every run.
(function () {
  var box = document.getElementById('ibm-live'); if (!box) return;
  function f(v, d) { return v == null ? '' : Number(v).toFixed(d); }
  // 30 Oct: IBM stamps carry a US Eastern offset ('2026-10-30 08:48:40-04:00'). They are shown in UTC, like the time column beside them.
  function utc(s) {
    var m = /^(\d{4})-(\d\d)-(\d\d)[ T](\d\d):(\d\d)(?::(\d\d))?(?:\.\d+)?([+-])(\d\d):?(\d\d)$/.exec(String(s));
    if (!m) return String(s).slice(0, 16).replace('T', ' ');
    var t = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)) - (m[7] === '-' ? -1 : 1) * (+m[8] * 60 + +m[9]) * 60000;
    return new Date(t).toISOString().slice(0, 16).replace('T', ' ');
  }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  fetch('/qia/ibm.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var bs = d.backends || []; if (!bs.length) { box.textContent = 'Waiting for the first read.'; return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Processor</th><th>IBM record stamped (UTC)</th><th>Qubits</th><th>T1 median, µs</th><th>T2 median, µs</th><th>Readout error median</th><th>Two-qubit error median</th><th>Records saved</th><th>Restamps, and records with a changed qubit or gate entry, 7 days</th><th>Last read, UTC</th></tr></thead>';
    var tb = document.createElement('tbody');
    bs.forEach(function (b) {
      var r = document.createElement('tr'); r.appendChild(td(b.backend)); r.appendChild(td(utc(b.stamp)));
      r.appendChild(td(b.n_qubits, 1)); r.appendChild(td(f(b.t1_us, 1), 1)); r.appendChild(td(f(b.t2_us, 1), 1)); r.appendChild(td(f(b.readout_error, 4), 1)); r.appendChild(td(f(b.two_qubit_error, 4), 1));
      r.appendChild(td(b.records_saved, 1)); r.appendChild(td(b.restamps_7d + ' and ' + b.value_changes_7d, 1)); r.appendChild(td(b.last_read)); tb.appendChild(r);
    });
    t.appendChild(tb); box.textContent = ''; box.appendChild(t);
    var p = document.createElement('p'); p.className = 'bench-note';
    var lost = 0, known = false; bs.forEach(function (b) { if (b.versions_replaced != null) { known = true; lost += b.versions_replaced; } });
    p.textContent = 'Read from IBM’s published properties for each processor about every half hour. Every record that IBM restamps or changes is saved whole, from ' + (bs[0].since || '') + ' onward. Records saved is the number of saved files. A restamp is a saved record after the first. A changed entry means any qubit or gate entry changed in value or date, and the audit table below counts qubit entries only. ' + (known && lost ? 'Until 30 Oct a record was saved under its stamp alone, so ' + lost + ' earlier versions that IBM changed under an unchanged stamp were overwritten. No record is replaced now. ' : '') + 'Updated ' + (d.updated || '') + ' UTC.';
    box.appendChild(p);
  }).catch(function () { box.textContent = 'The mirror could not be read just now.'; });
})();
