/* store.js - content accessors + persistent learner state (localStorage key "tsp:v1").
   Every storage access is wrapped in try/catch; if storage is blocked the app keeps
   working with in-memory state (progress is simply not remembered). */
(function (T) {
  'use strict';
  var U = T.U;
  var KEY = 'tsp:v1';

  /* ------------------------------------------------------------ content */
  var raw = window.TSP_CONTENT || { stages: [], lessons: {}, problems: {}, glossary: {}, mockSets: [], counts: {} };
  var C = T.C = {
    raw: raw,
    stages: raw.stages || [],
    lessons: raw.lessons || {},
    problems: raw.problems || {},
    glossary: raw.glossary || {},
    mockSets: raw.mockSets || [],
    stageById: {},
    lessonList: [],          // all lessons in curriculum order
    problemList: [],         // all problems in curriculum order
    nextOf: {}, prevOf: {}
  };
  C.stages.forEach(function (s) {
    C.stageById[s.id] = s;
    s.lessons.forEach(function (id) { C.lessonList.push(C.lessons[id]); });
  });
  C.lessonList.forEach(function (l, i) {
    if (C.lessonList[i + 1]) C.nextOf[l.id] = C.lessonList[i + 1].id;
    if (i > 0) C.prevOf[l.id] = C.lessonList[i - 1].id;
    l.problems.forEach(function (slug) { C.problemList.push(C.problems[slug]); });
  });
  C.stageIndex = function (id) { return C.stages.findIndex(function (s) { return s.id === id; }); };

  /* ------------------------------------------------------------ storage */
  var DEFAULTS = function () {
    return {
      v: 1,
      settings: { theme: 'auto', fontSize: 16, split: 46, aiOn: true, helpLang: 'English', syncOn: true },
      lessons: {}, problems: {}, cards: {}, activity: {}, xp: 0, drills: {}, mocks: [],
      mockSession: null, playground: '', created: Date.now()
    };
  };
  var state = DEFAULTS();
  var memoryOnly = false;
  var listeners = [];

  function load() {
    try {
      var txt = localStorage.getItem(KEY);
      if (txt) {
        var d = JSON.parse(txt);
        state = Object.assign(DEFAULTS(), d);
        state.settings = Object.assign(DEFAULTS().settings, d.settings || {});
      }
    } catch (e) { memoryOnly = true; }
  }
  var writeNow = function () {
    try { localStorage.setItem(KEY, JSON.stringify(state)); memoryOnly = false; } catch (e) { memoryOnly = true; }
  };
  var writeSoon = U.debounce(writeNow, 300);
  window.addEventListener('beforeunload', writeNow);

  function emit(what) { listeners.forEach(function (fn) { try { fn(what); } catch (e) { console.error(e); } }); }

  var S = T.S = {
    get: function () { return state; },
    isMemoryOnly: function () { return memoryOnly; },
    /** Mutate state inside fn, then save and notify. */
    update: function (fn, what) { fn(state); writeSoon(); emit(what || 'state'); },
    /** Save without notifying (used for high-frequency writes such as code autosave). */
    quiet: function (fn) { fn(state); writeSoon(); },
    flush: writeNow,
    on: function (fn) { listeners.push(fn); },
    off: function (fn) { listeners = listeners.filter(function (f) { return f !== fn; }); },

    lesson: function (id) { return state.lessons[id] || (state.lessons[id] = {}); },
    problem: function (slug) {
      return state.problems[slug] || (state.problems[slug] = { runs: 0, submits: 0, hints: 0, subs: [] });
    },

    /* ---- activity, XP, streak ---- */
    touch: function (n) {
      var d = U.ymd();
      state.activity[d] = (state.activity[d] || 0) + (n || 1);
    },
    addXP: function (n, why) {
      S.update(function (s) { s.xp += n; S.touch(1); });
      if (why) U.toast('+' + n + ' XP · ' + why, 'xp');
    },
    level: function () {
      var xp = state.xp, lvl = Math.floor(Math.sqrt(xp / 40)) + 1;
      var lo = 40 * Math.pow(lvl - 1, 2), hi = 40 * Math.pow(lvl, 2);
      return { level: lvl, xp: xp, lo: lo, hi: hi, pct: (xp - lo) / (hi - lo) };
    },
    streak: function () {
      var act = state.activity, d = U.ymd();
      if (!act[d]) d = U.addDays(d, -1);
      var cur = 0;
      while (act[d]) { cur++; d = U.addDays(d, -1); }
      var days = Object.keys(act).filter(function (k) { return act[k] > 0; }).sort();
      var best = 0, run = 0, prev = null;
      days.forEach(function (k) {
        run = prev && U.daysBetween(prev, k) === 1 ? run + 1 : 1;
        best = Math.max(best, run); prev = k;
      });
      return { current: cur, best: Math.max(best, cur), today: !!act[U.ymd()] };
    },

    /* ---- lesson / problem status ---- */
    problemSolved: function (slug) { return !!(state.problems[slug] && state.problems[slug].solved); },
    problemStatus: function (slug) {
      var p = state.problems[slug];
      if (!p) return 'todo';
      if (p.solved) return 'solved';
      return (p.subs && p.subs.length) || p.runs ? 'attempted' : 'todo';
    },
    /** none | learned | practiced | mastered  (see DESIGN.md: mastery learning) */
    lessonStatus: function (id) {
      var l = state.lessons[id], lesson = C.lessons[id];
      if (!l || !lesson) return 'none';
      var quizOk = l.quiz && l.quiz.best >= (lesson.quiz.pass || 0.8);
      var solved = lesson.problems.some(S.problemSolved);
      var hasProblems = lesson.problems.length > 0;
      var hasQuiz = lesson.quiz.questions && lesson.quiz.questions.length > 0;
      if (!l.learned && !quizOk && !solved) return l.visited ? 'none' : 'none';
      var masteredQuiz = !hasQuiz || quizOk, masteredProb = !hasProblems || solved;
      if (l.learned && masteredQuiz && masteredProb && (hasQuiz || hasProblems)) return 'mastered';
      if (l.learned && (quizOk || solved)) return 'practiced';
      return 'learned';
    },
    stageCounts: function (stageId) {
      var out = { total: 0, learned: 0, practiced: 0, mastered: 0 };
      C.stageById[stageId].lessons.forEach(function (id) {
        out.total++;
        var st = S.lessonStatus(id);
        if (st === 'learned' || st === 'practiced' || st === 'mastered') out.learned++;
        if (st === 'practiced' || st === 'mastered') out.practiced++;
        if (st === 'mastered') out.mastered++;
      });
      return out;
    },
    /** Lesson to resume: last visited unfinished lesson, else first lesson not yet learned. */
    continueLesson: function () {
      var last = state.lastLesson;
      if (last && C.lessons[last] && S.lessonStatus(last) === 'none') return last;
      var first = C.lessonList.find(function (l) { return S.lessonStatus(l.id) === 'none'; });
      if (last && C.lessons[last] && !first) return last;
      return first ? first.id : (C.lessonList[0] && C.lessonList[0].id);
    },

    /* ---- Leitner flashcards: boxes 1..5, intervals 1,2,4,8,16 days ---- */
    INTERVALS: [0, 1, 2, 4, 8, 16],
    addCards: function (lessonId) {
      var lesson = C.lessons[lessonId], n = 0;
      S.update(function (s) {
        lesson.cards.forEach(function (c, i) {
          var key = lessonId + '#' + i;
          if (!s.cards[key]) {
            s.cards[key] = { kind: 'card', lesson: lessonId, front: c.front, back: c.back, box: 1, due: U.addDays(U.ymd(), 1), added: Date.now() };
            n++;
          }
        });
      }, 'cards');
      return n;
    },
    addMissed: function (lessonId, idx) {
      var q = C.lessons[lessonId].quiz.questions[idx];
      S.update(function (s) {
        var key = lessonId + '#q' + idx;
        if (!s.cards[key]) s.cards[key] = { kind: 'q', lesson: lessonId, q: q, box: 1, due: U.addDays(U.ymd(), 1), added: Date.now() };
        else { s.cards[key].box = 1; s.cards[key].due = U.addDays(U.ymd(), 1); }
      }, 'cards');
    },
    dueCards: function (all) {
      var today = U.ymd();
      return Object.keys(state.cards).filter(function (k) { return all || state.cards[k].due <= today; })
        .map(function (k) { return Object.assign({ key: k }, state.cards[k]); })
        .sort(function (a, b) { return a.due < b.due ? -1 : a.due > b.due ? 1 : a.box - b.box; });
    },
    gradeCard: function (key, ok) {
      S.update(function (s) {
        var c = s.cards[key]; if (!c) return;
        c.box = ok ? Math.min(5, c.box + 1) : 1;
        c.due = U.addDays(U.ymd(), S.INTERVALS[c.box]);
        c.last = Date.now();
        S.touch(1);
        if (ok) s.xp += 1;
      }, 'cards');
    },
    boxCounts: function () {
      var out = [0, 0, 0, 0, 0, 0];
      Object.keys(state.cards).forEach(function (k) { out[state.cards[k].box]++; });
      return out;
    },

    /* ---- backup ---- */
    exportJSON: function () { return JSON.stringify({ app: 'timeseries-path', exported: new Date().toISOString(), data: state }, null, 1); },
    importJSON: function (text) {
      var d = JSON.parse(text);
      if (!d || d.app !== 'timeseries-path' || !d.data || typeof d.data !== 'object') throw new Error('This is not a TimeSeries Path backup file.');
      state = Object.assign(DEFAULTS(), d.data);
      state.settings = Object.assign(DEFAULTS().settings, d.data.settings || {});
      writeNow(); emit('import');
    },
    reset: function () { state = DEFAULTS(); writeNow(); emit('import'); }
  };

  load();
})(window.TSP = window.TSP || {});
