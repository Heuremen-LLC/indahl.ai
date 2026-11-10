// Brand index search: filters the list as you type. No tracking, nothing sent.
(function () {
  var q = document.getElementById('brand-q'), li = document.querySelectorAll('#brand-list li'), n = document.getElementById('brand-none'); if (!q) return;
  q.addEventListener('input', function () {
    var t = q.value.toLowerCase().trim(), shown = 0;
    li.forEach(function (x) { var on = !t || x.getAttribute('data-n').indexOf(t) >= 0; x.hidden = !on; if (on) shown++; });
    if (n) n.hidden = shown > 0;
  });
})();
