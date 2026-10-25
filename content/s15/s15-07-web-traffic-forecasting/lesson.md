---
id: s15-07-web-traffic-forecasting
title: Web Traffic Time Series Forecasting - 145k pages, SMAPE and seq2seq
minutes: 45
level: intermediate
goals: [Read the wide page-by-day format and parse page names, Compute SMAPE with zeros and missing days, Build strong median baselines and a weekday-adjusted version, Describe the seq2seq RNN approach of the winning team]
prereqs: [s15-03-store-sales-features-model-submission]
tags: [kaggle, web-traffic, wikipedia, SMAPE, median, seq2seq]
skills: [metrics, baseline-first, scale]
---

## Warm-up

```check
{"q": "Why is the median often a better 'typical level' than the mean for web traffic?", "type": "single",
 "options": ["It is faster to compute", "A viral spike changes the mean a lot but the median very little", "It uses all data", "It is always larger"],
 "answer": 1,
 "why": ["Speed is not the reason.", "Correct: the median is robust to outliers.", "Both use the data.", "Not always."]}
```

```check
{"q": "What is the problem with a percentage error when the actual value is 0?", "type": "single",
 "options": ["It is negative", "Division by zero: it needs a special rule", "It is always 100%", "No problem"],
 "answer": 1,
 "why": ["No.", "Correct.", "Not always.", "There is a problem."]}
```

## Why it matters

*Web Traffic Time Series Forecasting* (2017) asked for the daily page views for the next 60 days of about **145,000 Wikipedia pages**. It is the opposite of the Rossmann case: no promotions, no holidays given, only the history of each page. It teaches three things. First, how to handle **very many series with missing data**. Second, why **simple robust baselines** are strong. Third, how a **neural sequence model** can win. In interviews it is a good example for "forecast thousands of series with only history".

## Goal, data and metric

**Data.** `train_1.csv` / `train_2.csv` have one row per page. The first column is `Page`, then one column per day. The date is text, for example `2015-07-01`. Values are views; some are missing (`NaN`), for example before a page existed. The page name looks like `Title_en.wikipedia.org_all-access_spider`. It has the title, project, access type, and agent. `key_2.csv` maps `Page_date` to an `Id` for the submission. The submission has columns `Id, Visits`. Check the exact file names in the Data tab: the competition had two stages with different files.

**Metric: SMAPE**

`SMAPE = mean( 200 × |p − y| / (|y| + |p|) )`

- It is between 0 and 200.
- If actual and prediction are both 0, the day counts as 0 error.
- If the actual is 0 and the prediction is not, the error is 200: the **maximum**.
- Missing actuals are ignored.

Implement it in [[problem:smape-zero-median]].

```check
{"q": "Actual views 10, prediction 30. What is the SMAPE of this day?", "type": "numeric",
 "answer": 100, "tol": 0.01, "why": "200 × |30 − 10| / (10 + 30) = 200 × 20 / 40 = 100."}
```

## Data tour

```notebook
# Run this in a Kaggle notebook (Data: Web Traffic Time Series Forecasting)
import numpy as np
import pandas as pd

DATA = "/kaggle/input/web-traffic-time-series-forecasting/"
train = pd.read_csv(DATA + "train_2.csv")                  # check the file names in the Data tab
dates = [c for c in train.columns if c != "Page"]
Y = train[dates].to_numpy(dtype=float)                     # shape (pages, days)
print("pages:", len(train), "| days:", len(dates), "|", dates[0], "to", dates[-1])
print("share of missing values:", round(float(np.isnan(Y).mean()), 3))
print("share of zeros:", round(float((Y == 0).mean()), 3))

# Parse the page name: title_project_access_agent
parts = train["Page"].str.rsplit("_", n=3, expand=True)
train["title"], train["project"], train["access"], train["agent"] = parts[0], parts[1], parts[2], parts[3]
print(train.groupby("project")["Page"].count())
print(train.groupby("agent")["Page"].count())

# Typical level and spikes
print("median of page medians:", float(np.nanmedian(np.nanmedian(Y, axis=1))))
total = np.nansum(Y, axis=0)
print("total views, last 7 days:", total[-7:].astype(int).tolist())
```

Things to see on the real data: Many pages are small and noisy. Some have a clear weekly pattern. Some have yearly peaks. Some have spikes from news events. Many have missing days at the start.

## Validation

The test is the 60 days after the last training day. So hold out the **last 60 days** of the training data and train on the days before. Use SMAPE with the rules above. The real test was in the future of the data (stage 2). So the final score came from a period that was not yet known when the competition began. This made public-leaderboard overfitting less useful.

## Baselines

1. **Last value** (naive).
2. **Median of the last N days** (N = 7, 14, 28, 56).
3. **Weekday-adjusted median:** for each page, take the median of the last 8 weeks for each weekday separately. Predict that weekday level.

```chart
{"title": "Median of the last 14 days vs a spike: the median ignores the viral day", "x": "day", "height": 220,
 "series": [
   {"name": "page views", "gen": [["const", {"value": 100}], ["season", {"period": 7, "amp": 15}], ["spike", {"at": 40, "size": 400}], ["noise", {"sd": 5}]], "n": 70, "seed": 6},
   {"name": "median level", "gen": [["const", {"value": 100}]], "n": 70, "dash": true}
 ],
 "marks": [{"x": 40, "label": "viral spike"}],
 "caption": "A mean of the last 14 days would jump after the spike. The median stays near the normal level."}
```

```notebook
H = 60
hist, true = Y[:, :-H], Y[:, -H:]

def smape(y_true, y_pred):
    valid = ~np.isnan(y_true)
    y, p = y_true[valid], y_pred[valid]
    num, den = np.abs(p - y), np.abs(y) + np.abs(p)
    err = np.where(den == 0, 0.0, 200 * num / np.where(den == 0, 1, den))
    return float(err.mean())

def median_baseline(hist, h, window):
    level = np.nanmedian(hist[:, -window:], axis=1)
    level = np.nan_to_num(level)                              # all-NaN window -> 0
    return np.repeat(level[:, None], h, axis=1)

print("SMAPE last value :", round(smape(true, np.repeat(np.nan_to_num(hist[:, -1:]), H, axis=1)), 3))
for w in (7, 14, 28, 56):
    print(f"SMAPE median {w:>2} days:", round(smape(true, median_baseline(hist, H, w)), 3))

def weekday_median(hist, h, weeks=8):
    """Median of each weekday over the last `weeks` weeks (hist ends on the day before the forecast)."""
    n = hist.shape[1]
    out = np.zeros((hist.shape[0], h))
    for k in range(h):
        # day n + k has the same weekday as day n + k - 7 * m, for the smallest m with that day inside history
        m = k // 7 + 1
        idx = [n + k - 7 * (m + j) for j in range(weeks)]
        out[:, k] = np.nan_to_num(np.nanmedian(hist[:, idx], axis=1))
    return out

print("SMAPE weekday median 8 weeks:", round(smape(true, weekday_median(hist, H)), 3))
```

Write down the scores. The median baselines are strong. The weekday version helps when the weekly pattern is clear. Predicting a **zero** is dangerous: if the page has any views, the error for that day is 200.

```check
{"q": "A page had views [0, 0, 0, 3] in the last 4 days. A model predicts 2 for tomorrow, and the actual turns out 0. What is that day's SMAPE?", "type": "numeric",
 "answer": 200, "tol": 0.01, "why": "200 × |2 − 0| / (0 + 2) = 200. Predicting a positive value when the actual is 0 always gives the maximum."}
```

## Improving: ideas that worked

- **Log transform:** train on `log1p(views)`; view counts are skewed and errors are relative.
- **Per-page scaling:** divide each series by its recent median so one model can learn from all pages.
- **Long lags:** yearly (365 days) and quarterly lags capture yearly peaks.
- **Page features:** project, access, agent.
- **Ensembles:** averaging several models and medians gave stable gains.
- **Rounding:** views are integers; some teams rounded predictions.

A gradient boosting model on these features can be strong. The winning team went a different way.

## The winner: seq2seq with RNNs

The first-place solution (by Arthur Suilin, published on GitHub) used a **sequence-to-sequence** neural network:

1. An **encoder** reads the page's past views, on a log scale, normalised by the page's own mean. It is a recurrent network with GRU cells.
2. A **decoder** (also recurrent) produces the next 60 days one step at a time. It uses its own previous prediction and **known features** such as day of week.
3. Extra inputs: page identity (project, access, agent), and lagged values from one year and one quarter back.
4. The loss was close to SMAPE, and many models were trained and **averaged**.

## Why one global network works

The idea in plain words: one network learns shared patterns of all pages. Each page's history sets its level and shape. This is a **global model**, like LightGBM in Store Sales, but with a recurrent network. See the stage on deep learning in this course for RNN, GRU and seq2seq basics.

```notebook
# Sketch of the idea (not trained here)
# For each page: x = log1p(views[-365:]) / scale     -> encoder GRU -> hidden state
# Decoder step t: input = [previous prediction, day_of_week_t, page_features] -> GRU -> next value
# Training windows: slide the 60-day target window over the history
# Final forecast = average over many trained models
```

## Submission

For the real submission, forecast from the full history and map each `Page_date` key to its value.

```notebook
full = Y
future_days = pd.date_range(pd.Timestamp(dates[-1]) + pd.Timedelta(days=1), periods=H)
pred = weekday_median(full, H)                              # or your better model
pred_df = pd.DataFrame(pred, index=train["Page"], columns=future_days.strftime("%Y-%m-%d"))

key = pd.read_csv(DATA + "key_2.csv")                       # columns: Page (title_date), Id
key["page"] = key["Page"].str[:-11]                         # remove the underscore and the date
key["date"] = key["Page"].str[-10:]
long = pred_df.stack().rename("Visits").reset_index()
long.columns = ["page", "date", "Visits"]
sub = key.merge(long, on=["page", "date"], how="left")
sub["Visits"] = sub["Visits"].fillna(0).round()
sub[["Id", "Visits"]].to_csv("submission.csv", index=False)
print(sub[["Id", "Visits"]].head())
```

## Worked example

In the browser: six synthetic pages with zeros, missing days and one spike. We compare the median baselines and the mean with SMAPE, using the rules of the mini problem.

```python
import numpy as np

rng = np.random.default_rng(4)
T, H = 120, 14
levels = [200, 50, 8, 2, 0.3, 0.0]
Y = np.array([rng.poisson(l * (1 + 0.3 * np.sin(2 * np.pi * np.arange(T + H) / 7))) for l in levels], dtype=float)
Y[0, 100] += 3000                                      # a viral spike in the history of page 0
Y[:, :10] = np.nan                                     # pages not tracked yet
hist, true = Y[:, :T], Y[:, T:]

def smape(y, p):
    ok = ~np.isnan(y)
    y, p = y[ok], p[ok]
    den = np.abs(y) + np.abs(p)
    return float(np.where(den == 0, 0.0, 200 * np.abs(p - y) / np.where(den == 0, 1, den)).mean())

mean14 = np.repeat(np.nan_to_num(np.nanmean(hist[:, -14:], axis=1))[:, None], H, axis=1)
med14 = np.repeat(np.nan_to_num(np.nanmedian(hist[:, -14:], axis=1))[:, None], H, axis=1)
med56 = np.repeat(np.nan_to_num(np.nanmedian(hist[:, -56:], axis=1))[:, None], H, axis=1)
print("SMAPE mean 14 :", round(smape(true, mean14), 2))
print("SMAPE median 14:", round(smape(true, med14), 2))
print("SMAPE median 56:", round(smape(true, med56), 2))
print("SMAPE zeros     :", round(smape(true, np.zeros_like(true)), 2))
# Output:
# SMAPE mean 14 : 54.49
# SMAPE median 14: 30.52
# SMAPE median 56: 30.4
# SMAPE zeros     : 133.33
```

The median beats the mean by a wide margin. For pages with very few views, the mean is a small positive number. Every day with actual 0 then costs the maximum 200. The median is 0 for those pages. The 56-day median is also not hurt by the viral spike inside its window. Predicting all zeros is bad (133): it costs 200 for every active page.

## Common mistakes

- Dividing by zero in SMAPE and getting NaN.
- Counting missing actuals as zero.
- Using the mean on spiky pages.
- Predicting 0 for pages that have any recent traffic.
- A random validation split.
- Putting all 145k series through a slow per-series model such as ARIMA.
- Forgetting the 60-day gap between the training end and the scored period in stage 2.

## Interview lens

**Typical question:** "You must forecast views for 100,000 pages with only their history. Where do you start?"

**Strong answer:** "I start with robust baselines: the median of the last weeks, and a weekday-adjusted median. I validate on the last 60 days with the metric, SMAPE. I handle zeros and missing days with care. SMAPE gives the maximum error when I predict a positive number for an actual zero. So I treat dead pages carefully. Then I build one global model on log views scaled per page, with weekday and long-lag features. I use gradient boosting or a recurrent network, and I ensemble. I would not fit a separate classical model for each of 100,000 pages."

**Red flags:** per-page ARIMA for all pages; mean instead of median; ignoring NaN and zero rules.

## Real world

- The competition was hosted by Kaggle with Google as a sponsor, using Wikipedia page view counts. Its 1st-place solution is public, and so are many strong write-ups on median baselines.
- Problems of this shape are common in industry. They have traffic or demand for many items with short or missing histories. A global model beats per-series models in cost and often in accuracy.

## Key points

- Task: 60-day views for about 145k Wikipedia pages. The metric is SMAPE. A 0 vs 0 pair scores 0. Actual 0 with a positive forecast scores 200. Missing actuals are ignored.
- Median baselines are strong; a weekday-adjusted median is stronger when the week pattern is clear.
- Validate on the last 60 days; the real test was a future period.
- Global models on log, per-page scaled data (boosting or seq2seq GRU) with ensembles win.
