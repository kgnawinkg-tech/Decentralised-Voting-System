/**
 * cinematic_experience.js
 * 
 * Orchestrates the full-screen cinematic 3D WebGL experience,
 * scroll-driven transformations, pointer-responsive parallax,
 * and seamless interactive connections with the Decentralized Voting backend.
 */

(function () {
  'use strict';

  // Check WebGL availability
  function hasWebGL() {
    try {
      const canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  const canvas = document.getElementById('cinematic-canvas');
  if (!canvas || !window.THREE || !hasWebGL()) {
    console.warn('WebGL/Three.js not available, falling back to CSS 3D presentation.');
    document.body.classList.add('no-webgl');
    return;
  }

  // --- THREE.JS SCENE SETUP ---
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0a0f1d, 0.04);

  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 4.0, 7.5);

  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance'
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // --- LIGHTING ---
  const ambientLight = new THREE.AmbientLight(0x0f172a, 1.2);
  scene.add(ambientLight);

  const keySpot = new THREE.SpotLight(0x38bdf8, 3.5, 30, Math.PI / 4, 0.3, 1.0);
  keySpot.position.set(3, 8, 5);
  keySpot.castShadow = true;
  keySpot.shadow.mapSize.width = 1024;
  keySpot.shadow.mapSize.height = 1024;
  scene.add(keySpot);

  const fillSpot = new THREE.SpotLight(0x818cf8, 2.0, 25, Math.PI / 3, 0.5, 1.0);
  fillSpot.position.set(-4, 5, 4);
  scene.add(fillSpot);

  const rimLight = new THREE.PointLight(0x10b981, 1.8, 15);
  rimLight.position.set(0, -1, -3);
  scene.add(rimLight);

  // --- STUDIO FLOOR GRID ---
  const gridHelper = new THREE.GridHelper(30, 30, 0x38bdf8, 0x1e293b);
  gridHelper.position.y = -1.8;
  scene.add(gridHelper);

  // Reflective stage platform
  const stageGeo = new THREE.CylinderGeometry(4.8, 5.2, 0.3, 48);
  const stageMat = new THREE.MeshStandardMaterial({
    color: 0x0f172a,
    roughness: 0.3,
    metalness: 0.8,
  });
  const stageMesh = new THREE.Mesh(stageGeo, stageMat);
  stageMesh.position.y = -1.95;
  stageMesh.receiveShadow = true;
  scene.add(stageMesh);

  // Glowing platform edge ring
  const ringGeo = new THREE.TorusGeometry(4.85, 0.04, 16, 64);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
  const ringMesh = new THREE.Mesh(ringGeo, ringMat);
  ringMesh.rotation.x = Math.PI / 2;
  ringMesh.position.y = -1.8;
  scene.add(ringMesh);

  // --- FLOATING DUST PARTICLES ---
  const particleCount = 280;
  const particleGeo = new THREE.BufferGeometry();
  const particlePos = new Float32Array(particleCount * 3);
  for (let i = 0; i < particleCount * 3; i += 3) {
    particlePos[i] = (Math.random() - 0.5) * 18;
    particlePos[i + 1] = (Math.random() - 0.5) * 12;
    particlePos[i + 2] = (Math.random() - 0.5) * 14;
  }
  particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePos, 3));
  const particleMat = new THREE.PointsMaterial({
    color: 0x38bdf8,
    size: 0.04,
    transparent: true,
    opacity: 0.6,
  });
  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  // ==========================================
  // 1. THE 3D EVM ASSEMBLY (THE MAIN CENTERPIECE)
  // ==========================================
  const evmGroup = new THREE.Group();
  scene.add(evmGroup);

  // Main EVM Chassis (Polymer graphite body with beveled edges)
  const chassisGeo = new THREE.BoxGeometry(4.2, 0.35, 5.8);
  const chassisMat = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    roughness: 0.45,
    metalness: 0.25,
  });
  const chassis = new THREE.Mesh(chassisGeo, chassisMat);
  chassis.castShadow = true;
  chassis.receiveShadow = true;
  evmGroup.add(chassis);

  // Outer bezel border
  const borderGeo = new THREE.BoxGeometry(4.35, 0.25, 5.95);
  const borderMat = new THREE.MeshStandardMaterial({
    color: 0x0f172a,
    roughness: 0.2,
    metalness: 0.9,
  });
  const border = new THREE.Mesh(borderGeo, borderMat);
  border.position.y = -0.08;
  evmGroup.add(border);

  // Left Section: CONTROL UNIT
  const cuGeo = new THREE.BoxGeometry(1.6, 0.42, 5.4);
  const cuMat = new THREE.MeshStandardMaterial({
    color: 0x111827,
    roughness: 0.35,
    metalness: 0.4,
  });
  const controlUnit = new THREE.Mesh(cuGeo, cuMat);
  controlUnit.position.set(-1.15, 0.05, 0);
  evmGroup.add(controlUnit);

  // CU LCD Screen (Dynamic Canvas Texture)
  const lcdCanvas = document.createElement('canvas');
  lcdCanvas.width = 256;
  lcdCanvas.height = 128;
  const lcdCtx = lcdCanvas.getContext('2d');
  lcdCtx.fillStyle = '#064e3b';
  lcdCtx.fillRect(0, 0, 256, 128);
  lcdCtx.fillStyle = '#10b981';
  lcdCtx.font = 'bold 22px Courier New, monospace';
  lcdCtx.fillText('STATUS: READY', 20, 45);
  lcdCtx.font = '16px Courier New, monospace';
  lcdCtx.fillText('BALLOT ENABLED', 20, 75);
  lcdCtx.fillText('NODE CLUSTER: OK', 20, 105);

  const lcdTexture = new THREE.CanvasTexture(lcdCanvas);
  const lcdGeo = new THREE.PlaneGeometry(1.3, 0.7);
  const lcdMat = new THREE.MeshBasicMaterial({ map: lcdTexture });
  const lcdScreen = new THREE.Mesh(lcdGeo, lcdMat);
  lcdScreen.rotation.x = -Math.PI / 2;
  lcdScreen.position.set(-1.15, 0.28, -1.6);
  evmGroup.add(lcdScreen);

  // CU Diagnostic LEDs (Power: Green, Busy: Amber, Vote: Red)
  const ledGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.08, 16);
  const greenLedMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
  const amberLedMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });
  const redLedMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });

  const ledPower = new THREE.Mesh(ledGeo, greenLedMat);
  ledPower.position.set(-1.5, 0.28, -0.6);
  evmGroup.add(ledPower);

  const ledBusy = new THREE.Mesh(ledGeo, amberLedMat);
  ledBusy.position.set(-1.15, 0.28, -0.6);
  evmGroup.add(ledBusy);

  const ledVote = new THREE.Mesh(ledGeo, redLedMat);
  ledVote.position.set(-0.8, 0.28, -0.6);
  evmGroup.add(ledVote);

  // Right Section: BALLOT UNIT
  const buGeo = new THREE.BoxGeometry(2.2, 0.4, 5.4);
  const buMat = new THREE.MeshStandardMaterial({
    color: 0xf1f5f9,
    roughness: 0.6,
    metalness: 0.1,
  });
  const ballotUnit = new THREE.Mesh(buGeo, buMat);
  ballotUnit.position.set(0.85, 0.04, 0);
  evmGroup.add(ballotUnit);

  // 4 Candidate Rows (Serial, Nameplate, Red Lamp, Tactile 3D Blue Button)
  const evmButtons = [];
  const candidateRows = [
    { name: 'Dr. Alice Reed (Innovate)', symbol: '🌱', z: -1.8 },
    { name: 'Marcus Sterling (Progress)', symbol: '⚡', z: -0.6 },
    { name: 'Elena Rostova (Freedom)', symbol: '🕊️', z: 0.6 },
    { name: 'None of the Above (NOTA)', symbol: '⚪', z: 1.8 },
  ];

  const btnGeo = new THREE.CylinderGeometry(0.18, 0.20, 0.12, 24);
  const btnMat = new THREE.MeshStandardMaterial({
    color: 0x2563eb,
    roughness: 0.3,
    metalness: 0.4,
  });

  const rowPlateGeo = new THREE.BoxGeometry(2.0, 0.02, 0.85);
  const rowPlateMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.8 });

  candidateRows.forEach((cand, idx) => {
    // Row strip
    const rowPlate = new THREE.Mesh(rowPlateGeo, rowPlateMat);
    rowPlate.position.set(0.85, 0.25, cand.z);
    evmGroup.add(rowPlate);

    // Indicator lamp
    const lamp = new THREE.Mesh(ledGeo, redLedMat);
    lamp.position.set(1.2, 0.28, cand.z);
    evmGroup.add(lamp);

    // 3D Tactile Blue Button
    const btn = new THREE.Mesh(btnGeo, btnMat.clone());
    btn.position.set(1.6, 0.29, cand.z);
    btn.castShadow = true;
    btn.userData = { candidateIndex: idx, name: cand.name };
    evmGroup.add(btn);
    evmButtons.push(btn);
  });

  // Rear Kickstand / Base Support
  const standGeo = new THREE.BoxGeometry(3.6, 0.12, 2.2);
  const standMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.7, roughness: 0.3 });
  const kickstand = new THREE.Mesh(standGeo, standMat);
  kickstand.position.set(0, -0.22, 1.6);
  kickstand.rotation.x = 0.35;
  evmGroup.add(kickstand);

  // Initial pose: Lying flat on the platform
  evmGroup.position.set(0, -1.6, 0);
  evmGroup.rotation.set(-1.45, 0, 0);

  // ==========================================
  // 2. 3D VOTER IDENTITY CARD (SCENE 2)
  // ==========================================
  const voterCardGroup = new THREE.Group();
  voterCardGroup.position.set(0, -10, 0);
  scene.add(voterCardGroup);

  const cardGeo = new THREE.BoxGeometry(3.2, 2.0, 0.08);
  const cardMat = new THREE.MeshStandardMaterial({
    color: 0x0284c7,
    roughness: 0.2,
    metalness: 0.6,
  });
  const voterCard = new THREE.Mesh(cardGeo, cardMat);
  voterCardGroup.add(voterCard);

  // Gold Microchip on card
  const chipGeo = new THREE.BoxGeometry(0.7, 0.55, 0.09);
  const chipMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.2, metalness: 0.9 });
  const chip = new THREE.Mesh(chipGeo, chipMat);
  chip.position.set(-0.9, 0.2, 0.02);
  voterCardGroup.add(chip);

  // Cryptographic Lock Ring around identity card
  const lockRingGeo = new THREE.TorusGeometry(1.8, 0.05, 16, 48);
  const lockRingMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
  const lockRing = new THREE.Mesh(lockRingGeo, lockRingMat);
  voterCardGroup.add(lockRing);

  // ==========================================
  // 3. 3D BLOCKCHAIN CHAIN VISUALIZATION (SCENE 4)
  // ==========================================
  const chainGroup = new THREE.Group();
  chainGroup.position.set(0, -10, 0);
  scene.add(chainGroup);

  const blocks = [];
  const blockGeo = new THREE.BoxGeometry(0.9, 0.9, 0.9);
  const blockMat = new THREE.MeshStandardMaterial({
    color: 0x0284c7,
    transparent: true,
    opacity: 0.85,
    roughness: 0.2,
    metalness: 0.8,
  });

  const linkGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.7, 16);
  const linkMat = new THREE.MeshBasicMaterial({ color: 0x34d399 });

  for (let b = 0; b < 5; b++) {
    const bMesh = new THREE.Mesh(blockGeo, blockMat.clone());
    bMesh.position.set((b - 2) * 1.6, 0, 0);
    chainGroup.add(bMesh);
    blocks.push(bMesh);

    if (b > 0) {
      const link = new THREE.Mesh(linkGeo, linkMat);
      link.rotation.z = Math.PI / 2;
      link.position.set((b - 2) * 1.6 - 0.8, 0, 0);
      chainGroup.add(link);
    }
  }

  // ==========================================
  // 4. 3D 3-NODE DISTRIBUTED NETWORK (SCENE 5)
  // ==========================================
  const networkGroup = new THREE.Group();
  networkGroup.position.set(0, -10, 0);
  scene.add(networkGroup);

  const serverGeo = new THREE.BoxGeometry(0.7, 1.5, 0.7);
  const serverMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.3, metalness: 0.7 });

  const nodePositions = [
    { id: 'node_a', x: 0, z: -1.6, name: 'Node A (Leader)' },
    { id: 'node_b', x: -1.8, z: 1.2, name: 'Node B (Validator)' },
    { id: 'node_c', x: 1.8, z: 1.2, name: 'Node C (Validator)' },
  ];

  const nodeMeshes = [];
  nodePositions.forEach((np) => {
    const srv = new THREE.Mesh(serverGeo, serverMat);
    srv.position.set(np.x, 0, np.z);
    networkGroup.add(srv);
    nodeMeshes.push(srv);

    // Glowing aura ring
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.03, 16, 32), new THREE.MeshBasicMaterial({ color: 0x38bdf8 }));
    ring.rotation.x = Math.PI / 2;
    ring.position.set(np.x, -0.7, np.z);
    networkGroup.add(ring);
  });

  // Animated Packet spheres pulsing between nodes
  const packetGeo = new THREE.SphereGeometry(0.08, 16, 16);
  const packetMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
  const packet1 = new THREE.Mesh(packetGeo, packetMat);
  const packet2 = new THREE.Mesh(packetGeo, packetMat);
  networkGroup.add(packet1);
  networkGroup.add(packet2);

  // ==========================================
  // 5. 3D SHARDING RING (SCENE 9)
  // ==========================================
  const shardingGroup = new THREE.Group();
  shardingGroup.position.set(0, -10, 0);
  scene.add(shardingGroup);

  const shardRingGeo = new THREE.TorusGeometry(2.8, 0.06, 16, 64);
  const shardRingMat = new THREE.MeshBasicMaterial({ color: 0x818cf8 });
  const shardRingMesh = new THREE.Mesh(shardRingGeo, shardRingMat);
  shardRingMesh.rotation.x = Math.PI / 2;
  shardingGroup.add(shardRingMesh);

  // Virtual nodes dots around the ring
  const vnGeo = new THREE.SphereGeometry(0.06, 8, 8);
  const vnMatA = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
  const vnMatB = new THREE.MeshBasicMaterial({ color: 0x34d399 });
  const vnMatC = new THREE.MeshBasicMaterial({ color: 0xf59e0b });

  for (let i = 0; i < 48; i++) {
    const angle = (i / 48) * Math.PI * 2;
    const mat = i % 3 === 0 ? vnMatA : i % 3 === 1 ? vnMatB : vnMatC;
    const vnDot = new THREE.Mesh(vnGeo, mat);
    vnDot.position.set(Math.cos(angle) * 2.8, 0, Math.sin(angle) * 2.8);
    shardingGroup.add(vnDot);
  }

  // ==========================================
  // SCROLL-DRIVEN TRANSFORMATION ENGINE
  // ==========================================
  let scrollProgress = 0;
  let targetScrollProgress = 0;

  function updateScroll() {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    targetScrollProgress = docHeight > 0 ? Math.max(0, Math.min(1, window.scrollY / docHeight)) : 0;

    // Update active chapter nav dot
    const chapters = document.querySelectorAll('.scene-chapter');
    const dots = document.querySelectorAll('.chapter-dot');
    let currentChapter = 0;

    chapters.forEach((ch, idx) => {
      const rect = ch.getBoundingClientRect();
      if (rect.top <= window.innerHeight * 0.45 && rect.bottom >= window.innerHeight * 0.15) {
        currentChapter = idx;
      }
    });

    dots.forEach((dot, idx) => {
      if (idx === currentChapter) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });
  }

  window.addEventListener('scroll', updateScroll, { passive: true });
  updateScroll();

  // Pointer Interaction
  const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  window.addEventListener('mousemove', (e) => {
    mouse.targetX = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.targetY = -(e.clientY / window.innerHeight) * 2 + 1;
  });

  window.addEventListener('mouseleave', () => {
    mouse.targetX = 0;
    mouse.targetY = 0;
  });

  // Window Resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    updateScroll();
  });

  // Reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ==========================================
  // MAIN ANIMATION RENDER LOOP (60 FPS)
  // ==========================================
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const elapsedTime = clock.getElapsedTime();

    // Smooth scroll interpolation
    if (prefersReducedMotion) {
      scrollProgress = targetScrollProgress;
      mouse.x = 0;
      mouse.y = 0;
    } else {
      scrollProgress += (targetScrollProgress - scrollProgress) * 0.08;
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;
    }

    // Slowly drift dust particles
    const positions = particles.geometry.attributes.position.array;
    for (let p = 1; p < particleCount * 3; p += 3) {
      positions[p] -= 0.003;
      if (positions[p] < -6) positions[p] = 6;
    }
    particles.geometry.attributes.position.needsUpdate = true;

    // ----------------------------------------------------
    // SCENE TRANSITIONS BASED ON NORMALIZED SCROLL PROGRESS
    // ----------------------------------------------------
    // p: 0.0 to 1.0

    // CHAPTER 1: EVM Lying Down -> Rising -> Standing Upright (0.0 to 0.40)
    if (scrollProgress <= 0.42) {
      evmGroup.position.y = -1.6 + Math.min(1.0, scrollProgress / 0.35) * 1.6;
      
      // Interpolate rotation: from -1.45 (flat) to +0.05 (upright)
      const liftFactor = Math.min(1.0, Math.max(0, (scrollProgress - 0.08) / 0.28));
      const targetRotX = -1.45 + liftFactor * 1.50;
      evmGroup.rotation.x = targetRotX + mouse.y * 0.15;
      evmGroup.rotation.y = mouse.x * 0.25;
      evmGroup.rotation.z = -mouse.x * 0.05;

      // Camera elevation
      camera.position.set(0, 4.0 - liftFactor * 2.8, 7.5 - liftFactor * 1.0);
      camera.lookAt(0, evmGroup.position.y + 0.3, 0);

      // Visibility
      evmGroup.visible = true;
      voterCardGroup.position.y = -15;
      chainGroup.position.y = -15;
      networkGroup.position.y = -15;
      shardingGroup.position.y = -15;
    }
    // CHAPTER 2 & 3: Identity & Anonymous Ballot (0.42 to 0.55)
    else if (scrollProgress > 0.42 && scrollProgress <= 0.55) {
      evmGroup.position.set(-3.5, 0.2, -3.0);
      evmGroup.rotation.set(0.1, 0.4, 0);

      voterCardGroup.position.set(0, 0, 0);
      voterCardGroup.rotation.y = elapsedTime * 0.6 + mouse.x * 0.3;
      voterCardGroup.rotation.x = mouse.y * 0.2;
      lockRing.rotation.z = elapsedTime * 1.2;

      camera.position.set(0, 0.5, 6.0);
      camera.lookAt(0, 0, 0);

      chainGroup.position.y = -15;
      networkGroup.position.y = -15;
      shardingGroup.position.y = -15;
    }
    // CHAPTER 4: Blockchain Chain Assembly (0.55 to 0.68)
    else if (scrollProgress > 0.55 && scrollProgress <= 0.68) {
      evmGroup.position.y = -15;
      voterCardGroup.position.y = -15;

      chainGroup.position.set(0, 0, 0);
      chainGroup.rotation.y = Math.sin(elapsedTime * 0.3) * 0.2 + mouse.x * 0.25;
      chainGroup.rotation.x = mouse.y * 0.15;

      // Float blocks
      blocks.forEach((blk, idx) => {
        blk.position.y = Math.sin(elapsedTime * 1.5 + idx * 0.8) * 0.1;
      });

      camera.position.set(0, 0.6, 6.2);
      camera.lookAt(0, 0, 0);

      networkGroup.position.y = -15;
      shardingGroup.position.y = -15;
    }
    // CHAPTER 5 & 6: 3-Node Distributed Network & Consensus (0.68 to 0.82)
    else if (scrollProgress > 0.68 && scrollProgress <= 0.82) {
      evmGroup.position.y = -15;
      voterCardGroup.position.y = -15;
      chainGroup.position.y = -15;

      networkGroup.position.set(0, 0, 0);
      networkGroup.rotation.y = elapsedTime * 0.25 + mouse.x * 0.3;

      // Animate packet trajectories
      const t1 = (elapsedTime * 0.8) % 1.0;
      packet1.position.set(
        nodePositions[0].x * (1 - t1) + nodePositions[1].x * t1,
        0.2 + Math.sin(t1 * Math.PI) * 0.4,
        nodePositions[0].z * (1 - t1) + nodePositions[1].z * t1
      );

      const t2 = (elapsedTime * 0.8 + 0.5) % 1.0;
      packet2.position.set(
        nodePositions[1].x * (1 - t2) + nodePositions[2].x * t2,
        0.2 + Math.sin(t2 * Math.PI) * 0.4,
        nodePositions[1].z * (1 - t2) + nodePositions[2].z * t2
      );

      camera.position.set(0, 3.2, 5.8);
      camera.lookAt(0, 0, 0);

      shardingGroup.position.y = -15;
    }
    // CHAPTER 9 & OVERVIEW: Sharding Ring & Convergence (0.82 to 1.0)
    else {
      evmGroup.position.set(0, -0.6, 0.5);
      evmGroup.rotation.set(0.1 + mouse.y * 0.1, mouse.x * 0.2, 0);
      evmGroup.visible = true;

      shardingGroup.position.set(0, -0.6, 0.5);
      shardingGroup.rotation.y = elapsedTime * 0.3;

      networkGroup.position.y = -15;
      chainGroup.position.y = -15;
      voterCardGroup.position.y = -15;

      camera.position.set(0, 2.5, 7.5);
      camera.lookAt(0, 0, 0);
    }

    renderer.render(scene, camera);
  }

  animate();

  // Export for interactive controls
  window.Cinematic3D = {
    triggerTamperDemo: function (isTampered) {
      if (blocks && blocks[2]) {
        blocks[2].material.color.setHex(isTampered ? 0xef4444 : 0x0284c7);
        blocks[2].material.emissive.setHex(isTampered ? 0xb91c1c : 0x000000);
      }
    },
    pressEVMButton: function (candidateIdx) {
      if (evmButtons[candidateIdx]) {
        evmButtons[candidateIdx].position.y = 0.23;
        setTimeout(() => {
          evmButtons[candidateIdx].position.y = 0.29;
        }, 250);
      }
    }
  };

  console.log('Cinematic 3D experience initialized successfully.');
})();
