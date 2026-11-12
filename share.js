// Share (12 Nov 2026, Wayfinder: "what if someone wanted to post a data headline or page to their shit?").
// One row of plain links under the page's headline (or at the top of the page): the reader posts the headline or the page to their own accounts.
// Nothing loads from any social site and nothing is tracked: each button is an ordinary link that opens the site's own share page in a new tab.
(function () {
  var main = document.querySelector('main.wrap'); if (!main || document.querySelector('.sharebar')) return;
  var url = location.origin + location.pathname;
  function title() { return (document.title || '').split(' | ')[0]; }
  function text() {
    var b = document.querySelector('#hl-slot .hl-big'), l = document.querySelector('#hl-slot .hl-line');
    if (b && l && b.textContent.trim()) { var t = b.textContent.trim() + ' ' + l.textContent.trim(); return t.length > 230 ? t.slice(0, 227).replace(/\s+\S*$/, '') + '…' : t; }
    return title() + ', from Heuremen LLC';
  }
  function e(s) { return encodeURIComponent(s); }
  var nets = [
    ['X', function (t) { return 'https://twitter.com/intent/tweet?text=' + e(t) + '&url=' + e(url); }],
    ['Bluesky', function (t) { return 'https://bsky.app/intent/compose?text=' + e(t + ' ' + url); }],
    ['LinkedIn', function () { return 'https://www.linkedin.com/sharing/share-offsite/?url=' + e(url); }],
    ['Facebook', function () { return 'https://www.facebook.com/sharer/sharer.php?u=' + e(url); }],
    ['Threads', function (t) { return 'https://www.threads.net/intent/post?text=' + e(t + ' ' + url); }],
    ['Email', function (t) { return 'mailto:?subject=' + e(title()) + '&body=' + e(t + '\n\n' + url); }]
  ];
  var bar = document.createElement('div'); bar.className = 'sharebar'; bar.setAttribute('aria-label', 'Share this page');
  var lab = document.createElement('span'); lab.className = 'sharelab'; lab.textContent = 'Share'; bar.appendChild(lab);
  if (navigator.share) {
    var n = document.createElement('button'); n.type = 'button'; n.className = 'sharebtn'; n.textContent = 'Share…';
    n.onclick = function () { navigator.share({ title: title(), text: text(), url: url }).catch(function () {}); }; bar.appendChild(n);
  }
  nets.forEach(function (x) {
    var a = document.createElement('a'); a.className = 'sharebtn'; a.textContent = x[0]; a.href = x[1](text());
    if (x[0] !== 'Email') { a.target = '_blank'; a.rel = 'noopener noreferrer nofollow'; }
    a.addEventListener('mousedown', function () { a.href = x[1](text()); }); a.addEventListener('focus', function () { a.href = x[1](text()); });   // the headline refreshes in place, so read it at click time
    bar.appendChild(a);
  });
  var c = document.createElement('button'); c.type = 'button'; c.className = 'sharebtn'; c.textContent = 'Copy link';
  c.onclick = function () {
    var done = function () { c.textContent = 'Copied'; setTimeout(function () { c.textContent = 'Copy link'; }, 1600); };
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, function () {}); else { var i = document.createElement('input'); i.value = url; document.body.appendChild(i); i.select(); try { document.execCommand('copy'); done(); } catch (er) {} document.body.removeChild(i); }
  };
  bar.appendChild(c);
  var slot = document.getElementById('hl-slot');
  if (slot && slot.parentNode) slot.parentNode.insertBefore(bar, slot.nextSibling); else main.insertBefore(bar, main.firstChild);
})();
