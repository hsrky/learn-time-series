---
id: s13-06-ml-system-design-rubric
title: ML system design for forecasting - the rubric
minutes: 35
level: advanced
goals: [Use a six-part frame for any forecasting design question, Do quick back-of-the-envelope numbers for series count and compute, Name failure modes and monitoring checks, Score yourself with a rubric after a timed drill]
prereqs: [s13-01-how-interviews-work]
tags: [system-design, interview, rubric, forecasting]
skills: [scale, production, communication]
---

## Warm-up

```check
{"q": "A design prompt says: 'Forecast demand for our stores.' Which fact do you need first?", "type": "single",
 "options": ["The cloud vendor", "Which decision uses the forecast and how far ahead", "The GPU type", "The programming language"],
 "answer": 1,
 "why": ["A detail for later.", "Correct: the decision and the horizon shape the whole design.", "Compute comes after the problem is clear.", "A detail for later."]}
```

## Why it matters

In a system design round there is no single right answer. The interviewer scores **how you think**. They want to see that you ask questions, use numbers, compare options, and think about what breaks. A fixed frame keeps you calm and complete. This lesson gives a six-part frame, a time plan, and a rubric. After the lesson, do the timed drill below.

## The six-part frame

Use the same six parts every time.

| Part | Key questions |
|---|---|
| 1. Requirements and decision | Who acts on the forecast? What is the cost of a wrong forecast? Horizon, granularity, how often? |
| 2. Data and features | Sources, history, freshness, missing data, known-future inputs (price, promotion, holidays) |
| 3. Models and baselines | Baseline first. Local or global? Hierarchy? Cold start? Probabilistic? |
| 4. Evaluation and backtest | Metric tied to cost. Backtest design. Segments. Offline versus online test |
| 5. Serving and scale | Batch or real time? Storage, schedule, latency, cost, retries |
| 6. Monitoring and failure modes | Data checks, drift, accuracy tracking, fallbacks, retraining, human override |

```chart
{"title": "A 45-minute plan (minutes per part, bars 1 to 6 in table order)", "x": "part", "height": 210,
 "series": [
   {"name": "minutes", "kind": "bar", "x": [1,2,3,4,5,6], "y": [8, 7, 8, 8, 7, 7]}
 ],
 "caption": "Parts 1 and 4 get a little more time. Keep the last 5 minutes for questions from the interviewer."}
```

```check
{"q": "Which of these is a part-6 (monitoring) item?", "type": "single",
 "options": ["Choose the loss function", "Alert when the 7-day bias moves above 5%", "Pick the training window", "Decide the forecast horizon"],
 "answer": 1,
 "why": ["That belongs to models.", "Correct: tracking accuracy and bias after launch is monitoring.", "That belongs to models and evaluation.", "That belongs to requirements."]}
```

## Numbers first: size the problem

Use simple multiplication to find the scale. Do it out loud.

- 2,000 stores × 500 products = **1,000,000 series**.
- Daily data for 3 years = about 1,100 points per series, so about **1.1 billion rows**.
- Forecast 14 days ahead every night = 14 million numbers per night.
- If one local model takes 20 ms, 1,000,000 models take 20,000 s on one CPU, or about 5.6 hours. With 100 CPUs it takes about 3.3 minutes.

These numbers tell you if you need a distributed job, a global model, or both. See the worked example.

```check
{"q": "600 stores × 1,000 products = how many series?", "type": "numeric",
 "answer": 600000, "tol": 0,
 "why": "600 × 1,000 = 600,000 series. Each is a separate forecast target."}
```

## Show trade-offs, not just choices

For every major choice, say the option, the reason, and the cost.

- **Global LightGBM versus per-series ETS.** Global models share strength across short or sparse series and are fast to serve; they need good features. ETS is simple, but needs one fit per series.
- **Batch versus real time.** Daily retail replenishment is batch: forecasts are ready before the morning. Real time is only needed when the input changes within the hour, like ride-hailing demand.
- **Point versus quantile.** If over-stocking and under-stocking cost different amounts, forecast quantiles.

```check
{"q": "Which statement shows a real trade-off?", "type": "single",
 "options": ["I will use deep learning because it is modern.", "A global LightGBM is cheaper to serve and shares data across sparse series, but needs careful lag features and can miss a single series' quirks.", "Everything will be monitored.", "Use the best model."],
 "answer": 1,
 "why": ["No reason and no cost.", "Correct: it names a benefit, a cost, and a condition.", "Too vague.", "No criteria."]}
```

## Failure modes to mention

Interviewers love this part. Pick 4 or 5 from this list.

- Late or missing data (a store feed fails).
- A promotion that was not entered in the system.
- A new product with no history (cold start).
- A holiday that moved or was missing in the calendar.
- A change in the world: a competitor opens, supply problems, a policy change.
- Feedback loop: the forecast changes the stock, and the stock changes the sales you observe (censored demand, because sales stop when stock runs out).
- A bad deploy that changes the feature code between training and serving.

For each, say how you detect it and the fallback (for example, use seasonal naive, or last week's forecast).

```check
{"q": "Sales are zero on days when the shelf was empty. Why is this a problem for training?", "type": "single",
 "options": ["Zeros are always correct", "Observed sales understate true demand (censored demand), so the model learns too low", "Zero values are not allowed in LightGBM", "It makes the series stationary"],
 "answer": 1,
 "why": ["Zero sales from stock-outs are not zero demand.", "Correct: the model learns from sales, not from demand.", "LightGBM accepts zeros.", "Stationarity is not the issue."]}
```

## Worked example

A quick capacity estimate, the way you would do it on a whiteboard. We write it as code so the arithmetic is checked.

```python
stores, products = 2000, 500
series = stores * products
years, days_per_year = 3, 365
rows = series * years * days_per_year
horizon = 14

forecast_values_per_night = series * horizon
ms_per_local_model = 20
cpu_seconds = series * ms_per_local_model / 1000
cpu_hours = cpu_seconds / 3600
workers = 100
minutes_parallel = cpu_seconds / workers / 60

print("series:", f"{series:,}")
print("history rows:", f"{rows:,}")
print("forecast values per night:", f"{forecast_values_per_night:,}")
print("local models, one CPU:", round(cpu_hours, 1), "hours")
print("local models, 100 workers:", round(minutes_parallel, 1), "minutes")
# Output:
# series: 1,000,000
# history rows: 1,095,000,000
# forecast values per night: 14,000,000
# local models, one CPU: 5.6 hours
# local models, 100 workers: 3.3 minutes
```

So even a simple local model needs a parallel job. A global model trained once a week and scored nightly can be cheaper. Say this out loud in the interview, then pick one.

## Common mistakes

- Jumping to a model in the first minute.
- No numbers at all.
- Forgetting the baseline and the backtest.
- Ignoring cold start and holidays.
- No monitoring or fallback.
- Describing tools, not decisions (long lists of cloud services).
- Not asking about the cost of errors.

## Interview lens

**Typical question:** "Design a demand forecasting system for 2,000 stores."

**Strong answer:** "First I ask who uses it. Suppose it is store replenishment: a 14-day daily forecast, refreshed nightly, with quantiles because stock-outs and waste cost differently. I size it: about a million series. I would start with a seasonal naive baseline and a global LightGBM using lags, calendar, price and promotion features, plus a hierarchy reconciliation step. I evaluate with a 4-fold weekly backtest, WAPE and bias by segment, and then an A/B test on a subset of stores. Serving is a nightly batch job writing to a table. I monitor input freshness, bias and a rolling WAPE, with a fallback to seasonal naive."

**Red flags:** no clarifying questions; only one model; no baseline; no monitoring; random split.

## Real world

- Companies have written publicly about large forecasting platforms: Uber's engineering blog describes forecasting at scale, and the DeepAR paper from Amazon researchers describes one model trained across many related series. These are good reading before a design round.
- The M5 competition used Walmart sales for thousands of items in many stores, with a hierarchy. It is a useful public case for scale and hierarchy.

## Key points

- Use six parts: requirements, data, models, evaluation, serving, monitoring.
- Do back-of-the-envelope numbers early: series count, rows, compute time.
- State trade-offs (benefit, cost, condition) for every major choice.
- Name 4 or 5 failure modes with detection and a fallback.
- Practise with the timed drill and score yourself with the rubric.
