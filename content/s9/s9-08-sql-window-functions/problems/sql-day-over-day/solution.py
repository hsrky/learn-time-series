QUERY = """
SELECT day,
       revenue,
       LAG(revenue)  OVER (ORDER BY day) AS prev_revenue,
       LEAD(revenue) OVER (ORDER BY day) AS next_revenue,
       revenue - LAG(revenue) OVER (ORDER BY day) AS change
FROM daily
ORDER BY day
"""
