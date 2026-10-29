// STACK: reads /stack/live.json, written by the tick bus from the other pages' public feeds. Adds no reading of its own.
(function () {
  var box = document.getElementById('stack-live'); if (!box) return;
  var OC = { CONSISTENT: 'consistent', ABOVE: 'above', BELOW: 'below', CANNOT_TELL: 'cannot tell', NOTHING_RETURNED: 'nothing returned' };
  var COL = { ABOVE: '#c2410c', BELOW: '#1d4ed8', CONSISTENT: '#4d7c0f', CANNOT_TELL: '#6b7280' };
  var NS = 'http://www.w3.org/2000/svg';
  function el(t, txt, cls) { var e = document.createElement(t); if (txt != null) e.textContent = txt; if (cls) e.className = cls; return e; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t == null ? '' : t; return c; }
  function pc(x) { return x == null ? '' : (100 * x).toFixed(1) + '%'; }
  function table(head, rows, nums) {
    var t = el('table', null, 'mtx'), th = el('thead'), tr = el('tr'); head.forEach(function (h) { tr.appendChild(el('th', h)); }); th.appendChild(tr); t.appendChild(th);
    var b = el('tbody'); rows.forEach(function (r) { var x = el('tr'); r.forEach(function (c, i) { if (c && c.nodeType) { var d = el('td'); d.appendChild(c); x.appendChild(d); } else x.appendChild(td(c, nums && nums.indexOf(i) >= 0)); }); b.appendChild(x); }); t.appendChild(b); return t;
  }
  function link(href, txt) { var a = el('a', txt); a.href = href; return a; }
  function svg(n, attrs) { var e = document.createElementNS(NS, n); Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); }); return e; }
  function forest(rows, title, fixedMax) {
    var rs = rows.filter(function (r) { return r.share != null; }); if (!rs.length) return el('p');
    var max = fixedMax || Math.max.apply(null, rs.map(function (r) { return r.share_hi || r.share; })); max = fixedMax || Math.max(0.05, Math.ceil(max * 20) / 20);
    var W = 760, L = 330, R = 20, T = 26, H = T + rs.length * 24 + 30, s = svg('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': title, width: '100%' });
    function x(v) { return L + (W - L - R) * v / max; }
    for (var g = 0; g <= max + 1e-9; g += max <= 0.15 ? 0.05 : 0.1) {
      s.appendChild(svg('line', { x1: x(g), x2: x(g), y1: T - 6, y2: H - 24, stroke: '#888', 'stroke-opacity': '0.3' }));
      var tl = svg('text', { x: x(g), y: H - 8, 'text-anchor': 'middle', 'font-size': 11, fill: 'currentColor' }); tl.textContent = Math.round(g * 100) + '%'; s.appendChild(tl);
    }
    rs.forEach(function (r, i) {
      var y = T + i * 24 + 8, c = COL[r.outcome] || '#6b7280', lab = svg('text', { x: L - 8, y: y + 4, 'text-anchor': 'end', 'font-size': 12, fill: 'currentColor' });
      lab.textContent = (r.page + ': ' + r.test).slice(0, 52); s.appendChild(lab);
      s.appendChild(svg('line', { x1: x(r.share_lo != null ? r.share_lo : r.share), x2: x(r.share_hi != null ? r.share_hi : r.share), y1: y, y2: y, stroke: c, 'stroke-width': 3 }));
      var dot = svg('circle', { cx: x(r.share), cy: y, r: 5, fill: c }); var tt = svg('title'); tt.textContent = r.page + ': ' + r.test + ' | ' + r.n + ' of ' + r.of + ' | ' + pc(r.share) + ' [' + pc(r.share_lo) + ', ' + pc(r.share_hi) + '] | ' + (OC[r.outcome] || r.outcome); dot.appendChild(tt); s.appendChild(dot);
    });
    return s;
  }
  fetch('/stack/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    box.textContent = ''; box.appendChild(el('p', d.tests + ' tests listed. Updated ' + d.updated + ' UTC.', 'bench-note'));
    // 1 divisions
    box.appendChild(el('h3', 'Every division'));
    box.appendChild(table(['Division', 'What it holds', 'Reading now'], (d.divisions || []).map(function (v) { return [link(v.link, v.name), v.holds, v.reading]; })));
    // 2 forest of all tests
    var tests = d.rows || [], plotted = tests.filter(function (r) { return r.share != null; });
    box.appendChild(el('h3', 'Every test on one axis'));
    box.appendChild(el('p', 'Each line is the share of items that failed its own test, with its 95% interval. Colour is the outcome that page gave: orange above, blue below, green consistent, grey cannot tell. Two lines are not measures of the same thing. They share an axis so they can be read together.', 'bench-note'));
    var AXMAX = Math.max.apply(null, plotted.map(function (r) { return r.share_hi || r.share; })); AXMAX = Math.max(0.05, Math.ceil(AXMAX * 20) / 20);
    box.appendChild(forest(plotted, 'Every test on one axis', AXMAX));
    // 3 random stack
    box.appendChild(el('h3', 'Stack three at random'));
    var out = el('div'), btn = el('button', 'Stack three'); btn.type = 'button'; btn.className = 'btn';
    function pick() {
      var pool = plotted.slice(), three = []; while (three.length < 3 && pool.length) three.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
      out.textContent = ''; out.appendChild(forest(three, 'Three tests picked at random', AXMAX)); out.appendChild(el('p', three.map(function (r) { return r.page + ': ' + r.test + ', ' + r.n + ' of ' + r.of + ' (' + pc(r.share) + ')'; }).join('. ') + '.', 'bench-note'));
    }
    btn.addEventListener('click', pick); box.appendChild(btn); box.appendChild(out); pick();
    // 4 themed stacks
    box.appendChild(el('h3', 'Stacked by the question they ask'));
    Object.keys(d.stacks || {}).sort().forEach(function (g) {
      box.appendChild(el('h4', g)); box.appendChild(table(['Page', 'Test', 'Compared', 'Failed', 'Share, 95% interval', 'Outcome'], d.stacks[g].map(function (r) { return [r.page, r.test, r.of, r.n, pc(r.share) + ' [' + pc(r.share_lo) + ', ' + pc(r.share_hi) + ']', OC[r.outcome] || r.outcome]; }), [2, 3, 4]));
    });
    // 5 all tests table
    box.appendChild(el('h3', 'All tests, by outcome'));
    box.appendChild(table(['Page', 'Test', 'Compared', 'Failed', 'Share, 95% interval', 'Outcome'], tests.map(function (r) { return [r.page, r.test, r.of, r.n, r.share == null ? '' : pc(r.share) + ' [' + pc(r.share_lo) + ', ' + pc(r.share_hi) + ']', OC[r.outcome] || r.outcome]; }), [2, 3, 4]));
    // 6 running + items
    box.appendChild(el('h3', 'Running measurements'));
    box.appendChild(table(['Page', 'What is measured', 'Reading', 'State'], (d.running || []).map(function (r) { return [r.page, r.what, r.reading, OC[r.state] || r.state]; })));
    box.appendChild(el('h3', 'Pages that report many separate items, by the outcome of each item'));
    box.appendChild(table(['Page', 'Above', 'Below', 'Consistent', 'Cannot tell'], Object.keys(d.items || {}).map(function (k) { var v = d.items[k]; return [k, v.ABOVE, v.BELOW, v.CONSISTENT, v.CANNOT_TELL]; }), [1, 2, 3, 4]));
    var p = el('p', 'Pages of static tables: ', 'bench-note'); [['/iris', 'IRIS'], ['/sad', 'SAD'], ['/atlas', 'ATLAS'], ['/oy', 'OY']].forEach(function (x, i) { if (i) p.appendChild(document.createTextNode(', ')); p.appendChild(link(x[0], x[1])); }); p.appendChild(document.createTextNode('.')); box.appendChild(p);
  }).catch(function () { box.textContent = 'The read could not be loaded just now.'; });
})();
