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
const typeOf = (n) => /\.(whl|zip)$/.test(n) ? 'application/zip' : /\.wasm$/.test(n) ? 'application/wasm' : /\.json$/.test(n) ? 'application/json' : 'application/octet-stream';
let splitMap = null;                                   // set by setupSplit when split.json lists files
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
  splitMap = map;
  self.fetch = async function (input, init) {
    let name = '';
    try { name = decodeURIComponent(new URL(typeof input === 'string' ? input : (input && input.url) || String(input), BASE).pathname.split('/').pop()); } catch (e) { /* ignore */ }
    const entry = Object.prototype.hasOwnProperty.call(map, name) ? map[name] : null;
    const b64 = !!(entry && Array.isArray(entry.b64));
    const parts = b64 ? entry.b64 : Array.isArray(entry) ? entry : null;
    if (!parts) return orig(input, init);
    const bufs = await Promise.all(parts.map(async (p) => {
      const r = await orig(BASE + p);                    // parts: plain fetch, no `integrity` (the rebuilt file is verified instead)
      if (!r.ok) throw new Error('Missing part ' + p + ' (HTTP ' + r.status + ')');
      if (!b64) { const ab = await r.arrayBuffer(); countBytes(ab.byteLength); return ab; }
      const txt = (await r.text()).trim();
      countBytes(txt.length * 3 / 4);                    // progress counts the decoded size
      const bin = atob(txt);          // base64 parts: archives are not served as-is on some hosts
      const out = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
      return out;
    }));
    const blob = new Blob(bufs);
    return new Response(blob, { status: 200, headers: { 'Content-Type': typeOf(name), 'Content-Length': String(blob.size) } });
  };
}

/* Engine cache + integrity (needs engine/manifest.json, written by tools/engine_manifest.py).
   Every engine file listed in the manifest is stored once in Cache Storage ("tsp-engine-<version>") and its
   SHA-256 is checked before each use, so a corrupted or half-written copy is never served: it is deleted and
   downloaded again. A new manifest version opens a new cache and the old "tsp-engine-*" caches are deleted.
   It wraps whatever self.fetch is at that moment (the split/base64 wrapper above), so the check applies to the
   REBUILT file under its original name. Without a manifest, Cache Storage or crypto.subtle the engine still
   works (plain network, verified when crypto exists). */
const CACHE_PREFIX = 'tsp-engine-';
const stats = { hits: 0, downloads: 0, got: 0, want: 0, last: 0 };   // progress of this page load
let damaged = '';                                                     // message of a file that failed its check (Pyodide may swallow the error)
const counted = new Set();                                            // files already added to stats.want

/** Add downloaded bytes to the progress message "Downloading Python engine… 12 / 24 MB" (max 4 per second). */
function countBytes(n) {
  stats.got += n;
  const now = Date.now();
  if (now - stats.last < 250) return;
  stats.last = now;
  const mb = (x) => Math.round(x / 1048576);
  post({ type: 'status', msg: 'Downloading Python engine… ' + mb(stats.got) + ' / ' + mb(Math.max(stats.want, stats.got)) + ' MB' });
}

const hex = (buf) => Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, '0')).join('');
const sha256 = async (blob) => hex(await crypto.subtle.digest('SHA-256', await blob.arrayBuffer()));

async function setupCache() {
  // 1. The manifest: always from the network, never from an old cache.
  let man = null;
  try {
    const r = await fetch(BASE + 'manifest.json', { cache: 'no-store' });
    if (r.ok) {
      const j = JSON.parse(await r.text());
      if (j && typeof j.version === 'string' && j.files && typeof j.files === 'object') man = j;
    }
  } catch (e) { /* handled below */ }
  if (!man) { console.warn('Python engine: manifest.json missing or invalid; caching and checks are off.'); return; }
  if (!self.crypto || !self.crypto.subtle) { console.warn('Python engine: crypto.subtle unavailable (not a secure page); checks and caching are off.'); return; }

  // 2. The cache for this version; delete caches of other versions. Cache Storage may be missing or blocked.
  let cache = null;
  const cacheName = CACHE_PREFIX + man.version;
  try {
    if (self.caches) {
      cache = await caches.open(cacheName);
      for (const k of await caches.keys()) if (k.startsWith(CACHE_PREFIX) && k !== cacheName) await caches.delete(k);
    }
  } catch (e) { cache = null; console.warn('Python engine: Cache Storage not available; files are checked but not kept.'); }

  const key = (name) => new Request(new URL('/__tsp_engine__/' + man.version + '/' + name, self.location.href));
  const inner = self.fetch.bind(self);
  const inflight = new Map();                          // name -> promise of verified Blob (one download per file)
  const respond = (name, blob) => new Response(blob, { status: 200, headers: { 'Content-Type': typeOf(name), 'Content-Length': String(blob.size) } });

  /** A verified Blob for one manifest file: from the cache if its hash matches, else downloaded (and then stored). */
  async function load(name, want) {
    if (cache) {
      try {
        const hit = await cache.match(key(name));
        if (hit) {
          const blob = await hit.blob();
          if (blob.size === want.size && await sha256(blob) === want.sha256) { stats.hits++; return blob; }
          console.warn('Python engine: cached copy of ' + name + ' is damaged; downloading it again.');
          await cache.delete(key(name));
        }
      } catch (e) { /* unreadable entry: download again */ }
    }
    if (!counted.has(name)) { counted.add(name); stats.want += want.size; }
    stats.downloads++;
    // No `integrity` option here: Pyodide's value is for the file on the server, and we check the SHA-256 ourselves.
    const r = await inner(BASE + name);
    if (!r.ok) throw new Error('Could not download ' + name + ' (HTTP ' + r.status + ').');
    const chunks = [];
    if (r.body && !(splitMap && Object.prototype.hasOwnProperty.call(splitMap, name))) {
      const rd = r.body.getReader();                   // stream it to show progress (split files report per part)
      for (;;) { const { done, value } = await rd.read(); if (done) break; chunks.push(value); countBytes(value.length); }
    } else chunks.push(await r.arrayBuffer());
    const blob = new Blob(chunks);
    if (blob.size !== want.size || await sha256(blob) !== want.sha256) {
      damaged = 'The download of ' + name + ' was damaged. Please reload.';
      throw new Error(damaged);
    }
    if (cache) { try { await cache.put(key(name), respond(name, blob)); } catch (e) { /* storage full: serve it anyway */ } }
    return blob;
  }

  self.fetch = async function (input, init) {
    let name = '', url = '';
    try {
      url = new URL(typeof input === 'string' ? input : (input && input.url) || String(input), BASE);
      if (url.href.startsWith(BASE)) name = decodeURIComponent(url.pathname.slice(new URL(BASE).pathname.length));
    } catch (e) { /* not a URL we understand */ }
    const method = ((init && init.method) || (input && input.method) || 'GET').toUpperCase();
    const want = name && method === 'GET' && Object.prototype.hasOwnProperty.call(man.files, name) ? man.files[name] : null;
    if (!want) return inner(input, init);
    if (!inflight.has(name)) inflight.set(name, load(name, want).finally(() => inflight.delete(name)));
    return respond(name, await inflight.get(name));
  };
}

const ready = (async () => {
  await setupSplit();
  await setupCache();
  post({ type: 'status', msg: 'Loading Python…' });
  pyodide = await loadPyodide({ indexURL: BASE });
  post({ type: 'status', msg: 'Loading numpy and pandas…' });
  await pyodide.loadPackage(['numpy', 'pandas', 'sqlite3']);
  if (damaged) throw new Error(damaged);               // loadPackage can swallow a failed download: report it clearly
  const src = await (await fetch(BASE + 'harness.py', { cache: 'no-cache' })).text();
  pyodide.FS.writeFile('/home/pyodide/harness.py', src);
  pyodide.runPython("import sys\nif '/home/pyodide' not in sys.path: sys.path.insert(0, '/home/pyodide')\nimport harness");
  pyodide.runPython(PLAY_PY);
  if (stats.hits && !stats.downloads) post({ type: 'status', msg: 'Python engine loaded from this device' });
  post({ type: 'ready' });
})().catch((e) => { post({ type: 'error', fatal: true, msg: damaged || 'Could not start Python: ' + (e && e.message || e) }); throw e; });

async function ensurePackages(names) {
  const need = [];
  (names || []).forEach((n) => {
    const p = PKG_MAP[n] || n;
    if (!loaded.has(p)) need.push(p);
  });
  if (!need.length) return;
  post({ type: 'status', msg: 'Loading ' + need.join(', ') + ' (first time only)…' });
  await pyodide.loadPackage(need);
  if (damaged) throw new Error(damaged);
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
    post({ type: 'error', id: m.id, msg: damaged || String(e && e.message || e) });
    damaged = '';                                      // a later retry downloads the file again
  }
};
