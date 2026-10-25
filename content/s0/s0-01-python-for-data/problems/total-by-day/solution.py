def total_by_day(sales):
    """sales: list of (day, amount) pairs. Return {day: total amount}."""
    totals = {}
    for day, amount in sales:
        # .get gives 0 the first time we see a day
        totals[day] = totals.get(day, 0) + amount
    return totals
