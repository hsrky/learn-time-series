---
id: s12-05-frameworks
title: Forecasting frameworks: Darts, sktime and aeon, GluonTS, AutoGluon-TimeSeries
minutes: 30
level: intermediate
goals: [Describe what Darts, sktime, aeon, GluonTS and AutoGluon-TimeSeries are for, Recognise their basic code patterns, Choose a framework for a task]
prereqs: [s12-04-nixtla-stack]
tags: [darts, sktime, aeon, gluonts, autogluon, chronos]
skills: [forecasting-libraries]
---

## Warm-up

```check
{"q": "Which columns does the Nixtla long format use?", "type": "single",
 "options": ["unique_id, ds, y", "date, value", "id, label"],
 "answer": 0,
 "why": ["Correct.", "Too few: no series name.", "No time column."]}
```

```check
{"q": "What does hierarchicalforecast do?", "type": "single",
 "options": ["Reconciles forecasts across levels", "Trains LightGBM", "Calls an API"],
 "answer": 0,
 "why": ["Correct.", "That is mlforecast.", "That is the TimeGPT client."]}
```

## Why it matters

A **[[framework]]** gives you one interface for many models, plus backtesting, metrics and data handling. It saves time when you compare ideas. Each framework has its own data object and style, so learn the pattern of each. All code here is **notebook** code (libraries are not available in the browser). Argument names change between versions: always check the current documentation.

## Darts

**[[Darts]]** (Unit8) has one API for classical, ML and deep models. Data goes into a `TimeSeries` object. Models have `.fit()` and `.predict(n)`. It supports **global models** trained on many series, probabilistic forecasts, covariates and **historical forecasts** (backtesting).

```notebook
from darts import TimeSeries
from darts.models import ExponentialSmoothing, LightGBMModel
from darts.metrics import mae

series = TimeSeries.from_dataframe(df, time_col="ds", value_cols="y", freq="D")
train, val = series[:-14], series[-14:]

ets = ExponentialSmoothing()
ets.fit(train)
print("ETS MAE:", mae(val, ets.predict(14)))

gbm = LightGBMModel(lags=14, output_chunk_length=14)
gbm.fit(train)
print("LightGBM MAE:", mae(val, gbm.predict(14)))

# backtest: retrain at each step, forecast 7 days
bt = ets.historical_forecasts(series, start=0.8, forecast_horizon=7, stride=7, retrain=True)
```

## sktime and aeon

**[[sktime]]** is a scikit-learn-style toolkit for time series: forecasting, classification, clustering, annotation. Its forecasters have `fit(y, fh=...)` and `predict(fh)`, where `fh` is the **[[forecasting horizon]]**. It has **reduction** (turn forecasting into regression with a scikit-learn model), pipelines and tuning.

```notebook
import numpy as np
from sktime.forecasting.base import ForecastingHorizon
from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.compose import make_reduction
from sklearn.ensemble import HistGradientBoostingRegressor

fh = ForecastingHorizon(np.arange(1, 15), is_relative=True)
naive = NaiveForecaster(strategy="last", sp=7).fit(y_train)
pred_naive = naive.predict(fh)

gbm = make_reduction(HistGradientBoostingRegressor(early_stopping=False), window_length=14, strategy="recursive")
pred_gbm = gbm.fit(y_train).predict(fh)
```

**[[aeon]]** is a toolkit that grew out of sktime (a fork). It focuses on time series **machine learning**: classification, clustering, regression, distances (DTW), and anomaly detection. Use it when the task is not "forecast the next values" but "classify this series".

## GluonTS

**GluonTS** (Amazon) is a toolkit for **probabilistic** forecasting with deep models such as DeepAR, plus tools for quantile metrics. It trains one model across many series.

```notebook
from gluonts.dataset.pandas import PandasDataset
from gluonts.torch import DeepAREstimator

ds = PandasDataset.from_long_dataframe(df, item_id="unique_id", timestamp="ds", target="y", freq="D")
est = DeepAREstimator(prediction_length=14, freq="D", trainer_kwargs={"max_epochs": 10})
predictor = est.train(ds)
forecasts = list(predictor.predict(ds))
q90 = forecasts[0].quantile(0.9)        # 90% quantile of the first series
```

## AutoGluon-TimeSeries (with Chronos)

**AutoGluon-TimeSeries** is an **[[AutoML]]** library: it trains many models and **ensembles** them, with a time limit. The models include naive, ETS, ARIMA, boosting, deep models and Chronos. You give data and a horizon.

```notebook
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

data = TimeSeriesDataFrame.from_data_frame(df, id_column="unique_id", timestamp_column="ds")
predictor = TimeSeriesPredictor(prediction_length=14, target="y", eval_metric="MASE")
predictor.fit(data, presets="medium_quality", time_limit=600)   # presets also include Chronos-based ones
print(predictor.leaderboard(data))        # models ranked on a validation window
preds = predictor.predict(data)           # mean and quantile columns
```

It is a strong choice when you want a good result fast. The price is less control and more compute.

```chart
{"title": "Illustration: an ensemble of different models", "x": "day", "height": 220,
 "series": [
   {"name": "actual", "gen": [["trend", {"start": 40, "slope": 0.15}], ["season", {"period": 7, "amp": 6}], ["noise", {"sd": 2}]], "n": 70, "seed": 41},
   {"name": "pattern", "gen": [["trend", {"start": 40, "slope": 0.15}], ["season", {"period": 7, "amp": 6}]], "n": 70, "dash": true}
 ],
 "caption": "AutoML libraries train many models on the same data and combine them, because combinations are strong (see the M4 lesson)."}
```

```check
{"q": "Which tool is an AutoML library for time series that can ensemble many models and use Chronos?", "type": "single",
 "options": ["AutoGluon-TimeSeries", "aeon", "stumpy", "river"],
 "answer": 0,
 "why": ["Correct.", "aeon is a time series ML toolkit.", "stumpy computes the matrix profile.", "river does online learning."]}
```

## Worked example

A decision example, in code form: compare two frameworks on the same split and pick by backtest. This is a plan, not a result.

```notebook
# Plan: one dataset, one split, one metric, several frameworks
# 1) Baseline: SeasonalNaive (statsforecast or sktime NaiveForecaster)
# 2) Classical: ExponentialSmoothing (Darts) or AutoETS (statsforecast)
# 3) Global ML: LightGBMModel (Darts) or MLForecast
# 4) AutoML: TimeSeriesPredictor with a 10-minute limit
# Evaluate each on the same 3 rolling windows with MASE. Keep the simplest model within 3% of the best.
```

## Common mistakes

- Choosing a framework by popularity, not by the task.
- Comparing frameworks with different splits or metrics.
- Using AutoML as a black box: look at the leaderboard and check for leakage.
- Mixing up sktime and aeon APIs after reading old tutorials.
- Running deep models on a handful of series.

## Interview lens

**Typical question:** "Which libraries do you know for forecasting, and when would you use each?"

**Strong answer:** For quick classical baselines I use statsmodels or statsforecast. Darts and sktime give one interface for many models and backtesting. Like aeon, sktime also covers classification and clustering of series. GluonTS is for probabilistic deep models like DeepAR. AutoGluon-TimeSeries is an AutoML option that ensembles many models and includes Chronos, good for a strong first result. Whatever I use, I fix a rolling backtest and compare with seasonal naive.

**Red flags:** Listing names without use cases. Never comparing with a baseline.

## Real world

Darts is open source from the company Unit8. sktime is a community project with a large contributor base. GluonTS and AutoGluon come from Amazon. aeon is a community toolkit. All are public on GitHub. Their documentation has tutorials for each pattern above.

## Key points

- Darts: `TimeSeries`, many models, global models, historical forecasts.
- sktime: scikit-learn style, forecasting horizon, reduction. aeon: time series ML (classification, clustering, distances).
- GluonTS: probabilistic deep forecasting. AutoGluon-TimeSeries: AutoML ensembles, includes Chronos presets.
- Compare frameworks on the same rolling backtest and the same metric.
