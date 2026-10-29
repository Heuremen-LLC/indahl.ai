// Right of reply: posted responses to a page's rows, as received, dated, with the host each came from. Reads /replies.json. Shows nothing when there are none.
(function () {
  var s = document.getElementById('replies'); if (!s) return; var pre = s.getAttribute('data-prefix') + '-';
  fetch('/replies.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
    var rs = (d.replies || []).filter(function (x) { return String(x.unit).indexOf(pre) === 0; }); if (!rs.length) return;
    var h = document.createElement('h2'); h.textContent = 'Responses'; s.appendChild(h);
    var p = document.createElement('p'); p.className = 'bench-note'; p.textContent = 'Posted as received, with the date and the host each came from. A response changes a row only through a dated addendum after a recount.'; s.appendChild(p);
    var ul = document.createElement('ul');
    rs.forEach(function (x) {
      var li = document.createElement('li'), a = document.createElement('a'); a.href = x.url; a.rel = 'noopener'; a.textContent = 'Response to ' + x.unit + ' from ' + x.host; li.appendChild(a);
      li.appendChild(document.createTextNode(', received ' + String(x.received).slice(0, 10) + ', posted ' + x.posted + '. Our recount: ' + x.recount)); ul.appendChild(li);
    });
    s.appendChild(ul);
  }).catch(function () {});
})();
