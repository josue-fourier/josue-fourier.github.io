/* Awwwards-grade interaction layer: preloader, cursor, magnetic buttons, hero parallax. */
(function () {
    'use strict';
    var root = document.documentElement;
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    // ---- Lazy Mermaid loader: downloads the ~3MB library only when a diagram exists ----
    (function mermaidLazy() {
        var loading = null;
        var src = (document.querySelector('meta[name="mermaid-src"]') || {}).content;
        function load() {
            if (window.mermaid) return Promise.resolve(window.mermaid);
            if (loading) return loading;
            loading = new Promise(function (resolve, reject) {
                var s = document.createElement('script');
                s.src = src; s.async = true;
                s.onload = function () { resolve(window.mermaid); };
                s.onerror = function () { loading = null; reject(new Error('mermaid failed to load')); };
                document.head.appendChild(s);
            });
            return loading;
        }
        window.renderMermaid = function (container) {
            container = container || document;
            var blocks = container.querySelectorAll('code.language-mermaid');
            var nodes = [];
            blocks.forEach(function (el) {
                var pre = el.parentElement;
                var div = document.createElement('div');
                div.className = 'mermaid';
                div.textContent = el.textContent;
                pre.replaceWith(div);
                nodes.push(div);
            });
            if (!nodes.length) return Promise.resolve();
            if (!src) return Promise.resolve();
            return load().then(function (m) {
                m.initialize({
                    startOnLoad: false,
                    theme: root.getAttribute('data-theme') === 'dracula' ? 'dark' : 'default',
                    fontFamily: 'JetBrains Mono'
                });
                return m.run({ nodes: nodes });
            }).catch(function (e) { console.warn(e); });
        };
    })();

    // Skip link should target whatever <main> this page has.
    var skip = document.querySelector('.skip-link');
    var main = document.querySelector('main');
    if (skip && main) {
        if (!main.id) main.id = 'main-content';
        skip.setAttribute('href', '#' + main.id);
    }

    // ---- Preloader (once per session, never on reduced motion) ----
    (function preloader() {
        var el = document.getElementById('preloader');
        if (!el) return;
        var seen = false;
        try { seen = sessionStorage.getItem('boot_seen') === '1'; } catch (e) {}
        if (reduced || seen) { el.remove(); return; }
        root.classList.add('js-preload');
        var num = document.getElementById('preloader-num');
        var fill = document.getElementById('preloader-fill');
        var start = performance.now();
        var MIN = 1100;
        var loaded = document.readyState === 'complete';
        window.addEventListener('load', function () { loaded = true; });
        var value = 0;
        function tick(now) {
            var t = Math.min((now - start) / MIN, 1);
            var target = loaded ? 100 : Math.min(92, t * 92);
            value += (target - value) * 0.12 + (loaded ? 1.2 : 0);
            if (value > 100) value = 100;
            var v = Math.round(value);
            if (num) num.textContent = String(v).padStart(3, '0');
            if (fill) fill.style.width = v + '%';
            if (v >= 100 && now - start > MIN) {
                el.classList.add('is-done');
                try { sessionStorage.setItem('boot_seen', '1'); } catch (e) {}
                setTimeout(function () { el.remove(); }, 1000);
                root.classList.add('boot-complete');
                return;
            }
            requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    })();

    // ---- Custom cursor ----
    (function cursor() {
        if (!finePointer || reduced) return;
        var dot = document.getElementById('cursor-dot');
        var ring = document.getElementById('cursor-ring');
        var label = document.getElementById('cursor-label');
        if (!dot || !ring) return;
        root.classList.add('has-custom-cursor');
        var mx = -100, my = -100, rx = -100, ry = -100;
        window.addEventListener('pointermove', function (e) {
            mx = e.clientX; my = e.clientY;
            dot.style.transform = 'translate3d(' + mx + 'px,' + my + 'px,0)';
            dot.classList.remove('is-hidden'); ring.classList.remove('is-hidden');
        }, { passive: true });
        document.addEventListener('mouseleave', function () {
            dot.classList.add('is-hidden'); ring.classList.add('is-hidden');
        });
        window.addEventListener('pointerdown', function () { ring.classList.add('is-down'); });
        window.addEventListener('pointerup', function () { ring.classList.remove('is-down'); });
        (function loop() {
            rx += (mx - rx) * 0.18; ry += (my - ry) * 0.18;
            ring.style.transform = 'translate3d(' + rx + 'px,' + ry + 'px,0)';
            requestAnimationFrame(loop);
        })();
        document.addEventListener('pointerover', function (e) {
            var view = e.target.closest && e.target.closest('.project-card');
            var link = e.target.closest && e.target.closest('a, button, [role="button"], input, select, textarea, .log-item');
            ring.classList.toggle('is-view', !!view && !link);
            ring.classList.toggle('is-link', !!link);
            if (label) label.textContent = (view && !link) ? 'VIEW' : '';
        });
    })();

    // ---- Magnetic buttons ----
    (function magnetic() {
        if (!finePointer || reduced) return;
        var els = document.querySelectorAll('.btn-sweep, .profile-portrait-frame, #cursor-none');
        els.forEach(function (el) {
            if (el.classList.contains('profile-portrait-frame')) return; // portrait has its own tilt
            el.setAttribute('data-magnetic', '');
            el.addEventListener('pointermove', function (e) {
                var r = el.getBoundingClientRect();
                var x = (e.clientX - (r.left + r.width / 2)) * 0.25;
                var y = (e.clientY - (r.top + r.height / 2)) * 0.35;
                el.style.transform = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px)';
            });
            el.addEventListener('pointerleave', function () { el.style.transform = ''; });
        });
    })();

    // ---- Hero title scroll-linked drift & fade ----
    (function heroDrift() {
        if (reduced) return;
        var title = document.getElementById('hero-title');
        if (!title) return;
        var ticking = false;
        window.addEventListener('scroll', function () {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(function () {
                var y = Math.min(window.scrollY, window.innerHeight);
                title.style.transform = 'translate3d(0,' + (y * 0.18).toFixed(1) + 'px,0)';
                title.style.opacity = String(Math.max(0, 1 - y / (window.innerHeight * 1.1)));
                ticking = false;
            });
        }, { passive: true });
    })();
})();
