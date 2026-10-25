---
id: s14-05-fva-and-roi
title: Forecast value add (FVA) and ROI math
minutes: 35
level: staff
goals: [Compute FVA for each step of a forecast process, Find steps that destroy value and act on them, Build a simple ROI model with assumptions and ranges, Explain payback in terms a finance partner accepts]
prereqs: [s14-01-framing-problems]
tags: [staff, FVA, ROI, process, business-case]
skills: [staff, metrics, baseline-first]
---

## Warm-up

```check
{"q": "Cost of under-stock is 3 and over-stock is 1. Which quantile should you plan for?", "type": "single",
 "options": ["0.25", "0.50", "0.75", "0.90"],
 "answer": 2,
 "why": ["That is the over-stock share.", "That is for equal costs.", "Correct: 3 / (3 + 1) = 0.75.", "That would need a cost ratio of 9 to 1."]}
```

```check
{"q": "Which metric is scale-free, so you can compare series of different size?", "type": "single", "options": ["MAE", "MASE", "RMSE", "Total error in units"], "answer": 1, "why": ["MAE has the unit of the data.", "Correct: MASE divides by a naive error.", "RMSE has the unit of the data.", "Units depend on the series size."]}
```

## Why it matters

A company runs a monthly forecast process: a statistical model, then a machine-learning model, then planners adjust the numbers in a meeting. Everyone works hard. Nobody knows if all this effort helps. **Forecast value add (FVA)** answers one simple question for each step: *does this step make the forecast better than the step before it?* In practice, some steps do not. Finding them saves time and money. Then you need to prove the value of the steps that do help. That is **ROI** (return on investment).

## FVA step by step

1. List the steps in the forecast process in order.
2. Keep the forecast **after each step** (for example in a table).
3. Compute the same error metric for every step (for example WAPE) on the same periods.
4. FVA of a step = error of the previous step − error of this step. Positive means the step helps.

The first step is a **baseline**, usually naive or seasonal naive. A process whose final forecast is not better than the baseline wastes money.

```chart
{"title": "WAPE after each step of an example process (bars 1 to 4: naive, statistical, ML, manual override)", "x": "step", "height": 220,
 "series": [
   {"name": "WAPE (%)", "kind": "bar", "x": [1,2,3,4], "y": [24, 17, 14, 16]}
 ],
 "caption": "The statistical step and the ML step help. The manual override makes the forecast worse (14% to 16%): negative FVA."}
```

```check
{"q": "WAPE after the ML step is 14% and after the manual override it is 16%. What is the FVA of the override, in percentage points?", "type": "numeric",
 "answer": -2, "tol": 0.01,
 "why": "FVA = previous error − this error = 14 − 16 = −2 points. The override destroys value."}
```

## What FVA tells you

- **A step with negative FVA** should be changed or removed. Common culprits: manual overrides made without evidence, and complex models that lose to simple ones.
- **Where overrides do help.** Often for events the model cannot know (a new store opening, a one-off deal). Track FVA **by type of override**, and keep those that add value.
- **Bias.** Human adjustments often add optimism. Measure bias with FVA.
- **Cost.** A step that adds 0.1 point of accuracy but costs ten hours of work per week may still not be worth it.

The problem [[problem:fva-per-step]] lets you compute this table.

```check
{"q": "Which finding would make you change the process?", "type": "single",
 "options": ["Statistical model has positive FVA", "Planner overrides have negative FVA on most items", "The baseline is naive", "The ML model has positive FVA"],
 "answer": 1,
 "why": ["That is good.", "Correct: most overrides make the forecast worse. Fix or reduce them, and keep the useful ones.", "A naive baseline is expected.", "That is good."]}
```

## ROI math: from accuracy to money

A finance partner will not accept "WAPE improved by 3 points". Convert it to money in four steps:

1. **Cost of error.** How much does one unit of absolute error cost? (waste, lost margin, expedite fees, extra stock). Write it as a share of sales value: for example 0.25.
2. **Annual cost of error** = WAPE × annual sales × cost factor.
3. **Savings** = cost before − cost after.
4. **Net benefit** = savings − project cost (people, compute, licences). **Payback** = project cost ÷ monthly savings.

Always show **a range**: a cautious case and an expected case. State every assumption. Check the largest assumption first (usually the cost factor), because it moves the result most.

```check
{"q": "Annual sales 100M, cost factor 0.20. WAPE falls from 0.18 to 0.15. What are the annual savings, in millions?", "type": "numeric",
 "answer": 0.6, "tol": 0.01,
 "why": "Cost before = 0.18 × 100 × 0.20 = 3.6. Cost after = 0.15 × 100 × 0.20 = 3.0. Savings = 0.6 million."}
```

## Common traps in ROI

- **Counting savings twice** (the same stock-out reduction credited to two projects).
- **Ignoring run costs** after launch (monitoring, retraining, support).
- **Assuming 100% adoption.** If planners ignore the forecast, savings are zero.
- **Using the wrong baseline.** Compare to what would have happened without the project, not to a bad old model.
- **One number.** Give a range and name the main assumption.

```check
{"q": "Project cost is 600k. Expected savings are 1.2M per year. What is the payback time in months?", "type": "numeric",
 "answer": 6, "tol": 0.01,
 "why": "Monthly savings = 1.2M / 12 = 100k. Payback = 600k / 100k = 6 months."}
```

## Worked example

We compute a net benefit with a cautious and an expected case. Savings come from a lower WAPE.

```python
sales = 200e6            # annual sales value
scenarios = {
    "cautious": {"wape_old": 0.17, "wape_new": 0.155, "cost_factor": 0.15, "adoption": 0.7},
    "expected": {"wape_old": 0.17, "wape_new": 0.140, "cost_factor": 0.25, "adoption": 0.9},
}
project_cost = 1.2e6     # people + infrastructure per year

for name, s in scenarios.items():
    cost_old = s["wape_old"] * sales * s["cost_factor"]
    cost_new = s["wape_new"] * sales * s["cost_factor"]
    savings = (cost_old - cost_new) * s["adoption"]     # only adopted forecasts save money
    net = savings - project_cost
    payback_months = project_cost / (savings / 12)
    print(f"{name:9s} savings {savings/1e6:5.2f}M  net {net/1e6:5.2f}M  payback {payback_months:4.1f} months")
# Output:
# cautious  savings  0.32M  net -0.89M  payback 45.7 months
# expected  savings  1.35M  net  0.15M  payback 10.7 months
```

In the cautious case the project loses money in year one and needs almost four years to pay back. In the expected case it pays back in about 11 months. A decision maker sees both, and sees which assumptions matter (cost factor and adoption). The case is only safe if the cautious case is still acceptable, so you may need a smaller first scope.

## Common mistakes

- Measuring FVA on different periods for different steps.
- Computing FVA on a metric that hides bias.
- Treating all overrides alike.
- Claiming savings without a baseline for what happens without the project.
- Giving one ROI number without assumptions.
- Forgetting adoption and run costs.

## Interview lens

**Typical question:** "How would you show that a new forecasting project is worth 4 engineers for a year?"

**Strong answer:** "First I measure FVA of today's process on a golden backtest to see where value is made or lost. Then I convert the expected accuracy gain into money: cost of error per unit, annual volume, and a realistic adoption rate. I show a cautious case and an expected case, with payback time. I name the biggest assumption and plan a pilot that measures it directly, for example the cost of a stock-out. I include run costs. If the cautious case does not pay back, I would choose a smaller scope."

**Red flags:** no baseline; one number; no assumptions; ignoring adoption.

## Real world

- Forecast value added analysis was popularised in the business-forecasting community by Michael Gilliland of SAS in his writing and book on business forecasting. His public writing reports that, in many organisations, some manual adjustments make forecasts worse.
- The M-competition papers repeatedly show that simple methods and combinations are hard to beat. This is the reason a simple baseline sits at the start of any FVA table.

## Staff lens

FVA is also a political tool, so use it kindly. Show the table to planners as a way to focus their effort where it adds value, and not as a way to blame them. Offer them better inputs, like model explanations, so their overrides improve. Agree the metric and the periods with finance before you show results.

## Key points

- FVA = error of the previous step − error of this step, on the same periods; positive means value added.
- The first step is a baseline; steps with zero or negative FVA should change.
- ROI: WAPE × sales × cost factor gives cost of error; savings × adoption − run cost gives net benefit.
- Show a cautious and an expected case, name the main assumption, and measure it in a pilot.
