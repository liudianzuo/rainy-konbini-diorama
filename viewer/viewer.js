/* Rainy Night Konbini — interactive miniature diorama */
(function () {
  'use strict';

  const canvasHost = document.getElementById('stage');
  const viewport = window.visualViewport || null;
  const W = () => Math.round(viewport ? viewport.width : window.innerWidth);
  const H = () => Math.round(viewport ? viewport.height : window.innerHeight);

  // Phones / tablets: fewer particles, lower internal resolution, gentler bloom.
  const isTouch = (navigator.maxTouchPoints || 0) > 0 ||
    (window.matchMedia && window.matchMedia('(hover: none) and (pointer: coarse)').matches);
  const smallScreen = () => Math.min(W(), H()) < 700;
  const deviceCap = isTouch || smallScreen() ? 1.5 : 1.75;
  let dprCap = deviceCap;

  const renderer = new THREE.WebGLRenderer({
    antialias: !isTouch,
    alpha: false,
    powerPreference: 'high-performance'
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, dprCap));
  renderer.setSize(W(), H(), false);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.setClearColor(0x070f1d, 1);
  renderer.domElement.id = 'konbini-canvas';
  canvasHost.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x07101e);
  scene.fog = new THREE.FogExp2(0x081525, 0.0085);

  const camera = new THREE.PerspectiveCamera(36.2, W() / H(), 0.1, 260);
  camera.position.set(-26.3, 18.4, 32.8);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.target.set(-0.4, 2.2, 0.0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.055;
  controls.enablePan = true;
  controls.screenSpacePanning = true;
  controls.minDistance = 20;
  controls.maxDistance = 105;
  controls.minPolarAngle = 0.12;
  controls.maxPolarAngle = 1.52;
  controls.autoRotate = false;
  controls.autoRotateSpeed = 0.34;
  controls.rotateSpeed = isTouch ? 0.85 : 1.0;
  controls.zoomSpeed = isTouch ? 0.9 : 1.0;
  controls.panSpeed = isTouch ? 0.85 : 1.0;
  controls.update();

  // ------------------------------------------------------- responsive framing
  // The diorama is a fixed-size square block (the plinth is 26.3 x 26.3). Seen
  // from the default three-quarter angle its footprint is ~37 units wide, far
  // wider than a phone's horizontal field, so the camera must back off until
  // all four base corners fit. A fixed "scene radius" cannot express that,
  // so solve the perspective fit for the eight plinth corners instead.
  const LANDSCAPE_FOV = 36.2;
  const PORTRAIT_FOV = 50.0;
  const BASE_HALF = 13.15;
  const BASE_BOTTOM = -1.36;
  const BASE_DIR = new THREE.Vector3(-25.9, 16.2, 32.8).normalize();
  const SAFE = 0.93; // every corner stays inside 93% of the half-frame
  const camRight = new THREE.Vector3(BASE_DIR.z, 0, -BASE_DIR.x).normalize();
  const camUp = new THREE.Vector3().crossVectors(camRight, BASE_DIR.clone().negate()).normalize();
  let currentDistance = camera.position.distanceTo(controls.target);

  function frameDistance() {
    const aspect = W() / H();
    const portrait = aspect < 0.85;
    const fov = portrait ? PORTRAIT_FOV : LANDSCAPE_FOV;
    const vTan = Math.tan(THREE.MathUtils.degToRad(fov / 2));
    const hTan = vTan * aspect;

    // Camera sits at target + BASE_DIR * d, so a corner p (relative to the
    // target) is seen at depth d - p·BASE_DIR. The corner stays on screen when
    //   |p·right| <= SAFE * hTan * depth   and   |p·up| <= SAFE * vTan * depth.
    // Solve both inequalities for d and keep the largest requirement.
    let distance = 0;
    for (let i = 0; i < 8; i++) {
      const p = new THREE.Vector3(
        (i & 1) ? BASE_HALF : -BASE_HALF,
        (i & 2) ? 0 : BASE_BOTTOM,
        (i & 4) ? BASE_HALF : -BASE_HALF
      ).sub(controls.target);
      const depthOffset = p.dot(BASE_DIR);
      distance = Math.max(
        distance,
        Math.abs(p.dot(camRight)) / (SAFE * hTan) + depthOffset,
        Math.abs(p.dot(camUp)) / (SAFE * vTan) + depthOffset
      );
    }
    return { fov: fov, portrait: portrait, distance: distance };
  }

  function applyFraming(forceDistance) {
    const fit = frameDistance();
    camera.fov = fit.fov;
    camera.aspect = W() / H();
    camera.updateProjectionMatrix();
    controls.minDistance = fit.distance * 0.45;
    controls.maxDistance = fit.distance * 2.4;
    if (forceDistance) {
      currentDistance = fit.distance;
      camera.position.copy(controls.target).addScaledVector(BASE_DIR, currentDistance);
    }
    controls.update();
  }

  applyFraming(true);

  // Stop the lazy orbit the moment the visitor takes over.
  let touched = false;
  controls.addEventListener('start', function () {
    touched = true;
    controls.autoRotate = false;
  });
  controls.addEventListener('end', function () {
    // no UI, just let the view stay where the visitor put it
  });

  // ------------------------------------------------------------ sky dome
  const sky = new THREE.Mesh(
    new THREE.SphereGeometry(180, 40, 22),
    new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {
        topColor: { value: new THREE.Color(0x0b1d36).convertSRGBToLinear() },
        bottomColor: { value: new THREE.Color(0x030912).convertSRGBToLinear() },
        offset: { value: 20.0 },
        exponent: { value: 0.58 }
      },
      vertexShader: [
        'varying vec3 vWorldPosition;',
        'void main(){',
        '  vec4 wp = modelMatrix * vec4(position, 1.0);',
        '  vWorldPosition = wp.xyz;',
        '  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);',
        '}'
      ].join('\n'),
      fragmentShader: [
        'uniform vec3 topColor;',
        'uniform vec3 bottomColor;',
        'uniform float offset;',
        'uniform float exponent;',
        'varying vec3 vWorldPosition;',
        'void main(){',
        '  float h = normalize(vWorldPosition + vec3(0.0, offset, 0.0)).y;',
        '  float t = max(pow(max(h, 0.0), exponent), 0.0);',
        '  gl_FragColor = vec4(mix(bottomColor, topColor, t), 1.0);',
        '}'
      ].join('\n')
    })
  );
  sky.renderOrder = -10;
  scene.add(sky);

  // ------------------------------------------------------------ lights
  scene.add(new THREE.HemisphereLight(0x6f9bdb, 0x080d16, 0.38));
  scene.add(new THREE.AmbientLight(0x2b4568, 0.14));

  const moon = new THREE.DirectionalLight(0xa8c4ff, 1.10);
  moon.position.set(18, 34, 20);
  scene.add(moon);

  const fill = new THREE.DirectionalLight(0xffb368, 0.30);
  fill.position.set(-16, 13, 22);
  scene.add(fill);

  const rim = new THREE.DirectionalLight(0x5e86ff, 0.24);
  rim.position.set(-24, 8, -24);
  scene.add(rim);

  function warmPoint(x, y, z, color, intensity, distance) {
    const p = new THREE.PointLight(color, intensity, distance, 2);
    p.position.set(x, y, z);
    scene.add(p);
    return p;
  }

  // converted to three.js' Y-up coordinates: (x, z, -y)
  warmPoint(-4.6, 2.55, 0.8, 0xffa85a, 3.5, 10.0);   // storefront
  warmPoint(-6.2, 2.6, -1.2, 0xff9b48, 3.7, 8.0);
  warmPoint(-2.2, 2.6, -1.8, 0xffb45c, 3.9, 8.0);
  warmPoint(-4.8, 2.6, -4.6, 0xff9b48, 2.9, 7.5);
  warmPoint(0.2, 2.6, 0.1, 0xffbd7a, 2.0, 5.5);
  warmPoint(-3.5, 2.25, -2.4, 0xff9a43, 4.6, 9.0);   // interior wash
  warmPoint(-2.8, 5.5, 1.5, 0xffa75a, 0.95, 5.0);    // upstairs window
  warmPoint(3.8, 1.35, 3.9, 0x8fd8ff, 1.20, 4.6);    // vending machines
  warmPoint(5.36, 5.0, 4.85, 0xffb260, 3.8, 16.0);   // street lamp
  warmPoint(-11.9, 4.0, 5.0, 0xb8dcff, 1.20, 8.0);   // utility pole lamp
  warmPoint(-12.5, 3.0, 2.0, 0xff2d7d, 1.10, 5.5);   // snack neon
  warmPoint(-9.7, 2.5, 1.9, 0xff8235, 0.75, 4.0);    // alley lantern

  // ------------------------------------------------------------ materials
  const gradientMap = (function makeGradient() {
    const c = document.createElement('canvas');
    c.width = 4; c.height = 1;
    const ctx = c.getContext('2d');
    const steps = [28, 88, 166, 255];
    for (let i = 0; i < 4; i++) {
      ctx.fillStyle = 'rgb(' + steps[i] + ',' + steps[i] + ',' + steps[i] + ')';
      ctx.fillRect(i, 0, 1, 1);
    }
    const t = new THREE.CanvasTexture(c);
    t.minFilter = THREE.NearestFilter;
    t.magFilter = THREE.NearestFilter;
    t.generateMipmaps = false;
    t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
    return t;
  })();

  const glassNames = /Glass|glass/;
  const emissiveNames = /(Sign|Neon|Lamp|Light|Lightbox|Reflect|Headlight|Screen|Bulb|Lantern|Curtain|Window|Sensor|UnlitWhite|UnlitCream|UnlitGreen)/;
  const unlitNames = /Unlit/;
  const materialCache = new Map();
  const interiorMaterialCache = new Map();
  const interiorRegex = /^(Interior|Ceil|FloorSeam|Fridge|Bottle|Gondola|ProductG|PriceG|Endcap|Magazine|MagRack|Snack|Counter|Register|CardReader|Receipt|HotCase|Sausage|Coffee|Cigarette|CigPack|CigRack|HangingSign|HangingText|CupStack|Napkin|Donation|InnerMat|InnerPot|InnerPlant|Basket|Promo|FloorArrow|AisleBanner|BackWallIn|BackOffice|BackPoster|BackBrand|PosterWall|WindowPoster|ATM|GlassDecal)/;

  function emissiveGain(name) {
    if (/Neon/.test(name)) return 2.7;
    if (/SignWhite$/.test(name)) return 1.55;
    if (/SignWhiteSoft/.test(name)) return 1.42;
    if (/WarmLight|CoolLight|FridgeLight/.test(name)) return 1.60;
    if (/LampGlass/.test(name)) return 2.3;
    if (/Reflect/.test(name)) return 2.3;
    if (/Curtain|Window/.test(name)) return 1.05;
    if (/Unlit/.test(name)) return 1.0;
    if (/Screen/.test(name)) return 1.25;
    if (/Bulb|Lantern/.test(name)) return 1.7;
    return 1.0;
  }

  const colorOverrides = {
    BaseSide: 0x050d18,
    BaseTop: 0x070e16,
    WetAsphalt: 0x07131d,
    WetAsphalt2: 0x0b1a26,
    NeighborFacade: 0x070a0e,
    NeighborFacade2: 0x0d1014,
    NeighborDark: 0x06090d,
    NeighborWall: 0x1c2024,
    NeighborWall2: 0x24282c,
    Concrete: 0x4e5353,
    ConcreteDark: 0x1d2225,
    CurbStone: 0x9a9f9d,
    Sidewalk: 0x778083,
    SidewalkDark: 0x535b5d,
    StoreWall: 0x9c8f78,
    StoreWallWarm: 0xa99a7d,
    CeilingPanel: 0x827d70,
    InteriorWall: 0x746a56,
    InteriorFloor: 0x554b3a,
    ShelfWhite: 0x9e9d95
  };

  function convertMaterial(src) {
    if (!src) return src;
    if (materialCache.has(src.uuid)) return materialCache.get(src.uuid);
    const name = src.name || '';
    const color = src.color ? src.color.clone() : new THREE.Color(0xffffff);
    const doubleSide = src.side === THREE.DoubleSide;
    let out;

    if (glassNames.test(name) || (src.transparent && src.opacity < 0.4 && !/Rain/.test(name))) {
      out = new THREE.MeshBasicMaterial({
        color: new THREE.Color(0x6e9ab6),
        transparent: true,
        opacity: Math.max(0.075, Math.min(0.19, (src.opacity || 0.1) * 1.25)),
        depthWrite: false,
        side: THREE.DoubleSide,
        toneMapped: false
      });
      out.name = name;
      out.userData.isGlass = true;
    } else if (unlitNames.test(name)) {
      const c = new THREE.Color(0, 0, 0);
      if (src.emissive && src.emissive.getHex() !== 0) c.copy(src.emissive);
      else c.copy(color);
      out = new THREE.MeshBasicMaterial({ color: c, side: doubleSide ? THREE.DoubleSide : THREE.FrontSide, toneMapped: false });
      out.name = name;
      out.userData.isUnlit = true;
    } else if (emissiveNames.test(name)) {
      let c = (src.emissive && src.emissive.getHex() !== 0) ? src.emissive.clone() : color.clone();
      if (name === 'WarmCurtain') {
        c = new THREE.Color(0xffa33e).convertSRGBToLinear().multiplyScalar(1.55);
      } else if (name === 'CoolWindow') {
        c = new THREE.Color(0x5f9dff).convertSRGBToLinear().multiplyScalar(1.2);
      } else {
        c.multiplyScalar(emissiveGain(name));
      }
      out = new THREE.MeshBasicMaterial({
        color: c,
        side: doubleSide ? THREE.DoubleSide : THREE.FrontSide,
        transparent: src.opacity < 1,
        opacity: src.opacity,
        toneMapped: false,
        fog: true
      });
      out.name = name;
      out.userData.isEmissive = true;
    } else if (/Puddle/.test(name)) {
      out = new THREE.MeshBasicMaterial({
        color: new THREE.Color(0x06131d),
        transparent: true,
        opacity: 0.58,
        side: THREE.DoubleSide,
        toneMapped: false
      });
      out.name = name;
    } else {
      let em = (src.emissive && src.emissive.getHex() !== 0) ? src.emissive.clone() : new THREE.Color(0x000000);
      let emIntensity = (em.r + em.g + em.b) > 0.02 ? 1.1 : 0.0;
      if (/Interior|Shelf|Ceiling|PriceTag/.test(name)) {
        em = new THREE.Color(0xffa04a).convertSRGBToLinear();
        emIntensity = /Shelf|Ceiling/.test(name) ? 0.10 : 0.065;
      }
      let tint;
      if (colorOverrides[name] !== undefined) {
        tint = new THREE.Color(colorOverrides[name]).convertSRGBToLinear();
      } else {
        tint = color.clone().multiplyScalar(0.90);
      }
      out = new THREE.MeshToonMaterial({
        color: tint,
        gradientMap: gradientMap,
        emissive: em,
        emissiveIntensity: emIntensity,
        side: doubleSide ? THREE.DoubleSide : THREE.FrontSide
      });
      out.name = name;
    }
    materialCache.set(src.uuid, out);
    return out;
  }

  function convertInteriorMaterial(src) {
    if (!src) return src;
    if (interiorMaterialCache.has(src.uuid)) return interiorMaterialCache.get(src.uuid);
    const name = src.name || '';
    if (glassNames.test(name) || unlitNames.test(name) || emissiveNames.test(name) || src.transparent) {
      const m = convertMaterial(src);
      interiorMaterialCache.set(src.uuid, m);
      return m;
    }
    const c = src.color ? src.color.clone() : new THREE.Color(0xffffff);
    c.multiplyScalar(1.16);
    const out = new THREE.MeshBasicMaterial({
      color: c,
      side: src.side === THREE.DoubleSide ? THREE.DoubleSide : THREE.FrontSide,
      toneMapped: false,
      fog: true
    });
    out.name = name;
    interiorMaterialCache.set(src.uuid, out);
    return out;
  }

  // ------------------------------------------------------------ model
  let model = null;
  let items = [];
  let clock = new THREE.Clock();
  let startTime = 0;
  let buildEnd = 0;
  let loaded = false;

  // Windows: give the flat emissive curtain planes a soft radial falloff (in
  // world space) so the room light reads as light coming through fabric and
  // glass, instead of a painted panel. Cloned per window so each pane gets its
  // own centre/radius.
  function windowGlowMaterial(mesh) {
    mesh.updateWorldMatrix(true, false);
    if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    const box = mesh.geometry.boundingBox.clone().applyMatrix4(mesh.matrixWorld);
    const center = box.getCenter(new THREE.Vector3());
    const radius = Math.max(0.05, box.getSize(new THREE.Vector3()).length() * 0.5);
    const mat = mesh.material.clone();
    mat.onBeforeCompile = function (shader) {
      shader.uniforms.uWinCenter = { value: center };
      shader.uniforms.uWinRadius = { value: radius };
      shader.vertexShader = 'varying vec3 vWinWorld;\n' + shader.vertexShader.replace(
        '#include <begin_vertex>',
        '#include <begin_vertex>\n  vWinWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;'
      );
      shader.fragmentShader = [
        'uniform vec3 uWinCenter;',
        'uniform float uWinRadius;',
        'varying vec3 vWinWorld;',
        shader.fragmentShader.replace(
          '#include <fog_fragment>',
          'float winD = length(vWinWorld - uWinCenter) / uWinRadius;\n' +
          'float winGlow = smoothstep(1.12, 0.05, winD);\n' +
          'gl_FragColor.rgb *= 0.42 + 0.78 * winGlow;\n' +
          '#include <fog_fragment>'
        )
      ].join('\n');
    };
    return mat;
  }

  function decodeBase64(b64) {
    const bin = atob(b64);
    const len = bin.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    return bytes.buffer;
  }

  function onModelReady(gltf) {
    model = gltf.scene;
    model.updateMatrixWorld(true);
    const outlineCandidates = [];

    model.traverse(function (o) {
      if (!o.isMesh) return;
      if (!interiorRegex.test(o.name)) outlineCandidates.push(o);
      o.material = interiorRegex.test(o.name) ? convertInteriorMaterial(o.material) : convertMaterial(o.material);
      // Window light: add a soft falloff to curtain / window glow materials.
      if (o.material && o.material.userData && o.material.userData.isEmissive &&
          /Curtain|Window/.test(o.material.name || '')) {
        o.material = windowGlowMaterial(o);
      }
      o.frustumCulled = true;
      o.castShadow = false;
      o.receiveShadow = false;

      const ud = o.userData || {};
      const t0 = (typeof ud.asm_t0 === 'number') ? ud.asm_t0 : 0.0;
      const t1 = (typeof ud.asm_t1 === 'number') ? ud.asm_t1 : t0 + 0.5;
      const mode = ud.asm_mode || 'pop';
      const drop = (typeof ud.asm_drop === 'number') ? ud.asm_drop : 0.55;

      if (o.geometry && !o.geometry.boundingBox) o.geometry.computeBoundingBox();
      const bb = o.geometry ? o.geometry.boundingBox : null;
      const minY = bb ? bb.min.y : 0;
      const finalPos = o.position.clone();
      const finalScale = o.scale.clone();

      o.visible = false;
      items.push({
        o: o, t0: t0, t1: Math.max(t0 + 0.12, t1), mode: mode, drop: drop,
        finalPos: finalPos, finalScale: finalScale, minY: minY,
        phase: Math.random() * Math.PI * 2
      });
    });

    // A light ink outline on the largest silhouettes makes the toon shading
    // read as a hand-drawn miniature without doubling every tiny prop.
    const outlineMat = new THREE.MeshBasicMaterial({
      color: 0x060d16, side: THREE.BackSide, fog: true, toneMapped: false
    });
    outlineCandidates.sort(function (a, b) {
      if (!a.geometry.boundingSphere) a.geometry.computeBoundingSphere();
      if (!b.geometry.boundingSphere) b.geometry.computeBoundingSphere();
      return b.geometry.boundingSphere.radius - a.geometry.boundingSphere.radius;
    });
    for (let i = 0; i < Math.min(210, outlineCandidates.length); i++) {
      const o = outlineCandidates[i];
      if (!o.geometry || !o.geometry.boundingSphere) continue;
      if (o.material && o.material.userData && (o.material.userData.isGlass || o.material.userData.isEmissive)) continue;
      const r = o.geometry.boundingSphere.radius;
      if (r < 0.18) continue;
      const shell = new THREE.Mesh(o.geometry, outlineMat);
      const s = Math.min(1.024, Math.max(1.0015, 1 + 0.012 / Math.max(0.22, r)));
      shell.scale.setScalar(s);
      shell.renderOrder = -1;
      o.add(shell);
    }

    scene.add(model);
    loaded = true;
    clock.start();
    startTime = clock.getElapsedTime();
    renderer.domElement.classList.add('ready');

    // real-time rain, started only after the shell has mostly assembled
    createRain();
    buildEnd = 10.7;
    // Start the frame-rate probe now: decoding the embedded GLB blocks the
    // main thread, and counting that stall would drop the render scale on
    // phones that are perfectly capable.
    frames = 0;
    qualityCheckedAt = performance.now() + 6000;
    console.log('Rainy konbini loaded:', items.length, 'parts');
  }

  function onModelError(err) {
    console.error('Failed to load konbini:', err);
  }

  try {
    const glb = decodeBase64(window.__GLB_B64);
    const loader = new THREE.GLTFLoader();
    loader.parse(glb, '', onModelReady, onModelError);
  } catch (e) {
    console.error(e);
  }

  // ------------------------------------------------------------ rain
  let rain = null, rainPositions = null, rainSpeeds = null;
  const RAIN_COUNT = isTouch ? 850 : 1450;
  const RAIN_TOP = 25;
  const RAIN_RADIUS = 22;

  function createRain() {
    rainPositions = new Float32Array(RAIN_COUNT * 6);
    rainSpeeds = new Float32Array(RAIN_COUNT);
    for (let i = 0; i < RAIN_COUNT; i++) {
      const x = (Math.random() * 2 - 1) * RAIN_RADIUS;
      const y = Math.random() * RAIN_TOP;
      const z = (Math.random() * 2 - 1) * RAIN_RADIUS;
      const len = 0.35 + Math.random() * 0.55;
      rainPositions[i * 6 + 0] = x;
      rainPositions[i * 6 + 1] = y;
      rainPositions[i * 6 + 2] = z;
      rainPositions[i * 6 + 3] = x + 0.07;
      rainPositions[i * 6 + 4] = y - len;
      rainPositions[i * 6 + 5] = z + 0.02;
      rainSpeeds[i] = 7.5 + Math.random() * 5.5;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(rainPositions, 3));
    const mat = new THREE.LineBasicMaterial({
      color: 0xb7dcff, transparent: true, opacity: 0.34,
      depthWrite: false, blending: THREE.NormalBlending, fog: true
    });
    rain = new THREE.LineSegments(geo, mat);
    rain.frustumCulled = false;
    rain.visible = false;
    scene.add(rain);
  }

  function updateRain(dt, elapsed) {
    if (!rain || !rain.visible || !rainPositions) return;
    for (let i = 0; i < RAIN_COUNT; i++) {
      const base = i * 6;
      const fall = rainSpeeds[i] * dt;
      rainPositions[base + 1] -= fall;
      rainPositions[base + 4] -= fall;
      if (rainPositions[base + 1] < -0.8) {
        const x = (Math.random() * 2 - 1) * RAIN_RADIUS;
        const z = (Math.random() * 2 - 1) * RAIN_RADIUS;
        const len = 0.35 + Math.random() * 0.55;
        rainPositions[base + 0] = x;
        rainPositions[base + 1] = RAIN_TOP;
        rainPositions[base + 2] = z;
        rainPositions[base + 3] = x + 0.07;
        rainPositions[base + 4] = RAIN_TOP - len;
        rainPositions[base + 5] = z + 0.02;
      }
    }
    rain.geometry.attributes.position.needsUpdate = true;
    rain.material.opacity = 0.24 + 0.13 * Math.min(1, Math.max(0, (elapsed - 8.0) / 2.0));
  }

  // ------------------------------------------------------------ assembly
  const easeOutCubic = function (x) { return 1 - Math.pow(1 - x, 3); };
  const easeInOut = function (x) { return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; };

  function updateAssembly(elapsed) {
    if (!loaded) return;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      const o = it.o;
      let t = elapsed - 0.7;
      if (t < it.t0) {
        if (o.visible) o.visible = false;
        continue;
      }
      o.visible = true;
      const span = Math.max(0.12, it.t1 - it.t0);
      let p = Math.min(1, (t - it.t0) / span);
      if (p >= 1) {
        o.position.copy(it.finalPos);
        o.scale.copy(it.finalScale);
        continue;
      }
      const e = easeOutCubic(p);
      if (it.mode === 'grow') {
        const sy = Math.max(0.002, e);
        const sxz = 0.975 + 0.025 * e;
        o.scale.set(it.finalScale.x * sxz, it.finalScale.y * sy, it.finalScale.z * sxz);
        o.position.x = it.finalPos.x;
        o.position.z = it.finalPos.z;
        o.position.y = it.finalPos.y + it.minY * (1 - sy);
      } else if (it.mode === 'slide') {
        const s = Math.max(0.002, e);
        o.scale.set(it.finalScale.x * s, it.finalScale.y * s, it.finalScale.z * s);
        o.position.x = it.finalPos.x + (1 - e) * 0.30;
        o.position.y = it.finalPos.y;
        o.position.z = it.finalPos.z;
      } else {
        // pop with a small spring overshoot
        const spring = 1 + Math.sin(Math.min(1, p * 1.05) * Math.PI) * 0.055;
        const s = Math.max(0.002, e * spring);
        o.scale.set(it.finalScale.x * s, it.finalScale.y * s, it.finalScale.z * s);
        o.position.x = it.finalPos.x;
        o.position.y = it.finalPos.y + it.drop * (1 - e);
        o.position.z = it.finalPos.z;
      }
    }
    if (rain && !rain.visible && elapsed > 8.4) rain.visible = true;
  }

  // ------------------------------------------------------------ post
  let composer = null;
  let bloomPass = null;
  try {
    composer = new THREE.EffectComposer(renderer);
    composer.setPixelRatio(Math.min(window.devicePixelRatio || 1, isTouch ? 1.0 : 1.4));
    composer.addPass(new THREE.RenderPass(scene, camera));
    bloomPass = new THREE.UnrealBloomPass(
      new THREE.Vector2(W(), H()), 0.46, 0.58, 1.02
    );
    composer.addPass(bloomPass);
  } catch (e) {
    console.warn('Post-processing unavailable, using direct render.', e);
    composer = null;
  }

  // ------------------------------------------------------------ loop
  let last = performance.now();
  function animate(now) {
    requestAnimationFrame(animate);
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    const elapsed = clock.getElapsedTime();
    updateAssembly(elapsed);
    updateRain(dt, elapsed);
    if (!touched && elapsed > 10.6) controls.autoRotate = true;
    controls.update();
    sky.position.copy(camera.position);
    if (composer) composer.render();
    else renderer.render(scene, camera);
    watchPerformance(now);
  }
  requestAnimationFrame(animate);

  // ------------------------------------------------------- sizing / gestures
  let wasPortrait = (W() / H()) < 0.85;
  function resize() {
    const fit = frameDistance();
    camera.fov = fit.fov;
    camera.aspect = W() / H();
    camera.updateProjectionMatrix();
    renderer.setSize(W(), H(), false);
    if (composer) composer.setSize(W(), H());
    controls.minDistance = fit.distance * 0.45;
    controls.maxDistance = fit.distance * 2.4;
    // Re-fit when the device rotates between portrait and landscape, or when
    // the visitor has not orbited yet. Otherwise keep their chosen framing.
    if (!touched || fit.portrait !== wasPortrait) {
      const dir = camera.position.clone().sub(controls.target).normalize();
      if (dir.lengthSq() < 1e-6) dir.copy(BASE_DIR);
      camera.position.copy(controls.target).addScaledVector(dir, fit.distance);
      currentDistance = fit.distance;
    }
    wasPortrait = fit.portrait;
    controls.update();
  }

  let resizeQueued = false;
  function queueResize() {
    if (resizeQueued) return;
    resizeQueued = true;
    requestAnimationFrame(function () {
      resizeQueued = false;
      resize();
    });
  }

  window.addEventListener('resize', queueResize);
  window.addEventListener('orientationchange', function () {
    setTimeout(queueResize, 260);
  });
  if (viewport) {
    viewport.addEventListener('resize', queueResize);
    viewport.addEventListener('scroll', queueResize);
  }

  // Mobile browsers: no long-press menu, no double-tap page zoom.
  renderer.domElement.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  let lastTap = 0;
  renderer.domElement.addEventListener('touchend', function (e) {
    const now = Date.now();
    if (now - lastTap < 300) e.preventDefault();
    lastTap = now;
  }, { passive: false });
  document.addEventListener('gesturestart', function (e) { e.preventDefault(); });
  document.addEventListener('dblclick', function (e) { e.preventDefault(); });

  // Low-end phones: drop internal resolution once if the frame rate sags.
  let frames = 0;
  let slowWindows = 0;
  let qualityCheckedAt = performance.now() + 6000;
  function watchPerformance(now) {
    frames++;
    if (now < qualityCheckedAt) return;
    const fps = frames / ((now - (qualityCheckedAt - 6000)) / 1000);
    frames = 0;
    qualityCheckedAt = now;
    if (fps < 40 && dprCap > 1.0) {
      dprCap = 1.0;
      renderer.setPixelRatio(1);
      renderer.setSize(W(), H(), false);
      if (composer) composer.setPixelRatio(1);
      console.log('Konbini: lowered render scale for smoother playback (' + fps.toFixed(1) + ' fps)');
      return;
    }
    if (fps < 30 && bloomPass) {
      slowWindows++;
      if (slowWindows >= 2 && bloomPass.enabled) {
        bloomPass.enabled = false;
        console.log('Konbini: disabled bloom for smoother playback');
      }
    }
  }

  // Optional debug hook (not exposed as UI).
  window.__KONBINI__ = { scene: scene, camera: camera, controls: controls, renderer: renderer, composer: composer };

  // A quiet detail: the vending-machine / neon glow breathes very slightly.
  // It is done on the actual point lights so it reads in the model, not as UI.
  const moodLights = [];
  scene.traverse(function (o) {
    if (o.isPointLight) moodLights.push({ light: o, base: o.intensity, phase: Math.random() * 6.28 });
  });
  setInterval(function () {
    const t = clock.getElapsedTime();
    for (let i = 0; i < moodLights.length; i++) {
      const m = moodLights[i];
      m.light.intensity = m.base * (0.985 + Math.sin(t * 1.3 + m.phase) * 0.015);
    }
  }, 90);

})();
