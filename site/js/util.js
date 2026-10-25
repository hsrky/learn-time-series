/* util.js - tiny DOM helpers and shared utilities. Everything lives under window.TSP. */
(function (T) {
  'use strict';

  /** h('div.class#id', {attr: v, onclick: fn}, ...children) -> Element */
  function h(tag, attrs) {
    var m = /^([a-z0-9]+)?((?:[.#][\w-]+)*)$/i.exec(tag) || [];
    var el = document.createElement(m[1] || 'div');
    (m[2] || '').replace(/([.#])([\w-]+)/g, function (_, k, v) {
      if (k === '.') el.classList.add(v); else el.id = v;
    });
    var start = 1;
    if (attrs && typeof attrs === 'object' && !(attrs instanceof Node) && !Array.isArray(attrs)) {
      start = 2;
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v == null || v === false) return;
        if (k === 'class') el.className += (el.className ? ' ' : '') + v;
        else if (k === 'html') el.innerHTML = v;
        else if (k === 'text') el.textContent = v;
        else if (k === 'style' && typeof v === 'object') Object.keys(v).forEach(function (p) { if (p.slice(0, 2) === '--') el.style.setProperty(p, v[p]); else el.style[p] = v[p]; });
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') el.addEventListener(k.slice(2), v);
        else if (k === 'value' || k === 'checked' || k === 'disabled' || k === 'selected') el[k] = v;
        else el.setAttribute(k, v === true ? '' : v);
      });
    }
    for (var i = start; i < arguments.length; i++) add(el, arguments[i]);
    return el;
  }
  function add(el, c) {
    if (c == null || c === false) return;
    if (Array.isArray(c)) c.forEach(function (x) { add(el, x); });
    else if (c instanceof Node) el.appendChild(c);
    else el.appendChild(document.createTextNode(String(c)));
  }
  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); return el; }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function debounce(fn, ms) {
    var t; return function () { var a = arguments, s = this; clearTimeout(t); t = setTimeout(function () { fn.apply(s, a); }, ms); };
  }

  /* ---- dates (local time, "YYYY-MM-DD") ---- */
  function ymd(d) {
    d = d || new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function addDays(dateStr, n) {
    var p = dateStr.split('-').map(Number);
    var d = new Date(p[0], p[1] - 1, p[2] + n);
    return ymd(d);
  }
  function daysBetween(a, b) { // b - a in whole days
    var pa = a.split('-').map(Number), pb = b.split('-').map(Number);
    return Math.round((new Date(pb[0], pb[1] - 1, pb[2]) - new Date(pa[0], pa[1] - 1, pa[2])) / 864e5);
  }
  function fmtDuration(sec) {
    sec = Math.max(0, Math.round(sec));
    var m = Math.floor(sec / 60), s = sec % 60, hh = Math.floor(m / 60);
    if (hh) return hh + ':' + String(m % 60).padStart(2, '0') + ':' + String(s).padStart(2, '0');
    return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
  }
  function timeAgo(ts) {
    var s = (Date.now() - ts) / 1000;
    if (s < 60) return 'just now';
    if (s < 3600) return Math.floor(s / 60) + ' min ago';
    if (s < 86400) return Math.floor(s / 3600) + ' h ago';
    return Math.floor(s / 86400) + ' d ago';
  }

  /* ---- seeded random numbers (mulberry32) + normal via Box-Muller ---- */
  function rng(seed) {
    var a = (seed >>> 0) || 1;
    function u() {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
    u.normal = function () {
      var x = u() || 1e-12, y = u();
      return Math.sqrt(-2 * Math.log(x)) * Math.cos(2 * Math.PI * y);
    };
    return u;
  }
  function hashStr(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function shuffle(arr, seed) {
    var r = rng(seed), a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }

  /* ---- toasts ---- */
  function toast(msg, kind) {
    var host = document.getElementById('toasts');
    if (!host) return;
    var t = h('div.toast' + (kind ? '.' + kind : ''), msg);
    host.appendChild(t);
    setTimeout(function () { t.classList.add('out'); }, 3200);
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 3700);
  }

  /* ---- clipboard (works on http too) ---- */
  function copyText(text) {
    function fallback() {
      var ta = h('textarea', { style: { position: 'fixed', opacity: 0 } }); ta.value = text;
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (e) { /* ignore */ }
      document.body.removeChild(ta);
    }
    try {
      if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text).catch(fallback);
    } catch (e) { /* fall through */ }
    fallback();
    return Promise.resolve();
  }

  /* ---- download a text file ---- */
  function download(name, text, type) {
    var a = h('a', { href: URL.createObjectURL(new Blob([text], { type: type || 'application/json' })), download: name });
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  /* ---- icons: 24x24 stroke paths ---- */
  var ICONS = {
    wave: 'M2 12c2-6 4-6 6 0s4 6 6 0 4-6 6 0',
    tools: 'M14 6l4 4-9 9H5v-4zM13 7l4 4M16 3l5 5-2 2-5-5z',
    sigma: 'M18 5H6l7 7-7 7h12',
    trend: 'M3 17l6-6 4 4 8-8M15 7h6v6',
    target: 'M12 3a9 9 0 100 18 9 9 0 000-18zM12 8a4 4 0 100 8 4 4 0 000-8zM12 11.5a.5.5 0 100 1',
    tree: 'M12 3v18M12 8l-5-3M12 12l6-4M12 16l-5-3M12 17l5-3',
    layers: 'M12 3l9 5-9 5-9-5zM3 13l9 5 9-5M3 17.5l9 5 9-5',
    spark: 'M12 3l2 6 6 2-6 2-2 6-2-6-6-2 6-2z',
    alert: 'M12 4l9 16H3zM12 10v4M12 17v.5',
    code: 'M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16',
    server: 'M4 5h16v5H4zM4 14h16v5H4zM8 7.5h.01M8 16.5h.01',
    book: 'M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2zM4 19a2 2 0 012-2h13',
    box: 'M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10',
    briefcase: 'M3 8h18v12H3zM9 8V5h6v3M3 13h18',
    crown: 'M3 8l4.5 4L12 5l4.5 7L21 8l-2 11H5z',
    trophy: 'M8 4h8v6a4 4 0 01-8 0zM8 6H4v1a4 4 0 004 4M16 6h4v1a4 4 0 01-4 4M12 14v4M8 20h8',
    check: 'M5 12.5l4.5 4.5L19 7',
    x: 'M6 6l12 12M18 6L6 18',
    play: 'M7 4l13 8-13 8z',
    lock: 'M6 11h12v9H6zM8.5 11V8a3.5 3.5 0 017 0v3',
    star: 'M12 3l2.7 5.8 6.3.8-4.6 4.3 1.2 6.3L12 17l-5.6 3.2 1.2-6.3L3 9.6l6.3-.8z',
    menu: 'M4 7h16M4 12h16M4 17h16',
    sun: 'M12 8a4 4 0 100 8 4 4 0 000-8zM12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5',
    moon: 'M20 14.5A8.5 8.5 0 019.5 4 8.5 8.5 0 1020 14.5z',
    flame: 'M12 3c1 4 5 6 5 11a5 5 0 01-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-4-1-6 1-10z',
    copy: 'M9 9h11v11H9zM5 15V4h11',
    flask: 'M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3',
    refresh: 'M20 6v5h-5M4 18v-5h5M18.5 9A7 7 0 006 7.5M5.5 15A7 7 0 0018 16.5',
    chevron: 'M9 6l6 6-6 6',
    clock: 'M12 3a9 9 0 100 18 9 9 0 000-18zM12 7v5l3 2',
    list: 'M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01',
    cards: 'M4 7h13v12H4zM8 4h13v12',
    home: 'M4 11l8-7 8 7v9h-5v-6H9v6H4z'
  };
  function icon(name, size) {
    var s = size || 20;
    var span = document.createElement('span');
    span.className = 'ico';
    span.setAttribute('aria-hidden', 'true');
    span.innerHTML = '<svg viewBox="0 0 24 24" width="' + s + '" height="' + s + '" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="' + (ICONS[name] || ICONS.box) + '"/></svg>';
    return span;
  }

  T.U = {
    h: h, clear: clear, esc: esc, debounce: debounce, ymd: ymd, addDays: addDays, daysBetween: daysBetween,
    fmtDuration: fmtDuration, timeAgo: timeAgo, rng: rng, hashStr: hashStr, shuffle: shuffle, toast: toast,
    copyText: copyText, download: download, icon: icon
  };
})(window.TSP = window.TSP || {});
