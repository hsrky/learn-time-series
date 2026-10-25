QUERY = """
WITH RECURSIVE cal(day) AS (
    SELECT MIN(day) FROM daily
    UNION ALL
    SELECT date(day, '+1 day') FROM cal
    WHERE day < (SELECT MAX(day) FROM daily)
)
SELECT cal.day AS day, COALESCE(d.revenue, 0) AS revenue
FROM cal
LEFT JOIN daily d ON d.day = cal.day
ORDER BY cal.day
"""
