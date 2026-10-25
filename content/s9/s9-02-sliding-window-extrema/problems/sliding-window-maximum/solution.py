from collections import deque


def sliding_window_max(nums, k):
    if k <= 0 or k > len(nums):
        return []
    dq = deque()                                   # indices, values decreasing
    out = []
    for i, v in enumerate(nums):
        if dq and dq[0] <= i - k:                  # front left the window
            dq.popleft()
        while dq and nums[dq[-1]] <= v:            # smaller older values are useless
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
