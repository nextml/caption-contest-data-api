import pandas as pd
import os
import pytest
import sys

sys.path.append("../example-analyses")
import utils

dfs = {f: pd.read_csv("summaries/" + f) for f in os.listdir("summaries/") if "csv" in f}
df = utils.read_all_summaries()
expected_cols = {
    "rank",
    "caption",
    "score",
    "precision",
    "count",
    "funny",
    "somewhat_funny",
    "unfunny",
    "contest",
}


@pytest.mark.parametrize("f,df", list(dfs.items()))
def test_summary(f, df, expected_cols=expected_cols):
    cols = set(df.columns)
    top = df["score"].idxmax()
    bottom = df["score"].idxmin()
    assert df.loc[top]["rank"] == 1  # fails for certain contests
    assert expected_cols.issubset(cols), "Missing columns {} in {}".format(
        expected_cols - cols, f
    )  # a lot of dfs are missing column "contest"
    assert df.loc[bottom]["rank"] == len(df)  # often fails; use scipy.stats.rankdata


@pytest.mark.parametrize("df", [df])
@pytest.mark.parametrize("col", list(expected_cols))
def test_complete(df, col):
    nulls = df[col].isnull().sum()
    # need to reformulate a lot of columns
    # score, precision have 2 nans
    # somewhat_funny (" " vs "_"?)
    # count is also null for some contests
    assert nulls == 0, f"{col}"
