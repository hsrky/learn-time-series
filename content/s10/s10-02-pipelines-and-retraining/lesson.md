---
id: s10-02-pipelines-and-retraining
title: Pipelines, retraining cadence and backfills
minutes: 25
level: advanced
goals: [Choose batch or online forecasting for a use case, Pick a retraining schedule and a trigger, Make a pipeline idempotent so a backfill is safe]
prereqs: [s10-01-point-in-time-correctness]
tags: [pipeline, retraining, backfill, idempotency, production]
skills: [ml-system-design]
---

## Warm-up

```check
{"q": "Why can a feature NOT use data from after the prediction time?", "type": "single",
 "options": ["It makes the pipeline slower", "That data does not exist when the model runs live", "Pandas cannot join such data"],
 "answer": 1,
 "why": ["Speed is not the reason.", "Correct: in production the future is not yet known.", "Pandas can join it. That is the danger: it works, but it leaks."]}
```

```check
{"q": "An online store keeps...", "type": "single",
 "options": ["the full history", "the latest value per entity", "only the labels"],
 "answer": 1,
 "why": ["That is the offline store.", "Correct: it is built for fast reads of the newest value.", "Labels are separate from features."]}
```

## Why it matters

A forecast model is not a file. It is a **[[pipeline]]**: data comes in, features are built, the model predicts, results are stored, and someone uses them. Most production problems are not in the model. They are in the pipeline: a late file, a job that runs twice, a model that is never retrained. Interviewers for senior roles ask about these things first.

## Batch or online?

There are two ways to serve forecasts.

| | **[[batch prediction|Batch]]** | **[[online prediction|Online]]** |
|---|---|---|
| When | On a schedule (for example 02:00 every night) | On each request |
| Output | A table of forecasts for many series | One forecast in milliseconds |
| Cost | Low, compute is shared | Higher, servers must be always on |
| Fresh data | Up to one cycle old | Can use the newest value |
| Example | Stock plan for 5 000 stores for next 14 days | ETA for one delivery after the driver starts |

**Rule of thumb:** if the decision is made once per day or week, use batch. If a person or system waits for the answer, use online. Many systems mix: batch forecasts for the base level, and a small online step that corrects it with the latest data.

```check
{"q": "A supermarket orders stock once per day at 06:00 for the next 7 days. Which serving style fits best?", "type": "single",
 "options": ["Online prediction on each request", "A nightly batch job that writes a table", "Predict in the browser of the buyer"],
 "answer": 1,
 "why": ["Nobody waits for a single answer, so the cost of always-on servers is not needed.", "Correct: the decision is daily, so one scheduled run is cheaper and simpler.", "Not possible for shared planning data."]}
```

## Scheduling and dependencies

A batch pipeline is a chain of steps: **ingest, validate, build features, predict, write, check**. A **scheduler** (Airflow, cron, a cloud workflow tool) runs the steps in the right order and retries failed steps.

Good habits:

- **Validate input first.** Check row counts, missing days, and value ranges. Stop early if data is bad.
- **Write forecasts with a version**: model version, run time, and the *forecast origin* (the last day of data used).
- **Keep the old forecasts.** You need them later to measure real accuracy.
- **Set a fallback**: if the new run fails, keep yesterday's forecast or a seasonal naive forecast. Do not leave a hole.

## Retraining cadence

How often should you retrain? There are three common triggers.

1. **Time-based**: every night, week, or month. Simple and predictable.
2. **Performance-based**: retrain when the live error rises above a limit.
3. **Drift-based**: retrain when the input data changes a lot (next lessons).

```chart
{"title": "Error grows as the model gets old", "x": "days since training", "height": 220,
 "series": [
   {"name": "live error", "gen": [["trend", {"start": 8, "slope": 0.12}], ["noise", {"sd": 0.5}]], "n": 60, "seed": 4},
   {"name": "alert limit", "gen": [["const", {"value": 12}]], "n": 60, "dash": true}
 ],
 "marks": [{"x": 33, "label": "retrain here"}],
 "caption": "The error crosses the limit at about day 33. A weekly retrain would never reach it."}
```

The best cadence balances **cost** (compute, review time, risk of a bad new model) against **error** from old models. Fast-changing data (promotions, news) needs frequent retraining. Slow data (monthly energy) does not. A new model should never go live unchecked: run it as a **[[champion-challenger|challenger]]** next to the current **champion**, or in **[[shadow mode]]** where it predicts but nobody uses the output. Promote it only if it wins on a recent backtest.

```check
{"q": "Which trigger needs actual values (labels) to arrive first?", "type": "single",
 "options": ["Time-based retraining", "Performance-based retraining", "Drift-based retraining on input features"],
 "answer": 1,
 "why": ["It only needs a clock.", "Correct: you must compare forecasts with actuals, and actuals come later (label delay).", "Input drift can be seen without labels. This is why it is used as an early warning."]}
```

## Backfills and idempotency

A **[[backfill]]** re-runs the pipeline for past dates, for example after a bug fix or a new feature. It is dangerous if jobs are not **[[idempotent]]**.

**Idempotent** means: running the same job twice gives the same result as running it once. Example: a job that *appends* rows doubles the data when it runs twice. A job that *replaces* the rows for its key `(date, series_id)` does not.

How to build it:

- Use a **key** for every output row, and write with *upsert* (update or insert) or by replacing a whole date partition.
- Make the run depend only on its **inputs and the run date**, not on "now".
- Never read "latest" data inside the job. Read the data *as of the run date* (point-in-time again).
- Log which model version made each row.

```check
{"q": "A nightly job appends today's forecasts to a table. The scheduler retries it after a timeout, and it runs twice. What is the problem?", "type": "single",
 "options": ["Nothing, more data is better", "Duplicate rows: the job is not idempotent", "The model will become overfit", "The table will be sorted wrongly"],
 "answer": 1,
 "why": ["Duplicates double-count totals downstream.", "Correct. Use upsert on (date, series_id) so a retry gives the same table.", "The model is not changed by output rows.", "Sorting is not the issue."]}
```

## Worked example

We simulate a drifting series and compare retraining every 1, 7, 30 and 90 days. The "model" is simple: the mean of the last 28 days before the training day. We measure the mean absolute error.

```python
import numpy as np

rng = np.random.default_rng(0)
n = 400
level = 100 + np.cumsum(rng.normal(0, 1.0, n))   # slowly drifting level
y = level + rng.normal(0, 3, n)                   # plus noise

def mae_for_cadence(every, start=60):
    errs = []
    model = None
    for t in range(start, n):
        if (t - start) % every == 0:             # retrain on schedule
            model = y[t - 28:t].mean()
        errs.append(abs(y[t] - model))
    return np.mean(errs)

for every in [1, 7, 30, 90]:
    print(f"retrain every {every:>2} days -> MAE {mae_for_cadence(every):.2f}")
# Output:
# retrain every  1 days -> MAE 3.29
# retrain every  7 days -> MAE 3.51
# retrain every 30 days -> MAE 3.99
# retrain every 90 days -> MAE 6.37
```

The error falls as we retrain more often, but with diminishing returns. Going from 90 to 30 days removes 2.4 points of error. Going from 7 to 1 day removes only 0.2. This is the cost-versus-error trade-off in numbers.

## Common mistakes

- Retraining on a schedule and never comparing the new model with the old one.
- Using "latest data" inside a job. A backfill then gives different answers than the original run.
- Overwriting old forecasts. Without history you cannot compute live accuracy.
- No fallback forecast when the job fails.
- Retraining on the last few days only after an unusual event (a holiday, an outage) so the model learns the exception.

## Interview lens

**Typical question:** "How often would you retrain a daily demand model, and how do you do it safely?"

**Strong answer:** I start from how fast the data changes and what a bad forecast costs. I would begin with a weekly time-based retrain and add alerts on live error and input drift. Each new model runs as a challenger and is promoted only if it beats the champion on a recent rolling backtest. Jobs are idempotent and write to a keyed table with model version and forecast origin, so retries and backfills are safe. A seasonal naive forecast is the fallback.

**Red flags:** "Retrain every night" with no evidence. No version or origin stored. Appending instead of upserting. Not knowing label delay.

## Real world

Public engineering posts from many companies describe the same ideas: scheduled batch scoring, challenger models in shadow mode, and idempotent jobs for safe reruns. Workflow tools such as Apache Airflow made the "run the same job again for an old date" pattern (a backfill) a standard feature. The details differ per company, but the principles are the same.

## Key points

- Choose batch when decisions are periodic; choose online when someone waits for the answer.
- Retrain by time, by live error, or by drift. Balance cost against the error of an old model.
- Test every new model as a challenger or in shadow mode before it replaces the champion.
- Idempotent jobs (upsert by key, depend on run date only) make retries and backfills safe.
- Store model version and forecast origin with every forecast.
