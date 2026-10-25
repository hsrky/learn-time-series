QUERY = """
SELECT user_id, MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM logins
GROUP BY user_id
ORDER BY user_id, start_day
"""
