/* pages/path.js - the learning path: stages as bands, lessons as nodes on a winding trail. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  var OFFSETS = [0, -70, -95, -70, 0, 70, 95, 70];     // x offsets of the zig-zag, in px
  var TW = 320, ROW = 98, TOP = 44;
  var STATUS_TEXT = { none: '', learned: 'Learned', practiced: 'Practiced', mastered: 'Mastered' };

  function svgPath(points, upto) {
    var d = '';
    for (var i = 0; i <= upto && i < points.length; i++) {
      var p = points[i];
      if (i === 0) d = 'M' + p[0] + ',' + p[1];
      else { var q = points[i - 1], my = (q[1] + p[1]) / 2; d += ' C' + q[0] + ',' + my + ' ' + p[0] + ',' + my + ' ' + p[0] + ',' + p[1]; }
    }
    return d;
  }

  function mountains(color) {
    return h('span.mountains', { 'aria-hidden': 'true', html: '<svg viewBox="0 0 200 70" width="200" height="70"><path d="M0 70L40 24l22 26 30-40 38 46 24-20 46 38z" fill="' + color + '" opacity=".18"/><path d="M60 70l34-44 24 30 22-18 40 32z" fill="' + color + '" opacity=".18"/></svg>' });
  }

  function trail(stage) {
    var lessons = stage.lessons.map(function (id) { return C.lessons[id]; });
    var pts = lessons.map(function (l, i) { return [TW / 2 + OFFSETS[i % OFFSETS.length], TOP + i * ROW]; });
    var height = TOP + (lessons.length - 1) * ROW + 70;
    var statuses = lessons.map(function (l) { return S.lessonStatus(l.id); });
    var lastDone = -1;
    statuses.forEach(function (s, i) { if (s !== 'none') lastDone = i; });

    var box = h('div.trail', { style: { width: TW + 'px', height: height + 'px', '--stage': stage.color } });
    var svg = '<svg width="' + TW + '" height="' + height + '" viewBox="0 0 ' + TW + ' ' + height + '" aria-hidden="true">' +
      '<path d="' + svgPath(pts, pts.length) + '" class="trail-base"/>' +
      (lastDone >= 0 ? '<path d="' + svgPath(pts, lastDone) + '" class="trail-done" style="stroke:' + stage.color + '"/>' : '') + '</svg>';
    box.appendChild(h('div.trail-svg', { html: svg }));

    lessons.forEach(function (l, i) {
      var st = statuses[i], p = pts[i], right = p[0] <= TW / 2;
      var unmet = l.prereqs.filter(function (id) { return C.lessons[id] && S.lessonStatus(id) === 'none'; });
      var node = h('a.node.st-' + st + (unmet.length && st === 'none' ? '.soft' : ''), {
        href: '#/lesson/' + l.id, style: { left: (p[0] - 28) + 'px', top: (p[1] - 28) + 'px' },
        'aria-label': l.title + (STATUS_TEXT[st] ? ', ' + STATUS_TEXT[st] : '') + ', ' + l.minutes + ' minutes'
      }, st === 'mastered' ? U.icon('star', 24) : st === 'none' ? h('b', String(i + 1)) : U.icon('check', 24));
      var label = h('a.node-label', { href: '#/lesson/' + l.id, tabindex: -1, style: right ? { left: (p[0] + 38) + 'px', top: (p[1] - 24) + 'px', width: (TW - p[0] - 38) + 'px' } :
        { right: (TW - p[0] + 38) + 'px', top: (p[1] - 24) + 'px', width: (p[0] - 38) + 'px', textAlign: 'right' } },
        h('span.nl-title', l.title),
        h('span.nl-meta', l.minutes + ' min' + (STATUS_TEXT[st] ? ' · ' : ''), STATUS_TEXT[st] ? h('b.st-' + st, STATUS_TEXT[st]) : null),
        unmet.length && st === 'none' ? h('span.nl-soft', 'Best after: ' + C.lessons[unmet[0]].title) : null);
      box.appendChild(node); box.appendChild(label);
    });
    return box;
  }

  function stageBand(stage) {
    var cnt = S.stageCounts(stage.id);
    var pct = cnt.total ? Math.round(cnt.learned / cnt.total * 100) : 0;
    var head = h('div.stage-head', { style: { '--stage': stage.color } },
      h('span.stage-ico', U.icon(stage.icon, 26)),
      h('div.stage-title', h('span.stage-id', stage.id.toUpperCase()), h('h2', stage.title), h('p', stage.summary)),
      h('div.stage-prog', cnt.total ? [h('b', cnt.learned + ' / ' + cnt.total), h('span', ' learned'), h('div.bar', h('i', { style: { width: pct + '%' } }))] : h('span.muted', 'Coming soon')),
      mountains(stage.color));
    var band = h('section.stage', { id: 'stage-' + stage.id, 'aria-labelledby': 'h-' + stage.id, style: { '--stage': stage.color } }, head);
    head.querySelector('h2').id = 'h-' + stage.id;
    band.appendChild(stage.lessons.length ? trail(stage) : h('div.empty-stage', 'Lessons for this stage are being written.'));
    return band;
  }

  T.pages.path = {
    render: function (el) {
      T.setTitle('');
      var wrap = h('div.wrap');
      var cid = S.continueLesson(), st = S.streak(), lv = S.level(), due = S.dueCards().length;
      var cont = cid ? C.lessons[cid] : null;

      wrap.appendChild(h('section.hero',
        h('div.hero-text', h('h1', 'Learn time series. Pass the interview.'),
          h('p', 'Short lessons, real Python in your browser, and practice problems. Start at the top and move at your own speed.')),
        cont ? h('div.continue-card',
          h('span.eyebrow', S.lessonStatus(cid) === 'none' && !S.get().lessons[cid] ? 'Start here' : 'Continue'),
          h('h3', cont.title),
          h('p.muted', C.stageById[cont.stage].title + ' · ' + cont.minutes + ' min'),
          h('a.btn.primary', { href: '#/lesson/' + cid }, 'Continue', U.icon('chevron', 16))) : null));

      wrap.appendChild(h('div.stat-row',
        h('div.stat', U.icon('flame', 20), h('div', h('b', st.current + (st.current === 1 ? ' day' : ' days')), h('span', 'Streak'))),
        h('div.stat', U.icon('star', 20), h('div', h('b', 'Level ' + lv.level), h('span', lv.xp + ' XP'))),
        h('a.stat', { href: '#/review' }, U.icon('cards', 20), h('div', h('b', due + (due === 1 ? ' card' : ' cards')), h('span', 'Due for review'))),
        h('a.stat', { href: '#/problems' }, U.icon('code', 20), h('div', h('b', Object.keys(S.get().problems).filter(S.problemSolved).length + ' / ' + C.problemList.length), h('span', 'Problems solved')))));

      var chips = h('nav.chips', { 'aria-label': 'Jump to a stage' });
      C.stages.forEach(function (s) {
        chips.appendChild(h('button.chip.jump', { type: 'button', style: { '--stage': s.color }, title: s.title, onclick: function () {
          var t = document.getElementById('stage-' + s.id); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } }, h('i.dot'), s.id.toUpperCase() + ' ' + s.title));
      });
      wrap.appendChild(chips);
      C.stages.forEach(function (s) { wrap.appendChild(stageBand(s)); });
      el.appendChild(wrap);
    }
  };
})(window.TSP = window.TSP || {});
