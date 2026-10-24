/* Portrait reveal: the photo first appears as scrambling ASCII that settles into its shape, then dissolves into the real image.
   Plays once when the portrait scrolls into view and again on hover. Canvas overlay; the <img> underneath is untouched. */
(function () {
    'use strict';
    var frame = document.querySelector('.profile-portrait-frame');
    var img = frame && frame.querySelector('.portrait-img');
    if (!img || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var CELL = 6, RAMP = ' .:-=+*#%@', SCRAMBLE = '01<>/\\{}[]#$%&*+=';
    var cv = document.createElement('canvas');
    cv.className = 'portrait-ascii';
    cv.setAttribute('aria-hidden', 'true');
    frame.appendChild(cv);
    var ctx = cv.getContext('2d'), grid = null, raf = 0, t0 = 0;
    var SETTLE = 1300, HOLD = 350, FADE = 900;

    function sample() { // luminance per cell, from a tiny offscreen copy of the photo
        var w = frame.clientWidth, h = frame.clientHeight;
        var cols = Math.max(1, Math.round(w / CELL)), rows = Math.max(1, Math.round(h / CELL));
        var o = document.createElement('canvas'); o.width = cols; o.height = rows;
        var c = o.getContext('2d'); c.drawImage(img, 0, 0, cols, rows);
        var d = c.getImageData(0, 0, cols, rows).data, lum = new Float32Array(cols * rows), at = new Float32Array(cols * rows);
        for (var i = 0; i < lum.length; i++) {
            lum[i] = (0.299 * d[i * 4] + 0.587 * d[i * 4 + 1] + 0.114 * d[i * 4 + 2]) / 255;
            at[i] = (i % cols) / cols * 0.5 + Math.random() * 0.5; // settle time: left-to-right sweep with jitter
        }
        grid = { cols: cols, rows: rows, lum: lum, at: at, w: w, h: h };
    }
    function draw(now) {
        var e = now - t0, g = grid, dpr = Math.min(window.devicePixelRatio || 1, 2);
        var light = document.documentElement.getAttribute('data-theme') === 'lofi';
        if (cv.width !== Math.round(g.w * dpr)) { cv.width = Math.round(g.w * dpr); cv.height = Math.round(g.h * dpr); }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.fillStyle = light ? '#f3faf7' : '#050508'; ctx.fillRect(0, 0, g.w, g.h);
        ctx.font = (CELL + 3) + 'px "JetBrains Mono", monospace'; ctx.textBaseline = 'top';
        var u = Math.min(1, e / SETTLE);
        for (var r = 0; r < g.rows; r++) for (var c = 0; c < g.cols; c++) {
            var i = r * g.cols + c, l = g.lum[i], settled = u >= g.at[i];
            var ch = settled ? RAMP[Math.min(RAMP.length - 1, Math.floor(l * RAMP.length))] : SCRAMBLE[(Math.random() * SCRAMBLE.length) | 0];
            if (ch === ' ') continue;
            ctx.fillStyle = 'rgba(' + (light ? '4,120,87' : '52,211,153') + ',' + (settled ? 0.35 + 0.65 * l : 0.35) + ')';
            ctx.fillText(ch, c * CELL, r * CELL - 1);
        }
        cv.style.opacity = e < SETTLE + HOLD ? 1 : Math.max(0, 1 - (e - SETTLE - HOLD) / FADE);
        if (e < SETTLE + HOLD + FADE) raf = requestAnimationFrame(draw); else { raf = 0; cv.style.opacity = 0; }
    }
    function play() {
        if (!img.naturalWidth) return;
        cancelAnimationFrame(raf); sample(); t0 = performance.now(); cv.style.opacity = 1;
        raf = requestAnimationFrame(draw);
    }
    function ready(fn) { if (img.complete) fn(); else img.addEventListener('load', fn, { once: true }); }

    cv.style.opacity = 0;
    ready(function () {
        var io = new IntersectionObserver(function (e) { if (e[0].isIntersecting) { io.disconnect(); setTimeout(play, 500); } }, { threshold: 0.6 });
        io.observe(frame);
    });
    frame.addEventListener('mouseenter', function () { if (!raf) play(); });
})();
