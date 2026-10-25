# TimeSeries Path — Design

A static, LeetCode-style learning portal that takes a learner with **zero** time-series
knowledge to the level needed to pass a **Time Series / Forecasting ML Engineer** interview
and online assessment (OA).

It has two halves that are tightly linked:

1. **Learn** — short lessons built on proven learning science, written in plain English for
   non-native readers.
2. **Practice** — LeetCode-style coding problems judged in the browser (real Python with
   numpy + pandas + sqlite3 via Pyodide), plus quizzes, flashcards, mock OAs and design drills.

Hard constraint: **the final site is plain static files** (`site/`). It runs on any static host
(GitHub Pages, Netlify, S3, `python -m http.server`, nginx). No backend, no build step needed at
deploy time, no external network calls required (fonts are optional).

---

## 1. Learning design (how we teach)

The lesson template follows well-tested research on online learning. Each rule below maps to a
feature in the product.

| Principle (source) | What it means here |
|---|---|
| **Mastery learning** (Bloom 1968; Khan Academy) | A lesson counts as *mastered* only when the mastery quiz is ≥ 80% **and** its practice problem is accepted. The path shows *learned / practiced / mastered*. Next lessons are open (soft-lock) but marked "recommended after X". |
| **Gagné's nine events of instruction** | Fixed lesson order: Goals → Warm-up recall → Hook → Explain in chunks → Guided example → Practice → Feedback → Mastery check → Summary/transfer. |
| **Cognitive load theory** (Sweller) | Chunks of ≤ ~150 words, one idea each. Worked example before free problem. Starter code gives the signature and imports. Hints come in 3 levels. |
| **Worked-example → faded-example effect** | Every lesson has a fully commented worked example; the practice problem is the "faded" version (same idea, new data, some parts left to the learner). |
| **Retrieval practice / testing effect** (Roediger & Karpicke) | A quick "Check" question after every chunk; a mastery quiz at the end; questions explain *why* each wrong option is wrong. |
| **Spaced repetition** (Ebbinghaus, Leitner) | Each lesson adds flashcards to a Leitner box review queue (boxes 1→5, intervals 1, 2, 4, 8, 16 days). Wrong quiz answers are also added. "Review" page shows today's due cards. |
| **Interleaving** | Review sessions and Mock OAs mix topics from different stages. |
| **Multimedia & dual coding** (Mayer) | Every abstract idea has a chart or interactive widget next to its words; text is placed next to the picture it explains; no decorative images. |
| **Concrete → abstract** | Numbers and a small example first, the general formula after. |
| **Elaboration / transfer** | Each lesson ends with an *Interview lens* (how it is asked, model answer, common mistakes) and *Real world* (where a known company/project used it). |
| **Immediate feedback** | Judge shows per-case pass/fail with got vs expected; quizzes give instant explanations. |
| **Motivation (self-determination)** | Visible progress, streak, XP; never block the learner; "skip" is always possible. |

### 1.1 Plain-English rules (for non-native readers) — all content MUST follow

- Target **CEFR B1** reading level. Sentences ≤ 20 words. One idea per sentence.
- Active voice. Present tense. Speak to the reader ("you").
- No idioms, jokes that need culture, or phrasal verbs when a simple verb exists
  ("find" not "figure out", "remove" not "get rid of").
- **Define every technical word the first time**, and mark it `[[term]]` so the app shows a
  tooltip from `content/glossary.json`. Use the same word for the same thing everywhere.
- Example and numbers **before** formula. Formulas are written in plain text/HTML
  (`ŷ(t+1) = α·y(t) + (1 − α)·ŷ(t)`) and each symbol is explained in a list under it.
- Lists and tables over long paragraphs. Bold the key word in each chunk.
- No text inside images (so browser translation works). Page has `lang="en"`.
- Each lesson has a 3–5 bullet **Key points** summary that can be read alone.

### 1.2 Lesson template (every `lesson.md`)

```
---  (front matter, YAML-like key: value; lists as [a, b])
id: s1-03-resampling           # unique, = folder name
title: Resampling and time index
minutes: 20
goals: [Change the frequency of a series, Choose the right aggregation, Spot timezone traps]
prereqs: [s1-02-components]
tags: [pandas, resample]
---
## Warm-up            (2 retrieval questions on prereqs, ```check blocks)
## Why it matters     (hook: a real story, ≤ 80 words)
## <Concept chunk 1>  (≤ 150 words + a ```chart or ```widget + a ```check)
## <Concept chunk 2> …
## Worked example     (```python code block, fully commented, with printed output shown)
## Common mistakes    (bullets)
## Interview lens     (Typical question → model answer in 3–6 sentences; red flags)
## Real world         (1–3 short notes: company/project/competition and what they did)
## Key points         (3–5 bullets)
```

Next to `lesson.md`: `quiz.json` (mastery quiz, 5–8 questions), `cards.json` (4–8 flashcards),
`problems/<slug>/…` (0–3 coding problems). Exact formats are in `docs/CONTENT_GUIDE.md`.

---

## 2. Curriculum

Ordered so each stage only needs the previous ones. ~85 lessons, ~120 coding problems.
"★ trend" marks topics that are new/hot in 2024–2026 interviews.

| # | Stage | Lessons (short) |
|---|---|---|
| S0 | **Toolkit bootcamp** | Python for data in 1 hour (lists→numpy); numpy arrays & vectorization; pandas Series/DataFrame; datetime, `DatetimeIndex`, timezones; `shift`, `diff`, `rolling`, `resample`, `groupby` |
| S1 | **Foundations** | What is a time series (and what is not); components: trend/season/cycle/noise; frequency, resampling & aggregation; missing data, irregular timestamps & imputation; lags, differences, returns, log; rolling windows & EWMA; decomposition (classical, STL) |
| S2 | **Statistics of time** | White noise & random walk; stationarity & transforms (log, Box-Cox, differencing); autocorrelation ACF & PACF; unit-root tests ADF/KPSS (intuition + reading output); spurious regression & cross-correlation; Granger causality (concept) |
| S3 | **Classical forecasting** | Baselines: mean, naive, seasonal naive, drift (always first!); simple exp. smoothing; Holt & Holt-Winters / ETS; AR(p) by least squares; MA, ARMA, ARIMA; SARIMA & model selection (AIC/BIC); regression with trend, Fourier terms & holidays (Prophet idea); intermittent demand (Croston, TSB); hierarchical forecasting & reconciliation (bottom-up, top-down, MinT idea) |
| S4 | **Evaluation & backtesting** | Time-based split & data leakage; backtesting: expanding/sliding window, walk-forward, gap/embargo; point metrics MAE, RMSE, MAPE, sMAPE, WAPE, MASE, RMSSE; probabilistic forecasts: quantiles, pinball loss, intervals, coverage, CRPS idea; ★ conformal prediction for time series; comparing models fairly (Diebold-Mariano idea, M-competition style) |
| S5 | **Machine learning for TS** | Reduction to supervised learning (sliding windows); feature engineering: lags, rolling stats, calendar, holidays, events; target transforms & per-series scaling; multi-step strategies: recursive, direct, MIMO, hybrid; global vs local models; gradient boosting (LightGBM/XGBoost) in practice; exogenous & known-future covariates; cold-start & new series |
| S6 | **Deep learning for TS** | Tensors & windowed datasets; RNN/LSTM/GRU; TCN & dilated causal convolutions; seq2seq & DeepAR (probabilistic, Amazon); N-BEATS / N-HiTS; Temporal Fusion Transformer; Transformers for TS: Informer → Autoformer → ★ PatchTST, ★ iTransformer; ★ "Are Transformers effective?" (DLinear/NLinear) & RevIN normalization; ★ state-space models (S4/Mamba) idea |
| S7 | **★ Foundation models & LLMs** (2026 state) | What is a TS foundation model (pre-train on billions of points, zero-shot); ★ Chronos → Chronos-Bolt → Chronos-2 (Amazon, Oct 2025: univariate, multivariate and covariates; implement Chronos scaling + quantization tokens); ★ TimesFM 2.5 (Google, Sep 2025: 200M params, 16k context, decoder-only); ★ Moirai 2.0 (Salesforce, decoder-only), IBM TTM / FlowState, Lag-Llama, MOMENT, TimeGPT (API), Toto (observability), Mistral Timestral; zero-shot vs fine-tune vs routers/ensembles of FMs; benchmarking honestly: GIFT-Eval, fev-bench, TIME, data leakage from pre-training corpora, live leaderboards change monthly; ★ LLMs + time series and forecasting agents (tool-use, auto model selection, explaining forecasts); when NOT to use them (latency, cost, strong seasonal-naive / LightGBM baselines) |
| S8 | **Anomalies, change & other tasks** | Point anomalies: z-score, robust MAD, rolling; seasonal anomalies (S-H-ESD, Twitter); change-point detection (CUSUM, binary segmentation, PELT idea); Isolation Forest & reconstruction-error methods; evaluating anomaly detectors (NAB, point-adjust trap); TS classification: DTW + 1-NN, ★ ROCKET/MiniRocket idea; similarity search & matrix profile idea; clustering series |
| S9 | **Streaming & algorithms** (OA favourites) | Online mean/variance (Welford); sliding-window max/min (monotonic deque); moving median (two heaps); streaming EWMA & rate limiting; time-bucket aggregation & event sessionization; gaps-and-islands; downsampling for charts (LTTB); ★ SQL for time series: `LAG/LEAD`, window `AVG … ROWS BETWEEN`, running totals, gaps & islands (real SQL via sqlite) |
| S10 | **Production & system design** | Point-in-time correctness & feature stores; pipelines & retraining cadence; monitoring: data drift, concept drift, forecast-error alerts; forecasting at scale (millions of series, cost); forecast reconciliation with business (FVA, asymmetric costs, newsvendor quantile); design case: demand forecasting (retail/rides/food delivery); design case: metric anomaly detection platform; design case: capacity planning / ETA |
| S11 | **Case studies (high-profile projects)** | M-competitions (M3, M4: ES-RNN hybrid by Smyl at Uber; M5: LightGBM wins, Walmart data); Prophet at Facebook (and its criticism); Amazon DeepAR/GluonTS → Chronos; Google TimesFM; Uber forecasting platform & Orbit; Zillow Offers 2021 (forecast risk at scale); Kaggle (Rossmann, Web Traffic, Favorita, Optiver volatility); Netflix/LinkedIn anomaly detection; open source map: statsmodels, statsforecast/Nixtla, Darts, sktime, GluonTS, NeuralForecast |
| S12 | **Open-source library tour** (run for real in the browser where possible) | statsmodels (ARIMA/SARIMAX, ETS, STL, `adfuller`, `acf`) — *runs in browser*; scikit-learn for TS (`TimeSeriesSplit`, pipelines, HistGradientBoosting) — *runs in browser*; Nixtla stack (statsforecast, mlforecast, neuralforecast, TimeGPT) — API patterns; Darts, sktime/aeon, GluonTS, AutoGluon-TimeSeries, Prophet, pmdarima; feature/aux libraries: tsfresh, tslearn, stumpy (matrix profile), river (online learning), PyOD; how to pick a library (decision table) |
| S13 | **Interview & OA prep** | How TS interviews are structured; concept question bank (timed); coding OA patterns; take-home project playbook (baseline → backtest → error analysis → narrative); ML system design rubric; communicating with non-experts; behavioural stories with metrics |
| S14 | **Staff+ track** (expert / staff level) | Framing ambiguous business problems as forecasting problems (decision first, not model first); forecasting platform architecture (one platform, many teams, many series); build vs buy vs foundation-model API (cost, latency, risk, lock-in); evaluation governance (golden backtests, champion/challenger, offline↔online gap); forecast value add (FVA) and ROI math; probabilistic forecasts into decisions (inventory, staffing, pricing, capacity); hierarchical/organizational consistency; reliability: fallbacks, SLAs, incident post-mortems for bad forecasts (Zillow lesson); writing a design doc and a tech strategy; influencing without authority, mentoring, roadmap trade-offs; staff-level system design interview (deep dives, failure modes, numbers) |
| S15 | **Kaggle lab** (guided projects) | How Kaggle time-series competitions work (public/private leaderboard, time-based splits, leakage policing); ★ *Store Sales – Time Series Forecasting* (Favorita, permanent Getting-Started competition): full step-by-step tutorial; *M5 Forecasting – Accuracy* (Walmart, hierarchical, WRMSSE, LightGBM global model); *Predict Future Sales* (1C, monthly aggregation, lag features); *Rossmann Store Sales* (promotions, holidays, entity embeddings story); *Web Traffic* (145k series, seq2seq winner); *Optiver Realized Volatility* (high-frequency finance features). Each tutorial: goal → data tour → baseline → validation scheme → features → model → error analysis → submission, with code to run in a Kaggle notebook **and** an in-browser mini version on a small synthetic dataset with the same shape |

### 2.1 Skills interviewers value (spread across lessons, tagged `skill:*`)

These are marked with a badge on lessons/problems and get their own filter in the problem list:

- `skill:baseline-first` — always build naive/seasonal-naive before complex models and report the lift.
- `skill:leakage` — spot look-ahead bias, random splits, future covariates, target leakage in rolling features.
- `skill:backtest` — correct walk-forward evaluation, multiple origins, horizon-wise errors.
- `skill:metrics` — pick the metric for the business (scale-free, intermittent, asymmetric costs).
- `skill:uncertainty` — quantiles, intervals, calibration; "a forecast without uncertainty is half a forecast".
- `skill:pandas-fluency` — fast, vectorized, no Python loops over rows; correct index alignment.
- `skill:from-scratch` — implement EWMA, AR via least squares, ACF, DTW, Welford, pinball loss without libraries.
- `skill:scale` — global models, many series, compute cost, latency.
- `skill:production` — monitoring, drift, retraining, fallbacks, point-in-time data.
- `skill:communication` — explain trade-offs to a PM in 3 sentences; error analysis stories.
- `skill:sql` — window functions on event tables.
- `skill:staff` — problem framing, platform thinking, ROI, influence (S14 + a "Staff lens" box in advanced lessons).

Research notes (Oct 2026) that shaped this list: random splits on time data are a top red flag in
ML interview guides; MLOps/deployment and monitoring are now expected even for mid-level roles;
forecasting work is moving from per-dataset training toward *model selection* among foundation models
(Chronos-2, TimesFM 2.5, Moirai 2.0, IBM FlowState/PatchTST-FM, Mistral Timestral), and benchmark
literacy (GIFT-Eval, fev-bench, TIME; leakage, dated leaderboards) is now a real interview topic.

---

## 3. Practice design (LeetCode-style)

- **Problem list** (like LeetCode Problemset): table with status, title, stage, difficulty
  (Easy/Medium/Hard), tags, skill badges; filters + search; "Pick one" random.
- **Workspace**: left pane tabs *Description · Hints · Solution · Submissions*; right pane
  Python editor + console (*Test cases · Result*). Buttons **Run** (visible cases) and
  **Submit** (all cases, hidden included). Verdicts: Accepted / Wrong Answer / Runtime Error /
  Time Limit Exceeded / Syntax Error.
- **Hints**: 3 levels, opened one by one. **Solution** tab: locked until 1 submission or
  3 runs (can force-open with a confirm), shows reference code + explanation + complexity.
- **Problem types** (all judged by the same harness):
  - `function` — implement a function (most problems).
  - `class` — implement a streaming class; cases call methods in sequence.
  - `sql` — write `QUERY = """…"""`; the harness runs it on sqlite with the given tables.
  - `forecast` — return a forecast; graded by a metric threshold (e.g. MASE < 0.9 vs baseline).
- **Mock OA**: timed session (e.g. 3 problems / 75 min, mixed difficulty & stages), hidden
  verdicts until the end (like HackerRank), score report.
- **Quizzes**: types `single`, `multi`, `numeric` (with tolerance), `order` (put steps in order).
- **Design drills** (S10/S13/S14): prompt, timer, structured textareas (requirements, data,
  model, evaluation, serving, monitoring), then reveal a model answer and a self-grading rubric.

---

## 4. Technical architecture

```
content/            ← source of truth, authored by humans/agents (Markdown + JSON + Python)
  stages.json, glossary.json
  <stage>/<lesson>/lesson.md, quiz.json, cards.json, problems/<slug>/{problem.md,starter.py,solution.py,tests.py}
tools/
  harness.py        ← the judge (same file runs locally in CPython and in the browser in Pyodide)
  check_problem.py  ← validates one problem / a folder: reference passes, starter fails
  build.py          ← validates everything, renders Markdown → HTML, writes site/data/content.js
site/               ← the deployable static site (committed, built output + app code)
  index.html, css/app.css, js/*.js
  engine/           ← Pyodide 0.27.7 core + numpy, pandas, dateutil, pytz, six, sqlite3 (always loaded)
                      + scipy, statsmodels, scikit-learn, patsy, packaging, joblib, threadpoolctl, openblas
                      (lazy: only when a problem lists them in `packages:`), worker.js, harness.py.
                      Vendored (~60 MB) so the site works offline on any static host.
  data/content.js   ← generated: window.TSP_CONTENT = {...}
.github/workflows/pages.yml  ← optional GitHub Pages deploy of site/
```

- **No frameworks**, no bundler: vanilla JS (ES2020) split into modules loaded with plain
  `<script>` tags (works on `file://`-like static hosts; hash routing `#/lesson/<id>`).
- **Python engine**: Web Worker loads Pyodide from `engine/` (relative URL), then
  `loadPackage(["numpy","pandas","sqlite3"])` from the same folder on first use, plus any extra `packages` the problem front matter lists (e.g. `statsmodels`, `scikit-learn`). Status chip
  shows "Python loading… / ready". Run time limit 10 s → terminate worker and restart (TLE).
- **Editor**: textarea + syntax-highlight overlay (no external dependency): Tab/Shift-Tab indent,
  auto-indent after `:`, Ctrl/Cmd-Enter = Run, Ctrl/Cmd-' = Submit, code saved per problem.
- **Charts**: a tiny in-house SVG line/bar chart renderer (`js/charts.js`), theme-aware.
  ```` ```chart ```` blocks in Markdown hold a JSON spec; series can be literal arrays or
  generated by named generators (`trend`, `season`, `noise`, `randomWalk`, `ar1` …, seeded).
- **Widgets**: ```` ```widget ```` blocks name an interactive demo implemented in
  `js/widgets.js` (sliders + live chart): `components`, `moving-average`, `ses-alpha`,
  `holt-winters`, `differencing`, `acf`, `train-test-split`, `walk-forward`, `lag-features`,
  `quantile-loss`, `anomaly-zscore`, `chronos-tokens`, `sliding-window`.
- **State**: `localStorage` key `tsp:v1` (progress, code, quiz scores, Leitner boxes, streak,
  settings). Every read/write wrapped in try/catch. Export/Import progress as JSON file.
- **Theme**: light/dark tokens on `:root` (prefers-color-scheme + manual toggle). Visual language
  matches the author's Staffline clone (Figtree/JetBrains Mono, blue brand, rounded cards).
- **Accessibility**: keyboard reachable, focus rings, 16 px base font with a size setting,
  works at 360 px width (workspace stacks: Problem | Code switch on mobile).

### 4.1 Judge contract (`tools/harness.py`)

`run_job(job: dict) -> dict` where `job = {code, reference, tests, mode: "run"|"submit"}`
(all strings). Steps:

1. `exec(code)` into the user namespace (filename `solution.py`). Syntax error → `Syntax Error`.
2. `exec(reference)` into the reference namespace.
3. For each case in `CASES` from `tests` (run mode: only `visible: True` cases):
   - fresh test namespace = helpers (`np`, `pd`, `sql`, `math`) + `exec(tests)`;
   - `got = eval(case["call"], test_ns ∪ user_ns)`; `exp = eval(case["expected"])` if given,
     else `eval(case["call"], test_ns ∪ reference_ns)`;
   - compare with `check(got, exp, case)` if tests define it, else `default_compare`
     (numbers, lists, dicts, numpy arrays, Series, DataFrames; `tol` per case, NaN-aware).
   - For `class` problems `call` can be a multi-line script whose last expression is the result.
4. Returns `{status, passed, total, results:[{name, call, ok, got, expected, msg, stdout, error, ms}]}`.

---

## 5. Quality gates

- `python tools/build.py` fails if: a reference solution fails any case; a starter passes all
  cases; a lesson misses a required section; a `[[term]]` is not in the glossary; quiz answer
  index out of range; ids not unique; prereq ids unknown.
- Haiku review pass checks plain-English rules (sentence length, undefined terms), broken links,
  and runs the site in headless Chromium (engine boots, a problem is accepted, quiz works).
