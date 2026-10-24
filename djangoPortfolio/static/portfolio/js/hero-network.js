/* Hero status bar: live Raspberry Pi heartbeat and the latest ntfy message (both come from data-* on the element). */
(function () {
    'use strict';
    var root = document.getElementById('net-caption');
    if (!root) return;
    var rpiName = root.dataset.rpiName, rpiStatus = root.dataset.rpiStatus || '', ntfyMsg = root.dataset.ntfy || '';

    function el(tag, cls, text, parent) {
        var e = document.createElement(tag); e.className = cls; if (text != null) e.textContent = text;
        if (parent) parent.appendChild(e); return e;
    }
    var row = el('div', 'net-status-row', null, root);
    el('span', 'net-dot net-dot-live', null, row);
    el('span', 'net-status-label', 'live', row);
    var rpi = el('span', 'net-chip' + (rpiName ? ' net-chip-on' : ''), null, row);
    el('span', 'net-dot' + (rpiName ? ' net-dot-live' : ''), null, rpi);
    rpi.appendChild(document.createTextNode(rpiName ? 'rpi · ' + rpiStatus : 'rpi offline'));
    if (ntfyMsg) {
        var q = el('div', 'net-ntfy', null, root);
        el('span', 'net-ntfy-tag', 'ntfy', q);
        el('span', 'net-ntfy-msg', ntfyMsg, q);
    }
})();
