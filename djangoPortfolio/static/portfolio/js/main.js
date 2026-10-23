const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

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

    // 2m. Hero Portrait: pointer-driven 3D tilt & glare, plus Umami scroll-chapter / theme events
    function initPortraitFx() {
        const frame = document.querySelector('.profile-portrait-frame');
        if (!frame || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        frame.addEventListener('pointermove', (e) => {
            const r = frame.getBoundingClientRect();
            const px = (e.clientX - r.left) / r.width;
            const py = (e.clientY - r.top) / r.height;
            frame.style.setProperty('--tilt-y', ((px - 0.5) * 14).toFixed(2) + 'deg');
            frame.style.setProperty('--tilt-x', ((0.5 - py) * 14).toFixed(2) + 'deg');
            frame.style.setProperty('--glare-x', (px * 100).toFixed(1) + '%');
            frame.style.setProperty('--glare-y', (py * 100).toFixed(1) + '%');
        });
        frame.addEventListener('pointerleave', () => {
            frame.style.setProperty('--tilt-x', '0deg');
            frame.style.setProperty('--tilt-y', '0deg');
        });
    }
    window.initPortraitFx = initPortraitFx;
    initPortraitFx();

    function track(name, data) {
        if (window.umami && typeof window.umami.track === 'function') {
            window.umami.track(name, data);
        }
    }
    window.trackUmami = track;

    // Chapter views (fires once per chapter when >=50% visible)
    if ('IntersectionObserver' in window) {
        const seen = new Set();
        const chapterObs = new IntersectionObserver((entries) => {
            entries.forEach(en => {
                if (en.isIntersecting && !seen.has(en.target.id)) {
                    seen.add(en.target.id);
                    track('chapter-view', { chapter: en.target.id, title: en.target.dataset.chapterTitle || '' });
                }
            });
        }, { threshold: 0.4 });
        document.querySelectorAll('section[data-chapter]').forEach(s => chapterObs.observe(s));
    }

    // Scroll depth milestones
    (function () {
        const marks = [25, 50, 75, 100];
        const fired = new Set();
        window.addEventListener('scroll', () => {
            const h = document.documentElement.scrollHeight - window.innerHeight;
            if (h <= 0) return;
            const pct = (window.scrollY / h) * 100;
            marks.forEach(m => {
                if (pct >= m - 1 && !fired.has(m)) { fired.add(m); track('scroll-depth', { percent: m }); }
            });
        }, { passive: true });
    })();

    // Sidebar chapter nav & theme/language toggles (delegated)
    document.addEventListener('click', (e) => {
        const nav = e.target.closest('.sec-nav-link');
        if (nav) track('chapter-nav-click', { target: nav.dataset.sectionTarget || '' });
        const theme = e.target.closest('[data-theme-toggle], #theme-toggle');
        if (theme) track('theme-toggle');
    });

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

    // Expose for external orchestration & testing
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
        el.textContent = isDark ? el.dataset.labelDark : el.dataset.labelLight;
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

