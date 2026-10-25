def llm_encode(values, decimals=2):
    """Write the series as digit-separated text, e.g. '0 1 2 3 , 4 5 6 0'."""
    ints = [int(round(v * 10 ** decimals)) for v in values]
    if not ints:
        return ""
    width = max(1, max(len(str(abs(n))) for n in ints))   # same width for all numbers
    parts = []
    for n in ints:
        digits = " ".join(str(abs(n)).zfill(width))       # '0123' -> '0 1 2 3'
        parts.append(("- " + digits) if n < 0 else digits)
    return " , ".join(parts)


def llm_decode(text, decimals=2):
    """Inverse of llm_encode: return a list of floats."""
    if not text.strip():
        return []
    out = []
    for part in text.split(" , "):
        part = part.strip()
        neg = part.startswith("-")
        digits = part.replace("-", "").replace(" ", "")
        out.append((-1 if neg else 1) * int(digits) / 10 ** decimals)
    return out
