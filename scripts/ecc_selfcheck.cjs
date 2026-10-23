// Self-check for the hero's elliptic-curve animation math. Run: node scripts/ecc_selfcheck.cjs
const assert = require('assert');
const { add, steps, points, G, p } = require('../djangoPortfolio/static/portfolio/js/ecc-signature.js');

const pts = points();
assert.strictEqual(pts.length + 1, 100, 'group order (with infinity) should be 100');
for (const [x, y] of pts) assert.strictEqual(((y * y - (x ** 3 + 2 * x + 3)) % p + p) % p, 0);

// Double-and-add must match naive repeated addition for every d.
let naive = null;
for (let d = 1; d <= 60; d++) {
    naive = add(naive, G);
    const R = steps(d, G).at(-1).R;
    assert.deepStrictEqual(R, naive, `d=${d}`);
}
assert.strictEqual(steps(50, G).at(-1).R, null, 'G has order 50');
console.log('ecc self-check ok');
