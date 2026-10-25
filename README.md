# TimeSeries Path

A free, static, LeetCode-style learning portal that takes a complete beginner to **Time Series /
Forecasting ML Engineer interview level**, up to a Staff+ track. Lessons are written in plain English
(B1 level) for non-native readers and follow proven learning science: mastery learning, worked
examples, retrieval practice, spaced repetition and interleaving.

**What is inside**

- 16 stages, 127 lessons: toolkit bootcamp → foundations → statistics → classical forecasting →
  evaluation & backtesting → ML → deep learning → 2026 foundation models & LLMs → anomalies →
  streaming algorithms & SQL → production & system design → case studies → open-source library tour
  → interview & online-test prep → Staff+ → Kaggle lab.
- 149 coding problems judged by **real Python in your browser** (Pyodide: numpy, pandas, SQL via
  sqlite, and scipy / statsmodels / scikit-learn on demand). Run / Submit, hints, solutions.
- 768 flashcards with spaced repetition, mastery quizzes, 13 timed design drills with rubrics,
  6 mock online assessments, glossary tooltips, progress tracking, dark mode, mobile layout.
- Optional AI tutor when hosted as a Claude Artifact (see below).

Everything is plain static files in `site/`. No server, no framework, no bundler.

## How this site was created

This whole repository — design, curriculum, app code, lessons, problems and tests — was generated
with [Claude Code](https://claude.com/claude-code) from a short series of prompts:
**[docs/PROMPTS.md](docs/PROMPTS.md)**. Claude Opus did the research, design and integration,
Claude Sonnet agents wrote the app and the content in parallel, and a Claude Haiku agent reviewed it.
The process is recorded in [docs/PLAN.md](docs/PLAN.md) (work packages and status),
[docs/DESIGN.md](docs/DESIGN.md) (learning design and curriculum) and [docs/REVIEW.md](docs/REVIEW.md).

AI-written material can contain mistakes. Every coding problem is checked automatically (the reference
solution must pass and the starter code must fail), but please report errors in lessons as issues.

## Run locally

```bash
cd site && python3 -m http.server 8000
# open http://localhost:8000
```

Use a web server (not `file://`): the Python engine runs in a Web Worker.

## Build the content

The site reads `site/data/content.js`, generated from `content/` by `tools/build.py`.
You need Python 3.11+ with `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn` and `markdown`
(the same versions as the browser engine are best: numpy 2.0, pandas 2.2).

```bash
python tools/build.py                    # validate everything, run every reference solution, write the bundle
python tools/build.py --skip-judge       # faster: skip running the problems
python tools/build.py --include-samples  # also build content/_* sample folders
python tools/build.py --strict           # unknown [[glossary terms]] become errors
python tools/build.py --force            # write the bundle even when there are errors (preview only)
python tools/check_problem.py content/s1 # check one folder of problems
```

The build also copies `tools/harness.py` (the judge) to `site/engine/harness.py`.

## Author content

Formats are in [docs/CONTENT_GUIDE.md](docs/CONTENT_GUIDE.md); the learning design and curriculum are in
[docs/DESIGN.md](docs/DESIGN.md). In short: one folder per lesson with `lesson.md`, `quiz.json`,
`cards.json`, optional `drill.json` and `problems/<slug>/{problem.md,starter.py,solution.py,tests.py}`.
New glossary terms go in `content/<stage>/glossary.<stage>.json`.

## Deploy

`site/` is the whole website. All URLs are relative, so it works at a domain root or a sub-path
(such as `https://<user>.github.io/<repo>/`). Any static host works: GitHub Pages, Netlify,
Cloudflare Pages, S3, nginx. The steps below cover GitHub Pages and Claude Artifacts.

Before any deploy, rebuild the content if you changed anything in `content/`:

```bash
python tools/build.py        # writes site/data/content.js; commit it
```

### Deploy to GitHub Pages

The repo already contains `.github/workflows/pages.yml`, which uploads `site/` on every push to `main`.

1. Push this repository to GitHub. Free GitHub Pages needs a **public** repository (private repos need
   a paid plan).
2. Make sure the branch `main` exists and contains the latest `site/` (merge your work into `main`).
3. On GitHub, open **Settings → Pages**. Under **Build and deployment → Source**, choose
   **GitHub Actions**.
4. Open the **Actions** tab. Run **Deploy to GitHub Pages** (or push any commit to `main`).
5. When the job is green, the site is live at `https://<user>.github.io/<repo>/`. The URL is also
   shown in **Settings → Pages**.

Notes: the first visit downloads the Python engine (~25 MB core, more when a problem needs
statsmodels or scikit-learn); later visits use the browser cache. The workflow does not run the
build, so always commit `site/data/content.js` after `python tools/build.py`.

### Deploy to Claude Artifacts

A Claude Artifact is a private page on claude.ai that you can share from its **Share** menu. On an
Artifact the optional **AI tutor** (Claude answers on the viewer's own account, after they allow it)
and **progress sync across devices** turn on. Publishing needs Claude Code (claude.ai/code or the
CLI), because the Artifact tool runs inside a Claude session.

Artifacts do not serve `.whl`/`.zip` files, limit each file to about 15 MB, and accept at most
64 MB per publish. So you publish a prepared copy, in two parts:

1. Make the copy (archives become base64 text parts; `engine/worker.js` rebuilds them in the browser):

   ```bash
   python3 tools/split_engine.py /tmp/artifact-site --artifact
   ```

2. In Claude Code, opened in this repository, send this prompt:

   > Publish /tmp/artifact-site/index.html as a Claude Artifact titled "TimeSeries Path", with
   > root /tmp/artifact-site, capabilities {"sample": {}, "db": {}, "user": {}} and every other
   > file in /tmp/artifact-site as a supporting file (harness.py as text/plain). The total is over
   > 64 MB, so publish in two calls to the same artifact: first everything except the scipy and
   > statsmodels `*.b64-*.txt` parts, then those parts.

3. Open the link Claude returns. Try one lesson, one problem (Run, then Submit) and the AI tutor chip.
4. To share it, use the page's **Share** menu (it starts private).

To update it later, rebuild, run step 1 again, and ask Claude to republish to the same artifact URL.

Example of a live copy (private): https://claude.ai/artifact/F2oUd3gcjDLg8G61ZR2Nie

## Where progress is stored

In your browser (`localStorage`, key `tsp:v1`). Use *Settings > Export progress* to back it up.

## Project layout

```
content/   lessons, problems, glossary (source of truth)
tools/     build.py, harness.py (judge), check_problem.py
site/      index.html, css/, js/ (vanilla JS), engine/ (Pyodide + worker), data/content.js
```

## Credits and licenses

- [Pyodide](https://pyodide.org) 0.27.7 (MPL-2.0) and the bundled wheels: numpy, pandas, scipy,
  statsmodels, scikit-learn, patsy, joblib, threadpoolctl, python-dateutil, pytz, six, packaging, openblas
  (each under its own permissive licence: BSD / MIT / Apache-2.0 style).
- Fonts Figtree and JetBrains Mono (SIL Open Font License) are loaded optionally from Google Fonts;
  the site falls back to system fonts offline.
- Python-Markdown (BSD) is used at build time.
- Full list with licence names: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The vendored files in
  `site/engine/` are unmodified upstream releases; each wheel keeps its own licence file inside.
- Company, product, competition and paper names are used only to describe public, published work;
  no endorsement is implied. Kaggle datasets are **not** included —
  the Kaggle lab tutorials link to the competitions, where you accept each competition's rules.

On every host except a Claude Artifact, the AI tutor and progress sync stay hidden and the site works
the same. Design: [docs/AI_TUTOR.md](docs/AI_TUTOR.md).
