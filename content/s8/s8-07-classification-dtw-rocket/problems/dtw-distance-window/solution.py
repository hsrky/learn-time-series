def dtw_distance(a, b, window=None):
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return float("inf")
    w = max(n, m) if window is None else max(window, abs(n - m))
    inf = float("inf")
    prev = [inf] * (m + 1)              # row i-1 of the table
    prev[0] = 0.0                       # D[0][0]
    for i in range(1, n + 1):
        cur = [inf] * (m + 1)
        for j in range(max(1, i - w), min(m, i + w) + 1):
            cost = abs(a[i - 1] - b[j - 1])
            cur[j] = cost + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return float(prev[m])
