import os

import numpy as np
import pandas as pd
import pytest

from add_data import recover_counts

filenames = [
    f for f in os.listdir("summaries/") if ".DS" not in f and f[0] not in {"_", "."}
]


@pytest.fixture(params=filenames)
def df(request):
    filename = request.param
    df = pd.read_csv("summaries/" + filename)
    df.filename = filename
    return df


def poor_reconstruction(filename):
    contest = int(filename[:3])
    return contest in {513, 529, 534, 557, 549, 517, 516, 521, 515, 520, 530, 545, 572}


@pytest.mark.parametrize("filenames", [filenames])
def test_mostly_good_reconstructions(filenames):
    bad = [f for f in filenames if poor_reconstruction(f)]
    assert len(bad) / len(filenames) < 0.20


def test_recover(df):
    new_df = recover_counts(df)
    assert new_df is not df
    assert set(df.index) == set(new_df.index)
    for col in df.columns:
        if df[col].dtype == object:
            assert list(new_df[col]) == list(df[col])
        elif col in {"funny", "unfunny", "somewhat_funny"}:
            diff = np.abs(new_df[col] - df[col])
            if poor_reconstruction(df.filename):
                assert np.abs(new_df[col] - df[col]).max() <= 4
            else:
                assert np.allclose(new_df[col], df[col]) or diff.max() < 1e-7
