/* pages/ai-drawer.js - the AI tutor drawer: chat for the current page, quick buttons, drill "mock interviewer",
   interview-prep chat. Right side panel on desktop, bottom sheet on phones. Built only when first opened. */
(function (T) {
  'use strict';
  var AI = T.AI, U = T.U, h = U.h, S = T.S, C = T.C;
  var HKEY = 'tsp:ai:v1';
  var MAX_TURNS = 16, MAX_STORE_TURNS = 24, MAX_KEYS = 24;

  var el = null, P = {};                       // P = parts of the drawer
  var st = { open: false, busy: false, run: null, opener: null, stick: true, shownKey: null };
  var hist = {}, flows = {};

  /* ------------------------------------------------------------ best-effort storage */
  try {
    var saved = JSON.parse(localStorage.getItem(HKEY) || 'null');
    if (saved && typeof saved === 'object') { hist = saved.h || {}; flows = saved.f || {}; }
  } catch (e) { hist = {}; flows = {}; }
  function save() {
    try {
      var keys = Object.keys(hist);
      if (keys.length > MAX_KEYS) keys.slice(0, keys.length - MAX_KEYS).forEach(function (k) { delete hist[k]; });
      var out = {};
      Object.keys(hist).forEach(function (k) {
        out[k] = hist[k].slice(-MAX_STORE_TURNS).map(function (t) {
          var c = Object.assign({}, t); if (typeof c.content === 'string' && c.content.length > 6000) c.content = c.content.slice(0, 6000); return c;
        });
      });
      localStorage.setItem(HKEY, JSON.stringify({ h: out, f: flows }));
    } catch (e) { /* storage blocked or full: memory only */ }
  }

  function ctx() { return AI.context(); }
  function turnsFor(key) { return hist[key] || (hist[key] = []); }

  /* ------------------------------------------------------------ build the drawer */
  function build() {
    if (el) return;
    P.title = h('h2.ai-title', { id: 'ai-title' }, U.icon('spark', 18), ' AI tutor');
    P.sub = h('p.ai-sub');
    P.clear = h('button.btn.sm', { type: 'button', onclick: clearChat }, 'Clear chat');
    P.close = h('button.icon-btn', { type: 'button', 'aria-label': 'Close the AI tutor', onclick: function () { close(); } }, U.icon('x', 20));
    P.flow = h('div.ai-flow');
    P.log = h('div.ai-log', { role: 'region', 'aria-label': 'Conversation', tabindex: 0 });
    P.quick = h('div.ai-quick', { role: 'group', 'aria-label': 'Quick questions' });
    P.input = h('textarea.input.ai-input', { rows: 2, 'aria-label': 'Your message to the AI tutor', placeholder: 'Ask a question…', maxlength: 4000,
      onkeydown: function (e) { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); submit(); } },
      oninput: syncComposer });
    P.send = h('button.btn.primary', { type: 'submit' }, 'Send');
    P.stop = h('button.btn', { type: 'button', hidden: true, onclick: function () { if (st.run) st.run.abort(); } }, 'Stop');
    P.form = h('form.ai-composer', { onsubmit: function (e) { e.preventDefault(); submit(); } }, P.input, h('div.ai-composer-btns', P.send, P.stop));
    P.foot = h('p.ai-foot', 'AI can make mistakes. It uses your own Claude account. Enter sends, Shift+Enter adds a line.');
    el = h('aside.ai-drawer', { id: 'ai-drawer', role: 'dialog', 'aria-labelledby': 'ai-title', hidden: true, tabindex: -1,
      onkeydown: function (e) { if (e.key === 'Escape') { e.stopPropagation(); close(); } } },
      h('header.ai-head', h('div.ai-head-text', P.title, P.sub), h('div.ai-head-btns', P.clear, P.close)),
      P.flow, P.log, P.quick, P.form, P.foot);
    P.backdrop = h('div.ai-backdrop', { hidden: true, onclick: function () { close(); } });
    document.body.append(P.backdrop, el);
    P.log.addEventListener('scroll', function () { st.stick = P.log.scrollHeight - P.log.scrollTop - P.log.clientHeight < 40; });
  }

  function isMobile() { return window.matchMedia && matchMedia('(max-width: 760px)').matches; }
  function setInert(on) {
    ['main', 'topbar'].forEach(function (id) { var n = document.getElementById(id); if (n) { if (on) n.setAttribute('inert', ''); else n.removeAttribute('inert'); } });
  }

  /* ------------------------------------------------------------ open / close */
  function open(o) {
    o = o || {};
    if (!AI.active()) return;
    var c = ctx(); if (c.blocked) return;
    build();
    st.opener = o.opener || document.activeElement || null;
    var wasOpen = st.open;
    st.open = true;
    el.hidden = false; el.removeAttribute('inert');
    var mobile = isMobile();
    el.setAttribute('aria-modal', mobile ? 'true' : 'false');
    P.backdrop.hidden = !mobile;
    if (mobile) setInert(true);
    document.body.classList.add('ai-open');
    renderAll();
    markChips();
    if (!wasOpen) { if (mobile) el.focus(); else P.input.focus(); }
    if (o.send) send(o.send, { display: o.display });
  }
  function close() {
    if (!st.open) return;
    st.open = false;
    el.hidden = true; el.setAttribute('inert', ''); P.backdrop.hidden = true;
    setInert(false);
    document.body.classList.remove('ai-open');
    markChips();
    var back = st.opener && document.body.contains(st.opener) && !st.opener.disabled ? st.opener : document.querySelector('[data-ai-chip]');
    if (back && back.focus) back.focus();
    st.opener = null;
  }
  function toggle(opener) { if (st.open) close(); else open({ opener: opener }); }
  function markChips() {
    document.querySelectorAll('[data-ai-chip]').forEach(function (b) { b.setAttribute('aria-expanded', String(st.open)); });
  }

  AI.subscribe('ctx', function () {
    if (!el) return;
    var c = ctx();
    if (st.open && c.blocked) { close(); return; }
    if (st.open) renderAll();
  });
  AI.subscribe('route', function () { if (st.open && isMobile()) close(); });
  document.addEventListener('keydown', function (e) {      // Esc also works when focus fell back to the page body
    if (e.key === 'Escape' && st.open && (document.activeElement === document.body || el.contains(document.activeElement))) close();
  });
  AI.subscribe('state', function () { if (st.open && !AI.active()) close(); });
  window.addEventListener('resize', U.debounce(function () {
    if (!st.open) return;
    var m = isMobile(); el.setAttribute('aria-modal', m ? 'true' : 'false'); P.backdrop.hidden = !m; setInert(m);
  }, 150));

  /* ------------------------------------------------------------ rendering */
  function curKey() { return ctx().key || 'general'; }

  function renderAll() {
    var c = ctx(), key = curKey();
    st.shownKey = key;
    var sub = '';
    try { sub = c.sub ? c.sub() : ''; } catch (e) { sub = ''; }
    P.sub.textContent = (c.title ? c.title : '') + (sub ? ' · ' + sub : '');
    renderLog();
    renderFlow();
    renderQuick();
    syncComposer();
  }

  function bubble(role) {
    var b = h('div.ai-msg.' + role);
    if (role === 'assistant') { b.setAttribute('aria-live', 'polite'); b.setAttribute('aria-busy', 'false'); }
    return b;
  }
  function renderTurn(t) {
    if (t.hidden) return null;
    if (t.role === 'user') { var u = bubble('user'); u.appendChild(h('p', t.show || t.content)); return u; }
    if (t.role === 'assistant') { var a = bubble('assistant'); a.appendChild(AI.md(t.content)); if (t.stopped) a.appendChild(h('p.ai-note', 'Stopped.')); return a; }
    if (t.role === 'tool') return toolNote(t.code, t.out);
    if (t.role === 'result') return resultCard(t.data);
    return null;
  }
  function toolNote(code, out) {
    return h('details.ai-tool', h('summary', 'The tutor ran a small piece of Python'), h('pre.ai-code', h('code', code)), out ? h('pre.ai-code.out', h('code', out)) : null);
  }
  function welcome() {
    var c = ctx(), t;
    if (c.kind === 'lesson') t = 'Hi! Ask me about this lesson. I explain in simple words and ask you small questions.';
    else if (c.kind === 'problem') t = 'Hi! I help you with this problem. I give hints and ask questions. I do not give the full solution unless you ask for it.';
    else if (c.kind === 'drill') t = 'Hi! Write your answers first. Then I can be your interviewer: three follow-up questions and a grade.';
    else if (c.kind === 'interview') t = 'Choose a level and a topic. I will ask one interview question at a time.';
    else if (c.kind === 'playground') t = 'Hi! Ask me what your code does or why it fails. I can also run a tiny test for you.';
    else t = 'Hi! I am your study coach. Ask me anything about time series, or use a quick question below.';
    return h('div.ai-welcome', h('p', t));
  }
  function renderLog() {
    U.clear(P.log);
    var turns = turnsFor(curKey()), any = false;
    turns.forEach(function (t) { var n = renderTurn(t); if (n) { P.log.appendChild(n); any = true; } });
    if (!any) P.log.appendChild(welcome());
    P.log.scrollTop = P.log.scrollHeight; st.stick = true;
  }
  function scrollDown() { if (st.stick) P.log.scrollTop = P.log.scrollHeight; }

  function renderQuick() {
    U.clear(P.quick);
    var c = ctx(), list = [];
    try { list = (c.quick && c.quick()) || []; } catch (e) { list = []; }
    var f = flows[curKey()];
    if (c.kind === 'interview') {
      list = f ? [
        { label: 'Next question', prompt: 'Next question, please.' },
        { label: 'Give me a hint', prompt: 'I am stuck. Give me a small hint, not the answer.' },
        { label: 'End and give feedback', prompt: 'Please stop here. Give me a short summary: my strengths and 2 things to practise.' }] : [];
    } else if (f && f.type === 'drill' && f.phase === 'done') {
      list = [{ label: 'Interview me again', action: function () { startDrill(curKey()); }, primary: true }, { label: 'What should I improve first?', prompt: 'Look at the interview result above. What should I improve first? Give me one small step, not the full answer.' }];
    } else if (f && f.type === 'drill') {
      list = [{ label: 'Repeat the question', prompt: 'Please say your last question again in simpler words.' }];
      if (f.qa.length) list.push({ label: 'Grade me now', action: function () { gradeDrill(curKey()); } });
    } else if (c.kind === 'drill' && c.drill) {
      list = list.concat([{ label: 'Start the AI interviewer', action: function () { startDrill(curKey()); }, primary: true }]);
    }
    if (c.kind !== 'interview' && c.kind !== 'general' && !(f && f.type === 'drill' && f.phase !== 'done')) list.push({ label: 'Mock interview', action: function () { AI.openInterview(); } });
    list.forEach(function (q) {
      var b = h('button.ai-q' + (q.primary ? '.primary' : ''), { type: 'button', disabled: st.busy, onclick: function () {
        keepFocus();                                   // the button is rebuilt later: move focus somewhere stable first
        if (q.action) q.action();
        else if (q.solution) send('[Show me a solution] ' + q.prompt, { display: q.label });
        else send(q.prompt, { display: q.label });
      } }, q.label);
      P.quick.appendChild(b);
    });
    P.quick.hidden = !list.length;
  }

  function keepFocus() { if (isMobile()) P.log.focus(); else P.input.focus(); }

  function syncComposer() {
    var f = flows[curKey()], c = ctx();
    var need = c.kind === 'interview' && !f;           // interview setup first
    P.form.hidden = need && !turnsFor(curKey()).length;
    P.send.disabled = st.busy || !P.input.value.trim();
    P.send.hidden = st.busy; P.stop.hidden = !st.busy;
    P.input.disabled = false;
    var ph = 'Ask a question…';
    if (f && f.type === 'drill' && f.phase === 'answering') ph = 'Type your answer to question ' + (f.qa.length + 1) + '…';
    else if (c.kind === 'interview') ph = 'Type your answer…';
    P.input.placeholder = ph;
    P.clear.hidden = !turnsFor(curKey()).length && !f;
    var qs = P.quick.querySelectorAll('button'); qs.forEach(function (b) { b.disabled = st.busy; });
  }

  /* ------------------------------------------------------------ chat engine */
  function modeExtra(key) {
    var f = flows[key], c = ctx();
    if (c.kind === 'interview' && f) {
      var lvl = { junior: 'junior (fundamentals, simple pandas and metrics)', senior: 'senior (trade-offs, evaluation, production, debugging)', staff: 'staff (ambiguous framing, system design, ROI, influence)' }[f.level] || f.level;
      return '\n\nMODE: MOCK INTERVIEW. You are the interviewer for a ' + lvl + ' Time Series / Forecasting ML engineer role. Topic: ' + f.topic +
        '. Ask ONE question at a time (40 words or fewer). After the learner answers, give short feedback (what was good, what to add; 60 words or fewer), then ask the next question. Raise or lower difficulty by how they do. Do not lecture. After about 5 questions, or when asked to stop, give a short summary: strengths and 2 things to practise. Do not reveal full model answers unless asked.';
    }
    if (f && f.type === 'drill' && f.phase !== 'done') {
      return '\n\nMODE: MOCK INTERVIEWER for a design drill. The learner wrote written answers (see PAGE CONTEXT). You ask exactly ONE short follow-up question at a time (40 words or fewer), aimed at a weak or missing part of the written answer. Do not grade yet. Do not give the answer. When the learner answers, give one short sentence of feedback (20 words or fewer) and then ask the next question, as the hidden instruction in brackets says.';
    }
    return '';
  }

  function buildInput(key) {
    var c = ctx();
    var lead = AI.rules() + modeExtra(key) + '\n\nPAGE CONTEXT (' + (c.title || 'page') + '):\n' + AI.contextText();
    var turns = turnsFor(key).filter(function (t) { return (t.role === 'user' || t.role === 'assistant') && t.content; });
    turns = turns.slice(-MAX_TURNS);
    var total = lead.length;
    var kept = [];
    for (var i = turns.length - 1; i >= 0; i--) {                       // newest first; drop the oldest when too long
      total += turns[i].content.length;
      if (total > 180000 && kept.length) break;
      kept.unshift(turns[i]);
    }
    return [{ role: 'user', content: lead }].concat(kept.map(function (t) { return { role: t.role, content: t.content }; }));
  }

  function pythonTool(key, turns) {
    return {
      name: 'run_python',
      description: 'Runs a SHORT Python snippet (numpy as np and pandas as pd are ready) in the learner\'s browser and returns what it printed (4 KB at most, 5 second limit). Use it only to show a small value or to test a tiny idea. Returns the printed text or an error message.',
      inputSchema: { type: 'object', properties: { code: { type: 'string', description: 'Python code, 15 lines or fewer. Print what you want to see.' } }, required: ['code'] },
      execute: function (input) {
        var code = String(input && input.code || '').slice(0, 3000);
        if (!code.trim()) throw new Error('No code was given.');
        if (!T.Judge || T.Judge.busy()) throw new Error('The learner\'s Python is busy right now. Answer without running code.');
        return T.Judge.play(code, { limitMs: 5000 }).then(function (r) {
          var out = ((r.stdout || '') + (r.error ? (r.stdout ? '\n' : '') + r.error : '')).slice(0, 4096) || '(no output)';
          turns.push({ role: 'tool', code: code, out: out });
          if (st.open && curKey() === key && P.tmpBubble) P.log.insertBefore(toolNote(code, out), P.tmpBubble);
          scrollDown();
          return out;
        });
      }
    };
  }

  function addBubble() {
    var b = bubble('assistant');
    b.setAttribute('aria-busy', 'true');
    b.appendChild(h('span.ai-think', h('i.spin'), ' Thinking…'));
    P.log.querySelectorAll('.ai-welcome').forEach(function (w) { w.remove(); });
    P.log.appendChild(b); P.tmpBubble = b; st.stick = true; scrollDown();
    return b;
  }
  function paint(b, text) { U.clear(b); b.appendChild(AI.md(text)); scrollDown(); }

  function submit() {
    var v = P.input.value.trim();
    if (!v || st.busy) return;
    var key = curKey(), f = flows[key];
    P.input.value = '';
    if (f && f.type === 'drill' && f.phase === 'answering') { answerDrill(key, v); return; }
    send(v);
  }

  /** o: {display, hidden, tier, after(result)} */
  function send(text, o) {
    o = o || {};
    if (!AI.active() || st.busy) return;
    var c = ctx(); if (c.blocked) return;
    open_if_needed();
    var key = curKey(), turns = turnsFor(key);
    var turn = { role: 'user', content: text };
    if (o.display) turn.show = o.display;
    if (o.hidden) turn.hidden = true;
    turns.push(turn);
    var n = renderTurn(turn); if (n) { P.log.querySelectorAll('.ai-welcome').forEach(function (w) { w.remove(); }); P.log.appendChild(n); }
    run(key, turns, turn, o);
  }
  function open_if_needed() { if (!st.open) open({}); }

  function run(key, turns, turn, o) {
    var b = addBubble(), started = false;
    st.busy = true; renderQuick(); syncComposer();
    var cx = ctx();
    var tools = cx.tools && AI.tools ? [pythonTool(key, turns)] : null;
    var r = st.run = AI.stream({
      input: buildInput(key), tier: o.tier || 'default', cache: false, tools: tools,
      onText: function (u) { started = true; b.setAttribute('aria-busy', 'true'); paint(b, u.text); }
    });
    function done() { st.busy = false; st.run = null; P.tmpBubble = null; if (st.open) { renderQuick(); syncComposer(); } }
    r.promise.then(function (res) {
      turns.push({ role: 'assistant', content: res.text });
      b.setAttribute('aria-busy', 'false'); paint(b, res.text);
      if (res.truncated) b.appendChild(h('p.ai-note', 'The answer was cut short. Ask for less at a time.'));
      done(); save();
      if (o.after) o.after(res);
    }, function (e) {
      b.setAttribute('aria-busy', 'false');
      done();
      if (e.code === 'cancelled') {
        if (e.text) { turns.push({ role: 'assistant', content: e.text, stopped: true }); paint(b, e.text); b.appendChild(h('p.ai-note', 'Stopped.')); save(); }
        else {                                     // nothing was written: give the message back to the learner
          b.remove(); var i = turns.lastIndexOf(turn); if (i >= 0) turns.splice(i, 1);
          if (!turn.hidden && st.open && !P.input.value) { P.input.value = turn.show ? turn.content : turn.content; syncComposer(); }
          renderLog(); save();
        }
        return;
      }
      if (e.text && e.code !== 'refused') paint(b, e.text); else U.clear(b);
      var row = h('div.ai-error', { role: 'alert' }, h('span', AI.copyFor(e.code)));
      var noRetry = !!AI.NO_RESEND[e.code];
      if (e.code === 'refused' || e.code === 'prompt_too_large' || e.code === 'empty_completion') {
        var i2 = turns.lastIndexOf(turn); if (i2 >= 0) turns.splice(i2, 1);   // change what you ask; do not resend unchanged
        if (!turn.hidden && !P.input.value) P.input.value = turn.content;
      }
      if (!noRetry && !AI.disabledCode) {
        row.appendChild(h('button.btn.sm', { type: 'button', onclick: function () { keepFocus(); b.remove(); if (!st.busy) run(key, turns, turn, o); } }, 'Try again'));
      }
      b.appendChild(row); scrollDown(); save(); syncComposer();
    });
  }

  function clearChat() {
    if (st.busy && st.run) st.run.abort();
    var key = curKey();
    hist[key] = []; delete flows[key];
    save(); renderAll();
    P.input.focus();
  }

  /* ------------------------------------------------------------ interview-prep chat */
  AI.openInterview = function () {
    if (!AI.active()) return;
    var opener = document.activeElement;
    AI.setOverride({
      kind: 'interview', key: 'interview', title: 'Mock interview', sub: function () { return 'Interview practice'; },
      get: function () {
        var f = flows.interview;
        return 'Interview practice. ' + (f ? 'Level: ' + f.level + '. Topic: ' + f.topic + '.' : 'The learner has not started yet.') + ' The learner is preparing for a Time Series / Forecasting ML engineer interview.';
      },
      quick: function () { return []; }
    });
    open({ opener: opener });
  };

  function renderFlow() {
    U.clear(P.flow);
    var c = ctx(), key = curKey(), f = flows[key];
    P.flow.hidden = true;
    if (c.kind === 'interview' && !f) {
      var lvl = h('select.input', { id: 'ai-lvl', 'aria-label': 'Level' }, [['junior', 'Junior'], ['senior', 'Senior'], ['staff', 'Staff']].map(function (o) { return h('option', { value: o[0], selected: o[0] === 'senior' }, o[1]); }));
      var topics = ['Mixed topics'].concat(C.stages.map(function (s) { return s.title; }));
      var top = h('select.input', { id: 'ai-topic', 'aria-label': 'Topic' }, topics.map(function (t) { return h('option', { value: t }, t); }));
      P.flow.hidden = false;
      P.flow.appendChild(h('div.ai-setup',
        h('label', { for: 'ai-lvl' }, h('b', 'Level')), lvl,
        h('label', { for: 'ai-topic' }, h('b', 'Topic')), top,
        h('button.btn.primary', { type: 'button', onclick: function () {
          keepFocus();
          flows.interview = { type: 'interview', level: lvl.value, topic: top.value };
          hist.interview = []; save();
          renderAll();
          send('Please start the interview now with your first question.', { hidden: true });
        } }, 'Start the interview')));
    } else if (f && f.type === 'drill') {
      P.flow.hidden = false;
      var n = Math.min(3, f.qa.length + (f.phase === 'answering' ? 1 : 0));
      P.flow.appendChild(h('div.ai-progress', h('b', f.phase === 'done' ? 'Interview finished' : f.phase === 'grading' ? 'Grading…' : 'Interviewer: question ' + Math.max(1, n) + ' of 3'),
        h('div.bar', h('i', { style: { width: Math.round((f.phase === 'done' ? 3 : f.qa.length) / 3 * 100) + '%' } }))));
    }
  }

  /* ------------------------------------------------------------ drill mock interviewer */
  function drillOf(key) { var c = ctx(); return c.drill && ('drill:' + c.drill.id) === key ? c.drill : null; }

  function startDrill(key) {
    var dr = drillOf(key); if (!dr || st.busy) return;
    if (!dr.hasAnswers()) { U.toast('Write at least one answer first.'); return; }
    flows[key] = { type: 'drill', phase: 'asking', qa: [], result: null };
    hist[key] = []; save();
    renderAll();
    send('[Interviewer instruction] Ask follow-up question 1 of 3.', { hidden: true, after: function (res) { var f = flows[key]; if (f) { f.phase = 'answering'; f.last = res.text; } renderAll(); save(); } });
  }
  function answerDrill(key, text) {
    var f = flows[key]; if (!f) return;
    var n = f.qa.length + 1;
    f.qa.push({ q: f.last || '', a: text });
    f.phase = 'asking';
    var instr = n < 3 ? 'Give one short sentence of feedback, then ask follow-up question ' + (n + 1) + ' of 3.' : 'This was the last question. Say thank you in one sentence. Do not ask another question.';
    send(text + '\n\n[Interviewer instruction: ' + instr + ']', { display: text, after: function (res) {
      var ff = flows[key]; if (!ff) return;
      if (n < 3) { ff.phase = 'answering'; ff.last = res.text; renderAll(); save(); }
      else { gradeDrill(key); }
    } });
  }

  function gradeDrill(key) {
    var f = flows[key], dr = drillOf(key);
    if (!f || !dr || st.busy) return;
    f.phase = 'grading'; renderFlow(); st.busy = true; renderQuick(); syncComposer();
    var d = dr.d, rub = d.rubric.map(function (r, i) { return (i + 1) + '. ' + r.item + ' (weight ' + (r.weight || 1) + ')'; }).join('\n');
    var qa = f.qa.map(function (x, i) { return 'Follow-up question ' + (i + 1) + ': ' + AI.clip(x.q, 600) + '\nLearner answer ' + (i + 1) + ': ' + AI.clip(x.a, 1500); }).join('\n\n');
    var model = d.sections.map(function (s) { return s.label + ': ' + AI.text(d.modelHtml[s.id] || ''); }).join('\n');
    var prompt = AI.rules() + '\n\nTASK: You are a fair interviewer. Grade the learner against the rubric below. Use the written answers and the follow-up answers. ' +
      'The model answer is for your grading only: do not copy it. Write the "why" and "summary" in plain English.\n' +
      (AI.lang() !== 'English' ? 'Write "why", "summary" and "next_steps" in ' + AI.lang() + '.\n' : '') +
      'Reply with ONLY a JSON object of this shape: {"scores":[{"item":"<rubric item text>","score":0,"why":"<one short sentence>"}],"summary":"<2 or 3 short sentences>","next_steps":["<short step>","<short step>"]}. ' +
      'score is 0 (missing), 1 (partly covered) or 2 (clearly covered). Give one entry per rubric item, in the same order.\n\n' +
      'DRILL: ' + d.title + '\nRUBRIC:\n' + rub + '\n\nWRITTEN ANSWERS AND PROMPT:\n' + AI.clip(dr.context(), 6000) + '\n\nFOLLOW-UP INTERVIEW:\n' + qa + '\n\nMODEL ANSWER (for grading only):\n' + AI.clip(model, 4000);
    var b = addBubble();
    var r = st.run = AI.stream({ input: prompt, json: true, tier: 'complex', cache: false });
    function fin() { st.busy = false; st.run = null; P.tmpBubble = null; }
    r.promise.then(function (data) {
      fin();
      var ok = data && Array.isArray(data.scores) && data.scores.length;
      if (!ok) throw { code: 'invalid_json', message: 'bad shape' };
      var res = { scores: data.scores.map(function (s) { return { item: String(s.item || ''), score: Math.max(0, Math.min(2, Math.round(+s.score || 0))), why: String(s.why || '') }; }),
        summary: String(data.summary || ''), next_steps: Array.isArray(data.next_steps) ? data.next_steps.map(String).slice(0, 5) : [],
        weights: d.rubric.map(function (x) { return x.weight || 1; }) };
      f.phase = 'done'; f.result = true;
      turnsFor(key).push({ role: 'result', data: res });
      b.replaceWith(resultCard(res)); save(); renderAll(); scrollDown();
    }).catch(function (e) {
      fin(); f.phase = 'answering';
      if (e.code === 'cancelled') { b.remove(); renderAll(); return; }
      U.clear(b);
      var row = h('div.ai-error', { role: 'alert' }, h('span', AI.copyFor(e.code)));
      if (!AI.disabledCode) row.appendChild(h('button.btn.sm', { type: 'button', onclick: function () { keepFocus(); b.remove(); gradeDrill(key); } }, 'Try again'));
      b.appendChild(row); renderFlow(); renderQuick(); syncComposer();
    });
  }

  function resultCard(res) {
    var tot = 0, got = 0;
    var rows = res.scores.map(function (s, i) {
      var w = (res.weights && res.weights[i]) || 1; tot += 2 * w; got += s.score * w;
      var label = ['Missing', 'Partly', 'Covered'][s.score];
      return h('li.ai-score', h('div.ai-score-head', h('span.ai-score-item', s.item),
        h('span.ai-meter.s' + s.score, { role: 'img', 'aria-label': label + ' (' + s.score + ' of 2)' }, h('i'), h('i'))),
        h('p.ai-score-why', h('b', label + '. '), s.why));
    });
    var pct = tot ? Math.round(got / tot * 100) : 0;
    return h('div.ai-result',
      h('h3', 'Interview result: ', h('span.ai-pct', pct + '%')),
      h('p.ai-note', 'This is the AI view. Your own self-grade on the page stays as you set it.'),
      h('ul.ai-scores', rows),
      res.summary ? h('p', res.summary) : null,
      res.next_steps && res.next_steps.length ? h('div', h('b', 'Next steps'), h('ul', res.next_steps.map(function (x) { return h('li', x); }))) : null);
  }

  AI.drillStart = function () { startDrill(curKey()); };
  AI.Drawer = { open: open, close: close, toggle: toggle, isOpen: function () { return st.open; }, send: send };
})(window.TSP = window.TSP || {});
