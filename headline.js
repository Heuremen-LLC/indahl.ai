// Headlines: the page's headline number, and on the home page the strongest ones, from /headlines.json (built from the live feeds).
(function () {
  var path = location.pathname.replace(/\/+$/, '') || '/';
  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
  function block(h) { return '<div class="hl-big">' + esc(h.big) + '</div><p class="hl-line">' + esc(h.line) + '</p>'; }
  function run() {
    fetch('/headlines.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var pages = d.pages || {}, main = document.querySelector('main.wrap'); if (!main) return;
      var old = document.querySelector('.hl, .hlgrid'); if (old) old.parentNode.removeChild(old);
      if (path === '/') {
        var list = (d.home || []).filter(function (s) { return pages[s]; }); if (!list.length) return;
        var g = document.createElement('section'); g.className = 'hlgrid'; g.setAttribute('aria-label', 'Headlines');
        g.innerHTML = list.map(function (s) { var h = pages[s]; var m = /^(.*?[.!?])(\s+.+)$/.exec(h.line || ''); var line = m ? esc(m[1]) + '<span class="hl-rest">' + esc(m[2]) + '</span>' : esc(h.line); return '<a class="hlcard" href="' + esc(h.href) + '"><div class="hl-big">' + esc(h.big) + '</div><p class="hl-line">' + line + '</p><span class="hl-more">' + esc(s.toUpperCase()) + '</span></a>'; }).join('');
        main.insertBefore(g, main.firstChild);
      } else {
        var slug = path.split('/')[1]; if (path.split('/').length > 2 && path !== '/hermes/model') return; var h = pages[slug]; if (!h || path === '/hermes/model') return;
        var s = document.createElement('section'); s.className = 'hl'; s.innerHTML = block(h); main.insertBefore(s, main.firstChild);
      }
    }).catch(function () {});
  }
  run(); setInterval(run, 120000);
})();
