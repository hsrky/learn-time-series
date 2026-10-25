# WP2 status: S0 Toolkit bootcamp + S1 Foundations

Legend: ✅ done. `check_problem.py` result in the last column. All 22 problems: ok.
Validation: lesson python blocks run and "# Output:" matches; JSON parses; every check/quiz option has a `why`;
every [[term]] is in `content/s0/glossary.s0.json` or `content/s1/glossary.s1.json`.

## Stage s0 (5 lessons, 11 problems; minimum 5 / 8)

| Lesson | Status | Problems | check_problem |
|---|---|---|---|
| s0-01-python-for-data (welcome + how the portal works) | ✅ | mean-of-valid-readings (Easy), total-by-day (Easy) | ok, ok |
| s0-02-numpy-vectorization | ✅ | zscore-columns (Easy), mask-spikes (Easy) | ok, ok |
| s0-03-pandas-series-dataframe | ✅ | combine-reports (Easy), big-sellers (Easy) | ok, ok |
| s0-04-datetime-timezones | ✅ | utc-to-local-hours (Easy), hours-in-local-day (Easy) | ok, ok |
| s0-05-core-time-operations | ✅ | daily-totals (Easy), weekday-profile (Easy), lag-and-growth (Easy) | ok, ok, ok |

## Stage s1 (7 lessons, 11 problems; minimum 7 / 10)

| Lesson | Status | Problems | check_problem |
|---|---|---|---|
| s1-01-what-is-a-time-series | ✅ | missing-timestamps (Easy) | ok |
| s1-02-components | ✅ | linear-trend (Easy) | ok |
| s1-03-frequency-resampling | ✅ | carry-forward-daily (Easy), ohlc-bars (Medium) | ok, ok |
| s1-04-missing-data-imputation | ✅ | causal-fill (Medium), interpolate-by-time (Medium) | ok, ok |
| s1-05-lags-differences-returns | ✅ | log-returns (Easy), direct-dataset (Medium) | ok, ok |
| s1-06-rolling-ewma | ✅ | ewma-from-scratch (Medium), leak-free-zscore (Medium) | ok, ok |
| s1-07-decomposition | ✅ | classical-decomposition (Hard; reference matches statsmodels seasonal_decompose on 14 test series) | ok |

## Notes for integration (WP1/WP9)
- Charts use per-series `x` with `y` (also `kind: dots` for points) and `gen` generators; some charts use series of different lengths/x ranges. Bar charts use `kind: bar`.
- Widgets used: `components` (s1-02, s1-07), `lag-features` (s1-05), `moving-average` with `{"window": 7}` (s0-05), `ses-alpha` with `{"alpha": 0.4}` (s1-06). Empty or minimal `params` are used where unsure.
- `data leakage` and `rolling window` are defined in both glossaries with the same meaning (examples differ slightly).
- Validator used locally: scratchpad `val.py` (sections order, JSON blocks, terms, outputs, sentence length lint).
