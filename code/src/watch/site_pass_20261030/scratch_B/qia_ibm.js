// IBM's published calibration, mirrored. Reads /qia/ibm.json, written by the mirror on every run.
(function () {
  var box = document.getElementById('ibm-live'); if (!box) return;
  function f(v, d) { return v == null ? '' : Number(v).toFixed(d); }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  fetch('/qia/ibm.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var bs = d.backends || []; if (!bs.length) { box.textContent = 'Waiting for the first read.'; return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Processor</th><th>IBM record stamped</th><th>Qubits</th><th>T1 median, µs</th><th>T2 median, µs</th><th>Readout error median</th><th>Two-qubit error median</th><th>Records saved</th><th>Restamps and value changes, 7 days</th><th>Last read, UTC</th></tr></thead>';
    var tb = document.createElement('tbody');
    bs.forEach(function (b) {
      var r = document.createElement('tr'); r.appendChild(td(b.backend)); r.appendChild(td(String(b.stamp).slice(0, 16).replace('T', ' ')));
      r.appendChild(td(b.n_qubits, 1)); r.appendChild(td(f(b.t1_us, 1), 1)); r.appendChild(td(f(b.t2_us, 1), 1)); r.appendChild(td(f(b.readout_error, 4), 1)); r.appendChild(td(f(b.two_qubit_error, 4), 1));
      r.appendChild(td(b.records_saved, 1)); r.appendChild(td(b.restamps_7d + ' and ' + b.value_changes_7d, 1)); r.appendChild(td(b.last_read)); tb.appendChild(r);
    });
    t.appendChild(tb); box.textContent = ''; box.appendChild(t);
    var p = document.createElement('p'); p.className = 'bench-note';
    p.textContent = 'Read from IBM’s published properties for each processor every few minutes. Every record that IBM restamps or changes is saved whole, from ' + (bs[0].since || '') + ' onward. A restamp with the same values counts as a restamp only. Updated ' + (d.updated || '') + ' UTC.';
    box.appendChild(p);
  }).catch(function () { box.textContent = 'The mirror could not be read just now.'; });
})();
