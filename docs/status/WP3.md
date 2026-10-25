# WP3 status: s2 + s3

Legend: ⬜ todo, 🟨 in progress, ✅ done. Problem check = `tools/check_problem.py` result (reference passes all cases, starter fails).

Lesson check = scratch validator: front matter, section order, JSON blocks, `why` per option, quiz 5-8 questions with scenarios, 4-8 cards, glossary terms, every worked-example `# Output:` re-run and matched. `tools/build.py` on a copy: 0 errors, 0 warnings for s2/s3 (duplicate-glossary warnings from other stages are not caused by missing terms).

## s2 Statistics of time (6 lessons, 9 problems)
| Item | Status | Check |
|---|---|---|
| s2-01-white-noise-random-walk (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem random-walk-forecast-interval | ✅ | ok |
| s2-02-stationarity-transforms (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem seasonal-difference | ✅ | ok |
| - problem box-cox-transform | ✅ | ok |
| s2-03-acf-pacf (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem acf-from-scratch | ✅ | ok |
| - problem pacf-durbin-levinson | ✅ | ok |
| - problem ar-order-from-pacf | ✅ | ok |
| s2-04-unit-root-adf-kpss (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem unit-root-verdict (statsmodels) | ✅ | ok |
| s2-05-spurious-regression-cross-correlation (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem cross-correlation-lag | ✅ | ok |
| s2-06-granger-causality (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem granger-f-statistic | ✅ | ok |

## s3 Classical forecasting (10 lessons, 22 problems)
| Item | Status | Check |
|---|---|---|
| s3-01-baselines (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem baseline-forecasts | ✅ | ok |
| - problem baseline-leaderboard | ✅ | ok |
| s3-02-simple-exponential-smoothing (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem simple-exp-smoothing | ✅ | ok |
| - problem ses-fit-alpha | ✅ | ok |
| s3-03-holt-trend-damped (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem holt-damped | ✅ | ok |
| s3-04-holt-winters-ets (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem holt-winters | ✅ | ok |
| s3-05-autoregression (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem ar-least-squares | ✅ | ok |
| - problem ar-recursive-forecast | ✅ | ok |
| s3-06-ma-arma-arima (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem integrate-forecast | ✅ | ok |
| - problem ma-invertibility | ✅ | ok |
| s3-07-sarima-model-selection (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem ljung-box-q | ✅ | ok |
| - problem aic-bic-rank | ✅ | ok |
| - problem sarimax-forecast (statsmodels) | ✅ | ok |
| s3-08-regression-fourier-holidays (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem fourier-features | ✅ | ok |
| - problem holiday-dummies | ✅ | ok |
| - problem trend-fourier-forecast | ✅ | ok |
| s3-09-intermittent-demand (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem croston-forecast | ✅ | ok |
| - problem tsb-forecast | ✅ | ok |
| - problem demand-classification | ✅ | ok |
| s3-10-hierarchical-reconciliation (lesson, quiz, cards) | ✅ | lesson ok, outputs verified |
| - problem summing-matrix | ✅ | ok |
| - problem top-down-proportions | ✅ | ok |
| - problem ols-reconcile | ✅ | ok |

## Notes
- Problems that use statsmodels declare `packages: [statsmodels]`: unit-root-verdict, sarimax-forecast. sarimax-forecast uses short quarterly series and at most 2 candidates, so it stays fast in the browser.
- pacf-durbin-levinson matches `statsmodels pacf(method='ywm')`, acf-from-scratch matches `acf(fft=False)`, granger-f-statistic matches `ssr_ftest`, ljung-box-q matches `acorr_ljungbox`.
- Glossary: content/s2/glossary.s2.json (26 terms), content/s3/glossary.s3.json (45 terms).
