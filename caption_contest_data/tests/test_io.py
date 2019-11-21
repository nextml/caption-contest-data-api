import os, sys
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

root = Path(__file__).parent.parent.parent
zips = root / "contests" / "responses"
filenames = [
    f
    for f in zips.glob("*.zip")
    if all(s not in str(f) for s in ["dueling", "499", "497"])
]


@pytest.fixture(params=filenames)
def filename(request):
    return request.param


def test_responses(filename):
    expected_columns = {
        "network_delay",
        "participant_uid",
        "response_time",
        "target",
        "target_id",
        "target_reward",
        "timestamp_query_generated",
        "alg_label",
    }
    df = utils.read_responses(filename)
    assert set(df.columns) == expected_columns


def test_init_summary():
    responses = utils.read_responses("514-responses.csv.zip")
    summary = utils.init_summary(responses)

    df = utils.read_summary("514_summary_LilUCB.csv")

    for key in ["score", "funny", "unfunny", "somewhat_funny", "precision"]:
        assert key in df.columns
        assert key in summary.columns


def test_add_target_ids_to_summary():
    truth = utils.read_summary("513_summary_LilUCB.csv")
    responses = utils.read_responses("513-responses.csv.zip")

    truth = utils.add_target_ids(truth, responses)
    for target_id in truth["target_id"].unique():
        df1 = truth[truth["target_id"] == target_id]
        df2 = responses[responses["target_id"] == target_id]

        assert all(df1["target_id"].values[0] == df2["target_id"])
