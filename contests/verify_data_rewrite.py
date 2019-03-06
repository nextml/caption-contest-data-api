import pandas as pd
import numpy as np
import os

DIR = "summaries/_fill-in-button-click-backup/"
new_dfs = {name: pd.read_csv(DIR + name) for name in os.listdir(DIR) if name not in {".DS_Store"}}
old_dfs = {name: pd.read_csv("summaries/" + name) for name in new_dfs.keys()}

for name, new_df in new_dfs.items():
    old_df = old_dfs[name]
    int_cols = ['Unnamed: 0', 'target_id', 'count', 'caption', 'contest']
    float_cols = ['mean', 'precision', 'score']
    for col in int_cols:
        not_null = ~old_df[col].isnull()
        assert (new_df[col][not_null] == old_df[col][not_null]).all()
    for col in float_cols:
        assert np.allclose(new_df[col], old_df[col])
