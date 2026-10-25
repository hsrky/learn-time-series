/* ai-sync.js - optional progress mirror for the Claude Artifact build (phase 2).
   Needs claude.use("db") AND claude.use("user"). localStorage stays the primary store; the db copy is a mirror
   so progress follows the learner to another device.
   - Documents (private per viewer): data/users/<id>/progress  (everything except code)
                                     data/users/<id>/progress-code  (the code of each problem)
     (the runtime counts path segments: a document path needs an EVEN number, so "progress/main" would be a collection.)
   - Writes: only when something changed, debounced, never more than one write per 10 s, one at a time.
   - Merge: per item, the newest timestamp wins. Numbers (xp, activity) take the larger value; mock tests are united.
   On any other host window.claude does not exist and none of this runs. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S;
  var META_KEY = 'tsp:ai:sync', MIN_GAP = 10000, DEBOUNCE = 4000, MAX_DOC = 240000;

  var db = null, uid = null, on = false, busy = false, again = false, timer = null;
  var lastWrite = 0, lastPull = 0, lastSaved = 0, status = 'off', detail = '', lastPayloadHash = '', lastCodeHash = '';
  var meta = { ts: {}, hash: {} }, firstRun = true;

  try { var m0 = JSON.parse(localStorage.getItem(META_KEY) || 'null'); if (m0 && m0.ts && m0.hash) { meta = m0; firstRun = false; } } catch (e) { /* ignore */ }
  function saveMeta() { try { localStorage.setItem(META_KEY, JSON.stringify(meta)); } catch (e) { /* ignore */ } }

  function enabled() { return on && S.get().settings.syncOn !== false; }
  function hash(v) { return String(U.hashStr(JSON.stringify(v))); }
  function setStatus(s, d) { status = s; detail = d || ''; T.AI && T.AI.emit && T.AI.emit('sync'); }

  /* ------------------------------------------------------------ flatten the state into items */
  function collect() {
    var s = S.get(), main = {}, code = {};
    Object.keys(s.lessons || {}).forEach(function (id) { main['l:' + id] = s.lessons[id]; });
    Object.keys(s.problems || {}).forEach(function (slug) {
      var p = s.problems[slug], c = Object.assign({}, p);
      delete c.code;
      c.subs = (p.subs || []).slice(0, 10).map(function (x) { return { t: x.t, status: x.status, passed: x.passed, total: x.total, ms: x.ms }; });
      main['p:' + slug] = c;
      if (typeof p.code === 'string') code['k:' + slug] = p.code;
    });
    Object.keys(s.cards || {}).forEach(function (k) { main['c:' + k] = s.cards[k]; });
    Object.keys(s.activity || {}).forEach(function (d) { main['a:' + d] = s.activity[d]; });
    Object.keys(s.drills || {}).forEach(function (id) { main['d:' + id] = s.drills[id]; });
    main.x = s.xp || 0;
    main.m = s.mocks || [];
    main.s = { helpLang: (s.settings && s.settings.helpLang) || 'English' };
    return { main: main, code: code };
  }

  /** Stamp every item whose content changed since the last look with "now". Returns true if anything changed. */
  function detect(items) {
    var now = Date.now(), changed = false;
    [items.main, items.code].forEach(function (grp) {
      Object.keys(grp).forEach(function (k) {
        var hs = hash(grp[k]);
        if (meta.hash[k] !== hs) { meta.hash[k] = hs; meta.ts[k] = now; changed = true; }
      });
    });
    return changed;
  }

  /* ------------------------------------------------------------ apply a remote item to local state */
  function clone(v) { return v === undefined ? undefined : JSON.parse(JSON.stringify(v)); }
  function applyItem(key, v, ts) {
    v = clone(v);                                           // snapshots are frozen; local state must stay mutable
    var s = S.get(), id = key.slice(2), kind = key.slice(0, 2);
    if (key === 'x') s.xp = Math.max(s.xp || 0, +v || 0);
    else if (key === 'm') {
      var seen = {}; (s.mocks || []).forEach(function (x) { seen[x.at] = 1; });
      (Array.isArray(v) ? v : []).forEach(function (x) { if (x && !seen[x.at]) s.mocks.push(x); });
      s.mocks.sort(function (a, b) { return a.at - b.at; });
    } else if (key === 's') { if (v && v.helpLang) s.settings.helpLang = v.helpLang; }
    else if (kind === 'l:') s.lessons[id] = v;
    else if (kind === 'p:') {
      var local = s.problems[id] || {}, byT = {};
      (local.subs || []).forEach(function (x) { byT[x.t] = x; });
      var np = Object.assign({}, v); np.subs = (v.subs || []).map(function (x) { return byT[x.t] || x; });
      if (local.code != null) np.code = local.code;
      s.problems[id] = np;
    } else if (kind === 'k:') { if (!s.problems[id]) s.problems[id] = { runs: 0, submits: 0, hints: 0, subs: [] }; s.problems[id].code = v; }
    else if (kind === 'c:') s.cards[id] = v;
    else if (kind === 'a:') s.activity[id] = Math.max(s.activity[id] || 0, +v || 0);
    else if (kind === 'd:') s.drills[id] = v;
    else return;
    var cur = collect(), cv = key.charAt(1) === ':' && key.charAt(0) === 'k' ? cur.code[key] : cur.main[key];
    meta.hash[key] = hash(cv); meta.ts[key] = ts;           // the applied value is not a local change
  }
  var ALWAYS_MERGE = function (key) { return key === 'x' || key === 'm' || key.slice(0, 2) === 'a:'; };

  /** Merge a remote doc's items into local state. Returns the number of local items that changed. */
  function mergeRemote(remoteItems, initial) {
    var n = 0;
    Object.keys(remoteItems || {}).forEach(function (key) {
      var r = remoteItems[key]; if (!r || typeof r.ts !== 'number') return;
      var lts = initial ? 0 : (meta.ts[key] || 0);
      if (ALWAYS_MERGE(key) || r.ts > lts) { applyItem(key, r.v, r.ts); n++; }
    });
    return n;
  }

  /* ------------------------------------------------------------ talking to the db */
  function docRef(name) { return db.doc('data/users/' + uid + '/' + name); }
  function readDoc(name) { return docRef(name).get().then(function (snap) { return snap.exists ? snap.data() : null; }); }

  function payload(items, which) {
    var grp = which === 'code' ? items.code : items.main, out = {};
    Object.keys(grp).forEach(function (k) { out[k] = { ts: meta.ts[k] || Date.now(), v: clone(grp[k]) }; });
    return out;
  }
  function size(o) { return JSON.stringify(o).length; }
  function fit(itemsObj) {
    if (size(itemsObj) <= MAX_DOC) return itemsObj;
    var keys = Object.keys(itemsObj).sort(function (a, b) { return size(itemsObj[b]) - size(itemsObj[a]); }), o = Object.assign({}, itemsObj);
    for (var i = 0; i < keys.length && size(o) > MAX_DOC; i++) delete o[keys[i]];      // drop the biggest items first
    return o;
  }

  function fatal(code) { on = false; setStatus('off', code === 'invalid_argument' ? 'You can view this page but not save to it.' : 'Saving to your Claude account is not available here.'); }
  function handleErr(e) {
    var code = e && e.code;
    if (code === 'invalid_argument' || code === 'not_granted' || code === 'capability_disabled' || code === 'capability_removed' || code === 'revoked') fatal(code);
    else setStatus('error', 'Could not save just now. It will try again after your next change.');
  }

  /** Read remote, merge into local, write back what is newer. `write` = false for pull-only. */
  function sync(write) {
    if (!enabled()) return Promise.resolve();
    if (busy) { again = true; return Promise.resolve(); }
    busy = true;
    var initial = firstRun;
    return Promise.all([readDoc('progress'), readDoc('progress-code')]).then(function (docs) {
      lastPull = Date.now();
      var applied = mergeRemote(docs[0] && docs[0].items, initial) + mergeRemote(docs[1] && docs[1].items, initial);
      firstRun = false;
      var items = collect();
      detect(items);
      if (applied) { S.flush(); }
      var mainItems = fit(payload(items, 'main')), codeItems = fit(payload(items, 'code'));
      var hm = hash(mainItems), hc = hash(codeItems), jobs = [];
      var remoteSame = function (d, mine) { return d && d.items && hash(d.items) === hash(mine); };
      var pristine = !docs[0] && Object.keys(mainItems).every(function (k) { return k === 'x' || k === 'm' || k === 's'; }) && !mainItems.x.v;   // nothing learned yet: nothing worth saving
      if (write && !pristine && hm !== lastPayloadHash && !remoteSame(docs[0], mainItems)) jobs.push(docRef('progress').set({ v: 1, updatedAt: Date.now(), items: mainItems }));
      if (write && hc !== lastCodeHash && Object.keys(codeItems).length && !remoteSame(docs[1], codeItems)) jobs.push(docRef('progress-code').set({ v: 1, updatedAt: Date.now(), items: codeItems }));
      lastPayloadHash = hm; lastCodeHash = hc;
      saveMeta();
      return Promise.all(jobs).then(function () {
        if (jobs.length) { lastWrite = Date.now(); lastSaved = lastWrite; }
        setStatus('ok', '');
        if (applied) afterApply();
      });
    }).catch(handleErr).then(function () {
      busy = false;
      if (again) { again = false; schedule(); }
    });
  }
  function afterApply() {
    setTimeout(function () {
      try { S.get(); T.S.flush(); } catch (e) { /* ignore */ }
      var cur = T.R.current();
      // 'sync' is ignored by our own listener; header refresh happens through 'import'
      if (typeof T.buildHeader === 'function') T.buildHeader();
      if (cur && /^(path|progress|review|problems|settings)$/.test(cur.name)) T.R.render();
    }, 0);
  }

  function schedule() {
    if (!enabled()) return;
    clearTimeout(timer);
    timer = setTimeout(function () { timer = null; sync(true); }, Math.max(DEBOUNCE, lastWrite + MIN_GAP - Date.now()));
  }
  /** Called after a local change; cheap check first so an unchanged state never causes a write. */
  function markDirty() {
    if (!enabled()) return;
    var items = collect();
    if (detect(items)) { saveMeta(); schedule(); }
  }

  /* ------------------------------------------------------------ boot */
  function boot(claude) {
    Promise.all([claude.use('db'), claude.use('user')]).then(function (r) {
      var d = r[0], u = r[1];
      if (!d || !u) return null;
      return Promise.resolve(u.id()).then(function (id) { if (!id) return null; db = d; uid = id; return id; });
    }).then(function (id) {
      if (!id) return;
      on = true; setStatus('ok', '');
      var q = S.quiet;
      S.quiet = function (fn) { q(fn); markDirty(); };                 // code autosave etc. does not emit
      S.on(function (what) { if (what !== 'sync') markDirty(); });
      var rs = S.reset, im = S.importJSON;
      S.reset = function () {
        rs.apply(S, arguments);
        meta = { ts: {}, hash: {} }; saveMeta(); lastPayloadHash = lastCodeHash = '';
        if (on) { try { docRef('progress').delete(); docRef('progress-code').delete(); } catch (e) { /* ignore */ } }
      };
      S.importJSON = function () { var out = im.apply(S, arguments); meta.hash = {}; markDirty(); return out; };
      document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible' && enabled() && Date.now() - lastPull > 60000) sync(false);
      });
      T.AI && T.AI.emit && T.AI.emit('syncready');
      return sync(true);
    }).catch(function () { /* never break the site */ });
  }

  /* ------------------------------------------------------------ settings rows */
  function statusText() {
    if (!on) return detail || 'Not available.';
    if (S.get().settings.syncOn === false) return 'Off. Progress stays only in this browser.';
    if (status === 'error') return detail;
    return lastSaved ? 'Saved to your Claude account ' + U.timeAgo(lastSaved) + '.' : 'On. Saves after your next change.';
  }
  T.AISync = {
    boot: boot,
    available: function () { return on; },
    status: function () { return { on: on, status: status, detail: detail, lastSaved: lastSaved }; },
    syncNow: function () { return sync(true); },
    settingsRows: function () {
      var cb = h('input', { type: 'checkbox', id: 'ai-sync', checked: S.get().settings.syncOn !== false, onchange: function () {
        S.update(function (st) { st.settings.syncOn = cb.checked; }, 'sync'); out.textContent = statusText();
        if (cb.checked) schedule();
      } });
      var out = h('p.muted.small', { role: 'status' }, statusText());
      return h('div.sync-rows', h('div.field-row', h('label.check-row', { for: 'ai-sync' }, cb, h('span', ' Keep my progress in my Claude account'))),
        h('p.muted.small', 'Your browser stays the main copy. This is a backup that follows you to other devices.'), out);
    }
  };
})(window.TSP = window.TSP || {});
