---
id: s5-07-gradient-boosting-in-practice
title: Gradient boosting in practice (LightGBM and XGBoost ideas)
minutes: 35
level: intermediate
goals: [Explain how gradient boosting builds a forecast from many small trees, Pick an objective such as squared error or Tweedie or quantile, Use time-based early stopping and read feature importance with care]
prereqs: [s5-02-lag-and-rolling-features, s5-06-global-vs-local-models]
tags: [gradient-boosting, lightgbm, xgboost, early-stopping, importance]
skills: [leakage, scale, baseline-first]
---
## Warm-up
```check
{"q": "A global model is trained on many series. Which step is needed before training?", "type": "single",
 "options": ["Scale each series with its own training statistics", "Shuffle the rows", "Remove all lag features"],
 "answer": 0,
 "why": ["Correct: so that large series do not dominate.", "Shuffling mixes past and future.", "Lag features are the core inputs."]}
```

```check
{"q": "Direct strategy, horizon 5. How many models do you train?", "type": "numeric",
 "answer": 5, "tol": 0.001,
 "why": "One model for each horizon step: 5."}
```

## Why it matters
When people say "machine learning for forecasting", they most often mean **gradient boosting**. In many competitions the top solutions used LightGBM or XGBoost on lag and calendar features. Examples are M5 (Walmart sales) and many Kaggle sales contests. These tools are fast and accept missing values. They need no scaling of features. They handle non-linear effects and interactions, for example "promotion × weekend". But they have traps: they cannot extrapolate a trend, early stopping can leak, and feature importance can mislead.

## How boosting works
A **[[decision tree]]** splits the data with simple questions ("is lag_7 > 40?") and gives an average in each leaf. A single tree is weak. **[[gradient boosting|Gradient boosting]]** builds trees one after another:

1. Start with a simple guess (for example the mean).
2. Compute the errors (residuals) of the current model.
3. Train a small tree to predict these errors.
4. Add it to the model, multiplied by a small **[[learning rate]]** (for example 0.05).
5. Repeat for hundreds of rounds.

Important settings:

| Setting | Meaning | Effect |
|---|---|---|
| number of rounds (trees) | how many trees | more = better fit, risk of overfit |
| learning rate | size of each step | small = slower but safer |
| tree depth or number of leaves | tree size | bigger = more interactions, more overfit |
| minimum samples per leaf | smallest leaf | bigger = smoother |
| subsample / column sample | random part of rows / features per tree | reduces overfit |

LightGBM and XGBoost are fast, popular implementations. Scikit-learn has `HistGradientBoostingRegressor`, which uses the same histogram idea as LightGBM and runs in this course.

```check
{"q": "In boosting, what does each new tree try to predict?", "type": "single",
 "options": ["The target again, from scratch", "The remaining errors of the current model", "The next lag"],
 "answer": 1,
 "why": ["That would not use the earlier trees.", "Correct: each tree corrects the mistakes of the sum of earlier trees.", "Lags are inputs, not what trees predict."]}
```

## The objective (loss) must fit the problem
The **[[objective]]** is the loss the model minimizes. Choose it to match the business.

- **Squared error:** predicts the mean. Sensitive to big spikes.
- **Absolute error (L1):** predicts the median. Robust to spikes.
- **Poisson / [[tweedie|Tweedie]]:** for non-negative counts or sales with many zeros and a long right tail (intermittent demand). The model predicts the mean with a log link, so it never outputs negative values. Tweedie has a power between 1 (Poisson) and 2 (Gamma).
- **Quantile:** minimizes the pinball loss for a level such as 0.9. Train one model for each quantile (P10, P50, P90) to get prediction intervals.

Example: daily sales of a slow item: 0, 0, 3, 0, 0, 1, 0, 7. Squared error will chase the 7. Tweedie handles the zeros and the skew.

```check
{"q": "You need a P90 forecast to plan stock. Which objective?", "type": "single",
 "options": ["Squared error", "Quantile with level 0.9", "Poisson"],
 "answer": 1,
 "why": ["Squared error gives the mean.", "Correct: the pinball loss at 0.9 learns the 90% quantile.", "Poisson gives the mean of counts, not a quantile."]}
```

## Early stopping, the time-safe way
**[[early stopping|Early stopping]]** stops adding trees when the error on a validation set no longer improves. It saves time and avoids overfitting. The trap: the validation set must come **after** the training rows in time.

- Split by time: for example the last 10% of the training period is validation.
- Do not use a random validation split. Neighbouring days would be in both parts, and the score would be too good.
- In scikit-learn, `HistGradientBoostingRegressor(early_stopping=True)` takes a **random** validation part. For time series, set `early_stopping=False`. Then choose the number of rounds with your own time validation. In LightGBM you can pass a time-ordered validation set (`eval_set`).
- After you choose the number of rounds, retrain on all training data with that number.

```check
{"q": "Which validation set is correct for early stopping in a forecasting model?", "type": "single",
 "options": ["A random 10% of rows", "The last 10% of the training period", "The test set"],
 "answer": 1,
 "why": ["Random rows leak neighbouring days.", "Correct: the newest training data, which follows the rest in time.", "The test set must stay untouched."]}
```

## Trees cannot extrapolate
A tree predicts an average of training targets. So it **cannot predict values outside the range seen in training**. If the series has a trend and the test values are higher than any training value, a tree model will under-predict.

Fixes:
- Predict a **change** instead of the level: target = `y(t) − y(t−7)` (or `y(t) − y(t−1)`). Then add the lag back.
- Predict a ratio to a recent average, or use per-series scaling so that levels are comparable.
- Remove the trend first (detrend) and add it back.
- Use a linear model (or a linear tree) for the trend and a tree for the rest.

```chart
{"title": "A tree model flattens at the top of the training range", "x": "t", "height": 220,
 "series": [
   {"name": "actual (trend)", "gen": [["trend", {"slope": 1, "start": 0}]], "n": 60},
   {"name": "tree on levels", "y": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,39,39,39,39,39,39,39,39,39,39,39,39,39,39,39,39,39,39,39,39], "dash": true}
 ],
 "marks": [{"x": 40, "label": "end of training"}],
 "caption": "After the end of training, the tree model repeats its highest leaf value."}
```

## Feature importance pitfalls
[[feature importance|Importance]] tells which features the model used. Read it carefully.

- **Gain or split-count importance** favours features with many distinct values (like a continuous price or an id).
- **Correlated features** share the importance. Each looks smaller than it is.
- A **leaky** feature (target-like) will be at the top. This is useful: if one feature has 90% of the importance, look for leakage.
- Importance is not causation. A promotion flag may be used because promotions are planned on low-sales days.
- Prefer **[[permutation importance]]** on a time-ordered validation set: shuffle one feature and measure how much the error grows. Check it on out-of-time data, not on training data.

```check
{"q": "One feature has 95% of the total importance and the score is almost perfect. What is the first thing to check?", "type": "single",
 "options": ["Increase the learning rate", "Whether this feature leaks information about the target", "Add more trees"],
 "answer": 1,
 "why": ["That does not explain a perfect score.", "Correct: a single dominant feature plus an unrealistic score is the classic leakage sign.", "More trees do not explain it either."]}
```

## Worked example
We use `HistGradientBoostingRegressor` from scikit-learn. The series has a trend and a weekly season. We predict one step ahead on the last 28 days (the lags are real values, not predictions). We compare the seasonal naive baseline, a tree on levels, and a tree on the change from lag 7.

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

rng = np.random.default_rng(0)
n = 400
t = np.arange(n)
y = 50 + 0.2 * t + 8 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 1.5, n)

df = pd.DataFrame({"y": y})
for k in (1, 2, 7, 14):
    df[f"lag_{k}"] = df["y"].shift(k)
df["roll_mean_7"] = df["y"].shift(1).rolling(7).mean()     # shifted: no leak
df["dow"] = t % 7
df = df.dropna()

train, test = df.iloc[:-28], df.iloc[-28:]                 # split by time
feats = [c for c in df.columns if c != "y"]

def fit(target):
    return HistGradientBoostingRegressor(
        max_iter=200, learning_rate=0.1, early_stopping=False, random_state=0
    ).fit(train[feats], target)

# (a) seasonal naive baseline: the value 7 days ago
mae_naive = np.abs(test["y"] - test["lag_7"]).mean()
# (b) tree on levels: cannot go above the training range
pred_level = fit(train["y"]).predict(test[feats])
# (c) tree on the change from lag_7, then add the lag back
pred_delta = fit(train["y"] - train["lag_7"]).predict(test[feats]) + test["lag_7"].values

print("train max y:", round(train["y"].max(), 1), "| test max y:", round(test["y"].max(), 1))
print("MAE seasonal naive:", round(mae_naive, 2))
print("MAE tree on levels:", round(np.abs(test["y"] - pred_level).mean(), 2))
print("MAE tree on change:", round(np.abs(test["y"] - pred_delta).mean(), 2))
# Output:
# train max y: 131.2 | test max y: 137.4
# MAE seasonal naive: 2.01
# MAE tree on levels: 3.25
# MAE tree on change: 1.44
```

The test values are higher than anything in the training data, so the tree on levels falls behind. Predicting the change fixes this. Always include the seasonal naive baseline in the table.

## Common mistakes
- Early stopping with a random or test validation set.
- Using squared error for intermittent, zero-heavy sales.
- Feeding a trending level to trees without differencing or a ratio.
- Tuning hyperparameters on the test period.
- Reading gain importance as proof of cause.
- Training a quantile model for P90 and reporting RMSE.
- Comparing only with other fancy models and not with seasonal naive.

## Interview lens
**Typical question:** "You use LightGBM for sales forecasting. Walk me through the important choices."

**Strong answer:** I build lag, rolling (shifted) and calendar features, plus static features for a global model. I choose the objective to match the data: Tweedie or Poisson for non-negative skewed sales, quantile models for intervals. I validate with a walk-forward backtest, and I use a validation set that comes after the training rows for early stopping. Trees cannot extrapolate, so I predict a change or a ratio to a recent level when there is a trend. I check permutation importance on out-of-time data to find leaks, and I compare against seasonal naive.

**Red flags:** random K-fold; early stopping on the test set; no baseline; squared error on count data with many zeros; "feature importance shows what causes sales".

## Real world
- LightGBM (Microsoft) and XGBoost are open-source libraries that won many tabular competitions. In M5, many top teams used LightGBM on lag and calendar features, often with a Tweedie objective.
- The M5 data came from Walmart: 42,840 hierarchical series of daily unit sales, many with zeros.
- Nixtla's `mlforecast` and the Darts library wrap LightGBM and XGBoost for forecasting with lag features.

## Key points
- Gradient boosting adds small trees that fix the errors of the earlier trees.
- Choose the objective for the data: squared error (mean), L1 (median), Tweedie or Poisson (counts), quantile (intervals).
- Early stopping needs a validation set that follows the training period in time.
- Trees cannot go outside the training range, so predict changes or ratios when there is a trend.
- Treat feature importance as a clue and a leak detector, not as proof of cause.
