// CADA: public DNS filters stated against delivered. Reads /cada/live.json, written on every round by the tick bus.
(function () {
  var box = document.getElementById('cada-live'); if (!box) return;
  var NAMES = { 'cloudflare_malware_1.1.1.2': 'Cloudflare 1.1.1.2', 'quad9_9.9.9.9': 'Quad9 9.9.9.9', 'opendns': 'OpenDNS', 'adguard_default': 'AdGuard DNS default', 'cleanbrowsing_security': 'CleanBrowsing security', 'dns0_eu': 'DNS0.eu', 'controld_malware': 'Control D malware' };
  function cell(c) { if (!c || !c.n) return 'none yet'; return c.wilson[0] + '% [' + c.wilson[1] + ', ' + c.wilson[2] + '], ' + c.k + ' of ' + c.n; }
  fetch('/cada/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var rs = d.resolvers || [];
    var top = document.createElement('p'); top.className = 'bench-note';
    top.textContent = d.tracked + ' fresh domains tracked from ' + d.feed_reads + ' feed reads. Updated ' + d.updated + ' UTC. Domains the controls cannot resolve are left out of each rate.';
    if (!rs.length) { box.textContent = 'Waiting for the first fresh listings. The feeds are read on every round and each new domain is asked about at first sight, then after 1 hour, 6 hours and 24 hours.'; box.appendChild(top); return; }
    var t = document.createElement('table'); t.className = 'mtx';
    t.innerHTML = '<thead><tr><th>Resolver</th><th>At first sight</th><th>After 1 hour</th><th>After 6 hours</th><th>After 24 hours</th><th>Other answers</th></tr></thead>';
    var b = document.createElement('tbody');
    rs.forEach(function (x) {
      var o = x.classes || {}, other = ['SERVFAIL', 'TIMEOUT', 'NODATA'].filter(function (k) { return o[k]; }).map(function (k) { return o[k] + ' ' + k.toLowerCase(); }).join(', ');
      var r = document.createElement('tr'), td = function (s) { var c = document.createElement('td'); c.textContent = s; return c; };
      r.appendChild(td(NAMES[x.resolver] || x.resolver)); ['0', '3600', '21600', '86400'].forEach(function (k) { r.appendChild(td(cell(x.checkpoints[k]))); }); r.appendChild(td(other)); b.appendChild(r);
    });
    t.appendChild(b); box.textContent = ''; box.appendChild(top); box.appendChild(t);
  }).catch(function () { box.textContent = 'The round could not be read just now.'; });
})();
