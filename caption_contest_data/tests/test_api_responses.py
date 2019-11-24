from pathlib import Path

import pytest

import caption_contest_data as ccd

filenames = list(ccd._api._get_response_fnames().keys())

DUELING_XFAIL = """These contests are dueling bandits, not cardinal bandits
(which have pairwise comparisons, not single caption ratings).
These aren't officially supported.
"""


def _get_file(f):
    if "dueling" in str(f) or "497" in str(f):
        return pytest.param(f, marks=pytest.mark.xfail(reason=DUELING_XFAIL))
    return f


@pytest.fixture(params=[_get_file(f) for f in filenames])
def df(request):
    filename = request.param
    ccd.get_responses()
    return ccd.responses(filename)


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
