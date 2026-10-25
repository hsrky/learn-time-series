---
slug: patchify-series
title: Patching for PatchTST
difficulty: Medium
type: function
tags: [transformer, patchtst, numpy]
skills: [from-scratch]
packages: []
---
PatchTST does not feed single time steps to the Transformer. It cuts each series into short
overlapping pieces called **patches**. Each patch becomes one token. Each channel (variable) is cut on its own
("channel independence").

Write `patchify(x, patch_len, stride, pad=True)`:

- `x` has shape `[channels, time]`. A 1D array means one channel.
- If `pad` is true, first repeat the **last value** of each channel `stride` times at the end (PatchTST does this so the end of the series is not lost).
- Then cut patches of length `patch_len`. The first patch starts at 0, the next one `stride` steps later. Keep only full patches.
- Return an array with shape `[channels, n_patches, patch_len]`.
- If the (padded) series is shorter than `patch_len`, return shape `[channels, 0, patch_len]`.

Number of patches: `(T_padded − patch_len) // stride + 1`.

### Example 1
**Input:** `patchify(np.arange(8.0), patch_len=4, stride=2, pad=False)`
**Output:** shape `(1, 3, 4)`: patches `[0,1,2,3]`, `[2,3,4,5]`, `[4,5,6,7]`
**Explanation:** `(8 − 4)//2 + 1 = 3`.

### Example 2
**Input:** `patchify(np.arange(8.0), 4, 2)` (with `pad=True`)
**Output:** shape `(1, 4, 4)`; the last patch is `[6, 7, 7, 7]`
**Explanation:** Two copies of the last value 7 are added, so T = 10 and `(10 − 4)//2 + 1 = 4`.

### Constraints
- `1 <= channels <= 64`, `0 <= time <= 10^5`, `1 <= stride`, `1 <= patch_len`
- If `time = 0` and `pad=True`, there is no last value: return shape `[channels, 0, patch_len]`.

### Hints
1. First handle the 1D case: `x[None, :]`.
2. `np.repeat(x[:, -1:], stride, axis=1)` makes the padding. Join with `np.concatenate`.
3. `sliding_window_view(x, patch_len, axis=1)[:, ::stride]` gives the patches directly.

### Solution explanation
Fewer tokens means cheaper attention: attention cost grows with the square of the number of tokens.
With 512 steps, patch length 16 and stride 8, you get 64 tokens instead of 512.
Time `O(channels · n_patches · patch_len)`. Common bugs: padding with zeros instead of the last value, and mixing channels together.
