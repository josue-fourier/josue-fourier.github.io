/* Hero signature: scalar multiplication d·P by double-and-add on y² = x³ + 2x + 3 over F₉₇.
   Real arithmetic, drawn on a canvas; one step per bit, paused when off-screen. */
(function () {
    'use strict';

    // ---- Curve arithmetic (null is the point at infinity) ----
    var p = 97, a = 2, b = 3;
    function mod(n) { return ((n % p) + p) % p; }
    function inv(n) {
        var t = 0, nt = 1, r = p, nr = mod(n), q, tmp;
        while (nr) { q = Math.floor(r / nr); tmp = t - q * nt; t = nt; nt = tmp; tmp = r - q * nr; r = nr; nr = tmp; }
        return mod(t);
    }
    function add(P, Q) {
        if (!P) return Q;
        if (!Q) return P;
        if (P[0] === Q[0] && mod(P[1] + Q[1]) === 0) return null;
        var l = (P[0] === Q[0] && P[1] === Q[1])
            ? mod((3 * P[0] * P[0] + a) * inv(2 * P[1]))
            : mod((Q[1] - P[1]) * inv(Q[0] - P[0]));
        var x = mod(l * l - P[0] - Q[0]);
        return [x, mod(l * (P[0] - x) - P[1])];
    }
    // Double-and-add, MSB first; returns every intermediate R so it can be drawn.
    function steps(d, P) {
        var bits = d.toString(2), R = P, out = [{ R: R, op: 'start', bit: 0 }];
        for (var i = 1; i < bits.length; i++) {
            R = add(R, R); out.push({ R: R, op: 'double', bit: i });
            if (bits[i] === '1') { R = add(R, P); out.push({ R: R, op: 'add', bit: i }); }
        }
        return out;
    }
    function points() {
        var pts = [];
        for (var x = 0; x < p; x++) for (var y = 0; y < p; y++) if (mod(y * y - (x * x * x + a * x + b)) === 0) pts.push([x, y]);
        return pts;
    }
    var G = [0, 10]; // order 50

    if (typeof module === 'object' && module.exports) { module.exports = { add: add, steps: steps, points: points, G: G, p: p }; return; }

    // ---- Drawing ----
    var canvas = document.getElementById('ecc-canvas');
    var caption = document.getElementById('ecc-caption');
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var PTS = points();
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var seq = [], shown = 0, d = 0, timer = null, visible = true;

    function palette() {
        var light = document.documentElement.getAttribute('data-theme') === 'lofi';
        return light
            ? { dot: 'rgba(15,23,42,0.16)', line: '4,120,87', head: '#047857' }
            : { dot: 'rgba(255,255,255,0.14)', line: '16,185,129', head: '#34d399' };
    }
    function size() {
        var r = canvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(r.width * dpr); canvas.height = Math.round(r.height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function xy(P) {
        var r = canvas.getBoundingClientRect(), pad = 24;
        return [pad + P[0] / (p - 1) * (r.width - 2 * pad), r.height - pad - P[1] / (p - 1) * (r.height - 2 * pad)];
    }
    function draw() {
        var r = canvas.getBoundingClientRect(), c = palette(), i, q, prev;
        ctx.clearRect(0, 0, r.width, r.height);
        ctx.fillStyle = c.dot;
        for (i = 0; i < PTS.length; i++) { q = xy(PTS[i]); ctx.fillRect(q[0] - 1, q[1] - 1, 2, 2); }
        for (i = 1; i < shown; i++) {
            if (!seq[i].R || !seq[i - 1].R) continue;
            var age = shown - 1 - i;
            ctx.strokeStyle = 'rgba(' + c.line + ',' + Math.max(0.08, 0.45 - age * 0.06) + ')';
            ctx.lineWidth = 1;
            ctx.setLineDash(seq[i].op === 'add' ? [3, 4] : []);
            prev = xy(seq[i - 1].R); q = xy(seq[i].R);
            ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(q[0], q[1]); ctx.stroke();
        }
        ctx.setLineDash([]);
        var head = shown ? seq[shown - 1].R : null;
        if (head) {
            q = xy(head);
            ctx.strokeStyle = c.head; ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.arc(q[0], q[1], 5, 0, Math.PI * 2); ctx.stroke();
        }
        if (caption) renderCaption();
    }
    function renderCaption() {
        var bits = d.toString(2), cur = shown ? seq[shown - 1] : null, done = shown === seq.length, html = '';
        for (var i = 0; i < bits.length; i++) {
            html += '<span class="' + (cur && i === cur.bit && !done ? 'ecc-bit-on' : i < (cur ? cur.bit : 0) || done ? 'ecc-bit-done' : '') + '">' + bits[i] + '</span>';
        }
        var R = cur && cur.R;
        caption.innerHTML = 'd·P · y² = x³ + 2x + 3 (mod 97) · d = ' + html + '₂' +
            (done && R ? ' · Q = (' + R[0] + ', ' + R[1] + ')' : cur ? ' · ' + (cur.op === 'add' ? '+P' : cur.op === 'double' ? '2R' : 'R = P') : '');
    }
    function newRun() {
        d = 11 + Math.floor(Math.random() * 39); // 11..49, below the order of G
        seq = steps(d, G); shown = 1;
    }
    function tick() {
        timer = null;
        if (!visible || document.hidden) return;
        if (shown < seq.length) { shown++; draw(); timer = setTimeout(tick, 750); }
        else { timer = setTimeout(function () { newRun(); draw(); tick(); }, 2600); }
    }
    function resume() { if (!timer && !reduced) timer = setTimeout(tick, 750); }

    size(); newRun();
    if (reduced) shown = seq.length;
    draw();
    resume();

    new ResizeObserver(function () { size(); draw(); }).observe(canvas);
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; if (visible) resume(); }).observe(canvas);
    document.addEventListener('visibilitychange', resume);
    new MutationObserver(draw).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
})();
