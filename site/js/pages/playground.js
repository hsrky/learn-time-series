/* pages/playground.js - free Python (numpy + pandas, and scipy / statsmodels / scikit-learn on import). */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, J = T.Judge;
  T.pages = T.pages || {};

  var DEFAULT = '# Free Python. numpy (np) and pandas (pd) are ready.\n# The value of the last line is printed for you.\n\nidx = pd.date_range("2024-01-01", periods=10, freq="D")\ns = pd.Series(np.arange(10) ** 2, index=idx)\nprint(s.rolling(3).mean())\ns.diff()\n';
  var EXAMPLES = [
    ['Rolling mean', DEFAULT],
    ['Resample hourly to daily', 'idx = pd.date_range("2024-01-01", periods=72, freq="h")\ns = pd.Series(np.arange(72, dtype=float), index=idx)\ns.resample("D").sum()\n'],
    ['Autocorrelation', 'rng = np.random.default_rng(0)\ny = pd.Series(np.cumsum(rng.normal(size=200)))\nfor lag in [1, 2, 5, 10]:\n    print(lag, round(y.autocorr(lag), 3))\n'],
    ['statsmodels OLS', 'import statsmodels.api as sm\nt = np.arange(50)\ny = 3 + 0.5 * t + np.random.default_rng(1).normal(size=50)\nfit = sm.OLS(y, sm.add_constant(t)).fit()\nprint(fit.params)\n']
  ];

  T.pages.playground = {
    render: function (el) {
      T.setTitle('Playground');
      el.classList.add('page-workspace');
      J.boot();
      var code = S.get().playground || DEFAULT, running = false;
      var save = U.debounce(function () { S.quiet(function (s) { s.playground = code; }); }, 400);
      var editor = T.Editor.create({ value: code, label: 'Python playground editor', onChange: function (v) { code = v; save(); }, onRun: run, onSubmit: run });
      var out = h('pre.pg-out', { 'aria-live': 'polite' }, 'Output appears here.');
      var runBtn = h('button.btn.primary', { type: 'button', onclick: run }, U.icon('play', 14), ' Run');
      var ex = h('select.input.sm', { 'aria-label': 'Load an example', onchange: function () {
        var e = EXAMPLES[+ex.value - 1]; if (e) { editor.setValue(e[1]); code = e[1]; save(); } ex.value = '';
      } }, h('option', { value: '' }, 'Examples…'), EXAMPLES.map(function (e, i) { return h('option', { value: i + 1 }, e[0]); }));
      async function run() {
        if (running) return;
        running = true; runBtn.disabled = true;
        out.className = 'pg-out'; out.textContent = J.state().state === 'ready' ? 'Running…' : 'Starting Python… the first run loads about 12 MB.';
        S.update(function () { S.touch(1); }, 'quiet');
        var r;
        try { r = await J.play(code); } catch (e) { r = { stdout: '', error: e.message }; }
        running = false; runBtn.disabled = false;
        out.className = 'pg-out' + (r.error ? ' has-error' : '');
        out.textContent = (r.stdout || '') + (r.error ? (r.stdout ? '\n' : '') + r.error : '') || '(no output)';
        if (r.ms != null && !r.error) out.textContent += (r.stdout ? '' : '') + '\n\n— finished in ' + Math.round(r.ms) + ' ms';
      }
      el.append(
        h('div.ws-bar', h('b', 'Playground'), h('span.muted.small.hide-sm', 'Free Python in your browser. Nothing is sent anywhere.'), h('span.grow'), ex, J.chip(),
          h('button.btn.sm', { type: 'button', onclick: function () { if (window.confirm('Clear the editor?')) { editor.setValue(''); code = ''; save(); } } }, 'Clear'), runBtn),
        h('div.pg', h('div.pg-ed', editor.el, h('p.ed-hint', 'Run: Ctrl/Cmd+Enter. Esc then Tab leaves the editor.')), h('div.pg-res', h('div.tabs.small', h('span.tab.on', 'Output')), out)));
      return function () { el.classList.remove('page-workspace'); S.quiet(function (s) { s.playground = code; }); };
    }
  };
})(window.TSP = window.TSP || {});
