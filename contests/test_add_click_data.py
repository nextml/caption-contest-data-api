import os

import numpy as np
import pandas as pd
import pytest

from add_data import recover_counts

filenames = [
    f
    for f in os.listdir("summaries/")
    if ".DS" not in f and f[0] != "_" and int(f[:3]) < 587
]


def poor_reconstruction(filename):
    contest = int(filename[:3])
    return contest in {513, 529, 534, 557, 549, 517, 516, 521, 515, 520, 530, 545, 572}


@pytest.mark.parametrize("filenames", [filenames])
def test_mostly_good_reconstructions(filenames):
    bad = [f for f in filenames if poor_reconstruction(f)]
    assert len(bad) / len(filenames) < 0.20


@pytest.mark.parametrize("filename", filenames)
def test_recover(filename):
    """
    """
    df = pd.read_csv("summaries/" + filename)
    new_df = recover_counts(df)
    assert set(df.index) == set(new_df.index)
    for col in df.columns:
        if col in {"funny", "unfunny", "somewhat_funny"} and poor_reconstruction(
            filename
        ):
            assert np.abs(new_df[col] - df[col]).max() <= 4
        elif df[col].dtype == object:
            assert list(new_df[col]) == list(df[col])
        else:
            diff = np.abs(new_df[col] - df[col])
            assert np.allclose(new_df[col], df[col]) or diff.max() < 1e-7
