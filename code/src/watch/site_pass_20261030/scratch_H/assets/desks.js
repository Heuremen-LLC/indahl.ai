// Division pages: fills each desk's live reading from /stack/live.json, which the STACK rider writes from the other pages' public feeds.
(function () {
  var slots = document.querySelectorAll('.deskread'); if (!slots.length) return;
  var OC = { CONSISTENT: 'consistent', ABOVE: 'above', BELOW: 'below', CANNOT_TELL: 'cannot tell', NOTHING_RETURNED: 'nothing returned' };
  function pc(x) { return x == null ? '' : (100 * x).toFixed(1) + '%'; }
  fetch('/stack/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    slots.forEach(function (el) {
      var name = el.getAttribute('data-page'), rows = (d.rows || []).filter(function (r) { return r.page === name && r.share != null; }), run = (d.running || []).filter(function (r) { return r.page === name; });
      if (rows.length) { var r = rows[0]; el.textContent = r.test + ': ' + r.n + ' of ' + r.of + ' (' + pc(r.share) + '), ' + (OC[r.outcome] || r.outcome); }
      else if (run.length) el.textContent = run[0].what + ': ' + run[0].reading;
    });
  }).catch(function () {});
})();
