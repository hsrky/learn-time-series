---
slug: mask-spikes
title: Mask the Spikes
difficulty: Easy
type: function
tags: [numpy, boolean-mask, nan]
skills: [pandas-fluency]
packages: []
companies_style: [IoT sensors]
---
A sensor sometimes sends a wrong huge value (a **spike**). Any reading above `limit` is a spike.

Write `mask_spikes(x, limit)`. It returns a tuple `(clean, n)`:

- `clean`: a new float array. Spikes are replaced by `np.nan`. Other values stay the same.
- `n`: the number of spikes, as an int.

Do not change the input array.

### Example 1
**Input:** `x = np.array([1.0, 99.0, 3.0])`, `limit = 10`
**Output:** `(array([ 1., nan,  3.]), 1)`
**Explanation:** Only 99.0 is above 10.

### Constraints
- `0 <= len(x) <= 10^6`
- `x` may already contain `nan`. A nan is not a spike and is not counted.
- A value equal to `limit` is **not** a spike.

### Hints
1. Make a boolean mask with `x > limit`.
2. Copy the array first: `clean = x.astype(float).copy()`. Then assign `clean[mask] = np.nan`.
3. Comparing nan with `>` gives False, so existing nan values are not counted.

### Solution explanation
1. `mask = x > limit` marks the spikes. Comparisons with nan are False.
2. Copy and assign nan where the mask is True.
3. `int(mask.sum())` counts the spikes.

Time O(n), space O(n). Bug to avoid: `x[mask] = np.nan` changes the input array and may fail for an integer array.
