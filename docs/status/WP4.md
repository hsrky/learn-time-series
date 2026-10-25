# WP4 status — S4 Evaluation & backtesting, S5 Machine learning for TS

Legend: ✅ done. Validation: `check_problem.py` = ok for every problem (23/23). Lessons: sections, checks, quiz, cards, glossary, worked-example outputs verified with a local lint script (0 errors).

## Lessons

| Lesson | Min | Problems | Status |
|---|---|---|---|
| s4-01-time-split-and-leakage — Time-based split and data leakage | 25 | time-based-split, train-only-scaler | ✅ |
| s4-02-backtesting — Backtesting with walk-forward windows | 30 | backtest-splits, walk-forward-mae | ✅ |
| s4-03-point-metrics — Point forecast metrics | 30 | forecast-metrics-suite, mase-rmsse | ✅ |
| s4-04-probabilistic-forecasts — Quantiles, intervals and pinball loss | 30 | interval-score-coverage, pinball-loss | ✅ |
| s4-05-conformal-prediction — Conformal prediction for time series | 30 | rolling-conformal, split-conformal-interval | ✅ |
| s4-06-comparing-models — Comparing models fairly | 30 | diebold-mariano-stat, model-rank-comparison | ✅ |
| s5-01-reduction-to-supervised — Turning a series into a supervised table | 25 | make-windows | ✅ |
| s5-02-lag-and-rolling-features — Lag and rolling features without leakage | 30 | leakage-free-features | ✅ |
| s5-03-calendar-holidays-target-encoding — Calendar, holiday and event features, and the target encoding trap | 30 | calendar-features, expanding-target-encoding | ✅ |
| s5-04-target-transforms-scaling — Target transforms and per-series scaling | 25 | per-series-scaler | ✅ |
| s5-05-multistep-strategies — Multi-step strategies: recursive, direct, MIMO and hybrid | 30 | direct-forecast-lstsq, recursive-forecast-lstsq | ✅ |
| s5-06-global-vs-local-models — Global and local models | 25 | global-ar-forecast | ✅ |
| s5-07-gradient-boosting-in-practice — Gradient boosting in practice (LightGBM and XGBoost ideas) | 35 | hgb-lag-forecast | ✅ |
| s5-08-exogenous-and-known-future — Exogenous variables, known-future covariates and point-in-time joins | 30 | point-in-time-join | ✅ |
| s5-09-cold-start-and-new-series — Cold start: forecasting new series | 25 | cold-start-analog-forecast | ✅ |

## Problems (check_problem.py)

| Problem | Stage | Difficulty | Result |
|---|---|---|---|
| time-based-split | s4 | Easy | ✅ ok |
| train-only-scaler | s4 | Easy | ✅ ok |
| backtest-splits | s4 | Medium | ✅ ok |
| walk-forward-mae | s4 | Medium | ✅ ok |
| forecast-metrics-suite | s4 | Medium | ✅ ok |
| mase-rmsse | s4 | Medium | ✅ ok |
| interval-score-coverage | s4 | Medium | ✅ ok |
| pinball-loss | s4 | Easy | ✅ ok |
| rolling-conformal | s4 | Hard | ✅ ok |
| split-conformal-interval | s4 | Medium | ✅ ok |
| diebold-mariano-stat | s4 | Hard | ✅ ok |
| model-rank-comparison | s4 | Medium | ✅ ok |
| make-windows | s5 | Easy | ✅ ok |
| leakage-free-features | s5 | Medium | ✅ ok |
| calendar-features | s5 | Medium | ✅ ok |
| expanding-target-encoding | s5 | Medium | ✅ ok |
| per-series-scaler | s5 | Medium | ✅ ok |
| direct-forecast-lstsq | s5 | Medium | ✅ ok |
| recursive-forecast-lstsq | s5 | Medium | ✅ ok |
| global-ar-forecast | s5 | Medium | ✅ ok |
| hgb-lag-forecast | s5 | Hard | ✅ ok |
| point-in-time-join | s5 | Medium | ✅ ok |
| cold-start-analog-forecast | s5 | Medium | ✅ ok |

## Totals

- S4: 6 lessons, 12 problems.
- S5: 9 lessons, 11 problems (one uses `packages: [scikit-learn]`: hgb-lag-forecast).
- Glossary: content/s4/glossary.s4.json, content/s5/glossary.s5.json. Also uses terms defined by other stages: lag, window, residual, sliding window, least squares, autocorrelation, data leakage, global model, local model, cold start, newsvendor problem, training-serving skew, feature store, foundation model, zero-shot.
- Widgets used: train-test-split (s4-01), walk-forward (s4-02), quantile-loss (s4-04), conformal (s4-05), lag-features (s5-02).
- Note: run `check_problem.py` with `OMP_NUM_THREADS=1` when the machine is busy (scikit-learn threads).
