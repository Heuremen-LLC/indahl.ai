// FORECAST: stated chance of precipitation against what happened. Reads /forecast/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('forecast-live'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', BELOW: 'below', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  fetch('/forecast/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.cells) { box.textContent = 'Waiting for the first forecasts.'; return; }
    var f = d.floor || {}, top = document.createElement('p'); top.className = 'bench-note';
    function fmt(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
    top.textContent = d.period_rows == null
      ? d.stations + ' stations, ' + d.forecasts_stored + ' forecasts stored, ' + d.periods_stored + ' periods, ' + d.periods_scored + ' scored, ' + d.unscorable + ' unscorable for missing observations, ' + d.not_stated + ' with no stated chance. Chance floor: of ' + f.periods + ' periods with a stated chance of 0 or 5, ' + f.with_event + ' had an event. Updated ' + d.updated + ' UTC.'
      : fmt(d.stations) + ' stations, ' + fmt(d.forecasts_stored) + ' forecasts stored. They hold ' + fmt(d.period_rows) + ' period rows for ' + fmt(d.periods_stored) + ' distinct periods, and ' + fmt(d.negative_lead_rows) + ' rows were stored after their period had begun and are not read. Of the periods read, with a stated chance and a lead from 0 to 48 hours, ' + fmt(d.periods_scored) + ' were scored, ' + fmt(d.unscorable) + ' could not be for missing observations, and ' + fmt(d.periods_in_no_cell) + ' have a stated chance in a gap between the bins and are in no cell. ' + fmt(d.not_stated) + ' periods had no stated chance. A period counts once in each cell, and the table holds ' + fmt(d.cell_periods) + ' period counts. Chance floor: of ' + fmt(f.periods) + ' distinct periods with a stated chance of 0 or 5, ' + fmt(f.with_event) + ' had an event. Updated ' + d.updated + ' UTC.';
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Stated chance, percent</th><th>Lead</th><th>Mean stated</th><th>Happened, 95% interval</th><th>Periods</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    d.cells.forEach(function (c) {
      var r = document.createElement('tr'); r.appendChild(td(c.bin)); r.appendChild(td(c.lead));
      if (!c.n) { r.appendChild(td('')); r.appendChild(td('')); r.appendChild(td(0, 1)); r.appendChild(td('cannot tell')); }
      else { r.appendChild(td(c.mean_stated + '%', 1)); r.appendChild(td(c.observed + '% [' + c.lo + ', ' + c.hi + ']', 1)); r.appendChild(td(c.n, 1)); r.appendChild(td(W(c.outcome))); }
      b.appendChild(r);
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(top); box.appendChild(t);
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
