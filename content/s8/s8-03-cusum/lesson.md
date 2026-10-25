---
id: s8-03-cusum
title: Change points with CUSUM
minutes: 25
level: intermediate
goals: [Explain what a change point is, Implement two-sided CUSUM, Choose k and h]
prereqs: [s8-01-point-anomalies]
tags: [change-point, cusum]
skills: [anomaly-detection]
---
## Warm-up
```check
{"q": "A point anomaly is...", "type": "single", "options": ["One strange value", "A new normal level that lasts", "A missing value"], "answer": 0, "why": ["Correct: one point (or a few) that does not fit.", "That is a change point (a level shift).", "Missing values are a data problem, not an anomaly type."]}
```
```check
{"q": "Why is a rolling z-score poor at finding a level shift that lasts?", "type": "single", "options": ["The window slowly learns the new level, so the score drops", "It needs the future", "It cannot read numbers"], "answer": 0, "why": ["Correct: after a few steps the window is full of new-level values and nothing looks strange.", "It uses only the past.", "It reads numbers fine."]}
```

## Why it matters
A web service has a [[median]] response time of 120 ms. On Tuesday at 14:05 a new release makes it 150 ms. Every single request is still "normal" (some old requests were also 150 ms). But the **average level moved**. You want an alarm soon after the move, and not a thousand false alarms before it. This is a **[[change point]]** problem.

## CUSUM: add up small drifts
[[CUSUM]] (cumulative sum) collects evidence. Each point that is above the target adds a little to a counter. A point below the target takes a little away, but the counter never goes below 0. When the counter passes a limit, you raise an alarm.

Example. Target mean = 10. Slack k = 0.5. Limit h = 3. Values: 10, 11, 12, 12.

| step | value | value − 10 − 0.5 | counter S+ |
|---|---|---|---|
| 1 | 10 | −0.5 | max(0, 0 − 0.5) = 0 |
| 2 | 11 | 0.5 | 0.5 |
| 3 | 12 | 1.5 | 2.0 |
| 4 | 12 | 1.5 | 3.5 → alarm |

The formulas (one for up-shifts, one for down-shifts):

`S+(t) = max(0, S+(t−1) + x(t) − μ − k)`

`S−(t) = max(0, S−(t−1) + μ − x(t) − k)`

- `μ` = target (in-control) mean
- `k` = **slack**: the drift you accept as normal. A good choice is half of the shift you want to find.
- `h` = decision limit. Alarm when `S+ > h` or `S− > h`. Often `h` is 4 to 5 standard deviations.
- After an alarm, set both counters to 0 and continue.

```chart
{"title": "Level shift at t = 60 and the CUSUM counter", "x": "t", "height": 230, "series": [{"name": "signal", "gen": [["const", {"value": 10}], ["noise", {"sd": 1}], ["step", {"at": 60, "size": 2}]], "n": 100, "seed": 5}, {"name": "target", "gen": [["const", {"value": 10}]], "n": 100, "dash": true}], "marks": [{"x": 60, "label": "level shift"}], "caption": "The shift is only two standard deviations. A single point rarely looks strange, but CUSUM adds the small excesses."}
```

```check
{"q": "Target 10, k = 0.5. The counter S+ is 1.0. The next value is 13. What is the new S+?", "type": "numeric", "answer": 3.5, "tol": 0.01, "why": "S+ = max(0, 1.0 + 13 − 10 − 0.5) = 3.5."}
```

## The trade-off: speed against false alarms
- **Small h** → fast alarms, but more false alarms.
- **Large h** → few false alarms, but slower detection (the **[[detection delay]]**).
- **Small k** → sensitive to small shifts. **Large k** → only big shifts.

In quality control this trade-off is measured with the average run length (ARL): the average number of points before a [[false alarm]], and before a true alarm.

```check
{"q": "You want to detect small shifts quickly, and you accept more false alarms. What do you change?", "type": "single", "options": ["Make k and h smaller", "Make k and h larger", "Use only S−"], "answer": 0, "why": ["Correct: smaller slack and limit react sooner.", "This makes the detector slower and less sensitive.", "S− only finds down-shifts."]}
```

## Worked example
We simulate a mean shift from 10 to 12 at t = 60 ([[standard deviation]] 1) and run two-sided CUSUM.

```python
import numpy as np

rng = np.random.default_rng(5)
x = np.concatenate([rng.normal(10, 1, 60), rng.normal(12, 1, 40)])

mu, k, h = 10.0, 1.0, 5.0          # target, slack (half of the shift 2), limit
s_up = s_dn = 0.0
alarms = []
for t, v in enumerate(x):
    s_up = max(0.0, s_up + v - mu - k)     # evidence for a rise
    s_dn = max(0.0, s_dn + mu - v - k)     # evidence for a drop
    if s_up > h or s_dn > h:
        alarms.append((t, "up" if s_up > h else "down"))
        s_up = s_dn = 0.0                  # reset after an alarm
print("alarms before the shift:", [a for a in alarms if a[0] < 60])
print("first alarm after the shift:", [a for a in alarms if a[0] >= 60][0], "(delay of 2 points)")

# Output:
# alarms before the shift: []
# first alarm after the shift: (62, 'up') (delay of 2 points)
```

## Common mistakes
- Using a wrong target `μ`. CUSUM then drifts without any change. Estimate `μ` and σ from a clean period.
- Forgetting the reset after an alarm, so the counter stays above the limit.
- Not scaling: `k` and `h` are in the units of the data. Normalise by σ first.
- Using CUSUM for data with strong seasonality without removing it.
- Using CUSUM on past data to find the exact change time: CUSUM tells you "something changed", the exact time is earlier than the alarm.

## Interview lens
**Typical question:** "How do you detect that the mean of a metric shifted after a release?"

**Strong answer:** I use a one-sided or two-sided CUSUM on the standardised metric. The slack k is about half the smallest shift I care about, and the limit h sets the false-alarm rate. CUSUM adds small deviations, so it finds small shifts faster than a [[z-score]] on single points. I check the detection delay and the false-alarm rate on past data. If the series has a season, I remove it first. For offline analysis of past data I would compare with a binary-segmentation method.

**Red flags:** using point thresholds for shifts; no mention of k and h; not resetting after an alarm.

## Real world
- CUSUM was introduced by E. S. Page in 1954 for industrial quality control.
- Statistical process control uses CUSUM next to Shewhart charts and EWMA charts to watch production lines.

## Key points
- A **change point** is a lasting change in the level (or other property), not a single strange value.
- CUSUM keeps a counter of positive (and negative) drift, never below 0, and alarms above a limit h.
- Slack k is about half the shift you want to find. A smaller h means faster alarms and more false alarms.
- Reset the counter after an alarm.
