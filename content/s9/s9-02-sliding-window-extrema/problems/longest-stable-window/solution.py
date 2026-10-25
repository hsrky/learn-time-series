from collections import deque


def longest_stable(readings, limit):
    maxq, minq = deque(), deque()                  # indices; maxq decreasing, minq increasing
    left = 0
    best = 0
    for right, v in enumerate(readings):
        while maxq and readings[maxq[-1]] <= v:
            maxq.pop()
        maxq.append(right)
        while minq and readings[minq[-1]] >= v:
            minq.pop()
        minq.append(right)
        while readings[maxq[0]] - readings[minq[0]] > limit:
            left += 1                              # shrink the window
            if maxq[0] < left:
                maxq.popleft()
            if minq[0] < left:
                minq.popleft()
        best = max(best, right - left + 1)
    return best
