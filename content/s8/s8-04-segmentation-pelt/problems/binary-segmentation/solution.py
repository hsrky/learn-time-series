import numpy as np


def binary_segmentation(values, min_size, penalty):
    x = np.asarray(values, dtype=float)
    n = len(x)
    s1 = np.concatenate([[0.0], np.cumsum(x)])         # prefix sums of x
    s2 = np.concatenate([[0.0], np.cumsum(x * x)])     # prefix sums of x squared

    def cost(a, b):
        m = b - a
        return (s2[b] - s2[a]) - (s1[b] - s1[a]) ** 2 / m

    cuts = []

    def split(a, b):
        if b - a < 2 * min_size:
            return
        whole = cost(a, b)
        best_gain, best_c = -1.0, None
        for c in range(a + min_size, b - min_size + 1):
            g = whole - cost(a, c) - cost(c, b)
            if g > best_gain:                           # strict: first (smallest) c wins ties
                best_gain, best_c = g, c
        if best_c is not None and best_gain > penalty:
            cuts.append(best_c)
            split(a, best_c)
            split(best_c, b)

    split(0, n)
    return sorted(cuts)
