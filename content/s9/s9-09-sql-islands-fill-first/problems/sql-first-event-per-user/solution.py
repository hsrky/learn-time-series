QUERY = """
SELECT user_id, event_id, event_type, event_time
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time, event_id) AS rn
    FROM events
)
WHERE rn = 1
ORDER BY user_id
"""
