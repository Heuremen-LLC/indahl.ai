// OY: a standing sound wave between a speaker (bottom) and a reflector (top). Beads settle at the pressure nodes,
// half a wavelength apart. Speed of sound 343 m/s. (23 Oct 2026)
const cv = document.getElementById('wave'), g = cv.getContext('2d');
const fIn = document.getElementById('wave-f'), out = document.getElementById('wave-out');
const C = 343, GAP_MM = 40;                       // 4 cm between speaker and reflector
let f = 40000, beads = [];
function nodes() { const lam = C / f * 1000, n = []; for (let x = lam / 4; x < GAP_MM; x += lam / 2) n.push(x); return { lam, n }; }
function reset() {
  f = +fIn.value * 1000; const { lam, n } = nodes();
  out.textContent = `${(f / 1000).toFixed(0)} kHz: wavelength ${lam.toFixed(1)} mm, a node every ${(lam / 2).toFixed(1)} mm, ${n.length} nodes in the 40 mm gap`;
  beads = n.map(x => ({ target: x, y: x + (Math.random() - .5) * lam * .4 }));
}
function size() { const w = cv.parentElement.clientWidth; cv.width = Math.min(w, 520) * devicePixelRatio; cv.height = 360 * devicePixelRatio; cv.style.width = Math.min(w, 520) + 'px'; cv.style.height = '360px'; }
function frame(t) {
  const W = cv.width, H = cv.height, d = devicePixelRatio, top = 30 * d, bot = H - 30 * d, mm = (bot - top) / GAP_MM, k = 2 * Math.PI / (C / f * 1000);
  g.fillStyle = '#f7f0e0'; g.fillRect(0, 0, W, H);
  for (let py = top; py < bot; py += 2 * d) {                 // pressure: cos(k x) cos(w t), slowed down so you can see it
    const x = (bot - py) / mm, s = Math.cos(k * x), w = Math.cos(t / 260), p = s * w, a = Math.abs(s) * (.3 + .5 * Math.abs(w));
    g.fillStyle = p >= 0 ? `rgba(196,60,42,${a})` : `rgba(42,90,138,${a})`;
    g.fillRect(W * .2, py, W * .6, 2 * d);
  }
  g.fillStyle = '#24201a'; g.fillRect(W * .15, bot, W * .7, 14 * d); g.fillRect(W * .15, top - 14 * d, W * .7, 14 * d);
  g.font = `${12 * d}px Georgia`; g.fillStyle = '#f7f0e0'; g.textAlign = 'center';
  g.fillText('speaker', W / 2, bot + 11 * d); g.fillText('reflector', W / 2, top - 3 * d);
  for (const b of beads) { b.y += (b.target - b.y) * .04; const py = bot - b.y * mm;
    g.beginPath(); g.arc(W / 2, py, 6 * d, 0, 7); g.fillStyle = '#fffaf0'; g.fill(); g.strokeStyle = '#24201a'; g.lineWidth = 1.5 * d; g.stroke(); }
  requestAnimationFrame(frame);
}
fIn.addEventListener('input', reset); window.addEventListener('resize', size); size(); reset(); requestAnimationFrame(frame);
