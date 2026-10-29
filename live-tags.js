// LIVE tags: puts a small "live" mark beside a desk or division link while that desk is being read or evaluated, or finished a minute ago.
(function () {
  var HREF = { model: '/hermes/model' }, TAGGED = [];
  function href(slug) { return HREF[slug] || '/' + slug; }
  function mark(a, what) {
    if (a.querySelector('.livetag')) return; var t = document.createElement('span'); t.className = 'livetag'; t.title = 'Being ' + (what === 'evaluating' ? 'evaluated' : 'read') + ' now'; t.setAttribute('aria-label', 'live'); t.textContent = 'live'; a.appendChild(t); TAGGED.push(t);
  }
  function clear() { TAGGED.forEach(function (t) { if (t.parentNode) t.parentNode.removeChild(t); }); TAGGED = []; }
  function run() {
    fetch('/activity.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      clear(); var live = (d && d.live) || {};
      if (d && d.updated && (Date.now() - Date.parse(d.updated)) > 45 * 60 * 1000) return;
      Object.keys(live).forEach(function (slug) {
        var as = document.querySelectorAll('a[href="' + href(slug) + '"]'); as.forEach(function (a) { mark(a, live[slug]); });
      });
      document.querySelectorAll('.hdiv').forEach(function (card) {
        if (card.querySelector('.hdesks .livetag')) { var h = card.querySelector('h2 a'); if (h) mark(h, 'reading'); }
      });
    }).catch(function () {});
  }
  run(); setInterval(run, 60000);
})();
