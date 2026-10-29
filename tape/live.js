// TAPE: reads /tape/live.json, written by the tick bus. Shows the chain newest first, the beacon and the anchor.
(function () {
  var box = document.getElementById('tape-live'); if (!box) return;
  var GH = 'https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/tape/';
  var KIND = { pages: 'pages', feeds: 'feeds', beacon: 'beacon' };
  function el(t, txt, cls) { var e = document.createElement(t); if (txt != null) e.textContent = txt; if (cls) e.className = cls; return e; }
  function link(href, txt) { var a = el('a', txt); a.href = href; return a; }
  function short(h) { return h ? h.slice(0, 10) + '…' + h.slice(-6) : ''; }
  function when(t) { return t ? t.replace('T', ' ').replace('Z', ' UTC') : ''; }
  function render(d) {
    box.textContent = '';
    var top = el('div', null, 'tape-top');
    var b = el('div', null, 'tape-card'); b.appendChild(el('h3', 'Beacon'));
    b.appendChild(el('p', d.beacon.value, 'hashline'));
    var p = el('p', null, 'bench-note'); p.appendChild(document.createTextNode('Built at ' + when(d.beacon.t) + ' from drand round ')); p.appendChild(link('https://api.drand.sh/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971/public/' + d.beacon.drand_round, d.beacon.drand_round)); p.appendChild(document.createTextNode(', the feeds of that run and the line before it. Inputs: ')); p.appendChild(link(GH + 'leaves/' + d.beacon.n + '.json', 'entry ' + d.beacon.n)); p.appendChild(document.createTextNode('.')); b.appendChild(p);
    var h = el('div', null, 'tape-card'); h.appendChild(el('h3', 'Head of the chain'));
    h.appendChild(el('p', d.head.entry, 'hashline')); h.appendChild(el('p', 'Entry ' + d.head.n + ', ' + when(d.head.t) + '. ' + d.count + ' entries in all.', 'bench-note'));
    var a = el('div', null, 'tape-card'); a.appendChild(el('h3', 'Anchor'));
    var an = d.anchor || {};
    a.appendChild(el('p', an.archive_id ? ('Stamped through entry ' + an.covers_n + (an.attested ? ', attested in Bitcoin.' : ', waiting for its Bitcoin attestation.')) : 'No stamp covers the tape yet.', 'bench-note'));
    if (an.archive_id) a.appendChild(el('p', 'Entries ' + (an.covers_n + 1) + ' to ' + d.head.n + ' are chained and not yet stamped.', 'bench-note'));
    top.appendChild(b); top.appendChild(h); top.appendChild(a); box.appendChild(top);
    box.appendChild(el('h3', 'The tape, newest first'));
    var t = el('table', null, 'mtx tape'), th = el('thead'), tr = el('tr'); ['Entry', 'Time', 'Kind', 'What', 'Hash'].forEach(function (x) { tr.appendChild(el('th', x)); }); th.appendChild(tr); t.appendChild(th);
    var tb = el('tbody'); (d.entries || []).forEach(function (e) { var r = el('tr'); var c0 = el('td', null, 'n'); c0.appendChild(link(GH + 'leaves/' + e.n + '.json', String(e.n))); r.appendChild(c0); r.appendChild(el('td', when(e.t))); r.appendChild(el('td', KIND[e.kind] || e.kind)); r.appendChild(el('td', e.subject)); r.appendChild(el('td', short(e.entry), 'hashline')); tb.appendChild(r); });
    t.appendChild(tb); box.appendChild(t);
  }
  function load() { fetch('/tape/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) { if (!d || !d.head) { box.textContent = 'Waiting for the first entry.'; return; } render(d); }).catch(function () { box.textContent = 'The read could not be loaded just now.'; }); }
  load(); setInterval(load, 90000);
})();
