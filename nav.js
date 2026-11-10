// nav.js (10 Nov 2026): banner dropdowns on touch and keyboard, and the embed box. Nothing is sent anywhere.
// Without this script the dropdowns still open on hover and on keyboard focus (CSS), and a tap on a header goes to its page.
// With it, the first tap on a header on a touch screen opens its panel and the second tap goes to the page. Escape closes a panel.
(function () {
  var lastTouch = 0;
  document.addEventListener('pointerdown', function (e) { if (e.pointerType === 'touch' || e.pointerType === 'pen') lastTouch = Date.now(); }, true);
  function top(dd) { return dd.querySelector('a, button'); }
  function closeAll(except) {
    var o = document.querySelectorAll('.dd.open');
    for (var i = 0; i < o.length; i++) if (o[i] !== except) { o[i].classList.remove('open'); top(o[i]).setAttribute('aria-expanded', 'false'); }
  }
  document.addEventListener('click', function (e) {
    var t = e.target, a = t.closest ? t.closest('.dd > a') : null;
    var b = t.closest ? t.closest('.dd > button') : null;
    if (b) { var bd = b.parentNode, was = bd.classList.contains('open'); closeAll(bd); bd.classList.toggle('open', !was); bd.classList.toggle('shut', was); b.setAttribute('aria-expanded', was ? 'false' : 'true'); return; }   // the Grab and go button: a tap toggles its panel
    if (a) {
      var dd = a.parentNode, touch = (Date.now() - lastTouch < 1000) || (window.matchMedia && window.matchMedia('(hover: none)').matches);
      if (touch && !dd.classList.contains('open')) { e.preventDefault(); closeAll(dd); dd.classList.remove('shut'); dd.classList.add('open'); a.setAttribute('aria-expanded', 'true'); return; }
    }
    if (!(t.closest && t.closest('.dd'))) closeAll();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var f = document.activeElement, dd = f && f.closest ? f.closest('.dd') : null;
    closeAll();
    if (dd) { dd.classList.add('shut'); top(dd).focus(); }
  });
  function unshut(e) { var dd = e.target.closest ? e.target.closest('.dd') : null; if (dd && !dd.contains(e.relatedTarget)) dd.classList.remove('shut'); }
  document.addEventListener('focusout', unshut); document.addEventListener('mouseout', unshut);
  var dds = document.querySelectorAll('.dd > a, .dd > button');
  for (var i = 0; i < dds.length; i++) dds[i].setAttribute('aria-expanded', 'false');
  // the embed box: focus selects the whole snippet, ready to copy
  document.addEventListener('focusin', function (e) { var t = e.target; if (t.classList && t.classList.contains('embedcode')) setTimeout(function () { t.select(); }, 0); });
})();
