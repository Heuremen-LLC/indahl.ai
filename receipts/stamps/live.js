// STAMPS: reads /receipts/stamps/index.json, written by ledger/stamps.py after each release. Newest release first.
(function () {
  var box = document.getElementById('stamps-live'); if (!box) return;
  var GH = 'https://github.com/Heuremen-LLC/indahl.ai/commit/';
  function el(t, txt, cls) { var e = document.createElement(t); if (txt != null) e.textContent = txt; if (cls) e.className = cls; return e; }
  function link(href, txt) { var a = el('a', txt); a.href = href; return a; }
  function short(h) { return h ? h.slice(0, 12) + '…' + h.slice(-6) : ''; }
  function when(t) { return t ? t.replace('T', ' ').replace('Z', ' UTC') : ''; }
  function wts(ts) { return ts && ts.length === 14 ? ts.slice(0, 4) + '-' + ts.slice(4, 6) + '-' + ts.slice(6, 8) + ' ' + ts.slice(8, 10) + ':' + ts.slice(10, 12) + ' UTC' : ''; }
  function otsText(s) {
    if (!s || s === 'pending') return 'Sent to the calendars, waiting for a Bitcoin block';
    if (s.indexOf('bitcoin ') === 0) return 'In Bitcoin block ' + s.slice(8);
    if (s === 'failed') return 'Stamp failed at release time';
    return s;
  }
  function render(d) {
    box.textContent = '';
    var rs = d.releases || [];
    if (!rs.length) { box.appendChild(el('p', 'No release has been stamped yet.', 'bench-note')); return; }
    var t = el('table', null, 'mtx'), th = el('thead'), tr = el('tr');
    ['Released', 'Commit', 'Manifest hash', 'Release record', 'OpenTimestamps', 'Internet Archive'].forEach(function (h) { tr.appendChild(el('th', h)); });
    th.appendChild(tr); t.appendChild(th); var tb = el('tbody');
    rs.slice(0, 40).forEach(function (r) {
      var row = el('tr');
      row.appendChild(el('td', when(r.released_at)));
      var c = el('td'); c.appendChild(link(GH + r.commit, r.commit.slice(0, 12))); row.appendChild(c);
      var m = el('td', short(r.manifest_sha256), 'hashline'); m.title = r.manifest_sha256; row.appendChild(m);
      var j = el('td'); j.appendChild(link(r.json, 'JSON')); var s = el('span', ' sha256 ' + short(r.sha256), 'hashline'); s.title = r.sha256; j.appendChild(s); row.appendChild(j);
      var o = el('td'); if (r.ots) { o.appendChild(link(r.ots, '.ots')); o.appendChild(document.createTextNode(' ' + otsText(r.ots_status))); } else o.textContent = otsText(r.ots_status); row.appendChild(o);
      var w = el('td'), caps = r.wayback || [];
      if (caps.length) {
        var det = el('details'), sum = el('summary', caps.length === 1 ? 'One capture' : caps.length + ' captures'); det.appendChild(sum);
        var ul = el('ul'); caps.forEach(function (x) { var li = el('li'); li.appendChild(link(x.capture, x.url.replace('https://indahl.ai', '') || '/')); li.appendChild(document.createTextNode(' ' + wts(x.timestamp))); ul.appendChild(li); });
        det.appendChild(ul); w.appendChild(det);
      } else w.textContent = r.wayback_waiting ? 'Waiting in the queue' : 'None';
      if (caps.length && r.wayback_waiting) w.appendChild(el('div', 'More waiting in the queue', 'bench-note'));
      row.appendChild(w); tb.appendChild(row);
    });
    t.appendChild(tb); var wrap = el('div', null, 'scroll'); wrap.appendChild(t); box.appendChild(wrap);
    box.appendChild(el('p', 'Read at ' + when(d.built_utc) + '.', 'bench-note'));
  }
  fetch('/receipts/stamps/index.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(render).catch(function () { box.textContent = 'The stamp list could not be read just now.'; });
})();
