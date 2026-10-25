/* pages/glossary.js - searchable A-Z glossary. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, C = T.C;
  T.pages = T.pages || {};

  T.pages.glossary = {
    render: function (el, params, query) {
      T.setTitle('Glossary');
      var terms = Object.keys(C.glossary).sort(), wrap = h('div.wrap.narrow');
      var input = h('input.input.search', { type: 'search', placeholder: 'Search terms', 'aria-label': 'Search the glossary', value: query.q || '', oninput: draw });
      wrap.append(h('div.page-head', h('div', h('h1', 'Glossary'), h('p.muted', terms.length + ' terms in simple English. In lessons, tap a dotted word to see its meaning.'))), input);
      var jump = h('nav.az', { 'aria-label': 'Jump to letter' }), list = h('div.gloss-list');
      wrap.append(jump, list);
      el.appendChild(wrap);
      function draw() {
        var q = input.value.trim().toLowerCase(), by = {};
        terms.filter(function (k) { var g = C.glossary[k]; return !q || k.indexOf(q) >= 0 || g.simple.toLowerCase().indexOf(q) >= 0; })
          .forEach(function (k) { var L = (k[0] || '#').toUpperCase(); (by[L] = by[L] || []).push(k); });
        U.clear(list); U.clear(jump);
        var letters = Object.keys(by).sort();
        if (!letters.length) list.appendChild(h('div.empty', terms.length ? 'No terms match.' : 'The glossary is empty for now.'));
        letters.forEach(function (L) {
          jump.appendChild(h('a', { href: '#', onclick: function (e) { e.preventDefault(); document.getElementById('g-' + L).scrollIntoView(); } }, L));
          var sec = h('section', h('h2.gl', { id: 'g-' + L }, L));
          by[L].forEach(function (k) {
            var g = C.glossary[k];
            sec.appendChild(h('div.gloss-item' + (query.q === k ? '.hl' : ''), h('b', g.term || k), h('p', g.simple), g.example ? h('p.muted.small', 'Example: ' + g.example) : null));
          });
          list.appendChild(sec);
        });
      }
      draw();
    }
  };
})(window.TSP = window.TSP || {});
