---
slug: time-bucket-counts
title: Count Events per Time Bucket
difficulty: Easy
type: function
tags: [buckets, python, counting]
skills: [streaming-algorithms]
packages: []
companies_style: []
---
You get a list of integer timestamps `timestamps` (seconds, in any order) and a bucket size `size` (seconds). A timestamp `t` belongs to the bucket that starts at `(t // size) * size`.

Return a list of `(bucket_start, count)` tuples, sorted by `bucket_start`. The list must include **every bucket from the first to the last occupied bucket**; buckets without events have count 0. If `timestamps` is empty, return an empty list.

### Example 1
**Input:** `timestamps = [5, 61, 62, 200]`, `size = 60`
**Output:** `[(0, 1), (60, 2), (120, 0), (180, 1)]`
**Explanation:** Buckets 0, 60, 120, 180. Bucket 0 has one event, bucket 60 has two, bucket 120 has none, bucket 180 has one.

### Constraints
- 0 <= len(timestamps) <= 10^5
- 1 <= size <= 10^6
- 0 <= t <= 10^9, but the number of buckets between first and last is at most 10^6

### Hints
1. Use `collections.Counter` on `(t // size) * size`.
2. Find the smallest and the largest bucket start.
3. Loop with `range(lo, hi + size, size)` and use `counter.get(b, 0)`.

### Solution explanation
**Approach.** Count events per bucket with a dictionary, then walk through all bucket starts from the first to the last and fill zeros.

**Why it works.** Integer division maps every timestamp to exactly one bucket start; the walk covers the gaps.

**Complexity.** O(n + B) time and O(B) space, where B is the number of buckets between the first and the last event.

**Common bugs.** Missing the empty buckets; using float division; off-by-one in the final `range`.
