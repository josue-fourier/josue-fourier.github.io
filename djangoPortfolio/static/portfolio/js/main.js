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

if (typeof Lenis !== 'undefined') {
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

    // 2e. Monospace Rapid Character-Decode Scramble (Cryptographic Scramble on Hover & View)
    const CIPHER_CHARS = '0123456789ABCDEF#_//<>[]*~';
    function scrambleDecodeText(el, force = false) {
        if (!el || prefersReducedMotion) return;
        if (el.dataset.animating === 'true') return;

        if (!el.dataset.originalText) {
            el.dataset.originalText = el.textContent.trim();
        }
        const original = el.dataset.originalText;
        if (!original) return;

        el.dataset.animating = 'true';
        let iteration = 0;
        const totalChars = original.length;

        if (el._scrambleTimer) clearInterval(el._scrambleTimer);

        el._scrambleTimer = setInterval(() => {
            el.textContent = original
                .split('')
                .map((ch, idx) => {
                    if (ch === ' ' || ch === '/' || ch === '-' || ch === '|' || idx < iteration) {
                        return original[idx];
                    }
                    return CIPHER_CHARS[Math.floor(Math.random() * CIPHER_CHARS.length)];
                })
                .join('');

            iteration += 1.5;
            if (iteration >= totalChars + 2) {
                el.textContent = original;
                el.dataset.animating = 'false';
                clearInterval(el._scrambleTimer);
                el._scrambleTimer = null;
            }
        }, 22);
    }

    function initCryptographicScramble() {
        const scrambleEls = document.querySelectorAll('[data-scramble="true"]');
        scrambleEls.forEach(el => {
            if (!el.dataset.originalText) {
                el.dataset.originalText = el.textContent.trim();
            }
            el.addEventListener('mouseenter', () => {
                scrambleDecodeText(el, true);
            });
        });

        const heroTitle = document.getElementById('hero-title');
        if (heroTitle) {
            heroTitle.addEventListener('mouseenter', () => {
                heroTitle.querySelectorAll('[data-scramble="true"]').forEach(el => {
                    scrambleDecodeText(el, true);
                });
            });
        }

        if ('IntersectionObserver' in window) {
            const obs = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (!entry.target.dataset.kineticScrub) {
                            scrambleDecodeText(entry.target);
                        }
                        obs.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15 });
            scrambleEls.forEach(el => obs.observe(el));
        }
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
                    if (label && !label.dataset.kineticScrub) scrambleDecodeText(label);
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

    // 2g. Live Telemetry Progress Bars & Numeric Count-up (SEC-02 Benchmarks)
    function initTelemetryCountersAndBars() {
        const benchmarkSection = document.getElementById('chapter-02') || document.getElementById('chapter-03');
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

    // 2h. Word-by-Word Scroll Scrub on Hero Stance (#hero-stance-scrub - Ownitt style)
    function initHeroStanceScrub() {
        const stance = document.getElementById('hero-stance-scrub');
        if (!stance) return;

        const fragment = document.createDocumentFragment();
        const childNodes = Array.from(stance.childNodes);
        const wordsList = [];

        childNodes.forEach(node => {
            if (node.nodeType === Node.TEXT_NODE) {
                const tokens = node.textContent.split(/(\s+)/);
                tokens.forEach(token => {
                    if (!token) return;
                    if (/^\s+$/.test(token)) {
                        fragment.appendChild(document.createTextNode(token));
                    } else {
                        const span = document.createElement('span');
                        span.className = 'stance-word';
                        span.textContent = token;
                        fragment.appendChild(span);
                        wordsList.push(span);
                    }
                });
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                const isStrong = node.tagName.toLowerCase() === 'strong';
                const tokens = node.textContent.split(/(\s+)/);
                tokens.forEach(token => {
                    if (!token) return;
                    if (/^\s+$/.test(token)) {
                        fragment.appendChild(document.createTextNode(token));
                    } else {
                        const span = document.createElement('span');
                        span.className = 'stance-word' + (isStrong ? ' highlight' : '');
                        span.textContent = token;
                        fragment.appendChild(span);
                        wordsList.push(span);
                    }
                });
            }
        });

        stance.textContent = '';
        stance.appendChild(fragment);

        function updateScrub() {
            if (prefersReducedMotion) {
                wordsList.forEach(w => w.classList.add('active'));
                return;
            }

            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
            const scrubProgress = Math.min(1, Math.max(0, scrollY / 240));
            const activeCount = Math.floor(scrubProgress * wordsList.length);

            const threshold = Math.max(3, activeCount);
            wordsList.forEach((word, idx) => {
                if (idx < threshold) {
                    word.classList.add('active');
                } else {
                    word.classList.remove('active');
                }
            });
        }

        window.addEventListener('scroll', updateScrub, { passive: true });
        if (window.lenis) {
            window.lenis.on('scroll', updateScrub);
        }
        updateScrub();
    }

    // 2i. Mechanical Numeric Reel Odometer (Trionn style slot reels)
    function setMechanicalReel(el, valueStr) {
        if (!el) return;
        const chars = String(valueStr).split('');
        let digits = el.querySelectorAll('.mech-reel-digit');

        if (digits.length !== chars.length) {
            el.innerHTML = '';
            chars.forEach(ch => {
                const digitContainer = document.createElement('span');
                digitContainer.className = 'mech-reel-digit';

                if (/\d/.test(ch)) {
                    const strip = document.createElement('span');
                    strip.className = 'mech-reel-strip';
                    for (let i = 0; i <= 9; i++) {
                        const numSpan = document.createElement('span');
                        numSpan.className = 'mech-reel-char';
                        numSpan.textContent = i;
                        strip.appendChild(numSpan);
                    }
                    digitContainer.appendChild(strip);
                } else {
                    const charSpan = document.createElement('span');
                    charSpan.className = 'mech-reel-char';
                    charSpan.textContent = ch;
                    digitContainer.appendChild(charSpan);
                }
                el.appendChild(digitContainer);
            });
            digits = el.querySelectorAll('.mech-reel-digit');
        }

        chars.forEach((ch, idx) => {
            const digitContainer = digits[idx];
            if (!digitContainer) return;
            const strip = digitContainer.querySelector('.mech-reel-strip');
            if (strip && /\d/.test(ch)) {
                const digitVal = parseInt(ch, 10);
                strip.style.transform = `translateY(-${digitVal * 10}%)`;
            }
        });
    }
    window.setMechanicalReel = setMechanicalReel;

    function initMechanicalReels() {
        const reels = document.querySelectorAll('.mech-reel');
        reels.forEach(reel => {
            if (reel.id === 'section-nav-pct') return;
            const targetVal = reel.getAttribute('data-reel') || reel.textContent.trim();
            if (targetVal) {
                const initialZero = targetVal.replace(/\d/g, '0');
                setMechanicalReel(reel, initialZero);

                if ('IntersectionObserver' in window) {
                    const obs = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                setTimeout(() => {
                                    setMechanicalReel(reel, targetVal);
                                }, 120);
                                obs.unobserve(entry.target);
                            }
                        });
                    }, { threshold: 0.1 });
                    obs.observe(reel);
                } else {
                    setMechanicalReel(reel, targetVal);
                }
            }
        });
    }

    // 2j. Dual-Layer Character Split Hovers (Trionn clone)
    function initCharSplitLinks() {
        const links = document.querySelectorAll('#top-telemetry-bar nav a, .char-split-link');
        links.forEach(link => {
            if (link.querySelector('.char-split-track')) return;
            const text = link.textContent.trim();
            if (!text) return;

            link.classList.add('char-split-link');
            link.innerHTML = `
                <span class="char-split-track">
                    <span class="char-split-top">${text}</span>
                    <span class="char-split-bottom">${text}</span>
                </span>
            `;
        });
    }

    // 2k. Mobile Hero Segmented Switcher (< lg screens)
    function initHeroMobileTabs() {
        const tabCap = document.getElementById('hero-tab-capabilities');
        const tabTelem = document.getElementById('hero-tab-telemetry');
        const panelCap = document.getElementById('hero-panel-capabilities');
        const panelTelem = document.getElementById('hero-panel-telemetry');

        if (!tabCap || !tabTelem || !panelCap || !panelTelem) return;

        function setTab(activeTab) {
            if (activeTab === 'capabilities') {
                panelCap.classList.remove('hidden');
                panelCap.classList.add('block');
                panelTelem.classList.add('hidden');
                panelTelem.classList.remove('flex');

                tabCap.classList.add('text-emerald-400', 'border-emerald-500', 'bg-white/[0.02]');
                tabCap.classList.remove('text-zinc-500', 'border-transparent');

                tabTelem.classList.remove('text-emerald-400', 'border-emerald-500', 'bg-white/[0.02]');
                tabTelem.classList.add('text-zinc-500', 'border-transparent');
            } else {
                panelCap.classList.add('hidden');
                panelCap.classList.remove('block');
                panelTelem.classList.remove('hidden');
                panelTelem.classList.add('flex');

                tabTelem.classList.add('text-emerald-400', 'border-emerald-500', 'bg-white/[0.02]');
                tabTelem.classList.remove('text-zinc-500', 'border-transparent');

                tabCap.classList.remove('text-emerald-400', 'border-emerald-500', 'bg-white/[0.02]');
                tabCap.classList.add('text-zinc-500', 'border-transparent');
            }
        }

        tabCap.addEventListener('click', () => setTab('capabilities'));
        tabTelem.addEventListener('click', () => setTab('telemetry'));
    }

    // 2l. Skills Progressive Disclosure (+N MORE / LESS)
    function initSkillExpander() {
        const expandBtns = document.querySelectorAll('.skill-expand-btn');
        expandBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const parent = btn.closest('.cap-cell');
                if (!parent) return;
                const hiddenSkills = parent.querySelectorAll('.extra-skill');
                const isExpanded = btn.getAttribute('data-expanded') === 'true';

                if (isExpanded) {
                    hiddenSkills.forEach(s => s.classList.add('hidden'));
                    btn.setAttribute('data-expanded', 'false');
                    const count = btn.getAttribute('data-count') || '';
                    btn.textContent = `+${count} MORE`;
                } else {
                    hiddenSkills.forEach(s => s.classList.remove('hidden'));
                    btn.setAttribute('data-expanded', 'true');
                    btn.textContent = 'LESS';
                }
            });
        });
    }

    // 2m. Dragonfly2-Inspired Chapter Header Kinetic Decode on Scroll Scrub
    function initScrollScrubKineticDecode() {
        const scrubEls = document.querySelectorAll('[data-kinetic-scrub="true"]');
        if (!scrubEls.length) return;

        const CIPHER_GLYPHS = '0123456789ABCDEF#_//<>[]*~§$%&¥ΞΨΩΔλμ';

        scrubEls.forEach(el => {
            if (!el.dataset.targetText) {
                el.dataset.targetText = el.textContent.trim();
            }
            // Allow manual hover scramble
            el.addEventListener('mouseenter', () => {
                if (typeof scrambleDecodeText === 'function') {
                    scrambleDecodeText(el, true);
                }
            });
        });

        let ticking = false;

        function updateKineticScrub() {
            if (prefersReducedMotion) {
                scrubEls.forEach(el => {
                    const target = el.dataset.targetText || el.textContent.trim();
                    if (el.textContent !== target) el.textContent = target;
                });
                return;
            }

            const vh = window.innerHeight;
            const entryStart = vh * 0.88;
            const entryEnd = Math.min(vh * 0.28, 140);

            scrubEls.forEach(el => {
                if (el.dataset.animating === 'true') return; // let hover animation finish

                const section = el.closest('.c2-chapter-section') || el.closest('section') || el;
                const rect = section.getBoundingClientRect();

                let progress = 0;
                if (rect.top <= entryEnd) {
                    progress = 1.0;
                } else if (rect.top >= entryStart) {
                    progress = 0.0;
                } else {
                    progress = 1.0 - (rect.top - entryEnd) / (entryStart - entryEnd);
                }
                progress = Math.max(0, Math.min(1, progress));

                const target = el.dataset.targetText || el.textContent.trim();
                const totalLen = target.length;

                if (progress >= 1.0) {
                    if (el.textContent !== target) {
                        el.textContent = target;
                    }
                    return;
                }

                const solvedCount = Math.floor(progress * totalLen);
                let result = '';

                for (let i = 0; i < totalLen; i++) {
                    const char = target[i];
                    if (char === ' ' || char === '/' || char === '-' || char === '|' || char === ':' || char === '#') {
                        result += char;
                    } else if (i < solvedCount) {
                        result += char;
                    } else if (i === solvedCount && progress > 0) {
                        result += CIPHER_GLYPHS[Math.floor(Math.random() * CIPHER_GLYPHS.length)];
                    } else {
                        const code = target.charCodeAt(i);
                        const glyphIdx = (code * 11 + i * 7 + Math.floor(progress * 13)) % CIPHER_GLYPHS.length;
                        result += CIPHER_GLYPHS[glyphIdx];
                    }
                }

                el.textContent = result;
            });

            ticking = false;
        }

        function onScroll() {
            if (!ticking) {
                requestAnimationFrame(updateKineticScrub);
                ticking = true;
            }
        }

        window.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('resize', onScroll, { passive: true });
        updateKineticScrub();
    }

    // 2n. Scroll-Driven Fourier Harmonic Synthesizer Engine (Concept A // F0ur13r Harmonic Synthesis)
    function initFourierHarmonicSynthesizer() {
        const canvas = document.getElementById('fourier-waveform-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const panel = document.getElementById('fourier-harmonic-panel');
        const countEl = document.getElementById('fourier-harmonic-count');
        const freqEl = document.getElementById('fourier-freq-readout');
        const approxEl = document.getElementById('fourier-approx-readout');
        const scrubPctEl = document.getElementById('fourier-scrub-pct');

        let time = 0;
        let baseFreq = 440;
        let currentFreq = 440;
        let targetFreq = 440;
        let currentHarmonics = 1;
        let width = 0;
        let height = 0;

        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            width = rect.width;
            height = rect.height;
            canvas.width = Math.round(width * dpr);
            canvas.height = Math.round(height * dpr);
            if (typeof ctx.resetTransform === 'function') {
                ctx.resetTransform();
            } else {
                ctx.setTransform(1, 0, 0, 1, 0, 0);
            }
            ctx.scale(dpr, dpr);
        }

        resizeCanvas();
        window.addEventListener('resize', resizeCanvas, { passive: true });

        // Interactive Frequency Modulation on Hover / Pointer Movement
        if (panel) {
            panel.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                const relX = Math.max(0, Math.min(1, (e.clientX - rect.left) / (rect.width || 1)));
                targetFreq = 380 + relX * 140; // 380 Hz to 520 Hz
            }, { passive: true });

            panel.addEventListener('mouseleave', () => {
                targetFreq = baseFreq;
            });
        }

        // Scroll Scrub: Maps page progress into odd harmonic count (N = 1, 3, 5, 7, 9, 11, 13)
        const harmonicSteps = [1, 3, 5, 7, 9, 11, 13];
        function updateScrollState() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const totalProgress = Math.max(0, Math.min(1, scrollTop / Math.max(1, scrollHeight)));

            const pctFormatted = Math.round(totalProgress * 100);
            if (scrubPctEl) {
                scrubPctEl.textContent = String(pctFormatted).padStart(2, '0') + '%';
            }

            const stepIdx = Math.min(harmonicSteps.length - 1, Math.floor(totalProgress * harmonicSteps.length));
            currentHarmonics = harmonicSteps[stepIdx];

            if (countEl) {
                countEl.textContent = `N = ${currentHarmonics} HARMONIC${currentHarmonics > 1 ? 'S' : ''}`;
            }

            if (approxEl) {
                if (currentHarmonics === 1) {
                    approxEl.textContent = 'SINE FUNDAMENTAL';
                } else if (currentHarmonics < 7) {
                    approxEl.textContent = `ODD HARMONIC N=${currentHarmonics}`;
                } else if (currentHarmonics < 13) {
                    approxEl.textContent = `PARTIAL SQUARE (N=${currentHarmonics})`;
                } else {
                    approxEl.textContent = 'SQUARE WAVE (GIBBS)';
                }
            }
        }

        window.addEventListener('scroll', updateScrollState, { passive: true });
        updateScrollState();

        // Render Loop
        function render() {
            if (!width || !height) {
                resizeCanvas();
            }

            // Smooth frequency interpolation
            currentFreq += (targetFreq - currentFreq) * 0.08;
            if (freqEl) {
                freqEl.textContent = currentFreq.toFixed(2) + ' Hz';
            }

            const isLight = document.documentElement.getAttribute('data-theme') === 'lofi';

            ctx.clearRect(0, 0, width, height);

            const centerY = height / 2;
            const amplitude = height * 0.36;

            // 1. Background hairline calibration grid
            ctx.lineWidth = 1;
            ctx.strokeStyle = isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.06)';

            ctx.beginPath();
            ctx.moveTo(0, centerY);
            ctx.lineTo(width, centerY);
            ctx.moveTo(0, centerY - amplitude);
            ctx.lineTo(width, centerY - amplitude);
            ctx.moveTo(0, centerY + amplitude);
            ctx.lineTo(width, centerY + amplitude);
            ctx.stroke();

            const stepX = width / 12;
            ctx.beginPath();
            for (let x = stepX; x < width; x += stepX) {
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
            }
            ctx.stroke();

            // 2. Odd harmonic constituent sub-waves
            const numHarmonicsCount = Math.floor((currentHarmonics + 1) / 2);
            const fundamentalAngularFreq = (2 * Math.PI * (currentFreq / 260));

            if (numHarmonicsCount > 1) {
                for (let k = 1; k <= numHarmonicsCount; k++) {
                    const n = 2 * k - 1;
                    const harmAmp = (amplitude * (4 / Math.PI)) / n;
                    ctx.beginPath();
                    ctx.lineWidth = 1;
                    ctx.strokeStyle = isLight ? 'rgba(2, 132, 199, 0.22)' : 'rgba(6, 182, 212, 0.25)';
                    for (let px = 0; px <= width; px += 2) {
                        const t = (px / width) * 4 + time;
                        const py = centerY - harmAmp * Math.sin(n * fundamentalAngularFreq * 0.12 * t);
                        if (px === 0) ctx.moveTo(px, py);
                        else ctx.lineTo(px, py);
                    }
                    ctx.stroke();
                }
            }

            // 3. Composite Synthesized Fourier Waveform
            ctx.beginPath();
            ctx.lineWidth = 2.2;
            ctx.strokeStyle = isLight ? '#059669' : '#10B981';

            for (let px = 0; px <= width; px += 1.5) {
                const t = (px / width) * 4 + time;
                let sum = 0;
                for (let k = 1; k <= numHarmonicsCount; k++) {
                    const n = 2 * k - 1;
                    sum += Math.sin(n * fundamentalAngularFreq * 0.12 * t) / n;
                }
                const y = centerY - (amplitude * (4 / Math.PI)) * sum;
                if (px === 0) ctx.moveTo(px, y);
                else ctx.lineTo(px, y);
            }
            ctx.stroke();

            if (!prefersReducedMotion) {
                time += 0.032;
            }

            requestAnimationFrame(render);
        }

        render();
    }

    // Expose for external orchestration & testing
    window.initFourierHarmonicSynthesizer = initFourierHarmonicSynthesizer;
    window.initScrollScrubKineticDecode = initScrollScrubKineticDecode;

    // Run motion engine initializations
    function runAllMotionInitializers() {
        initMaskedTypographicReveals();
        initCadGridLines();
        initVelocityTransients();
        initParallaxMedia();
        initStickySectionHeaders();
        initTelemetryCountersAndBars();
        initCryptographicScramble();
        initHeroStanceScrub();
        initMechanicalReels();
        initCharSplitLinks();
        initHeroMobileTabs();
        initSkillExpander();
        initScrollScrubKineticDecode();
        initFourierHarmonicSynthesizer();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runAllMotionInitializers);
    } else {
        runAllMotionInitializers();
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


// --- 6. Theme Switcher Persistence (Default: Pure Light Mode 'lofi') ---
const themeControllers = document.querySelectorAll('.theme-controller');
const htmlTag = document.documentElement;

function updateThemeUI(theme) {
    const isDark = (theme === 'dracula');
    document.querySelectorAll('.theme-icon-sun').forEach(el => el.classList.toggle('hidden', isDark));
    document.querySelectorAll('.theme-icon-moon').forEach(el => el.classList.toggle('hidden', !isDark));
    document.querySelectorAll('.theme-text-label').forEach(el => {
        el.textContent = isDark ? 'DARK' : 'LIGHT';
    });
}

const savedTheme = localStorage.getItem('theme_v3');
const initialTheme = (savedTheme === 'dracula' || savedTheme === 'lofi') ? savedTheme : 'lofi';
htmlTag.setAttribute('data-theme', initialTheme);
updateThemeUI(initialTheme);

if (themeControllers.length > 0) {
    themeControllers.forEach(tc => {
        tc.checked = (initialTheme === 'dracula');
        tc.addEventListener('change', (e) => {
            const newTheme = e.target.checked ? 'dracula' : 'lofi';
            htmlTag.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme_v3', newTheme);
            updateThemeUI(newTheme);
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

    if (navPctEl) {
        if (typeof window.setMechanicalReel === 'function') {
            window.setMechanicalReel(navPctEl, '00%');
        } else {
            navPctEl.textContent = '00%';
        }
    }

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const pct = Math.max(0, Math.min(100, Math.round((scrollTop / Math.max(1, scrollHeight)) * 100)));
        if (navPctEl) {
            const formattedPct = String(pct).padStart(2, '0') + '%';
            if (typeof window.setMechanicalReel === 'function') {
                window.setMechanicalReel(navPctEl, formattedPct);
            } else {
                navPctEl.textContent = formattedPct;
            }
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

