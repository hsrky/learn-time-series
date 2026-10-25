# WP6 status: S8 Anomalies, change & other tasks; S9 Streaming & algorithms

Validation: `tools/check_problem.py content/s8 content/s9` -> 28/28 problems ok. Worked-example outputs were produced by running the code. All quiz/check `why` lists match option counts.

## Lessons

| Lesson | Status | Problems |
|---|---|---|
| s8-01-point-anomalies | ✅ | 2 |
| s8-02-seasonal-anomalies | ✅ | 1 |
| s8-03-cusum | ✅ | 1 |
| s8-04-segmentation-pelt | ✅ | 1 |
| s8-05-isolation-forest-reconstruction | ✅ | 1 |
| s8-06-evaluating-detectors | ✅ | 1 |
| s8-07-classification-dtw-rocket | ✅ | 1 |
| s8-08-similarity-matrix-profile | ✅ | 1 |
| s9-01-online-statistics | ✅ | 1 |
| s9-02-sliding-window-extrema | ✅ | 2 |
| s9-03-moving-median | ✅ | 2 |
| s9-04-ewma-rate-limiting | ✅ | 2 |
| s9-05-buckets-sessions | ✅ | 3 |
| s9-06-gaps-and-islands | ✅ | 2 |
| s9-07-downsampling-lttb | ✅ | 1 |
| s9-08-sql-window-functions | ✅ | 3 |
| s9-09-sql-islands-fill-first | ✅ | 3 |

## Problems

| Problem | Lesson | Difficulty | Type | Status | check_problem |
|---|---|---|---|---|---|
| robust-z-scores | s8-01-point-anomalies | Easy | function | ✅ | ok |
| rolling-zscore-anomalies | s8-01-point-anomalies | Easy | function | ✅ | ok |
| generalized-esd | s8-02-seasonal-anomalies | Hard | function | ✅ | ok |
| cusum-detector | s8-03-cusum | Medium | function | ✅ | ok |
| binary-segmentation | s8-04-segmentation-pelt | Hard | function | ✅ | ok |
| window-isolation-forest | s8-05-isolation-forest-reconstruction | Medium | function | ✅ | ok |
| event-precision-recall | s8-06-evaluating-detectors | Medium | function | ✅ | ok |
| dtw-distance-window | s8-07-classification-dtw-rocket | Medium | function | ✅ | ok |
| znorm-subsequence-search | s8-08-similarity-matrix-profile | Medium | function | ✅ | ok |
| welford-running-stats | s9-01-online-statistics | Medium | class | ✅ | ok |
| longest-stable-window | s9-02-sliding-window-extrema | Hard | function | ✅ | ok |
| sliding-window-maximum | s9-02-sliding-window-extrema | Medium | function | ✅ | ok |
| moving-median | s9-03-moving-median | Hard | class | ✅ | ok |
| streaming-median | s9-03-moving-median | Medium | class | ✅ | ok |
| streaming-ewma | s9-04-ewma-rate-limiting | Easy | class | ✅ | ok |
| token-bucket | s9-04-ewma-rate-limiting | Medium | class | ✅ | ok |
| sessionize-events | s9-05-buckets-sessions | Medium | function | ✅ | ok |
| sessionize-pandas | s9-05-buckets-sessions | Medium | function | ✅ | ok |
| time-bucket-counts | s9-05-buckets-sessions | Easy | function | ✅ | ok |
| login-islands-pandas | s9-06-gaps-and-islands | Medium | function | ✅ | ok |
| longest-login-streak | s9-06-gaps-and-islands | Easy | function | ✅ | ok |
| lttb-downsample | s9-07-downsampling-lttb | Hard | function | ✅ | ok |
| sql-day-over-day | s9-08-sql-window-functions | Easy | sql | ✅ | ok |
| sql-moving-average-7d | s9-08-sql-window-functions | Medium | sql | ✅ | ok |
| sql-running-total-by-group | s9-08-sql-window-functions | Medium | sql | ✅ | ok |
| sql-fill-missing-dates | s9-09-sql-islands-fill-first | Medium | sql | ✅ | ok |
| sql-first-event-per-user | s9-09-sql-islands-fill-first | Medium | sql | ✅ | ok |
| sql-login-islands | s9-09-sql-islands-fill-first | Hard | sql | ✅ | ok |

Totals: S8 = 8 lessons, 9 problems; S9 = 9 lessons, 19 problems.

Notes:
- Widgets `anomaly-zscore` (s8-01) and `sliding-window` (s9-02) are referenced with simple params; params may need alignment with site/js/widgets.js when it exists.
- `generalized-esd` uses packages: [scipy]; `window-isolation-forest` uses packages: [scikit-learn].
- Lesson worked examples in s8-02 (statsmodels STL) and s8-05 (scikit-learn) use libraries available in the venv but are not run in the browser.
