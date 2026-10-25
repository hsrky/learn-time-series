/* editor.js - Python syntax highlighter + a light code editor
   (a transparent <textarea> on top of a highlighted <pre>; no external dependency). */
(function (T) {
  'use strict';
  var U = T.U, h = U.h;

  /* ------------------------------------------------------------ highlighter */
  var KEYWORDS = 'False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split(' ');
  var BUILTINS = 'abs all any bool dict enumerate filter float int isinstance len list map max min print range reversed round set sorted str sum tuple type zip self super object open next iter divmod pow'.split(' ');
  var KW = {}, BI = {};
  KEYWORDS.forEach(function (k) { KW[k] = 1; });
  BUILTINS.forEach(function (k) { BI[k] = 1; });
  var TOKEN = new RegExp([
    '(#[^\\n]*)',                                                       // 1 comment
    '([rRbBfFuU]{0,2}(?:"""[\\s\\S]*?(?:"""|$)|\'\'\'[\\s\\S]*?(?:\'\'\'|$)))', // 2 triple string
    '([rRbBfFuU]{0,2}(?:"(?:\\\\.|[^"\\\\\\n])*"?|\'(?:\\\\.|[^\'\\\\\\n])*\'?))', // 3 string
    '(\\b\\d[\\d_]*(?:\\.\\d*)?(?:[eE][+-]?\\d+)?\\b)',                 // 4 number
    '(@[A-Za-z_][\\w.]*)',                                              // 5 decorator
    '([A-Za-z_]\\w*)'                                                   // 6 identifier
  ].join('|'), 'g');

  function highlight(code) {
    var out = '', last = 0, prev = '', m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(code))) {
      out += U.esc(code.slice(last, m.index));
      var t = m[0], cls = null;
      if (m[1]) cls = 'tk-c';
      else if (m[2] || m[3]) cls = 'tk-s';
      else if (m[4]) cls = 'tk-n';
      else if (m[5]) cls = 'tk-d';
      else if (KW[t]) cls = 'tk-k';
      else if (prev === 'def' || prev === 'class') cls = 'tk-f';
      else if (BI[t]) cls = 'tk-b';
      out += cls ? '<span class="' + cls + '">' + U.esc(t) + '</span>' : U.esc(t);
      if (m[6]) prev = t; else if (!/^\s+$/.test(t)) prev = '';
      last = m.index + t.length;
      if (t.length === 0) TOKEN.lastIndex++;
    }
    return out + U.esc(code.slice(last));
  }

  /* ------------------------------------------------------------ editor */
  function create(opts) {
    opts = opts || {};
    var ta = h('textarea.ed-ta', { spellcheck: 'false', autocapitalize: 'off', autocomplete: 'off', autocorrect: 'off',
      'aria-label': opts.label || 'Python code editor', wrap: 'off' });
    var hl = h('pre.ed-hl', { 'aria-hidden': 'true' });
    var layer = h('div.ed-layer', hl);
    var gutter = h('pre.ed-gutter', { 'aria-hidden': 'true' });
    var gutterIn = h('div.ed-gutter-in'); gutter.appendChild(gutterIn);
    var el = h('div.editor', gutter, h('div.ed-main', layer, ta));
    var escaped = false;

    function sync() {
      var v = ta.value;
      hl.innerHTML = highlight(v) + '\n';
      var n = v.split('\n').length, g = '';
      for (var i = 1; i <= n; i++) g += i + '\n';
      gutterIn.textContent = g;
      scroll();
    }
    function scroll() {
      layer.style.transform = 'translate(' + (-ta.scrollLeft) + 'px,' + (-ta.scrollTop) + 'px)';
      gutterIn.style.transform = 'translateY(' + (-ta.scrollTop) + 'px)';
    }
    function changed() { sync(); if (opts.onChange) opts.onChange(ta.value); }

    /** Insert text at the caret, keeping the browser undo stack when possible. */
    function insert(text) {
      ta.focus();
      var ok = false;
      try { ok = document.execCommand('insertText', false, text); } catch (e) { ok = false; }
      if (!ok) {
        ta.setRangeText(text, ta.selectionStart, ta.selectionEnd, 'end');
        changed();
      }
    }
    function lineBounds() {
      var v = ta.value, s = ta.selectionStart, e = ta.selectionEnd;
      var a = v.lastIndexOf('\n', s - 1) + 1, b = v.indexOf('\n', e > s && v[e - 1] === '\n' ? e - 1 : e);
      return { a: a, b: b < 0 ? v.length : b };
    }
    function replaceRange(a, b, text, selA, selB) {
      ta.setSelectionRange(a, b); insert(text);
      ta.setSelectionRange(selA, selB);
    }
    function indentLines(dedent) {
      var lb = lineBounds(), v = ta.value, s = ta.selectionStart, e = ta.selectionEnd;
      var lines = v.slice(lb.a, lb.b).split('\n'), delta0 = 0, deltaAll = 0;
      var out = lines.map(function (ln, i) {
        if (!dedent) { deltaAll += 4; if (i === 0) delta0 = 4; return '    ' + ln; }
        var rm = Math.min(4, (/^ */.exec(ln)[0]).length);
        deltaAll -= rm; if (i === 0) delta0 = -rm; return ln.slice(rm);
      });
      replaceRange(lb.a, lb.b, out.join('\n'), Math.max(lb.a, s + delta0), e + deltaAll);
    }
    function toggleComment() {
      var lb = lineBounds(), v = ta.value, s = ta.selectionStart, e = ta.selectionEnd;
      var lines = v.slice(lb.a, lb.b).split('\n'), all = lines.every(function (l) { return !l.trim() || /^\s*#/.test(l); }), d = 0;
      var out = lines.map(function (l) {
        if (!l.trim()) return l;
        if (all) { var r = l.replace(/^(\s*)# ?/, '$1'); d += r.length - l.length; return r; }
        d += 2; return l.replace(/^(\s*)/, '$1# ');
      });
      replaceRange(lb.a, lb.b, out.join('\n'), s, e + d);
    }

    ta.addEventListener('keydown', function (e) {
      var mod = e.ctrlKey || e.metaKey;
      if (mod && e.key === 'Enter') { e.preventDefault(); if (opts.onRun) opts.onRun(); return; }
      if (mod && (e.key === "'" || e.code === 'Quote')) { e.preventDefault(); if (opts.onSubmit) opts.onSubmit(); return; }
      if (mod && e.key === '/') { e.preventDefault(); toggleComment(); return; }
      if (e.key === 'Escape') { escaped = true; return; }
      if (e.key === 'Tab') {
        if (escaped) { escaped = false; return; }               // Esc then Tab leaves the editor
        e.preventDefault();
        var multi = ta.value.slice(ta.selectionStart, ta.selectionEnd).indexOf('\n') >= 0;
        if (multi || e.shiftKey) indentLines(e.shiftKey);
        else insert('    '.slice(0, 4 - ((ta.selectionStart - (ta.value.lastIndexOf('\n', ta.selectionStart - 1) + 1)) % 4)));
        return;
      }
      escaped = false;
      if (e.key === 'Enter' && !mod && !e.shiftKey) {
        var v = ta.value, s = ta.selectionStart, ls = v.lastIndexOf('\n', s - 1) + 1;
        var line = v.slice(ls, s), ind = /^[ \t]*/.exec(line)[0];
        if (/:\s*(#.*)?$/.test(line.replace(/\s+$/, '')) && ta.selectionStart === ta.selectionEnd) ind += '    ';
        e.preventDefault(); insert('\n' + ind); return;
      }
      if (e.key === 'Backspace' && ta.selectionStart === ta.selectionEnd) {
        var v2 = ta.value, p = ta.selectionStart, ls2 = v2.lastIndexOf('\n', p - 1) + 1, before = v2.slice(ls2, p);
        if (before.length >= 4 && /^ +$/.test(before) && before.length % 4 === 0) {
          e.preventDefault(); ta.setSelectionRange(p - 4, p);
          var done = false;
          try { done = document.execCommand('delete'); } catch (x) { done = false; }
          if (!done || ta.value.length === v2.length) { ta.setRangeText('', p - 4, p, 'end'); changed(); }
        }
      }
    });
    ta.addEventListener('input', changed);
    ta.addEventListener('scroll', scroll);
    ta.value = opts.value || '';
    sync();

    return {
      el: el,
      getValue: function () { return ta.value; },
      setValue: function (v) { ta.value = v; changed(); },
      focus: function () { ta.focus(); },
      refresh: sync
    };
  }

  T.Editor = { create: create, highlight: highlight };
})(window.TSP = window.TSP || {});
