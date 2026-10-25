---
id: s14-03-build-buy-foundation
title: Build vs buy vs foundation-model API
minutes: 35
level: staff
goals: [Compare build, buy and foundation-model options on cost, latency, risk, lock-in and evaluation, Build a simple monthly cost model and find the break-even volume, Design a fair evaluation before you choose, Write a decision that you can defend in a review]
prereqs: [s14-02-forecasting-platform]
tags: [staff, build-vs-buy, foundation-model, cost]
skills: [staff, scale]
---

## Warm-up

```check
{"q": "What is the main benefit of a shared backtest service?", "type": "single",
 "options": ["Faster GPUs", "Comparable accuracy numbers across teams", "Lower storage cost", "A nicer dashboard"],
 "answer": 1,
 "why": ["Hardware is not the point.", "Correct: same folds and metrics give comparable numbers.", "Not the main benefit.", "Not the main benefit."]}
```

```check
{"q": "What makes a backtest honest?", "type": "single", "options": ["Training only on data before each test period", "Using all data for training", "Random folds", "Tuning on the test period"], "answer": 0, "why": ["Correct: the model must not see the future.", "This leaks the future.", "Random folds mix past and future.", "Tuning on the test period makes the score too good."]}
```

## Why it matters

A vendor shows a demo where a [[foundation model]] forecasts your data with no training. The demo looks great. Your CFO asks: "Why do we keep a team that builds models?" A staff engineer answers with numbers and risks, not taste. The question is never "which model is best". It is "which **option** gives the best business result for the cost and risk, now and in two years".

## Three options

| Option | What it is | Typical strength | Typical weakness |
|---|---|---|---|
| **Build** | Your own statistical or ML models (ETS, LightGBM) on your infrastructure | Low cost per forecast at scale, full control, domain features | People cost, slower to start |
| **Buy** | A vendor forecasting product or cloud service | Fast start, little maintenance | Cost per use, lock-in, less control |
| **Foundation model** | A pre-trained model (open weights you host, or a paid API) used zero-shot or lightly tuned | Strong first baseline, little history needed | Latency, GPU or API cost, hard to add custom features, unclear training data |

These are not exclusive. A common plan is: **buy or use a foundation model to start, build where volume and value are high**.

```check
{"q": "A team has few years of history for thousands of new products and needs a fast first baseline in one week. Which option is the most natural start?", "type": "single",
 "options": ["Build a custom deep network", "Test a foundation model zero-shot next to seasonal naive", "Wait one year", "Hire ten people"],
 "answer": 1,
 "why": ["Too slow for a one-week start.", "Correct: zero-shot gives a quick baseline, and the comparison with seasonal naive keeps it honest.", "Waiting delivers nothing.", "Not a quick start."]}
```

## The decision criteria

| Criterion | Questions to ask |
|---|---|
| Cost | Fixed monthly cost? Cost per 1,000 forecasts? What happens at 10x volume? |
| Latency | Batch overnight or answer in 200 ms? |
| Accuracy | Lift over seasonal naive and over your tuned GBM, on **your** data? |
| Risk | Data privacy, vendor outage, price change, model version change |
| Lock-in | Can you move away in 3 months? Do you own the data and the evaluation? |
| Fit | Can it use your known-future features (price, promotions)? Does it give quantiles? |
| People | Who runs it at 3 am? Do we have the skills? |

```chart
{"title": "Monthly cost vs volume (example prices, not real quotes). x = million forecasts per month", "x": "million forecasts / month", "height": 250,
 "series": [
   {"name": "API (no fixed cost, 1.00 per 1k)", "x": [0,5,10,15,20,25,30,35,40], "y": [0,5000,10000,15000,20000,25000,30000,35000,40000]},
   {"name": "Hosted foundation model (6,000 fixed, 0.30 per 1k)", "x": [0,5,10,15,20,25,30,35,40], "y": [6000,7500,9000,10500,12000,13500,15000,16500,18000]},
   {"name": "Build (20,000 fixed, 0.02 per 1k)", "x": [0,5,10,15,20,25,30,35,40], "y": [20000,20100,20200,20300,20400,20500,20600,20700,20800]}
 ],
 "caption": "The API is cheapest at low volume. Hosting the model wins in the middle. Build wins at very high volume, if the fixed cost is really that low."}
```

The chart uses invented prices to show the shape. In real work, use your own quotes.

```check
{"q": "Option A costs 8,000 fixed plus 0.5 per 1,000 forecasts. Option B costs 2,000 fixed plus 1.5 per 1,000. At what volume (forecasts per month) do they cost the same?", "type": "numeric",
 "answer": 6000000, "tol": 1,
 "why": "8,000 + 0.5·v/1000 = 2,000 + 1.5·v/1000. So 6,000 = 1.0·v/1000, which gives v = 6,000,000 forecasts per month."}
```

## Evaluate fairly before you choose

A demo is not an evaluation. Run this procedure.

1. **Golden set.** Choose a representative set of series and several forecast origins. Freeze it.
2. **Baselines.** Include seasonal naive and a tuned LightGBM or ETS. A foundation model that does not beat them is not worth its cost.
3. **Same inputs.** Give all options the same history. Test one version **with** known-future covariates if you have them.
4. **Metrics.** Use the metric tied to your cost of error, plus bias and interval coverage.
5. **Segments.** Check short history, intermittent, high-volume, and holiday periods.
6. **Contamination.** Ask if the public series in the model's training data overlap with your test period. For public benchmarks this can inflate scores.
7. **Stability.** Does the output change when the vendor updates the model? Pin versions.

```check
{"q": "A vendor shows 15% better accuracy than your current model on a public benchmark. What is the right next step?", "type": "single",
 "options": ["Sign the contract", "Test it on your golden set with your baselines, segments and cost metric", "Reject it", "Ask for a longer demo"],
 "answer": 1,
 "why": ["A public benchmark may not match your data.", "Correct: your data and your cost of error decide.", "It may be good; you have not tested it.", "A demo is still not an evaluation."]}
```

## Lock-in and exit

Ask on day one: **"How do we leave?"**

- Keep your data, features and the golden evaluation in your own storage.
- Put a thin **interface** (a small adapter) between your pipeline and the vendor, so you can swap it.
- Keep a baseline model running as a fallback and as a negotiating tool.
- Write down the exit cost in months and money.

## Worked example

The cost model from the problem, with three example options. We list the monthly cost at 10 million forecasts, apply a latency limit, and find a break-even point.

```python
options = [
    {"name": "build",  "fixed": 20000, "per_1k": 0.02, "latency_ms": 50},
    {"name": "api",    "fixed": 0,     "per_1k": 1.00, "latency_ms": 400},
    {"name": "fm-gpu", "fixed": 6000,  "per_1k": 0.30, "latency_ms": 200},
]

def cost(o, volume):
    return o["fixed"] + o["per_1k"] * volume / 1000

volume = 10_000_000
for o in sorted(options, key=lambda o: cost(o, volume)):
    print(f"{o['name']:7s} {cost(o, volume):>9,.0f} per month, latency {o['latency_ms']} ms")

ok = [o for o in options if o["latency_ms"] <= 250]   # a latency limit of 250 ms
best = min(ok, key=lambda o: cost(o, volume))
print("with latency <= 250 ms the best is:", best["name"])

a, b = options[0], options[2]                         # build vs fm-gpu
v = (b["fixed"] - a["fixed"]) * 1000 / (a["per_1k"] - b["per_1k"])
print(f"build beats fm-gpu above {v:,.0f} forecasts per month")
# Output:
# fm-gpu      9,000 per month, latency 200 ms
# api        10,000 per month, latency 400 ms
# build      20,200 per month, latency 50 ms
# with latency <= 250 ms the best is: fm-gpu
# build beats fm-gpu above 50,000,000 forecasts per month
```

The cheapest option can change with volume and with hard limits like latency. Your job is to show the curve, not one number.

## Common mistakes

- Choosing from a demo or a public leaderboard.
- Comparing only accuracy and ignoring cost, latency and risk.
- Forgetting people cost in the "build" option.
- Forgetting the cost of change: version updates, retraining, migrations.
- No exit plan, no fallback.
- Treating the foundation model as a replacement for features you already have (price, promotions).

## Interview lens

**Typical question:** "Should we replace our forecasting models with a foundation-model API?"

**Strong answer:** "I would not decide from a demo. First I ask about volume, latency and the cost of error. Then I run a fair test on our golden backtest. I compare seasonal naive, our current model, and the API. All use the same inputs and our business metric, and the test includes segments like new products. I build a cost model with the break-even volume and a latency limit. I check data privacy, version changes and exit cost. A likely outcome is a hybrid. I use the foundation model for cold start and long-tail series. I keep our tuned model where we have rich features and high volume. I keep the baseline as a fallback."

**Red flags:** yes or no without a test; ignoring cost curves; ignoring lock-in; only public benchmarks.

## Real world

- Several time-series foundation models are public, such as Amazon's Chronos, Google's TimesFM and Salesforce's Moirai. Their papers and model cards describe zero-shot results on public benchmarks. Public leaderboards for them change often, so check the date and the data of any ranking.
- Some vendors offer forecasting through an API, for example Nixtla's TimeGPT. Cloud providers also offer managed forecasting services. Prices and features change, so always use a current quote.

## Staff lens

The decision is a **portfolio**, not a single choice. Write a one-page decision record: options, test results, cost curves, risks, the choice, the review date and the exit plan. Review it when volume doubles, when the vendor changes price, or when a new model appears. This protects the team from both hype and inertia.

## Key points

- Compare build, buy and foundation model on cost, latency, accuracy, risk, lock-in, fit and people.
- Model cost as fixed plus variable; find break-even volumes; apply hard limits like latency first.
- Evaluate on your golden set against seasonal naive and your tuned model; check contamination and version stability.
- Plan the exit: own your data and evaluation, use an adapter, keep a fallback.
- A hybrid is often the best answer.
