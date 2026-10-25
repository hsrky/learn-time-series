QUERY = """
SELECT store, day, amount, amount AS running_total
FROM orders
ORDER BY store, day, amount
"""
