// What the IRIS lab is running now. Reads /iris/live.json, written by the lab queue on every tick.
(function () {
  var box = document.getElementById('iris-run'); if (!box) return;
  function ago(t) { if (!t) return ''; var m = Math.round((Date.now() / 1000 - t) / 60); return m < 90 ? m + ' minutes' : Math.round(m / 60) + ' hours'; }
  function li(j, extra) { return '<tr><td>' + j.title + '</td><td><a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/iris">' + j.plan.replace('iris_index/', '') + '</a></td><td>' + extra + '</td></tr>'; }
  fetch('/iris/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var run = d.running || [], nx = d.next || [], dn = d.done || [];
    var rows = run.map(function (j) { return li(j, 'running' + (j.started ? ' for ' + ago(j.started) : '')); }).concat(nx.map(function (j) { return li(j, j.ready ? 'next, plan committed' : 'waiting for its plan'); })).concat(dn.map(function (j) { return '<tr><td>' + j.title + '</td><td></td><td>finished</td></tr>'; }));
    box.innerHTML = '<table class="mtx"><thead><tr><th>Job</th><th>Plan, committed before the run</th><th>State</th></tr></thead><tbody>' + (rows.join('') || '<tr><td colspan="3">Nothing is running. The next job starts as soon as its plan is committed.</td></tr>') + '</tbody></table><p class="bench-note">One job at a time on our own machine. Updated ' + (d.updated || '') + ' UTC.</p>';
  }).catch(function () { box.textContent = 'The lab status could not be read just now.'; });
})();
