from collections import Counter


def bucket_counts(timestamps, size):
    if not timestamps:
        return []
    counts = Counter((t // size) * size for t in timestamps)
    lo, hi = min(counts), max(counts)
    return [(b, counts.get(b, 0)) for b in range(lo, hi + size, size)]
