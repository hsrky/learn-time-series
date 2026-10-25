# WP10 Review: TimeSeries Path

Reviewer: Haiku (WP10). Date: 2026-10-25. Scope: `content/` (127 lessons, 149 problems), the built bundle `site/data/content.js`, and the static `site/` app.
Nothing was edited except this file. Nothing was committed. `tools/build.py` was not re-run because it writes `site/`; the review read the built bundle instead.

## Verdict

**Not ready to publish.** Four blocking items. Two are one-line code or data fixes, and two are content edits.

| Severity | Count | Items |
|---|---|---|
| Blocking | 4 | Stray `null` on every lesson Finish screen; wrong MAD glossary definition; 21 idiom hits; 593 sentences over 20 words (214 over 25) |
| Should fix | 5 | 42 concept chunks over 150 words; 32 glossary terms defined differently in two stage files; 16 lessons with one Warm-up check instead of two; s13-02 quiz and cards over the guide limits; one unsourced generalization in s6-07 |
| Nice to have | 9 | See section 8 |

What passed: all stages meet the PLAN minimums; all 622 `[[term]]` links resolve; no horizontal overflow at 1280 px or 360 px on any page or step walked; no JavaScript errors; Run and Submit give the right verdicts on desktop and mobile; the static build uses only relative paths.

---

## 1. Coverage (check 1)

Lessons and problems against PLAN targets. Every stage meets its minimum.

| Stage | Lessons (target) | Problems (target) |
|---|---|---|
| S0 | 5 (5) | 11 (8) |
| S1 | 7 (7) | 11 (10) |
| S2 | 6 (6) | 9 (7) |
| S3 | 10 (9) | 22 (12) |
| S4 | 6 (6) | 12 (9) |
| S5 | 9 (8) | 11 (9) |
| S6 | 10 (8) | 8 (7) |
| S7 | 7 (6) | 5 (4) |
| S8 | 8 (7) | 9 (9) |
| S9 | 9 (7) | 19 (12) |
| S10 | 9 (7) | 5 (4) |
| S11 | 8 (7) | 3 (3) |
| S12 | 7 (6) | 5 (5) |
| S13 | 8 (6) | 8 (8) |
| S14 | 10 (8) | 3 (3) |
| S15 | 8 (7) | 8 (7) |
| **Total** | **127 (110)** | **149 (117)** |

**DESIGN §2 bullets.** I grepped each bullet's key terms with word-boundary matching across all lessons and problems. Every named model, metric and technique appears in at least one lesson. Two notes:

- S11's "open-source map" bullet (statsmodels, statsforecast, Darts, sktime, GluonTS, NeuralForecast) is only covered in S12 (`s12-04-nixtla-stack`, `s12-05-frameworks`). This is a placement gap, not a content gap.
- S14's "hierarchical / organisational consistency" bullet is covered in `s14-02-forecasting-platform`, under "Consistency across the organisation".

**PLAN notes.** Verified: S3 has from-scratch SES, Holt and AR problems and one statsmodels problem (`sarimax-forecast`). S4 has two conformal problems. S6 has windowing, RevIN, DLinear and patching problems. S12 has three statsmodels and two scikit-learn in-browser problems.

**CONTENT_GUIDE and DESIGN template rules:**

- Key points has 3 to 5 bullets in every lesson. Pass.
- Warm-up should have 2 checks (DESIGN §1.2). 16 lessons have one: s13-02, s13-03, s13-05, s13-06, s13-07, s13-08, s14-02 to s14-10, and s15-03. s0-01 is exempt by design.
- Quiz 5 to 8 questions, and cards 4 to 8 with front at most 15 words and back at most 35 words. Pass everywhere except s13-02: a 23-question quiz and 42 cards. This may be an intentional question bank, but it is outside the guide.
- Concept chunks at most about 150 words (DESIGN §1, a design principle, not a MUST). 42 prose sections are over 150 words. The largest are `s10-06-forecasts-into-decisions` "Asymmetric costs and the newsvendor" (249), `s14-07-reliability-and-postmortems` "Case: Zillow Offers" (224), `s3-10-hierarchical-reconciliation` "Optimal reconciliation" (205), `s3-09-intermittent-demand` "Croston" (203), `s7-02-chronos-family` "Chronos (2024)" (203). The count is an underestimate for table-heavy sections, which the script skipped.

---

## 2. Plain-English lint (check 2)

Scope: prose in `content/s*/*/lesson.md`. Code, JSON, tables and headings were excluded. List items were counted as sentences.

- Sentences: 9,164. Average 10.8 words. Per-lesson averages range from 7.4 to 14.3. The highest are `s11-06-zillow-offers-2021` (14.3), `s7-06-llms-and-forecasting-agents` (14.2) and `s15-07-web-traffic-forecasting` (13.9).
- **Sentences over 20 words (DESIGN §1.1 limit, written as MUST): 593 (6.5%).**
- Sentences over 25 words: 214 (2.3%). They are in 80 of 127 lessons.
- Lessons with the most sentences over 20 words: `s7-06` (16), `s15-07` (15), `s6-08-are-transformers-effective` (12), `s11-03-deepar-gluonts-chronos` (12), `s15-03-store-sales-features-model-submission` (12).
- Paragraphs over 120 words: 1. `s14-10-staff-system-design-interview`, "Strong answer" paragraph, 134 words.

**Idioms and phrasal verbs from the required list (MUST, blocking).** 13 hits in lesson prose:

- "rule of thumb" (6): `s3-03-holt-trend-damped:106`, `s6-02-rnn-lstm-gru:95`, `s9-04-ewma-rate-limiting` (sentence "A rule of thumb: the memory..."), `s10-02-pipelines-and-retraining:44`, `s10-03-drift-monitoring:81` and `:161`.
- "deep dive" (5 in prose): `s13-01-how-interviews-work:66`, `:84`, `:147`, and `s14-10-staff-system-design-interview:58` and `:60`. These are used as a noun for an interview round. Replace with "in-depth question" or similar. One more in a table at `s13-01:34` (tables were excluded from the lint).
- "under the hood" (2): `s12-03-scikit-learn-for-ts`, `s12-04-nixtla-stack:116`.

Another 7 hits sit in learner-facing JSON or problem text, which my lint skipped:

- `s10-03-drift-monitoring/cards.json` ("PSI rule of thumb?")
- `s10-04-forecast-error-alerts/lesson.md:22` (check block, "By the common rule of thumb")
- `s2-03-acf-pacf/problems/ar-order-from-pacf/problem.md:11` ("Use the rule of thumb")
- `s13-01-how-interviews-work/cards.json:4` ("time-series deep dive")
- `s14-10-staff-system-design-interview/cards.json:7` ("Three layers of a deep dive?")
- `s14-10-staff-system-design-interview/quiz.json:26` and `:27` ("deep dives", "deep dives")

Total: 21 idiom hits (13 prose, 7 in other blocks, 1 table).

Secondary (judgment, not on the list): "look at" 59, "depend on" 10, "find out" 3, "set up" 2, "go through" 1. "find out" should be "find" or "learn".

Overuse: "very" 55, "easy" 14, "just" 23, "clearly" 7, "really" 6, "simply" 2, "easily" 2, "obviously" 0.

### Worst 40 sentences over 25 words

1. **49 words**, `content/s15/s15-08-optiver-realized-volatility/lesson.md`: Extra ideas: the same features for the level-2 prices, realized volatility of trade prices, stock-level averages of the target (target encoding computed inside the training folds only), and time-level features: the mean of CODE across all stocks in the same CODE (the market-wide volatility), which is a strong signal.
2. **46 words**, `content/s6/s6-07-transformers-for-ts/lesson.md`: The story has twists: first complex models, then a simple linear baseline that beat them (next lesson), then two designs (PatchTST and iTransformer) that made Transformers competitive again. 2026 trend: the building blocks of PatchTST (patches) are inside most time series foundation models in stage 7.
3. **45 words**, `content/s14/s14-10-staff-system-design-interview/lesson.md`: The senior design interview asks: "Can you design this system?" The staff interview asks: "Can you decide what to build, for whom, with which risks, and how to get it done by many people?" You are expected to lead the conversation, not follow a checklist.
4. **44 words**, `content/s9/s9-06-gaps-and-islands/lesson.md`: For many users or for a table, I use the "date minus row number" trick: it gives a constant key inside each consecutive block, so I can group by it in pandas or SQL and get the start, end, and length of every island.
5. **42 words**, `content/s12/s12-06-more-libraries/lesson.md`: Prophet came from Facebook, stumpy from the matrix profile research of the Keogh group at UC Riverside and implementation by TD Ameritrade engineers, tsfresh from a research project with Blue Yonder, and river from the merger of the creme and scikit-multiflow projects.
6. **40 words**, `content/s7/s7-01-what-is-a-foundation-model/lesson.md`: I would run it on my data with a time-based backtest and compare it with seasonal naive, a tuned classical model and a boosted-tree model, using a scale-free metric such as MASE and a probabilistic metric if I need intervals.
7. **39 words**, `content/s9/s9-06-gaps-and-islands/lesson.md`: "Find the longest streak of days when a user logged in." "Find periods when a machine was running without a break." "How many days in a row was the temperature above 30?" All are the gaps and islands problem.
8. **39 words**, `content/s9/s9-07-downsampling-lttb/lesson.md`: I would use LTTB: split the series into buckets, keep the first and last point, and in each bucket choose the point with the largest triangle area using the previously chosen point and the average of the next bucket.
9. **39 words**, `content/s12/s12-03-scikit-learn-for-ts/lesson.md`: I build lag and rolling features with shift so each window ends before the row, put preprocessing in a Pipeline, and validate with CODE, using a CODE when features or targets overlap and CODE equal to the forecast horizon.
10. **38 words**, `content/s11/s11-01-m-competitions/lesson.md`: So the rule is: for few series use strong statistical baselines and combine them; for many related series with covariates use global ML; always compare with a naive benchmark using a scale-free metric such as MASE or OWA.
11. **37 words**, `content/s10/s10-09-design-capacity-eta/lesson.md`: Features: distance and route estimate, restaurant preparation time (recent and typical), traffic level now, weather, hour and weekday, courier supply near the restaurant, order size, recent actual times in the same area (a rolling feature, built point-in-time).
12. **37 words**, `content/s12/s12-01-statsmodels/lesson.md`: STL recovers a trend slope near the true 0.3, a seasonal range of about 18 (the clean wave has range 16, and a little noise leaks in), and a residual standard deviation near the noise level 1.5.
13. **37 words**, `content/s15/s15-08-optiver-realized-volatility/lesson.md`: Strong answer: "I compute the weighted average price from the best bid and ask, take log returns inside each window, and use realized volatility, the square root of the sum of squared returns, as the main feature.
14. **36 words**, `content/s6/s6-08-are-transformers-effective/lesson.md`: Strong answer: The authors showed that a one-layer linear model, DLinear, which splits the window into a moving-average trend and a remainder and applies one linear layer to each, beat many Transformer forecasters on long-term benchmarks.
15. **36 words**, `content/s6/s6-08-are-transformers-effective/lesson.md`: For my work it means: always build naive, seasonal naive and a linear model first, report the lift of the complex model over them, and run the comparison on my own data with a time-based backtest.
16. **36 words**, `content/s9/s9-08-sql-window-functions/lesson.md`: An OA often asks: "Write a SQL query that shows the day-over-day change." "Compute a 7-day moving average." "Show the running total per store." You can do each of these in one query with window functions.
17. **36 words**, `content/s14/s14-06-probabilistic-decisions/lesson.md`: A decision needs more: "How many do I order?" "How many agents do I schedule?" "How much server capacity do I reserve?" The answer depends on how much it hurts to be wrong in each direction.
18. **36 words**, `content/s15/s15-07-web-traffic-forecasting/lesson.md`: Things to see on the real data: many pages are small and noisy; some have a clear weekly pattern; some have yearly peaks; some have spikes from news events; many have missing days at the start.
19. **35 words**, `content/s5/s5-05-multistep-strategies/lesson.md`: Examples: DirRec (a direct model for each step that also uses the predictions of earlier steps as inputs); or block strategies (one MIMO model per block of steps, such as days 1–7 and days 8–14).
20. **35 words**, `content/s10/s10-05-forecasting-at-scale/lesson.md`: A common design is tiered: global model for most series, a simple method (seasonal naive, moving average) for tiny or intermittent series, and special handling for the top revenue series with analysts in the loop.
21. **35 words**, `content/s11/s11-08-anomaly-detection-at-large-companies/lesson.md`: The package can find global anomalies (large compared with the whole series) and local anomalies (small in absolute value but large for their season), and can limit anomalies to only the positive or negative direction.
22. **35 words**, `content/s12/s12-01-statsmodels/lesson.md`: Rules of thumb for choosing ARIMA orders on a stationary series: an AR(p) process has a PACF that cuts off after lag p; an MA(q) process has an ACF that cuts off after lag q.
23. **35 words**, `content/s15/s15-07-web-traffic-forecasting/lesson.md`: Strong answer: "I start with robust baselines: median of the last weeks, and a weekday-adjusted median, and I validate on the last 60 days with the metric, SMAPE, taking care of zeros and missing days.
24. **34 words**, `content/s5/s5-03-calendar-holidays-target-encoding/lesson.md`: Red flags: target mean computed on all data; random K-fold target encoding on time series; holiday features built from the test period's actual sales; not knowing why a single feature gives a perfect score.
25. **34 words**, `content/s7/s7-04-zero-shot-finetune-routers/lesson.md`: The M4 and M5 forecasting competitions showed that combinations of different methods were among the strongest approaches (the M4 winner combined exponential smoothing and neural networks; many top M5 entries combined several LightGBM models).
26. **34 words**, `content/s11/s11-03-deepar-gluonts-chronos/lesson.md`: Chronos is a pretrained foundation model: it scales and quantises values into tokens, trains a T5-style model with cross-entropy on a large corpus of real and synthetic series, and forecasts zero-shot by sampling tokens.
27. **34 words**, `content/s12/s12-07-how-to-pick-a-library/lesson.md`: The ecosystem changes fast, but the pattern in public benchmarks is stable: classical models are strong baselines, global boosting models do well with rich covariates, and combinations or AutoML ensembles are hard to beat.
28. **33 words**, `content/s3/s3-06-ma-arma-arima/lesson.md`: Strong answer: p is the number of past values used (AR part). d is the number of differences that make the series stationary. q is the number of past shocks used (MA part).
29. **33 words**, `content/s7/s7-02-chronos-family/lesson.md`: It uses an attention that works across the items in a group (a group attention), so a series can use information from related series and from covariates in the context itself ("in-context learning").
30. **33 words**, `content/s7/s7-05-benchmarking-honestly/lesson.md`: Create one internal benchmark: golden backtests built from your own series, frozen test periods that no model team may tune on, a champion/challenger rule, and a dated results table that anyone can re-run.
31. **33 words**, `content/s7/s7-06-llms-and-forecasting-agents/lesson.md`: People ask: "Can I just give my sales table to an LLM and ask for a forecast?" And: "Can an LLM agent run the whole forecasting workflow?" The honest answer has two parts.
32. **33 words**, `content/s7/s7-06-llms-and-forecasting-agents/lesson.md`: Specialized time series foundation models (Chronos, TimesFM, Moirai; lessons 2 and 3) are trained on series, are much smaller than general LLMs, and are the usual choice when you want a pre-trained forecaster.
33. **33 words**, `content/s7/s7-06-llms-and-forecasting-agents/lesson.md`: The agent proposes, but a fixed harness decides by backtest against seasonal naive, all numbers come from tool outputs, I log every step, and I add a fallback and protection against prompt injection.
34. **33 words**, `content/s7/s7-07-when-not-to-use/lesson.md`: I would add two or three foundation models zero-shot on the same time-based backtest, with MASE and a quantile metric, and add cost per 1,000 forecasts, latency, explainability needs, data policy and license.
35. **33 words**, `content/s11/s11-05-uber-forecasting-orbit/lesson.md`: Strong answer: A Bayesian structural model has the same ingredients as exponential smoothing, level, trend and season, but it gives a distribution for the parameters and the forecast, so intervals include parameter uncertainty.
36. **33 words**, `content/s11/s11-06-zillow-offers-2021/lesson.md`: If you buy 1 000 houses at prices based on a forecast with a 5% typical error, and your profit margin per house is 2% to 3%, then error is larger than margin.
37. **33 words**, `content/s12/s12-03-scikit-learn-for-ts/lesson.md`: Most real forecasting systems at large scale are machine learning on a table: lag features in columns, a gradient-boosting model, and a good validation scheme. scikit-learn is the standard Python toolkit for that.
38. **33 words**, `content/s12/s12-06-more-libraries/lesson.md`: If the anomalies are unusual shapes and not just big values, I compute the matrix profile with stumpy and look at the largest values (discords), choosing the window length from the pattern length.
39. **32 words**, `content/s4/s4-03-point-metrics/lesson.md`: Red flags: "MAPE is the standard so I always use it"; not knowing what happens at y = 0; computing the MASE scale on test data; comparing RMSE of series with different units.
40. **32 words**, `content/s5/s5-04-target-transforms-scaling/lesson.md`: Red flags: one global scaler; scaling before the split; forgetting the inverse transform; using CODE on zeros; explaining the log transform as "it makes the data normal" without mentioning growth and variance.

Note: the lint is sentence-split with a regex, so a few counts may be off by one. The sentences above were read from the source.

---

## 3. Glossary (check 3)

- Terms in the built bundle: 356 (`site/data/content.js`, `counts.glossary`).
- Links in prose: 622 `[[term]]` links across lessons and problems. **All resolve** (the build lowercases and matches case-insensitively). Lesson and problem links: 0 broken.
- Missing `simple` field: 0.
- Definitions over 30 words: 1. `newsvendor problem`, 31 words (`content/s10/glossary.s10.json:102`).
- Terms defined in no lesson or problem: 15. Dead entries.
- **Terms defined in two stage files with different wording: 32.** The build keeps the first definition, so a learner sees whichever file loads first. In the served bundle, `mad` is the s10 version.

Meaning conflicts (blocking):

- **MAD.** `content/s10/glossary.s10.json:74-76` says "Mean absolute deviation ... Same as MAE." `content/s8/glossary.s8.json:18-20` says "Median absolute deviation." The S8 robust z-score lesson (`content/s8/s8-01-point-anomalies/lesson.md:48-53`) needs the median version. The bundle serves the wrong one. `content/s10/s10-04-forecast-error-alerts/lesson.md:37` also uses "MAD (mean absolute deviation, same as MAE)" as a term.

Other differences to unify (wording is different but meaning is the same, so these are not blocking):

- `timestamp`: s0 says "One moment in time ... as a pandas object"; s9 (`content/s9/glossary.s9.json:118`) says "A number or text that says when an event happened." The s9 one is imprecise.
- `downsampling`: s1 says "coarser time step"; s9 says "reducing the number of points ... to draw a chart". Different scope.
- Also differing: `EWMA`, `STL`, `stationary`, `ACF`, `PACF`, `ARIMA`, `backtest`, `Prophet`, `foundation model`, and about 20 more. List: `content/s*/glossary*.json` with a duplicate key.

---

## 4. Facts spot-check (check 4)

I checked 81 lines in "Real world" sections that contain a year, percentage or number, and read the company and project claims. I had no web access, so this is a check against my knowledge, not a web verification. Nothing looked invented. Examples I confirmed:

- Pandas started at AQR Capital in 2008 (`s0-03`).
- M4 has 100,000 series (`s1-01`, `s4-06`).
- Prophet paper: Taylor and Letham, 2018, with a 2017 preprint (`s11-02`).
- Granger 1969 in Econometrica; Granger and Engle shared the 2003 Nobel (`s2-04`, `s2-06`).
- Box and Jenkins 1970; Holt 1957; Winters 1960 (`s3-04`, `s3-06`, `s12-02`).
- PELT 2012 in JASA (`s8-04`); ROCKET 2020 and MiniRocket 2021 (`s8-07`); matrix profile 2016 (`s8-08`).
- Welford 1962 in Technometrics (`s9-01`); SQLite window functions from 3.25 (`s9-08`).
- Zillow Offers: a $304M Q3 2021 inventory write-down and a workforce cut of about a quarter (`s11-06`). The lesson limits itself to public facts, which is correct.

Flags (low risk, for the author to decide):

- `content/s6/s6-07-transformers-for-ts/lesson.md:27`: "2026 trend: the building blocks of PatchTST (patches) are inside most time series foundation models in stage 7." This is an unsourced generalization. Either cite it or soften it to "several".
- `content/s9/glossary.s9.json:118`: "timestamp" as "a number or text" is imprecise (see section 3).

---

## 5. Browser smoke (check 5)

**Setup.** Playwright with Chromium, served from `http://localhost:8765/`. Four combinations: desktop 1280x900 and mobile 360x740, each in light and dark. Ten lessons chosen with a fixed seed (20261025): s5-08, s1-03, s9-03, s14-02, s6-07, s10-05, s11-02, s0-03, s1-04, s3-01.

**Coverage.**

- Lessons: 40 walks (10 per combination), 544 steps total. Every walk reached "Finish".
- Quick checks: 200 "Check answer" clicks.
- Problems: reference solutions for `total-by-day` and `mean-of-valid-readings` were pasted, run and submitted. Submit returned "Accepted" on desktop light and dark. Starter code returned "Wrong Answer" on desktop. On mobile, the editor sits behind the "Code" tab, so the tab must be clicked first. That is the designed behaviour, not a bug. The first smoke pass logged "no editor" on mobile for this reason. The mobile workspace was then checked separately in light mode only (Run and Submit both correct). The mobile-dark workspace was not exercised.
- Pages: Path, Problems (149 rows), Review, Mock OA (start and run page, with timer), Drills (and a drill page), Glossary, Progress, Settings, Playground. All rendered.
- Run and Submit check, done separately (`ws.js`): Run shows "All sample cases passed, 2 / 2". Submit shows "Accepted". No page errors on either viewport.

**Errors and network.**

- JavaScript errors: 0. Console warnings: 0.
- HTTP 404 on `/engine/split.json` on each Python load. The worker fetches it on purpose and tolerates the 404 (`site/engine/worker.js:53`), so it is noise, not a bug.
- No other 4xx or 5xx, no failed requests.

**Overflow.** `scrollWidth > innerWidth` was never true on any step, page or modal at 1280 or 360 px.

**Bad text.** Searched the main content for `undefined`, `NaN`, `null` and `[object Object]`. None of `undefined` or `[object Object]` appeared.

- `NaN` (18 per combination) is legitimate pandas content.
- `null` (10 per combination, 40 total) is a real bug: the literal word "null" shows on every lesson's Finish screen. The cause is `site/js/pages/lesson.js:123-126`: `foot.append(..., next ? h(...) : null)`. DOM `append()` turns `null` into the text "null" when there is no next step.

**Visual review.** I looked at 12 screenshots in full. The rest are in the folder.

- Problem list, Path, lesson steps, workspace, Mock OA run, glossary, progress and settings all look correct in both themes and at 360 px.
- Real visual bugs: the "null" text beside the Back button on the Finish screen (all lessons, both themes, both viewports).
- Minor: the "+20 XP" toast covers the bottom of the content on several screens (lesson finish, problem solved, Mock OA). It is transient, but it hides text and buttons near the bottom.
- The Path stage chips scroll horizontally inside their strip. This looks intentional. The last visible chip is cut off, which is expected for a scroll strip.

Screenshot folder (39 files): `/tmp/claude-0/-home-user-learn-time-series/19bf3dde-e717-5f0a-90bd-65fb895cab5c/scratchpad/review/shots/`. Scripts: `smoke.js`, `ws.js` in the same folder. Raw results: `smoke.json`.

---

## 6. Static-host check (check 6)

- No root-relative (`/...`) URLs in `src`, `href`, `fetch`, `import` or `url()` in `site/`. Routes are hash-based (`#/lesson/...`).
- All script and stylesheet references in `site/index.html` are relative. The worker is `new Worker('engine/worker.js')` (`site/js/judge.js:17`). The worker loads `pyodide.js`, `harness.py` and `split.json` relative to its own URL (`site/engine/worker.js:5-7`, `53`, `83`) and calls `loadPyodide({ indexURL: BASE })` (`:80`).
- External requests: Google Fonts only, in `site/index.html:10-13`. It is optional and the page falls back. The string `cdn.jsdelivr.net/pyodide` appears inside the vendored `engine/pyodide.js`, but the worker sets `indexURL` to the local path, so the CDN is not used at runtime.
- The Pages workflow publishes `site/` as the site root (`.github/workflows/pages.yml`), so relative paths work under a project subpath.

---

## 7. Not covered

- `tools/build.py` was not re-run, because it writes `site/data/content.js`. The bundle was read instead. The PLAN status says the build was clean and 149 of 149 reference solutions were accepted in the engine. I did not re-verify that. I checked 2 problems in the browser.
- The quiz and card prose was not measured for sentence length. The idiom check did cover it.
- No web access, so facts were checked against knowledge, not sources.

---

## 8. Nice to have (9)

1. `/engine/split.json` 404 on every Python load (`site/engine/worker.js:53`). Add an empty `engine/split.json` (`{}`) or skip the fetch when the file is missing.
2. `newsvendor problem` glossary definition is 31 words (`content/s10/glossary.s10.json:102`). Cut to 30.
3. The "Strong answer" paragraph in `s14-10-staff-system-design-interview` is 134 words. Split it.
4. 15 glossary terms are never linked from any lesson or problem. Either link them or drop them.
5. Secondary phrasal verbs: "find out" (3), "set up" (2), "go through" (1). Replace with simple verbs.
6. Overuse: "very" 55, "just" 23, "clearly" 7, "really" 6. Not rule violations, but a light edit would help.
7. The transient "+20 XP" toast covers the bottom of content. Move it above the footer or shorten its time.
8. The Playground page has no `h1` or `h2`. Add a heading for screen readers.
9. S11 "open-source map" bullet is only in S12. Add a cross-link from `s11-08` or the S11 index.

---

## 9. Prioritized fix list

1. **Stray "null" on every Finish screen.** Fix `site/js/pages/lesson.js:123-126`: use `h('span')` instead of `null` as the second argument to `foot.append`. Affects 127 lessons. One line.
2. **MAD definition.** Rename or remove the s10 entry at `content/s10/glossary.s10.json:74-76` (say "MAE" there). Keep the median definition in `content/s8/glossary.s8.json:18-20`. Change `content/s10/s10-04-forecast-error-alerts/lesson.md:37` to use MAE. Re-run the build and check that `mad` in `site/data/content.js` matches the s8 text.
3. **Replace the 21 idioms.** "rule of thumb" becomes "common guideline"; "deep dive" becomes "in-depth question"; "under the hood" becomes "internally". Locations are in section 2.
4. **Sentences over 20 words (593).** Start with the 214 over 25 words, and the lessons `s7-06`, `s15-07`, `s6-08`, `s11-03`, `s15-03`. Add the sentence-length check to `tools/build.py` as a warning so it stays in place.
5. **Concept chunks over 150 words (42).** Split the largest first: `s10-06`, `s14-07`, `s3-10`, `s3-09`, `s7-02`.
6. **Duplicate glossary definitions (32 terms).** Keep one definition per term. Make the build fail on differing text, not just warn.
7. **Warm-up checks.** Add a second check to the 16 lessons that have one (S13 six, S14 nine, s15-03). Or change DESIGN §1.2 if one is enough.
8. **s13-02 quiz and cards.** Confirm the 23-question quiz and 42 cards are intentional. If so, document the exception in CONTENT_GUIDE.
9. **404 on `split.json`.** Add an empty file or skip the fetch (see nice-to-have 1).
10. **Small text fixes.** Cut the newsvendor definition to 30 words. Split the 134-word paragraph in `s14-10`. Add an S11 cross-link to the open-source map.

---

## Appendix: reproduce

Scripts and outputs are in `/tmp/claude-0/-home-user-learn-time-series/19bf3dde-e717-5f0a-90bd-65fb895cab5c/scratchpad/review/`:

- `lint.py` (writes `lint.json`, `lint.txt`): plain-English lint
- `gloss3.py`, `gconf.py`: glossary links and duplicate definitions
- `coverage.py`: curriculum term coverage
- `realworld.py`: numeric claims in Real world sections (`realworld_nums.txt`)
- `smoke.js` (writes `smoke.json`), `ws.js`: browser smoke
- `shots/`: 39 screenshots
