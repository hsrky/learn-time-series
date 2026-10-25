---
id: s1-99-sample
title: Sample lesson for testing
minutes: 10
level: beginner
goals: [See a chart, Use a widget, Answer a check question]
prereqs: []
tags: [sample]
skills: [baseline-first]
---
## Warm-up
Quick recall.

```check
{"q": "Hourly data, you need daily totals. Which call?", "type": "single",
 "options": ["s.resample('D').mean()", "s.resample('D').sum()", "s.rolling(24).sum()"],
 "answer": 1,
 "why": ["Mean gives the average hour, not the total.", "Correct: sum adds all 24 hours of each day.", "Rolling keeps hourly rows."]}
```

## Why it matters
A [[trend]] and a [[season|seasonal pattern]] hide inside most data. See [[sample term]]. Next: [[problem:sample-daily-sum]] and [[lesson:s1-99-sample]].

## Parts of a series
Every series has **trend**, season and noise.

```chart
{"title": "Trend + weekly season + noise", "x": "day", "height": 220,
 "series": [
   {"name": "sales", "gen": [["trend", {"slope": 0.5, "start": 10}], ["season", {"period": 7, "amp": 5}], ["noise", {"sd": 1.5}]], "n": 84, "seed": 3},
   {"name": "trend only", "gen": [["trend", {"slope": 0.5, "start": 10}]], "n": 84, "dash": true}
 ],
 "marks": [{"x": 60, "label": "forecast starts"}],
 "caption": "The line goes up (trend) and repeats every 7 days (season)."}
```

| a | b |
|---|---|
| 1 | 2 |

## Smoothing
Try the slider.

```widget
{"name": "moving-average", "params": {"window": 5}}
```

```check
{"q": "Pick all true.", "type": "multi", "options": ["A", "B", "C"], "answer": [0, 2], "why": ["a", "b", "c"]}
```

## Worked example
```python
import pandas as pd
s = pd.Series([1, 2, 3])
print(s.sum())
# Output:
# 6
```

## Common mistakes
- Using the wrong alias.

## Interview lens
Say baseline first.

## Real world
Competitions use this.

## Key points
- One
- Two
