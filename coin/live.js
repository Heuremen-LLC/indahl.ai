// COIN: Ravencoin stated against delivered. Reads /coin/live.json, written on every round by the tick bus.
(function () {
  var box = document.getElementById('coin-live'); if (!box) return;
  var HEX = '0123456789abcdef', NS = 'http://www.w3.org/2000/svg';
  function el(n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function fmt(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function tr(a, b) { return '<tr><td>' + a + '</td><td class="n">' + b + '</td></tr>'; }
  function W(o) { return o.replace('_', ' ').toLowerCase(); }
  fetch('/coin/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (j) {
    if (!j.latest_hash) { box.textContent = 'Waiting for the first round.'; return; }
    var q = j.gap_q || {}, pc = function (v) { return (v * 100).toFixed(1) + '%'; };
    box.innerHTML = '<div class="coin-top"><div><h3>Latest block hash</h3><div class="hashline" id="c-hash"></div></div><div><h3>Blocks read</h3><svg class="coin-svg" id="c-pg" viewBox="0 0 420 10" role="img" aria-label="Progress of blocks read"></svg><p class="bench-note" id="c-prog"></p></div></div>'
      + '<div class="coin-three"><div><h3>Seconds between blocks</h3><table class="mtx small"><tbody>' + tr('Mean, stated 60', j.gap_mean + ' s') + tr('Median', Math.round(q.p50) + ' s') + tr('Middle half', Math.round(q.p25) + ' to ' + Math.round(q.p75) + ' s') + tr('Under 5 s', pc(j.gap_under5)) + tr('Over 180 s', pc(j.gap_over180)) + '</tbody></table></div>'
      + '<div><h3>Who signs the blocks</h3><table class="mtx small"><tbody>' + j.tags.slice(0, 6).map(function (t) { return tr(t[0], fmt(t[1])); }).join('') + '</tbody></table></div>'
      + '<div><h3>First payout address, share</h3><table class="mtx small"><tbody>' + j.top_addr.slice(0, 6).map(function (t) { return tr(t[0], pc(t[1])); }).join('') + '</tbody></table></div></div>'
      + '<h3>Whitepaper statements</h3><table class="mtx"><thead><tr><th>Id</th><th>Whitepaper says</th><th>Chain record</th><th>Outcome</th></tr></thead><tbody>'
      + (j.claims || []).map(function (c) { return '<tr><td>' + c.id + '</td><td>' + c.quote + '</td><td>' + c.delivered + '</td><td class="o-' + c.outcome + '">' + W(c.outcome) + '</td></tr>'; }).join('') + '</tbody></table>';
    var f = Math.min(1, j.read_rows / j.target_rows), H = j.latest_hash, n = H.length, lock = Math.round(f * n), hl = document.getElementById('c-hash');
    function draw() { var s = ''; for (var i = 0; i < n; i++) s += i < lock ? H[i] : '<s>' + HEX[(Math.random() * 16) | 0] + '</s>'; hl.innerHTML = s; }
    draw(); if (f < 1 && !matchMedia('(prefers-reduced-motion: reduce)').matches) setInterval(draw, 500);
    document.getElementById('c-prog').textContent = (f >= 1 ? 'All ' + fmt(j.read_rows) + ' blocks read' : fmt(j.read_rows) + ' of ' + fmt(j.target_rows) + ' blocks read') + ', newest height ' + fmt(j.tip) + ', ' + j.read;
    var pg = document.getElementById('c-pg'); pg.appendChild(el('rect', { x: 1, y: 1, width: 418, height: 8, 'class': 'tr' })); pg.appendChild(el('rect', { x: 1, y: 1, width: Math.max(1, 418 * f), height: 8, 'class': 'fl' }));
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
