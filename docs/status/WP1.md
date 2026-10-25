# WP1 status (app, build, workflow, README) - DONE

- [x] tools/build.py (`--include-samples --skip-judge --strict --force`; env TSP_CONTENT = alternative content dir for tests)
- [x] site/index.html, css/app.css (light/dark tokens, 360px safe)
- [x] js: util, store, router, charts, quiz, widgets (14), md, editor, judge, review
- [x] pages: path, lesson, problems, workspace, playground, review, mock, drills, glossary, progress, settings
- [x] engine/worker.js (numpy, pandas, sqlite3 + lazy statsmodels / scikit-learn / scipy)
- [x] .github/workflows/pages.yml, README.md
- [x] Playwright tests passed (see report)

Notes: sample content lives in content/_sample (skipped unless --include-samples).
site/data/content.js currently holds a `--force --skip-judge` build of the real content; rebuild before release.
Contract: build errors if a lesson lacks "## Warm-up" except the first S0 lesson (s13-01, s14-01, s15-01 hit this).
