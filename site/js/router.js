/* router.js - tiny hash router. Routes look like "#/lesson/s1-03-resampling?s=2".
   A page module is { render(container, params, query) -> optional cleanup function }. */
(function (T) {
  'use strict';
  var routes = [], cleanup = null, container = null, current = null;

  function parse() {
    var hash = location.hash.replace(/^#/, '') || '/';
    var q = {}, path = hash;
    var i = hash.indexOf('?');
    if (i >= 0) {
      path = hash.slice(0, i);
      hash.slice(i + 1).split('&').forEach(function (kv) {
        var p = kv.split('='); if (p[0]) q[decodeURIComponent(p[0])] = decodeURIComponent(p[1] || '');
      });
    }
    return { path: path.replace(/\/+$/, '') || '/', query: q };
  }

  var R = T.R = {
    add: function (pattern, name, page) {
      var keys = [];
      var re = new RegExp('^' + pattern.replace(/:([a-z]+)/g, function (_, k) { keys.push(k); return '([^/]+)'; }) + '$');
      routes.push({ re: re, keys: keys, name: name, page: page });
    },
    start: function (el) {
      container = el;
      window.addEventListener('hashchange', R.render);
      R.render();
    },
    go: function (path) { location.hash = '#' + path; },
    /** Update the query string in the address bar without re-rendering the page. */
    replaceQuery: function (query) {
      var p = parse().path;
      var qs = Object.keys(query).map(function (k) { return encodeURIComponent(k) + '=' + encodeURIComponent(query[k]); }).join('&');
      try { history.replaceState(null, '', '#' + p + (qs ? '?' + qs : '')); } catch (e) { /* ignore */ }
    },
    current: function () { return current; },
    render: function () {
      var loc = parse();
      if (typeof cleanup === 'function') { try { cleanup(); } catch (e) { console.error(e); } }
      cleanup = null;
      var found = null, params = {};
      for (var i = 0; i < routes.length && !found; i++) {
        var m = routes[i].re.exec(loc.path);
        if (m) {
          found = routes[i];
          routes[i].keys.forEach(function (k, j) { params[k] = decodeURIComponent(m[j + 1]); });
        }
      }
      current = { name: found ? found.name : 'notfound', params: params, query: loc.query, path: loc.path };
      T.U.clear(container);
      container.className = 'page page-' + current.name;
      if (found) cleanup = found.page.render(container, params, loc.query);
      else container.appendChild(T.U.h('div.wrap', T.U.h('h1', 'Page not found'), T.U.h('p', 'We could not find this page. '), T.U.h('a.btn', { href: '#/' }, 'Go to the path')));
      document.dispatchEvent(new CustomEvent('tsp:route', { detail: current }));
      if (!loc.query.keep) window.scrollTo(0, 0);
    }
  };
})(window.TSP = window.TSP || {});
