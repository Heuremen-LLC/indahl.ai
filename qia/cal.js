// QIA hourly calibration: every qubit of every IBM processor we can reach, measured each hour against the record IBM had in force when our job ran.
(function () {
  var box = document.getElementById('cal-live'); if (!box) return;
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function n(c, o) { return c && c[o] != null ? c[o] : 0; }
  fetch('/qia/cal.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var P = d.processors || {}, names = Object.keys(P).sort(); box.textContent = '';
    if (!names.length) { box.textContent = 'The first runs are in IBM’s queues.'; return; }
    var t = el('table', 'mtx'); t.innerHTML = '<thead><tr><th>Processor</th><th>Our job ran (UTC)</th><th>Qubits read</th><th>Seat check</th><th>Readout P(1|0): IBM above / below ours</th><th>Readout P(0|1): IBM above / below ours</th><th>T1: IBM above / below ours (cannot tell)</th><th>Every qubit</th></tr></thead>';
    var b = el('tbody');
    names.forEach(function (k) {
      var p = P[k], c = p.counts || {}, r = el('tr');
      [k, (p.window_utc || [''])[0].replace('T', ' ').slice(0, 16) + ((d.waiting || {})[k] && (d.waiting[k] > ((p.window_utc || [''])[0])) ? '. A newer job has waited in IBM’s queue since ' + d.waiting[k].slice(11, 16) : ''), p.qubits_read, p.known_good, n(c.p10, 'ABOVE') + ' / ' + n(c.p10, 'BELOW'), n(c.p01, 'ABOVE') + ' / ' + n(c.p01, 'BELOW'), n(c.t1, 'ABOVE') + ' / ' + n(c.t1, 'BELOW') + ' (' + n(c.t1, 'CANNOT_TELL') + ')'].forEach(function (x) { r.appendChild(el('td', null, x)); });
      var td = el('td'); var a = el('a', null, p.job_id); a.href = '/qia/cal/' + p.job_id + '.json'; td.appendChild(a); r.appendChild(td); b.appendChild(r);
    });
    t.appendChild(b); box.appendChild(t);
    var f = el('div', 'pk-ctl'); var sel = el('select'); sel.setAttribute('aria-label', 'Processor'); names.forEach(function (k) { var o = el('option', null, k); o.value = k; sel.appendChild(o); });
    var qi = el('input'); qi.placeholder = 'qubits, e.g. 0, 1, 2'; qi.setAttribute('aria-label', 'Qubits'); var go = el('button', 'btn ghost', 'Show my qubits'); go.type = 'button';
    f.appendChild(sel); f.appendChild(qi); f.appendChild(go); box.appendChild(f); var res = el('div'); box.appendChild(res);
    go.onclick = function () {
      res.textContent = 'Loading.'; var want = (qi.value.match(/\d+/g) || []).map(Number);
      fetch('/qia/cal/' + P[sel.value].job_id + '.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (run) {
        var rows = run.qubits.filter(function (q) { return !want.length || want.indexOf(q.qubit) > -1; }); res.textContent = '';
        var tt = el('table', 'mtx'); tt.innerHTML = '<thead><tr><th>Qubit</th><th>P(1|0) ours [99.9%]</th><th>IBM</th><th></th><th>P(0|1) ours [99.9%]</th><th>IBM</th><th></th><th>T1 ours, µs [99.99%]</th><th>IBM, date</th><th></th></tr></thead>';
        var bb = el('tbody'); function W(o) { return { ABOVE: 'IBM above', BELOW: 'IBM below', CONSISTENT: 'consistent', CANNOT_TELL: 'cannot tell' }[o] || o; }
        rows.forEach(function (q) { var r = el('tr'); [q.qubit, q.p10 + ' [' + q.p10_ci.join(', ') + ']', q.ibm_p10, W(q.p10_outcome), q.p01 + ' [' + q.p01_ci.join(', ') + ']', q.ibm_p01, W(q.p01_outcome), q.t1 + ' [' + q.t1_ci.join(', ') + ']', (q.ibm_t1 == null ? '' : (+q.ibm_t1).toFixed(1)) + ', ' + q.ibm_t1_date, W(q.t1_outcome)].forEach(function (x) { r.appendChild(el('td', null, x)); }); bb.appendChild(r); });
        tt.appendChild(bb); res.appendChild(tt);
      }).catch(function () { res.textContent = 'That run could not be read just now.'; });
    };
    box.appendChild(el('p', 'bench-note', 'Each hour one job per processor: every usable qubit at rest and after an X, read out, and after delays of 15 to 320 µs for T1, all qubits at once. Compared with the calibration IBM had in force when our job ran. IBM’s readout figures are counts out of 4,096, so they get their own interval and a reading is off only when the two intervals do not overlap. IBM publishes no fit uncertainty for T1, so T1 is off only beyond a 25% margin past our interval. In planted tests where IBM is exactly right, these rules called nothing off. Every run is hashed into the chain below. Updated ' + (d.updated || '').replace('T', ' ').slice(0, 16) + ' UTC.'));
  }).catch(function () { box.textContent = 'The calibration could not be read just now.'; });
})();
