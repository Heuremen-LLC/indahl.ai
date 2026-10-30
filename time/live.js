// TIME: public time servers, stated against delivered. Reads /time/live.json, written on every round by the tick bus.
(function () {
  var box = document.getElementById('time-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', BELOW: 'below', CANNOT_TELL: 'cannot tell', NOTHING_RETURNED: 'nothing returned', REFUSED: 'refused' }[o] || o; }
  fetch('/time/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ss = d.servers || []; if (!ss.length) { box.textContent = 'Waiting for the first round.'; return; }
    var ref = d.reference || {}, t = d.totals || {}, s2 = d.seat2 || {};
    var NOTE = { 'nts.netnod.se': ' (NTS host)' };
    var top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = 'Reference: our GPS-disciplined clock, stratum ' + ref.stratum + ', disciplined by ' + String(ref.source || '').replace(/^\S+\s*/, '').replace(/[()]/g, '') + ' GPS pulse. ' + (ref.system_time || '') + ', RMS offset ' + (ref.rms || '') + '. Our reference seat reads every server about ' + d.seat_part_ms + ' ms ahead. That part is common to all of them and is different at the second seat, so we read it as the seat\'s own and not any server\'s. Updated ' + d.updated + ' UTC, ' + d.rounds + ' rounds scored at the reference seat.';
    if (s2.name) top.textContent += ' A second seat on another network, the ' + s2.name + ', reads the same servers about ' + s2.seat_part_ms + ' ms ahead. Its columns hold the latest round only, which is 8 queries per server.';
    var s = document.createElement('p'); s.textContent = 'At the reference seat: ' + Object.keys(t).map(function (k) { return t[k] + ' ' + W(k); }).join(', ') + '.';
    var cap = document.createElement('p'); cap.className = 'bench-note'; cap.textContent = 'Columns without the word runner are read at our reference seat over all rounds held. Replies kept is the count of queries answered out of the queries sent. A server whose name does not resolve or whose host does not answer ordinary NTP queries reads nothing returned. Names under pool.ntp.org answer from different pool members at each seat, so the two seats do not read the same machine for those rows.';
    var tb = document.createElement('table'); tb.className = 'mtx';
    tb.innerHTML = '<thead><tr><th>Server</th><th>Stratum</th><th>Reference id</th><th>Offset, ms</th><th>Path half-delay, ms</th><th>Server\u2019s own stated bound, ms</th><th>Outcome</th><th>Runner offset, ms</th><th>Runner path half-delay, ms</th><th>Runner stated bound, ms</th><th>Runner outcome</th><th>Replies kept</th></tr></thead>';
    var b = document.createElement('tbody');
    ss.forEach(function (x) {
      var r = document.createElement('tr'), c = x.counts || {}, n = (c.COMMITTED || 0), all = Object.keys(c).reduce(function (a, k) { return a + c[k]; }, 0);
      function v(y) { return y == null ? '' : y; }
      r.appendChild(td(x.server + (NOTE[x.server] || ''))); r.appendChild(td(v(x.stratum), 1)); r.appendChild(td(v(x.refid)));
      r.appendChild(td(v(x.offset_ms), 1)); r.appendChild(td(v(x.half_delay_ms), 1)); r.appendChild(td(v(x.stated_bound_ms), 1)); r.appendChild(td(W(x.outcome)));
      r.appendChild(td(v(x.offset_ms_2), 1)); r.appendChild(td(v(x.half_delay_ms_2), 1)); r.appendChild(td(v(x.stated_bound_ms_2), 1)); r.appendChild(td(x.outcome_2 ? W(x.outcome_2) : '')); r.appendChild(td(n + ' of ' + all, 1)); b.appendChild(r);
    });
    tb.appendChild(b); box.textContent = ''; box.appendChild(top); box.appendChild(s); box.appendChild(cap); box.appendChild(tb);
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
