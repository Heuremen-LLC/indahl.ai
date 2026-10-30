// LINKROT: code and data links stated in arXiv papers against whether they resolve. Reads /linkrot/live.json, written by the tick bus.
(function () {
  var box = document.getElementById('linkrot-live'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t; return c; }
  function pct(x) { return x == null ? '' : (100 * x).toFixed(1) + '%'; }
  function fmt(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function table(title, obj, first) {
    var h = document.createElement('h3'); h.textContent = title; var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>' + first + '</th><th>Links</th><th>Live</th><th>Page gone</th><th>Host gone</th><th>Blocked</th><th>Timed out</th><th>Rot share, 95% interval</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    Object.keys(obj).forEach(function (k) { var g = obj[k], r = document.createElement('tr'); r.appendChild(td(k));
      [g.links, g.live, g.gone, g.dns_fail, g.blocked, g.timeout].forEach(function (v) { r.appendChild(td(v, 1)); });
      r.appendChild(td(g.rot_share == null ? '' : pct(g.rot_share) + ' [' + pct(g.lo) + ', ' + pct(g.hi) + ']', 1)); r.appendChild(td(W(g.outcome))); b.appendChild(r); });
    t.appendChild(b); var f = document.createDocumentFragment(); f.appendChild(h); f.appendChild(t); return f;
  }
  fetch('/linkrot/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.all) { box.textContent = 'Waiting for the first pass.'; return; }
    var top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = fmt(d.papers) + ' papers read' + (d.papers_with_a_link == null ? '' : ', ' + fmt(d.papers_with_a_link) + ' of them with a code or data link') + '. ' + fmt(d.links) + ' distinct links, ' + fmt(d.read) + ' read so far, ' + fmt(d.due) + ' due. Controls: ' + (d.gate === 'passed' ? 'all ten read right' : 'FAILED, every row reads cannot tell') + '. Gone since the last read: ' + d.newly_gone + '. Back after being gone: ' + d.returned + '. Moved to a different repository name: ' + d.moved + '. Links read by both network seats: ' + (d.seat2_links || 0) + ', seat disagreements counted as blocked: ' + (d.seat_disagreements || 0) + '. Updated ' + d.updated + ' UTC.';
    box.textContent = ''; box.appendChild(top); box.appendChild(table('By year of the paper', d.by_year, 'Year')); box.appendChild(table('By host', d.by_host, 'Host'));
    if (d.repos && d.repos.all) {
      var rh = document.createElement('h3'); rh.textContent = 'Is there code behind a live GitHub link?'; box.appendChild(rh);
      var rn = document.createElement('p'); rn.className = 'bench-note'; rn.textContent = 'Controls for this check: ' + (d.repos.gate === 'passed' ? 'both read right' : 'FAILED, every row reads cannot tell') + '. Empty means the repository has no commits. A stub has three or fewer. Archived and not pushed in a year are shown for context and are not counted as misses. No license detected means GitHub finds no license file, so the code is available to read but not licensed for reuse.'; box.appendChild(rn);
      var rt = document.createElement('table'); rt.className = 'mtx';
      rt.innerHTML = '<thead><tr><th></th><th>Repositories read</th><th>Empty</th><th>Stub</th><th>Code</th><th>Archived</th><th>Not pushed in a year</th><th>No license detected</th><th>No license share, 95% interval (defined after the first pass)</th><th>Empty share, 95% interval</th><th>Outcome</th></tr></thead>';
      var rb = document.createElement('tbody');
      function rrow(name, g) { var tr = document.createElement('tr'); tr.appendChild(td(name)); [g.repos, g.empty, g.stub, g.code, g.archived, g.stale, g.no_license].forEach(function (v) { tr.appendChild(td(v, 1)); }); tr.appendChild(td(g.no_license_share == null ? '' : pct(g.no_license_share) + ' [' + pct(g.no_license_share_lo) + ', ' + pct(g.no_license_share_hi) + ']', 1)); tr.appendChild(td(g.empty_share == null ? '' : pct(g.empty_share) + ' [' + pct(g.lo) + ', ' + pct(g.hi) + ']', 1)); tr.appendChild(td(W(g.outcome))); rb.appendChild(tr); }
      rrow('All', d.repos.all); Object.keys(d.repos.by_year || {}).forEach(function (y) { rrow(y, d.repos.by_year[y]); });
      rt.appendChild(rb); box.appendChild(rt);
    }
  }).catch(function () { box.textContent = 'The pass could not be read just now.'; });
})();
