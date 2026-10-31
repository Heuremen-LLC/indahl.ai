// YO, training live: the step, train and validation loss as the trainer prints them, and the baselines scored before training (PLAN_YO_V2).
// The test reading appears once, after the run. Reads /iris/yo.json.
(function () {
  var box = document.getElementById('yo-live'); if (!box) return;
  var NS = 'http://www.w3.org/2000/svg';
  function el(n, a, t) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); if (t != null) e.textContent = t; return e; }
  function h(tag, txt, cls) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function f3(x) { return x == null ? '-' : x.toFixed(3); }
  function chart(d) {
    var W = 760, H = 240, L = 46, R = 16, T = 34, Bm = 30, steps = d.steps || 2000;
    var pts = (d.train || []).concat(d.val || []), ymax = 0.1; pts.forEach(function (p) { if (p[1] > ymax) ymax = p[1]; }); ymax = Math.ceil(ymax * 10) / 10;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Training loss by step', 'class': 'bench-svg' });
    function X(s) { return L + (W - L - R) * Math.min(1, s / steps); } function Y(v) { return T + (H - T - Bm) * (1 - v / ymax); }
    var f = Math.min(1, (d.step || 0) / steps);
    svg.appendChild(el('text', { x: 0, y: 14, 'class': 'bench-h' }, 'Step ' + (d.step || 0).toLocaleString('en-US') + ' of ' + steps.toLocaleString('en-US')));
    svg.appendChild(el('rect', { x: 200, y: 3, width: W - 200 - R, height: 14, rx: 3, 'class': 'bench-bg' }));
    if (f > 0) svg.appendChild(el('rect', { x: 200, y: 3, width: Math.max(2, (W - 200 - R) * f), height: 14, rx: 3, 'class': f >= 1 ? 'bench-done' : 'bench-run' }));
    [0, ymax / 2, ymax].forEach(function (v) { svg.appendChild(el('line', { x1: L, x2: W - R, y1: Y(v), y2: Y(v), stroke: 'currentColor', 'stroke-opacity': '0.15' })); svg.appendChild(el('text', { x: L - 6, y: Y(v) + 4, 'text-anchor': 'end', 'class': 'bench-n' }, v.toFixed(ymax < 1 ? 2 : 1))); });
    [0, steps / 2, steps].forEach(function (s) { svg.appendChild(el('text', { x: X(s), y: H - 10, 'text-anchor': 'middle', 'class': 'bench-n' }, String(s))); });
    function line(ps, dash, w) { if (ps.length < 2) return; svg.appendChild(el('polyline', { points: ps.map(function (p) { return X(p[0]).toFixed(1) + ',' + Y(p[1]).toFixed(1); }).join(' '), fill: 'none', stroke: 'currentColor', 'stroke-width': w, 'stroke-dasharray': dash || '' })); }
    line(d.train || [], '', 1.5); line(d.val || [], '5 4', 2);
    (d.val || []).forEach(function (p) { svg.appendChild(el('circle', { cx: X(p[0]), cy: Y(p[1]), r: 3, fill: 'currentColor' })); });
    svg.appendChild(el('text', { x: W - R, y: T + 14, 'text-anchor': 'end', 'class': 'bench-n' }, 'solid: training loss · dashed with dots: validation loss'));
    return svg;
  }
  function table(rows, head) {
    var t = h('table', null, 'hl-tab'), th = h('thead'), tr = h('tr'); head.forEach(function (c) { tr.appendChild(h('th', c)); }); th.appendChild(tr); t.appendChild(th);
    var tb = h('tbody'); rows.forEach(function (r) { var x = h('tr'); r.forEach(function (c) { x.appendChild(h('td', c)); }); tb.appendChild(x); }); t.appendChild(tb); return t;
  }
  function draw(d) {
    box.textContent = '';
    if (!d || !d.state) { box.textContent = 'Preparing the run.'; return; }
    box.appendChild(chart(d));
    var n = d.nulls || {};
    box.appendChild(h('p', 'Baselines, scored on the test items before training began:', 'bench-note'));
    box.appendChild(table([
      ['Record audit (0 to 1)', 'flag nothing ' + f3(n.A_flag_nothing), 'base model ' + f3(n.A_base) + (n.A_base_unparsed != null ? ' (' + n.A_base_unparsed + ' of ' + n.A_n + ' replies not valid JSON). Reading labels like q16 as 16, a rule defined after the replies were read: ' + f3(n.A_base_lenient) : '')],
      ['Four-outcome verdict (accuracy)', 'always CONSISTENT ' + f3(n.C_always_consistent) + ' · two-outcome rule ' + f3(n.C_binary_rule), 'base model ' + f3(n.C_base)],
      ['CANNOT_TELL cases given another verdict', 'always CONSISTENT ' + f3(n.C_always_consistent_forced) + ' · two-outcome rule ' + f3(n.C_binary_rule_forced), 'base model ' + f3(n.C_base_forced)]
    ], ['Job', 'Rule baselines', 'Base model, untrained']));
    if (d.result) {
      box.appendChild(h('p', 'Test reading, read once after training (95% intervals, paired bootstrap over records):', 'bench-note'));
      box.appendChild(table((d.result.rows || []), d.result.head || ['Comparison', 'Difference', 'Outcome']));
    }
    var p = h('p', null, 'bench-note'); p.appendChild(document.createTextNode(d.model + '. ' + (d.state === 'training' ? 'Training now. ' : d.state === 'done' ? 'Training finished. ' : 'Not training yet. ') + (d.updated ? 'Updated ' + d.updated.replace('T', ' ').replace(':00Z', '').replace('Z', '') + ' UTC. ' : '')));
    var a = h('a', 'The plan'); a.href = d.plan; p.appendChild(a); p.appendChild(document.createTextNode(' was committed before any data was built.')); box.appendChild(p);
  }
  function load() { fetch('/iris/yo.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(draw).catch(function () {}); }
  load(); setInterval(load, 20000);
})();
