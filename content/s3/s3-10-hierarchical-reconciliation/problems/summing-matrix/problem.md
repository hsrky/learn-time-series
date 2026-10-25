---
slug: summing-matrix
title: Summing Matrix and Bottom-Up Forecast
difficulty: Medium
type: function
tags: [hierarchical, summing-matrix, bottom-up, numpy]
skills: [from-scratch, scale]
packages: []
companies_style: [retail demand, multi-store forecasting]
---
A hierarchy is given as a dict `children` that maps each parent to the list of its children, plus the name of the `root`. Nodes that are not parents are the **bottom-level** series (leaves).

Write `summing_matrix(children, root)`. It returns a dict:

- `"rows"`: all node names in **breadth-first order** (root first, then its children in the given order, then the grandchildren, and so on, level by level, left to right).
- `"leaves"`: the leaf names in **depth-first, left-to-right order**.
- `"S"`: the summing matrix as a list of lists of 0 and 1 with `len(rows)` rows and `len(leaves)` columns. `S[i][j] = 1` if leaf `j` is the node `rows[i]` itself, or one of its descendants.

Also write `bottom_up(S, bottom_forecast)`. It returns the forecasts of all rows as a numpy array: `S @ bottom_forecast`.

### Example 1
**Input:** `summing_matrix({"Total": ["A", "B"]}, "Total")`
**Output:** `rows = ["Total", "A", "B"]`, `leaves = ["A", "B"]`, `S = [[1, 1], [1, 0], [0, 1]]`.

### Example 2
**Input:** `bottom_up([[1, 1], [1, 0], [0, 1]], [30, 20])`
**Output:** `array([50., 30., 20.])`

### Constraints
- The hierarchy is a tree: every non-root node has exactly one parent. At most 200 nodes.
- A node that appears in no key of `children` (or has an empty list) is a leaf.
- `bottom_forecast` has one entry per leaf, in the order of `"leaves"`.

### Hints
1. Do a depth-first search from the root to get the leaves in order, and to find the leaves below each node.
2. Do a breadth-first search (a queue) to get the row order.
3. For each node, the set of leaves below it gives one row: put `1` in the columns of those leaves.

### Solution explanation
A node's row in S is the indicator of the bottom series below it. A recursive helper returns the leaves of a node. We build the row for every node. Then `bottom_up` is a matrix-vector product, which gives all aggregates at once. Time O(N * L) for N nodes and L leaves. Common bugs: mixing up the row and column order, and forgetting that a leaf's own row has a single `1`.
