// TIME: public time servers, stated against delivered. Reads /time/live.json, written on every round by the tick bus.
(function () {
  var box = document.getElementById('time-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', BELOW: 'below', CANNOT_TELL: 'cannot tell', NOTHING_RETURNED: 'nothing returned', REFUSED: 'refused' }[o] || o; }
  fetch('/time/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ss = d.servers || []; if (!ss.length) { box.textContent = 'Waiting for the first round.'; return; }
    var ref = d.reference || {}, t = d.totals || {};
    var top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = 'Reference: the Pi, stratum ' + ref.stratum + ', disciplined by ' + String(ref.source || '').replace(/^\S+\s*/, '').replace(/[()]/g, '') + ' GPS pulse. ' + (ref.system_time || '') + ', RMS offset ' + (ref.rms || '') + '. Our seat reads every server about ' + d.seat_part_ms + ' ms ahead, common to all of them, so that part belongs to our access link and not to any server. Updated ' + d.updated + ' UTC, ' + d.rounds + ' rounds scored.';
    var s = document.createElement('p'); s.textContent = Object.keys(t).map(function (k) { return t[k] + ' ' + W(k); }).join(', ') + '.';
    var tb = document.createElement('table'); tb.className = 'mtx';
    tb.innerHTML = '<thead><tr><th>Server</th><th>Stratum</th><th>Reports</th><th>Offset, ms</th><th>Path half-delay, ms</th><th>Server’s own stated bound, ms</th><th>Outcome</th><th>Reads</th></tr></thead>';
    var b = document.createElement('tbody');
    ss.forEach(function (x) {
      var r = document.createElement('tr'), c = x.counts || {}, n = (c.COMMITTED || 0), all = Object.keys(c).reduce(function (a, k) { return a + c[k]; }, 0);
      r.appendChild(td(x.server)); r.appendChild(td(x.stratum == null ? '' : x.stratum, 1)); r.appendChild(td(x.refid == null ? '' : x.refid));
      r.appendChild(td(x.offset_ms == null ? '' : x.offset_ms, 1)); r.appendChild(td(x.half_delay_ms == null ? '' : x.half_delay_ms, 1)); r.appendChild(td(x.stated_bound_ms == null ? '' : x.stated_bound_ms, 1));
      r.appendChild(td(W(x.outcome))); r.appendChild(td(n + ' of ' + all, 1)); b.appendChild(r);
    });
    tb.appendChild(b); box.textContent = ''; box.appendChild(top); box.appendChild(s); box.appendChild(tb);
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
