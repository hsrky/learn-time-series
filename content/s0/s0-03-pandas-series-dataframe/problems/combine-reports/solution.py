import pandas as pd


def combine_reports(a, b):
    """Total per date over the union of both indexes; a missing day counts as 0."""
    # add() aligns on the index labels; fill_value=0 replaces a missing partner.
    total = a.fillna(0).add(b.fillna(0), fill_value=0)
    return total.sort_index()
