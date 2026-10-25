/* pages/review.js - Leitner review: today's due cards and all boxes. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C;
  T.pages = T.pages || {};

  T.pages.review = {
    render: function (el) {
      T.setTitle('Review');
      var wrap = h('div.wrap.narrow'), stop = null;
      el.appendChild(wrap);
      function home() {
        if (stop) { stop(); stop = null; }
        U.clear(wrap);
        var due = S.dueCards(), all = S.dueCards(true), boxes = S.boxCounts();
        wrap.appendChild(h('div.page-head', h('div', h('h1', 'Review'), h('p.muted', 'Spaced review helps you remember. Cards come back after 1, 2, 4, 8 and 16 days.'))));
        wrap.appendChild(h('div.boxes', [1, 2, 3, 4, 5].map(function (b) {
          return h('div.box', h('span.box-n', 'Box ' + b), h('b', String(boxes[b])), h('span.muted.small', 'every ' + S.INTERVALS[b] + (S.INTERVALS[b] === 1 ? ' day' : ' days')));
        })));
        if (!all.length) {
          wrap.appendChild(h('div.empty', h('h3', 'No cards yet'), h('p', 'Finish a lesson and its flashcards appear here. Questions you miss in a quiz come here too.'), h('a.btn.primary', { href: '#/' }, 'Go to the path')));
          return;
        }
        if (due.length) {
          wrap.appendChild(h('div.review-start', h('div', h('h3', due.length + (due.length === 1 ? ' card is' : ' cards are') + ' due today'),
            h('p.muted', 'About ' + Math.max(1, Math.round(due.length * 0.4)) + ' minutes.')),
            h('button.btn.primary', { type: 'button', onclick: function () { start(due); } }, 'Start review')));
        } else {
          var next = all.map(function (c) { return c.due; }).sort()[0];
          wrap.appendChild(h('div.review-start.done', h('div', h('h3', 'All done for today'), h('p.muted', 'Next cards are due ' + (U.daysBetween(U.ymd(), next) <= 1 ? 'tomorrow' : 'in ' + U.daysBetween(U.ymd(), next) + ' days') + '.')),
            h('button.btn', { type: 'button', onclick: function () { start(all.slice(0, 20)); } }, 'Practise 20 cards anyway')));
        }
        var list = h('details.card-list', h('summary', 'All cards (' + all.length + ')'));
        all.forEach(function (c) {
          list.appendChild(h('div.card-row', h('span.chip', 'Box ' + c.box), h('span.cr-text', c.kind === 'q' ? 'Quiz question: ' + c.q.q : c.front), h('span.muted.small', c.due <= U.ymd() ? 'due' : c.due)));
        });
        wrap.appendChild(list);
      }
      function start(cards) {
        U.clear(wrap);
        wrap.appendChild(h('div.page-head', h('h1', 'Review session'), h('button.btn.sm', { type: 'button', onclick: home }, 'Stop')));
        var host = h('div.review-host'); wrap.appendChild(host);
        stop = T.Review.session(host, cards, null);
      }
      home();
      return function () { if (stop) stop(); };
    }
  };
})(window.TSP = window.TSP || {});
