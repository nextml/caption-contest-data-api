import os

import pytest

from process_raw_dashboards import read_csv

DIR = "summaries/_raw-dashboards/"
filenames = sorted([f for f in os.listdir(DIR) if f[0] not in {".", "_"}])


@pytest.fixture(params=filenames)
def df(request):
    filename = request.param
    df = read_csv("summaries/_raw-dashboards/" + filename)
    df.filename = filename
    return df


def test_cols(df):
    cols = [col.lower() for col in df.columns]
    contest = int(df.filename[:3])
    if 587 <= contest <= 636:
        assert "unfunny" not in cols
        assert "funny" not in cols
        somewhat_funny = [key in cols for key in ["somewhat_funny", "somewhat funny"]]
        assert sum(somewhat_funny) == 0
        assert "mean" in cols
        assert "precision" in cols
        assert "count" in cols
    else:
        assert "unfunny" in cols
        assert "funny" in cols
        somewhat_funny = [key in cols for key in ["somewhat_funny", "somewhat funny"]]
        assert sum(somewhat_funny) == 1

def test_scores_bounded(df):
    contest = int(df.filename[:3])
    df.columns = [c.lower() for c in df.columns]
    if contest <= 526:
        assert "mean" not in df and "score" not in df
        return
    scores = "mean" if "mean" in df else "score"

    if contest not in {589, 591, 592, 599, 600}:
        assert 1 <= df[scores].min() < df[scores].max() <= 3
    elif contest in {591, 592, 599, 600}:
        assert 4 < df[scores].max()
    else:
        assert df[scores].min() < 1
