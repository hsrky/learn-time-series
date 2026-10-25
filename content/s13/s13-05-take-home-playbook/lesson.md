---
id: s13-05-take-home-playbook
title: The take-home project playbook
minutes: 30
level: intermediate
goals: [Follow the five steps baseline, backtest, error analysis, narrative, README, Know what reviewers grade and what makes them reject, Do error analysis by segment and by anomalous day, Write a one-page README that a reviewer can run in 5 minutes]
prereqs: [s13-04-oa-leakage-and-backtests]
tags: [take-home, project, error-analysis, README]
skills: [baseline-first, backtest, communication]
---

## Warm-up

```check
{"q": "Which split is correct for a forecasting project?", "type": "single",
 "options": ["Random 80/20", "Train on earlier dates, test on later dates", "Test on the first month, train on the rest", "Shuffle then split by store"],
 "answer": 1,
 "why": ["A random split lets the model see the future.", "Correct: the test period must come after the training period.", "Training on data after the test period leaks the future.", "Shuffling breaks time order."]}
```

## Why it matters

A take-home project is a small data set and 3 to 8 hours of work. Many candidates spend that time on a complex model. Reviewers do not reward this. They read 20 projects in one afternoon. They look for **clear thinking**: a baseline, an honest backtest, and an explanation of errors. A simple model with a clear story beats a complex model with no story.

## What reviewers grade

Most teams use a rubric like this one. Items near the top weigh more.

| Item | What a good project shows |
|---|---|
| Problem framing | The decision, the horizon, the metric, and why |
| Data checks | Missing dates, duplicates, outliers, time zones |
| Baseline | Naive and seasonal naive, with numbers |
| Validation | Time-based backtest, several folds, no leakage |
| Model | One or two sensible models, compared to the baseline |
| Error analysis | Error by segment, by horizon, by anomalous day |
| Narrative | A short story: what works, what does not, what next |
| Reproducibility | README, fixed seeds, one command to run |

```chart
{"title": "Where reviewers spend their attention (illustrative weights, bars 1 to 8 in table order)", "x": "item", "height": 220,
 "series": [
   {"name": "weight", "kind": "bar", "x": [1,2,3,4,5,6,7,8], "y": [15, 10, 15, 20, 10, 15, 10, 5]}
 ],
 "caption": "An example weighting. Validation and framing together are about a third of the score. Your own rubric may differ."}
```

```check
{"q": "Which project is most likely to get a strong review?", "type": "single",
 "options": ["A deep network with no baseline", "A seasonal naive baseline, a LightGBM model, a 3-fold backtest, and error by segment", "Ten models with a random split", "A notebook with no text"],
 "answer": 1,
 "why": ["Without a baseline the reviewer cannot judge the lift.", "Correct: baseline, honest validation and error analysis are what reviewers look for.", "A random split is a red flag, and many models add noise, not insight.", "No text means no narrative."]}
```

## The five steps

1. **Baseline.** Naive, seasonal naive, and a moving average. Report MAE and WAPE. This takes 30 minutes and sets the bar.
2. **Backtest.** At least 3 folds with the same horizon as the real task. Same folds for all models. See [[lesson:s13-04-oa-leakage-and-backtests]].
3. **Model.** One simple model (for example ETS) and one stronger model (for example LightGBM with lag features). Compare with the baseline, using lift: `(baseline error − model error) / baseline error`.
4. **Error analysis.** Where does the model fail? By segment, by weekday, by horizon step, by anomalous days. Practise in [[problem:forecast-error-by-segment]] and [[problem:top-k-anomalous-days]].
5. **Narrative and README.** A page that a manager can read in two minutes.

```check
{"q": "Baseline MAE is 20 and your model's MAE is 17. What is the lift?", "type": "numeric",
 "answer": 0.15, "tol": 0.005,
 "why": "Lift = (20 − 17) / 20 = 3 / 20 = 0.15, or 15% better than the baseline."}
```

## Error analysis that shows insight

An average error hides the story. Break it down:

- **By segment** (store, category, volume class). Show the share of total error, not only the WAPE. A segment with a high WAPE but a small share is not the top priority.
- **By bias.** Is the model always too high for one segment?
- **By horizon.** Error normally grows with the horizon.
- **By day.** The days with the largest errors are often holidays, promotions or data problems. Look at each of them.

Then write what you would do next, with a reason: "Fix holiday handling first because the 5 worst days are holidays and cause 30% of the error."

```widget
{"name": "anomaly-zscore", "params": {}}
```

```check
{"q": "Segment X has WAPE 60% but 2% of total error. Segment Y has WAPE 15% but 55% of total error. Where do you work first?", "type": "single",
 "options": ["X, because its WAPE is higher", "Y, because it carries most of the total error", "Neither", "Both equally"],
 "answer": 1,
 "why": ["High percentage on tiny volume has little impact on the total.", "Correct: improving Y by a little moves the total more than fixing X.", "Error analysis exists to choose a priority.", "The shares are very different, so the priority is not equal."]}
```

## The narrative and README

Write the README so a reviewer can run your work in 5 minutes. Use this outline:

1. **Goal and decision** (2 sentences).
2. **Data notes** (what you found, what you fixed).
3. **Method** (baseline, backtest design, models).
4. **Results table** (model, MAE, WAPE, lift) and one chart.
5. **Error analysis** (3 bullets with numbers).
6. **Limits and next steps.**
7. **How to run** (`pip install -r requirements.txt`, `python run.py`).

Keep seeds fixed. Pin library versions. Do not leave absolute paths in the code.

```check
{"q": "Which README line is the best?", "type": "single",
 "options": ["I used a very advanced model.", "Seasonal naive WAPE is 11.9%; LightGBM is 8.4%, a 29% lift. Most remaining error is on promotion days.", "The results are good.", "See the notebook."],
 "answer": 1,
 "why": ["No numbers and no evidence.", "Correct: numbers, lift and a clear finding.", "'Good' tells the reviewer nothing.", "A reviewer wants the summary without opening the notebook first."]}
```

## Worked example

A mini take-home on synthetic daily sales (weekly season and a small trend). We compare three baselines in a 3-fold backtest with horizon 14. Then we break the best baseline's error down by weekday.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
idx = pd.date_range("2024-01-01", periods=140, freq="D")
weekend = np.isin(idx.dayofweek, [5, 6])
y = pd.Series(100 + 0.2 * np.arange(140) + 20 * weekend + rng.normal(0, 4, 140), index=idx)

H, K = 14, 3                                          # horizon, number of folds

def naive(train, h):          return np.repeat(train.iloc[-1], h)
def mean_last_7(train, h):    return np.repeat(train.iloc[-7:].mean(), h)
def seasonal_naive(train, h): return np.array([train.iloc[-7 + (i % 7)] for i in range(h)])

rows = []
for name, f in [("naive", naive), ("mean of last 7", mean_last_7), ("seasonal naive", seasonal_naive)]:
    abs_err, actual = [], []
    for j in range(K):
        o = len(y) - (K - j) * H                      # origin: train only on y[:o]
        fc = f(y.iloc[:o], H)
        a = y.iloc[o:o + H].to_numpy()
        abs_err.append(np.abs(a - fc)); actual.append(a)
    e, a = np.concatenate(abs_err), np.concatenate(actual)
    rows.append((name, e.mean(), e.sum() / a.sum()))
res = pd.DataFrame(rows, columns=["model", "MAE", "WAPE"]).set_index("model")
print(res.round(3))

# error analysis of the best baseline, by weekday (a "segment")
test = y.iloc[-K * H:]
fc = np.concatenate([seasonal_naive(y.iloc[:len(y) - (K - j) * H], H) for j in range(K)])
err = pd.DataFrame({"abs_err": np.abs(test.to_numpy() - fc), "weekday": test.index.day_name()})
share = err.groupby("weekday")["abs_err"].sum() / err["abs_err"].sum()
print((share.sort_values(ascending=False) * 100).round(1).head(3))
# Output:
#                    MAE   WAPE
# model
# naive           15.380  0.119
# mean of last 7   9.037  0.070
# seasonal naive   4.493  0.035
# weekday
# Saturday    20.7
# Friday      20.2
# Thursday    19.6
# Name: abs_err, dtype: float64
```

The table shows the lift of seasonal naive over naive: its MAE is roughly one third. A real report adds the lift of the stronger model on top. The weekday table shows where the remaining error sits.

## Common mistakes

- No baseline, or a baseline that is not seasonal.
- One test split, not a backtest.
- Tuning on the test period.
- Reporting only one metric.
- Hiding failures. Reviewers like honest limits.
- A notebook that only works on your laptop.
- Spending 6 hours on a model and 10 minutes on the story.

## Interview lens

**Typical question:** "Walk me through your take-home project. What would you do with one more week?"

**Strong answer:** "The task was a 14-day demand forecast. I built seasonal naive first, with WAPE 11.9%. A LightGBM model with lags and calendar features reached 8.4%, a 29% lift, in a 3-fold backtest. Error analysis showed 40% of the error on promotion days, with a positive bias. With one more week I would add the promotion calendar as a known-future feature and test a model per volume class. I would also add a monitoring check on bias."

**Red flags:** cannot explain the validation scheme; no baseline number; blames the data without checking it; cannot say what to do next.

## Real world

- Forecasting competitions publish the winners' write-ups. The best ones follow the same order: baseline, validation scheme, features, model, error analysis. The M5 competition reports and many Kaggle solution posts are public examples.
- Many companies publish engineering blog posts on forecasting systems. They stress strong baselines and backtests with several origins before any complex model is accepted.

## Key points

- Reviewers grade framing, baseline, validation, error analysis, narrative and reproducibility.
- Always report lift over a seasonal naive baseline from a multi-fold backtest.
- Error analysis: rank segments by share of total error, check bias, look at the worst days.
- The README must contain numbers, a finding, a next step, and one command to run.
