---
id: s14-07-reliability-and-postmortems
title: Reliability - fallbacks, SLAs and post-mortems
minutes: 35
level: staff
goals: [Write service level objectives for a forecast product, Design a fallback ladder and guard-rails for decisions, Run a blameless post-mortem for a bad forecast, Tell the Zillow Offers case using public facts and draw general lessons]
prereqs: [s14-04-evaluation-governance]
tags: [staff, reliability, SLA, fallback, post-mortem, Zillow]
skills: [staff, production]
---

## Warm-up

```check
{"q": "Why does a promotion need a live check (shadow mode or small roll-out) as well as a backtest?", "type": "single",
 "options": ["To save time", "The offline result can differ from live results because of leakage, timing, or feedback loops", "Backtests are always wrong", "It is a legal rule"],
 "answer": 1,
 "why": ["It takes more time.", "Correct: the offline-online gap is real.", "Backtests are useful but not enough.", "Not a legal rule."]}
```

```check
{"q": "Why is seasonal naive a good fallback when the main model fails?", "type": "single", "options": ["It is simple and always available", "It is always the most accurate", "It needs a GPU", "It uses future data"], "answer": 0, "why": ["Correct: it needs only past values.", "It is often beaten by better models.", "It needs almost no compute.", "That would be leakage."]}
```

## Why it matters

A forecast that is right 95% of the time and catastrophic the other 5% can still ruin a business. At small scale, a bad forecast is an annoying report. At large scale, a forecast drives money: orders, hiring, prices, loans. A staff engineer thinks about **how the system fails**, not only how well it works on average. This lesson covers three tools: service level objectives, fallbacks with guard-rails, and post-mortems.

## Service level objectives for a forecast product

A **service level objective (SLO)** is a target that you measure and report. An **SLA** (agreement) is an SLO that you promise to someone, often with consequences. For a forecast product, set SLOs in four groups:

| Group | Example SLO |
|---|---|
| Availability | Forecasts for all stores are ready by 06:00 on 99% of days |
| Freshness | Inputs are no older than 24 hours when the forecast runs |
| Quality | 7-day WAPE is better than seasonal naive on 95% of days; bias within ±3% |
| Calibration | The 90% interval covers 88% to 92% of actuals over 4 weeks |

Notice the quality SLO is **relative to a baseline**. This is robust to events that make everything harder.

```check
{"q": "Which is a good quality SLO for a forecast?", "type": "single",
 "options": ["WAPE is always below 5%", "7-day WAPE is better than seasonal naive on 95% of days, with bias inside plus or minus 3%", "The model has many layers", "The job runs fast"],
 "answer": 1,
 "why": ["A fixed number can be impossible in hard periods.", "Correct: relative to a baseline, with bias as a guard.", "Complexity is not quality.", "Speed is an availability or cost topic."]}
```

## The fallback ladder

When something fails, the system should degrade in steps, not break. A typical **fallback ladder**:

1. **Primary model forecast** (all checks pass).
2. **Last good forecast** (data was late; reuse yesterday's, shifted).
3. **Seasonal naive** (model output failed a sanity check).
4. **Safe default rule** (for example the same as last week, or a manual number).
5. **Stop and alert a human** (when even the simple rules cannot be trusted).

Each step needs a **trigger** (stale data, forecast outside a plausible range, job failure) and an **alert**. Test the ladder in a drill, like a fire drill.

```chart
{"title": "A level shift the model does not see: forecast stays flat while demand jumps", "x": "day", "height": 230,
 "series": [
   {"name": "actual demand", "gen": [["const", {"value": 100}], ["step", {"at": 50, "size": 60}], ["noise", {"sd": 4}]], "n": 80, "seed": 5},
   {"name": "model forecast (not updated)", "gen": [["const", {"value": 101}]], "n": 80, "dash": true}
 ],
 "marks": [{"x": 50, "label": "regime change"}],
 "caption": "After day 50 the error is large and one-sided. A monitor on bias would fire within days; a monthly review would not."}
```

```check
{"q": "Input data is late today. Which fallback is the most reasonable?", "type": "single",
 "options": ["Predict zeros", "Reuse the last good forecast or seasonal naive, and send an alert", "Stop the whole system silently", "Make up numbers"],
 "answer": 1,
 "why": ["Zeros would cause large errors.", "Correct: degrade gracefully and tell people.", "Silent failure hides the problem.", "Invented numbers are worse than a simple baseline."]}
```

## Guard-rails on decisions

Fallbacks protect the forecast. **Guard-rails** protect the decision that uses it.

- **Change caps:** an order or price cannot change by more than X% from last week without review.
- **Exposure limits:** a cap on total money at risk. This matters when forecast error is large and the system acts at scale.
- **Uncertainty gates:** when the interval is very wide, act less or ask a human.
- **Kill switch:** a single switch to return to the old process.
- **Staged roll-out:** start with a small share of volume and increase only if live metrics stay inside bounds.

```check
{"q": "A pricing system uses a forecast to buy inventory automatically. Which guard-rail limits the damage if the forecast is badly wrong?", "type": "single",
 "options": ["A larger neural network", "An exposure limit on total money at risk and a kill switch", "More features", "A prettier dashboard"],
 "answer": 1,
 "why": ["A bigger model does not remove tail risk.", "Correct: limits cap the loss, and the switch stops it quickly.", "Features do not cap risk.", "Visibility helps but does not stop the loss."]}
```

## Blameless post-mortems

After a bad forecast with real cost, write a **post-mortem**. The aim is to learn, not to blame. A good one has:

1. **Summary and impact** (what happened, in numbers and dates).
2. **Timeline** (when it began, when we noticed, when we fixed it).
3. **Root causes** (several: technical and process, asked with "why" five times).
4. **What went well** (alerts that worked).
5. **Actions** with owner and date, and a check that they are done.
6. **Detection gap:** how could we have seen it earlier?

Typical root causes for forecasts are leakage, data delay, regime change, and a feedback loop. Others are an untested change in the feature code and a wrong assumption about the business.

```check
{"q": "Which sentence belongs in a blameless post-mortem?", "type": "single",
 "options": ["Anna forgot to check the data", "The data feed changed without a contract check, and our monitor had no freshness alert", "The vendor is incompetent", "Nobody is responsible"],
 "answer": 1,
 "why": ["It blames a person.", "Correct: describes system gaps and leads to actions.", "It blames without analysis.", "Responsibility lies in action owners, not in blame."]}
```

## Case: Zillow Offers (public facts only)

Zillow, a US real-estate company, ran a business called **Zillow Offers**. It used algorithms, including its home-value estimates, to make cash offers to buy homes. It planned to renovate and resell them. This is called "iBuying".

What was reported publicly:

- In **November 2021** Zillow announced that it would **wind down** Zillow Offers.
- The company reported a **large inventory write-down**, measured in hundreds of millions of dollars. It owned homes that it expected to sell for less than it paid.
- It announced a **reduction of about a quarter of its workforce**.
- In its statements, the company said that forecasting home prices had been less predictable than it had expected.

## What we can learn from the case

We do not know the internal model details, and outside reports differ on the causes. So here are **general lessons**, not a claim about the exact root cause:

- **Forecast errors are costly when the system acts at scale.** Buying thousands of homes turns a small bias into a big loss.
- **Decisions create exposure.** Inventory on the balance sheet is risk. Exposure limits and staged growth matter.
- **Regime changes** (fast-changing markets) can break models trained on calmer periods.
- **Feedback loops:** being a large buyer can influence prices and selection of homes (adverse selection).
- **Uncertainty must change behaviour.** A wide interval should reduce how much the business bets.

```check
{"q": "What is the most important general lesson for a staff engineer from the Zillow Offers case?", "type": "single",
 "options": ["Never forecast prices", "When forecasts drive large, hard-to-reverse bets, limit exposure and let uncertainty change the decision", "Always use a neural network", "Models never fail"],
 "answer": 1,
 "why": ["Forecasting is useful; the issue is how decisions use it.", "Correct: guard-rails and uncertainty-aware decisions limit tail loss.", "Model type is not the lesson.", "Models do fail."]}
```

## Worked example

A fallback ladder as a small function. It checks freshness and a plausible range, then returns the forecast source and a reason.

```python
import numpy as np

def choose_forecast(primary, last_good, seasonal_naive, data_age_hours, history):
    lo, hi = 0.5 * np.min(history), 1.5 * np.max(history)     # a simple plausible range
    if data_age_hours > 24:
        return last_good, "last_good", "stale data"
    if not np.all(np.isfinite(primary)) or np.any(primary < lo) or np.any(primary > hi):
        return seasonal_naive, "seasonal_naive", "primary outside plausible range"
    return primary, "primary", "all checks passed"

history = np.array([95, 100, 105, 98, 102, 110, 90])
last_good = np.array([100, 101, 99])
snaive = np.array([98, 102, 110])

for name, primary, age in [("normal", np.array([101, 103, 108]), 3),
                           ("stale", np.array([101, 103, 108]), 30),
                           ("broken", np.array([101, 900, 108]), 3)]:
    f, src, why = choose_forecast(primary, last_good, snaive, age, history)
    print(f"{name:7s} -> {src:15s} ({why})")
# Output:
# normal  -> primary         (all checks passed)
# stale   -> last_good       (stale data)
# broken  -> seasonal_naive  (primary outside plausible range)
```

In production you also log every fallback and alert on repeated use. A system that quietly uses the fallback for weeks is a failure that looks like success.

## Common mistakes

- No SLOs, so nobody knows what "good" means.
- A single failure mode: the system works or it is down.
- No guard-rails on automated decisions.
- Post-mortems that blame people, or that end without owned actions.
- Alerting on accuracy only, and not on bias, freshness, and calibration.
- Never testing the fallback path.

## Interview lens

**Typical question:** "Your forecasts drive automatic purchasing. What could go wrong, and how do you protect the business?"

**Strong answer:** "The forecast can fail in three ways. These are data problems, model error such as a regime change, and feedback effects. I would set SLOs for freshness, accuracy against seasonal naive, bias and calibration, and monitor them daily. I would add a fallback ladder: last good forecast, then seasonal naive, then a human. On the decision side I would add change caps, an exposure limit, uncertainty gates, and a kill switch. I would roll out by stages. After any incident I would run a blameless post-mortem with owned actions. The Zillow Offers wind-down is a public reminder that forecast errors at scale can be very costly."

**Red flags:** only average accuracy; no fallback; no exposure limits; blaming individuals.

## Real world

- Site reliability engineering (SRE) practices, such as SLOs, error budgets and blameless post-mortems, come from Google's public SRE books. They apply well to ML systems.
- Zillow's 2021 decision to close Zillow Offers is widely covered in public news and in the company's own shareholder communications. Read the primary sources if you want details.

## Staff lens

Reliability is a product feature that nobody sees until it fails. Make it visible: publish a monthly reliability report with SLO results, incidents, and actions closed. Ask for the budget to build fallbacks and monitors **before** the first incident. After an incident, ask for the change that makes this class of failure impossible, not only this one.

## Key points

- Define SLOs for availability, freshness, quality (relative to a baseline) and calibration.
- Use a fallback ladder and test it; log and alert every fallback.
- Guard-rails on decisions: change caps, exposure limits, uncertainty gates, kill switch, staged roll-out.
- Run blameless post-mortems with owned actions and a detection-gap analysis.
- Zillow Offers shows how forecast error at scale can become a business risk; draw general lessons, not invented details.
