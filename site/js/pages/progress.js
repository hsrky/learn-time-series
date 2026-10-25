/* pages/progress.js - stats, per-stage mastery bars, activity heatmap, streak and XP. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  function heatmap() {
    var act = S.get().activity, weeks = 26, cell = 12, gap = 3;
    var today = new Date(), dow = (today.getDay() + 6) % 7;                       // Monday = 0
    var start = new Date(today.getFullYear(), today.getMonth(), today.getDate() - dow - (weeks - 1) * 7);
    var W = weeks * (cell + gap) + 24, H = 7 * (cell + gap) + 20, svg = '', months = '';
    var lastMonth = -1;
    for (var w = 0; w < weeks; w++) {
      for (var d = 0; d < 7; d++) {
        var dt = new Date(start.getFullYear(), start.getMonth(), start.getDate() + w * 7 + d);
        if (dt > today) continue;
        var key = U.ymd(dt), n = act[key] || 0, lvl = n === 0 ? 0 : n < 3 ? 1 : n < 7 ? 2 : n < 15 ? 3 : 4;
        svg += '<rect x="' + (24 + w * (cell + gap)) + '" y="' + (16 + d * (cell + gap)) + '" width="' + cell + '" height="' + cell + '" rx="3" class="hm l' + lvl + '"><title>' + key + ': ' + n + ' action' + (n === 1 ? '' : 's') + '</title></rect>';
        if (d === 0 && dt.getMonth() !== lastMonth) { lastMonth = dt.getMonth(); months += '<text x="' + (24 + w * (cell + gap)) + '" y="10" class="hm-t">' + dt.toLocaleString('en', { month: 'short' }) + '</text>'; }
      }
    }
    ['Mon', 'Wed', 'Fri'].forEach(function (n, i) { months += '<text x="0" y="' + (16 + i * 2 * (cell + gap) + 10) + '" class="hm-t">' + n + '</text>'; });
    return h('div.heatmap', { role: 'img', 'aria-label': 'Activity in the last 26 weeks', html: '<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '">' + months + svg + '</svg>' });
  }

  T.pages.progress = {
    render: function (el) {
      T.setTitle('Progress');
      var wrap = h('div.wrap'); el.appendChild(wrap);
      var st = S.streak(), lv = S.level(), s = S.get();
      var solved = C.problemList.filter(function (p) { return S.problemSolved(p.slug); });
      var byDiff = { Easy: [0, 0], Medium: [0, 0], Hard: [0, 0] };
      C.problemList.forEach(function (p) { byDiff[p.difficulty][1]++; if (S.problemSolved(p.slug)) byDiff[p.difficulty][0]++; });
      var mastered = C.lessonList.filter(function (l) { return S.lessonStatus(l.id) === 'mastered'; }).length;
      var learned = C.lessonList.filter(function (l) { return S.lessonStatus(l.id) !== 'none'; }).length;

      wrap.appendChild(h('div.page-head', h('div', h('h1', 'Progress'), h('p.muted', 'Everything is saved in this browser. Use Settings to make a backup file.'))));
      wrap.appendChild(h('div.stat-row.big',
        h('div.stat', U.icon('flame', 22), h('div', h('b', st.current + ' day' + (st.current === 1 ? '' : 's')), h('span', 'Current streak · best ' + st.best))),
        h('div.stat', U.icon('star', 22), h('div', h('b', 'Level ' + lv.level), h('span', lv.xp + ' XP'), h('div.bar', h('i', { style: { width: Math.round(lv.pct * 100) + '%' } })))),
        h('div.stat', U.icon('book', 22), h('div', h('b', learned + ' / ' + C.lessonList.length), h('span', 'Lessons started · ' + mastered + ' mastered'))),
        h('div.stat', U.icon('code', 22), h('div', h('b', solved.length + ' / ' + C.problemList.length), h('span', 'Easy ' + byDiff.Easy[0] + '/' + byDiff.Easy[1] + ' · Medium ' + byDiff.Medium[0] + '/' + byDiff.Medium[1] + ' · Hard ' + byDiff.Hard[0] + '/' + byDiff.Hard[1])))));

      wrap.appendChild(h('h2', 'Mastery by stage'));
      var bars = h('div.stage-bars');
      C.stages.forEach(function (stg) {
        var c = S.stageCounts(stg.id);
        var pM = c.total ? c.mastered / c.total * 100 : 0, pP = c.total ? (c.practiced - c.mastered) / c.total * 100 : 0, pL = c.total ? (c.learned - c.practiced) / c.total * 100 : 0;
        bars.appendChild(h('div.sb', h('span.sb-name', h('i.dot', { style: { background: stg.color } }), stg.id.toUpperCase() + ' ' + stg.title),
          h('div.stack', { role: 'img', 'aria-label': c.mastered + ' mastered, ' + (c.practiced - c.mastered) + ' practiced, ' + (c.learned - c.practiced) + ' learned of ' + c.total },
            h('i.m', { style: { width: pM + '%' } }), h('i.p', { style: { width: pP + '%' } }), h('i.l', { style: { width: pL + '%' } })),
          h('span.muted.small', c.total ? c.mastered + '/' + c.total : '-')));
      });
      bars.appendChild(h('div.legend-row', h('span', h('i.sw.m'), ' Mastered'), h('span', h('i.sw.p'), ' Practiced'), h('span', h('i.sw.l'), ' Learned')));
      wrap.appendChild(bars);

      wrap.appendChild(h('h2', 'Activity'));
      wrap.appendChild(h('div.heat-wrap', heatmap()));
      var days = Object.keys(s.activity).length;
      wrap.appendChild(h('p.muted.small', days + ' active day' + (days === 1 ? '' : 's') + ' so far. Every answer, run or review counts.'));

      var lessonsWithQuiz = C.lessonList.filter(function (l) { return s.lessons[l.id] && s.lessons[l.id].quiz; });
      if (lessonsWithQuiz.length) {
        wrap.appendChild(h('h2', 'Quiz scores'));
        wrap.appendChild(h('div.table-wrap', h('table.subs', h('thead', h('tr', h('th', 'Lesson'), h('th', 'Best'), h('th', 'Attempts'))),
          h('tbody', lessonsWithQuiz.map(function (l) { var q = s.lessons[l.id].quiz; return h('tr', h('td', h('a', { href: '#/lesson/' + l.id }, l.title)), h('td', Math.round(q.best * 100) + '%'), h('td', String(q.attempts))); })))));
      }
    }
  };
})(window.TSP = window.TSP || {});
