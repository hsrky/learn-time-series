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

Copy the `site/` folder to any static host (GitHub Pages, Netlify, S3, nginx). All URLs are relative,
so a sub-path such as `https://user.github.io/repo/` works. For GitHub Pages, enable
*Settings > Pages > Source: GitHub Actions*; `.github/workflows/pages.yml` publishes `site/`.
Commit the built `site/data/content.js` first (the workflow does not run the build).

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

## Claude Artifact build

Live (private, share from its Share menu): https://claude.ai/artifact/F2oUd3gcjDLg8G61ZR2Nie

Artifacts do not serve `.whl`/`.zip` files and limit each file to ~15 MB, so the publish uses a copy:

```
python3 tools/split_engine.py /tmp/artifact-site --artifact
```

It writes archives as base64 text parts plus `engine/split.json`; `engine/worker.js` rebuilds them in
the browser. On the Artifact, the optional AI tutor (Claude `sample` capability) and progress sync
(`db` + `user`) turn on; on every other host they stay hidden. See `docs/AI_TUTOR.md`.
