// UPTIME: vendor status pages against independent probes. Reads /uptime/live.json, written on every round by the tick bus.
(function () {
  var box = document.getElementById('uptime-live'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', BELOW: 'below', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  fetch('/uptime/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var vs = d.vendors || []; if (!vs.length) { box.textContent = 'Waiting for the first round.'; return; }
    var c = d.control || {}, top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = 'Seats: ' + (d.seats || []).join(', ') + '. ' + d.buckets + ' ten-minute rounds so far. Control targets with no status page, ' + (c.targets || []).join(' and ') + ', failed on two or more seats in ' + c.misses + ' of ' + c.rounds + ' rounds, so the instrument floor is ' + (100 * (c.floor || 0)).toFixed(2) + '%. Updated ' + d.updated + ' UTC.';
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Vendor</th><th>Its page says now</th><th>Rounds</th><th>Page said operational, two seats failed</th><th>Page said trouble, two seats failed</th><th>One seat failed</th><th>Reachable, by seat</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    vs.forEach(function (v) {
      var r = document.createElement('tr'), seats = Object.keys(v.reach || {}).sort().map(function (k) { return k + ' ' + v.reach[k] + '%'; }).join(', ');
      r.appendChild(td(v.vendor)); r.appendChild(td(v.indicator_now === 'none' ? 'operational' : (v.indicator_now || ''))); r.appendChild(td(v.rounds, 1)); r.appendChild(td(v.disagree, 1)); r.appendChild(td(v.confirm, 1)); r.appendChild(td(v.blips, 1)); r.appendChild(td(seats)); r.appendChild(td(W(v.outcome))); b.appendChild(r);
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(top); box.appendChild(t);
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
