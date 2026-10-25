/* pages/workspace.js - the problem workspace: description / hints / solution / submissions on the left,
   Python editor and console on the right. Also used (embedded) by the Mock OA page. */
(function (T) {
  'use strict';
  var U = T.U, h = U.h, S = T.S, C = T.C, J = T.Judge;
  T.pages = T.pages || {};

  var XP = { Easy: 20, Medium: 40, Hard: 70 };

  /** Build the tests source for a run with edited or added cases. */
  function testsWithCases(p, cases) {
    var list = cases.map(function (c) {
      var o = { name: c.name, call: c.call, visible: true };
      if (c.expected != null && !c.changed) o.expected = c.expected;
      if (c.tol != null) o.tol = c.tol;
      if (c.check_index != null) o.check_index = c.check_index;
      return o;
    });
    return p.tests + '\n\nimport json as _tsp_json\nCASES = _tsp_json.loads(' + JSON.stringify(JSON.stringify(list)) + ')\n';
  }

  function sumMs(results) { return (results || []).reduce(function (a, r) { return a + (r.ms || 0); }, 0); }

  /** Result view: verdict + per-case details. */
  function resultView(res, opts) {
    opts = opts || {};
    var ok = res.status === 'Accepted';
    var box = h('div.result');
    box.appendChild(h('div.verdict.' + (ok ? 'ok' : 'bad'),
      h('span.v-title', ok ? (opts.mode === 'submit' ? 'Accepted' : 'All sample cases passed') : res.status),
      h('span.v-sub', res.passed + ' / ' + res.total + ' cases passed' + (res.results && res.results.length ? ' · ' + Math.round(sumMs(res.results)) + ' ms' : ''))));
    if (res.error) box.appendChild(h('pre.err', res.error));
    var firstBad = true;
    (res.results || []).forEach(function (r) {
      var d = h('details.case' + (r.ok ? '.ok' : '.bad'), { open: !r.ok && firstBad });
      if (!r.ok) firstBad = false;
      d.appendChild(h('summary', h('span.case-ico', r.ok ? U.icon('check', 14) : U.icon('x', 14)), h('span.case-name', r.name), h('span.muted.small', (r.ms || 0) + ' ms')));
      var inner = h('div.case-body');
      function field(label, text, cls) { if (text != null && text !== '') inner.appendChild(h('div.field', h('span.fl', label), h('pre' + (cls ? '.' + cls : ''), String(text)))); }
      field('Input', r.call);
      if (r.error) field('Error', r.error, 'err');
      else { field('Your output', r.got); field('Expected', r.expected); }
      if (r.msg && !r.ok) field('Why it differs', r.msg);
      field('Printed output', r.stdout);
      d.appendChild(inner); box.appendChild(d);
    });
    return box;
  }

  /**
   * Mount a workspace into `host`. opts: { mock: {onSubmit(res)} | null, onTitle }
   * Returns { destroy() }.
   */
  function mount(host, slug, opts) {
    opts = opts || {};
    var p = C.problems[slug], mock = opts.mock || null;
    var PS = S.problem(slug);
    var code = PS.code != null ? PS.code : p.starter;
    var running = false, lastResult = null;
    var cases = p.visible.map(function (c) { return Object.assign({ orig: c.call }, c); });
    var activeCase = 0, consoleTab = 'cases', leftTab = 'desc';
    var disposers = [];
    J.boot();

    var editor = T.Editor.create({
      value: code, label: 'Python code for ' + p.title,
      onChange: function (v) { code = v; saveSoon(); },
      onRun: function () { run('run'); }, onSubmit: function () { run('submit'); }
    });
    var saveSoon = U.debounce(function () { S.quiet(function () { S.problem(slug).code = code; }); }, 400);

    /* ---- layout ---- */
    var left = h('section.ws-left', { 'aria-label': 'Problem' });
    var right = h('section.ws-right', { 'aria-label': 'Code' });
    var vsplit = h('div.ws-vsplit', { role: 'separator', 'aria-orientation': 'vertical', 'aria-label': 'Resize panels', tabindex: 0 });
    var ws = h('div.ws', left, vsplit, right);
    var mobileTab = 'problem';
    var switcher = h('div.ws-switch', { role: 'tablist' },
      h('button', { type: 'button', role: 'tab', 'aria-selected': 'true', onclick: function () { setMobile('problem'); } }, 'Problem'),
      h('button', { type: 'button', role: 'tab', 'aria-selected': 'false', onclick: function () { setMobile('code'); } }, 'Code'));
    function setMobile(t) {
      mobileTab = t; ws.setAttribute('data-mobile', t);
      switcher.querySelectorAll('button').forEach(function (b, i) { b.setAttribute('aria-selected', (i === 0) === (t === 'problem')); });
      if (t === 'code') editor.refresh();
    }
    ws.setAttribute('data-mobile', 'problem');
    host.append(switcher, ws);
    var split = S.get().settings.split || 46;
    function applySplit() { ws.style.setProperty('--split', split + '%'); }
    applySplit();
    vsplit.addEventListener('pointerdown', function (e) {
      e.preventDefault(); vsplit.setPointerCapture(e.pointerId); ws.classList.add('dragging');
      function mv(ev) {
        var r = ws.getBoundingClientRect();
        split = Math.min(75, Math.max(25, (ev.clientX - r.left) / r.width * 100)); applySplit();
      }
      function up() {
        vsplit.removeEventListener('pointermove', mv); vsplit.removeEventListener('pointerup', up); ws.classList.remove('dragging');
        S.quiet(function (s) { s.settings.split = Math.round(split); });
      }
      vsplit.addEventListener('pointermove', mv); vsplit.addEventListener('pointerup', up);
    });
    vsplit.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') split = Math.max(25, split - 3); else if (e.key === 'ArrowRight') split = Math.min(75, split + 3); else return;
      e.preventDefault(); applySplit(); S.quiet(function (s) { s.settings.split = Math.round(split); });
    });

    /* ---- left pane ---- */
    var tabsEl = h('div.tabs', { role: 'tablist' });
    var leftBody = h('div.ws-left-body');
    left.append(tabsEl, leftBody);
    var TABS = mock ? [['desc', 'Description']] : [['desc', 'Description'], ['hints', 'Hints'], ['sol', 'Solution'], ['subs', 'Submissions']];
    function drawTabs() {
      U.clear(tabsEl);
      TABS.forEach(function (t) {
        tabsEl.appendChild(h('button.tab' + (leftTab === t[0] ? '.on' : ''), { type: 'button', role: 'tab', 'aria-selected': leftTab === t[0], onclick: function () { leftTab = t[0]; drawLeft(); } },
          t[1], t[0] === 'sol' && !solutionUnlocked() ? U.icon('lock', 13) : null, t[0] === 'subs' && PS.subs.length ? h('span.badge-count', String(PS.subs.length)) : null));
      });
    }
    function solutionUnlocked() { return PS.solutionOpen || PS.solved || PS.subs.length >= 1 || PS.runs >= 3; }

    function drawLeft() {
      drawTabs(); U.clear(leftBody);
      if (leftTab === 'desc') {
        var stage = C.stageById[p.stage], lesson = C.lessons[p.lesson];
        leftBody.appendChild(h('h1.ws-title', p.title));
        leftBody.appendChild(h('div.meta', h('span.diff.' + p.difficulty.toLowerCase(), p.difficulty), h('a.chip.stagechip', { href: '#/', style: { '--stage': stage.color } }, stage.id.toUpperCase() + ' ' + stage.title),
          h('span.chip', p.type), p.packages.map(function (k) { return h('span.tag.pkg', k); }),
          p.skills.map(function (s) { return h('span.skill', 'skill:' + s); }), p.tags.map(function (t) { return h('span.tag', t); })));
        var md = h('div.md.prose', { html: p.descriptionHtml });
        leftBody.appendChild(md); T.Md.hydrate(md, {});
        if (lesson && !mock) leftBody.appendChild(h('p.small.muted', 'From the lesson: ', h('a', { href: '#/lesson/' + lesson.id }, lesson.title)));
      } else if (leftTab === 'hints') {
        leftBody.appendChild(h('p.muted', 'Open hints one at a time. Try for a few minutes between hints.'));
        var shown = PS.hints || 0;
        for (var i = 0; i < Math.min(shown, p.hints.length); i++) {
          var hd = h('div.hint', h('b', 'Hint ' + (i + 1)), h('div.md', { html: p.hints[i] }));
          leftBody.appendChild(hd); T.Md.hydrate(hd, {});
        }
        if (!p.hints.length) leftBody.appendChild(h('p', 'This problem has no hints.'));
        else if (shown < p.hints.length) leftBody.appendChild(h('button.btn', { type: 'button', onclick: function () {
          S.update(function () { S.problem(slug).hints = shown + 1; }); drawLeft();
        } }, 'Show hint ' + (shown + 1) + ' of ' + p.hints.length));
        else leftBody.appendChild(h('p.muted', 'That was the last hint.'));
        if (T.AI && !mock) leftBody.appendChild(T.AI.slot(function () {
          return h('div.ai-tools', h('p.muted.small', 'Still stuck? The AI tutor can give one more hint.'),
            h('button.btn.sm', { type: 'button', onclick: function (e) { T.AI.ask(T.AI.PROMPTS.hint, { display: 'Give me another hint', opener: e.currentTarget }); } }, U.icon('spark', 14), ' Give me another hint'));
        }));
      } else if (leftTab === 'sol') {
        if (!solutionUnlocked()) {
          leftBody.appendChild(h('div.lock-card', U.icon('lock', 28), h('h3', 'The solution is locked'),
            h('p', 'Try the problem first. It opens after your first submission or 3 runs. You have run it ' + PS.runs + ' time' + (PS.runs === 1 ? '' : 's') + '.'),
            h('button.btn', { type: 'button', onclick: function () {
              if (window.confirm('Open the solution now? You learn more if you try first.')) { S.update(function () { S.problem(slug).solutionOpen = true; }); drawLeft(); }
            } }, 'Show it anyway')));
        } else {
          var box = h('div.md.prose', { html: p.solutionHtml });
          leftBody.appendChild(h('h2', 'Solution'));
          leftBody.appendChild(h('div.codeblock',
            h('div.codeblock-head', h('span.cb-label', 'Reference code'), h('span.cb-tools', h('button.btn.sm', { type: 'button', onclick: function () { U.copyText(p.solution); U.toast('Copied'); } }, 'Copy'))),
            h('pre.code-view', { tabindex: 0, html: T.Editor.highlight(p.solution) })));
          leftBody.appendChild(box); T.Md.hydrate(box, {});
        }
      } else {
        if (!PS.subs.length) leftBody.appendChild(h('p.muted', 'No submissions yet. Press Submit to test all cases, including hidden ones.'));
        else {
          var tb = h('tbody');
          PS.subs.forEach(function (s) {
            tb.appendChild(h('tr', h('td', h('span.verdict-text.' + (s.status === 'Accepted' ? 'ok' : 'bad'), s.status)), h('td', s.passed + '/' + s.total), h('td', Math.round(s.ms || 0) + ' ms'), h('td.muted', U.timeAgo(s.t)),
              h('td', h('button.btn.sm', { type: 'button', onclick: function () { editor.setValue(s.code); code = s.code; saveSoon(); U.toast('Loaded into the editor'); setMobile('code'); } }, 'Load'))));
          });
          leftBody.appendChild(h('div.table-wrap', h('table.subs', h('thead', h('tr', h('th', 'Result'), h('th', 'Cases'), h('th', 'Time'), h('th', 'When'), h('th', ''))), tb)));
        }
      }
    }

    /* ---- right pane ---- */
    var runBtn = h('button.btn', { type: 'button', onclick: function () { run('run'); }, title: 'Run sample cases (Ctrl/Cmd + Enter)' }, U.icon('play', 14), ' Run');
    var submitBtn = h('button.btn.primary', { type: 'button', onclick: function () { run('submit'); }, title: 'Submit all cases (Ctrl/Cmd + \')' }, 'Submit');
    var toolbar = h('div.ws-toolbar',
      h('span.lang', 'Python'), J.chip(),
      h('span.grow'),
      h('button.btn.sm', { type: 'button', onclick: function () {
        if (code !== p.starter && !window.confirm('Reset your code to the starter code?')) return;
        editor.setValue(p.starter); code = p.starter; saveSoon();
      } }, 'Reset'), runBtn, submitBtn);
    var edHost = h('div.ws-editor', editor.el, h('p.ed-hint', 'Tip: press Esc, then Tab, to leave the editor. Run: Ctrl/Cmd+Enter. Submit: Ctrl/Cmd+\'.'));
    var hsplit = h('div.ws-hsplit', { role: 'separator', 'aria-orientation': 'horizontal', 'aria-label': 'Resize editor and console', tabindex: 0 });
    var consoleTabs = h('div.tabs.small', { role: 'tablist' });
    var consoleBody = h('div.console-body', { 'aria-live': 'polite' });
    var consoleEl = h('div.ws-console', consoleTabs, consoleBody);
    right.append(toolbar, edHost, hsplit, consoleEl);
    var consoleH = 260;
    consoleEl.style.height = consoleH + 'px';
    hsplit.addEventListener('pointerdown', function (e) {
      e.preventDefault(); hsplit.setPointerCapture(e.pointerId);
      var startY = e.clientY, startH = consoleEl.offsetHeight;
      function mv(ev) { consoleH = Math.min(right.clientHeight - 160, Math.max(90, startH + (startY - ev.clientY))); consoleEl.style.height = consoleH + 'px'; }
      function up() { hsplit.removeEventListener('pointermove', mv); hsplit.removeEventListener('pointerup', up); }
      hsplit.addEventListener('pointermove', mv); hsplit.addEventListener('pointerup', up);
    });

    function drawConsoleTabs() {
      U.clear(consoleTabs);
      [['cases', 'Test cases'], ['result', 'Result']].forEach(function (t) {
        consoleTabs.appendChild(h('button.tab' + (consoleTab === t[0] ? '.on' : ''), { type: 'button', role: 'tab', 'aria-selected': consoleTab === t[0], onclick: function () { consoleTab = t[0]; drawConsole(); } }, t[1]));
      });
    }
    function drawConsole() {
      drawConsoleTabs(); U.clear(consoleBody);
      if (consoleTab === 'cases') drawCases(); else drawResult();
    }
    function drawCases() {
      var bar = h('div.case-tabs');
      cases.forEach(function (c, i) {
        bar.appendChild(h('button.case-tab' + (i === activeCase ? '.on' : ''), { type: 'button', onclick: function () { activeCase = i; drawConsole(); } }, c.custom ? 'Custom ' + (i - p.visible.length + 1) : 'Case ' + (i + 1)));
      });
      bar.appendChild(h('button.case-tab.add', { type: 'button', 'aria-label': 'Add a custom case', title: 'Add your own test call', onclick: function () {
        cases.push({ name: 'Custom', call: cases[0] ? cases[0].call : '', custom: true, changed: true }); activeCase = cases.length - 1; drawConsole();
      } }, '+'));
      consoleBody.appendChild(bar);
      var c = cases[activeCase];
      if (!c) { consoleBody.appendChild(h('p.muted', 'No sample cases.')); return; }
      var ta = h('textarea.input.mono', { rows: Math.min(8, Math.max(2, c.call.split('\n').length)), 'aria-label': 'Test call', spellcheck: 'false',
        oninput: function () { c.call = ta.value; c.changed = c.custom || ta.value !== c.orig; hint.hidden = !c.changed; } });
      ta.value = c.call;
      var hint = h('p.small.muted', { hidden: !c.changed }, 'You changed this call. Run uses the reference solution to find the expected answer.');
      consoleBody.appendChild(h('div.field', h('span.fl', c.name || 'Call'), ta, hint));
      if (c.expected && !c.changed) consoleBody.appendChild(h('div.field', h('span.fl', 'Expected'), h('pre', c.expected)));
      if (!c.custom && !c.expected && !c.changed) consoleBody.appendChild(h('p.small.muted', 'The expected value comes from the reference solution.'));
      var row = h('div.row');
      if (c.changed && !c.custom) row.appendChild(h('button.btn.sm', { type: 'button', onclick: function () { c.call = c.orig; c.changed = false; drawConsole(); } }, 'Reset call'));
      if (c.custom) row.appendChild(h('button.btn.sm', { type: 'button', onclick: function () { cases.splice(activeCase, 1); activeCase = 0; drawConsole(); } }, 'Remove case'));
      consoleBody.appendChild(row);
    }
    function drawResult() {
      if (running) { consoleBody.appendChild(h('div.running', h('i.spin'), h('span', runningMsg))); return; }
      if (!lastResult) { consoleBody.appendChild(h('p.muted', 'Press Run to test the sample cases, or Submit to test everything.')); return; }
      if (lastResult.hidden) {
        consoleBody.appendChild(h('div.verdict.neutral', h('span.v-title', 'Answer saved'), h('span.v-sub', 'Verdicts are hidden until you finish the test.')));
        return;
      }
      var v = resultView(lastResult.res, { mode: lastResult.mode });
      if (lastResult.res.status === 'Accepted' && lastResult.mode === 'submit' && !mock) {
        var l = C.lessons[p.lesson], nxt = l && l.problems[l.problems.indexOf(slug) + 1];
        v.appendChild(h('div.row.congrats', h('b', 'Nice work!'), nxt ? h('a.btn.sm.primary', { href: '#/problem/' + nxt }, 'Next problem') : null,
          h('a.btn.sm', { href: '#/problems' }, 'All problems'), l ? h('a.btn.sm', { href: '#/lesson/' + l.id }, 'Back to the lesson') : null));
      }
      consoleBody.appendChild(v);
      if (T.AI && !mock) {
        var okRes = lastResult.res.status === 'Accepted';
        consoleBody.appendChild(T.AI.slot(function () {
          var row = h('div.ai-tools.row');
          if (!okRes) row.appendChild(h('button.btn.sm', { type: 'button', onclick: function (e) { T.AI.ask(T.AI.PROMPTS.error, { display: 'Explain my error', opener: e.currentTarget }); } }, U.icon('spark', 14), ' Explain my error'));
          if (okRes && lastResult.mode === 'submit') row.appendChild(h('button.btn.sm', { type: 'button', onclick: function (e) { T.AI.ask(T.AI.PROMPTS.review, { display: 'Review my code like an interviewer', opener: e.currentTarget }); } }, U.icon('spark', 14), ' Review my code like an interviewer'));
          return row.childNodes.length ? row : null;
        }));
      }
    }

    var runningMsg = 'Running…';
    function setBusy(b) { running = b; runBtn.disabled = b; submitBtn.disabled = b; }

    async function run(mode) {
      if (running) return;
      var edited = mode === 'run' && cases.some(function (c) { return c.changed; });
      var useCases = edited ? cases.filter(function (c) { return c.call.trim(); }) : null;
      var job = { code: code, reference: p.solution, tests: edited ? testsWithCases(p, useCases) : p.tests, mode: mode };
      setBusy(true); runningMsg = J.state().state === 'ready' ? 'Running…' : 'Starting Python… the first run loads about 12 MB. After that it is fast.';
      consoleTab = 'result'; lastResult = null; drawConsole();
      if (window.matchMedia('(max-width: 860px)').matches) { /* stay on the code tab so the console is visible */ }
      S.update(function () { var s = S.problem(slug); if (mode === 'run') s.runs++; S.touch(1); }, 'quiet');
      var total = edited ? useCases.length : (mode === 'run' ? p.visible.length : p.nCases);
      var res;
      try {
        res = await J.run(job, { packages: p.packages, total: total,
          onStatus: function (m) { runningMsg = m; if (running && consoleTab === 'result') { var s = consoleBody.querySelector('.running span'); if (s) s.textContent = m; } },
          onCase: function () { runningMsg = 'Running…'; } });
      } catch (e) {
        res = { status: 'Runtime Error', passed: 0, total: total, results: [], error: 'The Python engine reported a problem: ' + e.message };
      }
      setBusy(false);
      lastResult = { res: res, mode: mode, hidden: !!(mock && mode === 'submit') };
      if (mode === 'submit') {
        S.update(function () {
          var s = S.problem(slug);
          s.submits++;
          s.subs.unshift({ t: Date.now(), status: res.status, passed: res.passed, total: res.total, ms: sumMs(res.results), code: code });
          s.subs = s.subs.slice(0, 30);
          if (res.status === 'Accepted' && !s.solved && !mock) { s.solved = Date.now(); S.get().xp += XP[p.difficulty] || 20; U.toast('+' + (XP[p.difficulty] || 20) + ' XP · problem solved', 'xp'); }
          S.touch(2);
        }, 'problem');
        if (mock && mock.onSubmit) mock.onSubmit(res);
      }
      if (leftTab === 'sol' || leftTab === 'subs') drawLeft(); else drawTabs();
      if (document.body.contains(consoleBody)) { consoleTab = 'result'; drawConsole(); }
      if (T.AI) T.AI.touch();
    }

    drawLeft(); drawConsole();
    if (T.AI) {
      if (mock) T.AI.setContext({ kind: 'mock-oa', key: 'mock-oa', title: 'Mock OA', blocked: 'The AI tutor is off during a mock test.', get: function () { return ''; } });
      else T.AI.setContext({
        kind: 'problem', key: 'problem:' + slug, title: p.title, tools: true,
        sub: function () { return p.difficulty + (PS.solved ? ' · solved' : ''); },
        get: aiContext,
        quick: function () {
          var AI = T.AI, q = [{ label: 'What is it asking?', prompt: AI.PROMPTS.asking }, { label: 'Give me another hint', prompt: AI.PROMPTS.hint }];
          if (lastResult && !lastResult.hidden && lastResult.res.status !== 'Accepted') q.unshift({ label: 'Explain my error', prompt: AI.PROMPTS.error });
          if (PS.solved || (lastResult && lastResult.res.status === 'Accepted' && lastResult.mode === 'submit')) q.push({ label: 'Review my code like an interviewer', prompt: AI.PROMPTS.review });
          if (solutionUnlocked()) q.push({ label: 'Show me a solution', prompt: 'Please show me a full solution and explain it in simple steps.', solution: true });
          return q;
        }
      });
    }
    /** What the tutor may see: problem text, hints already shown, the learner's code and the last result. */
    function aiContext() {
      var AI = T.AI, t = 'PROBLEM: ' + p.title + ' (' + p.difficulty + ', ' + p.type + ')\n\nDESCRIPTION:\n' + AI.clip(AI.text(p.descriptionHtml), 3500);
      var shown = Math.min(PS.hints || 0, p.hints.length);
      t += '\n\nSTATIC HINTS: ' + shown + ' of ' + p.hints.length + ' shown to the learner.';
      if (shown) t += '\n' + p.hints.slice(0, shown).map(function (x, i) { return 'Hint ' + (i + 1) + ': ' + AI.clip(AI.text(x), 600); }).join('\n');
      t += '\nSolution unlocked for the learner: ' + (solutionUnlocked() ? 'yes' : 'no') + '. Already solved: ' + (PS.solved ? 'yes' : 'no') + '.';
      t += '\n\nLEARNER CODE:\n```python\n' + AI.clip(code, 8000) + '\n```';
      if (lastResult && !lastResult.hidden && lastResult.res) {
        var r = lastResult.res;
        t += '\n\nLAST ' + (lastResult.mode === 'submit' ? 'SUBMIT' : 'RUN') + ': ' + r.status + ', ' + r.passed + ' of ' + r.total + ' cases passed.';
        if (r.error) t += '\nError: ' + AI.clip(r.error, 1200);
        var bad = (r.results || []).filter(function (x) { return !x.ok; })[0];
        if (bad) {
          t += '\nFIRST FAILING CASE: ' + bad.name + '\nInput: ' + AI.clip(bad.call, 800);
          if (bad.error) t += '\nError / traceback:\n' + AI.clip(bad.error, 1500);
          else t += '\nLearner output (got): ' + AI.clip(bad.got, 800) + '\nExpected: ' + AI.clip(bad.expected, 800);
          if (bad.msg) t += '\nChecker message: ' + AI.clip(bad.msg, 400);
          if (bad.stdout) t += '\nPrinted by learner code: ' + AI.clip(bad.stdout, 500);
        }
      } else t += '\n\nThe learner has not run the code yet.';
      return t;
    }
    return { destroy: function () { disposers.forEach(function (d) { d(); }); saveNow(); }, setMobile: setMobile };
    function saveNow() { S.quiet(function () { S.problem(slug).code = code; }); }
  }

  T.Workspace = { mount: mount, resultView: resultView };

  T.pages.problem = {
    render: function (el, params) {
      var p = C.problems[params.slug];
      if (!p) { el.appendChild(h('div.wrap', h('h1', 'Problem not found'), h('a.btn', { href: '#/problems' }, 'All problems'))); return; }
      T.setTitle(p.title);
      el.classList.add('page-workspace');
      var lessonProblems = C.lessons[p.lesson].problems, idx = lessonProblems.indexOf(p.slug);
      var bar = h('div.ws-bar',
        h('a.btn.sm', { href: '#/problems' }, '← Problems'),
        h('span.ws-bar-title', p.title),
        h('span.grow'),
        idx > 0 ? h('a.btn.sm', { href: '#/problem/' + lessonProblems[idx - 1] }, 'Previous') : null,
        idx >= 0 && idx < lessonProblems.length - 1 ? h('a.btn.sm', { href: '#/problem/' + lessonProblems[idx + 1] }, 'Next') : null);
      var host = h('div.ws-host');
      el.append(bar, host);
      var w = mount(host, p.slug, {});
      return function () { w.destroy(); el.classList.remove('page-workspace'); };
    }
  };
})(window.TSP = window.TSP || {});
