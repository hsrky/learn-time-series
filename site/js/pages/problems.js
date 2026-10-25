/* pages/problems.js - the problem list (like LeetCode's Problemset). */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  var filters = { q: '', stage: '', diff: '', status: '', skill: '', type: '' };   // kept while the app is open
  var DIFF_ORDER = { Easy: 0, Medium: 1, Hard: 2 };

  function uniq(arr) { return arr.filter(function (v, i) { return arr.indexOf(v) === i; }).sort(); }

  T.pages.problems = {
    render: function (el, params, query) {
      T.setTitle('Problems');
      if (query.stage) filters.stage = query.stage;
      if (query.skill) filters.skill = query.skill;
      var all = C.problemList;
      var wrap = h('div.wrap');
      var solvedN = all.filter(function (p) { return S.problemSolved(p.slug); }).length;
      wrap.appendChild(h('div.page-head',
        h('div', h('h1', 'Problems'), h('p.muted', solvedN + ' of ' + all.length + ' solved. Each problem runs real Python in your browser.')),
        h('button.btn.primary', { type: 'button', id: 'pick', onclick: pick }, U.icon('refresh', 16), ' Pick one for me')));

      var skills = uniq([].concat.apply([], all.map(function (p) { return p.skills; })));
      var types = uniq(all.map(function (p) { return p.type; }));
      function sel(key, label, opts) {
        var s = h('select.input', { 'aria-label': label, onchange: function () { filters[key] = s.value; draw(); } },
          h('option', { value: '' }, label), opts.map(function (o) { return h('option', { value: o[0], selected: filters[key] === o[0] }, o[1]); }));
        return s;
      }
      var search = h('input.input.search', { type: 'search', placeholder: 'Search title or tag', 'aria-label': 'Search problems', value: filters.q,
        oninput: function () { filters.q = search.value; draw(); } });
      wrap.appendChild(h('div.filters', search,
        sel('stage', 'All stages', C.stages.filter(function (s) { return all.some(function (p) { return p.stage === s.id; }); }).map(function (s) { return [s.id, s.id.toUpperCase() + ' ' + s.title]; })),
        sel('diff', 'Any difficulty', [['Easy', 'Easy'], ['Medium', 'Medium'], ['Hard', 'Hard']]),
        sel('status', 'Any status', [['todo', 'Not started'], ['attempted', 'Attempted'], ['solved', 'Solved']]),
        sel('skill', 'Any skill', skills.map(function (s) { return [s, 'skill:' + s]; })),
        sel('type', 'Any type', types.map(function (s) { return [s, s]; })),
        h('button.btn.sm', { type: 'button', onclick: function () { Object.keys(filters).forEach(function (k) { filters[k] = ''; }); T.R.render(); } }, 'Clear')));

      var tableHost = h('div.table-wrap.ptable'), count = h('p.muted.small', { 'aria-live': 'polite' });
      wrap.append(count, tableHost);
      el.appendChild(wrap);

      function visible() {
        var q = filters.q.trim().toLowerCase();
        return all.filter(function (p) {
          if (filters.stage && p.stage !== filters.stage) return false;
          if (filters.diff && p.difficulty !== filters.diff) return false;
          if (filters.status && S.problemStatus(p.slug) !== filters.status) return false;
          if (filters.skill && p.skills.indexOf(filters.skill) < 0) return false;
          if (filters.type && p.type !== filters.type) return false;
          if (q && (p.title + ' ' + p.tags.join(' ') + ' ' + p.skills.join(' ')).toLowerCase().indexOf(q) < 0) return false;
          return true;
        });
      }
      function pick() {
        var v = visible(), todo = v.filter(function (p) { return !S.problemSolved(p.slug); });
        var pool = todo.length ? todo : v;
        if (!pool.length) { U.toast('No problems match your filters.'); return; }
        T.R.go('/problem/' + pool[Math.floor(Math.random() * pool.length)].slug);
      }
      function draw() {
        var v = visible();
        count.textContent = 'Showing ' + v.length + ' of ' + all.length + ' problems';
        U.clear(tableHost);
        if (!v.length) {
          tableHost.appendChild(h('div.empty', all.length ? 'No problems match these filters.' : 'No problems yet. They appear here when the content is built.'));
          return;
        }
        var body = h('tbody');
        v.forEach(function (p, i) {
          var st = S.problemStatus(p.slug), stage = C.stageById[p.stage];
          body.appendChild(h('tr',
            h('td.c-status', { 'data-label': 'Status' }, h('span.pstatus.' + st, { title: st }, st === 'solved' ? U.icon('check', 16) : st === 'attempted' ? '…' : ''),
              h('span.sr-only', st === 'solved' ? 'Solved' : st === 'attempted' ? 'Attempted' : 'Not started')),
            h('td.c-title', { 'data-label': 'Title' }, h('a', { href: '#/problem/' + p.slug }, p.title)),
            h('td.c-stage', { 'data-label': 'Stage' }, h('a.chip.stagechip', { href: '#/problems?stage=' + p.stage, style: { '--stage': stage.color } }, p.stage.toUpperCase())),
            h('td.c-diff', { 'data-label': 'Difficulty' }, h('span.diff.' + p.difficulty.toLowerCase(), p.difficulty)),
            h('td.c-tags', { 'data-label': 'Tags' }, p.skills.map(function (s) { return h('span.skill', 'skill:' + s); }), p.tags.slice(0, 3).map(function (t) { return h('span.tag', t); }),
              p.packages.length ? h('span.tag.pkg', p.packages.join(', ')) : null)));
        });
        tableHost.appendChild(h('table.ptab', h('thead', h('tr', h('th', 'Status'), h('th', 'Title'), h('th', 'Stage'), h('th', 'Difficulty'), h('th', 'Tags and skills'))), body));
      }
      draw();
    }
  };
})(window.TSP = window.TSP || {});
