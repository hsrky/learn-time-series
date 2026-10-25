---
id: s7-07-when-not-to-use
title: When NOT to use foundation models
minutes: 25
level: staff
goals: [List the situations where a foundation model is the wrong tool, Do a simple cost and latency comparison, Write a decision rule that includes baselines and governance]
prereqs: [s7-05-benchmarking-honestly, s7-06-llms-and-forecasting-agents]
tags: [decision, cost, latency, explainability, baselines, 2026-trend]
skills: [scale, baseline-first, staff, communication]
---
## Warm-up

```check
{"q": "What should every model comparison table include?", "type": "single",
 "options": ["Seasonal naive and a tuned simple model", "Only the newest model", "Only deep models"], "answer": 0,
 "why": ["Correct.", "Then you cannot see the value added.", "Then you cannot see if simple is enough."]}
```

```check
{"q": "A router picks the winner of 8 models per series on a 7-day window. What is the main risk?", "type": "single",
 "options": ["Selection noise: the winner was lucky", "Too much memory", "No risk"], "answer": 0,
 "why": ["Correct.", "Memory is a smaller concern.", "Selection noise is a real risk."]}
```

## Why it matters

**2026 trend:** the pressure to use a foundation model "because everyone does" is strong. A senior engineer must know when to say no, and say it with numbers. Saying no is also a design skill: it protects the team from cost and risk that bring no value.

A strong interview answer is often this: "I would try a foundation model as one candidate. First I would check these conditions."

## Four performance and cost reasons to say no

- **1. A strong simple baseline already works.** On stable seasonal series, seasonal naive or ETS may come within a few percent of any model. Extra cost buys nothing. In the M5 competition, gradient boosting with good features (LightGBM) was the winning style on retail data with many covariates.
- **2. You have rich covariates and domain features.** Promotions, prices, stock, weather, events. A boosted-tree model with a carefully built feature set can use them directly and is cheap to run.
- **3. Low latency or edge devices.** A forecast needed in milliseconds, or on a small device, rules out large models. A classical model or a tiny model (such as a small TTM-type model) may fit.
- **4. Huge scale with a tight budget.** Millions of series each hour: a neural network call per series costs real money. Compute the cost per 1,000 forecasts first.

## Three policy and structure reasons to say no

- **5. Explainability and regulation.** Some domains need documented, reviewable models (finance, insurance, public reporting). Model risk rules, for example the US banking guidance known as SR 11-7, ask for documentation, validation and clear limits. A model you cannot inspect or version (an API) is hard to approve.
- **6. Data cannot leave your network** (privacy, contracts). Hosted API models are ruled out; self-hosting needs engineering effort.
- **7. Special structure or needs.** Examples are hierarchies that must add up, intermittent demand and custom business losses. Specialized models or a reconciliation step may fit better.

```chart
{"title": "Illustration: where each approach tends to fit (relative, not measured)", "x": "approach", "height": 200,
 "series": [
   {"name": "cost per forecast (relative)", "kind": "bar", "y": [1, 3, 30]},
   {"name": "setup effort (relative)", "kind": "bar", "y": [2, 8, 5]}
 ],
 "caption": "Illustrative only. Left to right: seasonal naive / ETS, boosted trees, foundation model. Measure your own numbers."}
```

```check
{"q": "A forecast is needed in 5 ms on a small device for 50 products. Which option is the best first choice?", "type": "single",
 "options": ["A classical or very small model with a baseline check", "A large foundation model through an API", "An LLM agent"], "answer": 0,
 "why": ["Correct: latency and device limits rule out the large options.", "Network delay alone can exceed 5 ms.", "Far too slow."]}
```

## Quick cost check

Always do this math before you decide. Steps:

1. Number of forecasts per day: `series × runs per day`.
2. Time per forecast for each option (measure it on your hardware).
3. Price per hour of that hardware.
4. `cost per day = forecasts × seconds per forecast / 3600 × price per hour`.
5. Compare with the **value** of the accuracy gain (for example fewer stock-outs).

If the accuracy gain is worth less than the extra cost, do not switch.

```check
{"q": "1,000,000 forecasts per day, 0.02 seconds each on a machine that costs 2 per hour. Cost per day?", "type": "numeric", "answer": 11.11, "tol": 0.05,
 "why": "1,000,000 · 0.02 s = 20,000 s = 5.56 hours. Times 2 = 11.11."}
```

## When they ARE a good fit

To keep balance, these are the cases where a foundation model is a strong candidate:

- **Many short series** or **cold start** (new products with little history).
- **Fast prototype** for a new domain, as a baseline.
- **Long tail of low-value series** where tuning each series is not worth it.
- **As a member of an ensemble** with classical and tree models.
- Teams with **little forecasting expertise** that need a robust default.

## A decision rule you can write down

Make the decision a short document, not a feeling:

1. Define the decision the forecast supports and the cost of error.
2. Build the baseline ladder: seasonal naive, a tuned classical model, a boosted-tree model.
3. Add foundation model candidates (zero-shot first) and run the same time-based backtest.
4. Compare accuracy **and** cost, latency, explainability, data policy, license.
5. Adopt a model only if the gain is worth the cost, then pin versions, set monitoring and a fallback.
6. Re-run the comparison every quarter: models change.

## Worked example

We compare three options by daily cost, check a latency limit, and apply a simple decision function. The times and prices are **assumed teaching numbers**. Replace them with measurements from your own system.

```python
# assumed numbers for a teaching exercise (NOT measurements)
options = {
    #  name                 seconds per forecast, price per hour of the machine, relative accuracy (MASE vs naive, lower is better)
    "seasonal naive / ETS": (0.001, 0.5, 1.00),
    "LightGBM global":      (0.002, 0.5, 0.90),
    "foundation model":     (0.050, 2.0, 0.88),
}
n_series = 1_000_000                    # forecasts per day
latency_limit_s = 0.010                 # the service must answer in 10 ms
explain_required = True

print(f"{'option':22s} {'cost/day':>9s} {'latency ok':>11s} {'MASE':>5s}")
for name, (sec, price, mase) in options.items():
    cost = n_series * sec / 3600 * price
    ok = sec <= latency_limit_s
    print(f"{name:22s} {cost:9.2f} {str(ok):>11s} {mase:5.2f}")

def decide(sec, price, mase, base_mase, extra_gain_value_per_day, explain_ok):
    cost = n_series * sec / 3600 * price
    base_cost = n_series * options["seasonal naive / ETS"][0] / 3600 * options["seasonal naive / ETS"][1]
    gain = (base_mase - mase) * extra_gain_value_per_day       # value of the accuracy lift
    return explain_ok and sec <= latency_limit_s and gain >= (cost - base_cost)

# suppose a MASE gain of 0.01 is worth 5 per day, so 1.0 is worth 500
value_per_mase = 500.0
for name, (sec, price, mase) in options.items():
    verdict = decide(sec, price, mase, 1.00, value_per_mase, explain_ok=(name != "foundation model"))
    print(name, "->", "adopt" if verdict else "do not adopt")

# Output:
# option                  cost/day  latency ok  MASE
# seasonal naive / ETS        0.14        True  1.00
# LightGBM global             0.28        True  0.90
# foundation model           27.78       False  0.88
# seasonal naive / ETS -> adopt
# LightGBM global -> adopt
# foundation model -> do not adopt
```

With these assumptions the foundation model is too slow for the 10 ms limit and costs more. LightGBM adds a clear gain for almost no extra cost. If the limit were 100 ms and the accuracy gain larger, the answer could change. The decision depends on numbers, so measure them.

## Common mistakes

- Choosing a model by fashion, not by decision and cost.
- Comparing only accuracy, not cost, latency, explainability and license.
- Forgetting the cost of running and monitoring the new service.
- Dropping the baseline ladder after the first success.
- Using an API without checking data policy.

## Interview lens

**Typical question:** "Your CTO wants to replace all forecasting models with a foundation model. What do you say?"

**Strong answer:** I would run a controlled comparison first. I would define the decision the forecast supports. Then I would build the baseline ladder: seasonal naive, a tuned classical model and a boosted-tree model with our covariates. I would add two or three foundation models zero-shot on the same time-based backtest. I would use MASE and a quantile metric. I would also add cost per 1,000 forecasts, latency, explainability needs, data policy and license. I expect the foundation model to be strong for the long tail and cold start. I do not expect it to win on high-value series with rich covariates. So I would propose a hybrid with segment-wise rules, version pinning, monitoring and a seasonal naive fallback. I would review the choice every quarter.

**Red flags:** "newer is better"; no cost or latency numbers; no baseline; ignoring regulation and data policy.

## Real world

- The M5 competition (Walmart sales data) was won by LightGBM-based solutions with careful features, not by deep models. This shows that tabular methods with good covariates can beat large models.
- Public benchmarks such as GIFT-Eval and fev-bench list foundation models next to classical and tree baselines. You can see where simple methods remain competitive. Check the current leaderboard and its date.
- Regulated industries use model risk management processes that ask for documentation and validation, which affects what models can be approved.

## Staff lens

- **Build vs buy vs foundation model.** Frame it as a portfolio. Use cheap models for the bulk and heavier models where value per series is high. Use an API or open model for cold start. Write down exit costs.
- **Evaluation governance.** Fix a golden backtest, a champion/challenger process, and a review calendar. Every model in production has an owner, a version, a baseline it must beat, and a retirement rule.
- **Offline vs online gap.** Verify that the offline gain shows in the business metric after launch with a staged rollout. Keep the fallback for incidents. Remember Zillow Offers (2021): forecast risk at scale needs guardrails, not only accuracy.

## Key points

- Say no when a simple baseline is enough or when covariates matter more. Also say no when latency, cost, explainability or data policy block it.
- Do the cost math: forecasts × seconds × price, then compare with the value of the accuracy gain.
- Foundation models fit best for the long tail, cold start, quick prototypes and ensembles.
- Make the decision a written process with baselines, pinned versions, monitoring, a fallback and a regular review.
