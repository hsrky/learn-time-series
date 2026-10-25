/* pages/mock.js - timed Mock OA: pick a set (or a random Easy+Medium+Hard), hidden verdicts until the end. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  var WEIGHT = { Easy: 1, Medium: 2, Hard: 3 }, XP = { Easy: 20, Medium: 40, Hard: 70 };

  function randomSet() {
    var picks = [];
    ['Easy', 'Medium', 'Hard'].forEach(function (d) {
      var pool = C.problemList.filter(function (p) { return p.difficulty === d && p.type !== 'sql' || p.difficulty === d; });
      var todo = pool.filter(function (p) { return !S.problemSolved(p.slug); });
      var src = todo.length ? todo : pool;
      if (src.length) picks.push(src[Math.floor(Math.random() * src.length)].slug);
    });
    return { id: 'random', title: 'Random mock OA', minutes: 75, problems: picks };
  }
  function startSession(set) {
    var slugs = set.problems.filter(function (s) { return C.problems[s]; });
    if (!slugs.length) { U.toast('This set has no problems yet.'); return; }
    S.update(function (s) {
      s.mockSession = { id: set.id, title: set.title, minutes: set.minutes || 75, startedAt: Date.now(), slugs: slugs, results: {}, finished: false };
    });
    T.R.go('/mock/run');
  }
  function scoreOf(sess) {
    var num = 0, den = 0;
    sess.slugs.forEach(function (slug) {
      var w = WEIGHT[C.problems[slug].difficulty], r = sess.results[slug];
      den += w; num += w * (r && r.total ? r.passed / r.total : 0);
    });
    return den ? Math.round(num / den * 100) : 0;
  }

  T.pages.mock = {
    render: function (el) {
      T.setTitle('Mock OA');
      var wrap = h('div.wrap'), sess = S.get().mockSession;
      el.appendChild(wrap);
      wrap.appendChild(h('div.page-head', h('div', h('h1', 'Mock OA'), h('p.muted', 'Practise a timed online test. You see the verdicts only when you finish, like in a real test.'))));
      if (sess && !sess.finished) {
        wrap.appendChild(h('div.review-start', h('div', h('h3', 'A test is in progress'), h('p.muted', sess.title)), h('a.btn.primary', { href: '#/mock/run' }, 'Resume')));
      }
      var grid = h('div.mock-grid');
      var sets = C.mockSets.concat([randomSet()]);
      sets.forEach(function (set) {
        var isRandom = set.id === 'random';
        var probs = (set.problems || []).map(function (s) { return C.problems[s]; }).filter(Boolean);
        grid.appendChild(h('div.mock-card',
          h('h3', isRandom ? 'Random mock' : set.title),
          h('p.muted', set.minutes + ' minutes · ' + (isRandom ? 'one Easy, one Medium, one Hard from any stage' : probs.length + ' problems')),
          isRandom ? null : h('ul.mock-list', probs.map(function (p) { return h('li', p.title, ' ', h('span.diff.' + p.difficulty.toLowerCase(), p.difficulty)); })),
          h('button.btn.primary', { type: 'button', onclick: function () { startSession(isRandom ? randomSet() : set); } }, 'Start')));
      });
      if (!C.problemList.length) grid.appendChild(h('div.empty', 'No problems yet.'));
      wrap.appendChild(grid);
      var past = S.get().mocks;
      if (past.length) {
        wrap.appendChild(h('h2', 'Your past tests'));
        wrap.appendChild(h('div.table-wrap', h('table.subs', h('thead', h('tr', h('th', 'Test'), h('th', 'Score'), h('th', 'Time used'), h('th', 'When'))),
          h('tbody', past.slice().reverse().slice(0, 10).map(function (m) {
            return h('tr', h('td', m.title), h('td', h('b', m.score + '%')), h('td', U.fmtDuration(m.used)), h('td.muted', U.timeAgo(m.at)));
          })))));
      }
    }
  };

  T.pages.mockRun = {
    render: function (el) {
      var sess = S.get().mockSession;
      if (!sess) { T.R.go('/mock'); return; }
      T.setTitle('Mock OA');
      el.classList.add('page-workspace');
      var tabs = h('div.mock-tabs'), timer = h('span.timer', { role: 'timer' }), host = h('div.ws-host');
      var cur = 0, ws = null, tick = null;
      var finishBtn = h('button.btn.primary.sm', { type: 'button', onclick: function () {
        if (window.confirm('Finish the test now? You cannot change your answers after this.')) finish();
      } }, 'Finish test');
      var bar = h('div.ws-bar', h('b', sess.title), timer, h('span.grow'), tabs, finishBtn);
      el.append(bar, host);

      function remaining() { return sess.startedAt + sess.minutes * 60000 - Date.now(); }
      function drawTabs() {
        U.clear(tabs);
        sess.slugs.forEach(function (slug, i) {
          var r = sess.results[slug];
          tabs.appendChild(h('button.btn.sm' + (i === cur ? '.primary' : ''), { type: 'button', onclick: function () { open(i); } },
            'Q' + (i + 1) + ' ', h('span.diff.' + C.problems[slug].difficulty.toLowerCase(), C.problems[slug].difficulty), r ? ' ✓' : ''));
        });
      }
      function open(i) {
        cur = i; if (ws) ws.destroy(); U.clear(host); drawTabs();
        ws = T.Workspace.mount(host, sess.slugs[i], { mock: { onSubmit: function (res) {
          var slug = sess.slugs[i], prev = sess.results[slug];
          if (!prev || res.passed / Math.max(1, res.total) >= prev.passed / Math.max(1, prev.total)) {
            S.update(function (s) { s.mockSession.results[slug] = { status: res.status, passed: res.passed, total: res.total, ms: (res.results || []).reduce(function (a, r) { return a + (r.ms || 0); }, 0) }; }, 'quiet');
            sess = S.get().mockSession;
          }
          drawTabs();
        } } });
      }
      function updateTimer() {
        var r = remaining();
        timer.textContent = r > 0 ? U.fmtDuration(r / 1000) + ' left' : 'Time is up';
        timer.classList.toggle('low', r < 5 * 60000);
        if (r <= 0) finish();
      }
      function finish() {
        if (tick) clearInterval(tick);
        if (ws) ws.destroy();
        var used = Math.min(sess.minutes * 60, (Date.now() - sess.startedAt) / 1000), score = scoreOf(sess);
        S.update(function (s) {
          s.mockSession.finished = true;
          s.mocks.push({ id: sess.id, title: sess.title, at: Date.now(), score: score, used: used });
          sess.slugs.forEach(function (slug) {
            var r = sess.results[slug], ps = S.problem(slug);
            if (r && r.status === 'Accepted' && !ps.solved) { ps.solved = Date.now(); s.xp += XP[C.problems[slug].difficulty]; }
          });
          s.xp += 50; S.touch(3);
        });
        U.toast('+50 XP · mock test finished', 'xp');
        report(score, used);
      }
      function report(score, used) {
        el.classList.remove('page-workspace');
        U.clear(el);
        var wrap = h('div.wrap.narrow'), s2 = S.get().mockSession || sess;
        wrap.appendChild(h('h1', 'Test report'));
        wrap.appendChild(h('div.quiz-result.' + (score >= 70 ? 'ok' : 'bad'), h('div.score-ring', { style: { '--p': score } }, h('b', score + '%')),
          h('div', h('h3', s2.title), h('p', 'Time used: ' + U.fmtDuration(used) + ' of ' + sess.minutes + ' minutes.'),
            h('p.muted', 'Score counts Easy 1, Medium 2 and Hard 3 points, by the share of cases you passed.'))));
        var tb = h('tbody');
        sess.slugs.forEach(function (slug) {
          var p = C.problems[slug], r = s2.results[slug];
          tb.appendChild(h('tr', h('td', p.title), h('td', h('span.diff.' + p.difficulty.toLowerCase(), p.difficulty)),
            h('td', r ? h('span.verdict-text.' + (r.status === 'Accepted' ? 'ok' : 'bad'), r.status) : h('span.muted', 'Not submitted')), h('td', r ? r.passed + '/' + r.total : '-'),
            h('td', h('a.btn.sm', { href: '#/problem/' + slug }, 'Open solution page'))));
        });
        wrap.appendChild(h('div.table-wrap', h('table.subs', h('thead', h('tr', h('th', 'Problem'), h('th', 'Level'), h('th', 'Verdict'), h('th', 'Cases'), h('th', ''))), tb)));
        wrap.appendChild(h('div.row', h('a.btn.primary', { href: '#/mock' }, 'Another test'), h('a.btn', { href: '#/' }, 'Back to the path')));
        el.appendChild(wrap);
      }
      if (sess.finished) { report(S.get().mocks.length ? S.get().mocks[S.get().mocks.length - 1].score : scoreOf(sess), S.get().mocks.length ? S.get().mocks[S.get().mocks.length - 1].used : 0); return; }
      open(0); updateTimer(); tick = setInterval(updateTimer, 1000);
      return function () { if (tick) clearInterval(tick); if (ws) ws.destroy(); el.classList.remove('page-workspace'); };
    }
  };
})(window.TSP = window.TSP || {});
