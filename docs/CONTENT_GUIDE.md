# Content authoring guide (exact formats)

Read `docs/DESIGN.md` §1 first (learning design + plain-English rules). This file is the contract
between content authors and the app/build. `tools/build.py` enforces it.

## Folder layout

```
content/
  stages.json                       # [{ "id":"s1", "title":"Foundations", "summary":"…", "color":"#2f6fed", "icon":"wave" }, …]
  glossary.json                     # { "stationary": {"simple":"A series whose average and spread do not change over time.", "example":"Daily temperature changes (differences) are often stationary."}, … }
  s1/                               # one folder per stage id
    s1-03-resampling/               # lesson id = folder name: <stage>-<NN>-<slug>
      lesson.md
      quiz.json
      cards.json
      problems/
        resample-daily-sum/         # problem slug, globally unique
          problem.md
          starter.py
          solution.py
          tests.py
```

Stage ids: `s0` … `s14` (see DESIGN §2). Lesson numbers `NN` give the order inside a stage.

Glossary: **do not edit `content/glossary.json` directly** when working in parallel. Put new terms in
`content/<stage>/glossary.<stage>.json` (same format). The build merges all of them; a term defined
twice must have the same meaning (first one wins, build warns).

## lesson.md

Front matter between `---` lines. Values: plain strings, or `[a, b, c]` lists (comma separated,
no quotes needed unless the item has a comma — then use `"…"`).

```
---
id: s1-03-resampling
title: Resampling and the time index
minutes: 20
level: beginner            # beginner | intermediate | advanced | staff
goals: [Change the frequency of a series, Pick the right aggregation for each column, Avoid timezone traps]
prereqs: [s1-02-components]
tags: [pandas, resample]
skills: [pandas-fluency]   # from DESIGN §2.1 without the "skill:" prefix
---
```

Body = Markdown (python-markdown with `tables`, `fenced_code` extensions) with these sections **in
this order** (headings exactly `## …`): `Warm-up` (optional for the very first lesson of S0),
`Why it matters`, one or more concept chunks (any titles), `Worked example`, `Common mistakes`,
`Interview lens`, `Real world`, `Key points`. Advanced/staff lessons may add `Staff lens` before
`Key points`.

Special fenced blocks (JSON inside):

````
```check
{"q": "Hourly data, you need daily totals. Which call?", "type": "single",
 "options": ["s.resample('D').mean()", "s.resample('D').sum()", "s.rolling(24).sum()"],
 "answer": 1,
 "why": ["Mean gives the average hour, not the total.", "Correct: sum adds all 24 hours of each day.", "Rolling keeps hourly rows; it does not change the frequency."]}
```
````

`check` / quiz question types:
- `single`: `options`, `answer` (index), `why` (list, one reason per option — **required**).
- `multi`: `options`, `answer` (list of indexes), `why` (list per option).
- `numeric`: `answer` (number), `tol` (absolute), `why` (string, shows the calculation).
- `order`: `options` (shown shuffled), answer is the given order, `why` (string).

````
```chart
{"title": "Trend + weekly season + noise", "x": "day", "height": 220,
 "series": [
   {"name": "sales", "gen": [["trend", {"slope": 0.5, "start": 10}], ["season", {"period": 7, "amp": 5}], ["noise", {"sd": 1.5}]], "n": 84, "seed": 3},
   {"name": "trend only", "gen": [["trend", {"slope": 0.5, "start": 10}]], "n": 84, "dash": true}
 ],
 "marks": [{"x": 60, "label": "forecast starts"}],
 "caption": "The orange line goes up (trend) and repeats every 7 days (season)."}
```
````

Series: either `"y": [numbers]` (optional `"x": [...]`) or `"gen"`: list of `[generator, params]`
that are **added** together. Generators (implemented in `site/js/charts.js`):
`trend{start,slope}`, `season{period,amp,phase}`, `noise{sd}`, `randomWalk{sd,start}`,
`ar1{phi,sd}`, `step{at,size}`, `spike{at,size}`, `exp{start,rate}`, `const{value}`.
Optional `"kind": "bar"|"line"|"dots"`, `"dash": true`.

````
```widget
{"name": "ses-alpha", "params": {"alpha": 0.3}}
```
````

Widget names (implemented in `site/js/widgets.js`): `components`, `moving-average`, `ses-alpha`,
`holt-winters`, `differencing`, `acf`, `train-test-split`, `walk-forward`, `lag-features`,
`quantile-loss`, `anomaly-zscore`, `chronos-tokens`, `sliding-window`, `conformal`.

Inline: `[[term]]` or `[[term|shown text]]` → glossary tooltip. `[[lesson:s2-01-white-noise]]` →
link to a lesson. `[[problem:resample-daily-sum]]` → link to a problem.

Worked example code blocks use ```` ```python ```` and show printed output as a comment block
(`# Output:` lines). All worked-example code **must be correct** for pandas 2.2 / numpy 2.0
(use freq aliases `"D"`, `"h"`, `"min"`, `"W"`, `"MS"`, `"ME"`, `"QE"`, `"YE"`; not `"H"`, `"T"`, `"M"`).

Real-world notes: only well-documented, public facts (competition results, published papers,
company engineering blogs). No invented numbers. If unsure, describe the idea without a figure.

## quiz.json (mastery quiz)

```json
{"pass": 0.8, "questions": [ { …same objects as ```check… }, … ] }
```
5–8 questions. Mix types. At least 2 must be "apply" questions (a small scenario), not just recall.

## cards.json (flashcards for spaced repetition)

```json
[{"front": "What does stationary mean?", "back": "Mean, variance and autocorrelation do not change over time."}, …]
```
4–8 cards. Front ≤ 15 words. Back ≤ 35 words.

## problems/<slug>/problem.md

```
---
slug: resample-daily-sum
title: Daily Totals from Hourly Data
difficulty: Easy            # Easy | Medium | Hard
type: function              # function | class | sql | forecast
tags: [pandas, resample]
skills: [pandas-fluency]
packages: []                # extra Pyodide packages: statsmodels, scikit-learn, scipy (numpy/pandas always on)
companies_style: []         # optional free text like [retail demand, ride-hailing] — never claim a real company asked it
---
Statement in plain English (same rules). Then:

### Example 1
**Input:** `s = …`
**Output:** `…`
**Explanation:** …

### Constraints
- …

### Hints
1. (gentle nudge)
2. (which function / idea)
3. (almost the answer)

### Solution explanation
Approach in steps, why it works, time/space complexity, common bugs.
```

## starter.py / solution.py

- `starter.py`: imports + the exact signature + docstring + `pass`/`raise NotImplementedError` body.
  It **must fail** at least one case (build checks).
- `solution.py`: clean, commented reference solution with the same names. It **must pass** all cases.
- Allowed imports: stdlib, `numpy`, `pandas`, and what `packages` lists. No file/network access.

## tests.py

Real Python, executed fresh for every case with `np`, `pd`, `math`, `sql` already in scope.

```python
import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=48, freq="h")
S1 = pd.Series(np.arange(48, dtype=float), index=idx)

CASES = [
    {"name": "two full days", "call": "daily_total(S1)", "visible": True},
    {"name": "explicit", "call": "daily_total(S1.iloc[:24])", "expected": "pd.Series([276.0], index=pd.DatetimeIndex(['2024-01-01'], freq='D'))", "visible": True},
    {"name": "with NaN", "call": "daily_total(S1.where(S1 % 5 != 0))"},
    # 'tol' (default 1e-6), 'check_index' (default True) are optional per case
]

# optional custom grader: return (ok: bool, message: str)
# def check(got, expected, case): ...
```

- 2–3 `visible` cases (shown in the Test cases tab), 4–10 total. Include edge cases
  (empty, NaN, single element, ties, unsorted index, gaps) and one larger random case (seeded).
- If `expected` is missing, the reference solution's output is the expected value.
- **class** problems: `call` is a small script; the last line is the value compared, e.g.
  `"call": "m = MovingAverage(3)\n[m.next(x) for x in [1, 10, 3, 5]]"`.
- **sql** problems: starter defines `QUERY = """…"""`; call like `"sql(QUERY, sales=SALES)"` where
  `SALES` is a DataFrame built in tests.py. Compare with `check_index: False`; sort with `ORDER BY`.
- **forecast** problems: define `check` that scores the forecast (e.g. MAE vs seasonal naive) and
  passes when it is better than a threshold; message shows the score.

Validate a problem (or a whole folder) while writing:

```
$VENV/bin/python tools/check_problem.py content/s1/s1-03-resampling
```

`$VENV` = `/tmp/claude-0/-home-user-learn-time-series/19bf3dde-e717-5f0a-90bd-65fb895cab5c/scratchpad/venv`
(Python 3.13 with numpy 2.0.2, pandas 2.2.3, scipy 1.14.1, statsmodels 0.14.4, scikit-learn 1.6.1,
markdown — the same library versions as the in-browser engine).

## drill.json (optional, design drills — S10, S13, S14)

A lesson folder may contain `drill.json`. The app shows it as a timed design drill under the lesson.

```json
{"title": "Design a demand forecasting system for 2,000 stores", "minutes": 45, "level": "senior",
 "prompt": "Markdown: the interviewer's prompt, constraints, numbers.",
 "sections": [
   {"id": "req", "label": "Requirements & decision", "hint": "Who uses the forecast? Horizon? Granularity?"},
   {"id": "data", "label": "Data & features", "hint": "…"},
   {"id": "model", "label": "Models & baselines", "hint": "…"},
   {"id": "eval", "label": "Evaluation & backtest", "hint": "…"},
   {"id": "serve", "label": "Serving & scale", "hint": "…"},
   {"id": "monitor", "label": "Monitoring & failure modes", "hint": "…"}
 ],
 "model_answer": {"req": "Markdown …", "data": "…", "model": "…", "eval": "…", "serve": "…", "monitor": "…"},
 "rubric": [{"item": "Starts from the business decision and its cost of error", "weight": 2}, …],
 "follow_ups": ["What if a new store opens tomorrow?", "…"]}
```

## Mock OA sets (S13 only)

`content/s13/mock_sets.json`:
`[{"id": "oa-1", "title": "Mock OA 1 — Data wrangling", "minutes": 75, "problems": ["slug-a", "slug-b", "slug-c"]}, …]`
Problems can come from any stage. The app also offers a random mock built from Easy+Medium+Hard.

## Notebook code (S12, S15)

Code that cannot run in the browser (library not vendored, real Kaggle data) goes in fenced
blocks with the language `notebook`:

````
```notebook
# Run this in a Kaggle notebook (Data: Store Sales – Time Series Forecasting)
import pandas as pd
train = pd.read_csv("/kaggle/input/store-sales-time-series-forecasting/train.csv", parse_dates=["date"])
```
````

The app shows it with a "Run on Kaggle / your laptop" label and a copy button (no Run button).
Keep it correct for current library APIs; do not invent function names — when unsure, use plain
pandas/numpy/scikit-learn.
