/* Site-wide background, one fragment shader: slowly evolving topographic contour lines, coloured by elevation
   (emerald > cyan > violet). Scroll nudges the terrain's phase rather than sliding it, and contours brighten near the pointer. */
(function () {
    'use strict';
    var canvas = document.getElementById('bg-shader');
    var gl = canvas && canvas.getContext('webgl', { antialias: false, alpha: true, powerPreference: 'low-power' });
    if (!gl) return;
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var VS = 'attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
    // fwidth needs OES_standard_derivatives in WebGL1; without it lines fall back to a fixed softness.
    var deriv = gl.getExtension('OES_standard_derivatives');
    var FS = [
        deriv ? '#extension GL_OES_standard_derivatives : enable' : '#define fwidth(x) .06',
        '#ifdef GL_FRAGMENT_PRECISION_HIGH\nprecision highp float;\n#else\nprecision mediump float;\n#endif',
        'uniform vec2 r,m;uniform float t,s,k;',   // r: canvas px, m: pointer, t: seconds, s: scroll in canvas px, k: theme gain
        'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
        'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);',
        ' return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
        'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<3;i++){v+=a*n(p);p*=2.03;a*=.5;}return v;}',   // 3 octaves: broad, calm terrain
        'vec3 pal(float x){return mix(mix(vec3(.06,.78,.5),vec3(.1,.72,.95),smoothstep(.25,.5,x)),vec3(.58,.36,.98),smoothstep(.55,.8,x));}', // emerald > cyan > violet by elevation
        'void main(){',
        ' vec2 p=(gl_FragCoord.xy-.5*r)/r.y;',
        ' float ph=t*.018+s/r.y*.05;',                         // slow evolution; scroll nudges the terrain's phase instead of sliding it
        ' vec2 q=p*1.35+vec2(ph*.6,-ph*.4);',
        ' vec2 w=vec2(fbm(q*.8+vec2(ph,3.)),fbm(q*.8+vec2(7.,-ph)));',
        ' float f=fbm(q+.9*w);',
        ' float x=(f-.18)*9.;',                                 // 9 contour levels across the range
        ' float g=abs(fract(x-.5)-.5);',                        // distance to nearest contour, in level units
        ' float aa=fwidth(x)*1.3+.0001;',
        ' float line=1.-smoothstep(0.,aa,g);',
        ' float major=step(mod(floor(x+.5),3.),.5);',           // every third line is stronger
        ' float glow=exp(-dot(p-m,p-m)*5.);',                   // contours brighten near the pointer
        ' float a=line*(.16+.2*major)*(1.+1.6*glow)+smoothstep(.3,.8,f)*.07;',
        ' vec3 c=pal(f);',
        ' a=clamp(a*k,0.,.8);',
        ' gl_FragColor=vec4(c*a,a);}'
    ].join('\n');

    function shader(type, src) { var o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o); return o; }
    var prog = gl.createProgram();
    gl.attachShader(prog, shader(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, shader(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
    gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, 'a');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var U = {};
    ['r', 'm', 't', 's', 'k'].forEach(function (n) { U[n] = gl.getUniformLocation(prog, n); });

    function scrollNow() { return window.lenis && typeof lenis.scroll === 'number' ? lenis.scroll : (scrollY || document.documentElement.scrollTop || 0); }
    var cur = 0, raf = 0, last = 0, t = 0, mx = 0, my = 0, tx = 0, ty = 0;
    function theme() {
        gl.uniform1f(U.k, document.documentElement.getAttribute('data-theme') === 'lofi' ? 1.0 : 1.0);
    }
    function size() {
        // Half resolution: the field is soft anyway, and it quarters the fragment work.
        canvas.width = Math.max(1, Math.round(innerWidth / 2)); canvas.height = Math.max(1, Math.round(innerHeight / 2));
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.uniform2f(U.r, canvas.width, canvas.height);
    }
    function draw() {
        gl.uniform1f(U.t, t); gl.uniform1f(U.s, cur / 2); gl.uniform2f(U.m, mx, my);
        gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    function frame(now) {
        raf = 0;
        if (document.hidden) return;
        if (!last) last = now; // first frame only sets the clock
        var dt = Math.min(now - last, 100);
        if (dt < 32) { raf = requestAnimationFrame(frame); return; } // ~30fps cap
        last = now; t += dt / 1000;
        cur += (scrollNow() - cur) * Math.min(1, dt / 900); // ease toward the real scroll
        mx += (tx - mx) * Math.min(1, dt / 600); my += (ty - my) * Math.min(1, dt / 600);
        draw();
        raf = requestAnimationFrame(frame);
    }
    function start() { if (!raf && !reduced) { last = 0; raf = requestAnimationFrame(frame); } }

    size(); theme(); cur = scrollNow(); draw();
    canvas.classList.add('ready');
    start();
    addEventListener('resize', function () { size(); draw(); });
    addEventListener('pointermove', function (e) { // same coordinate space as the shader: centred, y up, units of viewport height
        tx = (e.clientX - innerWidth / 2) / innerHeight; ty = (innerHeight / 2 - e.clientY) / innerHeight;
    }, { passive: true });
    document.addEventListener('visibilitychange', start);
    if (reduced) addEventListener('scroll', function () { cur = scrollNow(); draw(); }, { passive: true });
    new MutationObserver(function () { theme(); draw(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
})();
