---
id: s8-06-evaluating-detectors
title: Evaluating anomaly detectors
minutes: 25
level: intermediate
goals: [Compute event-level precision and recall, Explain the point-adjust trap, Describe how NAB scores timing]
prereqs: [s8-01-point-anomalies]
tags: [anomaly, evaluation, nab]
skills: [anomaly-detection, evaluation]
---
## Warm-up
```check
{"q": "Precision answers which question?", "type": "single", "options": ["Of the alarms I raised, how many were real?", "Of the real problems, how many did I find?", "How many points are in the data?"], "answer": 0, "why": ["Correct: precision = true alarms / all alarms.", "That is recall.", "That is not a metric."]}
```
```check
{"q": "You raise 10 alarms and 4 are real. What is the precision?", "type": "single", "options": ["0.4", "0.6", "4"], "answer": 0, "why": ["Correct: 4 / 10.", "0.6 is the share of false alarms.", "4 is a count."]}
```

## Why it matters
A team reports "F1 = 0.95" for a new [[anomaly]] detector. A month later, the on-call engineer says it is useless. Often the reason is the **evaluation**, not the model. Anomaly data is rare (maybe 1% of points), anomalies last for a while, and a late alarm may be worth nothing. A good evaluation must reflect how people use the alerts.

## Points or events?
An **[[event]]** is one anomalous period, for example 14:00 to 14:20. A detector may mark 5 minutes of it, or only 1 minute. For the on-call engineer, one alarm inside the event is enough to find it. So we score at the **event level**:

- **[[recall|Recall]]** = detected true events / all true events. An event is detected when any alarm overlaps it.
- **[[precision|Precision]]** = alarms that overlap a true event / all alarms. (Here "alarm" means one predicted event.)
- **F1** = 2 · precision · recall / (precision + recall)

Example: 4 true events. The detector raises 5 alarms. 3 true events have an overlapping alarm. 3 of the 5 alarms overlap a true event. Recall = 3/4 = 0.75. Precision = 3/5 = 0.6.

```check
{"q": "3 true events, 6 alarms. 2 events are found and 4 alarms touch a true event. What is the event recall? (give a decimal)", "type": "numeric", "answer": 0.667, "tol": 0.01, "why": "Recall = found events / true events = 2 / 3 = 0.667. (Precision would be 4 / 6.)"}
```

## The point-adjust trap
Some papers use **[[point adjustment]]**: if the detector flags **any** point inside a true event, the **whole** event is marked as detected before computing point-wise precision and recall.

Example: a true event is 100 points long. The model flags 1 of them. After adjustment: 100 true positives. Recall = 100%.

This **inflates** scores. A very weak, almost random detector gets a high F1 when events are long, because with enough points it hits each event by luck. Kim et al. (2022) showed that point adjustment can make random scores look as good as published methods.

Safer practice:
- Report event-level precision/recall, or a delay-aware score.
- Always compare with trivial baselines: random scores, a simple [[z-score]].
- Say how far in time an alarm may be from the event (the tolerance).

```chart
{"title": "One event, one lucky point", "x": "t", "height": 200, "series": [{"name": "series", "gen": [["const", {"value": 0}], ["noise", {"sd": 0.3}], ["spike", {"at": 100, "size": 0}]], "n": 200, "seed": 1}, {"name": "true event (t 90 to 130)", "y": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kind": "bar"}], "caption": "A detector that flags only one point in the event gets full recall after point adjustment."}
```

```check
{"q": "A detector flags 1 point out of a 200-point event. After point adjustment, what is the recall for that event?", "type": "single", "options": ["1/200", "100%", "0%"], "answer": 1, "why": ["That is the real point-wise recall.", "Correct: point adjustment marks the whole event as found. This is why the score is inflated.", "The detector did hit the event."]}
```

## Time matters: the Numenta Anomaly Benchmark
The **Numenta Anomaly Benchmark ([[NAB]])**, by Lavin and Ahmad (2015), scores detectors on streaming data. Its main ideas:

- Each true anomaly has a **window** around it. The **earliest** detection inside the window gets the most reward. A later one gets less.
- A [[false alarm]] outside every window costs points.
- Three **application profiles** change the weights: standard, "reward low false positives", "reward low false negatives".

You do not need the exact formula in an interview. You need the idea: **early detection is worth more**, and false alarms cost.

## Worked example
We compare an honest point-wise score with a point-adjusted score for a **random** detector.

```python
import numpy as np

rng = np.random.default_rng(0)
n = 2000
truth = np.zeros(n, dtype=int)
for start in (200, 700, 1200, 1700):
    truth[start:start + 100] = 1                 # four events of 100 points each

pred = (rng.random(n) < 0.03).astype(int)        # random detector: flags 3% of the points

def prf(t, p):
    tp = int(((t == 1) & (p == 1)).sum())
    prec = tp / max(1, int(p.sum()))
    rec = tp / max(1, int(t.sum()))
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    return round(prec, 3), round(rec, 3), round(f1, 3)

adj = pred.copy()
for start in (200, 700, 1200, 1700):
    if pred[start:start + 100].any():
        adj[start:start + 100] = 1               # point adjustment: mark the whole event

print("random, point-wise    (P, R, F1):", prf(truth, pred))
print("random, point-adjusted (P, R, F1):", prf(truth, adj))

# Output:
# random, point-wise    (P, R, F1): (0.164, 0.03, 0.051)
# random, point-adjusted (P, R, F1): (0.868, 1.0, 0.929)
```

## Common mistakes
- Reporting accuracy on data with 1% anomalies (a model that says "normal" always has 99%).
- Using point adjustment and comparing the numbers with papers that do not.
- Ignoring [[detection delay]]: an alarm after the damage is done is not useful.
- Tuning the [[threshold]] on the test set.
- Counting each alarm window as a separate false alarm when one event triggers many.

## Interview lens
**Typical question:** "How do you evaluate an anomaly detector when labels are rare?"

**Strong answer:** I define what a good alert is for the user. Usually that is: one alarm per real event, soon after it starts, and few alarms with no event. So I merge the model output into events and compute event-level precision and recall, plus the detection delay. I avoid point-adjusted F1 because a lucky single hit scores the full event. I compare with simple baselines like a rolling z-score and with random scores. I set the threshold on a validation period and check the alert volume per week.

**Red flags:** quoting accuracy; using point adjustment without caveats; tuning on test labels; no baseline.

## Real world
- The Numenta Anomaly Benchmark (Lavin and Ahmad, 2015) is a public benchmark with a scoring rule that rewards early detection.
- Kim and colleagues (2022), in "Towards a Rigorous Evaluation of Time-series Anomaly Detection", argued that point-adjusted F1 gives misleading scores and that random baselines can look strong.

## Key points
- Anomalies are rare, so do not use accuracy.
- Score at the **event level**: found events (recall) and real alarms (precision).
- **Point adjustment** inflates scores. A lucky single hit marks the full event as found.
- Time matters: NAB rewards early detection and penalises false alarms.
- Always compare with a trivial baseline.
