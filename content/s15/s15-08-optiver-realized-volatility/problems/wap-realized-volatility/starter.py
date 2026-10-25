import numpy as np
import pandas as pd


def wap(bid_price1, ask_price1, bid_size1, ask_size1):
    """Weighted average price of the best bid and ask."""
    raise NotImplementedError


def realized_volatility(book):
    """DataFrame time_id, rv: sqrt of the sum of squared WAP log returns inside each time_id."""
    raise NotImplementedError
