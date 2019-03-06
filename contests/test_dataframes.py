import pandas as pd
import pytest
import numpy as np
import os
import scipy.stats

filenames = [
    f
    for f in os.listdir("summaries/")
    if ".DS" not in f and f[0] != "_" and int(f[:3]) < 587
]


@pytest.fixture(params=filenames)
def df(request):
    filename = request.param
    df = pd.read_csv("summaries/" + filename)
    return df


def test_columns(df):
    for k in rank_score:
        if k >= 2:
            i = (ranks == k).argmax()
            if np.isnan(rank_score[k]):
                continue
            assert rank_score[ranks[i - 1]] >= rank_score[k]
    expected_cols = {
        "rank",
        "caption",
        "score",
        "precision",
        "count",
        "unfunny",
        "somewhat_funny",
        "funny",
    }
    assert expected_cols == set(df.columns)


if __name__ == "__main__":
    bad_dfs = [
        "529_summary_LilUCB.csv",
        "527_summary_LilUCB.csv",
        "530_summary_LilUCB.csv",
        "528_summary_LilUCB.csv",
    ]
    bad_dfs = filenames
    bad_dfs = {fname: pd.read_csv("summaries/" + fname) for fname in bad_dfs}

    for fname, df in bad_dfs.items():
        rank = scipy.stats.rankdata(-df["score"], method="min").astype(int)

        df["rank"] = rank

        rank_score = {r: s for r, s in zip(df["rank"], df["score"])}
        ranks = sorted(list(rank_score.keys()))
        ranks = np.array(ranks)

        for k in rank_score:
            if k >= 2:
                i = (ranks == k).argmax()
                if np.isnan(rank_score[k]):
                    continue
                assert rank_score[ranks[i - 1]] >= rank_score[k]
        for col in ["Unnamed: 0", "Unnamed: 0.1"]:
            if col in df:
                del df[col]
        if "count" not in df.columns:
            df["count"] = df["unfunny"] + df["funny"] + df["somewhat_funny"]
        test_columns(df)
        #  df.to_csv("summaries/" + fname)
