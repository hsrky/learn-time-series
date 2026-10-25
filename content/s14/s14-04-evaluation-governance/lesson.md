---
id: s14-04-evaluation-governance
title: Evaluation governance - golden sets, champion and challenger
minutes: 35
level: staff
goals: [Set up a golden backtest set and protect it from tuning, Run a champion/challenger promotion with clear rules, Explain the offline to online gap and how to shrink it, Spot and stop metric gaming]
prereqs: [s14-02-forecasting-platform]
tags: [staff, governance, evaluation, champion-challenger, metrics]
skills: [staff, backtest, metrics]
---

## Warm-up

```check
{"q": "Why is it wrong to tune a model on the same test period you report?", "type": "single",
 "options": ["It is slower", "The reported error becomes optimistic because the test guided your choices", "It uses more memory", "It breaks the index"],
 "answer": 1,
 "why": ["Speed is not the issue.", "Correct: your choices were fitted to the test data.", "Memory is not the issue.", "The index is not affected."]}
```

```check
{"q": "What is leakage in a forecasting model?", "type": "single", "options": ["A feature that uses information you will not have at forecast time", "A slow model", "A missing value", "A very large model"], "answer": 0, "why": ["Correct: the offline score then looks better than real life.", "Speed is another issue.", "Missing values are a data issue.", "Size is not leakage."]}
```

## Why it matters

When many people can launch models, the question "is the new model better?" gets many answers. One team shows a 12% gain on its own split. Another shows a loss on a different period. Without rules, the loudest chart wins. **Evaluation governance** is the set of rules that makes the answer trustworthy: one frozen test, a clear promotion rule, and checks that the offline number matches real life.

## Golden backtest sets

A **golden set** is a frozen collection of series and forecast origins used to compare models. It has these properties:

- **Representative.** It covers high and low volume, new and old series, intermittent series, holidays and promotions.
- **Frozen and versioned.** Nobody edits it. A new version gets a new name.
- **Protected.** It is not used for tuning. Teams tune on a separate development set. Only the final candidate sees the golden set.
- **Refreshed on a schedule.** Add the latest months so the set does not go stale, but keep the old version for history.
- **With baselines.** Seasonal naive and the current champion are always scored on it.

```check
{"q": "Which is the correct use of a golden set?", "type": "single",
 "options": ["Tune hyper-parameters on it every day", "Score final candidates on it, tune on a separate development set", "Edit it when a model does badly", "Share the labels in a public file"],
 "answer": 1,
 "why": ["Tuning on it makes it useless as a test.", "Correct: the golden set stays clean.", "Editing it to help a model destroys trust.", "Public labels invite overfitting."]}
```

## Champion and challenger

The **champion** is the model in production. A **challenger** is a candidate to replace it. Use a written promotion rule. A good rule has four parts:

1. **Average gain.** The challenger beats the champion by at least a margin (for example 2% lower WAPE) on the golden set.
2. **Win rate.** It wins on a clear majority of series (for example at least 55%). This avoids a few large series driving the average.
3. **No big losers.** No important segment gets worse by more than a limit (for example 5%).
4. **Live check.** It runs in shadow or on a small share of traffic. The gap to the champion matches the offline result.

```widget
{"name": "walk-forward", "params": {}}
```

```check
{"q": "A challenger has a 4% better average WAPE, but wins on only 38% of series. What does that suggest?", "type": "single",
 "options": ["It is clearly better", "A few large or lucky series drive the gain; investigate before promoting", "The golden set is too small", "The champion is perfect"],
 "answer": 1,
 "why": ["The majority of series did not improve.", "Correct: look at where the gain comes from, and check for a segment risk.", "Not enough information to say that.", "A champion can still lose on average."]}
```

## The offline to online gap

Offline backtests often look better than live results. Common causes:

| Cause | Fix |
|---|---|
| Leakage in features | Point-in-time features; a leakage review |
| Data arrives later live than in the backtest | Backtest with the real data cut-off times |
| The decision changes the data (stock-outs, prices) | Test with a business simulation or an A/B test |
| Golden set not representative | Add new segments and periods |
| Metric not linked to business value | Track a business metric too |
| Selection effect: you picked the best of many tries | Use a fresh hold-out period for the final test |

Track the **gap** itself: for each promoted model, store the offline result and the live result. If the gap is large, improve the process, not only the model.

```check
{"q": "You tried 40 model variants and promoted the one with the best backtest score. Why can its live score be worse than its backtest score?", "type": "single",
 "options": ["Selection effect: the best of many tries is partly lucky", "Python rounding", "The golden set was too clean", "Seasonality disappeared"],
 "answer": 0,
 "why": ["Correct: choosing the maximum of many noisy scores gives an optimistic value.", "Rounding is tiny.", "A clean set is the goal.", "Not related."]}
```

## Metric gaming

When a number becomes a target, people (and models) learn to push the number up without helping the business. This is known as Goodhart's law. Examples in forecasting:

- **Optimising MAPE** makes the model forecast low (under-forecast), because MAPE punishes over-forecasts more.
- **Removing hard series** from the test set.
- **Choosing a favourable period** for the report.
- **Averaging over many easy series** so that hard ones disappear. Show weighted and unweighted views.
- **Reporting lag-1 accuracy** when the decision needs 14 days.

Defences: use two or three metrics, such as accuracy, bias and interval coverage. Report by segment. Fix the report definition in code. Review changes to the metric like code changes.

```check
{"q": "A team's reported MAPE falls from 20% to 15%, but total bias moves from +1% to -9% (more under-forecast). What is a likely explanation?", "type": "single",
 "options": ["Real improvement", "Metric gaming or a side effect: MAPE favours low forecasts, so the model learned to under-forecast", "A data error in bias", "Nothing; ignore bias"],
 "answer": 1,
 "why": ["Bias worsened a lot, so check before celebrating.", "Correct: MAPE rewards under-forecasts, and bias reveals it.", "No evidence for that.", "Bias carries cost in most businesses."]}
```

## Worked example

A promotion check for a challenger. We simulate series-level WAPE for a champion and a challenger in 200 series, split into 3 volume segments. Then we apply the four-part rule.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(1)
n = 200
seg = rng.choice(["high", "mid", "low"], n, p=[0.2, 0.4, 0.4])
champ = rng.uniform(0.08, 0.30, n)                          # champion WAPE per series
noise = rng.normal(0, 0.03, n)
change = np.where(seg == "low", 0.02, -0.04)                # challenger: better on high/mid, worse on low
chall = champ * (1 + change) + noise * champ

df = pd.DataFrame({"seg": seg, "champ": champ, "chall": chall})
df["lift"] = (df["champ"] - df["chall"]) / df["champ"]      # positive = challenger better

mean_lift = (df["champ"].mean() - df["chall"].mean()) / df["champ"].mean()
win_rate = (df["chall"] < df["champ"]).mean()
seg_lift = df.groupby("seg")["lift"].mean()
worst = seg_lift.min()

print(f"mean lift: {mean_lift:.1%}   win rate: {win_rate:.0%}")
print(seg_lift.round(3).to_string())
ok = mean_lift >= 0.02 and win_rate >= 0.55 and worst >= -0.05
print("promote:", ok)
# Output:
# mean lift: 1.6%   win rate: 63%
# seg
# high    0.031
# low    -0.021
# mid     0.042
# promote: False
```

The win rate (63%) looks good. But the mean lift is 1.6%, below the 2% margin, and the low-volume segment gets worse. So the rule says: do not promote yet. A next step could be to use the challenger only for high and mid volume series. The rule was written in advance, so no one argues after the result.

## Common mistakes

- Tuning on the golden set.
- Promotion by "it looks better on my chart".
- One metric only.
- No live check before full roll-out.
- Never refreshing the golden set.
- Comparing models on different folds or different data cuts.
- Changing the metric definition quietly.

## Interview lens

**Typical question:** "Your new model is better offline. How do you decide to ship it?"

**Strong answer:** "I check the offline win against a golden set that was not used for tuning, with several folds. I compare average lift, the share of series that improve, and the worst segment. I check bias and interval coverage, not only one accuracy metric. Then I run it in shadow mode, and later on a small share of traffic, and compare the live gap with the offline result. If they agree and the business metric moves, I promote it. I keep the old model as a fallback for rollback."

**Red flags:** only one metric; a random split; no live test; ignoring selection effects when many models were tried.

## Real world

- The M-competitions (M4 and M5) use a fixed test period that participants never see until the end, and a common set of metrics. This is the same idea as a golden set at company scale.
- Many industry teams describe champion/challenger set-ups, in which a new model runs next to the production model before it replaces it. The pattern comes from credit-risk and marketing analytics and is now common in ML platforms.

## Staff lens

Governance must be light or it will be avoided. Automate it: the backtest service runs the golden set, prints the four-part rule, and posts the result in the review. Humans review exceptions only. Measure the process too: time from idea to promotion, and the offline-online gap per release.

## Key points

- A golden set is frozen, versioned, representative and protected from tuning.
- Promotion needs a written rule: average gain, win rate, no big loser segment, and a live check.
- Track the offline-to-online gap; selection effects and leakage are common causes.
- Guard against metric gaming with several metrics, segments and reviewed definitions.
