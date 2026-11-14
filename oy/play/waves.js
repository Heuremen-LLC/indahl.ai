// OY: how nodes are made. (1) Two waves going opposite ways add up to a standing wave whose nodes never move.
// (2) Ripples from one, two or three sources: where crests meet troughs the water stays still. (23 Oct 2026)
const $ = id => document.getElementById(id);
function fit(cv, h) { const w = Math.min(cv.parentElement.clientWidth, 560), d = devicePixelRatio; cv.width = w * d; cv.height = h * d; cv.style.width = w + 'px'; cv.style.height = h + 'px'; }
const line = $('waves-line'), lg = line.getContext('2d');
function drawLine(t) {
  const W = line.width, H = line.height, d = devicePixelRatio, k = 2 * Math.PI / (W / 3), w = t / 500, mid = H / 2, A = H * .17;
  lg.fillStyle = '#f7f0e0'; lg.fillRect(0, 0, W, H);
  const plot = (f, col, lw, dy) => { lg.beginPath(); for (let x = 0; x <= W; x += 2) { const y = mid + dy - A * f(x); x ? lg.lineTo(x, y) : lg.moveTo(x, y); } lg.strokeStyle = col; lg.lineWidth = lw * d; lg.stroke(); };
  plot(x => Math.sin(k * x - w), 'rgba(196,60,42,.75)', 1.5, -H * .28);                  // going right
  plot(x => Math.sin(k * x + w), 'rgba(42,90,138,.75)', 1.5, -H * .28);                  // going left
  plot(x => Math.sin(k * x - w) + Math.sin(k * x + w), '#24201a', 2.5, H * .12);          // together
  for (let n = 0; n * Math.PI / k <= W; n++) { lg.beginPath(); lg.arc(n * Math.PI / k, mid + H * .12, 5 * d, 0, 7); lg.fillStyle = '#c8902a'; lg.fill(); }
}
const pond = $('waves-pond'), pg = pond.getContext('2d'); let srcs = [[.5, .5]], still = false, img = null, avg = null;
const SETS = { 1: [[.5, .5]], 2: [[.38, .5], [.62, .5]], 3: [[.5, .36], [.38, .58], [.62, .58]] };
function drawPond(t) {
  const W = 220, H = 140; if (!img) { img = pg.createImageData(W, H); avg = new Float32Array(W * H); }
  const k = 2 * Math.PI / 14, w = t / 140;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    let v = 0; for (const [sx, sy] of srcs) { const r = Math.hypot(x - sx * W, y - sy * H); v += Math.sin(k * r - w) / Math.sqrt(1 + r / 6); }
    const i = y * W + x; avg[i] = avg[i] * .97 + Math.abs(v) * .03;
    const a = still ? Math.min(1, avg[i] * 1.4) : Math.min(1, Math.abs(v) * .8), p = i * 4;
    if (still) { img.data[p] = 40 + 200 * a; img.data[p + 1] = 34 + 180 * a; img.data[p + 2] = 26 + 120 * a; }
    else if (v > 0) { img.data[p] = 247 - 51 * a; img.data[p + 1] = 240 - 180 * a; img.data[p + 2] = 224 - 182 * a; }
    else { img.data[p] = 247 - 205 * a; img.data[p + 1] = 240 - 150 * a; img.data[p + 2] = 224 - 86 * a; }
    img.data[p + 3] = 255;
  }
  const off = drawPond.c || (drawPond.c = Object.assign(document.createElement('canvas'), { width: W, height: H }));
  off.getContext('2d').putImageData(img, 0, 0); pg.imageSmoothingEnabled = true; pg.drawImage(off, 0, 0, pond.width, pond.height);
  for (const [sx, sy] of srcs) { pg.beginPath(); pg.arc(sx * pond.width, sy * pond.height, 5 * devicePixelRatio, 0, 7); pg.fillStyle = '#24201a'; pg.fill(); }
}
for (const n of [1, 2, 3]) $('pond-' + n).addEventListener('click', () => { srcs = SETS[n].map(s => s.slice()); avg && avg.fill(0); });
$('pond-still').addEventListener('change', e => { still = e.target.checked; });
pond.addEventListener('click', e => { const r = pond.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
  let best = 0, bd = 9; srcs.forEach(([sx, sy], i) => { const dd = Math.hypot(sx - x, sy - y); if (dd < bd) { bd = dd; best = i; } }); srcs[best] = [x, y]; avg && avg.fill(0); });
function size() { fit(line, 230); fit(pond, 300); }
window.addEventListener('resize', size); size();
function tick(t) { drawLine(t); drawPond(t); requestAnimationFrame(tick); } requestAnimationFrame(tick);
