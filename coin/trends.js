// COIN trends: pool shares over time and batch payouts, from the blocks and transactions we hold. Reads /coin/trends.json.
(function () {
  var box = document.getElementById('coin-trends'); if (!box) return;
  function W(o) { return { CONSISTENT: 'consistent', ABOVE: 'above', CANNOT_TELL: 'cannot tell' }[o] || o; }
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t == null ? '' : t; return c; }
  fetch('/coin/trends.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.series) { box.textContent = 'Waiting for the first analysis.'; return; }
    var top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = 'Blocks held: ' + d.blocks + ' (heights ' + d.first_height + ' to ' + d.last_height + '), ' + d.span_days + ' days, ' + d.buckets + ' six hour buckets. Transactions scanned: ' + d.tx_scanned + '. The share test needs 14 days held. Updated ' + d.updated + ' UTC.';
    box.textContent = ''; box.appendChild(top);
    var h = document.createElement('h3'); h.textContent = 'Pool shares over time'; box.appendChild(h);
    var t = document.createElement('table'); t.className = 'mtx'; t.innerHTML = '<thead><tr><th>Series</th><th>Kind</th><th>Blocks</th><th>Share</th><th>Buckets tested</th><th>Moves found</th><th>Moves expected from chance</th><th>Outcome</th></tr></thead>';
    var b = document.createElement('tbody');
    d.series.forEach(function (s) { var r = document.createElement('tr'); r.appendChild(td(s.name)); r.appendChild(td(s.kind)); r.appendChild(td(s.blocks, 1)); r.appendChild(td((100 * s.share).toFixed(1) + '%', 1)); r.appendChild(td(s.tests, 1)); r.appendChild(td(s.flags, 1)); r.appendChild(td(s.expected, 1)); r.appendChild(td(W(s.outcome))); b.appendChild(r); });
    t.appendChild(b); box.appendChild(t);
    var rl = document.createElement('p'); rl.className = 'bench-note';
    rl.textContent = 'A move is a six hour bucket whose share is three or more standard deviations from the series\' own share over the preceding seven days. Chance alone gives a move in about 0.27 percent of tests. The reading is above when the moves found exceed the number expected plus two square roots of it, consistent when they do not, and cannot tell while fewer than 14 days are held. The address rows and the tag rows are tests on the same blocks, so one event can flag an address and a tag together. The normal approximation at three standard deviations understates the tail for small shares.'; box.appendChild(rl);
    var h2 = document.createElement('h3'); h2.textContent = 'Batch payouts by watched address'; box.appendChild(h2);
    var t2 = document.createElement('table'); t2.className = 'mtx'; t2.innerHTML = '<thead><tr><th>Address</th><th>Payouts found</th><th>Median gap, hours</th><th>Median outputs</th><th>Median total, RVN</th><th>Recipients</th><th>Largest five recipients, share of volume</th></tr></thead>';
    var b2 = document.createElement('tbody');
    d.batches.forEach(function (x) { var r = document.createElement('tr'); r.appendChild(td(x.address)); r.appendChild(td(x.payouts, 1)); r.appendChild(td(x.median_gap_h, 1)); r.appendChild(td(x.median_outputs, 1)); r.appendChild(td(x.median_total_rvn, 1)); r.appendChild(td(x.recipients, 1)); r.appendChild(td(x.top5_share == null ? '' : (100 * x.top5_share).toFixed(0) + '%', 1)); b2.appendChild(r); });
    t2.appendChild(b2); box.appendChild(t2);
    var l = d.linkage || {}, p = document.createElement('p'); p.className = 'bench-note';
    p.textContent = 'Shared infrastructure between pools: ' + W(l.outcome) + '. ' + (l.why || '') + '. Addresses are shown as the chain records them. Nothing here says who holds an address.'; box.appendChild(p);
  }).catch(function () { box.textContent = 'The analysis could not be read just now.'; });
})();
