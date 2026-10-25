/* pages/drills.js - design drills: timed writing, model answer, self-graded rubric. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  function allDrills() { return C.lessonList.filter(function (l) { return l.drill; }); }

  T.pages.drills = {
    render: function (el) {
      T.setTitle('Design drills');
      var wrap = h('div.wrap'); el.appendChild(wrap);
      wrap.appendChild(h('div.page-head', h('div', h('h1', 'Design drills'), h('p.muted', 'Practise open questions like "design a forecasting system". Write your answer on a timer, then compare it with a model answer.'))));
      var list = allDrills();
      if (!list.length) { wrap.appendChild(h('div.empty', 'No drills yet. They appear here when the content is built.')); return; }
      var grid = h('div.mock-grid');
      list.forEach(function (l) {
        var d = l.drill, rec = S.get().drills[l.id], stage = C.stageById[l.stage];
        grid.appendChild(h('a.mock-card.link', { href: '#/drill/' + l.id },
          h('span.chip.stagechip', { style: { '--stage': stage.color } }, stage.id.toUpperCase()),
          h('h3', d.title), h('p.muted', d.minutes + ' minutes' + (d.level ? ' · ' + d.level : '')),
          rec && rec.score != null ? h('p', 'Best self-score: ', h('b', rec.score + '%')) : h('p.muted', 'Not tried yet')));
      });
      wrap.appendChild(grid);
    }
  };

  T.pages.drill = {
    render: function (el, params) {
      var lesson = C.lessons[params.id], d = lesson && lesson.drill;
      if (!d) { el.appendChild(h('div.wrap', h('h1', 'Drill not found'), h('a.btn', { href: '#/drills' }, 'All drills'))); return; }
      T.setTitle(d.title);
      var rec = S.get().drills[lesson.id] || (S.get().drills[lesson.id] = { answers: {}, rubric: {} });
      rec.answers = rec.answers || {}; rec.rubric = rec.rubric || {};
      var wrap = h('div.wrap.narrow'), tick = null, startedAt = null, revealed = false;
      el.appendChild(wrap);
      var save = U.debounce(function () { S.quiet(function () {}); }, 300);

      wrap.appendChild(h('nav.crumbs', h('a', { href: '#/drills' }, 'Design drills'), ' / ', h('a', { href: '#/lesson/' + lesson.id }, lesson.title)));
      wrap.appendChild(h('h1', d.title));
      var prompt = h('div.md.prose.prompt', { html: d.promptHtml }); wrap.appendChild(prompt); T.Md.hydrate(prompt, {});

      var timer = h('span.timer', { role: 'timer' }, d.minutes + ':00');
      var startBtn = h('button.btn.primary', { type: 'button', onclick: startTimer }, U.icon('clock', 16), ' Start the ' + d.minutes + '-minute timer');
      wrap.appendChild(h('div.row.drill-bar', startBtn, timer));
      function startTimer() {
        startedAt = Date.now(); startBtn.hidden = true;
        tick = setInterval(function () {
          var left = d.minutes * 60 - (Date.now() - startedAt) / 1000;
          timer.textContent = left > 0 ? U.fmtDuration(left) : 'Time is up. Finish your thought, then compare.';
          timer.classList.toggle('low', left < 300);
        }, 500);
      }

      function answersText() {
        return d.sections.map(function (sec) { return sec.label + ':\n' + (rec.answers[sec.id] || '(empty)'); }).join('\n\n');
      }
      if (T.AI) T.AI.setContext({
        kind: 'drill', key: 'drill:' + lesson.id, title: d.title, sub: function () { return 'Design drill'; },
        drill: { id: lesson.id, d: d,
          hasAnswers: function () { return d.sections.some(function (sec) { return (rec.answers[sec.id] || '').trim(); }); },
          context: function () { return 'DRILL PROMPT:\n' + T.AI.text(d.promptHtml) + '\n\nLEARNER WRITTEN ANSWERS:\n' + T.AI.clip(answersText(), 6000); } },
        get: function () {
          return 'DESIGN DRILL: ' + d.title + ' (' + d.minutes + ' minutes)\n\nPROMPT:\n' + T.AI.clip(T.AI.text(d.promptHtml), 2500) +
            '\n\nSECTIONS THE LEARNER MUST WRITE: ' + d.sections.map(function (x) { return x.label; }).join('; ') +
            '\n\nLEARNER WRITTEN ANSWERS:\n' + T.AI.clip(answersText(), 6000) +
            '\n\nPossible follow-up topics: ' + (d.followUps || []).join(' | ') +
            '\n(The model answer is hidden from the tutor in normal chat. Do not write a full model answer.)';
        },
        quick: function () { return [
          { label: 'Is my answer on track?', prompt: 'Look at my written answers. Tell me in 3 short bullets what is good and what is missing. Do not write the answer for me.' },
          { label: 'Give me a hint', prompt: 'Give me one hint for the section where I am weakest. Do not write the answer.' }]; }
      });

      var form = h('div.drill-form');
      d.sections.forEach(function (s) {
        var ta = h('textarea.input', { rows: 5, id: 'dr-' + s.id, placeholder: s.hint, oninput: function () { rec.answers[s.id] = ta.value; save(); } });
        ta.value = rec.answers[s.id] || '';
        form.appendChild(h('div.drill-sec', h('label', { for: 'dr-' + s.id }, h('b', s.label), h('span.muted.small', ' ' + s.hint)), ta));
      });
      wrap.appendChild(form);

      var after = h('div.drill-after');
      wrap.appendChild(h('div.row', h('button.btn.primary', { type: 'button', onclick: reveal }, 'Reveal model answer'),
        T.AI ? T.AI.slot(function () {
          return h('button.btn', { type: 'button', onclick: function (e) { T.AI.Drawer.open({ opener: e.currentTarget }); T.AI.drillStart && T.AI.drillStart(); } },
            U.icon('spark', 14), ' Ask the AI interviewer (3 questions + grade)');
        }) : null));
      wrap.appendChild(after);
      if (Object.keys(rec.answers).some(function (k) { return rec.answers[k]; }) && rec.revealed) reveal();

      function reveal() {
        if (revealed) return;
        revealed = true; if (tick) clearInterval(tick);
        rec.revealed = true;
        U.clear(after);
        after.appendChild(h('h2', 'Model answer'));
        d.sections.forEach(function (s) {
          var box = h('div.model-sec', h('h3', s.label)); var md = h('div.md.prose', { html: d.modelHtml[s.id] || '' });
          box.appendChild(md); after.appendChild(box); T.Md.hydrate(md, {});
        });
        after.appendChild(h('h2', 'Grade yourself'));
        after.appendChild(h('p.muted', 'Be honest. Tick each point that your answer covered.'));
        var scoreEl = h('div.drill-score'), total = d.rubric.reduce(function (a, r) { return a + (r.weight || 1); }, 0);
        var list = h('div.rubric');
        d.rubric.forEach(function (r, i) {
          var cb = h('input', { type: 'checkbox', checked: !!rec.rubric[i], onchange: function () { rec.rubric[i] = cb.checked; calc(); } });
          list.appendChild(h('label.rubric-item', cb, h('span', r.item), h('span.chip', (r.weight || 1) + (r.weight === 1 ? ' point' : ' points'))));
        });
        after.append(list, scoreEl);
        if (d.followUps.length) {
          after.appendChild(h('h2', 'Follow-up questions'));
          after.appendChild(h('ul', d.followUps.map(function (q) { return h('li', q); })));
        }
        function calc() {
          var got = d.rubric.reduce(function (a, r, i) { return a + (rec.rubric[i] ? (r.weight || 1) : 0); }, 0), pct = Math.round(got / total * 100);
          var first = rec.score == null;
          S.update(function (s) {
            rec.score = Math.max(rec.score || 0, pct); rec.last = pct; rec.at = Date.now(); s.drills[lesson.id] = rec; S.touch(1);
            if (first && pct > 0) s.xp += 30;
          }, 'quiet');
          U.clear(scoreEl);
          scoreEl.append(h('div.score-ring', { style: { '--p': pct } }, h('b', pct + '%')), h('div', h('b', got + ' of ' + total + ' points'),
            h('p.muted', pct >= 70 ? 'Strong answer. Practise saying it out loud in the same time.' : 'Read the model answer again and write the missing points in your own words.')));
        }
        calc();
      }
      return function () { if (tick) clearInterval(tick); };
    }
  };
})(window.TSP = window.TSP || {});
