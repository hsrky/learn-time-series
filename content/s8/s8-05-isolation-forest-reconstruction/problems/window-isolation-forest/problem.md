---
slug: window-isolation-forest
title: Anomalous Windows with Isolation Forest
difficulty: Medium
type: function
tags: [anomaly, isolation-forest, scikit-learn]
skills: [anomaly-detection, feature-engineering]
packages: [scikit-learn]
companies_style: []
---
Find the most unusual windows of a series.

1. Build all windows of length `w`: window `i` is `values[i:i+w]` for `i = 0 .. n-w`.
2. For each window compute three features, in this order: the **mean**, the **standard deviation** (population, `np.std`) and the **range** (`max - min`).
3. Fit `IsolationForest(n_estimators=100, random_state=0)` on these features.
4. Return the **start positions** of the `k` windows with the most abnormal score (the lowest `score_samples`), as a sorted list of ints.

Use exactly these settings so that your answer matches the reference.

### Example 1
**Input:** `values` = a sine wave of 120 points with a flat piece, `w = 10`, `k = 3`
**Output:** `[70, 71, 72]`
**Explanation:** The flat piece creates windows with a very small standard deviation and range; they are isolated first.

### Constraints
- w <= len(values)
- 1 <= k <= number of windows
- Use scikit-learn (listed in packages)

### Hints
1. Stack the windows into a 2-D array with a list comprehension, then use `.mean(axis=1)`, `.std(axis=1)`.
2. `np.c_[a, b, c]` joins three columns into a feature table.
3. `np.argsort(iso.score_samples(F))[:k]` gives the k lowest scores (most abnormal).

### Solution explanation
**Approach.** Windows become a feature table with 3 columns. The forest is fitted on the table and each window gets a score. Lower `score_samples` = more abnormal, so we sort ascending and take the first k.

**Why it works.** A flat or spiky window has features that are far from most windows, so random splits isolate it after few steps.

**Complexity.** Building the features is O(n · w). Fitting t trees on a sample of size ψ (256 by default) costs about O(t · ψ log ψ); scoring costs O(n · t · log ψ). Space is O(n · w) for the windows (O(n) if you compute features in one pass).

**Common bugs.** Taking the highest scores instead of the lowest; forgetting `random_state`; returning the end index of the window instead of its start; not sorting the result.
