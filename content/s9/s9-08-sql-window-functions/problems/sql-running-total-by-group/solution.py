QUERY = """
SELECT store, day, amount,
       SUM(amount) OVER (PARTITION BY store ORDER BY day, amount
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders
ORDER BY store, day, amount
"""
