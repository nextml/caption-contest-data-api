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
    df.filename = filename
    return df


def test_columns(df):
    rank_score = {r: s for r, s in zip(df["rank"], df["score"])}
    ranks = sorted(list(rank_score.keys()))
    ranks = np.array(ranks)
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

    # Make sure the best caption comes first
    assert df["rank"].iloc[0] == 1


def test_counts(df):
    expected_count = df["funny"] + df["somewhat_funny"] + df["unfunny"]
    assert (df["count"] == expected_count).all()


def test_means(df):
    predicted_score = df["unfunny"] + 2 * df["somewhat_funny"] + 3 * df["funny"]
    predicted_score /= df["count"]
    nan = np.isnan(predicted_score) | df["score"].isnull()
    assert np.allclose(df["score"][~nan], predicted_score[~nan])


def test_few_nulls(df):
    for col in df.columns:
        nulls = df[col].isnull().sum()
        if col == "caption":
            assert nulls <= 3, "Sometimes people don't submit *anything*"
        elif col in {"score", "precision"} and any(
            x in df.filename for x in ["520", "521"]
        ):
            assert nulls == 1
        else:
            assert nulls == 0, f"{col}"


if __name__ == "__main__":
    dfs = {fname: pd.read_csv("summaries/" + fname) for fname in filenames}

    for fname, df in dfs.items():
        df = df.sort_values(by="rank")
        df.to_csv("summaries/" + fname, index=False)
