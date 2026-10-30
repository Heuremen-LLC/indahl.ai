// QIA: T1 and T2 measured together on the qubits the audit flagged, against what IBM published. Reads /qia/t1t2.json, written by publish_results.py.
(function () {
  var box = document.getElementById('t1t2-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t == null ? '' : t; return c; }
  function ci(v, c) { return v == null ? '' : v + (c && c.length ? ' [' + c[0] + ', ' + c[1] + ']' : ''); }
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', BELOW: 'below', CANNOT_TELL: 'cannot tell' }[o] || o; }
  fetch('/qia/t1t2.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ps = d.processors || []; if (!ps.length) { box.textContent = 'Waiting for the first job.'; return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Processor</th><th>Qubit</th><th>Role</th><th>T1 measured now, µs (95% interval)</th><th>T2 echo measured now, µs (95% interval)</th><th>T2 over T1, 95% interval</th><th>IBM published T1, µs, date (US Eastern)</th><th>IBM published T2, µs, date (US Eastern)</th><th>IBM T1 against the qubit now</th><th>IBM T2 against the qubit now (most it can be: 2 x T1)</th><th>T2 over T1 reading under the plan</th><th>Printed by the script</th></tr></thead>';
    var b = document.createElement('tbody');
    ps.forEach(function (p) {
      if (p.state !== 'ran') { var r = document.createElement('tr'); r.appendChild(td(p.backend)); var c = document.createElement('td'); c.colSpan = 11; c.textContent = p.state; r.appendChild(c); b.appendChild(r); return; }
      p.qubits.forEach(function (q) {
        var r = document.createElement('tr'); r.appendChild(td(p.backend + ' (' + p.ran + ' UTC)')); r.appendChild(td(q.qubit, 1)); r.appendChild(td(q.control ? 'control' : 'flagged')); r.appendChild(td(ci(q.t1, q.t1_ci), 1)); r.appendChild(td(ci(q.t2, q.t2_ci), 1));
        r.appendChild(td(ci(q.ratio, q.ratio_ci), 1)); r.appendChild(td(q.pub_t1 + ', ' + q.pub_t1_date, 1)); r.appendChild(td(q.pub_t2 + ', ' + q.pub_t2_date, 1)); r.appendChild(td(W(q.ibm_t1_vs_now || ''))); r.appendChild(td(W(q.ibm_t2_vs_now || '') + (q.t2_max_now != null ? ' (at most ' + q.t2_max_now + ')' : ''))); r.appendChild(td(W(q.reading) + (q.fit_on_bound ? ' (a fit sits on its bound)' : ''))); r.appendChild(td(W(q.printed))); b.appendChild(r);
      });
    });
    t.appendChild(b); box.textContent = '';
    var hits = []; ps.forEach(function (p) { (p.qubits || []).forEach(function (q) { if (!q.control && q.ibm_t2_vs_now === 'ABOVE') hits.push(p.backend + ' qubit ' + q.qubit + ' (' + p.ran + ' UTC): IBM publishes T2 ' + q.pub_t2 + ' µs, dated ' + q.pub_t2_date + ' US Eastern; this qubit can have at most ' + q.t2_max_now + ' µs now, measured T2 ' + ci(q.t2, q.t2_ci) + ' µs (95% interval)'); }); });
    if (hits.length) { var lead = document.createElement('div'); lead.className = 'bench-note'; var h = document.createElement('p'); h.innerHTML = '<b>IBM\u2019s published T2 is above what the qubit can have when we measured it:</b>'; lead.appendChild(h); var ul = document.createElement('ul'); hits.forEach(function (x) { var li = document.createElement('li'); li.textContent = x; ul.appendChild(li); }); lead.appendChild(ul); box.appendChild(lead); }
    box.appendChild(t);
    var n = document.createElement('p'); n.className = 'bench-note'; n.textContent = 'Controls passed their known-good gate in every job that ran. A joint measurement now does not date a past record, and IBM does not state whether its T2 is echo or Ramsey, but any T2 of either kind is at most 2 x T1, so a published T2 above 2 x the top of our measured T1 interval reads ABOVE: no T2 that large is possible on that qubit when we measured it. Inside that bound it reads cannot tell. The plan was committed before the results were read. Notes 3, 4 and 6 were written after some results were read. Note 3 followed the fez and kingston results. Note 4 set a second fez run after the first fez result. Note 6 followed the boston, kingston and fez results. Where the last two columns differ (fez qubit 148, first run), the script’s printed word is kept as printed and Note 3 gives the reading under the plan, which stands. Updated ' + d.updated + ' UTC.'; box.appendChild(n);
  }).catch(function () { box.textContent = 'The results could not be read just now.'; });
})();
