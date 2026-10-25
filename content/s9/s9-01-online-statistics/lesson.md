---
id: s9-01-online-statistics
title: Online mean and variance (Welford)
minutes: 25
level: beginner
goals: [Update a mean without storing the data, Implement Welford's algorithm, Explain why the naive formula fails]
prereqs: []
tags: [streaming, welford, variance]
skills: [streaming-algorithms]
---
## Warm-up
```check
{"q": "What is the variance of the numbers 2, 4, 6 (divide by n)?", "type": "single", "options": ["2.67", "4", "8"], "answer": 0, "why": ["Correct: mean 4, squared deviations 4, 0, 4, sum 8, 8/3 = 2.67.", "4 is the sample variance (divide by n − 1).", "8 is the sum of squared deviations."]}
```
```check
{"q": "What does 'O(1) memory' mean?", "type": "single", "options": ["The memory does not grow with the input size", "It uses exactly 1 byte", "It takes 1 second"], "answer": 0, "why": ["Correct.", "It means constant, not one byte.", "That is about time."]}
```

## Why it matters
A sensor sends one value per second, forever. You cannot keep all the values to compute the average and the spread. You need to **update** the answer with each new value, using a fixed amount of memory. This is a **streaming** (online) algorithm. "Compute a running mean and variance" is a classic interview question, because the obvious solution can give wrong answers.

## Running mean
Values arrive: 4, 8, 6. After each value, the mean is:

| n | new x | mean |
|---|---|---|
| 1 | 4 | 4 |
| 2 | 8 | 6 |
| 3 | 6 | 6 |

Instead of summing everything again, update the old mean:

`mean(n) = mean(n−1) + (x(n) − mean(n−1)) / n`

- `mean(n−1)` = the mean before the new value
- `x(n)` = the new value
- `n` = the number of values so far, including the new one

Check: mean(2) = 4 + (8 − 4) / 2 = 6. ✓

```check
{"q": "The mean of 3 values is 10. A new value 18 arrives. What is the new mean of 4 values?", "type": "numeric", "answer": 12, "tol": 0.01, "why": "mean = 10 + (18 − 10) / 4 = 12."}
```

## Running variance: Welford's algorithm
The naive way keeps `sum(x)` and `sum(x²)` and uses `var = E[x²] − (E[x])²`. When the values are large and close to each other, this **subtracts two huge, almost equal numbers**. Float rounding then destroys the answer (it can even become negative).

**Welford's algorithm** (1962) is stable. Keep three numbers: `n`, `mean` and `M2` (the sum of squared deviations from the current mean). For each new `x`:

1. `n = n + 1`
2. `delta = x − mean`
3. `mean = mean + delta / n`
4. `M2 = M2 + delta · (x − mean)`   (use the **new** mean here)

Then: population variance = `M2 / n`, sample variance = `M2 / (n − 1)`.

```chart
{"title": "Running mean and spread of a noisy stream", "x": "t", "height": 220, "series": [{"name": "stream", "gen": [["const", {"value": 20}], ["noise", {"sd": 3}]], "n": 100, "seed": 9}, {"name": "true mean", "gen": [["const", {"value": 20}]], "n": 100, "dash": true}], "caption": "With more values, the running mean settles near 20. Welford gives the exact mean and variance at every step, in O(1) memory."}
```

```check
{"q": "Why is `E[x²] − (E[x])²` dangerous in floating point?", "type": "single", "options": ["It subtracts two large, almost equal numbers and loses precision", "It is too slow", "It needs the future"], "answer": 0, "why": ["Correct: this is called catastrophic cancellation.", "Speed is fine.", "It only needs past data."]}
```

## Windows and merging (extra)
- **Sliding window of size k:** you can also *remove* the oldest value with a reverse update. Or keep a deque of values and recompute (O(k) per step).
- **Merging two groups** (Chan et al.): if you have `(n_a, mean_a, M2_a)` and `(n_b, mean_b, M2_b)`, then `n = n_a + n_b`, `delta = mean_b − mean_a`, `mean = mean_a + delta · n_b / n`, `M2 = M2_a + M2_b + delta² · n_a · n_b / n`. This is used to combine results from many machines.
- **Exponential** forgetting: weight new values more. This is the EWMA (a later lesson).

## Worked example
Naive formula against Welford, with large values.

```python
import numpy as np

xs = [1e9 + 4, 1e9 + 7, 1e9 + 13, 1e9 + 16]     # large values, small spread

# naive: keep sum and sum of squares
n = len(xs)
s = sum(xs)
s2 = sum(x * x for x in xs)
naive = (s2 - s * s / n) / n

# Welford: keep n, mean, M2
cnt, mean, M2 = 0, 0.0, 0.0
for x in xs:
    cnt += 1
    delta = x - mean
    mean += delta / cnt
    M2 += delta * (x - mean)
welford = M2 / cnt

print("true variance  :", float(np.var([4, 7, 13, 16])))
print("naive          :", naive)
print("welford        :", welford)

# Output:
# true variance  : 22.5
# naive          : 0.0
# welford        : 22.5
```

## Common mistakes
- Using the sum-of-squares formula with large values.
- Using the **old** mean in the `M2` update (you must use `delta` from the old mean times the deviation from the new mean).
- Dividing by `n` when the task wants the sample variance (`n − 1`), or dividing by 0 when `n = 1`.
- Returning `NaN` or crashing before the first value arrives.
- Storing all values "just in case" and breaking the O(1) memory rule.

## Interview lens
**Typical question:** "Design a class that returns the mean and variance of a stream, one value at a time."

**Strong answer:** I keep three numbers: the count, the mean, and M2, the sum of squared deviations. Each update uses Welford's algorithm: compute delta from the old mean, move the mean by delta/n, and add delta times the deviation from the new mean to M2. It is O(1) time and O(1) memory per value, and numerically stable. I avoid the sum-of-squares formula because of cancellation. For sample variance I divide M2 by n − 1 and return 0 or NaN for n < 2, which I state clearly. To combine workers I can merge counts, means and M2 values.

**Red flags:** storing the whole list; the E[x²] − E[x]² formula; no word about n = 1.

## Real world
- Welford's method was published in 1962 in the journal Technometrics. Numerical libraries use it, or variants, for running statistics.
- Streaming systems that combine partial results from many machines use the merge formula (Chan, Golub, LeVeque, 1979).

## Key points
- Streaming algorithms keep O(1) memory and update with each value.
- Running mean: `mean += (x − mean) / n`.
- Welford: track n, mean, M2; `M2 += delta · (x − new mean)`; variance = M2 / n or M2 / (n − 1).
- Avoid `E[x²] − E[x]²` with large values (cancellation).
- Partial results can be merged exactly.
