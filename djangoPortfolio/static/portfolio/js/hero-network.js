/* Hero signature: a quiet mesh of nodes with packets drifting along the links.
   Two nodes are real: "rpi" (lit while the Raspberry Pi heartbeat is recent) and "ntfy"
   (fires a packet chain ntfy -> srv -> rpi carrying the latest notification). */
(function () {
    'use strict';
    var canvas = document.getElementById('net-canvas');
    var caption = document.getElementById('net-caption');
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var rpiStatus = canvas.dataset.rpiStatus || '', ntfyMsg = canvas.dataset.ntfy || '';
    var rpiOnline = !!canvas.dataset.rpiName;
    var MONO = '10px "JetBrains Mono", monospace';

    // Normalised layout; 0 = ntfy, 1 = srv, 2 = rpi, the rest are anonymous mesh nodes.
    var N = [[.1, .86], [.44, .7], [.8, .8], [.08, .5], [.3, .42], [.6, .5], [.9, .55], [.2, .15],
             [.5, .2], [.75, .12], [.95, .3], [.36, .92], [.62, .94]].map(function (n) { return { x: n[0], y: n[1], glow: 0 }; });
    var E = [[0, 1], [1, 2]];
    N.forEach(function (n, i) {
        N.map(function (m, j) { return { j: j, d: Math.hypot(n.x - m.x, n.y - m.y) }; })
            .sort(function (a, b) { return a.d - b.d; }).slice(1, 3).forEach(function (m) {
                if (!E.some(function (e) { return (e[0] === i && e[1] === m.j) || (e[0] === m.j && e[1] === i); })) E.push([i, m.j]);
            });
    });

    var pulses = [], last = 0, nextPulse = 0, nextChain = 3000, chainText = 0, nextCaption = 0, raf = 0, paused = false, visible = true;

    function short(s, n) { return s.length > n ? s.slice(0, n) + '…' : s; }
    function palette() {
        var light = document.documentElement.getAttribute('data-theme') === 'lofi';
        return light
            ? { node: 'rgba(15,23,42,0.22)', link: 'rgba(15,23,42,0.07)', rgb: '4,120,87', head: '#047857', text: 'rgba(15,23,42,0.55)' }
            : { node: 'rgba(255,255,255,0.2)', link: 'rgba(255,255,255,0.05)', rgb: '16,185,129', head: '#34d399', text: 'rgba(255,255,255,0.45)' };
    }
    function size() {
        var r = canvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(r.width * dpr); canvas.height = Math.round(r.height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function xy(n, r) { var pad = 28; return [pad + n.x * (r.width - 2 * pad), pad + n.y * (r.height - 2 * pad)]; }
    function ease(u) { return u * u * (3 - 2 * u); }
    function send(a, b, dur, delay, strong) { pulses.push({ a: a, b: b, t0: last + (delay || 0), dur: dur, strong: !!strong }); }

    function draw(now) {
        var r = canvas.getBoundingClientRect(), c = palette(), i, p, A, B, u, q;
        ctx.clearRect(0, 0, r.width, r.height);
        ctx.lineWidth = 1; ctx.strokeStyle = c.link;
        ctx.beginPath();
        E.forEach(function (e) { A = xy(N[e[0]], r); B = xy(N[e[1]], r); ctx.moveTo(A[0], A[1]); ctx.lineTo(B[0], B[1]); });
        ctx.stroke();
        N.forEach(function (n, k) {
            q = xy(n, r);
            var real = k < 3, on = k === 2 ? rpiOnline : k === 0 ? !!ntfyMsg : true;
            ctx.fillStyle = c.node;
            ctx.beginPath(); ctx.arc(q[0], q[1], real ? 3 : 2, 0, 6.2832); ctx.fill();
            if (n.glow > 0.02 || (real && on)) {
                ctx.strokeStyle = 'rgba(' + c.rgb + ',' + Math.min(0.7, (real && on ? 0.25 : 0) + n.glow * 0.5) + ')';
                ctx.beginPath(); ctx.arc(q[0], q[1], 5 + n.glow * 4, 0, 6.2832); ctx.stroke();
            }
            if (real) {
                ctx.fillStyle = c.text; ctx.font = MONO;
                ctx.fillText(k === 0 ? 'ntfy' : k === 1 ? 'srv' : on ? 'rpi' : 'rpi · offline', q[0] + 9, q[1] + 3);
            }
        });
        for (i = 0; i < pulses.length; i++) {
            p = pulses[i]; u = (now - p.t0) / p.dur;
            if (u < 0) continue;
            A = xy(N[p.a], r); B = xy(N[p.b], r);
            var h = ease(Math.min(u, 1)), tail = Math.max(0, h - 0.18), fade = u > 0.85 ? Math.max(0, (1 - u) / 0.15) : 1;
            q = [A[0] + (B[0] - A[0]) * h, A[1] + (B[1] - A[1]) * h];
            ctx.strokeStyle = 'rgba(' + c.rgb + ',' + (0.5 * fade) + ')'; ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.moveTo(A[0] + (B[0] - A[0]) * tail, A[1] + (B[1] - A[1]) * tail); ctx.lineTo(q[0], q[1]); ctx.stroke();
            ctx.fillStyle = p.strong ? c.head : 'rgba(' + c.rgb + ',' + (0.85 * fade) + ')';
            ctx.beginPath(); ctx.arc(q[0], q[1], p.strong ? 2.5 : 2, 0, 6.2832); ctx.fill();
        }
        ctx.lineWidth = 1;
        if (chainText > now) {
            q = xy(N[0], r); ctx.fillStyle = c.head; ctx.globalAlpha = Math.min(1, (chainText - now) / 1200);
            ctx.font = MONO; ctx.fillText('“' + short(ntfyMsg, 34) + '”', q[0] + 9, q[1] - 10);
            ctx.globalAlpha = 1;
        }
    }
    function updateCaption() {
        if (!caption) return;
        caption.textContent = 'mesh · ' + N.length + ' nodes · ' + E.length + ' links · ' + pulses.length + ' in flight · ' +
            (rpiOnline ? 'rpi ' + short(rpiStatus, 24) : 'rpi offline') + (ntfyMsg ? ' · ntfy “' + short(ntfyMsg, 24) + '”' : '');
    }
    function frame(now) {
        raf = 0;
        if (paused || !visible || document.hidden) return;
        var dt = last ? Math.min(now - last, 100) : 16; last = now;
        if (now > nextPulse) {
            var e = E[Math.floor(Math.random() * E.length)], flip = Math.random() < 0.5;
            if (pulses.length < 6) send(flip ? e[1] : e[0], flip ? e[0] : e[1], 2600 + Math.random() * 1400);
            nextPulse = now + 900 + Math.random() * 900;
        }
        if (ntfyMsg && now > nextChain) { // ntfy -> srv -> rpi
            send(0, 1, 1800, 0, true); send(1, 2, 1800, 1800, true); chainText = now + 5200; nextChain = now + 16000;
        }
        pulses = pulses.filter(function (p) {
            if (now - p.t0 >= p.dur) { N[p.b].glow = 1; return false; }
            return true;
        });
        N.forEach(function (n) { n.glow *= Math.pow(0.5, dt / 500); });
        draw(now);
        if (now > nextCaption) { updateCaption(); nextCaption = now + 600; }
        raf = requestAnimationFrame(frame);
    }
    function resume() { if (!raf && !paused && visible && !reduced) { last = 0; raf = requestAnimationFrame(frame); } }

    size(); updateCaption(); draw(0);
    resume();

    new ResizeObserver(function () { size(); draw(last); }).observe(canvas);
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; resume(); }).observe(canvas);
    document.addEventListener('visibilitychange', resume);
    new MutationObserver(function () { draw(last); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    // Hold still while the pointer is over the hero text, so it never competes with reading.
    canvas.parentNode.addEventListener('mouseenter', function () { paused = true; });
    canvas.parentNode.addEventListener('mouseleave', function () { paused = false; resume(); });
})();
