import pandas as pd

CASES = [
    {"name": "spring forward", "call": "hours_in_day('2024-03-10', 'America/New_York')", "expected": "23", "visible": True},
    {"name": "normal day", "call": "hours_in_day('2024-03-11', 'America/New_York')", "expected": "24", "visible": True},
    {"name": "fall back", "call": "hours_in_day('2024-11-03', 'America/New_York')", "expected": "25"},
    {"name": "Europe spring", "call": "hours_in_day('2024-03-31', 'Europe/Berlin')", "expected": "23"},
    {"name": "Europe autumn", "call": "hours_in_day('2024-10-27', 'Europe/Berlin')", "expected": "25"},
    {"name": "no DST zone", "call": "hours_in_day('2024-03-10', 'Asia/Tokyo')", "expected": "24"},
    {"name": "southern hemisphere", "call": "hours_in_day('2024-04-07', 'Australia/Sydney')", "expected": "25"},
    {"name": "whole year Paris", "call": "sum(hours_in_day(d, 'Europe/Paris') for d in pd.date_range('2024-01-01', '2024-12-31').strftime('%Y-%m-%d'))", "expected": "8784"},
]
