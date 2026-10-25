QUERY = """
WITH d AS (
    SELECT DISTINCT user_id, day FROM logins
), r AS (
    SELECT user_id, day,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS rn
    FROM d
)
SELECT user_id, MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM r
GROUP BY user_id, date(day, '-' || rn || ' day')
ORDER BY user_id, start_day
"""
