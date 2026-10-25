/* ai-mock.js - LOCAL TESTING ONLY. Loaded by ai.js only when the URL contains ?ai=mock (and window.claude is absent).
   Fakes window.claude.use() with a canned "sample" (streams text), a tiny "db" and a "user", following the 0.2.75 contract:
   use() resolves later, namespaces are frozen, sample rejects {code, message, text?}.
   Extra URL switches:  mockfail=<error code>   every sample call rejects with that code
                        mocknull=1              use("sample") resolves null (feature must stay hidden)
                        mocktools=1             sample.limits() reports tools
                        mockslow=<ms>           delay per streamed chunk (default 25)
                        mockdb=0                use("db") resolves null
   Calls are recorded in window.__aiMock.calls = [{input, options, kind}] for tests. */
(function () {
  'use strict';
  var q = new URLSearchParams(location.search);
  var fail = q.get('mockfail'), slow = q.get('mockslow') != null ? +q.get('mockslow') : 25;
  var calls = [];
  var mock = window.__aiMock = { calls: calls, dbWrites: [], toolResults: [] };

  function lastUser(input) {
    if (typeof input === 'string') return input;
    for (var i = input.length - 1; i >= 0; i--) if (input[i].role === 'user') return input[i].content;
    return '';
  }
  function validate(input) {
    if (typeof input === 'string') return input.length ? null : 'empty';
    if (!Array.isArray(input) || !input.length) return 'turns';
    if (input[0].role !== 'user' || input[input.length - 1].role !== 'user') return 'must start and end with a user turn';
    for (var i = 0; i < input.length; i++) if (!input[i].content || (input[i].role !== 'user' && input[i].role !== 'assistant')) return 'bad turn';
    return null;
  }
  function allText(input) { return typeof input === 'string' ? input : input.map(function (t) { return t.content; }).join('\n'); }

  function reply(input, opts) {
    var last = lastUser(input), all = allText(input);
    var m = /follow-up question (\d) of 3/.exec(last);
    if (m) return 'Question ' + m[1] + ': How would you check that this design still works when the data volume grows ten times?';
    if (/Interviewer instruction: This was the last question/.test(last)) return 'Thank you. That was the last question.';
    if (/Start the interview/i.test(last) || /Next question, please/i.test(last)) return 'Interview question: What is the difference between a **trend** and a **seasonal** pattern? Give a short example.';
    if (/Explain my error/i.test(last)) return 'Your code fails on **Case 2**. The output is different from the expected value.\n\n- Check the line that builds the rolling window.\n- Look at `min_periods`.\n\n```python\ns.rolling(3, min_periods=1)\n```\n\nWhat do you expect for the first two rows?';
    if (/Review my code like an interviewer/i.test(last)) return 'Nice work. Complexity is **O(n)**.\n\n- Idiom: good use of `rolling`.\n- Edge case: empty input.\n\nFollow-up 1: What if the index has gaps?\nFollow-up 2: How would you do this for 1 million series?';
    if (/^\[Show me a solution\]/.test(last)) return 'Here is a solution:\n\n```python\ndef f(s):\n    return s.rolling(3).mean()\n```\nThe window size is 3.';
    if (/Explain this lesson section again|simpler/i.test(last)) return 'Simple version: a **time series** is a list of numbers in time order. Example: daily sales.\n\nCheck question: why does the order matter?';
    if (/Explain .* in (\w+)/i.test(last) && /help language/i.test(all)) return 'Mock reply in the help language: **stationarity** (estacionariedad) means the statistics do not change over time.';
    if (/answered this question wrongly|why is my answer wrong/i.test(last)) return 'Your answer is wrong because the order of time matters. A random split can leak the future into training.';
    if (/run a test|run_python/i.test(last) && opts.tools && opts.tools.length) return null; // handled with a tool call
    return 'This is a **mock** answer.\n\n- Point one: stay calm.\n- Point two: try a small example.\n\nShort check: what is a lag?';
  }

  function sampleImpl(input, opts) {
    opts = opts || {};
    return new Promise(function (resolve, reject) {
      calls.push({ kind: 'text', input: input, options: Object.assign({}, opts, { onText: !!opts.onText, signal: !!opts.signal }), signalObj: opts.signal });
      var bad = validate(input);
      if (bad) { reject({ code: 'invalid_request', message: bad }); return; }
      if (fail) { setTimeout(function () { reject({ code: fail, message: 'mock failure' }); }, 20); return; }
      if (opts.signal && opts.signal.aborted) { reject({ code: 'cancelled', message: 'aborted' }); return; }
      var text = reply(input, opts), shown = '', timer = null, i = 0;
      function abort() { clearTimeout(timer); reject({ code: 'cancelled', message: 'aborted', text: shown || undefined }); }
      if (opts.signal) opts.signal.addEventListener('abort', abort, { once: true });
      function stream(full) {
        var words = full.split(/(\s+)/);
        (function step() {
          if (opts.signal && opts.signal.aborted) return;
          if (i >= words.length) { if (opts.signal) opts.signal.removeEventListener('abort', abort); resolve({ text: full, truncated: false, modelTierApplied: opts.modelTier || 'default' }); return; }
          var delta = words.slice(i, i + 2).join(''); i += 2;
          if (!delta.trim() && !shown) { step(); return; }
          shown += delta;
          if (opts.onText) { try { opts.onText({ text: shown, delta: delta }); } catch (e) { /* ignore */ } }
          timer = setTimeout(step, slow);
        })();
      }
      setTimeout(function () {
        if (opts.signal && opts.signal.aborted) return;
        if (text == null) {                           // tool round
          var tool = opts.tools[0];
          Promise.resolve(tool.execute({ code: 'print(1 + 1)' }, { signal: opts.signal || new AbortController().signal })).then(function (out) {
            mock.toolResults.push(out);
            stream('I ran a small test. The output was: ' + out);
          }, function (e) { stream('The tool failed: ' + (e && e.message)); });
        } else stream(text);
      }, +q.get('mockthink') || 40);
    });
  }
  sampleImpl.json = function (input, opts) {
    calls.push({ kind: 'json', input: input, options: Object.assign({}, opts || {}, { onText: false, signal: false }) });
    if (fail) return new Promise(function (_, rej) { setTimeout(function () { rej({ code: fail, message: 'mock failure' }); }, 20); });
    var all = allText(input), n = (all.match(/RUBRIC:\n((?:\d+\..*\n?)+)/) || [0, ''])[1].trim().split('\n').filter(Boolean);
    return new Promise(function (resolve) {
      setTimeout(function () {
        resolve({
          scores: n.map(function (line, i) { return { item: line.replace(/^\d+\.\s*/, '').replace(/\s*\(weight \d+\)\s*$/, ''), score: i % 3, why: 'Mock reason ' + (i + 1) + '.' }; }),
          summary: 'Mock summary. You covered the basics and missed some details.', next_steps: ['Write the metric you would track.', 'Name one failure mode.']
        });
      }, 150);
    });
  };
  sampleImpl.limits = function () { return Promise.resolve(Object.assign({ maxPromptBytes: 262144 }, q.get('mocktools') ? { tools: { maxCount: 4 } } : {})); };
  Object.freeze(sampleImpl);

  /* ---- fake db (localStorage-backed) and user ---- */
  function dbDoc(path) {
    var segs = String(path).split('/');
    if (segs.length % 2 !== 0) throw new TypeError('A document path needs an even number of segments: ' + path);
    var k = 'tsp:mockdb:' + path;
    return Object.freeze({
      id: segs[segs.length - 1], path: path,
      get: function () {
        var raw = null; try { raw = localStorage.getItem(k); } catch (e) { /* ignore */ }
        var data = raw ? JSON.parse(raw) : undefined;
        return Promise.resolve({ exists: !!raw, data: function () { return data; } });
      },
      set: function (data) {
        mock.dbWrites.push({ path: path, t: Date.now(), bytes: JSON.stringify(data).length });
        try { localStorage.setItem(k, JSON.stringify(data)); } catch (e) { /* ignore */ }
        return Promise.resolve();
      },
      delete: function () { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } return Promise.resolve(); }
    });
  }
  var db = Object.freeze({ doc: dbDoc, collection: function () { throw new Error('mock: not implemented'); } });
  var user = Object.freeze({
    id: function () { return Promise.resolve('u_mock'); },
    me: function () { return Promise.resolve({ id: 'u_mock', name: 'Mock', avatarUrl: '', color: '#888', email: null, isOwner: true, canEdit: true }); },
    can: function () { return Promise.resolve(null); }, isOwner: function () { return Promise.resolve(true); }, canEdit: function () { return Promise.resolve(true); }
  });

  window.claude = Object.freeze({
    use: function (name) {
      return new Promise(function (resolve) {
        setTimeout(function () {                      // resolves LATER, never synchronously
          if (name === 'sample') resolve(q.get('mocknull') ? null : sampleImpl);
          else if (name === 'db') resolve(q.get('mockdb') === '0' ? null : db);
          else if (name === 'user') resolve(user);
          else resolve(null);
        }, 60);
      });
    }
  });
})();
