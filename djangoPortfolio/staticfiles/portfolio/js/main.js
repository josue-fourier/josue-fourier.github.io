// System Boot Sequence (Top Progress Bar)
const bootLoader = document.getElementById('boot-loader-bar');
let bootProgress = 0;
const bootInterval = setInterval(() => {
    bootProgress += Math.random() * 30;
    if (bootProgress > 90) bootProgress = 90;
    if (bootLoader) bootLoader.style.width = `${bootProgress}%`;
}, 100);

window.addEventListener('load', () => {
    clearInterval(bootInterval);
    if (bootLoader) {
        bootLoader.style.width = '100%';
        setTimeout(() => {
            bootLoader.style.opacity = '0';
            setTimeout(() => bootLoader.remove(), 500);
        }, 500);
    }
});

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// --- 0. Three.js 3D Cryptographic Data Topology & EM Telemetry Engine ---
(function initThreeCryptographicScene() {
    const canvas = document.getElementById('em-telemetry-canvas');
    if (!canvas) return;

    // Wait briefly if Three.js is still defer-loading, or fallback gracefully
    function bootScene() {
        if (typeof THREE === 'undefined') {
            initFallback2DCanvas(canvas);
            return;
        }

        let renderer;
        try {
            renderer = new THREE.WebGLRenderer({
                canvas: canvas,
                alpha: true,
                antialias: true,
                powerPreference: 'high-performance'
            });
        } catch (e) {
            initFallback2DCanvas(canvas);
            return;
        }

        const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        renderer.setPixelRatio(dpr);
        renderer.setSize(window.innerWidth, window.innerHeight);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        camera.position.z = 42;

        // Group holding the entire 3D cryptographic topology
        const rootGroup = new THREE.Group();
        scene.add(rootGroup);

        // 1. Central Geodesic Cryptographic Lattice (Wireframe Icosahedron + Inner Core)
        const outerGeo = new THREE.IcosahedronGeometry(14, 1);
        const outerWireframe = new THREE.WireframeGeometry(outerGeo);
        const outerMat = new THREE.LineBasicMaterial({
            color: 0x10b981,
            transparent: true,
            opacity: 0.14
        });
        const outerLattice = new THREE.LineSegments(outerWireframe, outerMat);
        outerLattice.position.set(14, 2, -6);
        rootGroup.add(outerLattice);

        const innerGeo = new THREE.OctahedronGeometry(7.5, 0);
        const innerWireframe = new THREE.WireframeGeometry(innerGeo);
        const innerMat = new THREE.LineBasicMaterial({
            color: 0x06b6d4,
            transparent: true,
            opacity: 0.18
        });
        const innerCore = new THREE.LineSegments(innerWireframe, innerMat);
        outerLattice.add(innerCore);

        // 2. Distributed Telemetry Node Cloud & Synaptic Network Edges (R2: 110 Spatial Nodes)
        let isMobile = window.innerWidth < 768;
        const nodeCount = 110;
        const nodePositions = new Float32Array(nodeCount * 3);
        const nodeVelocities = [];
        let spreadX = isMobile ? 65 : 85;
        const spreadY = 55;
        const spreadZ = 35;

        for (let i = 0; i < nodeCount; i++) {
            nodePositions[i * 3] = (Math.random() - 0.5) * spreadX;
            nodePositions[i * 3 + 1] = (Math.random() - 0.5) * spreadY;
            nodePositions[i * 3 + 2] = (Math.random() - 0.5) * spreadZ;
            nodeVelocities.push({
                vx: (Math.random() - 0.5) * 0.008,
                vy: (Math.random() - 0.5) * 0.008,
                vz: (Math.random() - 0.5) * 0.005
            });
        }

        const nodesGeo = new THREE.BufferGeometry();
        nodesGeo.setAttribute('position', new THREE.BufferAttribute(nodePositions, 3));

        const nodesMat = new THREE.PointsMaterial({
            color: 0x10b981,
            size: 0.42,
            transparent: true,
            opacity: 0.50
        });
        const nodeCloud = new THREE.Points(nodesGeo, nodesMat);
        rootGroup.add(nodeCloud);

        // Pre-allocate line segments buffer for dynamic cryptographic packet links
        const maxLines = nodeCount * 4;
        const linePositions = new Float32Array(maxLines * 6);
        const linesGeo = new THREE.BufferGeometry();
        linesGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
        const linesMat = new THREE.LineBasicMaterial({
            color: 0x06b6d4,
            transparent: true,
            opacity: 0.065
        });
        const networkLines = new THREE.LineSegments(linesGeo, linesMat);
        rootGroup.add(networkLines);

        // 2b. Dedicated C2 Live Network Packet Layer (Traversing synaptic node links)
        const packetCount = 44; // 36-48 glowing Emerald & Cyan data packets
        const packetPositions = new Float32Array(packetCount * 3);
        const packetColors = new Float32Array(packetCount * 3);
        const nodeNeighbors = Array.from({ length: nodeCount }, () => []);
        const connectedNodes = new Int32Array(nodeCount);
        let connectedNodeCount = 0;
        const packets = [];

        const EMERALD_RGB = [16 / 255, 185 / 255, 129 / 255]; // #10B981
        const CYAN_RGB = [6 / 255, 182 / 255, 212 / 255];     // #06B6D4

        for (let i = 0; i < packetCount; i++) {
            const isCyan = i % 2 === 1;
            const rgb = isCyan ? CYAN_RGB : EMERALD_RGB;
            packetColors[i * 3] = rgb[0];
            packetColors[i * 3 + 1] = rgb[1];
            packetColors[i * 3 + 2] = rgb[2];

            const fromNode = Math.floor(Math.random() * nodeCount);
            packets.push({
                fromNode: fromNode,
                toNode: (fromNode + 1) % nodeCount,
                t: Math.random(),
                speed: 0.003 + Math.random() * 0.0045,
                isCyan: isCyan
            });
        }

        const packetsGeo = new THREE.BufferGeometry();
        packetsGeo.setAttribute('position', new THREE.BufferAttribute(packetPositions, 3));
        packetsGeo.setAttribute('color', new THREE.BufferAttribute(packetColors, 3));

        const packetsMat = new THREE.PointsMaterial({
            size: isMobile ? 0.95 : 1.45,
            vertexColors: true,
            transparent: true,
            opacity: 0.95,
            blending: THREE.AdditiveBlending
        });
        const packetCloud = new THREE.Points(packetsGeo, packetsMat);
        rootGroup.add(packetCloud);

        // 2c. Continuous Low-Level Telemetry Ground Grid & Sine-Wave Particle Stream (Pillar 1)
        const gridCols = isMobile ? 26 : 42;
        const gridRows = isMobile ? 16 : 26;
        const gridParticleCount = gridCols * gridRows;
        const gridPositions = new Float32Array(gridParticleCount * 3);
        const gridColors = new Float32Array(gridParticleCount * 3);
        const gridSpacingX = isMobile ? 3.4 : 3.8;
        const gridSpacingZ = isMobile ? 3.0 : 3.4;
        const gridOriginX = -(gridCols * gridSpacingX) * 0.5;
        const gridOriginZ = -(gridRows * gridSpacingZ) * 0.5;
        const gridBaseY = -18;

        for (let r = 0; r < gridRows; r++) {
            for (let c = 0; c < gridCols; c++) {
                const idx = (r * gridCols + c) * 3;
                gridPositions[idx] = gridOriginX + c * gridSpacingX;
                gridPositions[idx + 1] = gridBaseY;
                gridPositions[idx + 2] = gridOriginZ + r * gridSpacingZ;

                const isMint = (r + c) % 13 === 0;
                const isCyan = (r * 3 + c) % 17 === 0;
                if (isMint) {
                    gridColors[idx] = 16 / 255;
                    gridColors[idx + 1] = 185 / 255;
                    gridColors[idx + 2] = 129 / 255;
                } else if (isCyan) {
                    gridColors[idx] = 6 / 255;
                    gridColors[idx + 1] = 182 / 255;
                    gridColors[idx + 2] = 212 / 255;
                } else {
                    gridColors[idx] = 30 / 255;
                    gridColors[idx + 1] = 41 / 255;
                    gridColors[idx + 2] = 59 / 255;
                }
            }
        }

        const gridGeo = new THREE.BufferGeometry();
        gridGeo.setAttribute('position', new THREE.BufferAttribute(gridPositions, 3));
        gridGeo.setAttribute('color', new THREE.BufferAttribute(gridColors, 3));
        const gridMat = new THREE.PointsMaterial({
            size: isMobile ? 0.65 : 0.95,
            vertexColors: true,
            transparent: true,
            opacity: 0.55
        });
        const telemetryGridPoints = new THREE.Points(gridGeo, gridMat);
        rootGroup.add(telemetryGridPoints);

        // 3. Expanding 3D Electromagnetic (EM) Wave Rings
        const emRings = [];
        const ringGeo = new THREE.RingGeometry(0.8, 0.92, 48);
        for (let i = 0; i < 4; i++) {
            const rMat = new THREE.MeshBasicMaterial({
                color: i % 2 === 0 ? 0x10b981 : 0x06b6d4,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.0
            });
            const ringMesh = new THREE.Mesh(ringGeo, rMat);
            ringMesh.position.copy(outerLattice.position);
            ringMesh.rotation.x = Math.PI * 0.32;
            ringMesh.rotation.y = -Math.PI * 0.15;
            rootGroup.add(ringMesh);
            emRings.push({
                mesh: ringMesh,
                scale: 1 + i * 4.5,
                maxScale: 22
            });
        }

        // Theme Sync (Obsidian Dark vs Cryo Light)
        function syncThreeTheme() {
            const isDark = document.documentElement.getAttribute('data-theme') !== 'lofi';
            const primaryHex = isDark ? 0x10b981 : 0x059669;
            const secondaryHex = isDark ? 0x06b6d4 : 0x0284c7;

            outerMat.color.setHex(primaryHex);
            outerMat.opacity = isDark ? 0.08 : 0.06;
            innerMat.color.setHex(secondaryHex);
            innerMat.opacity = isDark ? 0.10 : 0.08;
            nodesMat.color.setHex(primaryHex);
            nodesMat.opacity = isDark ? 0.45 : 0.35;
            linesMat.color.setHex(secondaryHex);
            linesMat.opacity = isDark ? 0.065 : 0.045;
            gridMat.opacity = isDark ? 0.55 : 0.35;

            // Sync packet layer colors and blending (Additive for Dark, Normal for Light)
            packetsMat.blending = isDark ? THREE.AdditiveBlending : THREE.NormalBlending;
            packetsMat.opacity = isDark ? 0.75 : 0.60;
            packetsMat.needsUpdate = true;

            // Sync EM ring colors
            for (let r = 0; r < emRings.length; r++) {
                emRings[r].mesh.material.color.setHex(r % 2 === 0 ? primaryHex : secondaryHex);
            }

            const pEmerald = isDark ? [16 / 255, 185 / 255, 129 / 255] : [5 / 255, 150 / 255, 105 / 255];
            const pCyan = isDark ? [6 / 255, 182 / 255, 212 / 255] : [2 / 255, 132 / 255, 199 / 255];
            for (let i = 0; i < packetCount; i++) {
                const rgb = packets[i].isCyan ? pCyan : pEmerald;
                packetColors[i * 3] = rgb[0];
                packetColors[i * 3 + 1] = rgb[1];
                packetColors[i * 3 + 2] = rgb[2];
            }
            packetsGeo.attributes.color.needsUpdate = true;

            if (prefersReducedMotion && renderer) {
                renderer.render(scene, camera);
            }
        }
        syncThreeTheme();

        // Observe data-theme changes on <html>
        const themeObserver = new MutationObserver(syncThreeTheme);
        themeObserver.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });

        // Interactive Mouse & Scroll Velocity Tracking (Pillars 1 & 2)
        let targetMouseX = 0;
        let targetMouseY = 0;
        let currentMouseX = 0;
        let currentMouseY = 0;
        let scrollProgressRatio = 0;
        let lastScrollY = window.pageYOffset || document.documentElement.scrollTop;
        let scrollVelocity = 0;
        let scrollVelDamped = 0;
        let waveTime = 0;

        window.addEventListener('mousemove', (e) => {
            targetMouseX = (e.clientX / window.innerWidth - 0.5) * 2;
            targetMouseY = -(e.clientY / window.innerHeight - 0.5) * 2;
        }, { passive: true });

        window.addEventListener('scroll', () => {
            const currentY = window.pageYOffset || document.documentElement.scrollTop;
            const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
            scrollProgressRatio = currentY / maxScroll;
            scrollVelocity = (currentY - lastScrollY) * 0.15;
            lastScrollY = currentY;
        }, { passive: true });

        // Spawn an EM pulse surge on click
        window.addEventListener('click', () => {
            if (emRings.length > 0) {
                emRings[0].scale = 1;
            }
        }, { passive: true });

        let lastWidth = window.innerWidth;
        let lastHeight = window.innerHeight;
        let connectionThresholdSq = isMobile ? 55 : 75;

        window.addEventListener('resize', () => {
            const newWidth = window.innerWidth;
            const newHeight = window.innerHeight;
            // On mobile devices, ignore minor vertical URL bar height oscillations
            if (newWidth === lastWidth && Math.abs(newHeight - lastHeight) < 80) {
                return;
            }
            lastWidth = newWidth;
            lastHeight = newHeight;
            isMobile = newWidth < 768;
            spreadX = isMobile ? 65 : 85;
            connectionThresholdSq = isMobile ? 55 : 75;
            packetsMat.size = isMobile ? 0.95 : 1.45;
            camera.aspect = newWidth / newHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(newWidth, newHeight);
            if (prefersReducedMotion) {
                renderer.render(scene, camera);
            }
        }, { passive: true });

        // Main WebGL Render Loop

        function computeSynapticLinks() {
            const posArr = nodesGeo.attributes.position.array;
            for (let i = 0; i < nodeCount; i++) {
                nodeNeighbors[i].length = 0;
            }

            let lineIdx = 0;
            connectedNodeCount = 0;
            for (let i = 0; i < nodeCount; i++) {
                const ax = posArr[i * 3];
                const ay = posArr[i * 3 + 1];
                const az = posArr[i * 3 + 2];

                for (let j = i + 1; j < nodeCount; j++) {
                    if (lineIdx >= maxLines) break;
                    const bx = posArr[j * 3];
                    const by = posArr[j * 3 + 1];
                    const bz = posArr[j * 3 + 2];

                    const dx = ax - bx;
                    const dy = ay - by;
                    const dz = az - bz;
                    const distSq = dx * dx + dy * dy + dz * dz;

                    if (distSq < connectionThresholdSq) {
                        const base = lineIdx * 6;
                        linePositions[base] = ax;
                        linePositions[base + 1] = ay;
                        linePositions[base + 2] = az;
                        linePositions[base + 3] = bx;
                        linePositions[base + 4] = by;
                        linePositions[base + 5] = bz;
                        lineIdx++;

                        nodeNeighbors[i].push(j);
                        nodeNeighbors[j].push(i);
                    }
                }
                if (nodeNeighbors[i].length > 0) {
                    connectedNodes[connectedNodeCount++] = i;
                }
            }
            linesGeo.setDrawRange(0, lineIdx * 2);
            linesGeo.attributes.position.needsUpdate = true;
        }

        function updatePackets(advance) {
            const posArr = nodesGeo.attributes.position.array;
            for (let p = 0; p < packetCount; p++) {
                const pkt = packets[p];
                if (advance) {
                    pkt.t += pkt.speed;
                    if (pkt.t >= 1.0) {
                        pkt.t = 0.0;
                        pkt.fromNode = pkt.toNode;
                        const neighbors = nodeNeighbors[pkt.fromNode];
                        if (neighbors && neighbors.length > 0) {
                            pkt.toNode = neighbors[Math.floor(Math.random() * neighbors.length)];
                        } else if (connectedNodeCount > 0) {
                            pkt.fromNode = connectedNodes[Math.floor(Math.random() * connectedNodeCount)];
                            const newNeighbors = nodeNeighbors[pkt.fromNode];
                            if (newNeighbors && newNeighbors.length > 0) {
                                pkt.toNode = newNeighbors[Math.floor(Math.random() * newNeighbors.length)];
                            } else {
                                pkt.toNode = (pkt.fromNode + 1) % nodeCount;
                            }
                        }
                    }
                }

                const fIdx = pkt.fromNode * 3;
                const tIdx = pkt.toNode * 3;
                const pBase = p * 3;

                packetPositions[pBase] = posArr[fIdx] + (posArr[tIdx] - posArr[fIdx]) * pkt.t;
                packetPositions[pBase + 1] = posArr[fIdx + 1] + (posArr[tIdx + 1] - posArr[fIdx + 1]) * pkt.t;
                packetPositions[pBase + 2] = posArr[fIdx + 2] + (posArr[tIdx + 2] - posArr[fIdx + 2]) * pkt.t;
            }
            packetsGeo.attributes.position.needsUpdate = true;
        }

        function animate() {
            if (!document.hidden) {
                // Smooth camera & topology response to mouse + scroll depth & velocity
                currentMouseX += (targetMouseX - currentMouseX) * 0.04;
                currentMouseY += (targetMouseY - currentMouseY) * 0.04;
                scrollVelDamped += (scrollVelocity - scrollVelDamped) * 0.08;
                scrollVelocity *= 0.88;

                rootGroup.rotation.y = currentMouseX * 0.18 + scrollProgressRatio * 0.85;
                rootGroup.rotation.x = currentMouseY * 0.12 + scrollProgressRatio * 0.35 + scrollVelDamped * 0.005;
                rootGroup.position.y = scrollProgressRatio * 10;

                // Rotate cryptographic geodesic core
                outerLattice.rotation.y += 0.0008;
                outerLattice.rotation.x += 0.0004;
                innerCore.rotation.y -= 0.0016;
                innerCore.rotation.z += 0.0008;

                // Update telemetry node positions & compute synaptic cryptographic links
                const posArr = nodesGeo.attributes.position.array;
                const halfX = spreadX * 0.5;
                const halfY = spreadY * 0.5;
                const halfZ = spreadZ * 0.5;

                for (let i = 0; i < nodeCount; i++) {
                    const ix = i * 3;
                    posArr[ix] += nodeVelocities[i].vx;
                    posArr[ix + 1] += nodeVelocities[i].vy;
                    posArr[ix + 2] += nodeVelocities[i].vz;

                    if (posArr[ix] > halfX) {
                        posArr[ix] = halfX;
                        nodeVelocities[i].vx = -Math.abs(nodeVelocities[i].vx);
                    } else if (posArr[ix] < -halfX) {
                        posArr[ix] = -halfX;
                        nodeVelocities[i].vx = Math.abs(nodeVelocities[i].vx);
                    }

                    if (posArr[ix + 1] > halfY) {
                        posArr[ix + 1] = halfY;
                        nodeVelocities[i].vy = -Math.abs(nodeVelocities[i].vy);
                    } else if (posArr[ix + 1] < -halfY) {
                        posArr[ix + 1] = -halfY;
                        nodeVelocities[i].vy = Math.abs(nodeVelocities[i].vy);
                    }

                    if (posArr[ix + 2] > halfZ) {
                        posArr[ix + 2] = halfZ;
                        nodeVelocities[i].vz = -Math.abs(nodeVelocities[i].vz);
                    } else if (posArr[ix + 2] < -halfZ) {
                        posArr[ix + 2] = -halfZ;
                        nodeVelocities[i].vz = Math.abs(nodeVelocities[i].vz);
                    }
                }
                nodesGeo.attributes.position.needsUpdate = true;

                // Recompute active synaptic links
                computeSynapticLinks();

                // Advance C2 data packets traversing synaptic edges
                updatePackets(true);

                // Animate continuous low-level telemetry sine-wave grid reacting to time & scroll velocity (Pillar 1)
                waveTime += 0.016 + Math.min(0.04, Math.abs(scrollVelDamped) * 0.03);
                const gridPosArr = gridGeo.attributes.position.array;
                for (let r = 0; r < gridRows; r++) {
                    for (let c = 0; c < gridCols; c++) {
                        const idx = (r * gridCols + c) * 3;
                        const gx = gridPosArr[idx];
                        const gz = gridPosArr[idx + 2];
                        gridPosArr[idx + 1] = gridBaseY + 
                            Math.sin(gx * 0.07 + waveTime) * Math.cos(gz * 0.07 + waveTime * 0.75) * 1.8 +
                            scrollVelDamped * Math.sin(gx * 0.12) * 1.2;
                    }
                }
                gridGeo.attributes.position.needsUpdate = true;

                // Expand 3D EM wave rings without per-frame function allocation
                for (let r = 0; r < emRings.length; r++) {
                    const ring = emRings[r];
                    ring.scale += 0.024;
                    if (ring.scale > ring.maxScale) {
                        ring.scale = 1;
                    }
                    const progress = ring.scale / ring.maxScale;
                    ring.mesh.scale.set(ring.scale, ring.scale, 1);
                    ring.mesh.material.opacity = (1 - progress) * 0.10;
                }

                renderer.render(scene, camera);
            }

            if (!prefersReducedMotion) {
                requestAnimationFrame(animate);
            }
        }

        // Initial setup pass: compute synaptic links and bind packets strictly to actual connected edges
        computeSynapticLinks();
        for (let p = 0; p < packetCount; p++) {
            if (connectedNodeCount > 0) {
                packets[p].fromNode = connectedNodes[Math.floor(Math.random() * connectedNodeCount)];
                const neighbors = nodeNeighbors[packets[p].fromNode];
                packets[p].toNode = neighbors[Math.floor(Math.random() * neighbors.length)];
            }
        }
        updatePackets(false);

        // Render initial frame immediately (fully connected even with prefersReducedMotion)
        renderer.render(scene, camera);
        if (!prefersReducedMotion) {
            requestAnimationFrame(animate);
        }
    }

    // Lightweight 2D fallback if WebGL is unavailable
    function initFallback2DCanvas(c) {
        const ctx = c.getContext('2d');
        if (!ctx) return;
        c.width = window.innerWidth;
        c.height = window.innerHeight;
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.15)';
        ctx.beginPath();
        ctx.arc(c.width * 0.7, c.height * 0.35, 140, 0, Math.PI * 2);
        ctx.stroke();
    }

    if (typeof THREE !== 'undefined') {
        bootScene();
    } else {
        window.addEventListener('load', bootScene);
    }
})();


// --- 1. Smooth Scrolling & GSAP Kinetic Synchronization Engine ---
const prefersReducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

if (typeof Lenis !== 'undefined' && !window.location.pathname.includes('/logging')) {
    const lenis = new Lenis({
        duration: 1.2,
        lerp: 0.09,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // easeOutExpo
        direction: 'vertical',
        gestureDirection: 'vertical',
        smoothWheel: true,
        smooth: true,
        mouseMultiplier: 1,
    });
    window.lenis = lenis;

    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        lenis.on('scroll', ScrollTrigger.update);
        gsap.ticker.add((time) => {
            lenis.raf(time * 1000);
        });
        gsap.ticker.lagSmoothing(0);
    } else {
        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);
    }
}

// --- 2. Kinetic Motion Engine & Advanced Choreography ---
if (typeof gsap !== 'undefined') {
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }

    // 2a. Masked Typographic Reveals (.reveal-text -> .reveal-text-inner)
    function initMaskedTypographicReveals() {
        if (prefersReducedMotion) return;

        const revealInners = gsap.utils.toArray('.reveal-text-inner');
        if (revealInners.length > 0) {
            gsap.from(revealInners, {
                yPercent: 105,
                rotateZ: 1.5,
                duration: 1.05,
                stagger: 0.065,
                ease: "power4.out",
                delay: 0.15
            });
        }
    }

    // 2b. CAD Hairline Grid Choreography (.grid-line-h and .grid-line-v)
    function initCadGridLines() {
        if (prefersReducedMotion) return;

        gsap.utils.toArray('.grid-line-h').forEach(line => {
            gsap.fromTo(line,
                { scaleX: 0 },
                {
                    scaleX: 1,
                    duration: 1.1,
                    ease: "expo.out",
                    scrollTrigger: {
                        trigger: line,
                        start: "top 92%",
                        toggleActions: "play none none none"
                    }
                }
            );
        });

        gsap.utils.toArray('.grid-line-v').forEach(line => {
            gsap.fromTo(line,
                { scaleY: 0 },
                {
                    scaleY: 1,
                    duration: 1.1,
                    ease: "expo.out",
                    scrollTrigger: {
                        trigger: line,
                        start: "top 92%",
                        toggleActions: "play none none none"
                    }
                }
            );
        });
    }

    // 2c. Scroll Velocity Transients on Kinetic Blocks (Edolus & Trionn effect)
    function initVelocityTransients() {
        if (prefersReducedMotion) return;

        const kineticBlocks = document.querySelectorAll('.kinetic-block');
        if (kineticBlocks.length === 0) return;

        let skewProxy = { skew: 0 };
        const setSkew = gsap.quickSetter(kineticBlocks, "skewY", "deg");
        const clampSkew = gsap.utils.clamp(-1.5, 1.5);

        if (window.lenis) {
            window.lenis.on('scroll', (e) => {
                const vel = (e.velocity || 0) * 0.12;
                if (Math.abs(vel) > 0.05) {
                    skewProxy.skew = clampSkew(vel);
                    gsap.to(skewProxy, {
                        skew: 0,
                        duration: 0.65,
                        ease: "power3.out",
                        overwrite: true,
                        onUpdate: () => setSkew(skewProxy.skew)
                    });
                }
            });
        }
    }

    // 2d. Parallax Media Scrubbing in Framed Windows
    function initParallaxMedia() {
        if (prefersReducedMotion) return;

        gsap.utils.toArray('.parallax-media').forEach(media => {
            gsap.fromTo(media,
                { yPercent: -7 },
                {
                    yPercent: 7,
                    ease: "none",
                    scrollTrigger: {
                        trigger: media.parentElement || media,
                        start: "top bottom",
                        end: "bottom top",
                        scrub: 0.6
                    }
                }
            );
        });
    }

    // 2e. Monospace Rapid Character-Decode Scramble (250ms)
    const CIPHER_CHARS = '0123456789ABCDEF#_//<>[]*~';
    function scrambleDecodeText(el) {
        if (!el || el.dataset.decoded === 'true' || prefersReducedMotion) return;
        el.dataset.decoded = 'true';
        const original = el.textContent;
        let iteration = 0;
        const totalChars = original.length;
        const interval = setInterval(() => {
            el.textContent = original
                .split('')
                .map((ch, idx) => {
                    if (ch === ' ' || ch === '/' || idx < iteration) return original[idx];
                    return CIPHER_CHARS[Math.floor(Math.random() * CIPHER_CHARS.length)];
                })
                .join('');
            iteration += 2;
            if (iteration >= totalChars + 2) {
                el.textContent = original;
                clearInterval(interval);
            }
        }, 22);
    }

    // 2f. Sticky Section Sub-Headers: Lock-in transient & Emerald LED pulse
    function initStickySectionHeaders() {
        const sections = document.querySelectorAll('.c2-chapter-section');
        sections.forEach(section => {
            const header = section.querySelector('.sec-sticky-header');
            if (!header) return;
            const label = header.querySelector('.sec-decode-label');

            ScrollTrigger.create({
                trigger: section,
                start: "top 25%",
                end: "bottom 25%",
                onEnter: () => {
                    header.classList.add('sec-pinned-active');
                    if (label) scrambleDecodeText(label);
                },
                onEnterBack: () => {
                    header.classList.add('sec-pinned-active');
                },
                onLeave: () => {
                    header.classList.remove('sec-pinned-active');
                },
                onLeaveBack: () => {
                    header.classList.remove('sec-pinned-active');
                }
            });
        });
    }

    // 2g. Live Telemetry Progress Bars & Numeric Count-up (SEC-03 Benchmarks)
    function initTelemetryCountersAndBars() {
        const benchmarkSection = document.getElementById('chapter-03');
        if (!benchmarkSection) return;

        ScrollTrigger.create({
            trigger: benchmarkSection,
            start: "top 75%",
            once: true,
            onEnter: () => {
                // Animate progress bars
                document.querySelectorAll('.benchmark-progress-bar').forEach(bar => {
                    const targetWidth = bar.getAttribute('data-progress') || '0';
                    gsap.fromTo(bar,
                        { width: '0%' },
                        {
                            width: `${targetWidth}%`,
                            duration: 1.35,
                            ease: "expo.out"
                        }
                    );
                });

                // Animate count-up numbers
                if (!prefersReducedMotion) {
                    document.querySelectorAll('.count-up-num').forEach(el => {
                        const target = parseInt(el.getAttribute('data-target'), 10);
                        if (isNaN(target)) return;
                        const obj = { val: 0 };
                        gsap.to(obj, {
                            val: target,
                            duration: 1.25,
                            ease: "power2.out",
                            onUpdate: () => {
                                el.textContent = Math.round(obj.val);
                            }
                        });
                    });
                }
            }
        });
    }

    // Run motion engine initializations
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initMaskedTypographicReveals();
            initCadGridLines();
            initVelocityTransients();
            initParallaxMedia();
            initStickySectionHeaders();
            initTelemetryCountersAndBars();
        });
    } else {
        initMaskedTypographicReveals();
        initCadGridLines();
        initVelocityTransients();
        initParallaxMedia();
        initStickySectionHeaders();
        initTelemetryCountersAndBars();
    }
}


// --- 3. Radial Cursor-Following Spotlight for Capability Cells (SEC-02) ---
(function initRadialCursorSpotlight() {
    const capCells = document.querySelectorAll('.cap-cell');
    if (capCells.length === 0 || !window.matchMedia('(pointer: fine)').matches) return;

    capCells.forEach(cell => {
        cell.addEventListener('mousemove', (e) => {
            const rect = cell.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            cell.style.setProperty('--mouse-x', `${x}px`);
            cell.style.setProperty('--mouse-y', `${y}px`);
        }, { passive: true });
    });
})();


// --- 4. Live Telemetry Stream Terminal with Syntax Highlighting (`telemetry_pulse.py`) ---
(function initTelemetryTerminal() {
    const codeDisplay = document.getElementById('c-code-display');
    const replayBtn = document.getElementById('c-replay-btn');
    const keyReadout = document.getElementById('active-key-readout');
    const compileStatus = document.getElementById('c-compile-status');
    const widget = document.getElementById('c-telemetry-widget');

    if (!codeDisplay || !widget) return;

    // Structured frames showcasing actual production codebase logic
    const TELEMETRY_STREAM_FRAMES = [
        // Frame 0: Real Edge Telemetry Ingestion View (portfolio/views.py)
        {
            status: "RUNTIME: VIEWS // INGESTION",
            readout: "ENDPOINT: POST /api/telemetry/heartbeat/",
            tokens: [
                { text: "@csrf_exempt\n", cls: "tok-kw" },
                { text: "def", cls: "tok-kw" }, { text: " telemetry_heartbeat", cls: "tok-fn" }, { text: "(request):\n" },
                { text: '    """Ingest hardware telemetry authenticated by edge token."""\n', cls: "tok-cmt" },
                { text: "    token = request.headers." }, { text: "get", cls: "tok-fn" }, { text: "(" }, { text: '"X-Telemetry-Token"', cls: "tok-str" }, { text: ")\n" },
                { text: "    if", cls: "tok-kw" }, { text: " token != config(" }, { text: '"TELEMETRY_TOKEN"', cls: "tok-str" }, { text: "):\n" },
                { text: "        return", cls: "tok-kw" }, { text: " JsonResponse({" }, { text: '"error"', cls: "tok-str" }, { text: ": " }, { text: '"Unauthorized"', cls: "tok-str" }, { text: "}, status=" }, { text: "401", cls: "tok-num" }, { text: ")\n\n" },
                { text: "    data = json." }, { text: "loads", cls: "tok-fn" }, { text: "(request.body." }, { text: "decode", cls: "tok-fn" }, { text: "(" }, { text: '"utf-8"', cls: "tok-str" }, { text: "))\n" },
                { text: "    hb, _ = NodeHeartbeat.objects." }, { text: "update_or_create", cls: "tok-fn" }, { text: "(\n" },
                { text: "        node_name=data." }, { text: "get", cls: "tok-fn" }, { text: "(" }, { text: '"node_name"', cls: "tok-str" }, { text: ", " }, { text: '"rpi-edge-scl"', cls: "tok-str" }, { text: "),\n" },
                { text: "        defaults={" }, { text: '"status"', cls: "tok-str" }, { text: ": data[" }, { text: '"status"', cls: "tok-str" }, { text: "], " }, { text: '"timestamp"', cls: "tok-str" }, { text: ": timezone." }, { text: "now", cls: "tok-fn" }, { text: "()},\n" },
                { text: "    )\n" },
                { text: "    return", cls: "tok-kw" }, { text: " JsonResponse({" }, { text: '"success"', cls: "tok-str" }, { text: ": " }, { text: "True", cls: "tok-kw" }, { text: ", " }, { text: '"node"', cls: "tok-str" }, { text: ": hb.node_name})" }
            ],
            pauseAfter: 2200
        },
        // Frame 1: Real Background Task for HackerRank Sync (portfolio/tasks.py)
        {
            status: "RUNTIME: TASKS // DAILY_SYNC",
            readout: "TASK: update_hackerrank_badges()",
            tokens: [
                { text: "@db_periodic_task", cls: "tok-kw" }, { text: "(" }, { text: "crontab", cls: "tok-fn" }, { text: "(minute=" }, { text: "'0'", cls: "tok-str" }, { text: ", hour=" }, { text: "'8'", cls: "tok-str" }, { text: "))\n" },
                { text: "def", cls: "tok-kw" }, { text: " update_hackerrank_badges", cls: "tok-fn" }, { text: "():\n" },
                { text: '    """Daily sync of verified algorithmic benchmarks at 08:00 SCL."""\n', cls: "tok-cmt" },
                { text: "    res = requests." }, { text: "get", cls: "tok-fn" }, { text: "(HACKERRANK_URL, timeout=" }, { text: "20", cls: "tok-num" }, { text: ")\n" },
                { text: "    res." }, { text: "raise_for_status", cls: "tok-fn" }, { text: "()\n\n" },
                { text: "    with", cls: "tok-kw" }, { text: " transaction." }, { text: "atomic", cls: "tok-fn" }, { text: "():\n" },
                { text: "        badges = " }, { text: "parse_and_save_badges", cls: "tok-fn" }, { text: "(\n" },
                { text: "            res." }, { text: "json", cls: "tok-fn" }, { text: "()." }, { text: "get", cls: "tok-fn" }, { text: "(" }, { text: '"models"', cls: "tok-str" }, { text: ", []),\n" },
                { text: "            snapshot_time=timezone." }, { text: "now", cls: "tok-fn" }, { text: "()\n" },
                { text: "        )\n" },
                { text: "    return", cls: "tok-kw" }, { text: " f" }, { text: '"Synced {len(badges)} verified badges"', cls: "tok-str" }
            ],
            pauseAfter: 2200
        },
        // Frame 2: Real Edge Node Ingestion Payload (JSON)
        {
            status: "STREAM: VERIFIED // HTTP 200",
            readout: "PAYLOAD: telemetry_heartbeat",
            tokens: [
                { text: "{\n" },
                { text: '  "node_name"', cls: "tok-str" }, { text: ': ' }, { text: '"rpi-edge-scl-01"', cls: "tok-str" }, { text: ",\n" },
                { text: '  "hardware"', cls: "tok-str" }, { text: ': ' }, { text: '"Raspberry Pi 5 (8GB ARM64)"', cls: "tok-str" }, { text: ",\n" },
                { text: '  "daemon"', cls: "tok-str" }, { text: ': ' }, { text: '"C++20 Native Telemetry Service"', cls: "tok-str" }, { text: ",\n" },
                { text: '  "auth"', cls: "tok-str" }, { text: ': ' }, { text: '"X-Telemetry-Token [VALIDATED]"', cls: "tok-kw" }, { text: ",\n" },
                { text: '  "cpu_temp"', cls: "tok-str" }, { text: ': ' }, { text: '"39.4°C"', cls: "tok-num" }, { text: ",\n" },
                { text: '  "memory_used"', cls: "tok-str" }, { text: ': ' }, { text: '"142MB / 8GB"', cls: "tok-num" }, { text: ",\n" },
                { text: '  "status"', cls: "tok-str" }, { text: ': ' }, { text: '"ONLINE // EDGE_HEALTHY"', cls: "tok-kw" }, { text: "\n" },
                { text: "}" }
            ],
            pauseAfter: 2400
        }
    ];

    let frameIndex = 0;
    let tokenIndex = 0;
    let charOffset = 0;
    let typingTimer = null;
    let isVisible = true;

    function renderTokens(currentTokens, upToTokenIdx, upToCharOffset) {
        codeDisplay.innerHTML = '';
        for (let i = 0; i <= upToTokenIdx && i < currentTokens.length; i++) {
            const tok = currentTokens[i];
            const span = document.createElement('span');
            if (tok.cls) span.className = tok.cls;

            if (i < upToTokenIdx) {
                span.textContent = tok.text;
            } else {
                span.textContent = tok.text.slice(0, upToCharOffset);
            }
            codeDisplay.appendChild(span);
        }
    }

    function stepTyping() {
        if (document.hidden || !isVisible) {
            typingTimer = setTimeout(stepTyping, 300);
            return;
        }

        const currentFrame = TELEMETRY_STREAM_FRAMES[frameIndex];
        const tokens = currentFrame.tokens;

        if (tokenIndex < tokens.length) {
            const currentTok = tokens[tokenIndex];
            charOffset++;
            renderTokens(tokens, tokenIndex, charOffset);

            let delay = 14 + Math.random() * 18;
            const currentChar = currentTok.text[charOffset - 1];
            if (currentChar === '\n') delay = 75;
            else if (currentChar === ':' || currentChar === ',') delay = 50;

            if (charOffset >= currentTok.text.length) {
                tokenIndex++;
                charOffset = 0;
            }

            typingTimer = setTimeout(stepTyping, delay);
        } else {
            // Frame completed
            if (compileStatus) compileStatus.textContent = currentFrame.status;
            if (keyReadout) keyReadout.textContent = currentFrame.readout;

            typingTimer = setTimeout(() => {
                if (prefersReducedMotion) return;
                const flushSpan = document.createElement('span');
                flushSpan.className = 'tok-cmt';
                flushSpan.textContent = "\n\n# -- Synced next telemetry frame --";
                codeDisplay.appendChild(flushSpan);
                if (compileStatus) compileStatus.textContent = "SYNCING NEXT FRAME...";

                typingTimer = setTimeout(() => {
                    frameIndex = (frameIndex + 1) % TELEMETRY_STREAM_FRAMES.length;
                    tokenIndex = 0;
                    charOffset = 0;
                    codeDisplay.innerHTML = '';
                    const nextFrame = TELEMETRY_STREAM_FRAMES[frameIndex];
                    if (compileStatus) compileStatus.textContent = nextFrame.status;
                    if (keyReadout) keyReadout.textContent = nextFrame.readout;
                    stepTyping();
                }, 400);
            }, currentFrame.pauseAfter);
        }
    }

    function startSequence() {
        clearTimeout(typingTimer);
        frameIndex = 0;
        tokenIndex = 0;
        charOffset = 0;
        codeDisplay.innerHTML = '';
        const firstFrame = TELEMETRY_STREAM_FRAMES[0];
        if (compileStatus) compileStatus.textContent = firstFrame.status;
        if (keyReadout) keyReadout.textContent = firstFrame.readout;

        if (prefersReducedMotion) {
            renderTokens(firstFrame.tokens, firstFrame.tokens.length, 0);
            return;
        }
        stepTyping();
    }

    if (replayBtn) {
        replayBtn.addEventListener('click', startSequence);
    }

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                isVisible = entry.isIntersecting;
            });
        }, { threshold: 0.1 });
        observer.observe(widget);
    }

    startSequence();
})();


// --- 5. Frontend Production Systems Filter with GSAP Animations ---
const filterBtns = document.querySelectorAll('.tech-filter-btn');
const projectCards = document.querySelectorAll('.project-card');
let activeFilter = null;

if (filterBtns.length > 0 && projectCards.length > 0) {
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tech = btn.getAttribute('data-tech');

            if (activeFilter === tech) {
                // Clear filter
                activeFilter = null;
                filterBtns.forEach(b => {
                    b.classList.remove('filter-active', 'border-accent', 'text-white');
                });
                projectCards.forEach(card => {
                    card.style.display = '';
                    requestAnimationFrame(() => card.classList.remove('filter-hidden'));
                });
                if (typeof ScrollTrigger !== 'undefined') setTimeout(() => ScrollTrigger.refresh(), 350);
            } else {
                // Apply filter
                activeFilter = tech;
                filterBtns.forEach(b => {
                    if (b === btn) {
                        b.classList.add('filter-active', 'border-accent', 'text-white');
                    } else {
                        b.classList.remove('filter-active', 'border-accent', 'text-white');
                    }
                });

                projectCards.forEach(card => {
                    const cardTechs = card.getAttribute('data-techs') || '';
                    if ((',' + cardTechs).includes(',' + tech + ',')) {
                        card.style.display = '';
                        requestAnimationFrame(() => card.classList.remove('filter-hidden'));
                    } else {
                        card.classList.add('filter-hidden');
                        setTimeout(() => {
                            if (activeFilter === tech) card.style.display = 'none';
                        }, 350);
                    }
                });
                if (typeof ScrollTrigger !== 'undefined') setTimeout(() => ScrollTrigger.refresh(), 350);
            }
        });
    });
}


// --- 6. Theme Switcher Persistence (Default: Pure Obsidian Carbon 'dracula') ---
const themeControllers = document.querySelectorAll('.theme-controller');
const htmlTag = document.documentElement;

const savedTheme = localStorage.getItem('theme_v3');
const initialTheme = (savedTheme === 'dracula' || savedTheme === 'lofi') ? savedTheme : 'dracula';
htmlTag.setAttribute('data-theme', initialTheme);

if (themeControllers.length > 0) {
    themeControllers.forEach(tc => {
        tc.checked = (initialTheme === 'dracula');
        tc.addEventListener('change', (e) => {
            const newTheme = e.target.checked ? 'dracula' : 'lofi';
            htmlTag.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme_v3', newTheme);
            themeControllers.forEach(other => {
                other.checked = e.target.checked;
            });
        });
    });
}


// --- 7. Snappy Chapter Navigation & Navigation Architecture ---
function initSnappyChapterNavigation() {
    const chapters = Array.from(document.querySelectorAll('.c2-chapter-section'));
    if (chapters.length === 0) return;

    // Enable CSS mode on body
    document.body.classList.add('c2-snapping-enabled');

    let currentChapterIndex = 0;

    // All chapters visible by default - natural scroll flow
    chapters.forEach((ch) => {
        ch.classList.add('c2-chapter-active');
        ch.classList.remove('c2-chapter-transitioning', 'c2-slide-up-exit', 'c2-slide-down-exit');
    });

    // 2. Core Transition: Smoothly scroll to target section without locking or hiding
    function goToChapter(targetIndex) {
        if (targetIndex < 0 || targetIndex >= chapters.length) return;
        const toChapter = chapters[targetIndex];
        if (!toChapter) return;

        currentChapterIndex = targetIndex;
        updateNavActive(toChapter.id);

        if (window.lenis) {
            window.lenis.scrollTo(toChapter, {
                duration: 0.85,
                easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t))
            });
        } else {
            window.scrollTo({
                top: toChapter.offsetTop,
                behavior: 'smooth'
            });
        }

        const targetId = toChapter.id;
        if (targetId && history.replaceState) {
            history.replaceState(null, '', '#' + targetId);
        }
    }

    // 3. Desktop Wheel Event handler (Natural scroll preserved)
    function handleWheel(e) {
        // Natural smooth scroll enabled; no e.preventDefault() trap
    }

    // 4. Section Navigator Sync (Hovering Sidebar on Desktop & Bottom Dock on Mobile)
    const navEl = document.getElementById('section-nav-sidebar');
    const navLinks = navEl ? Array.from(navEl.querySelectorAll('.sec-nav-link')) : [];
    const navPctEl = document.getElementById('section-nav-pct');

    function updateNavActive(activeId) {
        if (!navLinks.length) return;
        navLinks.forEach(link => {
            const targetId = link.getAttribute('data-section-target');
            if (targetId === activeId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const pct = Math.max(0, Math.min(100, Math.round((scrollTop / Math.max(1, scrollHeight)) * 100)));
        if (navPctEl) {
            navPctEl.textContent = String(pct).padStart(2, '0') + '%';
        }
    }, { passive: true });

    if ('IntersectionObserver' in window && navLinks.length) {
        const navObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && entry.intersectionRatio >= 0.25) {
                    updateNavActive(entry.target.id);
                }
            });
        }, {
            threshold: [0.25, 0.5]
        });
        chapters.forEach(ch => navObserver.observe(ch));
    }

    // 5. Navigation & Internal Anchor Link Delegation
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a[href*="#"]');
        if (!link) return;
        try {
            const url = new URL(link.href, window.location.href);
            if (url.pathname === window.location.pathname && url.hash) {
                const targetEl = document.querySelector(url.hash);
                if (targetEl) {
                    const chapter = targetEl.closest('.c2-chapter-section') || targetEl;
                    const targetIdx = chapters.indexOf(chapter);
                    if (targetIdx !== -1) {
                        e.preventDefault();
                        goToChapter(targetIdx);
                    }
                }
            }
        } catch (err) {
            // Ignore malformed URL
        }
    });
}

// Backwards-compatible alias for any template or script calling initMissionLifecycleHud
function initMissionLifecycleHud() {
    initSnappyChapterNavigation();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSnappyChapterNavigation);
} else {
    initSnappyChapterNavigation();
}

console.log(
    "%c🟢 SYSTEMS TELEMETRY ONLINE: Josué Leiva\n%c\nLooking under the hood? I like your style. \nTelematics Engineering student specializing in backend architecture, automation, flows, and human impact. \n\n👉 GitHub: https://github.com/josue-fourier\n👉 LinkedIn: https://linkedin.com/in/josuenicolas",
    "color: #10B981; font-size: 20px; font-weight: 800; font-family: 'JetBrains Mono', monospace;",
    "color: #94A3B8; font-size: 13px; font-family: 'JetBrains Mono', monospace; line-height: 1.5;"
);

