import pandas as pd
import pytest
import numpy as np
import os
import scipy.stats

filenames = [f for f in os.listdir("summaries/") if f[0] not in {"_", "."}]
filenames = sorted(filenames)


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
        "contest",
    }
    assert expected_cols == set(df.columns) - {"target_id"}
    contest = int(df.filename[:3])
    if contest >= 587:
        assert "target_id" in set(df.columns)

    # Make sure the best caption comes first
    assert df["rank"].iloc[0] == 1
    contest = int(df.filename[:3])
    assert (df["contest"] == contest).all()


def test_counts(df):
    expected_count = df["funny"] + df["somewhat_funny"] + df["unfunny"]
    diff = np.abs(df["count"] - expected_count)
    assert diff.max() <= 3


def test_means(df):
    df.dropna(inplace=True)
    predicted_score = df["unfunny"] + 2 * df["somewhat_funny"] + 3 * df["funny"]
    predicted_score /= df["count"]

    assert df["score"].min() >= 1
    assert df["score"].max() <= 3

    diff = np.abs(predicted_score - df["score"])
    assert diff.median() <= 0.01
    assert diff.quantile(0.8) <= 0.02
    assert diff.quantile(0.9) <= 0.03
    assert diff.quantile(0.99) <= 0.04


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
        #  score_col = {col for col in df.columns if "score" in col or "mean" in col}
        #  print(score_col, fname)
        df.filename = fname
        count_cols = [col for col in df.columns if "count" in col]
        if len(count_cols) > 1:
            #  print(fname, count_cols)
            diff = np.abs(df["count"] - df["counts"])
            if not diff.max() == 0:
                assert diff.max() == 1
                expected_count = df["funny"] + df["somewhat_funny"] + df["unfunny"]
                diff1 = np.abs(expected_count - df["count"])
                diff2 = np.abs(expected_count - df["counts"])
                assert diff1.max() == 1
                assert diff2.max() == 0
                df["count"] = expected_count
                del df["counts"]
                #  df.to_csv("summaries/" + fname)
        test_counts(df)
