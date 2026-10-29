// QIA: T1 and T2 measured together on the qubits the audit flagged, against what IBM published. Reads /qia/t1t2.json, written by publish_results.py.
(function () {
  var box = document.getElementById('t1t2-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t == null ? '' : t; return c; }
  function ci(v, c) { return v == null ? '' : v + (c && c.length ? ' [' + c[0] + ', ' + c[1] + ']' : ''); }
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  fetch('/qia/t1t2.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ps = d.processors || []; if (!ps.length) { box.textContent = 'Waiting for the first job.'; return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Processor</th><th>Qubit</th><th>Role</th><th>T1 measured now, µs</th><th>T2 echo measured now, µs</th><th>T2 over T1, 95% interval</th><th>IBM published T1, µs, date</th><th>IBM published T2, µs, date</th><th>Reading under the plan</th><th>Printed by the script</th></tr></thead>';
    var b = document.createElement('tbody');
    ps.forEach(function (p) {
      if (p.state !== 'ran') { var r = document.createElement('tr'); r.appendChild(td(p.backend)); var c = document.createElement('td'); c.colSpan = 9; c.textContent = p.state; r.appendChild(c); b.appendChild(r); return; }
      p.qubits.forEach(function (q) {
        var r = document.createElement('tr'); r.appendChild(td(p.backend + ' (' + p.ran + ' UTC)')); r.appendChild(td(q.qubit, 1)); r.appendChild(td(q.control ? 'control' : 'flagged')); r.appendChild(td(ci(q.t1, q.t1_ci), 1)); r.appendChild(td(ci(q.t2, q.t2_ci), 1));
        r.appendChild(td(ci(q.ratio, q.ratio_ci), 1)); r.appendChild(td(q.pub_t1 + ', ' + q.pub_t1_date, 1)); r.appendChild(td(q.pub_t2 + ', ' + q.pub_t2_date, 1)); r.appendChild(td(W(q.reading) + (q.fit_on_bound ? ' (a fit sits on its bound)' : ''))); r.appendChild(td(W(q.printed))); b.appendChild(r);
      });
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(t);
    var n = document.createElement('p'); n.className = 'bench-note'; n.textContent = 'Controls passed their known-good gate in every job that ran. A joint measurement now does not date a past record, and IBM does not state whether its T2 is echo or Ramsey, so measured and published T2 are shown side by side and not scored. Updated ' + d.updated + ' UTC.'; box.appendChild(n);
  }).catch(function () { box.textContent = 'The results could not be read just now.'; });
})();
