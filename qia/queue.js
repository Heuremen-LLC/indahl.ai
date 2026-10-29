// QIA queue ticker: IBM's pending-job count per processor and the waits our own jobs saw. Reads /qia/queue.json, written every 9 Nova ticks.
(function () {
  var box = document.getElementById('queue-live'); if (!box) return;
  function td(t, n) { var c = document.createElement('td'); if (n) c.className = 'n'; c.textContent = t == null ? '' : t; return c; }
  function ch(x) { return x == null ? '' : (x > 0 ? '+' : '') + x; }
  fetch('/qia/queue.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var ps = d.processors || []; if (!ps.length) { box.textContent = 'Waiting for the first read.'; return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Processor</th><th>Jobs pending at IBM</th><th>Change over 24 hours</th><th>Our finished jobs counted</th><th>Our median wait</th><th>Our longest wait</th><th>Our jobs queued now</th><th>Oldest of those</th></tr></thead>';
    var b = document.createElement('tbody');
    ps.forEach(function (p) {
      var r = document.createElement('tr'); r.appendChild(td(p.backend)); r.appendChild(td(p.pending == null ? 'nothing returned' : p.pending, 1)); r.appendChild(td(ch(p.change_24h), 1));
      r.appendChild(td(p.our_jobs, 1)); r.appendChild(td(p.our_median_wait, 1)); r.appendChild(td(p.our_longest_wait, 1)); r.appendChild(td(p.our_queued_now, 1)); r.appendChild(td(p.our_oldest_queued, 1)); b.appendChild(r);
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(t);
    var p = document.createElement('p'); p.className = 'bench-note'; p.textContent = 'Read ' + d.updated + '. ' + d.reads_held + ' rows held in the public history. Pending is the count IBM reports. IBM publishes no wait estimate and we do not make one. A wait is the time from creation to start of our own jobs, so it depends on the job and the plan on our account. A median is shown from three finished jobs.';
    box.appendChild(p);
  }).catch(function () { box.textContent = 'The ticker could not be read just now.'; });
})();
