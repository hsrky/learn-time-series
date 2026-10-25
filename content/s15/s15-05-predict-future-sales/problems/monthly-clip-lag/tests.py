import numpy as np
import pandas as pd

D1 = pd.DataFrame({"date_block_num": [0, 0, 1, 1], "shop_id": [1, 1, 1, 2], "item_id": [10, 10, 10, 10], "item_cnt_day": [3, 4, 30, -1]})
D2 = pd.DataFrame({"date_block_num": [2, 0, 2, 0], "shop_id": [5, 5, 5, 5], "item_id": [7, 7, 7, 7], "item_cnt_day": [1, 2, 3, 4]})
D3 = pd.DataFrame({"date_block_num": [], "shop_id": [], "item_id": [], "item_cnt_day": []})
rng = np.random.default_rng(14)
D4 = pd.DataFrame({"date_block_num": rng.integers(0, 12, 3000), "shop_id": rng.integers(0, 6, 3000),
                   "item_id": rng.integers(0, 15, 3000), "item_cnt_day": rng.integers(-1, 6, 3000)})

CASES = [
    {"name": "example", "call": "monthly_clip_lag(D1)", "visible": True,
     "expected": "pd.DataFrame({'date_block_num': [0,1,1], 'shop_id': [1,1,2], 'item_id': [10,10,10], 'item_cnt_month': [7.0,20.0,0.0], 'lag_1': [0.0,7.0,0.0]})"},
    {"name": "gap month gives lag 0", "call": "monthly_clip_lag(D2)", "visible": True,
     "expected": "pd.DataFrame({'date_block_num': [0,2], 'shop_id': [5,5], 'item_id': [7,7], 'item_cnt_month': [6.0,4.0], 'lag_1': [0.0,0.0]})"},
    {"name": "custom clip range", "call": "monthly_clip_lag(D1, 1, 5)",
     "expected": "pd.DataFrame({'date_block_num': [0,1,1], 'shop_id': [1,1,2], 'item_id': [10,10,10], 'item_cnt_month': [5.0,5.0,1.0], 'lag_1': [0.0,5.0,0.0]})"},
    {"name": "empty", "call": "monthly_clip_lag(D3)", "check_index": False},
    {"name": "larger random", "call": "monthly_clip_lag(D4)"},
]
