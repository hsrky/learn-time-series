/* pages/lesson.js - one lesson, shown as steps: each section, then practice, quiz and finish. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  var CALLOUT = {
    interview: ['Interview lens', 'briefcase'], realworld: ['Real world', 'book'], keypoints: ['Key points', 'check'],
    mistakes: ['Common mistakes', 'alert'], staff: ['Staff lens', 'crown'], warmup: ['Warm-up', 'refresh'], worked: ['Worked example', 'code'], why: ['Why it matters', 'spark']
  };

  function difficultyBadge(d) { return h('span.diff.' + d.toLowerCase(), d); }

  function problemRow(slug) {
    var p = C.problems[slug], st = S.problemStatus(slug);
    return h('a.prob-card', { href: '#/problem/' + slug },
      h('span.pstatus.' + st, { title: st === 'solved' ? 'Solved' : st === 'attempted' ? 'Attempted' : 'Not started' }, st === 'solved' ? U.icon('check', 16) : ''),
      h('span.pc-title', p.title), difficultyBadge(p.difficulty),
      h('span.btn.sm' + (st === 'solved' ? '' : '.primary'), st === 'solved' ? 'Solve again' : 'Solve'));
  }

  T.pages.lesson = {
    render: function (el, params, query) {
      var lesson = C.lessons[params.id];
      if (!lesson) { el.appendChild(h('div.wrap', h('h1', 'Lesson not found'), h('a.btn', { href: '#/' }, 'Back to the path'))); return; }
      T.setTitle(lesson.title);
      var stage = C.stageById[lesson.stage];
      var L = S.lesson(lesson.id);
      var secs = lesson.sections;
      var steps = secs.map(function (s) { return { type: 'section', title: s.title, kind: s.kind, sec: s }; });
      var lastSection = steps.length - 1;
      if (lesson.problems.length || lesson.drill) steps.push({ type: 'practice', title: 'Practice', kind: 'practice' });
      if (lesson.quiz.questions.length) steps.push({ type: 'quiz', title: 'Mastery quiz', kind: 'quiz' });
      steps.push({ type: 'done', title: 'Finish', kind: 'done' });

      var cur = query.s != null ? +query.s : (L.step || 0);
      if (!(cur >= 0 && cur < steps.length)) cur = 0;
      var visited = (L.seen || []).slice();

      S.update(function (s) { s.lastLesson = lesson.id; var l = S.lesson(lesson.id); l.visited = l.visited || Date.now(); });

      var wrap = h('div.wrap.lesson-wrap', { style: { '--stage': stage.color } });
      var head = h('header.lesson-head',
        h('nav.crumbs', { 'aria-label': 'Breadcrumb' }, h('a', { href: '#/' }, 'Path'), ' / ', h('a', { href: '#/', onclick: function (e) {
          e.preventDefault(); T.R.go('/'); setTimeout(function () { var t = document.getElementById('stage-' + stage.id); if (t) t.scrollIntoView(); }, 50);
        } }, stage.title)),
        h('h1', lesson.title),
        h('div.meta', h('span.chip', lesson.minutes + ' min'), h('span.chip', lesson.level),
          lesson.skills.map(function (s) { return h('span.skill', 'skill:' + s); }),
          lesson.tags.map(function (t) { return h('span.tag', t); })));
      var stepbar = h('nav.stepbar', { 'aria-label': 'Lesson steps' });
      var stepTitle = h('div.step-title');
      var content = h('div.lesson-content');
      var foot = h('div.step-foot');
      wrap.append(head, h('div.sticky-bar', stepTitle, stepbar), content, foot);
      el.appendChild(wrap);

      function drawBar() {
        U.clear(stepbar);
        steps.forEach(function (st, i) {
          stepbar.appendChild(h('button.seg' + (i === cur ? '.cur' : '') + (visited.indexOf(i) >= 0 ? '.seen' : ''), {
            type: 'button', title: st.title, 'aria-label': 'Step ' + (i + 1) + ': ' + st.title, 'aria-current': i === cur ? 'step' : null,
            onclick: function () { go(i); } }));
        });
        U.clear(stepTitle);
        stepTitle.append(h('span.muted', 'Step ' + (cur + 1) + ' of ' + steps.length), ' · ', h('b', steps[cur].title));
      }

      function completeLesson() {
        if (L.learned) return;
        var n = S.addCards(lesson.id);
        S.update(function (s) { var l = S.lesson(lesson.id); l.learned = Date.now(); s.xp += 20; S.touch(2); }, 'lesson');
        U.toast('+20 XP · lesson learned' + (n ? ' · ' + n + ' flashcards added to Review' : ''), 'xp');
      }

      function go(i) {
        cur = i;
        if (visited.indexOf(i) < 0) visited.push(i);
        if (i > lastSection) completeLesson();
        S.quiet(function () { var l = S.lesson(lesson.id); l.step = i; l.seen = visited; });
        T.R.replaceQuery({ s: i, keep: 1 });
        draw();
        var top = wrap.querySelector('.sticky-bar');
        window.scrollTo({ top: Math.max(0, wrap.offsetTop + head.offsetHeight - 12), behavior: 'auto' });
      }

      function draw() {
        drawBar();
        U.clear(content); U.clear(foot);
        var st = steps[cur];
        var body = h('article.step.k-' + st.kind);
        if (cur === 0) body.appendChild(intro());
        if (st.type === 'section') {
          var c = CALLOUT[st.kind];
          var sec = h('section.prose' + (c ? '.callout.c-' + st.kind : ''), h('h2', c ? [U.icon(c[1], 20), ' ', st.title] : st.title));
          var htmlBox = h('div.md', { html: st.sec.html });
          sec.appendChild(htmlBox);
          body.appendChild(sec);
          content.appendChild(body);
          T.Md.hydrate(htmlBox, { lessonId: lesson.id });
        } else if (st.type === 'practice') {
          body.appendChild(h('h2', 'Practice'));
          body.appendChild(h('p.muted', 'Now use the idea. Start with the first problem. A hint is always one click away.'));
          if (lesson.problems.length) body.appendChild(h('div.prob-cards', lesson.problems.map(problemRow)));
          if (lesson.drill) body.appendChild(h('a.drill-card', { href: '#/drill/' + lesson.id }, U.icon('server', 22),
            h('div', h('b', 'Design drill: ' + lesson.drill.title), h('span.muted', lesson.drill.minutes + ' minutes · write your answer, then compare with a model answer')), h('span.btn.sm', 'Open')));
          content.appendChild(body);
        } else if (st.type === 'quiz') {
          body.appendChild(h('h2', 'Mastery quiz'));
          var q = L.quiz;
          body.appendChild(h('p.muted', lesson.quiz.questions.length + ' questions. Score ' + Math.round((lesson.quiz.pass || 0.8) * 100) + '% or more to pass.' +
            (q ? ' Your best score: ' + Math.round(q.best * 100) + '%.' : '')));
          var host = h('div.quiz-host');
          body.appendChild(host); content.appendChild(body);
          T.Quiz.runQuiz(host, lesson, function () { L = S.lesson(lesson.id); });
        } else {
          body.appendChild(finish()); content.appendChild(body);
        }
        // footer navigation
        var next = steps[cur + 1];
        foot.append(
          cur > 0 ? h('button.btn', { type: 'button', onclick: function () { go(cur - 1); } }, 'Back') : h('span'),
          next ? h('button.btn.primary', { type: 'button', onclick: function () { go(cur + 1); } },
            (cur === lastSection ? 'Finish lesson' : 'Next') + ': ' + next.title, U.icon('chevron', 16)) : null);
      }

      function intro() {
        var box = h('section.intro-card');
        box.appendChild(h('h2', 'In this lesson you will'));
        box.appendChild(h('ul.goals', lesson.goals.map(function (g) { return h('li', g); })));
        if (lesson.prereqs.length) {
          box.appendChild(h('p.prereqs', h('b', 'Best after: '), lesson.prereqs.map(function (id, i) {
            var l = C.lessons[id], done = S.lessonStatus(id) !== 'none';
            return [i ? ', ' : '', h('a', { href: '#/lesson/' + id }, l.title), done ? ' ✓' : ''];
          })));
        }
        return box;
      }

      function finish() {
        var st = S.lessonStatus(lesson.id), l = S.lesson(lesson.id);
        var solved = lesson.problems.filter(S.problemSolved).length;
        var box = h('section.finish');
        box.appendChild(h('h2', 'Lesson complete'));
        box.appendChild(h('div.finish-grid',
          h('div.fin-item.ok', U.icon('check', 18), h('div', h('b', 'Lesson learned'), h('span', 'Flashcards added: ' + lesson.cards.length))),
          lesson.quiz.questions.length ? h('a.fin-item' + (l.quiz && l.quiz.best >= (lesson.quiz.pass || 0.8) ? '.ok' : ''), { href: '#', onclick: function (e) { e.preventDefault(); go(steps.findIndex(function (s) { return s.type === 'quiz'; })); } },
            U.icon('target', 18), h('div', h('b', 'Mastery quiz'), h('span', l.quiz ? 'Best: ' + Math.round(l.quiz.best * 100) + '%' : 'Not taken yet'))) : null,
          lesson.problems.length ? h('a.fin-item' + (solved ? '.ok' : ''), { href: '#', onclick: function (e) { e.preventDefault(); go(steps.findIndex(function (s) { return s.type === 'practice'; })); } },
            U.icon('code', 18), h('div', h('b', 'Problems'), h('span', solved + ' of ' + lesson.problems.length + ' solved'))) : null));
        box.appendChild(h('p', 'Status: ', h('b.st-' + st, { class: 'status-text' }, st === 'none' ? 'Not started' : st[0].toUpperCase() + st.slice(1)),
          st === 'mastered' ? '' : ' · To master this lesson, pass the quiz (80%) and solve a problem.'));
        var nxt = C.nextOf[lesson.id], prv = C.prevOf[lesson.id];
        box.appendChild(h('div.row.wrap-row',
          nxt ? h('a.btn.primary', { href: '#/lesson/' + nxt }, 'Next lesson: ' + C.lessons[nxt].title, U.icon('chevron', 16)) : null,
          prv ? h('a.btn', { href: '#/lesson/' + prv }, 'Previous lesson') : null,
          h('a.btn', { href: '#/' }, 'Back to the path')));
        return box;
      }

      go(cur);
      // go() writes the first visit; do not scroll the very first paint
      window.scrollTo(0, 0);
    }
  };
})(window.TSP = window.TSP || {});
