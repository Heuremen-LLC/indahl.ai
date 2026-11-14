// OY: three bodies pulling on each other with gravity (G = 1, equal masses, leapfrog steps). The figure-eight orbit
// (found by Cris Moore in 1993, proved by Chenciner and Montgomery in 2000; it is stable, so nudging it shows little) and chaos: a messy start and its twin moved by a thousandth, which split apart. (23 Oct 2026)
const cv = document.getElementById('tb'), g = cv.getContext('2d');
const F8 = () => { const x = [[-0.97000436, 0.24308753], [0.97000436, -0.24308753], [0, 0]], v3 = [-0.93240737, -0.86473146];
  return { x, v: [[-v3[0] / 2, -v3[1] / 2], [-v3[0] / 2, -v3[1] / 2], v3.slice()] }; };
let A, B, trailA, trailB, mode = 'eight';
const MESSY = () => ({ x: [[0.729, -0.043], [0.349, 0.252], [-1.078, -0.209]], v: [[0.003, 0.201], [0.183, 0.196], [-0.186, -0.397]] });
let SOFT = 1e-6;   // a little softening in the messy start keeps close passes gentle; the figure-eight runs without it
function reset(m) { mode = m; SOFT = m === 'chaos' ? 0.01 : 1e-6;
  if (m === 'chaos') { A = MESSY(); B = MESSY(); B.x[0][0] += 0.001; } else { A = F8(); B = F8(); }   // B: the same start, moved by a hair
  trailA = [[], [], []]; trailB = [[], [], []]; }
function acc(s) { const a = [[0, 0], [0, 0], [0, 0]];
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) if (i !== j) { const dx = s.x[j][0] - s.x[i][0], dy = s.x[j][1] - s.x[i][1], r2 = dx * dx + dy * dy + SOFT, r3 = r2 * Math.sqrt(r2); a[i][0] += dx / r3; a[i][1] += dy / r3; }
  return a; }
function step(s, h) { let a = acc(s); for (let i = 0; i < 3; i++) { s.v[i][0] += a[i][0] * h / 2; s.v[i][1] += a[i][1] * h / 2; s.x[i][0] += s.v[i][0] * h; s.x[i][1] += s.v[i][1] * h; }
  a = acc(s); for (let i = 0; i < 3; i++) { s.v[i][0] += a[i][0] * h / 2; s.v[i][1] += a[i][1] * h / 2; } }
function size() { const w = Math.min(cv.parentElement.clientWidth, 560), d = devicePixelRatio; cv.width = w * d; cv.height = w * .7 * d; cv.style.width = w + 'px'; cv.style.height = w * .7 + 'px'; }
const COL = ['#c43c2a', '#e6b422', '#2a5a8a'];
function draw(s, trail, ghost) {
  const W = cv.width, H = cv.height, k = W / 3.6, d = devicePixelRatio, P = p => [W / 2 + p[0] * k, H / 2 - p[1] * k];
  for (let i = 0; i < 3; i++) { trail[i].push(P(s.x[i])); if (trail[i].length > 400) trail[i].shift();
    g.beginPath(); trail[i].forEach(([x, y], n) => n ? g.lineTo(x, y) : g.moveTo(x, y)); g.strokeStyle = COL[i]; g.globalAlpha = ghost ? .35 : .8; g.lineWidth = (ghost ? 1 : 1.6) * d; g.setLineDash(ghost ? [4 * d, 4 * d] : []); g.stroke();
    const [x, y] = P(s.x[i]); g.beginPath(); g.arc(x, y, (ghost ? 5 : 8) * d, 0, 7); g.fillStyle = COL[i]; g.fill(); }
  g.globalAlpha = 1; g.setLineDash([]);
}
function frame() {
  for (let n = 0; n < 6; n++) { step(A, .004); if (mode === 'chaos') step(B, .004); }
  g.fillStyle = '#f7f0e0'; g.fillRect(0, 0, cv.width, cv.height);
  if (mode === 'chaos') draw(B, trailB, true); draw(A, trailA, false);
  requestAnimationFrame(frame);
}
document.getElementById('tb-eight').addEventListener('click', () => reset('eight'));
document.getElementById('tb-chaos').addEventListener('click', () => reset('chaos'));
window.addEventListener('resize', size); size(); reset('eight'); requestAnimationFrame(frame);
