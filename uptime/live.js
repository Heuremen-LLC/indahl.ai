// UPTIME: vendor status pages against independent probes. Reads /uptime/live.json, written on every round by the tick bus.
// 30 Oct 2026 (site pass A-2, A-3, A-4, A-14): two seats (home and cloud, the two home machines count as one), every count defined,
// the floor printed as the upper end of the 95% interval and not as 0.00%, and no machine names on the page (the feed keeps them).
(function () {
  var box = document.getElementById('uptime-live'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', BELOW: 'below', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  // The feed names the machines. The page shows the two seats: home (two machines on one home network) and cloud.
  function seatsText(reach) {
    var g = {};
    Object.keys(reach || {}).forEach(function (k) {
      var s = (k === 'mac' || k === 'pi') ? 'home' : 'cloud';
      g[s] = g[s] === undefined ? reach[k] : Math.min(g[s], reach[k]);
    });
    return Object.keys(g).sort().map(function (s) { return s + ' ' + g[s] + '%'; }).join(', ');
  }
  fetch('/uptime/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var vs = d.vendors || []; if (!vs.length) { box.textContent = 'Waiting for the first round.'; return; }
    var c = d.control || {}, top = document.createElement('p'); top.className = 'bench-note';
    var targets = (c.targets || []).map(function (x) { return String(x).replace(/^control:\s*/, ''); }).join(' and ');
    var ub = typeof d.floor_upper_bound === 'number' ? (100 * d.floor_upper_bound).toFixed(1) + '%' : null;
    top.textContent = 'Seats: home and cloud. ' + d.buckets + ' ten-minute rounds so far. A vendor\'s Rounds are the ones where both seats made a request and its status page was read. Control targets with no status page, ' + targets + ', are counted per target, so each round counts once for each. Both seats failed on them in ' + c.misses + ' of ' + c.rounds + ' control rounds' + (ub ? ', so the instrument floor is at most ' + ub + ' (upper end of the 95% interval)' : '') + '. Updated ' + d.updated + ' UTC.';
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Vendor</th><th>Its page says now</th><th>Rounds</th><th>Page said operational, both seats failed</th><th>Page said trouble, both seats failed</th><th>One seat failed</th><th>Reachable, by seat (home shows the lower of its two machines)</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    vs.forEach(function (v) {
      var r = document.createElement('tr');
      r.appendChild(td(v.vendor)); r.appendChild(td(v.indicator_now === 'none' ? 'operational' : (v.indicator_now || ''))); r.appendChild(td(v.rounds, 1)); r.appendChild(td(v.disagree, 1)); r.appendChild(td(v.confirm, 1)); r.appendChild(td(v.blips, 1)); r.appendChild(td(seatsText(v.reach))); r.appendChild(td(W(v.outcome))); b.appendChild(r);
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(top); box.appendChild(t);
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
