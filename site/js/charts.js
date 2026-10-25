/* charts.js - tiny SVG chart renderer (line / bar / dots / band) + seeded series generators.
   Colours come from CSS variables (--c1..--c6, --grid, --axis, --text-muted) so charts follow
   the light/dark theme without redrawing. Usage:
     var chart = TSP.Chart.draw(hostElement, spec);   // spec as in CONTENT_GUIDE.md
     chart.set({ series: [...] });                     // redraw with changed fields */
(function (T) {
  'use strict';
  var U = T.U, h = U.h;
  var NS = 'http://www.w3.org/2000/svg';

  /* ---------------------------------------------------------------- generators */
  var GEN = {
    trend: function (n, p) { var o = []; for (var t = 0; t < n; t++) o.push((p.start || 0) + (p.slope || 0) * t); return o; },
    season: function (n, p) {
      var o = [], per = p.period || 7, a = p.amp == null ? 1 : p.amp, ph = p.phase || 0;
      for (var t = 0; t < n; t++) o.push(a * Math.sin(2 * Math.PI * t / per + ph)); return o;
    },
    noise: function (n, p, r) { var o = []; for (var t = 0; t < n; t++) o.push((p.sd == null ? 1 : p.sd) * r.normal()); return o; },
    randomWalk: function (n, p, r) {
      var o = [], v = p.start || 0;
      for (var t = 0; t < n; t++) { v += (p.sd == null ? 1 : p.sd) * r.normal(); o.push(v); } return o;
    },
    ar1: function (n, p, r) {
      var o = [], v = 0, phi = p.phi == null ? 0.7 : p.phi;
      for (var t = 0; t < n; t++) { v = phi * v + (p.sd == null ? 1 : p.sd) * r.normal(); o.push(v); } return o;
    },
    step: function (n, p) { var o = []; for (var t = 0; t < n; t++) o.push(t >= (p.at || 0) ? (p.size || 0) : 0); return o; },
    spike: function (n, p) {
      var at = [].concat(p.at == null ? [] : p.at), o = [];
      for (var t = 0; t < n; t++) o.push(at.indexOf(t) >= 0 ? (p.size || 0) : 0); return o;
    },
    exp: function (n, p) { var o = []; for (var t = 0; t < n; t++) o.push((p.start == null ? 1 : p.start) * Math.exp((p.rate || 0) * t)); return o; },
    const: function (n, p) { var o = []; for (var t = 0; t < n; t++) o.push(p.value || 0); return o; }
  };
  /** Sum the generators of a series spec -> array of y values. */
  function generate(s) {
    var n = s.n || 50, y = new Array(n).fill(0);
    (s.gen || []).forEach(function (g, i) {
      var f = GEN[g[0]];
      if (!f) return;
      var part = f(n, g[1] || {}, U.rng((s.seed || 1) * 7919 + i * 104729));
      for (var t = 0; t < n; t++) y[t] += part[t];
    });
    return y;
  }
  function resolveSeries(s) {
    var y = s.y || generate(s);
    var x = s.x || y.map(function (_, i) { return i; });
    return Object.assign({}, s, { x: x, y: y });
  }

  /* ---------------------------------------------------------------- helpers */
  function svgEl(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(e);
    return e;
  }
  function niceStep(range, count) {
    var raw = range / Math.max(1, count), mag = Math.pow(10, Math.floor(Math.log10(raw))), r = raw / mag;
    return (r >= 5 ? 5 : r >= 2 ? 2 : 1) * mag * (r > 5 ? 2 : 1);
  }
  function ticks(lo, hi, count) {
    if (hi === lo) { hi = lo + 1; }
    var step = niceStep(hi - lo, count), t = [], v = Math.ceil(lo / step - 1e-9) * step;
    for (; v <= hi + step * 1e-9; v += step) t.push(Math.round(v / step) * step);
    return t;
  }
  function fmt(v) {
    if (v == null || isNaN(v)) return '-';
    var a = Math.abs(v);
    if (a >= 1e6) return (v / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (a >= 1e4) return (v / 1e3).toFixed(0) + 'k';
    if (a >= 100) return v.toFixed(0);
    if (a >= 10) return v.toFixed(1).replace(/\.0$/, '');
    if (a >= 1) return v.toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
    if (a === 0) return '0';
    return v.toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
  }
  function colorOf(s, i) {
    if (typeof s.color === 'string') return s.color.indexOf('#') === 0 ? s.color : 'var(--' + s.color + ')';
    return 'var(--c' + (((typeof s.color === 'number' ? s.color : i) % 6) + 1) + ')';
  }

  /* ---------------------------------------------------------------- the chart */
  function draw(host, spec0) {
    var spec = Object.assign({}, spec0);
    var fig = h('figure.chart');
    var titleEl = h('figcaption.chart-title');
    var legend = h('div.chart-legend');
    var box = h('div.chart-box');
    var tip = h('div.chart-tip', { hidden: true });
    var cap = h('p.chart-caption');
    box.appendChild(tip);
    fig.appendChild(titleEl); fig.appendChild(legend); fig.appendChild(box); fig.appendChild(cap);
    host.appendChild(fig);
    var svg = null, geom = null, ro = null, lastW = 0;

    function render() {
      var W = Math.max(220, Math.round(box.clientWidth || host.clientWidth || 320));
      var H = spec.height || 220;
      if (W < 420) H = Math.min(H, Math.round(W * 0.75));
      lastW = W;
      var series = (spec.series || []).map(resolveSeries);
      titleEl.textContent = spec.title || '';
      titleEl.hidden = !spec.title;
      cap.textContent = spec.caption || '';
      cap.hidden = !spec.caption;

      // legend (>= 2 series)
      U.clear(legend);
      var shown = series.filter(function (s) { return s.legend !== false && s.name; });
      legend.hidden = shown.length < 2;
      shown.forEach(function (s) {
        var i = series.indexOf(s), kind = s.kind || 'line';
        legend.appendChild(h('span.lg', h('i.lg-sw' + (s.dash ? '.dash' : '') + '.' + kind, { style: { '--sw': colorOf(s, i) } }), s.name));
      });

      var m = { l: 44, r: 12, t: 10, b: spec.x ? 40 : 26 };
      if (spec.ylabel) m.l = 52;
      var pw = W - m.l - m.r, ph = H - m.t - m.b;
      // data extents
      var xs = [], ys = [], hasBar = false;
      series.forEach(function (s) {
        s.x.forEach(function (v) { xs.push(v); });
        s.y.forEach(function (v) { if (v != null && isFinite(v)) ys.push(v); });
        if (s.y2) s.y2.forEach(function (v) { if (v != null && isFinite(v)) ys.push(v); });
        if (s.kind === 'bar') hasBar = true;
      });
      (spec.marks || []).forEach(function (mk) { if (mk.y != null) ys.push(mk.y); });
      if (!xs.length) xs = [0, 1];
      if (!ys.length) ys = [0, 1];
      var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
      var y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
      if (hasBar) { y0 = Math.min(y0, 0); y1 = Math.max(y1, 0); }
      var padY = (y1 - y0) * 0.06 || 1;
      if (!(hasBar && y0 === 0)) y0 -= padY;
      y1 += padY;
      if (spec.yMin != null) y0 = spec.yMin;
      if (spec.yMax != null) y1 = spec.yMax;
      var xPad = hasBar ? (x1 - x0) / Math.max(1, xs.length / series.length) * 0.5 || 0.5 : 0;
      var xa = x0 - xPad, xb = x1 + xPad;
      if (xa === xb) { xa -= 1; xb += 1; }
      var sx = function (v) { return m.l + (v - xa) / (xb - xa) * pw; };
      var sy = function (v) { return m.t + ph - (v - y0) / (y1 - y0) * ph; };
      geom = { sx: sx, sy: sy, m: m, pw: pw, ph: ph, series: series, xa: xa, xb: xb };

      if (svg) svg.remove();
      svg = svgEl('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img',
        'aria-label': (spec.title || 'Chart') + (spec.caption ? '. ' + spec.caption : '') });
      svg.setAttribute('class', 'chart-svg');
      box.insertBefore(svg, tip);

      // grid + y ticks
      ticks(y0, y1, Math.max(3, Math.round(ph / 42))).forEach(function (t) {
        var y = sy(t);
        svgEl('line', { x1: m.l, x2: W - m.r, y1: y, y2: y, class: t === 0 ? 'axis-line' : 'grid' }, svg);
        svgEl('text', { x: m.l - 6, y: y + 4, 'text-anchor': 'end', class: 'tick' }, svg).textContent = fmt(t);
      });
      // x ticks
      var cats = spec.categories;
      if (cats) {
        cats.forEach(function (c, i) {
          if (cats.length > 12 && i % Math.ceil(cats.length / 8)) return;
          svgEl('text', { x: sx(i), y: H - m.b + 15, 'text-anchor': 'middle', class: 'tick' }, svg).textContent = c;
        });
      } else {
        ticks(xa, xb, Math.max(3, Math.round(pw / 70))).forEach(function (t) {
          if (Math.abs(t - Math.round(t)) > 1e-9 && (xb - xa) > 5) return;
          svgEl('text', { x: sx(t), y: H - m.b + 15, 'text-anchor': 'middle', class: 'tick' }, svg).textContent = fmt(t);
        });
      }
      if (spec.x) svgEl('text', { x: m.l + pw / 2, y: H - 6, 'text-anchor': 'middle', class: 'axis-label' }, svg).textContent = spec.x;
      if (spec.ylabel) {
        var yl = svgEl('text', { x: 12, y: m.t + ph / 2, 'text-anchor': 'middle', class: 'axis-label',
          transform: 'rotate(-90 12 ' + (m.t + ph / 2) + ')' }, svg);
        yl.textContent = spec.ylabel;
      }

      // shaded regions and vertical/horizontal marks
      (spec.marks || []).forEach(function (mk) {
        if (mk.x0 != null && mk.x1 != null) {
          var a = Math.max(m.l, sx(mk.x0)), b = Math.min(W - m.r, sx(mk.x1));
          svgEl('rect', { x: a, y: m.t, width: Math.max(0, b - a), height: ph, class: 'region', style: mk.color ? 'fill:' + colorOf(mk, 0) : '' }, svg);
          if (mk.label) svgEl('text', { x: a + 4, y: m.t + 12, class: 'mark-label' }, svg).textContent = mk.label;
        }
      });
      series.forEach(function (s, i) {
        if (s.hidden) return;
        var col = colorOf(s, i), kind = s.kind || 'line', pts = s.x.length;
        if (kind === 'band') {
          var up = '', lo = '';
          s.x.forEach(function (xv, k) {
            if (s.y[k] == null || s.y2[k] == null) return;
            up += (up ? 'L' : 'M') + sx(xv) + ',' + sy(s.y2[k]);
            lo = 'L' + sx(xv) + ',' + sy(s.y[k]) + lo;
          });
          svgEl('path', { d: up + lo + 'Z', class: 'band', style: 'fill:' + col }, svg);
        } else if (kind === 'bar') {
          var bw = Math.max(1, Math.min(28, pw / Math.max(1, pts) * 0.7));
          var nSer = series.filter(function (q) { return q.kind === 'bar'; }).length || 1;
          var slot = series.filter(function (q) { return q.kind === 'bar'; }).indexOf(s);
          var w1 = bw / nSer;
          s.x.forEach(function (xv, k) {
            var v = s.y[k]; if (v == null) return;
            var yTop = sy(Math.max(v, 0)), yBot = sy(Math.min(v, 0));
            svgEl('rect', { x: sx(xv) - bw / 2 + slot * w1, y: yTop, width: Math.max(1, w1 - (nSer > 1 ? 1 : 0)), height: Math.max(1, yBot - yTop), rx: 1.5,
              style: 'fill:' + col }, svg);
          });
        } else if (kind === 'dots') {
          s.x.forEach(function (xv, k) {
            if (s.y[k] == null) return;
            svgEl('circle', { cx: sx(xv), cy: sy(s.y[k]), r: s.r || 3.5, class: 'dot', style: 'fill:' + col }, svg);
          });
        } else if (kind === 'step') {
          var d = '';
          s.x.forEach(function (xv, k) {
            if (s.y[k] == null) return;
            d += d ? 'H' + sx(xv) + 'V' + sy(s.y[k]) : 'M' + sx(xv) + ',' + sy(s.y[k]);
          });
          svgEl('path', { d: d, class: 'line', style: 'stroke:' + col, 'stroke-dasharray': s.dash ? '6 4' : '' }, svg);
        } else {
          var dd = '', pen = false;
          s.x.forEach(function (xv, k) {
            var v = s.y[k];
            if (v == null || !isFinite(v)) { pen = false; return; }
            dd += (pen ? 'L' : 'M') + sx(xv).toFixed(1) + ',' + sy(v).toFixed(1); pen = true;
          });
          svgEl('path', { d: dd, class: 'line', style: 'stroke:' + col + (s.width ? ';stroke-width:' + s.width : ''), 'stroke-dasharray': s.dash ? '6 4' : '' }, svg);
          if (s.points) s.x.forEach(function (xv, k) {
            if (s.y[k] != null) svgEl('circle', { cx: sx(xv), cy: sy(s.y[k]), r: 3, class: 'dot', style: 'fill:' + col }, svg);
          });
        }
      });
      (spec.marks || []).forEach(function (mk) {
        if (mk.x != null) {
          svgEl('line', { x1: sx(mk.x), x2: sx(mk.x), y1: m.t, y2: m.t + ph, class: 'mark' }, svg);
          if (mk.label) {
            var right = sx(mk.x) < W - 110;
            svgEl('text', { x: sx(mk.x) + (right ? 5 : -5), y: m.t + 11, 'text-anchor': right ? 'start' : 'end', class: 'mark-label' }, svg).textContent = mk.label;
          }
        } else if (mk.y != null) {
          svgEl('line', { x1: m.l, x2: W - m.r, y1: sy(mk.y), y2: sy(mk.y), class: 'mark' }, svg);
          if (mk.label) svgEl('text', { x: W - m.r - 3, y: sy(mk.y) - 4, 'text-anchor': 'end', class: 'mark-label' }, svg).textContent = mk.label;
        }
      });

      // hover layer: crosshair + tooltip (mouse and touch)
      var cross = svgEl('line', { y1: m.t, y2: m.t + ph, class: 'cross', visibility: 'hidden' }, svg);
      var hit = svgEl('rect', { x: m.l, y: m.t, width: pw, height: ph, fill: 'transparent', style: 'touch-action:pan-y' }, svg);
      function onMove(ev) {
        var r = svg.getBoundingClientRect();
        var px = ((ev.touches ? ev.touches[0].clientX : ev.clientX) - r.left) * (W / r.width);
        var xv = xa + (px - m.l) / pw * (xb - xa);
        var lines = [], best = null;
        series.forEach(function (s, i) {
          if (s.hidden || s.kind === 'band' || s.legend === false && !s.tip) return;
          var bi = -1, bd = Infinity;
          s.x.forEach(function (v, k) { var d = Math.abs(v - xv); if (d < bd && s.y[k] != null) { bd = d; bi = k; } });
          if (bi < 0) return;
          if (best === null || Math.abs(s.x[bi] - xv) < Math.abs(best - xv)) best = s.x[bi];
          lines.push([s, i, bi]);
        });
        if (!lines.length) return;
        var xs0 = best;
        U.clear(tip);
        tip.appendChild(h('div.tip-x', (cats && cats[xs0] != null ? cats[xs0] : (spec.x || 'x') + ' ' + fmt(xs0))));
        lines.forEach(function (L) {
          var s = L[0];
          if (Math.abs(s.x[L[2]] - xs0) > (xb - xa) / 40 + 0.5) return;
          tip.appendChild(h('div.tip-row', h('i.lg-sw', { style: { '--sw': colorOf(s, L[1]) } }), (s.name || 'value') + ': ', h('b', fmt(s.y[L[2]]))));
        });
        tip.hidden = false;
        cross.setAttribute('x1', sx(xs0)); cross.setAttribute('x2', sx(xs0)); cross.setAttribute('visibility', 'visible');
        var tw = tip.offsetWidth, left = sx(xs0) + 12;
        if (left + tw > W - 4) left = sx(xs0) - tw - 12;
        tip.style.left = Math.max(2, left) + 'px'; tip.style.top = (m.t + 4) + 'px';
      }
      function onLeave() { tip.hidden = true; cross.setAttribute('visibility', 'hidden'); }
      hit.addEventListener('mousemove', onMove);
      hit.addEventListener('mouseleave', onLeave);
      hit.addEventListener('touchstart', onMove, { passive: true });
      hit.addEventListener('touchmove', onMove, { passive: true });
      hit.addEventListener('touchend', function () { setTimeout(onLeave, 1200); });
    }

    render();
    if (window.ResizeObserver) {
      ro = new ResizeObserver(function () {
        var w = Math.round(box.clientWidth);
        if (w && Math.abs(w - lastW) > 1) render();
      });
      ro.observe(box);
    }
    return {
      el: fig,
      set: function (patch) { Object.assign(spec, patch); render(); },
      destroy: function () { if (ro) ro.disconnect(); fig.remove(); }
    };
  }

  T.Chart = { draw: draw, generate: generate, resolveSeries: resolveSeries, fmt: fmt, GEN: GEN };
})(window.TSP = window.TSP || {});
