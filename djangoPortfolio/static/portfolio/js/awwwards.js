/* Interaction layer: lazy Mermaid loader, email links, hero parallax. */
(function () {
    'use strict';
    var root = document.documentElement;
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

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

    // ---- Email: assembled at runtime so the address never appears in the HTML ----
    document.querySelectorAll('.js-email').forEach(function (el) {
        var addr = el.getAttribute('data-u') + '@' + el.getAttribute('data-d');
        el.href = 'mailto:' + addr;
        el.title = addr;
        if (el.hasAttribute('data-show')) el.textContent = addr;
    });

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
