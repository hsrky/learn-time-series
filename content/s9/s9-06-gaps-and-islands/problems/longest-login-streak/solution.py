import datetime as dt


def longest_streak(days):
    nums = sorted({dt.date.fromisoformat(d).toordinal() for d in days})
    if not nums:
        return (0, None, None)
    best_len, best_start = 1, nums[0]
    cur_len, cur_start = 1, nums[0]
    for prev, now in zip(nums, nums[1:]):
        if now == prev + 1:
            cur_len += 1
        else:
            cur_len, cur_start = 1, now
        if cur_len > best_len:                     # strict: the earlier run wins ties
            best_len, best_start = cur_len, cur_start
    f = lambda n: dt.date.fromordinal(n).isoformat()
    return (best_len, f(best_start), f(best_start + best_len - 1))
