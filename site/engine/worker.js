/* engine/worker.js - runs Python (Pyodide) off the main thread.
   Messages in : {type:'run', id, job, packages} | {type:'play', id, code}
   Messages out: {type:'status'|'ready'|'started'|'case'|'done'|'error', ...}
   Everything is loaded from this folder (relative URLs), so any static host works. */
importScripts('pyodide.js');

const BASE = new URL('./', self.location.href).href;
// Names a problem may list in `packages:` -> Pyodide package names.
const PKG_MAP = { sklearn: 'scikit-learn', scikit_learn: 'scikit-learn', 'scikit-learn': 'scikit-learn',
  statsmodels: 'statsmodels', scipy: 'scipy', numpy: 'numpy', pandas: 'pandas' };
const loaded = new Set(['numpy', 'pandas', 'sqlite3']);
let pyodide = null;

const post = (m) => self.postMessage(m);

// Python helper used by the playground: run code, capture output, show the last expression.
const PLAY_PY = `
import io, sys, ast, contextlib, traceback, time, json
import numpy as np, pandas as pd

def play(code):
    ns = {"__name__": "__main__", "np": np, "pd": pd}
    buf = io.StringIO()
    err = None
    t0 = time.perf_counter()
    try:
        tree = ast.parse(code, "playground.py", "exec")
        last = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = ast.Expression(tree.body.pop().value)
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            exec(compile(tree, "playground.py", "exec"), ns)
            if last is not None:
                v = eval(compile(last, "playground.py", "eval"), ns)
                if v is not None:
                    print(repr(v))
    except SyntaxError as e:
        err = "SyntaxError: %s (line %s)\\n    %s" % (e.msg, e.lineno, (e.text or "").rstrip())
    except BaseException as e:
        tb = traceback.extract_tb(e.__traceback__)
        lines = ['  File "playground.py", line %s, in %s\\n    %s' % (f.lineno, f.name, f.line) for f in tb if f.filename == "playground.py"]
        err = ("Traceback (most recent call last):\\n" + "\\n".join(lines) + "\\n" if lines else "") + "%s: %s" % (type(e).__name__, e)
    return json.dumps({"stdout": buf.getvalue()[-20000:], "error": err, "ms": round((time.perf_counter() - t0) * 1000, 1)})
`;

/* Split-file support (Claude Artifact build only). Hosts with a per-file size limit get big wheels as
   "<name>.part0..N" plus engine/split.json = { "<name>": ["<name>.part0", ...] }; hosts that do not serve
   archives get base64 text parts, listed as { "<name>": { "b64": ["<name>.b64-0.txt", ...] } }.
   When split.json lists a file, fetch() of that file name returns the rebuilt file as one Response. On normal static hosts
   split.json is missing (404) and nothing changes. */
async function setupSplit() {
  let map = null;
  try {
    const r = await fetch(BASE + 'split.json', { cache: 'no-cache' });
    if (r.ok) {
      const j = JSON.parse(await r.text());               // a host that answers 200 with HTML throws here -> ignored
      if (j && typeof j === 'object' && !Array.isArray(j)) map = j;
    }
  } catch (e) { /* no split.json: nothing to do */ }
  if (!map || !Object.keys(map).length) return;
  const orig = self.fetch.bind(self);
  const typeOf = (n) => /\.(whl|zip)$/.test(n) ? 'application/zip' : /\.wasm$/.test(n) ? 'application/wasm' : /\.json$/.test(n) ? 'application/json' : 'application/octet-stream';
  self.fetch = async function (input, init) {
    let name = '';
    try { name = decodeURIComponent(new URL(typeof input === 'string' ? input : (input && input.url) || String(input), BASE).pathname.split('/').pop()); } catch (e) { /* ignore */ }
    const entry = Object.prototype.hasOwnProperty.call(map, name) ? map[name] : null;
    const b64 = !!(entry && Array.isArray(entry.b64));
    const parts = b64 ? entry.b64 : Array.isArray(entry) ? entry : null;
    if (!parts) return orig(input, init);
    const bufs = await Promise.all(parts.map(async (p) => {
      const r = await orig(BASE + p);
      if (!r.ok) throw new Error('Missing part ' + p + ' (HTTP ' + r.status + ')');
      if (!b64) return r.arrayBuffer();
      const bin = atob((await r.text()).trim());          // base64 parts: archives are not served as-is on some hosts
      const out = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
      return out;
    }));
    const blob = new Blob(bufs);
    return new Response(blob, { status: 200, headers: { 'Content-Type': typeOf(name), 'Content-Length': String(blob.size) } });
  };
}

const ready = (async () => {
  await setupSplit();
  post({ type: 'status', msg: 'Loading Python…' });
  pyodide = await loadPyodide({ indexURL: BASE });
  post({ type: 'status', msg: 'Loading numpy and pandas…' });
  await pyodide.loadPackage(['numpy', 'pandas', 'sqlite3']);
  const src = await (await fetch(BASE + 'harness.py', { cache: 'no-cache' })).text();
  pyodide.FS.writeFile('/home/pyodide/harness.py', src);
  pyodide.runPython("import sys\nif '/home/pyodide' not in sys.path: sys.path.insert(0, '/home/pyodide')\nimport harness");
  pyodide.runPython(PLAY_PY);
  post({ type: 'ready' });
})().catch((e) => { post({ type: 'error', fatal: true, msg: 'Could not start Python: ' + (e && e.message || e) }); throw e; });

async function ensurePackages(names) {
  const need = [];
  (names || []).forEach((n) => {
    const p = PKG_MAP[n] || n;
    if (!loaded.has(p)) need.push(p);
  });
  if (!need.length) return;
  post({ type: 'status', msg: 'Loading ' + need.join(', ') + ' (first time only)…' });
  await pyodide.loadPackage(need);
  need.forEach((p) => loaded.add(p));
}

self.onmessage = async (ev) => {
  const m = ev.data;
  try {
    await ready;
    if (m.type === 'run') {
      await ensurePackages(m.packages);
      post({ type: 'started', id: m.id });
      pyodide.globals.set('_job_json', JSON.stringify(m.job));
      pyodide.globals.set('_emit', (s) => post({ type: 'case', id: m.id, res: JSON.parse(s) }));
      const out = pyodide.runPython('harness.run_job_json(_job_json, _emit)');
      post({ type: 'done', id: m.id, result: JSON.parse(out) });
    } else if (m.type === 'play') {
      try { await pyodide.loadPackagesFromImports(m.code); } catch (e) { /* missing package: the import error will explain */ }
      post({ type: 'started', id: m.id });
      pyodide.globals.set('_play_code', m.code);
      const out = pyodide.runPython('play(_play_code)');
      post({ type: 'done', id: m.id, result: JSON.parse(out) });
    }
  } catch (e) {
    post({ type: 'error', id: m.id, msg: String(e && e.message || e) });
  }
};
