// LAUNCH: stated launch time against the time launches flew. Reads /launch/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('launch-live'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  fetch('/launch/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.updated) { box.textContent = 'Waiting for the first snapshot.'; return; }
    var s = d.scored || {}, top = document.createElement('p'); top.className = 'bench-note';
    function fmt(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
    top.textContent = fmt(d.launches_tracked) + ' launches tracked since ' + d.first_read + ', ' + fmt(d.snapshots) + ' snapshots stored, ' + fmt(d.waiting) + ' waiting to fly. ' + (d.flown_watched == null ? '' : fmt(d.flown_watched) + ' have flown since we began reading them. ' + fmt(d.flown_before_first_read) + ' were already flown at our first read, were never watched before they flew, and cannot be scored. ') + 'Scored launches: ' + s['1 day'] + ' at 1 day, ' + s['7 days'] + ' at 7 days, ' + s['30 days'] + ' at 30 days. ' + d.coarse_precision + ' readings set aside for coarse time precision. Updated ' + d.updated + ' UTC.';
    box.textContent = ''; box.appendChild(top);
    if (!d.cells || !d.cells.length) { var p = document.createElement('p'); p.textContent = 'No launch we were watching has flown yet with a stored time far enough ahead. Rows appear here as they do.'; box.appendChild(p); return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Provider</th><th>Lead</th><th>Launches</th><th>Median slip, hours</th><th>Slipped over 24 hours, 95% interval</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    d.cells.forEach(function (c) {
      var r = document.createElement('tr'); r.appendChild(td(c.who)); r.appendChild(td(c.lead)); r.appendChild(td(c.n, 1)); r.appendChild(td(c.median_abs_slip_h, 1));
      r.appendChild(td(c.over_24h + ' of ' + c.n + ', ' + (100 * c.share).toFixed(1) + '% [' + (100 * c.lo).toFixed(1) + ', ' + (100 * c.hi).toFixed(1) + ']', 1)); r.appendChild(td(W(c.outcome))); b.appendChild(r);
    });
    t.appendChild(b); box.appendChild(t);
  }).catch(function () { box.textContent = 'The snapshot could not be loaded just now.'; });
})();
