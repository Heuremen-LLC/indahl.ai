// Live progress of the Faults and Guards run on open models. Counts of replies received only. Reads /iris/bench.json.
(function () {
  var box = document.getElementById('bench-live'), box2 = document.getElementById('bench-live2'); if (!box) return;
  var NS = 'http://www.w3.org/2000/svg', ARMS = [['bare', 'Bare'], ['bare_copy', 'Repeat'], ['guard', 'Guard']];
  function el(n, a, t) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); if (t != null) e.textContent = t; return e; }
  function draw(d, box) {
    var ms = d.models || []; if (!ms.length) { box.textContent = 'Waiting for the first reply.'; return; }
    var W = 760, L = 150, bw = 170, gap = 12, rowh = 30, H = 44 + ms.length * rowh;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Replies received per model and arm', 'class': 'bench-svg' });
    ARMS.forEach(function (a, i) { svg.appendChild(el('text', { x: L + i * (bw + gap), y: 16, 'class': 'bench-h' }, a[1])); });
    ms.forEach(function (m, r) {
      var y = 28 + r * rowh;
      svg.appendChild(el('text', { x: 0, y: y + 14, 'class': 'bench-m' }, m.name));
      ARMS.forEach(function (a, i) {
        var x = L + i * (bw + gap), f = Math.min(1, (m[a[0]] || 0) / (d.of || 1));
        svg.appendChild(el('rect', { x: x, y: y, width: bw, height: 18, rx: 3, 'class': 'bench-bg' }));
        if (f > 0) svg.appendChild(el('rect', { x: x, y: y, width: Math.max(2, bw * f), height: 18, rx: 3, 'class': f >= 1 ? 'bench-done' : 'bench-run' }));
        svg.appendChild(el('text', { x: x + bw + 4, y: y + 13, 'class': 'bench-n' }, f >= 1 ? '✓' : ''));
      });
    });
    box.textContent = ''; box.appendChild(svg);
    var p = document.createElement('p'); p.className = 'bench-note';
    p.textContent = 'Replies received per model and arm. Updated as each batch lands' + (d.updated ? ' (' + d.updated + ' UTC)' : '') + '. Results are published after review.';
    box.appendChild(p);
  }
  function started(d) { return (d.models || []).some(function (m) { return m.bare > 0; }); }
  var extra = document.getElementById('bench-more'), done = {};
  function hideDone() { if (done[1]) box.hidden = true; for (var k in done) { var h = document.getElementById('bench-r' + k + 'h'), c = document.getElementById('bench-r' + k); if (h) h.hidden = true; if (c) c.hidden = true; } }
  function load() {
    fetch('/iris/bench.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) { draw(d, box); }).catch(function () {});
    if (!extra) return;
    for (var n = 2; n <= 11; n++) (function (n) {
      fetch('/iris/bench' + n + '.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
        if (!started(d)) return;
        var id = 'bench-r' + n, c = document.getElementById(id);
        if (!c) { var h = document.createElement('h3'); h.id = id + 'h'; h.textContent = 'Round ' + n + ': different questions'; c = document.createElement('div'); c.id = id; c.className = 'bench-live';
          extra.appendChild(h); extra.appendChild(c); }
        draw(d, c); hideDone();
      }).catch(function () {});
    })(n);
  }

  // Results of finished rounds: per model and Fault family, share of readable replies that commit the Fault, bare and with the Guard wording, with the 95% interval.
  var res = document.getElementById('bench-results');
  var FAM = [['P1', 'Forced verdict', 'Fault 19'], ['P2', 'Verdict without a width', 'Fault 25'], ['P3', 'Unchecked equals sign', 'Fault 29'], ['P4', 'Best of n', 'Fault 3']];
  function drawRound(rd) {
    var ms = rd.models, L = 150, cw = 142, gap = 10, rowh = 40, W = L + 4 * (cw + gap), H = 52 + ms.length * rowh;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Fault rates per model and family, round ' + rd.round, 'class': 'bench-svg' });
    FAM.forEach(function (f, i) { var x = L + i * (cw + gap); svg.appendChild(el('text', { x: x, y: 14, 'class': 'bench-h' }, f[1])); svg.appendChild(el('text', { x: x, y: 29, 'class': 'bench-f' }, f[2])); });
    ms.forEach(function (m, r) {
      var y = 40 + r * rowh; svg.appendChild(el('text', { x: 0, y: y + 17, 'class': 'bench-m' }, m.name));
      FAM.forEach(function (f, i) {
        var x = L + i * (cw + gap), c = m.fam[f[0]];
        [['bare', 0, 'bench-run'], ['guard', 15, 'bench-done']].forEach(function (a) {
          var v = c[a[0]], yy = y + a[1];
          svg.appendChild(el('rect', { x: x, y: yy, width: cw, height: 11, rx: 3, 'class': c.ct ? 'bench-ct' : 'bench-bg' }));
          if (c.ct || !v) { if (a[0] === 'bare') svg.appendChild(el('text', { x: x + 4, y: yy + 9, 'class': 'bench-cn' }, 'cannot tell')); return; }
          if (v[0] > 0) svg.appendChild(el('rect', { x: x, y: yy, width: Math.max(2, cw * v[0] / 100), height: 11, rx: 3, 'class': a[2] }));
          svg.appendChild(el('text', { x: x + cw - 3, y: yy + 9, 'text-anchor': 'end', 'class': 'bench-v' }, v[0] + '% [' + v[1] + ', ' + v[2] + ']'));
        });
      });
    });
    return svg;
  }
  // One index over every finished round: per model and Fault family, the lowest and highest share across the rounds that could be read, bare and with the Guard wording.
  function span(vals) { if (!vals.length) return null; var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals); return lo === hi ? lo + '%' : lo + '\u2013' + hi + '%'; }
  function drawIndex(rs) {
    var tbl = document.createElement('table'), hd = '<thead><tr><th>Model</th>';
    FAM.forEach(function (f) { hd += '<th>' + f[1] + '<span class="by"> ' + f[2] + '</span></th>'; });
    tbl.className = 'mtx'; tbl.innerHTML = hd + '</tr></thead>'; var tb = document.createElement('tbody');
    rs[0].models.forEach(function (m0, mi) {
      var tr = document.createElement('tr'), cells = '<td>' + m0.name + '</td>';
      FAM.forEach(function (f) {
        var b = [], g = [], n = 0;
        rs.forEach(function (rd) { var c = rd.models[mi].fam[f[0]]; if (c.ct || !c.bare) return; n++; b.push(c.bare[0]); if (c.guard) g.push(c.guard[0]); });
        cells += n ? '<td>Bare ' + span(b) + '<br>Guard ' + span(g) + '<span class="by"> in ' + n + ' of ' + rs.length + ' rounds</span></td>' : '<td><span class="by">Cannot tell in all ' + rs.length + ' rounds</span></td>';
      });
      tr.innerHTML = cells; tb.appendChild(tr);
    });
    tbl.appendChild(tb); return tbl;
  }
  function loadResults() {
    if (!res) return;
    fetch('/iris/bench-results.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var rs = d.rounds || []; if (!rs.length) return; res.textContent = ''; rs.forEach(function (rd) { done[rd.round] = 1; }); hideDone();
      res.appendChild(drawIndex(rs));
      var p = document.createElement('p'); p.className = 'bench-note';
      p.textContent = 'Each cell gives the lowest and highest share of readable replies that commit the Fault, across the rounds in which that cell could be read. Bare is the plain prompt. Guard adds the Fault and Guard wording. Every round used different questions. Cannot tell means the round\u2019s repeat or control checks failed. No ranking.';
      res.appendChild(p);
      rs.forEach(function (rd) { var dt = document.createElement('details'); dt.className = 'bench-round'; var s = document.createElement('summary'); s.textContent = 'Round ' + rd.round + ', full grid with intervals'; dt.appendChild(s); dt.appendChild(drawRound(rd)); res.appendChild(dt); });
    }).catch(function () {});
  }
  load(); loadResults(); setInterval(function () { load(); loadResults(); }, 60000);
})();
