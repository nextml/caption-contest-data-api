import pytest
from pathlib import Path
import caption_contest_data as ccd


filenames = list(ccd._api._get_response_fnames().keys())

DUELING_XFAIL = """These contests are dueling bandits, not cardinal bandits
(which have pairwise comparisons, not single caption ratings).
These aren't officially supported.
"""

@pytest.fixture(
    params=[
        f
        if "dueling" not in str(f) and "497" not in str(f)
        else pytest.param(f, marks=pytest.mark.xfail(reason=DUELING_XFAIL))
        for f in filenames
    ]
)
def df(request):
    filename = request.param
    root = Path(__file__).parent.parent.parent
    responses = root / "contests" / "responses"
    return ccd.responses(filename, responses=responses)


def test_responses(df):
    expected = {
        "contest",
        "network_delay",
        "response_time",
        "participant_uid",
        "timestamp_query_generated",
        "filename",
        "alg_label",
        "target",
        "target_id",
        "target_reward",
        "timestamp_query_generated",
        "label",
    }
    assert set(df.columns) == expected


#  def test_init_summary():
#  responses = utils.read_responses("514-responses.csv.zip")
#  summary = utils.init_summary(responses)

#  df = utils.read_summary("514_summary_LilUCB.csv")

#  for key in ["score", "funny", "unfunny", "somewhat_funny", "precision"]:
#  assert key in df.columns
#  assert key in summary.columns


#  def test_add_target_ids_to_summary():
#  truth = utils.read_summary("513_summary_LilUCB.csv")
#  responses = utils.read_responses("513-responses.csv.zip")

#  truth = utils.add_target_ids(truth, responses)
#  for target_id in truth["target_id"].unique():
#  df1 = truth[truth["target_id"] == target_id]
#  df2 = responses[responses["target_id"] == target_id]

#  assert all(df1["target_id"].values[0] == df2["target_id"])
