import os, sys
import numpy as np
import pandas as pd
import pytest

contest_dir = "/".join(os.path.abspath(__file__).split("/")[:-1])
sys.path.append(contest_dir + "/../example-analyses")
import utils

DIR = f"{contest_dir}/responses/"
filenames = [
    f
    for f in os.listdir(DIR)
    if f[-4:] == ".zip" and all(s not in f for s in ["dueling", "499", "497"])
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


@pytest.mark.parametrize(
    "contest",
    [532, 533, 534, 535, 536, 537, 538, 539, 541, 542, 543, 544, 545, 546, 547, 548],
)
def test_calculate_stats(contest):
    tol = {536: 0.025, 537: 0.014, 538: 0.013, 539: 0.014, 542: 0.018}
    fname = "{}_summary_LilUCB.csv".format(contest)
    df1 = utils.read_summary(fname)
    df2 = utils.read_summary(fname)
    df2.drop(columns=["score", "precision"])

    df2 = utils.calculate_stats(df2)

    for col in ["score", "precision"]:
        diff = np.abs(df1[col] - df2[col])
        assert diff.max() < tol.get(contest, max(tol))

    high_scores = df1["score"] > 1.05
    assert len(df1) * 0.5 < high_scores.sum(), "Testing more than half the df"
    assert np.allclose(df1["score"][high_scores], df2["score"][high_scores])

    assert np.abs(df1["count"] - df2["count"]).max() < 10
    diff = np.abs(df1["unfunny"] - df2["unfunny"]) / df1["count"]
    if contest in {536, 543, 544, 545}:
        assert diff.median() < 0.13
        assert diff.max() < 0.15
    else:
        assert diff.median() < 0.02
        assert diff.max() < 0.13

    diff = np.abs(df1["funny"] - df2["funny"]) / df1["count"]
    assert diff.median() < 0.02
    assert diff.max() < 0.15

    diff = np.abs(df1["somewhat_funny"] - df2["somewhat_funny"]) / df1["count"]
    assert diff.median() < 0.05
    assert diff.max() < 0.3


def test_summary_rank(contest="558"):
    responses = utils.read_responses(f"{contest}-responses.csv.zip")
    summary = utils.init_summary(responses)
    summary = utils.read_summary(f"{contest}_summary_LilUCB.csv")

    df = utils.calculate_stats(summary)

    ranks = {rank: mean for rank, mean in zip(df["rank"], df["score"])}
    for i in range(len(ranks) - 1):
        assert ranks[i + 1] >= ranks[i + 2]


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
