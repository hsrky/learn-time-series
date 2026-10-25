/* quiz.js - question renderer (single / multi / numeric / order) used by inline checks,
   the mastery quiz and the review page, plus the mastery-quiz runner. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;

  /** Text with `backticks` -> <code>. Safe: built with DOM nodes. */
  function rich(text) {
    var out = [];
    String(text).split(/(`[^`]+`)/).forEach(function (p) {
      if (p.length > 2 && p[0] === '`' && p[p.length - 1] === '`') out.push(h('code', p.slice(1, -1)));
      else if (p) out.push(p);
    });
    return out;
  }

  /**
   * Render one question.
   * opts: { retry: bool (show "Try again" after a wrong answer), onChecked(correct), seed }
   * Returns { el, checked() }.
   */
  function render(q, opts) {
    opts = opts || {};
    var type = q.type || 'single';
    var el = h('div.q.q-' + type);
    var checked = false, correct = false;
    var sel = type === 'multi' ? [] : null;           // selected option indexes
    var order = null;                                  // current order (order type)
    var numInput = null;
    var feedback = h('div.q-feedback', { 'aria-live': 'polite' });
    var checkBtn = h('button.btn.primary', { type: 'button', onclick: check }, 'Check answer');
    var again = h('button.btn', { type: 'button', hidden: true, onclick: reset }, 'Try again');
    var body = h('div.q-body');

    el.appendChild(h('p.q-text', rich(q.q)));
    el.appendChild(body);
    el.appendChild(h('div.q-actions', checkBtn, again));
    el.appendChild(feedback);

    function optionButtons() { return body.querySelectorAll('.opt'); }

    function build() {
      U.clear(body); U.clear(feedback);
      checked = false; correct = false; checkBtn.hidden = false; again.hidden = true;
      checkBtn.disabled = type !== 'order';
      if (type === 'single' || type === 'multi') {
        sel = type === 'multi' ? [] : null;
        var group = h('div.opts', { role: type === 'single' ? 'radiogroup' : 'group', 'aria-label': 'Answer options' });
        q.options.forEach(function (o, i) {
          var b = h('button.opt', { type: 'button', role: type === 'single' ? 'radio' : 'checkbox', 'aria-checked': 'false',
            onclick: function () { if (!checked) toggle(i); } },
            h('span.opt-mark', type === 'single' ? '' : ''), h('span.opt-text', rich(o)));
          b.dataset.i = i;
          group.appendChild(b);
        });
        body.appendChild(group);
      } else if (type === 'numeric') {
        numInput = h('input.input', { type: 'text', inputmode: 'decimal', 'aria-label': 'Your answer', placeholder: 'Type a number',
          oninput: function () { checkBtn.disabled = numInput.value.trim() === '' || isNaN(parseFloat(numInput.value.replace(',', '.'))); },
          onkeydown: function (e) { if (e.key === 'Enter' && !checkBtn.disabled) check(); } });
        body.appendChild(numInput);
      } else if (type === 'order') {
        var correctIdx = q.options.map(function (_, i) { return i; });
        order = U.shuffle(correctIdx, U.hashStr(q.q + (opts.seed || '')));
        if (order.length > 1 && order.every(function (v, i) { return v === i; })) order.reverse();
        drawOrder();
      }
    }
    function toggle(i) {
      if (type === 'single') sel = i;
      else { var k = sel.indexOf(i); if (k >= 0) sel.splice(k, 1); else sel.push(i); }
      optionButtons().forEach(function (b) {
        var on = type === 'single' ? sel === +b.dataset.i : sel.indexOf(+b.dataset.i) >= 0;
        b.classList.toggle('sel', on); b.setAttribute('aria-checked', on);
      });
      checkBtn.disabled = type === 'single' ? sel == null : sel.length === 0;
    }
    function drawOrder() {
      U.clear(body);
      var list = h('ol.order-list');
      order.forEach(function (idx, pos) {
        list.appendChild(h('li.order-item', h('span.opt-text', rich(q.options[idx])),
          h('span.order-btns',
            h('button.icon-btn', { type: 'button', 'aria-label': 'Move up', disabled: checked || pos === 0, onclick: function () { move(pos, -1); } }, '↑'),
            h('button.icon-btn', { type: 'button', 'aria-label': 'Move down', disabled: checked || pos === order.length - 1, onclick: function () { move(pos, 1); } }, '↓'))));
      });
      body.appendChild(h('p.muted.small', 'Use the arrows to put the steps in the right order.'));
      body.appendChild(list);
    }
    function move(pos, d) {
      var t = order[pos]; order[pos] = order[pos + d]; order[pos + d] = t;
      drawOrder();
      var btns = body.querySelectorAll('.order-item')[pos + d].querySelectorAll('button');
      (btns[d < 0 ? 0 : 1].disabled ? btns[d < 0 ? 1 : 0] : btns[d < 0 ? 0 : 1]).focus();
    }

    function check() {
      if (checked) return;
      checked = true;
      checkBtn.hidden = true;
      var why = q.why;
      if (type === 'single') {
        correct = sel === q.answer;
        optionButtons().forEach(function (b) {
          var i = +b.dataset.i;
          b.classList.add(i === q.answer ? 'right' : (i === sel ? 'wrong' : 'dim'));
          b.querySelector('.opt-mark').textContent = i === q.answer ? '✓' : (i === sel ? '✗' : '');
          b.appendChild(h('span.opt-why', why[i]));
        });
      } else if (type === 'multi') {
        var ans = q.answer.slice().sort().join(',');
        correct = sel.slice().sort().join(',') === ans;
        optionButtons().forEach(function (b) {
          var i = +b.dataset.i, isRight = q.answer.indexOf(i) >= 0, chosen = sel.indexOf(i) >= 0;
          b.classList.add(isRight ? 'right' : (chosen ? 'wrong' : 'dim'));
          b.querySelector('.opt-mark').textContent = isRight ? '✓' : (chosen ? '✗' : '');
          if (isRight && !chosen) b.classList.add('missed');
          b.appendChild(h('span.opt-why', (isRight && !chosen ? 'You missed this one. ' : '') + why[i]));
        });
      } else if (type === 'numeric') {
        var v = parseFloat(numInput.value.replace(',', '.'));
        correct = Math.abs(v - q.answer) <= (q.tol || 0) + 1e-12;
        numInput.disabled = true;
        numInput.classList.add(correct ? 'right' : 'wrong');
      } else if (type === 'order') {
        correct = order.every(function (v, i) { return v === i; });
        drawOrder();
        body.querySelectorAll('.order-item').forEach(function (li, pos) {
          li.classList.add(order[pos] === pos ? 'right' : 'wrong');
        });
      }
      var head = h('div.q-verdict.' + (correct ? 'ok' : 'bad'), correct ? 'Correct!' : 'Not quite.');
      feedback.appendChild(head);
      if (type === 'numeric') feedback.appendChild(h('p', 'Answer: ' + q.answer + (q.tol ? ' (± ' + q.tol + ')' : '') + '. ' + why));
      if (type === 'order') {
        if (!correct) feedback.appendChild(h('p', 'Correct order: ' + q.options.map(function (o, i) { return (i + 1) + '. ' + o; }).join('  ')));
        feedback.appendChild(h('p', why));
      }
      if (!correct && T.AI && T.AI.wrongSlot) feedback.appendChild(T.AI.wrongSlot(q, { type: type, sel: sel, order: order, num: numInput ? numInput.value : '' }));
      if (!correct && opts.retry) again.hidden = false;
      if (opts.onChecked) opts.onChecked(correct, { sel: sel, order: order });
    }
    function reset() { build(); }

    build();
    return { el: el, checked: function () { return checked; }, correct: function () { return correct; } };
  }

  /** Inline "check" blocks in lessons (Warm-up and concept chunks). */
  function hydrateCheck(host, spec, ctx) {
    var done = false;
    var card = h('div.check-card', h('div.check-label', U.icon('target', 16), ' Quick check'));
    var q = render(spec, {
      retry: true, seed: ctx && ctx.lessonId,
      onChecked: function (ok) {
        if (ok && !done) {
          done = true;
          S.update(function (s) { s.xp += 2; S.touch(1); });
        }
      }
    });
    card.appendChild(q.el);
    host.appendChild(card);
  }

  /* ------------------------------------------------------------ mastery quiz */
  function runQuiz(host, lesson, onDone) {
    var qs = lesson.quiz.questions, pass = lesson.quiz.pass || 0.8;
    var idx = 0, score = 0, missed = [];
    function start() { idx = 0; score = 0; missed = []; show(); }
    function show() {
      U.clear(host);
      if (idx >= qs.length) return finish();
      var pct = idx / qs.length * 100;
      host.appendChild(h('div.quiz-head',
        h('span.muted', 'Question ' + (idx + 1) + ' of ' + qs.length),
        h('div.bar', h('i', { style: { width: pct + '%' } }))));
      var next = h('button.btn.primary', { type: 'button', hidden: true, onclick: function () { idx++; show(); } },
        idx === qs.length - 1 ? 'See my score' : 'Next question');
      var q = render(qs[idx], {
        seed: lesson.id + idx,
        onChecked: function (ok) {
          if (ok) score++; else missed.push(idx);
          next.hidden = false; next.focus();
        }
      });
      host.appendChild(q.el);
      host.appendChild(h('div.q-next', next));
    }
    function finish() {
      var frac = score / qs.length, ok = frac >= pass - 1e-9;
      var firstPass = false;
      S.update(function (s) {
        var l = S.lesson(lesson.id);
        var prev = l.quiz || { best: 0, attempts: 0 };
        firstPass = ok && !(prev.best >= pass);
        l.quiz = { best: Math.max(prev.best, frac), last: frac, attempts: (prev.attempts || 0) + 1, at: Date.now() };
        S.touch(2);
        if (firstPass) s.xp += 30;
      }, 'quiz');
      missed.forEach(function (i) { S.addMissed(lesson.id, i); });
      if (firstPass) U.toast('+30 XP · mastery quiz passed', 'xp');
      U.clear(host);
      host.appendChild(h('div.quiz-result.' + (ok ? 'ok' : 'bad'),
        h('div.score-ring', { style: { '--p': Math.round(frac * 100) } }, h('b', Math.round(frac * 100) + '%')),
        h('div',
          h('h3', ok ? 'You passed the mastery quiz!' : 'Almost there.'),
          h('p', score + ' of ' + qs.length + ' correct. You need ' + Math.round(pass * 100) + '% to pass.'),
          missed.length ? h('p.muted', 'We added ' + missed.length + ' missed question' + (missed.length > 1 ? 's' : '') + ' to your review list.') : null,
          h('div.row', h('button.btn' + (ok ? '' : '.primary'), { type: 'button', onclick: start }, ok ? 'Take it again' : 'Try again')))));
      if (onDone) onDone(ok, frac);
    }
    start();
  }

  T.Quiz = { render: render, hydrateCheck: hydrateCheck, runQuiz: runQuiz, rich: rich };
})(window.TSP = window.TSP || {});
