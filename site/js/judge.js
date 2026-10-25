/* judge.js - client for the Python worker: boot status, running jobs, 10 s time limit.
   If a run takes longer than the limit the worker is terminated and restarted. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h;
  var LIMIT_MS = 10000;

  var worker = null, state = 'idle', message = '', listeners = [], seq = 0, active = null;

  function setState(s, msg) {
    state = s; message = msg || '';
    listeners.forEach(function (fn) { fn(state, message); });
  }

  function boot() {
    if (worker) return;
    try { worker = new Worker('engine/worker.js'); } catch (e) { setState('error', 'This browser cannot run Python here.'); return; }
    setState('loading', 'Loading Python… (about 12 MB the first time)');
    worker.onmessage = onMessage;
    worker.onerror = function (e) {
      setState('error', 'Python stopped: ' + (e.message || 'unknown error'));
      if (active) { active.reject(new Error(e.message || 'worker error')); active = null; }
    };
  }

  function onMessage(ev) {
    var m = ev.data;
    if (m.type === 'status') {
      if (active && active.onStatus) active.onStatus(m.msg);
      setState(state === 'ready' || state === 'busy' ? 'busy' : 'loading', m.msg);
      return;
    }
    if (m.type === 'ready') { setState('ready'); return; }
    if (m.type === 'error' && m.fatal) { setState('error', m.msg); return; }
    if (!active || m.id !== active.id) return;
    if (m.type === 'started') { arm(); setState('busy', 'Running…'); return; }
    if (m.type === 'case') { active.partial.push(m.res); arm(); if (active.onCase) active.onCase(m.res); return; }
    if (m.type === 'done') { var a = active; active = null; clearTimeout(a.timer); setState('ready'); a.resolve(m.result); return; }
    if (m.type === 'error') { var b = active; active = null; clearTimeout(b.timer); setState('ready'); b.reject(new Error(m.msg)); }
  }

  /** (Re)start the time limit; called when a job starts and after every finished case. */
  function arm() {
    if (!active) return;
    clearTimeout(active.timer);
    active.timer = setTimeout(timeout, active.limit || LIMIT_MS);
  }
  function timeout() {
    var a = active; if (!a) return;
    active = null;
    worker.terminate(); worker = null;
    setState('idle'); boot();                          // fresh worker for the next run
    a.resolve({ tle: true, partial: a.partial });
  }

  function request(msg, opts) {
    boot();
    return new Promise(function (resolve, reject) {
      if (active) { reject(new Error('Python is busy. Wait for the current run to finish.')); return; }
      var id = ++seq;
      active = { id: id, limit: opts && opts.limitMs, resolve: resolve, reject: reject, partial: [], onCase: opts && opts.onCase, onStatus: opts && opts.onStatus, timer: null };
      msg.id = id;
      if (state === 'ready') setState('busy', 'Starting…');
      worker.postMessage(msg);
    });
  }

  var Judge = T.Judge = {
    LIMIT_MS: LIMIT_MS,
    state: function () { return { state: state, message: message }; },
    subscribe: function (fn) { listeners.push(fn); fn(state, message); return function () { listeners = listeners.filter(function (f) { return f !== fn; }); }; },
    boot: boot,
    busy: function () { return !!active; },

    /** Run a judge job. Resolves with the harness result (or a Time Limit Exceeded result). */
    run: function (job, opts) {
      opts = opts || {};
      return request({ type: 'run', job: job, packages: opts.packages || [] }, opts).then(function (r) {
        if (r && r.tle) {
          var done = r.partial || [];
          var results = done.slice();
          results.push({ i: done.length, name: 'Case ' + (done.length + 1), call: opts.nextCall || '', visible: true, ok: false, got: null, expected: null,
            msg: '', stdout: '', error: 'Time Limit Exceeded: your code ran for more than ' + LIMIT_MS / 1000 + ' seconds. Check for an infinite loop or a very slow approach.', ms: LIMIT_MS });
          return { status: 'Time Limit Exceeded', passed: done.filter(function (x) { return x.ok; }).length, total: opts.total || results.length, results: results,
            error: 'Time limit of ' + LIMIT_MS / 1000 + ' seconds exceeded.' };
        }
        return r;
      });
    },

    /** Playground: run free code. Resolves {stdout, error, ms}. */
    play: function (code, opts) {
      var lim = (opts && opts.limitMs) || LIMIT_MS;
      return request({ type: 'play', code: code }, { limitMs: lim }).then(function (r) {
        if (r && r.tle) return { stdout: '', error: 'Time Limit Exceeded: the code ran for more than ' + lim / 1000 + ' seconds and was stopped.', ms: LIMIT_MS, tle: true };
        return r;
      });
    },

    /** Small status chip: "Python: ready". */
    chip: function () {
      var dot = h('i.dot'), txt = h('span');
      var el = h('span.chip.engine', { role: 'status', title: 'Python engine status' }, dot, txt);
      Judge.subscribe(function (s, msg) {
        el.className = 'chip engine ' + s;
        txt.textContent = s === 'ready' ? 'Python: ready' : s === 'idle' ? 'Python: not started' : s === 'busy' ? 'Python: running' :
          s === 'error' ? 'Python: error' : 'Python: loading…';
        el.title = msg || txt.textContent;
        el.setAttribute('aria-label', msg || txt.textContent);
      });
      return el;
    }
  };
})(window.TSP = window.TSP || {});
