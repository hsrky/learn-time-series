def llm_encode(values, decimals=2):
    """Write the series as digit-separated text, e.g. '0 1 2 3 , 4 5 6 0'."""
    raise NotImplementedError


def llm_decode(text, decimals=2):
    """Inverse of llm_encode: return a list of floats."""
    raise NotImplementedError
