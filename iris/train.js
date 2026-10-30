// Live progress of the trained Falcon on the Faults and Guards. Training steps and counts of replies received only. Reads /iris/train.json.
(function () {
  var box = document.getElementById('train-live'); if (!box) return;
  var NS = 'http://www.w3.org/2000/svg', ARMS = [['bare', 'Bare'], ['bare_copy', 'Repeat'], ['guard', 'Guard']];
  function el(n, a, t) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); if (t != null) e.textContent = t; return e; }
  function bar(svg, x, y, w, f, done) {
    svg.appendChild(el('rect', { x: x, y: y, width: w, height: 18, rx: 3, 'class': 'bench-bg' }));
    if (f > 0) svg.appendChild(el('rect', { x: x, y: y, width: Math.max(2, w * f), height: 18, rx: 3, 'class': done ? 'bench-done' : 'bench-run' }));
  }
  function draw(d) {
    if (!d || !d.sets) { box.textContent = 'Waiting for the first step.'; return; }
    var all = d.sets.tA.concat(d.sets.tB).every(function (m) { return ARMS.every(function (x) { return (m[x[0]] || 0) >= (d.of || 170); }); }), stepsDone = ['trained', 'mixed'].every(function (k) { return (parseInt((d.step || {})[k] || 0, 10) || 0) >= (d.steps || 600); });
    if (all && stepsDone) { box.textContent = d.model + '. Training finished, ' + (d.steps || 600) + ' steps each, and every reply was received on both evaluation sets' + (d.updated ? ' (status last checked ' + d.updated + ' UTC)' : '') + '.'; return; }
    var W = 760, L = 230, bw = 150, gap = 12, rowh = 30, rows = 2 + 3 + 3, H = 60 + rows * rowh + 40;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Training steps and replies received', 'class': 'bench-svg' });
    var y = 14; svg.appendChild(el('text', { x: 0, y: y, 'class': 'bench-h' }, 'Training, ' + (d.steps || 600) + ' steps each'));
    [['trained', 'Faults and Guards labels'], ['mixed', 'Mixed labels (control)']].forEach(function (t, i) {
      var yy = 24 + i * rowh, s = parseInt((d.step || {})[t[0]] || 0, 10) || 0, f = Math.min(1, s / (d.steps || 600));
      svg.appendChild(el('text', { x: 0, y: yy + 14, 'class': 'bench-m' }, t[1])); bar(svg, L, yy, bw * 2 + gap, f, f >= 1);
      svg.appendChild(el('text', { x: L + bw * 2 + gap + 4, y: yy + 13, 'class': 'bench-n' }, f >= 1 ? '✓' : (s ? 'step ' + s : '')));
    });
    var base = 24 + 2 * rowh + 18;
    ['tA', 'tB'].forEach(function (S, si) {
      var y0 = base + si * (4 * rowh);
      svg.appendChild(el('text', { x: 0, y: y0, 'class': 'bench-h' }, 'Evaluation set ' + (si ? 'B' : 'A')));
      ARMS.forEach(function (a, i) { svg.appendChild(el('text', { x: L + i * (bw + gap), y: y0, 'class': 'bench-h' }, a[1])); });
      (d.sets[S] || []).forEach(function (m, r) {
        var yy = y0 + 8 + r * rowh;
        svg.appendChild(el('text', { x: 0, y: yy + 14, 'class': 'bench-m' }, m.name));
        ARMS.forEach(function (a, i) { var f = Math.min(1, (m[a[0]] || 0) / (d.of || 170)); bar(svg, L + i * (bw + gap), yy, bw, f, f >= 1); svg.appendChild(el('text', { x: L + i * (bw + gap) + bw + 4, y: yy + 13, 'class': 'bench-n' }, f >= 1 ? '✓' : '')); });
      });
    });
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + (base + 2 * 4 * rowh + 10));
    box.textContent = ''; box.appendChild(svg);
    var p = document.createElement('p'); p.className = 'bench-note';
    p.textContent = d.model + '. Replies received per arm and evaluation set' + (d.updated ? ' (updated ' + d.updated + ' UTC)' : '') + '. Scores are published after the parser check (replies read in full), as in every round.';
    box.appendChild(p);
  }
  function load() { fetch('/iris/train.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(draw).catch(function () {}); }
  load(); setInterval(load, 20000);
})();
