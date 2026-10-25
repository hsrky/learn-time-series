---
id: s12-07-how-to-pick-a-library
title: How to pick a library: a decision table
minutes: 25
level: intermediate
goals: [Choose a library from task, data size and need for probabilistic output, hierarchy or deep models, Explain a sensible order of trying models, Justify the choice in an interview]
prereqs: [s12-06-more-libraries]
tags: [library-choice, decision-table, baselines]
skills: [forecasting-libraries, ml-system-design]
---

## Warm-up

```check
{"q": "Which tool finds discords (unusual subsequences) with the matrix profile?", "type": "single",
 "options": ["stumpy", "tsfresh", "pmdarima"],
 "answer": 0,
 "why": ["Correct.", "tsfresh extracts features.", "pmdarima searches ARIMA orders."]}
```

```check
{"q": "What is the safe order for predict and learn in a stream evaluation?", "type": "single",
 "options": ["Predict first, then learn", "Learn first, then predict", "Either order"],
 "answer": 0,
 "why": ["Correct.", "That leaks the answer.", "The order matters."]}
```

## Why it matters

There are dozens of libraries, and new ones appear every year. A strong engineer does not know all of them. A strong engineer has a **[[backtest|rolling backtest]]** and a **method** to choose: start from the task and the data, try the simplest tool that could work, and compare on a fair backtest. Interviewers often ask "which library would you use, and why?". A short, structured answer shows maturity.

## Four questions

1. **Task.** Forecast the future, classify series, cluster series, find anomalies, or extract features?
2. **Size.** One series, hundreds, or millions?
3. **Output.** Point forecast or probabilistic (quantiles)? Hierarchy that must add up?
4. **Model type.** Is classical enough, do we need covariates and global models (boosting), or deep models?

## Decision table: forecasting

| Situation | First choice | Why |
|---|---|---|
| One or few series, need to learn or explain | statsmodels (ETS, SARIMAX, STL) | Clear, classical, runs anywhere |
| Quick auto order for ARIMA | pmdarima, or statsforecast AutoARIMA | Automatic search |
| Thousands to millions of series, classical models | statsforecast | Fast compiled code, parallel |
| Many series with price, promotions, calendar | mlforecast (LightGBM) or scikit-learn lags | Global boosting wins on rich retail data |
| Need quantiles for decisions | statsforecast intervals, LightGBM quantile loss, GluonTS or AutoGluon | Planners need risk |
| Hierarchy must add up | hierarchicalforecast (reconciliation) | Coherent forecasts |
| Lots of data, long horizons, deep models wanted | neuralforecast (NHITS, PatchTST) or GluonTS | Deep models need data |
| Want the best result fast, little tuning | AutoGluon-TimeSeries (ensemble, Chronos) | AutoML ensemble |
| Many models and clean backtesting API | Darts or sktime | One interface |
| No training data, quick baseline | Chronos or TimesFM zero-shot, TimeGPT API | Pretrained |
| Business data with holidays and analysts | Prophet (as one candidate) | Interpretable parts |

## Decision table: other tasks

| Task | Library |
|---|---|
| Classify or cluster series | aeon, sktime, tslearn |
| Hand-crafted features for series | tsfresh |
| Motifs, discords in one long series | stumpy |
| Outliers on window features | PyOD |
| Stream, online learning | river |
| Stationarity tests, ACF, decomposition | statsmodels |

```check
{"q": "You need quantile forecasts for 2 million series with price and promotion features. What is a sensible first choice?", "type": "single",
 "options": ["mlforecast with LightGBM quantile models, compared with statsforecast intervals and seasonal naive", "One SARIMAX per series", "Prophet per series", "tsfresh"],
 "answer": 0,
 "why": ["Correct: global boosting scales and uses covariates.", "Too slow and no sharing.", "Too slow at that scale.", "tsfresh extracts features; it does not forecast."]}
```

```chart
{"title": "Illustration: gain from effort has diminishing returns", "x": "effort (models tried)", "height": 220,
 "series": [{"name": "error relative to naive", "x": [0, 1, 2, 3, 4, 5, 6], "y": [1.0, 0.82, 0.74, 0.70, 0.68, 0.675, 0.67]}],
 "caption": "Made-up shape. The big gain comes from the first sensible models (seasonal, then global features). Later tools give small gains."}
```

## A sensible order of work

1. **Plot and decompose** (statsmodels STL, ACF).
2. **Baselines**: naive, seasonal naive, and seasonal average.
3. **Classical**: ETS/Theta/ARIMA (statsmodels or statsforecast).
4. **Global ML** with lags and covariates (mlforecast, scikit-learn).
5. **Foundation model** zero-shot as a candidate (Chronos, TimesFM).
6. **Ensemble** the best different ones.
7. **Deep models** only if data is large and the gain is proven.

At each step use the **same rolling backtest** and a metric that fits the decision. Stop when the next step does not pay for its cost in time, compute and risk.

```check
{"q": "Why compare every library on the same rolling backtest?", "type": "single",
 "options": ["Otherwise differences in splits or metrics can look like differences in models", "It is faster", "Libraries require it", "It removes the need for baselines"],
 "answer": 0,
 "why": ["Correct.", "It is not faster.", "Libraries do not require it.", "Baselines are still needed."]}
```

## Worked example

Read this scenario and make a plan. The plan is an answer you could say in an interview.

**Scenario.** A grocery chain has 800 000 daily store-item series, price and promotion data, and needs quantiles for ordering. Some products are new.

**Plan.**

1. Baseline: seasonal naive (statsforecast), plus the planners' current method.
2. Global LightGBM in mlforecast with lags 1, 7, 14, 28, rolling means (shifted), calendar, price, promotion; target differencing; quantile objectives.
3. Compare on 4 rolling windows with WAPE, bias and pinball loss, by segment.
4. Hierarchy: reconcile with hierarchicalforecast if totals must match.
5. New products: group-level features, or zero-shot foundation model as a fallback.
6. Serving: nightly batch, idempotent upsert, fallback to seasonal naive.

## Common mistakes

- Choosing a library because a blog liked it.
- Starting with deep learning on a small dataset.
- Not using a baseline.
- Mixing too many libraries and data formats with no benefit.
- Ignoring the team: choose tools your team can run and maintain.
- Using a library you cannot run in production (licence, API cost, privacy).

## Interview lens

**Typical question:** "Which Python library would you use for forecasting, and why?"

**Strong answer:** It depends on the task, data size and output. For a few series I use statsmodels for tests, STL, ETS and SARIMAX. For many series I use statsforecast for fast classical baselines and mlforecast or scikit-learn with LightGBM for a global model with covariates, and I get quantiles through quantile objectives. If forecasts must add up I reconcile with hierarchicalforecast. For a strong result with little effort I try AutoGluon-TimeSeries or a zero-shot foundation model. Always I start with seasonal naive and compare on the same rolling backtest, then choose the simplest approach that wins.

**Red flags:** "I always use Prophet" or "I always use deep learning". No mention of baselines or of size and output type.

## Real world

The ecosystem changes fast, but the pattern in public benchmarks is stable: classical models are strong baselines, global boosting models do well with rich covariates, and combinations or AutoML ensembles are hard to beat. Always check the current documentation and release notes, because APIs change.

## Key points

- Choose by task, size, output type (point, quantile, hierarchy) and model type.
- Order of work: plot, baselines, classical, global ML, foundation model, ensemble, deep.
- Same rolling backtest and metric for every library.
- Pick the simplest tool that wins and that your team can operate.
