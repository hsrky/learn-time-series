/* app.js - boot: header/nav, theme, routes. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, R = T.R;

  /* ------------------------------------------------------------ theme + font size */
  function effectiveTheme() {
    var t = S.get().settings.theme;
    if (t === 'light' || t === 'dark') return t;
    return window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function applySettings() {
    var s = S.get().settings, root = document.documentElement;
    if (s.theme === 'light' || s.theme === 'dark') root.setAttribute('data-theme', s.theme); else root.removeAttribute('data-theme');
    root.style.fontSize = (s.fontSize || 16) + 'px';
  }
  T.applySettings = applySettings;

  /* ------------------------------------------------------------ header */
  var NAV = [
    ['path', '#/', 'Path', 'home'], ['problems', '#/problems', 'Problems', 'code'], ['review', '#/review', 'Review', 'cards'],
    ['mock', '#/mock', 'Mock OA', 'clock'], ['drills', '#/drills', 'Design drills', 'server'], ['playground', '#/playground', 'Playground', 'flask']
  ];
  var MORE = [['glossary', '#/glossary', 'Glossary', 'book'], ['progress', '#/progress', 'Progress', 'trend'], ['settings', '#/settings', 'Settings', 'tools']];
  var routeGroup = { lesson: 'path', problem: 'problems', 'mock-run': 'mock', drill: 'drills' };

  function buildHeader() {
    var bar = document.getElementById('topbar');
    U.clear(bar);
    var cur = (R.current() && R.current().name) || 'path';
    cur = routeGroup[cur] || cur;
    var due = S.dueCards().length, st = S.streak(), lv = S.level();
    function link(n, withIcon) {
      return h('a.nav-link' + (n[0] === cur ? '.active' : ''), { href: n[1], 'aria-current': n[0] === cur ? 'page' : null },
        withIcon ? U.icon(n[3], 18) : null, h('span', n[2]), n[0] === 'review' && due ? h('span.badge-count', String(due)) : null);
    }
    var moreOpen = false;
    var morePanel = h('div.menu-panel', { hidden: true }, MORE.map(function (n) { return link(n, true); }));
    var moreBtn = h('button.nav-link.more', { type: 'button', 'aria-haspopup': 'true', 'aria-expanded': 'false', onclick: function (e) {
      e.stopPropagation(); moreOpen = !moreOpen; morePanel.hidden = !moreOpen; moreBtn.setAttribute('aria-expanded', moreOpen);
    } }, h('span', 'More'), U.icon('chevron', 14));
    if (MORE.some(function (n) { return n[0] === cur; })) moreBtn.classList.add('active');
    var burger = h('button.icon-btn.burger', { type: 'button', 'aria-label': 'Open menu', 'aria-expanded': 'false', onclick: function () {
      var open = bar.classList.toggle('open'); burger.setAttribute('aria-expanded', open);
    } }, U.icon('menu', 22));
    var themeBtn = h('button.icon-btn', { type: 'button', 'aria-label': 'Switch light and dark theme', title: 'Switch theme', onclick: function () {
      S.update(function (s) { s.settings.theme = effectiveTheme() === 'dark' ? 'light' : 'dark'; }, 'settings'); applySettings(); buildHeader();
    } }, U.icon(effectiveTheme() === 'dark' ? 'sun' : 'moon', 20));

    bar.appendChild(h('div.topbar-in',
      h('a.brand', { href: '#/', 'aria-label': 'TimeSeries Path, home' },
        h('span.logo', { html: '<svg viewBox="0 0 32 32" width="30" height="30" aria-hidden="true"><rect width="32" height="32" rx="9" fill="var(--brand)"/><path d="M6 21l6-8 5 5 6-10 4 6" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>' }),
        h('span.brand-name', 'TimeSeries', h('b', ' Path'))),
      h('nav.nav', { 'aria-label': 'Main' }, NAV.map(function (n) { return link(n, true); }), h('div.menu', moreBtn, morePanel), h('div.nav-more-mobile', MORE.map(function (n) { return link(n, true); }))),
      h('div.top-right',
        h('a.stat-chip', { href: '#/progress', title: 'Streak and level' }, U.icon('flame', 16), h('b', String(st.current)), h('span.sep', '·'), h('span', 'Lv ' + lv.level)),
        themeBtn, burger)));
    document.addEventListener('click', function close() {
      if (moreOpen) { moreOpen = false; morePanel.hidden = true; moreBtn.setAttribute('aria-expanded', 'false'); }
    });
  }

  /* ------------------------------------------------------------ boot */
  document.addEventListener('DOMContentLoaded', function () {
    applySettings();
    T.Md.initTooltips();
    R.add('/', 'path', T.pages.path);
    R.add('/lesson/:id', 'lesson', T.pages.lesson);
    R.add('/problems', 'problems', T.pages.problems);
    R.add('/problem/:slug', 'problem', T.pages.problem);
    R.add('/playground', 'playground', T.pages.playground);
    R.add('/review', 'review', T.pages.review);
    R.add('/mock', 'mock', T.pages.mock);
    R.add('/mock/run', 'mock-run', T.pages.mockRun);
    R.add('/drills', 'drills', T.pages.drills);
    R.add('/drill/:id', 'drill', T.pages.drill);
    R.add('/glossary', 'glossary', T.pages.glossary);
    R.add('/progress', 'progress', T.pages.progress);
    R.add('/settings', 'settings', T.pages.settings);
    document.addEventListener('tsp:route', function () {
      document.title = 'TimeSeries Path';
      document.body.classList.remove('nav-open');
      buildHeader();
      var m = document.getElementById('main'); m.focus({ preventScroll: true });
    });
    S.on(function (what) { if (what === 'cards' || what === 'import' || what === 'settings') buildHeader(); });
    window.matchMedia && matchMedia('(prefers-color-scheme: dark)').addEventListener &&
      matchMedia('(prefers-color-scheme: dark)').addEventListener('change', buildHeader);
    R.start(document.getElementById('main'));
  });

  T.pages = T.pages || {};
  T.setTitle = function (t) { document.title = t ? t + ' · TimeSeries Path' : 'TimeSeries Path'; };
})(window.TSP = window.TSP || {});
