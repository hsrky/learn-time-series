---
id: s10-07-design-demand-forecasting
title: Design case: demand forecasting for retail and food delivery
minutes: 40
level: staff
goals: [Follow a six-part structure for a forecasting design interview, Explain why sales are not the same as demand, Size the problem with simple numbers]
prereqs: [s10-06-forecasts-into-decisions]
tags: [system-design, demand, retail, censoring, drill]
skills: [ml-system-design]
---

## Warm-up

```check
{"q": "Shortage cost is 2 and waste cost is 6 per unit. Which quantile of demand do you order?", "type": "numeric",
 "answer": 0.25, "tol": 0.001,
 "why": "cu / (cu + co) = 2 / 8 = 0.25. Waste is expensive, so order a low quantile."}
```

```check
{"q": "FVA of a model with WAPE 18% against naive WAPE 24%:", "type": "single",
 "options": ["25%", "6%", "−25%", "33%"],
 "answer": 0,
 "why": ["Correct: (24 − 18) / 24 = 0.25.", "6 is the difference in points, not the relative gain.", "The sign is positive because the model is better.", "That divides by the model error instead of the naive error."]}
```

## Why it matters

"Design a demand forecasting system" is the most common system-design question for forecasting roles. The interviewer does not want a model name. They want to see that you ask about the **decision**, size the problem, handle messy data, and think about failures. This lesson gives a structure. Then you practise with the timed drill below.

## The six-part structure

Use the same six parts every time. The drill sections follow it.

1. **Requirements and decision.** Who uses the forecast, for what action? Horizon, granularity, update speed, cost of errors.
2. **Data and features.** Sources, history length, calendar, price, promotions, weather, stock levels. Point-in-time rules.
3. **Models and baselines.** Start simple (seasonal naive), then a global gradient-boosting model. Explain why.
4. **Evaluation and backtest.** Rolling-origin backtest, the right metric (WAPE, bias, pinball), baselines, segments.
5. **Serving and scale.** Batch or online, compute estimate, storage, fallbacks, who reads the output.
6. **Monitoring and failure modes.** Drift, bias alerts, retraining, new items, outages, feedback loops.

Spend about 2 minutes on part 1 and 8 minutes on each of the others in a 45-minute interview. Say your assumptions out loud.

```check
{"q": "What should you do FIRST in a design interview?", "type": "single",
 "options": ["Name the best model", "Ask what decision the forecast supports and what an error costs", "Draw the database schema", "Discuss GPUs"],
 "answer": 1,
 "why": ["A model name without a decision is a weak start.", "Correct: the decision sets the horizon, level of detail and metric.", "Too early.", "Hardware depends on the problem size, which you do not know yet."]}
```

## Sales are not demand

The most important data fact in retail: **you observe sales, not demand**. If a shelf is empty at 14:00, sales stop, but demand continues. The data shows low sales, and a naive model learns "this product sells less on this day". This is **[[censored demand]]**.

```chart
{"title": "Demand versus recorded sales when stock runs out", "x": "hour", "height": 230,
 "series": [
   {"name": "true demand", "y": [2, 3, 5, 8, 10, 12, 12, 11, 9, 8, 7, 6, 5, 4]},
   {"name": "recorded sales (stock = 40)", "y": [2, 3, 5, 8, 10, 12, 0, 0, 0, 0, 0, 0, 0, 0]}
 ],
 "caption": "Stock is 40 units. After hour 5 the shelf is empty, so sales are zero while demand continues."}
```

Ways to handle it:

- Mark **stock-out hours** (needs inventory data) and treat them as missing, not as zero.
- Model demand with a method that accepts missing targets, or fill the gap with a model estimate.
- Use **availability** as a feature.
- Evaluate on days with stock, or report the share of stock-out days.

```check
{"q": "A product sells 0 units all day because it was out of stock. What should the training label be?", "type": "single",
 "options": ["0, it is the real value", "Missing or an estimate of demand", "The maximum of last week", "Remove the whole product"],
 "answer": 1,
 "why": ["Zero sales is not zero demand.", "Correct: do not teach the model that demand was zero.", "That invents data.", "You would lose a product that may be important."]}
```

## Retail and food delivery are different

| | Grocery retail | Food delivery |
|---|---|---|
| Entities | Store × SKU (millions of series) | Zone × hour (thousands of series), or restaurant |
| Horizon | 1 to 14 days | 15 minutes to 7 days |
| Decision | Order, stock, staff | Courier supply, incentives, kitchen prep |
| Main patterns | Weekly, yearly, promotions, holidays | Daily and weekly peaks (lunch, dinner), weather, events |
| Trap | Stock-outs, new items, markdowns | Supply limits shape orders; feedback loop with incentives |

The **feedback loop** in delivery: if you predict low demand, you send few couriers, delivery times grow, fewer people order, and your low forecast "comes true". Include supply and price as features, and be careful with what you call demand.

## Worked example

We simulate a product with a stock limit and show the bias of learning from sales.

```python
import numpy as np

rng = np.random.default_rng(5)
days = 200
demand = rng.poisson(50, days).astype(float)       # true daily demand
stock = rng.choice([45, 60], days)                  # shelf stock before opening
sales = np.minimum(demand, stock)                   # what the system records
stockout = demand > stock                           # we know it from inventory data

print("true mean demand       :", round(demand.mean(), 1))
print("mean of recorded sales :", round(sales.mean(), 1))
print("share of stock-out days:", round(stockout.mean(), 2))
print("mean sales, no-stock-out days only:", round(sales[~stockout].mean(), 1))
# Output:
# true mean demand       : 50.2
# mean of recorded sales : 47.0
# share of stock-out days: 0.44
# mean sales, no-stock-out days only: 47.4
```

Recorded sales are lower than the true demand. Using only no-stock-out days is also biased (it keeps only low-demand days). A better fix is a model that treats stock-out days as **censored** observations: the true demand is at least the sales.

## Common mistakes

- Training on sales as if they were demand.
- A single model for all products with no baseline.
- Forgetting promotions, price and holidays, which the business knows in advance.
- Evaluating with random splits instead of rolling-origin backtests.
- Measuring MAPE on slow items with many zeros.
- Not checking what happens for new stores and new items.

## Interview lens

**Typical question:** "Design a demand forecasting system for a grocery chain."

**Strong answer:** I start with the decision: daily store orders for the next 14 days with a 2-day lead time, where waste and stock-outs have different costs. I size the problem: stores × SKUs gives tens of millions of series, so I use a global gradient-boosting model with lag, calendar, price and promotion features, and a seasonal naive baseline. I treat stock-out days as censored. I evaluate with a rolling-origin backtest using WAPE, bias and pinball loss by segment. Batch scoring runs nightly, writes to a keyed table, and falls back to the baseline. I monitor bias, drift and cost, and handle new items with group-level models.

**Red flags:** Starting with LSTM. Ignoring stock-outs. No numbers. No baseline. No plan for new items.

## Real world

Public competitions show these ideas. The Rossmann Store Sales and Favorita Grocery Sales competitions on Kaggle used store-level retail data with promotions and holidays. The M5 competition (2020) used Walmart sales with prices and calendar events, and global LightGBM-style models did very well. See the case-study stage for details.

## Key points

- Use six parts: requirements, data, models, evaluation, serving, monitoring.
- Start from the decision and the cost of errors.
- Sales are censored demand. Handle stock-outs explicitly.
- Global models with strong calendar, price and promotion features are the usual choice, with a seasonal naive baseline.
- Plan for new items, fallbacks and feedback loops.
