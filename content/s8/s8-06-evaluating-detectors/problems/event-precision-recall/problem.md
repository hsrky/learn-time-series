---
slug: event-precision-recall
title: Event-Level Precision and Recall
difficulty: Medium
type: function
tags: [anomaly, evaluation, intervals]
skills: [anomaly-detection, metrics]
packages: []
companies_style: []
---
Events are closed intervals `(start, end)` with `start <= end`. Both `true_events` and `pred_events` are lists of such tuples. Inside one list the events do not overlap each other. They may be unsorted.

Two intervals **overlap** if they share at least one position: `a_start <= b_end and b_start <= a_end`.

- **precision** = (number of predicted events that overlap at least one true event) / (number of predicted events)
- **recall** = (number of true events that overlap at least one predicted event) / (number of true events)
- **f1** = 2 * precision * recall / (precision + recall)

If a denominator is 0, that value is 0.0. If precision + recall is 0, f1 is 0.0.

Return a dict `{"precision": ..., "recall": ..., "f1": ...}` with floats.

### Example 1
**Input:** `true_events = [(10, 20), (40, 50), (70, 75)]`, `pred_events = [(18, 22), (45, 46), (60, 62), (90, 91)]`
**Output:** `{'precision': 0.5, 'recall': 0.6666666666666666, 'f1': 0.5714285714285715}`
**Explanation:** Two true events are found (recall 2/3). Two of four alarms touch a true event (precision 1/2).

### Constraints
- 0 <= len(true_events), len(pred_events) <= 10^5
- 0 <= start <= end <= 10^9

### Hints
1. Sort both lists by start. Then move two pointers.
2. Two intervals do not overlap if one ends before the other starts. Move the pointer of the interval that ends first.
3. Count each event once, even if it overlaps many events of the other list.

### Solution explanation
**Approach.** Sort both lists. Use two pointers `i`, `j`. If the intervals overlap, mark both as matched. Then advance the pointer whose interval ends first (it cannot overlap anything later in the other list). This marks every event that overlaps at least one event of the other list.

**Why it works.** Events inside a list do not overlap and are sorted, so an interval that ends first can only touch intervals we have already seen or the current one.

**Complexity.** Sorting costs O(n log n + m log m). The sweep is O(n + m). Space O(n + m) for the flags. A simple double loop is O(n · m), which is too slow for 10^5 events.

**Common bugs.** Counting a predicted event once per true event it touches; treating touching ends (end == start) as no overlap; dividing by zero when a list is empty.
