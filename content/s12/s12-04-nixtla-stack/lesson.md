---
id: s12-04-nixtla-stack
title: The Nixtla stack: statsforecast, mlforecast, neuralforecast, hierarchicalforecast, TimeGPT
minutes: 30
level: intermediate
goals: [Put data in the long format unique_id/ds/y, Use statsforecast and mlforecast for many series, Know what neuralforecast, hierarchicalforecast and TimeGPT are for]
prereqs: [s12-03-scikit-learn-for-ts]
tags: [nixtla, statsforecast, mlforecast, neuralforecast, hierarchicalforecast, timegpt]
skills: [forecasting-libraries, global-models]
---

## Warm-up

```check
{"q": "Why set early_stopping=False in HistGradientBoostingRegressor for time series?", "type": "single",
 "options": ["The automatic validation split is random, so it leaks time", "It is faster", "It removes NaN"],
 "answer": 0,
 "why": ["Correct.", "Speed is not the reason.", "It does not affect NaN."]}
```

```check
{"q": "A shifted rolling mean for time t should end at...", "type": "single",
 "options": ["t", "t-1", "t+1"],
 "answer": 1,
 "why": ["That includes the target.", "Correct.", "That is the future."]}
```

## Why it matters

Nixtla is a company and an open-source family of libraries built for **many series** and **speed**. They share one data format and one style. So you can try a classical model, a boosting model and a neural model on the same table. You will see them in many forecasting teams. The code on this page cannot run in the browser. It is shown as **notebook** code. Run it on your laptop or in a notebook service. Library versions change, so check the current documentation for exact argument names.

## The long format

All Nixtla libraries use a **[[long format|long]]** table with three standard columns:

| Column | Meaning |
|---|---|
| `unique_id` | the name of the series (store, product, sensor) |
| `ds` | the timestamp |
| `y` | the value to forecast |

Many series live in one DataFrame, stacked one below the other. Extra columns (price, holiday flag) are optional exogenous variables.

```notebook
import pandas as pd

df = pd.DataFrame({
    "unique_id": ["store_1"] * 4 + ["store_2"] * 4,
    "ds": list(pd.date_range("2024-01-01", periods=4, freq="D")) * 2,
    "y": [10, 12, 11, 13, 50, 48, 52, 51],
})
print(df.head())
```

```check
{"q": "Which table is in Nixtla long format?", "type": "single",
 "options": ["One row per day and one column per store", "Columns unique_id, ds, y with many series stacked", "A single list of numbers", "A 3D array"],
 "answer": 1,
 "why": ["That is the wide format.", "Correct.", "It has no series names or dates.", "The libraries expect a DataFrame."]}
```

## statsforecast: fast classical models

**[[statsforecast]]** runs ETS, ARIMA, Theta, seasonal naive and more on thousands of series. It uses compiled code (numba) and parallel workers. So it is much faster than fitting statsmodels models in a Python loop. Models: `AutoARIMA`, `AutoETS`, `AutoTheta`, `SeasonalNaive`, `Naive`, `HistoricAverage`.

```notebook
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS, SeasonalNaive

sf = StatsForecast(
    models=[SeasonalNaive(season_length=7), AutoETS(season_length=7), AutoARIMA(season_length=7)],
    freq="D",
    n_jobs=-1,                       # use all CPU cores
)
fcst = sf.forecast(df=df, h=14, level=[80, 95])     # columns: unique_id, ds, one column per model (+ intervals)

# rolling-origin backtest: 3 windows of 14 days
cv = sf.cross_validation(df=df, h=14, step_size=14, n_windows=3)
```

The output is again a long table. Always include `SeasonalNaive` as the baseline.

## mlforecast: boosting with lags

**[[mlforecast]]** builds lag features, rolling features and date features for many series, and trains any scikit-learn-style model (LightGBM, XGBoost, `HistGradientBoostingRegressor`). It also handles the **recursive** forecasting for you.

```notebook
import lightgbm as lgb
from mlforecast import MLForecast
from mlforecast.lag_transforms import RollingMean
from mlforecast.target_transforms import Differences

mlf = MLForecast(
    models=[lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, verbose=-1)],
    freq="D",
    lags=[1, 7, 14],
    lag_transforms={1: [RollingMean(window_size=7)]},     # mean of the last 7 values, ending at lag 1
    date_features=["dayofweek", "month"],
    target_transforms=[Differences([1])],                 # model the change; trees cannot extrapolate trends
)
mlf.fit(df)
preds = mlf.predict(14)
```

`Differences` is the answer to the "trees cannot extrapolate" problem from the previous lesson.

```check
{"q": "What does the lag transform RollingMean on lag 1 protect you from?", "type": "single",
 "options": ["Using the current value inside its own feature", "Missing values", "Slow training", "Seasonality"],
 "answer": 0,
 "why": ["Correct: the window is built from lag 1, so it ends at t-1.", "It does not fill missing values.", "It has no effect on speed.", "It does not model season."]}
```

## neuralforecast, hierarchicalforecast, TimeGPT

- **neuralforecast**: deep models for forecasting in the same long format, with PyTorch inside. It includes NBEATS, NHITS, PatchTST, TFT and DeepAR-style models. Use it with many series and enough data.

```notebook
from neuralforecast import NeuralForecast
from neuralforecast.models import NHITS

nf = NeuralForecast(models=[NHITS(h=14, input_size=56, max_steps=500)], freq="D")
nf.fit(df=df)
preds = nf.predict()
```

- **hierarchicalforecast**: **[[reconciliation]]**. If you forecast each store and also the total, the numbers will not add up. This library adjusts them (BottomUp, TopDown, MinTrace) so that the hierarchy is coherent. See the stage on hierarchical forecasting for the theory.
- **[[TimeGPT]]** (package `nixtla`): a pretrained foundation model that you call through a web **API** (key needed). No training on your side.

```notebook
from nixtla import NixtlaClient

client = NixtlaClient(api_key="YOUR_API_KEY")
fcst = client.forecast(df=df, h=14, freq="D", level=[80, 90])
```

```chart
{"title": "Illustration: one table, many models, one backtest", "x": "day", "height": 220,
 "series": [
   {"name": "actual", "gen": [["trend", {"start": 30, "slope": 0.2}], ["season", {"period": 7, "amp": 5}], ["noise", {"sd": 1.5}]], "n": 84, "seed": 31},
   {"name": "seasonal naive", "gen": [["trend", {"start": 30, "slope": 0.2}], ["season", {"period": 7, "amp": 5}]], "n": 84, "dash": true}
 ],
 "marks": [{"x": 70, "label": "forecast window"}],
 "caption": "Made-up data. In each library you compare every model with the seasonal naive line on the same rolling windows."}
```

```check
{"q": "Which Nixtla library makes store forecasts add up to the total forecast?", "type": "single",
 "options": ["statsforecast", "mlforecast", "hierarchicalforecast", "neuralforecast"],
 "answer": 2,
 "why": ["It fits classical models.", "It does boosting with lags.", "Correct: reconciliation.", "It fits neural models."]}
```

## Worked example

A typical workflow on a retail dataset, as notebook code. Run it where the packages are installed.

```notebook
# pip install statsforecast mlforecast lightgbm utilsforecast
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import SeasonalNaive, AutoETS
from utilsforecast.losses import mae

# df has columns unique_id, ds, y  (daily, many series)
h = 14
sf = StatsForecast(models=[SeasonalNaive(season_length=7), AutoETS(season_length=7)], freq="D", n_jobs=-1)
cv = sf.cross_validation(df=df, h=h, step_size=h, n_windows=3)     # adds the column "cutoff"

# MAE per model: lower is better; AutoETS must beat SeasonalNaive to earn its place
for model in ["SeasonalNaive", "AutoETS"]:
    print(model, (cv["y"] - cv[model]).abs().mean())
```

Compare the models on the same windows, then repeat the same steps with `mlforecast` using the same `df`.

## Common mistakes

- Wrong column names, or a missing `freq`.
- Series with gaps in dates: fill them first, or the lags are wrong.
- Reporting an average over series that hides bad series.
- Using a neural model on a few short series.
- Trusting a foundation-model API without a baseline comparison, and sending private data without checking the policy.
- Copying code from old tutorials: argument names have changed between versions.

## Interview lens

**Typical question:** "You have 100 000 daily series. Which tools and models do you use?"

**Strong answer:** I put the data in the long format `unique_id, ds, y`. I start with a seasonal naive baseline in statsforecast. For classical candidates I add fast AutoETS or AutoTheta. Then a global LightGBM model with mlforecast using lags, rolling means, calendar and price features, with differencing for trends. If the data is large I try a neural model like NHITS from neuralforecast. If the series form a hierarchy, I reconcile with hierarchicalforecast. I compare everything on the same rolling windows, and use a foundation model like TimeGPT only as another candidate.

**Red flags:** Fitting a statsmodels model in a loop over 100 000 series. No baseline. Not knowing the long format.

## Real world

Nixtla's open-source libraries are widely used for large-scale benchmarks, and their documentation shows speed comparisons with other tools. TimeGPT was announced by Nixtla in 2023 as a foundation model offered through an API. As with any vendor claim, check it on your own data.

## Key points

- Long format: `unique_id`, `ds`, `y`.
- statsforecast: fast ETS, ARIMA, Theta and naive models for many series.
- mlforecast: lag/rolling/date features, any regressor, recursive forecasting, target differencing.
- neuralforecast: deep models. hierarchicalforecast: reconciliation. TimeGPT: API foundation model.
- Always compare with seasonal naive on rolling windows.
