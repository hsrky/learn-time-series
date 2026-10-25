/* widgets.js - interactive teaching widgets used by ```widget blocks.
   Each widget is  function(host, params)  that builds sliders + a live chart + a short caption.
   Data is generated with fixed seeds, so every learner sees the same picture. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, Chart = T.Chart;

  /* ------------------------------------------------------------ small helpers */
  function sum(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return s; }
  function mean(a) { return a.length ? sum(a) / a.length : NaN; }
  function sd(a) { var m = mean(a); return Math.sqrt(mean(a.map(function (v) { return (v - m) * (v - m); }))); }
  function range(n) { var o = []; for (var i = 0; i < n; i++) o.push(i); return o; }
  function gen(n, seed, parts) { return Chart.generate({ n: n, seed: seed, gen: parts }); }
  function quantile(sorted, q) { // linear interpolation on a sorted copy
    var pos = (sorted.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  }
  var f1 = function (v) { return (Math.round(v * 10) / 10).toString(); };
  var f2 = function (v) { return (Math.round(v * 100) / 100).toString(); };

  /** Slider control. opts: {label, min, max, step, value, fmt}. Returns {el, get(), set()}. */
  function slider(opts, onInput) {
    var out = h('output', ''), input = h('input', { type: 'range', min: opts.min, max: opts.max, step: opts.step || 1, value: opts.value });
    var id = 'w' + Math.random().toString(36).slice(2, 8);
    input.id = id;
    function show() { out.textContent = (opts.fmt || String)(+input.value); }
    input.addEventListener('input', function () { show(); onInput(); });
    show();
    return {
      el: h('div.w-ctl', h('label', { for: id }, h('span', opts.label), out), input),
      get: function () { return +input.value; },
      set: function (v) { input.value = v; show(); }
    };
  }
  function select(label, options, value, onChange) {
    var sel = h('select.input', { onchange: onChange }, options.map(function (o) { return h('option', { value: o[0], selected: o[0] === value }, o[1]); }));
    var id = 'w' + Math.random().toString(36).slice(2, 8); sel.id = id;
    return { el: h('div.w-ctl', h('label', { for: id }, h('span', label)), sel), get: function () { return sel.value; } };
  }
  function check(label, value, onChange) {
    var cb = h('input', { type: 'checkbox', checked: !!value, onchange: onChange });
    return { el: h('label.w-check', cb, ' ', label), get: function () { return cb.checked; } };
  }
  /** Common frame: controls, chart hosts, readout, caption. */
  function frame(host, title, caption) {
    var controls = h('div.w-controls'), charts = h('div.w-charts'), readout = h('div.w-readout', { 'aria-live': 'polite' });
    host.appendChild(h('div.widget-card',
      h('div.widget-label', U.icon('spark', 14), ' Try it: ' + title), controls, charts, readout, h('p.w-caption', caption)));
    return { controls: controls, charts: charts, readout: readout };
  }
  function readout(el, items) {
    U.clear(el);
    items.forEach(function (it) { el.appendChild(h('div.w-stat' + (it[2] ? '.' + it[2] : ''), h('span', it[0]), h('b', it[1]))); });
  }
  function p(params, key, d) { return params && params[key] != null ? params[key] : d; }

  var W = {};

  /* ------------------------------------------------------------ components */
  W.components = function (host, params) {
    var f = frame(host, 'build a series from its parts', 'Trend, season and noise add up to the series you see. Move the sliders and watch the blue line change.');
    var n = 96, noise = gen(n, 5, [['noise', { sd: 1 }]]);
    var slope = slider({ label: 'Trend slope', min: -0.5, max: 1, step: 0.05, value: p(params, 'slope', 0.4), fmt: f2 }, up);
    var amp = slider({ label: 'Season size', min: 0, max: 10, step: 0.5, value: p(params, 'amp', 5), fmt: f1 }, up);
    var sdv = slider({ label: 'Noise', min: 0, max: 5, step: 0.25, value: p(params, 'sd', 1.5), fmt: f2 }, up);
    var per = select('Season length', [['7', '7 (weekly)'], ['12', '12 (monthly)'], ['24', '24 (hourly)']], String(p(params, 'period', 12)), up);
    var showT = check('Show trend', true, up), showTS = check('Show trend + season', false, up);
    f.controls.append(slope.el, amp.el, sdv.el, per.el, h('div.w-checks', showT.el, showTS.el));
    var chart = Chart.draw(f.charts, { height: 230, x: 'time', series: [] });
    function up() {
      var P = +per.get(), x = range(n);
      var tr = x.map(function (t) { return 20 + slope.get() * t; });
      var ts = x.map(function (t, i) { return tr[i] + amp.get() * Math.sin(2 * Math.PI * t / P); });
      var y = ts.map(function (v, i) { return v + sdv.get() * noise[i]; });
      var series = [{ name: 'series', y: y, color: 0 }];
      if (showT.get()) series.push({ name: 'trend', y: tr, color: 1, dash: true });
      if (showTS.get()) series.push({ name: 'trend + season', y: ts, color: 2 });
      chart.set({ series: series });
      readout(f.readout, [['Trend per step', f2(slope.get())], ['Season size', f1(amp.get())], ['Noise (sd)', f2(sdv.get())]]);
    }
    up();
  };

  /* ------------------------------------------------------------ moving average */
  W['moving-average'] = function (host, params) {
    var f = frame(host, 'moving average', 'A longer window smooths more noise, but the line reacts later. A trailing average always lags behind the data.');
    var n = 90;
    var y = gen(n, 11, [['trend', { start: 20, slope: 0.15 }], ['season', { period: 30, amp: 4 }], ['noise', { sd: 2.5 }]]);
    var win = slider({ label: 'Window size', min: 1, max: 30, value: p(params, 'window', 7) }, up);
    var mode = select('Window position', [['trailing', 'Trailing (past only)'], ['centered', 'Centered (uses future)']], p(params, 'mode', 'trailing'), up);
    f.controls.append(win.el, mode.el);
    var chart = Chart.draw(f.charts, { height: 230, x: 'time', series: [] });
    function up() {
      var w = win.get(), ma = [], m = mode.get(), half = Math.floor(w / 2);
      for (var t = 0; t < n; t++) {
        var a = m === 'trailing' ? t - w + 1 : t - half, b = m === 'trailing' ? t : a + w - 1;
        ma.push(a < 0 || b >= n ? null : mean(y.slice(a, b + 1)));
      }
      chart.set({ series: [{ name: 'data', y: y, color: 0, width: 1.5 }, { name: 'moving average', y: ma, color: 1, width: 3 }] });
      var res = []; for (var i = 0; i < n; i++) if (ma[i] != null) res.push(y[i] - ma[i]);
      readout(f.readout, [['Window', String(w)], ['Points without an average', String(n - res.length)], ['Spread left over (sd)', f2(sd(res))]]);
    }
    up();
  };

  /* ------------------------------------------------------------ simple exponential smoothing */
  function sesFit(y, a) {
    var l = y[0], fit = [null], sse = 0;
    for (var t = 1; t < y.length; t++) { fit.push(l); sse += (y[t] - l) * (y[t] - l); l = a * y[t] + (1 - a) * l; }
    return { fit: fit, level: l, sse: sse };
  }
  W['ses-alpha'] = function (host, params) {
    var f = frame(host, 'simple exponential smoothing', 'Alpha is how fast the forecast forgets the past. A high alpha follows the last values. A low alpha is calm and slow.');
    var y = gen(60, 4, [['const', { value: 50 }], ['step', { at: 25, size: 12 }], ['noise', { sd: 3 }]]), n = y.length;
    var al = slider({ label: 'Alpha (α)', min: 0.02, max: 1, step: 0.01, value: p(params, 'alpha', 0.3), fmt: f2 }, up);
    f.controls.append(al.el);
    var chart = Chart.draw(f.charts, { height: 230, x: 'time', series: [] });
    function up() {
      var a = al.get(), r = sesFit(y, a);
      var fx = range(13).map(function (k) { return n - 1 + k; });
      var fc = fx.map(function (k) { return k === n - 1 ? y[n - 1] : r.level; });
      var best = 0.02, bs = Infinity;
      for (var g = 0.02; g <= 1.0001; g += 0.01) { var s = sesFit(y, g).sse; if (s < bs) { bs = s; best = g; } }
      chart.set({ series: [{ name: 'data', y: y, color: 0, width: 1.5 }, { name: 'one-step forecast', y: r.fit, color: 1, width: 2.5 },
        { name: 'future forecast', x: fx, y: fc, color: 2, dash: true, width: 2.5 }] });
      readout(f.readout, [['Weight on newest value', Math.round(a * 100) + '%'], ['Weight 5 steps back', Math.round(a * Math.pow(1 - a, 5) * 100) + '%'],
        ['Squared error', f1(r.sse)], ['Best alpha here', f2(best)]]);
    }
    up();
  };

  /* ------------------------------------------------------------ Holt-Winters (additive) */
  function holtWinters(y, m, a, b, g, hor) {
    var n = y.length, lvl = mean(y.slice(0, m)), tr = (mean(y.slice(m, 2 * m)) - mean(y.slice(0, m))) / m;
    var s = y.slice(0, m).map(function (v) { return v - lvl; }), fit = [];
    for (var t = 0; t < n; t++) {
      var si = s[t % m];
      fit.push(t < m ? null : lvl + tr + si);
      var l0 = lvl;
      lvl = a * (y[t] - si) + (1 - a) * (l0 + tr);
      tr = b * (lvl - l0) + (1 - b) * tr;
      s[t % m] = g * (y[t] - lvl) + (1 - g) * si;
    }
    var fc = [];
    for (var k = 1; k <= hor; k++) fc.push(lvl + k * tr + s[(n + k - 1) % m]);
    return { fit: fit, fc: fc };
  }
  W['holt-winters'] = function (host, params) {
    var f = frame(host, 'Holt-Winters', 'Level, trend and season are each smoothed with their own weight. The orange line is the forecast of the last 24 points that the model has not seen.');
    var m = 12, N = 96, ntr = 72;
    var y = gen(N, 8, [['trend', { start: 30, slope: 0.35 }], ['season', { period: m, amp: 8 }], ['noise', { sd: 1.5 }]]);
    var al = slider({ label: 'Level (α)', min: 0.01, max: 1, step: 0.01, value: p(params, 'alpha', 0.3), fmt: f2 }, up);
    var be = slider({ label: 'Trend (β)', min: 0, max: 1, step: 0.01, value: p(params, 'beta', 0.1), fmt: f2 }, up);
    var ga = slider({ label: 'Season (γ)', min: 0, max: 1, step: 0.01, value: p(params, 'gamma', 0.2), fmt: f2 }, up);
    f.controls.append(al.el, be.el, ga.el);
    var chart = Chart.draw(f.charts, { height: 240, x: 'time', series: [], marks: [{ x: ntr - 0.5, label: 'forecast starts' }] });
    function up() {
      var r = holtWinters(y.slice(0, ntr), m, al.get(), be.get(), ga.get(), N - ntr);
      var fx = range(N - ntr).map(function (k) { return ntr + k; });
      var mae = mean(r.fc.map(function (v, k) { return Math.abs(v - y[ntr + k]); }));
      var naive = mean(fx.map(function (t) { return Math.abs(y[t - m] - y[t]); }));
      chart.set({ series: [{ name: 'actual', y: y, color: 0, width: 1.5 }, { name: 'fitted', y: r.fit, color: 2, width: 2 },
        { name: 'forecast', x: fx, y: r.fc, color: 1, width: 2.5 }] });
      var better = mae < naive;
      readout(f.readout, [['Forecast error (MAE)', f2(mae)], ['Seasonal naive error', f2(naive)], [better ? 'Beats the baseline' : 'Worse than the baseline', better ? 'yes' : 'no', better ? 'good' : 'bad']]);
    }
    up();
  };

  /* ------------------------------------------------------------ differencing */
  W.differencing = function (host, params) {
    var f = frame(host, 'differencing', 'Differencing subtracts the previous value. It removes a trend. A seasonal difference removes a repeating pattern. The goal is a series with a steady mean and spread.');
    var n = 120, m = 12;
    var y = gen(n, 21, [['trend', { start: 10, slope: 0.4 }], ['season', { period: m, amp: 6 }], ['noise', { sd: 1.2 }]]);
    var d = slider({ label: 'Differences (d)', min: 0, max: 2, value: p(params, 'd', 0) }, up);
    var sd_ = check('Also take a seasonal difference (lag 12)', !!p(params, 'seasonal', false), up);
    f.controls.append(d.el, h('div.w-checks', sd_.el));
    var chart = Chart.draw(f.charts, { height: 230, x: 'time', series: [] });
    function diff(a, lag) { return a.map(function (v, i) { return i < lag || a[i - lag] == null || v == null ? null : v - a[i - lag]; }); }
    function up() {
      var z = y.slice();
      if (sd_.get()) z = diff(z, m);
      for (var i = 0; i < d.get(); i++) z = diff(z, 1);
      var ok = z.filter(function (v) { return v != null; }), half = Math.floor(ok.length / 2);
      var a = ok.slice(0, half), b = ok.slice(half);
      var pooled = (sd(a) + sd(b)) / 2 || 1;
      var steady = Math.abs(mean(a) - mean(b)) < 0.5 * pooled && sd(a) / sd(b) < 1.6 && sd(b) / sd(a) < 1.6 && sd(ok) < 1e9;
      chart.set({ series: [{ name: 'transformed series', y: z, color: 0 }], marks: [{ x: n / 2, label: 'halfway' }] });
      readout(f.readout, [['Mean, first half', f2(mean(a))], ['Mean, second half', f2(mean(b))], ['Spread, first / second half', f2(sd(a)) + ' / ' + f2(sd(b))],
        [steady ? 'Looks stationary' : 'Not steady yet', steady ? 'yes' : 'no', steady ? 'good' : 'bad']]);
    }
    up();
  };

  /* ------------------------------------------------------------ ACF */
  function acf(y, maxLag) {
    var n = y.length, m = mean(y), c0 = sum(y.map(function (v) { return (v - m) * (v - m); })), out = [];
    for (var k = 1; k <= maxLag; k++) {
      var s = 0; for (var t = k; t < n; t++) s += (y[t] - m) * (y[t - k] - m);
      out.push(s / c0);
    }
    return out;
  }
  W.acf = function (host, params) {
    var f = frame(host, 'autocorrelation (ACF)', 'Each bar shows how much the series looks like itself shifted by that many steps. Bars outside the dashed lines are unlikely to be pure luck.');
    var n = 150;
    var procs = [['white', 'White noise'], ['ar1', 'AR(1) (memory)'], ['walk', 'Random walk'], ['trend', 'Trend + noise'], ['season', 'Season (period 12) + noise']];
    var pr = select('Process', procs, p(params, 'process', 'ar1'), up);
    var phi = slider({ label: 'Memory φ (AR only)', min: -0.95, max: 0.95, step: 0.05, value: p(params, 'phi', 0.7), fmt: f2 }, up);
    f.controls.append(pr.el, phi.el);
    var c1 = Chart.draw(f.charts, { height: 150, series: [], x: 'time' });
    var c2 = Chart.draw(f.charts, { height: 170, series: [], x: 'lag', title: 'ACF' });
    function up() {
      var k = pr.get(), y;
      if (k === 'white') y = gen(n, 31, [['noise', { sd: 1 }]]);
      else if (k === 'ar1') y = gen(n, 31, [['ar1', { phi: phi.get(), sd: 1 }]]);
      else if (k === 'walk') y = gen(n, 31, [['randomWalk', { sd: 1 }]]);
      else if (k === 'trend') y = gen(n, 31, [['trend', { slope: 0.1 }], ['noise', { sd: 1.5 }]]);
      else y = gen(n, 31, [['season', { period: 12, amp: 3 }], ['noise', { sd: 1 }]]);
      var a = acf(y, 30), bound = 1.96 / Math.sqrt(n);
      c1.set({ series: [{ name: 'series', y: y }] });
      c2.set({ series: [{ name: 'ACF', kind: 'bar', x: range(30).map(function (i) { return i + 1; }), y: a, color: 0 }],
        marks: [{ y: bound }, { y: -bound }], yMin: -1.05, yMax: 1.05 });
      var out = a.filter(function (v) { return Math.abs(v) > bound; }).length;
      readout(f.readout, [['Lags outside the lines', out + ' of 30'], ['Lag 1', f2(a[0])], ['Lag 12', f2(a[11])]]);
    }
    up();
  };

  /* ------------------------------------------------------------ train / test split */
  W['train-test-split'] = function (host, params) {
    var f = frame(host, 'train / test split', 'A random split mixes the future into the training set. The test looks easy, but the score is too good to be true. Only a split by time is honest.');
    var n = 60;
    var y = gen(n, 6, [['trend', { start: 20, slope: 0.5 }], ['season', { period: 12, amp: 5 }], ['noise', { sd: 2 }]]);
    var frac = slider({ label: 'Share used for training', min: 50, max: 90, step: 5, value: p(params, 'train', 70), fmt: function (v) { return v + '%'; } }, up);
    var mode = select('Split method', [['time', 'By time (honest)'], ['random', 'Random shuffle (leaks)']], p(params, 'mode', 'time'), up);
    f.controls.append(frac.el, mode.el);
    var chart = Chart.draw(f.charts, { height: 230, x: 'time', series: [] });
    function up() {
      var nt = Math.round(n * frac.get() / 100), isTrain = new Array(n).fill(false), i;
      if (mode.get() === 'time') for (i = 0; i < nt; i++) isTrain[i] = true;
      else { var order = U.shuffle(range(n), 99); for (i = 0; i < nt; i++) isTrain[order[i]] = true; }
      var tr = { x: [], y: [] }, te = { x: [], y: [] };
      y.forEach(function (v, t) { var o = isTrain[t] ? tr : te; o.x.push(t); o.y.push(v); });
      // honest error: last training value (naive). random split: average of nearest training neighbours.
      var errs = te.x.map(function (t, k) {
        var pred;
        if (mode.get() === 'time') pred = y[nt - 1];
        else {
          var l = t - 1, r = t + 1;
          while (l >= 0 && !isTrain[l]) l--;
          while (r < n && !isTrain[r]) r++;
          pred = l < 0 ? y[r] : r >= n ? y[l] : (y[l] + y[r]) / 2;
        }
        return Math.abs(pred - te.y[k]);
      });
      chart.set({ series: [{ name: 'train', kind: 'dots', x: tr.x, y: tr.y, color: 0 }, { name: 'test', kind: 'dots', x: te.x, y: te.y, color: 1 }],
        marks: mode.get() === 'time' ? [{ x: nt - 0.5, label: 'split' }] : [] });
      var leak = mode.get() === 'random';
      readout(f.readout, [['Training points', String(nt)], ['Test points', String(n - nt)],
        [leak ? 'Test error (neighbours in the future)' : 'Test error (forecast from the past)', f2(mean(errs)), leak ? 'bad' : 'good']]);
    }
    up();
  };

  /* ------------------------------------------------------------ walk-forward */
  W['walk-forward'] = function (host, params) {
    var f = frame(host, 'walk-forward backtest', 'Each row is one test. The model trains on the blue cells, then predicts the orange cells that come after. Then the origin moves forward.');
    var N = 24;
    var init = slider({ label: 'First training size', min: 6, max: 16, value: p(params, 'initial', 10) }, up);
    var hor = slider({ label: 'Forecast horizon', min: 1, max: 6, value: p(params, 'horizon', 3) }, up);
    var step = slider({ label: 'Step between origins', min: 1, max: 6, value: p(params, 'step', 3) }, up);
    var gap = slider({ label: 'Gap (embargo)', min: 0, max: 4, value: p(params, 'gap', 0) }, up);
    var mode = select('Window', [['expanding', 'Expanding (keep all past)'], ['sliding', 'Sliding (fixed size)']], p(params, 'mode', 'expanding'), up);
    f.controls.append(init.el, hor.el, step.el, gap.el, mode.el);
    var grid = h('div.wf-grid', { role: 'img', 'aria-label': 'Walk-forward folds' });
    f.charts.appendChild(grid);
    function up() {
      U.clear(grid);
      var folds = 0, i = init.get(), H = hor.get(), G = gap.get();
      for (var o = i; o + G + H <= N; o += step.get()) {
        folds++;
        var start = mode.get() === 'sliding' ? o - i : 0, row = h('div.wf-row', h('span.wf-label', 'Fold ' + folds));
        var cells = h('div.wf-cells');
        for (var t = 0; t < N; t++) {
          var cls = t >= start && t < o ? 'train' : (t >= o && t < o + G ? 'gap' : (t >= o + G && t < o + G + H ? 'test' : ''));
          cells.appendChild(h('i.wf-cell' + (cls ? '.' + cls : '')));
        }
        row.appendChild(cells); grid.appendChild(row);
      }
      grid.appendChild(h('div.wf-legend', h('span', h('i.wf-cell.train'), ' train'), h('span', h('i.wf-cell.gap'), ' gap'), h('span', h('i.wf-cell.test'), ' test'), h('span.muted', 'time →')));
      readout(f.readout, [['Number of tests', String(folds)], ['Points predicted', String(folds * H)]]);
    }
    up();
  };

  /* ------------------------------------------------------------ lag features */
  W['lag-features'] = function (host, params) {
    var f = frame(host, 'lag and rolling features', 'To predict y at time t you may only use values before t. A rolling mean must be shifted by one step, or it contains the answer.');
    var y = [12, 15, 14, 18, 21, 19, 24, 27, 25, 30, 33, 31, 36, 38];
    var lags = slider({ label: 'Number of lags', min: 1, max: 4, value: p(params, 'lags', 2) }, up);
    var rw = slider({ label: 'Rolling window', min: 2, max: 4, value: p(params, 'window', 3) }, up);
    var shifted = check('Shift the rolling mean by 1 (correct)', p(params, 'shift', true), up);
    var row = slider({ label: 'Row to inspect (t)', min: 0, max: y.length - 1, value: p(params, 'row', 6) }, up);
    f.controls.append(lags.el, rw.el, row.el, h('div.w-checks', shifted.el));
    var tableHost = h('div.table-wrap'); f.charts.appendChild(tableHost);
    function up() {
      var L = lags.get(), R = rw.get(), sh = shifted.get(), sel = row.get(), lost = 0;
      var head = h('tr', h('th', 't'), h('th', 'y (target)'));
      for (var k = 1; k <= L; k++) head.appendChild(h('th', 'lag_' + k));
      head.appendChild(h('th', 'roll_mean_' + R + (sh ? ' (shifted)' : ' (not shifted)')));
      var body = h('tbody');
      y.forEach(function (v, t) {
        var tr = h('tr' + (t === sel ? '.sel' : ''));
        var start = sh ? t - R : t - R + 1, end = sh ? t - 1 : t;
        var rollOk = start >= 0, lagOk = t - L >= 0;
        if (!(rollOk && lagOk)) { tr.classList.add('drop'); lost++; }
        tr.appendChild(h('td', String(t))); tr.appendChild(h('td', String(v)));
        for (var k = 1; k <= L; k++) tr.appendChild(h('td', t - k >= 0 ? String(y[t - k]) : '–'));
        var rm = rollOk ? f1(mean(y.slice(start, end + 1))) : '–';
        tr.appendChild(h('td' + (!sh && rollOk ? '.leak' : ''), rm));
        body.appendChild(tr);
      });
      U.clear(tableHost);
      tableHost.appendChild(h('table.w-table', h('thead', head), body));
      var used = [];
      for (var k2 = 1; k2 <= L; k2++) if (sel - k2 >= 0) used.push('y(' + (sel - k2) + ')');
      readout(f.readout, [['Rows lost to missing values', String(lost)], ['Row ' + sel + ' uses', used.join(', ') || 'nothing yet'],
        [sh ? 'No leakage' : 'Leakage: roll mean includes y(t)', sh ? 'ok' : 'LEAK', sh ? 'good' : 'bad']]);
    }
    up();
  };

  /* ------------------------------------------------------------ quantile (pinball) loss */
  W['quantile-loss'] = function (host, params) {
    var f = frame(host, 'pinball loss', 'Pinball loss punishes under- and over-forecasts differently. For tau = 0.9, being too low costs 9 times more than being too high, so the best forecast is the 90th percentile.');
    var data = gen(80, 3, [['noise', { sd: 1 }]]).map(function (v) { return Math.exp(0.5 * v + 3); });
    var sorted = data.slice().sort(function (a, b) { return a - b; });
    var tau = slider({ label: 'Quantile (τ)', min: 0.05, max: 0.95, step: 0.05, value: p(params, 'tau', 0.9), fmt: f2 }, up);
    f.controls.append(tau.el);
    var c1 = Chart.draw(f.charts, { height: 170, title: 'Loss for one forecast, by error (actual − forecast)', series: [], x: 'error' });
    var c2 = Chart.draw(f.charts, { height: 190, title: 'Average loss for our 80 data points, by forecast value', series: [], x: 'forecast value' });
    function loss(e, q) { return e >= 0 ? q * e : (q - 1) * e; }
    function up() {
      var q = tau.get(), es = range(81).map(function (i) { return -20 + i * 0.5; });
      c1.set({ series: [{ name: 'pinball loss', x: es, y: es.map(function (e) { return loss(e, q); }), color: 0 }], marks: [{ x: 0 }] });
      var lo = sorted[0], hi = sorted[sorted.length - 1], xs = range(100).map(function (i) { return lo + (hi - lo) * i / 99; });
      var ys = xs.map(function (c) { return mean(data.map(function (v) { return loss(v - c, q); })); });
      var qv = quantile(sorted, q);
      c2.set({ series: [{ name: 'average loss', x: xs, y: ys, color: 1 }], marks: [{ x: qv, label: 'best: ' + f1(qv) }] });
      readout(f.readout, [['Cost of forecasting too low', f2(q) + ' per unit'], ['Cost of forecasting too high', f2(1 - q) + ' per unit'], ['Best forecast (empirical quantile)', f1(qv)]]);
    }
    up();
  };

  /* ------------------------------------------------------------ anomaly z-score */
  W['anomaly-zscore'] = function (host, params) {
    var f = frame(host, 'z-score anomaly detector', 'A point is flagged when it is more than z standard deviations from the average. With a trend, the global average fails; a rolling window follows the data.');
    var n = 140, spikes = [28, 55, 80, 104, 125];
    var y = gen(n, 17, [['trend', { start: 20, slope: 0.12 }], ['season', { period: 14, amp: 2 }], ['noise', { sd: 1.2 }], ['spike', { at: spikes, size: 9 }]]);
    var z = slider({ label: 'Threshold (z)', min: 1, max: 5, step: 0.25, value: p(params, 'z', p(params, 'threshold', 3)), fmt: f2 }, up);
    var mode = select('Reference', [['global', 'Whole series'], ['rolling', 'Rolling window (past only)']], p(params, 'mode', 'global'), up);
    var win = slider({ label: 'Rolling window', min: 10, max: 40, value: p(params, 'window', 20) }, up);
    f.controls.append(z.el, mode.el, win.el);
    var chart = Chart.draw(f.charts, { height: 230, x: 'time', series: [] });
    function up() {
      var thr = z.get(), W_ = win.get(), flagged = [];
      var gm = mean(y), gs = sd(y);
      for (var t = 0; t < n; t++) {
        var m, s;
        if (mode.get() === 'global') { m = gm; s = gs; }
        else { if (t < W_) continue; var w = y.slice(t - W_, t); m = mean(w); s = sd(w) || 1e-9; }
        if (Math.abs((y[t] - m) / s) > thr) flagged.push(t);
      }
      var caught = spikes.filter(function (t) { return flagged.indexOf(t) >= 0; }).length;
      chart.set({ series: [{ name: 'series', y: y, color: 0 }, { name: 'flagged', kind: 'dots', x: flagged, y: flagged.map(function (t) { return y[t]; }), color: 4, r: 5 }] });
      var fa = flagged.length - caught;
      readout(f.readout, [['Real spikes found', caught + ' of ' + spikes.length, caught === spikes.length ? 'good' : ''], ['False alarms', String(fa), fa > 3 ? 'bad' : ''], ['Points flagged', String(flagged.length)]]);
    }
    up();
  };

  /* ------------------------------------------------------------ Chronos tokens */
  W['chronos-tokens'] = function (host, params) {
    var f = frame(host, 'Chronos-style tokens', 'Chronos divides the series by its average size (scaling), then puts each value into one of many bins. The bin number is the "token". More bins give a smaller rounding error.');
    var n = 48;
    var y = gen(n, 12, [['trend', { start: 200, slope: 1.5 }], ['season', { period: 12, amp: 40 }], ['noise', { sd: 8 }]]);
    var bins = select('Number of bins', [['16', '16'], ['64', '64'], ['256', '256'], ['4096', '4096 (like Chronos)']], String(p(params, 'bins', 256)), up);
    var scale = check('Scale by the mean absolute value first', p(params, 'scale', true), up);
    f.controls.append(bins.el, h('div.w-checks', scale.el));
    var chart = Chart.draw(f.charts, { height: 220, x: 'time', series: [] });
    var tokensEl = h('p.w-tokens'); f.charts.appendChild(tokensEl);
    function up() {
      var B = +bins.get(), lo = -15, hi = 15, sc = scale.get() ? mean(y.map(Math.abs)) : 1, tok = [], rec = [];
      y.forEach(function (v) {
        var z = Math.max(lo, Math.min(hi, v / sc)), k = Math.min(B - 1, Math.floor((z - lo) / (hi - lo) * B));
        tok.push(k); rec.push((lo + (k + 0.5) * (hi - lo) / B) * sc);
      });
      var err = mean(y.map(function (v, i) { return Math.abs(v - rec[i]); }));
      chart.set({ series: [{ name: 'original', y: y, color: 0 }, { name: 'after tokens', y: rec, color: 1, kind: 'step', width: 2 }] });
      tokensEl.textContent = 'First tokens: ' + tok.slice(0, 12).join(', ') + ' …';
      readout(f.readout, [['Scale factor', f1(sc)], ['Average rounding error', f2(err)], ['Distinct tokens used', String(new Set(tok).size)]]);
    }
    up();
  };

  /* ------------------------------------------------------------ sliding window */
  W['sliding-window'] = function (host, params) {
    var f = frame(host, 'sliding windows', 'To use a normal model, cut the series into pieces. Each piece has inputs (blue) and a target (orange). The window moves by the stride.');
    var N = 18, vals = range(N).map(function (i) { return i + 1; });
    var L = slider({ label: 'Input length', min: 2, max: 8, value: p(params, 'input', p(params, 'window', 4)) }, up);
    var H = slider({ label: 'Horizon (targets)', min: 1, max: 4, value: p(params, 'horizon', 1) }, up);
    var St = slider({ label: 'Stride', min: 1, max: 4, value: p(params, 'stride', 1) }, up);
    var Sel = slider({ label: 'Show window number', min: 1, max: 10, value: 1 }, up);
    f.controls.append(L.el, H.el, St.el, Sel.el);
    var strip = h('div.sw-strip'), tableHost = h('div.table-wrap');
    f.charts.append(strip, tableHost);
    function up() {
      var l = L.get(), hz = H.get(), st = St.get();
      var count = Math.max(0, Math.floor((N - l - hz) / st) + 1);
      var selInput = f.controls.querySelectorAll('input[type=range]')[3];
      selInput.max = Math.max(1, count);
      var sel = Math.min(Sel.get(), Math.max(1, count)) - 1, s0 = sel * st;
      U.clear(strip);
      vals.forEach(function (v, i) {
        var cls = i >= s0 && i < s0 + l ? 'in' : (i >= s0 + l && i < s0 + l + hz ? 'out' : '');
        strip.appendChild(h('span.sw-cell' + (cls ? '.' + cls : ''), String(v)));
      });
      var body = h('tbody');
      for (var w = 0; w < Math.min(count, 6); w++) {
        var a = w * st;
        body.appendChild(h('tr' + (w === sel ? '.sel' : ''), h('td', String(w + 1)), h('td', '[' + vals.slice(a, a + l).join(', ') + ']'), h('td', '[' + vals.slice(a + l, a + l + hz).join(', ') + ']')));
      }
      U.clear(tableHost);
      tableHost.appendChild(h('table.w-table', h('thead', h('tr', h('th', '#'), h('th', 'inputs (X)'), h('th', 'target (y)'))), body));
      readout(f.readout, [['Samples made', String(count)], ['Formula', '(' + N + ' − ' + l + ' − ' + hz + ') ÷ ' + st + ' + 1 → ' + count]]);
    }
    up();
  };

  /* ------------------------------------------------------------ conformal prediction */
  W.conformal = function (host, params) {
    var f = frame(host, 'conformal prediction interval', 'We measure the forecast errors on a calibration set, then use their quantile as the interval half-width. If the noise grows later, the coverage drops, because the past no longer looks like the future.');
    var nc = 80, nt = 80, N = nc + nt;
    var base = gen(N, 14, [['noise', { sd: 1 }]]);
    var cov = slider({ label: 'Target coverage', min: 50, max: 99, step: 1, value: p(params, 'coverage', 90), fmt: function (v) { return v + '%'; } }, up);
    var drift = check('Noise grows in the test period', !!p(params, 'drift', false), up);
    f.controls.append(cov.el, h('div.w-checks', drift.el));
    var chart = Chart.draw(f.charts, { height: 240, x: 'time', series: [], marks: [{ x: nc - 0.5, label: 'calibration | test' }] });
    function up() {
      var fcst = range(N).map(function (t) { return 30 + 6 * Math.sin(2 * Math.PI * t / 20); });
      var y = fcst.map(function (v, t) { return v + base[t] * 2 * (drift.get() && t >= nc ? 1 + 1.5 * (t - nc) / nt : 1); });
      var res = []; for (var t = 0; t < nc; t++) res.push(Math.abs(y[t] - fcst[t]));
      res.sort(function (a, b) { return a - b; });
      var alpha = 1 - cov.get() / 100, k = Math.min(nc, Math.ceil((nc + 1) * (1 - alpha))), q = res[k - 1];
      var xs = range(nt).map(function (i) { return nc + i; }), inside = 0, out = [];
      xs.forEach(function (t) { if (Math.abs(y[t] - fcst[t]) <= q) inside++; else out.push(t); });
      chart.set({ series: [
        { name: 'interval', kind: 'band', x: xs, y: xs.map(function (t) { return fcst[t] - q; }), y2: xs.map(function (t) { return fcst[t] + q; }), color: 0, legend: true },
        { name: 'actual', y: y, color: 0, width: 1.5 }, { name: 'forecast', x: xs, y: xs.map(function (t) { return fcst[t]; }), color: 1, dash: true },
        { name: 'outside', kind: 'dots', x: out, y: out.map(function (t) { return y[t]; }), color: 4, r: 4 }] });
      var actual = Math.round(inside / nt * 100), good = actual >= cov.get() - 5;
      readout(f.readout, [['Interval half-width (±)', f2(q)], ['Target coverage', cov.get() + '%'], ['Actual coverage in test', actual + '%', good ? 'good' : 'bad']]);
    }
    up();
  };

  T.Widgets = {
    names: Object.keys(W),
    render: function (host, spec) {
      var fn = W[spec.name];
      if (!fn) { host.appendChild(h('div.tsp-error', 'Unknown widget: ' + spec.name)); return; }
      try { fn(host, spec.params || {}); } catch (e) { console.error(e); host.appendChild(h('div.tsp-error', 'This widget could not load.')); }
    }
  };
})(window.TSP = window.TSP || {});
