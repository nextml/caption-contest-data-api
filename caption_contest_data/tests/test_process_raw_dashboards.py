import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import caption_contest_data._raw as prd


root = Path(__file__).parent.parent.parent
raw_dashboards = root / "contests" / "summaries" / "_raw-dashboards"
filenames = sorted(list(raw_dashboards.glob("*.csv")))


@pytest.fixture(params=filenames)
def df(request):
    filename = str(request.param)
    return prd.process(filename)


@pytest.mark.parametrize("filename", filenames)
def test_same_dataframe(filename: Path):
    fname = filename.name
    df1 = pd.read_csv(str(root / "contests" / "summaries" / fname))
    df2 = prd.process(str(raw_dashboards / fname))
    assert (df1.columns == df2.columns).all()
    for col in df1.columns:
        if "float" in df1[col].dtype.name:
            assert np.allclose(df1[col], df2[col])
        else:
            assert (df1[col] == df2[col]).all()


def test_correct_order(df):
    # Make sure the best caption comes first
    assert df["rank"].iloc[0] == 1, "funniest first"
    contest = int(df.filename[:3])
    assert (df["contest"] == contest).all()


def test_score(df):
    """ This test is failing because button_clicks isn't
    returning the correct result? """
    pred_score = df.funny * 3 + df.somewhat_funny * 2 + df.unfunny
    pred_score /= df["count"]

    diff = np.abs(pred_score - df["score"])
    assert diff.max() < 1e-4


def test_counts(df):
    count = df.funny + df.somewhat_funny + df.unfunny
    diff = count - df["count"]
    assert diff.max() == diff.min() == 0
    assert (count == df["count"]).all()


def test_columns(df):
    contest = int(df.filename[:3])
    expected_cols = {
        "caption",
        "count",
        "unfunny",
        "somewhat_funny",
        "funny",
        "contest",
        "score",
        "precision",
        "rank",
    }
    assert expected_cols == set(df.columns) - {"target_id"}
    if contest >= 587:
        assert "target_id" in df
    assert df["contest"].dtype == int
    assert df["count"].dtype == int
    assert df["unfunny"].dtype == int
    assert df["somewhat_funny"].dtype == int
    assert df["funny"].dtype == int
    assert df["score"].dtype == float
    assert df["precision"].dtype == float
    assert df["rank"].dtype == int
    assert (df.isnull().sum() == 0).all()


def test_ranks(df):
    funniest = df["score"].idxmax()
    assert df.loc[funniest]["rank"] == 1
    assert df.iloc[0]["rank"] == 1


def test_recover_counts():
    rng = np.random.RandomState(42)
    rand_clicks = lambda size: rng.randint(10, size=size).tolist()
    df = pd.DataFrame(
        {
            "unfunny": rand_clicks(50) + [1, 0, 0, 1, 1],
            "somewhat_funny": rand_clicks(50) + [0, 0, 1, 1, 1],
            "funny": rand_clicks(50) + [0, 1, 0, 1, 0],
        }
    )
    df["count"] = df.funny + df.somewhat_funny + df.unfunny
    score, prec = prd.score_and_prec(
        df.unfunny, df.somewhat_funny, df.funny, df["count"]
    )
    df["score"] = score
    df["precision"] = prec

    count_cols = ["unfunny", "somewhat_funny", "funny"]
    clicks = {key: df[key].copy() for key in count_cols}
    df.drop(count_cols, axis=1, inplace=True)
    df.filename = None
    assert sum([col in df for col in count_cols]) == 0

    out = prd.recover_counts(df)
    for col in count_cols:
        assert (out[col] == clicks[col]).all()
