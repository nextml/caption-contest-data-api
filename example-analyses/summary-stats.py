import os
import pandas as pd
import utils

if __name__ == "__main__":
    df = utils.read_all_summaries()
    unique_captions = df['caption'].unique()

    print("# unique captions =", len(unique_captions))
    print("# ratings =", df['count'].sum() / 1e6, 'million')
