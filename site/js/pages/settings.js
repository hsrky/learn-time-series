/* pages/settings.js - theme, text size, backup (export / import) and reset. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  T.pages.settings = {
    render: function (el) {
      T.setTitle('Settings');
      var wrap = h('div.wrap.narrow'); el.appendChild(wrap);
      var s = S.get().settings;
      wrap.appendChild(h('div.page-head', h('h1', 'Settings')));

      function set(k, v) { S.update(function (st) { st.settings[k] = v; }, 'settings'); T.applySettings(); }

      var themeBtns = [['auto', 'Match my device'], ['light', 'Light'], ['dark', 'Dark']].map(function (t) {
        return h('label.seg-opt', h('input', { type: 'radio', name: 'theme', value: t[0], checked: s.theme === t[0], onchange: function () { set('theme', t[0]); } }), h('span', t[1]));
      });
      wrap.appendChild(h('section.card', h('h2', 'Theme'), h('div.seg-group', { role: 'radiogroup', 'aria-label': 'Theme' }, themeBtns)));

      var out = h('output', s.fontSize + ' px');
      var range = h('input', { type: 'range', min: 14, max: 22, step: 1, value: s.fontSize, 'aria-label': 'Text size', oninput: function () { out.textContent = range.value + ' px'; set('fontSize', +range.value); } });
      wrap.appendChild(h('section.card', h('h2', 'Text size'), h('div.row', range, out), h('p.muted.small', 'The default is 16 px.')));

      var fileInput = h('input', { type: 'file', accept: 'application/json,.json', hidden: true, onchange: function () {
        var f = fileInput.files[0]; if (!f) return;
        var r = new FileReader();
        r.onload = function () {
          try {
            if (!window.confirm('Replace your current progress with this backup?')) return;
            S.importJSON(String(r.result)); T.applySettings(); U.toast('Progress imported'); T.R.render();
          } catch (e) { U.toast(e.message || 'Could not read this file.', 'bad'); }
        };
        r.readAsText(f); fileInput.value = '';
      } });
      wrap.appendChild(h('section.card', h('h2', 'Backup'),
        h('p', 'Your progress lives in this browser only. Save a backup file to move it to another device.'),
        h('div.row', h('button.btn', { type: 'button', onclick: function () { U.download('timeseries-path-progress-' + U.ymd() + '.json', S.exportJSON()); } }, 'Export progress'),
          h('button.btn', { type: 'button', onclick: function () { fileInput.click(); } }, 'Import progress'), fileInput),
        S.isMemoryOnly() ? h('p.warn', 'Your browser blocks storage, so progress is not saved. Export a backup before you close this tab.') : null));

      wrap.appendChild(h('section.card', h('h2', 'Reset'),
        h('p', 'Delete all progress, code, flashcards and settings from this browser.'),
        h('button.btn.danger', { type: 'button', onclick: function () {
          if (window.confirm('Delete ALL progress in this browser? This cannot be undone.')) { S.reset(); T.applySettings(); U.toast('Progress reset'); T.R.render(); }
        } }, 'Reset everything')));

      var raw = C.raw;
      wrap.appendChild(h('section.card', h('h2', 'About'),
        h('p.muted', 'TimeSeries Path. Content built ' + (raw.built || 'unknown') + (raw.samples ? ' (includes sample content)' : '') + '. ' +
          (raw.counts ? raw.counts.lessons + ' lessons, ' + raw.counts.problems + ' problems, ' + raw.counts.glossary + ' glossary terms.' : '')),
        h('p.muted.small', 'Python runs in your browser with Pyodide. Nothing you type is sent to a server.')));
    }
  };
})(window.TSP = window.TSP || {});
