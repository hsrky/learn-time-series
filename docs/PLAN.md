# Implementation plan & status

Design: [DESIGN.md](DESIGN.md) · Content format: [CONTENT_GUIDE.md](CONTENT_GUIDE.md)

Roles: **Opus** = design, plan, contracts, integration. **Sonnet** = implementation (app + content,
in parallel work packages). **Haiku** = check & report ([REVIEW.md](REVIEW.md)).

Status legend: ⬜ todo · 🟨 in progress · ✅ done · ❌ blocked

Each work package keeps a detailed live status file in `docs/status/<wp>.md` (lesson by lesson,
problem by problem, with `check_problem.py` result). This table is the summary.

| WP | Owner | Scope | Status |
|---|---|---|---|
| WP0 | Opus | Design, curriculum, content contract, judge harness (`tools/harness.py`), `tools/check_problem.py`, vendored Pyodide 0.27.7 engine + wheels (`site/engine/`), `content/stages.json` | ✅ |
| WP1 | Sonnet | App: `tools/build.py`, `site/index.html`, `site/css`, `site/js/*` (router, store, editor, worker/judge client, charts, widgets, quiz, Leitner review, problem list, workspace, mock OA, design drills, glossary, progress, settings, export/import), GitHub Pages workflow, README | ✅ |
| WP2 | Sonnet | Content S0 Toolkit + S1 Foundations | ✅ |
| WP3 | Sonnet | Content S2 Statistics + S3 Classical forecasting | ✅ |
| WP4 | Sonnet | Content S4 Evaluation + S5 ML for TS | ✅ |
| WP5 | Sonnet | Content S6 Deep learning + S7 Foundation models & LLMs (2026) | ✅ |
| WP6 | Sonnet | Content S8 Anomalies + S9 Streaming & SQL | ✅ |
| WP7 | Sonnet | Content S10 Production/design + S11 Case studies + S12 Library tour | ✅ |
| WP8 | Sonnet | Content S13 Interview & OA prep + S14 Staff+ + S15 Kaggle lab | ✅ |
| WP9 | Opus | Integration: merge glossaries, full build, fix cross-links, commit, publish | 🟨 build clean (127 lessons, 149 problems, 768 cards); 149/149 reference solutions Accepted in the browser engine |
| WP10 | Haiku | Review: full validation, plain-English lint, headless browser smoke test, report | 🟨 |
| WP11 | Opus → Sonnet | After round 1: research Claude Artifact runtime capabilities and add an optional AI tutor (hint coach, explain my error, explain this chart, plain-English rewrite) that appears only when the page runs as a Claude Artifact; the static-host build keeps working without it. Design: [AI_TUTOR.md](AI_TUTOR.md) | ✅ (mock-tested; real Claude calls tested after publish) |

## Milestones

1. M1 — Contracts frozen (WP0) ✅
2. M2 — App renders a sample lesson and judges a problem in the browser (WP1)
3. M3 — All stages authored, every problem passes `check_problem.py` (WP2–WP8)
4. M4 — `tools/build.py` clean, site deployable from `site/` (WP9)
5. M5 — Review report with no blocking issues (WP10)

## Targets per stage (minimums)

| Stage | Lessons | Coding problems | Notes |
|---|---|---|---|
| S0 | 5 | 8 | from zero: Python → numpy → pandas time index |
| S1 | 7 | 10 | |
| S2 | 6 | 7 | |
| S3 | 9 | 12 | implement SES/Holt/AR from scratch; one statsmodels problem |
| S4 | 6 | 9 | incl. conformal prediction |
| S5 | 8 | 9 | |
| S6 | 8 | 7 | numpy implementations (windowing, RevIN, DLinear, patching) |
| S7 | 6 | 4 | Chronos tokenizer, zero-shot eval harness |
| S8 | 7 | 9 | |
| S9 | 7 | 12 | many classic OA problems + real SQL |
| S10 | 7 | 4 | mostly design drills |
| S11 | 7 | 3 | case quizzes |
| S12 | 6 | 5 | statsmodels + scikit-learn running in browser |
| S13 | 6 | 8 | OA-pattern problems, mock OA sets, question bank |
| S14 | 8 | 3 | staff design drills, ROI/newsvendor math problems |
| S15 | 7 | 7 | one in-browser "mini" problem per Kaggle tutorial |
