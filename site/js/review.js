/* review.js - Leitner review session UI (flashcards and missed quiz questions).
   Boxes 1-5, intervals 1, 2, 4, 8, 16 days (see store.js). */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S;

  /** Run a session over `cards` (array from S.dueCards). */
  function session(host, cards, onDone) {
    var queue = cards.slice(), total = cards.length, done = 0, right = 0, requeued = {};
    function show() {
      U.clear(host);
      if (!queue.length) return summary();
      var c = queue[0], flipped = false;
      host.appendChild(h('div.quiz-head', h('span.muted', 'Card ' + Math.min(done + 1, total) + ' of ' + total + ' · Box ' + c.box),
        h('div.bar', h('i', { style: { width: (done / total * 100) + '%' } }))));
      if (c.kind === 'q') {
        var q = T.Quiz.render(c.q, { seed: c.key, onChecked: function (ok) { grade(c, ok); } });
        host.appendChild(h('p.muted.small', 'A question you missed in a quiz'));
        host.appendChild(q.el);
        return;
      }
      var back = h('div.fc-back', { hidden: true }, c.back);
      var flipBtn = h('button.btn.primary', { type: 'button', onclick: flip }, 'Show answer');
      var grades = h('div.row.grades', { hidden: true },
        h('button.btn.bad', { type: 'button', onclick: function () { grade(c, false); } }, 'Missed it (1)'),
        h('button.btn.good', { type: 'button', onclick: function () { grade(c, true); } }, 'Got it (2)'));
      function flip() { flipped = true; back.hidden = false; grades.hidden = false; flipBtn.hidden = true; grades.querySelector('button').focus(); }
      var card = h('div.flashcard', { tabindex: 0, onclick: function () { if (!flipped) flip(); } },
        h('div.fc-front', c.front), back);
      host.append(card, flipBtn, grades);
      flipBtn.focus();
      show.keys = function (e) {
        if (e.key === ' ' && !flipped) { e.preventDefault(); flip(); }
        else if (flipped && e.key === '1') grade(c, false);
        else if (flipped && e.key === '2') grade(c, true);
      };
    }
    function grade(c, ok) {
      S.gradeCard(c.key, ok);
      queue.shift();
      if (ok) { right++; done++; }
      else if (!requeued[c.key]) { requeued[c.key] = 1; queue.push(c); }  // see missed cards once more today
      else done++;
      if (c.kind === 'q') setTimeout(show, 900); else show();
    }
    function summary() {
      show.keys = null;
      host.appendChild(h('div.quiz-result.ok', h('div.score-ring', { style: { '--p': Math.round(right / Math.max(1, total) * 100) } }, h('b', Math.round(right / Math.max(1, total) * 100) + '%')),
        h('div', h('h3', 'Session complete'), h('p', right + ' of ' + total + ' remembered at the first try.'),
          h('p.muted', 'Cards you missed go back to box 1. Cards you knew move up and come back later.'),
          h('a.btn.primary', { href: '#/' }, 'Back to the path'))));
      if (onDone) onDone();
    }
    var key = function (e) { if (show.keys) show.keys(e); };
    document.addEventListener('keydown', key);
    show();
    return function () { document.removeEventListener('keydown', key); };
  }

  T.Review = { session: session };
})(window.TSP = window.TSP || {});
