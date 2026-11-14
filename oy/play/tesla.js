// OY: Tesla's rotating magnetic field. Three coils 120 degrees apart, fed three currents 120 degrees out of step:
// their fields add up to one field of constant strength that turns, with nothing moving. With DC (no step) it can't turn. (23 Oct 2026)
const cv = document.getElementById('tesla'), g = cv.getContext('2d'); let ac = true, speed = 1, th = 0, last = 0;
function size() { const w = Math.min(cv.parentElement.clientWidth, 460), d = devicePixelRatio; cv.width = w * d; cv.height = w * d; cv.style.width = cv.style.height = w + 'px'; }
function arrow(x, y, dx, dy, col, w) { const d = devicePixelRatio; g.strokeStyle = g.fillStyle = col; g.lineWidth = w * d; g.beginPath(); g.moveTo(x, y); g.lineTo(x + dx, y + dy); g.stroke();
  const a = Math.atan2(dy, dx), L = Math.hypot(dx, dy); if (L < 6 * d) return; g.beginPath(); g.moveTo(x + dx, y + dy); g.lineTo(x + dx - 12 * d * Math.cos(a - .4), y + dy - 12 * d * Math.sin(a - .4)); g.lineTo(x + dx - 12 * d * Math.cos(a + .4), y + dy - 12 * d * Math.sin(a + .4)); g.fill(); }
function frame(t) {
  const dt = Math.min(.05, (t - last) / 1000); last = t; if (ac) th += dt * speed * 2;
  const W = cv.width, c = W / 2, R = W * .36, d = devicePixelRatio; g.fillStyle = '#f7f0e0'; g.fillRect(0, 0, W, W);
  const cols = ['#c43c2a', '#e6b422', '#2a5a8a']; let sx = 0, sy = 0;
  for (let k = 0; k < 3; k++) {
    const a = -Math.PI / 2 + k * 2 * Math.PI / 3, I = ac ? Math.cos(th - k * 2 * Math.PI / 3) : (k === 0 ? 1 : -.5);   // DC: fixed currents
    g.save(); g.translate(c + R * 1.12 * Math.cos(a), c + R * 1.12 * Math.sin(a)); g.rotate(a); g.fillStyle = cols[k]; g.globalAlpha = .35 + .65 * Math.abs(I); g.fillRect(-14 * d, -26 * d, 28 * d, 52 * d); g.restore();
    const fx = I * Math.cos(a), fy = I * Math.sin(a); sx += fx; sy += fy;
    arrow(c, c, fx * R * .6, fy * R * .6, cols[k], 2);
  }
  arrow(c, c, sx * R * .45, sy * R * .45, '#24201a', 5);           // the sum: 1.5 x one coil, always the same length
  g.font = `${13 * d}px Georgia`; g.fillStyle = '#24201a'; g.textAlign = 'center'; g.fillText(ac ? 'three currents, out of step: the field turns' : 'DC: the field just sits there', c, W - 12 * d);
  requestAnimationFrame(frame);
}
document.getElementById('tesla-ac').addEventListener('click', e => { ac = !ac; e.target.textContent = ac ? 'Switch to DC' : 'Switch to AC'; });
document.getElementById('tesla-speed').addEventListener('input', e => { speed = +e.target.value; });
window.addEventListener('resize', size); size(); requestAnimationFrame(frame);
