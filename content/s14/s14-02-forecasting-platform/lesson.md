---
id: s14-02-forecasting-platform
title: Forecasting platform architecture - one platform, many teams
minutes: 40
level: staff
goals: [Explain why a shared platform beats one-off models once you have several teams, Name the six building blocks and what each one guarantees, Choose between self-serve and managed service levels, Keep forecasts consistent across levels of the organisation]
prereqs: [s14-01-framing-problems]
tags: [staff, platform, architecture, data-contract, registry]
skills: [staff, scale, production]
---

## Warm-up

```check
{"q": "From the last lesson: what sets the minimum forecast horizon?", "type": "single",
 "options": ["The size of the data", "Lead time plus review period", "The model type", "The number of teams"],
 "answer": 1,
 "why": ["Data size does not set the horizon.", "Correct: the forecast must cover until the next decision can take effect.", "The model type is chosen after the horizon.", "Teams do not set the horizon."]}
```

## Why it matters

The first team that needs forecasts builds a notebook. The second team copies it. By the fifth team, you have five pipelines, five metrics, and five different answers to "what is the forecast for next quarter?". Finance and operations argue about whose numbers are right. A **platform** is one set of shared parts that many teams use. It does not make every forecast better. It makes forecasting **cheaper, safer, and consistent**.

```chart
{"title": "Cost of forecasting for N teams (arbitrary units)", "x": "teams", "height": 230,
 "series": [
   {"name": "separate pipelines (10 per team)", "x": [1,2,3,4,5,6,7,8], "y": [10,20,30,40,50,60,70,80]},
   {"name": "shared platform (25 fixed + 3 per team)", "x": [1,2,3,4,5,6,7,8], "y": [28,31,34,37,40,43,46,49]}
 ],
 "caption": "With one or two teams, separate pipelines are cheaper. Around the fourth team the platform wins, and the gap grows."}
```

```check
{"q": "In the chart, when does the shared platform become cheaper?", "type": "single",
 "options": ["With 1 team", "With 2 teams", "With 4 or more teams", "Never"],
 "answer": 2,
 "why": ["At 1 team: platform 28 vs separate 10.", "At 2 teams: platform 31 vs separate 20.", "Correct: at 4 teams the platform costs 37 and separate pipelines 40.", "The lines cross, so it becomes cheaper."]}
```

## Six building blocks

| Block | Job | Guarantee to teams |
|---|---|---|
| 1. Data contracts | Agree schema, freshness and quality of inputs | "Your data arrives on time, in this shape, or we alert you" |
| 2. Feature and calendar layer | Shared holidays, events, lags, point-in-time joins | "No leakage; the same feature means the same thing" |
| 3. Model library and registry | Versioned models, parameters, lineage | "You can reproduce any past forecast" |
| 4. Backtest service | One way to evaluate, same folds, same metrics | "Numbers are comparable between teams" |
| 5. Training and serving | Batch jobs, scheduling, storage, APIs | "Forecasts are ready by 6 am; failures retry and alert" |
| 6. Monitoring and governance | Accuracy, drift, cost, access, change control | "A bad model is caught before the business is" |

A **data contract** is a written agreement between the team that produces data and the team that uses it. It lists column names and types, how fresh the data is, and rules such as "no negative sales". A **model registry** is a catalogue that stores each model version with its code, data, parameters and scores.

```check
{"q": "Which block makes sure two teams report comparable accuracy numbers?", "type": "single",
 "options": ["Model registry", "Backtest service with shared folds and metrics", "Data contracts", "Serving API"],
 "answer": 1,
 "why": ["The registry stores versions, not evaluation rules.", "Correct: one evaluation path gives numbers that can be compared.", "Contracts protect inputs.", "Serving delivers forecasts."]}
```

## Self-serve versus managed

Different teams need different support. Offer levels, not one size.

| Level | What the team gets | Good for |
|---|---|---|
| Self-serve | Libraries, templates, docs; the team owns the pipeline | Strong data-science teams with unique needs |
| Managed forecast | The platform team runs forecasts for you from a config | Teams with a standard need (daily demand) |
| Embedded | A platform engineer works inside the team for one quarter | New, high-value use cases |

Rules of thumb: put standard cases on the managed path (cheap and safe). Keep self-serve for special cases, but require the same contracts, the backtest service and monitoring. A platform that forces every team into one model will be ignored.

```check
{"q": "A new team needs a standard daily demand forecast and has no ML staff. Which level fits?", "type": "single",
 "options": ["Self-serve", "Managed forecast", "No support", "Embedded for a year"],
 "answer": 1,
 "why": ["They have no staff to own a pipeline.", "Correct: a config-driven managed service is fast and safe.", "They would build an unsafe pipeline.", "Too costly for a standard need."]}
```

## Consistency across the organisation

Finance plans by country and quarter. Operations plans by store and day. If both forecast separately, the totals will not match. Two answers:

- **Hierarchical reconciliation:** adjust the forecasts so that the parts add up to the total. The platform can offer this as a standard step.
- **One source of truth:** publish the official forecast with a version and an owner. Other teams consume it and do not rebuild it.

Say clearly which number is "the plan" and which one is "the best estimate". They can differ, but the difference must be known.

## Worked example

A data contract check is a small piece of code that every input table must pass. This one checks columns, types, freshness and quality.

```python
import pandas as pd

CONTRACT = {
    "columns": {"store": "object", "date": "datetime64[ns]", "sales": "float64"},
    "max_age_days": 2,
    "rules": ["sales >= 0", "no duplicate (store, date)"],
}

def check_contract(df, contract, today):
    problems = []
    for col, dtype in contract["columns"].items():
        if col not in df.columns:
            problems.append(f"missing column: {col}")
        elif str(df[col].dtype) != dtype:
            problems.append(f"wrong type for {col}: {df[col].dtype}")
    if problems:
        return problems
    age = (today - df["date"].max()).days
    if age > contract["max_age_days"]:
        problems.append(f"stale data: newest row is {age} days old")
    if (df["sales"] < 0).any():
        problems.append("negative sales")
    if df.duplicated(["store", "date"]).any():
        problems.append("duplicate (store, date) rows")
    return problems

df = pd.DataFrame({
    "store": ["A", "A", "B"],
    "date": pd.to_datetime(["2024-03-01", "2024-03-01", "2024-03-02"]),
    "sales": [10.0, -4.0, 7.0],
})
for p in check_contract(df, CONTRACT, pd.Timestamp("2024-03-06")):
    print(p)
# Output:
# stale data: newest row is 4 days old
# negative sales
# duplicate (store, date) rows
```

The platform runs this check before every training and scoring job. A failure blocks the job and alerts the data owner. This is cheaper than a wrong forecast.

## Common mistakes

- Building the platform before three real teams need it.
- One model for all teams.
- No data contracts, so the platform breaks silently when an upstream table changes.
- Different metric definitions per team.
- No versioning, so nobody can reproduce last month's forecast.
- A platform without an owner or a roadmap.
- Counting platform success by "number of models" and not by business results.

## Interview lens

**Typical question:** "Five teams each build their own forecasts. How would you consolidate them?"

**Strong answer:** "I would not start with code. I would interview the five teams about their decisions and see what they share: calendars, data sources, metrics. I would offer a shared backtest service and data contracts first, because they give quick wins and comparable numbers. Then I would add a managed path for the standard use cases and keep self-serve for special ones. I would measure success by onboarded teams, forecast value add over each team's old process, and incidents avoided. Finance and operations numbers would be reconciled at a defined level."

**Red flags:** a big-bang rewrite; forcing one model on everyone; no metric for platform success; no migration path.

## Real world

- Uber's engineering blog has described its internal forecasting platform and open-source forecasting work, such as the Orbit library, for use across many teams. Amazon published the DeepAR approach, which trains one model across many related series, as a service building block.
- Open-source and cloud services such as GluonTS, Nixtla's tools and managed forecasting services exist because many companies faced the same problem.

## Staff lens

Platforms fail for organisational reasons more than technical ones. Start with the two teams that hurt the most, and give them something they cannot build faster alone. Publish a short roadmap and a service level for each block. Say what the platform will **not** do. Review adoption every quarter: if teams route around the platform, find out why.

## Key points

- A shared platform pays off from about the third or fourth team; before that, keep it light.
- Six blocks: data contracts, feature layer, model registry, backtest service, training and serving, monitoring and governance.
- Offer service levels: self-serve, managed, embedded.
- Reconcile forecasts across levels, and publish one official version.
- Measure the platform by adoption and business results, not by the number of models.
