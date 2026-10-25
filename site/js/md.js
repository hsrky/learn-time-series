/* md.js - turns the build's rendered lesson HTML into live content:
   quiz checks, charts, widgets, code blocks, tables and glossary tooltips. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, C = T.C;

  function readSpec(el) {
    try { return JSON.parse(el.getAttribute('data-spec')); } catch (e) { return null; }
  }

  /** Code block with a header, copy button and (for Python) "Open in playground". */
  function codeBlock(pre) {
    var lang = pre.getAttribute('data-lang') || 'python', code = pre.textContent;
    var box = h('div.codeblock.' + lang);
    var copy = h('button.btn.sm', { type: 'button', onclick: function () {
      U.copyText(code).then(function () { copy.textContent = 'Copied'; setTimeout(function () { copy.textContent = 'Copy'; }, 1500); });
    } }, 'Copy');
    var tools = [copy];
    if (lang === 'python') {
      tools.push(h('button.btn.sm.primary', { type: 'button', onclick: function () {
        T.S.quiet(function (s) { s.playground = code; });
        T.R.go('/playground');
      } }, U.icon('play', 14), ' Open in playground'));
    }
    box.appendChild(h('div.codeblock-head', h('span.cb-label', lang === 'notebook' ? 'Run on Kaggle / your laptop (not in the browser)' : 'Python'), h('span.cb-tools', tools)));
    var body = h('pre.code-view', { tabindex: 0 });
    body.innerHTML = T.Editor.highlight(code);
    box.appendChild(body);
    pre.replaceWith(box);
  }

  function hydrate(root, ctx) {
    ctx = ctx || {};
    root.querySelectorAll('.tsp-check').forEach(function (el) {
      var spec = readSpec(el); if (spec) T.Quiz.hydrateCheck(el, spec, ctx);
    });
    root.querySelectorAll('.tsp-chart').forEach(function (el) {
      var spec = readSpec(el); if (spec) T.Chart.draw(el, spec);
    });
    root.querySelectorAll('.tsp-widget').forEach(function (el) {
      var spec = readSpec(el); if (spec) T.Widgets.render(el, spec);
    });
    root.querySelectorAll('pre.tsp-code').forEach(codeBlock);
    root.querySelectorAll('pre > code').forEach(function (code) {
      var pre = code.parentNode;
      if (pre.parentNode && pre.parentNode.classList.contains('codeblock')) return;
      pre.classList.add('plain-code'); pre.tabIndex = 0;
    });
    root.querySelectorAll('table').forEach(function (t) {
      if (t.closest('.table-wrap')) return;
      var w = h('div.table-wrap'); t.replaceWith(w); w.appendChild(t);
    });
  }

  /* ------------------------------------------------------------ glossary tooltip */
  var tip = null, tipFor = null, hideTimer = null;
  function ensureTip() {
    if (tip) return tip;
    tip = h('div.term-tip', { role: 'tooltip', hidden: true,
      onmouseenter: function () { clearTimeout(hideTimer); }, onmouseleave: scheduleHide });
    document.body.appendChild(tip);
    return tip;
  }
  function showTip(el) {
    var key = el.getAttribute('data-term'), g = C.glossary[key];
    if (!g) return;
    clearTimeout(hideTimer);
    var t = ensureTip();
    U.clear(t);
    t.appendChild(h('b', g.term || key));
    t.appendChild(h('p', g.simple));
    if (g.example) t.appendChild(h('p.ex', 'Example: ' + g.example));
    t.appendChild(h('a.small', { href: '#/glossary?q=' + encodeURIComponent(key) }, 'Open in glossary'));
    t.hidden = false; tipFor = el;
    el.setAttribute('aria-describedby', 'term-tip'); t.id = 'term-tip';
    var r = el.getBoundingClientRect(), tw = t.offsetWidth, th = t.offsetHeight;
    var left = Math.min(Math.max(8, r.left + r.width / 2 - tw / 2), window.innerWidth - tw - 8);
    var top = r.bottom + 8;
    if (top + th > window.innerHeight - 8 && r.top - th - 8 > 8) top = r.top - th - 8;
    t.style.left = left + window.scrollX + 'px'; t.style.top = top + window.scrollY + 'px';
  }
  function hideTip() { if (tip) tip.hidden = true; if (tipFor) tipFor.removeAttribute('aria-describedby'); tipFor = null; }
  function scheduleHide() { clearTimeout(hideTimer); hideTimer = setTimeout(hideTip, 160); }

  function initTooltips() {
    var termOf = function (e) { return e.target.closest && e.target.closest('.tsp-term:not(.missing)'); };
    document.addEventListener('mouseover', function (e) { var t = termOf(e); if (t) showTip(t); });
    document.addEventListener('mouseout', function (e) { if (termOf(e)) scheduleHide(); });
    document.addEventListener('focusin', function (e) { var t = termOf(e); if (t) showTip(t); });
    document.addEventListener('focusout', function (e) { if (termOf(e)) scheduleHide(); });
    document.addEventListener('click', function (e) {          // tap on touch screens
      var t = termOf(e);
      if (t) { if (tipFor === t && !tip.hidden && e.detail !== 0 && 'ontouchstart' in window) hideTip(); else showTip(t); }
      else if (tip && !tip.hidden && !e.target.closest('.term-tip')) hideTip();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') hideTip();
      if ((e.key === 'Enter' || e.key === ' ') && termOf(e)) { e.preventDefault(); showTip(termOf(e)); }
    });
    window.addEventListener('scroll', hideTip, { passive: true });
    document.addEventListener('tsp:route', hideTip);
  }

  /** Make an HTML string from a markdown-ish glossary text (plain) - not needed; text only. */
  T.Md = { hydrate: hydrate, initTooltips: initTooltips };
})(window.TSP = window.TSP || {});
