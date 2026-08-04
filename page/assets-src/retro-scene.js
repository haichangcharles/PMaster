import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

export function initRetro(canvas, opts = {}) {
  const host = canvas.parentElement;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  const BG = { light: opts.bgLight ?? 0xf2efe9, dark: opts.bgDark ?? 0x0c0c11 };
  scene.background = new THREE.Color(BG.light);
  scene.fog = new THREE.Fog(BG.light, 26, 62);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 120);
  camera.position.set(7.6, 4.8, 11.6);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.minDistance = 7;
  controls.maxDistance = 24;
  controls.maxPolarAngle = Math.PI * 0.5;
  controls.enablePan = false;
  controls.target.set(0, 2.3, 0.4);
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.75;

  /* lights */
  const keyLight = new THREE.DirectionalLight(0xfff5e6, 2.2);
  keyLight.position.set(7, 11, 8);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(2048, 2048);
  keyLight.shadow.camera.left = -11; keyLight.shadow.camera.right = 11;
  keyLight.shadow.camera.top = 11; keyLight.shadow.camera.bottom = -11;
  keyLight.shadow.bias = -0.0004; keyLight.shadow.radius = 8;
  scene.add(keyLight);
  const fillLight = new THREE.DirectionalLight(0xbcd0ff, 0.6);
  fillLight.position.set(-8, 5, -6);
  scene.add(fillLight);
  const screenGlow = new THREE.PointLight(0x46ff8a, 0.5, 9);
  screenGlow.position.set(0, 3.4, 3.0);
  scene.add(screenGlow);

  /* helpers */
  const plastic = (color, roughness = 0.55, extra = {}) =>
    new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.0, ...extra });
  function rbox(parent, w, h, d, r, x, y, z, material) {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 4, r), material);
    m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true;
    parent.add(m); return m;
  }

  const MAT = {
    body: plastic(0xe6ddc9, 0.5), bodyDark: plastic(0xd3c8ad, 0.55),
    bezel: plastic(0xcfc3a6, 0.5), dark: plastic(0x35312a, 0.6),
    keyMain: plastic(0xede5d3, 0.42), keyMod: plastic(0xa29881, 0.45),
    keyFn: plastic(0xd9cfb8, 0.45), cable: plastic(0x49443a, 0.8),
  };

  const computer = new THREE.Group();
  scene.add(computer);

  /* monitor */
  const monitor = new THREE.Group();
  monitor.position.set(0, 3.12, -1.0);
  computer.add(monitor);
  rbox(monitor, 5.9, 4.3, 2.6, 0.14, 0, 0, -0.5, MAT.body);
  rbox(monitor, 5.1, 3.7, 1.5, 0.12, 0, -0.05, -2.1, MAT.bodyDark);
  rbox(monitor, 4.1, 2.9, 1.0, 0.10, 0, -0.1, -3.2, MAT.body);
  rbox(monitor, 6.0, 4.4, 0.5, 0.12, 0, 0, 0.85, MAT.bezel);
  for (let i = 0; i < 9; i++) rbox(monitor, 0.14, 0.05, 1.6, 0.02, -2.0 + i * 0.5, 2.16, -0.6, MAT.dark);
  for (let i = 0; i < 6; i++) rbox(monitor, 0.05, 1.8, 0.14, 0.02, 2.96, 0.4, -0.2 - i * 0.4, MAT.dark);

  /* CRT screen */
  const scrCanvas = document.createElement('canvas');
  scrCanvas.width = 160; scrCanvas.height = 120;
  const sctx = scrCanvas.getContext('2d');
  const scrTexture = new THREE.CanvasTexture(scrCanvas);
  scrTexture.magFilter = THREE.NearestFilter;
  scrTexture.colorSpace = THREE.SRGBColorSpace;
  const screenMat = new THREE.MeshStandardMaterial({
    map: scrTexture, emissive: 0xffffff, emissiveMap: scrTexture,
    emissiveIntensity: 0.9, roughness: 0.18, metalness: 0.0,
  });
  const screenMesh = new THREE.Mesh(new RoundedBoxGeometry(5.0, 3.3, 0.5, 5, 0.22), screenMat);
  screenMesh.scale.set(1, 1, 0.55);
  screenMesh.position.set(0, 0.42, 1.12);
  monitor.add(screenMesh);
  rbox(monitor, 5.3, 3.6, 0.12, 0.08, 0, 0.42, 1.08, MAT.dark);

  /* front controls */
  rbox(monitor, 1.8, 0.5, 0.12, 0.03, 1.35, -1.55, 1.12, MAT.dark);
  rbox(monitor, 1.4, 0.07, 0.06, 0.02, 1.28, -1.5, 1.19, plastic(0x11100e, 0.5));
  rbox(monitor, 0.28, 0.16, 0.08, 0.03, 1.95, -1.68, 1.18, MAT.bodyDark);
  const powerBtn = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.1, 24), MAT.bodyDark);
  powerBtn.rotation.x = Math.PI / 2; powerBtn.position.set(-2.35, -1.55, 1.14);
  powerBtn.castShadow = true; monitor.add(powerBtn);
  rbox(monitor, 0.12, 0.12, 0.06, 0.02, -1.85, -1.55, 1.12,
    new THREE.MeshStandardMaterial({ color: 0x0a2a15, emissive: 0x46ff8a, emissiveIntensity: 1.6, roughness: 0.3 }));
  rbox(monitor, 0.95, 0.3, 0.06, 0.03, -0.6, -1.55, 1.12, MAT.bodyDark);
  rbox(monitor, 2.3, 0.85, 1.7, 0.1, 0, -2.55, -0.3, MAT.bodyDark);
  rbox(monitor, 3.9, 0.34, 2.7, 0.12, 0, -2.95, -0.1, MAT.body);

  /* keyboard */
  const keyboard = new THREE.Group();
  keyboard.position.set(0, 0.3, 3.6);
  keyboard.rotation.x = -0.055;
  computer.add(keyboard);
  rbox(keyboard, 7.3, 0.5, 2.7, 0.14, 0, 0, 0, MAT.body);
  rbox(keyboard, 6.75, 0.06, 2.05, 0.03, 0, 0.26, 0.05, MAT.bodyDark);
  const KEY_W = 0.4, KEY_H = 0.24, PITCH = 0.47;
  const keyMeshes = [];
  const key = (x, z, w, m) => {
    const k = rbox(keyboard, w, KEY_H, KEY_W, 0.05, x, 0.35, z, m);
    keyMeshes.push({ m: k, y: 0.35 }); return k;
  };
  for (let r = 0; r < 4; r++) {
    const z = -0.72 + r * PITCH;
    for (let c = 0; c < 14; c++) {
      const x = -3.05 + c * PITCH;
      const isMod = c === 0 || c === 13;
      key(x, z, KEY_W, r === 0 ? (isMod ? MAT.keyMod : MAT.keyFn) : (isMod ? MAT.keyMod : MAT.keyMain));
    }
  }
  key(-2.9, 1.16, 0.62, MAT.keyMod); key(-2.25, 1.16, KEY_W, MAT.keyMod);
  key(-1.75, 1.16, KEY_W, MAT.keyMod); key(0.1, 1.16, 2.5, MAT.keyMain);
  key(1.85, 1.16, KEY_W, MAT.keyMod); key(2.35, 1.16, KEY_W, MAT.keyMod);
  key(2.95, 1.16, 0.62, MAT.keyMod);
  rbox(keyboard, 0.09, 0.05, 0.09, 0.02, 3.28, 0.32, -0.95,
    new THREE.MeshStandardMaterial({ color: 0x0a2a15, emissive: 0x46ff8a, emissiveIntensity: 1.4 }));

  /* mouse */
  const mouse = new THREE.Group();
  mouse.position.set(5.1, 0.24, 3.7);
  mouse.rotation.y = -0.45;
  computer.add(mouse);
  rbox(mouse, 1.05, 0.42, 1.55, 0.19, 0, 0, 0, MAT.body);
  rbox(mouse, 0.4, 0.08, 0.55, 0.03, -0.23, 0.21, -0.42, MAT.keyMod);
  rbox(mouse, 0.4, 0.08, 0.55, 0.03, 0.23, 0.21, -0.42, MAT.keyMod);

  /* cables (parented to computer so they float together) */
  function cable(points, radius = 0.05) {
    const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
    const m = new THREE.Mesh(new THREE.TubeGeometry(curve, 48, radius, 8), MAT.cable);
    m.castShadow = true; computer.add(m); return m;
  }
  cable([[2.6, 0.45, 2.35], [2.2, 0.2, 1.4], [1.4, 0.15, 0.6], [1.2, 0.4, -0.2]], 0.05);
  cable([[4.9, 0.35, 3.0], [4.3, 0.18, 2.1], [3.4, 0.15, 1.7], [3.2, 0.3, 2.4]], 0.04);
  cable([[-1.8, 1.6, -4.6], [-2.6, 0.8, -5.2], [-3.4, 0.1, -4.8], [-4.2, 0.06, -4.0]], 0.06);

  /* ground */
  const GROUND = { light: opts.groundLight ?? 0xe7e2d5, dark: opts.groundDark ?? 0x0c0c11 };
  const groundMat = new THREE.MeshStandardMaterial({ color: GROUND.light, roughness: 0.95, metalness: 0 });
  const ground = new THREE.Mesh(new THREE.CircleGeometry(40, 64), groundMat);
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
  scene.add(ground);

  /* boot sequence */
  const BOOT_LINES = opts.bootLines || ['PM-KB BIOS v1.0', 'READY.'];
  let lineIdx = 0, charIdx = 0, cursorOn = true, glitchTimer = 0;
  const typedLines = [];
  function drawScreen(t) {
    const W = scrCanvas.width, H = scrCanvas.height;
    sctx.fillStyle = '#05130b'; sctx.fillRect(0, 0, W, H);
    if (lineIdx < BOOT_LINES.length) {
      if (t % 3 === 0) {
        charIdx++;
        if (charIdx > BOOT_LINES[lineIdx].length) { typedLines.push(BOOT_LINES[lineIdx]); lineIdx++; charIdx = 0; }
      }
    } else if (t % 420 === 0) { lineIdx = 0; charIdx = 0; typedLines.length = 0; }
    if (t % 16 === 0) cursorOn = !cursorOn;
    glitchTimer = Math.random() < 0.012 ? 3 : Math.max(0, glitchTimer - 1);
    sctx.font = '8px "Press Start 2P", monospace';
    sctx.textBaseline = 'top';
    sctx.fillStyle = '#46ff8a'; sctx.shadowColor = '#46ff8a'; sctx.shadowBlur = 5;
    const gx = glitchTimer > 0 ? (Math.random() - 0.5) * 3 : 0;
    typedLines.forEach((line, i) => sctx.fillText(line, 7 + gx, 8 + i * 12));
    if (lineIdx < BOOT_LINES.length) {
      sctx.fillText(BOOT_LINES[lineIdx].slice(0, charIdx) + (cursorOn ? '█' : ''), 7 + gx, 8 + typedLines.length * 12);
    } else if (cursorOn) {
      sctx.fillText('█', 7 + gx, 8 + typedLines.length * 12);
    }
    sctx.shadowBlur = 0;
    sctx.fillStyle = 'rgba(0,0,0,0.22)';
    for (let y = 0; y < H; y += 3) sctx.fillRect(0, y, W, 1);
    const grad = sctx.createRadialGradient(W / 2, H / 2, H * 0.32, W / 2, H / 2, H * 0.78);
    grad.addColorStop(0, 'rgba(0,0,0,0)'); grad.addColorStop(1, 'rgba(0,0,0,0.5)');
    sctx.fillStyle = grad; sctx.fillRect(0, 0, W, H);
    scrTexture.needsUpdate = true;
  }

  /* sizing */
  function resize() {
    const w = host.clientWidth, h = host.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    const a = w / h;
    camera.aspect = a;
    camera.fov = a < 0.9 ? 62 : a < 1.3 ? 52 : a < 1.7 ? 44 : 40;
    camera.updateProjectionMatrix();
  }
  resize();
  if (window.ResizeObserver) new ResizeObserver(resize).observe(host);
  window.addEventListener('resize', resize);

  /* theme */
  function setTheme(isDark) {
    const bg = isDark ? BG.dark : BG.light;
    scene.background.setHex(bg); scene.fog.color.setHex(bg);
    groundMat.color.setHex(isDark ? GROUND.dark : GROUND.light);
    keyLight.intensity = isDark ? 1.1 : 2.2;
    fillLight.intensity = isDark ? 1.0 : 0.6;
    screenGlow.intensity = isDark ? 2.2 : 0.5;
    renderer.toneMappingExposure = isDark ? 1.15 : 1.0;
  }

  /* interaction: pause autorotate on drag */
  let resumeTimer;
  renderer.domElement.addEventListener('pointerdown', () => {
    controls.autoRotate = false;
    clearTimeout(resumeTimer);
    resumeTimer = setTimeout(() => { controls.autoRotate = true; }, 4000);
  });

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced) controls.autoRotate = false;

  let visible = true;
  if (window.IntersectionObserver) {
    new IntersectionObserver(es => { visible = es[0].isIntersecting; }, { threshold: 0 }).observe(canvas);
  }

  let frame = 0;
  function animate() {
    requestAnimationFrame(animate);
    if (!visible || document.hidden) return;
    frame++;
    drawScreen(frame);
    if (!reduced) computer.position.y = Math.sin(frame * 0.008) * 0.04;
    // idle keypress twinkle
    if (!reduced && frame % 37 === 0) {
      const k = keyMeshes[(Math.random() * keyMeshes.length) | 0];
      k.m.position.y = k.y - 0.05;
      setTimeout(() => { k.m.position.y = k.y; }, 110);
    }
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  return { setTheme, controls };
}

window.RETRO = { init: initRetro };
