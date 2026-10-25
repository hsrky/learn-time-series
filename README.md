# TimeSeries Path

A static, LeetCode-style learning portal for time series and forecasting. It goes from zero
knowledge to Time Series / Forecasting ML Engineer interview level. Lessons, quizzes, flashcards,
design drills, mock online tests and coding problems that run **real Python (numpy, pandas, and
scipy / statsmodels / scikit-learn on demand) in your browser** with Pyodide.

Everything is plain static files in `site/`. No server, no framework, no bundler.

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
