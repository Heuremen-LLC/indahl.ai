// Live model-claim rounds: each round checks one open-weight model's own stated results by rerunning them. Reads /sad/live.json.
(function () {
  var box = document.getElementById('sad-live'); if (!box) return;
  function td(t, b) { var c = document.createElement('td'); if (b) { var s = document.createElement('strong'); s.textContent = t; c.appendChild(s); } else c.textContent = t; return c; }
  function draw(d) {
    var rs = (d && d.rounds) || []; if (!rs.length) { box.textContent = 'No round has started.'; return; }
    box.textContent = '';
    rs.forEach(function (r) {
      var h = document.createElement('h3'); h.textContent = 'Round ' + r.id + ': ' + r.model; box.appendChild(h);
      var p = document.createElement('p'); p.className = 'meta';
      p.textContent = r.status + (r.updated ? ' (updated ' + r.updated + ' UTC)' : ''); box.appendChild(p);
      if (r.known_good) { var k = document.createElement('p'); k.className = 'meta'; k.textContent = 'Known-good check: ' + r.known_good; box.appendChild(k); }
      var w = document.createElement('div'); w.className = 'scroll'; var t = document.createElement('table'); t.className = 'mtx';
      var th = document.createElement('thead'), tr = document.createElement('tr');
      ['Claim', 'Stated', 'Delivered', 'Outcome', 'State'].forEach(function (x) { var c = document.createElement('th'); c.textContent = x; tr.appendChild(c); });
      th.appendChild(tr); t.appendChild(th); var tb = document.createElement('tbody');
      (r.claims || []).forEach(function (c) {
        var row = document.createElement('tr'); row.appendChild(td(c.name)); row.appendChild(td(c.stated)); row.appendChild(td(c.ours || '')); row.appendChild(td(c.outcome || '', true)); row.appendChild(td(c.state)); tb.appendChild(row);
      });
      t.appendChild(tb); w.appendChild(t); box.appendChild(w);
      var q = document.createElement('p'); q.className = 'meta'; var a = document.createElement('a'); a.href = '/respond?u=sad-live-' + String(r.id).toLowerCase(); a.textContent = 'Respond'; q.appendChild(a); box.appendChild(q);
    });
  }
  function load() { fetch('/sad/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(draw).catch(function () {}); }
  load(); setInterval(load, 30000);
})();
