# WP7 status (s10, s11, s12)

Legend: ✅ done and validated, 🟨 in progress, ⬜ not started. Problem check = tools/check_problem.py.

## s10 Production & system design
| Item | Status | Notes |
|---|---|---|
| s10-01-point-in-time-correctness | ✅ | problem pit-join-asof: ok |
| s10-02-pipelines-and-retraining | ✅ | problem idempotent-forecast-upsert: ok |
| s10-03-drift-monitoring | ✅ | problem psi-drift-score: ok |
| s10-04-forecast-error-alerts | ✅ | problem tracking-signal-alert: ok |
| s10-05-forecasting-at-scale | ✅ | |
| s10-06-forecasts-into-decisions | ✅ | problem newsvendor-order: ok |
| s10-07-design-demand-forecasting | ✅ | drill.json |
| s10-08-design-anomaly-platform | ✅ | drill.json |
| s10-09-design-capacity-eta | ✅ | drill.json |

## s11 Case studies
| Item | Status | Notes |
|---|---|---|
| s11-01-m-competitions | ✅ | problem m4-owa: ok |
| s11-02-prophet-at-facebook | ✅ | problem piecewise-linear-trend: ok |
| s11-03-deepar-gluonts-chronos | ✅ | |
| s11-04-timesfm-foundation-models | ✅ | |
| s11-05-uber-forecasting-orbit | ✅ | |
| s11-06-zillow-offers-2021 | ✅ | public facts only |
| s11-07-kaggle-competitions | ✅ | |
| s11-08-anomaly-detection-at-large-companies | ✅ | problem esd-outlier-test: ok (scipy) |

## s12 Library tour
| Item | Status | Notes |
|---|---|---|
| s12-01-statsmodels | ✅ | problems adf-differencing-order, acf-dominant-season: ok |
| s12-02-statsmodels-models | ✅ | problem ets-forecast-beats-naive: ok |
| s12-03-scikit-learn-for-ts | ✅ | problems ridge-lag-backtest-gap, hgb-recursive-forecast: ok |
| s12-04-nixtla-stack | ✅ | notebook code |
| s12-05-frameworks | ✅ | notebook code |
| s12-06-more-libraries | ✅ | notebook code |
| s12-07-how-to-pick-a-library | ✅ | decision tables |

Validation: check_problem 14/14 ok for s10-s12 (use OMP_NUM_THREADS=1 for the HGB problem); build.py --strict has no errors in s10-s12.
