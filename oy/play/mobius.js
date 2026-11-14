// OY: a Möbius strip. An ant walks the middle line (home only after two laps); cut it down the middle (still one piece,
// twice as long) or a third of the way in (two pieces, linked). The cuts are the strip itself with a gap: honest geometry. (23 Oct 2026)
import * as THREE from '../quantum-dice/three.module.min.js';
import { OrbitControls } from '../quantum-dice/OrbitControls.js';
const $ = id => document.getElementById(id), box = $('mob');
const renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setClearColor(0xf7f0e0); box.appendChild(renderer.domElement);
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, 1, .1, 100); camera.position.set(0, -7.5, 5); camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xfff6e0, 0x3a2f1e, 1.2)); const sun = new THREE.DirectionalLight(0xffffff, 1.2); sun.position.set(3, -4, 6); scene.add(sun);
const R = 2.2, W = .9;
const P = (u, v) => new THREE.Vector3((R + v * Math.cos(u / 2)) * Math.cos(u), (R + v * Math.cos(u / 2)) * Math.sin(u), v * Math.sin(u / 2));
function band(v0, v1, hue0, hue1) {       // the strip between widths v0..v1, coloured along its length
  const nu = 240, nv = 6, pos = [], col = [], idx = [], c = new THREE.Color();
  for (let i = 0; i <= nu; i++) for (let j = 0; j <= nv; j++) { const u = 2 * Math.PI * i / nu, v = v0 + (v1 - v0) * j / nv, p = P(u, v); pos.push(p.x, p.y, p.z);
    c.setHSL(hue0 + (hue1 - hue0) * i / nu, .6, .55); col.push(c.r, c.g, c.b); }
  for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) { const a = i * (nv + 1) + j, b = a + nv + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.setIndex(idx); g.computeVertexNormals();
  return new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, side: THREE.DoubleSide, roughness: .6 }));
}
let strip = new THREE.Group(); scene.add(strip);
function show(mode) {
  scene.remove(strip); strip = new THREE.Group(); scene.add(strip); const gap = .07;
  if (mode === 'whole') strip.add(band(-W, W, .08, .58));
  if (mode === 'half') { strip.add(band(gap, W, .08, .33)); strip.add(band(-W, -gap, .33, .58)); }   // one loop: the halves join end to end
  if (mode === 'third') { strip.add(band(W / 3 + gap, W, .02, .02)); strip.add(band(-W, -W / 3 - gap, .02, .02)); strip.add(band(-W / 3 + gap, W / 3 - gap, .55, .55)); }
  ant.visible = trail.visible = mode === 'whole';
  $('mob-msg').textContent = { whole: 'One strip, half a twist. Follow the ant.', half: 'Cut down the middle: still ONE piece, twice as long. Follow the colours all the way round.',
    third: 'Cut a third of the way in: TWO pieces, linked together. A skinny strip (blue) and a long loop (red).' }[mode];
}
// the ant: walks the middle line, just off the surface on whichever side it started
const ant = new THREE.Mesh(new THREE.SphereGeometry(.09, 16, 12), new THREE.MeshStandardMaterial({ color: 0x24201a })); scene.add(ant);
const trailPts = [], trailGeo = new THREE.BufferGeometry(), trail = new THREE.Line(trailGeo, new THREE.LineBasicMaterial({ color: 0x24201a })); scene.add(trail);
function normal(u) { const e = 1e-3, du = P(u + e, 0).sub(P(u - e, 0)), dv = P(u, e).sub(P(u, -e)); return du.cross(dv).normalize(); }
let u = 0, last = 0;
function size() { const w = box.clientWidth, h = Math.max(320, Math.min(520, w * .65)); renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }
window.addEventListener('resize', size); size();
$('mob-whole').addEventListener('click', () => { show('whole'); u = 0; last = 0; trailPts.length = 0; $('mob-ant').textContent = 'The ant is on lap 1. Watch which side it comes back on.'; });
$('mob-half').addEventListener('click', () => show('half'));
$('mob-third').addEventListener('click', () => show('third'));
show('whole'); $('mob-ant').textContent = 'The ant is on lap 1. Watch which side it comes back on.';
function tick(t) {
  if (ant.visible) {
    u += .006; const p = P(u, 0).add(normal(u).multiplyScalar(.1)); ant.position.copy(p);
    trailPts.push(p.clone()); if (trailPts.length > 2200) trailPts.shift(); trailGeo.setFromPoints(trailPts);
    const lap = Math.floor(u / (2 * Math.PI));
    if (lap !== last) { last = lap; $('mob-ant').textContent = lap % 2 ? `Lap ${lap}: back where it started, but on the other side.` : `Lap ${lap}: home, on its own side again. Two laps, one side.`; }
  }
  controls.update(); renderer.render(scene, camera); requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
