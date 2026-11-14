// OY Quantum Dice twin (23 Oct 2026). Parts and rules: Quantum Dice by Qlab, University of Twente, CC BY 4.0
// (github.com/qlab-utwente/Quantum-Dice-by-UTwente). Shells, mounts and battery holder: their print files. The board: their
// ProcessorPCB v4.2 outline and part placement (board.json; part bodies are nominal sizes). Rules: their firmware
// (StateMachine.cpp enterObserved, ScreenDeterminator.hpp), reimplemented here for the browser. Our changes: the browser itself,
// the cup placement, and a plain note that the real dice fake the link with a radio.
import * as THREE from './three.module.min.js';
import { STLLoader } from './STLLoader.js';
import { OrbitControls } from './OrbitControls.js';
const $ = id => document.getElementById(id);
const box = $('die');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); renderer.setClearColor(0xf7f0e0); box.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 1, 3000); camera.position.set(60, -420, 230); camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xfff6e0, 0x3a2f1e, 1.1));
const sun = new THREE.DirectionalLight(0xffffff, 1.5); sun.position.set(120, -200, 260); scene.add(sun);

// ---------- shared parts ----------
const loader = new STLLoader(), cache = {};
const stl = f => cache[f] || (cache[f] = loader.loadAsync('/oy/quantum-dice/stl/' + f).then(g => (g.computeVertexNormals(), g)));
const shellMats = [];
const shell = c => { const m = new THREE.MeshStandardMaterial({ color: c, roughness: .55, metalness: .05, transparent: true, opacity: 1 }); shellMats.push(m); return m; };
const COL = { frame: 0x24201a, yellow: 0xe6b422, red: 0xc43c2a, blue: 0x2a5a8a, white: 0xf3efe4 };
// rotation taking a cup's +z (its inside, where the mounts sit) onto the given direction
const R = { 'z1': [1,0,0, 0,1,0, 0,0,1], 'z-1': [1,0,0, 0,-1,0, 0,0,-1], 'x1': [0,0,1, 0,1,0, -1,0,0], 'x-1': [0,0,-1, 0,1,0, 1,0,0],
            'y1': [1,0,0, 0,0,1, 0,-1,0], 'y-1': [1,0,0, 0,0,-1, 0,1,0] };
const FACES = [['x',1],['x',-1],['y',1],['y',-1],['z',1],['z',-1]];
const KEY = (a, s) => a + (s > 0 ? '0' : '1');           // their naming: x0 = +x face, x1 = -x face
const CLASSIC = { x0: 2, x1: 5, y0: 3, y1: 4, z0: 6, z1: 1 };
const CUPFILE = { x0: '02A_Yellow_PLA_V9_display_cup_power.stl', x1: '02B_Yellow_PLA_V8_display_cup_ESP32.stl',
                  y0: '02C_Red_PLA_V8_display_cup_left_right.stl', y1: '02C_Red_PLA_V8_display_cup_left_right.stl',
                  z0: '02D_Blue_PLA_V8_display_cup_top_bottom.stl', z1: '02D_Blue_PLA_V8_display_cup_top_bottom.stl' };
const CUPCOL = { x: 'yellow', y: 'red', z: 'blue' };
let board = null;

function screenTex() { const c = document.createElement('canvas'); c.width = c.height = 256; const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return { c, t }; }
function draw(s, kind, n, tint) {     // kind: 'num' | 'mix' ; tint: entanglement colour or null
  const g = s.c.getContext('2d'); g.fillStyle = '#0d0b08'; g.fillRect(0, 0, 256, 256);
  if (tint) { g.strokeStyle = tint; g.lineWidth = 14; g.beginPath(); g.arc(128, 128, 112, 0, 7); g.stroke(); }
  if (kind === 'num') { g.fillStyle = '#fff8e8'; g.font = 'bold 150px Georgia, serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(String(n), 128, 138); }
  else { g.font = 'bold 44px Georgia, serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
         for (let k = 1; k <= 6; k++) { const a = -Math.PI / 2 + (k - 1) * Math.PI / 3; g.fillStyle = tint || '#c9b98f'; g.globalAlpha = .75; g.fillText(String(k), 128 + 70 * Math.cos(a), 128 + 70 * Math.sin(a)); }
         g.globalAlpha = 1; g.fillStyle = tint || '#fff8e8'; g.font = 'bold 58px Georgia, serif'; g.fillText('?', 128, 132); }
  s.t.needsUpdate = true;
}

async function buildDie(x0) {
  const die = { group: new THREE.Group(), cups: {}, screens: {}, mode: 'classic', ent: 'PURE', lastBasis: null, lastNum: null,
                partnerAxis: null, partnerNum: null, color: null, up: null, num: null, frame: [] };
  die.group.position.x = x0; scene.add(die.group);
  const top = new THREE.Mesh(await stl('01A_Blck_TPU_V81_top_frame.stl'), shell(COL.frame));
  const bot = new THREE.Mesh(await stl('01B_Blck_TPU_V81_bottom_frame.stl'), shell(COL.frame));
  die.group.add(top, bot); die.frame = [top, bot];
  for (const [ax, sg] of FACES) {
    const k = KEY(ax, sg), cup = new THREE.Group(), r = R[ax + (-sg)], m = new THREE.Matrix4();
    m.set(r[0], r[1], r[2], 0, r[3], r[4], r[5], 0, r[6], r[7], r[8], 0, 0, 0, 0, 1); cup.quaternion.setFromRotationMatrix(m);
    cup.add(new THREE.Mesh(await stl(CUPFILE[k]), shell(COL[CUPCOL[ax]])));
    const mount = k === 'x1' ? '03B_White_PLA_V8_display_mount_PCB.stl' : '03A_White_PLA_V8_display_mount.stl';
    cup.add(new THREE.Mesh(await stl(mount), new THREE.MeshStandardMaterial({ color: COL.white, roughness: .7 })));
    const mod = new THREE.Mesh(new THREE.CylinderGeometry(19, 19, 1.6, 48), new THREE.MeshStandardMaterial({ color: 0x1f3d6b, roughness: .5 }));
    mod.rotation.x = Math.PI / 2; mod.position.z = 5.2; cup.add(mod);                          // round GC9A01A display module
    const s = screenTex(); const scr = new THREE.Mesh(new THREE.CircleGeometry(16.2, 64), new THREE.MeshBasicMaterial({ map: s.t }));
    scr.rotation.y = Math.PI; scr.position.z = 1.0; cup.add(scr); die.screens[k] = s;          // the screen faces out (-z of the cup)
    if (k === 'x0') {                                                                            // power side: battery holder + LiPo
      cup.add(new THREE.Mesh(await stl('03C_White_PLA_V8_battery_holder.stl'), new THREE.MeshStandardMaterial({ color: COL.white, roughness: .7 })));
      const bat = new THREE.Mesh(new THREE.BoxGeometry(48, 30, 9), new THREE.MeshStandardMaterial({ color: 0x3a3a40, roughness: .4, metalness: .2 }));
      bat.position.z = 13.6 + 4.5; cup.add(bat);
    }
    if (k === 'x1' && board) cup.add(boardMesh());                                               // the ProcessorPCB on the rear yellow cup
    die.cups[k] = { group: cup, ax, sg }; die.group.add(cup);
  }
  return die;
}
function boardMesh() {
  const g = new THREE.Group(), shape = new THREE.Shape(board.outline.map(([x, y]) => new THREE.Vector2(x, y)));
  const pcb = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, { depth: board.thickness, bevelEnabled: false }), new THREE.MeshStandardMaterial({ color: 0x1d5c34, roughness: .6 }));
  g.add(pcb);
  for (const p of board.parts) {
    const body = new THREE.Mesh(new THREE.BoxGeometry(p.w, p.d, p.h), new THREE.MeshStandardMaterial({
      color: p.id === 'IC1' ? 0xb9bcc2 : /^J[2-7]$/.test(p.id) ? 0xe8dfc8 : /^J/.test(p.id) ? 0xf2f2f2 : 0x2b2622, roughness: .45, metalness: p.id === 'IC1' ? .6 : .1 }));
    body.position.set(p.x, p.y, p.side === 'top' ? board.thickness + p.h / 2 : -p.h / 2); body.rotation.z = p.rot * Math.PI / 180; g.add(body);
  }
  g.position.z = 15.6; return g;                                                                 // on top of the PCB mount (03B), inside the cup
}
let explode = 0;
function place(die) {
  die.frame[0].position.z = explode * .6; die.frame[1].position.z = -explode * .6;
  for (const c of Object.values(die.cups)) { c.group.position.set(0, 0, 0); c.group.position[c.ax] = c.sg * (40 + explode); }
}
function paint(die) {
  for (const [ax, sg] of FACES) {
    const k = KEY(ax, sg), s = die.screens[k];
    if (die.mode === 'classic') draw(s, 'num', CLASSIC[k], null);
    else if (die.up === k && die.num) draw(s, 'num', die.num, die.ent === 'ENTANGLED' ? die.color : null);
    else draw(s, 'mix', 0, die.ent === 'ENTANGLED' || die.ent === 'POST' ? die.color : null);
  }
}

// ---------- their rules ----------
const rnd6 = () => 1 + Math.floor(crypto.getRandomValues(new Uint32Array(1))[0] / 4294967296 * 6);
const AXNAME = { x: 'yellow', y: 'red', z: 'blue' };
function measure(die, other, k) {
  const axis = k[0]; die.up = k;
  if (die.mode === 'classic') { die.num = CLASSIC[k]; return `${CLASSIC[k]}`; }
  let n, why;
  if (die.ent === 'ENTANGLED') { n = rnd6(); why = 'measured first: random';
    other.ent = 'POST'; other.partnerAxis = axis; other.partnerNum = n; die.ent = 'PURE'; }
  else if (die.ent === 'POST') {
    if (axis === die.partnerAxis) { n = 7 - die.partnerNum; why = `same axis as its partner: ${die.partnerNum} + ${n} = 7`; }
    else { n = rnd6(); why = 'different axis from its partner: random'; }
    die.ent = 'PURE'; die.partnerAxis = die.partnerNum = null; }
  else if (axis === die.lastBasis && die.lastNum) { n = die.lastNum; why = 'same axis as its last roll: it remembers'; }
  else { n = rnd6(); why = 'new axis: random'; }
  die.lastBasis = axis; die.lastNum = n; die.num = n;
  if (die.ent === 'PURE' && other.ent !== 'POST') die.color = null;
  return `${n} on the ${AXNAME[axis]} axis (${why})`;
}

// ---------- motion ----------
const UPROT = { z0: new THREE.Euler(0, 0, 0), z1: new THREE.Euler(Math.PI, 0, 0), y0: new THREE.Euler(Math.PI / 2, 0, 0),
                y1: new THREE.Euler(-Math.PI / 2, 0, 0), x0: new THREE.Euler(0, -Math.PI / 2, 0), x1: new THREE.Euler(0, Math.PI / 2, 0) };
const anims = [];
function rollDie(die, other, label) {
  const keys = Object.keys(UPROT), k = keys[rnd6() - 1];
  const to = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), Math.random() * Math.PI * 2).multiply(new THREE.Quaternion().setFromEuler(UPROT[k]));
  die.num = null; die.up = null; paint(die);
  anims.push({ t0: performance.now(), dur: 1300, from: die.group.quaternion.clone(), to, spin: 2 + Math.random() * 2, die,
               done: () => { const msg = measure(die, other, k); paint(die); paint(other); say(`${label}: ${msg}`); } });
}
function say(t) { const r = $('die-result'); r.textContent = t + (r.textContent ? '\n' + r.textContent : ''); r.textContent = r.textContent.split('\n').slice(0, 4).join('\n'); }

// ---------- page ----------
function size() { const w = box.clientWidth, h = Math.max(340, Math.min(600, w * .62)); renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }
window.addEventListener('resize', size); size();
let A, B;
async function main() {
  board = await (await fetch('/oy/quantum-dice/board.json')).json();
  A = await buildDie(-75); B = await buildDie(75); [A, B].forEach(d => { place(d); paint(d); });
  $('die-status').textContent = '';
}
const COLORS = ['#3fd0ff', '#ff5fd2', '#7dff6a', '#ffb84a'];
$('die-mode').addEventListener('click', () => { const q = A.mode === 'classic'; for (const d of [A, B]) { d.mode = q ? 'quantum' : 'classic'; d.ent = 'PURE'; d.up = d.num = d.color = null; d.lastBasis = d.lastNum = null; paint(d); }
  $('die-mode').textContent = q ? 'Classic mode' : 'Quantum mode'; say(q ? 'Quantum mode: every face is a superposition of 1 to 6' : 'Classic mode: a normal die'); });
$('die-entangle').addEventListener('click', () => {
  if (A.mode !== 'quantum') { say('Switch to quantum mode first'); return; }
  const c = COLORS[rnd6() % COLORS.length];
  anims.push({ t0: performance.now(), dur: 1600, slide: true, done: () => { for (const d of [A, B]) { d.ent = 'ENTANGLED'; d.color = c; d.up = d.num = null; paint(d); } say('Entangled: same colour on both. Roll them one at a time.'); } });
});
$('die-roll-a').addEventListener('click', () => rollDie(A, B, 'Left die'));
$('die-roll-b').addEventListener('click', () => rollDie(B, A, 'Right die'));
$('die-inside').addEventListener('change', e => { for (const m of shellMats) { m.opacity = e.target.checked ? .16 : 1; m.depthWrite = !e.target.checked; } });
$('die-explode').addEventListener('input', e => { explode = +e.target.value; [A, B].forEach(place); });
function tick(now) {
  for (let i = anims.length - 1; i >= 0; i--) {
    const a = anims[i], k = Math.min(1, (now - a.t0) / a.dur), e = 1 - Math.pow(1 - k, 3);
    if (a.slide) { const gap = 75 - 45 * Math.sin(Math.PI * k); A.group.position.x = -gap; B.group.position.x = gap; }
    else { const tumble = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, .6, .3).normalize(), (1 - e) * a.spin * Math.PI * 2);
           a.die.group.quaternion.slerpQuaternions(a.from, a.to, e).premultiply(tumble); }
    if (k === 1) { anims.splice(i, 1); a.done && a.done(); }
  }
  controls.update(); renderer.render(scene, camera); requestAnimationFrame(tick);
}
requestAnimationFrame(tick); main();
