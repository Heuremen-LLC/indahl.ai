// QIA calibration: every qubit of every IBM processor we can reach, measured when IBM publishes new readout or T1 figures (at least every 6 hours) against the record IBM had in force when our job ran.
(function () {
  var box = document.getElementById('cal-live'); if (!box) return;
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function n(c, o) { return c && c[o] != null ? c[o] : 0; }
  // 30 Oct: all four outcomes are printed, IBM's side first (IBM above ours, IBM below ours, consistent, cannot tell). A zero is printed as a zero.
  function tally(c) { return n(c, 'ABOVE') + ' above, ' + n(c, 'BELOW') + ' below, ' + n(c, 'CONSISTENT') + ' consistent, ' + n(c, 'CANNOT_TELL') + ' cannot tell'; }
  fetch('/qia/cal.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var P = d.processors || {}, names = Object.keys(P).sort(); box.textContent = '';
    if (!names.length) { box.textContent = 'The first runs are in IBM’s queues.'; return; }
    var t = el('table', 'mtx'); t.innerHTML = '<thead><tr><th>Processor</th><th>Our job ran (UTC)</th><th>Qubits read</th><th>Seat check</th><th>Readout P(1|0), IBM against ours</th><th>Readout P(0|1), IBM against ours</th><th>T1, IBM against ours</th><th>Every qubit</th></tr></thead>';
    var b = el('tbody');
    names.forEach(function (k) {
      var p = P[k], c = p.counts || {}, r = el('tr');
      [k, (p.window_utc || [''])[0].replace('T', ' ').slice(0, 16) + ((d.waiting || {})[k] && (d.waiting[k] > ((p.window_utc || [''])[0])) ? '. A newer job has waited in IBM’s queue since ' + d.waiting[k].slice(11, 16) : ''), p.qubits_read, p.known_good, tally(c.p10), tally(c.p01), tally(c.t1)].forEach(function (x) { r.appendChild(el('td', null, x)); });
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
        var tt = el('table', 'mtx'); tt.innerHTML = '<thead><tr><th>Qubit</th><th>P(1|0) ours [99.9%]</th><th>IBM, date (US Eastern)</th><th></th><th>P(0|1) ours [99.9%]</th><th>IBM, date (US Eastern)</th><th></th><th>T1 ours, µs [99.99%]</th><th>IBM, date (US Eastern)</th><th></th></tr></thead>';
        var bb = el('tbody'); function rd(v, d) { return v == null ? '' : (+v).toFixed(4) + (d ? ', ' + d : ''); }
        function W(o) { return { ABOVE: 'IBM above', BELOW: 'IBM below', CONSISTENT: 'consistent', CANNOT_TELL: 'cannot tell' }[o] || o; }
        rows.forEach(function (q) { var r = el('tr'); [q.qubit, q.p10 + ' [' + q.p10_ci.join(', ') + ']', rd(q.ibm_p10, q.ibm_p10_date), W(q.p10_outcome), q.p01 + ' [' + q.p01_ci.join(', ') + ']', rd(q.ibm_p01, q.ibm_p01_date), W(q.p01_outcome), q.t1 + ' [' + q.t1_ci.join(', ') + ']', (q.ibm_t1 == null ? '' : (+q.ibm_t1).toFixed(1)) + ', ' + q.ibm_t1_date, W(q.t1_outcome)].forEach(function (x) { r.appendChild(el('td', null, x)); }); bb.appendChild(r); });
        tt.appendChild(bb); res.appendChild(tt);
      }).catch(function () { res.textContent = 'That run could not be read just now.'; });
    };
    box.appendChild(el('p', 'bench-note', 'One job per processor whenever IBM publishes new readout or T1 figures for it, and at least every 6 hours (hourly until 30 Oct): every usable qubit at rest and after an X, read out, and after delays of 15 to 320 µs for T1, all qubits at once. Compared with the calibration IBM had in force when our job ran. IBM’s readout figures are counts out of 4,096 or 1,024 shots, depending on the processor’s record, so they get their own interval and a reading is off only when the two intervals do not overlap. IBM publishes no fit uncertainty for T1, so T1 is off only beyond a 25% margin past our interval. The two interval rules were set after the first aachen run was read and before any US run was read. The rule for the shot count behind IBM’s readout figures was set on 30 Oct after the fez and marrakesh readings were published. In 40 planted runs where IBM is exactly right, these rules called nothing off. IBM’s dates are in US Eastern time. Every run is hashed into the chain below. Updated ' + (d.updated || '').replace('T', ' ').slice(0, 16) + ' UTC.'));
  }).catch(function () { box.textContent = 'The calibration could not be read just now.'; });
})();
