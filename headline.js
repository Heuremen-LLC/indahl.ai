// Headlines: the page's headline number, and on the home page the strongest ones, from /headlines.json (built from the live feeds).
(function () {
  var path = location.pathname.replace(/\/+$/, '') || '/';
  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
  function block(h) { return '<div class="hl-big">' + esc(h.big) + '</div><p class="hl-line">' + esc(h.line) + '</p>'; }
  // STACK: pick any two tests on the site and see how their shares stack. The number is the difference in points with its interval (Newcombe, from each test's own 95% interval).
  function stackPick(main) {
    fetch('/stack/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var rows = (d.rows || []).filter(function (r) { return r.share != null && r.of > 0; }); if (rows.length < 2) return;
      function pct(x) { var v = x * 100; return (v < 10 ? v.toFixed(1) : Math.round(v)) + '%'; }
      function pts(x) { var v = Math.abs(x * 100); return (v < 10 ? v.toFixed(1) : Math.round(v)); }
      function label(r) { return r.page + ': ' + r.test; }
      var a = Math.floor(Math.random() * rows.length), b = a; while (b === a) b = Math.floor(Math.random() * rows.length);
      var slot0 = document.getElementById('hl-slot'), s = slot0 || document.createElement('section'); s.className = (slot0 ? 'hl-slot hl-stack ' : '') + 'hl pick'; if (slot0) slot0.removeAttribute('aria-hidden');
      var opts = rows.map(function (r, i) { return '<option value="' + i + '">' + esc(label(r).slice(0, 90)) + '</option>'; }).join('');
      s.innerHTML = '<div class="hl-big" id="pk-big"></div><p class="hl-line" id="pk-line"></p><div class="pk-ctl"><select id="pk-a" aria-label="First test">' + opts + '</select><span class="pk-vs">against</span><select id="pk-b" aria-label="Second test">' + opts + '</select><button type="button" class="btn ghost" id="pk-go">Shuffle</button></div><div id="pk-graph"></div>';
      if (!slot0) { var old = document.querySelector('.hl'); if (old) old.parentNode.removeChild(old); main.insertBefore(s, main.firstChild); }
      var sa = s.querySelector('#pk-a'), sb = s.querySelector('#pk-b');
      function show() {
        var x = rows[+sa.value], y = rows[+sb.value]; if (x.share < y.share) { var t = x; x = y; y = t; } var diff = x.share - y.share;
        var lo = diff - Math.sqrt(Math.pow(x.share - x.share_lo, 2) + Math.pow(y.share_hi - y.share, 2)), hi = diff + Math.sqrt(Math.pow(x.share_hi - x.share, 2) + Math.pow(y.share - y.share_lo, 2));
        var big = (diff === 0 ? '0' : pts(diff)) + ' points';
        s.querySelector('#pk-big').textContent = big; window.__stackPicked = [x, y]; document.dispatchEvent(new CustomEvent('stackpick', { detail: { rows: [x, y] } }));
        s.querySelector('#pk-line').textContent = x.page + ' ' + pct(x.share) + ' (' + x.n + ' of ' + x.of + ', ' + x.outcome.toLowerCase().replace(/_/g, ' ') + ') against ' + y.page + ' ' + pct(y.share) + ' (' + y.n + ' of ' + y.of + ', ' + y.outcome.toLowerCase().replace(/_/g, ' ') + '). ' + x.page + ' is higher. Difference ' + (lo * 100).toFixed(1) + ' to ' + (hi * 100).toFixed(1) + ' points, 95% interval.';
      }
      sa.value = a; sb.value = b; sa.onchange = sb.onchange = show;
      s.querySelector('#pk-go').onclick = function () { var i = Math.floor(Math.random() * rows.length), j = i; while (j === i) j = Math.floor(Math.random() * rows.length); sa.value = i; sb.value = j; show(); };
      show();
    }).catch(function () {});
  }
  // 29 Oct 2026: the receipt line. Says only that the feed behind the number was hashed onto the tape at an entry (TAPE PLAN Addendum 3).
  function receipt(box, slug) {
    fetch('/tape/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (t) {
      var f = t.feeds && t.feeds[slug]; if (!f || box.querySelector('.hl-receipt')) return;
      var p = document.createElement('p'); p.className = 'hl-receipt'; p.appendChild(document.createTextNode('Receipt: the feed behind this number was hashed onto the tape at entry ' + f.n + ', ' + f.hash.slice(0, 10) + '\u2026 '));
      var a = document.createElement('a'); a.href = '/tape'; a.textContent = 'See the tape'; p.appendChild(a); p.appendChild(document.createTextNode('.')); box.appendChild(p);
    }).catch(function () {});
  }
  function run() {
    fetch('/headlines.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var pages = d.pages || {}, main = document.querySelector('main.wrap'); if (!main) return;
      var slot = document.getElementById('hl-slot');
      var old = slot ? null : document.querySelector('.hl, .hlgrid'); if (old) old.parentNode.removeChild(old);
      function fill(cls, html) { if (slot) { slot.className = 'hl-slot ' + cls + (slot.className.indexOf('hl-home') > -1 ? ' hl-home' : '') + (slot.className.indexOf('hl-stack') > -1 ? ' hl-stack' : ''); slot.removeAttribute('aria-hidden'); slot.innerHTML = html; return slot; } var e = document.createElement('section'); e.className = cls; e.innerHTML = html; main.insertBefore(e, main.firstChild); return e; }
      if (path === '/') {
        var list = (d.home || []).filter(function (s) { return pages[s]; }); if (!list.length) return;
        fill('hlgrid', list.map(function (s) { var h = pages[s]; var m = /^(.*?[.!?])(\s+.+)$/.exec(h.line || ''); var line = m ? esc(m[1]) + '<span class="hl-rest">' + esc(m[2]) + '</span>' : esc(h.line); return '<a class="hlcard" href="' + esc(h.href) + '"><div class="hl-big">' + esc(h.big) + '</div><p class="hl-line">' + line + '</p><span class="hl-more">' + esc(s.toUpperCase()) + '</span></a>'; }).join(''));
      } else {
        if (path === '/stack') { stackPick(main); return; }
        var slug = path.split('/')[1]; if (path.split('/').length > 2 && path !== '/hermes/model') return; var h = pages[slug]; if (!h || path === '/hermes/model') return;
        var hs = fill('hl', block(h)); receipt(hs, slug);
      }
    }).catch(function () {});
  }
  run(); if (path !== '/stack') setInterval(run, 120000);
})();
