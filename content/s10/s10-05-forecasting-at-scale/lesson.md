---
id: s10-05-forecasting-at-scale
title: Forecasting at scale: millions of series
minutes: 25
level: advanced
goals: [Estimate the compute and cost of forecasting millions of series, Choose between local and global models at scale, Use parallelism, caching and fallbacks to keep a system reliable]
prereqs: [s10-04-forecast-error-alerts]
tags: [scale, global-models, cost, parallelism, fallback]
skills: [ml-system-design]
---

## Warm-up

```check
{"q": "The tracking signal is...", "type": "single",
 "options": ["Running sum of errors / running MAD", "MAE / mean actual", "PSI of the target"],
 "answer": 0,
 "why": ["Correct: it shows slow bias.", "That is closer to WAPE.", "PSI measures distribution shift of inputs."]}
```

```check
{"q": "A job writes forecasts by upsert on (date, series_id). It is retried. The table is unchanged by the retry. This property is called...", "type": "single",
 "options": ["Stationarity", "Idempotency", "Seasonality"],
 "answer": 1,
 "why": ["Stationarity is a property of data.", "Correct.", "Seasonality is a data pattern."]}
```

## Why it matters

A retail company has 3 000 stores and 50 000 products. That is 150 million possible store-product series. Forecasting one series takes a fraction of a second, but 150 million fractions add up to days. Say the plan is needed at 06:00 and the job needs 30 hours. Then the system is useless, however good the model is. At scale, **engineering decisions are modelling decisions**.

## The size of the problem

Start with a back-of-the-envelope estimate. It is a skill interviewers like.

Example: 2 million series, one local model fit and predict takes 20 ms on one CPU core.

- Total work = 2 000 000 × 0.02 s = 40 000 s = **11.1 hours** on one core.
- On 100 cores = 6.7 minutes (if the work splits evenly and loading data is cheap).

```chart
{"title": "Wall time for 2 million series (20 ms each)", "x": "workers (cores)", "height": 220,
 "series": [{"name": "minutes", "x": [1, 2, 4, 8, 16, 32, 64, 128, 256], "y": [666.7, 333.3, 166.7, 83.3, 41.7, 20.8, 10.4, 5.2, 2.6]}],
 "caption": "Time halves when workers double, as long as the work can be split. In practice, reading data and writing results add a fixed cost."}
```

```check
{"q": "300 000 series, 50 ms per series, 20 cores. How many minutes (ideal)?", "type": "numeric",
 "answer": 12.5, "tol": 0.01,
 "why": "300 000 × 0.05 s = 15 000 s. Divide by 20 cores = 750 s = 12.5 minutes."}
```

## Local or global models

A **[[local model]]** is fitted separately for each series (ETS, ARIMA per series). A **[[global model]]** is one model trained on many series together (LightGBM with lag features, or a neural net).

| | Local | Global |
|---|---|---|
| Models to train | One per series (millions) | One, or one per group |
| Training cost | Grows with series count | Grows with total rows, one big job |
| Short or new series | Poor: little history | Good: learns from similar series |
| Per-series quirks | Captured | Needs features (id, group) |
| Serving | Store millions of parameters | One model file, fast batch predict |

In the M5 competition (later lesson), global LightGBM-style models won. At large scale, global models are also much easier to run. There is one training job and one artifact. New series work from day one, so the **[[cold start]]** problem is smaller.

A common design is **tiered**. A global model covers most series. A simple method, such as seasonal naive or a moving average, covers tiny or intermittent series. The top revenue series get special handling with analysts in the loop.

```check
{"q": "A new product has 10 days of history. Which approach copes best?", "type": "single",
 "options": ["A separate ARIMA with a yearly season", "A global model that uses product group and price as features", "No forecast"],
 "answer": 1,
 "why": ["10 days cannot support a yearly season.", "Correct: it borrows strength from similar products.", "A fallback such as the group average is better than nothing."]}
```

## Parallelism and data layout

Time-series forecasting is **embarrassingly parallel** across series: each series is independent. Good patterns:

- **Partition by series id** (or a hash of it), so each worker gets whole series. Tools: Spark, Dask, Ray, or many small batch jobs.
- **Keep series together.** Sort and store data by `(series_id, time)`. Avoid a full shuffle.
- **Batch many series into one call** (vectorised numpy or one DataFrame per worker) instead of one tiny task per series.
- **Incremental runs**: score only series whose input changed, or whose forecast is stale.
- **Cache** features and forecasts. If sales for a series did not change, reuse the last forecast.
- **Right-size the model.** A model that is 1% more accurate but 20 times slower is often the wrong choice.

```check
{"q": "Why is 'one task per series' a bad design for 5 million short series?", "type": "single",
 "options": ["Python cannot run 5 million tasks", "Task start-up cost is larger than the work, so batch many series per task", "Series depend on each other", "It uses too little memory"],
 "answer": 1,
 "why": ["It can, but it is slow.", "Correct: overhead dominates. Group series into batches.", "They are independent. That is why they are parallel.", "Memory is not the reason."]}
```

## Reliability: fallbacks and guards

At scale, something always fails: a bad file, a slow worker, a series with all zeros. Design for it.

1. **Fallback chain.** Primary model, then simple model, then last known forecast. Log which level was used.
2. **Sanity checks** on output: no NaN or negative demand, and values within a range of recent history. An example limit is 5 times the recent maximum.
3. **Timeouts** per series or batch, so one slow series does not block the job.
4. **Partial success.** If 0.1% of series fail, publish the rest and alert.
5. **Cost tracking.** Record compute minutes and cost per run. Cost can grow silently with the catalogue size.

## Worked example

We compare the "work estimate" for three designs. Then we run a vectorised seasonal naive forecast for 20 000 series at once with pandas. There is no Python loop over series.

```python
import numpy as np
import pandas as pd

# 1) back-of-the-envelope plan
series = 2_000_000
for name, ms, cores in [("local ETS", 20, 100), ("local ARIMA", 150, 100), ("global LightGBM (1 job)", None, 64)]:
    if ms is None:
        print(f"{name:<24} one training job + batch predict")
    else:
        minutes = series * ms / 1000 / 60 / cores
        print(f"{name:<24} {minutes:7.1f} min on {cores} cores")

# 2) vectorised seasonal naive for many series: last 7 days repeated
rng = np.random.default_rng(0)
n_series, n_days = 20_000, 28
wide = pd.DataFrame(rng.poisson(20, (n_days, n_series)))   # rows = days, columns = series
last_week = wide.iloc[-7:]                                   # one slice, all series at once
forecast = pd.concat([last_week] * 2, ignore_index=True)     # 14-day horizon
print("forecast shape:", forecast.shape)
print("first series, first 7 days:", forecast.iloc[:7, 0].tolist())
# Output:
# local ETS                    6.7 min on 100 cores
# local ARIMA                 50.0 min on 100 cores
# global LightGBM (1 job)  one training job + batch predict
# forecast shape: (14, 20000)
# first series, first 7 days: [16, 13, 22, 19, 17, 19, 18]
```

The point: the loop is over **groups of data**, not over single series. The same idea (vectorise, batch, partition) works with Spark or Dask.

## Common mistakes

- Fitting a heavy model per series because "it worked on 10 series".
- Not measuring cost per run. The bill grows with the catalogue.
- No fallback: one failed batch means missing forecasts for thousands of items.
- Forecasting everything at the same quality, even the long tail that nobody uses. Match effort to business value.
- Skipping a cache: the same unchanged series is recomputed every night.

## Interview lens

**Typical question:** "We have 5 million series and need forecasts every night in 2 hours. How do you design it?"

**Strong answer:** First I estimate the compute: series count times time per series divided by cores. Then I choose models by value. A global gradient-boosting model covers most series. A simple baseline covers the long tail and intermittent series. Analysts review the top series. I partition by series id, batch many series per task, and score only series whose inputs changed. Output goes to a keyed table by upsert. Each step has a fallback and a timeout. I alert when more than a small share of series fall back. I track cost per run.

**Red flags:** Starting with the most complex model. No numbers. One model per series with no plan for cold start. No fallback.

## Real world

Public papers and talks show the same trend. Amazon's DeepAR paper (2017) trains one neural model across many related series. The M5 competition (2020) was won by global models built with LightGBM. Open-source tools such as Nixtla's statsforecast focus on making per-series classical models fast with compiled code and parallelism. The approach is always: fewer, shared models and fast compiled loops.

## Key points

- Estimate first: series × time per series ÷ cores.
- Global models train once, handle new series, and are easier to serve. Local models can be better for a few important series.
- Series are independent, so partition by series id and batch many series per task.
- Cache and score only what changed.
- Add fallbacks, sanity checks, timeouts and cost tracking.
