---
id: s12-06-more-libraries
title: More libraries: Prophet, pmdarima, tsfresh, tslearn, stumpy, river, PyOD
minutes: 30
level: intermediate
goals: [State what each of seven libraries does, Recognise the basic call for each, Match a library to a task]
prereqs: [s12-05-frameworks]
tags: [prophet, pmdarima, tsfresh, tslearn, stumpy, river, pyod]
skills: [forecasting-libraries, anomaly-detection]
---

## Warm-up

```check
{"q": "Which library makes a scikit-learn-like interface for time series, with forecasting horizon fh?", "type": "single",
 "options": ["sktime", "stumpy", "river"],
 "answer": 0,
 "why": ["Correct.", "stumpy computes the matrix profile.", "river learns online."]}
```

```check
{"q": "AutoGluon-TimeSeries is...", "type": "single",
 "options": ["An AutoML library that ensembles many models", "A decomposition method", "A database"],
 "answer": 0,
 "why": ["Correct.", "STL is a decomposition.", "It is a modelling library."]}
```

## Why it matters

Beyond the big frameworks there are small, sharp tools. Some forecast (Prophet, pmdarima). Some turn a series into **features** (tsfresh). Some compare series or search patterns (tslearn, stumpy). Some learn from a **stream** (river). Some find outliers (PyOD). In an interview you do not need every argument, but you should know what each one is for. All code here is **notebook** code.

## Forecasting helpers

**Prophet**: decomposable model with trend, seasonality and holidays (see the case-study lesson). Input is a DataFrame with `ds` and `y`.

```notebook
from prophet import Prophet

m = Prophet(yearly_seasonality=True, weekly_seasonality=True)
m.add_country_holidays(country_name="US")
m.fit(df)                                          # df: columns ds, y
future = m.make_future_dataframe(periods=30)       # history + 30 future days
fc = m.predict(future)                             # columns yhat, yhat_lower, yhat_upper, ...
```

**pmdarima**: `auto_arima`, a search for the best ARIMA/SARIMA order with AIC, like R's `auto.arima`.

```notebook
import pmdarima as pm

model = pm.auto_arima(y_train, seasonal=True, m=7, stepwise=True, suppress_warnings=True)
print(model.order, model.seasonal_order)
forecast = model.predict(n_periods=14)
```

## Features and similarity

**[[tsfresh]]** extracts hundreds of statistics (mean, number of peaks, entropy, autocorrelation) per series and selects the useful ones. Use it to turn many series into one feature table for a classifier or regressor.

```notebook
from tsfresh import extract_features, select_features
from tsfresh.feature_extraction import MinimalFCParameters

X = extract_features(long_df, column_id="id", column_sort="time",
                     default_fc_parameters=MinimalFCParameters())
X_sel = select_features(X.dropna(axis=1), labels)        # keep features related to the label
```

**tslearn** offers time series distances and clustering, notably **[[DTW]]** (dynamic time warping), which compares series even if they are shifted or stretched in time.

```notebook
from tslearn.metrics import dtw
from tslearn.clustering import TimeSeriesKMeans

d = dtw(series_a, series_b)
km = TimeSeriesKMeans(n_clusters=3, metric="dtw", random_state=0).fit(X_train_3d)   # shape (n_series, length, 1)
labels = km.labels_
```

**stumpy** computes the **[[matrix profile]]**: for each window of length `m`, the distance to its nearest neighbour elsewhere in the series. Low values mark **motifs** (repeated patterns); high values mark **discords** (anomalies).

```notebook
import numpy as np
import stumpy

mp = stumpy.stump(series.astype(float), m=50)       # column 0 = matrix profile distance
motif_start = int(np.argmin(mp[:, 0]))
discord_start = int(np.argmax(mp[:, 0]))
```

```check
{"q": "In a matrix profile, a window with a very large value is most likely...", "type": "single",
 "options": ["A discord: an unusual pattern, possibly an anomaly", "A motif", "A missing value", "A seasonal peak"],
 "answer": 0,
 "why": ["Correct: no other window looks like it.", "Motifs have small values.", "Missing values are separate.", "A regular season gives small values."]}
```

## Streams and outliers

**river** does **[[online learning]]**: the model updates with one observation at a time and never stores the whole dataset. It suits streams and drifting data.

```notebook
from river import linear_model, preprocessing, metrics

model = preprocessing.StandardScaler() | linear_model.LinearRegression()
mae = metrics.MAE()
for x, y in stream:                 # x: dict of features, y: target
    y_pred = model.predict_one(x)   # predict first (test-then-train)
    mae.update(y, y_pred)
    model.learn_one(x, y)           # then learn
```

This "predict, then learn" order is called **[[prequential evaluation|prequential]]** evaluation and avoids leakage.

**[[PyOD]]** collects many outlier detectors (Isolation Forest, LOF, kNN, autoencoders) with one interface. For time series, first turn the series into **windows** (each row = the last `w` values), then detect outliers among the rows.

```notebook
import numpy as np
from pyod.models.iforest import IForest

w = 24
X = np.lib.stride_tricks.sliding_window_view(series, w)     # rows are windows
clf = IForest(contamination=0.01, random_state=0).fit(X)
scores = clf.decision_scores_                               # high = more unusual
flags = clf.labels_                                         # 1 = outlier
```

```chart
{"title": "Illustration: a repeated pattern and one unusual shape", "x": "time", "height": 220,
 "series": [
   {"name": "sensor", "gen": [["season", {"period": 25, "amp": 10}], ["noise", {"sd": 0.8}], ["spike", {"at": 130, "size": 14}]], "n": 200, "seed": 51}
 ],
 "marks": [{"x": 130, "label": "discord"}],
 "caption": "The wave repeats, so windows match each other (motifs). The window around time 130 has no match: a discord."}
```

```check
{"q": "What is the order of prequential evaluation in river?", "type": "single",
 "options": ["Predict, then learn from the new example", "Learn, then predict on the same example", "Shuffle, then learn", "Predict at the end only"],
 "answer": 0,
 "why": ["Correct: the prediction is made before the model sees the answer.", "That leaks the answer.", "Streams keep time order.", "You would lose the running score."]}
```

## Worked example

Which tool for which job? Read the table, then try to match without looking.

| Task | Tool |
|---|---|
| Quick forecast of a daily series with holidays | Prophet (and compare with ETS) |
| Pick ARIMA order automatically | pmdarima `auto_arima` |
| Turn 5 000 sensor recordings into features for a classifier | tsfresh |
| Group customers by the shape of their usage curve | tslearn with DTW |
| Find a repeated pattern or an odd subsequence in one long series | stumpy |
| Update a model on every new event, without retraining | river |
| Many ready-made outlier detectors on window features | PyOD |

## Common mistakes

- Using Prophet or `auto_arima` without a baseline and a rolling backtest.
- Running tsfresh on huge data without limiting features: it is slow and creates many columns.
- Computing DTW on thousands of long series without thinking about cost.
- Choosing the window length `m` in stumpy at random: use the length of the pattern you care about.
- Feeding PyOD raw single points, which ignores the time context.
- Evaluating a river model with a random split.

## Interview lens

**Typical question:** "How would you find anomalies in a long sensor series with no labels?"

**Strong answer:** I start with a simple seasonal baseline and a robust z-score. If the anomalies are unusual shapes and not just big values, I compute the matrix profile with stumpy and look at the largest values (discords), choosing the window length from the pattern length. I can also turn the series into windows and use an Isolation Forest from PyOD. Without labels I check the top results by hand and measure how many alerts per day the method would produce.

**Red flags:** Using a point-wise 3-sigma rule on a seasonal series. Not knowing what a motif is.

## Real world

Prophet came from Facebook, stumpy from the matrix profile research of the Keogh group at UC Riverside and implementation by TD Ameritrade engineers, tsfresh from a research project with Blue Yonder, and river from the merger of the creme and scikit-multiflow projects. These are all open source with public documentation.

## Key points

- Prophet and pmdarima forecast; always add baselines.
- tsfresh makes features; tslearn compares shapes with DTW; stumpy finds motifs and discords.
- river learns online with predict-then-learn; PyOD offers many outlier detectors on window features.
- Match the tool to the task, and validate with time-aware methods.
